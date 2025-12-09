# 🚀 Server Tests - Quick Start Guide

## How to Run Tests

### Prerequisites
```bash
# Python 3.8+ required
python --version

# Install dependencies
pip install requests python-dotenv
```

### Environment Setup
Create `.env` file in the `server` directory:
```env
# Service URLs (for integration tests)
AUTH_SERVER=http://localhost:7051
SAVING_server=http://localhost:7052
GATEWAY_SERVER=http://localhost:7050

# Auth Service (for unit tests)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

---

## Running Tests

### Option 1: Run All Tests
```bash
cd server

# Run all test types
python tests/test_unit.py
python tests/test_integration.py
python tests/test_contract.py
```

### Option 2: Run Specific Test Type

#### Unit Tests (Fast - No Services Needed)
```bash
cd server
python tests/test_unit.py
```
**What it tests:** Module imports, environment variables, data models

#### Integration Tests (Requires Running Services)
```bash
cd server
python tests/test_integration.py
```
**What it tests:** Service communication, health checks, cross-service calls

#### Contract Tests (Fast - No Services Needed)
```bash
cd server
python tests/test_contract.py
```
**What it tests:** API contracts, data formats, request/response schemas

### Option 3: Run with Verbose Output
```bash
cd server

# Verbose unit tests
python tests/test_unit.py -v

# Verbose integration tests
python tests/test_integration.py -v

# Verbose contract tests
python tests/test_contract.py -v
```

### Option 4: Run Specific Test Class/Method
```bash
cd server

# Run specific test class
python -m unittest tests.test_unit.TestGatewayUnit

# Run specific test method
python -m unittest tests.test_unit.TestGatewayUnit.test_role_enum
```

---

## Test Results Interpretation

### ✅ SUCCESS Indicators
```
✅ authHelper imported successfully
✅ All required environment variables present
✅ Auth Service reachable: 200
✅ Auth Service signup contract verified
```

### ⚠️ SKIP Indicators (Expected)
```
⚠️ Missing env vars: ['SUPABASE_URL']
⚠️ Auth Service not reachable
skipped 'Auth Service not running'
```

### ❌ FAILURE Indicators
```
FAIL: test_method_name
AssertionError: Expected X but got Y
```

---

## Test Types Overview

### 🧪 Unit Tests (6 tests)
- **Purpose:** Test individual components in isolation
- **Duration:** ~0.6 seconds
- **Requirements:** None (runs without services)
- **Coverage:** Imports, environment, data models

### 🔗 Integration Tests (5 tests)
- **Purpose:** Test service communication
- **Duration:** ~4 seconds
- **Requirements:** Running services
- **Coverage:** Health checks, cross-service calls

### 📋 Contract Tests (10 tests)
- **Purpose:** Validate API contracts
- **Duration:** ~0.03 seconds
- **Requirements:** None
- **Coverage:** Request/response schemas, data formats

---

## Quick Commands

```bash
# Navigate to server directory
cd server

# Run all tests (fastest first)
python tests/test_contract.py    # 0.03s - No services needed
python tests/test_unit.py        # 0.6s  - No services needed
python tests/test_integration.py # 4s    - Requires services

# Check test results
echo "Tests completed! Check output above for ✅ success or ⚠️ skips"
```

---

## Troubleshooting

### Services Not Running (Integration Tests)
**Symptom:** Tests skip with "Service not running"
**Solution:** Start services or run unit/contract tests only

### Missing Environment Variables
**Symptom:** "Missing env vars" warnings
**Solution:** Create `.env` file with required variables

### Import Errors
**Symptom:** Module import failures
**Solution:** Check Python path or install missing packages

---

## CI/CD Integration

Tests automatically run in Jenkins pipeline defined in `Jenkinsfile`:
```groovy
stage('Run Tests') {
    steps {
        sh 'cd Server && python tests/test_unit.py'
        sh 'cd Server && python tests/test_integration.py'
        sh 'cd Server && python tests/test_contract.py'
    }
}
```

For detailed documentation, see `TESTS_DOCUMENTATION.md`