# Citizen Portal - Development Plan

## Executive Summary

This document outlines the comprehensive development plan for the Citizen Portal of the SMART (State Management and Analytics for Rajasthan Transformation) Platform. The portal is a public-facing web application enabling citizens of Rajasthan to access government services, apply for schemes, submit documents, track applications, make payments, and provide feedback.

## Current State Assessment

### ✅ What Exists
- **Directory Structure**: Complete folder structure with all necessary directories
- **Database Schema**: Comprehensive schema defined in `database/schemas/01_citizen_schema.sql`
  - Citizens, Schemes, Service Applications, Documents
  - Application Status History, Notifications, Payments
  - Feedback, Audit Log
- **Configuration Files**: Base application configuration files
- **i18n Structure**: Locale directories (English, Hindi, Rajasthani)
- **Backend Service Structure**: Service directories created (citizen-service, auth-service)

### ❌ What Needs Development
- **Frontend**: Complete React application (empty directory)
- **Backend Services**: Full implementation of microservices
- **API Endpoints**: RESTful API implementation
- **Authentication & Authorization**: Complete auth flow
- **File Upload/Download**: Document handling service
- **Notifications**: Email/SMS notification integration
- **Payment Gateway**: Payment processing integration
- **Internationalization**: Translation files
- **Testing**: Unit, integration, and E2E tests
- **Docker/Kubernetes**: Containerization and orchestration configs

## Architecture Overview

### Technology Stack

**Frontend:**
- React 18+ with TypeScript
- React Router for navigation
- Redux Toolkit / Zustand for state management
- React Query / SWR for data fetching
- i18next for internationalization
- Material-UI / Ant Design for UI components
- Axios for HTTP requests
- React Hook Form for form management
- Tailwind CSS / CSS Modules for styling

**Backend:**
- Java 17+
- Spring Boot 3.x
- Spring Data JPA for database access
- Spring Security for authentication/authorization
- Spring Cloud Gateway for API gateway (optional)
- Flyway for database migrations
- Maven for dependency management

**Database:**
- PostgreSQL 14+
- UUID for primary keys
- JSONB for flexible data storage

**Infrastructure:**
- Docker for containerization
- Kubernetes for orchestration
- Nginx for reverse proxy/load balancing

## Development Phases

### Phase 1: Foundation & Setup (Week 1-2)

#### 1.1 Project Setup
- [ ] Initialize React frontend project with TypeScript
- [ ] Set up project structure (components, pages, services, hooks, utils, store, routes)
- [ ] Configure build tools (Webpack/Vite, ESLint, Prettier)
- [ ] Set up routing structure
- [ ] Configure state management (Redux Toolkit)
- [ ] Set up API service layer
- [ ] Configure i18n (i18next)

#### 1.2 Backend Service Setup
- [ ] Initialize Spring Boot services:
  - [ ] citizen-service (main service)
  - [ ] auth-service (authentication)
- [ ] Configure database connection (PostgreSQL)
- [ ] Set up JPA entities based on schema
- [ ] Configure Flyway migrations
- [ ] Set up REST controllers structure
- [ ] Configure Spring Security
- [ ] Set up exception handling
- [ ] Configure logging

#### 1.3 Development Environment
- [ ] Docker Compose for local development
- [ ] Database setup scripts
- [ ] Environment configuration files
- [ ] Development documentation

### Phase 2: Authentication & User Management (Week 3-4)

#### 2.1 Authentication Service
- [ ] OTP-based authentication (mobile/email)
- [ ] Aadhaar verification integration
- [ ] JWT token generation and validation
- [ ] Password management (if required)
- [ ] Session management
- [ ] Refresh token mechanism

#### 2.2 Citizen Registration & Profile
- [ ] Registration flow (mobile OTP)
- [ ] Profile creation and update
- [ ] Profile verification workflow
- [ ] Address management
- [ ] Document upload for verification

#### 2.3 Frontend Auth Implementation
- [ ] Login/Signup pages
- [ ] OTP verification component
- [ ] Protected routes
- [ ] Auth context/hooks
- [ ] Token management (storage, refresh)

### Phase 3: Core Features - Schemes & Applications (Week 5-7)

#### 3.1 Schemes Module
- [ ] Scheme listing API
- [ ] Scheme details API
- [ ] Scheme search and filtering
- [ ] Eligibility checking API
- [ ] Frontend: Scheme browsing pages
- [ ] Frontend: Scheme details page
- [ ] Frontend: Eligibility checker UI

#### 3.2 Application Submission
- [ ] Application creation API
- [ ] Application form data validation
- [ ] Document attachment in applications
- [ ] Application number generation
- [ ] Frontend: Application form pages
- [ ] Frontend: Multi-step form wizard
- [ ] Frontend: Document upload component

#### 3.3 Application Tracking
- [ ] Application status API
- [ ] Application history API
- [ ] Real-time status updates (WebSocket/SSE)
- [ ] Frontend: Application dashboard
- [ ] Frontend: Application details page
- [ ] Frontend: Status timeline component

### Phase 4: Document Management (Week 8-9)

#### 4.1 File Service Integration
- [ ] File upload API
- [ ] File download API
- [ ] File validation (size, type, virus scan)
- [ ] File storage (local/S3)
- [ ] File metadata management
- [ ] Document verification workflow

#### 4.2 Frontend Document Handling
- [ ] Document upload component
- [ ] Document viewer
- [ ] Document list/download
- [ ] Document verification status

### Phase 5: Payments Integration (Week 10-11)

#### 5.1 Payment Service
- [ ] Payment gateway integration (Razorpay/PayU/BharatPay)
- [ ] Payment initiation API
- [ ] Payment status callback handling
- [ ] Payment history API
- [ ] Refund processing
- [ ] Payment receipt generation

#### 5.2 Frontend Payment Flow
- [ ] Payment page
- [ ] Payment gateway redirect handling
- [ ] Payment status page
- [ ] Payment history

### Phase 6: Notifications & Communication (Week 12)

#### 6.1 Notification Service
- [ ] Email notification service (SMTP/SES)
- [ ] SMS notification service (Twilio/Msg91)
- [ ] Push notification (if mobile app)
- [ ] In-app notifications
- [ ] Notification templates
- [ ] Notification preferences

#### 6.2 Frontend Notifications
- [ ] Notification center/bell icon
- [ ] Notification list
- [ ] Email/SMS preferences

### Phase 7: Feedback & Complaints (Week 13)

#### 7.1 Feedback Module
- [ ] Feedback submission API
- [ ] Complaint submission API
- [ ] Rating system
- [ ] Feedback listing (user's own)
- [ ] Feedback status tracking

#### 7.2 Frontend Feedback
- [ ] Feedback form
- [ ] Complaint form
- [ ] Rating component
- [ ] Feedback history

### Phase 8: Dashboard & Analytics (Week 14)

#### 8.1 User Dashboard
- [ ] Dashboard API (summary stats)
- [ ] Recent applications
- [ ] Pending actions
- [ ] Quick links
- [ ] Frontend: Dashboard page
- [ ] Frontend: Widgets and charts

### Phase 9: Internationalization (Week 15)

#### 9.1 Translation Files
- [ ] English translations (all UI text)
- [ ] Hindi translations
- [ ] Rajasthani translations
- [ ] Date/time localization
- [ ] Number formatting

#### 9.2 Frontend i18n
- [ ] Language switcher
- [ ] RTL support (if needed)
- [ ] Dynamic content translation

### Phase 10: Mobile Responsiveness & UX (Week 16)

#### 10.1 Responsive Design
- [ ] Mobile-first approach
- [ ] Tablet layouts
- [ ] Desktop layouts
- [ ] Touch-friendly interactions

#### 10.2 Performance Optimization
- [ ] Code splitting
- [ ] Lazy loading
- [ ] Image optimization
- [ ] Caching strategies
- [ ] API response optimization

### Phase 11: Testing (Week 17-18)

#### 11.1 Backend Testing
- [ ] Unit tests (services, repositories)
- [ ] Integration tests (API endpoints)
- [ ] Security testing
- [ ] Performance testing

#### 11.2 Frontend Testing
- [ ] Unit tests (components, utilities)
- [ ] Integration tests
- [ ] E2E tests (Playwright/Cypress)
- [ ] Accessibility testing

### Phase 12: Security & Compliance (Week 19)

#### 12.1 Security Implementation
- [ ] Input validation and sanitization
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] CSRF protection
- [ ] Rate limiting
- [ ] API authentication/authorization
- [ ] Data encryption (at rest, in transit)
- [ ] PII data protection

#### 12.2 Compliance
- [ ] Data privacy (GDPR-like compliance)
- [ ] Audit logging
- [ ] Data retention policies
- [ ] Security headers

### Phase 13: Deployment & DevOps (Week 20)

#### 13.1 Containerization
- [ ] Dockerfiles for services
- [ ] Docker Compose for local/dev
- [ ] Multi-stage builds

#### 13.2 Kubernetes
- [ ] Deployment manifests
- [ ] Service definitions
- [ ] ConfigMaps and Secrets
- [ ] Ingress configuration
- [ ] Health checks and probes

#### 13.3 CI/CD
- [ ] Build pipelines
- [ ] Test automation
- [ ] Deployment automation
- [ ] Environment management

### Phase 14: Documentation & Training (Week 21)

#### 14.1 Technical Documentation
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Architecture documentation
- [ ] Deployment guides
- [ ] Development setup guide
- [ ] Database schema documentation

#### 14.2 User Documentation
- [ ] User guide
- [ ] FAQ
- [ ] Video tutorials (optional)

## Feature Breakdown

### Core Features

1. **Authentication & Registration**
   - Mobile OTP login
   - Aadhaar-based verification
   - Profile management
   - Account settings

2. **Scheme Discovery**
   - Browse available schemes
   - Search and filter schemes
   - Scheme details and eligibility
   - Category-based navigation

3. **Application Management**
   - Submit new applications
   - View application status
   - Track application history
   - Download application receipts

4. **Document Management**
   - Upload documents
   - View uploaded documents
   - Document verification status
   - Download documents

5. **Payment Processing**
   - Make payments for services
   - Payment history
   - Payment receipts
   - Refund status

6. **Notifications**
   - Application status updates
   - Payment confirmations
   - Document verification updates
   - System announcements

7. **Feedback & Complaints**
   - Submit feedback
   - File complaints
   - Rate services
   - View feedback history

8. **Dashboard**
   - Application summary
   - Pending actions
   - Quick links
   - Recent activity

### Advanced Features (Future)

1. **AI Integration**
   - Eligibility scoring (using AI/ML models)
   - Scheme recommendations
   - Chatbot assistance

2. **Mobile App**
   - Native mobile applications
   - Push notifications

3. **Offline Support**
   - Offline form filling
   - Sync when online

## Database Schema Highlights

Key tables from the existing schema:
- `citizens` - User accounts and profiles
- `schemes` - Government schemes
- `service_applications` - Applications
- `documents` - Document storage
- `application_status_history` - Status tracking
- `notifications` - Notifications
- `payments` - Payment transactions
- `feedback` - Feedback and complaints
- `audit_log` - Audit trail

## API Endpoint Structure

### Authentication APIs
```
POST   /api/v1/auth/login              - Login with mobile OTP
POST   /api/v1/auth/verify-otp         - Verify OTP
POST   /api/v1/auth/register           - Register new citizen
POST   /api/v1/auth/refresh            - Refresh token
POST   /api/v1/auth/logout             - Logout
```

### Citizen APIs
```
GET    /api/v1/citizens/profile        - Get profile
PUT    /api/v1/citizens/profile        - Update profile
POST   /api/v1/citizens/verify-aadhaar - Verify Aadhaar
```

### Scheme APIs
```
GET    /api/v1/schemes                 - List schemes
GET    /api/v1/schemes/{id}            - Get scheme details
GET    /api/v1/schemes/search          - Search schemes
POST   /api/v1/schemes/{id}/check-eligibility - Check eligibility
```

### Application APIs
```
GET    /api/v1/applications            - List user applications
POST   /api/v1/applications            - Create application
GET    /api/v1/applications/{id}       - Get application details
GET    /api/v1/applications/{id}/status - Get status
GET    /api/v1/applications/{id}/history - Get status history
PUT    /api/v1/applications/{id}       - Update application (if allowed)
```

### Document APIs
```
POST   /api/v1/documents               - Upload document
GET    /api/v1/documents/{id}          - Get document
GET    /api/v1/documents/application/{appId} - List documents for application
DELETE /api/v1/documents/{id}          - Delete document (if allowed)
```

### Payment APIs
```
POST   /api/v1/payments                - Initiate payment
GET    /api/v1/payments/{id}           - Get payment details
GET    /api/v1/payments/application/{appId} - Get payment for application
POST   /api/v1/payments/{id}/verify    - Verify payment
```

### Notification APIs
```
GET    /api/v1/notifications           - List notifications
GET    /api/v1/notifications/{id}      - Get notification
PUT    /api/v1/notifications/{id}/read - Mark as read
PUT    /api/v1/notifications/preferences - Update preferences
```

### Feedback APIs
```
GET    /api/v1/feedback                - List feedback
POST   /api/v1/feedback                - Submit feedback
GET    /api/v1/feedback/{id}           - Get feedback details
```

## Frontend Page Structure

### Public Pages
- Landing Page
- Login/Signup
- Forgot Password
- Scheme Listing (public view)
- Scheme Details (public view)

### Authenticated Pages
- Dashboard
- Profile
- Schemes (authenticated view with eligibility)
- Application Form
- My Applications
- Application Details
- Application Status
- Upload Documents
- My Documents
- Make Payment
- Payment History
- Notifications
- Feedback/Complaint Form
- My Feedback

## Integration Points

### External Services
1. **Aadhaar Verification API** - Government Aadhaar verification service
2. **Payment Gateway** - Razorpay/PayU/BharatPay
3. **SMS Service** - Twilio/Msg91/Government SMS gateway
4. **Email Service** - SMTP/SES
5. **OTP Service** - Integrated with SMS service

### Internal Services
1. **Shared Auth Service** - For authentication (if shared)
2. **AI/ML Services** - Eligibility scoring, recommendations
3. **Department Portal Integration** - For application processing updates

## Security Considerations

1. **Authentication**
   - OTP-based authentication (no passwords)
   - JWT tokens with short expiry
   - Refresh token rotation
   - Secure token storage

2. **Authorization**
   - Role-based access control
   - Resource-level permissions
   - API endpoint protection

3. **Data Protection**
   - Encryption of sensitive data (Aadhaar, mobile)
   - HTTPS only
   - Secure file storage
   - PII data masking in logs

4. **Input Validation**
   - Server-side validation
   - SQL injection prevention
   - XSS prevention
   - File upload validation

5. **Rate Limiting**
   - API rate limiting
   - OTP request limiting
   - File upload limiting

## Performance Targets

- **Page Load Time**: < 3 seconds
- **API Response Time**: < 500ms (95th percentile)
- **Time to Interactive**: < 5 seconds
- **Mobile Performance**: Lighthouse score > 80
- **Availability**: 99.9% uptime

## Success Metrics

1. **User Adoption**
   - Number of registered users
   - Active users per month
   - Application submission rate

2. **User Experience**
   - Application completion rate
   - Time to submit application
   - User satisfaction scores

3. **System Performance**
   - API response times
   - Error rates
   - System uptime

4. **Business Metrics**
   - Applications processed
   - Payment success rate
   - Feedback ratings

## Risk Assessment & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Integration failures with external services | High | Implement fallback mechanisms, circuit breakers |
| Security vulnerabilities | High | Regular security audits, penetration testing |
| Performance issues under load | Medium | Load testing, caching, CDN |
| Data privacy concerns | High | Compliance review, encryption, audit logs |
| User adoption challenges | Medium | User testing, intuitive UI, training |

## Next Steps

1. **Review & Approval**: Review this plan with stakeholders
2. **Resource Allocation**: Assign development team members
3. **Sprint Planning**: Break down phases into sprints (2-week sprints recommended)
4. **Tool Setup**: Set up development tools, repositories, CI/CD
5. **Kick-off Meeting**: Align team on plan and priorities

## Appendix

### Recommended Libraries & Tools

**Frontend:**
- React 18+
- TypeScript
- React Router v6
- Redux Toolkit
- React Query
- i18next
- Material-UI / Ant Design
- Axios
- React Hook Form
- Zod (validation)
- Tailwind CSS

**Backend:**
- Spring Boot 3.x
- Spring Data JPA
- Spring Security
- Spring Cloud (optional)
- Flyway
- Lombok
- MapStruct
- Swagger/OpenAPI

**Development:**
- ESLint, Prettier
- Husky (git hooks)
- Jest, React Testing Library
- Playwright/Cypress (E2E)
- Docker, Docker Compose
- Kubernetes

### References
- Database Schema: `portals/citizen/database/schemas/01_citizen_schema.sql`
- Portal README: `portals/citizen/README.md`
- Architecture Docs: `ARCHITECTURE.md`
- Deployment Guide: `DEPLOYMENT.md`

