# 🎓 Intern Assignment: Extend the Student Grading System

## Overview

You will be extending the existing Student Grading System microservices architecture. This assignment will help you understand:
- Building REST APIs with Flask
- Creating Docker containers
- Deploying to Kubernetes
- Configuring Ingress for external access
- Setting up NetworkPolicies for security

## Current Architecture

The system currently has three microservices:

| Service | Port | Description |
|---------|------|-------------|
| **Frontend** | 5000 | Web UI for the system |
| **Student Service** | 5001 | CRUD API for student records |
| **Grade Service** | 5002 | CRUD API for grades |

## Your Assignment Options

Choose **ONE** of the following assignments:

---

### 📚 Option A: Course Service (Beginner)

Create a new microservice to manage courses.

**Requirements:**
1. Create a `course-service` that runs on port `5003`
2. Implement the following API endpoints:
   - `GET /api/courses` - List all courses
   - `GET /api/courses/<id>` - Get course by ID
   - `POST /api/courses` - Create a course
   - `DELETE /api/courses/<id>` - Delete a course
   - `GET /health` - Health check

3. Course data model:
   ```json
   {
     "id": 1,
     "code": "CS101",
     "name": "Introduction to Programming",
     "credits": 4,
     "department": "Computer Science",
     "instructor": "Dr. Smith"
   }
   ```

4. Create Kubernetes deployment and service manifests
5. Update the Ingress to route `/api/courses` to your service
6. Add a NetworkPolicy allowing grade-service to reach course-service

**Bonus:**
- Add a frontend page to manage courses
- Modify grade-service to validate course codes 

---

### 📊 Option B: Analytics Service (Intermediate)

Create a service that calculates statistics and analytics.

**Requirements:**
1. Create an `analytics-service` that runs on port `5004`
2. Implement the following API endpoints:
   - `GET /api/analytics/student/<id>/gpa` - Calculate GPA for a student
   - `GET /api/analytics/course/<name>/average` - Average grade for a course
   - `GET /api/analytics/semester/<semester>/summary` - Semester statistics
   - `GET /api/analytics/top-students?limit=10` - Top performing students
   - `GET /health` - Health check

3. The analytics service must call other services:
   - Call student-service to get student data
   - Call grade-service to get grade data

4. GPA Calculation (use standard 4.0 scale):
   ```
   A = 4.0, A- = 3.7, B+ = 3.3, B = 3.0, B- = 2.7
   C+ = 2.3, C = 2.0, C- = 1.7, D = 1.0, F = 0.0
   
   GPA = Σ(grade_points × credits) / Σ(credits)
   ```

5. Create Kubernetes manifests (Deployment, Service, NetworkPolicy)
6. Update Ingress for `/api/analytics`
7. NetworkPolicy must allow analytics-service → student-service AND grade-service

**Bonus:**
- Add caching to reduce API calls
- Create visualization on the frontend

---

### 🔔 Option C: Notification Service (Advanced)

Create a service that sends notifications and demonstrates external egress.

**Requirements:**
1. Create a `notification-service` on port `5005`
2. Implement:
   - `POST /api/notifications/send` - Queue a notification
   - `GET /api/notifications` - List pending notifications
   - `GET /api/notifications/<id>` - Get notification status
   - `GET /api/notifications/test-egress` - Test external internet access
   - `GET /health` - Health check

3. Notification data model:
   ```json
   {
     "id": 1,
     "type": "grade_posted",
     "recipient_id": 1,
     "message": "Your grade for CS101 has been posted",
     "status": "pending|sent|failed",
     "created_at": "2024-01-15T10:30:00Z"
   }
   ```

4. **Egress Challenge**: Add an endpoint that attempts to reach an external URL (e.g., `https://httpbin.org/get` or `https://ifconfig.me`). This demonstrates external egress.

5. Create NetworkPolicies that:
   - ALLOW notification-service → student-service (to get student info)
   - BLOCK notification-service → external internet (default)
   
   Then create a second policy that ALLOWS external egress and observe the difference:
   ```bash
   # Test from inside the pod
   kubectl exec -it deployment/notification-service -n grading-system -- \
     curl -s --max-time 5 https://httpbin.org/get
   
   # With egress blocked: connection times out
   # With egress allowed: returns JSON response
   ```

6. Create Kubernetes manifests (Deployment, Service, NetworkPolicy)
7. Update Ingress for `/api/notifications`

**Bonus:**
- Call student-service to get the student's name when sending notifications
- Add a simple in-memory queue for pending notifications

---

## Step-by-Step Guide

### Step 1: Create Your Service

```bash
# Create service directory
mkdir -p services/YOUR-SERVICE-NAME

# Create the required files
touch services/YOUR-SERVICE-NAME/app.py
touch services/YOUR-SERVICE-NAME/requirements.txt
touch services/YOUR-SERVICE-NAME/Dockerfile
```

### Step 2: Implement the API

Use the existing services as reference:
- `services/student-service/app.py` - Example of a Flask REST API
- `services/grade-service/app.py` - Example of calling another service

### Step 3: Create Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
ENV SERVICE_PORT=YOUR_PORT
EXPOSE YOUR_PORT
CMD ["gunicorn", "--bind", "0.0.0.0:YOUR_PORT", "--workers", "2", "app:app"]
```

### Step 4: Create Kubernetes Manifests

Create in `k8s/deployments/your-service.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: your-service
  namespace: grading-system
# ... (use existing deployments as reference)
```

Create in `k8s/services/your-service.yaml`:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: your-service
  namespace: grading-system
# ... (use existing services as reference)
```

### Step 5: Update Ingress

Add your path to `k8s/ingress/ingress.yaml`:
```yaml
- path: /api/your-endpoint(/|$)(.*)
  pathType: ImplementationSpecific
  backend:
    service:
      name: your-service
      port:
        number: YOUR_PORT
```

### Step 6: Create NetworkPolicy

Create `k8s/network-policies/XX-your-service.yaml`:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: your-service-policy
  namespace: grading-system
spec:
  podSelector:
    matchLabels:
      app: your-service
  policyTypes:
  - Ingress
  - Egress
  # Define your rules...
```

### Step 7: Build and Deploy

```bash
# Configure Docker to use minikube
eval $(minikube docker-env)

# Build your image
docker build -t your-service:latest services/YOUR-SERVICE-NAME/

# Apply your manifests
kubectl apply -f k8s/deployments/your-service.yaml
kubectl apply -f k8s/services/your-service.yaml
kubectl apply -f k8s/ingress/ingress.yaml
kubectl apply -f k8s/network-policies/XX-your-service.yaml
```

### Step 8: Test Your Service

```bash
# Check pod status
kubectl get pods -n grading-system

# View logs
kubectl logs -f deployment/your-service -n grading-system

# Test the API
curl http://grading.local/api/your-endpoint

# Test NetworkPolicy
kubectl exec -it deployment/your-service -n grading-system -- curl -s --max-time 5 https://httpbin.org/get
```

---

## Evaluation Criteria

| Criterion | Points |
|-----------|--------|
| API endpoints work correctly | 25 |
| Dockerfile builds successfully | 15 |
| Kubernetes Deployment works | 20 |
| Ingress routing configured | 15 |
| NetworkPolicy implemented | 15 |
| Code quality and documentation | 10 |
| **Total** | **100** |

## Submission

1. Create a new branch: `feature/YOUR-NAME-assignment`
2. Commit all your files
3. Create a pull request with:
   - Description of what you built
   - How to test it
   - Screenshot of working functionality

## Tips

- Use `kubectl describe pod <pod-name> -n grading-system` to debug issues
- Check logs with `kubectl logs <pod-name> -n grading-system`
- Test locally first before deploying to Kubernetes
- Look at existing code for patterns and conventions

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [NetworkPolicy Guide](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Ingress Guide](https://kubernetes.io/docs/concepts/services-networking/ingress/)

Good luck! 🚀

