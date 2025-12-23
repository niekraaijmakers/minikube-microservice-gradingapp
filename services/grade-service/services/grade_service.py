"""
Grade service.
Contains business logic for grade operations.
"""
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any
from models.grade import Grade, VALID_GRADES
from repositories.grade_repository import GradeRepository
from services.student_client import StudentClient
from services.external_notifier import ExternalNotifier, ExternalNotifyResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of validation operation."""
    is_valid: bool
    errors: List[str]


@dataclass
class CreateGradeResult:
    """Result of grade creation operation."""
    success: bool
    message: str
    grade_id: Optional[int] = None
    egress_result: Optional[Dict[str, Any]] = None


class GradeService:
    """
    Business logic for grade operations.
    
    Orchestrates:
    - Grade repository (data access)
    - Student client (internal service call)
    - External notifier (external egress - may be blocked by NetworkPolicy!)
    """
    
    def __init__(
        self, 
        repository: GradeRepository,
        student_client: StudentClient,
        external_notifier: ExternalNotifier = None
    ):
        """
        Initialize with dependencies.
        
        Args:
            repository: GradeRepository for data access
            student_client: StudentClient for student lookups
            external_notifier: ExternalNotifier for egress demo
        """
        self.repository = repository
        self.student_client = student_client
        self.external_notifier = external_notifier or ExternalNotifier()
    
    def validate_grade(self, grade: Grade) -> ValidationResult:
        """
        Validate grade data.
        
        Returns:
            ValidationResult with is_valid flag and list of errors.
        """
        errors = []
        
        if not grade.student_id:
            errors.append("Student ID is required")
        
        if not grade.course or len(grade.course.strip()) < 2:
            errors.append("Course name must be at least 2 characters")
        
        if not grade.grade:
            errors.append("Grade is required")
        elif grade.grade not in VALID_GRADES:
            errors.append(f"Invalid grade. Must be one of: {', '.join(VALID_GRADES)}")
        
        if not grade.semester:
            errors.append("Semester is required")
        
        if grade.credits is not None:
            if not isinstance(grade.credits, int):
                try:
                    grade.credits = int(grade.credits)
                except (ValueError, TypeError):
                    errors.append("Credits must be a number")
            if isinstance(grade.credits, int) and (grade.credits < 1 or grade.credits > 6):
                errors.append("Credits must be between 1 and 6")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
    
    def get_all_grades(
        self, 
        student_id: Optional[int] = None,
        course: Optional[str] = None,
        semester: Optional[str] = None,
        enrich: bool = True
    ) -> List[Grade]:
        """
        Get all grades with optional filtering.
        
        Args:
            student_id: Filter by student
            course: Filter by course (partial match)
            semester: Filter by semester
            enrich: Whether to add student names
        """
        grades = self.repository.find_all(student_id, course, semester)
        
        if enrich:
            self._enrich_with_student_names(grades)
        
        return grades
    
    def get_grade(self, grade_id: int, enrich: bool = True) -> Optional[Grade]:
        """Get a single grade by ID."""
        grade = self.repository.find_by_id(grade_id)
        
        if grade and enrich:
            grade.student_name = self.student_client.get_student_name(grade.student_id)
        
        return grade
    
    def get_all_semesters(self) -> List[str]:
        """Get list of all unique semesters."""
        return self.repository.get_all_semesters()
    
    def get_all_courses(self) -> List[str]:
        """Get list of all unique courses."""
        return self.repository.get_all_courses()
    
    def create_grade(self, grade: Grade) -> CreateGradeResult:
        """
        Create a new grade.
        
        This method demonstrates EGRESS patterns:
        1. Internal egress: Calls student-service to verify student exists
        2. External egress: Attempts to notify external service (may be blocked!)
        
        Args:
            grade: Grade to create
            
        Returns:
            CreateGradeResult with success status, message, and egress result.
        """
        # Validate
        validation = self.validate_grade(grade)
        if not validation.is_valid:
            return CreateGradeResult(
                success=False, 
                message="; ".join(validation.errors)
            )
        
        # Verify student exists (INTERNAL egress to student-service)
        if not self.student_client.student_exists(grade.student_id):
            return CreateGradeResult(
                success=False, 
                message="Student not found"
            )
        
        # Get student name for notification
        student_name = self.student_client.get_student_name(grade.student_id)
        
        # Create grade
        try:
            grade_id = self.repository.create(grade)
            logger.info(f"📝 GRADE CREATED: ID={grade_id}, Student={student_name}, Course={grade.course}, Grade={grade.grade}")
        except Exception as e:
            logger.error(f"❌ GRADE CREATION FAILED: {str(e)}")
            return CreateGradeResult(
                success=False, 
                message=f"Failed to create grade: {str(e)}"
            )
        
        # Attempt EXTERNAL egress - notify external service
        # This will be BLOCKED if NetworkPolicy doesn't allow external access!
        egress_result = self.external_notifier.notify_grade_created(
            student_name=student_name,
            course=grade.course,
            grade=grade.grade
        )
        
        return CreateGradeResult(
            success=True,
            message="Grade created successfully",
            grade_id=grade_id,
            egress_result={
                'success': egress_result.success,
                'blocked': egress_result.blocked,
                'message': egress_result.message
            }
        )
    
    def delete_grade(self, grade_id: int) -> Tuple[bool, str]:
        """
        Delete a grade by ID.
        
        Returns:
            Tuple of (success, message)
        """
        grade = self.repository.find_by_id(grade_id)
        if not grade:
            return False, "Grade not found"
        
        if self.repository.delete(grade_id):
            return True, "Grade deleted successfully"
        else:
            return False, "Failed to delete grade"
    
    def _enrich_with_student_names(self, grades: List[Grade]) -> None:
        """
        Add student names to grade records.
        
        Uses caching to avoid repeated service calls.
        """
        student_cache = {}
        
        for grade in grades:
            if grade.student_id not in student_cache:
                student_cache[grade.student_id] = self.student_client.get_student_name(
                    grade.student_id
                )
            grade.student_name = student_cache[grade.student_id]

