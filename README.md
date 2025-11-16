# Forex Trading Signals API

A comprehensive Python Flask API that provides forex trading signals from multiple free data sources. Perfect for intraday trading with support for numerous trades throughout a single day.

## 🌟 Features

- **Multiple Data Sources**: Integrates with 4 free forex data providers
  - TradingView TA (Technical Analysis)
  - Alpha Vantage (Real-time & Intraday Data)
  - Twelve Data (Comprehensive Forex Data)
  - TrueFX (Historical Tick Data)
  
- **Swagger Documentation**: Interactive API documentation at `/swagger/`
- **Intraday Trading Focus**: Optimized for multiple trades throughout a single day
- **Aggregated Signals**: Combine signals from all sources for consensus recommendations
- **Well Documented**: Comprehensive code comments for beginners
- **Vercel Ready**: Configured for seamless deployment on Vercel via GitHub

## 📋 Table of Contents

- [Installation](#installation)
- [Local Development](#local-development)
- [API Endpoints](#api-endpoints)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for deployment)

### Setup Steps

1. **Clone the repository**:
```bash
git clone <your-repo-url>
cd "Vercel Deployment"
```

2. **Create a virtual environment** (recommended):
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## 💻 Local Development

### Running the Application

1. **Start the Flask development server**:
```bash
python app.py
```

2. **Access the API**:
   - API Base URL: `http://localhost:5000/api`
   - Swagger Documentation: `http://localhost:5000/swagger/`
   - Health Check: `http://localhost:5000/api/health`

### Testing Endpoints

You can test the API using:
- **Swagger UI**: Visit `http://localhost:5000/swagger/` for interactive testing
- **cURL**: Use command line tools
- **Postman**: Import the API endpoints
- **Python requests**: Use the `requests` library

### Example: Testing with cURL

```bash
# Health check
curl http://localhost:5000/api/health

# Get TradingView signals
curl http://localhost:5000/api/tradingview/signals/EURUSD?interval=5min

# Get aggregated signals
curl http://localhost:5000/api/aggregated/signals/EURUSD
```

## 📡 API Endpoints

### Quick Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/tradingview/signals/<symbol>` | GET | TradingView TA signals |
| `/api/tradingview/signals?symbols=...` | GET | Multiple TradingView signals |
| `/api/alphavantage/realtime/<symbol>` | GET | Alpha Vantage real-time rate |
| `/api/alphavantage/intraday/<symbol>` | GET | Alpha Vantage intraday data |
| `/api/twelvedata/quote/<symbol>` | GET | Twelve Data real-time quote |
| `/api/twelvedata/timeseries/<symbol>` | GET | Twelve Data time series |
| `/api/truefx/latest/<symbol>` | GET | TrueFX latest data info |
| `/api/truefx/intraday/<symbol>` | GET | TrueFX intraday signals |
| `/api/aggregated/signals/<symbol>` | GET | Aggregated signals from all sources |

### Detailed Documentation

For complete endpoint documentation, see [ENDPOINTS_DOCUMENTATION.md](./ENDPOINTS_DOCUMENTATION.md)

## 🚢 Deployment

### Deploying to Render.com (Recommended for Python Flask)

See [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md) for complete Render.com deployment guide.

**Quick Steps**:
1. Push code to GitHub
2. Create account at [render.com](https://render.com)
3. Create new Web Service
4. Connect GitHub repository
5. Render will auto-detect `render.yaml` and deploy

**Files for Render**:
- `Procfile` - Start command
- `render.yaml` - Deployment configuration
- `gunicorn_config.py` - Production server config

### Deploying to Vercel via GitHub

1. **Push to GitHub**:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

2. **Connect to Vercel**:
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will automatically detect the `vercel.json` configuration

3. **Deploy**:
   - Vercel will automatically build and deploy your application
   - The API will be available at `https://your-project.vercel.app`

### Deployment Options

**Render.com** (Recommended):
- Better for Python Flask applications
- Traditional web service (always on with paid plans)
- Uses Gunicorn for production
- See `RENDER_DEPLOYMENT.md` for details

**Vercel**:
- Serverless functions
- Good for quick deployments
- May have cold starts

### Vercel Configuration

The project includes `vercel.json` configured for Python Flask deployment:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

### Environment Variables (Optional)

If you want to use your own API keys, you can set them in Vercel:

1. Go to your project settings in Vercel
2. Navigate to "Environment Variables"
3. Add variables if needed (currently using provided/default keys)

## 📁 Project Structure

```
Vercel Deployment/
├── api/
│   └── index.py              # Vercel serverless function entry point
├── endpoints/
│   ├── __init__.py
│   ├── tradingview_endpoint.py    # TradingView TA endpoints
│   ├── alphavantage_endpoint.py   # Alpha Vantage endpoints
│   ├── twelvedata_endpoint.py     # Twelve Data endpoints
│   ├── truefx_endpoint.py          # TrueFX endpoints
│   └── aggregated_endpoint.py      # Aggregated signals endpoint
├── services/
│   ├── __init__.py
│   ├── tradingview_service.py     # TradingView TA service logic
│   ├── alphavantage_service.py    # Alpha Vantage service logic
│   ├── twelvedata_service.py        # Twelve Data service logic
│   └── truefx_service.py            # TrueFX service logic
├── utils/
│   └── __init__.py
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── vercel.json              # Vercel deployment configuration
├── README.md               # This file
└── ENDPOINTS_DOCUMENTATION.md  # Detailed API documentation
```

## ⚙️ Configuration

### API Keys

The project uses the following API keys:

- **Twelve Data**: `217116a3a840410197f04f747300b3b1` (provided)
- **Alpha Vantage**: Uses demo key (you can replace with your own)
- **TradingView TA**: No API key required
- **TrueFX**: No API key required (CSV downloads)

### Rate Limits

- **Alpha Vantage**: 5 calls/minute, 500 calls/day (free tier)
- **Twelve Data**: 800 API calls/day (free tier)
- **TradingView TA**: No official limits (use responsibly)
- **TrueFX**: No limits (CSV downloads)

## 📖 Usage Examples

### Python Example

```python
import requests

# Base URL (change for production)
BASE_URL = "http://localhost:5000/api"

# Get TradingView signals
response = requests.get(f"{BASE_URL}/tradingview/signals/EURUSD?interval=5min")
data = response.json()
print(f"Recommendation: {data['summary']['recommendation']}")

# Get aggregated signals
response = requests.get(f"{BASE_URL}/aggregated/signals/EURUSD")
data = response.json()
print(f"Consensus: {data['consensus']['overall_recommendation']}")
print(f"Agreement: {data['consensus']['agreement_level']}")
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:5000/api';

// Get intraday data for multiple trades
async function getIntradaySignals(symbol) {
  try {
    const response = await axios.get(
      `${BASE_URL}/twelvedata/timeseries/${symbol}?interval=5min&outputsize=200`
    );
    return response.data;
  } catch (error) {
    console.error('Error:', error);
  }
}

// Get aggregated signals
async function getAggregatedSignals(symbol) {
  try {
    const response = await axios.get(
      `${BASE_URL}/aggregated/signals/${symbol}?interval=5min`
    );
    return response.data;
  } catch (error) {
    console.error('Error:', error);
  }
}
```

## 🎯 Use Cases

### Intraday Trading (Multiple Trades/Day)

Use short intervals (1min, 5min, 15min) and monitor signals throughout the day:

```bash
# Get 5-minute signals for EURUSD
GET /api/twelvedata/timeseries/EURUSD?interval=5min&outputsize=200

# Get aggregated signals every 5 minutes
GET /api/aggregated/signals/EURUSD?interval=5min
```

### Single Trade Analysis

Get comprehensive analysis before entering a trade:

```bash
# Get consensus from all sources
GET /api/aggregated/signals/EURUSD

# Compare individual sources
GET /api/tradingview/signals/EURUSD
GET /api/twelvedata/timeseries/EURUSD
```

### Session-Based Trading

Use TrueFX endpoint for session-specific signals:

```bash
# Get signals for specific date
GET /api/truefx/intraday/EURUSD?date=2024-01-15
```

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check that you're using the correct Python version (3.8+)

2. **API Rate Limits**:
   - Alpha Vantage: Wait 12 seconds between calls (5 calls/minute)
   - Twelve Data: Monitor your daily usage (800 calls/day)

3. **Vercel Deployment Issues**:
   - Ensure `vercel.json` is in the root directory
   - Check that `api/index.py` exists and imports `app` correctly
   - Verify all dependencies are in `requirements.txt`

4. **Port Already in Use**:
   - Change the port in `app.py`: `app.run(port=5001)`
   - Or kill the process using port 5000

## 📚 Learning Resources

This project is designed for beginners with extensive comments. Key concepts:

- **Flask REST API**: Web framework for building APIs
- **Flask-RESTX**: Extension for building REST APIs with Swagger
- **Service Layer Pattern**: Separating business logic from API endpoints
- **Namespace Organization**: Organizing endpoints into logical groups
- **Error Handling**: Proper error responses and logging

## 🤝 Contributing

This is an independent project. To extend it:

1. Add new data sources in `services/`
2. Create corresponding endpoints in `endpoints/`
3. Update documentation
4. Test thoroughly

## 📝 License

This project is provided as-is for educational purposes.

## 🆘 Support

For issues or questions:
1. Check the [ENDPOINTS_DOCUMENTATION.md](./ENDPOINTS_DOCUMENTATION.md)
2. Review code comments (extensive documentation in code)
3. Check Swagger UI at `/swagger/` for interactive testing

## 🎓 For Beginners

This project is designed to be educational:

- **Extensive Comments**: Every function and class has detailed comments
- **Clear Structure**: Organized into logical modules
- **Swagger Documentation**: Interactive API testing
- **Error Handling**: Proper error messages and logging
- **Best Practices**: Follows Python and Flask best practices

Start by:
1. Reading `app.py` to understand the main application
2. Exploring `endpoints/` to see how API endpoints are structured
3. Reviewing `services/` to understand business logic
4. Testing endpoints using Swagger UI

---

**Happy Trading! 📈**

