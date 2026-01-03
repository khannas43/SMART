# Citizen Portal Screen to AI/ML Use Case Mapping

**Purpose:** Complete mapping of 20 Citizen Portal screens to AI/ML use cases  
**Created:** 2024-12-30  
**For:** Citizen Portal Development Team  
**Version:** 1.0  
**Status:** ✅ Complete - All 20 screens mapped

---

## Executive Summary

This document provides comprehensive mapping of all 20 Citizen Portal screens to the 11 AI/ML use cases available in the SMART Platform. Each screen mapping includes:

- **AI/ML Use Cases Used:** Which use cases power the screen's functionality
- **API Integration:** Specific API endpoints and request/response patterns
- **Data Flow:** Sequence of operations and data transformations
- **UI Components:** What AI/ML data is displayed and where
- **User Actions:** What triggers AI/ML operations
- **Gaps & Requirements:** Missing features or enhancements needed

---

## Quick Reference: Available AI/ML Use Cases

| Use Case ID | Name | Status | Key Capabilities |
|-------------|------|--------|------------------|
| AI-PLATFORM-01 | Golden Records | ✅ Complete | Identity verification, deduplication |
| AI-PLATFORM-02 | 360° Profiles | ✅ Complete | Profile data, income inference, relationships |
| AI-PLATFORM-03 | Eligibility Identification | ✅ Complete | Auto-identify eligible schemes |
| AI-PLATFORM-04 | Auto Intimation & Consent | ✅ Complete | Notifications, consent management |
| AI-PLATFORM-05 | Auto Application Submission | ⏳ Partial | Form prefill, auto-submit |
| AI-PLATFORM-06 | Auto Approval & STP | ✅ Complete | Auto-approval, decision routing |
| AI-PLATFORM-07 | Beneficiary Detection | ✅ Complete | Detect ineligible cases |
| AI-PLATFORM-08 | Eligibility Checker | ✅ Complete | Real-time eligibility checking |
| AI-PLATFORM-09 | Proactive Inclusion | ✅ Complete | Identify inclusion gaps |
| AI-PLATFORM-10 | Benefit Forecast | ✅ Complete | Future benefit predictions |
| AI-PLATFORM-11 | Personalized Nudging | ✅ Complete | Optimized notifications |

---

## Screen Mapping

### Screen 1: Unified Login & SSO

**Screen ID:** CIT-AUTH-01  
**Screen Name:** Unified Login & SSO  
**Purpose:** Provide unified secure authentication via Jan Aadhaar OTP or Raj SSO with seamless session creation and identity unification.

**AI/ML Use Cases Used:**
- **AI-PLATFORM-01 (Golden Records):** 
  - Primary function: Identity verification and deduplication during login
  - Data shown: Unified identity record post-login
  - Usage: Account linking (Raj SSO ↔ Jan Aadhaar), duplicate detection

**API Integration:**
1. `GET /api/v1/golden-records/{citizen_id}` - Get golden record after authentication
   - Request params: `citizen_id` (from Jan Aadhaar/SSO)
   - Response used for: Profile summary display, identity unification
2. `POST /api/v1/golden-records/search` - Search for existing records (duplicate check)
   - Request body: `{aadhaar_id, mobile, email}`
   - Response used for: Detecting duplicate accounts before linking
3. `POST /api/v1/golden-records/merge` - Merge SSO and Jan Aadhaar identities
   - Request body: `{primary_id, secondary_id, merge_type}`
   - Response used for: Unified identity creation

**Data Flow:**
1. User enters Jan Aadhaar ID → OTP sent → OTP verified
2. Backend calls Golden Records API to fetch/verify identity
3. On Raj SSO login → Token exchange → Golden Records lookup
4. If identities need linking → Merge API called → Unified profile created
5. Session created with unified `citizen_id` → Redirect to Profile Dashboard

**UI Components:**
- **Login Form** - No direct AI/ML display (authentication only)
- **Post-Login Profile Summary** (Raj SSO flow) - Shows Golden Record data
- **Account Linking Prompt** - Displayed when SSO account needs Jan Aadhaar link

**User Actions:**
- **Enter Jan Aadhaar ID & OTP** → Triggers Golden Records lookup
- **Click "Link Jan Aadhaar"** (SSO flow) → Triggers merge API
- **Login Success** → Redirects to Profile Dashboard (CIT-PROF-03)

**Gaps & Required Features:**
- ✅ No gaps - Authentication doesn't require advanced AI/ML features
- ⚠️ Consider: ML-based fraud detection for login attempts (future enhancement)

---

### Screen 2: MFA & Security Challenge

**Screen ID:** CIT-AUTH-02  
**Screen Name:** MFA & Security Challenge  
**Purpose:** Provide additional layer of security through multi-factor authentication during login or sensitive transactions.

**AI/ML Use Cases Used:**
- **None** - This screen handles authentication security (OTP, TOTP, biometrics)
  - Note: Could leverage AI-PLATFORM-07 (Beneficiary Detection) for anomaly-based step-up auth in future

**API Integration:**
1. Standard MFA APIs (not AI/ML-specific)
   - OTP generation/verification
   - TOTP validation
   - Biometric verification

**Data Flow:**
1. User completes primary authentication → MFA prompt shown
2. User selects MFA method (OTP/TOTP/Biometric)
3. MFA verification → Session authorized
4. Redirect to target screen

**UI Components:**
- **MFA Input Fields** - OTP/TOTP entry
- **Biometric Prompt** - Device biometric authentication
- **MFA Method Selector** - Choose authentication method

**User Actions:**
- **Enter OTP/TOTP** → MFA verification
- **Use Biometric** → Device biometric authentication
- **MFA Success** → Continue to authenticated session

**Gaps & Required Features:**
- ⚠️ **Future Enhancement:** Integrate AI-PLATFORM-07 for risk-based MFA (skip MFA for low-risk, require for high-risk)
- ⚠️ **Future Enhancement:** ML-based device fingerprinting for trusted device recognition

---

### Screen 3: Profile Dashboard & 360° View

**Screen ID:** CIT-PROF-03  
**Screen Name:** Profile Dashboard & 360° View  
**Purpose:** Deliver comprehensive Golden Record dashboard with summary insights, interactive 360° family network visualization, ML confidence transparency, benefit aggregation, and one-click profile actions.

**AI/ML Use Cases Used:**
- **AI-PLATFORM-01 (Golden Records):**
  - Primary function: Display unified citizen identity with source attribution
  - Data shown: Core attributes, confidence badges (Green/Yellow/Red), source tracking
- **AI-PLATFORM-02 (360° Profiles):**
  - Primary function: Complete profile with income inference, eligibility scores, family graph
  - Data shown: Income band, vulnerability category, relationship graph (Neo4j), anomaly indicators
- **AI-PLATFORM-03 (Eligibility Identification):**
  - Primary function: Show eligibility hints and precomputed eligible schemes
  - Data shown: Top N eligible schemes, eligibility scores, priority rankings
- **AI-PLATFORM-11 (Personalized Nudging):**
  - Primary function: Display ML-driven profile alerts and recommendations
  - Data shown: Profile completion nudges, verification reminders

**API Integration:**
1. `GET /api/v1/golden-records/{gr_id}?summary=true` - Get golden record summary
   - Request params: `gr_id`, `summary=true`
   - Response used for: Summary tab - core attributes + confidence metadata
2. `GET /api/v1/golden-records/{gr_id}?depth=3` - Get full profile with 3-level family
   - Request params: `gr_id`, `depth=3`
   - Response used for: 360° tab - full profile + family graph
3. `GET /api/v1/profiles/{family_id}` - Get complete 360° profile
   - Request params: `family_id`
   - Response used for: Income band, vulnerability, eligibility scores
4. `GET /api/v1/profiles/{family_id}/relationships` - Get family relationship graph
   - Request params: `family_id`
   - Response used for: Interactive family tree visualization (vis.js/D3)
5. `GET /api/v1/profiles/{family_id}/eligibility-scores` - Get eligibility scores
   - Request params: `family_id`
   - Response used for: Scheme eligibility cards, predicted entitlements
6. `GET /api/v1/eligibility/citizen-hints?family_id={id}&limit=5` - Top eligible schemes
   - Request params: `family_id`, `limit=5`
   - Response used for: "AI Eligibility" CTA recommendations
7. `GET /api/v1/nudges/active?family_id={id}` - Get active nudges
   - Request params: `family_id`
   - Response used for: Profile alerts, ML nudges section
8. `WebSocket /notifications/{gr_id}` - Real-time updates
   - Response used for: Live GR changes, new alerts, benefit status updates

**Data Flow:**
1. User opens Profile Dashboard → Load Golden Record summary (Summary tab)
2. Load 360° Profile data (income, vulnerability, eligibility scores)
3. Load family relationship graph (Neo4j)
4. Load top eligible schemes hints
5. Load active nudges/alerts
6. User switches to 360° tab → Load full profile + 3-level family graph
7. User clicks "AI Eligibility" → Navigate to Eligibility Checker (CIT-SCHEME-07)
8. WebSocket connection → Real-time updates for GR changes, alerts, benefits

**UI Components:**
- **Summary Tab:**
  - **Personal Details Card** - Shows Golden Record attributes with confidence badges (Green ≥95%, Yellow 80-95%, Red <80%)
  - **Family Snapshot Carousel** - 1st-degree family members (3-5), clickable → 360° tab
  - **Active Schemes Pie Chart** - Current benefits + predicted entitlements
  - **Profile Alerts Section** - ML nudges from AI-PLATFORM-11
  - **Quick CTAs:** "Edit Profile", "AI Eligibility", "Verify Data", "View 360° Profile"
- **360° View Tab:**
  - **Full Golden Record Attributes** - All fields with per-field source badges
  - **Interactive Family Graph** - 3-level family tree (vis.js/D3) with node popovers showing confidence, relationships
  - **Family Benefit Sankey Diagram** - Scheme aggregation and overlap analysis
  - **Consent Toggles** - Granular data sharing controls
  - **GR Audit Timeline** - Change history with confidence deltas
  - **ML-Suggested Relations** - "Add Family" with AI recommendations

**User Actions:**
- **Click "Edit Profile"** → Navigate to CIT-PROF-04
- **Click "AI Eligibility"** → Navigate to CIT-SCHEME-07 (Eligibility & Recommendations)
- **Click "View 360° Profile"** → Switch to 360° tab
- **Click Family Node** → Popover with details → GR update → Real-time refresh
- **Toggle Consent** → Data masking/unmasking in both tabs
- **Click ML-Suggested Relation** → Verification workflow

**Gaps & Required Features:**
- ✅ Core features covered by AI-PLATFORM-01, 02, 03, 11
- ⚠️ **Enhancement:** Consider adding AI-PLATFORM-09 (Proactive Inclusion) for missing scheme alerts
- ⚠️ **Performance:** WebSocket updates need to handle 100 updates/sec without lag

---

### Screen 4: Profile Edit & Verification

**Screen ID:** CIT-PROF-04  
**Screen Name:** Profile Edit & Verification  
**Purpose:** Unified workspace for editing Golden Record attributes, viewing verification statuses, managing source consents, and previewing ML confidence impacts.

**AI/ML Use Cases Used:**
- **AI-PLATFORM-01 (Golden Records):**
  - Primary function: Edit attributes, conflict resolution, source selection
  - Data shown: Current attrs, conflicts/sources, confidence metadata
- **AI-PLATFORM-02 (360° Profiles):**
  - Primary function: Income inference updates, relationship corrections
  - Data shown: Income band updates, relationship confidence changes

**API Integration:**
1. `GET /api/v1/golden-records/{gr_id}?editable=true` - Get editable fields
   - Request params: `gr_id`, `editable=true`
   - Response used for: Edit tab - current attrs + conflicts/sources
2. `GET /api/v1/profiles/{family_id}` - Get verification status
   - Request params: `family_id`
   - Response used for: Verification tab - statuses, timestamps, confidence
3. `POST /document/ocr-extract` - OCR extraction for document uploads
   - Request body: `{document_file, document_type}`
   - Response used for: Auto-populate fields from uploaded documents
4. `POST /api/v1/ai-reconcile/preview` - Preview confidence impact
   - Request body: `{gr_id, field_changes, source_selections}`
   - Response used for: Real-time confidence preview ("New confidence: 98% ↑+6%")
5. `PATCH /api/v1/golden-records/{gr_id}` - Update golden record
   - Request body: `{field_updates, source_selections, consent_matrix}`
   - Response used for: Save changes to GR
6. `POST /api/v1/profiles/{family_id}/family-corrections` - Update family relationships
   - Request body: `{relationship_updates, verification_data}`
   - Response used for: Family relationship corrections
7. `WebSocket /profile-updates/{gr_id}` - Real-time status updates
   - Response used for: Verification status changes, GR updates

**Data Flow:**
1. User opens Edit tab → Load editable fields + conflicts + sources
2. User edits field (e.g., DOB) → Debounced API call to preview confidence impact
3. User selects ML Source Selector → Confidence delta calculated → Preview shown
4. User uploads document → OCR extraction → Auto-populate fields → ML confidence score
5. User clicks "Save" → GR update API → Reconciliation process → Verification status updated
6. Verification tab → Real-time WebSocket updates → Status badges refresh

**UI Components:**
- **Edit Tab:**
  - **Editable Fields** - Golden Record attributes with inline confidence badges
  - **ML Source Selector Dropdowns** - For conflicted attributes (UIDAI/Passport/Manual)
  - **Document Upload** - OCR auto-extract proposals
  - **Confidence Preview** - "New confidence: 98% ↑+6%" real-time updates
  - **Save/Preview/Reset Buttons** - With consent matrix
- **Verification Tab:**
  - **Status Dashboard** - Green/Yellow/Red badges (Verified/Pending/Rejected)
  - **Source Attribution** - Source badges (UIDAI/Passport/Manual) + confidence scores
  - **Progress Bar** - Overall verification completion
  - **Expiry Alerts** - Verification expiry warnings
  - **One-Click Edit Links** - "Edit This Field" → Switches to Edit tab

**User Actions:**
- **Edit Field** → Triggers confidence preview API
- **Select Source from Dropdown** → Confidence delta calculated
- **Upload Document** → OCR extraction → Auto-populate fields
- **Click "Save"** → GR update → Reconciliation → Verification status update
- **Toggle Consent** → Data visibility changes in both tabs
- **Click "Edit This Field"** (Verification tab) → Switch to Edit tab with field focused

**Gaps & Required Features:**
- ✅ Core features covered by AI-PLATFORM-01, 02
- ⚠️ **Enhancement:** Document OCR service integration needed (not currently in AI/ML use cases)
- ⚠️ **Performance:** ML inference for confidence delta <500ms required

---

### Screen 5: Scheme Catalog & Search

**Screen ID:** CIT-SCHEME-05  
**Screen Name:** Scheme Catalog & Search  
**Purpose:** Unified scheme discovery combining browsing, advanced search, filtering, AI recommendations, comparison, and sorting.

**AI/ML Use Cases Used:**
- **AI-PLATFORM-03 (Eligibility Identification):**
  - Primary function: AI recommendations for profile-matched schemes
  - Data shown: Top N recommended schemes with match scores (≥80% profile match)
- **AI-PLATFORM-08 (Eligibility Checker):**
  - Primary function: Real-time eligibility hints on scheme cards
  - Data shown: Eligibility status badges, confidence scores

**API Integration:**
1. `GET /schemes?search={q}&filters={json}&sort={field}&page={n}&limit=20` - Search schemes
   - Request params: `search`, `filters`, `sort`, `page`, `limit`
   - Response used for: Scheme results grid/list with eligibility hints
2. `GET /schemes/ai-recommendations/{gr_id}?limit=5` - Get AI recommendations
   - Request params: `gr_id`, `limit=5`
   - Response used for: AI Recommendations panel (top-right) with match scores
3. `POST /schemes/compare` - Compare up to 3 schemes
   - Request body: `{scheme_ids: [id1, id2, id3]}`
   - Response used for: Compare panel - side-by-side eligibility/benefit analysis
4. `GET /api/v1/eligibility/precomputed?family_id={id}` - Get precomputed eligibility
   - Request params: `family_id`
   - Response used for: Eligibility hints on scheme cards

**Data Flow:**
1. User opens screen → Load AI recommendations (top 5 schemes)
2. User enters search query → Debounced search API (300ms) → Results update
3. User applies filters → Results refresh with filtered schemes + eligibility hints
4. User drags scheme to compare panel → Compare API → Side-by-side eligibility view
5. User clicks scheme card → Navigate to Scheme Details (CIT-SCHEME-06)

**UI Components:**
- **Search Bar + Autocomplete** - Keyword search with semantic matching
- **Filter Panel** - Category, department, benefit type, location filters
- **AI Recommendations Panel** - Top 5 profile-matched schemes with match scores (92%, 85%)
- **Scheme Results Grid/List** - Scheme cards with eligibility badges, highlights
- **Compare Panel** - Up to 3 schemes side-by-side with eligibility comparison

**User Actions:**
- **Type in Search Bar** → Triggers search API (debounced 300ms)
- **Apply Filters** → Results refresh with eligibility hints
- **Drag Scheme to Compare** → Compare API → Eligibility side-by-side view
- **Click Scheme Card** → Navigate to CIT-SCHEME-06 (Scheme Details)
- **Click AI Recommendation** → Same filtering as manual search

**Gaps & Required Features:**
- ✅ Core features covered by AI-PLATFORM-03, 08
- ⚠️ **Enhancement:** Consider AI-PLATFORM-09 (Proactive Inclusion) for highlighting missing schemes
- ⚠️ **Performance:** Search/filter response <200ms, initial load <500ms

---

### Screen 6: Scheme Details

**Screen ID:** CIT-SCHEME-06  
**Screen Name:** Scheme Details  
**Purpose:** Provide detailed information about a selected government scheme including eligibility, benefits, required documents, and application process.

**AI/ML Use Cases Used:**
- **AI-PLATFORM-08 (Eligibility Checker):**
  - Primary function: Real-time eligibility check for the specific scheme
  - Data shown: Eligibility status, score, confidence, explanations
- **AI-PLATFORM-03 (Eligibility Identification):**
  - Primary function: Related scheme recommendations
  - Data shown: "You may also be eligible for" suggestions

**API Integration:**
1. `GET /api/v1/eligibility/schemes/{schemeCode}` - Check specific scheme eligibility
   - Request params: `schemeCode`, `family_id` (optional)
   - Response used for: Eligibility status badge, "Apply Now" button state
2. `GET /api/v1/eligibility/citizen-hints?family_id={id}&limit=5` - Related schemes
   - Request params: `family_id`, `limit=5`
   - Response used for: Related scheme suggestions section
3. Standard Scheme Management APIs (not AI/ML) - Scheme metadata, documents, FAQs

**Data Flow:**
1. User opens scheme details → Load scheme metadata
2. Check eligibility for this scheme (if authenticated) → Eligibility Checker API
3. Load related scheme recommendations → Eligibility Identification API
4. User clicks "Apply Now" → Eligibility check → Navigate to consent/application flow
5. User clicks related scheme → Navigate to that scheme's details

**UI Components:**
- **Scheme Header** - Name, department, category
- **Eligibility Status Badge** - Eligible/Potentially Eligible/Not Eligible with confidence %
- **Eligibility Explanation** - Human-readable explanation (from AI-PLATFORM-08)
- **"Apply Now" Button** - Enabled/disabled based on eligibility check
- **Related Schemes Section** - AI-recommended similar schemes

**User Actions:**
- **View Scheme Details** → Eligibility check triggered automatically
- **Click "Apply Now"** → Eligibility validation → Navigate to consent/application
- **Click Related Scheme** → Navigate to that scheme's details page
- **View Eligibility Explanation** → Shows "Why shown?" with key drivers

**Gaps & Required Features:**
- ✅ Core features covered by AI-PLATFORM-08, 03
- ⚠️ **Enhancement:** Consider adding AI-PLATFORM-10 (Benefit Forecast) for future benefit projections

---

### Screen 7: Eligibility & Recommendations

**Screen ID:** CIT-SCHEME-07  
**Screen Name:** Eligibility & Recommendations  
**Purpose:** Let citizens answer an adaptive AI questionnaire and immediately see eligible, suggested, and last-check schemes in one unified view.

**AI/ML Use Cases Used:**
- **AI-PLATFORM-08 (Eligibility Checker):**
  - Primary function: Real-time eligibility checking with questionnaire responses
  - Data shown: Eligibility status per scheme, scores, confidence, explanations
- **AI-PLATFORM-03 (Eligibility Identification):**
  - Primary function: Auto-identified eligible schemes (pre-populated)
  - Data shown: Schemes tagged "Auto-identified" with priority rankings
- **AI-PLATFORM-01 (Golden Records):**
  - Primary function: Baseline data for questionnaire pre-filling
  - Data shown: Pre-filled answers from Golden Record
- **AI-PLATFORM-02 (360° Profiles):**
  - Primary function: Family context, income band, vulnerability data
  - Data shown: Family members, income inference, eligibility context

**API Integration:**
1. `GET /api/v1/golden-records/{gr_id}?summary=true` - Get baseline data
   - Request params: `gr_id`
   - Response used for: Pre-filling questionnaire answers
2. `GET /api/v1/profiles/{family_id}` - Get 360° profile context
   - Request params: `family_id`
   - Response used for: Family members, income band, vulnerability
3. `GET /api/v1/eligibility/questionnaire?template_name={name}` - Get questionnaire template
   - Request params: `template_name`
   - Response used for: Multi-step adaptive questionnaire
4. `POST /api/v1/eligibility/check` - Perform eligibility check
   - Request body: `{familyId, questionnaireResponses, checkType, schemeCodes}`
   - Response used for: Live results panel - eligible/suggested schemes with scores
5. `POST /api/v1/eligibility/evaluate?family_id={id}&scheme_ids={list}` - On-demand evaluation
   - Request params: `family_id`, `scheme_ids` (optional)
   - Request body: `{questionnaire_answers, use_ml: true}`
   - Response used for: Recomputing scheme scores as user answers (debounced)
6. `GET /api/v1/eligibility/history?family_id={id}` - Get past eligibility runs
   - Request params: `family_id`
   - Response used for: "From my last check" chip - reload previous run

**Data Flow:**
1. User opens screen → Load Golden Record + 360° Profile → Pre-fill questionnaire
2. User answers questions → Each answer debounced → Eligibility Engine recomputes scores
3. Live Results Panel updates → Eligible/Suggested/Last check schemes displayed
4. User clicks "Finish questionnaire" → Creates Eligibility Assessment Run → Results saved
5. User clicks "From my last check" chip → Loads latest completed run
6. User clicks "Why shown?" → Display explanations (rule paths, SHAP values)
7. User clicks "Apply now" → Navigate to consent/application flow

**UI Components:**
- **Questionnaire Zone:**
  - **Multi-step Adaptive Questions** - Age, income, family, location, disability, life events
  - **Pre-filled Values** - From Golden Record with "Confirm/Change" options
  - **Progress Indicator** - Step 2 of 7, back/next controls
  - **Autosave** - Each step saved, resume across devices
- **Live Results Panel:**
  - **Chip Filters** - Eligible now, Suggested for you, From my last check, All
  - **Scheme Cards** - Name, department, benefit summary, status pill (Eligible/Potential/Not eligible), confidence %, origin tag (Auto-identified/From questionnaire/Recommended)
  - **"Why shown?" Link** - Explanations with key drivers
  - **CTAs** - View details, Apply now, Track application, Bookmark, Not relevant
  - **Sorting/Filtering Bar** - Category, department, benefit, life-event tags, recency, priority, amount

**User Actions:**
- **Answer Questionnaire Questions** → Debounced eligibility recalculation → Live results update
- **Click "Finish Questionnaire"** → Eligibility Assessment Run created → Results saved
- **Click "From my last check"** → Latest completed run loaded
- **Click "Why shown?"** → Display eligibility explanations
- **Click "Apply now"** → Navigate to consent/application flow
- **Click "Bookmark"** → Save scheme to watchlist
- **Click "Not relevant"** → Feedback to recommendation models

**Gaps & Required Features:**
- ✅ Core features covered by AI-PLATFORM-08, 03, 01, 02
- ⚠️ **Enhancement:** Question branching logic needs to respect scheme criteria and model features
- ⚠️ **Performance:** Debounced AI calls under load need acceptable response times
- ⚠️ **Fallback:** Rule-only evaluation fallback when AI/Auto-ID unavailable

---

### Screen 8: Consent & Clarifications

**Screen ID:** CIT-CONSENT-08  
**Screen Name:** Consent & Clarifications  
**Purpose:** Unified workspace for scheme consent submission and application clarification responses with progress tracking.

**AI/ML Use Cases Used:**
- **AI-PLATFORM-04 (Auto Intimation & Consent):**
  - Primary function: Consent capture, lifecycle management, versioning
  - Data shown: Pending consents, consent history, status tracking

**API Integration:**
1. `GET /api/v1/intimation/status?family_id={id}` - Get pending intimations
   - Request params: `family_id`
   - Response used for: List of pending consents grouped by scheme
2. `POST /api/v1/consent/capture` - Record consent response
   - Request body: `{family_id, scheme_id, response: "YES|NO|MORE_INFO", captured_via, ip_address}`
   - Response used for: Submit consent with timestamped, versioned record
3. `POST /api/v1/consent/revoke` - Revoke existing consent
   - Request body: `{consent_id, family_id, scheme_id, reason}`
   - Response used for: Withdraw consent with impact preview
4. `GET /api/v1/consent/history?family_id={id}` - Get consent history
   - Request params: `family_id`
   - Response used for: Consent history timeline

**Data Flow:**
1. User opens screen → Load pending consents and clarifications
2. User toggles consent checkboxes → Consent capture API
3. User clicks "Submit All" → Bulk consent capture → Single OTP confirmation
4. Consent recorded → Triggers Auto Application Submission (AI-PLATFORM-05) if consent=YES

**UI Components:**
- **Scheme Consents Section:** Pending consents list, mandatory flags, privacy policy links
- **Application Clarifications Section:** Pending clarifications, text responses, document uploads
- **Progress Bar:** Overall progress (2/5 Consents, 1/3 Clarifications)

**User Actions:**
- **Toggle Consent** → Consent capture API → Status update
- **Submit All** → Bulk consent capture → Single OTP → All services updated
- **Revoke Consent** → Impact preview → Consent revoked

**Gaps & Required Features:**
- ✅ Core features covered by AI-PLATFORM-04
- ⚠️ **Integration:** Needs connection to AI-PLATFORM-05 (Auto Application Submission) for post-consent application creation

---

### Screen 9: Applications Hub

**Screen ID:** CIT-APP-09  
**Screen Name:** Applications Hub  
**Purpose:** Unified dashboard showing all current applications (real-time tracking) and past applications (historical record).

**AI/ML Use Cases Used:**
- **AI-PLATFORM-05 (Auto Application Submission):**
  - Primary function: Display application details with field source tracking
  - Data shown: Application status, mapped fields count, field sources
- **AI-PLATFORM-06 (Auto Approval & STP):**
  - Primary function: Show decision status, risk scores, approval explanations
  - Data shown: Decision status, risk scores, explanations
- **AI-PLATFORM-07 (Beneficiary Detection):**
  - Primary function: Display case alerts for ineligible/mistargeted detection
  - Data shown: Case alerts, verification requests

**API Integration:**
1. `GET /api/v1/applications?family_id={id}` - List applications
   - Request params: `family_id`, `filters`
   - Response used for: Active and past applications list
2. `GET /api/v1/decision/history?applicationId={id}` - Get decision history
   - Request params: `applicationId`
   - Response used for: Decision timeline, risk scores, explanations
3. `GET /api/v1/detection/cases?family_id={id}` - Get detected cases
   - Request params: `family_id`
   - Response used for: Case alerts, verification requests
4. `WebSocket /app-status/{app_id}` - Real-time status updates

**Data Flow:**
1. User opens screen → Load active and past applications
2. Expand application → Load timeline + decision history
3. Real-time WebSocket → Status updates
4. If case detected → Display case alert

**UI Components:**
- **ACTIVE Section:** Application cards with progress bars, status, expandable details
- **PAST Section:** Completed applications with final outcomes
- **Case Alerts:** Detection notifications with verification requests

**User Actions:**
- **Click Application** → Expand → Timeline + decision details
- **View Decision** → Display decision explanations, risk scores
- **Respond to Case Alert** → Verification workflow

**Gaps & Required Features:**
- ✅ Core features covered by AI-PLATFORM-05, 06, 07
- ⚠️ **Note:** AI-PLATFORM-05 is partial (needs external department API integration)

---

### Screen 10: Document Center

**Screen ID:** CIT-DOC-10  
**Screen Name:** Document Center  
**Purpose:** Unified document management hub combining application-required uploads, personal library, Raj-e-Sign verification, and e-Vault integration.

**AI/ML Use Cases Used:**
- **AI-PLATFORM-01 (Golden Records):**
  - Primary function: Document source tracking, verification status
  - Data shown: Document verification status, source attribution

**API Integration:**
1. Standard Document Management APIs (not AI/ML-specific)
2. `GET /api/v1/golden-records/{gr_id}/sources` - Get source records
   - Request params: `gr_id`
   - Response used for: Document source tracking

**Data Flow:**
1. User opens screen → Load documents from all sources
2. User uploads document → Processing → Library → Signed → eVault
3. Real-time WebSocket → Document status updates

**UI Components:**
- **5-Pane Workflow:** REQ'D, LIBRARY, SIGNED, E-VAULT, DOWNLOAD
- **Unified Filter Bar:** Source, Type, Status filters

**User Actions:**
- **Upload Document** → Auto-targets correct pane
- **Filter Documents** → Cross-pane filtering
- **Sync eVault** → External sync

**Gaps & Required Features:**
- ✅ Document management is standard (not AI/ML-specific)
- ⚠️ **Future Enhancement:** Consider ML-based document classification

---

### Screen 11: Benefits & Entitlements

**Screen ID:** CIT-BEN-11  
**Screen Name:** Benefits & Entitlements  
**Purpose:** Unified dashboard showing current benefits, family breakdowns, historical trends, and AI forecasts.

**AI/ML Use Cases Used:**
- **AI-PLATFORM-02 (360° Profiles):**
  - Primary function: Family aggregation, consent-gated data
  - Data shown: Family allocation, vulnerability indicators
- **AI-PLATFORM-10 (Benefit Forecast):**
  - Primary function: Future benefit predictions with scenarios
  - Data shown: Forecast projections, confidence levels, probability estimates
- **AI-PLATFORM-09 (Proactive Inclusion):**
  - Primary function: Missing scheme notifications, inclusion gaps
  - Data shown: Missing schemes, inclusion alerts

**API Integration:**
1. `GET /api/v1/forecast/benefits?family_id={id}&horizon={months}` - Get benefit forecast
   - Request params: `family_id`, `horizon`
   - Response used for: FORECAST section - AI predictions with confidence bars
2. `GET /api/v1/inclusion/households?priority={level}` - Get priority households
   - Request params: `family_id`, `priority`
   - Response used for: Missing scheme alerts, inclusion gaps
3. `WebSocket /benefit-updates/{gr_id}` - Real-time benefit updates

**Data Flow:**
1. User opens screen → Load current benefits, forecast, history
2. User applies filters → All sections update
3. Real-time WebSocket → Status updates, expiry alerts

**UI Components:**
- **CURRENT Section:** Active benefits, pending benefits, renewal alerts
- **FORECAST Section:** AI predictions with confidence bars, scenario comparisons
- **HISTORY Section:** Payment timeline, export options

**User Actions:**
- **Apply Filters** → All sections update
- **View Forecast** → AI predictions loaded
- **Click Missing Scheme Alert** → Navigate to eligibility checker

**Gaps & Required Features:**
- ✅ Core features covered by AI-PLATFORM-02, 10, 09

---

### Screen 12: Payments & Ledger

**Screen ID:** CIT-BEN-12  
**Screen Name:** Payments & Ledger  
**Purpose:** Unified payment tracking dashboard combining DBT transaction details with month/year ledger views.

**AI/ML Use Cases Used:**
- **AI-PLATFORM-06 (Auto Approval & STP):**
  - Primary function: Payment trigger status, decision explanations
  - Data shown: Payment status linked to approval decisions

**API Integration:**
1. `GET /api/v1/decision/family/{familyId}` - Get decisions by family
   - Request params: `familyId`
   - Response used for: Link payments to approval decisions
2. Standard Payment Management APIs (not AI/ML-specific)

**Data Flow:**
1. User opens screen → Load transactions and ledger
2. User clicks transaction → Expand → Decision details
3. Real-time WebSocket → Payment status updates

**UI Components:**
- **TRANSACTIONS Pane:** DBT payments list with status badges
- **LEDGER Pane:** Monthly/yearly summary with progress bars
- **Smart Alerts:** Failed/pending payments with action guidance

**User Actions:**
- **Click Transaction** → Expand → Decision details, receipt
- **Click Failed Payment** → Resolution workflow

**Gaps & Required Features:**
- ✅ Core features covered by AI-PLATFORM-06

---

### Screen 13: Service Catalog

**Screen ID:** CIT-SERV-13  
**Screen Name:** Service Catalog  
**Purpose:** Provide citizens with a browsable catalog of 25+ government services available for online access.

**AI/ML Use Cases Used:**
- **None** - Service catalog browsing is standard (not AI/ML-specific)
  - Note: Could leverage AI-PLATFORM-03 or AI-PLATFORM-08 for service eligibility hints in future

**API Integration:**
1. Standard Service Management APIs (not AI/ML-specific)
   - Service metadata, categories, status indicators

**Data Flow:**
1. User opens screen → Load service catalog
2. User searches/filters → Results update
3. User clicks service → Navigate to service request form

**UI Components:**
- **Service Grid/List:** Categorized services with icons, descriptions
- **Search & Filter:** By department, service type, eligibility
- **Status Indicators:** Active, maintenance, upcoming

**User Actions:**
- **Browse Services** → View catalog
- **Search/Filter** → Filtered results
- **Click Service** → Navigate to CIT-SERV-14 (Service Request)

**Gaps & Required Features:**
- ✅ Service catalog is standard (not AI/ML-specific)
- ⚠️ **Future Enhancement:** Consider AI-PLATFORM-08 for eligibility hints on services

---

### Screen 14: Service Request

**Screen ID:** CIT-SERV-14  
**Screen Name:** Service Request  
**Purpose:** Enable citizens to submit requests for various government services with required details and document uploads.

**AI/ML Use Cases Used:**
- **AI-PLATFORM-01 (Golden Records):**
  - Primary function: Pre-fill form data from Golden Record
  - Data shown: Pre-populated personal information
- **AI-PLATFORM-05 (Auto Application Submission):**
  - Primary function: Form pre-filling from Golden Records & 360° Profiles
  - Data shown: Auto-populated fields, field sources

**API Integration:**
1. `GET /api/v1/golden-records/{gr_id}?summary=true` - Get Golden Record for pre-fill
   - Request params: `gr_id`
   - Response used for: Pre-populate form fields
2. Standard Service Request APIs (not AI/ML-specific)
   - Form submission, workflow initiation

**Data Flow:**
1. User opens service request form → Load Golden Record → Pre-fill form
2. User fills remaining fields → Submit → Service request created
3. User uploads documents → Document service → Attachments linked

**UI Components:**
- **Dynamic Form:** Service-specific fields with pre-filled data
- **Document Upload:** Supporting documents with validation
- **Preview:** Form preview before submission

**User Actions:**
- **View Form** → Pre-filled from Golden Record
- **Fill Fields** → Complete remaining fields
- **Upload Documents** → Document attachments
- **Submit Request** → Service request created with reference number

**Gaps & Required Features:**
- ✅ Core features covered by AI-PLATFORM-01, 05
- ⚠️ **Note:** AI-PLATFORM-05 is partial (needs external department API integration)

---

### Screen 15: Service Status & Feedback

**Screen ID:** CIT-SERV-15  
**Screen Name:** Service Status & Feedback  
**Purpose:** Unified service request dashboard combining real-time status tracking with embedded feedback collection.

**AI/ML Use Cases Used:**
- **None** - Service status tracking and feedback is standard (not AI/ML-specific)
  - Note: Could leverage AI-PLATFORM-11 (Personalized Nudging) for feedback reminders in future

**API Integration:**
1. Standard Service Request Management APIs (not AI/ML-specific)
   - Status tracking, timeline, feedback submission

**Data Flow:**
1. User opens screen → Load service requests
2. User views status → Timeline displayed
3. User submits feedback → Feedback recorded
4. Real-time WebSocket → Status updates

**UI Components:**
- **ACTIVE Section:** In-progress requests with progress bars
- **COMPLETED Section:** Finished requests with feedback controls
- **FEEDBACK DUE:** Completed requests awaiting rating

**User Actions:**
- **View Request Status** → Timeline displayed
- **Submit Feedback** → Ratings, comments recorded
- **Download Documents** → Acknowledgments, decision letters

**Gaps & Required Features:**
- ✅ Service status and feedback is standard (not AI/ML-specific)
- ⚠️ **Future Enhancement:** Consider AI-PLATFORM-11 for feedback reminders

---

### Screen 16: Notification Preferences

**Screen ID:** CIT-USER-16  
**Screen Name:** Notification Preferences  
**Purpose:** Enable citizens to customize their notification preferences for alerts, reminders, and messages.

**AI/ML Use Cases Used:**
- **AI-PLATFORM-11 (Personalized Nudging):**
  - Primary function: Get/update nudge preferences, channel optimization
  - Data shown: Current preferences, channel effectiveness data

**API Integration:**
1. `GET /api/v1/nudges/preferences?family_id={id}` - Get nudge preferences
   - Request params: `family_id`
   - Response used for: Current notification preferences
2. `POST /api/v1/nudges/preferences` - Update nudge preferences
   - Request body: `{family_id, channels, quiet_hours, preferences}`
   - Response used for: Save preference changes

**Data Flow:**
1. User opens screen → Load current notification preferences
2. User updates preferences → Save → Preferences updated
3. User sets quiet hours → DND period configured

**UI Components:**
- **Notification Types:** Scheme updates, application status, payments, security, feedback
- **Channel Selection:** Email, SMS, in-app push toggles
- **Quiet Hours:** Do-not-disturb period configuration
- **Test Notifications:** Verify settings button

**User Actions:**
- **Toggle Notification Types** → Preferences updated
- **Select Channels** → Channel preferences saved
- **Set Quiet Hours** → DND period configured
- **Test Notification** → Verification message sent

**Gaps & Required Features:**
- ✅ Core features covered by AI-PLATFORM-11

---

### Screen 17: Opt-Out Schemes

**Screen ID:** CIT-USER-17  
**Screen Name:** Opt-Out Schemes  
**Purpose:** Allow citizens to select schemes/programs to opt-out, review existing participation, and manage scheme exit preferences.

**AI/ML Use Cases Used:**
- **AI-PLATFORM-04 (Auto Intimation & Consent):**
  - Primary function: Consent revocation, opt-out management
  - Data shown: Active schemes, opt-out impact preview
- **AI-PLATFORM-10 (Benefit Forecast):**
  - Primary function: Impact preview showing benefit reduction
  - Data shown: Forecast impact of opt-out

**API Integration:**
1. `POST /api/v1/consent/revoke` - Revoke scheme consent (opt-out)
   - Request body: `{consent_id, family_id, scheme_id, reason: "OPT_OUT"}`
   - Response used for: Opt-out confirmation
2. `GET /api/v1/forecast/benefits?family_id={id}&scenario=opt_out` - Get opt-out impact
   - Request params: `family_id`, `scenario=opt_out`
   - Response used for: Benefit reduction preview
3. `GET /api/v1/consent/history?family_id={id}` - Get active scheme participations
   - Request params: `family_id`
   - Response used for: List of enrolled schemes

**Data Flow:**
1. User opens screen → Load active scheme participations
2. User selects scheme to opt-out → Load impact preview (benefit reduction)
3. User confirms opt-out → Consent revocation API → Scheme opt-out recorded
4. User enters reason (optional) → Audit trail updated

**UI Components:**
- **Active Schemes List:** Enrolled schemes with descriptions, benefits
- **Opt-Out Impact Preview:** Benefit reduction forecast, implications
- **Confirmation Dialog:** Opt-out confirmation with impact summary
- **Opt-Out History:** Past opt-outs with timestamps, reasons

**User Actions:**
- **View Active Schemes** → List of enrolled schemes displayed
- **Click "Opt-Out"** → Impact preview shown → Confirmation dialog
- **Confirm Opt-Out** → Consent revoked → Scheme opt-out recorded
- **Enter Reason** → Optional reason recorded in audit trail

**Gaps & Required Features:**
- ✅ Core features covered by AI-PLATFORM-04, 10

---

### Screen 18: Account & Security Settings

**Screen ID:** CIT-USER-18  
**Screen Name:** Account & Security Settings  
**Purpose:** Unified account management dashboard combining profile updates, communication preferences, password/MFA controls, session management, and security monitoring.

**AI/ML Use Cases Used:**
- **AI-PLATFORM-01 (Golden Records):**
  - Primary function: Profile contact updates, data export
  - Data shown: Profile data, contact information
- **AI-PLATFORM-07 (Beneficiary Detection):**
  - Primary function: Suspicious activity detection (future enhancement)
  - Data shown: Security alerts, anomaly indicators

**API Integration:**
1. `GET /api/v1/golden-records/{gr_id}?editable=true` - Get profile data
   - Request params: `gr_id`
   - Response used for: Profile & contact section
2. Standard Account/Security APIs (not AI/ML-specific)
   - Password change, MFA management, session management

**Data Flow:**
1. User opens screen → Load profile, security, notification preferences
2. User updates profile → Golden Records API → Profile updated
3. User changes password/MFA → Security API → Settings updated
4. User views sessions → Active sessions displayed

**UI Components:**
- **Profile & Contact:** Name, mobile, email, language, accessibility
- **Notifications & Consent:** Channels, quiet hours, data sharing
- **Password & MFA:** Password strength, MFA methods
- **Sessions & Security:** Active sessions, login history, suspicious activity

**User Actions:**
- **Update Profile** → Golden Records API → Profile updated
- **Change Password** → Security API → Password updated → All sessions logged out
- **Configure MFA** → MFA settings updated
- **View Sessions** → Active sessions displayed with device info

**Gaps & Required Features:**
- ✅ Core features covered by AI-PLATFORM-01
- ⚠️ **Future Enhancement:** Consider AI-PLATFORM-07 for ML-based suspicious activity detection

---

### Screen 19: Help & Support Hub

**Screen ID:** CIT-HELP-19  
**Screen Name:** Help & Support Hub  
**Purpose:** Unified support center combining self-service FAQs, knowledge base search, contact options, announcements, and embedded ticket creation/tracking.

**AI/ML Use Cases Used:**
- **None** - Help & support is standard (not AI/ML-specific)
  - Note: Could leverage AI-PLATFORM-11 for personalized help recommendations in future

**API Integration:**
1. Standard Customer Support APIs (not AI/ML-specific)
   - FAQ search, knowledge base, ticket creation

**Data Flow:**
1. User opens screen → Load FAQs, announcements, contact options
2. User searches → FAQ results displayed
3. User creates ticket → Ticket created with reference number
4. Authenticated users → My Tickets section displayed

**UI Components:**
- **Search Bar:** FAQ and knowledge base search
- **Top Articles:** Most relevant help articles
- **Announcements:** Latest service updates
- **Contact Options:** Helpline, chat, callback
- **Ticket Form:** Create new support ticket (collapsible)
- **My Tickets:** Active tickets (authenticated users only)

**User Actions:**
- **Search FAQs** → Search results displayed
- **View Articles** → Help article content
- **Create Ticket** → Ticket form → Submit → Ticket created
- **View My Tickets** → Navigate to CIT-HELP-20 (Tickets & Status)

**Gaps & Required Features:**
- ✅ Help & support is standard (not AI/ML-specific)
- ⚠️ **Future Enhancement:** Consider AI-powered search/NLP for better FAQ matching

---

### Screen 20: Tickets & Status

**Screen ID:** CIT-HELP-20  
**Screen Name:** Tickets & Status  
**Purpose:** Unified ticket management dashboard combining citizen ticket tracking, status updates, follow-up communication, and departmental routing visibility.

**AI/ML Use Cases Used:**
- **None** - Ticket management is standard (not AI/ML-specific)
  - Note: Could leverage AI-PLATFORM-11 for ticket status reminders in future

**API Integration:**
1. Standard Ticketing/CRM APIs (not AI/ML-specific)
   - Ticket status, timeline, comments, attachments

**Data Flow:**
1. User opens screen → Load tickets with status filters
2. User expands ticket → Timeline, comments, attachments displayed
3. User adds comment → Comment API → Communication updated
4. Real-time WebSocket → Status updates, agent replies

**UI Components:**
- **Ticket List:** Filtered by status/service with departmental assignment
- **Expandable Timeline:** Full history (Submitted → Routed → Resolved)
- **Communication Panel:** Agent replies, citizen follow-ups, attachments
- **Actions:** Comment, download docs, rate resolution (post-close)
- **New Ticket Form:** Embedded form (collapsible)

**User Actions:**
- **View Tickets** → Filtered list displayed
- **Expand Ticket** → Timeline, comments, attachments
- **Add Comment** → Follow-up communication
- **Rate Resolution** → Post-resolution feedback
- **Create New Ticket** → Ticket form → Submit

**Gaps & Required Features:**
- ✅ Ticket management is standard (not AI/ML-specific)
- ⚠️ **Future Enhancement:** Consider AI-PLATFORM-11 for ticket status reminders

---

## Summary Matrix

| Screen ID | Screen Name | Primary Use Cases | Secondary Use Cases | Integration Complexity |
|-----------|-------------|-------------------|---------------------|----------------------|
| CIT-AUTH-01 | Unified Login & SSO | AI-01 | - | Low |
| CIT-AUTH-02 | MFA & Security Challenge | - | AI-07 (future) | Low |
| CIT-PROF-03 | Profile Dashboard & 360° View | AI-01, AI-02 | AI-03, AI-11 | High |
| CIT-PROF-04 | Profile Edit & Verification | AI-01, AI-02 | - | Medium |
| CIT-SCHEME-05 | Scheme Catalog & Search | AI-03, AI-08 | - | Medium |
| CIT-SCHEME-06 | Scheme Details | AI-08 | AI-03 | Low |
| CIT-SCHEME-07 | Eligibility & Recommendations | AI-08, AI-03 | AI-01, AI-02 | High |
| CIT-CONSENT-08 | Consent & Clarifications | AI-04 | AI-05 | Medium |
| CIT-APP-09 | Applications Hub | AI-05, AI-06 | AI-07 | High |
| CIT-DOC-10 | Document Center | AI-01 | - | Low |
| CIT-BEN-11 | Benefits & Entitlements | AI-02, AI-10 | AI-09 | High |
| CIT-BEN-12 | Payments & Ledger | AI-06 | - | Low |
| CIT-SERV-13 | Service Catalog | - | - | Low |
| CIT-SERV-14 | Service Request | AI-01, AI-05 | - | Low |
| CIT-SERV-15 | Service Status & Feedback | - | - | Low |
| CIT-USER-16 | Notification Preferences | AI-11 | - | Low |
| CIT-USER-17 | Opt-Out Schemes | AI-04 | AI-10 | Medium |
| CIT-USER-18 | Account & Security Settings | AI-01 | AI-07 (future) | Low |
| CIT-HELP-19 | Help & Support Hub | - | - | Low |
| CIT-HELP-20 | Tickets & Status | - | - | Low |

---

## Integration Priority

### High Priority (Core Functionality - AI/ML Intensive)

**Must integrate for MVP:**
1. **CIT-PROF-03** (Profile Dashboard) - Core profile experience
2. **CIT-SCHEME-07** (Eligibility & Recommendations) - Primary discovery mechanism
3. **CIT-APP-09** (Applications Hub) - Application tracking with decisions
4. **CIT-BEN-11** (Benefits & Entitlements) - Core benefits experience with forecasts

### Medium Priority (Enhanced Features)

**Important for enhanced experience:**
5. **CIT-PROF-04** (Profile Edit & Verification) - Profile management
6. **CIT-SCHEME-05** (Scheme Catalog) - Discovery with recommendations
7. **CIT-CONSENT-08** (Consent & Clarifications) - Consent management
8. **CIT-USER-17** (Opt-Out Schemes) - Scheme management

### Low Priority (Standard Features)

**Standard functionality with minimal AI/ML:**
- All authentication screens (CIT-AUTH-01, 02)
- Document management (CIT-DOC-10)
- Payments (CIT-BEN-12)
- Service delivery (CIT-SERV-13, 14, 15)
- Settings and help (CIT-USER-16, 18, CIT-HELP-19, 20)

---

## Gaps Analysis & Required Features

### Critical Gaps

1. **AI-PLATFORM-05 (Auto Application Submission) - Partial Status**
   - ⚠️ **Impact:** Screens CIT-APP-09, CIT-SERV-14 depend on this
   - **Requirement:** External department API integration needed
   - **Workaround:** Manual application forms until integration complete

2. **Document OCR Service**
   - ⚠️ **Impact:** CIT-PROF-04 (Profile Edit) requires OCR for document uploads
   - **Requirement:** Document OCR service not currently in AI/ML use cases
   - **Recommendation:** Integrate OCR service or add to AI-PLATFORM-01 capabilities

### Enhancement Opportunities

3. **Risk-Based MFA (AI-PLATFORM-07)**
   - **Screen:** CIT-AUTH-02 (MFA)
   - **Enhancement:** ML-based risk scoring for step-up authentication

4. **ML-Based Document Classification**
   - **Screen:** CIT-DOC-10 (Document Center)
   - **Enhancement:** Auto-categorize uploaded documents

5. **AI-Powered FAQ Search**
   - **Screen:** CIT-HELP-19 (Help & Support Hub)
   - **Enhancement:** NLP-based search for better FAQ matching

6. **Personalized Help Recommendations (AI-PLATFORM-11)**
   - **Screen:** CIT-HELP-19, CIT-HELP-20
   - **Enhancement:** Context-aware help suggestions

### Performance Requirements

- **Real-time Updates:** WebSocket connections must handle 100 updates/sec
- **API Response Times:** Eligibility checks <200ms, Profile retrieval <300ms, Forecast generation <2s
- **ML Inference:** Confidence delta calculations <500ms, Document OCR <3s

---

## Questions for AI/ML Team

1. **Question about AI-PLATFORM-05:**
   - What is the timeline for external department API integration?
   - Can we provide manual fallback workflows until integration is complete?

2. **Question about Document OCR:**
   - Should OCR be part of AI-PLATFORM-01 or a separate service?
   - What OCR accuracy and processing time can we expect?

3. **Question about AI-PLATFORM-07 (Beneficiary Detection):**
   - Can we use this for risk-based authentication in CIT-AUTH-02?
   - What is the latency for real-time risk scoring?

4. **Question about Performance:**
   - Can we achieve <200ms eligibility checks under load (10K concurrent users)?
   - What caching strategies are recommended for profile and forecast data?

5. **Question about Future Enhancements:**
   - Which enhancements (ML-based document classification, AI-powered search) are planned?
   - What is the priority for these features?

---

**Document Version:** 1.0  
**Created:** 2024-12-30  
**Status:** ✅ Complete - All 20 screens mapped  
**Next Steps:** 
1. AI/ML Team to review mapping and address questions
2. Portal Development Team to begin integration planning
3. Prioritize High Priority screens for MVP development

