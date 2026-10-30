import pytest
from starlette.testclient import TestClient
from microservices.app.main import app
from microservices.app.config import settings

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == settings.APP_NAME
    assert data["status"] == "healthy"

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert "NVDA" in data["stocks_supported"]

def test_technicals_endpoint(client):
    response = client.get("/api/technicals/NVDA")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "NVDA"
    assert "latest_close" in data
    assert "rsi_14" in data
    assert "sma_20" in data
    assert "ema_20" in data

def test_historical_candles_endpoint(client):
    response = client.get("/api/technicals/history/AAPL?period=1mo")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert data["period"] == "1mo"
    assert "data" in data
    assert len(data["data"]) > 0

def test_universe_technicals_snapshot(client):
    response = client.get("/api/technicals/universe/snapshot?limit=15")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5
    for ticker in list(data.keys()):
        assert "latest_close" in data[ticker]

def test_predictions_endpoint(client):
    response = client.get("/api/predictions/MSFT")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "MSFT"
    assert data["prediction"] in ["BUY", "HOLD", "WAIT"]
    assert 0.0 <= data["confidence"] <= 1.0
    assert "BUY" in data["probabilities"]
    assert "HOLD" in data["probabilities"]
    assert "WAIT" in data["probabilities"]

def test_news_scraping_and_fallback(client):
    response = client.get("/api/news/scrape/AMZN?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "headline" in data[0]

def test_news_analysis_pipeline(client):
    response = client.get("/api/news/analyze/GOOGL?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "GOOGL"
    assert "Sentiment_Score" in data
    assert "sentiment_label" in data
    assert data["sentiment_label"] in ["Bullish", "Neutral", "Bearish"]

