# Citizen Portal - i18n & PWA Alignment Checklist

**Created:** 2024-12-30  
**Purpose:** Address alignment questions for English/Hindi i18n and PWA development  
**Status:** Review & Action Items

---

## Question 1: English and Hindi Language Support

### Current Status

✅ **Already Aligned:**
- i18n structure exists: `portals/citizen/i18n/locales/`
- Tech stack includes: `i18next` for internationalization
- SRS mentions: "Hindi, English, Rajasthani (RTL support)"
- Screen specifications reference multi-language support

### Required Items for English + Hindi Only

#### ✅ **Already Planned:**
1. **Translation Files Structure**
   - `portals/citizen/i18n/locales/en/` - English translations
   - `portals/citizen/i18n/locales/hi/` - Hindi translations
   - Format: JSON files per module/screen (e.g., `auth.json`, `profile.json`, `schemes.json`)

2. **Frontend i18n Implementation**
   - React i18next library integration
   - Language switcher component
   - Language detection (browser/device preference)
   - Language persistence (localStorage/cookies)

3. **Backend i18n Support**
   - API response language headers
   - Error message translations
   - Email/SMS template translations
   - Document template translations

#### ⚠️ **Additional Items Required:**

1. **Hindi Font Support**
   - **Required:** Include Hindi fonts (Devanagari script) in frontend
   - **Recommendation:** Use web-safe fonts like:
     - Noto Sans Devanagari (Google Fonts)
     - Mangal (Windows system font)
     - Arial Unicode MS (fallback)
   - **Action:** Add font loading in `frontend/public/index.html` or CSS

2. **Hindi Typography & Layout**
   - **Required:** Test text rendering for Hindi (Devanagari script)
   - **Required:** Verify proper line-height and spacing for Hindi text
   - **Note:** Hindi text may require different line-height than English
   - **Action:** Add Hindi-specific CSS rules if needed

3. **RTL (Right-to-Left) Support**
   - **Current:** SRS mentions "RTL support" but for Rajasthani
   - **For Hindi:** Hindi is LTR (left-to-right) like English
   - **Status:** ✅ No RTL needed for English + Hindi only
   - **Note:** If Rajasthani is added later, RTL support will be needed

4. **Translation Coverage**
   - **Required:** All 20 screens need English + Hindi translations
   - **Translation Files Needed:**
     ```
     portals/citizen/i18n/locales/en/
       ├── common.json          # Common terms (buttons, labels, errors)
       ├── auth.json            # Authentication screens
       ├── profile.json         # Profile screens
       ├── schemes.json         # Scheme discovery screens
       ├── applications.json    # Application screens
       ├── documents.json       # Document screens
       ├── benefits.json        # Benefits screens
       ├── services.json        # Service delivery screens
       ├── settings.json        # Settings screens
       └── help.json            # Help & support screens
     
     portals/citizen/i18n/locales/hi/
       └── [same structure]
     ```
   - **Action:** Create translation file template structure

5. **AI/ML Content Translation**
   - **Required:** AI/ML-generated content (explanations, recommendations) needs translation
   - **Affected Use Cases:**
     - AI-PLATFORM-08: Eligibility explanations need Hindi translation
     - AI-PLATFORM-11: Nudge messages need Hindi translation
     - AI-PLATFORM-03: Scheme recommendations descriptions
   - **Action:** Coordinate with AI/ML team on content translation strategy

6. **Date/Time/Number Formatting**
   - **Required:** Localized date/time formats
   - **Required:** Number formatting (Indian numbering system)
   - **Example:** ₹1,23,456.78 (Indian) vs ₹123,456.78 (US)
   - **Action:** Use `Intl` API or library (e.g., `date-fns` with locale support)

7. **Language Selector UI**
   - **Required:** Language switcher in header/navigation
   - **Design:** Dropdown or toggle (EN/HI)
   - **Placement:** Top-right corner (standard location)
   - **Persistence:** Remember user preference

8. **Backend API Language Headers**
   - **Required:** Accept-Language header support
   - **Required:** API responses return language-appropriate content
   - **Action:** Backend services need to handle `Accept-Language` header

9. **Email/SMS Templates**
   - **Required:** OTP messages in Hindi
   - **Required:** Notification templates in both languages
   - **Action:** Create Hindi templates for all notification types

10. **Document Templates**
    - **Required:** Generated PDFs/documents need Hindi support
    - **Examples:** Application receipts, certificates, decision letters
    - **Action:** PDF generation library with Hindi font support

---

## Question 2: PWA (Progressive Web App) Alignment

### Current Status

✅ **Partially Aligned:**
- Documentation mentions "Mobile-compatible"
- SRS mentions "Mobile-first" design
- PWA cache mentioned (24h TTL with staleness indicator)
- Offline support mentioned (PWA sync queue)
- Responsive breakpoints defined

⚠️ **Missing PWA Implementation Details:**

### Required Items for PWA Development

#### 1. **PWA Manifest File**
   - **Required:** `manifest.json` file in `frontend/public/`
   - **Contents:**
     ```json
     {
       "name": "SMART Citizen Portal",
       "short_name": "SMART Citizen",
       "description": "Rajasthan Government Citizen Portal",
       "start_url": "/citizen/",
       "display": "standalone",
       "background_color": "#ffffff",
       "theme_color": "#1976d2",
       "orientation": "portrait-primary",
       "icons": [
         {
           "src": "/icons/icon-72x72.png",
           "sizes": "72x72",
           "type": "image/png",
           "purpose": "any maskable"
         },
         // More icon sizes: 96, 128, 144, 152, 192, 384, 512
       ]
     }
     ```
   - **Action:** Create manifest.json with proper icons

2. **Service Worker**
   - **Required:** Service worker for offline support and caching
   - **Strategies Needed:**
     - **Cache First:** Static assets (JS, CSS, images, fonts)
     - **Network First with Cache Fallback:** API responses
     - **Stale-While-Revalidate:** Dynamic content
   - **Action:** Implement service worker with workbox or custom implementation

3. **App Icons**
   - **Required:** Multiple icon sizes for different devices
   - **Sizes Needed:**
     - 72x72, 96x96, 128x128, 144x144 (Android)
     - 152x152, 192x192, 384x384, 512x512 (iOS/Android)
     - 180x180 (Apple touch icon)
   - **Format:** PNG with transparent background
   - **Action:** Generate app icons in all required sizes

4. **Offline Support Strategy**
   - **Required:** Define what works offline
   - **Offline Capabilities:**
     - ✅ View cached pages (previously visited)
     - ✅ View cached scheme details
     - ✅ View cached profile data
     - ✅ View cached application status
     - ⚠️ **Cannot Work Offline:**
       - Submit new applications
       - Upload documents
       - Make payments
       - Real-time eligibility checks
   - **Action:** Implement offline detection and UI indicators

5. **App Installation Prompts**
   - **Required:** "Add to Home Screen" prompt
   - **Trigger Conditions:**
     - User visits portal multiple times
     - User engages with portal (scroll, click)
     - Not already installed
   - **Action:** Implement beforeinstallprompt event handling

6. **Push Notifications (Optional but Recommended)**
   - **Required for PWA Best Practices:** Web Push API
   - **Use Cases:**
     - Application status updates
     - Payment confirmations
     - Eligibility notifications
     - Deadline reminders
   - **Action:** Implement push notification service worker registration

7. **Background Sync**
   - **Recommended:** Background sync for offline actions
   - **Use Cases:**
     - Queue form submissions when offline
     - Sync document uploads when connection restored
   - **Action:** Implement Background Sync API for critical actions

8. **Responsive Design Verification**
   - **Required:** Test on various screen sizes
   - **Breakpoints:**
     - Mobile: < 480px
     - Tablet: 480px - 1024px
     - Desktop: > 1024px
   - **Action:** Ensure all 20 screens work on mobile devices

9. **Mobile-Specific Features**
   - **Required:** Touch gestures support
   - **Examples:**
     - Swipe navigation (already mentioned in SRS)
     - Pull to refresh
     - Long press for context menus
   - **Action:** Implement gesture handlers

10. **Performance Optimization for Mobile**
    - **Required:** Lazy loading for images
    - **Required:** Code splitting for faster initial load
    - **Required:** Optimize bundle size (< 200KB initial bundle)
    - **Target:** Lighthouse PWA score > 90
    - **Action:** Implement performance optimizations

11. **HTTPS Requirement**
    - **Required:** PWA requires HTTPS (or localhost for development)
    - **Status:** ✅ Should be standard for production
    - **Action:** Ensure HTTPS is configured in production

12. **PWA Testing**
    - **Required:** Test PWA installation on:
      - Android Chrome
      - iOS Safari
      - Desktop Chrome/Edge
    - **Required:** Test offline functionality
    - **Required:** Test push notifications
    - **Action:** Create PWA testing checklist

---

## Summary Checklist

### For English + Hindi i18n:

- [x] i18n structure exists
- [x] i18next library planned
- [ ] **Hindi fonts added to frontend**
- [ ] **Translation files created (20 screens worth)**
- [ ] **Language selector UI implemented**
- [ ] **Backend Accept-Language header support**
- [ ] **Email/SMS templates in Hindi**
- [ ] **Date/time/number formatting (Indian locale)**
- [ ] **AI/ML content translation strategy**
- [ ] **PDF/document generation with Hindi support**

### For PWA Development:

- [x] Mobile-first design mentioned
- [x] Responsive breakpoints defined
- [ ] **manifest.json created**
- [ ] **Service worker implemented**
- [ ] **App icons generated (all sizes)**
- [ ] **Offline support strategy defined and implemented**
- [ ] **Installation prompts implemented**
- [ ] **Push notifications (optional)**
- [ ] **Background sync (optional)**
- [ ] **PWA testing completed**
- [ ] **Performance optimization for mobile**

---

## Recommended Next Steps

1. **i18n Implementation:**
   - Create translation file structure template
   - Add Hindi fonts to frontend
   - Implement language switcher component
   - Coordinate with AI/ML team on content translation

2. **PWA Implementation:**
   - Create manifest.json
   - Generate app icons
   - Implement service worker
   - Define offline support boundaries
   - Test PWA installation on devices

3. **Documentation Updates:**
   - Update TECHNICAL_ARCHITECTURE.md with PWA details
   - Add i18n implementation guide
   - Create PWA deployment checklist

---

**Note:** Both English+Hindi i18n and PWA are fully achievable with the current tech stack (React + TypeScript). The main work is implementation, not architecture changes.

