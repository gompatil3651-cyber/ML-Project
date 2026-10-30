from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class NewsItem(BaseModel):
    ticker: str
    headline: str
    url: Optional[str] = None
    source: Optional[str] = "Finviz"
    timestamp_raw: Optional[str] = None
    published_at: Optional[str] = None

class NewsArticleSentiment(BaseModel):
    headline: str
    sentiment: str  # positive, neutral, negative
    positive_prob: float
    neutral_prob: float
    negative_prob: float
    score: float  # continuous score from -1.0 (most negative) to +1.0 (most positive)
    published_at: Optional[str] = None
    url: Optional[str] = None

class DailySentimentAggregate(BaseModel):
    ticker: str
    Sentiment_Score: float = Field(..., description="Daily average compound sentiment score (-1 to +1)")
    News_Count: int = Field(..., description="Total count of articles analyzed")
    positive_count: int
    neutral_count: int
    negative_count: int
    sentiment_label: str  # Bullish, Neutral, Bearish based on score thresholds
    headlines: List[NewsArticleSentiment] = []

class SentimentBatchRequest(BaseModel):
    ticker: str
    headlines: List[str]

class TechnicalIndicators(BaseModel):
    ticker: str
    latest_close: float
    daily_return: float
    return_7d: float
    return_30d: float
    sma_5: float
    sma_10: float
    sma_20: float
    ema_5: float
    ema_10: float
    ema_20: float
    rsi_14: float
    volatility_20: float
    momentum_10: float
    updated_at: str

class RecommendationResponse(BaseModel):
    ticker: str
    prediction: str  # BUY, HOLD, WAIT
    confidence: float
    probabilities: Dict[str, float]
    technical_summary: Optional[Dict[str, float]] = None
    sentiment_summary: Optional[Dict[str, float]] = None
    model_version: str = "xgboost_v1"
