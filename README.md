# Swing Trade Analyzer

A scalable stock swing trade analyzer that performs technical and fundamental analysis, providing daily buy/sell recommendations with detailed reasoning.

## Features

- **Technical Analysis**: RSI, MACD, Moving Averages, Bollinger Bands, Volume Analysis
- **Fundamental Analysis**: P/E Ratio, EPS Growth, Profit Margins, Debt Ratios, ROE/ROA
- **Scoring Engine**: Combined 60% technical + 40% fundamental weighted scoring
- **Interactive Dashboard**: Streamlit-based web interface with charts and metrics
- **Daily Automation**: Scheduled analysis runs after market close
- **Portfolio Tracking**: Track holdings and calculate P/L
- **SQLite Database**: Stores historical data, indicators, and recommendations

## Project Structure

```
swing-trade/
├── app.py                      # Streamlit dashboard
├── data_fetcher.py             # API data collection (yfinance, Alpha Vantage)
├── technical_analysis.py       # Technical indicators calculation
├── fundamental_analysis.py     # Fundamental metrics analysis
├── scoring_engine.py           # Stock scoring and ranking
├── database.py                 # SQLite database operations
├── config.py                   # Configuration and parameters
├── scheduler.py                # Daily automation scheduler
├── requirements.txt            # Python dependencies
├── .env                        # API keys (create this)
├── .env.example               # Example environment file
├── .gitignore                 # Git ignore rules
└── data/
    └── stocks.db              # SQLite database (auto-created)
```

## Installation

### 1. Clone or Create Project Directory

```bash
cd e:\proj\Swing-trade
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

Create a `.env` file in the project root:

```bash
# Copy the example file
copy .env.example .env
```

Edit `.env` and add your Alpha Vantage API key (optional, for enhanced fundamental data):

```
ALPHA_VANTAGE_API_KEY=your_key_here
```

Get a free API key from: https://www.alphavantage.co/support/#api-key

**Note**: Alpha Vantage is optional. The app works with yfinance (no API key required) for both price and fundamental data.

## Usage

### Run the Dashboard

```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

### Dashboard Features

1. **Buy Recommendations Tab**
   - Top 5 buy opportunities
   - Overall score, technical/fundamental breakdown
   - Detailed reasoning for each recommendation
   - Current price and trend indicators

2. **Sell Signals Tab**
   - View active holdings
   - Check current P/L for each position
   - Get sell recommendations based on current scores
   - One-click sell functionality

3. **Stock Analysis Tab**
   - Detailed analysis for individual stocks
   - Interactive price charts with indicators
   - Technical and fundamental metrics
   - Add stocks to your portfolio

4. **Portfolio Overview Tab**
   - Total portfolio value and P/L
   - Holdings breakdown
   - Trade history
   - Performance metrics

### Run Daily Analysis

**From Dashboard:**
Click the "Run Daily Analysis" button in the sidebar.

**From Command Line:**
```bash
python scheduler.py now
```

### Schedule Automatic Analysis

Run the scheduler to automatically analyze stocks every weekday at 5:30 PM ET:

```bash
python scheduler.py
```

Press `Ctrl+C` to stop the scheduler.

## Configuration

Edit [config.py](config.py) to customize:

### Stock Universe

```python
STOCK_UNIVERSE = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',
    # Add more stocks...
]
```

### Technical Parameters

```python
RSI_PERIOD = 14              # RSI calculation period
RSI_OVERSOLD = 30            # Oversold threshold
RSI_OVERBOUGHT = 70          # Overbought threshold
SMA_SHORT = 20               # Short-term moving average
SMA_MEDIUM = 50              # Medium-term moving average
SMA_LONG = 200               # Long-term moving average
```

### Scoring Weights

```python
TECHNICAL_WEIGHT = 0.6       # 60% weight to technical analysis
FUNDAMENTAL_WEIGHT = 0.4     # 40% weight to fundamental analysis
```

### Recommendation Thresholds

```python
MIN_BUY_SCORE = 60           # Minimum score to recommend buy
MAX_SELL_SCORE = 40          # Maximum score to recommend sell
```

## How It Works

### 1. Data Collection

- **Price Data**: Fetched from yfinance (free, no API key)
  - Historical OHLCV data (Open, High, Low, Close, Volume)
  - Up to 1 year of daily data

- **Fundamental Data**: Fetched from yfinance or Alpha Vantage
  - Financial metrics: P/E, EPS, profit margins
  - Balance sheet: debt ratios, current ratio
  - Growth metrics: revenue and earnings growth

### 2. Technical Analysis

Calculates multiple indicators:

- **RSI (Relative Strength Index)**: Identifies overbought/oversold conditions
- **MACD**: Detects trend changes and momentum
- **Moving Averages**: Identifies trends and support/resistance
- **Bollinger Bands**: Measures volatility and price extremes
- **Volume Analysis**: Confirms price movements

**Scoring Logic**:
- RSI < 30: Bullish (oversold)
- MACD bullish crossover: Strong buy signal
- Price above all MAs: Bullish trend
- Price at lower Bollinger Band: Potential bounce

### 3. Fundamental Analysis

Evaluates company health:

- **Valuation**: P/E ratio vs industry benchmarks
- **Profitability**: Profit margins, ROE, ROA
- **Growth**: Revenue and earnings growth rates
- **Financial Health**: Debt levels, liquidity ratios

**Scoring Logic**:
- P/E < 15: Undervalued
- Profit margin > 15%: Excellent profitability
- Revenue growth > 15%: Strong growth
- Debt-to-equity < 0.5: Low debt risk

### 4. Combined Scoring

```
Overall Score = (Technical Score × 0.6) + (Fundamental Score × 0.4)
```

**Recommendation Scale**:
- 80-100: **STRONG BUY**
- 65-79: **BUY**
- 45-64: **HOLD**
- 30-44: **SELL**
- 0-29: **STRONG SELL**

### 5. Reasoning Generation

Each recommendation includes detailed reasoning:

```
Technical (72.5/100): RSI at 28.3 indicates oversold conditions |
MACD bullish crossover detected | Price below lower Bollinger Band
(oversold) || Fundamental (68.0/100): P/E ratio of 14.2 indicates
good value | Strong profit margin of 24.5% | Revenue growing at 18.2%
```

## Database Schema

### Tables

1. **price_data**: Historical OHLCV data
2. **fundamental_data**: Financial metrics
3. **technical_indicators**: Calculated indicators
4. **recommendations**: Buy/sell recommendations with reasoning
5. **holdings**: Portfolio tracking (purchases and sales)

### Data Retention

- Price data: 1 year rolling
- Recommendations: All historical records
- Holdings: Complete trade history

## API Rate Limits

### yfinance (Free, Unlimited)
- No API key required
- No rate limits for basic usage
- Provides both price and fundamental data

### Alpha Vantage (Optional, Free Tier)
- 25 API calls per day
- 5 calls per minute
- Use sparingly for enhanced fundamental data

**Recommendation**: Start with yfinance only. Add Alpha Vantage if you need more detailed financials.

## Testing Individual Modules

Each module can be tested independently:

```bash
# Test database
python database.py

# Test data fetcher
python data_fetcher.py

# Test technical analysis
python technical_analysis.py

# Test fundamental analysis
python fundamental_analysis.py

# Test scoring engine
python scoring_engine.py
```

## Troubleshooting

### Common Issues

**1. Module Import Errors**
```bash
# Make sure you're in the virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

**2. Database Errors**
```bash
# Delete and recreate database
del data\stocks.db
python database.py
```

**3. API Rate Limit Errors**
- yfinance: Add delays between requests
- Alpha Vantage: Stay under 25 calls/day limit

**4. No Data for Stock**
- Check ticker symbol is correct
- Some stocks may not have complete fundamental data
- Try with well-known stocks (AAPL, MSFT, GOOGL)

## Scaling Path

### Phase 1: MVP (Current)
- 20 stocks
- SQLite database
- EOD analysis
- Streamlit dashboard

### Phase 2: Scale Up
- Expand to 100+ stocks
- Migrate to PostgreSQL
- Docker containerization
- Add Apache Airflow for orchestration

### Phase 3: Production
- Real-time data with Apache Kafka
- Snowflake data warehouse
- Machine learning predictions
- Power BI dashboards
- Email/SMS alerts

## Contributing

To add new features:

1. **New Technical Indicator**: Add to [technical_analysis.py](technical_analysis.py)
2. **New Fundamental Metric**: Add to [fundamental_analysis.py](fundamental_analysis.py)
3. **Modify Scoring**: Update weights in [config.py](config.py)
4. **Add Data Source**: Extend [data_fetcher.py](data_fetcher.py)

## License

This project is for educational purposes. Use at your own risk. Not financial advice.

## Disclaimer

This tool is for informational purposes only. It does not constitute financial advice. Always do your own research and consult with a qualified financial advisor before making investment decisions.

Stock trading involves risk of loss. Past performance does not guarantee future results.

## Support

For issues or questions:
1. Check this README
2. Review module documentation in code comments
3. Test individual modules to isolate issues
4. Check logs in `data/analyzer.log`

## Next Steps

1. **Run Initial Analysis**:
   ```bash
   streamlit run app.py
   # Click "Run Daily Analysis" in sidebar
   ```

2. **Review Recommendations**:
   - Check Buy Recommendations tab
   - Review reasoning for each stock
   - Analyze charts and metrics

3. **Track Performance**:
   - Add holdings to portfolio
   - Monitor daily
   - Review sell signals

4. **Customize**:
   - Adjust stock universe in [config.py](config.py)
   - Fine-tune scoring weights
   - Modify thresholds

Happy trading! 📈
