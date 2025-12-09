# Quick Start Guide

Get started with Swing Trade Analyzer in 5 minutes!

## Step 1: Setup Environment (2 minutes)

```bash
# Navigate to project directory
cd e:\proj\Swing-trade

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure (Optional - 1 minute)

Create `.env` file (optional - only if using Alpha Vantage):

```bash
copy .env.example .env
```

Edit `.env` and add your Alpha Vantage API key if you have one. Otherwise, skip this step - the app works fine with just yfinance (no API key needed).

## Step 3: Run First Analysis (2 minutes)

```bash
# Start the dashboard
streamlit run app.py
```

Your browser will open to `http://localhost:8501`

## Step 4: Generate Recommendations

In the dashboard:

1. Click **"Run Daily Analysis"** button in the left sidebar
2. Wait 2-3 minutes for analysis to complete
3. View results in the **"Buy Recommendations"** tab

## What You'll See

### Buy Recommendations Tab
- Top 5 stocks to buy
- Overall score (0-100)
- Detailed reasoning combining technical and fundamental analysis
- Current price

### Example Output

```
AAPL - Overall Score: 78.5/100 - BUY

Technical (75.2/100): RSI at 32.1 indicates oversold conditions |
MACD bullish crossover detected | Price above SMA 50

Fundamental (84.5/100): P/E ratio of 24.3 indicates fair value |
Strong profit margin of 25.8% | Revenue growing at 12.5%

Current Price: $182.45
```

## Quick Commands

```bash
# Run dashboard
streamlit run app.py

# Run analysis manually
python scheduler.py now

# Test individual components
python database.py          # Test database
python data_fetcher.py      # Test data fetching
python scoring_engine.py    # Test scoring

# Start automatic scheduler (weekdays at 5:30 PM)
python scheduler.py
```

## Customize Your Stock List

Edit `config.py`:

```python
STOCK_UNIVERSE = [
    'AAPL', 'MSFT', 'GOOGL',  # Add your stocks here
]
```

## Common First-Time Issues

**Problem**: "Module not found"
**Solution**: Make sure virtual environment is activated
```bash
venv\Scripts\activate  # Windows
```

**Problem**: "No data available"
**Solution**: Run "Daily Analysis" first to fetch data

**Problem**: Analysis takes too long
**Solution**: Reduce stock universe in `config.py` to 5-10 stocks for testing

## Next Steps

1. Review buy recommendations
2. Analyze individual stocks in "Stock Analysis" tab
3. Add stocks to portfolio to track P/L
4. Set up scheduler for automatic daily analysis

## Need Help?

- See full [README.md](README.md) for detailed documentation
- Check `data/analyzer.log` for error messages
- Test individual modules to isolate issues

That's it! You're ready to start analyzing stocks. 🚀
