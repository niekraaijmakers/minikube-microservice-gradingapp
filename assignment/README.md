# Assignment Specifications

This folder contains the data model specifications for each assignment option.

## Files

| File | Option | Description |
|------|--------|-------------|
| [option-a-course.md](option-a-course.md) | A | Course Service - data model & endpoints |
| [option-b-analytics.md](option-b-analytics.md) | B | Analytics Service - response models & calculations |
| [option-c-notification.md](option-c-notification.md) | C | Notification Service - data model & egress demo |

## How to Use

1. Read the specification for your chosen option
2. Implement the data model in Python (use `@dataclass` or a regular class)
3. Build your Flask API with the specified endpoints
4. Look at the existing services in `services/` for patterns and conventions

## Reference Implementation

The existing services show you the patterns to follow:

```
services/student-service/     # Good reference for CRUD operations
services/grade-service/       # Good reference for calling other services
```
