"""
Database module.
Manages SQLite database connection using Singleton pattern.
"""
import sqlite3
from typing import List, Dict, Any, Optional


class Database:
    """
    Singleton database connection manager.
    
    Uses in-memory SQLite for demo purposes.
    In production, this would connect to a real database.
    """
    
    _instance: Optional['Database'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'Database':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not Database._initialized:
            self.connection = sqlite3.connect(':memory:', check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            Database._initialized = True
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query and commit."""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor
    
    def fetchall(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Fetch all rows as list of dicts."""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def fetchone(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Fetch single row as dict."""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None


# Global database instance
db = Database()

