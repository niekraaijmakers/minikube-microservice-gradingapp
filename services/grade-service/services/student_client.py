"""
Student service client.
Handles HTTP communication with the student-service.

This demonstrates EGRESS - making outbound calls to another service.
"""
import requests
from typing import Optional, Dict, Any
from core.config import Config


class StudentClient:
    """
    HTTP client for student-service.
    
    Encapsulates all communication with the student microservice.
    This is an example of the Gateway/Client pattern.
    """
    
    def __init__(self, base_url: str = None, timeout: int = 5):
        """
        Initialize client.
        
        Args:
            base_url: Student service URL (default from config)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or Config.STUDENT_SERVICE_URL
        self.timeout = timeout
    
    def get_student(self, student_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch a student by ID.
        
        Args:
            student_id: Student ID to fetch
            
        Returns:
            Student data dict or None if not found/unavailable.
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/students/{student_id}",
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data'):
                    return data['data']
            return None
        except requests.RequestException as e:
            print(f"⚠ Could not reach student-service: {e}")
            return None
    
    def get_student_name(self, student_id: int) -> str:
        """
        Get student name by ID.
        
        Args:
            student_id: Student ID
            
        Returns:
            Student name or "Unknown" if not found.
        """
        student = self.get_student(student_id)
        if student:
            return student.get('name', 'Unknown')
        return "Unknown"
    
    def student_exists(self, student_id: int) -> bool:
        """
        Check if a student exists.
        
        Args:
            student_id: Student ID to check
            
        Returns:
            True if student exists, False otherwise.
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/students/{student_id}",
                timeout=self.timeout
            )
            return response.status_code == 200
        except requests.RequestException:
            # If service unavailable, assume student exists
            return True

