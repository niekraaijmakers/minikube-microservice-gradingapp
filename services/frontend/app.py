"""
Frontend Service - Web UI for the Student Grading System.
This service provides the web interface and proxies API calls to backend services.
"""
import os
import requests
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Configuration
SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 5000))
STUDENT_SERVICE_URL = os.environ.get('STUDENT_SERVICE_URL', 'http://student-service:5001')
GRADE_SERVICE_URL = os.environ.get('GRADE_SERVICE_URL', 'http://grade-service:5002')


# ============ WEB PAGES ============

@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')


@app.route('/students')
def students_page():
    """Students management page."""
    return render_template('students.html')


@app.route('/grades')
def grades_page():
    """Grades management page."""
    return render_template('grades.html')


@app.route('/architecture')
def architecture_page():
    """Architecture visualization page."""
    return render_template('architecture.html')


# ============ API PROXY ENDPOINTS ============
# These proxy requests to the backend services

@app.route('/api/students', methods=['GET', 'POST'])
@app.route('/api/students/<path:path>', methods=['GET', 'DELETE'])
def proxy_students(path=''):
    """Proxy requests to student-service."""
    url = f"{STUDENT_SERVICE_URL}/api/students"
    if path:
        url += f"/{path}"
    
    try:
        if request.method == 'GET':
            response = requests.get(url, params=request.args, timeout=10)
        elif request.method == 'POST':
            response = requests.post(url, json=request.get_json(), timeout=10)
        elif request.method == 'DELETE':
            response = requests.delete(url, timeout=10)
        else:
            return jsonify({'error': 'Method not allowed'}), 405
        
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Could not reach student-service: {str(e)}'
        }), 503


@app.route('/api/grades', methods=['GET', 'POST'])
@app.route('/api/grades/<path:path>', methods=['GET', 'POST', 'DELETE'])
def proxy_grades(path=''):
    """Proxy requests to grade-service."""
    url = f"{GRADE_SERVICE_URL}/api/grades"
    if path:
        url += f"/{path}"
    
    try:
        if request.method == 'GET':
            response = requests.get(url, params=request.args, timeout=10)
        elif request.method == 'POST':
            response = requests.post(url, json=request.get_json(), timeout=10)
        elif request.method == 'DELETE':
            response = requests.delete(url, timeout=10)
        else:
            return jsonify({'error': 'Method not allowed'}), 405
        
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Could not reach grade-service: {str(e)}'
        }), 503


# ============ HEALTH & STATUS ============

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'frontend',
        'version': '1.0.0'
    })


@app.route('/api/status', methods=['GET'])
def service_status():
    """Check status of all backend services."""
    status = {
        'frontend': 'healthy',
        'student_service': 'unknown',
        'grade_service': 'unknown'
    }
    
    try:
        resp = requests.get(f"{STUDENT_SERVICE_URL}/health", timeout=5)
        status['student_service'] = 'healthy' if resp.status_code == 200 else 'unhealthy'
    except requests.RequestException:
        status['student_service'] = 'unreachable'
    
    try:
        resp = requests.get(f"{GRADE_SERVICE_URL}/health", timeout=5)
        status['grade_service'] = 'healthy' if resp.status_code == 200 else 'unhealthy'
    except requests.RequestException:
        status['grade_service'] = 'unreachable'
    
    return jsonify(status)


# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


# ============ STARTUP ============

if __name__ == '__main__':
    print(f"""
╔════════════════════════════════════════════════════════════╗
║                FRONTEND SERVICE - Starting                  ║
╠════════════════════════════════════════════════════════════╣
║  Port: {SERVICE_PORT}                                              ║
║  Student Service: {STUDENT_SERVICE_URL:<34} ║
║  Grade Service: {GRADE_SERVICE_URL:<36} ║
║                                                             ║
║  Pages:                                                     ║
║    /              - Home page                               ║
║    /students      - Student management                      ║
║    /grades        - Grade management                        ║
║    /architecture  - System architecture                     ║
╚════════════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)

