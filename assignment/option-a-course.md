# Option A: Course Service

## Data Model

### Course

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | integer | Unique identifier (auto-generated) | `1` |
| `code` | string | Course code (required, unique) | `"CS101"` |
| `name` | string | Full course name (required) | `"Introduction to Programming"` |
| `credits` | integer | Credit hours (1-6) | `3` |
| `instructor` | string | Instructor name | `"Dr. Smith"` |
| `semester` | string | Semester offered | `"Fall 2024"` |
| `created_at` | datetime | When the course was created | `"2024-01-15T10:30:00Z"` |

### Example JSON

```json
{
  "id": 1,
  "code": "CS101",
  "name": "Introduction to Programming",
  "credits": 3,
  "instructor": "Dr. Smith",
  "semester": "Fall 2024",
  "created_at": "2024-01-15T10:30:00Z"
}
```

## API Endpoints

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/api/courses` | List all courses | - | Array of courses |
| POST | `/api/courses` | Create a course | Course JSON (without id) | Created course with id |
| GET | `/api/courses/<id>` | Get course by ID | - | Course or 404 |
| GET | `/api/courses/code/<code>` | Get course by code | - | Course or 404 |
| DELETE | `/api/courses/<id>` | Delete a course | - | Success message or 404 |
| GET | `/health` | Health check | - | `{"status": "healthy"}` |

## Validation Rules

- `code` is required and must be unique
- `name` is required
- `credits` must be between 1 and 6 (default: 3)

