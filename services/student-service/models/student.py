"""
Student model.
Defines the Student entity and its data structure.
"""
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


@dataclass
class Student:
    """
    Student entity.
    
    Represents a student in the grading system.
    Uses dataclass for clean, immutable data representation.
    """
    id: Optional[int]
    name: str
    email: str
    age: Optional[int] = None
    major: Optional[str] = None
    gpa: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Student':
        """Create Student from dictionary."""
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            email=data.get('email', ''),
            age=data.get('age'),
            major=data.get('major'),
            gpa=data.get('gpa')
        )
    
    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> 'Student':
        """Create Student from database row."""
        return cls(
            id=row['id'],
            name=row['name'],
            email=row['email'],
            age=row.get('age'),
            major=row.get('major'),
            gpa=row.get('gpa')
        )

