"""
Student Service - Microservice for student management.

This service demonstrates a clean layered architecture:
- models/       Data classes and domain entities
- repositories/ Data access layer (database operations)
- services/     Business logic layer
- routes/       HTTP endpoint handlers (presentation layer)
- core/         Configuration and shared utilities

Architecture Principles:
1. Dependency Injection - components receive their dependencies
2. Single Responsibility - each class has one job
3. Separation of Concerns - layers don't know about each other
"""
from flask import Flask, jsonify
from flask_cors import CORS

# Core
from core.config import Config
from core.database import db

# Layers
from repositories.student_repository import StudentRepository
from services.student_service import StudentService
from routes.student_routes import create_student_routes
from routes.health_routes import create_health_routes


def create_app() -> Flask:
    """
    Application factory.
    
    Creates and configures the Flask application with all dependencies
    wired together using dependency injection.
    
    Returns:
        Configured Flask application.
    """
    app = Flask(__name__)
    CORS(app)
    
    # === DEPENDENCY INJECTION ===
    # Wire up the layers from bottom to top:
    # Database -> Repository -> Service -> Routes
    
    # 1. Repository layer (depends on database)
    student_repository = StudentRepository(db)
    
    # 2. Service layer (depends on repository)
    student_service = StudentService(student_repository)
    
    # 3. Register routes (depends on service)
    app.register_blueprint(create_health_routes())
    app.register_blueprint(create_student_routes(student_service))
    
    # === ERROR HANDLERS ===
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Endpoint not found'
        }), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    return app


def initialize_database(repository: StudentRepository) -> None:
    """Seed database with sample data."""
    count = repository.seed_sample_data()
    print(f"✓ Database initialized with {count} sample students")


# Create app and initialize
app = create_app()

# Initialize database with sample data
student_repository = StudentRepository(db)
initialize_database(student_repository)


if __name__ == '__main__':
    print(f"""
╔════════════════════════════════════════════════════════════╗
║              STUDENT SERVICE - Starting                     ║
╠════════════════════════════════════════════════════════════╣
║  Port: {Config.SERVICE_PORT}                                              ║
║  Database: In-memory SQLite                                 ║
║                                                             ║
║  Architecture:                                              ║
║    models/        → Data classes                            ║
║    repositories/  → Data access layer                       ║
║    services/      → Business logic                          ║
║    routes/        → HTTP endpoints                          ║
║                                                             ║
║  Endpoints:                                                 ║
║    GET  /health              - Health check                 ║
║    GET  /api/students        - List all students            ║
║    GET  /api/students/<id>   - Get student by ID            ║
║    POST /api/students        - Create student               ║
║    DELETE /api/students/<id> - Delete student               ║
║    GET  /api/students/majors - List majors                  ║
╚════════════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=Config.SERVICE_PORT, debug=True)
