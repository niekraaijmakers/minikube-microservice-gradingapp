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

## Getting Started

📁 **Check the `assignment/` folder** for data model specifications!

```
assignment/
├── README.md                    # Overview
├── option-a-course.md          # Course Service spec
├── option-b-analytics.md       # Analytics Service spec
└── option-c-notification.md    # Notification Service spec
```

## Your Assignment Options

Choose **ONE** of the following assignments:

---

### 📚 Option A: Course Service (Beginner)

Create a new microservice to manage courses.

> 📋 **Spec:** See `assignment/option-a-course.md` for the full data model specification

**Requirements:**
1. Create a `course-service` that runs on port `5003`
2. Implement the following API endpoints:
   - `GET /api/courses` - List all courses
   - `POST /api/courses` - Create a course (returns ID)
   - `GET /api/courses/<id>` - Get course by ID (use ID from POST)
   - `GET /api/courses/code/<code>` - Get course by code (e.g., CS101)
   - `DELETE /api/courses/<id>` - Delete a course
   - `GET /health` - Health check

3. Course data model:
   ```json
   {
     "id": 1,
     "code": "CS101",
     "name": "Introduction to Programming",
     "credits": 4,
     "instructor": "Dr. Smith",
     "semester": "Fall 2024"
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

> 📋 **Spec:** See `assignment/option-b-analytics.md` for response models and GPA calculation

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

Create a service that manages notifications and demonstrates **external egress** (calling external URLs from inside the cluster).

> 📋 **Spec:** See `assignment/option-c-notification.md` for the full data model and egress details

**Scenario:**
When a grade is posted, the system should notify the student. Your notification service will simulate sending an email/SMS by calling an external API (`https://httpbin.org/get`). This demonstrates how Kubernetes NetworkPolicies can control outbound internet access.

**Requirements:**

1. Create a `notification-service` on port `5005`

2. Implement these endpoints:
   | Method | Endpoint | Description |
   |--------|----------|-------------|
   | POST | `/api/notifications` | Create AND send a notification (returns ID) |
   | GET | `/api/notifications` | List all notifications |
   | GET | `/api/notifications/<id>` | Get notification by ID (use ID from POST) |
   | GET | `/health` | Health check |

3. **How it works:**
   - `POST /api/notifications` creates a notification AND immediately attempts to send it
   - The "send" action makes an HTTP GET to `https://httpbin.org/get` (simulating an external email/SMS API)
   - The response includes the notification ID and whether sending succeeded or was blocked
   - Use `GET /api/notifications/<id>` to retrieve the full notification details later

4. **Example flow:**
   ```bash
   # Create and send a notification
   curl -X POST http://grading.local/api/notifications \
     -H "Content-Type: application/json" \
     -d '{"student_id": 1, "message": "Your grade for CS101: A"}'
   
   # Response includes the ID and send status:
   # {"id": 1, "status": "sent", "egress_blocked": false}
   # OR if NetworkPolicy blocks it:
   # {"id": 1, "status": "failed", "egress_blocked": true}
   
   # Retrieve the notification details using the returned ID
   curl http://grading.local/api/notifications/1
   ```

5. **Data model** (see `assignment/models/notification.py` for starter code):
   ```json
   {
     "id": 1,
     "student_id": 1,
     "message": "Your grade for CS101 has been posted: A",
     "status": "sent",
     "egress_blocked": false,
     "created_at": "2024-01-15T10:30:00Z",
     "sent_at": "2024-01-15T10:30:01Z",
     "external_response": {"args": {...}, "url": "..."}
   }
   ```
   
   Status values: `sent` (success) or `failed` (blocked/error)

6. **Egress Challenge** - Create TWO NetworkPolicies:

   **Policy 1: Base policy (always applied)**
   - Block external internet access (default-deny already does this)
   
   **Policy 2: External egress policy (toggle on/off for demo)**
   - ALLOW notification-service → external HTTPS (port 443)
   - Use `ipBlock` with `0.0.0.0/0` and `except` for private ranges

   Test the difference:
   ```bash
   # Without external egress policy: sending fails (blocked)
   curl -X POST http://grading.local/api/notifications \
     -H "Content-Type: application/json" \
     -d '{"student_id": 1, "message": "Test notification"}'
   # Response: {"id": 1, "status": "failed", "egress_blocked": true}
   
   # Apply external egress policy
   kubectl apply -f k8s/network-policies/XX-allow-notification-egress.yaml
   
   # Now sending works!
   curl -X POST http://grading.local/api/notifications \
     -H "Content-Type: application/json" \
     -d '{"student_id": 2, "message": "Another test"}'
   # Response: {"id": 2, "status": "sent", "egress_blocked": false}
   ```

7. Create Kubernetes manifests (Deployment, Service, NetworkPolicy)
8. Update Ingress for `/api/notifications`

**Bonus:**
- Call student-service to get the student's name and include it in the notification
- Add logging to show egress attempts in pod logs
- Create a frontend page showing notification status with send buttons

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

