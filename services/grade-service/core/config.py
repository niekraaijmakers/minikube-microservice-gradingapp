"""
Configuration module.
Centralizes all configuration and environment variables.
"""
import os


class Config:
    """Application configuration loaded from environment variables."""
    
    SERVICE_NAME = "grade-service"
    VERSION = "1.0.0"
    
    # Server
    SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 5002))
    DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    # Database
    DATABASE_PATH = os.environ.get('DATABASE_PATH', ':memory:')
    
    # External Services
    STUDENT_SERVICE_URL = os.environ.get(
        'STUDENT_SERVICE_URL', 
        'http://student-service:5001'
    )
    
    # Webhook Configuration (for EGRESS demo)
    WEBHOOK_URL = os.environ.get(
        'WEBHOOK_URL', 
        'http://webhook-receiver.external-services.svc.cluster.local:5005'
    )
    WEBHOOK_ENABLED = os.environ.get('WEBHOOK_ENABLED', 'true').lower() == 'true'

