"""
Alpha Vantage Service
This service fetches forex data from Alpha Vantage's free API.

Alpha Vantage provides free forex exchange rate data with rate limits.
Free tier allows 5 API calls per minute and 500 calls per day.
API Key: Can be set via ALPHA_VANTAGE_API_KEY environment variable
"""
import requests
from datetime import datetime, timedelta
import logging
import time
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlphaVantageService:
    """
    Service class to interact with Alpha Vantage API.
    This class handles fetching forex data and generating trading signals.
    """
    
    # Base URL for Alpha Vantage API
    BASE_URL = "https://www.alphavantage.co/query"
    
    # API Key - read from environment variable or use demo key
    # Get your free API key from: https://www.alphavantage.co/support/#api-key
    # Set ALPHA_VANTAGE_API_KEY in Render dashboard environment variables
    API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY', 'demo')
    
    @staticmethod
    def get_realtime_rate(from_currency: str, to_currency: str) -> dict:
        """
        Get real-time exchange rate between two currencies.
        
        Args:
            from_currency: Base currency (e.g., 'EUR')
            to_currency: Quote currency (e.g., 'USD')
            
        Returns:
            dict: Real-time exchange rate data
        """
        try:
            # Prepare API request parameters
            params = {
                'function': 'CURRENCY_EXCHANGE_RATE',
                'from_currency': from_currency.upper(),
                'to_currency': to_currency.upper(),
                'apikey': AlphaVantageService.API_KEY
            }
            
            # Make API request
            # Note: Alpha Vantage has rate limits, so we add a small delay
            response = requests.get(AlphaVantageService.BASE_URL, params=params, timeout=10)
            response.raise_for_status()  # Raise exception for bad status codes
            
            data = response.json()
            
            # Check for API errors
            if 'Error Message' in data:
                return {
                    'source': 'Alpha Vantage',
                    'error': data['Error Message'],
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            if 'Note' in data:
                # Rate limit exceeded
                return {
                    'source': 'Alpha Vantage',
                    'error': 'API rate limit exceeded. Please wait before making another request.',
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Extract exchange rate data
            if 'Realtime Currency Exchange Rate' in data:
                rate_data = data['Realtime Currency Exchange Rate']
                
                # Parse the data
                symbol = f"{from_currency.upper()}{to_currency.upper()}"
                exchange_rate = float(rate_data.get('5. Exchange Rate', 0))
                last_refreshed = rate_data.get('6. Last Refreshed', '')
                timezone = rate_data.get('7. Time Zone', '')
                
                # Generate simple trading signal based on price movement
                # This is a basic example - in production, you'd use more sophisticated analysis
                signal = AlphaVantageService._generate_signal(exchange_rate)
                
                return {
                    'source': 'Alpha Vantage',
                    'symbol': symbol,
                    'from_currency': from_currency.upper(),
                    'to_currency': to_currency.upper(),
                    'exchange_rate': exchange_rate,
                    'last_refreshed': last_refreshed,
                    'timezone': timezone,
                    'signal': signal,
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            return {
                'source': 'Alpha Vantage',
                'error': 'Unexpected response format',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Alpha Vantage data: {str(e)}")
            return {
                'source': 'Alpha Vantage',
                'error': f'Request failed: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error processing Alpha Vantage data: {str(e)}")
            return {
                'source': 'Alpha Vantage',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def get_intraday_data(symbol: str, interval: str = '5min') -> dict:
        """
        Get intraday (within the day) forex data.
        
        This is useful for analyzing price movements throughout a single trading day.
        
        Args:
            symbol: Forex pair symbol (e.g., 'EURUSD')
            interval: Time interval (1min, 5min, 15min, 30min, 60min)
            
        Returns:
            dict: Intraday forex data with trading signals
        """
        try:
            # Parse symbol into base and quote currencies
            # Assuming standard format like EURUSD (3 letters + 3 letters)
            if len(symbol) == 6:
                from_currency = symbol[:3]
                to_currency = symbol[3:]
            else:
                return {
                    'source': 'Alpha Vantage',
                    'error': 'Invalid symbol format. Expected format: EURUSD',
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Map interval to Alpha Vantage format
            interval_map = {
                '1min': '1min',
                '5min': '5min',
                '15min': '15min',
                '30min': '30min',
                '60min': '60min',
                '1hour': '60min'
            }
            
            av_interval = interval_map.get(interval.lower(), '5min')
            
            # Prepare API request
            params = {
                'function': 'FX_INTRADAY',
                'from_symbol': from_currency.upper(),
                'to_symbol': to_currency.upper(),
                'interval': av_interval,
                'apikey': AlphaVantageService.API_KEY,
                'outputsize': 'compact'  # 'compact' returns last 100 data points, 'full' returns all
            }
            
            # Make API request
            response = requests.get(AlphaVantageService.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for errors
            if 'Error Message' in data:
                return {
                    'source': 'Alpha Vantage',
                    'error': data['Error Message'],
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            if 'Note' in data:
                return {
                    'source': 'Alpha Vantage',
                    'error': 'API rate limit exceeded',
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Extract time series data
            if f'Time Series FX ({av_interval})' in data:
                time_series = data[f'Time Series FX ({av_interval})']
                metadata = data.get('Meta Data', {})
                
                # Convert time series to list format for easier processing
                # Time series comes as dictionary with timestamps as keys
                data_points = []
                for timestamp, values in time_series.items():
                    data_points.append({
                        'timestamp': timestamp,
                        'open': float(values.get('1. open', 0)),
                        'high': float(values.get('2. high', 0)),
                        'low': float(values.get('3. low', 0)),
                        'close': float(values.get('4. close', 0))
                    })
                
                # Sort by timestamp (most recent first)
                data_points.sort(key=lambda x: x['timestamp'], reverse=True)
                
                # Generate signals from the data
                signals = AlphaVantageService._generate_intraday_signals(data_points)
                
                return {
                    'source': 'Alpha Vantage',
                    'symbol': symbol.upper(),
                    'interval': interval,
                    'metadata': {
                        'information': metadata.get('1. Information', ''),
                        'from_symbol': metadata.get('2. From Symbol', ''),
                        'to_symbol': metadata.get('3. To Symbol', ''),
                        'last_refreshed': metadata.get('4. Last Refreshed', ''),
                        'timezone': metadata.get('5. Time Zone', '')
                    },
                    'data_points': data_points[:50],  # Return last 50 data points
                    'signals': signals,
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            return {
                'source': 'Alpha Vantage',
                'error': 'Unexpected response format',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching Alpha Vantage intraday data: {str(e)}")
            return {
                'source': 'Alpha Vantage',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def _generate_signal(exchange_rate: float) -> dict:
        """
        Generate a simple trading signal based on exchange rate.
        
        This is a basic example. In production, you'd use more sophisticated
        technical analysis algorithms.
        
        Args:
            exchange_rate: Current exchange rate
            
        Returns:
            dict: Trading signal information
        """
        # This is a placeholder - in real trading, you'd compare with historical data
        # and use technical indicators
        return {
            'recommendation': 'NEUTRAL',
            'confidence': 'LOW',
            'note': 'Basic signal generation. Use intraday data for more accurate signals.'
        }
    
    @staticmethod
    def _generate_intraday_signals(data_points: list) -> dict:
        """
        Generate trading signals from intraday price data.
        
        This analyzes price movements to generate buy/sell signals.
        
        Args:
            data_points: List of price data points with open, high, low, close
            
        Returns:
            dict: Trading signals and analysis
        """
        if len(data_points) < 2:
            return {
                'recommendation': 'NEUTRAL',
                'reason': 'Insufficient data points'
            }
        
        # Get most recent data points
        latest = data_points[0]
        previous = data_points[1] if len(data_points) > 1 else latest
        
        # Calculate price change
        price_change = latest['close'] - previous['close']
        price_change_percent = (price_change / previous['close']) * 100 if previous['close'] > 0 else 0
        
        # Simple signal generation based on price movement
        if price_change_percent > 0.1:  # Price increased by more than 0.1%
            recommendation = 'BUY'
            confidence = 'MEDIUM'
        elif price_change_percent < -0.1:  # Price decreased by more than 0.1%
            recommendation = 'SELL'
            confidence = 'MEDIUM'
        else:
            recommendation = 'NEUTRAL'
            confidence = 'LOW'
        
        # Calculate simple moving average (SMA) for last 20 points
        if len(data_points) >= 20:
            sma_20 = sum(point['close'] for point in data_points[:20]) / 20
            current_price = latest['close']
            
            # If current price is above SMA, it's bullish
            if current_price > sma_20:
                recommendation = 'BUY'
                confidence = 'HIGH'
            elif current_price < sma_20:
                recommendation = 'SELL'
                confidence = 'HIGH'
        
        return {
            'recommendation': recommendation,
            'confidence': confidence,
            'price_change': price_change,
            'price_change_percent': round(price_change_percent, 4),
            'current_price': latest['close'],
            'previous_price': previous['close']
        }


