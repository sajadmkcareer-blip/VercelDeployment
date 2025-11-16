"""
Twelve Data Service
This service fetches forex data from Twelve Data API.

Twelve Data provides free-tier access to forex data with WebSocket support.
Free tier includes 800 API calls per day.
API Key: 217116a3a840410197f04f747300b3b1
"""
import requests
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TwelveDataService:
    """
    Service class to interact with Twelve Data API.
    This class handles fetching forex data and generating trading signals.
    """
    
    # Base URL for Twelve Data API
    BASE_URL = "https://api.twelvedata.com"
    
    # API Key provided by user
    API_KEY = "217116a3a840410197f04f747300b3b1"
    
    @staticmethod
    def get_realtime_quote(symbol: str) -> dict:
        """
        Get real-time quote for a forex pair.
        
        Args:
            symbol: Forex pair symbol (e.g., 'EUR/USD')
                  Note: Twelve Data uses '/' separator format
            
        Returns:
            dict: Real-time quote data with trading signals
        """
        try:
            # Convert symbol format if needed
            # Twelve Data uses EUR/USD format, but we accept EURUSD
            formatted_symbol = TwelveDataService._format_symbol(symbol)
            
            # Prepare API request
            params = {
                'symbol': formatted_symbol,
                'apikey': TwelveDataService.API_KEY
            }
            
            # Make API request to get real-time quote
            response = requests.get(
                f"{TwelveDataService.BASE_URL}/quote",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if 'status' in data and data['status'] == 'error':
                return {
                    'source': 'Twelve Data',
                    'error': data.get('message', 'Unknown error'),
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Extract quote data
            if 'symbol' in data:
                # Generate trading signal from quote data
                signal = TwelveDataService._generate_signal_from_quote(data)
                
                return {
                    'source': 'Twelve Data',
                    'symbol': symbol.upper(),
                    'formatted_symbol': formatted_symbol,
                    'quote': {
                        'symbol': data.get('symbol', ''),
                        'name': data.get('name', ''),
                        'exchange': data.get('exchange', ''),
                        'currency': data.get('currency', ''),
                        'datetime': data.get('datetime', ''),
                        'timestamp': data.get('timestamp', 0),
                        'open': float(data.get('open', 0)),
                        'high': float(data.get('high', 0)),
                        'low': float(data.get('low', 0)),
                        'close': float(data.get('close', 0)),
                        'volume': int(data.get('volume', 0)),
                        'previous_close': float(data.get('previous_close', 0)),
                        'change': float(data.get('change', 0)),
                        'percent_change': float(data.get('percent_change', 0))
                    },
                    'signal': signal,
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            return {
                'source': 'Twelve Data',
                'error': 'Unexpected response format',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Twelve Data quote: {str(e)}")
            return {
                'source': 'Twelve Data',
                'error': f'Request failed: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error processing Twelve Data quote: {str(e)}")
            return {
                'source': 'Twelve Data',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def get_time_series(symbol: str, interval: str = '5min', outputsize: int = 100) -> dict:
        """
        Get time series data for a forex pair.
        
        This is useful for intraday analysis and generating multiple trading signals
        throughout a single day.
        
        Args:
            symbol: Forex pair symbol (e.g., 'EURUSD')
            interval: Time interval (1min, 5min, 15min, 30min, 45min, 1h, 2h, 4h, 1day)
            outputsize: Number of data points to retrieve (default: 100, max: 5000)
            
        Returns:
            dict: Time series data with trading signals
        """
        try:
            # Convert symbol format
            formatted_symbol = TwelveDataService._format_symbol(symbol)
            
            # Prepare API request
            params = {
                'symbol': formatted_symbol,
                'interval': interval,
                'outputsize': min(outputsize, 5000),  # Limit to API maximum
                'apikey': TwelveDataService.API_KEY,
                'format': 'json'
            }
            
            # Make API request
            response = requests.get(
                f"{TwelveDataService.BASE_URL}/time_series",
                params=params,
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Check for errors
            if 'status' in data and data['status'] == 'error':
                return {
                    'source': 'Twelve Data',
                    'error': data.get('message', 'Unknown error'),
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Extract time series data
            if 'values' in data:
                values = data['values']
                meta = data.get('meta', {})
                
                # Process time series data
                # Values come in reverse chronological order (newest first)
                data_points = []
                for value in values:
                    data_points.append({
                        'datetime': value.get('datetime', ''),
                        'open': float(value.get('open', 0)),
                        'high': float(value.get('high', 0)),
                        'low': float(value.get('low', 0)),
                        'close': float(value.get('close', 0)),
                        'volume': int(value.get('volume', 0))
                    })
                
                # Generate signals from time series
                signals = TwelveDataService._generate_signals_from_timeseries(data_points)
                
                return {
                    'source': 'Twelve Data',
                    'symbol': symbol.upper(),
                    'formatted_symbol': formatted_symbol,
                    'interval': interval,
                    'metadata': {
                        'symbol': meta.get('symbol', ''),
                        'interval': meta.get('interval', ''),
                        'currency_base': meta.get('currency_base', ''),
                        'currency_quote': meta.get('currency_quote', ''),
                        'exchange': meta.get('exchange', ''),
                        'type': meta.get('type', '')
                    },
                    'data_points': data_points,
                    'signals': signals,
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            return {
                'source': 'Twelve Data',
                'error': 'Unexpected response format',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching Twelve Data time series: {str(e)}")
            return {
                'source': 'Twelve Data',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def _format_symbol(symbol: str) -> str:
        """
        Convert symbol format to Twelve Data format (EUR/USD).
        
        Args:
            symbol: Symbol in various formats (EURUSD, EUR/USD, etc.)
            
        Returns:
            str: Symbol in Twelve Data format (EUR/USD)
        """
        symbol = symbol.upper().replace(' ', '')
        
        # If already in correct format, return as is
        if '/' in symbol:
            return symbol
        
        # If 6 characters (e.g., EURUSD), split into 3+3
        if len(symbol) == 6:
            return f"{symbol[:3]}/{symbol[3:]}"
        
        # Return as is if format is unclear
        return symbol
    
    @staticmethod
    def _generate_signal_from_quote(quote_data: dict) -> dict:
        """
        Generate trading signal from real-time quote data.
        
        Args:
            quote_data: Quote data from Twelve Data API
            
        Returns:
            dict: Trading signal information
        """
        try:
            current_price = float(quote_data.get('close', 0))
            previous_close = float(quote_data.get('previous_close', 0))
            percent_change = float(quote_data.get('percent_change', 0))
            
            # Generate signal based on price change
            if percent_change > 0.05:  # Price increased by more than 0.05%
                recommendation = 'BUY'
                confidence = 'MEDIUM'
            elif percent_change < -0.05:  # Price decreased by more than 0.05%
                recommendation = 'SELL'
                confidence = 'MEDIUM'
            else:
                recommendation = 'NEUTRAL'
                confidence = 'LOW'
            
            return {
                'recommendation': recommendation,
                'confidence': confidence,
                'price_change_percent': round(percent_change, 4),
                'current_price': current_price,
                'previous_close': previous_close
            }
        except Exception as e:
            logger.error(f"Error generating signal from quote: {str(e)}")
            return {
                'recommendation': 'NEUTRAL',
                'confidence': 'LOW',
                'error': str(e)
            }
    
    @staticmethod
    def _generate_signals_from_timeseries(data_points: list) -> dict:
        """
        Generate trading signals from time series data.
        
        This analyzes multiple data points to generate more accurate signals.
        
        Args:
            data_points: List of price data points
            
        Returns:
            dict: Trading signals and analysis
        """
        if len(data_points) < 2:
            return {
                'recommendation': 'NEUTRAL',
                'reason': 'Insufficient data points'
            }
        
        # Get most recent data
        latest = data_points[0]
        previous = data_points[1] if len(data_points) > 1 else latest
        
        # Calculate price change
        price_change = latest['close'] - previous['close']
        price_change_percent = (price_change / previous['close']) * 100 if previous['close'] > 0 else 0
        
        # Calculate simple moving averages
        sma_20 = None
        sma_50 = None
        
        if len(data_points) >= 20:
            sma_20 = sum(point['close'] for point in data_points[:20]) / 20
        
        if len(data_points) >= 50:
            sma_50 = sum(point['close'] for point in data_points[:50]) / 50
        
        # Generate signal based on multiple factors
        recommendation = 'NEUTRAL'
        confidence = 'LOW'
        reasons = []
        
        # Factor 1: Price momentum
        if price_change_percent > 0.1:
            recommendation = 'BUY'
            confidence = 'MEDIUM'
            reasons.append('Positive price momentum')
        elif price_change_percent < -0.1:
            recommendation = 'SELL'
            confidence = 'MEDIUM'
            reasons.append('Negative price momentum')
        
        # Factor 2: Moving average crossover
        if sma_20 and sma_50:
            if latest['close'] > sma_20 > sma_50:
                recommendation = 'BUY'
                confidence = 'HIGH'
                reasons.append('Price above both moving averages (bullish)')
            elif latest['close'] < sma_20 < sma_50:
                recommendation = 'SELL'
                confidence = 'HIGH'
                reasons.append('Price below both moving averages (bearish)')
        
        # Factor 3: Support and resistance levels
        highs = [point['high'] for point in data_points[:20]]
        lows = [point['low'] for point in data_points[:20]]
        resistance = max(highs) if highs else None
        support = min(lows) if lows else None
        
        if resistance and support:
            if latest['close'] > (resistance + support) / 2:
                if recommendation == 'NEUTRAL':
                    recommendation = 'BUY'
                    confidence = 'MEDIUM'
                reasons.append('Price above midpoint of support/resistance range')
        
        return {
            'recommendation': recommendation,
            'confidence': confidence,
            'price_change': round(price_change, 6),
            'price_change_percent': round(price_change_percent, 4),
            'current_price': latest['close'],
            'previous_price': previous['close'],
            'sma_20': round(sma_20, 6) if sma_20 else None,
            'sma_50': round(sma_50, 6) if sma_50 else None,
            'support': round(support, 6) if support else None,
            'resistance': round(resistance, 6) if resistance else None,
            'reasons': reasons
        }


