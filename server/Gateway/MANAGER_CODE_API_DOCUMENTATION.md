# Manager Code Generation API Documentation

## Overview
This API provides functionality for managers to generate invitation codes that allow employees to join their teams and become managers themselves.

## Authentication
All endpoints require JWT authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

---

## 1. Generate Manager Invitation Code

### Endpoint
```
GET /getCodeForManager
```

### Description
Allows an authenticated manager to generate a unique invitation code that can be shared with employees. This code allows employees to join the manager's team and become managers themselves.

### Request
- **Method**: GET
- **Headers**:
  - `Authorization: Bearer <jwt_token>` (required)
  - `Content-Type: application/json`

### Response
**Success (200):**
```json
{
  "code": "ABC123XYZ789",
  "expires_at": "2025-12-15T10:30:00Z",
  "manager_email": "manager@company.com"
}
```

**Error (400):**
```json
{
  "Text": "Manager email is required"
}
```

**Error (401):**
```json
{
  "error": "Missing or invalid JWT token"
}
```

---

## 2. Become Manager Using Code

### Endpoint
```
POST /becamemanager
```

### Description
Allows an authenticated employee to use a manager invitation code to become a manager. This promotes the employee to manager role and allows them to generate their own invitation codes.

### Request
- **Method**: POST
- **Headers**:
  - `Authorization: Bearer <jwt_token>` (required)
  - `Content-Type: application/json`
- **Body**:
```json
{
  "code": "ABC123XYZ789"
}
```

### Response
**Success (200):**
```json
{
  "success": true,
  "message": "Successfully became manager",
  "new_role": "MANAGER",
  "user_email": "employee@company.com"
}
```

**Error (400):**
```json
{
  "error": "Invalid or expired code"
}
```

**Error (401):**
```json
{
  "error": "Could not resolve user identity"
}
```

---

## 3. Generate System Manager Code (Admin Only)

### Endpoint
```
GET /generateBecameManagerCode
```

### Description
Administrative endpoint to generate manager codes. This is typically used by system administrators to create initial manager accounts or for special cases.

### Request
- **Method**: GET
- **Headers**:
  - `Content-Type: application/json`
- **Body** (optional - depends on implementation):
```json
{
  "admin_key": "system_admin_key",
  "target_email": "user@company.com"
}
```

### Response
**Success (200):**
```json
{
  "code": "SYS456DEF012",
  "generated_for": "user@company.com",
  "expires_at": "2025-12-15T10:30:00Z"
}
```

**Error (403):**
```json
{
  "error": "Unauthorized access"
}
```

---

## Usage Flow

1. **Manager Login**: Manager authenticates and receives JWT token
2. **Generate Code**: Manager calls `GET /getCodeForManager` to get invitation code
3. **Share Code**: Manager shares the code with potential employees
4. **Employee Login**: Employee authenticates and receives JWT token
5. **Become Manager**: Employee calls `POST /becamemanager` with the code
6. **New Manager**: Employee is now a manager and can generate their own codes

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request (missing/invalid data)
- `401`: Authentication required
- `403`: Forbidden (insufficient permissions)
- `503`: Service unavailable (backend service issues)

## Notes

- All codes have expiration times (typically 24-48 hours)
- Each code can only be used once
- Codes are tied to specific managers
- The system supports hierarchical team structures