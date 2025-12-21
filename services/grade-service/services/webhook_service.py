"""
Webhook service.
Handles sending notifications to external webhook receivers.

THIS IS THE KEY EGRESS DEMONSTRATION!

When NetworkPolicy blocks egress to external-services namespace:
  → Webhook calls will FAIL with timeout/connection errors.

When NetworkPolicy allows egress to external-services namespace:
  → Webhook calls will SUCCEED and receiver will log notifications.
"""
import requests
from datetime import datetime
from typing import Dict, Any
from models.webhook_status import WebhookStatus, WebhookResult
from models.grade import Grade
from core.config import Config


class WebhookService:
    """
    Service for sending webhook notifications.
    
    Demonstrates egress to an external service (different namespace).
    """
    
    def __init__(self, webhook_url: str = None, enabled: bool = None, timeout: int = 5):
        """
        Initialize webhook service.
        
        Args:
            webhook_url: Webhook receiver URL (default from config)
            enabled: Whether webhooks are enabled (default from config)
            timeout: Request timeout in seconds
        """
        self.webhook_url = webhook_url or Config.WEBHOOK_URL
        self.enabled = enabled if enabled is not None else Config.WEBHOOK_ENABLED
        self.timeout = timeout
        
        # Track webhook statistics
        self.status = WebhookStatus()
    
    def send_grade_notification(self, grade: Grade, student_name: str) -> WebhookResult:
        """
        Send notification when a grade is created.
        
        THIS IS THE KEY EGRESS DEMONSTRATION!
        
        Args:
            grade: Grade that was created
            student_name: Name of the student
            
        Returns:
            WebhookResult indicating success/failure.
        """
        if not self.enabled:
            return WebhookResult(success=False, error='Webhooks disabled')
        
        self.status.record_attempt()
        
        payload = self._build_payload(grade, student_name)
        
        return self._send_webhook(payload)
    
    def _build_payload(self, grade: Grade, student_name: str) -> Dict[str, Any]:
        """Build webhook payload."""
        return {
            'event': 'grade_created',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'student_id': grade.student_id,
                'student_name': student_name,
                'course': grade.course,
                'grade': grade.grade,
                'semester': grade.semester,
                'credits': grade.credits
            },
            'message': f"New grade posted: {student_name} received {grade.grade} in {grade.course}"
        }
    
    def _send_webhook(self, payload: Dict[str, Any]) -> WebhookResult:
        """
        Send HTTP POST to webhook receiver.
        
        This is where egress happens - the request leaves our pod
        and travels to the external-services namespace.
        """
        try:
            url = f"{self.webhook_url}/webhook/grade-notification"
            print(f"📤 Sending webhook to {url}")
            
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                self.status.record_success()
                print("✅ Webhook sent successfully!")
                return WebhookResult(
                    success=True, 
                    response=response.json()
                )
            else:
                error = f"HTTP {response.status_code}"
                self.status.record_failure(error)
                print(f"⚠️ Webhook failed: {error}")
                return WebhookResult(success=False, error=error)
                
        except requests.exceptions.Timeout:
            error = "Connection timeout - likely blocked by NetworkPolicy"
            self.status.record_failure(error)
            print(f"❌ Webhook BLOCKED: {error}")
            return WebhookResult(success=False, error=error, blocked=True)
            
        except requests.exceptions.ConnectionError as e:
            error = f"Connection refused - likely blocked by NetworkPolicy"
            self.status.record_failure(error)
            print(f"❌ Webhook BLOCKED: {error}")
            return WebhookResult(success=False, error=error, blocked=True)
            
        except requests.RequestException as e:
            error = str(e)
            self.status.record_failure(error)
            print(f"❌ Webhook failed: {error}")
            return WebhookResult(success=False, error=error)
    
    def test_connection(self) -> WebhookResult:
        """
        Test webhook connectivity.
        
        Use this to demonstrate egress being blocked/allowed!
        """
        test_payload = {
            'event': 'test',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'student_id': 0,
                'student_name': 'Test Student',
                'course': 'TEST',
                'grade': 'A',
                'semester': 'Test',
                'credits': 0
            },
            'message': 'Test webhook - demonstrating egress'
        }
        return self._send_webhook(test_payload)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current webhook status for monitoring."""
        return {
            'webhook_url': self.webhook_url,
            'webhook_enabled': self.enabled,
            'status': self.status.to_dict()
        }

