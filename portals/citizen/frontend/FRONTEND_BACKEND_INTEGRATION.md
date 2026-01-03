# Frontend-Backend Integration Guide

## Overview

This document describes the frontend-backend integration setup for the Citizen Portal.

## API Configuration

### Base URL
- **Development**: `http://localhost:8081/citizen/api/v1`
- **Environment Variable**: `VITE_API_BASE_URL` (optional)

### API Client
Located at: `src/services/api.ts`

The API client uses Axios with:
- Automatic JWT token injection in request headers
- Language header (Accept-Language) from i18n
- Global error handling with toast notifications
- Automatic redirect to login on 401 errors

## API Services

All API services are located in `src/services/`:

1. **auth.service.ts** - Authentication endpoints
2. **citizen.service.ts** - Citizen/profile management
3. **scheme.service.ts** - Scheme browsing and details
4. **application.service.ts** - Application management
5. **document.service.ts** - Document upload and management
6. **notification.service.ts** - Notification management
7. **payment.service.ts** - Payment processing
8. **feedback.service.ts** - Feedback submission

## TypeScript Types

All API types are defined in `src/types/api.ts` and match the backend DTOs:

- `ApiResponse<T>` - Standard API response wrapper
- `PagedResponse<T>` - Paginated response
- Domain-specific types (User, Scheme, Application, etc.)

## Authentication Flow

### Current Implementation (Test Token)

Currently using the test token endpoint (`/auth/test-token`) for development:

```typescript
// In LoginPage.tsx
const result = await dispatch(loginWithTestToken(janAadhaar)).unwrap();
await dispatch(fetchCurrentUser()).unwrap();
```

### Future Implementation (OTP-based)

When OTP endpoints are available, the flow will be:

1. User enters Jan Aadhaar ID
2. Frontend calls `/auth/send-otp` with Jan Aadhaar ID
3. User enters OTP
4. Frontend calls `/auth/verify-otp` with Jan Aadhaar ID and OTP
5. Backend returns JWT token
6. Frontend stores token and fetches user profile

## Redux Integration

### Auth Slice

The auth slice (`src/store/slices/auth.slice.ts`) includes:

- **Async Thunks**:
  - `loginWithTestToken` - Login using test token endpoint
  - `fetchCurrentUser` - Fetch current user profile

- **State**:
  - `user`: Current user object
  - `token`: JWT access token
  - `refreshToken`: Refresh token
  - `isAuthenticated`: Boolean flag
  - `isLoading`: Loading state
  - `error`: Error message

- **Actions**:
  - `logout` - Clear auth state and localStorage
  - `updateUser` - Update user profile in state
  - `clearError` - Clear error message

## Usage Examples

### Making API Calls

```typescript
import { citizenService } from '@/services';

// Get current user
const user = await citizenService.getCurrentUser();

// Get schemes (paginated)
const schemes = await schemeService.getSchemes(0, 10, 'ACTIVE');

// Create application
const application = await applicationService.createApplication({
  schemeId: 'scheme-uuid',
  serviceType: 'PENSION',
  description: 'Application description'
});
```

### Using Redux Async Thunks

```typescript
import { useAppDispatch } from '@/store/hooks';
import { fetchCurrentUser } from '@/store/slices/auth.slice';

const dispatch = useAppDispatch();

// In component
useEffect(() => {
  dispatch(fetchCurrentUser());
}, [dispatch]);
```

### Error Handling

Errors are automatically handled by the API interceptor:
- 401 → Redirect to login + clear tokens
- 403 → Show "Access denied" toast
- 404 → Show "Resource not found" toast
- 500 → Show "Server error" toast
- Network errors → Show "Network error" toast

You can also handle errors manually:

```typescript
try {
  const result = await dispatch(loginWithTestToken(username)).unwrap();
} catch (error) {
  // Handle error
  console.error('Login failed:', error);
}
```

## Token Management

### Storage
- Access token: `localStorage.getItem('auth_token')`
- Refresh token: `localStorage.getItem('refresh_token')`

### Automatic Injection
The API client automatically adds the token to all requests:

```typescript
// In api.ts interceptor
const token = localStorage.getItem('auth_token');
if (token && config.headers) {
  config.headers.Authorization = `Bearer ${token}`;
}
```

### Logout
Logout clears both Redux state and localStorage:

```typescript
dispatch(logout());
// This also clears localStorage tokens
```

## Development Notes

### CORS Configuration
The backend CORS is configured to allow requests from:
- `http://localhost:3000` (frontend dev server)

### Vite Proxy
Vite proxy is configured in `vite.config.ts`:

```typescript
proxy: {
  '/citizen/api': {
    target: 'http://localhost:8081',
    changeOrigin: true,
  },
}
```

### Testing API Endpoints

1. **Swagger UI**: `http://localhost:8081/citizen/api/v1/swagger-ui.html`
2. **Get Test Token**: 
   - Endpoint: `POST /auth/test-token?username=test-user`
   - Use this token in Swagger UI "Authorize" button

## Next Steps

1. ✅ API service layer created
2. ✅ TypeScript types defined
3. ✅ Auth slice with async thunks
4. ✅ LoginPage connected to API
5. ⏳ Implement proper OTP endpoints in backend
6. ⏳ Update LoginPage to use OTP flow
7. ⏳ Connect Dashboard to fetch real data
8. ⏳ Connect other components to APIs

## Troubleshooting

### API calls failing with CORS errors
- Verify backend CORS configuration allows `http://localhost:3000`
- Check Vite proxy configuration

### 401 errors
- Verify token is stored in localStorage
- Check token expiration
- Verify token format (should be `Bearer <token>`)

### Network errors
- Verify backend is running on port 8081
- Check Vite proxy target URL
- Verify API base URL in `api.ts`

