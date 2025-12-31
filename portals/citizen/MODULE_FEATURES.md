# Citizen Portal - Module Features & Requirements

This document provides detailed feature requirements for each module, based on the screen specifications.

## Module 1: Authentication & Profile

### Screen: CIT-AUTH-01 - Login Screen
**Requirements:**
- Jan Aadhaar ID input field with validation
- OTP delivery mechanism (SMS/Email)
- Biometric authentication support (fingerprint, face recognition)
- Multi-language UI support (English, Hindi, Rajasthani)
- Forgot password/reset functionality
- Remember me option
- Secure session management
- Error handling and user feedback

**Technical Needs:**
- Integration with Jan Aadhaar API
- OTP service integration
- Biometric SDK integration (device-specific)
- i18n implementation
- Session storage/cookies

### Screen: CIT-AUTH-02 - Raj SSO Login
**Requirements:**
- Rajasthan Single Sign-On integration
- Token exchange mechanism
- Alternative login options (fallback)
- OAuth 2.0/OIDC protocol support
- Redirect handling
- Token storage and management

**Technical Needs:**
- Raj SSO API integration
- OAuth 2.0 client implementation
- Token management service
- SSO configuration

### Screen: CIT-AUTH-03 - MFA Verification
**Requirements:**
- OTP-based MFA
- TOTP app support (Google Authenticator, Authy)
- Biometric MFA
- Backup codes generation
- MFA device management
- Skip MFA option (configurable)

**Technical Needs:**
- TOTP generation and validation
- QR code generation for TOTP setup
- Biometric verification
- Backup code storage

### Screen: CIT-PROF-04 - Profile Dashboard
**Requirements:**
- Consolidated citizen profile display
- Family snapshot (up to 3 levels)
- Key benefits summary
- Active notifications
- Quick actions
- Recent activity feed
- Profile completion indicator

**Technical Needs:**
- Profile aggregation API
- Family relationship data structure
- Benefits aggregation service
- Real-time notification updates

### Screen: CIT-PROF-05 - Edit Profile
**Requirements:**
- Form-based profile editing
- Field-level validation
- Document upload for profile updates
- Re-verification workflow triggers
- Save draft functionality
- Change history tracking
- Confirmation dialogs for critical changes

**Technical Needs:**
- Profile update API
- Validation rules engine
- Document upload integration
- Version history tracking

### Screen: CIT-PROF-06 - Profile Verification Status
**Requirements:**
- Field-level verification status display
- Source of verification details
- Pending verification alerts
- Re-verification requests
- Verification timeline/history
- Action buttons for pending items

**Technical Needs:**
- Verification status tracking
- Source system integration
- Alert generation system
- Status update workflow

---

## Module 2: Scheme Discovery

### Screen: CIT-SCHEME-07 - Browse All Schemes
**Requirements:**
- Grid/list view of schemes
- Category-based filtering
- Eligibility-based filtering
- AI-driven personalized suggestions
- Sorting options (date, relevance, popularity)
- Pagination or infinite scroll
- Scheme card with key information
- Bookmark/watchlist feature

**Technical Needs:**
- Scheme catalog API
- Filtering and search service
- AI recommendation engine integration
- Bookmark storage

### Screen: CIT-SCHEME-08 - Scheme Details
**Requirements:**
- Comprehensive scheme information
- Eligibility criteria display
- Benefits breakdown
- Required documents list
- Application process steps
- Apply button with eligibility check
- Related schemes suggestions
- FAQs section
- Contact information

**Technical Needs:**
- Scheme detail API
- Eligibility checking service
- Document requirement service
- Related scheme recommendation

### Screen: CIT-SCHEME-09 - Search & Filter
**Requirements:**
- Advanced search bar with autocomplete
- Multi-criteria filtering:
  - Category
  - Eligibility status
  - Department
  - Benefit type
  - Age group
  - Income criteria
- Sort options
- Save filter preferences
- Recent searches
- Search suggestions

**Technical Needs:**
- Search API with autocomplete
- Advanced filtering service
- Preference storage
- Search analytics

### Screen: CIT-SCHEME-10 - Eligibility Checker
**Requirements:**
- Interactive questionnaire
- Progressive disclosure (show relevant questions)
- Real-time eligibility calculation
- Explanation of eligibility/ineligibility
- Missing criteria highlighting
- Recommendations for improving eligibility
- Save progress functionality
- Results visualization

**Technical Needs:**
- AI-powered eligibility engine
- Questionnaire management system
- Real-time calculation service
- Explanation generation service

### Screen: CIT-SCHEME-11 - Personalized Recommendations
**Requirements:**
- AI-driven scheme suggestions
- Explanation of why schemes are recommended
- Save/watchlist features
- Recommendation refresh
- Filter recommendations
- Dismiss recommendations
- Recommendation preferences
- Category-based grouping

**Technical Needs:**
- AI recommendation engine
- Personalization algorithm
- User preference tracking
- Recommendation scoring

### Screen: CIT-SCHEME-12 - Eligible and Recommendation Schemes
**Requirements:**
- Filtered list by eligibility status
- AI assessment indicators
- Bookmark functionality
- Dynamic updates when eligibility changes
- Comparison view
- Bulk actions (save multiple)
- Export eligible schemes
- Eligibility expiry warnings

**Technical Needs:**
- Eligibility assessment service
- Real-time eligibility updates
- Bookmark management
- Comparison engine

---

## Module 3: Consent & Application

### Screen: CIT-CONSENT-13 - Consent Submission
**Requirements:**
- Explicit consent collection forms
- Scheme-specific consent
- Data sharing consent options
- Digital signature support
- OTP verification for consent
- Consent terms and conditions display
- Consent history
- Revoke consent option

**Technical Needs:**
- Consent management service
- Digital signature integration
- OTP verification
- Consent storage and audit

### Screen: CIT-APP-14 - Application Tracking
**Requirements:**
- Real-time status updates
- Status timeline/flow visualization
- Application details view
- Filter by status, scheme, date
- Search applications
- Status notifications
- Download application receipt
- Status change history

**Technical Needs:**
- Application status API
- Real-time update mechanism (WebSocket/SSE)
- Status workflow engine
- Notification triggers

### Screen: CIT-DOC-15 - Document Upload
**Requirements:**
- Multi-file upload
- Drag-and-drop interface
- File type validation
- File size validation
- Upload progress indicators
- Document preview
- Document status tracking
- Re-upload option
- Document deletion (if allowed)

**Technical Needs:**
- File upload service
- File validation service
- Document storage (local/S3)
- Document metadata management

### Screen: CIT-CLAR-16 - Clarification Form
**Requirements:**
- Response form for clarification requests
- Question/requirement display
- Document attachment support
- Deadline tracking and warnings
- Save draft functionality
- Submit confirmation
- Response history
- Deadline extension requests

**Technical Needs:**
- Clarification management service
- Deadline tracking system
- Document attachment
- Notification service

### Screen: CIT-APP-17 - Application History
**Requirements:**
- Historical application records
- Advanced filtering
- Search functionality
- Detailed view for each application
- Export history
- Timeline view
- Status-based grouping
- Statistics/summary view

**Technical Needs:**
- Application history API
- Filtering and search service
- Export functionality
- Analytics aggregation

---

## Module 4: Benefits & Entitlements

### Screen: CIT-BEN-18 - Current Benefits Dashboard
**Requirements:**
- Summary of active schemes
- Benefits overview cards
- Drill-down to details
- Alert notifications
- Benefit status indicators
- Payment information
- Upcoming benefits
- Quick actions

**Technical Needs:**
- Benefits aggregation service
- Real-time status updates
- Alert generation
- Dashboard data API

### Screen: CIT-PROF-360 - 360-Degree Profile
**Requirements:**
- Interactive profile visualization
- Family network visualization (up to 3 levels)
- Scheme participation aggregation
- Relationship mapping
- Profile completeness indicators
- Family member benefits view
- Interactive navigation
- Export profile view

**Technical Needs:**
- Family relationship data structure
- Graph/network visualization library
- Profile aggregation service
- Family benefits aggregation

### Screen: CIT-BEN-19 - DBT Payment Tracking
**Requirements:**
- Direct Benefit Transfer payment list
- Payment status indicators
- Payment amount and date
- Filtering options
- Download payment receipts
- Payment alerts
- Payment calendar view
- Expected payment dates

**Technical Needs:**
- DBT system integration
- Payment tracking API
- Receipt generation
- Alert service

### Screen: CIT-BEN-20 - Annual Ledger View
**Requirements:**
- Month/year-wise benefit ledger
- Payment breakdown
- Category-wise grouping
- Export functionality (PDF/Excel)
- Drill-down capabilities
- Summary statistics
- Comparison views
- Graphical representation

**Technical Needs:**
- Ledger aggregation service
- Export service (PDF/Excel generation)
- Chart/graph library
- Data aggregation queries

### Screen: CIT-BEN-21 - Family Benefits View
**Requirements:**
- Consolidated family-level benefits
- Family member selection/filtering
- Alerts for family members
- Profile links to family members
- Family benefit summary
- Comparative view
- Export family benefits

**Technical Needs:**
- Family data aggregation
- Family relationship service
- Benefit aggregation by family
- Alert aggregation

### Screen: CIT-BEN-22 - Historical Benefits
**Requirements:**
- Past benefits data
- Trend visualization
- Export functionality
- Advanced filtering
- Graphical representation
- Year-over-year comparison
- Benefit category breakdown

**Technical Needs:**
- Historical data service
- Analytics aggregation
- Chart/graph library
- Export service

### Screen: CIT-BEN-23 - Personal Entitlement Forecast
**Requirements:**
- AI-driven eligibility forecasts
- Benefit predictions
- Scenario comparisons
- Forecast timeline
- Confidence indicators
- Assumptions display
- Action recommendations
- Forecast accuracy feedback

**Technical Needs:**
- AI forecasting service
- ML model integration
- Scenario engine
- Forecast storage and tracking

---

## Module 5: Documents & Certificates

### Screen: CIT-DOC-24 - Document Library
**Requirements:**
- Document list/grid view
- Search functionality
- Filter by type, date, status
- Document preview
- Sharing functionality
- Expiry alerts
- Document metadata display
- Bulk actions

**Technical Needs:**
- Document management service
- Search and filter service
- Preview service
- Sharing service
- Alert service for expiry

### Screen: CIT-DOC-25 - Download Documents
**Requirements:**
- Secure PDF download
- Bulk download option
- Download history
- Audit logging
- Download permissions check
- Download links expiration
- Download queue for bulk operations

**Technical Needs:**
- Secure download service
- PDF generation service
- Audit logging service
- Permission checking

### Screen: CIT-DOC-26 - e-Vault Integration
**Requirements:**
- e-Vault document access
- Upload to e-Vault
- Download from e-Vault
- Document versioning
- Consent controls
- Document metadata sync
- e-Vault authentication

**Technical Needs:**
- e-Vault API integration
- Version control system
- Consent management
- Authentication integration

### Screen: CIT-DOC-27 - Digital Signature View
**Requirements:**
- View digitally signed documents
- Real-time signature validation
- Signature details display
- Signer information
- Signature timestamp
- Audit log display
- Signature status indicators

**Technical Needs:**
- Digital signature validation service
- Certificate validation
- Audit logging
- Signature parsing

---

## Module 6: 24 Hours Service Delivery

### Screen: CIT-SERV-28 - Service Catalog
**Requirements:**
- Browse government services
- Categorization
- Search functionality
- Filtering options
- Multi-language support
- Service details
- Service availability status
- Quick links

**Technical Needs:**
- Service catalog API
- Categorization service
- Search service
- i18n support

### Screen: CIT-SERV-29 - Service Request Form
**Requirements:**
- Multi-step form wizard
- Form validation
- Document uploads
- Save draft functionality
- Form progress indicator
- Conditional fields
- Auto-fill from profile
- Submit confirmation

**Technical Needs:**
- Form builder service
- Validation engine
- Document upload
- Draft storage

### Screen: CIT-SERV-30 - Service Request Status
**Requirements:**
- Real-time status tracking
- Timeline visualization
- Filter by status, service type, date
- Download service documents
- Status change notifications
- Expected completion time
- Escalation option

**Technical Needs:**
- Status tracking service
- Real-time updates (WebSocket/SSE)
- Timeline generation
- Notification service

### Screen: CIT-SERV-31 - Service Feedback
**Requirements:**
- Feedback form
- Rating system (stars/numbers)
- Anonymous feedback option
- Content moderation
- Feedback categories
- Attachment support
- Feedback history
- Thank you confirmation

**Technical Needs:**
- Feedback service
- Rating system
- Content moderation service
- Notification service

---

## Module 7: Notifications

### Screen: CIT-USER-35 - Notification Settings
**Requirements:**
- Manage notification preferences
- Channel selection (Email, SMS, Push, In-app)
- Alert type preferences
- Quiet hours configuration
- Test notification feature
- Notification history
- Enable/disable by category
- Frequency settings

**Technical Needs:**
- Preference management service
- Multi-channel notification service
- Quiet hours logic
- Test notification service

---

## Module 8: Opt-out & Preferences

### Screen: CIT-USER-99 - Opt-Out Schemes Screen
**Requirements:**
- List of enrolled schemes
- Opt-out action for schemes
- Confirmation dialogs
- Impact summary before opt-out
- Audit logs
- Opt-out history
- Re-enrollment option
- Opt-out reason collection

**Technical Needs:**
- Opt-out management service
- Impact calculation service
- Audit logging
- Notification service

---

## Module 9: Account Management

### Screen: CIT-USER-33 - User Account Settings
**Requirements:**
- Core account information management
- Communication preferences
- Data consent management
- Accessibility options
- Language preferences
- Theme preferences
- Privacy settings
- Data export/delete options

**Technical Needs:**
- Account management service
- Preference storage
- Consent management
- Accessibility configuration

### Screen: CIT-USER-34 - Security Settings Screen
**Requirements:**
- Password management (if applicable)
- MFA configuration
- Active sessions management
- Device management
- Security alerts configuration
- Suspicious activity monitoring
- Login history
- Security recommendations

**Technical Needs:**
- Security service
- Session management
- Device tracking
- Activity monitoring
- Alert service

---

## Module 10: Help & Support

### Screen: CIT-HELP-36 - Help & Support
**Requirements:**
- FAQ section with search
- Troubleshooting guides
- Ticket management interface
- Contact options
- Multi-language support
- Accessibility features
- Video tutorials (optional)
- Chat support (optional)

**Technical Needs:**
- FAQ management system
- Ticket service integration
- Search service
- i18n support

### Screen: CIT-HELP-37 - Support Ticket Creation Page
**Requirements:**
- Ticket creation form
- Category selection
- Priority selection
- Attachment support
- Validation
- Category-based routing
- Notifications
- Draft saving

**Technical Needs:**
- Ticket service
- Category routing logic
- File upload service
- Notification service

### Screen: CIT-HELP-38 - Ticket Flow and Dept Routing
**Requirements:**
- Automated ticket routing
- Category-based routing
- Keyword-based routing
- Department assignment
- Notifications
- Audit logging
- Routing rules configuration
- Escalation rules

**Technical Needs:**
- Routing engine
- Keyword analysis
- Department service integration
- Audit logging
- Rule engine

### Screen: CIT-HELP-39 - Resolution and Status Tracking
**Requirements:**
- Ticket status view
- Status history
- Notifications
- Escalation options
- Communication channels
- Resolution details
- Feedback on resolution
- Ticket closure

**Technical Needs:**
- Status tracking service
- Communication service
- Notification service
- Feedback service

---

## Cross-Module Features

### Common Requirements Across Modules

1. **Internationalization**
   - All screens support English, Hindi, Rajasthani
   - Right-to-left support if needed
   - Date/time localization
   - Number formatting

2. **Accessibility**
   - WCAG 2.1 AA compliance
   - Screen reader support
   - Keyboard navigation
   - High contrast mode
   - Font size adjustment

3. **Responsive Design**
   - Mobile-first approach
   - Tablet optimization
   - Desktop layouts
   - Touch-friendly interactions

4. **Security**
   - Authentication on all protected screens
   - Authorization checks
   - Data encryption
   - Audit logging
   - Input validation

5. **Performance**
   - Lazy loading
   - Code splitting
   - API optimization
   - Caching strategies
   - Image optimization

6. **Error Handling**
   - User-friendly error messages
   - Retry mechanisms
   - Error logging
   - Fallback UI states

