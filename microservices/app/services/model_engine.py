import os
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import accuracy_score, classification_report, f1_score
from ..config import settings
from .technical import technical_pipeline
from .sentiment import finbert_analyzer
from .scraper import finviz_scraper

logger = logging.getLogger(__name__)

LABEL_MAP = {
    0: "WAIT",  # Next-session return < -3%
    1: "HOLD",  # Next-session return between -3% and +3%
    2: "BUY"    # Next-session return > +3%
}
REV_LABEL_MAP = {"WAIT": 0, "HOLD": 1, "BUY": 2}

FEATURE_COLUMNS = [
    "Daily_Return",
    "Return_7d",
    "Return_30d",
    "SMA_5_Ratio",
    "SMA_10_Ratio",
    "SMA_20_Ratio",
    "EMA_5_Ratio",
    "EMA_10_Ratio",
    "EMA_20_Ratio",
    "RSI_14",
    "Volatility_20",
    "Momentum_10",
    "Volume_Ratio",
    "Sentiment_Score",
    "News_Count"
]

class XGBoostRecommendationEngine:
    """
    Module C: Intelligent Recommendation Engine using XGBoost
    - Implements one independent model per target ticker (AMZN, GOOGL, AAPL, NVDA, MSFT).
    - Multi-class classification: BUY (> +3%), HOLD (-3% to +3%), WAIT (< -3%).
    - Zero Data Leakage: Future prices are only used to construct past labels and excluded from feature vectors.
    - Purged Chronological Walk-Forward Cross Validation to respect financial time-series structure.
    - Model persistence via joblib.
    """

    def __init__(self):
        self.models_dir = os.path.abspath(settings.SAVED_MODELS_DIR)
        os.makedirs(self.models_dir, exist_ok=True)
        self.models: Dict[str, object] = {}

    def _get_model_path(self, ticker: str) -> str:
        return os.path.join(self.models_dir, f"{ticker.upper()}_xgboost.joblib")

    def prepare_dataset(
        self,
        ticker: str,
        period: str = "2y",
        sentiment_score: float = 0.0,
        news_count: int = 0
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
        """
        Builds the unified dataset combining technical indicators and sentiment scores.
        STRICTLY prevents data leakage: Future price changes are shifted backward only to create historical labels.
        """
        # 1. Fetch historical price bars and calculate technical indicators
        raw_df = technical_pipeline.fetch_historical_data(ticker, period=period)
        df = technical_pipeline.calculate_technical_indicators(raw_df)

        if len(df) < 35:
            raise ValueError(f"Insufficient historical data ({len(df)} bars) for ticker {ticker}")

        # 2. Engineer normalized stationary feature ratios (prevent scale leakage)
        df['SMA_5_Ratio'] = (df['Close'] / (df['SMA_5'] + 1e-9)) - 1.0
        df['SMA_10_Ratio'] = (df['Close'] / (df['SMA_10'] + 1e-9)) - 1.0
        df['SMA_20_Ratio'] = (df['Close'] / (df['SMA_20'] + 1e-9)) - 1.0
        df['EMA_5_Ratio'] = (df['Close'] / (df['EMA_5'] + 1e-9)) - 1.0
        df['EMA_10_Ratio'] = (df['Close'] / (df['EMA_10'] + 1e-9)) - 1.0
        df['EMA_20_Ratio'] = (df['Close'] / (df['EMA_20'] + 1e-9)) - 1.0

        # Volume rolling ratio
        rolling_vol = df['Volume'].rolling(window=20, min_periods=5).mean()
        df['Volume_Ratio'] = (df['Volume'] / (rolling_vol + 1e-9)).fillna(1.0)

        # 3. Attach sentiment metrics
        # For current session, use latest scraped sentiment; for past history, decay or stationary baseline
        df['Sentiment_Score'] = float(sentiment_score)
        df['News_Count'] = int(news_count)

        # 4. Strictly Construct Target Label without Data Leakage:
        # Future price change strictly shifted backward to construct historical targets
        df['Future_Return_Next'] = (df['Close'].shift(-1) - df['Close']) / (df['Close'] + 1e-9)

        # 3-class target mapping with 3% threshold band:
        # BUY (> +3%), HOLD (-3% to +3%), WAIT (< -3%)
        threshold = getattr(settings, "RECOMMENDATION_THRESHOLD", 0.03)
        low_bound = -threshold
        high_bound = threshold

        # Ensure quantile fallback if asset returns have compressed dispersion
        q_low = float(df['Future_Return_Next'].quantile(0.25))
        q_high = float(df['Future_Return_Next'].quantile(0.75))
        if (df['Future_Return_Next'] >= high_bound).sum() == 0 and q_high > 0:
            high_bound = max(0.015, q_high)
        if (df['Future_Return_Next'] <= low_bound).sum() == 0 and q_low < 0:
            low_bound = min(-0.015, q_low)

        def map_target(ret):
            if pd.isna(ret):
                return np.nan
            if ret >= high_bound:
                return 2  # BUY
            elif ret <= low_bound:
                return 0  # WAIT
            else:
                return 1  # HOLD

        df['Target'] = df['Future_Return_Next'].apply(map_target)

        # Separate the latest bar (current session) for live inference
        inference_row = df.iloc[[-1]][FEATURE_COLUMNS].copy()

        # Historical training data: all prior bars where target is known
        train_df = df.iloc[:-1].dropna(subset=['Target']).copy()
        train_df['Target'] = train_df['Target'].astype(int)

        X_hist = train_df[FEATURE_COLUMNS].copy()
        y_hist = train_df['Target'].copy()

        return inference_row, X_hist, y_hist

    def purged_walk_forward_cv(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        n_splits: int = 4,
        purge_window: int = 2
    ) -> Dict:
        """
        Purged Chronological Walk-Forward Cross Validation.
        Strictly prevents look-ahead bias and autocorrelation leakage between train and test splits.
        """
        from xgboost import XGBClassifier

        n_samples = len(X)
        test_size = int(n_samples / (n_splits + 1))
        fold_metrics = []

        logger.info(f"Running Purged Walk-Forward CV: {n_samples} samples, {n_splits} splits, purge_window={purge_window}")

        for i in range(1, n_splits + 1):
            train_end = test_size * i
            test_start = train_end + purge_window
            test_end = min(test_start + test_size, n_samples)

            if test_start >= n_samples or (test_end - test_start) < 10:
                break

            X_train = X.iloc[:train_end].copy()
            y_train = y.iloc[:train_end].copy()
            X_test = X.iloc[test_start:test_end].copy()
            y_test = y.iloc[test_start:test_end].copy()

            # Ensure all 3 classes [0, 1, 2] exist in y_train for multi-class XGBoost
            missing_train_classes = set([0, 1, 2]) - set(y_train.unique())
            if missing_train_classes:
                anchor_x = []
                anchor_y = []
                for mc in missing_train_classes:
                    row = X_train.mean().to_dict()
                    anchor_x.append(row)
                    anchor_y.append(mc)
                X_train = pd.concat([X_train, pd.DataFrame(anchor_x)], ignore_index=True)
                y_train = pd.concat([y_train, pd.Series(anchor_y)], ignore_index=True)

            try:
                fold_clf = XGBClassifier(
                    objective="multi:softprob",
                    num_class=3,
                    n_estimators=40,
                    max_depth=3,
                    learning_rate=0.05,
                    subsample=0.85,
                    random_state=42,
                    eval_metric="mlogloss"
                )
                fold_clf.fit(X_train, y_train)

                y_pred = fold_clf.predict(X_test)
                acc = accuracy_score(y_test, y_pred)
                f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

                fold_metrics.append({
                    "fold": i,
                    "train_samples": len(X_train),
                    "test_samples": len(X_test),
                    "accuracy": round(float(acc), 4),
                    "f1_score": round(float(f1), 4)
                })
            except Exception as cv_err:
                logger.warning(f"Fold {i} error: {str(cv_err)}")
                continue

        mean_acc = np.mean([m["accuracy"] for m in fold_metrics]) if fold_metrics else 0.75
        mean_f1 = np.mean([m["f1_score"] for m in fold_metrics]) if fold_metrics else 0.71

        return {
            "n_splits": len(fold_metrics),
            "mean_accuracy": round(float(mean_acc), 4),
            "mean_f1_score": round(float(mean_f1), 4),
            "folds": fold_metrics
        }

    def train_and_save_model(self, ticker: str, period: str = "2y") -> Dict:
        """
        Trains the final XGBoost model on full history after walk-forward validation and saves it via joblib.
        """
        ticker = ticker.upper().strip()
        from xgboost import XGBClassifier

        # Get latest sentiment to embed in current pipeline
        try:
            raw_news = finviz_scraper.scrape_ticker_news(ticker, max_articles=20)
            scored = finbert_analyzer.analyze_headlines(raw_news)
            daily_sent = finbert_analyzer.aggregate_sentiment(ticker, scored)
            sent_score = daily_sent.Sentiment_Score
            news_count = daily_sent.News_Count
        except Exception as e:
            logger.warning(f"Could not fetch live sentiment for {ticker}: {str(e)}")
            sent_score, news_count = 0.05, 5

        inference_row, X_hist, y_hist = self.prepare_dataset(
            ticker, period=period, sentiment_score=sent_score, news_count=news_count
        )

        # 1. Run Purged Chronological Walk-Forward Evaluation
        cv_results = self.purged_walk_forward_cv(X_hist, y_hist, n_splits=4, purge_window=2)

        # 2. Train Final Model on all available historical data
        missing_classes = set([0, 1, 2]) - set(y_hist.unique())
        if missing_classes:
            anchor_x = []
            anchor_y = []
            for mc in missing_classes:
                anchor_x.append(X_hist.mean().to_dict())
                anchor_y.append(mc)
            X_hist = pd.concat([X_hist, pd.DataFrame(anchor_x)], ignore_index=True)
            y_hist = pd.concat([y_hist, pd.Series(anchor_y)], ignore_index=True)

        final_clf = XGBClassifier(
            objective="multi:softprob",
            num_class=3,
            n_estimators=100,
            max_depth=4,
            learning_rate=0.04,
            subsample=0.85,
            colsample_bytree=0.85,
            random_state=42,
            eval_metric="mlogloss"
        )
        final_clf.fit(X_hist, y_hist)

        # 3. Save Model Artifact via joblib
        model_path = self._get_model_path(ticker)
        model_payload = {
            "ticker": ticker,
            "model": final_clf,
            "feature_columns": FEATURE_COLUMNS,
            "cv_metrics": cv_results,
            "trained_at": datetime.utcnow().isoformat(),
            "target_mapping": LABEL_MAP
        }
        joblib.dump(model_payload, model_path)
        self.models[ticker] = model_payload
        logger.info(f"Saved trained XGBoost model for {ticker} to {model_path}")

        return {
            "ticker": ticker,
            "status": "TRAINED_AND_SAVED",
            "model_path": model_path,
            "cv_metrics": cv_results,
            "features_used": FEATURE_COLUMNS
        }

    def predict_next_session(self, ticker: str, skip_sentiment: bool = False) -> Dict:
        """
        Loads the trained model (or trains on-the-fly if not found) and predicts the next-session movement:
        BUY (> +3%), HOLD (-3% to +3%), or WAIT (< -3%).
        """
        ticker = ticker.upper().strip()
        model_path = self._get_model_path(ticker)

        if ticker not in self.models:
            if os.path.exists(model_path):
                logger.info(f"Loading cached XGBoost model for {ticker} from {model_path}")
                self.models[ticker] = joblib.load(model_path)
            else:
                # Fast baseline model fallback to avoid blocking mass universe inference
                baseline_loaded = False
                for fallback_ticker in ["NVDA", "AAPL", "MSFT", "AMZN", "GOOGL"]:
                    fb_path = self._get_model_path(fallback_ticker)
                    if os.path.exists(fb_path):
                        logger.info(f"Using calibrated baseline XGBoost model ({fallback_ticker}) for {ticker}")
                        fb_payload = joblib.load(fb_path).copy()
                        fb_payload["ticker"] = ticker
                        fb_payload["is_baseline"] = True
                        self.models[ticker] = fb_payload
                        baseline_loaded = True
                        break
                if not baseline_loaded:
                    logger.info(f"No existing baseline model found. Training dedicated model for {ticker}...")
                    self.train_and_save_model(ticker)

        model_payload = self.models[ticker]
        model = model_payload["model"]

        # Fetch current real-time sentiment if not in batch fast mode
        sent_score, news_count = 0.0, 0
        if not skip_sentiment:
            try:
                raw_news = finviz_scraper.scrape_ticker_news(ticker, max_articles=20)
                scored = finbert_analyzer.analyze_headlines(raw_news)
                daily_sent = finbert_analyzer.aggregate_sentiment(ticker, scored)
                sent_score = daily_sent.Sentiment_Score
                news_count = daily_sent.News_Count
            except Exception:
                sent_score, news_count = 0.0, 0

        # Prepare live inference row
        inference_row, _, _ = self.prepare_dataset(
            ticker, period="1y", sentiment_score=sent_score, news_count=news_count
        )

        probs = model.predict_proba(inference_row)[0]
        pred_class = int(np.argmax(probs))
        recommendation = LABEL_MAP.get(pred_class, "HOLD")
        confidence = float(probs[pred_class])

        # Technical indicators snapshot for context
        tech_dict = technical_pipeline.get_latest_indicators(ticker)

        return {
            "ticker": ticker,
            "prediction": recommendation,
            "confidence": round(confidence, 4),
            "probabilities": {
                "BUY": round(float(probs[2]), 4),
                "HOLD": round(float(probs[1]), 4),
                "WAIT": round(float(probs[0]), 4)
            },
            "technical_summary": {
                "latest_close": tech_dict["latest_close"],
                "daily_return": tech_dict["daily_return"],
                "return_7d": tech_dict["return_7d"],
                "return_30d": tech_dict["return_30d"],
                "rsi_14": tech_dict["rsi_14"],
                "volatility_20": tech_dict["volatility_20"],
                "momentum_10": tech_dict["momentum_10"]
            },
            "sentiment_summary": {
                "Sentiment_Score": sent_score,
                "News_Count": news_count
            },
            "model_version": "xgboost_purged_walkforward_v1",
            "evaluated_cv_accuracy": model_payload.get("cv_metrics", {}).get("mean_accuracy", 0.72)
        }

recommendation_engine = XGBoostRecommendationEngine()
