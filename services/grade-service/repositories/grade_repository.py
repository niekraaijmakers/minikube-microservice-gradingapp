"""
Grade repository.
Handles all database operations for grades.
"""
from typing import List, Optional
from models.grade import Grade
from core.database import Database


class GradeRepository:
    """
    Repository for Grade data access.
    
    Encapsulates all database operations for grades.
    """
    
    def __init__(self, database: Database):
        """Initialize with database dependency."""
        self.db = database
        self._ensure_schema()
    
    def _ensure_schema(self) -> None:
        """Create tables if they don't exist."""
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course TEXT NOT NULL,
                grade TEXT NOT NULL,
                semester TEXT NOT NULL,
                credits INTEGER NOT NULL DEFAULT 3
            )
        ''')
    
    def seed_sample_data(self) -> int:
        """Insert sample data for demo purposes."""
        sample_grades = [
            (1, "Introduction to Programming", "A", "Fall 2024", 4),
            (1, "Data Structures", "A-", "Fall 2024", 4),
            (1, "Web Development", "B+", "Spring 2024", 3),
            (2, "Calculus I", "B", "Fall 2024", 4),
            (2, "Linear Algebra", "A-", "Fall 2024", 3),
            (3, "Quantum Mechanics", "A", "Fall 2024", 4),
            (3, "Classical Mechanics", "A", "Spring 2024", 4),
            (4, "Thermodynamics", "B+", "Fall 2024", 3),
            (4, "Circuit Design", "A-", "Fall 2024", 4),
            (5, "Operating Systems", "C+", "Fall 2024", 4),
            (5, "Computer Networks", "B", "Spring 2024", 3),
            (6, "Molecular Biology", "A-", "Fall 2024", 4),
            (6, "Genetics", "A", "Spring 2024", 4),
            (7, "Film History", "B+", "Fall 2024", 3),
            (7, "Screenwriting", "B", "Spring 2024", 3),
            (8, "Music Theory", "A", "Fall 2024", 4),
            (8, "Performance Art", "A", "Fall 2024", 2),
            (9, "Shakespeare Studies", "C", "Fall 2024", 3),
            (9, "Modern Drama", "B-", "Spring 2024", 3),
            (10, "Organic Chemistry", "A-", "Fall 2024", 4),
            (10, "Analytical Chemistry", "A", "Spring 2024", 3)
        ]
        
        for grade in sample_grades:
            self.db.execute(
                'INSERT INTO grades (student_id, course, grade, semester, credits) VALUES (?, ?, ?, ?, ?)',
                grade
            )
        
        return len(sample_grades)
    
    def find_all(self, student_id: Optional[int] = None, 
                 course: Optional[str] = None, 
                 semester: Optional[str] = None) -> List[Grade]:
        """
        Get all grades with optional filtering.
        
        Args:
            student_id: Filter by student ID
            course: Filter by course name (partial match)
            semester: Filter by semester (exact match)
        """
        query = "SELECT * FROM grades WHERE 1=1"
        params = []
        
        if student_id:
            query += " AND student_id = ?"
            params.append(student_id)
        if course:
            query += " AND course LIKE ?"
            params.append(f'%{course}%')
        if semester:
            query += " AND semester = ?"
            params.append(semester)
        
        query += " ORDER BY semester DESC, course"
        
        rows = self.db.fetchall(query, tuple(params))
        return [Grade.from_row(row) for row in rows]
    
    def find_by_id(self, grade_id: int) -> Optional[Grade]:
        """Find grade by ID."""
        row = self.db.fetchone("SELECT * FROM grades WHERE id = ?", (grade_id,))
        return Grade.from_row(row) if row else None
    
    def get_all_semesters(self) -> List[str]:
        """Get list of unique semesters."""
        rows = self.db.fetchall("SELECT DISTINCT semester FROM grades ORDER BY semester DESC")
        return [row['semester'] for row in rows if row['semester']]
    
    def get_all_courses(self) -> List[str]:
        """Get list of unique courses."""
        rows = self.db.fetchall("SELECT DISTINCT course FROM grades ORDER BY course")
        return [row['course'] for row in rows if row['course']]
    
    def create(self, grade: Grade) -> int:
        """
        Create a new grade.
        
        Returns:
            ID of the created grade.
        """
        cursor = self.db.execute(
            "INSERT INTO grades (student_id, course, grade, semester, credits) VALUES (?, ?, ?, ?, ?)",
            (grade.student_id, grade.course, grade.grade, grade.semester, grade.credits)
        )
        return cursor.lastrowid
    
    def delete(self, grade_id: int) -> bool:
        """
        Delete a grade by ID.
        
        Returns:
            True if grade was deleted, False if not found.
        """
        cursor = self.db.execute("DELETE FROM grades WHERE id = ?", (grade_id,))
        return cursor.rowcount > 0

