"""
TradingView TA Service
This service fetches technical analysis signals from TradingView using the tradingview-ta library.

The TradingView TA library provides technical indicators and signals based on
TradingView's analysis algorithms. This is a free alternative to accessing TradingView data.
"""
from tradingview_ta import TA_Handler, Interval
from datetime import datetime, timedelta
import logging

# Set up logging to track errors and debug information
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradingViewService:
    """
    Service class to interact with TradingView TA library.
    This class encapsulates all logic for fetching trading signals from TradingView.
    """
    
    # Mapping of common forex pairs to TradingView symbols
    # TradingView uses specific symbol formats (e.g., FX:EURUSD)
    FOREX_SYMBOLS = {
        'EURUSD': 'FX:EURUSD',
        'GBPUSD': 'FX:GBPUSD',
        'USDJPY': 'FX:USDJPY',
        'USDCHF': 'FX:USDCHF',
        'AUDUSD': 'FX:AUDUSD',
        'USDCAD': 'FX:USDCAD',
        'NZDUSD': 'FX:NZDUSD',
        'EURGBP': 'FX:EURGBP',
        'EURJPY': 'FX:EURJPY',
        'GBPJPY': 'FX:GBPJPY',
    }
    
    # Interval mapping for different timeframes
    # These intervals determine the granularity of the data (1min, 5min, 15min, etc.)
    INTERVAL_MAP = {
        '1min': Interval.INTERVAL_1_MINUTE,
        '5min': Interval.INTERVAL_5_MINUTES,
        '15min': Interval.INTERVAL_15_MINUTES,
        '30min': Interval.INTERVAL_30_MINUTES,
        '1hour': Interval.INTERVAL_1_HOUR,
        '4hour': Interval.INTERVAL_4_HOURS,
        '1day': Interval.INTERVAL_1_DAY,
    }
    
    @staticmethod
    def get_tradingview_symbol(symbol: str) -> str:
        """
        Convert a standard forex pair symbol to TradingView format.
        
        Args:
            symbol: Standard forex pair (e.g., 'EURUSD')
            
        Returns:
            str: TradingView formatted symbol (e.g., 'FX:EURUSD')
        """
        # Convert to uppercase to handle case variations
        symbol_upper = symbol.upper()
        
        # Check if symbol is in our mapping
        if symbol_upper in TradingViewService.FOREX_SYMBOLS:
            return TradingViewService.FOREX_SYMBOLS[symbol_upper]
        
        # If not in mapping, try to format it as FX:SYMBOL
        # This handles cases where the symbol might not be in our predefined list
        return f'FX:{symbol_upper}'
    
    @staticmethod
    def get_signals(symbol: str, interval: str = '15min', exchange: str = 'FX') -> dict:
        """
        Fetch trading signals for a given forex pair using TradingView TA.
        
        This method:
        1. Creates a TA_Handler instance for the specified symbol
        2. Retrieves technical analysis data including indicators and signals
        3. Processes the data into a standardized format
        
        Args:
            symbol: Forex pair symbol (e.g., 'EURUSD')
            interval: Time interval for analysis (default: '15min')
                     Options: '1min', '5min', '15min', '30min', '1hour', '4hour', '1day'
            exchange: Exchange identifier (default: 'FX' for forex)
            
        Returns:
            dict: Dictionary containing trading signals and technical indicators
        """
        try:
            # Convert symbol to TradingView format
            tv_symbol = TradingViewService.get_tradingview_symbol(symbol)
            
            # Get the interval enum value
            # Default to 15 minutes if interval is not recognized
            tv_interval = TradingViewService.INTERVAL_MAP.get(
                interval.lower(), 
                Interval.INTERVAL_15_MINUTES
            )
            
            # Create TA_Handler instance
            # This is the main class from tradingview-ta library that fetches data
            handler = TA_Handler(
                symbol=tv_symbol,
                screener="forex",  # Specify that we're analyzing forex pairs
                exchange=exchange,
                interval=tv_interval
            )
            
            # Get the analysis which includes:
            # - Summary (BUY, SELL, NEUTRAL recommendation)
            # - Various technical indicators (RSI, MACD, Moving Averages, etc.)
            analysis = handler.get_analysis()
            
            # Extract summary information
            # The summary contains the overall recommendation
            summary = analysis.summary
            
            # Extract indicators
            # Indicators contain detailed technical analysis data
            indicators = analysis.indicators
            
            # Build response in a standardized format
            # This makes it easy for frontend applications to consume
            result = {
                'source': 'TradingView TA',
                'symbol': symbol.upper(),
                'tradingview_symbol': tv_symbol,
                'interval': interval,
                'timestamp': datetime.utcnow().isoformat(),
                'summary': {
                    'recommendation': summary.get('RECOMMENDATION', 'NEUTRAL'),
                    'buy_signals': summary.get('BUY', 0),
                    'sell_signals': summary.get('SELL', 0),
                    'neutral_signals': summary.get('NEUTRAL', 0)
                },
                'indicators': {
                    # Relative Strength Index (RSI) - momentum oscillator
                    'rsi': indicators.get('RSI', None),
                    # Moving Average Convergence Divergence (MACD)
                    'macd': indicators.get('MACD', None),
                    'macd_signal': indicators.get('MACD Signal', None),
                    'macd_histogram': indicators.get('MACD Hist', None),
                    # Simple Moving Averages
                    'sma_20': indicators.get('SMA20', None),
                    'sma_50': indicators.get('SMA50', None),
                    # Exponential Moving Averages
                    'ema_20': indicators.get('EMA20', None),
                    'ema_50': indicators.get('EMA50', None),
                    # Current price
                    'close': indicators.get('close', None),
                    # Volume (if available)
                    'volume': indicators.get('volume', None),
                },
                'raw_analysis': {
                    'summary': summary,
                    'indicators': indicators
                }
            }
            
            return result
            
        except Exception as e:
            # Log the error for debugging
            logger.error(f"Error fetching TradingView signals for {symbol}: {str(e)}")
            
            # Return error response
            return {
                'source': 'TradingView TA',
                'symbol': symbol.upper(),
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def get_multiple_signals(symbols: list, interval: str = '15min') -> dict:
        """
        Fetch trading signals for multiple forex pairs.
        
        This is useful when you want to analyze multiple currency pairs at once.
        
        Args:
            symbols: List of forex pair symbols (e.g., ['EURUSD', 'GBPUSD'])
            interval: Time interval for analysis (default: '15min')
            
        Returns:
            dict: Dictionary containing signals for all requested symbols
        """
        results = {}
        
        # Process each symbol
        for symbol in symbols:
            results[symbol.upper()] = TradingViewService.get_signals(symbol, interval)
        
        return {
            'source': 'TradingView TA',
            'interval': interval,
            'timestamp': datetime.utcnow().isoformat(),
            'signals': results
        }


