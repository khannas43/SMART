# Swagger UI Testing Guide

## Access Swagger UI

Open your browser and navigate to:
```
http://localhost:8081/citizen/api/v1/swagger-ui.html
```

## Testing Endpoints

### Step 1: Test Public Endpoints First

Start with endpoints that don't require authentication:

#### 1. Health Check Endpoint

1. Expand the **Health** section
2. Click on **GET** `/health`
3. Click **Try it out**
4. Click **Execute**
5. You should see a successful response (200 OK)

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "status": "UP",
    "service": "Citizen Service"
  }
}
```

---

### Step 2: Testing Authenticated Endpoints

Most endpoints require JWT authentication. You have two options:

#### Option A: Create a Test Authentication Endpoint (Recommended)

We'll create a simple test endpoint that returns a JWT token for testing purposes.

#### Option B: Use Swagger's Authorize Feature

1. Click the **Authorize** button (🔒) at the top right of Swagger UI
2. Enter a JWT token in the format: `Bearer <your-jwt-token>`
3. Click **Authorize**
4. Now you can test protected endpoints

**Note:** To get a JWT token, you'll need to either:
- Create a test auth endpoint (Option A)
- Generate one manually using the JwtTokenProvider
- Or temporarily disable authentication for testing

---

## Testing Workflow

### 1. Health Check (Public)
✅ Test first to verify service is running

### 2. Citizen Endpoints
- GET `/citizens/{id}` - Get citizen by ID
- POST `/citizens` - Create new citizen
- PUT `/citizens/{id}` - Update citizen
- GET `/citizens` - List citizens (paginated)

### 3. Scheme Endpoints
- GET `/schemes` - List all schemes
- GET `/schemes/{id}` - Get scheme by ID
- GET `/schemes/code/{code}` - Get scheme by code

### 4. Application Endpoints
- POST `/applications` - Create new application
- GET `/applications/{id}` - Get application by ID
- GET `/applications/citizen/{citizenId}` - Get applications by citizen

### 5. Document Endpoints
- POST `/documents` - Upload document
- GET `/documents/{id}` - Get document by ID
- GET `/documents/citizen/{citizenId}` - Get documents by citizen

### 6. Notification Endpoints
- GET `/notifications/citizen/{citizenId}` - Get notifications
- PUT `/notifications/{id}/read` - Mark as read

### 7. Payment Endpoints
- POST `/payments` - Initiate payment
- GET `/payments/{id}` - Get payment by ID
- GET `/payments/citizen/{citizenId}` - Get payments by citizen

### 8. Feedback Endpoints
- POST `/feedback` - Submit feedback
- GET `/feedback/{id}` - Get feedback by ID
- GET `/feedback/citizen/{citizenId}` - Get feedback by citizen

---

## Sample Test Data

### Create Citizen Request
```json
{
  "janAadhaarId": "123456789012",
  "name": "Test User",
  "email": "test@example.com",
  "mobile": "9876543210",
  "dateOfBirth": "1990-01-01",
  "gender": "MALE",
  "address": {
    "street": "123 Main St",
    "city": "Jaipur",
    "state": "Rajasthan",
    "pincode": "302001"
  }
}
```

### Create Application Request
```json
{
  "citizenId": "uuid-here",
  "schemeId": "uuid-here",
  "applicationData": {
    "field1": "value1"
  }
}
```

---

## Common Testing Scenarios

### Scenario 1: Create and Retrieve Citizen
1. POST `/citizens` - Create a citizen
2. Copy the `id` from the response
3. GET `/citizens/{id}` - Retrieve the created citizen

### Scenario 2: Browse Schemes and Apply
1. GET `/schemes` - List available schemes
2. Copy a `schemeId` from the response
3. POST `/applications` - Create application for that scheme

### Scenario 3: Upload Document
1. POST `/documents` - Upload a document
2. Copy the `documentId` from response
3. GET `/documents/{id}` - Verify document was uploaded

---

## Troubleshooting

### Error: 401 Unauthorized
- **Cause:** Missing or invalid JWT token
- **Solution:** 
  - Use the Authorize button to add a token
  - Or create a test auth endpoint to get a token

### Error: 404 Not Found
- **Cause:** Invalid UUID or resource doesn't exist
- **Solution:** Check the ID format (must be valid UUID)

### Error: 400 Bad Request
- **Cause:** Invalid request body or missing required fields
- **Solution:** Check the request body matches the schema shown in Swagger

### Error: 500 Internal Server Error
- **Cause:** Server-side error (check server logs)
- **Solution:** Check the application logs for detailed error messages

---

## Next Steps

1. **Create Test Auth Endpoint** - For easy JWT token generation during testing
2. **Add Test Data** - Seed database with sample data for testing
3. **Integration Tests** - Create automated API tests
4. **Postman Collection** - Export API collection for external testing

