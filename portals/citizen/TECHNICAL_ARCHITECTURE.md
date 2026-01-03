# Citizen Portal - Technical Architecture

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│                   (React 18 + TypeScript)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Pages   │  │Components│  │  Store   │  │ Services │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                          │
        ┌─────────────────┴─────────────────┐
        │         API Gateway/LB             │
        │      (Nginx / Spring Cloud)        │
        └─────────────────┬─────────────────┘
                          │
        ┌─────────────────┴─────────────────┐
        │      Backend Microservices         │
        │      (Spring Boot 3.x)             │
        │  ┌──────────────┐ ┌──────────────┐│
        │  │  Citizen     │ │   Auth       ││
        │  │  Service     │ │   Service    ││
        │  └──────┬───────┘ └──────┬───────┘│
        │         │                 │        │
        │  ┌──────▼───────────────▼──────┐  │
        │  │  Notification  │  File      │  │
        │  │  Service       │  Service   │  │
        │  └─────────────────────────────┘  │
        └─────────────────┬─────────────────┘
                          │
        ┌─────────────────┴─────────────────┐
        │         PostgreSQL Database        │
        │        (smart_citizen DB)          │
        └───────────────────────────────────┘
```

## Frontend Architecture

### Directory Structure
```
frontend/
├── public/                 # Static assets
├── src/
│   ├── assets/            # Images, fonts, etc.
│   ├── components/        # Reusable UI components
│   │   ├── common/        # Shared components (Button, Input, etc.)
│   │   ├── forms/         # Form components
│   │   ├── layout/        # Layout components (Header, Footer, Sidebar)
│   │   └── features/      # Feature-specific components
│   ├── pages/             # Page components
│   │   ├── auth/          # Authentication pages
│   │   ├── dashboard/     # Dashboard
│   │   ├── schemes/       # Schemes pages
│   │   ├── applications/  # Application pages
│   │   ├── documents/     # Document pages
│   │   ├── payments/      # Payment pages
│   │   └── feedback/      # Feedback pages
│   ├── services/          # API service layer
│   │   ├── api.ts         # Axios instance
│   │   ├── auth.service.ts
│   │   ├── citizen.service.ts
│   │   ├── scheme.service.ts
│   │   ├── application.service.ts
│   │   ├── document.service.ts
│   │   ├── payment.service.ts
│   │   └── notification.service.ts
│   ├── store/             # State management (Redux Toolkit)
│   │   ├── index.ts       # Store configuration
│   │   ├── slices/
│   │   │   ├── auth.slice.ts
│   │   │   ├── citizen.slice.ts
│   │   │   └── application.slice.ts
│   │   └── hooks.ts       # Typed hooks
│   ├── hooks/             # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useApi.ts
│   │   └── useNotifications.ts
│   ├── routes/            # Route configuration
│   │   ├── index.tsx      # Route definitions
│   │   └── ProtectedRoute.tsx
│   ├── utils/             # Utility functions
│   │   ├── validators.ts
│   │   ├── formatters.ts
│   │   └── constants.ts
│   ├── types/             # TypeScript types
│   │   ├── auth.types.ts
│   │   ├── citizen.types.ts
│   │   └── application.types.ts
│   ├── styles/            # Global styles
│   │   ├── index.css
│   │   └── theme.css
│   ├── i18n/              # Internationalization
│   │   ├── config.ts
│   │   └── resources/     # Translation files
│   ├── App.tsx            # Root component
│   └── main.tsx           # Entry point
├── package.json
├── tsconfig.json
└── vite.config.ts / webpack.config.js
```

### Component Hierarchy

```
App
├── Router
│   ├── Public Routes
│   │   ├── LandingPage
│   │   ├── LoginPage
│   │   ├── RegisterPage
│   │   └── SchemeListingPage (public view)
│   │
│   └── Protected Routes (requires auth)
│       ├── DashboardPage
│       ├── ProfilePage
│       ├── SchemesPage
│       ├── ApplicationFormPage
│       ├── ApplicationListPage
│       ├── ApplicationDetailPage
│       ├── DocumentUploadPage
│       ├── PaymentPage
│       ├── NotificationCenter
│       └── FeedbackPage
│
└── Common Layout
    ├── Header (with navigation, user menu, notifications)
    ├── Main Content Area
    └── Footer
```

### State Management

**Redux Toolkit Store Structure:**
```typescript
{
  auth: {
    user: Citizen | null,
    token: string | null,
    isAuthenticated: boolean,
    loading: boolean,
    error: string | null
  },
  citizen: {
    profile: CitizenProfile | null,
    loading: boolean,
    error: string | null
  },
  schemes: {
    list: Scheme[],
    selected: Scheme | null,
    loading: boolean,
    error: string | null
  },
  applications: {
    list: Application[],
    selected: Application | null,
    loading: boolean,
    error: string | null
  },
  notifications: {
    list: Notification[],
    unreadCount: number,
    loading: boolean
  }
}
```

### Data Flow

1. **User Action** → Component dispatches action
2. **Action** → API service method called
3. **API Service** → HTTP request via Axios
4. **Response** → Redux action dispatched
5. **Reducer** → State updated
6. **Component** → Re-renders with new data

### API Service Layer Pattern

```typescript
// Example: application.service.ts
class ApplicationService {
  private api = axios.create({
    baseURL: '/api/v1/applications',
    headers: {
      'Authorization': `Bearer ${getToken()}`
    }
  });

  async getApplications(): Promise<Application[]> {
    const response = await this.api.get('/');
    return response.data;
  }

  async createApplication(data: CreateApplicationDto): Promise<Application> {
    const response = await this.api.post('/', data);
    return response.data;
  }

  async getApplicationById(id: string): Promise<Application> {
    const response = await this.api.get(`/${id}`);
    return response.data;
  }
}
```

## Backend Architecture

### Service Structure

```
citizen-service/
├── src/main/java/com/smart/citizen/
│   ├── CitizenServiceApplication.java
│   │
│   ├── config/                    # Configuration classes
│   │   ├── SecurityConfig.java
│   │   ├── CorsConfig.java
│   │   ├── SwaggerConfig.java
│   │   └── DatabaseConfig.java
│   │
│   ├── controller/                # REST controllers
│   │   ├── CitizenController.java
│   │   ├── SchemeController.java
│   │   ├── ApplicationController.java
│   │   ├── DocumentController.java
│   │   ├── PaymentController.java
│   │   └── FeedbackController.java
│   │
│   ├── service/                   # Business logic
│   │   ├── CitizenService.java
│   │   ├── SchemeService.java
│   │   ├── ApplicationService.java
│   │   ├── DocumentService.java
│   │   ├── PaymentService.java
│   │   └── NotificationService.java
│   │
│   ├── repository/                # Data access
│   │   ├── CitizenRepository.java
│   │   ├── SchemeRepository.java
│   │   ├── ApplicationRepository.java
│   │   ├── DocumentRepository.java
│   │   └── PaymentRepository.java
│   │
│   ├── entity/                    # JPA entities
│   │   ├── Citizen.java
│   │   ├── Scheme.java
│   │   ├── ServiceApplication.java
│   │   ├── Document.java
│   │   └── Payment.java
│   │
│   ├── dto/                       # Data transfer objects
│   │   ├── request/
│   │   │   ├── CreateApplicationDto.java
│   │   │   └── UpdateProfileDto.java
│   │   └── response/
│   │       ├── ApplicationResponseDto.java
│   │       └── DashboardResponseDto.java
│   │
│   ├── mapper/                    # Entity-DTO mappers
│   │   └── ApplicationMapper.java
│   │
│   ├── exception/                 # Exception handling
│   │   ├── GlobalExceptionHandler.java
│   │   ├── ResourceNotFoundException.java
│   │   └── ValidationException.java
│   │
│   ├── security/                  # Security
│   │   ├── JwtTokenProvider.java
│   │   └── JwtAuthenticationFilter.java
│   │
│   └── util/                      # Utilities
│       └── Constants.java
│
├── src/main/resources/
│   ├── application.yml
│   ├── application-dev.yml
│   ├── application-prod.yml
│   └── db/migration/              # Flyway migrations
│       └── V1__Initial_schema.sql
│
└── src/test/                      # Tests
    ├── java/.../
    └── resources/
```

### Service Layer Pattern

```java
@Service
@Transactional
public class ApplicationService {
    
    private final ApplicationRepository applicationRepository;
    private final CitizenRepository citizenRepository;
    private final SchemeRepository schemeRepository;
    private final ApplicationMapper applicationMapper;
    private final NotificationService notificationService;
    
    public ApplicationResponseDto createApplication(
            CreateApplicationDto dto, UUID citizenId) {
        
        // 1. Validate citizen exists
        Citizen citizen = citizenRepository.findById(citizenId)
            .orElseThrow(() -> new ResourceNotFoundException("Citizen not found"));
        
        // 2. Validate scheme (if provided)
        if (dto.getSchemeId() != null) {
            schemeRepository.findById(dto.getSchemeId())
                .orElseThrow(() -> new ResourceNotFoundException("Scheme not found"));
        }
        
        // 3. Create entity
        ServiceApplication application = applicationMapper.toEntity(dto);
        application.setCitizen(citizen);
        application.setStatus(ApplicationStatus.SUBMITTED);
        
        // 4. Save
        application = applicationRepository.save(application);
        
        // 5. Send notification
        notificationService.sendApplicationSubmittedNotification(application);
        
        // 6. Return DTO
        return applicationMapper.toDto(application);
    }
}
```

### Repository Pattern

```java
@Repository
public interface ApplicationRepository extends JpaRepository<ServiceApplication, UUID> {
    
    List<ServiceApplication> findByCitizenIdOrderBySubmissionDateDesc(UUID citizenId);
    
    Optional<ServiceApplication> findByApplicationNumber(String applicationNumber);
    
    List<ServiceApplication> findByStatus(ApplicationStatus status);
    
    @Query("SELECT a FROM ServiceApplication a WHERE a.citizenId = :citizenId " +
           "AND a.status IN :statuses")
    List<ServiceApplication> findByCitizenIdAndStatuses(
        @Param("citizenId") UUID citizenId,
        @Param("statuses") List<ApplicationStatus> statuses
    );
}
```

## Database Architecture

### Entity Relationships

```
Citizen (1) ────< (N) ServiceApplication
                       │
                       ├──> (N) Document
                       │
                       ├──> (N) Payment
                       │
                       ├──> (N) ApplicationStatusHistory
                       │
                       └──> (N) Notification

Scheme (1) ────< (N) ServiceApplication

Citizen (1) ────< (N) Feedback
Citizen (1) ────< (N) Notification
Citizen (1) ────< (N) Payment
```

### Key Tables

1. **citizens** - User accounts and profiles
2. **schemes** - Government schemes
3. **service_applications** - Applications submitted
4. **documents** - Uploaded documents
5. **application_status_history** - Status tracking
6. **payments** - Payment transactions
7. **notifications** - Notifications sent
8. **feedback** - Feedback and complaints
9. **audit_log** - Audit trail

## Security Architecture

### Authentication Flow

```
1. User enters mobile number
   ↓
2. Backend generates OTP and sends via SMS
   ↓
3. User enters OTP
   ↓
4. Backend validates OTP
   ↓
5. Backend generates JWT access token + refresh token
   ↓
6. Frontend stores tokens securely
   ↓
7. Frontend includes token in Authorization header for subsequent requests
```

### Authorization

- **Role-based**: Based on user type (citizen, officer, admin)
- **Resource-based**: Users can only access their own resources
- **JWT Claims**: User ID and roles included in token

### Security Measures

1. **Authentication**
   - OTP-based (no passwords)
   - JWT tokens with expiration
   - Refresh token rotation

2. **Authorization**
   - Spring Security for endpoint protection
   - Method-level security
   - Resource-level access control

3. **Data Protection**
   - HTTPS only
   - Encryption for sensitive fields (Aadhaar)
   - Secure file storage

4. **Input Validation**
   - Server-side validation
   - SQL injection prevention (parameterized queries)
   - XSS prevention (input sanitization)

5. **Rate Limiting**
   - OTP request limiting
   - API rate limiting per user/IP

## Integration Points

### External Services

1. **Aadhaar Verification API**
   - Endpoint: Government Aadhaar API
   - Method: REST API
   - Authentication: API Key
   - Used for: Citizen verification

2. **Payment Gateway**
   - Provider: Razorpay/PayU/BharatPay
   - Integration: REST API + SDK
   - Used for: Payment processing

3. **SMS Service**
   - Provider: Twilio/Msg91/Government gateway
   - Integration: REST API
   - Used for: OTP and notifications

4. **Email Service**
   - Provider: SMTP/AWS SES/SendGrid
   - Integration: SMTP or REST API
   - Used for: Notifications

### Internal Services

1. **Department Portal**
   - Integration: Webhook/API
   - Used for: Application status updates

2. **AI/ML Services**
   - Integration: REST API
   - Used for: Eligibility scoring, recommendations

## API Design

### RESTful API Principles

- **Resources**: Nouns (applications, schemes, documents)
- **HTTP Methods**: GET, POST, PUT, DELETE
- **Status Codes**: Proper HTTP status codes
- **Versioning**: `/api/v1/`
- **Pagination**: Query parameters (`page`, `size`)
- **Filtering**: Query parameters (`status`, `category`)
- **Sorting**: Query parameters (`sort`, `order`)

### API Response Format

```json
// Success Response
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}

// Error Response
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Application not found",
    "details": { ... }
  }
}

// Paginated Response
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 100,
    "totalPages": 5
  }
}
```

## Deployment Architecture

### Docker Container Structure

```
┌─────────────────────────────────────────┐
│         Nginx (Reverse Proxy)           │
│         Port: 80, 443                   │
└────────────┬────────────────────────────┘
             │
     ┌───────┴────────┐
     │                │
┌────▼────┐    ┌──────▼─────┐
│ Frontend│    │   Backend  │
│  (React)│    │  Services  │
│  :3000  │    │   :8080    │
└─────────┘    └──────┬─────┘
                      │
              ┌───────▼────────┐
              │   PostgreSQL   │
              │     :5432      │
              └────────────────┘
```

### Kubernetes Deployment

- **Frontend**: Deployment + Service + Ingress
- **Backend**: Deployment + Service (citizen-service, auth-service)
- **Database**: StatefulSet (or external managed DB)
- **ConfigMaps**: Configuration
- **Secrets**: Passwords, API keys
- **Ingress**: External access

## Performance Considerations

1. **Frontend**
   - Code splitting
   - Lazy loading
   - Image optimization
   - API response caching (React Query)

2. **Backend**
   - Database query optimization
   - Connection pooling
   - Caching (Redis, if needed)
   - Pagination for large datasets

3. **Database**
   - Proper indexing
   - Query optimization
   - Connection pooling

## Monitoring & Logging

1. **Application Logs**
   - Structured logging (JSON)
   - Log levels (DEBUG, INFO, WARN, ERROR)
   - Centralized logging (ELK stack)

2. **Metrics**
   - Application metrics (Prometheus)
   - Business metrics (application count, payment success rate)
   - System metrics (CPU, memory, disk)

3. **Alerting**
   - Error rate alerts
   - Performance alerts
   - Business metric alerts

## Error Handling

### Frontend Error Handling

- Global error boundary
- API error interceptor
- User-friendly error messages
- Retry mechanisms for transient errors

### Backend Error Handling

- Global exception handler
- Custom exception classes
- Consistent error response format
- Proper HTTP status codes
- Error logging

## Testing Strategy

1. **Unit Tests**
   - Services, repositories, utilities
   - Components, hooks, utils

2. **Integration Tests**
   - API endpoints
   - Database operations
   - Service integrations

3. **E2E Tests**
   - Critical user flows
   - Cross-browser testing

4. **Performance Tests**
   - Load testing
   - Stress testing

## Internationalization (i18n)

### Overview

The Citizen Portal supports **English (en)** and **Hindi (hi)** languages. All UI text, error messages, notifications, and documents must be available in both languages.

### Frontend i18n Implementation

**Library:** `react-i18next`

**Configuration:**
```typescript
// src/i18n/config.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './locales/en/common.json';
import hi from './locales/hi/common.json';

i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      hi: { translation: hi }
    },
    lng: 'en', // default language
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });
```

**Language Detection:**
- Browser language preference
- User preference (localStorage)
- Default: English

**Language Switcher Component:**
```typescript
// Located in header/navigation
<LanguageSwitcher>
  <option value="en">English</option>
  <option value="hi">हिंदी</option>
</LanguageSwitcher>
```

### Translation File Structure

```
i18n/locales/
├── en/
│   ├── common.json       # Common terms, buttons, labels, errors
│   ├── auth.json         # Authentication screens
│   ├── profile.json      # Profile screens
│   ├── schemes.json      # Scheme discovery screens
│   ├── applications.json # Application screens
│   ├── documents.json    # Document screens
│   ├── benefits.json     # Benefits screens
│   ├── services.json     # Service delivery screens
│   ├── settings.json     # Settings screens
│   └── help.json         # Help & support screens
└── hi/
    └── [same structure]
```

### Hindi Font Support

**Recommended Font:** Noto Sans Devanagari (Google Fonts)

**Implementation:**
```css
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap');

body {
  font-family: 'Noto Sans Devanagari', 'Mangal', 'Arial Unicode MS', sans-serif;
}
```

### Date and Number Formatting

**Date Formatting (Indian Locale):**
- Format: `DD/MM/YYYY`
- Library: `date-fns` with locale support

**Number Formatting (Indian Numbering System):**
- Format: `₹1,23,456.78` (Indian) vs `₹123,456.78` (US)
- Use: `Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' })`

### Backend i18n Support

**Accept-Language Header:**
```java
@RequestHeader(value = "Accept-Language", defaultValue = "en") String lang
```

**API Response Translation:**
- Error messages translated based on `Accept-Language` header
- Content language indicated in response headers

**Email/SMS Templates:**
- Separate templates for English and Hindi
- Template selection based on user preference

**PDF/Document Generation:**
- Hindi font support required
- Use libraries that support Devanagari script (e.g., iText, PDFKit with font embedding)

### AI/ML Content Translation

**Challenge:** AI-generated content (explanations, recommendations) needs translation

**Strategy:**
1. Coordinate with AI/ML team for translation strategy
2. Use translation APIs or services for dynamic content
3. Cache translated content to avoid repeated translation calls

---

## Progressive Web App (PWA)

### Overview

The Citizen Portal is designed as a **Progressive Web App (PWA)** enabling:
- Installation on mobile devices (Add to Home Screen)
- Offline functionality with cached content
- Native app-like experience
- Push notifications
- Background sync

### PWA Manifest

**Location:** `frontend/public/manifest.json`

**Key Configuration:**
- **Name:** SMART Citizen Portal
- **Short Name:** SMART Citizen
- **Start URL:** `/citizen/`
- **Display Mode:** `standalone`
- **Theme Color:** `#1976d2`
- **Background Color:** `#ffffff`
- **Orientation:** `portrait-primary`

**Icons Required:**
- 72x72, 96x96, 128x128, 144x144, 152x152, 192x192, 384x384, 512x512
- Apple touch icon: 180x180
- Maskable icons: 192x192, 512x512

### Service Worker

**Library:** Workbox (recommended) or custom implementation

**Caching Strategies:**
1. **Cache First:** Static assets (JS, CSS, images, fonts)
2. **Network First with Cache Fallback:** API responses
3. **Stale-While-Revalidate:** Dynamic content

**Service Worker Registration:**
```typescript
// src/serviceWorker.ts
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js')
      .then(registration => {
        console.log('SW registered:', registration);
      })
      .catch(error => {
        console.log('SW registration failed:', error);
      });
  });
}
```

### Offline Support Strategy

**What Works Offline:**
- ✅ View previously visited cached pages
- ✅ View cached scheme details
- ✅ View cached profile data
- ✅ View cached application status
- ✅ View cached documents

**What Requires Online:**
- ⚠️ Submit new applications
- ⚠️ Upload documents
- ⚠️ Make payments
- ⚠️ Real-time eligibility checks
- ⚠️ Authentication/login

**Offline Detection:**
```typescript
// Detect online/offline status
window.addEventListener('online', () => {
  // Show online indicator
  // Sync queued actions
});

window.addEventListener('offline', () => {
  // Show offline indicator
  // Enable offline mode
});
```

### Background Sync

**Use Cases:**
- Queue form submissions when offline
- Sync document uploads when connection restored
- Sync consent submissions

**Implementation:**
```typescript
// Register background sync
navigator.serviceWorker.ready.then(registration => {
  return registration.sync.register('submit-application');
});
```

### Push Notifications

**Use Cases:**
- Application status updates
- Payment confirmations
- Eligibility notifications
- Deadline reminders

**Implementation:**
```typescript
// Request notification permission
Notification.requestPermission().then(permission => {
  if (permission === 'granted') {
    // Register push subscription
  }
});
```

### Installation Prompt

**Trigger Conditions:**
- User visits portal multiple times
- User engages with portal (scroll, click, interaction)
- Not already installed

**Implementation:**
```typescript
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  // Show install button
});

// When user clicks install
installButton.addEventListener('click', () => {
  deferredPrompt.prompt();
  deferredPrompt.userChoice.then((choiceResult) => {
    if (choiceResult.outcome === 'accepted') {
      console.log('User accepted install');
    }
    deferredPrompt = null;
  });
});
```

### Mobile Responsiveness

**Breakpoints:**
- **Mobile:** < 480px
- **Tablet:** 480px - 1024px
- **Desktop:** > 1024px

**Mobile-First Approach:**
- Design for mobile first, then scale up
- Touch-friendly targets (minimum 44x44px)
- Swipe gestures for navigation
- Pull-to-refresh functionality

**Touch Gestures:**
- Swipe left/right: Navigation
- Pull down: Refresh
- Long press: Context menus

### PWA Performance Targets

**Lighthouse Scores:**
- PWA: > 90
- Performance: > 80
- Accessibility: > 90
- Best Practices: > 90
- SEO: > 90

**Bundle Size:**
- Initial bundle: < 200KB (gzipped)
- Code splitting by route
- Lazy loading for images and components

### PWA Testing

**Test Platforms:**
- Android Chrome
- iOS Safari
- Desktop Chrome/Edge
- Desktop Firefox

**Test Scenarios:**
- Installation on all platforms
- Offline functionality
- Push notifications
- Background sync
- Service worker updates
- Cache invalidation

