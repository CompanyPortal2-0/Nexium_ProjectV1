# Meeting Service - Architecture Analysis

## Overview
This document analyzes the complete microservices architecture of the CompanyPortal project and explains how the Meeting Service fits within the system.

---

## System Architecture Summary

### **Architectural Pattern: Microservices with API Gateway**

```
CLIENT (Browser/Mobile)
    ↓
GATEWAY LAYER (Port 8000 + SocketIO)
    ↓
┌─────────────────────────────────────────────────────────┐
│            MICROSERVICES LAYER                          │
├──────────────┬──────────────┬──────────────┬───────────┤
│ authService  │ userServices │ dataService  │ Meeting   │
│ (Port 7051)  │ (Port 7052)  │ (Port 7055)  │ (7053)    │
└──────────────┴──────────────┴──────────────┴───────────┘
    ↓
SAVING_SERVER (Centralized Data Persistence)
(192.168.148.94:5001)
```

---

## Current Architecture Components

### 1. **Gateway Layer** (`Gateway/app.py`)
**Responsibilities:**
- Request routing and load balancing
- JWT authentication and validation
- User email extraction from JWT tokens
- WebSocket proxy for real-time communication
- Internal API key management

**Key Features:**
- **SocketIO Namespaces:**
  - `/game` - Routes game events to GameService
  - `/meeting` - Routes meeting events to MeetingService
- **HTTP Endpoints:**
  - File operations routing (`filesGateway.py`)
  - Meeting operations routing (`meetGateway.py`)

**Communication Pattern:**
```python
# Gateway validates JWT → Extracts user_email → Adds X-Internal-Key
headers = {
    'X-Internal-Key': 'nexus-internal-secret-key-123',
    'X-User-Email': user_email  # From JWT
}
```

---

### 2. **authService** (Port 7051)
**Tech Stack:** Flask + Supabase Auth

**Responsibilities:**
- User registration with Supabase
- User authentication (login/logout)
- JWT token generation
- Two-phase commit with SAVING_SERVER

**Integration with SAVING_SERVER:**
```python
# 1. Create user in Supabase
result = auth_helper.CreateUser(email, password)

# 2. Store user data in SAVING_SERVER
response = requests.post(
    f'http://{SAVING_server}/users/', 
    json=user_data, 
    headers={"X-Internal-Key": "nexus-internal-secret-key-123"}
)

# 3. Rollback if SAVING_SERVER fails
if response.status_code != 200:
    auth_helper.deleteUser(id)
```

**API Usage:**
- `POST /users/` - Create user record in SAVING_SERVER

---

### 3. **userServices** (Port 7052)
**Responsibilities:**
- User lookup by email
- Invitation code generation and validation
- User management operations

**Integration with SAVING_SERVER:**
```python
# Get all users, filter by email locally
response = requests.get(
    f'http://{SAVING_server}/users/',
    headers={"X-Internal-Key": "nexus-internal-secret-key-123"}
)

# Create invitation code
response = requests.post(
    f'http://{SAVING_server}/invites/',
    json={"manager_id": id, "code": code, "max_uses": 1},
    headers={"X-Internal-Key": "nexus-internal-secret-key-123"}
)
```

**API Usage:**
- `GET /users/` - Retrieve user list
- `POST /invites/` - Create invitation codes

---

### 4. **dataService** (Port 7055)
**Responsibilities:**
- File upload/download operations
- File metadata management
- Access control for files

**Integration Pattern:**
```python
class FileHelper:
    HEADERS = {"X-Internal-Key": "nexus-internal-secret-key-123"}
    
    def upload_file(self, file, user_email):
        files = {'file': (file.filename, file.stream, file.content_type)}
        data = {'user_email': user_email}
        
        response = requests.post(
            f"{self.base_url}/file/upload",
            files=files,
            headers=FileHelper.HEADERS,
            data=data
        )
```

**API Usage:**
- `POST /file/upload` - Upload files
- `GET /file/get/{filename}` - Download files
- `GET /file/getAll` - List all files

---

### 5. **meetingService** (Port 7053) - **CURRENT SERVICE**
**Tech Stack:** Flask + Flask-SocketIO + WebRTC

**Current State:**
- ✅ WebRTC signaling server (offers, answers, ICE candidates)
- ✅ Room management (join, leave, peer tracking)
- ✅ In-memory meeting storage (`Helper.py`)
- ✅ Basic CRUD operations (create, join, room access)
- ❌ **NOT INTEGRATED WITH SAVING_SERVER**

**Current Data Model:**
```python
class Meeting:
    __ID: str                      # UUID
    __Title: str
    __Object: str
    __Description: str
    __InvitationLink: str
    __LogPath: str                 # NOT IMPLEMENTED
    __InvitedEmployeesList: List[str]
    __CreatedAt: str
    __Password: str
```

**Current Storage:**
```python
class MeetHelper:
    __meetings: List[Meeting] = []  # IN-MEMORY ONLY!
```

**Problem:** All meeting data is lost when the service restarts! 🔴

---

## SAVING_SERVER Integration Pattern

### **Standard Integration Pattern Used by All Services:**

```python
# 1. Import requests and load environment
import requests
from dotenv import load_dotenv

load_dotenv()

# 2. Get SAVING_SERVER URL from environment
SAVING_server = os.getenv('SAVING_SERVER')  # e.g., "192.168.148.94:5001"

# 3. Set internal API key header
HEADERS = {"X-Internal-Key": "nexus-internal-secret-key-123"}

# 4. Make HTTP requests to SAVING_SERVER
response = requests.post(
    f'http://{SAVING_server}/endpoint',
    json=data,
    headers=HEADERS
)

# 5. Handle response
if response.status_code == 200:
    return response.json()
else:
    # Handle error
```

---

## What Needs to be Implemented in Meeting Service

### **Required Changes:**

1. **Add SAVING_SERVER Communication** (`Helper.py`)
   - Replace in-memory storage with API calls
   - Implement all CRUD operations via HTTP

2. **Update Meeting Model** (`meeting.py`)
   - Add missing fields: `created_by`, `is_active`, `started_at`, `ended_at`
   - Add database ID field
   - Implement log file operations

3. **Update API Endpoints** (`app.py`)
   - `/create-meet` → POST to `/meetings/` on SAVING_SERVER
   - Add `/meetings/<id>` endpoints (GET, PUT, DELETE)
   - Add `/meetings/<id>/start` and `/meetings/<id>/end`
   - Add `/meetings/<id>/log` for log operations

4. **Add Environment Configuration** (`.env`)
   ```
   SAVING_SERVER=192.168.148.94:5001
   ```

5. **Implement Log File Management**
   - Create log files in `./storage/meeting_logs/`
   - Implement append operations
   - Track meeting events (start, end, participants)

---

## SAVING_SERVER Meeting API Endpoints

According to `MEETINGS_API.md`, the following endpoints are available:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/meetings/` | Create new meeting |
| GET | `/meetings/` | Get all meetings (with filters) |
| GET | `/meetings/<id>` | Get specific meeting |
| PUT | `/meetings/<id>` | Update meeting |
| DELETE | `/meetings/<id>` | Soft delete meeting |
| POST | `/meetings/<id>/start` | Mark meeting as started |
| POST | `/meetings/<id>/end` | Mark meeting as ended |
| POST | `/meetings/<id>/log` | Append to meeting log |
| GET | `/meetings/<id>/log` | Get meeting log |

---

## Communication Flow After Integration

### **Flow: Create Meeting**
```
Client
  ↓ POST /create-meet
Gateway (meetGateway.py)
  ↓ Forward with X-Internal-Key
MeetingService (app.py)
  ↓ Helper.createMeeting()
  ↓ POST http://192.168.148.94:5001/meetings/
SAVING_SERVER
  ↓ Store in PostgreSQL
  ↓ Return meeting data
MeetingService
  ↓ Return to client
```

### **Flow: Join Meeting**
```
Client
  ↓ POST /join-meet {meet_id, password, user_email}
MeetingService
  ↓ Helper.getMeetingByID(meet_id)
  ↓ GET http://192.168.148.94:5001/meetings/<meet_id>
SAVING_SERVER
  ↓ Return meeting data
MeetingService
  ↓ Verify password
  ↓ POST http://192.168.148.94:5001/meetings/<meet_id>/log
  ↓ {log_entry: "User {email} joined"}
  ↓ Return room URL
```

---

## Security & Authentication

### **Internal Service Communication:**
- All services → SAVING_SERVER: `X-Internal-Key: nexus-internal-secret-key-123`
- No JWT required for internal communication
- Gateway handles JWT validation for external clients

### **Client → Gateway:**
- JWT token in Authorization header
- Gateway extracts `user_email` from JWT
- Gateway adds `X-User-Email` header for internal services

---

## Consistency Pattern

All services follow the same integration pattern:

1. **Environment Configuration** - SAVING_SERVER URL in `.env`
2. **Helper Class** - Encapsulates SAVING_SERVER communication
3. **Standard Headers** - `X-Internal-Key` for authentication
4. **Error Handling** - Rollback on SAVING_SERVER failures (see authService)
5. **HTTP Requests** - Use `requests` library

---

## Summary

**Current State:**
- MeetingService is a standalone WebRTC signaling server
- Uses in-memory storage (data loss on restart)
- No persistence layer integration

**Target State:**
- Integrate with SAVING_SERVER for persistence
- Follow the same pattern as authService, userServices, and dataService
- Implement all meeting CRUD operations
- Add log file management
- Support meeting lifecycle (create → start → end)

**Benefits of Integration:**
- Data persistence across service restarts
- Centralized data management
- Consistent architecture across all services
- Meeting history and logging
- Better scalability and reliability
