import logging
from typing import Dict, List
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from ..config import settings
from ..services.model_engine import recommendation_engine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/predictions", tags=["XGBoost Recommendations"])

@router.get("/{ticker}")
def get_prediction(ticker: str):
    """
    Generate next-session stock price movement recommendation (BUY / HOLD / WAIT)
    along with confidence score and class probability distributions.
    """
    ticker_clean = ticker.upper().strip()
    try:
        result = recommendation_engine.predict_next_session(ticker_clean)
        return result
    except Exception as e:
        logger.error(f"Error generating recommendation for {ticker_clean}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train/{ticker}")
def train_stock_model(ticker: str):
    """
    Empirically evaluate with purged chronological walk-forward CV, train XGBoost model,
    and persist the model artifact to disk.
    """
    ticker_clean = ticker.upper().strip()
    try:
        train_result = recommendation_engine.train_and_save_model(ticker_clean)
        return train_result
    except Exception as e:
        logger.error(f"Error training model for {ticker_clean}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train-all")
def train_all_models():
    """
    Batch train and evaluate models for all target universe stocks.
    """
    results = {}
    for ticker in settings.TARGET_STOCKS:
        try:
            res = recommendation_engine.train_and_save_model(ticker)
            results[ticker] = res
        except Exception as e:
            logger.error(f"Failed training for {ticker}: {str(e)}")
            results[ticker] = {"error": str(e)}
    return results

import time

_universe_recs_cache = {"timestamp": 0, "data": {}}
CACHE_TTL_SECONDS = 300  # 5 minutes

@router.get("/universe/recommendations")
def get_universe_recommendations(limit: int = Query(150, ge=1, le=150), refresh: bool = False):
    """
    Retrieve recommendations for the entire target universe with in-memory caching.
    """
    now = time.time()
    if not refresh and (now - _universe_recs_cache["timestamp"] < CACHE_TTL_SECONDS) and _universe_recs_cache["data"]:
        cached = _universe_recs_cache["data"]
        selected_keys = list(cached.keys())[:limit]
        return {k: cached[k] for k in selected_keys}

    recs = {}
    target_list = settings.TARGET_STOCKS[:limit]
    for ticker in target_list:
        try:
            # Use fast batch mode (skip per-ticker Finviz scrape for mass universe)
            recs[ticker] = recommendation_engine.predict_next_session(ticker, skip_sentiment=True)
        except Exception as e:
            logger.error(f"Failed inference for {ticker}: {str(e)}")
            recs[ticker] = {
                "ticker": ticker,
                "prediction": "HOLD",
                "confidence": 0.50,
                "probabilities": {"BUY": 0.25, "HOLD": 0.50, "WAIT": 0.25},
                "error": str(e)
            }
    _universe_recs_cache["timestamp"] = now
    _universe_recs_cache["data"] = recs
    return recs
