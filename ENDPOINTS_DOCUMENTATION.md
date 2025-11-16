# Forex Trading Signals API - Endpoints Documentation

This document provides detailed documentation for all API endpoints, including their logic, parameters, and usage examples.

## Table of Contents

1. [Overview](#overview)
2. [Base URL](#base-url)
3. [TradingView TA Endpoints](#tradingview-ta-endpoints)
4. [Alpha Vantage Endpoints](#alpha-vantage-endpoints)
5. [Twelve Data Endpoints](#twelve-data-endpoints)
6. [TrueFX Endpoints](#truefx-endpoints)
7. [Aggregated Endpoints](#aggregated-endpoints)
8. [Health Check](#health-check)

---

## Overview

This API provides forex trading signals from multiple free data sources:
- **TradingView TA**: Technical analysis using TradingView algorithms
- **Alpha Vantage**: Real-time and intraday forex data
- **Twelve Data**: Comprehensive forex data with WebSocket support
- **TrueFX**: Historical tick data for backtesting

All endpoints are optimized for **intraday trading** with support for multiple trades throughout a single day.

---

## Base URL

- **Local Development**: `http://localhost:5000/api`
- **Vercel Deployment**: `https://your-project.vercel.app/api`
- **Swagger Documentation**: `/swagger/` (e.g., `http://localhost:5000/swagger/`)

---

## TradingView TA Endpoints

### 1. Get Trading Signals for Single Pair

**Endpoint**: `GET /api/tradingview/signals/<symbol>`

**Description**: 
Fetches technical analysis signals for a single forex pair using TradingView TA library. This endpoint provides comprehensive technical indicators including RSI, MACD, Moving Averages, and generates buy/sell/neutral recommendations.

**Logic Flow**:
1. Accepts forex pair symbol (e.g., EURUSD)
2. Converts symbol to TradingView format (FX:EURUSD)
3. Fetches technical analysis data from TradingView TA
4. Extracts indicators (RSI, MACD, SMAs, EMAs)
5. Generates summary recommendation based on indicator signals
6. Returns structured response with all indicators and signals

**Parameters**:
- `symbol` (path, required): Forex pair symbol (e.g., EURUSD, GBPUSD, USDJPY)
- `interval` (query, optional): Time interval for analysis
  - Options: `1min`, `5min`, `15min`, `30min`, `1hour`, `4hour`, `1day`
  - Default: `15min`

**Response Structure**:
```json
{
  "source": "TradingView TA",
  "symbol": "EURUSD",
  "tradingview_symbol": "FX:EURUSD",
  "interval": "15min",
  "timestamp": "2024-01-15T10:30:00",
  "summary": {
    "recommendation": "BUY",
    "buy_signals": 8,
    "sell_signals": 2,
    "neutral_signals": 1
  },
  "indicators": {
    "rsi": 65.5,
    "macd": 0.0012,
    "macd_signal": 0.0010,
    "macd_histogram": 0.0002,
    "sma_20": 1.08500,
    "sma_50": 1.08300,
    "ema_20": 1.08520,
    "ema_50": 1.08350,
    "close": 1.08550,
    "volume": 1250000
  }
}
```

**Example Requests**:
```bash
# Get signals for EURUSD with default 15min interval
GET /api/tradingview/signals/EURUSD

# Get signals for GBPUSD with 5min interval (better for intraday)
GET /api/tradingview/signals/GBPUSD?interval=5min

# Get signals for USDJPY with 1min interval (high-frequency trading)
GET /api/tradingview/signals/USDJPY?interval=1min
```

**Use Cases**:
- Single pair analysis before entering a trade
- Quick signal check for a specific currency pair
- Technical indicator analysis

---

### 2. Get Trading Signals for Multiple Pairs

**Endpoint**: `GET /api/tradingview/signals?symbols=<symbol1,symbol2,...>`

**Description**: 
Fetches trading signals for multiple forex pairs in a single request. Useful for comparing signals across different currency pairs.

**Logic Flow**:
1. Accepts comma-separated list of symbols
2. Processes each symbol individually
3. Fetches signals for all symbols
4. Returns aggregated response with signals for all pairs

**Parameters**:
- `symbols` (query, required): Comma-separated list of forex pairs (e.g., EURUSD,GBPUSD,USDJPY)
- `interval` (query, optional): Time interval (default: `15min`)

**Response Structure**:
```json
{
  "source": "TradingView TA",
  "interval": "15min",
  "timestamp": "2024-01-15T10:30:00",
  "signals": {
    "EURUSD": { /* signal data */ },
    "GBPUSD": { /* signal data */ },
    "USDJPY": { /* signal data */ }
  }
}
```

**Example Request**:
```bash
GET /api/tradingview/signals?symbols=EURUSD,GBPUSD,USDJPY&interval=5min
```

**Use Cases**:
- Comparing multiple pairs simultaneously
- Portfolio analysis across different currencies
- Finding the best trading opportunity among multiple pairs

---

## Alpha Vantage Endpoints

### 1. Get Real-Time Exchange Rate

**Endpoint**: `GET /api/alphavantage/realtime/<symbol>`

**Description**: 
Fetches real-time exchange rate between two currencies using Alpha Vantage's free API. Provides current rate and basic signal generation.

**Logic Flow**:
1. Parses symbol into base and quote currencies (e.g., EURUSD → EUR, USD)
2. Calls Alpha Vantage CURRENCY_EXCHANGE_RATE API
3. Retrieves current exchange rate
4. Generates basic trading signal based on rate
5. Returns rate and signal information

**Parameters**:
- `symbol` (path, required): Forex pair symbol in 6-character format (e.g., EURUSD)

**Response Structure**:
```json
{
  "source": "Alpha Vantage",
  "symbol": "EURUSD",
  "from_currency": "EUR",
  "to_currency": "USD",
  "exchange_rate": 1.08550,
  "last_refreshed": "2024-01-15 10:30:00",
  "timezone": "UTC",
  "signal": {
    "recommendation": "NEUTRAL",
    "confidence": "LOW",
    "note": "Basic signal generation. Use intraday data for more accurate signals."
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

**Example Request**:
```bash
GET /api/alphavantage/realtime/EURUSD
```

**Use Cases**:
- Quick rate check
- Basic signal for immediate trading decision
- Rate monitoring

**Note**: Alpha Vantage free tier has rate limits (5 calls/minute, 500 calls/day). For more detailed analysis, use the intraday endpoint.

---

### 2. Get Intraday Data (Multiple Trades)

**Endpoint**: `GET /api/alphavantage/intraday/<symbol>`

**Description**: 
Fetches intraday price data at specified intervals. **Optimized for multiple trades throughout a single day**. This endpoint provides price data points and generates trading signals based on price movements and moving averages.

**Logic Flow**:
1. Parses symbol into currencies
2. Calls Alpha Vantage FX_INTRADAY API
3. Retrieves time series data at specified interval
4. Processes data points (open, high, low, close)
5. Calculates moving averages (SMA 20)
6. Generates signals based on:
   - Price momentum (price change percentage)
   - Moving average position
   - Support/resistance levels
7. Returns data points and comprehensive signals

**Parameters**:
- `symbol` (path, required): Forex pair symbol (e.g., EURUSD)
- `interval` (query, optional): Time interval
  - Options: `1min`, `5min`, `15min`, `30min`, `60min`, `1hour`
  - Default: `5min` (optimal for intraday trading)

**Response Structure**:
```json
{
  "source": "Alpha Vantage",
  "symbol": "EURUSD",
  "interval": "5min",
  "metadata": {
    "information": "Forex Intraday (5min) open, high, low, close prices",
    "from_symbol": "EUR",
    "to_symbol": "USD",
    "last_refreshed": "2024-01-15 10:30:00",
    "timezone": "UTC"
  },
  "data_points": [
    {
      "timestamp": "2024-01-15 10:30:00",
      "open": 1.08500,
      "high": 1.08550,
      "low": 1.08480,
      "close": 1.08520
    }
    // ... more data points
  ],
  "signals": {
    "recommendation": "BUY",
    "confidence": "HIGH",
    "price_change": 0.00020,
    "price_change_percent": 0.0184,
    "current_price": 1.08520,
    "previous_price": 1.08500
  }
}
```

**Example Requests**:
```bash
# Get 5-minute data (good for intraday trading)
GET /api/alphavantage/intraday/EURUSD?interval=5min

# Get 1-minute data (high-frequency trading)
GET /api/alphavantage/intraday/GBPUSD?interval=1min

# Get 15-minute data (swing trading within day)
GET /api/alphavantage/intraday/USDJPY?interval=15min
```

**Use Cases**:
- **Multiple trades in a single day**: Analyze price movements throughout the day
- **Day trading**: Get signals for different time periods
- **Entry/exit timing**: Identify optimal entry and exit points
- **Trend analysis**: Track price trends within a trading day

**Signal Generation Logic**:
- **BUY Signal**: Price increased by >0.1% OR current price > SMA 20
- **SELL Signal**: Price decreased by >0.1% OR current price < SMA 20
- **NEUTRAL Signal**: Price change <0.1% and price near SMA

---

## Twelve Data Endpoints

### 1. Get Real-Time Quote

**Endpoint**: `GET /api/twelvedata/quote/<symbol>`

**Description**: 
Fetches real-time quote from Twelve Data API. Provides current price, price change, volume, and generates trading signal.

**Logic Flow**:
1. Formats symbol to Twelve Data format (EUR/USD)
2. Calls Twelve Data quote API
3. Retrieves current quote data
4. Calculates price change and percentage change
5. Generates signal based on price movement
6. Returns quote and signal

**Parameters**:
- `symbol` (path, required): Forex pair symbol (e.g., EURUSD or EUR/USD)

**Response Structure**:
```json
{
  "source": "Twelve Data",
  "symbol": "EURUSD",
  "formatted_symbol": "EUR/USD",
  "quote": {
    "symbol": "EUR/USD",
    "name": "Euro/US Dollar",
    "exchange": "FX",
    "currency": "USD",
    "datetime": "2024-01-15 10:30:00",
    "timestamp": 1705315800,
    "open": 1.08500,
    "high": 1.08550,
    "low": 1.08480,
    "close": 1.08520,
    "volume": 1250000,
    "previous_close": 1.08490,
    "change": 0.00030,
    "percent_change": 0.0277
  },
  "signal": {
    "recommendation": "BUY",
    "confidence": "MEDIUM",
    "price_change_percent": 0.0277,
    "current_price": 1.08520,
    "previous_close": 1.08490
  }
}
```

**Example Request**:
```bash
GET /api/twelvedata/quote/EURUSD
```

**Use Cases**:
- Real-time price monitoring
- Quick signal check
- Price change tracking

---

### 2. Get Time Series Data (Intraday Trading)

**Endpoint**: `GET /api/twelvedata/timeseries/<symbol>`

**Description**: 
Fetches time series data from Twelve Data. **Designed for multiple trades throughout a single day**. Provides comprehensive technical analysis including moving averages, support/resistance levels, and detailed trading signals.

**Logic Flow**:
1. Formats symbol to Twelve Data format
2. Calls Twelve Data time_series API
3. Retrieves historical price data at specified interval
4. Processes data points
5. Calculates technical indicators:
   - Simple Moving Averages (SMA 20, SMA 50)
   - Support and resistance levels
   - Price momentum
6. Generates comprehensive signals based on multiple factors:
   - Price momentum
   - Moving average crossovers
   - Support/resistance analysis
7. Returns data points and detailed signals

**Parameters**:
- `symbol` (path, required): Forex pair symbol (e.g., EURUSD)
- `interval` (query, optional): Time interval
  - Options: `1min`, `5min`, `15min`, `30min`, `45min`, `1h`, `2h`, `4h`, `1day`
  - Default: `5min` (optimal for intraday trading)
- `outputsize` (query, optional): Number of data points
  - Default: `100`
  - Maximum: `5000`
  - More data points = more historical context

**Response Structure**:
```json
{
  "source": "Twelve Data",
  "symbol": "EURUSD",
  "formatted_symbol": "EUR/USD",
  "interval": "5min",
  "metadata": {
    "symbol": "EUR/USD",
    "interval": "5min",
    "currency_base": "EUR",
    "currency_quote": "USD",
    "exchange": "FX",
    "type": "Forex"
  },
  "data_points": [
    {
      "datetime": "2024-01-15 10:30:00",
      "open": 1.08500,
      "high": 1.08550,
      "low": 1.08480,
      "close": 1.08520,
      "volume": 1250000
    }
    // ... more data points
  ],
  "signals": {
    "recommendation": "BUY",
    "confidence": "HIGH",
    "price_change": 0.00020,
    "price_change_percent": 0.0184,
    "current_price": 1.08520,
    "previous_price": 1.08500,
    "sma_20": 1.08450,
    "sma_50": 1.08300,
    "support": 1.08400,
    "resistance": 1.08600,
    "reasons": [
      "Positive price momentum",
      "Price above both moving averages (bullish)",
      "Price above midpoint of support/resistance range"
    ]
  }
}
```

**Example Requests**:
```bash
# Get 5-minute data with 100 data points (default)
GET /api/twelvedata/timeseries/EURUSD?interval=5min

# Get 1-minute data with 200 data points (more granular)
GET /api/twelvedata/timeseries/GBPUSD?interval=1min&outputsize=200

# Get 15-minute data with 500 data points (more history)
GET /api/twelvedata/timeseries/USDJPY?interval=15min&outputsize=500
```

**Use Cases**:
- **Intraday trading**: Multiple trades throughout the day
- **Technical analysis**: Comprehensive indicator analysis
- **Entry/exit points**: Identify optimal trading times
- **Trend following**: Track and follow trends

**Signal Generation Logic**:
1. **Price Momentum**: 
   - BUY if price change > 0.1%
   - SELL if price change < -0.1%
2. **Moving Average Crossover**:
   - BUY if price > SMA20 > SMA50 (bullish alignment)
   - SELL if price < SMA20 < SMA50 (bearish alignment)
3. **Support/Resistance**:
   - BUY if price above midpoint of support/resistance range
   - Additional confirmation from price position

---

## TrueFX Endpoints

### 1. Get Latest Available Data

**Endpoint**: `GET /api/truefx/latest/<symbol>`

**Description**: 
Returns information about the latest available data from TrueFX. TrueFX provides historical tick data in CSV format for download.

**Logic Flow**:
1. Formats symbol to TrueFX format (EUR/USD)
2. Checks if pair is available on TrueFX
3. Returns data availability information
4. Provides structure for CSV data format

**Parameters**:
- `symbol` (path, required): Forex pair symbol (e.g., EURUSD)
- `year` (query, optional): Year for data (default: current year)
- `month` (query, optional): Month for data (default: current month)

**Response Structure**:
```json
{
  "source": "TrueFX",
  "symbol": "EURUSD",
  "formatted_symbol": "EUR/USD",
  "year": 2024,
  "month": 1,
  "data_available": true,
  "note": "TrueFX provides historical CSV downloads. To use real data, download CSV files from https://www.truefx.com and parse them.",
  "sample_structure": {
    "format": "CSV with columns: Timestamp, Bid, Ask",
    "example": "2024-01-15 10:30:45.123,1.08500,1.08505"
  }
}
```

**Example Request**:
```bash
GET /api/truefx/latest/EURUSD?year=2024&month=1
```

**Note**: TrueFX provides CSV downloads. To get actual tick data, you need to download CSV files from TrueFX website and parse them.

---

### 2. Get Intraday Trading Signals

**Endpoint**: `GET /api/truefx/intraday/<symbol>`

**Description**: 
Generates intraday trading signals from TrueFX data structure. **Designed for multiple trades throughout a single day** across different trading sessions.

**Logic Flow**:
1. Formats symbol to TrueFX format
2. Parses target date
3. Generates signals for different times throughout the day
4. Identifies signals for different trading sessions:
   - Asian session (00:00)
   - European session (08:00)
   - US session (13:00, 17:00)
   - Session transitions (21:00)
5. Returns signals for each time period

**Parameters**:
- `symbol` (path, required): Forex pair symbol (e.g., EURUSD)
- `date` (query, optional): Date in YYYY-MM-DD format (default: today)

**Response Structure**:
```json
{
  "source": "TrueFX",
  "symbol": "EURUSD",
  "formatted_symbol": "EUR/USD",
  "date": "2024-01-15",
  "signals": {
    "date": "2024-01-15",
    "symbol": "EUR/USD",
    "total_signals": 5,
    "signals": [
      {
        "time": "00:00",
        "session": "Asian session start",
        "recommendation": "NEUTRAL",
        "confidence": "MEDIUM",
        "note": "Signal for Asian session start. In production, this would be calculated from actual tick data."
      },
      {
        "time": "08:00",
        "session": "European session start",
        "recommendation": "BUY",
        "confidence": "HIGH",
        "note": "Signal for European session start."
      }
      // ... more signals
    ],
    "note": "These are sample signals. To get real signals, download and parse TrueFX CSV files for the specified date."
  }
}
```

**Example Request**:
```bash
GET /api/truefx/intraday/EURUSD?date=2024-01-15
```

**Use Cases**:
- **Session-based trading**: Trade during specific market sessions
- **Multiple daily trades**: Get signals for different times
- **Historical analysis**: Analyze past trading days
- **Backtesting**: Test strategies on historical data

**Note**: In production, you would download TrueFX CSV files and parse actual tick data to generate real signals.

---

## Aggregated Endpoints

### Get Aggregated Signals from All Sources

**Endpoint**: `GET /api/aggregated/signals/<symbol>`

**Description**: 
Combines trading signals from all four data sources (TradingView TA, Alpha Vantage, Twelve Data, TrueFX) and generates a consensus recommendation. This is the most comprehensive endpoint for getting a complete market view.

**Logic Flow**:
1. Fetches signals from all four sources in parallel:
   - TradingView TA
   - Alpha Vantage (intraday data)
   - Twelve Data (time series)
   - TrueFX (intraday signals)
2. Extracts recommendations from each source
3. Calculates consensus:
   - Counts votes for BUY, SELL, NEUTRAL
   - Determines overall recommendation (majority vote)
   - Calculates average confidence
   - Determines agreement level between sources
4. Generates human-readable summary
5. Returns comprehensive aggregated analysis

**Parameters**:
- `symbol` (path, required): Forex pair symbol (e.g., EURUSD)
- `interval` (query, optional): Time interval (default: `15min`)

**Response Structure**:
```json
{
  "symbol": "EURUSD",
  "timestamp": "2024-01-15T10:30:00",
  "interval": "15min",
  "sources": {
    "tradingview": { /* TradingView signal data */ },
    "alphavantage": { /* Alpha Vantage signal data */ },
    "twelvedata": { /* Twelve Data signal data */ },
    "truefx": { /* TrueFX signal data */ }
  },
  "consensus": {
    "overall_recommendation": "BUY",
    "buy_votes": 3,
    "sell_votes": 0,
    "neutral_votes": 1,
    "total_sources": 4,
    "average_confidence": "HIGH",
    "agreement_level": "STRONG_AGREEMENT"
  },
  "summary": "Consensus Recommendation: BUY | Agreement Level: STRONG_AGREEMENT | Votes - BUY: 3, SELL: 0, NEUTRAL: 1 | Average Confidence: HIGH | TradingView: BUY | Alphavantage: BUY | Twelvedata: BUY"
}
```

**Example Request**:
```bash
GET /api/aggregated/signals/EURUSD?interval=5min
```

**Use Cases**:
- **Comprehensive analysis**: Get complete market view from all sources
- **Decision making**: Make trading decisions based on consensus
- **Signal validation**: Verify signals across multiple sources
- **Risk management**: Use agreement level to assess signal reliability

**Consensus Logic**:
- **Overall Recommendation**: Majority vote (BUY/SELL/NEUTRAL)
- **Agreement Levels**:
  - `STRONG_AGREEMENT`: ≥75% of sources agree
  - `MODERATE_AGREEMENT`: 50-74% of sources agree
  - `MIXED_SIGNALS`: <50% agreement
  - `SINGLE_SOURCE`: Only one source available
  - `NO_DATA`: No sources available

**Confidence Calculation**:
- Maps confidence levels: LOW=1, MEDIUM=2, HIGH=3
- Calculates average across all sources
- Returns average confidence level

---

## Health Check

**Endpoint**: `GET /api/health`

**Description**: 
Simple health check endpoint to verify the API is running.

**Response**:
```json
{
  "status": "healthy",
  "message": "Forex Trading Signals API is running",
  "version": "1.0"
}
```

**Use Cases**:
- Deployment verification
- Monitoring and health checks
- API availability testing

---

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200 OK`: Successful request
- `400 Bad Request`: Invalid parameters
- `500 Internal Server Error`: Server error

Error responses include:
```json
{
  "error": "Error message",
  "source": "Source name",
  "timestamp": "2024-01-15T10:30:00"
}
```

---

## Rate Limits

**Alpha Vantage**:
- Free tier: 5 calls/minute, 500 calls/day
- Use intraday endpoint for more detailed analysis

**Twelve Data**:
- Free tier: 800 API calls/day
- API key: 217116a3a840410197f04f747300b3b1

**TradingView TA**:
- No official rate limits, but use responsibly

**TrueFX**:
- Free historical CSV downloads
- No API rate limits

---

## Best Practices

1. **For Intraday Trading (Multiple Trades/Day)**:
   - Use intervals: `1min`, `5min`, or `15min`
   - Use aggregated endpoint for comprehensive view
   - Monitor signals throughout the day

2. **For Single Trade Analysis**:
   - Use individual source endpoints
   - Compare signals from different sources
   - Check consensus for validation

3. **For High-Frequency Trading**:
   - Use `1min` or `5min` intervals
   - Use Twelve Data or Alpha Vantage intraday endpoints
   - Monitor rate limits

4. **For Session-Based Trading**:
   - Use TrueFX intraday endpoint
   - Focus on specific trading sessions
   - Analyze session transitions

---

## Notes

- All timestamps are in UTC
- All prices are in the quote currency
- Symbols can be in various formats (EURUSD, EUR/USD) - the API handles conversion
- The API is designed to be independent and not modify global Python libraries
- All dependencies are specified in `requirements.txt`

