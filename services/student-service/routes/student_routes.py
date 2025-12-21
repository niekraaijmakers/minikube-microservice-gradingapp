"""
Student routes.
HTTP endpoints for student management.
"""
from flask import Blueprint, jsonify, request
from services.student_service import StudentService
from models.student import Student


def create_student_routes(student_service: StudentService) -> Blueprint:
    """
    Create student routes blueprint.
    
    Args:
        student_service: StudentService instance (dependency injection)
        
    Returns:
        Flask Blueprint with student endpoints.
    """
    bp = Blueprint('students', __name__, url_prefix='/api/students')
    
    @bp.route('', methods=['GET'])
    def get_students():
        """Get all students with optional filtering."""
        search = request.args.get('search', '').strip()
        major = request.args.get('major', '').strip()
        
        if search:
            students = student_service.search_students(search)
        elif major:
            students = student_service.filter_by_major(major)
        else:
            students = student_service.get_all_students()
        
        return jsonify({
            'success': True,
            'count': len(students),
            'data': [s.to_dict() for s in students]
        })
    
    @bp.route('/<int:student_id>', methods=['GET'])
    def get_student(student_id: int):
        """Get a single student by ID."""
        student = student_service.get_student(student_id)
        
        if not student:
            return jsonify({
                'success': False,
                'error': 'Student not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': student.to_dict()
        })
    
    @bp.route('', methods=['POST'])
    def create_student():
        """Create a new student."""
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Create Student model from request data
        student = Student(
            id=None,
            name=data.get('name', '').strip(),
            email=data.get('email', '').strip(),
            age=data.get('age'),
            major=data.get('major', '').strip() or None,
            gpa=data.get('gpa')
        )
        
        success, message, student_id = student_service.create_student(student)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': {'id': student_id}
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400
    
    @bp.route('/<int:student_id>', methods=['DELETE'])
    def delete_student(student_id: int):
        """Delete a student by ID."""
        success, message = student_service.delete_student(student_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 404
    
    @bp.route('/majors', methods=['GET'])
    def get_majors():
        """Get list of all unique majors."""
        majors = student_service.get_all_majors()
        return jsonify({
            'success': True,
            'data': majors
        })
    
    return bp

