# Citizen Portal - Screens & Modules Mapping

## Overview

This document maps all 39 screens across 9 modules for the Citizen Portal, aligned with the portal's core mission to provide a unified, AI-driven gateway for accessing government welfare schemes and services.

## Problem Statement

The Citizen Portal addresses fragmentation and complexity in accessing government services:

### Problems Solved
- **Fragmentation**: Eliminates need to visit multiple portals/departments
- **Document Duplication**: Resolves duplicate document requests and manual verification
- **Consent Confusion**: Simplifies consent management and data privacy clarity
- **Poor Visibility**: Addresses lack of visibility into benefits and family eligibility
- **Communication Gaps**: Tackles notification and communication issues

### How It Solves Them
- Unified authenticated gateway (Jan Aadhaar, Raj SSO, MFA)
- AI-driven scheme discovery, eligibility prediction, and personalized recommendations
- Consent-driven applications with transparent status tracking
- Aggregated benefits dashboard with real-time status and forecasting
- Fast communication, notifications, and multi-language support
- Security, regulatory validations, error handling, and audit logging

## Modules & Screens Breakdown

### 1. Authentication & Profile (6 screens)

| Screen ID | Screen Name | Access | Description |
|-----------|-------------|--------|-------------|
| CIT-AUTH-01 | Login Screen | Public | Secure login using Jan Aadhaar ID and OTP; supports biometric authentication and multi-language UI |
| CIT-AUTH-02 | Raj SSO Login | Public | Rajasthan Single Sign-On authentication with token exchange; alternative login options |
| CIT-AUTH-03 | MFA Verification | Authenticated | Multi-factor authentication via OTP, TOTP apps, biometrics for added security |
| CIT-PROF-04 | Profile Dashboard | Authenticated | Displays consolidated citizen profile, family snapshot, key benefits, and notifications |
| CIT-PROF-05 | Edit Profile | Authenticated | Allows updating personal info and documents with validation and re-verification workflows |
| CIT-PROF-06 | Profile Verification Status | Authenticated | Shows verification status of profile fields with source details and alerts for user action |

**Key Features:**
- Jan Aadhaar integration
- Raj SSO integration
- Multi-factor authentication
- Profile management
- Verification workflows

---

### 2. Scheme Discovery (6 screens)

| Screen ID | Screen Name | Access | Description |
|-----------|-------------|--------|-------------|
| CIT-SCHEME-07 | Browse All Schemes | Authenticated | Search and filter government schemes by category, eligibility, personalized AI-driven suggestions |
| CIT-SCHEME-08 | Scheme Details | Authenticated | Detailed scheme info, eligibility, benefits, apply button, and related scheme links |
| CIT-SCHEME-09 | Search & Filter | Authenticated | Search bar with autocomplete, filters, sorting; saves filter preferences |
| CIT-SCHEME-10 | Eligibility Checker | Authenticated | AI-powered interactive eligibility questionnaire with real-time results and explanations |
| CIT-SCHEME-11 | Personalized Recommendations | Authenticated | AI-driven personalized scheme suggestions with explanations and save/watchlist features |
| CIT-SCHEME-12 | Eligible and Recommendation Schemes | Authenticated | List filtered by eligibility from AI assessments; allows bookmark and dynamic updates |

**Key Features:**
- AI-driven discovery and recommendations
- Eligibility prediction
- Personalized suggestions
- Advanced search and filtering
- Real-time eligibility checking

---

### 3. Consent & Application (5 screens)

| Screen ID | Screen Name | Access | Description |
|-----------|-------------|--------|-------------|
| CIT-CONSENT-13 | Consent Submission | Authenticated | Explicit consent collection for schemes and data sharing with digital signature/OTP verification |
| CIT-APP-14 | Application Tracking | Authenticated | Track real-time status of submitted applications with filtering and notifications |
| CIT-DOC-15 | Document Upload | Authenticated | Upload and manage supplementary documents with validation and status tracking |
| CIT-CLAR-16 | Clarification Form | Authenticated | Submit responses for missing info requests with document attachments and deadline tracking |
| CIT-APP-17 | Application History | Authenticated | Historical records of scheme applications including filtering and detailed views |

**Key Features:**
- Explicit consent management
- Real-time application tracking
- Document management
- Clarification workflows
- Application history

---

### 4. Benefits & Entitlements (7 screens)

| Screen ID | Screen Name | Access | Description |
|-----------|-------------|--------|-------------|
| CIT-BEN-18 | Current Benefits Dashboard | Authenticated | Summary of active schemes and benefits with drill-down and alert features |
| CIT-PROF-360 | 360-Degree Profile | Authenticated | Interactive profile & family network visualization up to 3 levels, scheme participation aggregation |
| CIT-BEN-19 | DBT Payment Tracking | Authenticated | Track direct benefit transfer payments with filters, downloads, and alerts |
| CIT-BEN-20 | Annual Ledger View | Authenticated | Month/year-wise benefit/payment ledger with export and drill-down capabilities |
| CIT-BEN-21 | Family Benefits View | Authenticated | Consolidated family-level benefits with filtering, alerts, and profile links |
| CIT-BEN-22 | Historical Benefits | Authenticated | Past benefits data and trends with export, filters, and graphical representation |
| CIT-BEN-23 | Personal Entitlement Forecast | Authenticated | Predictive insights on eligibility and benefits with AI-driven forecasts and scenario comparisons |

**Key Features:**
- Consolidated benefits dashboard
- 360-degree profile with family network
- DBT payment tracking
- Historical benefits and trends
- AI-driven entitlement forecasting
- Family-level benefit aggregation

---

### 5. Documents & Certificates (4 screens)

| Screen ID | Screen Name | Access | Description |
|-----------|-------------|--------|-------------|
| CIT-DOC-24 | Document Library | Authenticated | Manage certificates/documents with search, filter, preview, sharing, and expiry alerts |
| CIT-DOC-25 | Download Documents | Authenticated | Secure PDF download with bulk options and audit logging |
| CIT-DOC-26 | e-Vault Integration | Authenticated | Secure access to e-Vault documents with upload/download, versioning, and consent controls |
| CIT-DOC-27 | Digital Signature View | Authenticated | View digitally signed documents with real-time signature validation and audit logging |

**Key Features:**
- Document library management
- e-Vault integration
- Digital signature validation
- Secure document handling
- Version control

---

### 6. 24 Hours Service Delivery (4 screens)

| Screen ID | Screen Name | Access | Description |
|-----------|-------------|--------|-------------|
| CIT-SERV-28 | Service Catalog | Authenticated | Browse government services with categorization, search, filtering, and multi-language support |
| CIT-SERV-29 | Service Request Form | Authenticated | Multi-step service request forms with document uploads and validations |
| CIT-SERV-30 | Service Request Status | Authenticated | Real-time tracking of service requests with timeline, filters, and downloads |
| CIT-SERV-31 | Service Feedback | Authenticated | Feedback and rating for government services with anonymous option and content moderation |

**Key Features:**
- Service catalog
- Service request management
- Real-time status tracking
- Feedback and ratings

---

### 7. Notifications (1 screen)

| Screen ID | Screen Name | Access | Description |
|-----------|-------------|--------|-------------|
| CIT-USER-35 | Notification Settings | Authenticated | Manage notification preferences across channels and alert types with quiet hours and test features |

**Key Features:**
- Multi-channel notifications
- Preference management
- Quiet hours
- Test notifications

---

### 8. Opt-out & Preferences (1 screen)

| Screen ID | Screen Name | Access | Description |
|-----------|-------------|--------|-------------|
| CIT-USER-99 | Opt-Out Schemes Screen | Authenticated | Manage scheme opt-outs with confirmation, audit logs, and impact summaries |

**Key Features:**
- Scheme opt-out management
- Impact summaries
- Audit logging

---

### 9. Account Management (2 screens)

| Screen ID | Screen Name | Access | Description |
|-----------|-------------|--------|-------------|
| CIT-USER-33 | User Account Settings | Authenticated | Manage core account info, communication preferences, data consent, and accessibility options |
| CIT-USER-34 | Security Settings Screen | Authenticated | Configure passwords, MFA, sessions, devices, security alerts, and suspicious activity monitoring |

**Key Features:**
- Account management
- Security configuration
- Communication preferences
- Accessibility options
- Device management

---

### 10. Help & Support (4 screens)

| Screen ID | Screen Name | Access | Description |
|-----------|-------------|--------|-------------|
| CIT-HELP-36 | Help & Support | Public/Authenticated | FAQs, troubleshooting, ticket management, contact options with multi-language and accessibility |
| CIT-HELP-37 | Support Ticket Creation Page | Authenticated | Submit new support tickets with attachments, category routing, validation, and notifications |
| CIT-HELP-38 | Ticket Flow and Dept Routing | Authenticated | Automated ticket routing based on categories/keywords, notifications, and audit logging |
| CIT-HELP-39 | Resolution and Status Tracking | Authenticated | View and manage ticket status with history, notifications, escalations, and communication channels |

**Key Features:**
- FAQ and troubleshooting
- Ticket management
- Automated routing
- Status tracking
- Multi-language support

---

## Screen Summary Statistics

| Module | Screen Count | Public Access | Authenticated Access |
|--------|--------------|---------------|---------------------|
| Authentication & Profile | 6 | 2 | 4 |
| Scheme Discovery | 6 | 0 | 6 |
| Consent & Application | 5 | 0 | 5 |
| Benefits & Entitlements | 7 | 0 | 7 |
| Documents & Certificates | 4 | 0 | 4 |
| 24 Hours Service Delivery | 4 | 0 | 4 |
| Notifications | 1 | 0 | 1 |
| Opt-out & Preferences | 1 | 0 | 1 |
| Account Management | 2 | 0 | 2 |
| Help & Support | 4 | 1 | 3 |
| **Total** | **40** | **3** | **37** |

*Note: CIT-HELP-36 has both public and authenticated access*

## Key Technical Requirements

### Authentication Integrations
- **Jan Aadhaar**: Primary authentication mechanism
- **Raj SSO**: Rajasthan Single Sign-On
- **MFA**: Multi-factor authentication (OTP, TOTP, Biometric)

### AI/ML Capabilities
- Scheme discovery and recommendations
- Eligibility prediction
- Personalized suggestions
- Entitlement forecasting
- 360-degree profile insights

### Integrations
- **e-Vault**: Document storage and management
- **DBT System**: Direct Benefit Transfer tracking
- **Payment Gateway**: For service payments
- **Notification Services**: Email, SMS, Push

### Advanced Features
- 360-degree profile with family network (3 levels)
- Real-time status tracking
- Digital signatures
- Document versioning
- Audit logging throughout

## Development Priority Mapping

### Phase 1: Foundation (Critical - MVP)
- CIT-AUTH-01, CIT-AUTH-02: Login screens
- CIT-AUTH-03: MFA
- CIT-PROF-04, CIT-PROF-05, CIT-PROF-06: Profile management
- CIT-USER-34: Security settings

### Phase 2: Core Features (Critical - MVP)
- CIT-SCHEME-07, CIT-SCHEME-08: Scheme browsing
- CIT-SCHEME-10: Eligibility checker
- CIT-APP-14: Application tracking
- CIT-CONSENT-13: Consent submission
- CIT-DOC-15: Document upload

### Phase 3: Enhanced Features (High Priority)
- CIT-SCHEME-11, CIT-SCHEME-12: Recommendations
- CIT-BEN-18: Benefits dashboard
- CIT-BEN-19: DBT tracking
- CIT-SERV-28, CIT-SERV-29, CIT-SERV-30: Service delivery

### Phase 4: Advanced Features (Medium Priority)
- CIT-PROF-360: 360-degree profile
- CIT-BEN-20, CIT-BEN-21, CIT-BEN-22: Historical benefits
- CIT-BEN-23: Entitlement forecast
- CIT-DOC-26: e-Vault integration
- CIT-DOC-27: Digital signatures

### Phase 5: Supporting Features
- CIT-USER-35: Notification settings
- CIT-USER-99: Opt-out management
- CIT-USER-33: Account settings
- CIT-HELP-36, CIT-HELP-37, CIT-HELP-38, CIT-HELP-39: Help & support

## Screen Dependencies

### Authentication Flow
```
CIT-AUTH-01 (Login) 
  → CIT-AUTH-02 (Raj SSO) [optional]
  → CIT-AUTH-03 (MFA)
  → CIT-PROF-04 (Profile Dashboard)
```

### Scheme Application Flow
```
CIT-SCHEME-07 (Browse Schemes)
  → CIT-SCHEME-08 (Scheme Details)
  → CIT-SCHEME-10 (Eligibility Checker)
  → CIT-CONSENT-13 (Consent Submission)
  → CIT-DOC-15 (Document Upload)
  → CIT-APP-14 (Application Tracking)
```

### Benefits Flow
```
CIT-PROF-04 (Profile Dashboard)
  → CIT-BEN-18 (Current Benefits)
  → CIT-BEN-19 (DBT Tracking)
  → CIT-PROF-360 (360-Degree Profile)
```

## Next Steps

1. **Screen Specifications**: Receive detailed specifications for each screen
2. **Update Development Plan**: Align development phases with screen priorities
3. **Create Wireframes/Mockups**: Visual design for each screen
4. **API Design**: Define APIs needed for each screen
5. **Component Library**: Identify reusable components across screens

