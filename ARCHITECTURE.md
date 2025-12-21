# Architecture Documentation

## System Components

### 1. Frontend Service (Port 5000)
**Purpose**: Web-based user interface for the grading system

**Responsibilities**:
- Render HTML pages for students and grades
- Make API calls to backend services
- Handle user interactions

**Technology**: Flask + Jinja2 templates

### 2. Student Service (Port 5001)
**Purpose**: RESTful API for student management

**Endpoints**:
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/students` | List all students |
| GET | `/api/students/<id>` | Get student by ID |
| POST | `/api/students` | Create new student |
| DELETE | `/api/students/<id>` | Delete student |
| GET | `/api/students/majors` | List unique majors |
| GET | `/health` | Health check endpoint |

**Data Model**:
```python
Student = {
    "id": int,
    "name": str,
    "email": str,
    "age": int,
    "major": str,
    "gpa": float
}
```

### 3. Grade Service (Port 5002)
**Purpose**: RESTful API for grade management

**Endpoints**:
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/grades` | List all grades |
| GET | `/api/grades/<id>` | Get grade by ID |
| POST | `/api/grades` | Create new grade |
| DELETE | `/api/grades/<id>` | Delete grade |
| GET | `/api/grades/semesters` | List unique semesters |
| GET | `/api/grades/courses` | List unique courses |
| GET | `/health` | Health check endpoint |

**Data Model**:
```python
Grade = {
    "id": int,
    "student_id": int,
    "course": str,
    "grade": str,      # A, A-, B+, B, B-, C+, C, C-, D, F
    "semester": str,
    "credits": int,
    "student_name": str  # Enriched from student service
}
```

**Inter-Service Communication**:
The grade service calls the student service to enrich grade data with student names.

---

## Kubernetes Resources

### Namespace
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: grading-system
```

### Deployments
Each service runs as a Kubernetes Deployment with:
- 2 replicas for high availability
- Resource limits (CPU/Memory)
- Health checks (liveness/readiness probes)
- Environment variables for configuration

### Services
ClusterIP services for internal communication:
- `frontend-service` → port 5000
- `student-service` → port 5001
- `grade-service` → port 5002

### Ingress
nginx-ingress routes external traffic:

```
http://grading.local/                → frontend-service:5000
http://grading.local/api/students/*  → student-service:5001
http://grading.local/api/grades/*    → grade-service:5002
```

### Network Policies

```
┌────────────────────────────────────────────────────────────────┐
│                    NETWORK POLICY OVERVIEW                      │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐         ┌─────────────┐        ┌────────────┐ │
│  │   INGRESS   │────────▶│  FRONTEND   │───────▶│  STUDENT   │ │
│  │ CONTROLLER  │         │             │───────▶│  SERVICE   │ │
│  └─────────────┘         └─────────────┘        └────────────┘ │
│        │                        │                      ▲        │
│        │                        │                      │        │
│        │                        ▼               ┌──────┘        │
│        │                 ┌─────────────┐        │               │
│        └────────────────▶│   GRADE     │────────┘               │
│                          │   SERVICE   │                        │
│                          └─────────────┘                        │
│                                 │                               │
│                                 ▼                               │
│                          ┌─────────────┐                        │
│                          │  EXTERNAL   │  ❌ BLOCKED            │
│                          │  INTERNET   │                        │
│                          └─────────────┘                        │
│                                                                 │
└────────────────────────────────────────────────────────────────┘

LEGEND:
  ───▶  Allowed traffic
  ❌    Blocked traffic
```

**Policy Details**:

1. **default-deny**: Blocks all traffic by default
2. **allow-ingress-to-frontend**: Ingress controller → Frontend
3. **allow-ingress-to-apis**: Ingress controller → Student & Grade services
4. **allow-frontend-to-backends**: Frontend → Student & Grade services
5. **allow-grade-to-student**: Grade service → Student service
6. **allow-dns**: All pods → kube-dns (required for service discovery)

---

## Data Flow Examples

### 1. Viewing Student List

```
User Browser
    │
    │ GET http://grading.local/students
    ▼
Ingress Controller
    │
    │ Route: /students → frontend
    ▼
Frontend Service
    │
    │ fetch('/api/students')
    ▼
Student Service
    │
    │ Query in-memory SQLite
    ▼
Return JSON → Frontend renders HTML → Browser displays
```

### 2. Adding a Grade

```
User Browser
    │
    │ POST /api/grades {student_id: 1, course: "Math", grade: "A"}
    ▼
Ingress Controller
    │
    │ Route: /api/grades → grade-service
    ▼
Grade Service
    │
    │ 1. Validate grade data
    │ 2. Call student-service to verify student exists
    │ 3. Insert into database
    ▼
Return success → Browser updates
```

### 3. Egress Blocked Example

```
Grade Service Pod
    │
    │ Attempt: curl http://google.com
    ▼
NetworkPolicy Check
    │
    │ Rule: grade-service can only reach student-service
    │ Result: ❌ DENIED
    ▼
Connection timeout/refused
```

---

## Extension Points (For Assignments)

The architecture is designed to be extended. Suggested additions:

1. **Course Service**: Manage course catalog
2. **Notification Service**: Email/webhook notifications
3. **Analytics Service**: GPA calculations, statistics
4. **Authentication Service**: JWT-based auth

Each new service would require:
- New Deployment + Service
- Updated Ingress rules
- New NetworkPolicies

