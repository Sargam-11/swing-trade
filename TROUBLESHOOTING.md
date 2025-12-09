# Troubleshooting Guide

Common issues and solutions for Swing Trade Analyzer.

## Installation Issues

### Problem: "Python not found"

**Symptoms**:
```
'python' is not recognized as an internal or external command
```

**Solutions**:
1. Install Python 3.8+ from https://python.org/
2. During installation, check "Add Python to PATH"
3. Restart terminal/command prompt
4. Verify: `python --version`

---

### Problem: "pip not found"

**Symptoms**:
```
'pip' is not recognized as an internal or external command
```

**Solutions**:
1. Try `python -m pip` instead of `pip`
2. Reinstall Python with "pip" option checked
3. Add Python Scripts folder to PATH

---

### Problem: Virtual environment activation fails

**Symptoms**:
```
venv\Scripts\activate : cannot be loaded because running scripts is disabled
```

**Solution (Windows PowerShell)**:
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate normally
venv\Scripts\activate
```

**Alternative**: Use Command Prompt instead of PowerShell
```cmd
venv\Scripts\activate.bat
```

---

### Problem: Package installation fails

**Symptoms**:
```
ERROR: Could not find a version that satisfies the requirement...
```

**Solutions**:
1. Upgrade pip: `python -m pip install --upgrade pip`
2. Install packages one by one to identify the problem:
   ```bash
   pip install streamlit
   pip install yfinance
   pip install pandas
   # etc.
   ```
3. Check Python version: Must be 3.8+
4. Clear pip cache: `pip cache purge`

---

## Data Fetching Issues

### Problem: "No data available for symbol"

**Symptoms**:
```
WARNING: No price data found for AAPL
```

**Solutions**:
1. Check internet connection
2. Verify ticker symbol is correct (use uppercase)
3. Try a well-known stock like AAPL, MSFT
4. Check if yfinance is working:
   ```python
   import yfinance as yf
   data = yf.Ticker("AAPL").history(period="1d")
   print(data)
   ```
5. Wait and retry (temporary API issues)

---

### Problem: "Rate limit exceeded"

**Symptoms**:
```
ERROR: 429 Too Many Requests
```

**Solutions**:
1. **yfinance**: Add delays between requests
   - Edit `config.py`: Increase delay values
   - Reduce stock universe temporarily

2. **Alpha Vantage**: 25 calls/day limit
   - Use yfinance instead (set `use_alpha_vantage=False`)
   - Wait 24 hours for limit reset
   - Upgrade to paid tier

---

### Problem: "Connection timeout"

**Symptoms**:
```
ERROR: Connection timeout after 10 seconds
```

**Solutions**:
1. Check firewall settings
2. Check antivirus blocking connections
3. Try different network
4. Increase timeout in `data_fetcher.py`

---

## Database Issues

### Problem: "Database locked"

**Symptoms**:
```
ERROR: database is locked
```

**Solutions**:
1. Close all other processes using the database
2. Close Streamlit dashboard
3. Restart scheduler if running
4. Delete `data/stocks.db-journal` if exists
5. As last resort, restart computer

---

### Problem: "Table doesn't exist"

**Symptoms**:
```
ERROR: no such table: price_data
```

**Solutions**:
1. Run database initialization:
   ```python
   python database.py
   ```
2. Delete and recreate database:
   ```bash
   del data\stocks.db
   python database.py
   ```

---

### Problem: "Corrupt database"

**Symptoms**:
```
ERROR: database disk image is malformed
```

**Solutions**:
1. Delete database and start fresh:
   ```bash
   del data\stocks.db
   python verify_setup.py
   ```
2. Run analysis to rebuild data:
   ```bash
   python scheduler.py now
   ```

---

## Analysis Issues

### Problem: "Analysis takes too long"

**Symptoms**: Analysis running for >10 minutes

**Solutions**:
1. Reduce stock universe in `config.py`:
   ```python
   STOCK_UNIVERSE = ['AAPL', 'MSFT', 'GOOGL']  # Start with 3
   ```
2. Check internet speed
3. Disable Alpha Vantage (slower)
4. Check logs for stuck stocks

---

### Problem: "All recommendations are HOLD"

**Symptoms**: No BUY or SELL signals

**Possible Causes**:
1. Market conditions neutral
2. Thresholds too strict
3. Insufficient data

**Solutions**:
1. Adjust thresholds in `config.py`:
   ```python
   MIN_BUY_SCORE = 55  # Lower from 60
   MAX_SELL_SCORE = 45  # Raise from 40
   ```
2. Wait for more volatile market conditions
3. Check that analysis is using recent data

---

### Problem: "Technical indicators are NaN"

**Symptoms**:
```
RSI: NaN, MACD: NaN
```

**Causes**: Insufficient historical data

**Solutions**:
1. Increase historical data period:
   ```python
   # In config.py
   HISTORICAL_DAYS = 365  # Increase from default
   ```
2. Check if stock has enough trading history
3. Use well-established stocks (not recent IPOs)

---

## Dashboard Issues

### Problem: "Dashboard won't start"

**Symptoms**:
```
ERROR: streamlit: command not found
```

**Solutions**:
1. Ensure virtual environment is activated
2. Reinstall streamlit:
   ```bash
   pip install streamlit --force-reinstall
   ```
3. Use full path:
   ```bash
   python -m streamlit run app.py
   ```

---

### Problem: "Dashboard shows blank page"

**Solutions**:
1. Clear browser cache
2. Try different browser
3. Check console for errors (F12)
4. Restart Streamlit:
   ```bash
   # Press Ctrl+C to stop
   streamlit run app.py
   ```

---

### Problem: "Charts not displaying"

**Symptoms**: Empty chart areas

**Solutions**:
1. Check if plotly is installed:
   ```bash
   pip install plotly --upgrade
   ```
2. Ensure data exists in database
3. Run analysis first ("Run Daily Analysis")
4. Check browser console for JavaScript errors

---

### Problem: "Run Daily Analysis button does nothing"

**Solutions**:
1. Check Streamlit console for errors
2. Ensure internet connection active
3. Check `data/analyzer.log` for errors
4. Try manual analysis:
   ```bash
   python scheduler.py now
   ```

---

## Scheduler Issues

### Problem: "Scheduler not running at scheduled time"

**Solutions**:
1. Ensure computer is on at scheduled time
2. Check timezone settings (schedule uses local time)
3. Verify schedule in `scheduler.py`
4. Run manually to test:
   ```bash
   python scheduler.py now
   ```

---

### Problem: "Scheduler crashes"

**Symptoms**: Process exits unexpectedly

**Solutions**:
1. Check logs: `data/analyzer.log`
2. Test with single stock first
3. Add more error handling
4. Run in debug mode:
   ```python
   # In config.py
   LOG_LEVEL = 'DEBUG'
   ```

---

## Performance Issues

### Problem: "High memory usage"

**Solutions**:
1. Reduce stock universe
2. Clear old data:
   ```python
   # In database.py
   db.clear_old_data(days=180)  # Keep 6 months
   ```
3. Restart application periodically
4. Close unused applications

---

### Problem: "Slow chart rendering"

**Solutions**:
1. Reduce historical data period
2. Simplify charts (remove some indicators)
3. Use faster browser (Chrome recommended)
4. Close other browser tabs

---

## API Key Issues

### Problem: "Alpha Vantage not working"

**Symptoms**:
```
Alpha Vantage API key not configured
```

**Solutions**:
1. Create `.env` file from `.env.example`:
   ```bash
   copy .env.example .env
   ```
2. Get free API key: https://www.alphavantage.co/support/#api-key
3. Add to `.env`:
   ```
   ALPHA_VANTAGE_API_KEY=YOUR_KEY_HERE
   ```
4. Restart application

**Alternative**: Use yfinance only (no API key needed)
```python
# In scoring_engine.py, run_daily_analysis()
use_alpha_vantage=False
```

---

## Module Import Errors

### Problem: "ModuleNotFoundError"

**Symptoms**:
```
ModuleNotFoundError: No module named 'pandas_ta'
```

**Solutions**:
1. Activate virtual environment:
   ```bash
   venv\Scripts\activate
   ```
2. Reinstall requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Check virtual environment is active:
   ```bash
   which python  # Should show venv path
   ```

---

### Problem: "Circular import errors"

**Symptoms**:
```
ImportError: cannot import name 'X' from partially initialized module
```

**Solutions**:
1. Don't run modules from wrong directory
2. Ensure you're in project root
3. Check for naming conflicts (e.g., file named `pandas.py`)

---

## Data Quality Issues

### Problem: "Inconsistent recommendations"

**Symptoms**: Recommendations change dramatically day-to-day

**Causes**: Normal market volatility or data issues

**Solutions**:
1. Check data quality:
   ```python
   python data_fetcher.py
   ```
2. Review reasoning in dashboard
3. Adjust scoring weights in `config.py`
4. Consider longer analysis periods

---

### Problem: "Missing fundamental data"

**Symptoms**: Fundamental score always 50

**Solutions**:
1. Some stocks lack complete data
2. Try well-known large-cap stocks
3. Use Alpha Vantage for better coverage
4. Accept that some stocks have limited data

---

## Verification & Testing

### Run Full System Check

```bash
python verify_setup.py
```

This checks:
- ✓ Python version
- ✓ Dependencies installed
- ✓ Project files exist
- ✓ Database creation
- ✓ Data fetching
- ✓ Technical analysis

### Test Individual Components

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

---

## Getting Help

### Check Logs

```bash
# View recent logs
type data\analyzer.log  # Windows
cat data/analyzer.log   # Mac/Linux

# Watch logs in real-time
tail -f data/analyzer.log  # Mac/Linux
```

### Enable Debug Mode

```python
# In config.py
LOG_LEVEL = 'DEBUG'
```

### Gather Information for Support

1. Python version: `python --version`
2. OS version: `ver` (Windows) or `uname -a` (Mac/Linux)
3. Package versions: `pip list`
4. Error message from logs
5. Steps to reproduce issue

---

## Known Limitations

1. **API Rate Limits**: Free APIs have limits
2. **EOD Data Only**: Not real-time by design
3. **SQLite Scalability**: Not ideal for 1000+ stocks
4. **Data Coverage**: Some stocks lack fundamentals
5. **Network Dependency**: Requires internet

---

## Emergency Reset

If all else fails, complete reset:

```bash
# 1. Deactivate and remove virtual environment
deactivate
rmdir /s venv  # Windows
rm -rf venv    # Mac/Linux

# 2. Delete database
del data\stocks.db  # Windows
rm data/stocks.db   # Mac/Linux

# 3. Delete .env
del .env  # Windows
rm .env   # Mac/Linux

# 4. Start fresh
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python verify_setup.py
streamlit run app.py
```

---

## Prevention Tips

1. **Regular backups**: Copy `data/stocks.db` weekly
2. **Update dependencies**: Monthly `pip install --upgrade -r requirements.txt`
3. **Monitor logs**: Check `analyzer.log` regularly
4. **Test changes**: Run `verify_setup.py` after modifications
5. **Keep virtual environment**: Don't delete/recreate unnecessarily

---

## Still Having Issues?

1. Review [README.md](README.md) for setup instructions
2. Check [QUICKSTART.md](QUICKSTART.md) for basic usage
3. Review [ARCHITECTURE.md](ARCHITECTURE.md) for system understanding
4. Search error message in documentation
5. Check Python package documentation:
   - [Streamlit](https://docs.streamlit.io/)
   - [yfinance](https://pypi.org/project/yfinance/)
   - [pandas](https://pandas.pydata.org/)

Good luck! 🚀
