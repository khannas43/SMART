# Citizen Portal - Menu & Navigation Structure

**Created:** 2024-12-30  
**Purpose:** Draft menu and submenu structure for 20 Citizen Portal screens  
**Status:** Draft - Pending Review

---

## Menu Structure Overview

### Header Layout with Logo

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  [Logo]    [Dashboard] [My Profile ▼] [Schemes ▼] ... [🔔] [👤] [EN/HI] │
│  (120px)                                                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Logo Specifications:**
- **Position:** Top-left corner
- **Image:** National Emblem of India (Lion Capital of Ashoka)
- **Size:** 120px width (desktop), 80px (mobile)
- **Behavior:** Clickable - links to Dashboard
- **File Location:** `/images/logos/smart-logo.png`
- **Styling:** Maintains aspect ratio, proper padding, hover effects

For detailed logo and header specifications, see: `HEADER_LAYOUT_SPECIFICATION.md`

---

## Main Navigation Menu

### Menu Item 1: Dashboard
- **Icon:** 📊 (Dashboard/House icon)
- **Route:** `/citizen/dashboard`
- **Screen:** CIT-PROF-03 (Profile Dashboard & 360° View)
- **Access:** Authenticated
- **Submenu:** None (direct link)

---

### Menu Item 2: My Profile
- **Icon:** 👤 (User/Profile icon)
- **Route:** `/citizen/profile`
- **Access:** Authenticated
- **Submenu:**
  - **Profile Dashboard** → `/citizen/profile/dashboard` (CIT-PROF-03)
    - Summary Tab
    - 360° View Tab
  - **Edit Profile** → `/citizen/profile/edit` (CIT-PROF-04)
    - Edit Tab
    - Verification Tab

---

### Menu Item 3: Schemes
- **Icon:** 📋 (Document/List icon)
- **Route:** `/citizen/schemes`
- **Access:** Authenticated
- **Submenu:**
  - **Browse Schemes** → `/citizen/schemes/browse` (CIT-SCHEME-05)
    - Scheme Catalog & Search
    - AI Recommendations
    - Compare Schemes
  - **Scheme Details** → `/citizen/schemes/:schemeId` (CIT-SCHEME-06)
    - Dynamic route (accessed from browse/details link)
  - **Eligibility Checker** → `/citizen/schemes/eligibility` (CIT-SCHEME-07)
    - Eligibility Questionnaire
    - Live Results Panel

---

### Menu Item 4: My Applications
- **Icon:** 📝 (Application/Form icon)
- **Route:** `/citizen/applications`
- **Access:** Authenticated
- **Submenu:**
  - **Applications Hub** → `/citizen/applications` (CIT-APP-09)
    - Active Applications
    - Past Applications
  - **Consent & Clarifications** → `/citizen/applications/consent` (CIT-CONSENT-08)
    - Scheme Consents
    - Application Clarifications

---

### Menu Item 5: Documents
- **Icon:** 📄 (Document/Folder icon)
- **Route:** `/citizen/documents`
- **Screen:** CIT-DOC-10 (Document Center)
- **Access:** Authenticated
- **Submenu:**
  - **Document Center** → `/citizen/documents` (CIT-DOC-10)
    - Required Documents
    - Personal Library
    - Signed Documents (Raj-e-Sign)
    - e-Vault
    - Downloads

---

### Menu Item 6: Benefits
- **Icon:** 💰 (Money/Benefits icon)
- **Route:** `/citizen/benefits`
- **Access:** Authenticated
- **Submenu:**
  - **Benefits & Entitlements** → `/citizen/benefits` (CIT-BEN-11)
    - Current Benefits
    - Forecast
    - History
  - **Payments & Ledger** → `/citizen/benefits/payments` (CIT-BEN-12)
    - Transactions
    - Ledger Summary

---

### Menu Item 7: Services
- **Icon:** 🛠️ (Tools/Services icon)
- **Route:** `/citizen/services`
- **Access:** Authenticated
- **Submenu:**
  - **Service Catalog** → `/citizen/services/catalog` (CIT-SERV-13)
    - Browse Services
    - Service Categories
  - **Request Service** → `/citizen/services/request` (CIT-SERV-14)
    - Service Request Form
  - **Service Status** → `/citizen/services/status` (CIT-SERV-15)
    - Active Requests
    - Completed Requests
    - Feedback

---

### Menu Item 8: Settings
- **Icon:** ⚙️ (Settings/Gear icon)
- **Route:** `/citizen/settings`
- **Access:** Authenticated
- **Submenu:**
  - **Notification Preferences** → `/citizen/settings/notifications` (CIT-USER-16)
    - Notification Types
    - Channel Selection
    - Quiet Hours
  - **Opt-Out Schemes** → `/citizen/settings/opt-out` (CIT-USER-17)
    - Active Schemes
    - Opt-Out Management
  - **Account & Security** → `/citizen/settings/account` (CIT-USER-18)
    - Profile & Contact
    - Notifications & Consent
    - Password & MFA
    - Sessions & Security

---

### Menu Item 9: Help & Support
- **Icon:** ❓ (Help/Question icon)
- **Route:** `/citizen/help`
- **Access:** Public (some features), Authenticated (full access)
- **Submenu:**
  - **Help Hub** → `/citizen/help` (CIT-HELP-19)
    - FAQs
    - Search
    - Announcements
    - Contact Options
    - Create Ticket
  - **My Tickets** → `/citizen/help/tickets` (CIT-HELP-20)
    - Ticket Status
    - Ticket History
    - Create New Ticket

---

## Secondary Navigation Elements

### Header Components (Always Visible)

1. **Logo/Home Link**
   - Left side of header
   - Click → Navigate to Dashboard (CIT-PROF-03)

2. **Search Bar** (Global Search)
   - Center of header
   - Quick search across schemes, services, help
   - Icon: 🔍

3. **Language Switcher**
   - Top-right area
   - EN/HI dropdown
   - Icon: 🌐

4. **Notifications Icon**
   - Top-right area (bell icon)
   - Badge with unread count
   - Click → Notification Center dropdown
   - Icon: 🔔

5. **User Menu**
   - Top-right area (user avatar/name)
   - Dropdown menu:
     - Profile Dashboard
     - Account Settings
     - Language Preferences
     - Logout

---

## Authentication Screens (Not in Main Menu)

These screens are accessed during authentication flow:

1. **CIT-AUTH-01: Unified Login & SSO**
   - Route: `/citizen/login` or `/login`
   - Access: Public
   - No menu item (standalone page)

2. **CIT-AUTH-02: MFA & Security Challenge**
   - Route: `/citizen/mfa` or `/mfa`
   - Access: Authenticated (step-up auth)
   - No menu item (modal/overlay or separate page)

---

## Complete Route Structure

```
/citizen/
├── /login                          # CIT-AUTH-01 (Public)
├── /mfa                            # CIT-AUTH-02 (Authenticated - step-up)
│
├── /dashboard                      # CIT-PROF-03 (Authenticated)
│
├── /profile                        # Profile Section
│   ├── /dashboard                  # CIT-PROF-03 (Summary & 360° View)
│   └── /edit                       # CIT-PROF-04 (Edit & Verification)
│
├── /schemes                        # Schemes Section
│   ├── /browse                     # CIT-SCHEME-05 (Catalog & Search)
│   ├── /eligibility                # CIT-SCHEME-07 (Eligibility Checker)
│   └── /:schemeId                  # CIT-SCHEME-06 (Scheme Details - dynamic)
│
├── /applications                   # Applications Section
│   ├── /                           # CIT-APP-09 (Applications Hub)
│   └── /consent                    # CIT-CONSENT-08 (Consent & Clarifications)
│
├── /documents                      # CIT-DOC-10 (Document Center)
│   └── /                           # All document types in one screen
│
├── /benefits                       # Benefits Section
│   ├── /                           # CIT-BEN-11 (Benefits & Entitlements)
│   └── /payments                   # CIT-BEN-12 (Payments & Ledger)
│
├── /services                       # Services Section
│   ├── /catalog                    # CIT-SERV-13 (Service Catalog)
│   ├── /request                    # CIT-SERV-14 (Service Request)
│   └── /status                     # CIT-SERV-15 (Service Status & Feedback)
│
├── /settings                       # Settings Section
│   ├── /notifications              # CIT-USER-16 (Notification Preferences)
│   ├── /opt-out                    # CIT-USER-17 (Opt-Out Schemes)
│   └── /account                    # CIT-USER-18 (Account & Security)
│
└── /help                           # Help & Support Section
    ├── /                           # CIT-HELP-19 (Help Hub)
    └── /tickets                    # CIT-HELP-20 (Tickets & Status)
```

---

## Mobile Navigation (Hamburger Menu)

For mobile devices (< 768px), the main menu collapses into a hamburger menu:

```
┌─────────────────────────┐
│ ☰ Menu                  │  ← Hamburger Icon
└─────────────────────────┘
    ↓ (When opened)
┌─────────────────────────┐
│ Dashboard               │
│ My Profile              │
│   → Profile Dashboard   │
│   → Edit Profile        │
│ Schemes                 │
│   → Browse Schemes      │
│   → Eligibility Checker │
│ My Applications         │
│   → Applications Hub    │
│   → Consent             │
│ Documents               │
│ Benefits                │
│   → Benefits            │
│   → Payments            │
│ Services                │
│   → Service Catalog     │
│   → Request Service     │
│   → Service Status      │
│ Settings                │
│   → Notifications       │
│   → Opt-Out             │
│   → Account             │
│ Help & Support          │
│   → Help Hub            │
│   → My Tickets          │
│                         │
│ [Language: EN/HI]       │
│ [Notifications 🔔]       │
│ [Logout]                │
└─────────────────────────┘
```

---

## Menu Item Details

### 1. Dashboard
- **Label (EN):** "Dashboard"
- **Label (HI):** "डैशबोर्ड"
- **Icon:** Home/Dashboard icon
- **Badge:** None
- **Route:** `/citizen/dashboard`
- **Access:** Authenticated only
- **Quick Access:** Click logo to return to dashboard

---

### 2. My Profile
- **Label (EN):** "My Profile"
- **Label (HI):** "मेरी प्रोफ़ाइल"
- **Icon:** User/Profile icon
- **Badge:** Verification status indicator (optional)
- **Route:** `/citizen/profile`
- **Access:** Authenticated only
- **Submenu Items:**
  - **Profile Dashboard** (EN) / "प्रोफ़ाइल डैशबोर्ड" (HI)
    - Route: `/citizen/profile/dashboard`
    - Tabs: Summary, 360° View
  - **Edit Profile** (EN) / "प्रोफ़ाइल संपादित करें" (HI)
    - Route: `/citizen/profile/edit`
    - Tabs: Edit, Verification

---

### 3. Schemes
- **Label (EN):** "Schemes"
- **Label (HI):** "योजनाएं"
- **Icon:** Document/List icon
- **Badge:** Count of eligible schemes (optional)
- **Route:** `/citizen/schemes`
- **Access:** Authenticated (full), Public (limited browse)
- **Submenu Items:**
  - **Browse Schemes** (EN) / "योजनाएं ब्राउज़ करें" (HI)
    - Route: `/citizen/schemes/browse`
    - Features: Search, Filter, AI Recommendations, Compare
  - **Eligibility Checker** (EN) / "पात्रता जांचकर्ता" (HI)
    - Route: `/citizen/schemes/eligibility`
    - Features: Questionnaire, Live Results

---

### 4. My Applications
- **Label (EN):** "My Applications"
- **Label (HI):** "मेरे आवेदन"
- **Icon:** Application/Form icon
- **Badge:** Count of pending applications (optional)
- **Route:** `/citizen/applications`
- **Access:** Authenticated only
- **Submenu Items:**
  - **Applications Hub** (EN) / "आवेदन हब" (HI)
    - Route: `/citizen/applications`
    - Sections: Active, Past
  - **Consent & Clarifications** (EN) / "सहमति और स्पष्टीकरण" (HI)
    - Route: `/citizen/applications/consent`
    - Sections: Scheme Consents, Application Clarifications

---

### 5. Documents
- **Label (EN):** "Documents"
- **Label (HI):** "दस्तावेज़"
- **Icon:** Document/Folder icon
- **Badge:** Count of pending uploads (optional)
- **Route:** `/citizen/documents`
- **Access:** Authenticated only
- **Submenu:** None (single screen with multiple panes)
- **Note:** Document Center (CIT-DOC-10) is a unified screen with 5 panes (Required, Library, Signed, e-Vault, Download)

---

### 6. Benefits
- **Label (EN):** "Benefits"
- **Label (HI):** "लाभ"
- **Icon:** Money/Benefits icon
- **Badge:** None
- **Route:** `/citizen/benefits`
- **Access:** Authenticated only
- **Submenu Items:**
  - **Benefits & Entitlements** (EN) / "लाभ और पात्रता" (HI)
    - Route: `/citizen/benefits`
    - Sections: Current, Forecast, History
  - **Payments & Ledger** (EN) / "भुगतान और खाता" (HI)
    - Route: `/citizen/benefits/payments`
    - Sections: Transactions, Ledger

---

### 7. Services
- **Label (EN):** "Services"
- **Label (HI):** "सेवाएं"
- **Icon:** Tools/Services icon
- **Badge:** Count of active service requests (optional)
- **Route:** `/citizen/services`
- **Access:** Authenticated only
- **Submenu Items:**
  - **Service Catalog** (EN) / "सेवा कैटलॉग" (HI)
    - Route: `/citizen/services/catalog`
    - Features: Browse, Search, Categories
  - **Request Service** (EN) / "सेवा अनुरोध करें" (HI)
    - Route: `/citizen/services/request`
    - Dynamic form per service type
  - **Service Status** (EN) / "सेवा स्थिति" (HI)
    - Route: `/citizen/services/status`
    - Sections: Active, Completed, Feedback

---

### 8. Settings
- **Label (EN):** "Settings"
- **Label (HI):** "सेटिंग्स"
- **Icon:** Settings/Gear icon
- **Badge:** None
- **Route:** `/citizen/settings`
- **Access:** Authenticated only
- **Submenu Items:**
  - **Notifications** (EN) / "अधिसूचनाएं" (HI)
    - Route: `/citizen/settings/notifications`
    - Features: Channel selection, Quiet hours
  - **Opt-Out Schemes** (EN) / "योजनाएं से बाहर निकलें" (HI)
    - Route: `/citizen/settings/opt-out`
    - Features: Scheme opt-out management
  - **Account & Security** (EN) / "खाता और सुरक्षा" (HI)
    - Route: `/citizen/settings/account`
    - Sections: Profile, Notifications, Password & MFA, Sessions

---

### 9. Help & Support
- **Label (EN):** "Help & Support"
- **Label (HI):** "सहायता और समर्थन"
- **Icon:** Help/Question icon
- **Badge:** Count of active tickets (optional)
- **Route:** `/citizen/help`
- **Access:** Public (limited), Authenticated (full)
- **Submenu Items:**
  - **Help Hub** (EN) / "सहायता हब" (HI)
    - Route: `/citizen/help`
    - Features: FAQs, Search, Announcements, Contact, Create Ticket
  - **My Tickets** (EN) / "मेरे टिकट" (HI)
    - Route: `/citizen/help/tickets`
    - Features: Ticket Status, History, Create New

---

## Breadcrumb Navigation

Each page (except Dashboard) should show breadcrumbs:

**Example 1:**
```
Home > Schemes > Browse Schemes
```

**Example 2:**
```
Home > My Applications > Consent & Clarifications
```

**Example 3:**
```
Home > Settings > Account & Security
```

---

## Quick Actions (Dashboard Widgets)

The Dashboard (CIT-PROF-03) should have quick action buttons/links:

1. **Quick Links:**
   - "Browse Schemes" → `/citizen/schemes/browse`
   - "Check Eligibility" → `/citizen/schemes/eligibility`
   - "My Applications" → `/citizen/applications`
   - "Upload Documents" → `/citizen/documents`
   - "View Benefits" → `/citizen/benefits`
   - "Help & Support" → `/citizen/help`

2. **Status Indicators:**
   - Pending Applications count
   - Pending Documents count
   - Active Benefits count
   - Unread Notifications count

---

## Menu Icons Reference

| Menu Item | Icon (Unicode) | Alternative Icon |
|-----------|---------------|------------------|
| Dashboard | 🏠 📊 | Home, Dashboard |
| My Profile | 👤 | User, Person |
| Schemes | 📋 📄 | Document, List |
| My Applications | 📝 ✅ | Form, Application |
| Documents | 📁 📄 | Folder, Document |
| Benefits | 💰 💵 | Money, Currency |
| Services | 🛠️ ⚙️ | Tools, Services |
| Settings | ⚙️ 🔧 | Gear, Settings |
| Help & Support | ❓ 💬 | Question, Chat |

---

## Accessibility Considerations

1. **Keyboard Navigation:**
   - Tab key navigates through menu items
   - Enter/Space activates menu item
   - Arrow keys navigate submenu items
   - Esc closes submenu

2. **Screen Reader Support:**
   - ARIA labels on all menu items
   - ARIA-expanded for submenus
   - ARIA-current for active page

3. **Visual Indicators:**
   - Highlight active menu item
   - Show active submenu item
   - Breadcrumb trail for current location

---

## Mobile-Specific Considerations

1. **Hamburger Menu:**
   - Collapse main menu into hamburger icon (< 768px)
   - Slide-in drawer menu
   - Overlay when menu is open

2. **Bottom Navigation (Optional):**
   - For mobile: Fixed bottom navigation bar
   - Show 5 key items: Dashboard, Schemes, Applications, Benefits, More (settings/help)

3. **Swipe Gestures:**
   - Swipe left/right to navigate
   - Pull down to refresh (where applicable)

---

## Menu State Management

**Menu States:**
- **Collapsed:** Mobile view, hamburger menu
- **Expanded:** Desktop view, full menu
- **Submenu Open:** When hovering/clicking parent menu item
- **Active State:** Current page highlighted

**Menu Behavior:**
- Desktop: Hover to show submenu, click to navigate
- Mobile: Tap to expand submenu, tap again to navigate
- Touch devices: Tap to expand, tap outside to collapse

---

## Implementation Notes

1. **Menu Component Structure:**
   ```typescript
   - Header Component
     - Logo
     - MainMenu Component
       - MenuItem Components (with submenus)
     - SearchBar
     - LanguageSwitcher
     - NotificationsIcon
     - UserMenu
   ```

2. **Routing Integration:**
   - Use React Router for navigation
   - Active route detection for menu highlighting
   - Protected routes for authenticated pages

3. **Responsive Breakpoints:**
   - Desktop: > 1024px (Full menu)
   - Tablet: 768px - 1024px (Collapsible menu)
   - Mobile: < 768px (Hamburger menu)

---

**Status:** Draft - Ready for Review  
**Next Steps:**
1. Review menu structure with stakeholders
2. Confirm icon choices
3. Validate route structure
4. Review mobile navigation approach
5. Finalize menu labels in both languages

