"""
Student repository.
Handles all database operations for students.
Implements the Repository pattern for data access abstraction.
"""
import sqlite3
from typing import List, Optional
from models.student import Student
from core.database import Database


class StudentRepository:
    """
    Repository for Student data access.
    
    This class encapsulates all database operations for students,
    providing a clean interface for the service layer.
    """
    
    def __init__(self, database: Database):
        """
        Initialize with database dependency.
        
        Args:
            database: Database instance (dependency injection)
        """
        self.db = database
        self._ensure_schema()
    
    def _ensure_schema(self) -> None:
        """Create tables if they don't exist."""
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                age INTEGER,
                major TEXT,
                gpa REAL
            )
        ''')
    
    def seed_sample_data(self) -> int:
        """
        Insert sample data for demo purposes.
        
        Returns:
            Number of records inserted.
        """
        sample_students = [
            ("Alice Johnson", "alice@university.edu", 20, "Computer Science", 3.8),
            ("Bob Smith", "bob@university.edu", 22, "Mathematics", 3.5),
            ("Charlie Brown", "charlie@university.edu", 21, "Physics", 3.9),
            ("Diana Prince", "diana@university.edu", 19, "Engineering", 3.7),
            ("Edward Norton", "edward@university.edu", 23, "Computer Science", 3.2),
            ("Fiona Apple", "fiona@university.edu", 20, "Biology", 3.6),
            ("George Lucas", "george@university.edu", 22, "Film Studies", 3.4),
            ("Hannah Montana", "hannah@university.edu", 21, "Music", 3.9),
            ("Ian McKellen", "ian@university.edu", 24, "Theater", 3.1),
            ("Julia Roberts", "julia@university.edu", 20, "Chemistry", 3.8)
        ]
        
        for student in sample_students:
            try:
                self.db.execute(
                    'INSERT INTO students (name, email, age, major, gpa) VALUES (?, ?, ?, ?, ?)',
                    student
                )
            except sqlite3.IntegrityError:
                pass  # Skip duplicates
        
        return len(sample_students)
    
    def find_all(self) -> List[Student]:
        """Get all students ordered by name."""
        rows = self.db.fetchall("SELECT * FROM students ORDER BY name")
        return [Student.from_row(row) for row in rows]
    
    def find_by_id(self, student_id: int) -> Optional[Student]:
        """Find student by ID."""
        row = self.db.fetchone("SELECT * FROM students WHERE id = ?", (student_id,))
        return Student.from_row(row) if row else None
    
    def find_by_email(self, email: str) -> Optional[Student]:
        """Find student by email."""
        row = self.db.fetchone("SELECT * FROM students WHERE email = ?", (email,))
        return Student.from_row(row) if row else None
    
    def search_by_name(self, search_term: str) -> List[Student]:
        """Search students by name (partial match)."""
        rows = self.db.fetchall(
            "SELECT * FROM students WHERE name LIKE ? ORDER BY name",
            (f'%{search_term}%',)
        )
        return [Student.from_row(row) for row in rows]
    
    def find_by_major(self, major: str) -> List[Student]:
        """Find students by major."""
        rows = self.db.fetchall(
            "SELECT * FROM students WHERE major = ? ORDER BY name",
            (major,)
        )
        return [Student.from_row(row) for row in rows]
    
    def get_all_majors(self) -> List[str]:
        """Get list of unique majors."""
        rows = self.db.fetchall("SELECT DISTINCT major FROM students ORDER BY major")
        return [row['major'] for row in rows if row['major']]
    
    def create(self, student: Student) -> int:
        """
        Create a new student.
        
        Args:
            student: Student to create (id is ignored)
            
        Returns:
            ID of the created student.
            
        Raises:
            sqlite3.IntegrityError: If email already exists.
        """
        cursor = self.db.execute(
            "INSERT INTO students (name, email, age, major, gpa) VALUES (?, ?, ?, ?, ?)",
            (student.name, student.email, student.age, student.major, student.gpa)
        )
        return cursor.lastrowid
    
    def update(self, student: Student) -> bool:
        """
        Update an existing student.
        
        Args:
            student: Student with updated values (must have id)
            
        Returns:
            True if student was updated, False if not found.
        """
        cursor = self.db.execute(
            """UPDATE students 
               SET name = ?, email = ?, age = ?, major = ?, gpa = ?
               WHERE id = ?""",
            (student.name, student.email, student.age, student.major, student.gpa, student.id)
        )
        return cursor.rowcount > 0
    
    def delete(self, student_id: int) -> bool:
        """
        Delete a student by ID.
        
        Returns:
            True if student was deleted, False if not found.
        """
        cursor = self.db.execute("DELETE FROM students WHERE id = ?", (student_id,))
        return cursor.rowcount > 0

