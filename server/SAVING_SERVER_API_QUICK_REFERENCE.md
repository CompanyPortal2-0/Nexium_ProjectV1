# SAVING SERVER API - Quick Reference

## Base URL
```
http://192.168.148.94:5001
```

## Authentication
All requests require:
```
X-Internal-Key: INTERNAL_API_KEY
```

---

## Endpoints Summary

### User Management

| Method | Endpoint | Description | Called By |
|--------|----------|-------------|-----------|
| POST | `/users/` | Create new user | authService |
| GET | `/users/` | Get all users | userServices |

### Invitation Codes

| Method | Endpoint | Description | Called By |
|--------|----------|-------------|-----------|
| POST | `/invites/` | Create invitation code | userServices |

### File Management

| Method | Endpoint | Description | Called By |
|--------|----------|-------------|-----------|
| POST | `/file/upload` | Upload file | dataService |
| GET | `/file/get/{filename}` | Download file | dataService |
| GET | `/file/getAll` | List all files | dataService |

---

## Quick Examples

### Create User
```bash
curl -X POST http://192.168.148.94:5001/users/ \
  -H "Content-Type: application/json" \
  -H "X-Internal-Key: INTERNAL_API_KEY" \
  -d '{
    "email": "user@example.com",
    "password": "temp_password_not_us11447DDDD@@@ed",
    "role": "EMPLOYER",
    "first_name": "John",
    "last_name": "Doe",
    "address": "123 Main St",
    "department": "Engineering",
    "userID": "auth_id_12345",
    "date_of_birth": "1990-01-01"
  }'
```

### Get All Users
```bash
curl -X GET http://192.168.148.94:5001/users/ \
  -H "X-Internal-Key: INTERNAL_API_KEY"
```

### Create Invitation Code
```bash
curl -X POST http://192.168.148.94:5001/invites/ \
  -H "Content-Type: application/json" \
  -H "X-Internal-Key: INTERNAL_API_KEY" \
  -d '{
    "manager_id": "auth_id_12345",
    "code": "A7K9M2X5",
    "max_uses": 1
  }'
```

### Upload File
```bash
curl -X POST http://192.168.148.94:5001/file/upload \
  -H "X-Internal-Key: INTERNAL_API_KEY" \
  -F "file=@document.pdf" \
  -F "user_email=user@example.com"
```

### Get All Files
```bash
curl -X GET http://192.168.148.94:5001/file/getAll \
  -H "X-Internal-Key: INTERNAL_API_KEY"
```

### Download File
```bash
curl -X GET http://192.168.148.94:5001/file/get/document.pdf \
  -H "X-Internal-Key: INTERNAL_API_KEY" \
  -o document.pdf
```

---

## Database Schema Requirements

### Users Table
- `id` (PK, auto-increment)
- `email` (unique, indexed)
- `userID` (unique, indexed)
- `password` (placeholder)
- `first_name`
- `last_name`
- `role` (hr|manager|employee|guest)
- `department` (nullable)
- `address`
- `date_of_birth`
- `employeesList` (JSON array)
- `created_at`
- `updated_at`

### Invites Table
- `id` (PK, auto-increment)
- `manager_id` (FK to users.userID)
- `code` (unique, 8 chars)
- `max_uses` (integer)
- `current_uses` (default: 0)
- `is_active` (default: true)
- `created_at`
- `expires_at` (created_at + 7 days)
- `used_by` (JSON array)

### Files Table
- `id` (PK, auto-increment)
- `file_id` (unique)
- `filename`
- `original_filename`
- `size` (bytes)
- `content_type`
- `uploaded_by` (user email)
- `uploaded_at`
- `file_path` (internal storage)
- `is_deleted` (default: false)
- `download_count` (default: 0)

---

## Response Format Standards

### Success (User Creation)
```json
{
  "id": 1,
  "email": "user@example.com",
  "userID": "auth_id_12345",
  "first_name": "John",
  "last_name": "Doe",
  "role": "EMPLOYER",
  "department": "Engineering",
  "created_at": "2025-11-30T10:30:00Z"
}
```

### Success (Get All Users)
```json
{
  "data": [
    {
      "id": 1,
      "email": "user@example.com",
      "userID": "auth_id_12345",
      "first_name": "John",
      "last_name": "Doe",
      "role": "employee",
      "department": "Engineering",
      "employeesList": []
    }
  ]
}
```

### Success (File Upload)
```json
{
  "success": true,
  "filename": "document.pdf",
  "file_id": "unique_file_id_123",
  "size": 1048576,
  "uploaded_at": "2025-11-30T10:30:00Z",
  "uploaded_by": "user@example.com"
}
```

### Success (Get All Files)
```json
{
  "files": [
    {
      "filename": "document.pdf",
      "file_id": "unique_file_id_123",
      "size": 1048576,
      "uploaded_at": "2025-11-30T10:30:00Z",
      "uploaded_by": "user@example.com",
      "content_type": "application/pdf",
      "url": "/file/get/document.pdf"
    }
  ],
  "total": 1
}
```

### Error
```json
{
  "error": "Human-readable error message"
}
```

---

## HTTP Status Codes
- `200` - Success (GET)
- `201` - Created (POST)
- `400` - Bad Request
- `401` - Unauthorized (invalid API key)
- `404` - Not Found
- `409` - Conflict (duplicate)
- `500` - Server Error

---

## Important Notes

1. **Role Values**: Use lowercase in responses ("hr", "manager", "employee")
2. **Date Format**: ISO 8601 (YYYY-MM-DD or full timestamp)
3. **File Size Limit**: Recommend 10MB max
4. **Code Expiration**: Invitation codes expire after 7 days
5. **Unique Constraints**: email, userID, code must be unique

---

For full documentation, see: `SAVING_SERVER_API_SPECIFICATION.md`
