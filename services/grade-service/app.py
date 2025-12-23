"""
Grade Service - Microservice for grade management.

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
4. Gateway Pattern - StudentClient abstracts external service
"""
from flask import Flask, jsonify
from flask_cors import CORS

# Core
from core.config import Config
from core.database import db

# Layers
from repositories.grade_repository import GradeRepository
from services.student_client import StudentClient
from services.external_notifier import ExternalNotifier
from services.grade_service import GradeService
from routes.grade_routes import create_grade_routes
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
    # Wire up the layers from bottom to top
    
    # 1. Repository layer (depends on database)
    grade_repository = GradeRepository(db)
    
    # 2. External service clients
    student_client = StudentClient()
    external_notifier = ExternalNotifier()  # Calls httpbin.org (EGRESS DEMO!)
    
    # 3. Service layer (depends on repository + clients)
    grade_service = GradeService(
        repository=grade_repository,
        student_client=student_client,
        external_notifier=external_notifier
    )
    
    # 4. Register routes (depends on services)
    app.register_blueprint(create_health_routes())
    app.register_blueprint(create_grade_routes(grade_service))
    
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


def initialize_database(repository: GradeRepository) -> None:
    """Seed database with sample data."""
    count = repository.seed_sample_data()
    print(f"✓ Database initialized with {count} sample grades")


# Create app and initialize
app = create_app()

# Initialize database with sample data
grade_repository = GradeRepository(db)
initialize_database(grade_repository)


if __name__ == '__main__':
    print(f"""
╔════════════════════════════════════════════════════════════╗
║               GRADE SERVICE - Starting                      ║
╠════════════════════════════════════════════════════════════╣
║  Port: {Config.SERVICE_PORT}                                              ║
║  Student Service: {Config.STUDENT_SERVICE_URL:<34} ║
║  Database: In-memory SQLite                                 ║
║                                                             ║
║  Architecture:                                              ║
║    models/        → Data classes                            ║
║    repositories/  → Data access layer                       ║
║    services/      → Business logic + external clients       ║
║    routes/        → HTTP endpoints                          ║
║                                                             ║
║  Endpoints:                                                 ║
║    GET  /health               - Health check                ║
║    GET  /api/grades           - List all grades             ║
║    GET  /api/grades/<id>      - Get grade by ID             ║
║    POST /api/grades           - Create grade (+ egress!)    ║
║    DELETE /api/grades/<id>    - Delete grade                ║
║    GET  /api/grades/semesters - List semesters              ║
║    GET  /api/grades/courses   - List courses                ║
║                                                             ║
║  EGRESS DEMO: POST /api/grades calls httpbin.org            ║
║  (will be blocked if NetworkPolicy denies external egress)  ║
╚════════════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=Config.SERVICE_PORT, debug=True)
