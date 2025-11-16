"""
TradingView TA Endpoint
This module defines the REST API endpoints for TradingView TA service.

Endpoints:
- GET /api/tradingview/signals/<symbol> - Get trading signals for a single pair
- GET /api/tradingview/signals - Get trading signals for multiple pairs
"""
from flask_restx import Namespace, Resource, fields
from services.tradingview_service import TradingViewService

# Create a namespace for TradingView endpoints
# Namespaces help organize related endpoints together
ns = Namespace('tradingview', description='TradingView TA trading signals operations')

# Define data models for Swagger documentation
# These models describe the structure of request/response data
signal_model = ns.model('TradingViewSignal', {
    'source': fields.String(description='Data source name'),
    'symbol': fields.String(description='Forex pair symbol'),
    'tradingview_symbol': fields.String(description='TradingView formatted symbol'),
    'interval': fields.String(description='Time interval used for analysis'),
    'timestamp': fields.String(description='Timestamp of the response'),
    'summary': fields.Nested(ns.model('Summary', {
        'recommendation': fields.String(description='Overall recommendation (BUY/SELL/NEUTRAL)'),
        'buy_signals': fields.Integer(description='Number of buy signals'),
        'sell_signals': fields.Integer(description='Number of sell signals'),
        'neutral_signals': fields.Integer(description='Number of neutral signals')
    })),
    'indicators': fields.Nested(ns.model('Indicators', {
        'rsi': fields.Float(description='Relative Strength Index'),
        'macd': fields.Float(description='MACD value'),
        'macd_signal': fields.Float(description='MACD signal line'),
        'macd_histogram': fields.Float(description='MACD histogram'),
        'sma_20': fields.Float(description='20-period Simple Moving Average'),
        'sma_50': fields.Float(description='50-period Simple Moving Average'),
        'ema_20': fields.Float(description='20-period Exponential Moving Average'),
        'ema_50': fields.Float(description='50-period Exponential Moving Average'),
        'close': fields.Float(description='Current closing price'),
        'volume': fields.Float(description='Trading volume')
    }))
})

# Define query parameters for the endpoints
# These parameters can be passed in the URL query string
parser = ns.parser()
parser.add_argument('interval', type=str, default='15min', 
                   choices=['1min', '5min', '15min', '1hour', '4hour', '1day'],
                   help='Time interval for analysis (default: 15min). Note: 30min is not supported by TradingView TA, use 15min or 1hour instead.',
                   location='args')
parser.add_argument('symbols', type=str,
                   help='Comma-separated list of forex pair symbols',
                   location='args')


@ns.route('/signals/<string:symbol>')
@ns.param('symbol', 'Forex pair symbol (e.g., EURUSD, GBPUSD)')
class TradingViewSignal(Resource):
    """
    Endpoint to get trading signals for a single forex pair from TradingView TA.
    
    This endpoint fetches technical analysis signals for a specified currency pair.
    It uses the TradingView TA library which provides various technical indicators
    and generates buy/sell/neutral recommendations.
    """
    
    @ns.doc('get_tradingview_signal')
    @ns.marshal_with(signal_model)
    @ns.expect(parser)
    def get(self, symbol):
        """
        Get trading signals for a single forex pair.
        
        This method:
        1. Accepts a forex pair symbol (e.g., EURUSD)
        2. Optionally accepts an interval parameter (default: 15min)
        3. Fetches technical analysis data from TradingView TA
        4. Returns trading signals and indicators
        
        Example usage:
        - GET /api/tradingview/signals/EURUSD
        - GET /api/tradingview/signals/EURUSD?interval=5min
        
        Args:
            symbol: Forex pair symbol (e.g., 'EURUSD')
            
        Query Parameters:
            interval: Time interval (1min, 5min, 15min, 1hour, 4hour, 1day)
                     Note: 30min is not supported by TradingView TA
            
        Returns:
            dict: Trading signals and technical indicators
        """
        # Parse query parameters
        args = parser.parse_args()
        interval = args.get('interval', '15min')
        
        # Fetch signals from TradingView service
        result = TradingViewService.get_signals(symbol, interval)
        
        return result, 200


@ns.route('/signals')
class TradingViewMultipleSignals(Resource):
    """
    Endpoint to get trading signals for multiple forex pairs.
    
    This endpoint allows you to fetch signals for multiple currency pairs
    in a single request, which is useful for comparing different pairs.
    """
    
    # Define model for multiple symbols request
    multiple_symbols_model = ns.model('MultipleSymbols', {
        'symbols': fields.List(fields.String, required=True, 
                               description='List of forex pair symbols'),
        'interval': fields.String(default='15min', 
                                 description='Time interval for analysis')
    })
    
    @ns.doc('get_multiple_tradingview_signals')
    @ns.expect(parser)
    def post(self):
        """
        Get trading signals for multiple forex pairs.
        
        This method accepts a list of symbols and returns signals for all of them.
        This is useful when you want to analyze multiple pairs at once.
        
        Example request body:
        {
            "symbols": ["EURUSD", "GBPUSD", "USDJPY"],
            "interval": "15min"
        }
        
        Query Parameters:
            interval: Time interval (optional, can also be in body)
            
        Returns:
            dict: Trading signals for all requested symbols
        """
        # Parse query parameters
        args = parser.parse_args()
        interval = args.get('interval', '15min')
        
        # Get JSON body (for POST requests)
        # In a real implementation, you'd parse the JSON body
        # For simplicity, we'll use query parameter or accept symbols as comma-separated
        return {
            'message': 'Use GET /api/tradingview/signals/<symbol> for single pair, or implement POST with JSON body',
            'example': 'GET /api/tradingview/signals/EURUSD?interval=15min'
        }, 200
    
    @ns.doc('get_multiple_tradingview_signals_get')
    @ns.expect(parser)
    def get(self):
        """
        Get trading signals for multiple forex pairs using query parameters.
        
        Example usage:
        - GET /api/tradingview/signals?symbols=EURUSD,GBPUSD,USDJPY&interval=15min
        
        Query Parameters:
            symbols: Comma-separated list of forex pair symbols
            interval: Time interval (default: 15min)
            
        Returns:
            dict: Trading signals for all requested symbols
        """
        # Parse query parameters
        args = parser.parse_args()
        interval = args.get('interval', '15min')
        
        # Get symbols from query parameter
        # In a real implementation, you'd parse this from the request
        symbols_param = args.get('symbols', '')
        
        if not symbols_param:
            return {
                'error': 'Please provide symbols parameter',
                'example': '/api/tradingview/signals?symbols=EURUSD,GBPUSD&interval=15min'
            }, 400
        
        # Split comma-separated symbols
        symbols = [s.strip().upper() for s in symbols_param.split(',') if s.strip()]
        
        if not symbols:
            return {
                'error': 'No valid symbols provided'
            }, 400
        
        # Fetch signals for all symbols
        result = TradingViewService.get_multiple_signals(symbols, interval)
        
        return result, 200

