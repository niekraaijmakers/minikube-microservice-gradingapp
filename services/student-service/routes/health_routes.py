"""
Health check routes.
Endpoints for Kubernetes probes and service status.
"""
from flask import Blueprint, jsonify
from core.config import Config


def create_health_routes() -> Blueprint:
    """
    Create health check routes blueprint.
    
    Returns:
        Flask Blueprint with health endpoints.
    """
    bp = Blueprint('health', __name__)
    
    @bp.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint for Kubernetes probes."""
        return jsonify({
            'status': 'healthy',
            'service': Config.SERVICE_NAME,
            'version': Config.VERSION
        })
    
    return bp

