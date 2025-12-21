"""
Webhook Receiver - Simulates an External Webhook Service
=========================================================
This service simulates an external webhook endpoint (like Slack, email service, etc.)
It runs in a SEPARATE NAMESPACE to simulate being "external" to our application.

This is used to demonstrate EGRESS network policies:
- When egress is BLOCKED: grade-service cannot reach this webhook
- When egress is ALLOWED: grade-service can send notifications here
"""
import os
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 5005))

# Store received webhooks in memory (for demo purposes)
received_webhooks = []


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'webhook-receiver',
        'namespace': 'external-services',
        'message': 'External webhook service ready to receive notifications'
    })


@app.route('/webhook/grade-notification', methods=['POST'])
def receive_grade_notification():
    """
    Receive grade notification webhook.
    This endpoint is called by grade-service when a new grade is posted.
    """
    data = request.get_json() or {}
    
    webhook_entry = {
        'id': len(received_webhooks) + 1,
        'timestamp': datetime.now().isoformat(),
        'type': 'grade_notification',
        'data': data,
        'source_ip': request.remote_addr
    }
    
    received_webhooks.append(webhook_entry)
    
    # Keep only last 50 webhooks
    if len(received_webhooks) > 50:
        received_webhooks.pop(0)
    
    print(f"📨 Received webhook: {data}")
    
    return jsonify({
        'success': True,
        'message': 'Webhook received successfully',
        'webhook_id': webhook_entry['id']
    }), 200


@app.route('/webhook/history', methods=['GET'])
def get_webhook_history():
    """Get history of received webhooks."""
    return jsonify({
        'success': True,
        'count': len(received_webhooks),
        'webhooks': list(reversed(received_webhooks))  # Most recent first
    })


@app.route('/webhook/clear', methods=['POST'])
def clear_history():
    """Clear webhook history."""
    received_webhooks.clear()
    return jsonify({
        'success': True,
        'message': 'Webhook history cleared'
    })


if __name__ == '__main__':
    print(f"""
╔════════════════════════════════════════════════════════════╗
║         WEBHOOK RECEIVER - External Service                 ║
╠════════════════════════════════════════════════════════════╣
║  Port: {SERVICE_PORT}                                              ║
║  Namespace: external-services                               ║
║                                                             ║
║  This simulates an EXTERNAL webhook service.                ║
║  Grade-service will try to call this when grades are added. ║
║                                                             ║
║  Endpoints:                                                 ║
║    POST /webhook/grade-notification - Receive notification  ║
║    GET  /webhook/history            - View received hooks   ║
║    POST /webhook/clear              - Clear history         ║
║    GET  /health                     - Health check          ║
╚════════════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)

