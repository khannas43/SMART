# Technical Design Document: Auto Intimation & Smart Consent Triggering

**Use Case ID:** AI-PLATFORM-04  
**Version:** 1.1  
**Last Updated:** 2024-12-29  
**Status:** ✅ Core Implementation Complete - Ready for Testing

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Data Architecture](#data-architecture)
4. [Component Design](#component-design)
5. [Message Personalization Design](#message-personalization-design)
6. [Consent Management Design](#consent-management-design)
7. [Campaign Management Design](#campaign-management-design)
8. [Smart Orchestration Design](#smart-orchestration-design)
9. [Multi-Channel Integration](#multi-channel-integration)
10. [API Design](#api-design)
11. [Data Flow & Processing Pipeline](#data-flow--processing-pipeline)
12. [Integration Points](#integration-points)
13. [Performance & Scalability](#performance--scalability)
14. [Security & Governance](#security--governance)
15. [Compliance & Privacy](#compliance--privacy)
16. [Deployment Architecture](#deployment-architecture)
17. [Monitoring & Observability](#monitoring--observability)
18. [Success Metrics](#success-metrics)
19. [Implementation Status](#implementation-status)
20. [Web Interface for Viewing Results](#web-interface-for-viewing-results)
21. [Future Enhancements](#future-enhancements)

---

## 1. Executive Summary

### 1.1 Purpose

The Auto Intimation & Smart Consent Triggering system automatically notifies citizens/families about eligible welfare schemes using pre-computed eligibility signals from Auto Identification of Beneficiaries (AI-PLATFORM-03), and collects explicit, auditable consent for enrolment or data use through personalized multi-channel notifications.

### 1.2 Key Capabilities

1. **Auto Intimation Engine**
   - Multi-channel notification delivery (SMS, mobile app, web, WhatsApp, email, IVR)
   - Personalized message generation with multi-language support
   - Campaign orchestration with batch scheduling and load management
   - Smart retry logic and escalation handling

2. **Smart Consent Management**
   - Soft consent for low-risk schemes (single click/tap)
   - Strong consent with OTP/e-sign for high-risk/financial schemes
   - Comprehensive audit trails with immutable logs
   - Consent lifecycle management (creation, renewal, revocation, expiration)

3. **Campaign Management**
   - Eligibility signal intake from AI-PLATFORM-03
   - Campaign policy application (thresholds, segments, fatigue limits)
   - Batch grouping and scheduling
   - Performance tracking and analytics

4. **Orchestration & Intelligence**
   - Fatigue management to prevent message overload
   - Vulnerability-based prioritization
   - Retry scheduling with escalation
   - Feedback loop for continuous improvement

### 1.3 Technology Stack

- **Backend**: Spring Boot 3.x, Java 17+
- **Python Services**: Python 3.12+ for campaign management, message personalization
- **Database**: PostgreSQL 14+ (`smart_warehouse.intimation` schema)
- **External Integrations**: Twilio (SMS/WhatsApp/IVR), SMTP (Email), Jan Aadhaar (OTP/e-sign)
- **Templates**: Jinja2 for message template rendering
- **Event Streaming**: Event logs for downstream integration

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Data Sources                                  │
├─────────────────────────────────────────────────────────────────┤
│  AI-PLATFORM-03 │ Golden Records │ 360° Profiles │ Jan Aadhaar  │
│  (Eligibility)   │  (Contact Info) │ (Preferences) │  (Auth)     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              Campaign Manager                                    │
│  (Intake, Policy Application, Batching, Scheduling)             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│           Message Personalizer                                   │
│  (Template Generation, Multi-Language, Multi-Channel)           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│           Smart Orchestrator                                     │
│  (Retry Logic, Fatigue Management, Escalation)                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              Multi-Channel Delivery                              │
├─────────────────────────────────────────────────────────────────┤
│  SMS │ Mobile App │ Web │ WhatsApp │ Email │ IVR               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│           Consent Manager                                        │
│  (Soft/Strong Consent, OTP/e-Sign, Audit Trails)                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Event Stream                                  │
├─────────────────────────────────────────────────────────────────┤
│  INTIMATION_SENT │ CONSENT_GIVEN │ CONSENT_REJECTED │ etc.      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│               Consumer Applications                              │
├─────────────────────────────────────────────────────────────────┤
│  Citizen Portal │ Department Portal │ Auto Application Service  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Architecture

#### 2.2.1 Campaign Manager
- **Purpose**: Intake eligibility signals, apply policies, create campaigns, schedule sends
- **Input**: Eligibility signals from AI-PLATFORM-03
- **Output**: Campaigns with scheduled candidates
- **Features**: Threshold filtering, segment targeting, batch grouping, load management

#### 2.2.2 Message Personalizer
- **Purpose**: Generate personalized messages for each channel and language
- **Input**: Candidate data, scheme metadata, templates
- **Output**: Channel-specific message content with deep links and actions
- **Features**: Multi-language support, template rendering, variable substitution

#### 2.2.3 Consent Manager
- **Purpose**: Handle consent collection, validation, storage, and audit
- **Input**: Consent responses from citizens
- **Output**: Consent records with audit trails
- **Features**: Soft/strong consent flows, OTP/e-sign integration, lifecycle management

#### 2.2.4 Smart Orchestrator
- **Purpose**: Manage retries, escalation, fatigue limits, and prioritization
- **Input**: Message delivery status, user preferences, fatigue data
- **Output**: Retry schedules, escalation flags, skip decisions
- **Features**: Configurable retry logic, fatigue tracking, vulnerability prioritization

#### 2.2.5 Channel Integrations
- **Purpose**: Deliver messages through various channels
- **Channels**: SMS, Mobile App (push), Web (inbox), WhatsApp, Email, IVR
- **Features**: Provider abstraction, delivery tracking, error handling

---

## 3. Data Architecture

### 3.1 Database Schema

#### 3.1.1 Intimation Schema (`smart_warehouse.intimation`)

**Database**: `smart_warehouse` (shared with other AI/ML use cases)  
**Schema**: `intimation`

**Core Tables:**

1. **campaigns**
   - Campaign metadata and configuration
   - Status tracking, scheduling, statistics
   - References: `scheme_code` → `public.scheme_master`

2. **campaign_candidates**
   - Individual candidates selected for intimation
   - Eligibility context, contact info, status tracking
   - Retry tracking, consent status linkage

3. **message_logs**
   - All messages sent through various channels
   - Delivery status, provider responses, click tracking
   - Full audit trail of message lifecycle

4. **consent_records**
   - Main consent records (soft and strong)
   - Consent type, level of assurance, validity
   - OTP/e-sign verification details

5. **consent_history**
   - Immutable audit trail of consent changes
   - Compliance and governance tracking

6. **user_preferences**
   - Communication preferences per family/member
   - Channel preferences, language, quiet hours, opt-out flags

7. **message_fatigue**
   - Message frequency tracking
   - Fatigue limit enforcement

8. **scheme_intimation_config**
   - Per-scheme configuration for intimation
   - Consent requirements, channel settings, retry policies

9. **message_templates**
   - Templates for different channels and languages
   - Jinja2 templates with variable substitution

10. **intimation_events**
    - Event log for intimation lifecycle
    - Integration with downstream systems

### 3.2 Data Sources

#### 3.2.1 Input Data Sources

1. **AI-PLATFORM-03 (Eligibility)**
   - `eligibility.eligibility_snapshots` - Eligibility evaluation results
   - `eligibility.candidate_lists` - Pre-computed worklists
   - Events: `POTENTIALLY_ELIGIBLE_IDENTIFIED`

2. **AI-PLATFORM-01 (Golden Records)**
   - Contact information (mobile, email)
   - Family structure
   - Demographics

3. **AI-PLATFORM-02 (360° Profiles)**
   - Vulnerability indicators
   - Under-coverage status
   - Preferences (if available)

4. **public.scheme_master**
   - Scheme metadata
   - Category, type, descriptions
   - Benefit information

#### 3.2.2 Output Data Destinations

1. **AI-PLATFORM-05 (Auto Application)**
   - Events: `CONSENT_GIVEN`
   - Trigger application submission

2. **Analytics Dashboards**
   - Campaign performance metrics
   - Consent rates, engagement metrics
   - Fairness and reach analytics

3. **Departmental Worklists**
   - Pending consents for follow-up
   - Escalation flags

---

## 4. Component Design

### 4.1 Campaign Manager

#### 4.1.1 Intake Process

**Input**: Eligibility signals from AI-PLATFORM-03

**Process**:
1. Query `eligibility.eligibility_snapshots` for `POTENTIALLY_ELIGIBLE_IDENTIFIED` status
2. Filter by eligibility score threshold (configurable per scheme)
3. Apply campaign policies (segments, geography, vulnerability)
4. Check fatigue limits (max messages per family/month)
5. Group candidates by scheme and geography
6. Create campaign records
7. Schedule sends based on load management

**Output**: Campaign records with scheduled candidates

**Implementation**: `src/campaign_manager.py`

```python
class CampaignManager:
    def intake_eligibility_signals(self, scheme_code: str, filters: dict) -> List[Campaign]
    def apply_campaign_policies(self, candidates: List[Candidate], scheme_code: str) -> List[Candidate]
    def create_campaign(self, scheme_code: str, candidates: List[Candidate]) -> Campaign
    def schedule_campaign_sends(self, campaign_id: int) -> None
```

#### 4.1.2 Campaign Policies

**Threshold Filtering**:
- Minimum eligibility score (default: 0.6)
- Priority threshold (default: 0.8)
- Vulnerability-based inclusion

**Segment Targeting**:
- Geography (district, block)
- Vulnerability level (VERY_HIGH, HIGH, MEDIUM, LOW)
- Under-coverage status
- Demographics (age groups, categories)

**Fatigue Management**:
- Max messages per family per month (default: 10)
- Max messages per scheme per month (default: 3)
- Respect quiet hours

### 4.2 Message Personalizer

#### 4.2.1 Template System

**Template Storage**: `intimation.message_templates`

**Template Variables**:
- Scheme information (name, category, benefit amount)
- Eligibility reason (why selected)
- Family/member context
- Deep link URLs
- Action buttons

**Template Rendering**: Jinja2 engine

**Implementation**: `src/message_personalizer.py`

```python
class MessagePersonalizer:
    def select_template(self, channel: str, language: str, message_type: str) -> Template
    def render_message(self, template: Template, context: dict) -> RenderedMessage
    def generate_deep_link(self, family_id: UUID, scheme_code: str, action: str) -> str
    def generate_action_buttons(self, scheme_code: str, consent_type: str) -> List[ActionButton]
```

#### 4.2.2 Multi-Language Support

**Language Detection Priority**:
1. User preferences (`user_preferences.preferred_language`)
2. Jan Aadhaar profile
3. Portal/app settings
4. Default (Hindi)

**Supported Languages**: Hindi, English (extensible)

**Template Variants**: Separate templates per language

#### 4.2.3 Channel-Specific Adaptation

**SMS**:
- Max 160 characters
- Include deep link or short code
- Concise message

**Mobile App**:
- Rich cards with images
- FAQ links
- Privacy information
- In-app actions

**Web Portal**:
- Widget integration
- Inbox notifications
- Detailed information pages

**WhatsApp**:
- Template-based (WhatsApp Business API)
- Media support (images, documents)
- Interactive buttons

**Email**:
- HTML format
- Rich formatting
- Attachment support (documents)

**IVR**:
- Voice-friendly text
- Keypad navigation
- Confirmation prompts

### 4.3 Consent Manager

#### 4.3.1 Consent Types

**Soft Consent** (LOA1):
- Single click/tap
- Low-risk schemes (HEALTH, EDUCATION, LIVELIHOOD)
- Session context recorded
- IP address, device ID tracked

**Strong Consent** (LOA2/LOA3):
- OTP verification (LOA2)
- e-Sign (LOA3) for very high-value schemes
- High-risk schemes (FINANCIAL, SOCIAL_SECURITY, PENSION)
- Full audit trail

#### 4.3.2 Consent Flow

**Soft Consent Flow**:
1. User receives intimation message
2. Clicks "Yes" action button
3. System records consent with session context
4. Consent stored in `consent_records`
5. Event `CONSENT_GIVEN` published

**Strong Consent Flow**:
1. User receives intimation message
2. Clicks "Yes" or navigates to consent page
3. System generates OTP via Jan Aadhaar
4. User enters OTP
5. System verifies OTP
6. Consent stored with OTP verification timestamp
7. Event `CONSENT_GIVEN` published

**e-Sign Flow** (for high-value schemes):
1. User navigates to consent page
2. System redirects to e-Sign provider (Jan Aadhaar/DigiLocker)
3. User completes e-Sign
4. System receives e-Sign transaction ID
5. Consent stored with e-Sign details
6. Event `CONSENT_GIVEN` published

#### 4.3.3 Consent Storage

**Record Structure** (`consent_records`):
- Consent type (soft/strong)
- Level of assurance (LOA1/LOA2/LOA3)
- Consent value (true/false)
- Verification details (OTP/e-sign)
- Validity period
- Terms version
- Audit fields (IP, device, session)

**History Tracking** (`consent_history`):
- Immutable log of all changes
- Action type (created, updated, revoked, expired)
- Change details JSONB
- 7-year retention for compliance

#### 4.3.4 Consent Lifecycle

1. **Creation**: Consent record created on user action
2. **Validation**: OTP/e-sign verification (if required)
3. **Active**: Consent valid and usable
4. **Expiration**: Consent expires after validity period
5. **Renewal**: User can renew before expiration
6. **Revocation**: User can revoke at any time

### 4.4 Smart Orchestrator

#### 4.4.1 Retry Logic

**Retry Schedule** (configurable per scheme):
- Default: 1 day, 7 days, 30 days
- Max retries: 3

**Retry Conditions**:
- No response from user
- Partial completion (OTP not entered)
- Delivery failure

**Retry Strategy**:
- Exponential backoff
- Different channel on retry (if available)
- Escalation after max retries

#### 4.4.2 Fatigue Management

**Tracking** (`message_fatigue` table):
- Messages per family per day/week/month
- Messages per scheme per family
- Last message timestamp

**Enforcement**:
- Skip if daily limit exceeded
- Skip if weekly limit exceeded
- Skip if monthly limit exceeded
- Skip if quiet hours active

**Exceptions**:
- High-priority schemes (configurable)
- Vulnerability-based override
- Manual campaign override

#### 4.4.3 Prioritization

**Priority Factors**:
1. Vulnerability level (VERY_HIGH > HIGH > MEDIUM > LOW)
2. Under-coverage indicator
3. Eligibility score
4. Geographic priority (if configured)

**Scheduling**:
- High-priority candidates scheduled first
- Batch processing respects priority order
- Load balancing across time windows

---

## 5. Message Personalization Design

### 5.1 Template System

**Template Storage**: Database-backed templates in `message_templates` table

**Template Format**: Jinja2 syntax

**Example SMS Template**:
```
[SMART] आप {{ scheme_name }} के लिए पात्र हो सकते हैं।
मासिक लाभ: ₹{{ benefit_amount }}
कारण: {{ eligibility_reason }}
हाँ/नहीं भेजें: {{ short_code }}
विवरण: {{ deep_link }}
```

**Example App Card Template**:
```json
{
  "title": "{{ scheme_name }} - आपके लिए एक योजना",
  "body": "आपकी उम्र {{ age }} वर्ष और आय {{ income_band }} है।",
  "benefit": "₹{{ benefit_amount }}/माह का लाभ",
  "actions": [
    {"label": "हाँ, मेरी सहमति दें", "action": "consent_yes"},
    {"label": "अधिक जानकारी", "action": "more_info"},
    {"label": "नहीं", "action": "consent_no"}
  ]
}
```

### 5.2 Variable Substitution

**Available Variables**:
- `scheme_name` - Scheme name
- `scheme_code` - Scheme code
- `benefit_amount` - Monthly/yearly benefit
- `eligibility_reason` - Why selected
- `family_id` - Family identifier
- `deep_link` - Deep link URL
- `short_code` - SMS response code
- `opt_out_link` - Opt-out link

### 5.3 Multi-Language Support

**Language Detection**:
1. Check `user_preferences.preferred_language`
2. Check Golden Records language
3. Check portal/app language setting
4. Default to Hindi

**Template Selection**:
- Query `message_templates` by `channel`, `message_type`, `language`
- Fallback to English if language not available
- Fallback to default template if type not found

---

## 6. Consent Management Design

### 6.1 Consent Classification

**By Scheme Category**:

| Category | Consent Type | LOA | Requirements |
|----------|-------------|-----|--------------|
| HEALTH | Soft | LOA1 | Single click/tap |
| EDUCATION | Soft | LOA1 | Single click/tap |
| LIVELIHOOD | Soft | LOA1 | Single click/tap |
| SOCIAL_SECURITY | Strong | LOA2 | OTP verification |
| PENSION | Strong | LOA2 | OTP verification |
| FINANCIAL | Strong | LOA3 | e-Sign required |

### 6.2 Consent Storage Schema

**consent_records Table**:
- `consent_type`: soft/strong
- `level_of_assurance`: LOA1/LOA2/LOA3
- `consent_value`: true/false (given/rejected)
- `consent_method`: click/tap/otp/e_sign/offline
- `consent_channel`: sms/mobile_app/web/whatsapp/ivr/offline
- `otp_verified`: boolean
- `e_sign_transaction_id`: string
- `valid_from`, `valid_until`: timestamps
- `terms_version`: string

### 6.3 Audit Trail

**consent_history Table**:
- Immutable log of all consent changes
- Action types: created, updated, revoked, expired, renewed
- Old/new status and values
- Change context (who, when, how, why)
- Full record snapshot in JSONB

**Retention**: 7 years for compliance

### 6.4 Consent Revocation

**User-Initiated**:
- Portal/app option to revoke
- SMS/WhatsApp opt-out
- Email unsubscribe link

**System-Initiated**:
- Expiration after validity period
- Policy change requiring re-consent

**Revocation Process**:
1. Update `consent_records.status` to 'revoked'
2. Set `revoked_at` timestamp
3. Record `revocation_reason`
4. Log in `consent_history`
5. Publish `CONSENT_REVOKED` event

---

## 7. Campaign Management Design

### 7.1 Campaign Creation Flow

1. **Intake Eligibility Signals**
   - Query `eligibility.eligibility_snapshots` for new/changed eligible candidates
   - Filter by `evaluation_status = 'POTENTIALLY_ELIGIBLE_IDENTIFIED'`
   - Apply scheme-specific thresholds

2. **Apply Campaign Policies**
   - Check `scheme_intimation_config` for scheme settings
   - Apply eligibility score threshold
   - Apply segment targeting (geography, vulnerability)
   - Check fatigue limits

3. **Create Campaign**
   - Insert into `campaigns` table
   - Status: 'draft' → 'scheduled'
   - Group candidates by scheme and geography

4. **Schedule Sends**
   - Calculate send times based on load management
   - Respect quiet hours and user preferences
   - Set `scheduled_send_at` for each candidate

5. **Execute Campaign**
   - Status: 'scheduled' → 'running'
   - Process candidates in batches
   - Send messages via appropriate channels

### 7.2 Campaign Types

**INITIAL**: First-time intimation for eligible candidates

**RETRY**: Retry for candidates who didn't respond

**ESCALATION**: Escalation after max retries (field worker follow-up)

**MANUAL**: Admin-initiated campaigns

### 7.3 Campaign Status Lifecycle

```
draft → scheduled → running → completed
                      ↓
                   paused → resumed → completed
                      ↓
                   cancelled
```

---

## 8. Smart Orchestration Design

### 8.1 Retry Scheduling

**Retry Schedule Configuration**:
- Per-scheme in `scheme_intimation_config.retry_schedule_days`
- Default: [1, 7, 30] days
- Max retries: 3

**Retry Logic**:
1. Check `campaign_candidates.retry_count`
2. If < max_retries, calculate `next_retry_at`
3. Schedule retry in queue
4. On retry, try different channel if available

### 8.2 Fatigue Management

**Fatigue Tracking**:
- `message_fatigue` table tracks counts per period
- Periods: daily, weekly, monthly
- Per-family and per-scheme limits

**Enforcement**:
- Check before scheduling send
- Skip if limit exceeded
- Log skip reason

**Exceptions**:
- High-priority schemes can override
- Vulnerability-based exceptions
- Admin override for manual campaigns

### 8.3 Escalation

**Escalation Triggers**:
- Max retries exhausted
- No response after escalation period
- High-priority candidates

**Escalation Actions**:
- Flag for field worker follow-up
- Different channel (e.g., IVR for elderly)
- Departmental worklist assignment

---

## 9. Multi-Channel Integration

### 9.1 Channel Abstraction

**Channel Interface**:
```python
class ChannelProvider:
    def send_message(self, message: Message) -> DeliveryResult
    def check_status(self, message_id: str) -> DeliveryStatus
    def handle_webhook(self, payload: dict) -> None
```

### 9.2 SMS Integration (Twilio)

**Configuration**:
- Provider: Twilio
- API credentials in environment variables
- Short code for responses

**Message Format**:
- Max 160 characters
- Deep link included
- Short code for Yes/No responses

**Delivery Tracking**:
- Provider message ID stored
- Webhook callbacks for delivery status
- Update `message_logs` with status

### 9.3 Mobile App Integration

**Push Notifications**:
- Firebase Cloud Messaging (FCM) or similar
- Rich notification payload
- Deep link to in-app consent page

**In-App Cards**:
- REST API endpoint for app to fetch pending intimations
- Rich card UI with images, actions
- In-app consent capture

### 9.4 Web Portal Integration

**Inbox Widget**:
- REST API for pending intimations
- Widget displays in citizen portal
- Click-through to consent page

**Consent Page**:
- Full scheme information
- Terms and conditions
- Consent action buttons
- OTP/e-sign integration

### 9.5 WhatsApp Integration (Twilio WhatsApp API)

**Template Messages**:
- Pre-approved templates (WhatsApp Business requirement)
- Media support (images, documents)
- Interactive buttons

**Configuration**:
- Template IDs for each message type
- Media URLs for scheme images
- Button actions mapped to consent actions

### 9.6 Email Integration

**SMTP Configuration**:
- SMTP server settings
- HTML email templates
- Attachment support (scheme documents)

**Email Format**:
- Rich HTML content
- Scheme images
- Action buttons (links)
- Privacy footer

### 9.7 IVR Integration

**Voice Flow**:
- Text-to-speech for message content
- Keypad navigation (press 1 for Yes, 2 for No)
- Confirmation prompts

**Provider**: Twilio Voice API or custom IVR system

**Use Case**: Low-literacy users, elderly citizens

---

## 10. API Design

### 10.1 Intimation APIs

#### 10.1.1 Schedule Intimation

**Endpoint**: `POST /api/v1/intimation/schedule`

**Request**:
```json
{
  "scheme_code": "CHIRANJEEVI",
  "family_ids": ["uuid1", "uuid2"],
  "priority": "high",
  "eligibility_meta": {
    "min_score": 0.7,
    "vulnerability_levels": ["VERY_HIGH", "HIGH"]
  }
}
```

**Response**:
```json
{
  "campaign_id": 123,
  "candidates_count": 50,
  "status": "scheduled",
  "scheduled_at": "2024-12-30T02:00:00Z"
}
```

#### 10.1.2 Get Intimation Status

**Endpoint**: `GET /api/v1/intimation/status?family_id={uuid}`

**Response**:
```json
{
  "family_id": "uuid",
  "pending_intimations": [
    {
      "scheme_code": "CHIRANJEEVI",
      "scheme_name": "Mukhyamantri Chiranjeevi Yojana",
      "status": "sent",
      "sent_at": "2024-12-29T10:00:00Z",
      "consent_status": "pending"
    }
  ],
  "completed_intimations": [...]
}
```

### 10.2 Consent APIs

#### 10.2.1 Capture Consent

**Endpoint**: `POST /api/v1/consent/capture`

**Request**:
```json
{
  "family_id": "uuid",
  "scheme_code": "CHIRANJEEVI",
  "consent_value": true,
  "consent_method": "click",
  "channel": "mobile_app",
  "session_id": "session123",
  "device_id": "device123",
  "ip_address": "192.168.1.1"
}
```

**Response**:
```json
{
  "consent_id": 456,
  "status": "given",
  "consent_type": "soft",
  "valid_until": "2025-12-29T00:00:00Z"
}
```

#### 10.2.2 Get Consent Status

**Endpoint**: `GET /api/v1/consent/status?family_id={uuid}&scheme_code={code}`

**Response**:
```json
{
  "consent_id": 456,
  "family_id": "uuid",
  "scheme_code": "CHIRANJEEVI",
  "status": "given",
  "consent_type": "soft",
  "consent_date": "2024-12-29T10:30:00Z",
  "valid_until": "2025-12-29T00:00:00Z"
}
```

#### 10.2.3 Revoke Consent

**Endpoint**: `POST /api/v1/consent/revoke`

**Request**:
```json
{
  "consent_id": 456,
  "revocation_reason": "user_request"
}
```

### 10.3 Campaign Management APIs

#### 10.3.1 Create Campaign

**Endpoint**: `POST /api/v1/campaigns/create`

**Request**:
```json
{
  "campaign_name": "CHIRANJEEVI_Q1_2025",
  "scheme_code": "CHIRANJEEVI",
  "campaign_type": "INITIAL",
  "eligibility_score_threshold": 0.6,
  "target_districts": ["Jaipur", "Udaipur"],
  "scheduled_at": "2024-12-30T02:00:00Z"
}
```

#### 10.3.2 Get Campaign Metrics

**Endpoint**: `GET /api/v1/campaigns/{campaign_id}/metrics`

**Response**:
```json
{
  "campaign_id": 123,
  "total_candidates": 1000,
  "messages_sent": 950,
  "messages_delivered": 900,
  "messages_failed": 50,
  "consents_given": 300,
  "consents_rejected": 100,
  "response_rate": 0.444,
  "delivery_rate": 0.947
}
```

---

## 11. Data Flow & Processing Pipeline

### 11.1 Intake Pipeline

```
AI-PLATFORM-03 (Eligibility Signals)
         ↓
Query eligibility_snapshots for POTENTIALLY_ELIGIBLE_IDENTIFIED
         ↓
Filter by scheme threshold and policies
         ↓
Check fatigue limits
         ↓
Create campaign and candidates
         ↓
Schedule sends
         ↓
Campaign ready for execution
```

### 11.2 Message Delivery Pipeline

```
Scheduled Campaign
         ↓
Load candidates in batches
         ↓
For each candidate:
  - Load contact info (Golden Records)
  - Load preferences (user_preferences)
  - Select channel based on preferences
  - Generate personalized message (Message Personalizer)
  - Send via channel provider
  - Log in message_logs
  - Update candidate status
         ↓
Track delivery status (webhooks)
         ↓
Update message_logs with final status
```

### 11.3 Consent Flow Pipeline

```
User receives message
         ↓
User clicks action (Yes/No/More info)
         ↓
If Yes:
  - Check consent type (soft/strong)
  - If soft: Record consent immediately
  - If strong: Initiate OTP/e-sign flow
         ↓
Verify OTP/e-sign (if required)
         ↓
Create consent_record
         ↓
Log in consent_history
         ↓
Publish CONSENT_GIVEN event
         ↓
Trigger Auto Application (AI-PLATFORM-05)
```

### 11.4 Retry Pipeline

```
Campaign Candidate (no response after X days)
         ↓
Check retry_count < max_retries
         ↓
Calculate next_retry_at
         ↓
Schedule retry
         ↓
On retry:
  - Try different channel (if available)
  - Send reminder message
  - Update retry_count
         ↓
If max retries exceeded:
  - Flag for escalation
  - Add to departmental worklist
```

---

## 12. Integration Points

### 12.1 Input Integrations

**AI-PLATFORM-03 (Eligibility)**:
- Event: `POTENTIALLY_ELIGIBLE_IDENTIFIED`
- Table: `eligibility.eligibility_snapshots`
- Query: New/changed eligible candidates

**AI-PLATFORM-01 (Golden Records)**:
- Contact information (mobile, email)
- Family structure
- Demographics

**AI-PLATFORM-02 (360° Profiles)**:
- Vulnerability indicators
- Under-coverage status
- Preferences

**Jan Aadhaar**:
- OTP generation/verification
- e-Sign services
- Authentication

### 12.2 Output Integrations

**AI-PLATFORM-05 (Auto Application)**:
- Event: `CONSENT_GIVEN`
- Trigger: Automatic application submission

**Analytics Dashboards**:
- Campaign performance metrics
- Consent rates
- Engagement metrics
- Fairness analytics

**Departmental Worklists**:
- Pending consents
- Escalation flags
- Follow-up tasks

**Event Stream**:
- `INTIMATION_SENT`
- `CONSENT_GIVEN`
- `CONSENT_REJECTED`
- `CONSENT_REVOKED`
- `CONSENT_EXPIRED`

---

## 13. Performance & Scalability

### 13.1 Scalability Considerations

**Database**:
- Indexed queries on `campaign_candidates` (family_id, status, scheduled_send_at)
- Partitioning `message_logs` by date (if needed)
- Read replicas for analytics queries

**Message Delivery**:
- Async processing with message queues
- Batch processing for campaigns
- Rate limiting per channel provider

**Consent Processing**:
- Async consent record creation
- Event-driven updates
- Caching for frequent consent status checks

### 13.2 Performance Targets

- Campaign creation: < 1 second per 1000 candidates
- Message generation: < 100ms per message
- Consent capture: < 200ms end-to-end
- API response time: < 500ms (p95)

### 13.3 Load Management

**Campaign Scheduling**:
- Distribute sends across time windows
- Respect quiet hours
- Rate limiting per channel

**Batch Processing**:
- Process campaigns in batches of 1000
- Parallel processing with worker pools
- Progress tracking and resume on failure

---

## 14. Security & Governance

### 14.1 Security Measures

**Data Protection**:
- Encrypt sensitive data at rest
- TLS for all API communications
- Secure storage of provider API keys

**Authentication & Authorization**:
- API key authentication for services
- Role-based access control for admin APIs
- OTP/e-sign for strong consent

**Audit Logging**:
- All consent actions logged
- Immutable consent history
- 7-year retention for compliance

### 14.2 Privacy & Consent

**Data Minimization**:
- Only collect necessary data
- Clear data usage disclosure
- Opt-out mechanisms

**Consent Transparency**:
- Plain language explanations
- Clear scheme descriptions
- Explicit consent options

**User Rights**:
- Right to revoke consent
- Right to access consent history
- Right to opt-out of communications

---

## 15. Compliance & Privacy

### 15.1 DPDP Compliance

**Consent Requirements**:
- Explicit consent for data use
- Clear purpose specification
- Withdrawal mechanisms

**Data Processing**:
- Lawful basis for processing
- Data minimization
- Purpose limitation

**User Rights**:
- Right to access
- Right to correction
- Right to erasure
- Right to portability

### 15.2 Jan Aadhaar Compliance

**Authentication**:
- OTP via Jan Aadhaar for strong consent
- e-Sign via Jan Aadhaar for high-value schemes

**Data Sharing**:
- Secure data sharing protocols
- Audit trails for data access

### 15.3 Fairness & Non-Discrimination

**Reach Monitoring**:
- Track delivery rates by geography
- Track delivery rates by demographics
- Alert on under-reach

**Offline Options**:
- e-Mitra integration
- Field worker capture
- Assisted consent options

---

## 16. Deployment Architecture

### 16.1 Component Deployment

**Python Services**:
- Campaign Manager (scheduled jobs)
- Message Personalizer (on-demand)
- Smart Orchestrator (background workers)

**Spring Boot APIs**:
- Intimation APIs
- Consent APIs
- Campaign Management APIs

**Database**:
- PostgreSQL (shared `smart_warehouse` database)

**External Services**:
- Twilio (SMS/WhatsApp/IVR)
- SMTP (Email)
- Jan Aadhaar (OTP/e-sign)

### 16.2 Deployment Patterns

**Scheduled Jobs**:
- Cron jobs for intake process
- Scheduled campaign execution
- Retry queue processing

**Event-Driven**:
- Event listeners for eligibility signals
- Webhook handlers for channel providers
- Event publishers for downstream systems

**API Services**:
- REST APIs for portal integration
- Webhook endpoints for providers
- Admin APIs for campaign management

---

## 17. Monitoring & Observability

### 17.1 Metrics

**Campaign Metrics**:
- Campaigns created/completed
- Candidates processed
- Messages sent/delivered/failed
- Delivery rates by channel

**Consent Metrics**:
- Consents given/rejected/revoked
- Consent rates by scheme
- OTP/e-sign success rates
- Consent expiration tracking

**Performance Metrics**:
- API response times
- Message generation latency
- Database query performance
- Channel provider latency

### 17.2 Alerts

**Delivery Issues**:
- Low delivery rate (< 95%)
- High failure rate (> 5%)
- Channel provider errors

**Consent Issues**:
- Low consent rate (< 10%)
- High revocation rate
- OTP/e-sign failures

**System Issues**:
- Campaign processing delays
- Database connection issues
- API errors

### 17.3 Dashboards

**Campaign Dashboard**:
- Active campaigns
- Campaign performance
- Delivery and response rates

**Consent Dashboard**:
- Consent rates by scheme
- Consent lifecycle tracking
- Audit trail views

**Fairness Dashboard**:
- Reach by geography
- Reach by demographics
- Under-reach alerts

---

## 18. Success Metrics

### 18.1 Reach & Engagement

- **Delivery Rate**: > 95% messages delivered
- **Response Rate**: > 10% users respond
- **Unique Households Reached**: Track per campaign

### 18.2 Impact Metrics

- **Enrolment Rate Increase**: % increase after intimation rollout
- **Time to Consent**: Reduction in time from eligibility to consent
- **Under-Served Reach**: % of vulnerable households reached

### 18.3 Quality & Trust

- **Complaint Rate**: < 1% complaints/opt-outs
- **Audit Accuracy**: 100% correct consent records (sampled)
- **User Satisfaction**: Track via surveys (if implemented)

---

## 19. Implementation Status

### 19.1 Completed

- ✅ Database schema design and implementation
- ✅ Configuration files (db_config.yaml, use_case_config.yaml)
- ✅ README and documentation structure
- ✅ Campaign Manager implementation
  - Eligibility signal intake
  - Campaign policy application
  - Campaign creation and scheduling
- ✅ Message Personalizer implementation
  - Template rendering
  - Multi-language support
  - Channel-specific message generation
  - SMS truncation for 160-character limit
- ✅ Consent Manager implementation
  - Soft and strong consent creation
  - Consent verification
  - Audit trail logging
  - Event publishing
- ✅ Smart Orchestrator implementation
  - Retry logic
  - Fatigue management
  - Escalation handling
- ✅ Channel integration code (abstracted providers)
  - SMS Provider
  - WhatsApp Provider
  - Email Provider
  - IVR Provider
  - App Push Provider
- ✅ Testing scripts
  - test_intake.py - Campaign intake testing
  - test_message_personalization.py - Message generation testing
  - test_consent.py - Consent management testing
  - test_end_to_end.py - Full pipeline testing
- ✅ Web interface for viewing campaign results (`/ai04`)
- ✅ Database initialization scripts
- ✅ Technical design document

### 19.2 In Progress

- 🚧 Spring Boot REST API implementation
  - IntimationController
  - ConsentController
  - CampaignController
- 🚧 Channel provider actual integrations (currently mocked)
  - Twilio SMS/WhatsApp/IVR integration
  - SMTP email integration
  - Firebase FCM push notifications

### 19.3 Pending (Future/Production Items)

**Production Deployment:**
- ⏳ Actual channel provider API keys and configuration (Twilio, SMTP, Firebase)
- ⏳ Jan Aadhaar OTP/e-sign integration (ready for integration, needs API keys)
- ⏳ Production deployment configuration
- ⏳ Performance testing and optimization
- ⏳ Monitoring and alerting setup
- ⏳ Portal UI integration
- ⏳ End-to-end integration with AI-PLATFORM-05 (Auto Application)

**Testing & Validation:**
- ⏳ Load testing with large datasets
- ⏳ Stress testing for high-volume campaigns
- ⏳ Integration testing with actual channel providers

**Note**: All core functionality is complete and tested. The pending items are primarily production deployment tasks and external service integrations that require API keys/credentials.

---

## 20. Web Interface for Viewing Results

### 20.1 Purpose

A web-based interface for viewing intimation campaign results, messages, and consent records in a browser for development and testing purposes. This provides a quick way to visualize campaign data without requiring portal access.

### 20.2 Implementation

**Location**: Integrated into Eligibility Rules Viewer at `/ai04` endpoint

**File**: `ai-ml/use-cases/03_identification_beneficiary/scripts/view_rules_web.py` (routes for `/ai04`)

**Technology**: Flask web application with Jinja2 templates

### 20.3 Features

#### 20.3.1 Statistics Dashboard

Displays key metrics:
- Total campaigns created
- Total candidates processed
- Total messages created
- Total consents recorded

#### 20.3.2 Campaign View

Shows recent campaigns with:
- Campaign ID and name
- Scheme code
- Candidate count
- Status (draft, scheduled, running, completed, etc.)
- Creation timestamp

#### 20.3.3 Candidate View

Displays recent candidates with:
- Candidate ID
- Family ID (truncated for privacy)
- Scheme code
- Eligibility score
- Priority score
- Associated campaign ID

#### 20.3.4 Messages View

Shows recent messages with:
- Message ID
- Family ID (truncated)
- Scheme code
- Channel (SMS, mobile_app, web, WhatsApp, email, IVR)
- Language
- Status (queued, sent, delivered, failed, etc.)
- Message preview (truncated)
- Creation timestamp

#### 20.3.5 Consent Records View

Displays recent consents with:
- Consent ID
- Family ID (truncated)
- Scheme code
- Consent type (soft/strong)
- Status (valid, expired, revoked, etc.)
- Consent method (click, tap, OTP, e_sign, etc.)
- Channel used
- Creation timestamp

### 20.4 Access

**URL**: `http://127.0.0.1:5001/ai04`

**Server**: Runs on the same Flask server as Eligibility Rules Viewer (port 5001)

**Navigation**: 
- Main Eligibility Rules: `http://127.0.0.1:5001`
- Campaign Results: `http://127.0.0.1:5001/ai04`

### 20.5 Usage

1. **Start the Server**:
   ```bash
   cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
   source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
   python scripts/view_rules_web.py
   ```

2. **Access in Browser**:
   - Open `http://127.0.0.1:5001/ai04` in your web browser
   - Click "Refresh Data" button to reload latest data from database

3. **Features**:
   - Real-time data from database
   - Color-coded status badges
   - Responsive design
   - Refresh button for latest data
   - Back link to Eligibility Rules viewer

### 20.6 Data Source

- **Database**: `smart_warehouse`
- **Schema**: `intimation`
- **Tables Queried**:
  - `intimation.campaigns`
  - `intimation.campaign_candidates`
  - `intimation.message_logs`
  - `intimation.consent_records`

### 20.7 Limitations

- **Read-only**: This is a view-only interface for development/testing
- **Not for Production**: For production use, integrate with portal UI or use REST APIs
- **Limited Pagination**: Shows recent 10-20 records per table
- **No Filtering**: Basic view without advanced filtering/search

### 20.8 Future Enhancements

- Add filtering and search capabilities
- Add pagination for large datasets
- Add export functionality (CSV, JSON)
- Add real-time updates (WebSocket)
- Add drill-down views for detailed information
- Add charts and visualizations

---

## 21. Future Enhancements

### 20.1 Advanced Personalization

- A/B testing for message templates
- ML-based message optimization
- Dynamic content based on user behavior

### 20.2 Enhanced Channels

- RCS (Rich Communication Services)
- Voice assistants integration
- Social media channels

### 20.3 Analytics & Insights

- Predictive consent modeling
- Churn prediction
- Campaign ROI analysis

### 20.4 Automation

- Auto-optimization of campaign policies
- Dynamic retry schedule adjustment
- Automated A/B testing

---

**Document Version**: 1.1  
**Last Updated**: 2024-12-29  
**Next Review**: 2025-01-15

