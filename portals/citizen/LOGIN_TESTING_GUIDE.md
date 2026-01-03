# Login Testing Guide

## Current Implementation Status

**⚠️ Note**: The login system is currently using a **test token endpoint** for development purposes. Actual OTP verification is **not implemented yet**.

## Test Credentials

Since we're using the test token endpoint, you can use **any values** for testing:

### Jan Aadhaar ID
- **Format**: 12 digits
- **Example**: `123456789012`
- **Note**: This is used as the "username" parameter for the test token endpoint

### OTP
- **Format**: 6 digits
- **Example**: `123456`
- **Note**: Currently **NOT validated** - any 6-digit number will work
- The OTP sending is simulated (no actual SMS/email is sent)

## How to Login

1. **Open the login page**: `http://localhost:3000/citizen/login`

2. **Enter Jan Aadhaar ID**: 
   - Type any 12-digit number (e.g., `123456789012`)
   - Click "Send OTP"

3. **Enter OTP**:
   - Type any 6-digit number (e.g., `123456`)
   - Click "Login"

4. **Result**:
   - The system calls `/auth/test-token` endpoint with the Jan Aadhaar ID as username
   - A JWT token is generated and stored
   - You'll be redirected to the dashboard

## Test Examples

### Example 1: Basic Login
```
Jan Aadhaar ID: 123456789012
OTP: 123456
```

### Example 2: Different Values
```
Jan Aadhaar ID: 987654321098
OTP: 654321
```

**All combinations work** - the OTP is not validated in the current implementation.

## What Happens Behind the Scenes

1. **"Send OTP" Click**:
   - Frontend validates Jan Aadhaar ID format (12 digits)
   - Shows "OTP sent" message (simulated)
   - No actual API call is made

2. **"Login" Click**:
   - Frontend validates OTP format (6 digits) - but doesn't verify it
   - Makes API call: `POST /auth/test-token?username={janAadhaarId}`
   - Backend generates JWT token
   - Frontend stores token and tries to fetch user profile
   - Redirects to dashboard

## Backend Endpoint Used

```
POST /citizen/api/v1/auth/test-token?username={janAadhaarId}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzUxMiJ9...",
    "tokenType": "Bearer",
    "username": "123456789012",
    "expiresIn": "24 hours"
  }
}
```

## Important Notes

### ⚠️ Current Limitations

1. **No OTP Validation**: The OTP you enter is not verified
2. **No User Lookup**: The Jan Aadhaar ID is not checked against the database
3. **No SMS/Email**: OTP is not actually sent
4. **Test Token Only**: This is for development/testing only

### ✅ What Works

1. **Token Generation**: JWT tokens are generated correctly
2. **Token Storage**: Tokens are stored in localStorage
3. **API Authentication**: Subsequent API calls include the token
4. **Redirect**: Login redirects to dashboard

## Next Steps (When OTP is Implemented)

When actual OTP endpoints are added to the backend, the flow will be:

1. **Send OTP**:
   ```
   POST /citizen/api/v1/auth/send-otp
   Body: { "janAadhaarId": "123456789012" }
   ```
   - Backend validates Jan Aadhaar ID
   - Generates OTP and sends via SMS/Email
   - Stores OTP temporarily (with expiry)

2. **Verify OTP**:
   ```
   POST /citizen/api/v1/auth/verify-otp
   Body: { "janAadhaarId": "123456789012", "otp": "123456" }
   ```
   - Backend validates OTP
   - Returns JWT token on success

3. **User Profile**:
   - Backend looks up user by Jan Aadhaar ID
   - Returns user profile along with token

## Testing in Swagger UI

You can also test the token endpoint directly in Swagger UI:

1. Open: `http://localhost:8081/citizen/api/v1/swagger-ui.html`
2. Navigate to **Authentication** section
3. Try the **POST /auth/test-token** endpoint
4. Use any username (e.g., `test-user`)
5. Copy the token from the response
6. Click "Authorize" button in Swagger UI
7. Paste the token (format: `Bearer {token}`)
8. Now you can test other endpoints with authentication

## Troubleshooting

### Login Fails
- Check if backend is running on port 8081
- Check browser console for errors
- Verify API base URL is correct (`http://localhost:8081/citizen/api/v1`)

### Token Not Working
- Check localStorage for `auth_token`
- Verify token format (should start with `eyJ`)
- Check if token expired (test tokens last 24 hours)

### Dashboard Not Loading
- Check if user profile fetch is failing
- The login will still work, but profile data might be missing
- Check browser console for API errors

## Summary

**For Testing Right Now**:
- Use **any 12-digit number** as Jan Aadhaar ID
- Use **any 6-digit number** as OTP
- Both will work because validation is simulated

**Example**:
```
Jan Aadhaar ID: 123456789012
OTP: 123456
```

These values will work for testing the current implementation! 🚀

