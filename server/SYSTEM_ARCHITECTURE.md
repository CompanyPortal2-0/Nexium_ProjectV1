# Complete System Architecture Diagram

## Full Microservices Architecture with SAVING_SERVER

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                                   CLIENT LAYER                                  │
│                         Web Browser / Mobile App / Desktop                      │
│                                                                                 │
│  Features:                                                                      │
│  • User Authentication (JWT)                                                    │
│  • File Upload/Download                                                         │
│  • User Management                                                              │
│  • Game Sessions (Tic-Tac-Toe)                                                  │
│  • Video Meetings (WebRTC)                                                      │
└────────────────────────────────┬───────────────────────────────────────────────┘
                                 │
                                 │ HTTPS + JWT Token
                                 │
┌────────────────────────────────▼───────────────────────────────────────────────┐
│                               GATEWAY LAYER                                     │
│                          (Request Routing & Auth)                               │
├─────────────────────────┬──────────────────────┬──────────────────────────────┤
│   filesGateway.py       │   app.py (main)      │   meetGateway.py             │
│   Port: 8000            │   SocketIO           │   Port: varies               │
│                         │   Namespaces:        │                              │
│   • JWT validation      │   • /game            │   • WebRTC signaling         │
│   • Extract user email  │   • /meeting         │   • Room management          │
│   • Route file requests │                      │                              │
└────────┬────────────────┴──────────┬───────────┴──────────────────────┬────────┘
         │                           │                                  │
         │                           │                                  │
┌────────▼────────────────────────┬──▼──────────────┬─────────────────▼────────┐
│      BUSINESS LOGIC LAYER       │                 │                           │
│      (Microservices)            │                 │                           │
├─────────────────────────────────┼─────────────────┼───────────────────────────┤
│                                 │                 │                           │
│  ┌─────────────────────────┐   │  ┌───────────┐  │  ┌────────────────────┐  │
│  │   authService           │   │  │  Game     │  │  │  meetingService    │  │
│  │   Port: 7051            │   │  │  Service  │  │  │  Port: 7053        │  │
│  │                         │   │  │           │  │  │                    │  │
│  │ • User signup           │   │  │ Node.js   │  │  │ • WebRTC           │  │
│  │ • User login            │   │  │ Port:     │  │  │ • MediaSoup        │  │
│  │ • JWT generation        │   │  │ 7054      │  │  │ • Room management  │  │
│  │ • Supabase auth         │   │  │           │  │  │                    │  │
│  └──────────┬──────────────┘   │  └───────────┘  │  └────────────────────┘  │
│             │                   │                 │                           │
│  ┌──────────▼──────────────┐   │                 │                           │
│  │   userServices          │   │                 │                           │
│  │   Port: 7052            │   │                 │                           │
│  │                         │   │                 │                           │
│  │ • User lookup           │   │                 │                           │
│  │ • Invitation codes      │   │                 │                           │
│  │ • User management       │   │                 │                           │
│  └──────────┬──────────────┘   │                 │                           │
│             │                   │                 │                           │
│  ┌──────────▼──────────────┐   │                 │                           │
│  │   dataService           │   │                 │                           │
│  │   Port: 7055            │   │                 │                           │
│  │                         │   │                 │                           │
│  │ • File operations       │   │                 │                           │
│  │ • File metadata         │   │                 │                           │
│  │ • Access control        │   │                 │                           │
│  └──────────┬──────────────┘   │                 │                           │
│             │                   │                 │                           │
└─────────────┼───────────────────┴─────────────────┴───────────────────────────┘
              │
              │ All services communicate via:
              │ Header: X-Internal-Key: INTERNAL_API_KEY
              │
┌─────────────▼───────────────────────────────────────────────────────────────────┐
│                            PERSISTENCE LAYER                                     │
│                      SAVING_SERVER (192.168.148.94:5001)                        │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────────┐  ┌────────────────────────┐  ┌────────────────────┐  │
│  │  User Management    │  │  Invitation Codes      │  │  File Management   │  │
│  ├─────────────────────┤  ├────────────────────────┤  ├────────────────────┤  │
│  │ POST /users/        │  │ POST /invites/         │  │ POST /file/upload  │  │
│  │ • Create user       │  │ • Create inv. code     │  │ • Upload file      │  │
│  │                     │  │ • Track usage          │  │ • Store metadata   │  │
│  │ GET /users/         │  │ • Set expiration       │  │                    │  │
│  │ • Get all users     │  │                        │  │ GET /file/get/{f}  │  │
│  │ • Filter by email   │  │                        │  │ • Download file    │  │
│  │                     │  │                        │  │                    │  │
│  │                     │  │                        │  │ GET /file/getAll   │  │
│  │                     │  │                        │  │ • List all files   │  │
│  └─────────────────────┘  └────────────────────────┘  └────────────────────┘  │
│                                                                                  │
├──────────────────────────────────────────────────────────────────────────────────┤
│                              DATABASE & STORAGE                                  │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                   │
│  │   users      │     │   invites    │     │   files      │                   │
│  │              │     │              │     │              │                   │
│  │ • id         │     │ • id         │     │ • id         │                   │
│  │ • email      │     │ • manager_id │     │ • file_id    │                   │
│  │ • userID     │     │ • code       │     │ • filename   │                   │
│  │ • first_name │     │ • max_uses   │     │ • size       │                   │
│  │ • last_name  │     │ • current_uses│    │ • uploaded_by│                   │
│  │ • role       │     │ • expires_at │     │ • uploaded_at│                   │
│  │ • department │     │ • is_active  │     │ • file_path  │                   │
│  │ • address    │     │              │     │              │                   │
│  └──────────────┘     └──────────────┘     └──────────────┘                   │
│                                                                                  │
│  File System: /path/to/file/storage/                                           │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘


┌────────────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SERVICES                                       │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  ┌──────────────────────┐                                                     │
│  │  Supabase Auth       │  ← Used by authService                             │
│  │                      │     for user authentication                         │
│  │ • User creation      │                                                     │
│  │ • Login/logout       │                                                     │
│  │ • JWT generation     │                                                     │
│  └──────────────────────┘                                                     │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Complete User Journey

### Flow 1: User Registration
```
1. Client submits signup form
   ↓
2. authService (7051)
   ↓
3. Create user in Supabase (external auth)
   ↓
4. POST to SAVING_SERVER /users/ (store user data)
   ↓
5. Return JWT token to client
```

### Flow 2: User Login
```
1. Client submits login credentials
   ↓
2. authService validates with Supabase
   ↓
3. Generate JWT token
   ↓
4. Return token to client
```

### Flow 3: Manager Creates Invitation Code
```
1. Client requests code (with JWT)
   ↓
2. filesGateway validates JWT, extracts user email
   ↓
3. userServices validates manager role
   ↓
4. GET /users/ from SAVING_SERVER to verify users
   ↓
5. Generate random 8-character code
   ↓
6. POST /invites/ to SAVING_SERVER
   ↓
7. Return code to client
```

### Flow 4: User Uploads File
```
1. Client uploads file (with JWT)
   ↓
2. filesGateway (8000)
   - Validates JWT
   - Extracts user email
   - Adds X-User-Email header
   ↓
3. dataService (7055)
   - Validates internal API key
   - Processes file
   ↓
4. POST /file/upload to SAVING_SERVER
   - Stores file on disk
   - Saves metadata in database
   ↓
5. Return success to client
```

### Flow 5: User Downloads File
```
1. Client requests file (with JWT)
   ↓
2. filesGateway validates JWT
   ↓
3. dataService receives request
   ↓
4. GET /file/get/{filename} from SAVING_SERVER
   ↓
5. Stream file to client
```

### Flow 6: User Joins Game
```
1. Client connects to Gateway via SocketIO (/game namespace)
   ↓
2. Gateway creates backend connection to Game Service
   ↓
3. Client creates or joins match
   ↓
4. Game Service manages game state
   ↓
5. Real-time updates via SocketIO
```

### Flow 7: User Joins Meeting
```
1. Client connects to meetGateway via SocketIO
   ↓
2. Gateway forwards to meetingService (7053)
   ↓
3. WebRTC signaling through MediaSoup
   ↓
4. Peer-to-peer video/audio connection established
```

---

## Port Allocation

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| authService | 7051 | HTTP | Authentication |
| userServices | 7052 | HTTP | User management |
| meetingService | 7053 | HTTPS/WSS | Video meetings |
| Game Service | 7054 | HTTP/WS | Game server |
| dataService | 7055 | HTTP | File operations |
| filesGateway | 8000 | HTTP | File gateway |
| Gateway (SocketIO) | varies | WS | Real-time communication |
| SAVING_SERVER | 5001 | HTTP | Persistence layer |

---

## Technology Stack

### Backend Services
- **Python Flask** - authService, userServices, dataService, Gateway
- **Node.js** - Game Service (Tic-Tac-Toe)
- **MediaSoup** - meetingService (WebRTC)

### Gateway
- **Flask-SocketIO** - Real-time WebSocket communication
- **Flask-CORS** - Cross-origin resource sharing
- **Flask-JWT-Extended** - JWT authentication

### Database & Storage
- **SAVING_SERVER** - Custom REST API for persistence
  - User database (SQL recommended)
  - File storage (filesystem or cloud)
  - Invitation codes database

### Authentication
- **Supabase** - External authentication provider
- **JWT** - Token-based authentication across services

---

## Security Architecture

### Layer 1: Client Authentication
```
Client → JWT Token → Gateway
```
- All client requests include JWT in Authorization header
- Gateway validates token
- Gateway extracts user identity (email)

### Layer 2: Internal Service Authentication
```
Gateway/Services → X-Internal-Key → SAVING_SERVER
```
- All internal service-to-service calls include internal API key
- Prevents external access to SAVING_SERVER
- Ensures only authorized services can access persistence layer

### Layer 3: User Context Propagation
```
Gateway extracts user email from JWT
    ↓
Passes via X-User-Email header to services
    ↓
Services track actions by user
```

---

## Deployment Architecture

### Development Environment
```
All services running on localhost
- authService: localhost:7051
- userServices: localhost:7052
- meetingService: localhost:7053
- Game Service: localhost:7054
- dataService: localhost:7055
- filesGateway: localhost:8000
- SAVING_SERVER: 192.168.148.94:5001
```

### Production Environment (Recommended)
```
Load Balancer
    ↓
Gateway Cluster (multiple instances)
    ↓
Service Mesh
    ├─ authService cluster
    ├─ userServices cluster
    ├─ dataService cluster
    ├─ Game Service cluster
    └─ meetingService cluster
    ↓
SAVING_SERVER (High Availability)
    ├─ Primary database
    ├─ Replica databases
    └─ Distributed file storage
```

---

## Scalability Considerations

### Horizontal Scaling
- All services are stateless (except SocketIO connections)
- Can run multiple instances behind load balancer
- SAVING_SERVER needs database replication for HA

### Vertical Scaling
- SAVING_SERVER may need more resources for file storage
- meetingService (MediaSoup) is CPU-intensive
- Game Service handles real-time connections

### Caching Strategy
- Cache GET /users/ responses in userServices
- Use Redis for session management
- CDN for static file delivery

---

## Monitoring & Logging

### Service Health
- All services should implement /health endpoint
- Monitor response times
- Track error rates

### SAVING_SERVER Metrics
- Database query performance
- File upload/download rates
- Storage usage
- API response times

### Business Metrics
- User registrations
- Active users
- File uploads/downloads
- Game sessions
- Meeting durations

---

## Disaster Recovery

### Backup Strategy
- **Database:** Daily backups of user, invites, files tables
- **Files:** Replicate to cloud storage (S3, Azure Blob)
- **Configuration:** Version control for all .env files

### Recovery Plan
1. Restore database from latest backup
2. Restore files from cloud storage
3. Redeploy services from Docker images
4. Verify connectivity between services

---

## Future Enhancements

### Planned Features
1. **Invitation Code Validation** - POST /invites/validate endpoint
2. **File Sharing** - Share files between users
3. **File Versioning** - Track file versions
4. **User Roles & Permissions** - Fine-grained access control
5. **Audit Logs** - Track all user actions
6. **API Rate Limiting** - Prevent abuse
7. **File Preview** - Generate thumbnails/previews

### Technical Improvements
1. **Service Discovery** - Consul or Eureka
2. **API Gateway** - Kong or Nginx
3. **Message Queue** - RabbitMQ for async processing
4. **Caching Layer** - Redis for performance
5. **Microservices Monitoring** - Prometheus + Grafana
6. **Distributed Tracing** - Jaeger or Zipkin

---

**This architecture provides a solid foundation for a scalable, secure, and maintainable microservices application! 🚀**
