import logging
try:
    import torch
    HAS_TORCH = True
except ImportError:
    torch = None
    HAS_TORCH = False

from typing import List, Dict, Optional
from ..config import settings
from ..models.schemas import NewsArticleSentiment, DailySentimentAggregate

logger = logging.getLogger(__name__)

class FinbertSentimentAnalyzer:
    """
    FinBERT NLP Sentiment Analysis Engine powered by Hugging Face Transformers ('ProsusAI/finbert').
    Computes fine-grained probabilities for financial headlines and aggregates daily ticker sentiment.
    """

    def __init__(self, model_name: str = settings.FINBERT_MODEL_NAME):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if (HAS_TORCH and torch and torch.cuda.is_available()) else "cpu"
        self._is_initialized = False

    def load_model(self):
        """
        Loads the tokenizer and sequence classification model on demand.
        """
        if self._is_initialized:
            return

        if not HAS_TORCH:
            logger.info("PyTorch is not installed in current environment. Using financial sentiment scoring engine.")
            self._is_initialized = False
            return

        try:
            logger.info(f"Loading FinBERT model '{self.model_name}' on device: {self.device}")
            from transformers import AutoTokenizer, AutoModelForSequenceClassification

            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            self._is_initialized = True
            logger.info("FinBERT model and tokenizer initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to load Hugging Face FinBERT model: {str(e)}. Fallback sentiment heuristics will be used.", exc_info=True)
            self._is_initialized = False

    def analyze_headlines(self, items: List[Dict]) -> List[NewsArticleSentiment]:
        """
        Analyzes a list of raw news headline dictionaries and returns scored sentiment objects.
        """
        if not items:
            return []

        # Ensure model is loaded or prepare heuristic fallback
        if not self._is_initialized:
            self.load_model()

        results: List[NewsArticleSentiment] = []

        if self._is_initialized and self.model and self.tokenizer:
            try:
                headlines = [item.get("headline", "") for item in items]
                batch_size = settings.BATCH_SIZE

                for i in range(0, len(headlines), batch_size):
                    batch_headlines = headlines[i:i + batch_size]
                    batch_items = items[i:i + batch_size]

                    inputs = self.tokenizer(
                        batch_headlines,
                        padding=True,
                        truncation=True,
                        max_length=128,
                        return_tensors="pt"
                    ).to(self.device)

                    with torch.no_grad():
                        outputs = self.model(**inputs)
                        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)

                    # FinBERT classes: [0: positive, 1: negative, 2: neutral]
                    id2label = self.model.config.id2label

                    for j, prob_tensor in enumerate(probs):
                        prob_list = prob_tensor.cpu().numpy().tolist()
                        
                        # Match label names dynamically from model config
                        label_prob_map = {id2label[k].lower(): prob_list[k] for k in range(len(prob_list))}
                        pos = float(label_prob_map.get("positive", 0.0))
                        neg = float(label_prob_map.get("negative", 0.0))
                        neu = float(label_prob_map.get("neutral", 0.0))

                        # Determine primary label
                        max_label = max([("positive", pos), ("neutral", neu), ("negative", neg)], key=lambda x: x[1])[0]
                        
                        # Compound sentiment score (-1.0 to +1.0)
                        score = float(pos - neg)

                        results.append(NewsArticleSentiment(
                            headline=batch_items[j].get("headline", ""),
                            sentiment=max_label,
                            positive_prob=round(pos, 4),
                            neutral_prob=round(neu, 4),
                            negative_prob=round(neg, 4),
                            score=round(score, 4),
                            published_at=batch_items[j].get("published_at"),
                            url=batch_items[j].get("url")
                        ))

                return results
            except Exception as e:
                logger.error(f"Error during FinBERT batch inference: {str(e)}. Using rule-based fallback.", exc_info=True)

        # Fallback heuristic analyzer for uninterrupted reliability
        return self._heuristic_analyze(items)

    def _heuristic_analyze(self, items: List[Dict]) -> List[NewsArticleSentiment]:
        """
        Financial domain lexicon fallback when transformer weights are unavailable or offline.
        """
        bullish_keywords = {"surge", "beat", "rally", "growth", "high", "upgrade", "profit", "gain", "soar", "record", "strong"}
        bearish_keywords = {"drop", "fall", "miss", "plunge", "downgrade", "loss", "decline", "slump", "lawsuit", "cut", "weak"}

        results = []
        for item in items:
            text = item.get("headline", "").lower()
            pos_matches = sum(1 for kw in bullish_keywords if kw in text)
            neg_matches = sum(1 for kw in bearish_keywords if kw in text)

            if pos_matches > neg_matches:
                sentiment = "positive"
                pos, neu, neg = 0.75, 0.20, 0.05
                score = 0.70
            elif neg_matches > pos_matches:
                sentiment = "negative"
                pos, neu, neg = 0.05, 0.20, 0.75
                score = -0.70
            else:
                sentiment = "neutral"
                pos, neu, neg = 0.15, 0.70, 0.15
                score = 0.00

            results.append(NewsArticleSentiment(
                headline=item.get("headline", ""),
                sentiment=sentiment,
                positive_prob=pos,
                neutral_prob=neu,
                negative_prob=neg,
                score=score,
                published_at=item.get("published_at"),
                url=item.get("url")
            ))
        return results

    def aggregate_sentiment(self, ticker: str, articles: List[NewsArticleSentiment]) -> DailySentimentAggregate:
        """
        Aggregates article-level sentiment into daily Sentiment_Score and News_Count.
        """
        if not articles:
            return DailySentimentAggregate(
                ticker=ticker,
                Sentiment_Score=0.0,
                News_Count=0,
                positive_count=0,
                neutral_count=0,
                negative_count=0,
                sentiment_label="Neutral",
                headlines=[]
            )

        total_score = sum(a.score for a in articles)
        news_count = len(articles)
        avg_score = round(total_score / news_count, 4)

        pos_count = sum(1 for a in articles if a.sentiment == "positive")
        neu_count = sum(1 for a in articles if a.sentiment == "neutral")
        neg_count = sum(1 for a in articles if a.sentiment == "negative")

        if avg_score >= 0.15:
            sentiment_label = "Bullish"
        elif avg_score <= -0.15:
            sentiment_label = "Bearish"
        else:
            sentiment_label = "Neutral"

        return DailySentimentAggregate(
            ticker=ticker,
            Sentiment_Score=avg_score,
            News_Count=news_count,
            positive_count=pos_count,
            neutral_count=neu_count,
            negative_count=neg_count,
            sentiment_label=sentiment_label,
            headlines=articles
        )

finbert_analyzer = FinbertSentimentAnalyzer()
