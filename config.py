import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

# Stock Universe (20 stocks to start)
STOCK_UNIVERSE = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',
    'NVDA', 'TSLA', 'JPM', 'V', 'WMT',
    'JNJ', 'PG', 'MA', 'HD', 'DIS',
    'BAC', 'XOM', 'ABBV', 'PFE', 'KO'
]

# Technical Analysis Parameters
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
SMA_SHORT = 20
SMA_MEDIUM = 50
SMA_LONG = 200
VOLUME_SPIKE_THRESHOLD = 1.5

# Bollinger Bands
BB_PERIOD = 20
BB_STD = 2

# Scoring Weights
TECHNICAL_WEIGHT = 0.6
FUNDAMENTAL_WEIGHT = 0.4

# Minimum score to recommend
MIN_BUY_SCORE = 60
MAX_SELL_SCORE = 40

# Database
DATABASE_PATH = 'data/stocks.db'

# Data fetch settings
HISTORICAL_DAYS = 365  # Fetch 1 year of historical data
API_RETRY_ATTEMPTS = 3
API_RETRY_DELAY = 5  # seconds

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'data/analyzer.log'
