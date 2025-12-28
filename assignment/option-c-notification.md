# Option C: Notification Service

## Overview

The notification service simulates sending notifications (email/SMS) by making HTTP requests to an external API. This demonstrates **external egress** - outbound traffic from a Kubernetes pod to the internet.

When you POST a notification, the service:
1. Creates the notification record
2. Immediately attempts to "send" it by calling `https://httpbin.org/get`
3. Records whether the external call succeeded or was blocked by NetworkPolicy

## Data Model

### Notification

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | integer | Unique identifier (auto-generated) | `1` |
| `student_id` | integer | Which student to notify | `1` |
| `message` | string | Notification content | `"Your grade for CS101: A"` |
| `status` | string | `"sent"` or `"failed"` | `"sent"` |
| `egress_blocked` | boolean | True if NetworkPolicy blocked the call | `false` |
| `created_at` | datetime | When notification was created | `"2024-01-15T10:30:00Z"` |
| `sent_at` | datetime | When notification was sent (null if failed) | `"2024-01-15T10:30:01Z"` |
| `external_response` | object | Response from httpbin.org (null if failed) | `{"args": {...}, "url": "..."}` |
| `error_message` | string | Error details if failed (null if success) | `"Connection timed out"` |

### Status Values

| Status | Meaning |
|--------|---------|
| `sent` | External HTTP call succeeded |
| `failed` | External HTTP call failed (timeout, connection error, etc.) |

## API Endpoints

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/api/notifications` | Create and send a notification | `{"student_id": 1, "message": "..."}` | Short response with id/status |
| GET | `/api/notifications` | List all notifications | - | Array of notifications |
| GET | `/api/notifications/<id>` | Get notification by ID | - | Full notification or 404 |
| GET | `/health` | Health check | - | `{"status": "healthy"}` |

## Example Flow

### Request
```bash
curl -X POST http://grading.local/api/notifications \
  -H "Content-Type: application/json" \
  -d '{"student_id": 1, "message": "Your grade for CS101 has been posted: A"}'
```

### Response (if egress is allowed)
```json
{
  "id": 1,
  "status": "sent",
  "egress_blocked": false
}
```

### Response (if egress is blocked by NetworkPolicy)
```json
{
  "id": 1,
  "status": "failed",
  "egress_blocked": true
}
```

### Get full details
```bash
curl http://grading.local/api/notifications/1
```

## "Sending" a Notification

When you "send" a notification, your code should:

1. Make an HTTP GET request to `https://httpbin.org/get`
2. Include notification details as query parameters
3. Use a timeout (5 seconds recommended)
4. Handle success: set `status = "sent"`, store the response
5. Handle timeout/connection error: set `status = "failed"`, `egress_blocked = true`

The httpbin.org service echoes back your request, so you can see what was sent.

## NetworkPolicy Challenge

Create TWO NetworkPolicies:

1. **Default behavior** (already exists): Blocks all external egress
2. **Your policy**: Allows notification-service to reach external HTTPS (port 443)

Test by applying/removing your egress policy and observing the difference in notification status.

