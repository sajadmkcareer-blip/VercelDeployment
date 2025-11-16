"""
Forex Trading Signals API
Main Flask application file that sets up the API with Swagger documentation.

This application provides multiple endpoints to fetch forex trading signals
from various free data sources including TradingView TA, Alpha Vantage,
Twelve Data, and TrueFX.
"""
from flask import Flask
from flask_restx import Api, Resource, fields
from flask_cors import CORS
import os

# Import all endpoint modules
from endpoints.tradingview_endpoint import ns as tradingview_ns
from endpoints.alphavantage_endpoint import ns as alphavantage_ns
from endpoints.twelvedata_endpoint import ns as twelvedata_ns
from endpoints.truefx_endpoint import ns as truefx_ns
from endpoints.aggregated_endpoint import ns as aggregated_ns

# Initialize Flask application
app = Flask(__name__)

# Enable CORS (Cross-Origin Resource Sharing) to allow requests from any origin
# This is important for web applications that might call this API from different domains
CORS(app)

# Configure API with Swagger documentation
# This creates an interactive API documentation at /swagger
api = Api(
    app,
    version='1.0',
    title='Forex Trading Signals API',
    description='A comprehensive API to fetch forex trading signals from multiple free data sources. '
                'Supports TradingView TA, Alpha Vantage, Twelve Data, and TrueFX.',
    doc='/swagger/',  # Swagger UI will be available at /swagger/
    prefix='/api'  # All endpoints will be prefixed with /api
)

# Register all namespace modules (each module contains related endpoints)
# Namespaces help organize endpoints into logical groups
api.add_namespace(tradingview_ns, path='/tradingview')
api.add_namespace(alphavantage_ns, path='/alphavantage')
api.add_namespace(twelvedata_ns, path='/twelvedata')
api.add_namespace(truefx_ns, path='/truefx')
api.add_namespace(aggregated_ns, path='/aggregated')

# Health check endpoint - useful for monitoring and deployment verification
@api.route('/health')
class Health(Resource):
    """
    Health check endpoint.
    Returns a simple status message to verify the API is running.
    """
    def get(self):
        """
        GET request to check API health status.
        
        Returns:
            dict: Status message indicating the API is running
        """
        return {
            'status': 'healthy',
            'message': 'Forex Trading Signals API is running',
            'version': '1.0'
        }

# Run the application if this file is executed directly
# This is useful for local development
if __name__ == '__main__':
    # Get port from environment variable or use default 5000
    port = int(os.environ.get('PORT', 5000))
    # Run the Flask development server
    app.run(debug=True, host='0.0.0.0', port=port)


