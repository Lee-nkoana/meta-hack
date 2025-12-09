# Testing Guide for Medical Records Bridge API

## Overview

This guide covers all testing tools and methods available for the Medical Records Bridge API.

## Test Suite

### Installation

Install test dependencies:

```bash
pip install -r requirements-test.txt
```

### Running Tests

Run all tests:

```bash
pytest
```

Run tests with verbose output:

```bash
pytest -v
```

Run specific test categories:

```bash
# Authentication tests only
pytest -m auth

# Medical records tests only
pytest -m records

# AI service tests only
pytest -m ai

# User profile tests only
pytest -m users
```

Run specific test file:

```bash
pytest tests/test_auth.py
pytest tests/test_medical_records.py
pytest tests/test_users.py
pytest tests/test_ai.py
```

Run a specific test:

```bash
pytest tests/test_auth.py::TestUserRegistration::test_register_new_user
```

### Test Coverage

The test suite includes 50+ comprehensive tests covering:

#### Authentication Tests (test_auth.py)
- User registration with valid data
- Registration with duplicate username/email
- Registration with invalid email format
- Registration with short password/username
- Registration with missing fields
- Successful login
- Login with wrong password
- Login with non-existent user
- Login with missing credentials
- Getting current authenticated user
- Authentication without token
- Authentication with invalid token

#### Medical Records Tests (test_medical_records.py)
- Creating medical records successfully
- Creating records without authentication
- Creating records with missing fields
- Listing records (empty and with data)
- Listing records without authentication
- Pagination of record lists
- Getting specific medical record
- Getting non-existent record
- Updating record title
- Updating record text (clears AI cache)
- Updating non-existent record
- Deleting medical records
- Deleting non-existent record

#### User Profile Tests (test_users.py)
- Getting user profile
- Getting profile with record counts
- Updating email
- Updating full name
- Updating password
- Updating with duplicate email
- Dashboard with no records
- Dashboard with multiple records
- Dashboard with AI translations
- Profile operations without authentication

#### AI Service Tests (test_ai.py)
- Translating medical text
- Getting lifestyle suggestions
- Explaining medical records
- Using cached AI responses
- Force refreshing cached responses
- AI service unavailable (no API key)
- AI operations without authentication

### Test Database

Tests use an isolated SQLite database (`test.db`) that is:
- Created fresh for each test function
- Automatically cleaned up after each test
- Completely separate from the development database

### Test Fixtures

Available fixtures for testing:

- `client` - FastAPI test client
- `db_session` - Database session for direct DB operations
- `test_user_data` - Sample user registration data
- `test_user` - Pre-created user in database
- `auth_headers` - Authentication headers with valid JWT token
- `test_medical_record_data` - Sample medical record data
- `test_medical_record` - Pre-created medical record
- `multiple_medical_records` - 5 pre-created records for list testing

## Interactive API Demo

### Running the Demo

The interactive demo script shows all API endpoints with real requests and responses:

```bash
python demo_api.py
```

Or specify a custom API URL:

```bash
python demo_api.py http://your-server:8000
```

### Demo Features

The demo script:
- Shows colored, formatted output for easy reading
- Displays both request and response for each API call
- Walks through complete user workflow:
  1. Health check
  2. User registration
  3. User login (saves token)
  4. Get current user info
  5. Create medical record
  6. List medical records
  7. Get specific record
  8. Update record
  9. AI translation (if configured)
  10. AI suggestions (if configured)
  11. User profile
  12. Dashboard statistics
  13. Update profile
  14. Delete record

### Demo Output Example

```
================================================================================
                     Medical Records Bridge API - Interactive Demo
================================================================================

1. Health Check
---------------
REQUEST:
  GET /health
  
RESPONSE:
  Status: 200
  Body:
    {"status": "healthy"}
```

## Postman Collection

### Importing the Collection

1. Open Postman
2. Click "Import"
3. Select `Medical_Records_Bridge_API.postman_collection.json`
4. Collection will be imported with all endpoints

### Using the Collection

The collection includes:
- All API endpoints organized by category
- Example request bodies
- Automatic token management (JWT saved to environment)
- Environment variables for base URL and IDs

#### Setting up Environment

Create a Postman environment with:

```
base_url = http://localhost:8000
```

The collection will automatically save:
- `access_token` - JWT token after login
- `user_id` - User ID after registration
- `record_id` - Record ID after creation

#### Collection Structure

1. Health & Status
   - Health Check
   - API Root

2. Authentication
   - Register User (saves user_id)
   - Login (saves access_token)
   - Get Current User

3. Medical Records
   - Create Medical Record (saves record_id)
   - List Medical Records
   - Get Medical Record
   - Update Medical Record
   - Delete Medical Record

4. AI Services
   - Translate Medical Text
   - Get Lifestyle Suggestions
   - Explain Medical Record

5. User Profile
   - Get User Profile
   - Update User Profile
   - Get Dashboard Statistics

### Workflow Testing with Postman

Recommended testing workflow:

1. Run "Register User" to create account
2. Run "Login" to get authentication token
3. Token is automatically saved and used for all subsequent requests
4. Test medical records CRUD operations
5. Test AI services (requires API key configuration)
6. Test user profile management

## Manual Testing with cURL

### Authentication Flow

Register:
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpass123",
    "full_name": "Test User"
  }'
```

Login:
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass123"
```

Save the token from the response, then use it:

```bash
TOKEN="your-token-here"
```

### Medical Records with cURL

Create record:
```bash
curl -X POST "http://localhost:8000/api/records" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Blood Test Results",
    "original_text": "WBC: 7.5, RBC: 4.8, HGB: 14.2",
    "record_type": "lab_result"
  }'
```

List records:
```bash
curl -X GET "http://localhost:8000/api/records" \
  -H "Authorization: Bearer $TOKEN"
```

Get specific record:
```bash
curl -X GET "http://localhost:8000/api/records/1" \
  -H "Authorization: Bearer $TOKEN"
```

Update record:
```bash
curl -X PUT "http://localhost:8000/api/records/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'
```

Delete record:
```bash
curl -X DELETE "http://localhost:8000/api/records/1" \
  -H "Authorization: Bearer $TOKEN"
```

## Interactive API Documentation

FastAPI provides automatic interactive documentation:

### Swagger UI

Visit: http://localhost:8000/docs

Features:
- Try out all endpoints directly in the browser
- See request/response schemas
- View response codes
- Test authentication by clicking "Authorize"

Using Swagger UI:
1. Click "Authorize" button at top
2. Login first to get token
3. Enter token in format: paste token value only
4. Click "Authorize"
5. All subsequent requests will include the token

### ReDoc

Visit: http://localhost:8000/redoc

Features:
- Clean, readable API documentation
- Detailed schema information
- Response examples
- Perfect for sharing with team

## Testing Best Practices

1. Run tests before committing changes
2. Add new tests for new features
3. Test both success and failure cases
4. Use fixtures to avoid code duplication
5. Mock external services (like AI API)
6. Keep tests isolated and independent
7. Use descriptive test names
8. Test edge cases and validation

## Continuous Integration

### GitHub Actions Example

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    - name: Run tests
      run: pytest -v
```

## Troubleshooting Tests

### Tests failing with import errors
```bash
# Make sure you're in the backend directory
cd backend

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### Tests failing with database errors
```bash
# Delete test database
rm test.db

# Run tests again
pytest
```

### Demo script connection errors
```bash
# Make sure API server is running
uvicorn app.main:app --reload

# In another terminal, run demo
python demo_api.py
```

## Summary

Testing tools available:

1. Pytest Test Suite - 50+ automated tests
2. Interactive Demo Script - Walkthrough of all endpoints
3. Postman Collection - Import and test in Postman
4. Swagger UI - Interactive browser testing
5. ReDoc - API documentation
6. cURL Examples - Manual command-line testing

Choose the right tool for your needs:
- Development: Pytest test suite
- Manual testing: Swagger UI or Demo script
- Team collaboration: Postman collection
- Documentation: ReDoc
- CI/CD: Pytest with GitHub Actions
