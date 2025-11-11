# 🚀 Quick Start Guide

## Installation

### 1. Install Python Dependencies

Open PowerShell in the server directory and run:

```powershell
pip install -r requirements.txt
```

If you encounter any issues, install individually:

```powershell
pip install Flask==3.0.0
pip install python-dotenv==1.0.0
pip install flask-jwt-extended==4.6.0
pip install flask-socketio==5.3.5
pip install flask-cors==4.0.0
pip install python-socketio==5.10.0
pip install eventlet==0.33.3
pip install supabase==2.3.0
pip install httpx==0.25.2
```

### 2. Configure Environment

Make sure your `.env` file exists with:

```env
SUPABASE_URL="http://localhost:8000"
SUPABASE_KEY="your-supabase-anon-key"
```

### 3. Run the Server

```powershell
python app.py
```

You should see:
```
Starting Flask-SocketIO server on port 6021...
 * Running on http://0.0.0.0:6021
```

---

## Testing the Integration

### Test 1: Create a Manager Account

```powershell
# Using curl (or Postman)
curl -X POST http://localhost:6021/signup `
  -H "Content-Type: application/json" `
  -d '{
    "email": "manager@test.com",
    "FirstName": "Test",
    "LastName": "Manager",
    "Password": "password123",
    "DateOfBirth": "1990-01-01",
    "Address": "123 Test St"
  }'
```

Save the `accessToken` from the response.

### Test 2: Create a Meeting

```powershell
curl -X POST http://localhost:6021/manager/createMeeting `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer YOUR_TOKEN_HERE" `
  -d '{
    "title": "Team Meeting",
    "object": "Weekly Standup",
    "description": "Test meeting"
  }'
```

Save the `meetingID` from the response (e.g., "A7K9M2P4").

### Test 3: Join the Meeting

1. Open browser: `http://localhost:6021/meeting/A7K9M2P4`
2. Enter your email and name when prompted
3. Allow camera/microphone access
4. You should see yourself in the video!

### Test 4: Join from Another Device/Browser

1. Open another browser tab or use a different device
2. Go to: `http://localhost:6021/meeting/A7K9M2P4`
3. Enter different email/name
4. You should now see both video streams!

---

## Common Issues & Solutions

### Issue: Module 'flask_cors' not found
**Solution:**
```powershell
pip install flask-cors
```

### Issue: Port 6021 already in use
**Solution:** Kill the process or change the port in `app.py`:
```python
socketio.run(app, host='0.0.0.0', port=6022, debug=False)
```

### Issue: Camera not working
**Solution:** 
- Use HTTPS or localhost
- Check browser permissions
- Try Chrome/Edge (best WebRTC support)

### Issue: Can't connect to Supabase
**Solution:** 
- Ensure Docker Supabase is running
- Check `.env` file has correct URL/KEY
- Verify URL is accessible

---

## What Was Integrated?

### ✅ Added to `app.py`:
- Flask-SocketIO initialization
- CORS support
- WebSocket signaling handlers:
  - `connect`, `disconnect`
  - `join`, `leave`
  - `offer`, `answer`, `ice-candidate`
- Meeting room routes:
  - `/meeting/<meeting_id>` - Meeting room interface
  - `/meetfiles/<filename>` - Static file serving
  - `/api/meeting/<id>/details` - Meeting details API
  - `/api/my-meetings` - User's meetings API

### ✅ Enhanced `meetHelper.py`:
- `get_meeting(meeting_id)` - Retrieve meeting
- `get_user_meetings(user_email)` - Get user's meetings
- `is_user_in_meeting(user_email, meeting_id)` - Authorization check
- `delete_meeting(meeting_id, user_email)` - Delete meeting

### ✅ Created New Files:
- `meetfiles/index.html` - Modern meeting interface (updated)
- `meetfiles/webrtc_new.js` - WebRTC client using Socket.IO
- `requirements.txt` - All Python dependencies
- `INTEGRATION_GUIDE.md` - Complete documentation

### ✅ Features Working:
- Multi-peer video conferencing
- Real-time audio/video
- Toggle video/audio controls
- Participant tracking
- WebRTC peer-to-peer connections
- Automatic reconnection
- Meeting management APIs

---

## Architecture Overview

```
User Browser
    ↓
    ├─ HTTPS → Flask Routes (API calls)
    │   ├─ /signup, /login
    │   ├─ /manager/createMeeting
    │   ├─ /joinMeeting
    │   └─ /api/my-meetings
    │
    └─ WebSocket → Flask-SocketIO (Signaling)
        ├─ join room
        ├─ WebRTC offer/answer/ICE
        └─ peer notifications
            ↓
        WebRTC P2P (Direct video/audio)
```

---

## Next Steps

1. **✅ Install dependencies** - `pip install -r requirements.txt`
2. **✅ Run the server** - `python app.py`
3. **✅ Test meeting creation** - Use Postman or curl
4. **✅ Join meeting** - Open in browser
5. **✅ Test multi-peer** - Join from multiple devices

---

## Production Deployment Checklist

Before deploying to production:

- [ ] Change `JWT_SECRET_KEY` in app.py
- [ ] Change `app.secret_key` in app.py
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure production TURN servers
- [ ] Set up proper logging
- [ ] Add rate limiting
- [ ] Configure database (move from JSON to PostgreSQL)
- [ ] Set up monitoring/analytics
- [ ] Test with 10+ concurrent users

---

**🎉 Your meeting system is ready to use!**

Need help? Check `INTEGRATION_GUIDE.md` for detailed documentation.
