# System Architecture

## Overview Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│                     (Streamlit Dashboard)                        │
│                          app.py                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐       │
│  │   Buy    │ │   Sell   │ │  Stock   │ │  Portfolio   │       │
│  │  Recs    │ │ Signals  │ │ Analysis │ │   Overview   │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SCORING ENGINE                              │
│                     scoring_engine.py                            │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Combined Analysis (60% Tech + 40% Fundamental)        │    │
│  │  • Score calculation                                    │    │
│  │  • Recommendation generation                           │    │
│  │  • Reasoning creation                                  │    │
│  └────────────────────────────────────────────────────────┘    │
└──────────────┬────────────────────────────┬────────────────────┘
               │                            │
               ▼                            ▼
┌──────────────────────────┐   ┌───────────────────────────────┐
│   TECHNICAL ANALYSIS     │   │   FUNDAMENTAL ANALYSIS        │
│  technical_analysis.py   │   │  fundamental_analysis.py      │
│                          │   │                               │
│  • RSI                   │   │  • P/E Ratio                  │
│  • MACD                  │   │  • Profit Margin              │
│  • Moving Averages       │   │  • Revenue Growth             │
│  • Bollinger Bands       │   │  • Debt Ratios                │
│  • Volume Analysis       │   │  • ROE/ROA                    │
│  • Trend Detection       │   │  • Quality Metrics            │
│  • Signal Generation     │   │  • Valuation Category         │
└──────────────┬───────────┘   └────────────┬──────────────────┘
               │                            │
               └──────────┬─────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA FETCHER                                │
│                     data_fetcher.py                              │
│                                                                  │
│  ┌──────────────────┐              ┌──────────────────────┐    │
│  │    yfinance      │              │   Alpha Vantage      │    │
│  │  (Price Data)    │              │  (Fundamentals)      │    │
│  │   Free, No Key   │              │   25 calls/day       │    │
│  └──────────────────┘              └──────────────────────┘    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         DATABASE                                 │
│                       database.py                                │
│                      SQLite (stocks.db)                          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐     │
│  │ price_data   │  │ fundamental  │  │   technical      │     │
│  │              │  │    _data     │  │  _indicators     │     │
│  └──────────────┘  └──────────────┘  └──────────────────┘     │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │recommen-     │  │   holdings   │                            │
│  │  dations     │  │              │                            │
│  └──────────────┘  └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       AUTOMATION                                 │
│                     scheduler.py                                 │
│                                                                  │
│  • Daily scheduled runs (5:30 PM ET, Weekdays)                  │
│  • Manual trigger support                                       │
│  • Logging and error handling                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      CONFIGURATION                               │
│                       config.py                                  │
│                                                                  │
│  • Stock universe                                               │
│  • Technical parameters                                         │
│  • Scoring weights                                              │
│  • Thresholds                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Data Acquisition Flow

```
External APIs → Data Fetcher → Database
     ↓
yfinance (Price)   →  OHLCV data     → price_data table
Alpha Vantage      →  Financial data → fundamental_data table
```

### 2. Analysis Flow

```
Database → Price Data → Technical Analyzer → Indicators → Database
                                                ↓
                                          Technical Score

Database → Fundamental Data → Fundamental Analyzer → Metrics
                                                         ↓
                                                 Fundamental Score

Technical Score + Fundamental Score → Scoring Engine → Recommendation
                                                              ↓
                                                         Database
```

### 3. User Interaction Flow

```
User → Dashboard → Button Click → Trigger Analysis
                        ↓
                  Scoring Engine → Generate Recommendations
                        ↓
                    Database → Store Results
                        ↓
                    Dashboard → Display Results
```

## Module Dependencies

```
app.py
├── scoring_engine.py
│   ├── technical_analysis.py
│   │   └── pandas_ta
│   ├── fundamental_analysis.py
│   ├── data_fetcher.py
│   │   ├── yfinance
│   │   └── requests (Alpha Vantage)
│   └── database.py
│       └── sqlalchemy
├── database.py
└── config.py

scheduler.py
└── scoring_engine.py (full tree above)
```

## Component Responsibilities

### Core Analysis Components

**technical_analysis.py**
- Input: Price DataFrame (OHLCV)
- Processing: Calculate 10+ technical indicators
- Output: Indicators DataFrame + Technical Score (0-100)

**fundamental_analysis.py**
- Input: Fundamental metrics dictionary
- Processing: Evaluate financial health and growth
- Output: Fundamental Score (0-100) + Quality metrics

**scoring_engine.py**
- Input: Technical score + Fundamental score
- Processing: Weighted combination + reasoning generation
- Output: Overall score + Recommendation + Detailed reasoning

### Data Components

**data_fetcher.py**
- Input: Stock symbol
- Processing: API calls with rate limiting
- Output: Price DataFrame + Fundamental dictionary

**database.py**
- Input: Various data types
- Processing: SQL operations
- Output: Stored/Retrieved data

### Interface Components

**app.py**
- Input: User interactions
- Processing: Orchestrate analysis, format display
- Output: Interactive web dashboard

**scheduler.py**
- Input: Schedule configuration
- Processing: Trigger analysis at specified times
- Output: Updated database + logs

**config.py**
- Input: None (configuration file)
- Processing: Parameter definitions
- Output: Configuration constants

## Technical Stack

### Backend
```
Python 3.8+
├── Data Processing
│   ├── pandas (DataFrames)
│   ├── pandas_ta (Technical Analysis)
│   └── numpy (Numerical operations)
├── Data Sources
│   ├── yfinance (Market data)
│   └── requests (API calls)
├── Database
│   └── sqlalchemy + sqlite3
└── Scheduling
    └── schedule
```

### Frontend
```
Streamlit
├── plotly (Interactive charts)
└── Custom CSS (Styling)
```

### Infrastructure
```
SQLite (Database)
├── File-based
├── Zero setup
└── Easy migration path
```

## Scalability Architecture

### Current (MVP)
```
Single Python Process
    ↓
SQLite Database (single file)
    ↓
20 Stocks
    ↓
EOD Analysis
```

### Phase 2 (100+ Stocks)
```
Docker Container
    ↓
PostgreSQL Database (network)
    ↓
Apache Airflow (orchestration)
    ↓
Parallel Processing
```

### Phase 3 (Production)
```
Kubernetes Cluster
    ↓
Apache Kafka (streaming)
    ↓
Snowflake (data warehouse)
    ↓
Real-time Processing
    ↓
ML Predictions
```

## API Architecture

### Data Source Strategy

**Primary: yfinance**
- Free, unlimited
- No API key required
- Price + Fundamental data
- Rate limits: None (be respectful)

**Secondary: Alpha Vantage**
- 25 calls/day free tier
- Enhanced fundamentals
- 5 calls/minute limit
- API key required

### Rate Limiting Strategy

```python
# yfinance
for stock in stocks:
    fetch_data(stock)
    time.sleep(1)  # Respectful delay

# Alpha Vantage
for stock in stocks[:25]:  # Daily limit
    fetch_data(stock)
    time.sleep(12)  # 5 calls/minute = 12 sec delay
```

## Database Schema Design

### Normalization Strategy

**Level**: 3rd Normal Form (3NF)

**Rationale**:
- Eliminate data redundancy
- Maintain referential integrity
- Allow efficient queries
- Support future scaling

### Table Relationships

```
price_data
    ↓ (1:1)
technical_indicators (same symbol, same date)

fundamental_data
    ↓ (1:1)
recommendations (same symbol, same date)

holdings
    ↓ (Many:1)
price_data (symbol lookup)
```

### Indexing Strategy

```sql
-- Primary indexes (auto-created)
id (PRIMARY KEY)

-- Composite indexes for performance
(symbol, date) UNIQUE

-- Query optimization
symbol (for filtering)
date (for sorting)
```

## Error Handling Architecture

### Layered Error Handling

```
Level 1: API Calls
    ├── Retry logic (3 attempts)
    ├── Exponential backoff
    └── Graceful degradation

Level 2: Data Processing
    ├── Null/NaN handling
    ├── Type validation
    └── Range checking

Level 3: Database Operations
    ├── Transaction management
    ├── Constraint handling
    └── Rollback support

Level 4: User Interface
    ├── User-friendly messages
    ├── Error logging
    └── Recovery suggestions
```

### Logging Architecture

```
Logger Hierarchy
├── Root Logger (INFO)
│   ├── Console Handler (INFO)
│   └── File Handler (DEBUG)
│
├── data_fetcher (INFO)
├── technical_analysis (INFO)
├── scoring_engine (INFO)
└── scheduler (INFO)
```

## Security Architecture

### API Key Management
```
.env file (not committed)
    ↓
Environment variables
    ↓
config.py (runtime)
    ↓
Modules (access only when needed)
```

### Data Security
- No sensitive data stored
- Read-only API access
- No trading execution
- No personal information

## Performance Considerations

### Optimization Strategies

1. **Caching**: Historical data cached in database
2. **Batch Processing**: Analyze multiple stocks in single run
3. **Lazy Loading**: Load data only when needed
4. **Efficient Queries**: Indexed database queries
5. **Vectorization**: pandas operations for speed

### Performance Metrics

| Operation | Time | Notes |
|-----------|------|-------|
| Single stock analysis | ~5 sec | Including API calls |
| 20 stock portfolio | ~2-3 min | With rate limiting |
| Database query | <100ms | Indexed queries |
| Dashboard load | ~1 sec | From cached data |
| Technical indicators | <1 sec | Vectorized operations |

## Deployment Architecture

### Local Development
```
Local Machine
├── Python venv
├── SQLite database (file)
├── Streamlit server (localhost:8501)
└── Manual execution
```

### Production Deployment
```
Cloud Server (AWS/GCP/Azure)
├── Docker container
├── PostgreSQL database (RDS)
├── Streamlit Cloud / EC2
├── Airflow scheduler
└── Automated daily runs
```

## Monitoring & Observability

### Logging
- All operations logged
- Debug level for development
- INFO level for production
- File + console output

### Metrics
- Analysis completion time
- API call success rate
- Recommendation count
- Database size growth

### Alerts (Future)
- Failed analysis
- API quota exceeded
- Database errors
- Exceptional recommendations

## Backup & Recovery

### Database Backup
```
Daily: Copy stocks.db → backup/
Weekly: Compress and archive
Monthly: Off-site storage
```

### Recovery Strategy
```
Level 1: Restore from daily backup
Level 2: Re-fetch recent data from APIs
Level 3: Full historical rebuild (time-consuming)
```

## Testing Strategy

### Unit Testing
- Each module independently testable
- `if __name__ == "__main__"` blocks
- Sample data validation

### Integration Testing
- Full pipeline execution
- verify_setup.py script
- End-to-end analysis run

### Performance Testing
- Time critical operations
- Monitor API response times
- Database query optimization

## Conclusion

This architecture provides:

✅ **Modularity**: Each component independent
✅ **Scalability**: Clear upgrade path
✅ **Maintainability**: Well-organized code
✅ **Reliability**: Error handling at all levels
✅ **Performance**: Optimized for 20-100 stocks
✅ **Security**: Safe API key management
✅ **Extensibility**: Easy to add features

The system is production-ready for MVP scale and designed for future growth.
