# Microservices Architecture Analysis
## Complete Project Documentation

**Generated:** November 29, 2025  
**Project:** CompanyPortal2-0 Server  
**Branch:** change_to_microServices

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Microservices Details](#microservices-details)
3. [API Endpoints Plan](#api-endpoints-plan)
4. [Service Dependencies & Relationships](#service-dependencies--relationships)
5. [Data Models](#data-models)
6. [Communication Patterns](#communication-patterns)
7. [Environment Variables](#environment-variables)
8. [Deployment Configuration](#deployment-configuration)

---

## Architecture Overview

This project implements a **microservices architecture** with the following services:

### Service Inventory
| Service | Technology | Port | Purpose |
|---------|-----------|------|---------|
| **Gateway** | Python/Flask | 7050 | API Gateway, WebSocket Proxy |
| **authService** | Python/Flask | 7051 | Authentication with Supabase |
| **userServices** | Python/Flask | 7052 | User management |
| **meetingService** | Python/Flask | 7053 | Video conferencing (WebRTC) |
| **GameService** | Node.js/Express | 3000 | Real-time multiplayer games |
| **SAVING_server** | External | N/A | Database/Persistence layer |

### Architecture Pattern
- **API Gateway Pattern**: Single entry point for all client requests
- **Service-to-Service Communication**: HTTP REST + WebSocket
- **Authentication**: JWT-based with Supabase
- **Real-time Communication**: Socket.IO for WebSocket connections
- **Data Storage**: External saving service (NEXUS/Database)

---

## Microservices Details

### 1. Gateway Service (Port 7050)

**File:** `Gateway/app.py`

#### Purpose
Acts as the central **API Gateway** and **WebSocket proxy** for all client communications.

#### Key Components

##### Variables & Configuration
```python
# Line 18-31: Environment Variables
AUTH_server = os.getenv('AUTH_SERVER')          # Authentication service URL
SAVING_server = os.getenv('SAVING_server')      # Database service URL
UserServices = os.getenv('UserServices_server') # User service URL
Game_server = os.getenv('Game_server')          # Game service URL
Meet_server = os.getenv('Meet_server')          # Meeting service URL
app.secret_key = 'your-super-secret-jwt-token...'  # JWT secret
```

##### WebSocket Management
```python
# Line 23-25: Connection Dictionaries
client_connections_game = {}      # {client_sid: backend_socketio_client}
client_connections_meeting = {}   # {client_sid: {'backend': client, 'user_email': email}}
```

#### Functions Analysis

##### `create_GameServer_connection(client_sid, namespace_instance)`
**Lines:** 41-70  
**Purpose:** Creates dedicated backend Socket.IO connection for each game client  
**Returns:** `socketio.Client` or `None`  
**Event Handlers:** matchCreated, matchJoined, gameState, error

##### `create_MeetServer_connection(client_sid, namespace_instance, user_email)`
**Lines:** 73-151  
**Purpose:** Creates dedicated backend connection for meeting client with SSL support  
**Parameters:**
- `client_sid`: Client session ID
- `user_email`: User's email for meeting authentication
**Returns:** `socketio.Client` or `None`  
**Event Handlers:** room-joined, new-peer, peer-disconnected, offer, answer, ice-candidate, error, room-full

##### GameNamespace Class
**Lines:** 156-220  
**Namespace:** `/game`  
**Methods:**
- `on_connect()`: Creates backend connection for new game client
- `on_disconnect()`: Cleans up backend connection
- `on_createMatch()`: Forwards match creation request
- `on_joinMatch(match_code)`: Forwards join request
- `on_makeMove(data)`: Forwards player move
- `on_restartGame(match_code)`: Forwards game restart

##### MeetingNamespace Class
**Lines:** 225-301  
**Namespace:** `/meeting`  
**Methods:**
- `on_connect()`: Creates backend connection with user email
- `on_disconnect()`: Cleans up backend connection
- `on_join(data)`: Forwards room join
- `on_leave(data)`: Forwards room leave
- `on_offer(data)`: Forwards WebRTC offer
- `on_answer(data)`: Forwards WebRTC answer
- `on_ice_candidate(data)`: Forwards ICE candidate

#### HTTP Endpoints

##### Health & Monitoring
```
GET /health          # Kubernetes readiness check (Lines 316-361)
GET /ready           # Simple readiness probe (Lines 364-367)
GET /live            # Liveness probe (Lines 370-373)
GET /metrics         # Prometheus metrics (Lines 376-382)
```

##### Authentication
```
POST /login          # User login (Lines 386-396)
POST /signup         # User registration (Lines 399-442)
```

**`/signup` Flow (Lines 399-442):**
1. Receives: email, FirstName, LastName, Password, DateOfBirth, Address, managercode
2. Calls `AUTH_server/signup` to create Supabase user
3. Calls `SAVING_server/users/` to persist user data
4. Returns: AuthToken

##### User Management
```
POST /getCodeForManager   # Generate manager invitation code (Lines 445-471)
```

##### Meeting Endpoints
```
POST /create-meet         # Create new meeting (Lines 475-485)
POST /join-meet          # Join existing meeting (Lines 488-512)
GET /room/<meet_id>/<user_email>  # Meeting room page (Lines 515-539)
```

---

### 2. authService (Port 7051)

**Files:** `authService/app.py`, `authService/Helper.py`, `authService/supaBase/supaBase.py`

#### Purpose
Handles user authentication using **Supabase** as the identity provider.

#### Variables & Configuration

**app.py (Lines 1-14):**
```python
authenter = dataBaseAuth(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
auth_helper = authHelper(authenter)
SAVING_server = os.getenv('SAVING_server')
```

#### API Endpoints

##### `/signup` (Lines 18-31)
**Method:** GET (should be POST)  
**Input:**
```json
{
  "email": "user@example.com",
  "Password": "securepassword"
}
```
**Process:**
1. Calls `auth_helper.CreateUser(email, Password)`
2. Returns JWT token and user ID from Supabase

**Output:**
```json
{
  "Token": "jwt_access_token",
  "id": "supabase_user_id"
}
```

##### `/login` (Lines 33-42)
**Method:** POST  
**Input:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```
**Output:**
```json
{
  "Token": "jwt_access_token"
}
```

#### Helper Classes

##### `authHelper` Class (Helper.py)

**`CreateUser(Email, password)` (Lines 7-21):**
- Calls Supabase `createUser()`
- Extracts session and user data
- Returns: `{"Token": access_token, "id": user_id}`

**`login(Email, password)` (Lines 24-37):**
- Calls Supabase `sign_in_with_password()`
- Returns: `{"Token": access_token, "id": user_id}`

##### `dataBaseAuth` Class (supaBase.py)

**Variables:**
```python
# Lines 8-13: Supabase client configuration
timeout = httpx.Timeout(100.0, connect=100.0)
http_client = httpx.Client(timeout=timeout)
self.supabase: Client = create_client(url, key, options)
```

**Methods:**

**`createUser(email, password)` (Lines 17-23):**
```python
self.supabase.auth.sign_up({
    "email": f"{email}",
    "password": f"{password}",
}).model_dump_json()
```

**`login(email, password)` (Lines 27-32):**
```python
self.supabase.auth.sign_in_with_password({
    "email": f"{email}",
    "password": f"{password}",
}).model_dump_json()
```

#### Dependencies (requirements.txt)
- Flask==3.0.0
- Flask-CORS==4.0.0
- python-dotenv==1.0.0
- requests==2.31.0
- supabase==2.3.4
- postgrest==0.13.2

---

### 3. userServices (Port 7052)

**Files:** `userServices/app.py`, `userServices/userHelper.py`, `userServices/modeles/user.py`

#### Purpose
Manages user data, roles, departments, and manager invitation codes.

#### Variables & Configuration

**app.py (Lines 10-16):**
```python
HEADERS = {"X-Internal-Key": "INTERNAL_API_KEY"}  # Internal service auth
SAVING_server = os.getenv('SAVING_server')
```

#### API Endpoints

##### `/users/by-email/<email>` (Lines 18-28)
**Method:** GET  
**Purpose:** Retrieve user by email  
**Returns:**
```json
{
  "Email": "user@example.com",
  "FirstName": "John",
  "LastName": "Doe",
  "ID": "uuid",
  "DateOfBirth": "1990-01-01",
  "Address": "123 Main St",
  "EmployeesList": [],
  "Role": "MANAGER",
  "Department": "IT"
}
```

##### `/getCodeForManager` (Lines 67-119)
**Method:** POST  
**Input:**
```json
{
  "current_user_email": "hr@company.com",
  "manager_email": "manager@company.com"
}
```
**Process:**
1. Verify current user exists and has MANAGER role
2. Verify target manager exists
3. Generate 8-character alphanumeric code
4. Save code to SAVING_server with manager_id
5. Return code

**Output:**
```json
{
  "code": "A3B7CX9Z"
}
```

#### Helper Classes

##### `userHelper` Class (userHelper.py)

**Variables:**
```python
# Line 18: Service URL
SAVING_SERVER_URL = os.getenv('SAVING_server', 'http://127.0.0.1:5001')
```

**Methods:**

**`getUserByEmail(email)` (Lines 20-32):**
- Calls `get_user_by_email_from_SavingServer()`
- Returns `User` object or `None`

**`get_user_by_email_from_SavingServer(email)` (Lines 34-59):**
- Fetches all users from `SAVING_server/users/`
- Searches for email match (case-insensitive)
- Converts to internal `User` object

**`_convert_role_from_server(server_role)` (Lines 61-68):**
- Maps server roles: "hr" → ROLE.HR, "manager" → ROLE.MANAGER, "employee" → ROLE.EMPLOYER

**`_convert_department_from_server(dept_str)` (Lines 70-76):**
- Converts string to Department enum

**`_convert_server_user_to_internal(user_data)` (Lines 78-101):**
- Builds User object from API response
- Maps all fields including role and department

#### Data Models

##### `User` Class (modeles/user.py)

**Constructor (Lines 11-21):**
```python
def __init__(self, Email=None, FirstName=None, LastName=None, ID=None, 
             DateOfBirth=None, Address=None, EmployeesList=None, 
             Department=None, Role=ROLE.GUEST)
```

**Properties:**
- `ID`: User unique identifier
- `FirstName`, `LastName`: User names
- `DateOfBirth`: Birth date
- `Email`: User email
- `Address`: Physical address
- `EmployeesList`: List of employees (for managers)
- `Department`: Department enum
- `Role`: ROLE enum

**Methods:**
- Getters/Setters for all properties (Lines 23-76)
- `to_dict()`: Serialize to JSON (Lines 78-90)
- `from_dict(data)`: Deserialize from JSON (Lines 92-106)

##### `ROLE` Enum (modeles/role.py)
```python
class ROLE(Enum):
    GUEST = "GUEST"
    MANAGER = "MANAGER"
    EMPLOYER = "EMPLOYER"
    HR = "HR"
    ADMIN = "ADMIN"
```

##### `Department` Enum (modeles/department.py)
```python
class Department(Enum):
    HR = "HR"
    IT = "IT"
    SALES = "SALES"
    MARKETING = "MARKETING"
```

---

### 4. meetingService (Port 7053)

**Files:** `meetingService/app.py`, `meetingService/Helper.py`, `meetingService/meeting.py`

#### Purpose
Provides **WebRTC-based video conferencing** with signaling server for peer-to-peer connections.

#### Variables & Configuration

**app.py (Lines 11-17):**
```python
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
rooms = {}  # {room_id: {user_sid: {'user_email': email, 'joined': True}}}
signalingServer = os.getenv("SIGNALING_SERVER")
```

#### HTTP Endpoints

##### `/create-meet` (Lines 20-61)
**Method:** POST  
**Input:**
```json
{
  "title": "Team Standup",
  "object": "Daily sync",
  "description": "Morning standup meeting",
  "invitedEmployeesList": ["user1@company.com", "user2@company.com"],
  "password": "meeting123"
}
```
**Process:**
1. Creates new `Meeting` object with UUID
2. Adds to `MeetHelper.meetings` list
3. Returns meeting details

**Output:**
```json
{
  "success": true,
  "meeting": {
    "id": "uuid-v4",
    "title": "Team Standup",
    "object": "Daily sync",
    "description": "Morning standup meeting",
    "invitationLink": "http://localhost:7053/room/uuid-v4",
    "createdAt": "2025-11-29 10:30:00",
    "invitedEmployees": ["user1@company.com", "user2@company.com"]
  }
}
```

##### `/join-meet` (Lines 63-75)
**Method:** POST  
**Input:**
```json
{
  "meet_id": "uuid-v4",
  "password": "meeting123",
  "user_email": "user1@company.com"
}
```
**Process:**
1. Verify password via `MeetHelper.verifyMeetingPassword()`
2. Add user to meeting via `MeetHelper.addUserToMeeting()`
3. Return redirect URL

**Output:**
```json
{
  "success": true,
  "redirectUrl": "https://192.168.100.183:7053/room/uuid-v4/user1@company.com"
}
```

##### `/room/<meet_id>/<user_email>` (Lines 77-89)
**Method:** GET  
**Purpose:** Serve video conference HTML page  
**Process:**
1. Verify meeting exists
2. Verify user is invited
3. Render `video.html` template

#### WebSocket Events

##### `connect` (Lines 92-94)
- Logs client connection with user_email parameter

##### `disconnect` (Lines 96-107)
- Removes user from all rooms
- Emits `peer-disconnected` to remaining peers
- Cleans up empty rooms

##### `join` (Lines 109-134)
**Data:**
```json
{
  "room": "meeting-uuid",
  "user_email": "user@company.com"
}
```
**Process:**
1. Create room if doesn't exist
2. Add user to room dictionary
3. Get list of existing peers
4. Emit `room-joined` with peer list
5. Notify others with `new-peer`

##### `leave` (Lines 136-152)
**Data:**
```json
{
  "room": "meeting-uuid"
}
```
**Process:**
1. Remove user from room
2. Emit `peer-disconnected` to others
3. Delete room if empty

##### `offer` (Lines 154-167)
**Data:**
```json
{
  "room": "meeting-uuid",
  "targetId": "peer-socket-id",
  "offer": { "sdp": "...", "type": "offer" },
  "user_email": "user@company.com"
}
```
**Purpose:** Forward WebRTC offer to specific peer

##### `answer` (Lines 169-182)
**Data:**
```json
{
  "room": "meeting-uuid",
  "targetId": "peer-socket-id",
  "answer": { "sdp": "...", "type": "answer" },
  "user_email": "user@company.com"
}
```
**Purpose:** Forward WebRTC answer to specific peer

##### `ice-candidate` (Lines 184-194)
**Data:**
```json
{
  "room": "meeting-uuid",
  "targetId": "peer-socket-id",
  "candidate": { "candidate": "...", "sdpMid": "...", "sdpMLineIndex": 0 }
}
```
**Purpose:** Forward ICE candidate for NAT traversal

#### Helper Classes

##### `MeetHelper` Class (Helper.py)

**Variables:**
```python
# Line 6: In-memory storage
__meetings: List[Meeting] = []
```

**Methods:**

**`addMeeting(meeting)` (Lines 8-10):**
- Appends meeting to list

**`getMeetings()` (Lines 12-14):**
- Returns all meetings

**`addUserToMeeting(meetingID, userEmail)` (Lines 16-23):**
- Finds meeting by ID
- Adds user to invited list if not present

**`verifyUserInMeeting(meetingID, userEmail)` (Lines 25-29):**
- Checks if user is in meeting's invited list

**`verifyMeetingPassword(meetingID, password)` (Lines 31-35):**
- Validates meeting password

**`getMeetingByID(meetingID)` (Lines 37-41):**
- Returns Meeting object or None

##### `Meeting` Class (meeting.py)

**Constructor (Lines 5-15):**
```python
def __init__(self, title="", obj="", description="", 
             invited_employees=None, password="")
```

**Properties:**
- `__ID`: UUID v4
- `__Title`: Meeting title
- `__Object`: Meeting subject
- `__InvitationLink`: Auto-generated URL
- `__LogPath`: Path to meeting logs
- `__Description`: Meeting description
- `__InvitedEmployeesList`: List of user emails
- `__CreatedAt`: Timestamp
- `__Password`: Meeting password

**Methods:** Getters and setters for all properties (Lines 17-69)

---

### 5. GameService (Port 3000)

**File:** `GameService/tic-tac-toe/server.js`

#### Purpose
Provides **real-time multiplayer Tic-Tac-Toe** game with Redis pub/sub for scalability.

#### Variables & Configuration

**Lines 1-21:**
```javascript
const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: { origin: "*", methods: ["GET", "POST"] }
});

const pubClient = createClient();  // Redis publisher
const subClient = createClient();  // Redis subscriber
const games = new Map();           // {matchCode: gameData}
```

#### Functions

##### `generateMatchCode()` (Lines 26-28)
**Purpose:** Generate 6-character random match code  
**Returns:** String like "A3BX7Z"

##### `createGame(matchCode)` (Lines 31-39)
**Purpose:** Initialize new game state  
**Returns:**
```javascript
{
  board: Array(9).fill(null),       // 3x3 grid
  xIsNext: true,                     // Turn tracker
  players: { X: null, O: null },     // Socket IDs
  spectators: [],                    // Observer socket IDs
  winner: null                       // Winner: 'X', 'O', or null
}
```

##### `calculateWinner(board)` (Lines 144-157)
**Purpose:** Check for winning condition  
**Algorithm:** Checks 8 possible lines (3 rows, 3 cols, 2 diagonals)  
**Returns:** 'X', 'O', or null

#### Redis Pub/Sub

**Lines 42-46:**
```javascript
await subClient.subscribe('game-updates', (message) => {
  const { matchCode, gameState } = JSON.parse(message);
  games.set(matchCode, gameState);
  io.to(matchCode).emit('gameState', gameState);
});
```

#### WebSocket Events

##### `connection` (Line 48)
- Logs client connection

##### `createMatch` (Lines 52-61)
**Process:**
1. Generate unique match code
2. Create new game state
3. Assign creator as Player X
4. Store in games Map
5. Join socket to room
6. Emit `matchCreated` with code and role
7. Emit initial `gameState`

##### `joinMatch` (Lines 64-90)
**Input:** `matchCode`  
**Process:**
1. Find game by code
2. Assign role: X (if empty), O (if X filled), or spectator
3. Join socket to room
4. Emit `matchJoined` with role
5. Broadcast updated `gameState`

##### `makeMove` (Lines 93-113)
**Input:**
```javascript
{
  matchCode: "A3BX7Z",
  index: 4  // 0-8 for board position
}
```
**Validation:**
1. Check player turn matches socket
2. Check cell is empty
3. Check game not finished

**Process:**
1. Update board
2. Toggle turn
3. Check for winner
4. Publish to Redis
5. Broadcast `gameState`

##### `restartGame` (Lines 116-128)
**Input:** `matchCode`  
**Validation:** Only players X or O can restart  
**Process:**
1. Reset board to empty
2. Reset turn to X
3. Clear winner
4. Broadcast new `gameState`

##### `disconnect` (Lines 130-142)
**Process:**
1. Remove socket from all game player slots
2. Remove from spectators
3. Broadcast updated `gameState`

#### Dependencies (package.json)
- express: ^4.18.2
- socket.io: ^4.6.0
- redis: ^4.6.0
- dotenv: ^17.2.3

---

## API Endpoints Plan

### Complete Endpoint Inventory

#### Gateway Service (https://localhost:7050)

**Health & Monitoring**
```
GET  /health    - Kubernetes readiness check with downstream services
GET  /ready     - Simple readiness probe
GET  /live      - Liveness probe
GET  /metrics   - Prometheus metrics
```

**Authentication (proxied to authService)**
```
POST /login     - User login
    Input:  { email, password }
    Output: { Token }

POST /signup    - User registration
    Input:  { email, FirstName, LastName, Password, DateOfBirth, Address, managercode? }
    Output: { AuthToken }
```

**User Management (proxied to userServices)**
```
POST /getCodeForManager   - Generate manager invitation code [JWT required]
    Input:  { managermail }
    Output: { code }
```

**Meeting (proxied to meetingService)**
```
POST /create-meet                 - Create new meeting
    Input:  { title, object, description, invitedEmployeesList, password }
    Output: { success, meeting: {...} }

POST /join-meet                   - Join meeting
    Input:  { meet_id, password, user_email }
    Output: { success, redirectUrl }

GET  /room/<meet_id>/<user_email> - Meeting room page
    Output: HTML page
```

**WebSocket Namespaces**
```
/game      - Game WebSocket proxy
    Events: createMatch, joinMatch, makeMove, restartGame
    
/meeting   - Meeting WebSocket proxy
    Events: join, leave, offer, answer, ice-candidate
```

#### authService (http://AUTH_SERVER:7051)

```
GET  /signup   - Create new user [Should be POST]
    Input:  { email, Password }
    Output: { Token, id }

POST /login    - Authenticate user
    Input:  { email, password }
    Output: { Token }
```

#### userServices (http://UserServices:7052)

```
GET  /users/by-email/<email>  - Get user by email
    Output: User object

POST /getCodeForManager       - Generate invitation code
    Input:  { current_user_email, manager_email }
    Output: { code }
```

#### meetingService (https://Meet_server:7053)

**HTTP Endpoints**
```
POST /create-meet                 - Create meeting
POST /join-meet                   - Join meeting
GET  /room/<meet_id>/<user_email> - Meeting room
```

**WebSocket Events**
```
connect                - Client connection
disconnect             - Client disconnection
join                   - Join room
leave                  - Leave room
offer                  - WebRTC offer
answer                 - WebRTC answer
ice-candidate          - ICE candidate
```

#### GameService (http://Game_server:3000)

**WebSocket Events**
```
connect                - Client connection
disconnect             - Client disconnection
createMatch            - Create new game
joinMatch              - Join game by code
makeMove               - Make game move
restartGame            - Restart game
```

#### External Services

**SAVING_server (Database/Persistence)**
```
GET  /users/                      - Get all users
POST /users/                      - Create user
    Headers: { X-Internal-Key: "INTERNAL_API_KEY" }
    
POST /invites/                    - Create invitation code
    Headers: { X-Internal-Key: "INTERNAL_API_KEY" }
    Input: { manager_id, code, max_uses }
```

---

## Service Dependencies & Relationships

### Dependency Graph

```
                                    ┌─────────────────┐
                                    │   Supabase      │
                                    │  (Auth Provider)│
                                    └────────▲────────┘
                                             │
                                             │ Auth calls
                                             │
┌──────────┐         ┌───────────────────────┴─────────────────────┐
│          │         │                                              │
│  Client  │◄───────►│            Gateway (Port 7050)               │
│  (Web)   │  HTTPS  │       ┌──────────────────────────┐          │
│          │  WSS    │       │ HTTP Routes              │          │
└──────────┘         │       │ - /login → authService   │          │
                     │       │ - /signup → authService  │          │
                     │       │ - /getCodeForManager     │          │
                     │       │ - /create-meet           │          │
                     │       │ - /join-meet             │          │
                     │       ├──────────────────────────┤          │
                     │       │ WebSocket Namespaces     │          │
                     │       │ - /game → GameService    │          │
                     │       │ - /meeting → meetingService│        │
                     │       └──────────────────────────┘          │
                     └───────────────────┬──────────────────────────┘
                                         │
                     ┌───────────────────┼──────────────────────────┐
                     │                   │                          │
                     ▼                   ▼                          ▼
          ┌──────────────────┐  ┌──────────────────┐    ┌──────────────────┐
          │  authService     │  │  userServices    │    │ meetingService   │
          │  (Port 7051)     │  │  (Port 7052)     │    │  (Port 7053)     │
          ├──────────────────┤  ├──────────────────┤    ├──────────────────┤
          │ - CreateUser     │  │ - getUserByEmail │    │ - createMeeting  │
          │ - login          │  │ - getCode        │    │ - joinMeeting    │
          └────────┬─────────┘  └────────┬─────────┘    │ - WebRTC Signal  │
                   │                     │               └──────────────────┘
                   │                     │
                   │              ┌──────▼──────────────┐
                   │              │   SAVING_server     │
                   └─────────────►│   (Database)        │
                                  ├─────────────────────┤
                                  │ - /users/           │
                                  │ - /invites/         │
                                  └─────────────────────┘

                                  ┌──────────────────┐
                                  │  GameService     │
                                  │  (Port 3000)     │
                     ┌───────────►├──────────────────┤
                     │            │ - WebSocket      │
           Gateway WSS            │ - Redis Pub/Sub  │
           /game namespace        └────────┬─────────┘
                                           │
                                           ▼
                                  ┌──────────────────┐
                                  │     Redis        │
                                  │  (game-updates)  │
                                  └──────────────────┘
```

### Service Communication Matrix

| From Service | To Service | Protocol | Purpose | Authentication |
|-------------|-----------|----------|---------|----------------|
| Client | Gateway | HTTPS/WSS | All requests | JWT (some endpoints) |
| Gateway | authService | HTTP | Login/Signup | None |
| Gateway | userServices | HTTP | User operations | JWT |
| Gateway | meetingService | HTTP/WSS | Meeting operations | User email |
| Gateway | GameService | WSS | Game operations | None |
| authService | Supabase | HTTPS | Authentication | API Key |
| userServices | SAVING_server | HTTP | Data persistence | X-Internal-Key |
| authService | SAVING_server | HTTP | User creation | X-Internal-Key |
| GameService | Redis | TCP | Game state sync | None |

### Data Flow Examples

#### 1. User Registration Flow
```
1. Client → Gateway: POST /signup
   { email, FirstName, LastName, Password, DateOfBirth, Address }

2. Gateway → authService: POST /signup
   { email, Password }

3. authService → Supabase: sign_up()
   Returns: { Token, id }

4. Gateway → SAVING_server: POST /users/
   Headers: { X-Internal-Key }
   Body: { email, first_name, last_name, userID, role, department, ... }

5. Gateway → Client: 200 OK
   { AuthToken }
```

#### 2. Create Meeting Flow
```
1. Client → Gateway: POST /create-meet
   { title, object, description, invitedEmployeesList, password }

2. Gateway → meetingService: POST /create-meet
   (same payload)

3. meetingService: Creates Meeting object
   - Generates UUID
   - Creates invitation link
   - Stores in memory (MeetHelper.meetings)

4. meetingService → Gateway: 201 Created
   { success, meeting: { id, title, invitationLink, ... } }

5. Gateway → Client: 201 Created
   (forwards response)
```

#### 3. WebSocket Game Flow
```
1. Client connects to Gateway: wss://gateway:7050/game

2. Gateway: Creates backend connection to GameService
   - Creates socketio.Client
   - Sets up event forwarding
   - Stores in client_connections_game[sid]

3. Client → Gateway: emit('createMatch')

4. Gateway → GameService: emit('createMatch')

5. GameService: 
   - Generates match code
   - Creates game state
   - Stores in games Map

6. GameService → Gateway: emit('matchCreated', {matchCode, role})

7. Gateway → Client: emit('matchCreated', {matchCode, role})

8. GameService → Gateway: emit('gameState', gameData)

9. Gateway → Client: emit('gameState', gameData)
```

#### 4. WebRTC Meeting Flow
```
1. User A connects: wss://gateway:7050/meeting?user_email=userA@co.com

2. User A → Gateway: emit('join', {room: 'meeting-id', user_email})

3. Gateway → meetingService: emit('join', ...)

4. meetingService:
   - Adds user to room
   - Gets list of existing peers

5. meetingService → User A: emit('room-joined', {peers: ['userB-sid']})

6. meetingService → User B: emit('new-peer', {peerId: 'userA-sid'})

7. User A → meetingService: emit('offer', {targetId: 'userB-sid', offer})

8. meetingService → User B: emit('offer', {peerId: 'userA-sid', offer})

9. User B → meetingService: emit('answer', {targetId: 'userA-sid', answer})

10. meetingService → User A: emit('answer', {peerId: 'userB-sid', answer})

11. Both users exchange ICE candidates through same pattern
```

### Service Dependencies Summary

#### Gateway Dependencies
- **authService**: User authentication
- **userServices**: User management
- **meetingService**: Video conferencing
- **GameService**: Real-time games
- **SAVING_server**: Indirect (through other services)

#### authService Dependencies
- **Supabase**: Identity provider
- **SAVING_server**: User data persistence (called by Gateway)

#### userServices Dependencies
- **SAVING_server**: All user data operations

#### meetingService Dependencies
- **None** (stores meetings in memory)
- **Note:** Should integrate with SAVING_server for persistence

#### GameService Dependencies
- **Redis**: Cross-instance game state synchronization

---

## Data Models

### User Model

**Source:** `userServices/modeles/user.py`

```python
{
  "ID": "string (UUID)",
  "Email": "string",
  "FirstName": "string",
  "LastName": "string",
  "DateOfBirth": "string (YYYY-MM-DD)",
  "Address": "string",
  "Role": "GUEST|MANAGER|EMPLOYER|HR|ADMIN",
  "Department": "HR|IT|SALES|MARKETING|null",
  "EmployeesList": ["user_id", ...]  // For managers
}
```

### Meeting Model

**Source:** `meetingService/meeting.py`

```python
{
  "ID": "string (UUID v4)",
  "Title": "string",
  "Object": "string",
  "Description": "string",
  "InvitationLink": "string (URL)",
  "LogPath": "string",
  "InvitedEmployeesList": ["email", ...],
  "CreatedAt": "string (YYYY-MM-DD HH:MM:SS)",
  "Password": "string"
}
```

### Game State Model

**Source:** `GameService/tic-tac-toe/server.js`

```javascript
{
  "board": [null|"X"|"O", ...],  // Array of 9
  "xIsNext": boolean,
  "players": {
    "X": "socket_id|null",
    "O": "socket_id|null"
  },
  "spectators": ["socket_id", ...],
  "winner": null|"X"|"O"
}
```

### Invitation Code Model

**Source:** Referenced in `userServices/app.py`

```python
{
  "manager_id": "string (user ID)",
  "code": "string (8 chars alphanumeric)",
  "max_uses": 1
}
```

---

## Communication Patterns

### 1. API Gateway Pattern
**Implementation:** Gateway service  
**Purpose:** Single entry point for all client requests  
**Benefits:**
- Centralized authentication
- Request routing
- Protocol translation (HTTP ↔ WebSocket)

### 2. Service-to-Service HTTP
**Usage:** Gateway → microservices  
**Pattern:** Synchronous request/response  
**Example:**
```python
response = requests.post(f'http://{AUTH_server}/login', json=data)
```

### 3. WebSocket Proxying
**Usage:** Gateway ↔ GameService, Gateway ↔ meetingService  
**Pattern:** Each client gets dedicated backend connection  
**Implementation:**
```python
backend = socketio.Client()
client_connections[client_sid] = backend
backend.emit('event', data)  # Forward to backend
gateway.emit('event', data, to=client_sid)  # Forward to client
```

### 4. Pub/Sub Pattern
**Usage:** GameService with Redis  
**Purpose:** Multi-instance game state synchronization  
**Implementation:**
```javascript
pubClient.publish('game-updates', JSON.stringify({matchCode, gameState}));
subClient.subscribe('game-updates', (message) => { ... });
```

### 5. Internal API Key Authentication
**Usage:** Gateway/Services → SAVING_server  
**Implementation:**
```python
HEADERS = {"X-Internal-Key": "INTERNAL_API_KEY"}
requests.post(url, json=data, headers=HEADERS)
```

### 6. WebRTC Signaling
**Usage:** meetingService  
**Pattern:** Server relays signaling messages between peers  
**Flow:** Client A → Server → Client B (offer/answer/ICE)

---

## Environment Variables

### Gateway (.env)
```bash
AUTH_SERVER=localhost:7051
SAVING_server=localhost:5001
UserServices_server=localhost:7052
Game_server=http://localhost:3000
Meet_server=https://192.168.100.190:7053
POD_NAME=gateway-pod-001        # Kubernetes pod name
POD_IP=10.0.0.1                 # Kubernetes pod IP
```

### authService (.env)
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SAVING_server=localhost:5001
```

### userServices (.env)
```bash
SAVING_server=http://127.0.0.1:5001
```

### meetingService (.env)
```bash
SIGNALING_SERVER=https://192.168.100.190:7053
```

### GameService (.env)
```bash
PORT=3000
REDIS_URL=redis://localhost:6379  # Inferred
```

---

## Deployment Configuration

### Kubernetes Resources

**File:** `k8s/gateway-pipeline.yaml`

This file contains the CI/CD pipeline configuration for deploying the Gateway service to Kubernetes.

### Docker Configuration

#### authService Dockerfile
**File:** `authService/Dockerfile`  
- Base image: Python
- Installs requirements.txt
- Exposes port 7051
- Runs Flask app

#### Gateway Dockerfile
**File:** `Gateway/Dockerfile`  
- Base image: Python
- Installs requirements.txt
- Exposes port 7050
- Runs Flask with SSL certificates

### SSL Certificates

**Location:** `meetingService/certifs/`
- `cert.pem`: SSL certificate
- `key.pem`: Private key

**Usage:**
- meetingService (port 7053): HTTPS/WSS
- Gateway (port 7050): HTTPS/WSS for meeting namespace

---

## Architecture Observations & Recommendations

### Strengths
1. ✅ **Clear separation of concerns** - Each service has single responsibility
2. ✅ **API Gateway pattern** - Centralized entry point
3. ✅ **WebSocket support** - Real-time communication for games and meetings
4. ✅ **External authentication** - Supabase for identity management
5. ✅ **Scalability consideration** - Redis pub/sub for GameService

### Issues & Recommendations

#### 1. Data Persistence
**Issue:** meetingService stores data in memory  
**Risk:** Data loss on service restart  
**Recommendation:** Integrate with SAVING_server for meeting persistence

#### 2. Authentication Inconsistency
**Issue:** Some endpoints lack JWT validation  
**Recommendation:**
- Add JWT to all protected endpoints
- Implement `@jwt_required()` decorator consistently

#### 3. HTTP Method Misuse
**Issue:** `authService/signup` uses GET instead of POST  
**Recommendation:** Change to POST method (Line 18 in authService/app.py)

#### 4. Hardcoded URLs
**Issue:** Hardcoded IPs in templates and responses  
**Example:** `https://192.168.100.183:7053`  
**Recommendation:** Use environment variables for all service URLs

#### 5. Error Handling
**Issue:** Inconsistent error responses  
**Recommendation:** Standardize error format:
```json
{
  "error": {
    "code": "AUTH_FAILED",
    "message": "Invalid credentials"
  }
}
```

#### 6. Service Discovery
**Issue:** Manual URL configuration  
**Recommendation:** Implement service discovery (Kubernetes DNS, Consul, etc.)

#### 7. Security
**Issue:** Internal API key in code  
**Recommendation:** 
- Use proper secrets management (Kubernetes Secrets, Vault)
- Implement mTLS for service-to-service communication

#### 8. Monitoring
**Issue:** Limited observability  
**Recommendation:**
- Add distributed tracing (OpenTelemetry)
- Enhance Prometheus metrics
- Implement structured logging

#### 9. Testing
**Issue:** No test files visible  
**Recommendation:** Add unit and integration tests for all services

#### 10. Documentation
**Issue:** No API documentation  
**Recommendation:** 
- Add OpenAPI/Swagger specs
- Generate API documentation

---

## Technology Stack Summary

### Backend Frameworks
- **Python Services:** Flask 3.0.0, Flask-SocketIO, Flask-CORS
- **Node.js Services:** Express 4.18.2, Socket.IO 4.6.0

### Real-time Communication
- **Socket.IO:** WebSocket implementation
- **WebRTC:** Peer-to-peer video/audio
- **Redis:** Pub/sub for game state

### Authentication & Security
- **Supabase:** Identity provider
- **Flask-JWT-Extended:** JWT handling
- **bcrypt:** Password hashing

### Infrastructure
- **Kubernetes:** Container orchestration
- **Docker:** Containerization
- **SSL/TLS:** Certificate-based encryption

### Data Storage
- **SAVING_server:** External database service
- **Redis:** In-memory data store
- **In-memory:** Temporary storage (meetingService, GameService)

---

## Port Allocation

| Port | Service | Protocol | Purpose |
|------|---------|----------|---------|
| 7050 | Gateway | HTTPS/WSS | API Gateway & WebSocket proxy |
| 7051 | authService | HTTP | Authentication |
| 7052 | userServices | HTTP | User management |
| 7053 | meetingService | HTTPS/WSS | Video conferencing |
| 3000 | GameService | WS | Real-time games |
| 5001 | SAVING_server | HTTP | Database (external) |
| 6379 | Redis | TCP | Pub/sub (inferred) |

---

## Conclusion

This microservices architecture implements a **company portal** with the following features:
- **User Authentication** (Supabase)
- **User Management** (roles, departments, manager codes)
- **Video Conferencing** (WebRTC)
- **Real-time Gaming** (Tic-Tac-Toe)

The system uses a **Gateway pattern** for client communication and **service-to-service HTTP** for internal requests. Real-time features leverage **WebSocket** connections proxied through the Gateway.

**Key architectural decisions:**
- Centralized authentication
- Stateless services (except meetingService)
- External database layer
- Redis for distributed game state

This analysis provides a complete view of the system's architecture, APIs, data models, and service relationships.
