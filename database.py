import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd
from sqlalchemy import create_engine, text
import config

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class StockDatabase:
    """SQLite database manager for stock data"""

    def __init__(self, db_path: str = config.DATABASE_PATH):
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        self._create_tables()

    def _create_tables(self):
        """Create all necessary tables if they don't exist"""
        with self.engine.connect() as conn:
            # Price data table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS price_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    date DATE NOT NULL,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    adj_close REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, date)
                )
            """))

            # Fundamental data table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS fundamental_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    date DATE NOT NULL,
                    pe_ratio REAL,
                    eps REAL,
                    profit_margin REAL,
                    debt_to_equity REAL,
                    revenue_growth REAL,
                    market_cap REAL,
                    dividend_yield REAL,
                    beta REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, date)
                )
            """))

            # Technical indicators table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS technical_indicators (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    date DATE NOT NULL,
                    rsi REAL,
                    macd REAL,
                    macd_signal REAL,
                    macd_histogram REAL,
                    sma_20 REAL,
                    sma_50 REAL,
                    sma_200 REAL,
                    bb_upper REAL,
                    bb_middle REAL,
                    bb_lower REAL,
                    volume_sma_20 REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, date)
                )
            """))

            # Recommendations table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    date DATE NOT NULL,
                    recommendation TEXT NOT NULL,
                    score REAL NOT NULL,
                    technical_score REAL,
                    fundamental_score REAL,
                    reasoning TEXT,
                    price_at_recommendation REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, date)
                )
            """))

            # Holdings table (for tracking positions)
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS holdings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    purchase_date DATE NOT NULL,
                    purchase_price REAL NOT NULL,
                    quantity INTEGER NOT NULL,
                    status TEXT DEFAULT 'ACTIVE',
                    sell_date DATE,
                    sell_price REAL,
                    profit_loss REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

            conn.commit()

        logger.info("Database tables created successfully")

    def insert_price_data(self, symbol: str, df: pd.DataFrame):
        """Insert price data from DataFrame"""
        df = df.copy()
        df['symbol'] = symbol
        df['date'] = df.index
        df = df.reset_index(drop=True)

        # Rename columns to match database schema
        column_mapping = {
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume',
            'Adj Close': 'adj_close'
        }
        df = df.rename(columns=column_mapping)

        # Select only relevant columns
        df = df[['symbol', 'date', 'open', 'high', 'low', 'close', 'volume', 'adj_close']]

        try:
            df.to_sql('price_data', self.engine, if_exists='append', index=False)
            logger.info(f"Inserted {len(df)} price records for {symbol}")
        except Exception as e:
            logger.error(f"Error inserting price data for {symbol}: {e}")

    def insert_fundamental_data(self, symbol: str, date: str, data: Dict):
        """Insert fundamental data"""
        with self.engine.connect() as conn:
            try:
                conn.execute(text("""
                    INSERT OR REPLACE INTO fundamental_data
                    (symbol, date, pe_ratio, eps, profit_margin, debt_to_equity,
                     revenue_growth, market_cap, dividend_yield, beta)
                    VALUES (:symbol, :date, :pe_ratio, :eps, :profit_margin,
                            :debt_to_equity, :revenue_growth, :market_cap,
                            :dividend_yield, :beta)
                """), {
                    'symbol': symbol,
                    'date': date,
                    'pe_ratio': data.get('pe_ratio'),
                    'eps': data.get('eps'),
                    'profit_margin': data.get('profit_margin'),
                    'debt_to_equity': data.get('debt_to_equity'),
                    'revenue_growth': data.get('revenue_growth'),
                    'market_cap': data.get('market_cap'),
                    'dividend_yield': data.get('dividend_yield'),
                    'beta': data.get('beta')
                })
                conn.commit()
                logger.info(f"Inserted fundamental data for {symbol}")
            except Exception as e:
                logger.error(f"Error inserting fundamental data for {symbol}: {e}")

    def insert_technical_indicators(self, symbol: str, df: pd.DataFrame):
        """Insert technical indicators from DataFrame"""
        df = df.copy()
        df['symbol'] = symbol
        df['date'] = df.index
        df = df.reset_index(drop=True)

        try:
            df.to_sql('technical_indicators', self.engine, if_exists='append', index=False)
            logger.info(f"Inserted {len(df)} technical indicator records for {symbol}")
        except Exception as e:
            logger.error(f"Error inserting technical indicators for {symbol}: {e}")

    def insert_recommendation(self, symbol: str, date: str, recommendation: str,
                            score: float, technical_score: float,
                            fundamental_score: float, reasoning: str,
                            price: float):
        """Insert stock recommendation"""
        with self.engine.connect() as conn:
            try:
                conn.execute(text("""
                    INSERT OR REPLACE INTO recommendations
                    (symbol, date, recommendation, score, technical_score,
                     fundamental_score, reasoning, price_at_recommendation)
                    VALUES (:symbol, :date, :recommendation, :score, :technical_score,
                            :fundamental_score, :reasoning, :price)
                """), {
                    'symbol': symbol,
                    'date': date,
                    'recommendation': recommendation,
                    'score': score,
                    'technical_score': technical_score,
                    'fundamental_score': fundamental_score,
                    'reasoning': reasoning,
                    'price': price
                })
                conn.commit()
                logger.info(f"Inserted recommendation for {symbol}: {recommendation}")
            except Exception as e:
                logger.error(f"Error inserting recommendation for {symbol}: {e}")

    def get_price_data(self, symbol: str, limit: int = None) -> pd.DataFrame:
        """Retrieve price data for a symbol"""
        query = f"SELECT * FROM price_data WHERE symbol = '{symbol}' ORDER BY date DESC"
        if limit:
            query += f" LIMIT {limit}"

        df = pd.read_sql(query, self.engine)
        return df

    def get_latest_recommendations(self, recommendation_type: str = None,
                                  limit: int = 10) -> pd.DataFrame:
        """Get latest recommendations, optionally filtered by type"""
        query = """
            SELECT * FROM recommendations
            WHERE date = (SELECT MAX(date) FROM recommendations)
        """
        if recommendation_type:
            query += f" AND recommendation = '{recommendation_type}'"
        query += f" ORDER BY score DESC LIMIT {limit}"

        return pd.read_sql(query, self.engine)

    def get_technical_indicators(self, symbol: str, limit: int = None) -> pd.DataFrame:
        """Retrieve technical indicators for a symbol"""
        query = f"SELECT * FROM technical_indicators WHERE symbol = '{symbol}' ORDER BY date DESC"
        if limit:
            query += f" LIMIT {limit}"

        return pd.read_sql(query, self.engine)

    def get_fundamental_data(self, symbol: str) -> Optional[Dict]:
        """Get latest fundamental data for a symbol"""
        query = f"""
            SELECT * FROM fundamental_data
            WHERE symbol = '{symbol}'
            ORDER BY date DESC LIMIT 1
        """
        df = pd.read_sql(query, self.engine)
        if len(df) > 0:
            return df.iloc[0].to_dict()
        return None

    def add_holding(self, symbol: str, purchase_date: str, purchase_price: float,
                   quantity: int):
        """Add a new holding to track"""
        with self.engine.connect() as conn:
            try:
                conn.execute(text("""
                    INSERT INTO holdings
                    (symbol, purchase_date, purchase_price, quantity, status)
                    VALUES (:symbol, :purchase_date, :purchase_price, :quantity, 'ACTIVE')
                """), {
                    'symbol': symbol,
                    'purchase_date': purchase_date,
                    'purchase_price': purchase_price,
                    'quantity': quantity
                })
                conn.commit()
                logger.info(f"Added holding: {quantity} shares of {symbol} at ${purchase_price}")
            except Exception as e:
                logger.error(f"Error adding holding for {symbol}: {e}")

    def get_active_holdings(self) -> pd.DataFrame:
        """Get all active holdings"""
        query = "SELECT * FROM holdings WHERE status = 'ACTIVE' ORDER BY purchase_date DESC"
        return pd.read_sql(query, self.engine)

    def close_holding(self, holding_id: int, sell_date: str, sell_price: float):
        """Close a holding and record profit/loss"""
        with self.engine.connect() as conn:
            try:
                # Get the holding details
                result = conn.execute(text("""
                    SELECT purchase_price, quantity FROM holdings WHERE id = :id
                """), {'id': holding_id})
                row = result.fetchone()

                if row:
                    purchase_price, quantity = row
                    profit_loss = (sell_price - purchase_price) * quantity

                    conn.execute(text("""
                        UPDATE holdings
                        SET status = 'CLOSED', sell_date = :sell_date,
                            sell_price = :sell_price, profit_loss = :profit_loss
                        WHERE id = :id
                    """), {
                        'id': holding_id,
                        'sell_date': sell_date,
                        'sell_price': sell_price,
                        'profit_loss': profit_loss
                    })
                    conn.commit()
                    logger.info(f"Closed holding {holding_id} with P/L: ${profit_loss:.2f}")
            except Exception as e:
                logger.error(f"Error closing holding {holding_id}: {e}")

    def clear_old_data(self, days: int = 365):
        """Clear data older than specified days"""
        with self.engine.connect() as conn:
            try:
                cutoff_date = datetime.now().date()
                # Implementation would depend on specific requirements
                logger.info(f"Data cleanup for entries older than {days} days")
            except Exception as e:
                logger.error(f"Error during data cleanup: {e}")


if __name__ == "__main__":
    # Test database creation
    db = StockDatabase()
    print("Database initialized successfully")
