"""
Webhook status models.
Tracks webhook delivery status for egress demonstration.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class WebhookResult:
    """Result of a webhook delivery attempt."""
    success: bool
    error: Optional[str] = None
    blocked: bool = False
    response: Optional[Dict[str, Any]] = None


@dataclass
class WebhookStatus:
    """
    Tracks overall webhook delivery statistics.
    
    Useful for demonstrating egress policy effects.
    """
    last_attempt: Optional[str] = None
    last_success: Optional[str] = None
    last_error: Optional[str] = None
    total_attempts: int = 0
    total_successes: int = 0
    total_failures: int = 0
    
    def record_attempt(self) -> None:
        """Record a webhook attempt."""
        self.total_attempts += 1
        self.last_attempt = datetime.now().isoformat()
    
    def record_success(self) -> None:
        """Record successful webhook delivery."""
        self.total_successes += 1
        self.last_success = datetime.now().isoformat()
        self.last_error = None
    
    def record_failure(self, error: str) -> None:
        """Record failed webhook delivery."""
        self.total_failures += 1
        self.last_error = error
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'last_attempt': self.last_attempt,
            'last_success': self.last_success,
            'last_error': self.last_error,
            'total_attempts': self.total_attempts,
            'total_successes': self.total_successes,
            'total_failures': self.total_failures
        }

