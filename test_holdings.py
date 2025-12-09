"""Test script to add and retrieve holdings"""
from database import StockDatabase
from datetime import datetime
import pandas as pd

# Initialize database
db = StockDatabase()

# Add a test holding
print("Adding test holding...")
try:
    db.add_holding(
        symbol='AAPL',
        purchase_date=datetime.now().strftime('%Y-%m-%d'),
        purchase_price=150.50,
        quantity=10
    )
    print("✓ Successfully added holding")
except Exception as e:
    print(f"✗ Error adding holding: {e}")

# Retrieve holdings
print("\nRetrieving holdings...")
holdings = db.get_active_holdings()

if not holdings.empty:
    print(f"\n✓ Found {len(holdings)} active holdings:")
    print(holdings)
else:
    print("✗ No holdings found")

# Check all holdings (including closed)
all_holdings = pd.read_sql('SELECT * FROM holdings', db.engine)
print(f"\nTotal holdings in database: {len(all_holdings)}")
if not all_holdings.empty:
    print(all_holdings)
