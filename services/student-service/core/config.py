"""
Configuration module.
Centralizes all configuration and environment variables.
"""
import os


class Config:
    """Application configuration loaded from environment variables."""
    
    SERVICE_NAME = "student-service"
    VERSION = "1.0.0"
    
    # Server
    SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 5001))
    DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    # Database
    DATABASE_PATH = os.environ.get('DATABASE_PATH', ':memory:')

