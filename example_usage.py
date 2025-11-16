"""
Example Usage Script
This script demonstrates how to use the Forex Trading Signals API.

Run this script after starting the Flask server to test the API endpoints.
Make sure the Flask server is running on http://localhost:5000
"""
import requests
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:5000/api"

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_health_check():
    """Test the health check endpoint."""
    print_section("Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_tradingview_signal():
    """Test TradingView TA signal endpoint."""
    print_section("TradingView TA Signal")
    try:
        symbol = "EURUSD"
        interval = "15min"
        response = requests.get(f"{BASE_URL}/tradingview/signals/{symbol}?interval={interval}")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        
        if 'summary' in data:
            print(f"\nSymbol: {data.get('symbol', 'N/A')}")
            print(f"Recommendation: {data['summary'].get('recommendation', 'N/A')}")
            print(f"Buy Signals: {data['summary'].get('buy_signals', 0)}")
            print(f"Sell Signals: {data['summary'].get('sell_signals', 0)}")
            if 'indicators' in data and 'rsi' in data['indicators']:
                print(f"RSI: {data['indicators'].get('rsi', 'N/A')}")
        else:
            print(f"Response: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_alphavantage_intraday():
    """Test Alpha Vantage intraday endpoint."""
    print_section("Alpha Vantage Intraday Data")
    try:
        symbol = "EURUSD"
        interval = "5min"
        response = requests.get(f"{BASE_URL}/alphavantage/intraday/{symbol}?interval={interval}")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        
        if 'signals' in data:
            print(f"\nSymbol: {data.get('symbol', 'N/A')}")
            print(f"Recommendation: {data['signals'].get('recommendation', 'N/A')}")
            print(f"Confidence: {data['signals'].get('confidence', 'N/A')}")
            print(f"Price Change: {data['signals'].get('price_change_percent', 0)}%")
        else:
            print(f"Response: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_twelvedata_timeseries():
    """Test Twelve Data time series endpoint."""
    print_section("Twelve Data Time Series")
    try:
        symbol = "EURUSD"
        interval = "5min"
        response = requests.get(f"{BASE_URL}/twelvedata/timeseries/{symbol}?interval={interval}&outputsize=50")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        
        if 'signals' in data:
            print(f"\nSymbol: {data.get('symbol', 'N/A')}")
            print(f"Recommendation: {data['signals'].get('recommendation', 'N/A')}")
            print(f"Confidence: {data['signals'].get('confidence', 'N/A')}")
            if 'reasons' in data['signals']:
                print(f"Reasons: {', '.join(data['signals']['reasons'])}")
        else:
            print(f"Response: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_aggregated_signals():
    """Test aggregated signals endpoint."""
    print_section("Aggregated Signals (All Sources)")
    try:
        symbol = "EURUSD"
        interval = "15min"
        response = requests.get(f"{BASE_URL}/aggregated/signals/{symbol}?interval={interval}")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        
        if 'consensus' in data:
            print(f"\nSymbol: {data.get('symbol', 'N/A')}")
            consensus = data['consensus']
            print(f"Overall Recommendation: {consensus.get('overall_recommendation', 'N/A')}")
            print(f"Buy Votes: {consensus.get('buy_votes', 0)}")
            print(f"Sell Votes: {consensus.get('sell_votes', 0)}")
            print(f"Neutral Votes: {consensus.get('neutral_votes', 0)}")
            print(f"Agreement Level: {consensus.get('agreement_level', 'N/A')}")
            print(f"Average Confidence: {consensus.get('average_confidence', 'N/A')}")
            print(f"\nSummary: {data.get('summary', 'N/A')}")
        else:
            print(f"Response: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Run all example tests."""
    print("\n" + "="*60)
    print("  Forex Trading Signals API - Example Usage")
    print("="*60)
    print(f"\nTesting API at: {BASE_URL}")
    print(f"Make sure the Flask server is running on http://localhost:5000")
    print(f"Start the server with: python app.py")
    
    # Run tests
    test_health_check()
    test_tradingview_signal()
    test_alphavantage_intraday()
    test_twelvedata_timeseries()
    test_aggregated_signals()
    
    print("\n" + "="*60)
    print("  Testing Complete!")
    print("="*60)
    print("\nFor more examples, check the Swagger UI at: http://localhost:5000/swagger/")
    print("For detailed documentation, see: ENDPOINTS_DOCUMENTATION.md")

if __name__ == "__main__":
    main()

