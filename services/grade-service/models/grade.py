"""
Grade model.
Defines the Grade entity and its data structure.
"""
from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any, List


# Valid grade values
VALID_GRADES: List[str] = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D', 'F']


@dataclass
class Grade:
    """
    Grade entity.
    
    Represents a grade record in the grading system.
    """
    id: Optional[int]
    student_id: int
    course: str
    grade: str
    semester: str
    credits: int = 3
    
    # Enriched field (not stored in DB)
    student_name: Optional[str] = field(default=None, compare=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        # Remove None student_name if not enriched
        if result.get('student_name') is None:
            del result['student_name']
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Grade':
        """Create Grade from dictionary."""
        return cls(
            id=data.get('id'),
            student_id=data.get('student_id'),
            course=data.get('course', ''),
            grade=data.get('grade', ''),
            semester=data.get('semester', ''),
            credits=data.get('credits', 3),
            student_name=data.get('student_name')
        )
    
    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> 'Grade':
        """Create Grade from database row."""
        return cls(
            id=row['id'],
            student_id=row['student_id'],
            course=row['course'],
            grade=row['grade'],
            semester=row['semester'],
            credits=row['credits']
        )
    
    def is_valid_grade(self) -> bool:
        """Check if grade value is valid."""
        return self.grade in VALID_GRADES

