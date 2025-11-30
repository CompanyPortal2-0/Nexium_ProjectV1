# Meeting Service - SAVING_SERVER Integration Guide

## Overview
This guide documents the complete integration of the Meeting Service with the SAVING_SERVER for persistent data storage.

---

## What Changed

### Before Integration
- **Storage**: In-memory list (`List[Meeting]`)
- **Data Persistence**: None (data lost on restart)
- **API Endpoints**: Basic create/join only
- **Logging**: Not implemented

### After Integration
- **Storage**: SAVING_SERVER PostgreSQL database
- **Data Persistence**: Full persistence across restarts
- **API Endpoints**: Complete CRUD + lifecycle management
- **Logging**: Meeting log files in SAVING_SERVER

---

## New Features

### 1. **Persistent Storage**
All meetings are now stored in SAVING_SERVER's PostgreSQL database with the following schema:

```sql
meetings (
  id SERIAL PRIMARY KEY,
  meeting_id UUID UNIQUE,
  title VARCHAR,
  object VARCHAR,
  description TEXT,
  invitation_link VARCHAR,
  log_path VARCHAR,
  invited_employees_list TEXT[],
  created_by VARCHAR,
  created_at TIMESTAMP,
  is_active BOOLEAN,
  started_at TIMESTAMP,
  ended_at TIMESTAMP,
  password VARCHAR
)
```

### 2. **Meeting Lifecycle Management**
- **Create** → Meeting is created in database
- **Start** → `started_at` timestamp recorded
- **Active** → WebRTC signaling, user joins/leaves logged
- **End** → `ended_at` timestamp recorded, duration calculated
- **Logs** → All events stored in log file

### 3. **Automatic Log File Generation**
Each meeting gets a log file in SAVING_SERVER:
- **Path**: `./storage/meeting_logs/meeting_{id}_{timestamp}.log`
- **Format**: Timestamped entries
- **Events Logged**:
  - Meeting creation
  - Meeting start/end
  - User joins/leaves
  - Custom events

### 4. **Enhanced Meeting Model**
New fields added to `Meeting` class:
```python
__DatabaseID: Optional[int]      # SAVING_SERVER database ID
__CreatedBy: str                 # Email of creator
__IsActive: bool                 # Active status
__StartedAt: Optional[str]       # Start timestamp
__EndedAt: Optional[str]         # End timestamp
```

---

## API Endpoints

### Legacy Endpoints (Updated)

#### 1. Create Meeting
```http
POST /create-meet
Content-Type: application/json

{
  "title": "Team Standup",
  "object": "Daily sync",
  "description": "Daily team standup meeting",
  "created_by": "manager@example.com",
  "password": "meeting123",
  "invitedEmployeesList": ["employee@example.com"]
}
```

**Response:**
```json
{
  "success": true,
  "meeting": {
    "id": 1,
    "meeting_id": "a1b2c3d4-...",
    "title": "Team Standup",
    "invitationLink": "http://localhost:7053/room/a1b2c3d4-...",
    "log_path": "./storage/meeting_logs/meeting_a1b2c3d4_20251130_120000.log",
    "created_by": "manager@example.com",
    "is_active": true
  }
}
```

#### 2. Join Meeting
```http
POST /join-meet
Content-Type: application/json

{
  "meet_id": "a1b2c3d4-...",
  "password": "meeting123",
  "user_email": "employee@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "redirectUrl": "https://192.168.100.183:7053/room/a1b2c3d4-.../employee@example.com"
}
```

---

### New CRUD Endpoints

#### 3. Get All Meetings
```http
GET /meetings?user_email=manager@example.com&is_active=true
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "meeting_id": "a1b2c3d4-...",
      "title": "Team Standup",
      "invitation_link": "http://localhost:7053/room/...",
      "created_by": "manager@example.com",
      "created_at": "2025-11-30 12:00:00",
      "is_active": true,
      "has_password": true
    }
  ]
}
```

#### 4. Get Meeting by ID
```http
GET /meetings/a1b2c3d4-...
```

**Response:**
```json
{
  "id": 1,
  "meeting_id": "a1b2c3d4-...",
  "title": "Team Standup",
  "object": "Daily sync",
  "description": "Daily team standup meeting",
  "log_path": "./storage/meeting_logs/...",
  "invited_employees_list": ["employee@example.com"],
  "created_by": "manager@example.com",
  "created_at": "2025-11-30 12:00:00",
  "is_active": true,
  "started_at": "2025-11-30 14:00:00",
  "ended_at": null
}
```

#### 5. Update Meeting
```http
PUT /meetings/a1b2c3d4-...
Content-Type: application/json

{
  "title": "Updated Title",
  "description": "New description",
  "invited_employees": ["new@example.com"]
}
```

#### 6. Delete Meeting
```http
DELETE /meetings/a1b2c3d4-...
```

**Response:**
```json
{
  "success": true,
  "message": "Meeting deleted successfully"
}
```

---

### Lifecycle Endpoints

#### 7. Start Meeting
```http
POST /meetings/a1b2c3d4-.../start
```

**Response:**
```json
{
  "success": true,
  "meeting_id": "a1b2c3d4-...",
  "message": "Meeting started"
}
```

**Effect:**
- Sets `started_at` timestamp
- Adds log entry: "Meeting started"

#### 8. End Meeting
```http
POST /meetings/a1b2c3d4-.../end
```

**Response:**
```json
{
  "success": true,
  "meeting_id": "a1b2c3d4-...",
  "message": "Meeting ended"
}
```

**Effect:**
- Sets `ended_at` timestamp
- Sets `is_active` to false
- Adds log entry: "Meeting ended"
- Calculates duration

---

### Logging Endpoints

#### 9. Add Log Entry
```http
POST /meetings/a1b2c3d4-.../log
Content-Type: application/json

{
  "log_entry": "Screen sharing started"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Log entry added"
}
```

#### 10. Get Meeting Log
```http
GET /meetings/a1b2c3d4-.../log
```

**Response:**
```json
{
  "meeting_id": "a1b2c3d4-...",
  "log_content": "Meeting Log: Team Standup\n[2025-11-30 14:00:00] Meeting started\n..."
}
```

---

## Helper Class Methods

### MeetHelper Class API

```python
# Create and manage meetings
MeetHelper.createMeeting(meeting: Meeting) -> Optional[Meeting]
MeetHelper.getMeetingByID(meeting_id: str) -> Optional[Meeting]
MeetHelper.getAllMeetings(user_email: str = None, is_active: bool = None) -> List[Meeting]
MeetHelper.updateMeeting(meeting_id: str, updates: dict) -> bool
MeetHelper.deleteMeeting(meeting_id: str) -> bool

# Lifecycle management
MeetHelper.startMeeting(meeting_id: str) -> bool
MeetHelper.endMeeting(meeting_id: str) -> bool

# User management
MeetHelper.addUserToMeeting(meeting_id: str, user_email: str) -> bool
MeetHelper.verifyUserInMeeting(meeting_id: str, user_email: str) -> bool
MeetHelper.verifyMeetingPassword(meeting_id: str, password: str) -> bool

# Logging
MeetHelper.addLogEntry(meeting_id: str, log_entry: str) -> bool
MeetHelper.getMeetingLog(meeting_id: str) -> Optional[str]
```

---

## Communication Pattern

### HTTP Request Pattern
All methods in `MeetHelper` follow this pattern:

```python
import requests

HEADERS = {"X-Internal-Key": "nexus-internal-secret-key-123"}
SAVING_SERVER = "192.168.148.94:5001"

response = requests.post(
    f"http://{SAVING_SERVER}/meetings/",
    json=data,
    headers=HEADERS
)

if response.status_code in [200, 201]:
    return response.json()
else:
    logger.error(f"Failed: {response.status_code}")
    return None
```

### Caching Strategy
- **Local Cache**: `Dict[str, Meeting]` for quick lookups
- **Cache Updates**: On create, update, delete operations
- **Cache Invalidation**: Automatic on updates/deletes
- **Fallback**: Always query SAVING_SERVER if not in cache

---

## Configuration

### Environment Variables (.env)
```bash
SAVING_SERVER=192.168.148.94:5001
SIGNALING_SERVER=https://192.168.100.190:7053
```

### Internal API Key
All services use the same internal key:
```python
X-Internal-Key: nexus-internal-secret-key-123
```

---

## Testing Guide

### 1. Test Meeting Creation

**Using curl:**
```bash
curl -X POST http://localhost:7053/create-meet \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Meeting",
    "object": "Testing",
    "description": "Integration test",
    "created_by": "test@example.com",
    "password": "test123",
    "invitedEmployeesList": ["user1@example.com", "user2@example.com"]
  }'
```

**Using Python:**
```python
import requests

response = requests.post(
    'http://localhost:7053/create-meet',
    json={
        "title": "Test Meeting",
        "object": "Testing",
        "description": "Integration test",
        "created_by": "test@example.com",
        "password": "test123",
        "invitedEmployeesList": ["user1@example.com"]
    }
)

meeting = response.json()
meeting_id = meeting['meeting']['meeting_id']
print(f"Meeting created: {meeting_id}")
```

### 2. Test Meeting Lifecycle

```python
# Start meeting
requests.post(f'http://localhost:7053/meetings/{meeting_id}/start')

# Add log entries
requests.post(
    f'http://localhost:7053/meetings/{meeting_id}/log',
    json={"log_entry": "User joined"}
)

# Get meeting status
response = requests.get(f'http://localhost:7053/meetings/{meeting_id}')
print(response.json())

# End meeting
requests.post(f'http://localhost:7053/meetings/{meeting_id}/end')

# Get log
log = requests.get(f'http://localhost:7053/meetings/{meeting_id}/log')
print(log.json()['log_content'])
```

### 3. Test Meeting Join

```python
response = requests.post(
    'http://localhost:7053/join-meet',
    json={
        "meet_id": meeting_id,
        "password": "test123",
        "user_email": "user1@example.com"
    }
)

redirect_url = response.json()['redirectUrl']
print(f"Join URL: {redirect_url}")
```

### 4. Verify Data in SAVING_SERVER

```bash
# Check if meeting exists in SAVING_SERVER
curl -H "X-Internal-Key: nexus-internal-secret-key-123" \
  http://192.168.148.94:5001/meetings/{meeting_id}
```

---

## Error Handling

### Common Errors

#### 1. SAVING_SERVER Unreachable
```python
Error: Failed to create meeting in SAVING_SERVER
Cause: SAVING_SERVER is down or URL is incorrect
Solution: Check SAVING_SERVER environment variable and network
```

#### 2. Invalid API Key
```python
Status: 401 Unauthorized
Cause: X-Internal-Key header is missing or incorrect
Solution: Check HEADERS in Helper.py
```

#### 3. Meeting Not Found
```python
Status: 404 Not Found
Cause: Meeting ID doesn't exist
Solution: Verify meeting_id is correct
```

### Error Response Format
```json
{
  "error": "Error message description",
  "details": "Additional error information"
}
```

---

## Migration from Old System

### For Existing Meetings
If you have meetings created before integration:
1. **Data Loss**: Old in-memory meetings are lost
2. **Fresh Start**: All new meetings will be persistent
3. **No Migration**: Old data cannot be recovered

### Backward Compatibility
✅ **All old endpoints still work**:
- `POST /create-meet`
- `POST /join-meet`
- `GET /room/<meet_id>/<user_email>`

✅ **SocketIO events unchanged**:
- `join`, `leave`, `offer`, `answer`, `ice-candidate`

---

## Monitoring and Logging

### Application Logs
```python
logger.info(f"Meeting created successfully: {meeting_id}")
logger.error(f"Failed to create meeting: {response.status_code}")
```

### Meeting Logs (in SAVING_SERVER)
```
Meeting Log: Team Standup
Meeting ID: a1b2c3d4-...
Created By: manager@example.com
Created At: 2025-11-30 12:00:00
================================================================================

[2025-11-30 14:00:00] Meeting started
[2025-11-30 14:05:00] User employee@example.com joined the room
[2025-11-30 14:30:00] Screen sharing started
[2025-11-30 14:35:00] User employee@example.com left the room
[2025-11-30 15:00:00] Meeting ended
Duration: 1:00:00
```

---

## Benefits of Integration

1. **Data Persistence**: Meetings survive service restarts
2. **Audit Trail**: Complete log of all meeting events
3. **Centralized Data**: All services use same database
4. **Scalability**: Can add more meeting service instances
5. **Consistency**: Follows same pattern as other services
6. **RESTful API**: Standard HTTP endpoints for integration
7. **Meeting History**: Query past meetings by user/date
8. **Better UX**: Users can see their meeting history

---

## Next Steps

### Recommended Enhancements
1. **Add authentication** to meeting endpoints (JWT)
2. **Implement pagination** for `GET /meetings`
3. **Add meeting search** by title/description
4. **Add meeting recording** integration
5. **Add calendar integration** (Google Calendar, Outlook)
6. **Add email notifications** for meeting invites
7. **Add meeting reminders**
8. **Add screen sharing logs**
9. **Add participant analytics** (who joined, duration)
10. **Add meeting templates**

### Gateway Integration
Update `Gateway/meetGateway.py` to route new endpoints:
```python
@app.route('/meetings/', methods=['GET', 'POST'])
@app.route('/meetings/<meeting_id>', methods=['GET', 'PUT', 'DELETE'])
@app.route('/meetings/<meeting_id>/start', methods=['POST'])
@app.route('/meetings/<meeting_id>/end', methods=['POST'])
@app.route('/meetings/<meeting_id>/log', methods=['GET', 'POST'])
```

---

## Summary

✅ **Completed**:
- Full SAVING_SERVER integration
- Persistent storage for meetings
- Complete CRUD API
- Meeting lifecycle management
- Automatic log file generation
- WebRTC event logging
- Backward compatibility maintained
- Caching for performance

📋 **File Changes**:
- `meeting.py` - Enhanced with new fields and methods
- `Helper.py` - Complete rewrite with SAVING_SERVER integration
- `app.py` - New endpoints and enhanced logging
- `.env` - SAVING_SERVER configuration

🔗 **Integration Pattern**:
Follows the exact same pattern as `authService`, `userServices`, and `dataService` for consistency across the microservices architecture.
