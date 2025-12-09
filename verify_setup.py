"""
Setup Verification Script
Run this to verify your installation is correct
"""

import sys
import importlib


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("  ⚠ Warning: Python 3.8+ recommended")
        return False
    return True


def check_dependencies():
    """Check if all required packages are installed"""
    required = [
        'streamlit',
        'yfinance',
        'pandas',
        'pandas_ta',
        'requests',
        'dotenv',
        'plotly',
        'schedule',
        'sqlalchemy'
    ]

    print("\nChecking dependencies:")
    all_installed = True

    for package in required:
        try:
            if package == 'dotenv':
                importlib.import_module('dotenv')
            elif package == 'pandas_ta':
                importlib.import_module('pandas_ta')
            else:
                importlib.import_module(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - NOT INSTALLED")
            all_installed = False

    return all_installed


def check_project_files():
    """Check if all required project files exist"""
    import os

    required_files = [
        'config.py',
        'database.py',
        'data_fetcher.py',
        'technical_analysis.py',
        'fundamental_analysis.py',
        'scoring_engine.py',
        'app.py',
        'scheduler.py',
        'requirements.txt'
    ]

    print("\nChecking project files:")
    all_exist = True

    for file in required_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - MISSING")
            all_exist = False

    return all_exist


def check_data_directory():
    """Check if data directory exists"""
    import os

    print("\nChecking data directory:")

    if not os.path.exists('data'):
        print("  ! data/ directory not found - creating...")
        os.makedirs('data')
        print("  ✓ data/ directory created")
    else:
        print("  ✓ data/ directory exists")

    return True


def test_database():
    """Test database creation"""
    print("\nTesting database:")

    try:
        from database import StockDatabase
        db = StockDatabase()
        print("  ✓ Database initialized successfully")
        return True
    except Exception as e:
        print(f"  ✗ Database error: {e}")
        return False


def test_data_fetcher():
    """Test data fetching"""
    print("\nTesting data fetcher:")

    try:
        from data_fetcher import DataFetcher
        fetcher = DataFetcher()

        print("  Testing yfinance data fetch for AAPL...")
        data = fetcher.fetch_price_data("AAPL", period="5d")

        if data is not None and not data.empty:
            print(f"  ✓ Data fetched successfully ({len(data)} records)")
            return True
        else:
            print("  ✗ No data returned")
            return False

    except Exception as e:
        print(f"  ✗ Data fetcher error: {e}")
        return False


def test_technical_analysis():
    """Test technical analysis"""
    print("\nTesting technical analysis:")

    try:
        from technical_analysis import TechnicalAnalyzer
        from data_fetcher import DataFetcher

        analyzer = TechnicalAnalyzer()
        fetcher = DataFetcher()

        data = fetcher.fetch_price_data("AAPL", period="1mo")
        if data is not None and not data.empty:
            indicators = analyzer.calculate_all_indicators(data)

            if 'rsi' in indicators.columns and 'macd' in indicators.columns:
                print("  ✓ Technical indicators calculated successfully")
                return True
            else:
                print("  ✗ Indicators missing")
                return False
        else:
            print("  ✗ No data for analysis")
            return False

    except Exception as e:
        print(f"  ✗ Technical analysis error: {e}")
        return False


def main():
    """Run all checks"""
    print("=" * 60)
    print("SWING TRADE ANALYZER - SETUP VERIFICATION")
    print("=" * 60)

    results = []

    results.append(("Python Version", check_python_version()))
    results.append(("Dependencies", check_dependencies()))
    results.append(("Project Files", check_project_files()))
    results.append(("Data Directory", check_data_directory()))
    results.append(("Database", test_database()))
    results.append(("Data Fetcher", test_data_fetcher()))
    results.append(("Technical Analysis", test_technical_analysis()))

    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    all_passed = True
    for check, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{check:.<40} {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n🎉 All checks passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Run: streamlit run app.py")
        print("2. Click 'Run Daily Analysis' in the dashboard")
        print("3. View buy recommendations")
    else:
        print("\n⚠ Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Ensure you're in the virtual environment")
        print("3. Check that all project files are present")

    print("\n")


if __name__ == "__main__":
    main()
