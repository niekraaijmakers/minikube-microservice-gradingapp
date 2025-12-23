"""
Grade routes.
HTTP endpoints for grade management.
"""
from flask import Blueprint, jsonify, request
from services.grade_service import GradeService
from models.grade import Grade


def create_grade_routes(grade_service: GradeService) -> Blueprint:
    """
    Create grade routes blueprint.
    
    Args:
        grade_service: GradeService instance (dependency injection)
        
    Returns:
        Flask Blueprint with grade endpoints.
    """
    bp = Blueprint('grades', __name__, url_prefix='/api/grades')
    
    @bp.route('', methods=['GET'])
    def get_grades():
        """Get all grades with optional filtering."""
        student_id = request.args.get('student_id', '').strip()
        course = request.args.get('course', '').strip()
        semester = request.args.get('semester', '').strip()
        
        grades = grade_service.get_all_grades(
            student_id=int(student_id) if student_id else None,
            course=course or None,
            semester=semester or None
        )
        
        return jsonify({
            'success': True,
            'count': len(grades),
            'data': [g.to_dict() for g in grades]
        })
    
    @bp.route('/<int:grade_id>', methods=['GET'])
    def get_grade(grade_id: int):
        """Get a single grade by ID."""
        grade = grade_service.get_grade(grade_id)
        
        if not grade:
            return jsonify({
                'success': False,
                'error': 'Grade not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': grade.to_dict()
        })
    
    @bp.route('', methods=['POST'])
    def create_grade():
        """Create a new grade."""
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Create Grade model from request data
        grade = Grade(
            id=None,
            student_id=data.get('student_id'),
            course=data.get('course', '').strip(),
            grade=data.get('grade', '').strip(),
            semester=data.get('semester', '').strip(),
            credits=data.get('credits', 3)
        )
        
        result = grade_service.create_grade(grade)
        
        if result.success:
            response = {
                'success': True,
                'message': result.message,
                'data': {'id': result.grade_id}
            }
            # Include egress result for demo visibility
            if result.egress_result:
                response['egress'] = result.egress_result
            return jsonify(response), 201
        else:
            return jsonify({
                'success': False,
                'error': result.message
            }), 400
    
    @bp.route('/<int:grade_id>', methods=['DELETE'])
    def delete_grade(grade_id: int):
        """Delete a grade by ID."""
        success, message = grade_service.delete_grade(grade_id)
        
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
    
    @bp.route('/semesters', methods=['GET'])
    def get_semesters():
        """Get list of all unique semesters."""
        semesters = grade_service.get_all_semesters()
        return jsonify({
            'success': True,
            'data': semesters
        })
    
    @bp.route('/courses', methods=['GET'])
    def get_courses():
        """Get list of all unique courses."""
        courses = grade_service.get_all_courses()
        return jsonify({
            'success': True,
            'data': courses
        })
    
    return bp

