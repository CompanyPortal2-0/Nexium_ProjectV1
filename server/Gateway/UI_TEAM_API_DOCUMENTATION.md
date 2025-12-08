# Gateway API Documentation for UI Team

> **Version:** 1.0.0  
> **Base URL:** `https://localhost:7050`  
> **Last Updated:** December 7, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Common Response Formats](#common-response-formats)
4. [Error Handling](#error-handling)
5. [API Endpoints](#api-endpoints)
   - [Health & Status](#health--status-endpoints)
   - [Authentication Endpoints](#authentication-endpoints-1)
   - [User & Team Management](#user--team-management)
   - [Activities](#activities-management)
   - [Meetings](#meetings-management)
   - [File Management](#file-management)
6. [Data Models](#data-models)
7. [Quick Reference Table](#quick-reference-table)

---

## Overview

The Gateway API serves as the single entry point for all client applications. It handles authentication, authorization, and routes requests to the appropriate microservices.

### Architecture
```
┌─────────────────┐         ┌─────────────────────────────────────────────┐
│                 │         │              GATEWAY (Port 7050)            │
│   UI/Frontend   │ ◄─────► │                                             │
│   Application   │  HTTPS  │   ┌─────────┐  ┌────────────┐  ┌──────────┐ │
│                 │         │   │  Auth   │  │   User     │  │ Activity │ │
└─────────────────┘         │   │ Service │  │  Service   │  │ Service  │ │
                            │   └─────────┘  └────────────┘  └──────────┘ │
                            │                                             │
                            │   ┌─────────┐  ┌────────────┐               │
                            │   │ Meeting │  │   File     │               │
                            │   │ Service │  │  Service   │               │
                            │   └─────────┘  └────────────┘               │
                            └─────────────────────────────────────────────┘
```

---

## Authentication

### JWT Token Authentication

All protected endpoints require a valid JWT token in the request header.

#### Header Format
```http
Authorization: Bearer <your_jwt_token>
```

#### Token Lifecycle
- Tokens are issued upon successful login or signup
- Include the token in all subsequent API requests
- Store tokens securely (localStorage/sessionStorage with proper security measures)

#### Example Request with Authentication
```javascript
fetch('https://localhost:7050/teammates', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
    'Content-Type': 'application/json'
  }
})
```

---

## Common Response Formats

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error description message"
}
```

---

## Error Handling

| Status Code | Meaning | Common Causes |
|-------------|---------|---------------|
| `200` | Success | Request completed successfully |
| `400` | Bad Request | Missing required fields, invalid data format |
| `401` | Unauthorized | Missing/invalid JWT token, expired session |
| `403` | Forbidden | User lacks permission for this action |
| `404` | Not Found | Resource doesn't exist |
| `500` | Internal Server Error | Server-side error |
| `503` | Service Unavailable | Backend service communication error |
| `504` | Gateway Timeout | Backend service timeout |

---

## API Endpoints

---

### Health & Status Endpoints

These endpoints don't require authentication and are used for monitoring.

#### GET `/health`
Check gateway health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "gateway",
  "version": "1.0.0",
  "timestamp": "2025-12-07T12:00:00.000000"
}
```

#### GET `/ready`
Simple readiness check.

**Response:**
```json
{
  "status": "ready"
}
```

#### GET `/live`
Simple liveness check.

**Response:**
```json
{
  "status": "alive"
}
```

---

### Authentication Endpoints

#### POST `/login`
Authenticate a user and receive a JWT token.

**Authentication Required:** ❌ No

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "userPassword123"
}
```

**Success Response (200):**
```json
{
  "Token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "id": "user_uuid_here"
}
```

**Error Response (401):**
```json
{
  "Text": "missing content"
}
```

---

#### POST `/signup`
Register a new user account.

**Authentication Required:** ❌ No

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "Password": "securePassword123",
  "FirstName": "John",
  "LastName": "Doe",
  "DateOfBirth": "1990-05-15",
  "Address": "123 Main Street, City",
  "managercode": "OPTIONAL_MANAGER_CODE"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | ✅ | User's email address |
| `Password` | string | ✅ | User's password |
| `FirstName` | string | ✅ | User's first name |
| `LastName` | string | ✅ | User's last name |
| `DateOfBirth` | string | ✅ | Date of birth (YYYY-MM-DD) |
| `Address` | string | ✅ | User's address |
| `managercode` | string | ❌ | Manager invitation code (if signing up under a manager) |

**Success Response (200):**
```json
{
  "AuthToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "id": "new_user_uuid",
  "firstname": "John",
  "lastname": "Doe",
  "role": "employee"
}
```

**Error Response (400):**
```json
{
  "Text": "Missing required fields"
}
```

---

#### GET `/user/identity`
Get the current authenticated user's identity.

**Authentication Required:** ✅ Yes

**Success Response (200):**
```json
{
  "user_id": "user_uuid_here",
  "email": "user@example.com"
}
```

---

### User & Team Management

#### GET `/teammates`
Get teammates of the currently logged-in user.

**Authentication Required:** ✅ Yes

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_details` | boolean | `true` | If true, returns full user objects |
| `include_manager` | boolean | `true` | If true, includes manager information |

**Example Request:**
```
GET /teammates?include_details=true&include_manager=true
```

**Success Response (200):**
```json
{
  "success": true,
  "teammates": [
    {
      "email": "teammate1@example.com",
      "firstName": "Jane",
      "lastName": "Smith"
    },
    {
      "email": "teammate2@example.com",
      "firstName": "Bob",
      "lastName": "Johnson"
    }
  ],
  "manager": {
    "email": "manager@example.com",
    "firstName": "Alice",
    "lastName": "Williams"
  }
}
```

---

#### GET `/team`
Get full team information for the currently logged-in user.

**Authentication Required:** ✅ Yes

**Success Response (200):**
```json
{
  "success": true,
  "employee": {
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe"
  },
  "manager": {
    "email": "manager@example.com",
    "firstName": "Alice",
    "lastName": "Williams"
  },
  "teammates": [
    {
      "email": "teammate1@example.com",
      "firstName": "Jane",
      "lastName": "Smith"
    }
  ]
}
```

---

#### GET `/getCodeForManager`
Get an invitation code for managers to invite employees.

**Authentication Required:** ✅ Yes (Manager role required)

**Success Response (200):**
```json
{
  "code": "ABC123XYZ",
  "expires_at": "2025-12-14T12:00:00Z"
}
```

---

#### POST `/becamemanager`
Convert a regular employee to a manager role using a code.

**Authentication Required:** ✅ Yes

**Request Body:**
```json
{
  "code": "MANAGER_UPGRADE_CODE"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Successfully upgraded to manager role"
}
```

---

#### GET `/generateBecameManagerCode`
Generate a code to become a manager.

**Authentication Required:** ❌ No

**Success Response (200):**
```json
{
  "code": "MANAGER_CODE_123"
}
```

---

### Activities Management

#### POST `/activities`
Create a new activity.

**Authentication Required:** ✅ Yes

**Request Body:**
```json
{
  "title": "Team Building Event",
  "description": "Annual team building activity",
  "activity_type": "team_building",
  "scheduled_date": "2025-12-20T14:00:00Z",
  "location": "Conference Room A",
  "max_participants": 20
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | ✅ | Activity title |
| `description` | string | ❌ | Activity description |
| `activity_type` | string | ❌ | Type of activity |
| `scheduled_date` | string | ❌ | ISO 8601 date-time |
| `location` | string | ❌ | Activity location |
| `max_participants` | integer | ❌ | Maximum number of participants |

**Success Response (200):**
```json
{
  "success": true,
  "activity": {
    "id": 1,
    "title": "Team Building Event",
    "creator": "user@example.com",
    "created_at": "2025-12-07T12:00:00Z"
  }
}
```

---

#### GET `/activities`
List all activities with optional filters.

**Authentication Required:** ✅ Yes

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status (active, completed, cancelled) |
| `activity_type` | string | Filter by activity type |
| `creator` | string | Filter by creator email |
| `limit` | integer | Limit number of results |
| `offset` | integer | Pagination offset |

**Example Request:**
```
GET /activities?status=active&limit=10&offset=0
```

**Success Response (200):**
```json
{
  "success": true,
  "activities": [
    {
      "id": 1,
      "title": "Team Building Event",
      "description": "Annual team building activity",
      "creator": "manager@example.com",
      "scheduled_date": "2025-12-20T14:00:00Z",
      "participant_count": 5
    }
  ],
  "total": 15
}
```

---

#### GET `/activities/{activity_id}`
Get a specific activity by ID.

**Authentication Required:** ✅ Yes

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `activity_id` | integer | The activity ID |

**Success Response (200):**
```json
{
  "success": true,
  "activity": {
    "id": 1,
    "title": "Team Building Event",
    "description": "Annual team building activity",
    "creator": "manager@example.com",
    "scheduled_date": "2025-12-20T14:00:00Z",
    "participants": ["user1@example.com", "user2@example.com"]
  }
}
```

---

#### PUT `/activities/{activity_id}`
Update an existing activity.

**Authentication Required:** ✅ Yes

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `activity_id` | integer | The activity ID |

**Request Body:** (partial update - include only fields to update)
```json
{
  "title": "Updated Team Building Event",
  "description": "Updated description",
  "scheduled_date": "2025-12-21T14:00:00Z"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "activity": {
    "id": 1,
    "title": "Updated Team Building Event",
    "updated_at": "2025-12-07T12:30:00Z"
  }
}
```

---

#### DELETE `/activities/{activity_id}`
Delete an activity.

**Authentication Required:** ✅ Yes

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `activity_id` | integer | The activity ID |

**Success Response (200):**
```json
{
  "success": true,
  "message": "Activity deleted successfully"
}
```

---

#### POST `/activities/{activity_id}/join`
Join an activity as a participant.

**Authentication Required:** ✅ Yes

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `activity_id` | integer | The activity ID |

**Success Response (200):**
```json
{
  "success": true,
  "message": "Successfully joined activity"
}
```

---

#### POST `/activities/{activity_id}/leave`
Leave an activity.

**Authentication Required:** ✅ Yes

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `activity_id` | integer | The activity ID |

**Success Response (200):**
```json
{
  "success": true,
  "message": "Successfully left activity"
}
```

---

#### POST `/activities/{activity_id}/participants`
Add participants to an activity by email(s).

**Authentication Required:** ✅ Yes

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `activity_id` | integer | The activity ID |

**Request Body:**
```json
{
  "emails": ["user1@example.com", "user2@example.com"]
}
```

**OR single participant:**
```json
{
  "participant_email": "user1@example.com"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Participants added successfully",
  "added_count": 2
}
```

---

#### GET `/activities/{activity_id}/participants`
Get all participants of an activity.

**Authentication Required:** ✅ Yes

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `activity_id` | integer | The activity ID |

**Success Response (200):**
```json
{
  "success": true,
  "participants": [
    {
      "email": "user1@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "joined_at": "2025-12-07T10:00:00Z"
    }
  ]
}
```

---

#### DELETE `/activities/{activity_id}/participants/{participant_email}`
Remove a participant from an activity.

**Authentication Required:** ✅ Yes

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `activity_id` | integer | The activity ID |
| `participant_email` | string | Participant's email (URL encoded) |

**Success Response (200):**
```json
{
  "success": true,
  "message": "Participant removed successfully"
}
```

---

#### GET `/my-activities`
Get all activities for the current user.

**Authentication Required:** ✅ Yes

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `filter` | string | `all` | Filter type: `all`, `created`, `joined`, `upcoming` |

**Example Request:**
```
GET /my-activities?filter=upcoming
```

**Success Response (200):**
```json
{
  "success": true,
  "activities": [
    {
      "id": 1,
      "title": "Team Building Event",
      "role": "creator",
      "scheduled_date": "2025-12-20T14:00:00Z"
    },
    {
      "id": 2,
      "title": "Workshop",
      "role": "participant",
      "scheduled_date": "2025-12-22T09:00:00Z"
    }
  ]
}
```

---

### Meetings Management

#### POST `/create-meet`
Create a new meeting.

**Authentication Required:** ✅ Yes

**Request Body:**
```json
{
  "title": "Weekly Standup",
  "description": "Weekly team sync meeting",
  "scheduled_time": "2025-12-08T09:00:00Z",
  "invited_emails": ["user1@example.com", "user2@example.com"]
}
```

**Success Response (200):**
```json
{
  "success": true,
  "meeting_id": "abc123",
  "invitation_link": "https://localhost:7050/room/abc123"
}
```

---

#### POST `/join-meet`
Join an existing meeting.

**Authentication Required:** ❌ No

**Request Body:**
```json
{
  "meeting_id": "abc123",
  "user_email": "user@example.com"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "redirectUrl": "https://localhost:7050/room/abc123/user@example.com"
}
```

---

#### GET `/room/{meeting_id}/{user_email}`
Access the meeting room page.

**Authentication Required:** ❌ No

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `meeting_id` | string | The meeting ID |
| `user_email` | string | Participant's email |

**Response:** HTML page for the meeting room.

---

#### GET `/meetings`
Get all meetings with optional filters.

**Authentication Required:** ✅ Yes

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `user_email` | string | Filter by user email |
| `is_active` | boolean | Filter by active status |

**Success Response (200):**
```json
{
  "success": true,
  "meetings": [
    {
      "id": "abc123",
      "title": "Weekly Standup",
      "creator": "manager@example.com",
      "is_active": true,
      "created_at": "2025-12-07T08:00:00Z"
    }
  ]
}
```

---

#### GET `/meetings/{meeting_id}`
Get a specific meeting by ID.

**Authentication Required:** ✅ Yes

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `meeting_id` | string | The meeting ID |

**Success Response (200):**
```json
{
  "success": true,
  "meeting": {
    "id": "abc123",
    "title": "Weekly Standup",
    "description": "Weekly team sync meeting",
    "creator": "manager@example.com",
    "invited_employees": ["user1@example.com", "user2@example.com"],
    "is_active": true,
    "created_at": "2025-12-07T08:00:00Z"
  }
}
```

---

#### PUT `/meetings/{meeting_id}`
Update a meeting.

**Authentication Required:** ✅ Yes

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `meeting_id` | string | The meeting ID |

**Request Body:**
```json
{
  "title": "Updated Weekly Standup",
  "description": "Updated description"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "meeting": {
    "id": "abc123",
    "title": "Updated Weekly Standup"
  }
}
```

---

#### DELETE `/meetings/{meeting_id}`
Delete a meeting.

**Authentication Required:** ✅ Yes

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `meeting_id` | string | The meeting ID |

**Success Response (200):**
```json
{
  "success": true,
  "message": "Meeting deleted successfully"
}
```

---

#### POST `/meetings/{meeting_id}/start`
Start a meeting.

**Authentication Required:** ✅ Yes

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `meeting_id` | string | The meeting ID |

**Success Response (200):**
```json
{
  "success": true,
  "message": "Meeting started",
  "started_at": "2025-12-07T09:00:00Z"
}
```

---

#### POST `/meetings/{meeting_id}/end`
End a meeting.

**Authentication Required:** ✅ Yes

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `meeting_id` | string | The meeting ID |

**Success Response (200):**
```json
{
  "success": true,
  "message": "Meeting ended",
  "ended_at": "2025-12-07T10:00:00Z"
}
```

---

#### POST `/meetings/{meeting_id}/log`
Add a log entry to a meeting.

**Authentication Required:** ✅ Yes

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `meeting_id` | string | The meeting ID |

**Request Body:**
```json
{
  "action": "user_joined",
  "user_email": "user@example.com",
  "details": "User joined the meeting"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Log entry added"
}
```

---

#### GET `/meetings/{meeting_id}/log`
Get meeting logs.

**Authentication Required:** ✅ Yes

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `meeting_id` | string | The meeting ID |

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `download` | boolean | If true, downloads as file |

**Success Response (200):**
```json
{
  "success": true,
  "logs": [
    {
      "timestamp": "2025-12-07T09:00:00Z",
      "action": "meeting_started",
      "user_email": "manager@example.com"
    },
    {
      "timestamp": "2025-12-07T09:01:00Z",
      "action": "user_joined",
      "user_email": "user1@example.com"
    }
  ]
}
```

---

### User Meeting Endpoints

These endpoints allow users to manage their own meetings.

#### GET `/meetings/my`
Get all meetings for the currently logged-in user.

**Authentication Required:** ✅ Yes

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `filter` | string | `all` | Filter type: `all`, `created`, or `invited` |
| `is_active` | boolean | - | Filter by active status |
| `include_details` | boolean | `false` | Include creator details |

**Success Response (200):**
```json
{
  "success": true,
  "email": "user@example.com",
  "filter": "all",
  "meetings": [
    {
      "id": "meet_abc123",
      "title": "Weekly Standup",
      "description": "Weekly team sync",
      "creator": "manager@example.com",
      "invited_employees": ["user@example.com"],
      "is_active": true,
      "scheduled_time": "2025-12-08T09:00:00Z",
      "created_at": "2025-12-07T08:00:00Z",
      "relationship": "invited"
    }
  ],
  "total_count": 1
}
```

**Error Response (404):**
```json
{
  "success": false,
  "error": "No meetings found for user@example.com"
}
```

---

#### GET `/meetings/my/upcoming`
Get all upcoming meetings for the currently logged-in user.

**Authentication Required:** ✅ Yes

**Success Response (200):**
```json
{
  "success": true,
  "email": "user@example.com",
  "upcoming_meetings": [
    {
      "id": "meet_abc123",
      "title": "Weekly Standup",
      "description": "Weekly team sync",
      "creator": "manager@example.com",
      "scheduled_time": "2025-12-08T09:00:00Z",
      "relationship": "invited",
      "time_until": "23 hours"
    }
  ],
  "total_count": 1
}
```

---

#### GET `/meetings/user/{email}`
Get all meetings for a specific user by email (admin/manager use).

**Authentication Required:** ✅ Yes

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `email` | string | User's email address |

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `filter` | string | `all` | Filter type: `all`, `created`, or `invited` |
| `is_active` | boolean | - | Filter by active status |
| `include_details` | boolean | `false` | Include creator details |

**Success Response (200):**
```json
{
  "success": true,
  "email": "targetuser@example.com",
  "filter": "all",
  "meetings": [...],
  "total_count": 5
}
```

---

#### GET `/meetings/user/{email}/upcoming`
Get all upcoming meetings for a specific user by email.

**Authentication Required:** ✅ Yes

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `email` | string | User's email address |

**Success Response (200):**
```json
{
  "success": true,
  "email": "targetuser@example.com",
  "upcoming_meetings": [...],
  "total_count": 3
}
```

---

#### DELETE `/meetings/{meeting_id}/delete`
Soft delete a meeting (only the creator can delete).

**Authentication Required:** ✅ Yes

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `meeting_id` | string | The meeting ID |

**Success Response (200):**
```json
{
  "success": true,
  "message": "Meeting successfully deleted",
  "meeting_id": "meet_abc123"
}
```

**Error Response (403):**
```json
{
  "success": false,
  "error": "Permission denied: only the creator can delete this meeting"
}
```

**Error Response (404):**
```json
{
  "success": false,
  "error": "Meeting not found"
}
```

---

#### DELETE `/meetings/{meeting_id}/hard-delete`
Permanently delete a meeting and all associated data (only the creator can do this).

**Authentication Required:** ✅ Yes

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `meeting_id` | string | The meeting ID |

**Request Body:**
```json
{
  "confirm": true
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Meeting permanently deleted",
  "meeting_id": "meet_abc123"
}
```

**Error Response (400):**
```json
{
  "success": false,
  "error": "Confirmation required. Set 'confirm': true in request body to permanently delete this meeting."
}
```

**Error Response (403):**
```json
{
  "success": false,
  "error": "Permission denied: only the creator can permanently delete this meeting"
}
```

---

### File Management

> **Note:** File endpoints are handled by the Files Gateway service.

#### POST `/upload`
Upload a file.

**Authentication Required:** ✅ Yes (currently disabled for testing)

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | ✅ | The file to upload |

**Example (JavaScript):**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('https://localhost:7050/upload', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer <token>'
  },
  body: formData
});
```

**Success Response (200):**
```json
{
  "success": true,
  "filename": "document.pdf",
  "file_id": "file_uuid_123",
  "url": "/file/get/document.pdf"
}
```

**Error Response (400):**
```json
{
  "error": "No file provided"
}
```

---

#### GET `/getAllfiles`
Get all files.

**Authentication Required:** ✅ Yes (currently disabled for testing)

**Success Response (200):**
```json
{
  "success": true,
  "files": [
    {
      "filename": "document.pdf",
      "size": 102400,
      "uploaded_at": "2025-12-07T12:00:00Z",
      "uploaded_by": "user@example.com"
    }
  ]
}
```

---

#### GET `/file/get/{filename}`
Download a specific file.

**Authentication Required:** ✅ Yes (currently disabled for testing)

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `filename` | string | Name of the file to download |

**Response:** Binary file content with appropriate Content-Type header.

---

## Data Models

### User Roles
```typescript
enum Role {
  GUEST = "GUEST",
  EMPLOYER = "EMPLOYER",
  MANAGER = "MANAGER",
  HR = "HR",
  ADMIN = "ADMIN"
}
```

### Departments
```typescript
enum Department {
  HR = "HR",
  IT = "IT",
  SALES = "SALES",
  MARKETING = "MARKETING"
}
```

### User Object
```typescript
interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  dateOfBirth: string;
  address: string;
  role: Role;
  department?: Department;
  manager_email?: string;
}
```

### Activity Object
```typescript
interface Activity {
  id: number;
  title: string;
  description?: string;
  activity_type?: string;
  creator: string;
  scheduled_date?: string;
  location?: string;
  max_participants?: number;
  participants: string[];
  created_at: string;
  updated_at?: string;
}
```

### Meeting Object
```typescript
interface Meeting {
  id: string;
  title: string;
  object?: string;
  description?: string;
  invitation_link: string;
  log_path?: string;
  invited_employees: string[];
  creator: string;
  is_active: boolean;
  started_at?: string;
  ended_at?: string;
  created_at: string;
}
```

---

## Quick Reference Table

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/health` | GET | ❌ | Health check |
| `/ready` | GET | ❌ | Readiness check |
| `/live` | GET | ❌ | Liveness check |
| `/login` | POST | ❌ | User login |
| `/signup` | POST | ❌ | User registration |
| `/user/identity` | GET | ✅ | Get current user identity |
| `/teammates` | GET | ✅ | Get user's teammates |
| `/team` | GET | ✅ | Get full team info |
| `/getCodeForManager` | GET | ✅ | Get manager invitation code |
| `/becamemanager` | POST | ✅ | Upgrade to manager role |
| `/generateBecameManagerCode` | GET | ❌ | Generate manager upgrade code |
| `/activities` | GET | ✅ | List activities |
| `/activities` | POST | ✅ | Create activity |
| `/activities/{id}` | GET | ✅ | Get activity |
| `/activities/{id}` | PUT | ✅ | Update activity |
| `/activities/{id}` | DELETE | ✅ | Delete activity |
| `/activities/{id}/join` | POST | ✅ | Join activity |
| `/activities/{id}/leave` | POST | ✅ | Leave activity |
| `/activities/{id}/participants` | GET | ✅ | Get participants |
| `/activities/{id}/participants` | POST | ✅ | Add participants |
| `/activities/{id}/participants/{email}` | DELETE | ✅ | Remove participant |
| `/my-activities` | GET | ✅ | Get user's activities |
| `/create-meet` | POST | ✅ | Create meeting |
| `/join-meet` | POST | ❌ | Join meeting |
| `/room/{id}/{email}` | GET | ❌ | Meeting room page |
| `/meetings` | GET | ✅ | List meetings |
| `/meetings/{id}` | GET | ✅ | Get meeting |
| `/meetings/{id}` | PUT | ✅ | Update meeting |
| `/meetings/{id}` | DELETE | ✅ | Delete meeting |
| `/meetings/{id}/start` | POST | ✅ | Start meeting |
| `/meetings/{id}/end` | POST | ✅ | End meeting |
| `/meetings/{id}/log` | GET | ✅ | Get meeting logs |
| `/meetings/{id}/log` | POST | ✅ | Add meeting log |
| `/upload` | POST | ✅* | Upload file |
| `/getAllfiles` | GET | ✅* | List files |
| `/file/get/{filename}` | GET | ✅* | Download file |

> *File endpoints: JWT currently disabled for testing

---

## Usage Examples

### JavaScript/TypeScript

#### Login and Store Token
```javascript
async function login(email, password) {
  const response = await fetch('https://localhost:7050/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email, password })
  });
  
  const data = await response.json();
  if (data.Token) {
    localStorage.setItem('authToken', data.Token);
    return data;
  }
  throw new Error('Login failed');
}
```

#### Authenticated API Call
```javascript
async function getTeammates() {
  const token = localStorage.getItem('authToken');
  
  const response = await fetch('https://localhost:7050/teammates', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  if (!response.ok) {
    if (response.status === 401) {
      // Token expired, redirect to login
      window.location.href = '/login';
    }
    throw new Error('Request failed');
  }
  
  return response.json();
}
```

#### Create Activity
```javascript
async function createActivity(activityData) {
  const token = localStorage.getItem('authToken');
  
  const response = await fetch('https://localhost:7050/activities', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(activityData)
  });
  
  return response.json();
}
```

#### File Upload
```javascript
async function uploadFile(file) {
  const token = localStorage.getItem('authToken');
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('https://localhost:7050/upload', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });
  
  return response.json();
}
```

---

## Notes for UI Team

1. **HTTPS Required:** The gateway runs on HTTPS with self-signed certificates. In development, you may need to accept the certificate or configure your HTTP client to ignore certificate validation.

2. **CORS:** The gateway is configured to accept requests from all origins (`*`).

3. **Token Storage:** Store JWT tokens securely. Consider using httpOnly cookies for production.

4. **Error Handling:** Always handle 401 responses by redirecting users to login.

5. **Timeouts:** API requests have a 10-second timeout. Consider implementing retry logic for better UX.

6. **Date Formats:** All dates are in ISO 8601 format (e.g., `2025-12-07T12:00:00Z`).

---

## Contact

For API-related questions or issues, contact the Backend Team.
