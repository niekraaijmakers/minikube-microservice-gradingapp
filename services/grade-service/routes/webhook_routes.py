"""
Webhook routes.
Endpoints for webhook status and testing.

These endpoints are for the EGRESS DEMO - they allow you to:
1. Check webhook status (seeing if calls are being blocked)
2. Manually test webhook connectivity
3. Test external internet access (should be blocked)
"""
import requests
from flask import Blueprint, jsonify
from services.webhook_service import WebhookService


def create_webhook_routes(webhook_service: WebhookService) -> Blueprint:
    """
    Create webhook routes blueprint.
    
    Args:
        webhook_service: WebhookService instance
        
    Returns:
        Flask Blueprint with webhook endpoints.
    """
    bp = Blueprint('webhook', __name__, url_prefix='/api/webhook')
    
    @bp.route('/status', methods=['GET'])
    def get_webhook_status():
        """
        Get the current webhook status.
        
        This shows whether webhooks are being sent successfully or blocked.
        Useful for monitoring during the egress demo.
        """
        status = webhook_service.get_status()
        return jsonify({
            'success': True,
            **status
        })
    
    @bp.route('/test', methods=['POST'])
    def test_webhook():
        """
        Test the webhook connection manually.
        
        Use this to demonstrate egress being blocked/allowed!
        
        Try this endpoint:
        1. Before applying allow-webhook-egress → Should show BLOCKED
        2. After applying allow-webhook-egress → Should show SUCCESS
        """
        result = webhook_service.test_connection()
        
        if result.blocked:
            return jsonify({
                'success': False,
                'message': '❌ Webhook BLOCKED by NetworkPolicy!',
                'details': 'The grade-service cannot reach webhook-receiver in external-services namespace.',
                'hint': 'Apply the allow-webhook-egress NetworkPolicy to enable this.',
                'result': {
                    'success': result.success,
                    'error': result.error,
                    'blocked': result.blocked
                }
            })
        elif result.success:
            return jsonify({
                'success': True,
                'message': '✅ Webhook sent successfully!',
                'details': 'The grade-service can reach the webhook-receiver.',
                'result': {
                    'success': result.success,
                    'response': result.response
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': '⚠️ Webhook failed',
                'result': {
                    'success': result.success,
                    'error': result.error
                }
            })
    
    @bp.route('/test-external', methods=['GET'])
    def test_external_access():
        """
        Test endpoint to demonstrate NetworkPolicy blocking external egress.
        
        This tries to reach the public internet (httpbin.org).
        It should FAIL when NetworkPolicies are properly applied!
        """
        try:
            response = requests.get('https://httpbin.org/get', timeout=5)
            return jsonify({
                'success': True,
                'message': '⚠ WARNING: External access is allowed! NetworkPolicy not working.',
                'external_response': response.status_code
            })
        except requests.RequestException as e:
            return jsonify({
                'success': True,
                'message': '✓ External access blocked as expected by NetworkPolicy',
                'error': str(e)
            })
    
    return bp

