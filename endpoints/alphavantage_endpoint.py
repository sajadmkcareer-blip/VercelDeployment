"""
Alpha Vantage Endpoint
This module defines the REST API endpoints for Alpha Vantage service.

Endpoints:
- GET /api/alphavantage/realtime/<symbol> - Get real-time exchange rate
- GET /api/alphavantage/intraday/<symbol> - Get intraday data for multiple trades
"""
from flask_restx import Namespace, Resource, fields
from services.alphavantage_service import AlphaVantageService

# Create namespace for Alpha Vantage endpoints
ns = Namespace('alphavantage', description='Alpha Vantage forex data operations')

# Define data models for Swagger documentation
realtime_model = ns.model('AlphaVantageRealtime', {
    'source': fields.String(description='Data source name'),
    'symbol': fields.String(description='Forex pair symbol'),
    'from_currency': fields.String(description='Base currency'),
    'to_currency': fields.String(description='Quote currency'),
    'exchange_rate': fields.Float(description='Current exchange rate'),
    'last_refreshed': fields.String(description='Last refresh timestamp'),
    'timezone': fields.String(description='Timezone'),
    'signal': fields.Nested(ns.model('Signal', {
        'recommendation': fields.String(description='Trading recommendation'),
        'confidence': fields.String(description='Signal confidence level'),
        'note': fields.String(description='Additional notes')
    })),
    'timestamp': fields.String(description='Response timestamp')
})

intraday_model = ns.model('AlphaVantageIntraday', {
    'source': fields.String(description='Data source name'),
    'symbol': fields.String(description='Forex pair symbol'),
    'interval': fields.String(description='Time interval'),
    'metadata': fields.Nested(ns.model('Metadata', {
        'information': fields.String(description='Data description'),
        'from_symbol': fields.String(description='Base currency'),
        'to_symbol': fields.String(description='Quote currency'),
        'last_refreshed': fields.String(description='Last refresh time'),
        'timezone': fields.String(description='Timezone')
    })),
    'data_points': fields.List(fields.Nested(ns.model('DataPoint', {
        'timestamp': fields.String(description='Data point timestamp'),
        'open': fields.Float(description='Opening price'),
        'high': fields.Float(description='Highest price'),
        'low': fields.Float(description='Lowest price'),
        'close': fields.Float(description='Closing price')
    }))),
    'signals': fields.Nested(ns.model('IntradaySignals', {
        'recommendation': fields.String(description='Overall recommendation'),
        'confidence': fields.String(description='Signal confidence'),
        'price_change': fields.Float(description='Price change'),
        'price_change_percent': fields.Float(description='Price change percentage'),
        'current_price': fields.Float(description='Current price'),
        'previous_price': fields.Float(description='Previous price')
    })),
    'timestamp': fields.String(description='Response timestamp')
})

# Define query parameter parser
parser = ns.parser()
parser.add_argument('interval', type=str, default='5min',
                   choices=['1min', '5min', '15min', '30min', '60min', '1hour'],
                   help='Time interval for intraday data (default: 5min)',
                   location='args')


@ns.route('/realtime/<string:symbol>')
@ns.param('symbol', 'Forex pair symbol (e.g., EURUSD)')
class AlphaVantageRealtime(Resource):
    """
    Endpoint to get real-time exchange rate from Alpha Vantage.
    
    This endpoint fetches the current exchange rate for a forex pair
    and generates a basic trading signal based on the rate.
    """
    
    @ns.doc('get_alphavantage_realtime')
    @ns.marshal_with(realtime_model)
    def get(self, symbol):
        """
        Get real-time exchange rate for a forex pair.
        
        This method:
        1. Parses the symbol into base and quote currencies
        2. Fetches real-time exchange rate from Alpha Vantage
        3. Generates a basic trading signal
        4. Returns the rate and signal information
        
        Example usage:
        - GET /api/alphavantage/realtime/EURUSD
        
        Args:
            symbol: Forex pair symbol (e.g., 'EURUSD')
            
        Returns:
            dict: Real-time exchange rate and trading signal
        """
        # Parse symbol into currencies
        if len(symbol) == 6:
            from_currency = symbol[:3]
            to_currency = symbol[3:]
        else:
            return {
                'error': 'Invalid symbol format. Expected format: EURUSD (6 characters)'
            }, 400
        
        # Fetch real-time rate
        result = AlphaVantageService.get_realtime_rate(from_currency, to_currency)
        
        return result, 200


@ns.route('/intraday/<string:symbol>')
@ns.param('symbol', 'Forex pair symbol (e.g., EURUSD)')
class AlphaVantageIntraday(Resource):
    """
    Endpoint to get intraday forex data from Alpha Vantage.
    
    This endpoint is designed for multiple trades throughout a single day.
    It fetches intraday price data at specified intervals and generates
    trading signals based on price movements.
    """
    
    @ns.doc('get_alphavantage_intraday')
    @ns.marshal_with(intraday_model)
    @ns.expect(parser)
    def get(self, symbol):
        """
        Get intraday forex data for multiple trades.
        
        This method:
        1. Fetches intraday price data at specified intervals
        2. Analyzes price movements throughout the day
        3. Generates trading signals for different time periods
        4. Returns data points and signals for numerous trades
        
        This endpoint is optimized for analyzing multiple trading opportunities
        within a single day, making it ideal for day trading strategies.
        
        Example usage:
        - GET /api/alphavantage/intraday/EURUSD?interval=5min
        - GET /api/alphavantage/intraday/GBPUSD?interval=15min
        
        Args:
            symbol: Forex pair symbol (e.g., 'EURUSD')
            
        Query Parameters:
            interval: Time interval (1min, 5min, 15min, 30min, 60min, 1hour)
                     Default: 5min (good for intraday trading)
            
        Returns:
            dict: Intraday price data and trading signals
        """
        # Parse query parameters
        args = parser.parse_args()
        interval = args.get('interval', '5min')
        
        # Fetch intraday data
        result = AlphaVantageService.get_intraday_data(symbol, interval)
        
        return result, 200

