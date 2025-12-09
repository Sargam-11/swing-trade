import logging
from typing import Dict, Optional
import pandas as pd
import config

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class FundamentalAnalyzer:
    """Analyze fundamental metrics and score stocks"""

    def __init__(self):
        # Benchmark values for scoring (industry averages for S&P 500)
        self.benchmarks = {
            'pe_ratio': {'good': 15, 'acceptable': 25, 'weight': 2},
            'profit_margin': {'good': 0.15, 'acceptable': 0.08, 'weight': 2},
            'debt_to_equity': {'good': 0.5, 'acceptable': 1.5, 'weight': 1.5},
            'revenue_growth': {'good': 0.15, 'acceptable': 0.05, 'weight': 2},
            'return_on_equity': {'good': 0.15, 'acceptable': 0.08, 'weight': 2},
            'return_on_assets': {'good': 0.08, 'acceptable': 0.04, 'weight': 1.5},
            'current_ratio': {'good': 2.0, 'acceptable': 1.0, 'weight': 1},
            'earnings_growth': {'good': 0.15, 'acceptable': 0.05, 'weight': 2},
            'operating_margin': {'good': 0.15, 'acceptable': 0.08, 'weight': 1.5}
        }

    def analyze_fundamentals(self, fundamental_data: Dict) -> Dict:
        """
        Analyze fundamental data and generate score

        Args:
            fundamental_data: Dictionary with fundamental metrics

        Returns:
            Dictionary with score, signals, and reasoning
        """
        if not fundamental_data:
            return {
                'score': 50,
                'signals': {},
                'reasoning': 'No fundamental data available',
                'metrics': {}
            }

        signals = {}

        # Analyze each metric
        if 'pe_ratio' in fundamental_data:
            signals['pe_ratio'] = self._analyze_pe_ratio(fundamental_data['pe_ratio'])

        if 'profit_margin' in fundamental_data:
            signals['profit_margin'] = self._analyze_profit_margin(
                fundamental_data['profit_margin'])

        if 'debt_to_equity' in fundamental_data:
            signals['debt_to_equity'] = self._analyze_debt_to_equity(
                fundamental_data['debt_to_equity'])

        if 'revenue_growth' in fundamental_data:
            signals['revenue_growth'] = self._analyze_growth_metric(
                fundamental_data['revenue_growth'], 'revenue_growth')

        if 'return_on_equity' in fundamental_data:
            signals['return_on_equity'] = self._analyze_profitability_metric(
                fundamental_data['return_on_equity'], 'return_on_equity')

        if 'return_on_assets' in fundamental_data:
            signals['return_on_assets'] = self._analyze_profitability_metric(
                fundamental_data['return_on_assets'], 'return_on_assets')

        if 'earnings_growth' in fundamental_data:
            signals['earnings_growth'] = self._analyze_growth_metric(
                fundamental_data['earnings_growth'], 'earnings_growth')

        if 'current_ratio' in fundamental_data:
            signals['current_ratio'] = self._analyze_current_ratio(
                fundamental_data['current_ratio'])

        if 'operating_margin' in fundamental_data:
            signals['operating_margin'] = self._analyze_profitability_metric(
                fundamental_data['operating_margin'], 'operating_margin')

        # Calculate overall fundamental score
        score = self._calculate_fundamental_score(signals)

        # Generate reasoning
        reasoning = self._generate_reasoning(signals, fundamental_data)

        return {
            'score': score,
            'signals': signals,
            'reasoning': reasoning,
            'metrics': fundamental_data
        }

    def _analyze_pe_ratio(self, pe_ratio: float) -> Dict:
        """Analyze P/E ratio"""
        if pe_ratio is None or pe_ratio <= 0:
            return {'signal': 'neutral', 'strength': 0, 'value': pe_ratio}

        benchmark = self.benchmarks['pe_ratio']

        # Lower P/E is generally better (more value)
        if pe_ratio < benchmark['good']:
            return {'signal': 'bullish', 'strength': 2, 'value': pe_ratio,
                   'interpretation': 'undervalued'}
        elif pe_ratio < benchmark['acceptable']:
            return {'signal': 'bullish', 'strength': 1, 'value': pe_ratio,
                   'interpretation': 'fairly valued'}
        elif pe_ratio < 35:
            return {'signal': 'neutral', 'strength': 0, 'value': pe_ratio,
                   'interpretation': 'slightly expensive'}
        else:
            return {'signal': 'bearish', 'strength': -1, 'value': pe_ratio,
                   'interpretation': 'overvalued'}

    def _analyze_profit_margin(self, margin: float) -> Dict:
        """Analyze profit margin"""
        if margin is None:
            return {'signal': 'neutral', 'strength': 0, 'value': margin}

        benchmark = self.benchmarks['profit_margin']

        # Higher margin is better
        if margin >= benchmark['good']:
            return {'signal': 'bullish', 'strength': 2, 'value': margin,
                   'interpretation': 'excellent profitability'}
        elif margin >= benchmark['acceptable']:
            return {'signal': 'bullish', 'strength': 1, 'value': margin,
                   'interpretation': 'good profitability'}
        elif margin >= 0.03:
            return {'signal': 'neutral', 'strength': 0, 'value': margin,
                   'interpretation': 'moderate profitability'}
        else:
            return {'signal': 'bearish', 'strength': -1, 'value': margin,
                   'interpretation': 'low profitability'}

    def _analyze_debt_to_equity(self, debt_to_equity: float) -> Dict:
        """Analyze debt-to-equity ratio"""
        if debt_to_equity is None:
            return {'signal': 'neutral', 'strength': 0, 'value': debt_to_equity}

        benchmark = self.benchmarks['debt_to_equity']

        # Lower debt is better
        if debt_to_equity <= benchmark['good']:
            return {'signal': 'bullish', 'strength': 2, 'value': debt_to_equity,
                   'interpretation': 'low debt'}
        elif debt_to_equity <= benchmark['acceptable']:
            return {'signal': 'bullish', 'strength': 1, 'value': debt_to_equity,
                   'interpretation': 'manageable debt'}
        elif debt_to_equity <= 2.5:
            return {'signal': 'neutral', 'strength': 0, 'value': debt_to_equity,
                   'interpretation': 'moderate debt'}
        else:
            return {'signal': 'bearish', 'strength': -1, 'value': debt_to_equity,
                   'interpretation': 'high debt'}

    def _analyze_growth_metric(self, growth: float, metric_name: str) -> Dict:
        """Analyze growth metrics (revenue, earnings)"""
        if growth is None:
            return {'signal': 'neutral', 'strength': 0, 'value': growth}

        benchmark = self.benchmarks.get(metric_name, {'good': 0.15, 'acceptable': 0.05})

        # Higher growth is better
        if growth >= benchmark['good']:
            return {'signal': 'bullish', 'strength': 2, 'value': growth,
                   'interpretation': 'strong growth'}
        elif growth >= benchmark['acceptable']:
            return {'signal': 'bullish', 'strength': 1, 'value': growth,
                   'interpretation': 'moderate growth'}
        elif growth >= 0:
            return {'signal': 'neutral', 'strength': 0, 'value': growth,
                   'interpretation': 'slow growth'}
        elif growth >= -0.05:
            return {'signal': 'bearish', 'strength': -1, 'value': growth,
                   'interpretation': 'slight decline'}
        else:
            return {'signal': 'bearish', 'strength': -2, 'value': growth,
                   'interpretation': 'significant decline'}

    def _analyze_profitability_metric(self, value: float, metric_name: str) -> Dict:
        """Analyze profitability metrics (ROE, ROA, operating margin)"""
        if value is None:
            return {'signal': 'neutral', 'strength': 0, 'value': value}

        benchmark = self.benchmarks.get(metric_name,
                                       {'good': 0.15, 'acceptable': 0.08})

        # Higher is better
        if value >= benchmark['good']:
            return {'signal': 'bullish', 'strength': 2, 'value': value,
                   'interpretation': 'excellent'}
        elif value >= benchmark['acceptable']:
            return {'signal': 'bullish', 'strength': 1, 'value': value,
                   'interpretation': 'good'}
        elif value >= 0:
            return {'signal': 'neutral', 'strength': 0, 'value': value,
                   'interpretation': 'below average'}
        else:
            return {'signal': 'bearish', 'strength': -1, 'value': value,
                   'interpretation': 'poor'}

    def _analyze_current_ratio(self, ratio: float) -> Dict:
        """Analyze current ratio (liquidity)"""
        if ratio is None:
            return {'signal': 'neutral', 'strength': 0, 'value': ratio}

        benchmark = self.benchmarks['current_ratio']

        # Optimal range is around 1.5-3.0
        if ratio >= benchmark['good']:
            return {'signal': 'bullish', 'strength': 2, 'value': ratio,
                   'interpretation': 'strong liquidity'}
        elif ratio >= benchmark['acceptable']:
            return {'signal': 'bullish', 'strength': 1, 'value': ratio,
                   'interpretation': 'adequate liquidity'}
        elif ratio >= 0.8:
            return {'signal': 'neutral', 'strength': 0, 'value': ratio,
                   'interpretation': 'tight liquidity'}
        else:
            return {'signal': 'bearish', 'strength': -1, 'value': ratio,
                   'interpretation': 'liquidity concerns'}

    def _calculate_fundamental_score(self, signals: Dict) -> float:
        """Calculate overall fundamental score (0-100)"""
        if not signals:
            return 50.0

        total_weighted_strength = 0
        total_weight = 0

        for metric_name, signal in signals.items():
            if signal and 'strength' in signal:
                weight = self.benchmarks.get(metric_name, {}).get('weight', 1)
                strength = signal['strength']
                total_weighted_strength += strength * weight
                total_weight += 2 * weight  # Max strength is 2

        if total_weight > 0:
            # Normalize to 0-100 scale
            score = ((total_weighted_strength + total_weight) / (2 * total_weight)) * 100
        else:
            score = 50

        return round(score, 2)

    def _generate_reasoning(self, signals: Dict, fundamental_data: Dict) -> str:
        """Generate human-readable reasoning for fundamental analysis"""
        reasons = []

        # P/E Ratio
        if 'pe_ratio' in signals:
            pe_signal = signals['pe_ratio']
            if pe_signal['signal'] == 'bullish':
                reasons.append(f"P/E ratio of {pe_signal['value']:.1f} indicates good value")
            elif pe_signal['signal'] == 'bearish':
                reasons.append(f"P/E ratio of {pe_signal['value']:.1f} suggests overvaluation")

        # Profit Margin
        if 'profit_margin' in signals:
            pm_signal = signals['profit_margin']
            if pm_signal['strength'] >= 1:
                reasons.append(
                    f"Strong profit margin of {pm_signal['value']*100:.1f}%")

        # Revenue Growth
        if 'revenue_growth' in signals:
            rg_signal = signals['revenue_growth']
            if rg_signal['value'] is not None:
                if rg_signal['strength'] >= 1:
                    reasons.append(
                        f"Revenue growing at {rg_signal['value']*100:.1f}%")
                elif rg_signal['strength'] <= -1:
                    reasons.append(
                        f"Revenue declining at {abs(rg_signal['value'])*100:.1f}%")

        # Earnings Growth
        if 'earnings_growth' in signals:
            eg_signal = signals['earnings_growth']
            if eg_signal['value'] is not None and eg_signal['strength'] >= 1:
                reasons.append(
                    f"Earnings growth of {eg_signal['value']*100:.1f}%")

        # ROE
        if 'return_on_equity' in signals:
            roe_signal = signals['return_on_equity']
            if roe_signal['value'] is not None and roe_signal['strength'] >= 1:
                reasons.append(
                    f"ROE of {roe_signal['value']*100:.1f}% shows efficient equity use")

        # Debt
        if 'debt_to_equity' in signals:
            debt_signal = signals['debt_to_equity']
            if debt_signal['value'] is not None:
                if debt_signal['strength'] >= 1:
                    reasons.append(
                        f"Low debt-to-equity ratio of {debt_signal['value']:.2f}")
                elif debt_signal['strength'] <= -1:
                    reasons.append(
                        f"High debt-to-equity ratio of {debt_signal['value']:.2f}")

        # Current Ratio
        if 'current_ratio' in signals:
            cr_signal = signals['current_ratio']
            if cr_signal['value'] is not None and cr_signal['strength'] >= 1:
                reasons.append(
                    f"Current ratio of {cr_signal['value']:.2f} indicates good liquidity")

        if not reasons:
            reasons.append("Limited fundamental data available for analysis")

        return " | ".join(reasons)

    def get_valuation_category(self, fundamental_data: Dict) -> str:
        """
        Categorize stock valuation: value, growth, or balanced

        Returns:
            String: 'value', 'growth', or 'balanced'
        """
        pe_ratio = fundamental_data.get('pe_ratio')
        revenue_growth = fundamental_data.get('revenue_growth', 0)
        earnings_growth = fundamental_data.get('earnings_growth', 0)

        if pe_ratio and pe_ratio < 15:
            if revenue_growth and revenue_growth < 0.05:
                return 'value'
            else:
                return 'balanced'
        elif revenue_growth and revenue_growth > 0.15:
            return 'growth'
        else:
            return 'balanced'

    def get_quality_score(self, fundamental_data: Dict) -> float:
        """
        Calculate quality score based on profitability and efficiency

        Returns:
            Float: 0-100 score
        """
        quality_metrics = {
            'return_on_equity': fundamental_data.get('return_on_equity', 0) or 0,
            'return_on_assets': fundamental_data.get('return_on_assets', 0) or 0,
            'profit_margin': fundamental_data.get('profit_margin', 0) or 0,
            'operating_margin': fundamental_data.get('operating_margin', 0) or 0
        }

        # Simple average of normalized metrics
        scores = []
        for metric, value in quality_metrics.items():
            if value > 0:
                benchmark = self.benchmarks.get(metric, {}).get('good', 0.15)
                normalized = min(value / benchmark, 1.0) * 100
                scores.append(normalized)

        if scores:
            return round(sum(scores) / len(scores), 2)
        return 50.0


if __name__ == "__main__":
    # Test fundamental analysis
    analyzer = FundamentalAnalyzer()

    # Sample fundamental data
    test_data = {
        'pe_ratio': 18.5,
        'eps': 6.12,
        'profit_margin': 0.25,
        'debt_to_equity': 0.8,
        'revenue_growth': 0.12,
        'return_on_equity': 0.28,
        'return_on_assets': 0.15,
        'current_ratio': 1.8,
        'earnings_growth': 0.18,
        'operating_margin': 0.30
    }

    result = analyzer.analyze_fundamentals(test_data)

    print(f"Fundamental Score: {result['score']}")
    print(f"Reasoning: {result['reasoning']}")
    print(f"Valuation Category: {analyzer.get_valuation_category(test_data)}")
    print(f"Quality Score: {analyzer.get_quality_score(test_data)}")
