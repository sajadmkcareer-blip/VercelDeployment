"""
Twelve Data Endpoint
This module defines the REST API endpoints for Twelve Data service.

Endpoints:
- GET /api/twelvedata/quote/<symbol> - Get real-time quote
- GET /api/twelvedata/timeseries/<symbol> - Get time series data for intraday trading
"""
from flask_restx import Namespace, Resource, fields
from services.twelvedata_service import TwelveDataService

# Create namespace for Twelve Data endpoints
ns = Namespace('twelvedata', description='Twelve Data forex operations')

# Define data models for Swagger documentation
quote_model = ns.model('TwelveDataQuote', {
    'source': fields.String(description='Data source name'),
    'symbol': fields.String(description='Forex pair symbol'),
    'formatted_symbol': fields.String(description='Twelve Data formatted symbol'),
    'quote': fields.Nested(ns.model('Quote', {
        'symbol': fields.String(description='Symbol'),
        'name': fields.String(description='Pair name'),
        'exchange': fields.String(description='Exchange'),
        'currency': fields.String(description='Currency'),
        'datetime': fields.String(description='Quote datetime'),
        'timestamp': fields.Integer(description='Unix timestamp'),
        'open': fields.Float(description='Opening price'),
        'high': fields.Float(description='Highest price'),
        'low': fields.Float(description='Lowest price'),
        'close': fields.Float(description='Closing price'),
        'volume': fields.Integer(description='Trading volume'),
        'previous_close': fields.Float(description='Previous close price'),
        'change': fields.Float(description='Price change'),
        'percent_change': fields.Float(description='Price change percentage')
    })),
    'signal': fields.Nested(ns.model('QuoteSignal', {
        'recommendation': fields.String(description='Trading recommendation'),
        'confidence': fields.String(description='Signal confidence'),
        'price_change_percent': fields.Float(description='Price change percentage'),
        'current_price': fields.Float(description='Current price'),
        'previous_close': fields.Float(description='Previous close')
    })),
    'timestamp': fields.String(description='Response timestamp')
})

timeseries_model = ns.model('TwelveDataTimeSeries', {
    'source': fields.String(description='Data source name'),
    'symbol': fields.String(description='Forex pair symbol'),
    'formatted_symbol': fields.String(description='Twelve Data formatted symbol'),
    'interval': fields.String(description='Time interval'),
    'metadata': fields.Nested(ns.model('TimeSeriesMetadata', {
        'symbol': fields.String(description='Symbol'),
        'interval': fields.String(description='Time interval'),
        'currency_base': fields.String(description='Base currency'),
        'currency_quote': fields.String(description='Quote currency'),
        'exchange': fields.String(description='Exchange'),
        'type': fields.String(description='Data type')
    })),
    'data_points': fields.List(fields.Nested(ns.model('TimeSeriesPoint', {
        'datetime': fields.String(description='Data point datetime'),
        'open': fields.Float(description='Opening price'),
        'high': fields.Float(description='Highest price'),
        'low': fields.Float(description='Lowest price'),
        'close': fields.Float(description='Closing price'),
        'volume': fields.Integer(description='Trading volume')
    }))),
    'signals': fields.Nested(ns.model('TimeSeriesSignals', {
        'recommendation': fields.String(description='Overall recommendation'),
        'confidence': fields.String(description='Signal confidence'),
        'price_change': fields.Float(description='Price change'),
        'price_change_percent': fields.Float(description='Price change percentage'),
        'current_price': fields.Float(description='Current price'),
        'previous_price': fields.Float(description='Previous price'),
        'sma_20': fields.Float(description='20-period Simple Moving Average'),
        'sma_50': fields.Float(description='50-period Simple Moving Average'),
        'support': fields.Float(description='Support level'),
        'resistance': fields.Float(description='Resistance level'),
        'reasons': fields.List(fields.String, description='Reasons for the signal')
    })),
    'timestamp': fields.String(description='Response timestamp')
})

# Define query parameter parser
parser = ns.parser()
parser.add_argument('interval', type=str, default='5min',
                   choices=['1min', '5min', '15min', '30min', '45min', '1h', '2h', '4h', '1day'],
                   help='Time interval (default: 5min)',
                   location='args')
parser.add_argument('outputsize', type=int, default=100,
                   help='Number of data points to retrieve (default: 100, max: 5000)',
                   location='args')


@ns.route('/quote/<string:symbol>')
@ns.param('symbol', 'Forex pair symbol (e.g., EURUSD or EUR/USD)')
class TwelveDataQuote(Resource):
    """
    Endpoint to get real-time quote from Twelve Data.
    
    This endpoint fetches the latest quote for a forex pair including
    current price, price change, and generates a trading signal.
    """
    
    @ns.doc('get_twelvedata_quote')
    @ns.marshal_with(quote_model)
    def get(self, symbol):
        """
        Get real-time quote for a forex pair.
        
        This method:
        1. Formats the symbol to Twelve Data format (EUR/USD)
        2. Fetches real-time quote from Twelve Data API
        3. Generates trading signal based on price change
        4. Returns quote data and signal
        
        Example usage:
        - GET /api/twelvedata/quote/EURUSD
        - GET /api/twelvedata/quote/EUR/USD
        
        Args:
            symbol: Forex pair symbol (e.g., 'EURUSD' or 'EUR/USD')
            
        Returns:
            dict: Real-time quote and trading signal
        """
        result = TwelveDataService.get_realtime_quote(symbol)
        
        return result, 200


@ns.route('/timeseries/<string:symbol>')
@ns.param('symbol', 'Forex pair symbol (e.g., EURUSD)')
class TwelveDataTimeSeries(Resource):
    """
    Endpoint to get time series data from Twelve Data.
    
    This endpoint is optimized for intraday trading with multiple trades
    throughout a single day. It fetches historical price data at specified
    intervals and generates comprehensive trading signals.
    """
    
    @ns.doc('get_twelvedata_timeseries')
    @ns.marshal_with(timeseries_model)
    @ns.expect(parser)
    def get(self, symbol):
        """
        Get time series data for intraday trading.
        
        This method:
        1. Fetches time series data at specified intervals
        2. Analyzes price movements and calculates technical indicators
        3. Generates trading signals with confidence levels
        4. Identifies support and resistance levels
        5. Returns data suitable for multiple trades in a single day
        
        This endpoint is ideal for day trading strategies that require
        numerous trading opportunities throughout the day.
        
        Example usage:
        - GET /api/twelvedata/timeseries/EURUSD?interval=5min&outputsize=200
        - GET /api/twelvedata/timeseries/GBPUSD?interval=15min&outputsize=100
        
        Args:
            symbol: Forex pair symbol (e.g., 'EURUSD')
            
        Query Parameters:
            interval: Time interval (1min, 5min, 15min, 30min, 45min, 1h, 2h, 4h, 1day)
                     Default: 5min (optimal for intraday trading)
            outputsize: Number of data points (default: 100, max: 5000)
                       More data points = more historical context for signals
            
        Returns:
            dict: Time series data with comprehensive trading signals
        """
        # Parse query parameters
        args = parser.parse_args()
        interval = args.get('interval', '5min')
        outputsize = args.get('outputsize', 100)
        
        # Fetch time series data
        result = TwelveDataService.get_time_series(symbol, interval, outputsize)
        
        return result, 200

