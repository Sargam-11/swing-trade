import yfinance as yf
import requests
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
import pandas as pd
import config

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class DataFetcher:
    """Fetch stock data from yfinance and Alpha Vantage"""

    def __init__(self, alpha_vantage_key: str = None):
        self.alpha_vantage_key = alpha_vantage_key or config.ALPHA_VANTAGE_API_KEY
        self.base_url = "https://www.alphavantage.co/query"

    def fetch_price_data(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """
        Fetch historical price data from yfinance

        Args:
            symbol: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

        Returns:
            DataFrame with OHLCV data
        """
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(period=period)

            if df.empty:
                logger.warning(f"No price data found for {symbol}")
                return None

            logger.info(f"Fetched {len(df)} price records for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Error fetching price data for {symbol}: {e}")
            return None

    def fetch_fundamental_data(self, symbol: str) -> Optional[Dict]:
        """
        Fetch fundamental data from yfinance

        Returns:
            Dictionary with fundamental metrics
        """
        try:
            stock = yf.Ticker(symbol)
            info = stock.info

            # Extract key fundamental metrics
            fundamentals = {
                'pe_ratio': info.get('trailingPE') or info.get('forwardPE'),
                'eps': info.get('trailingEps'),
                'profit_margin': info.get('profitMargins'),
                'debt_to_equity': info.get('debtToEquity'),
                'revenue_growth': info.get('revenueGrowth'),
                'market_cap': info.get('marketCap'),
                'dividend_yield': info.get('dividendYield'),
                'beta': info.get('beta'),
                'current_price': info.get('currentPrice') or info.get('regularMarketPrice'),
                'book_value': info.get('bookValue'),
                'price_to_book': info.get('priceToBook'),
                'return_on_equity': info.get('returnOnEquity'),
                'return_on_assets': info.get('returnOnAssets'),
                'operating_margin': info.get('operatingMargins'),
                'current_ratio': info.get('currentRatio'),
                'quick_ratio': info.get('quickRatio'),
                'earnings_growth': info.get('earningsGrowth')
            }

            # Clean None values
            fundamentals = {k: v for k, v in fundamentals.items() if v is not None}

            logger.info(f"Fetched fundamental data for {symbol}")
            return fundamentals

        except Exception as e:
            logger.error(f"Error fetching fundamental data for {symbol}: {e}")
            return None

    def fetch_company_overview_av(self, symbol: str) -> Optional[Dict]:
        """
        Fetch company overview from Alpha Vantage
        Note: Limited to 25 calls per day on free tier

        Returns:
            Dictionary with company data
        """
        if not self.alpha_vantage_key:
            logger.warning("Alpha Vantage API key not configured")
            return None

        try:
            params = {
                'function': 'OVERVIEW',
                'symbol': symbol,
                'apikey': self.alpha_vantage_key
            }

            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            if 'Symbol' not in data:
                logger.warning(f"No overview data found for {symbol}")
                return None

            # Convert relevant fields to proper types
            overview = {
                'pe_ratio': self._safe_float(data.get('PERatio')),
                'eps': self._safe_float(data.get('EPS')),
                'profit_margin': self._safe_float(data.get('ProfitMargin')),
                'debt_to_equity': self._safe_float(data.get('DebtToEquity')),
                'revenue_growth': self._safe_float(data.get('QuarterlyRevenueGrowthYOY')),
                'market_cap': self._safe_float(data.get('MarketCapitalization')),
                'dividend_yield': self._safe_float(data.get('DividendYield')),
                'beta': self._safe_float(data.get('Beta')),
                'book_value': self._safe_float(data.get('BookValue')),
                'price_to_book': self._safe_float(data.get('PriceToBookRatio')),
                'return_on_equity': self._safe_float(data.get('ReturnOnEquityTTM')),
                'return_on_assets': self._safe_float(data.get('ReturnOnAssetsTTM')),
                'operating_margin': self._safe_float(data.get('OperatingMarginTTM')),
                'earnings_growth': self._safe_float(data.get('QuarterlyEarningsGrowthYOY'))
            }

            # Clean None values
            overview = {k: v for k, v in overview.items() if v is not None}

            logger.info(f"Fetched Alpha Vantage overview for {symbol}")
            return overview

        except Exception as e:
            logger.error(f"Error fetching Alpha Vantage data for {symbol}: {e}")
            return None

    def fetch_all_stock_data(self, symbol: str, use_alpha_vantage: bool = False) -> Dict:
        """
        Fetch both price and fundamental data for a stock

        Args:
            symbol: Stock ticker symbol
            use_alpha_vantage: Whether to use Alpha Vantage for fundamentals

        Returns:
            Dictionary with price_data and fundamental_data
        """
        logger.info(f"Fetching all data for {symbol}")

        # Fetch price data from yfinance
        price_data = self.fetch_price_data(symbol)

        # Fetch fundamental data
        if use_alpha_vantage:
            fundamental_data = self.fetch_company_overview_av(symbol)
            time.sleep(12)  # Rate limiting: 5 calls/minute for Alpha Vantage
        else:
            fundamental_data = self.fetch_fundamental_data(symbol)

        return {
            'price_data': price_data,
            'fundamental_data': fundamental_data
        }

    def fetch_multiple_stocks(self, symbols: list, use_alpha_vantage: bool = False,
                            delay: float = 1.0) -> Dict:
        """
        Fetch data for multiple stocks with rate limiting

        Args:
            symbols: List of stock ticker symbols
            use_alpha_vantage: Whether to use Alpha Vantage
            delay: Delay between requests in seconds

        Returns:
            Dictionary mapping symbols to their data
        """
        all_data = {}

        for i, symbol in enumerate(symbols):
            logger.info(f"Processing {symbol} ({i+1}/{len(symbols)})")

            try:
                all_data[symbol] = self.fetch_all_stock_data(symbol, use_alpha_vantage)

                # Rate limiting
                if i < len(symbols) - 1:
                    time.sleep(delay)

            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                all_data[symbol] = {'price_data': None, 'fundamental_data': None}

        return all_data

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current market price for a symbol"""
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period='1d')
            if not data.empty:
                return float(data['Close'].iloc[-1])
            return None
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            return None

    @staticmethod
    def _safe_float(value) -> Optional[float]:
        """Safely convert value to float"""
        if value is None or value == 'None' or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None


def update_database_for_symbols(symbols: list, db, use_alpha_vantage: bool = False):
    """
    Fetch and store data for multiple symbols

    Args:
        symbols: List of stock symbols
        db: Database instance
        use_alpha_vantage: Whether to use Alpha Vantage API
    """
    fetcher = DataFetcher()
    today = datetime.now().strftime('%Y-%m-%d')

    logger.info(f"Starting data update for {len(symbols)} symbols")

    for i, symbol in enumerate(symbols):
        logger.info(f"Updating {symbol} ({i+1}/{len(symbols)})")

        try:
            # Fetch price data
            price_data = fetcher.fetch_price_data(symbol)
            if price_data is not None and not price_data.empty:
                db.insert_price_data(symbol, price_data)

            # Fetch fundamental data
            if use_alpha_vantage and i < 25:  # Alpha Vantage daily limit
                fundamental_data = fetcher.fetch_company_overview_av(symbol)
                time.sleep(12)  # Rate limiting
            else:
                fundamental_data = fetcher.fetch_fundamental_data(symbol)

            if fundamental_data:
                db.insert_fundamental_data(symbol, today, fundamental_data)

            # Small delay between stocks
            time.sleep(1)

        except Exception as e:
            logger.error(f"Error updating {symbol}: {e}")

    logger.info("Data update completed")


if __name__ == "__main__":
    # Test data fetcher
    fetcher = DataFetcher()

    # Test with one stock
    test_symbol = "AAPL"
    data = fetcher.fetch_all_stock_data(test_symbol)

    print(f"\nPrice Data for {test_symbol}:")
    if data['price_data'] is not None:
        print(data['price_data'].tail())

    print(f"\nFundamental Data for {test_symbol}:")
    print(data['fundamental_data'])
