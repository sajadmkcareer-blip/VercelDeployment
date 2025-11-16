"""
Aggregated Signals Endpoint
This module defines the endpoint that combines signals from all data sources.

Endpoint:
- GET /api/aggregated/signals/<symbol> - Get aggregated signals from all sources
"""
from flask_restx import Namespace, Resource, fields
from services.tradingview_service import TradingViewService
from services.alphavantage_service import AlphaVantageService
from services.twelvedata_service import TwelveDataService
from services.truefx_service import TrueFXService
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create namespace for aggregated endpoints
ns = Namespace('aggregated', description='Aggregated trading signals from all sources')

# Define data model for aggregated response
aggregated_model = ns.model('AggregatedSignals', {
    'symbol': fields.String(description='Forex pair symbol'),
    'timestamp': fields.String(description='Response timestamp'),
    'sources': fields.Nested(ns.model('SourceSignals', {
        'tradingview': fields.Raw(description='TradingView TA signals'),
        'alphavantage': fields.Raw(description='Alpha Vantage signals'),
        'twelvedata': fields.Raw(description='Twelve Data signals'),
        'truefx': fields.Raw(description='TrueFX signals')
    })),
    'consensus': fields.Nested(ns.model('Consensus', {
        'overall_recommendation': fields.String(description='Overall recommendation based on all sources'),
        'buy_votes': fields.Integer(description='Number of sources recommending BUY'),
        'sell_votes': fields.Integer(description='Number of sources recommending SELL'),
        'neutral_votes': fields.Integer(description='Number of sources recommending NEUTRAL'),
        'average_confidence': fields.String(description='Average confidence level'),
        'agreement_level': fields.String(description='Level of agreement between sources')
    })),
    'summary': fields.String(description='Summary of all signals')
})

# Define query parameter parser
parser = ns.parser()
parser.add_argument('interval', type=str, default='15min',
                   choices=['1min', '5min', '15min', '30min', '1hour', '4hour', '1day'],
                   help='Time interval for analysis (default: 15min)',
                   location='args')


@ns.route('/signals/<string:symbol>')
@ns.param('symbol', 'Forex pair symbol (e.g., EURUSD)')
class AggregatedSignals(Resource):
    """
    Endpoint to get aggregated trading signals from all data sources.
    
    This endpoint combines signals from:
    - TradingView TA
    - Alpha Vantage
    - Twelve Data
    - TrueFX
    
    It then generates a consensus recommendation based on all sources,
    making it ideal for getting a comprehensive view of market sentiment.
    """
    
    @ns.doc('get_aggregated_signals')
    @ns.marshal_with(aggregated_model)
    @ns.expect(parser)
    def get(self, symbol):
        """
        Get aggregated trading signals from all data sources.
        
        This method:
        1. Fetches signals from all four data sources in parallel
        2. Extracts recommendations from each source
        3. Calculates a consensus recommendation
        4. Determines agreement level between sources
        5. Returns comprehensive aggregated analysis
        
        This endpoint is perfect when you want to:
        - Get a comprehensive view of market sentiment
        - Compare signals from different sources
        - Make trading decisions based on multiple data points
        - Analyze numerous trading opportunities throughout a day
        
        Example usage:
        - GET /api/aggregated/signals/EURUSD
        - GET /api/aggregated/signals/EURUSD?interval=5min
        
        Args:
            symbol: Forex pair symbol (e.g., 'EURUSD')
            
        Query Parameters:
            interval: Time interval (default: 15min)
            
        Returns:
            dict: Aggregated signals from all sources with consensus recommendation
        """
        # Parse query parameters
        args = parser.parse_args()
        interval = args.get('interval', '15min')
        
        # Fetch signals from all sources
        # We'll fetch them sequentially, but in production you could use async/parallel requests
        sources = {}
        
        try:
            # Fetch from TradingView TA
            sources['tradingview'] = TradingViewService.get_signals(symbol, interval)
        except Exception as e:
            logger.error(f"Error fetching TradingView signals: {str(e)}")
            sources['tradingview'] = {'error': str(e)}
        
        try:
            # Fetch from Alpha Vantage (intraday data)
            sources['alphavantage'] = AlphaVantageService.get_intraday_data(symbol, interval)
        except Exception as e:
            logger.error(f"Error fetching Alpha Vantage signals: {str(e)}")
            sources['alphavantage'] = {'error': str(e)}
        
        try:
            # Fetch from Twelve Data (time series)
            sources['twelvedata'] = TwelveDataService.get_time_series(symbol, interval, 100)
        except Exception as e:
            logger.error(f"Error fetching Twelve Data signals: {str(e)}")
            sources['twelvedata'] = {'error': str(e)}
        
        try:
            # Fetch from TrueFX (intraday signals)
            sources['truefx'] = TrueFXService.get_intraday_signals(symbol)
        except Exception as e:
            logger.error(f"Error fetching TrueFX signals: {str(e)}")
            sources['truefx'] = {'error': str(e)}
        
        # Calculate consensus recommendation
        consensus = AggregatedSignals._calculate_consensus(sources)
        
        # Build response
        result = {
            'symbol': symbol.upper(),
            'timestamp': datetime.utcnow().isoformat(),
            'interval': interval,
            'sources': sources,
            'consensus': consensus,
            'summary': AggregatedSignals._generate_summary(sources, consensus)
        }
        
        return result, 200
    
    @staticmethod
    def _calculate_consensus(sources: dict) -> dict:
        """
        Calculate consensus recommendation from all sources.
        
        This method analyzes recommendations from all sources and determines:
        - Overall recommendation (BUY/SELL/NEUTRAL)
        - Number of votes for each recommendation
        - Average confidence level
        - Agreement level between sources
        
        Args:
            sources: Dictionary containing signals from all sources
            
        Returns:
            dict: Consensus recommendation and statistics
        """
        recommendations = []
        confidences = []
        
        # Extract recommendations from each source
        for source_name, source_data in sources.items():
            if 'error' in source_data:
                continue  # Skip sources with errors
            
            recommendation = None
            confidence = 'LOW'
            
            # Extract recommendation based on source structure
            if source_name == 'tradingview':
                if 'summary' in source_data and 'recommendation' in source_data['summary']:
                    recommendation = source_data['summary']['recommendation']
                    # Determine confidence based on signal counts
                    buy = source_data['summary'].get('buy_signals', 0)
                    sell = source_data['summary'].get('sell_signals', 0)
                    if buy > sell * 1.5:
                        confidence = 'HIGH'
                    elif sell > buy * 1.5:
                        confidence = 'HIGH'
                    else:
                        confidence = 'MEDIUM'
            
            elif source_name == 'alphavantage':
                if 'signals' in source_data and 'recommendation' in source_data['signals']:
                    recommendation = source_data['signals']['recommendation']
                    confidence = source_data['signals'].get('confidence', 'LOW')
            
            elif source_name == 'twelvedata':
                if 'signals' in source_data and 'recommendation' in source_data['signals']:
                    recommendation = source_data['signals']['recommendation']
                    confidence = source_data['signals'].get('confidence', 'LOW')
            
            elif source_name == 'truefx':
                # TrueFX signals are structured differently
                if 'signals' in source_data and 'signals' in source_data['signals']:
                    # Get the most recent signal
                    signals_list = source_data['signals'].get('signals', [])
                    if signals_list:
                        recommendation = signals_list[0].get('recommendation', 'NEUTRAL')
                        confidence = signals_list[0].get('confidence', 'LOW')
            
            if recommendation:
                recommendations.append(recommendation.upper())
                confidences.append(confidence)
        
        # Count votes
        buy_votes = recommendations.count('BUY')
        sell_votes = recommendations.count('SELL')
        neutral_votes = recommendations.count('NEUTRAL')
        
        # Determine overall recommendation
        if buy_votes > sell_votes and buy_votes > neutral_votes:
            overall_recommendation = 'BUY'
        elif sell_votes > buy_votes and sell_votes > neutral_votes:
            overall_recommendation = 'SELL'
        else:
            overall_recommendation = 'NEUTRAL'
        
        # Calculate average confidence
        confidence_map = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3}
        if confidences:
            avg_confidence_num = sum(confidence_map.get(c, 1) for c in confidences) / len(confidences)
            if avg_confidence_num >= 2.5:
                average_confidence = 'HIGH'
            elif avg_confidence_num >= 1.5:
                average_confidence = 'MEDIUM'
            else:
                average_confidence = 'LOW'
        else:
            average_confidence = 'LOW'
        
        # Determine agreement level
        total_votes = len(recommendations)
        if total_votes == 0:
            agreement_level = 'NO_DATA'
        elif total_votes == 1:
            agreement_level = 'SINGLE_SOURCE'
        else:
            max_votes = max(buy_votes, sell_votes, neutral_votes)
            agreement_ratio = max_votes / total_votes
            if agreement_ratio >= 0.75:
                agreement_level = 'STRONG_AGREEMENT'
            elif agreement_ratio >= 0.5:
                agreement_level = 'MODERATE_AGREEMENT'
            else:
                agreement_level = 'MIXED_SIGNALS'
        
        return {
            'overall_recommendation': overall_recommendation,
            'buy_votes': buy_votes,
            'sell_votes': sell_votes,
            'neutral_votes': neutral_votes,
            'total_sources': total_votes,
            'average_confidence': average_confidence,
            'agreement_level': agreement_level
        }
    
    @staticmethod
    def _generate_summary(sources: dict, consensus: dict) -> str:
        """
        Generate a human-readable summary of all signals.
        
        Args:
            sources: Dictionary containing signals from all sources
            consensus: Consensus recommendation dictionary
            
        Returns:
            str: Human-readable summary
        """
        summary_parts = []
        
        summary_parts.append(f"Consensus Recommendation: {consensus['overall_recommendation']}")
        summary_parts.append(f"Agreement Level: {consensus['agreement_level']}")
        summary_parts.append(f"Votes - BUY: {consensus['buy_votes']}, SELL: {consensus['sell_votes']}, NEUTRAL: {consensus['neutral_votes']}")
        summary_parts.append(f"Average Confidence: {consensus['average_confidence']}")
        
        # Add source-specific summaries
        for source_name, source_data in sources.items():
            if 'error' not in source_data:
                if source_name == 'tradingview' and 'summary' in source_data:
                    rec = source_data['summary'].get('recommendation', 'N/A')
                    summary_parts.append(f"TradingView: {rec}")
                elif source_name in ['alphavantage', 'twelvedata'] and 'signals' in source_data:
                    rec = source_data['signals'].get('recommendation', 'N/A')
                    summary_parts.append(f"{source_name.title()}: {rec}")
        
        return " | ".join(summary_parts)

