import os
from typing import List
from pydantic import BaseModel
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

TICKERS: List[str] = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'AVGO', 'ORCL', 'CRM', 'AMD',
    'ADBE', 'CSCO', 'IBM', 'QCOM', 'TXN', 'INTU', 'AMAT', 'MU', 'LRCX', 'NOW',
    'PANW', 'SNPS', 'CDNS', 'ADI', 'KLAC', 'ANET', 'APH', 'MSI', 'FTNT', 'PLTR',
    'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'BLK', 'SCHW', 'USB',
    'PNC', 'TFC', 'COF', 'CB', 'CME', 'ICE', 'SPGI', 'MCO', 'AON', 'MMC',
    'LLY', 'JNJ', 'ABBV', 'MRK', 'PFE', 'ABT', 'TMO', 'DHR', 'AMGN', 'GILD',
    'ISRG', 'VRTX', 'REGN', 'BSX', 'SYK', 'MDT', 'ELV', 'CI', 'HCA', 'ZTS',
    'WMT', 'COST', 'HD', 'LOW', 'MCD', 'NKE', 'TJX', 'SBUX', 'TGT', 'BKNG',
    'MAR', 'CMG', 'ORLY', 'AZO', 'ROST', 'YUM', 'CL', 'PG', 'KO', 'PEP',
    'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PSX', 'VLO', 'OXY', 'FANG', 'KMI',
    'CAT', 'DE', 'GE', 'HON', 'ETN', 'PH', 'EMR', 'UPS', 'UNP', 'RTX',
    'LMT', 'NOC', 'GD', 'WM', 'CSX', 'NSC', 'FDX', 'MMM', 'ITW', 'CARR',
    'AMT', 'PLD', 'EQIX', 'PSA', 'SPG', 'O', 'CCI', 'DLR', 'WELL', 'AVB',
    'NEE', 'CEG', 'SO', 'DUK', 'AEP', 'SRE', 'VST', 'EXC', 'D', 'PEG',
    'TMUS', 'VZ', 'T', 'CMCSA', 'CHTR', 'DIS', 'NFLX', 'FOXA', 'EA', 'TTWO'
]

class Settings(BaseModel):
    APP_NAME: str = "Stock Insight Data & ML Microservice"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    HOST: str = os.getenv("MICROSERVICE_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("MICROSERVICE_PORT", "8000"))
    
    # Target Stock Universe (Scaled to 150 S&P Market Leaders)
    TARGET_STOCKS: List[str] = TICKERS
    
    # Web Scraping Configuration
    FINVIZ_BASE_URL: str = "https://finviz.com/quote.ashx?t="
    SCRAPER_USER_AGENT: str = os.getenv(
        "SCRAPER_USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    REQUEST_TIMEOUT_SECONDS: int = 15

    # FinBERT Model Configuration
    FINBERT_MODEL_NAME: str = "ProsusAI/finbert"
    BATCH_SIZE: int = 16

    # Model & Recommendation Thresholds
    RECOMMENDATION_THRESHOLD: float = float(os.getenv("RECOMMENDATION_THRESHOLD", "0.03"))  # 3% threshold band
    SAVED_MODELS_DIR: str = os.path.join(os.path.dirname(__file__), "..", "saved_models")

settings = Settings()
