# Flyway Migrations and Spring Security Setup

## ✅ Flyway Migrations Created

All database migration files have been created following Flyway naming convention (V{version}__{description}.sql).

### Migration Files

1. **V1__create_extension_and_citizens_table.sql**
   - Creates UUID extension
   - Creates citizens table with all fields and indexes

2. **V2__create_schemes_table.sql**
   - Creates schemes table with eligibility criteria (JSONB)
   - Creates indexes for code, category, and status

3. **V3__create_service_applications_table.sql**
   - Creates service_applications table
   - Creates application_number_seq sequence
   - Creates foreign keys and indexes

4. **V4__create_documents_table.sql**
   - Creates documents table with verification fields
   - Creates indexes for application, citizen, type, and verification status

5. **V5__create_application_status_history_table.sql**
   - Creates application_status_history table
   - Tracks status changes with actor information

6. **V6__create_notifications_table.sql**
   - Creates notifications table with read status
   - Supports multiple channels (email, SMS, push, in-app)
   - Creates indexes for efficient querying

7. **V7__create_payments_table.sql**
   - Creates payments table with gateway integration fields
   - Creates indexes for transaction lookup

8. **V8__create_feedback_table.sql**
   - Creates feedback table with rating and resolution fields
   - Creates indexes for filtering

9. **V9__create_audit_log_table.sql**
   - Creates audit_log table for audit trail
   - Creates composite indexes for efficient querying

10. **V10__create_triggers.sql**
    - Creates update_updated_at_column() function
    - Applies triggers to tables with updated_at column
    - Creates generate_application_number() function and trigger

### Features

✅ Proper Flyway versioning
✅ All tables, indexes, and constraints
✅ Foreign key relationships
✅ Triggers for automatic timestamp updates
✅ Application number generation trigger
✅ JSONB support for flexible data

## ✅ Spring Security Configuration

### Components Created

1. **SecurityConfig**
   - Security filter chain configuration
   - CORS configuration for frontend (localhost:3000)
   - Session management (STATELESS for JWT)
   - Public endpoints (health, actuator)
   - JWT filter integration

2. **JwtTokenProvider**
   - JWT token generation
   - Token validation
   - Token expiration checking
   - Claims extraction

3. **JwtAuthenticationFilter**
   - Filters all requests
   - Extracts JWT from Authorization header
   - Validates token and sets authentication in security context

4. **JwtAuthenticationEntryPoint**
   - Handles unauthorized access
   - Returns consistent error response format

### Security Features

✅ JWT-based authentication
✅ Stateless session management
✅ CORS enabled for frontend
✅ Password encoder (BCrypt)
✅ Authentication manager bean
✅ Method-level security enabled
✅ Custom authentication entry point
✅ Request filtering for JWT tokens

### Configuration

**application.yml settings:**
- JPA ddl-auto: `none` (Flyway manages schema)
- JWT secret: Configured via property (default provided for development)
- JWT expiration: 24 hours (configurable)

**Public Endpoints:**
- `/health` - Health check
- `/actuator/**` - Actuator endpoints

**Protected Endpoints:**
- All other endpoints require JWT authentication

### CORS Configuration

- **Allowed Origins**: `http://localhost:3000`
- **Allowed Methods**: GET, POST, PUT, PATCH, DELETE, OPTIONS
- **Allowed Headers**: All
- **Credentials**: Enabled
- **Max Age**: 3600 seconds

## Next Steps

1. Integrate with authentication service (when auth-service is ready)
2. Add role-based access control (RBAC) if needed
3. Configure JWT secret in production environment
4. Add refresh token support
5. Add rate limiting
6. Add request/response logging
7. Test authentication flow

## Notes

- JWT secret should be changed in production (minimum 256 bits/32 bytes)
- Authentication endpoints will be added when auth-service is integrated
- All endpoints except health and actuator require authentication
- JWT token should be sent in Authorization header: `Bearer {token}`

