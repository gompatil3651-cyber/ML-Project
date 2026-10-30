import logging
from typing import List, Dict
from fastapi import APIRouter, HTTPException, Query
from ..config import settings
from ..services.technical import technical_pipeline

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/technicals", tags=["Technical Indicators"])

@router.get("/{ticker}")
def get_latest_technicals(ticker: str):
    """
    Get latest OHLCV and computed technical indicators (SMA, EMA, RSI, Volatility, Momentum).
    """
    ticker_clean = ticker.upper().strip()
    try:
        indicators = technical_pipeline.get_latest_indicators(ticker_clean)
        return indicators
    except Exception as e:
        logger.error(f"Error fetching technicals for {ticker_clean}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{ticker}")
def get_historical_technicals(
    ticker: str,
    period: str = Query("1y", pattern="^(1mo|3mo|6mo|1y|2y|5y)$")
):
    """
    Returns historical price candles and computed indicators for charting.
    """
    ticker_clean = ticker.upper().strip()
    try:
        df = technical_pipeline.fetch_historical_data(ticker_clean, period=period)
        df_indicators = technical_pipeline.calculate_technical_indicators(df)
        
        # Convert date to string for JSON serialization
        if 'Date' in df_indicators.columns:
            df_indicators['Date'] = df_indicators['Date'].astype(str)

        records = df_indicators.to_dict(orient="records")
        return {
            "ticker": ticker_clean,
            "period": period,
            "count": len(records),
            "data": records
        }
    except Exception as e:
        logger.error(f"Error fetching historical technicals for {ticker_clean}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

import time

_universe_tech_cache = {"timestamp": 0, "data": {}}
CACHE_TTL_SECONDS = 300  # 5 minutes

@router.get("/universe/snapshot")
def get_universe_technicals(limit: int = Query(150, ge=1, le=150), refresh: bool = False):
    """
    Returns latest technical indicators for target stocks with TTL caching.
    """
    now = time.time()
    if not refresh and (now - _universe_tech_cache["timestamp"] < CACHE_TTL_SECONDS) and _universe_tech_cache["data"]:
        cached = _universe_tech_cache["data"]
        selected_keys = list(cached.keys())[:limit]
        return {k: cached[k] for k in selected_keys}

    snapshot = {}
    target_list = settings.TARGET_STOCKS[:limit]
    for ticker in target_list:
        try:
            snapshot[ticker] = technical_pipeline.get_latest_indicators(ticker)
        except Exception as e:
            logger.error(f"Error generating snapshot for {ticker}: {str(e)}")
    _universe_tech_cache["timestamp"] = now
    _universe_tech_cache["data"] = snapshot
    return snapshot
