# Meeting Service API Quick Reference

## Base URL
```
http://localhost:7053
```

## Authentication
Internal services use header:
```
X-Internal-Key: nexus-internal-secret-key-123
```

---

## 📋 Quick API Reference

### Create Meeting
```http
POST /create-meet

{
  "title": "Meeting Title",
  "object": "Meeting Purpose",
  "description": "Meeting Description",
  "created_by": "manager@example.com",
  "password": "secret123",
  "invitedEmployeesList": ["user1@example.com", "user2@example.com"]
}

→ Returns: meeting object with meeting_id
```

### Join Meeting
```http
POST /join-meet

{
  "meet_id": "uuid-here",
  "password": "secret123",
  "user_email": "user@example.com"
}

→ Returns: redirectUrl to meeting room
```

### List Meetings
```http
GET /meetings?user_email=user@example.com&is_active=true

→ Returns: array of meetings
```

### Get Meeting Details
```http
GET /meetings/{meeting_id}

→ Returns: full meeting object
```

### Update Meeting
```http
PUT /meetings/{meeting_id}

{
  "title": "New Title",
  "description": "New Description"
}

→ Returns: success message
```

### Delete Meeting
```http
DELETE /meetings/{meeting_id}

→ Returns: success message
```

### Start Meeting
```http
POST /meetings/{meeting_id}/start

→ Sets started_at timestamp
→ Logs "Meeting started"
```

### End Meeting
```http
POST /meetings/{meeting_id}/end

→ Sets ended_at timestamp
→ Sets is_active = false
→ Logs "Meeting ended"
```

### Add Log Entry
```http
POST /meetings/{meeting_id}/log

{
  "log_entry": "Custom log message"
}

→ Appends to meeting log file
```

### Get Meeting Log
```http
GET /meetings/{meeting_id}/log

→ Returns: log file content
```

---

## 🐍 Python Helper Methods

```python
from Helper import MeetHelper

# Create meeting
meeting = Meeting(title="Test", obj="Testing", ...)
created = MeetHelper.createMeeting(meeting)

# Get meeting
meeting = MeetHelper.getMeetingByID("meeting-uuid")

# Get all meetings
meetings = MeetHelper.getAllMeetings()
meetings = MeetHelper.getAllMeetings(user_email="user@example.com")
meetings = MeetHelper.getAllMeetings(is_active=True)

# Update meeting
MeetHelper.updateMeeting("meeting-uuid", {"title": "New Title"})

# Delete meeting
MeetHelper.deleteMeeting("meeting-uuid")

# Start/End meeting
MeetHelper.startMeeting("meeting-uuid")
MeetHelper.endMeeting("meeting-uuid")

# User management
MeetHelper.addUserToMeeting("meeting-uuid", "user@example.com")
MeetHelper.verifyUserInMeeting("meeting-uuid", "user@example.com")
MeetHelper.verifyMeetingPassword("meeting-uuid", "password123")

# Logging
MeetHelper.addLogEntry("meeting-uuid", "Custom log message")
log = MeetHelper.getMeetingLog("meeting-uuid")
```

---

## 🔌 WebSocket Events (SocketIO)

### Client → Server

```javascript
// Join room
socket.emit('join', {
  room: 'meeting-uuid',
  user_email: 'user@example.com'
});

// Leave room
socket.emit('leave', {
  room: 'meeting-uuid'
});

// Send offer
socket.emit('offer', {
  room: 'meeting-uuid',
  targetId: 'peer-socket-id',
  offer: sdpOffer,
  user_email: 'user@example.com'
});

// Send answer
socket.emit('answer', {
  room: 'meeting-uuid',
  targetId: 'peer-socket-id',
  answer: sdpAnswer,
  user_email: 'user@example.com'
});

// Send ICE candidate
socket.emit('ice-candidate', {
  room: 'meeting-uuid',
  targetId: 'peer-socket-id',
  candidate: iceCandidate
});
```

### Server → Client

```javascript
// Room joined confirmation
socket.on('room-joined', (data) => {
  // data: { room, peers, peerInfo }
});

// New peer joined
socket.on('new-peer', (data) => {
  // data: { peerId, user_email }
});

// Peer disconnected
socket.on('peer-disconnected', (data) => {
  // data: { peerId }
});

// Receive offer
socket.on('offer', (data) => {
  // data: { peerId, offer, user_email }
});

// Receive answer
socket.on('answer', (data) => {
  // data: { peerId, answer, user_email }
});

// Receive ICE candidate
socket.on('ice-candidate', (data) => {
  // data: { peerId, candidate }
});
```

---

## 📦 Meeting Object Structure

```python
{
  "id": 1,                                    # Database ID
  "meeting_id": "uuid",                       # Meeting UUID
  "title": "Meeting Title",
  "object": "Meeting Purpose",
  "description": "Meeting Description",
  "invitation_link": "http://...",
  "log_path": "./storage/meeting_logs/...",
  "invited_employees_list": ["email1", "email2"],
  "created_by": "creator@example.com",
  "created_at": "2025-11-30 12:00:00",
  "is_active": true,
  "started_at": "2025-11-30 14:00:00",        # null if not started
  "ended_at": null,                           # null if not ended
  "password": "secret123",
  "has_password": true
}
```

---

## 🧪 Testing with curl

```bash
# Create meeting
curl -X POST http://localhost:7053/create-meet \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","object":"Test","description":"Test","created_by":"test@test.com","password":"123"}'

# Get all meetings
curl http://localhost:7053/meetings

# Get specific meeting
curl http://localhost:7053/meetings/{meeting_id}

# Start meeting
curl -X POST http://localhost:7053/meetings/{meeting_id}/start

# Add log
curl -X POST http://localhost:7053/meetings/{meeting_id}/log \
  -H "Content-Type: application/json" \
  -d '{"log_entry":"Test log"}'

# Get log
curl http://localhost:7053/meetings/{meeting_id}/log

# End meeting
curl -X POST http://localhost:7053/meetings/{meeting_id}/end
```

---

## 🔧 Configuration

### Environment Variables (.env)
```bash
SAVING_SERVER=192.168.148.94:5001
SIGNALING_SERVER=https://192.168.100.190:7053
```

### Internal API Key
```python
HEADERS = {"X-Internal-Key": "nexus-internal-secret-key-123"}
```

---

## 📊 Meeting Lifecycle

```
CREATE → ACTIVE → START → [USERS JOIN/LEAVE] → END → INACTIVE
   ↓        ↓       ↓              ↓              ↓        ↓
  Save    Log    Log            Log            Log    Save
   DB     File   File           File           File    DB
```

---

## 🎯 Common Use Cases

### 1. Schedule Meeting
```python
meeting = Meeting(
    title="Team Standup",
    obj="Daily sync",
    description="Daily standup",
    created_by="manager@company.com",
    password="secret123",
    invited_employees=["dev1@company.com", "dev2@company.com"]
)
created = MeetHelper.createMeeting(meeting)
print(f"Meeting ID: {created.getID()}")
print(f"Invite link: {created.getInvitationLink()}")
```

### 2. Get My Meetings
```python
my_meetings = MeetHelper.getAllMeetings(
    user_email="user@company.com",
    is_active=True
)
for meeting in my_meetings:
    print(f"{meeting.getTitle()} - {meeting.getCreatedAt()}")
```

### 3. Run Meeting Lifecycle
```python
# Start
MeetHelper.startMeeting(meeting_id)

# During meeting
MeetHelper.addLogEntry(meeting_id, "Screen sharing started")
MeetHelper.addLogEntry(meeting_id, "User presented slides")

# End
MeetHelper.endMeeting(meeting_id)

# Review
log = MeetHelper.getMeetingLog(meeting_id)
print(log)
```

---

## ❗ Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (missing fields) |
| 401 | Unauthorized (wrong password) |
| 403 | Forbidden (not invited) |
| 404 | Not Found (meeting doesn't exist) |
| 500 | Server Error (SAVING_SERVER issue) |

---

## 🐛 Troubleshooting

### Meeting Not Found
- Check meeting_id is correct UUID
- Verify meeting exists in SAVING_SERVER
- Check SAVING_SERVER is running

### Cannot Create Meeting
- Verify SAVING_SERVER URL in .env
- Check SAVING_SERVER is reachable
- Verify internal API key is correct
- Check all required fields are provided

### Cannot Join Meeting
- Verify password is correct
- Check meeting is active
- Ensure user is invited

---

## 📖 More Information

- Full API documentation: `INTEGRATION_GUIDE.md`
- Architecture analysis: `ARCHITECTURE_ANALYSIS.md`
- SAVING_SERVER API: `MEETINGS_API.md`
