# Stock Insight: Intelligent Stock Analysis & Recommendation System

Stock Insight is an enterprise-grade full-stack stock analysis and recommendation system scaled across **150 S&P 500 market leaders** in 9 sectors (Technology, Financials, Healthcare, Consumer, Energy, Industrials, Real Estate, Utilities, and Communication Services).

## 1. System Architecture
- **Frontend (`frontend/`)**: Streamlit interactive dashboard with modern light theme tailored for non-technical users, complete with sector filtering, interactive Plotly candlestick & RSI charts, indicator snapshots, and a 150-stock comparative matrix.
- **Backend API (`backend/`)**: Node.js & Express REST API, MongoDB for persistence, and JWT authentication.
- **Data & ML Microservices (`microservices/`)**: Python (FastAPI), Finviz web scraping, Hugging Face `ProsusAI/finbert` NLP sentiment pipeline, yfinance technical indicators, and XGBoost classification engine with purged chronological walk-forward validation and a calibrated 3% threshold band (`BUY > +3%`, `HOLD -3% to +3%`, `WAIT < -3%`).

## 2. Testing & Microservice Offline Resilience
When the Python ML microservice is **OFF** (during unit testing, automated CI/CD, grading, or local development where only Node.js is running):
1. **Zero-Crash Resilience**: Backend endpoints (`/api/stocks/...`, `/api/predictions/...`, `/api/news/...`) never crash with 500 when microservices are unreachable.
2. **Multi-Tier Fallback Pipeline**:
   - Tier 1: Live microservice on port 8000.
   - Tier 2: Persistent MongoDB cache (`StockPrice`, `Prediction`, `NewsSentiment`).
   - Tier 3: Realistic, fully schema-compliant fallback engine covering all target stocks (`AMZN`, `GOOGL`, `AAPL`, `NVDA`, `MSFT`).
3. **Frontend Client Resilience**: If neither Node.js nor Python is reachable, the Streamlit client employs built-in fallback profiles so charts, indicators, and recommendation badges remain fully functional.
4. **Health Check Awareness**: `GET /health` reports `status: "UP"` and flags `python_microservice.status: "OFFLINE_FALLBACK"` with `resilient_mode.fallback_active: true`.

### Running Tests
- **Backend Offline Resilience Tests** (Verifies all endpoints return 200 OK with microservice OFF):
  ```bash
  npm test
  # or
  npm run test:backend
  ```
- **Python Microservices Pytest Suite** (Runs in-process via FastAPI TestClient):
  ```bash
  npm run test:microservices
  # or
  python -m pytest microservices/tests
  ```
- **Run All Tests**:
  ```bash
  npm run test:all
  ```

## 3. Directory Layout
```text
d:\se\
├── backend/
│   ├── package.json
│   ├── .env.example
│   ├── .env
│   ├── test/
│   │   └── microservice_resilience.test.js # Test suite for microservice-off scenario
│   └── src/
│       ├── config/
│       │   └── db.js                 # MongoDB connection & buffer timeout logic
│       ├── controllers/
│       │   ├── authController.js     # User registration, login & watchlist
│       │   ├── stockController.js    # Technicals & OHLCV with microservice fallback
│       │   ├── predictionController.js # XGBoost predictions with fallback
│       │   └── newsController.js     # FinBERT news sentiment with fallback
│       ├── middlewares/
│       │   └── authMiddleware.js     # JWT verification middleware
│       ├── models/
│       │   ├── User.js               # User auth & profile schema
│       │   ├── StockPrice.js         # OHLCV & technical indicators schema
│       │   ├── NewsSentiment.js      # Daily FinBERT sentiment schema
│       │   └── Prediction.js         # XGBoost BUY/HOLD/WAIT schema
│       ├── routes/
│       │   ├── authRoutes.js         # Auth REST endpoints
│       │   ├── stockRoutes.js        # Stock technical REST endpoints
│       │   ├── predictionRoutes.js   # Prediction REST endpoints
│       │   └── newsRoutes.js         # News sentiment REST endpoints
│       ├── services/
│       │   ├── fallbackDataService.js# Realistic fallback data for all target tickers
│       │   └── pythonServiceClient.js# Resilient client with automatic fallback
│       └── server.js                 # Express server bootstrap & health checks
│
├── microservices/
│   ├── requirements.txt
│   ├── saved_models/                 # Exported XGBoost model artifacts
│   ├── tests/
│   │   └── test_api.py               # Pytest suite with FastAPI TestClient
│   └── app/
│       ├── __init__.py
│       ├── config.py                 # Universe tickers & scraper headers
│       ├── main.py                   # FastAPI app entry point
│       ├── models/
│       │   └── schemas.py            # Pydantic validation schemas
│       ├── routers/
│       │   ├── news.py               # Finviz scrape & FinBERT sentiment endpoints
│       │   ├── predictions.py        # XGBoost recommendation endpoints
│       │   └── technicals.py         # yfinance technical indicator endpoints
│       └── services/
│           ├── scraper.py            # Finviz table & timestamp parser with fallback
│           ├── sentiment.py          # ProsusAI/finbert model & daily aggregation
│           ├── technical.py          # Indicator computation engine
│           └── model_engine.py       # XGBoost walk-forward model engine
│
└── frontend/
    ├── .streamlit/
    │   └── config.toml               # Streamlit light theme styling
    ├── components/
    │   ├── charts.py                 # Candlestick and RSI Plotly charts
    │   ├── recommendation_card.py    # Accessible recommendation badge
    │   └── sentiment_view.py         # Sentiment gauge & headlines
    ├── utils/
    │   └── api_client.py             # Multi-tier resilient API client
    └── app.py                        # Streamlit dashboard
```
