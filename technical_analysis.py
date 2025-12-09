import pandas as pd
import pandas_ta as ta
import logging
from typing import Dict, Tuple
import config

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class TechnicalAnalyzer:
    """Calculate technical indicators and generate signals"""

    def __init__(self):
        self.rsi_period = config.RSI_PERIOD
        self.rsi_oversold = config.RSI_OVERSOLD
        self.rsi_overbought = config.RSI_OVERBOUGHT
        self.macd_fast = config.MACD_FAST
        self.macd_slow = config.MACD_SLOW
        self.macd_signal = config.MACD_SIGNAL
        self.sma_short = config.SMA_SHORT
        self.sma_medium = config.SMA_MEDIUM
        self.sma_long = config.SMA_LONG
        self.bb_period = config.BB_PERIOD
        self.bb_std = config.BB_STD

    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all technical indicators

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with indicators added
        """
        if df is None or df.empty:
            logger.warning("Empty DataFrame provided")
            return df

        df = df.copy()

        try:
            # RSI
            df['rsi'] = ta.rsi(df['Close'], length=self.rsi_period)

            # MACD
            macd = ta.macd(df['Close'], fast=self.macd_fast,
                          slow=self.macd_slow, signal=self.macd_signal)
            if macd is not None:
                df['macd'] = macd[f'MACD_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}']
                df['macd_signal'] = macd[f'MACDs_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}']
                df['macd_histogram'] = macd[f'MACDh_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}']

            # Moving Averages
            df['sma_20'] = ta.sma(df['Close'], length=self.sma_short)
            df['sma_50'] = ta.sma(df['Close'], length=self.sma_medium)
            df['sma_200'] = ta.sma(df['Close'], length=self.sma_long)

            # Bollinger Bands
            bb = ta.bbands(df['Close'], length=self.bb_period, std=self.bb_std)
            if bb is not None and not bb.empty:
                # Try different column name formats that pandas_ta might use
                try:
                    df['bb_upper'] = bb[f'BBU_{self.bb_period}_{self.bb_std}.0']
                    df['bb_middle'] = bb[f'BBM_{self.bb_period}_{self.bb_std}.0']
                    df['bb_lower'] = bb[f'BBL_{self.bb_period}_{self.bb_std}.0']
                except KeyError:
                    # Try alternative naming without .0
                    try:
                        df['bb_upper'] = bb[f'BBU_{self.bb_period}_{self.bb_std}']
                        df['bb_middle'] = bb[f'BBM_{self.bb_period}_{self.bb_std}']
                        df['bb_lower'] = bb[f'BBL_{self.bb_period}_{self.bb_std}']
                    except KeyError:
                        # If still failing, just use the columns as they are
                        if len(bb.columns) >= 3:
                            df['bb_lower'] = bb.iloc[:, 0]
                            df['bb_middle'] = bb.iloc[:, 1]
                            df['bb_upper'] = bb.iloc[:, 2]

            # Volume SMA for volume analysis
            df['volume_sma_20'] = ta.sma(df['Volume'], length=20)

            # Additional indicators
            # Stochastic Oscillator
            stoch = ta.stoch(df['High'], df['Low'], df['Close'])
            if stoch is not None:
                df['stoch_k'] = stoch[f'STOCHk_14_3_3']
                df['stoch_d'] = stoch[f'STOCHd_14_3_3']

            # Average True Range (ATR) for volatility
            df['atr'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)

            # On-Balance Volume (OBV)
            df['obv'] = ta.obv(df['Close'], df['Volume'])

            logger.info("All technical indicators calculated successfully")

        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")

        return df

    def generate_technical_signals(self, df: pd.DataFrame) -> Dict:
        """
        Generate buy/sell signals based on technical indicators

        Returns:
            Dictionary with signals and scores
        """
        if df is None or df.empty:
            return {'error': 'No data available'}

        # Get latest values
        latest = df.iloc[-1]
        previous = df.iloc[-2] if len(df) > 1 else latest

        signals = {
            'rsi_signal': self._analyze_rsi(latest['rsi']),
            'macd_signal': self._analyze_macd(latest, previous),
            'ma_signal': self._analyze_moving_averages(latest),
            'bb_signal': self._analyze_bollinger_bands(latest),
            'volume_signal': self._analyze_volume(latest),
            'trend_signal': self._analyze_trend(df),
            'stoch_signal': self._analyze_stochastic(latest) if 'stoch_k' in latest else None
        }

        # Calculate overall technical score (0-100)
        score = self._calculate_technical_score(signals)

        # Generate reasoning
        reasoning = self._generate_reasoning(signals, latest)

        return {
            'score': score,
            'signals': signals,
            'reasoning': reasoning,
            'current_price': latest['Close'],
            'latest_indicators': {
                'rsi': latest['rsi'],
                'macd': latest.get('macd'),
                'sma_20': latest['sma_20'],
                'sma_50': latest['sma_50'],
                'sma_200': latest['sma_200']
            }
        }

    def _analyze_rsi(self, rsi: float) -> Dict:
        """Analyze RSI indicator"""
        if pd.isna(rsi):
            return {'value': None, 'signal': 'neutral', 'strength': 0}

        if rsi < self.rsi_oversold:
            return {'value': rsi, 'signal': 'bullish', 'strength': 2}
        elif rsi > self.rsi_overbought:
            return {'value': rsi, 'signal': 'bearish', 'strength': -2}
        elif rsi < 40:
            return {'value': rsi, 'signal': 'bullish', 'strength': 1}
        elif rsi > 60:
            return {'value': rsi, 'signal': 'bearish', 'strength': -1}
        else:
            return {'value': rsi, 'signal': 'neutral', 'strength': 0}

    def _analyze_macd(self, latest: pd.Series, previous: pd.Series) -> Dict:
        """Analyze MACD indicator"""
        if pd.isna(latest.get('macd')) or pd.isna(latest.get('macd_signal')):
            return {'signal': 'neutral', 'strength': 0}

        macd = latest['macd']
        macd_signal = latest['macd_signal']
        prev_macd = previous.get('macd', macd)
        prev_signal = previous.get('macd_signal', macd_signal)

        # Bullish crossover
        if prev_macd <= prev_signal and macd > macd_signal:
            return {'signal': 'bullish', 'strength': 2, 'crossover': 'bullish'}
        # Bearish crossover
        elif prev_macd >= prev_signal and macd < macd_signal:
            return {'signal': 'bearish', 'strength': -2, 'crossover': 'bearish'}
        # Above signal line
        elif macd > macd_signal:
            return {'signal': 'bullish', 'strength': 1, 'crossover': None}
        # Below signal line
        else:
            return {'signal': 'bearish', 'strength': -1, 'crossover': None}

    def _analyze_moving_averages(self, latest: pd.Series) -> Dict:
        """Analyze moving average relationships"""
        price = latest['Close']
        sma_20 = latest['sma_20']
        sma_50 = latest['sma_50']
        sma_200 = latest['sma_200']

        if pd.isna(sma_20) or pd.isna(sma_50) or pd.isna(sma_200):
            return {'signal': 'neutral', 'strength': 0}

        # Golden cross pattern (bullish)
        if sma_20 > sma_50 > sma_200 and price > sma_20:
            return {'signal': 'bullish', 'strength': 2, 'pattern': 'golden_cross'}
        # Death cross pattern (bearish)
        elif sma_20 < sma_50 < sma_200 and price < sma_20:
            return {'signal': 'bearish', 'strength': -2, 'pattern': 'death_cross'}
        # Above all MAs (bullish)
        elif price > sma_20 and price > sma_50 and price > sma_200:
            return {'signal': 'bullish', 'strength': 1, 'pattern': 'above_all'}
        # Below all MAs (bearish)
        elif price < sma_20 and price < sma_50 and price < sma_200:
            return {'signal': 'bearish', 'strength': -1, 'pattern': 'below_all'}
        else:
            return {'signal': 'neutral', 'strength': 0, 'pattern': 'mixed'}

    def _analyze_bollinger_bands(self, latest: pd.Series) -> Dict:
        """Analyze Bollinger Bands position"""
        price = latest['Close']
        bb_upper = latest.get('bb_upper')
        bb_lower = latest.get('bb_lower')
        bb_middle = latest.get('bb_middle')

        if pd.isna(bb_upper) or pd.isna(bb_lower):
            return {'signal': 'neutral', 'strength': 0}

        # Near lower band (oversold)
        if price < bb_lower:
            return {'signal': 'bullish', 'strength': 2, 'position': 'below_lower'}
        # Near upper band (overbought)
        elif price > bb_upper:
            return {'signal': 'bearish', 'strength': -2, 'position': 'above_upper'}
        # In lower half
        elif price < bb_middle:
            return {'signal': 'bullish', 'strength': 1, 'position': 'lower_half'}
        # In upper half
        else:
            return {'signal': 'bearish', 'strength': -1, 'position': 'upper_half'}

    def _analyze_volume(self, latest: pd.Series) -> Dict:
        """Analyze volume patterns"""
        volume = latest['Volume']
        volume_sma = latest.get('volume_sma_20')

        if pd.isna(volume_sma):
            return {'signal': 'neutral', 'strength': 0}

        volume_ratio = volume / volume_sma

        # High volume spike
        if volume_ratio > config.VOLUME_SPIKE_THRESHOLD:
            return {'signal': 'bullish', 'strength': 1, 'volume_ratio': volume_ratio}
        # Low volume
        elif volume_ratio < 0.7:
            return {'signal': 'bearish', 'strength': -1, 'volume_ratio': volume_ratio}
        else:
            return {'signal': 'neutral', 'strength': 0, 'volume_ratio': volume_ratio}

    def _analyze_trend(self, df: pd.DataFrame, periods: int = 20) -> Dict:
        """Analyze overall trend direction"""
        if len(df) < periods:
            return {'signal': 'neutral', 'strength': 0}

        recent = df.tail(periods)
        close_prices = recent['Close']

        # Calculate trend strength
        slope = (close_prices.iloc[-1] - close_prices.iloc[0]) / periods
        avg_price = close_prices.mean()
        trend_strength = (slope / avg_price) * 100  # Percentage trend

        if trend_strength > 1:
            return {'signal': 'bullish', 'strength': 2, 'trend_strength': trend_strength}
        elif trend_strength > 0.2:
            return {'signal': 'bullish', 'strength': 1, 'trend_strength': trend_strength}
        elif trend_strength < -1:
            return {'signal': 'bearish', 'strength': -2, 'trend_strength': trend_strength}
        elif trend_strength < -0.2:
            return {'signal': 'bearish', 'strength': -1, 'trend_strength': trend_strength}
        else:
            return {'signal': 'neutral', 'strength': 0, 'trend_strength': trend_strength}

    def _analyze_stochastic(self, latest: pd.Series) -> Dict:
        """Analyze Stochastic Oscillator"""
        stoch_k = latest.get('stoch_k')
        stoch_d = latest.get('stoch_d')

        if pd.isna(stoch_k) or pd.isna(stoch_d):
            return {'signal': 'neutral', 'strength': 0}

        # Oversold
        if stoch_k < 20:
            return {'signal': 'bullish', 'strength': 1, 'k': stoch_k, 'd': stoch_d}
        # Overbought
        elif stoch_k > 80:
            return {'signal': 'bearish', 'strength': -1, 'k': stoch_k, 'd': stoch_d}
        else:
            return {'signal': 'neutral', 'strength': 0, 'k': stoch_k, 'd': stoch_d}

    def _calculate_technical_score(self, signals: Dict) -> float:
        """Calculate overall technical score (0-100)"""
        total_strength = 0
        max_possible = 0

        weights = {
            'rsi_signal': 2,
            'macd_signal': 2.5,
            'ma_signal': 2,
            'bb_signal': 1.5,
            'volume_signal': 1,
            'trend_signal': 2,
            'stoch_signal': 1
        }

        for signal_name, weight in weights.items():
            signal = signals.get(signal_name)
            if signal and signal is not None:
                strength = signal.get('strength', 0)
                total_strength += strength * weight
                max_possible += 2 * weight  # Max strength is 2

        # Normalize to 0-100 scale
        if max_possible > 0:
            score = ((total_strength + max_possible) / (2 * max_possible)) * 100
        else:
            score = 50

        return round(score, 2)

    def _generate_reasoning(self, signals: Dict, latest: pd.Series) -> str:
        """Generate human-readable reasoning for the signals"""
        reasons = []

        # RSI analysis
        rsi_signal = signals.get('rsi_signal', {})
        if rsi_signal.get('signal') == 'bullish':
            reasons.append(f"RSI at {rsi_signal.get('value', 0):.1f} indicates oversold conditions")
        elif rsi_signal.get('signal') == 'bearish':
            reasons.append(f"RSI at {rsi_signal.get('value', 0):.1f} indicates overbought conditions")

        # MACD analysis
        macd_signal = signals.get('macd_signal', {})
        if macd_signal.get('crossover') == 'bullish':
            reasons.append("MACD bullish crossover detected")
        elif macd_signal.get('crossover') == 'bearish':
            reasons.append("MACD bearish crossover detected")
        elif macd_signal.get('signal') == 'bullish':
            reasons.append("MACD above signal line (bullish)")

        # Moving average analysis
        ma_signal = signals.get('ma_signal', {})
        pattern = ma_signal.get('pattern')
        if pattern == 'golden_cross':
            reasons.append("Golden cross pattern: strong uptrend")
        elif pattern == 'death_cross':
            reasons.append("Death cross pattern: strong downtrend")
        elif pattern == 'above_all':
            reasons.append("Price above all moving averages")
        elif pattern == 'below_all':
            reasons.append("Price below all moving averages")

        # Bollinger Bands
        bb_signal = signals.get('bb_signal', {})
        if bb_signal.get('position') == 'below_lower':
            reasons.append("Price below lower Bollinger Band (oversold)")
        elif bb_signal.get('position') == 'above_upper':
            reasons.append("Price above upper Bollinger Band (overbought)")

        # Volume
        volume_signal = signals.get('volume_signal', {})
        if volume_signal.get('strength', 0) > 0:
            ratio = volume_signal.get('volume_ratio', 0)
            reasons.append(f"Volume spike detected ({ratio:.1f}x average)")

        # Trend
        trend_signal = signals.get('trend_signal', {})
        trend_strength = trend_signal.get('trend_strength', 0)
        if abs(trend_strength) > 1:
            direction = "upward" if trend_strength > 0 else "downward"
            reasons.append(f"Strong {direction} trend ({abs(trend_strength):.1f}%)")

        if not reasons:
            reasons.append("Mixed technical signals - neutral outlook")

        return " | ".join(reasons)


if __name__ == "__main__":
    # Test technical analysis
    import yfinance as yf

    analyzer = TechnicalAnalyzer()

    # Get test data
    stock = yf.Ticker("AAPL")
    df = stock.history(period="6mo")

    # Calculate indicators
    df_with_indicators = analyzer.calculate_all_indicators(df)
    print("Indicators calculated:")
    print(df_with_indicators[['Close', 'rsi', 'macd', 'sma_20', 'sma_50']].tail())

    # Generate signals
    signals = analyzer.generate_technical_signals(df_with_indicators)
    print(f"\nTechnical Score: {signals['score']}")
    print(f"Reasoning: {signals['reasoning']}")
