import logging
from typing import Dict, List, Tuple
import pandas as pd
from datetime import datetime
import config
from technical_analysis import TechnicalAnalyzer
from fundamental_analysis import FundamentalAnalyzer
from database import StockDatabase
from data_fetcher import DataFetcher

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class ScoringEngine:
    """Score stocks and generate buy/sell recommendations"""

    def __init__(self, db: StockDatabase = None):
        self.db = db or StockDatabase()
        self.technical_analyzer = TechnicalAnalyzer()
        self.fundamental_analyzer = FundamentalAnalyzer()
        self.data_fetcher = DataFetcher()

        self.technical_weight = config.TECHNICAL_WEIGHT
        self.fundamental_weight = config.FUNDAMENTAL_WEIGHT

    def score_stock(self, symbol: str, price_data: pd.DataFrame = None,
                   fundamental_data: Dict = None) -> Dict:
        """
        Score a single stock combining technical and fundamental analysis

        Args:
            symbol: Stock ticker symbol
            price_data: DataFrame with price data (optional, will fetch if not provided)
            fundamental_data: Dict with fundamental data (optional)

        Returns:
            Dictionary with overall score and recommendation
        """
        logger.info(f"Scoring {symbol}")

        # Fetch data if not provided
        if price_data is None or price_data.empty:
            price_data = self.data_fetcher.fetch_price_data(symbol)

        if price_data is None or price_data.empty:
            logger.warning(f"No price data available for {symbol}")
            return self._create_error_result(symbol, "No price data available")

        if fundamental_data is None:
            fundamental_data = self.data_fetcher.fetch_fundamental_data(symbol)

        # Calculate technical indicators
        price_data_with_indicators = self.technical_analyzer.calculate_all_indicators(
            price_data)

        # Generate technical analysis
        technical_result = self.technical_analyzer.generate_technical_signals(
            price_data_with_indicators)

        # Generate fundamental analysis
        fundamental_result = self.fundamental_analyzer.analyze_fundamentals(
            fundamental_data or {})

        # Calculate combined score
        technical_score = technical_result['score']
        fundamental_score = fundamental_result['score']

        overall_score = (
            technical_score * self.technical_weight +
            fundamental_score * self.fundamental_weight
        )

        # Generate recommendation
        recommendation = self._generate_recommendation(overall_score)

        # Combine reasoning
        combined_reasoning = self._combine_reasoning(
            technical_result['reasoning'],
            fundamental_result['reasoning'],
            technical_score,
            fundamental_score
        )

        # Get current price
        current_price = technical_result.get('current_price')
        if current_price is None:
            current_price = price_data['Close'].iloc[-1]

        result = {
            'symbol': symbol,
            'overall_score': round(overall_score, 2),
            'technical_score': technical_score,
            'fundamental_score': fundamental_score,
            'recommendation': recommendation,
            'reasoning': combined_reasoning,
            'current_price': current_price,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'technical_signals': technical_result.get('signals', {}),
            'fundamental_signals': fundamental_result.get('signals', {}),
            'latest_indicators': technical_result.get('latest_indicators', {}),
            'fundamental_metrics': fundamental_result.get('metrics', {})
        }

        logger.info(
            f"{symbol}: Score={overall_score:.1f}, Recommendation={recommendation}")

        return result

    def score_portfolio(self, symbols: List[str]) -> List[Dict]:
        """
        Score multiple stocks and return sorted results

        Args:
            symbols: List of stock ticker symbols

        Returns:
            List of dictionaries with scores, sorted by overall_score descending
        """
        logger.info(f"Scoring portfolio of {len(symbols)} stocks")

        results = []

        for symbol in symbols:
            try:
                result = self.score_stock(symbol)
                results.append(result)
            except Exception as e:
                logger.error(f"Error scoring {symbol}: {e}")
                results.append(self._create_error_result(symbol, str(e)))

        # Sort by overall score descending
        results.sort(key=lambda x: x.get('overall_score', 0), reverse=True)

        return results

    def get_buy_recommendations(self, symbols: List[str], top_n: int = 5) -> List[Dict]:
        """
        Get top buy recommendations

        Args:
            symbols: List of stock ticker symbols
            top_n: Number of top recommendations to return

        Returns:
            List of top N buy recommendations
        """
        all_scores = self.score_portfolio(symbols)

        # Filter for buy recommendations
        buy_candidates = [
            s for s in all_scores
            if s.get('recommendation') in ['STRONG BUY', 'BUY']
            and s.get('overall_score', 0) >= config.MIN_BUY_SCORE
        ]

        return buy_candidates[:top_n]

    def get_sell_recommendations(self, holdings: List[str]) -> List[Dict]:
        """
        Get sell recommendations for current holdings

        Args:
            holdings: List of stock symbols currently held

        Returns:
            List of stocks to consider selling
        """
        all_scores = self.score_portfolio(holdings)

        # Filter for sell recommendations
        sell_candidates = [
            s for s in all_scores
            if s.get('recommendation') in ['SELL', 'STRONG SELL']
            or s.get('overall_score', 100) <= config.MAX_SELL_SCORE
        ]

        return sell_candidates

    def save_recommendations_to_db(self, recommendations: List[Dict]):
        """Save recommendations to database"""
        for rec in recommendations:
            try:
                self.db.insert_recommendation(
                    symbol=rec['symbol'],
                    date=rec['date'],
                    recommendation=rec['recommendation'],
                    score=rec['overall_score'],
                    technical_score=rec['technical_score'],
                    fundamental_score=rec['fundamental_score'],
                    reasoning=rec['reasoning'],
                    price=rec['current_price']
                )
            except Exception as e:
                logger.error(f"Error saving recommendation for {rec['symbol']}: {e}")

    def _generate_recommendation(self, score: float) -> str:
        """Generate recommendation based on score"""
        if score >= 80:
            return "STRONG BUY"
        elif score >= 65:
            return "BUY"
        elif score >= 45:
            return "HOLD"
        elif score >= 30:
            return "SELL"
        else:
            return "STRONG SELL"

    def _combine_reasoning(self, technical_reasoning: str,
                          fundamental_reasoning: str,
                          technical_score: float,
                          fundamental_score: float) -> str:
        """Combine technical and fundamental reasoning"""
        parts = []

        parts.append(f"Technical ({technical_score:.1f}/100): {technical_reasoning}")
        parts.append(f"Fundamental ({fundamental_score:.1f}/100): {fundamental_reasoning}")

        return " || ".join(parts)

    def _create_error_result(self, symbol: str, error_message: str) -> Dict:
        """Create error result for failed analysis"""
        return {
            'symbol': symbol,
            'overall_score': 50,
            'technical_score': 50,
            'fundamental_score': 50,
            'recommendation': 'HOLD',
            'reasoning': f"Error: {error_message}",
            'current_price': None,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'error': error_message
        }

    def analyze_stock_details(self, symbol: str) -> Dict:
        """
        Get detailed analysis for a single stock including charts data

        Returns:
            Dictionary with comprehensive analysis and chart-ready data
        """
        # Get price data
        price_data = self.data_fetcher.fetch_price_data(symbol, period="6mo")

        if price_data is None or price_data.empty:
            return {'error': f'No data available for {symbol}'}

        # Get fundamental data
        fundamental_data = self.data_fetcher.fetch_fundamental_data(symbol)

        # Calculate indicators
        price_data_with_indicators = self.technical_analyzer.calculate_all_indicators(
            price_data)

        # Get full analysis
        analysis = self.score_stock(symbol, price_data, fundamental_data)

        # Add chart data - only include columns that exist
        available_cols = ['Close', 'Volume']
        optional_cols = ['rsi', 'macd', 'macd_signal', 'sma_20', 'sma_50', 'sma_200',
                        'bb_upper', 'bb_lower', 'bb_middle']

        for col in optional_cols:
            if col in price_data_with_indicators.columns:
                available_cols.append(col)

        chart_data = price_data_with_indicators[available_cols].copy()

        analysis['chart_data'] = chart_data
        analysis['price_data'] = price_data_with_indicators

        # Get valuation category
        if fundamental_data:
            analysis['valuation_category'] = (
                self.fundamental_analyzer.get_valuation_category(fundamental_data)
            )
            analysis['quality_score'] = (
                self.fundamental_analyzer.get_quality_score(fundamental_data)
            )

        return analysis


def run_daily_analysis(symbols: List[str] = None, save_to_db: bool = True):
    """
    Run daily analysis for all stocks in universe

    Args:
        symbols: List of symbols to analyze (defaults to config.STOCK_UNIVERSE)
        save_to_db: Whether to save results to database
    """
    if symbols is None:
        symbols = config.STOCK_UNIVERSE

    logger.info(f"Starting daily analysis for {len(symbols)} stocks")

    # Initialize components
    db = StockDatabase()
    scoring_engine = ScoringEngine(db)
    fetcher = DataFetcher()

    # Update price and fundamental data
    today = datetime.now().strftime('%Y-%m-%d')

    for i, symbol in enumerate(symbols):
        logger.info(f"Processing {symbol} ({i+1}/{len(symbols)})")

        try:
            # Fetch and store price data
            price_data = fetcher.fetch_price_data(symbol)
            if price_data is not None and not price_data.empty:
                db.insert_price_data(symbol, price_data)

                # Calculate and store technical indicators
                indicators = scoring_engine.technical_analyzer.calculate_all_indicators(
                    price_data)

                # Extract indicator columns for database
                indicator_cols = [
                    'rsi', 'macd', 'macd_signal', 'macd_histogram',
                    'sma_20', 'sma_50', 'sma_200',
                    'bb_upper', 'bb_middle', 'bb_lower', 'volume_sma_20'
                ]
                indicator_data = indicators[indicator_cols].copy()
                db.insert_technical_indicators(symbol, indicator_data)

            # Fetch and store fundamental data
            fundamental_data = fetcher.fetch_fundamental_data(symbol)
            if fundamental_data:
                db.insert_fundamental_data(symbol, today, fundamental_data)

        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")

    # Generate recommendations
    logger.info("Generating recommendations")
    buy_recommendations = scoring_engine.get_buy_recommendations(symbols, top_n=10)

    # Get active holdings and check for sells
    active_holdings_df = db.get_active_holdings()
    if not active_holdings_df.empty:
        holding_symbols = active_holdings_df['symbol'].unique().tolist()
        sell_recommendations = scoring_engine.get_sell_recommendations(holding_symbols)
    else:
        sell_recommendations = []

    # Save to database
    if save_to_db:
        scoring_engine.save_recommendations_to_db(buy_recommendations)
        scoring_engine.save_recommendations_to_db(sell_recommendations)

    logger.info(f"Daily analysis complete. {len(buy_recommendations)} buy recommendations, "
               f"{len(sell_recommendations)} sell recommendations")

    return {
        'buy_recommendations': buy_recommendations,
        'sell_recommendations': sell_recommendations,
        'date': today
    }


if __name__ == "__main__":
    # Test scoring engine
    engine = ScoringEngine()

    # Test single stock
    result = engine.score_stock("AAPL")
    print(f"\nAnalysis for AAPL:")
    print(f"Overall Score: {result['overall_score']}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Reasoning: {result['reasoning']}")

    # Test portfolio
    test_symbols = ["AAPL", "MSFT", "GOOGL"]
    results = engine.score_portfolio(test_symbols)
    print(f"\nPortfolio Analysis:")
    for r in results:
        print(f"{r['symbol']}: {r['overall_score']:.1f} - {r['recommendation']}")
