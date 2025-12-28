# Option B: Analytics Service

## Overview

The analytics service doesn't store its own data. It fetches data from `student-service` and `grade-service`, then computes statistics.

## Response Models

### Student GPA

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `student_id` | integer | The student's ID | `1` |
| `student_name` | string | The student's name | `"Alice Johnson"` |
| `gpa` | float | Calculated GPA (0.0 - 4.0) | `3.75` |
| `total_credits` | integer | Sum of all course credits | `12` |
| `grades_count` | integer | Number of grades included | `4` |

### Course Average

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `course` | string | Course name/code | `"CS101"` |
| `average_gpa` | float | Average GPA for the course | `3.2` |
| `students_count` | integer | Number of students | `25` |
| `grade_distribution` | object | Count per letter grade | `{"A": 5, "B": 10, ...}` |

### Semester Summary

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `semester` | string | Semester name | `"Fall 2024"` |
| `total_students` | integer | Unique students with grades | `50` |
| `total_grades` | integer | Total grades recorded | `200` |
| `average_gpa` | float | Overall average GPA | `3.1` |
| `courses` | array | List of courses | `["CS101", "MATH201"]` |

### Top Student

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `rank` | integer | Position in ranking | `1` |
| `student_id` | integer | Student ID | `1` |
| `student_name` | string | Student name | `"Alice Johnson"` |
| `gpa` | float | Calculated GPA | `4.0` |

## GPA Calculation

Use the standard 4.0 scale:

| Grade | Points |
|-------|--------|
| A | 4.0 |
| A- | 3.7 |
| B+ | 3.3 |
| B | 3.0 |
| B- | 2.7 |
| C+ | 2.3 |
| C | 2.0 |
| C- | 1.7 |
| D+ | 1.3 |
| D | 1.0 |
| D- | 0.7 |
| F | 0.0 |

**Formula:**
```
GPA = Σ(grade_points × credits) / Σ(credits)
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/student/<id>/gpa` | Calculate GPA for a student |
| GET | `/api/analytics/course/<name>/average` | Average grade for a course |
| GET | `/api/analytics/semester/<semester>/summary` | Semester statistics |
| GET | `/api/analytics/top-students?limit=10` | Top performing students |
| GET | `/health` | Health check |

## Service Dependencies

Your analytics service needs to call:
- `http://student-service:5001/api/students` - Get student data
- `http://grade-service:5002/api/grades` - Get grade data

