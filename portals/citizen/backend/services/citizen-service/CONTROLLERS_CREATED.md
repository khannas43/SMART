# REST Controllers Created

## ✅ All REST Controllers Created

All REST controllers have been created with proper endpoints, validation, and error handling.

## Controllers

### 1. CitizenController (`/citizens`)
**Endpoints:**
- `POST /citizens` - Create new citizen
- `GET /citizens/{id}` - Get citizen by ID
- `GET /citizens/mobile/{mobileNumber}` - Get citizen by mobile number
- `GET /citizens/aadhaar/{aadhaarNumber}` - Get citizen by Aadhaar number
- `GET /citizens` - Get all citizens (paginated)
- `GET /citizens/status/{status}` - Get citizens by status
- `PUT /citizens/{id}` - Update citizen
- `DELETE /citizens/{id}` - Delete citizen
- `GET /citizens/exists/mobile/{mobileNumber}` - Check mobile number exists
- `GET /citizens/exists/aadhaar/{aadhaarNumber}` - Check Aadhaar number exists

### 2. SchemeController (`/schemes`)
**Endpoints:**
- `POST /schemes` - Create new scheme
- `GET /schemes/{id}` - Get scheme by ID
- `GET /schemes/code/{code}` - Get scheme by code
- `GET /schemes` - Get all schemes (paginated)
- `GET /schemes/active` - Get all active schemes
- `GET /schemes/category/{category}` - Get schemes by category
- `GET /schemes/department/{department}` - Get schemes by department
- `PUT /schemes/{id}` - Update scheme
- `DELETE /schemes/{id}` - Delete scheme

### 3. ServiceApplicationController (`/applications`)
**Endpoints:**
- `POST /applications/citizens/{citizenId}` - Create new application
- `GET /applications/{id}` - Get application by ID
- `GET /applications/number/{applicationNumber}` - Get application by number
- `GET /applications/citizens/{citizenId}` - Get applications by citizen (paginated)
- `GET /applications/citizens/{citizenId}/status/{status}` - Get applications by citizen and status
- `GET /applications/status/{status}` - Get applications by status (paginated)
- `PATCH /applications/{id}/status` - Update application status
- `PUT /applications/{id}` - Update application
- `DELETE /applications/{id}` - Delete application

### 4. DocumentController (`/documents`)
**Endpoints:**
- `POST /documents/citizens/{citizenId}` - Upload document
- `GET /documents/{id}` - Get document by ID
- `GET /documents/citizens/{citizenId}` - Get documents by citizen
- `GET /documents/applications/{applicationId}` - Get documents by application
- `GET /documents/citizens/{citizenId}/type/{documentType}` - Get documents by citizen and type
- `PATCH /documents/{id}/verification` - Update document verification status
- `DELETE /documents/{id}` - Delete document

### 5. NotificationController (`/notifications`)
**Endpoints:**
- `GET /notifications/{id}` - Get notification by ID
- `GET /notifications/citizens/{citizenId}` - Get notifications by citizen (paginated)
- `GET /notifications/citizens/{citizenId}/unread` - Get unread notifications
- `GET /notifications/citizens/{citizenId}/unread/count` - Get unread notification count
- `PATCH /notifications/{id}/read` - Mark notification as read
- `PATCH /notifications/citizens/{citizenId}/read-all` - Mark all notifications as read

### 6. PaymentController (`/payments`)
**Endpoints:**
- `POST /payments/citizens/{citizenId}` - Initiate payment
- `GET /payments/{id}` - Get payment by ID
- `GET /payments/transaction/{transactionId}` - Get payment by transaction ID
- `GET /payments/citizens/{citizenId}` - Get payments by citizen (paginated)
- `GET /payments/applications/{applicationId}` - Get payments by application
- `PATCH /payments/transaction/{transactionId}/status` - Update payment status (gateway callback)

### 7. FeedbackController (`/feedback`)
**Endpoints:**
- `POST /feedback/citizens/{citizenId}` - Submit feedback
- `GET /feedback/{id}` - Get feedback by ID
- `GET /feedback/citizens/{citizenId}` - Get feedback by citizen (paginated)
- `GET /feedback/applications/{applicationId}` - Get feedback by application
- `GET /feedback/type/{type}` - Get feedback by type
- `PATCH /feedback/{id}/status` - Update feedback status

### 8. HealthController (`/health`)
**Endpoints:**
- `GET /health` - Health check endpoint

## Global Exception Handler

### GlobalExceptionHandler
**Handles:**
- `ResourceNotFoundException` - Returns 404 with error message
- `BadRequestException` - Returns 400 with error message
- `MethodArgumentNotValidException` - Returns 400 with validation errors map
- `IllegalArgumentException` - Returns 400 with error message
- `Exception` - Returns 500 with generic error message (catches all unhandled exceptions)

**Features:**
- Consistent error response format using `ApiResponse`
- Error code for each exception type
- Logging of exceptions
- Validation error details in response

## Features

✅ RESTful API design with proper HTTP methods
✅ Request validation using `@Valid` and Bean Validation
✅ Consistent response format using `ApiResponse<T>`
✅ Pagination support with `PagedResponse<T>`
✅ Proper HTTP status codes (200, 201, 400, 404, 500)
✅ Path variables and query parameters
✅ Request body validation
✅ Global exception handling
✅ Logging support
✅ Sorting support in pagination
✅ Health check endpoint

## API Base Path

All endpoints are under `/citizen/api/v1` as configured in `application.yml`

Example: `http://localhost:8080/citizen/api/v1/citizens`

## Next Steps

1. Add Spring Security configuration
2. Add JWT authentication
3. Add API documentation (Swagger/OpenAPI)
4. Add request/response logging (interceptor)
5. Add rate limiting
6. Add caching where appropriate
7. Add integration tests

