# SAVING SERVER Documentation Package

## 📋 Overview

This package contains comprehensive documentation for the SAVING_SERVER team to implement the backend API that will integrate with our microservices architecture.

---

## 📦 Included Documents

### 1. **SAVING_SERVER_API_SPECIFICATION.md** (Main Document)
**Purpose:** Complete API specification with all endpoints, request/response formats, and business logic.

**Contents:**
- Overview and architecture
- Authentication & security requirements
- Detailed endpoint specifications:
  - User Management (POST /users/, GET /users/)
  - Invitation Codes (POST /invites/)
  - File Management (POST /file/upload, GET /file/get/{filename}, GET /file/getAll)
- Complete data models
- Error handling standards
- Integration flows
- Implementation notes
- Performance recommendations
- Testing guidelines

**Who should read this:** Backend developers implementing the SAVING_SERVER

---

### 2. **SAVING_SERVER_API_QUICK_REFERENCE.md**
**Purpose:** Quick reference guide for developers who need fast access to API details.

**Contents:**
- Endpoint summary table
- Quick examples (cURL commands)
- Database schema requirements
- Response format standards
- HTTP status codes
- Important notes

**Who should read this:** Developers during implementation, QA testers

---

### 3. **SAVING_SERVER_INTEGRATION_GUIDE.md**
**Purpose:** Visual guide showing how SAVING_SERVER integrates with all microservices.

**Contents:**
- System architecture diagram
- API usage by each microservice
- Authentication flow
- Complete data flow examples
- Error handling scenarios
- Security considerations
- Performance requirements
- Testing checklist
- Deployment checklist

**Who should read this:** System architects, DevOps, integration teams

---

## 🎯 Quick Start for SAVING_SERVER Team

### Step 1: Read the Specification
Start with `SAVING_SERVER_API_SPECIFICATION.md` to understand all requirements.

### Step 2: Review Integration Flows
Read `SAVING_SERVER_INTEGRATION_GUIDE.md` to see how your API will be used.

### Step 3: Implement Endpoints
Use `SAVING_SERVER_API_QUICK_REFERENCE.md` while coding for quick reference.

### Step 4: Test
Use the test examples and checklist provided in all documents.

---

## 🔑 Key Information

### Server Details
- **Address:** `192.168.148.94:5001`
- **Protocol:** HTTP (recommend HTTPS for production)
- **Authentication:** Internal API Key (`X-Internal-Key: INTERNAL_API_KEY`)

### Consuming Services
1. **authService** (Port 7051)
   - Uses: POST /users/
   - Purpose: User registration

2. **userServices** (Port 7052)
   - Uses: GET /users/, POST /invites/
   - Purpose: User lookup, invitation code management

3. **dataService** (Port 7055)
   - Uses: POST /file/upload, GET /file/get/{filename}, GET /file/getAll
   - Purpose: File operations

---

## 📊 API Endpoints Summary

| Method | Endpoint | Purpose | Priority |
|--------|----------|---------|----------|
| POST | `/users/` | Create user | HIGH |
| GET | `/users/` | Get all users | HIGH |
| POST | `/invites/` | Create invitation code | MEDIUM |
| POST | `/file/upload` | Upload file | HIGH |
| GET | `/file/get/{filename}` | Download file | HIGH |
| GET | `/file/getAll` | List all files | MEDIUM |
| GET | `/health` | Health check | LOW |

---

## 🗄️ Database Requirements

### Tables Needed
1. **users** - Store user information
2. **invites** - Store invitation codes
3. **files** - Store file metadata

### Key Fields
- Users: email (unique), userID (unique), role, department
- Invites: code (unique), manager_id, max_uses, expires_at
- Files: filename, uploaded_by, size, content_type

**See full schema in SAVING_SERVER_API_SPECIFICATION.md**

---

## 🔒 Security Requirements

1. **API Key Authentication:** All requests must include `X-Internal-Key` header
2. **Input Validation:** Validate all inputs before processing
3. **SQL Injection Prevention:** Use parameterized queries
4. **File Security:** Scan uploads for malware, validate file types
5. **HTTPS:** Use HTTPS in production

---

## ⚡ Performance Targets

- User endpoints: < 500ms response time
- File upload: < 2s (depends on size)
- File download: < 1s
- Support 100+ concurrent users
- Handle 10,000+ files

---

## ✅ Implementation Checklist

### Phase 1: Core Setup
- [ ] Set up database (PostgreSQL/MySQL/MongoDB)
- [ ] Create tables with proper schema
- [ ] Add indexes on key fields
- [ ] Set up file storage system
- [ ] Configure environment variables

### Phase 2: User Management
- [ ] Implement POST /users/ endpoint
- [ ] Implement GET /users/ endpoint
- [ ] Add validation for unique email/userID
- [ ] Test user creation and retrieval

### Phase 3: Invitation Codes
- [ ] Implement POST /invites/ endpoint
- [ ] Add code generation validation (8 chars)
- [ ] Implement expiration logic (7 days)
- [ ] Test code creation

### Phase 4: File Management
- [ ] Implement POST /file/upload endpoint
- [ ] Implement GET /file/get/{filename} endpoint
- [ ] Implement GET /file/getAll endpoint
- [ ] Add file type validation
- [ ] Add file size limits (10MB)
- [ ] Test file upload/download

### Phase 5: Security & Testing
- [ ] Implement API key authentication
- [ ] Add input validation
- [ ] Add error handling
- [ ] Test all endpoints with cURL
- [ ] Test error scenarios
- [ ] Load testing

### Phase 6: Production Readiness
- [ ] Set up logging
- [ ] Set up monitoring
- [ ] Configure rate limiting
- [ ] Set up backups
- [ ] Deploy to production
- [ ] Verify with integration tests

---

## 🧪 Testing

### Test with cURL Examples

**Create User:**
```bash
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
    "userID": "test_123",
    "date_of_birth": "1995-01-01"
  }'
```

**Get All Users:**
```bash
curl -X GET http://192.168.148.94:5001/users/ \
  -H "X-Internal-Key: INTERNAL_API_KEY"
```

**Upload File:**
```bash
curl -X POST http://192.168.148.94:5001/file/upload \
  -H "X-Internal-Key: INTERNAL_API_KEY" \
  -F "file=@test.pdf" \
  -F "user_email=test@example.com"
```

**More examples in SAVING_SERVER_API_QUICK_REFERENCE.md**

---

## 🐛 Common Issues & Solutions

### Issue: "Unauthorized" error
**Solution:** Ensure `X-Internal-Key` header is included with value `INTERNAL_API_KEY`

### Issue: Duplicate email/userID
**Solution:** Return 409 Conflict status with clear error message

### Issue: File upload fails
**Solution:** Check file size limits, validate content type, ensure storage directory exists

### Issue: GET /users/ returns wrong format
**Solution:** Ensure response has `{"data": [...]}` structure with lowercase role values

---

## 📞 Contact & Support

For questions about this specification:
- Review the three documentation files first
- Check the integration guide for flow diagrams
- Refer to test examples for implementation guidance

---

## 📝 Response Format Examples

### Success Response (User Creation)
```json
{
  "id": 1,
  "email": "user@example.com",
  "userID": "abc123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "EMPLOYER",
  "created_at": "2025-11-30T10:30:00Z"
}
```

### Success Response (Get All Users)
```json
{
  "data": [
    {
      "id": 1,
      "email": "user@example.com",
      "userID": "abc123",
      "first_name": "John",
      "last_name": "Doe",
      "role": "employee",
      "department": "Engineering",
      "address": "123 Main St",
      "date_of_birth": "1990-01-01",
      "employeesList": []
    }
  ]
}
```

### Error Response
```json
{
  "error": "Email already exists"
}
```

---

## 🚀 Next Steps

1. **SAVING_SERVER Team:**
   - Review all three documents
   - Set up development environment
   - Implement endpoints following specification
   - Test with provided examples
   - Deploy to staging environment
   - Notify integration team when ready

2. **Integration Team:**
   - Wait for SAVING_SERVER implementation
   - Test connectivity from microservices
   - Validate data flows
   - Perform end-to-end testing

3. **DevOps Team:**
   - Prepare production environment
   - Set up monitoring and logging
   - Configure backups
   - Plan deployment

---

## 📚 Document Versions

| Document | Version | Date | Status |
|----------|---------|------|--------|
| API Specification | 1.0 | 2025-11-30 | Final |
| Quick Reference | 1.0 | 2025-11-30 | Final |
| Integration Guide | 1.0 | 2025-11-30 | Final |

---

## ✨ Summary

This documentation package provides everything the SAVING_SERVER team needs to implement a fully compatible API for our microservices architecture. The three documents work together to provide:

- **Complete specifications** (API Specification)
- **Quick reference** (Quick Reference)
- **Integration context** (Integration Guide)

All documents include examples, test cases, and implementation guidance.

**Good luck with the implementation! 🎯**
