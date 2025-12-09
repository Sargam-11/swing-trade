# Swing Trade Analyzer - Documentation Index

Welcome! This index will guide you to the right documentation based on what you need.

## Getting Started

### New Users - Start Here

1. **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide
   - Quick installation
   - First analysis
   - Basic usage
   - **START HERE IF YOU'RE NEW**

2. **[README.md](README.md)** - Complete documentation
   - Full feature list
   - Detailed installation
   - Configuration guide
   - Usage examples
   - **READ THIS SECOND**

3. **Run Setup** (Windows users)
   ```batch
   setup.bat
   ```

4. **Verify Installation**
   ```bash
   python verify_setup.py
   ```

## Reference Documentation

### System Understanding

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
  - Component diagrams
  - Data flow
  - Module dependencies
  - Scalability path
  - **For developers and architects**

- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Project overview
  - What's been built
  - Features implemented
  - Technical specifications
  - Statistics
  - **For project managers**

### Troubleshooting

- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Problem solving
  - Common issues
  - Solutions
  - Debugging tips
  - Emergency reset
  - **When something goes wrong**

## Quick Reference by Task

### I want to...

#### Install and Setup
→ [QUICKSTART.md](QUICKSTART.md) - Section "Step 1: Setup"
→ Run `setup.bat` (Windows)
→ Run `python verify_setup.py`

#### Run the Dashboard
→ [QUICKSTART.md](QUICKSTART.md) - Section "Step 3"
→ Run `run_dashboard.bat` (Windows)
→ Or: `streamlit run app.py`

#### Analyze Stocks
→ [README.md](README.md) - Section "Usage"
→ Click "Run Daily Analysis" in dashboard
→ Or: `python scheduler.py now`

#### Understand How It Works
→ [README.md](README.md) - Section "How It Works"
→ [ARCHITECTURE.md](ARCHITECTURE.md) - Full architecture

#### Customize Settings
→ [README.md](README.md) - Section "Configuration"
→ Edit [config.py](config.py)

#### Fix Problems
→ [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
→ Check `data/analyzer.log`

#### Understand the Code
→ [ARCHITECTURE.md](ARCHITECTURE.md) - Module descriptions
→ [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Component details
→ Code comments in each `.py` file

#### Scale the System
→ [README.md](README.md) - Section "Scaling Path"
→ [ARCHITECTURE.md](ARCHITECTURE.md) - Scalability Architecture
→ [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Future enhancements

## Documentation by User Type

### For Traders (End Users)

**Priority order:**
1. [QUICKSTART.md](QUICKSTART.md) - Get started fast
2. [README.md](README.md) - Learn all features
3. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Fix issues

**Skip:**
- ARCHITECTURE.md (too technical)

### For Developers

**Priority order:**
1. [README.md](README.md) - Understand project
2. [ARCHITECTURE.md](ARCHITECTURE.md) - System design
3. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Implementation details
4. Code files with inline comments

**Focus on:**
- Module dependencies
- Data flow
- API integration
- Database schema

### For DevOps/System Admins

**Priority order:**
1. [QUICKSTART.md](QUICKSTART.md) - Quick setup
2. [ARCHITECTURE.md](ARCHITECTURE.md) - Deployment architecture
3. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
4. [README.md](README.md) - Configuration

**Focus on:**
- Deployment options
- Scalability path
- Monitoring
- Backup strategy

### For Project Managers

**Priority order:**
1. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Project overview
2. [README.md](README.md) - Features and capabilities
3. [ARCHITECTURE.md](ARCHITECTURE.md) - Technical approach

**Focus on:**
- Features implemented
- Project statistics
- Success metrics
- Future roadmap

## Core Files Reference

### Python Modules

| File | Purpose | Documentation |
|------|---------|---------------|
| [config.py](config.py) | Configuration | [README.md](README.md#configuration) |
| [database.py](database.py) | Database operations | [ARCHITECTURE.md](ARCHITECTURE.md#database-schema-design) |
| [data_fetcher.py](data_fetcher.py) | Data collection | [README.md](README.md#1-data-collection) |
| [technical_analysis.py](technical_analysis.py) | Technical indicators | [README.md](README.md#2-technical-analysis) |
| [fundamental_analysis.py](fundamental_analysis.py) | Fundamental metrics | [README.md](README.md#3-fundamental-analysis) |
| [scoring_engine.py](scoring_engine.py) | Stock scoring | [README.md](README.md#4-combined-scoring) |
| [app.py](app.py) | Dashboard | [README.md](README.md#dashboard-features) |
| [scheduler.py](scheduler.py) | Automation | [README.md](README.md#schedule-automatic-analysis) |

### Documentation Files

| File | Purpose | Target Audience |
|------|---------|-----------------|
| [README.md](README.md) | Complete guide | Everyone |
| [QUICKSTART.md](QUICKSTART.md) | Fast setup | New users |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design | Developers |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Project overview | Managers |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Problem solving | Everyone |
| [INDEX.md](INDEX.md) | Navigation | Everyone |

### Utility Files

| File | Purpose | Usage |
|------|---------|-------|
| [requirements.txt](requirements.txt) | Dependencies | `pip install -r requirements.txt` |
| [.env.example](.env.example) | Config template | Copy to `.env` |
| [verify_setup.py](verify_setup.py) | Setup check | `python verify_setup.py` |
| [setup.bat](setup.bat) | Windows setup | Double-click or `setup.bat` |
| [run_dashboard.bat](run_dashboard.bat) | Start dashboard | Double-click or `run_dashboard.bat` |
| [run_analysis.bat](run_analysis.bat) | Run analysis | Double-click or `run_analysis.bat` |

## Learning Path

### Beginner Path (Just Want to Use It)

```
1. QUICKSTART.md (5 min)
   ↓
2. Run setup.bat or manual setup (5 min)
   ↓
3. Run dashboard (run_dashboard.bat)
   ↓
4. Click "Run Daily Analysis"
   ↓
5. View recommendations
   ↓
6. DONE! (Refer to TROUBLESHOOTING.md if issues)
```

### Intermediate Path (Want to Understand & Customize)

```
1. QUICKSTART.md (5 min)
   ↓
2. README.md - Features & How It Works (15 min)
   ↓
3. Set up and run (10 min)
   ↓
4. README.md - Configuration section (10 min)
   ↓
5. Customize config.py
   ↓
6. Test with your settings
```

### Advanced Path (Want to Develop/Extend)

```
1. README.md - Complete read (30 min)
   ↓
2. ARCHITECTURE.md - System design (30 min)
   ↓
3. PROJECT_SUMMARY.md - Implementation (20 min)
   ↓
4. Review code files with inline docs
   ↓
5. Test individual modules
   ↓
6. Make modifications
   ↓
7. Contribute improvements
```

## FAQ Quick Links

### Installation & Setup
- How do I install? → [QUICKSTART.md](QUICKSTART.md)
- Setup verification? → Run `python verify_setup.py`
- Dependencies? → [requirements.txt](requirements.txt)

### Usage
- How to run? → [README.md](README.md#run-the-dashboard)
- How to analyze stocks? → [README.md](README.md#run-daily-analysis)
- How to schedule? → [README.md](README.md#schedule-automatic-analysis)

### Configuration
- Change stocks? → [README.md](README.md#stock-universe)
- Adjust parameters? → [README.md](README.md#technical-parameters)
- Modify scoring? → [README.md](README.md#scoring-weights)

### Troubleshooting
- Dashboard won't start? → [TROUBLESHOOTING.md](TROUBLESHOOTING.md#dashboard-wont-start)
- No data? → [TROUBLESHOOTING.md](TROUBLESHOOTING.md#no-data-available-for-symbol)
- Errors? → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Understanding
- How does it work? → [README.md](README.md#how-it-works)
- Architecture? → [ARCHITECTURE.md](ARCHITECTURE.md)
- What's implemented? → [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

### Development
- Code structure? → [ARCHITECTURE.md](ARCHITECTURE.md#module-dependencies)
- Add features? → [README.md](README.md#contributing)
- Scale up? → [ARCHITECTURE.md](ARCHITECTURE.md#scalability-architecture)

## Command Cheat Sheet

```bash
# Setup (one time)
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux
pip install -r requirements.txt

# Verify installation
python verify_setup.py

# Run dashboard
streamlit run app.py

# Run analysis manually
python scheduler.py now

# Start scheduler (auto-run daily)
python scheduler.py

# Test individual modules
python database.py
python data_fetcher.py
python technical_analysis.py
python scoring_engine.py

# Windows shortcuts
setup.bat              # One-time setup
run_dashboard.bat      # Start dashboard
run_analysis.bat       # Run analysis
```

## Support Resources

### Documentation
1. This index (you are here)
2. README.md for features
3. TROUBLESHOOTING.md for issues
4. ARCHITECTURE.md for deep dive

### Code
- Inline comments in each module
- Test code in `if __name__ == "__main__"` blocks
- Configuration in config.py

### Logs
- Check `data/analyzer.log` for errors
- Enable DEBUG mode in config.py for details

### External Resources
- Streamlit docs: https://docs.streamlit.io/
- yfinance docs: https://pypi.org/project/yfinance/
- pandas docs: https://pandas.pydata.org/

## Document Change Log

| File | Last Updated | Major Changes |
|------|--------------|---------------|
| README.md | 2025-12-07 | Complete documentation |
| QUICKSTART.md | 2025-12-07 | Initial creation |
| ARCHITECTURE.md | 2025-12-07 | System design |
| PROJECT_SUMMARY.md | 2025-12-07 | Project overview |
| TROUBLESHOOTING.md | 2025-12-07 | Issue resolution |
| INDEX.md | 2025-12-07 | Navigation guide |

## Next Steps

**New User?** → Start with [QUICKSTART.md](QUICKSTART.md)

**Existing User?** → Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for any issues

**Developer?** → Review [ARCHITECTURE.md](ARCHITECTURE.md)

**Need Help?** → Find your issue in [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

Happy trading! 📈
