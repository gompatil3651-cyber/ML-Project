import logging
from typing import List, Dict
from fastapi import APIRouter, HTTPException, Query
from ..config import settings
from ..models.schemas import (
    DailySentimentAggregate,
    SentimentBatchRequest,
    NewsArticleSentiment
)
from ..services.scraper import finviz_scraper
from ..services.sentiment import finbert_analyzer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/news", tags=["News & Sentiment"])

@router.get("/scrape/{ticker}", response_model=List[Dict])
def scrape_news(ticker: str, limit: int = Query(25, ge=1, le=100)):
    """
    Scrape recent financial news headlines for a ticker from Finviz.
    """
    ticker_clean = ticker.upper().strip()
    articles = finviz_scraper.scrape_ticker_news(ticker=ticker_clean, max_articles=limit)
    if not articles:
        raise HTTPException(status_code=404, detail=f"No news articles found for ticker {ticker_clean}")
    return articles

@router.post("/sentiment", response_model=List[NewsArticleSentiment])
def analyze_custom_headlines(payload: SentimentBatchRequest):
    """
    Evaluate sentiment using ProsusAI/finbert for a batch of provided headlines.
    """
    items = [{"headline": hl, "published_at": None, "url": None} for hl in payload.headlines]
    return finbert_analyzer.analyze_headlines(items)

@router.get("/analyze/{ticker}", response_model=DailySentimentAggregate)
def analyze_ticker_news(ticker: str, limit: int = Query(25, ge=1, le=100)):
    """
    End-to-end NLP pipeline: Scrapes Finviz news for the ticker, scores them with FinBERT,
    and returns article-level sentiment and aggregated daily metrics (Sentiment_Score, News_Count).
    """
    ticker_clean = ticker.upper().strip()
    raw_articles = finviz_scraper.scrape_ticker_news(ticker=ticker_clean, max_articles=limit)
    scored_articles = finbert_analyzer.analyze_headlines(raw_articles)
    aggregated = finbert_analyzer.aggregate_sentiment(ticker=ticker_clean, articles=scored_articles)
    return aggregated

import time

_universe_news_cache = {"timestamp": 0, "data": {}}
CACHE_TTL_SECONDS = 300  # 5 minutes

@router.get("/universe", response_model=Dict[str, DailySentimentAggregate])
def analyze_universe(limit: int = Query(15, ge=1, le=50), max_stocks: int = Query(150, ge=1, le=150), refresh: bool = False):
    """
    Runs sentiment analysis across target universe stocks with TTL caching.
    """
    now = time.time()
    if not refresh and (now - _universe_news_cache["timestamp"] < CACHE_TTL_SECONDS) and _universe_news_cache["data"]:
        cached = _universe_news_cache["data"]
        selected_keys = list(cached.keys())[:max_stocks]
        return {k: cached[k] for k in selected_keys}

    universe_results = {}
    target_list = settings.TARGET_STOCKS[:max_stocks]
    for ticker in target_list:
        try:
            raw_articles = finviz_scraper.scrape_ticker_news(ticker=ticker, max_articles=limit)
            scored_articles = finbert_analyzer.analyze_headlines(raw_articles)
            aggregated = finbert_analyzer.aggregate_sentiment(ticker=ticker, articles=scored_articles)
            universe_results[ticker] = aggregated
        except Exception as e:
            logger.error(f"Error analyzing universe ticker {ticker}: {str(e)}")
            universe_results[ticker] = finbert_analyzer.aggregate_sentiment(ticker=ticker, articles=[])
    _universe_news_cache["timestamp"] = now
    _universe_news_cache["data"] = universe_results
    return universe_results
