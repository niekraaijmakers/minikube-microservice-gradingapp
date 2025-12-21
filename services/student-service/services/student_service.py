"""
Student service.
Contains business logic for student operations.
"""
from dataclasses import dataclass
from typing import List, Optional, Tuple
from models.student import Student
from repositories.student_repository import StudentRepository


@dataclass
class ValidationResult:
    """Result of validation operation."""
    is_valid: bool
    errors: List[str]


class StudentService:
    """
    Business logic for student operations.
    
    This class handles validation, business rules, and orchestrates
    calls to the repository. It does NOT know about HTTP or databases.
    """
    
    def __init__(self, repository: StudentRepository):
        """
        Initialize with repository dependency.
        
        Args:
            repository: StudentRepository instance (dependency injection)
        """
        self.repository = repository
    
    def validate_student(self, student: Student, is_update: bool = False) -> ValidationResult:
        """
        Validate student data.
        
        Args:
            student: Student to validate
            is_update: Whether this is an update (skip email uniqueness check)
            
        Returns:
            ValidationResult with is_valid flag and list of errors.
        """
        errors = []
        
        # Name validation
        if not student.name or len(student.name.strip()) < 2:
            errors.append("Name must be at least 2 characters")
        
        # Email validation
        if not student.email or '@' not in student.email:
            errors.append("Invalid email address")
        
        # Age validation
        if student.age is not None:
            if not isinstance(student.age, int):
                try:
                    student.age = int(student.age)
                except (ValueError, TypeError):
                    errors.append("Age must be a number")
            if isinstance(student.age, int) and (student.age < 16 or student.age > 100):
                errors.append("Age must be between 16 and 100")
        
        # GPA validation
        if student.gpa is not None:
            if not isinstance(student.gpa, (int, float)):
                try:
                    student.gpa = float(student.gpa)
                except (ValueError, TypeError):
                    errors.append("GPA must be a number")
            if isinstance(student.gpa, (int, float)) and (student.gpa < 0 or student.gpa > 4.0):
                errors.append("GPA must be between 0 and 4.0")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
    
    def get_all_students(self) -> List[Student]:
        """Get all students."""
        return self.repository.find_all()
    
    def search_students(self, search_term: str) -> List[Student]:
        """Search students by name."""
        return self.repository.search_by_name(search_term)
    
    def filter_by_major(self, major: str) -> List[Student]:
        """Filter students by major."""
        return self.repository.find_by_major(major)
    
    def get_student(self, student_id: int) -> Optional[Student]:
        """Get a single student by ID."""
        return self.repository.find_by_id(student_id)
    
    def get_all_majors(self) -> List[str]:
        """Get list of all unique majors."""
        return self.repository.get_all_majors()
    
    def create_student(self, student: Student) -> Tuple[bool, str, Optional[int]]:
        """
        Create a new student.
        
        Args:
            student: Student to create
            
        Returns:
            Tuple of (success, message, created_id)
        """
        # Validate
        validation = self.validate_student(student)
        if not validation.is_valid:
            return False, "; ".join(validation.errors), None
        
        # Check for duplicate email
        existing = self.repository.find_by_email(student.email)
        if existing:
            return False, "Email already exists", None
        
        # Create
        try:
            student_id = self.repository.create(student)
            return True, "Student created successfully", student_id
        except Exception as e:
            return False, f"Failed to create student: {str(e)}", None
    
    def delete_student(self, student_id: int) -> Tuple[bool, str]:
        """
        Delete a student by ID.
        
        Returns:
            Tuple of (success, message)
        """
        student = self.repository.find_by_id(student_id)
        if not student:
            return False, "Student not found"
        
        if self.repository.delete(student_id):
            return True, "Student deleted successfully"
        else:
            return False, "Failed to delete student"

