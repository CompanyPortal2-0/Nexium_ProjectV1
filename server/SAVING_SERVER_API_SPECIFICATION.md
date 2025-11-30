# SAVING SERVER API Specification
**Version:** 1.0  
**Date:** November 30, 2025  
**Server Address:** `192.168.148.94:5001`  
**Protocol:** HTTP

---

## Table of Contents
1. [Overview](#overview)
2. [Authentication & Security](#authentication--security)
3. [API Endpoints](#api-endpoints)
   - [User Management](#1-user-management)
   - [Invitation Codes](#2-invitation-codes)
   - [File Management](#3-file-management)
4. [Data Models](#data-models)
5. [Error Handling](#error-handling)
6. [Integration Flow](#integration-flow)

---

## Overview

The SAVING_SERVER serves as the central persistence layer for the entire microservices architecture. It handles:
- User data storage and retrieval
- Manager invitation code management
- File storage and retrieval

### Consuming Services:
1. **authService** (Port 7051) - User registration
2. **userServices** (Port 7052) - User management and invitation codes
3. **dataService** (Port 7055) - File operations
4. **Gateway** (Port 8000) - Request routing

---

## Authentication & Security

### Internal API Key
All requests from microservices must include an internal API key header:

```
X-Internal-Key: INTERNAL_API_KEY
```

**Purpose:** Ensures only authorized internal services can access the SAVING_SERVER.

**Security Note:** This key should be shared securely among all internal services and never exposed to clients.

---

## API Endpoints

### 1. User Management

#### 1.1 Create User
**Endpoint:** `POST /users/`

**Description:** Creates a new user in the system. Called during user registration.

**Headers:**
```
Content-Type: application/json
X-Internal-Key: INTERNAL_API_KEY
```

**Request Body:**
```json
{
  "email": "string (required, unique)",
  "password": "string (required, but placeholder value)",
  "role": "string (required)",
  "first_name": "string (required)",
  "last_name": "string (required)",
  "address": "string (required)",
  "department": "string (optional)",
  "userID": "string (required, unique - from auth provider)",
  "date_of_birth": "string (required, format: YYYY-MM-DD)"
}
```

**Example Request:**
```json
{
  "email": "john.doe@example.com",
  "password": "temp_password_not_us11447DDDD@@@ed",
  "role": "EMPLOYER",
  "first_name": "John",
  "last_name": "Doe",
  "address": "123 Main St, City",
  "department": "Engineering",
  "userID": "auth0_unique_id_12345",
  "date_of_birth": "1990-05-15"
}
```

**Success Response:**
```
Status: 200 OK or 201 Created
Content-Type: application/json

{
  "id": "integer (auto-generated)",
  "email": "john.doe@example.com",
  "userID": "auth0_unique_id_12345",
  "first_name": "John",
  "last_name": "Doe",
  "role": "EMPLOYER",
  "department": "Engineering",
  "address": "123 Main St, City",
  "date_of_birth": "1990-05-15",
  "created_at": "2025-11-30T10:30:00Z"
}
```

**Error Response:**
```
Status: 400 Bad Request
{
  "error": "Email already exists"
}

Status: 422 Unprocessable Entity
{
  "error": "Missing required field: email"
}

Status: 500 Internal Server Error
{
  "error": "Database error"
}
```

**Business Logic:**
- Email must be unique
- userID must be unique (from authentication provider)
- Password field is a placeholder and not used for authentication
- Role values: "HR", "MANAGER", "EMPLOYER", "GUEST"
- Department is optional

**Called By:** authService during signup process

---

#### 1.2 Get All Users
**Endpoint:** `GET /users/`

**Description:** Retrieves all users from the system.

**Headers:**
```
X-Internal-Key: INTERNAL_API_KEY
```

**Request:** No body required

**Success Response:**
```
Status: 200 OK
Content-Type: application/json

{
  "data": [
    {
      "id": 1,
      "email": "john.doe@example.com",
      "userID": "auth0_unique_id_12345",
      "first_name": "John",
      "last_name": "Doe",
      "role": "employee",
      "department": "Engineering",
      "address": "123 Main St, City",
      "date_of_birth": "1990-05-15",
      "employeesList": []
    },
    {
      "id": 2,
      "email": "jane.smith@example.com",
      "userID": "auth0_unique_id_67890",
      "first_name": "Jane",
      "last_name": "Smith",
      "role": "manager",
      "department": "HR",
      "address": "456 Oak Ave, City",
      "date_of_birth": "1985-08-20",
      "employeesList": ["john.doe@example.com"]
    }
  ]
}
```

**Error Response:**
```
Status: 500 Internal Server Error
{
  "error": "Database error"
}
```

**Business Logic:**
- Returns all users regardless of role or status
- Role should be lowercase in response: "hr", "manager", "employee"
- employeesList contains emails of employees managed by this user (empty array if not a manager)

**Called By:** userServices for user lookup operations

---

### 2. Invitation Codes

#### 2.1 Create Invitation Code
**Endpoint:** `POST /invites/`

**Description:** Creates a new invitation code for a manager to invite employees.

**Headers:**
```
Content-Type: application/json
X-Internal-Key: INTERNAL_API_KEY
```

**Request Body:**
```json
{
  "manager_id": "string (required)",
  "code": "string (required, 8 characters, alphanumeric)",
  "max_uses": "integer (required, typically 1)"
}
```

**Example Request:**
```json
{
  "manager_id": "auth0_unique_id_67890",
  "code": "A7K9M2X5",
  "max_uses": 1
}
```

**Success Response:**
```
Status: 200 OK or 201 Created
Content-Type: application/json

{
  "id": 1,
  "manager_id": "auth0_unique_id_67890",
  "code": "A7K9M2X5",
  "max_uses": 1,
  "current_uses": 0,
  "created_at": "2025-11-30T10:30:00Z",
  "expires_at": "2025-12-07T10:30:00Z",
  "is_active": true
}
```

**Error Response:**
```
Status: 400 Bad Request
{
  "error": "Code already exists"
}

Status: 404 Not Found
{
  "error": "Manager not found"
}

Status: 422 Unprocessable Entity
{
  "error": "Invalid code format"
}
```

**Business Logic:**
- Code must be unique
- Code is 8 characters, uppercase letters and digits only
- manager_id must reference an existing user with "manager" or "hr" role
- max_uses typically is 1 (one invitation per code)
- Code should have an expiration date (suggest 7 days)
- Track current_uses to enforce max_uses limit

**Called By:** userServices when managers generate invitation codes

---

#### 2.2 Validate/Use Invitation Code (Future)
**Endpoint:** `POST /invites/validate`

**Description:** Validates and marks an invitation code as used.

**Note:** This endpoint is suggested for future implementation to complete the invitation flow.

**Headers:**
```
Content-Type: application/json
X-Internal-Key: INTERNAL_API_KEY
```

**Request Body:**
```json
{
  "code": "string (required)",
  "employee_email": "string (required)"
}
```

**Success Response:**
```
Status: 200 OK

{
  "valid": true,
  "manager_id": "auth0_unique_id_67890",
  "remaining_uses": 0
}
```

**Error Response:**
```
Status: 404 Not Found
{
  "error": "Invalid code"
}

Status: 410 Gone
{
  "error": "Code expired or maximum uses reached"
}
```

---

### 3. File Management

#### 3.1 Upload File
**Endpoint:** `POST /file/upload`

**Description:** Uploads a file to the server with user context.

**Headers:**
```
Content-Type: multipart/form-data
X-Internal-Key: INTERNAL_API_KEY
```

**Request Body (multipart/form-data):**
```
file: <binary file data> (required)
user_email: <string> (required, owner of the file)
```

**Example Request (cURL):**
```bash
curl -X POST http://192.168.148.94:5001/file/upload \
  -H "X-Internal-Key: INTERNAL_API_KEY" \
  -F "file=@/path/to/document.pdf" \
  -F "user_email=john.doe@example.com"
```

**Success Response:**
```
Status: 200 OK
Content-Type: application/json

{
  "success": true,
  "filename": "document.pdf",
  "file_id": "unique_file_id_123",
  "size": 1048576,
  "uploaded_at": "2025-11-30T10:30:00Z",
  "uploaded_by": "john.doe@example.com",
  "url": "/file/get/document.pdf"
}
```

**Error Response:**
```
Status: 400 Bad Request
{
  "error": "No file provided"
}

Status: 413 Payload Too Large
{
  "error": "File size exceeds maximum limit (10MB)"
}

Status: 500 Internal Server Error
{
  "error": "Failed to save file"
}
```

**Business Logic:**
- Store file with original filename (handle duplicates with versioning/timestamps)
- Track file ownership via user_email
- Recommended max file size: 10MB
- Store metadata: filename, size, upload date, owner
- Supported file types: PDF, DOC, DOCX, XLS, XLSX, TXT, PNG, JPG, JPEG (expandable)

**Called By:** dataService when users upload files via gateway

---

#### 3.2 Get File
**Endpoint:** `GET /file/get/{filename}`

**Description:** Retrieves a specific file by filename.

**Headers:**
```
X-Internal-Key: INTERNAL_API_KEY
```

**Path Parameters:**
- `filename`: Name of the file to retrieve (required)

**Example Request:**
```
GET /file/get/document.pdf
```

**Success Response:**
```
Status: 200 OK
Content-Type: application/pdf (or appropriate MIME type)
Content-Disposition: attachment; filename="document.pdf"

<binary file data>
```

**Error Response:**
```
Status: 404 Not Found
{
  "error": "File not found"
}

Status: 500 Internal Server Error
{
  "error": "Failed to retrieve file"
}
```

**Business Logic:**
- Return file with appropriate Content-Type header
- Set Content-Disposition for file download
- Handle file not found scenarios
- Optional: Track download statistics

**Called By:** dataService when users download files via gateway

---

#### 3.3 Get All Files
**Endpoint:** `GET /file/getAll`

**Description:** Retrieves a list of all uploaded files with metadata.

**Headers:**
```
X-Internal-Key: INTERNAL_API_KEY
```

**Query Parameters (Optional):**
- `user_email`: Filter by specific user (optional)
- `limit`: Max number of results (optional, default: 100)
- `offset`: Pagination offset (optional, default: 0)

**Example Request:**
```
GET /file/getAll?user_email=john.doe@example.com
```

**Success Response:**
```
Status: 200 OK
Content-Type: application/json

{
  "files": [
    {
      "filename": "document.pdf",
      "file_id": "unique_file_id_123",
      "size": 1048576,
      "uploaded_at": "2025-11-30T10:30:00Z",
      "uploaded_by": "john.doe@example.com",
      "content_type": "application/pdf",
      "url": "/file/get/document.pdf"
    },
    {
      "filename": "report.xlsx",
      "file_id": "unique_file_id_124",
      "size": 524288,
      "uploaded_at": "2025-11-30T11:45:00Z",
      "uploaded_by": "john.doe@example.com",
      "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      "url": "/file/get/report.xlsx"
    }
  ],
  "total": 2,
  "limit": 100,
  "offset": 0
}
```

**Error Response:**
```
Status: 500 Internal Server Error
{
  "error": "Failed to retrieve file list"
}
```

**Business Logic:**
- Return list of all files with metadata
- Support filtering by user_email
- Implement pagination for large datasets
- Include file size, upload date, owner, content type

**Called By:** dataService to display file listings to users

---

## Data Models

### User Model
```json
{
  "id": "integer (auto-generated primary key)",
  "email": "string (unique, indexed)",
  "userID": "string (unique, indexed - from auth provider)",
  "password": "string (placeholder, not used)",
  "first_name": "string",
  "last_name": "string",
  "role": "string (hr|manager|employee|guest)",
  "department": "string (nullable)",
  "address": "string",
  "date_of_birth": "string (YYYY-MM-DD)",
  "employeesList": "array of strings (email addresses)",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

**Indexes:**
- Primary: `id`
- Unique: `email`, `userID`
- Index: `role` (for filtering)

---

### Invitation Code Model
```json
{
  "id": "integer (auto-generated primary key)",
  "manager_id": "string (foreign key to User.userID)",
  "code": "string (unique, 8 characters)",
  "max_uses": "integer",
  "current_uses": "integer (default: 0)",
  "is_active": "boolean (default: true)",
  "created_at": "timestamp",
  "expires_at": "timestamp (7 days from creation)",
  "used_by": "array of strings (emails of users who used this code)"
}
```

**Indexes:**
- Primary: `id`
- Unique: `code`
- Index: `manager_id`, `is_active`

---

### File Model
```json
{
  "id": "integer (auto-generated primary key)",
  "file_id": "string (unique identifier)",
  "filename": "string",
  "original_filename": "string",
  "size": "integer (bytes)",
  "content_type": "string (MIME type)",
  "uploaded_by": "string (user email)",
  "uploaded_at": "timestamp",
  "file_path": "string (internal storage path)",
  "is_deleted": "boolean (default: false)",
  "download_count": "integer (default: 0)"
}
```

**Indexes:**
- Primary: `id`
- Unique: `file_id`
- Index: `uploaded_by`, `filename`

---

## Error Handling

### Standard Error Response Format
All errors should follow this format:

```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": "Additional details (optional)"
}
```

### HTTP Status Codes
- `200 OK` - Successful GET request
- `201 Created` - Successful POST request creating resource
- `400 Bad Request` - Invalid request format or parameters
- `401 Unauthorized` - Missing or invalid API key
- `404 Not Found` - Resource not found
- `409 Conflict` - Duplicate resource (email, code, etc.)
- `413 Payload Too Large` - File size exceeds limit
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server-side error
- `503 Service Unavailable` - Service temporarily unavailable

---

## Integration Flow

### 1. User Registration Flow
```
Client → authService → SAVING_SERVER

1. Client sends signup request to authService
2. authService creates user in Supabase (authentication)
3. authService calls SAVING_SERVER POST /users/ (user data)
4. If SAVING_SERVER fails, authService deletes Supabase user (rollback)
5. Return JWT token to client
```

### 2. User Lookup Flow
```
Client → Gateway → userServices → SAVING_SERVER

1. Client requests user data (with JWT)
2. Gateway extracts email from JWT
3. userServices calls SAVING_SERVER GET /users/
4. SAVING_SERVER returns all users
5. userServices filters by email
6. Return user data to client
```

### 3. Invitation Code Generation Flow
```
Client → Gateway → userServices → SAVING_SERVER

1. Manager requests invitation code (with JWT)
2. Gateway extracts manager email from JWT
3. userServices validates manager role
4. userServices generates random 8-char code
5. userServices calls SAVING_SERVER POST /invites/
6. Return code to manager
```

### 4. File Upload Flow
```
Client → filesGateway → dataService → SAVING_SERVER

1. Client uploads file (with JWT)
2. filesGateway extracts user email from JWT
3. filesGateway forwards to dataService with X-User-Email header
4. dataService calls SAVING_SERVER POST /file/upload
5. SAVING_SERVER stores file and returns metadata
6. Return success to client
```

### 5. File Retrieval Flow
```
Client → filesGateway → dataService → SAVING_SERVER

1. Client requests file (with JWT)
2. filesGateway validates JWT
3. filesGateway forwards to dataService
4. dataService calls SAVING_SERVER GET /file/get/{filename}
5. SAVING_SERVER returns file binary
6. Stream file to client
```

---

## Implementation Notes

### Security Recommendations
1. **HTTPS Required**: All production traffic should use HTTPS
2. **Rate Limiting**: Implement rate limiting on all endpoints
3. **File Scanning**: Scan uploaded files for malware
4. **Input Validation**: Validate all inputs before processing
5. **SQL Injection Prevention**: Use parameterized queries
6. **CORS**: Configure CORS appropriately for your domains

### Performance Recommendations
1. **Database Indexing**: Index frequently queried fields (email, userID, code)
2. **File Storage**: Use dedicated file storage (S3, Azure Blob, or local filesystem)
3. **Caching**: Implement caching for GET /users/ endpoint
4. **Connection Pooling**: Use database connection pooling
5. **Pagination**: Implement pagination for list endpoints

### Monitoring & Logging
1. Log all API requests with timestamp, endpoint, and status
2. Track file upload/download statistics
3. Monitor storage usage
4. Alert on repeated failed authentication attempts
5. Track API response times

---

## Testing Endpoints

### Health Check (Recommended)
```
GET /health

Response:
{
  "status": "healthy",
  "service": "SAVING_SERVER",
  "version": "1.0",
  "timestamp": "2025-11-30T10:30:00Z"
}
```

### Sample Test Data
```bash
# Create test user
curl -X POST http://192.168.148.94:5001/users/ \
  -H "Content-Type: application/json" \
  -H "X-Internal-Key: INTERNAL_API_KEY" \
  -d '{
    "email": "test@example.com",
    "password": "temp_password",
    "role": "employee",
    "first_name": "Test",
    "last_name": "User",
    "address": "123 Test St",
    "department": "QA",
    "userID": "test_user_123",
    "date_of_birth": "1995-01-01"
  }'

# Get all users
curl -X GET http://192.168.148.94:5001/users/ \
  -H "X-Internal-Key: INTERNAL_API_KEY"

# Create invitation code
curl -X POST http://192.168.148.94:5001/invites/ \
  -H "Content-Type: application/json" \
  -H "X-Internal-Key: INTERNAL_API_KEY" \
  -d '{
    "manager_id": "test_user_123",
    "code": "TEST1234",
    "max_uses": 1
  }'

# Upload file
curl -X POST http://192.168.148.94:5001/file/upload \
  -H "X-Internal-Key: INTERNAL_API_KEY" \
  -F "file=@test.pdf" \
  -F "user_email=test@example.com"

# Get all files
curl -X GET http://192.168.148.94:5001/file/getAll \
  -H "X-Internal-Key: INTERNAL_API_KEY"

# Download file
curl -X GET http://192.168.148.94:5001/file/get/test.pdf \
  -H "X-Internal-Key: INTERNAL_API_KEY" \
  -o downloaded.pdf
```

---

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-30 | Initial API specification |

---

## Contact & Support

For questions or clarifications about this API specification, please contact:
- **Architecture Team**: [Your contact info]
- **Integration Support**: [Your contact info]

---

**End of Document**
