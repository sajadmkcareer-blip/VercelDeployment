"""
TrueFX Endpoint
This module defines the REST API endpoints for TrueFX service.

Endpoints:
- GET /api/truefx/latest/<symbol> - Get latest available data
- GET /api/truefx/intraday/<symbol> - Get intraday trading signals
"""
from flask_restx import Namespace, Resource, fields
from services.truefx_service import TrueFXService

# Create namespace for TrueFX endpoints
ns = Namespace('truefx', description='TrueFX historical tick data operations')

# Define data models for Swagger documentation
latest_data_model = ns.model('TrueFXLatest', {
    'source': fields.String(description='Data source name'),
    'symbol': fields.String(description='Forex pair symbol'),
    'formatted_symbol': fields.String(description='TrueFX formatted symbol'),
    'year': fields.Integer(description='Year of data'),
    'month': fields.Integer(description='Month of data'),
    'data_available': fields.Boolean(description='Whether data is available'),
    'note': fields.String(description='Additional information'),
    'timestamp': fields.String(description='Response timestamp')
})

intraday_model = ns.model('TrueFXIntraday', {
    'source': fields.String(description='Data source name'),
    'symbol': fields.String(description='Forex pair symbol'),
    'formatted_symbol': fields.String(description='TrueFX formatted symbol'),
    'date': fields.String(description='Date of analysis'),
    'signals': fields.Nested(ns.model('IntradaySignals', {
        'date': fields.String(description='Analysis date'),
        'symbol': fields.String(description='Forex pair symbol'),
        'total_signals': fields.Integer(description='Total number of signals'),
        'signals': fields.List(fields.Nested(ns.model('Signal', {
            'time': fields.String(description='Time of signal'),
            'session': fields.String(description='Trading session'),
            'recommendation': fields.String(description='Trading recommendation'),
            'confidence': fields.String(description='Signal confidence'),
            'note': fields.String(description='Additional notes')
        }))),
        'note': fields.String(description='Implementation note')
    })),
    'note': fields.String(description='Data source note'),
    'timestamp': fields.String(description='Response timestamp')
})

# Define query parameter parser
parser = ns.parser()
parser.add_argument('date', type=str,
                   help='Date in YYYY-MM-DD format (default: today)',
                   location='args')
parser.add_argument('year', type=int,
                   help='Year for data retrieval',
                   location='args')
parser.add_argument('month', type=int,
                   help='Month for data retrieval (1-12)',
                   location='args')


@ns.route('/latest/<string:symbol>')
@ns.param('symbol', 'Forex pair symbol (e.g., EURUSD)')
class TrueFXLatest(Resource):
    """
    Endpoint to get latest available data from TrueFX.
    
    TrueFX provides historical tick data in CSV format. This endpoint
    returns information about the latest available data for a pair.
    """
    
    @ns.doc('get_truefx_latest')
    @ns.marshal_with(latest_data_model)
    @ns.expect(parser)
    def get(self, symbol):
        """
        Get latest available data information for a forex pair.
        
        This method:
        1. Formats the symbol to TrueFX format
        2. Checks if the pair is available on TrueFX
        3. Returns information about available data
        
        Note: TrueFX provides CSV downloads. To get actual tick data,
        you would need to download and parse CSV files from TrueFX website.
        
        Example usage:
        - GET /api/truefx/latest/EURUSD
        - GET /api/truefx/latest/EURUSD?year=2024&month=1
        
        Args:
            symbol: Forex pair symbol (e.g., 'EURUSD')
            
        Query Parameters:
            year: Year for data (default: current year)
            month: Month for data (default: current month)
            
        Returns:
            dict: Information about latest available data
        """
        # Parse query parameters
        args = parser.parse_args()
        year = args.get('year')
        month = args.get('month')
        
        # Fetch latest data info
        result = TrueFXService.get_latest_data(symbol, year, month)
        
        return result, 200


@ns.route('/intraday/<string:symbol>')
@ns.param('symbol', 'Forex pair symbol (e.g., EURUSD)')
class TrueFXIntraday(Resource):
    """
    Endpoint to get intraday trading signals from TrueFX data.
    
    This endpoint is designed for analyzing multiple trading opportunities
    throughout a single day using TrueFX historical tick data.
    """
    
    @ns.doc('get_truefx_intraday')
    @ns.marshal_with(intraday_model)
    @ns.expect(parser)
    def get(self, symbol):
        """
        Get intraday trading signals from TrueFX data.
        
        This method:
        1. Analyzes tick data for a specific date
        2. Generates trading signals for different times throughout the day
        3. Identifies trading opportunities across different market sessions
        4. Returns signals optimized for numerous trades in a single day
        
        Note: TrueFX provides historical CSV data. In production, you would:
        1. Download CSV files from TrueFX for the specified date
        2. Parse the CSV to extract tick data
        3. Analyze the tick data to generate actual signals
        
        This endpoint currently provides a structure showing how signals
        would be generated from TrueFX tick data.
        
        Example usage:
        - GET /api/truefx/intraday/EURUSD
        - GET /api/truefx/intraday/EURUSD?date=2024-01-15
        
        Args:
            symbol: Forex pair symbol (e.g., 'EURUSD')
            
        Query Parameters:
            date: Date in YYYY-MM-DD format (default: today)
            
        Returns:
            dict: Intraday trading signals for multiple time periods
        """
        # Parse query parameters
        args = parser.parse_args()
        date = args.get('date')
        
        # Fetch intraday signals
        result = TrueFXService.get_intraday_signals(symbol, date)
        
        return result, 200

