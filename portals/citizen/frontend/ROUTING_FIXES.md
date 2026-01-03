# Routing and Path Fixes

## Issues Fixed

### 1. Logo Path ✅
**Problem**: Logo wasn't loading because path didn't account for base path `/citizen/`

**Fix**: Changed from `/images/logos/smart-logo.png` to `/citizen/images/logos/smart-logo.png`

**File**: `src/components/layout/Header.tsx`

### 2. Translation Keys ✅
**Problem**: Translation keys in LoginPage didn't match the structure in `auth.json`

**Fixed Keys**:
- `auth.login_screen_title` → `auth.title`
- `auth.jan_aadhaar_id` → `auth.janAadhaarLogin`
- `auth.enter_jan_aadhaar` → `auth.enterJanAadhaar`
- `auth.send_otp` → `auth.sendOTP`
- `auth.enter_otp` → `auth.enterOTP`
- `auth.resend_otp` → `auth.resendOTP`
- `auth.login_with_raj_sso` → `auth.loginWithRajSSO`
- `auth.forgot_jan_aadhaar` → `auth.forgotJanAadhaar`
- `auth.need_help` → `auth.needHelp`

**File**: `src/pages/auth/LoginPage.tsx`

### 3. Route Paths ✅
**Problem**: Routes were using `/citizen/` prefix, but BrowserRouter already has `basename="/citizen"`, causing double `/citizen/citizen/` in URLs

**Fix**: Removed `/citizen/` prefix from all routes since `basename="/citizen"` in BrowserRouter handles it

**Example Changes**:
- `/citizen/login` → `/login`
- `/citizen/dashboard` → `/dashboard`
- `/citizen/profile` → `/profile`

**Files Updated**:
- `src/App.tsx` - Route definitions
- `src/components/layout/Header.tsx` - Navigation links
- `src/components/layout/Footer.tsx` - Footer links
- `src/pages/auth/LoginPage.tsx` - Navigation after login
- `src/pages/TermsAndConditions.tsx` - Back button
- `src/pages/Sitemap.tsx` - All sitemap links

## How It Works

With `basename="/citizen"` in BrowserRouter:
- React Router handles the `/citizen` prefix automatically
- Routes defined as `/login` become `/citizen/login` in the browser
- Links using `<Link to="/dashboard">` navigate to `/citizen/dashboard`
- No need to manually add `/citizen/` prefix in routes or links

## Testing

After these fixes:
1. ✅ Logo should display in header
2. ✅ Translation text should show instead of keys
3. ✅ URLs should be `http://localhost:3000/citizen/login` (not `/citizen/citizen/login`)
4. ✅ Navigation should work correctly
5. ✅ All links should navigate properly

## Notes

- Static assets (images, etc.) in `public/` folder need `/citizen/` prefix in `src` attributes
- Routes and navigation links should NOT include `/citizen/` prefix
- BrowserRouter `basename` handles the prefix automatically

