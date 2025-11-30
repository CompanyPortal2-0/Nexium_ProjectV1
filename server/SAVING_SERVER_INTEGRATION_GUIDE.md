# SAVING SERVER Integration Architecture

## System Overview
```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENT                                      │
│                         (Web Browser/App)                                │
│                         with JWT Token                                   │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                    ┌────────────┴───────────┐
                    │                        │
         ┌──────────▼──────────┐  ┌─────────▼─────────┐
         │   filesGateway      │  │   Gateway         │
         │   (Port 8000)       │  │   (SocketIO)      │
         │   - JWT Auth        │  │   - Game/Meeting  │
         └──────────┬──────────┘  └───────────────────┘
                    │
         ┌──────────┴──────────┬────────────────┬─────────────────┐
         │                     │                │                 │
┌────────▼────────┐   ┌────────▼────────┐  ┌──▼──────────┐  ┌───▼──────────┐
│  authService    │   │  userServices   │  │ dataService │  │ meetService  │
│  (Port 7051)    │   │  (Port 7052)    │  │ (Port 7055) │  │ (Port 7053)  │
│  - Signup       │   │  - User lookup  │  │ - Files     │  │              │
│  - Login        │   │  - Inv. codes   │  │             │  │              │
└────────┬────────┘   └────────┬────────┘  └──┬──────────┘  └──────────────┘
         │                     │               │
         └─────────────────────┴───────────────┴───────────────┐
                                                                │
                                                    ┌───────────▼───────────┐
                                                    │   SAVING SERVER       │
                                                    │ (192.168.148.94:5001) │
                                                    │                       │
                                                    │ APIs:                 │
                                                    │ • POST /users/        │
                                                    │ • GET  /users/        │
                                                    │ • POST /invites/      │
                                                    │ • POST /file/upload   │
                                                    │ • GET  /file/get/{f}  │
                                                    │ • GET  /file/getAll   │
                                                    └───────────────────────┘
```

---

## API Usage by Service

### 1. authService → SAVING_SERVER

**Flow: User Registration**
```
┌─────────┐         ┌──────────────┐         ┌───────────────┐
│ Client  │────────▶│ authService  │────────▶│ SAVING_SERVER │
└─────────┘         └──────────────┘         └───────────────┘
   1. Signup          2. Create in             3. Store user
      request            Supabase                 data
                      3. POST /users/
```

**API Used:**
- `POST /users/` - Create user record

**Request:**
```json
{
  "email": "user@example.com",
  "password": "temp_password_not_us11447DDDD@@@ed",
  "role": "EMPLOYER",
  "first_name": "John",
  "last_name": "Doe",
  "address": "123 Main St",
  "department": "Engineering",
  "userID": "supabase_uuid",
  "date_of_birth": "1990-01-01"
}
```

**Critical:** If SAVING_SERVER fails, authService deletes the Supabase user (rollback)

---

### 2. userServices → SAVING_SERVER

**Flow 1: User Lookup**
```
┌─────────┐         ┌──────────────┐         ┌───────────────┐
│ Gateway │────────▶│ userServices │────────▶│ SAVING_SERVER │
└─────────┘         └──────────────┘         └───────────────┘
   1. Request          2. GET /users/          3. Return all
      user by             Filter by email         users
      email
```

**Flow 2: Generate Invitation Code**
```
┌─────────┐         ┌──────────────┐         ┌───────────────┐
│ Manager │────────▶│ userServices │────────▶│ SAVING_SERVER │
└─────────┘         └──────────────┘         └───────────────┘
   1. Request          2. Validate manager     3. Store code
      inv. code        3. Generate code
                       4. POST /invites/
```

**APIs Used:**
- `GET /users/` - Get all users (then filter by email)
- `POST /invites/` - Create invitation code

**Invitation Code Request:**
```json
{
  "manager_id": "manager_user_id",
  "code": "A7K9M2X5",
  "max_uses": 1
}
```

---

### 3. dataService → SAVING_SERVER

**Flow: File Operations**
```
┌─────────┐       ┌──────────────┐       ┌─────────────┐       ┌───────────────┐
│ Client  │──────▶│ filesGateway │──────▶│ dataService │──────▶│ SAVING_SERVER │
└─────────┘       └──────────────┘       └─────────────┘       └───────────────┘
  1. Upload         2. Extract user        3. Forward file      4. Store file
     file              from JWT               + user email         + metadata
  (with JWT)        3. Add headers
```

**APIs Used:**
- `POST /file/upload` - Upload file
- `GET /file/get/{filename}` - Download file
- `GET /file/getAll` - List files

**Upload Request (multipart/form-data):**
```
file: <binary data>
user_email: "user@example.com"
```

**Get All Response:**
```json
{
  "files": [
    {
      "filename": "document.pdf",
      "file_id": "unique_id",
      "size": 1048576,
      "uploaded_at": "2025-11-30T10:30:00Z",
      "uploaded_by": "user@example.com",
      "url": "/file/get/document.pdf"
    }
  ]
}
```

---

## Authentication Flow

### Internal Service Authentication
```
Every microservice → SAVING_SERVER request includes:

Headers:
  X-Internal-Key: INTERNAL_API_KEY
```

**Purpose:** Prevents external/unauthorized access to SAVING_SERVER

---

### User Authentication Flow
```
┌────────┐         ┌──────────────┐         ┌──────────┐
│ Client │────────▶│ authService  │────────▶│ Supabase │
└────────┘         └──────────────┘         └──────────┘
  1. Login           2. Validate              3. Return
     (email/pwd)        credentials              JWT Token

     ↓
     JWT Token contains: user email, userID, role
     ↓
     Client includes in all requests:
     Authorization: Bearer <JWT>
     ↓
     Gateway extracts email from JWT
     ↓
     Gateway passes to microservices via headers
```

---

## Data Flow Examples

### Example 1: Complete User Registration
```
Step 1: Client → authService
POST /signup
{
  "email": "john@example.com",
  "FirstName": "John",
  "LastName": "Doe",
  "Password": "secure123",
  "DateOfBirth": "1990-01-01",
  "Address": "123 Main St"
}

Step 2: authService → Supabase
Create authentication user
Returns: userID = "abc123"

Step 3: authService → SAVING_SERVER
POST /users/
Headers: X-Internal-Key: INTERNAL_API_KEY
{
  "email": "john@example.com",
  "userID": "abc123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "EMPLOYER",
  "department": "Engineering",
  "address": "123 Main St",
  "date_of_birth": "1990-01-01",
  "password": "temp_password_not_us11447DDDD@@@ed"
}

Step 4: SAVING_SERVER Response
{
  "id": 1,
  "email": "john@example.com",
  "userID": "abc123",
  "created_at": "2025-11-30T10:30:00Z"
}

Step 5: authService → Client
{
  "Token": "eyJhbGc...",
  "id": "abc123"
}
```

---

### Example 2: Manager Generates Invitation Code
```
Step 1: Client → Gateway
POST /getCodeForManager
Authorization: Bearer <JWT>
{
  "current_user_email": "manager@example.com",
  "manager_email": "newmanager@example.com"
}

Step 2: Gateway → userServices
Forwards request + JWT

Step 3: userServices → SAVING_SERVER
GET /users/
Headers: X-Internal-Key: INTERNAL_API_KEY

Step 4: SAVING_SERVER → userServices
{
  "data": [
    {"email": "manager@example.com", "role": "manager", "userID": "m123"},
    {"email": "newmanager@example.com", "role": "manager", "userID": "m456"}
  ]
}

Step 5: userServices validates and generates code
code = "A7K9M2X5"

Step 6: userServices → SAVING_SERVER
POST /invites/
Headers: X-Internal-Key: INTERNAL_API_KEY
{
  "manager_id": "m456",
  "code": "A7K9M2X5",
  "max_uses": 1
}

Step 7: SAVING_SERVER → userServices
{
  "id": 1,
  "manager_id": "m456",
  "code": "A7K9M2X5",
  "created_at": "2025-11-30T10:30:00Z",
  "expires_at": "2025-12-07T10:30:00Z"
}

Step 8: userServices → Client
{
  "code": "A7K9M2X5"
}
```

---

### Example 3: File Upload
```
Step 1: Client → filesGateway
POST /upload
Authorization: Bearer <JWT>
Content-Type: multipart/form-data
file: document.pdf

Step 2: filesGateway extracts email from JWT
user_email = "john@example.com"

Step 3: filesGateway → dataService
POST /upload
Headers:
  X-Internal-Key: INTERNAL_API_KEY
  X-User-Email: john@example.com
Body: file data

Step 4: dataService → SAVING_SERVER
POST /file/upload
Headers: X-Internal-Key: INTERNAL_API_KEY
Form Data:
  file: <binary>
  user_email: john@example.com

Step 5: SAVING_SERVER stores file and responds
{
  "success": true,
  "filename": "document.pdf",
  "file_id": "file_123",
  "size": 1048576,
  "uploaded_at": "2025-11-30T10:30:00Z",
  "uploaded_by": "john@example.com"
}

Step 6: dataService → filesGateway → Client
{
  "message": "File uploaded successfully",
  "data": { ... }
}
```

---

## Error Handling Scenarios

### Scenario 1: User Already Exists
```
authService → SAVING_SERVER
POST /users/
{
  "email": "existing@example.com",
  ...
}

SAVING_SERVER Response:
Status: 409 Conflict
{
  "error": "Email already exists"
}

authService Action:
- Delete user from Supabase (rollback)
- Return error to client
```

---

### Scenario 2: SAVING_SERVER Unavailable
```
authService → SAVING_SERVER
POST /users/
(Connection timeout or 503 error)

authService Action:
- Catch exception
- Delete user from Supabase (rollback)
- Return error to client:
  {
    "message": "error creating in the saving server",
    "del result": "..."
  }
```

---

### Scenario 3: Invalid Invitation Code Data
```
userServices → SAVING_SERVER
POST /invites/
{
  "manager_id": "invalid_id",
  "code": "ABC",  // Too short
  "max_uses": 1
}

SAVING_SERVER Response:
Status: 422 Unprocessable Entity
{
  "error": "Invalid code format"
}

userServices → Client:
Status: 500
{
  "Text": "Failed to save code to database"
}
```

---

## Security Considerations

### 1. API Key Protection
- `INTERNAL_API_KEY` must be kept secret
- Only internal microservices should have access
- Rotate periodically

### 2. JWT Validation
- Client requests are authenticated via JWT
- Gateway extracts user identity
- Never trust client-provided user email directly

### 3. File Upload Security
- Validate file types
- Scan for malware
- Limit file size (10MB recommended)
- Sanitize filenames

### 4. Database Security
- Use parameterized queries (prevent SQL injection)
- Encrypt sensitive data at rest
- Regular backups

---

## Performance Requirements

### Response Time Targets
- `GET /users/`: < 200ms
- `POST /users/`: < 500ms
- `POST /invites/`: < 300ms
- `GET /file/getAll`: < 300ms
- `POST /file/upload`: < 2s (depends on file size)
- `GET /file/get/{filename}`: < 1s

### Scalability
- Support 100+ concurrent users
- Handle 1000+ user records
- Store 10,000+ files
- Database connection pooling

---

## Required Database Indexes

```sql
-- Users table
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_userID ON users(userID);
CREATE INDEX idx_users_role ON users(role);

-- Invites table
CREATE INDEX idx_invites_code ON invites(code);
CREATE INDEX idx_invites_manager_id ON invites(manager_id);
CREATE INDEX idx_invites_active ON invites(is_active);

-- Files table
CREATE INDEX idx_files_filename ON files(filename);
CREATE INDEX idx_files_uploaded_by ON files(uploaded_by);
CREATE INDEX idx_files_file_id ON files(file_id);
```

---

## Testing Checklist for SAVING_SERVER Team

- [ ] Create user successfully
- [ ] Reject duplicate email
- [ ] Reject duplicate userID
- [ ] Get all users returns correct format
- [ ] Create invitation code successfully
- [ ] Reject duplicate invitation code
- [ ] Invitation code expires after 7 days
- [ ] Upload file successfully
- [ ] Reject file without user_email
- [ ] Download file returns correct content type
- [ ] List all files returns metadata
- [ ] Reject requests without X-Internal-Key
- [ ] Handle database connection errors gracefully
- [ ] Validate all required fields
- [ ] Return appropriate HTTP status codes

---

## Deployment Checklist

- [ ] Database schema created
- [ ] Indexes created
- [ ] File storage directory configured
- [ ] Environment variables set
- [ ] INTERNAL_API_KEY configured
- [ ] CORS configured (if needed)
- [ ] Logging configured
- [ ] Error handling implemented
- [ ] Rate limiting configured
- [ ] Backup strategy in place
- [ ] Health check endpoint working
- [ ] SSL/TLS certificates installed (for HTTPS)

---

For detailed API documentation, see:
- **Full Specification:** `SAVING_SERVER_API_SPECIFICATION.md`
- **Quick Reference:** `SAVING_SERVER_API_QUICK_REFERENCE.md`
