"""
External notifier service.
Demonstrates EGRESS by calling an external URL when a grade is created.

This is used to demonstrate NetworkPolicy egress control:
- With default-deny policy: This call will be BLOCKED (timeout)
- With egress policy allowing external access: This call will SUCCEED
"""
import logging
import requests
from dataclasses import dataclass
from typing import Optional
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# External URL for egress demonstration
EXTERNAL_URL = os.environ.get('EXTERNAL_NOTIFY_URL', 'https://httpbin.org/get')
EXTERNAL_TIMEOUT = int(os.environ.get('EXTERNAL_TIMEOUT', '5'))


@dataclass
class ExternalNotifyResult:
    """Result of external notification attempt."""
    success: bool
    blocked: bool
    message: str
    response_data: Optional[dict] = None


class ExternalNotifier:
    """
    Simulates sending a notification to an external service.
    
    This demonstrates EGRESS - outbound traffic from the pod to the internet.
    NetworkPolicy can block this traffic.
    """
    
    def __init__(self, url: str = None, timeout: int = None):
        """
        Initialize the notifier.
        
        Args:
            url: External URL to call (default: httpbin.org)
            timeout: Request timeout in seconds
        """
        self.url = url or EXTERNAL_URL
        self.timeout = timeout or EXTERNAL_TIMEOUT
    
    def notify_grade_created(self, student_name: str, course: str, grade: str) -> ExternalNotifyResult:
        """
        Attempt to notify an external service about a new grade.
        
        This call will be blocked if NetworkPolicy doesn't allow external egress.
        
        Args:
            student_name: Name of the student
            course: Course name
            grade: Grade value
            
        Returns:
            ExternalNotifyResult indicating success or if blocked by NetworkPolicy.
        """
        logger.info(f"📤 EGRESS: Attempting external notification to {self.url}")
        logger.info(f"   Student: {student_name}, Course: {course}, Grade: {grade}")
        
        try:
            # Make a simple GET request to the external URL
            # We pass grade info as query params (httpbin.org will echo them back)
            response = requests.get(
                self.url,
                params={
                    'event': 'grade_created',
                    'student': student_name,
                    'course': course,
                    'grade': grade
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                logger.info(f"✅ EGRESS SUCCESS: External notification sent to {self.url}")
                return ExternalNotifyResult(
                    success=True,
                    blocked=False,
                    message="External notification sent successfully",
                    response_data=response.json() if response.headers.get('content-type', '').startswith('application/json') else None
                )
            else:
                logger.warning(f"⚠️ EGRESS FAILED: External service returned status {response.status_code}")
                return ExternalNotifyResult(
                    success=False,
                    blocked=False,
                    message=f"External service returned status {response.status_code}"
                )
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ EGRESS BLOCKED: Connection to {self.url} timed out (NetworkPolicy likely blocking)")
            return ExternalNotifyResult(
                success=False,
                blocked=True,
                message="Connection timed out - likely blocked by NetworkPolicy"
            )
        except requests.exceptions.ConnectionError as e:
            logger.error(f"❌ EGRESS BLOCKED: Connection to {self.url} failed (NetworkPolicy likely blocking)")
            return ExternalNotifyResult(
                success=False,
                blocked=True,
                message=f"Connection failed - likely blocked by NetworkPolicy: {str(e)}"
            )
        except Exception as e:
            logger.error(f"❌ EGRESS ERROR: Unexpected error calling {self.url}: {str(e)}")
            return ExternalNotifyResult(
                success=False,
                blocked=False,
                message=f"Unexpected error: {str(e)}"
            )
    
    def test_egress(self) -> ExternalNotifyResult:
        """
        Test if external egress is allowed.
        
        Returns:
            ExternalNotifyResult indicating if egress is blocked or allowed.
        """
        return self.notify_grade_created("Test Student", "TEST101", "A")

