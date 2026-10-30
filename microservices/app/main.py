import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import news, technicals, predictions

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("stock_insight_microservice")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Stock Insight ML & Data Microservice: Finviz Scraping, FinBERT Sentiment NLP, Technical Indicators, and XGBoost Recommendations."
)

# Enable CORS for Streamlit and Node.js backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(news.router)
app.include_router(technicals.router)
app.include_router(predictions.router)

@app.get("/", tags=["General"])
async def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "target_universe": settings.TARGET_STOCKS,
        "documentation": "/docs",
        "status": "healthy"
    }

@app.get("/health", tags=["General"])
async def health_check():
    return {
        "status": "UP",
        "timestamp": datetime.utcnow().isoformat(),
        "stocks_supported": settings.TARGET_STOCKS,
        "nlp_model": settings.FINBERT_MODEL_NAME
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
