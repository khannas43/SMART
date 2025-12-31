# Technical Design Document: Personalized Communication & Nudging

**Use Case ID:** AI-PLATFORM-11  
**Version:** 1.0  
**Last Updated:** 2024-12-30  
**Status:** ✅ Complete - Core Implementation

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Data Architecture](#data-architecture)
4. [Component Design](#component-design)
5. [Channel Optimization](#channel-optimization)
6. [Send Time Optimization](#send-time-optimization)
7. [Content Personalization](#content-personalization)
8. [Fatigue Management](#fatigue-management)
9. [API Design](#api-design)
10. [Data Flow & Processing Pipeline](#data-flow--processing-pipeline)
11. [Integration Points](#integration-points)
12. [Performance & Scalability](#performance--scalability)
13. [Security & Governance](#security--governance)
14. [Compliance & Privacy](#compliance--privacy)
15. [Deployment Architecture](#deployment-architecture)
16. [Monitoring & Observability](#monitoring--observability)
17. [Success Metrics](#success-metrics)
18. [Implementation Status](#implementation-status)
19. [Web Interface](#web-interface)
20. [Future Enhancements](#future-enhancements)

---

## 1. Executive Summary

### 1.1 Purpose

The Personalized Communication & Nudging system optimizes reminders and informational messages for renewals, missing documents, pending consents/applications, and important deadlines by learning from citizen behavior and outcomes. The system chooses the optimal channel (SMS/app/web/WhatsApp/IVR), timing, frequency, and content variant that maximizes response while respecting consent, fatigue limits, and ethical "nudge" practices for public policy.

### 1.2 Key Capabilities

1. **Channel and Send Time Optimization**
   - ML-based channel selection (SMS, App Push, Web Inbox, WhatsApp, IVR, Assisted Visit)
   - Time window optimization (morning/afternoon/evening, weekday/weekend)
   - Multi-class classification for channel selection
   - Probability prediction for send time windows

2. **Content and Frequency Personalization**
   - Template selection based on past effectiveness (bandit/A-B testing)
   - Content personalization with family-specific variables
   - Fatigue management with vulnerability adjustments
   - Cooldown periods after responses/complaints

3. **Multi-Channel Support**
   - SMS (with DLT compliance, 160 char limit)
   - App Push Notifications (rich content, deep linking)
   - Web Inbox Messages (attachments, read/click tracking)
   - WhatsApp Business API (templates, read receipts)
   - IVR (multilingual, callback support)
   - Assisted Field Visits (scheduling, field staff coordination)

4. **Governance and Ethics**
   - Consent management (DPDP aligned)
   - Opt-out respect
   - Hard frequency limits (policy-driven)
   - Vulnerability-sensitive messaging
   - No manipulative/coercive content
   - Transparent purpose, easy decline

### 1.3 Technology Stack

- **Backend**: Spring Boot 3.x, Java 17+
- **Python Services**: Python 3.12+ for ML models and optimization
- **Database**: PostgreSQL 14+ (`smart.nudging` schema)
- **ML Libraries**: scikit-learn (RandomForest, LogisticRegression, GradientBoosting)
- **Integration**: Golden Records, 360° Profiles, Eligibility Engine
- **Frontend**: Web viewer (Flask), portal/app integration ready

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Input Sources                                 │
├─────────────────────────────────────────────────────────────────┤
│  AI-PLATFORM-02  │ AI-PLATFORM-05  │ Events  │ Golden Records │
│  (360° Profile)  │ (Applications)   │ (Triggers)│ (Family Data) │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│          Personalized Communication & Nudging System             │
├─────────────────────────────────────────────────────────────────┤
│  NudgeOrchestrator                                              │
│  ├── FatigueModel (limit checks)                                │
│  ├── ChannelOptimizer (ML-based selection)                      │
│  ├── SendTimeOptimizer (time window prediction)                 │
│  └── ContentPersonalizer (template + personalization)           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Output Channels                               │
├─────────────────────────────────────────────────────────────────┤
│  SMS │ App Push │ Web Inbox │ WhatsApp │ IVR │ Assisted Visit  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Feedback Loop                                 │
├─────────────────────────────────────────────────────────────────┤
│  Delivered │ Opened │ Clicked │ Responded │ Completed │ Ignored │
│  → Continuous Learning → Model Updates                          │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Overview

1. **NudgeOrchestrator**: Main workflow coordinator
   - Validates fatigue limits
   - Checks consent/preferences
   - Orchestrates channel, time, and content selection
   - Creates nudge records
   - Handles feedback processing

2. **FatigueModel**: Enforces frequency limits
   - Daily/weekly/monthly counters per family
   - Vulnerability category adjustments
   - Cooldown period enforcement

3. **ChannelOptimizer**: ML-based channel selection
   - Features: past engagement, scheme type, urgency, geography, demographics
   - Fallback rules (no digital footprint → assisted visit)
   - Consent/opt-out respect

4. **SendTimeOptimizer**: Time window optimization
   - Predicts optimal send time (morning/afternoon/evening)
   - Learns from historical response patterns
   - Applies time restrictions (no SMS after 8 PM)

5. **ContentPersonalizer**: Template selection and personalization
   - Bandit algorithms (UCB, Thompson Sampling, Epsilon-Greedy)
   - A-B testing support
   - Template effectiveness tracking
   - Content variable substitution

---

## 3. Data Architecture

### 3.1 Database Schema

The system uses the `nudging` schema in PostgreSQL with 10 core tables:

#### 3.1.1 Core Tables

**`nudges`** - Main nudge records
- `nudge_id` (UUID, PK)
- `family_id` (VARCHAR)
- `action_type` (VARCHAR) - renewal, missing_doc, consent, deadline, informational
- `action_context` (JSONB) - scheme_name, deadline, document_type, etc.
- `urgency` (VARCHAR) - CRITICAL, HIGH, MEDIUM, LOW
- `expiry_date` (TIMESTAMP)
- `scheduled_channel` (VARCHAR)
- `scheduled_time` (TIMESTAMP)
- `template_id` (UUID, FK)
- `personalized_content` (TEXT)
- `status` (VARCHAR) - SCHEDULED, SENT, DELIVERED, OPENED, CLICKED, RESPONDED, COMPLETED, FAILED
- `delivery_status` (VARCHAR)
- `sent_at`, `delivered_at`, `opened_at`, `clicked_at`, `responded_at`, `completed_at` (TIMESTAMP)

**`nudge_channels`** - Available communication channels
- `channel_code` (VARCHAR, PK) - SMS, APP_PUSH, WEB_INBOX, WHATSAPP, IVR, ASSISTED_VISIT
- `channel_name` (VARCHAR)
- `description` (TEXT)
- `capabilities` (JSONB) - max_length, template_required, delivery_tracking, etc.
- `cost_per_unit` (DECIMAL)
- `is_active` (BOOLEAN)

**`nudge_templates`** - Message templates by action type
- `template_id` (UUID, PK)
- `action_type` (VARCHAR)
- `template_name` (VARCHAR)
- `template_content` (TEXT) - with placeholders like {family_name}, {scheme_name}, {deadline}
- `language_code` (VARCHAR) - en, hi, ta, etc.
- `channel_code` (VARCHAR)
- `tone` (VARCHAR) - urgent, friendly, neutral, supportive
- `length_category` (VARCHAR) - short, medium, long
- `approval_status` (VARCHAR) - DRAFT, APPROVED, REJECTED
- `approved_by`, `approved_at` (TIMESTAMP)

**`nudge_history`** - Historical tracking for learning
- `history_id` (UUID, PK)
- `nudge_id` (UUID, FK)
- `family_id` (VARCHAR)
- `channel_code` (VARCHAR)
- `action_type` (VARCHAR)
- `template_id` (UUID)
- `sent_time` (TIMESTAMP)
- `time_window` (VARCHAR) - MORNING, AFTERNOON, EVENING, NIGHT
- `day_of_week` (INTEGER), `is_weekend` (BOOLEAN)
- `delivered`, `opened`, `clicked`, `responded`, `completed`, `ignored` (BOOLEAN)

#### 3.1.2 Learning & Optimization Tables

**`fatigue_tracking`** - Family-level fatigue counters
- `tracking_id` (UUID, PK)
- `family_id` (VARCHAR)
- `period_type` (VARCHAR) - DAY, WEEK, MONTH
- `period_start` (DATE)
- `nudge_count` (INTEGER)
- `last_nudge_time` (TIMESTAMP)
- `vulnerability_category` (VARCHAR)

**`channel_preferences`** - Learned channel preferences per family
- `preference_id` (UUID, PK)
- `family_id` (VARCHAR)
- `channel_code` (VARCHAR)
- `action_type` (VARCHAR)
- `engagement_score` (DECIMAL) - computed from history
- `response_rate` (DECIMAL)
- `completion_rate` (DECIMAL)
- `last_updated_at` (TIMESTAMP)

**`send_time_preferences`** - Learned optimal send times
- `preference_id` (UUID, PK)
- `family_id` (VARCHAR)
- `channel_code` (VARCHAR)
- `time_window` (VARCHAR)
- `day_of_week` (INTEGER)
- `response_probability` (DECIMAL)
- `sample_count` (INTEGER)

**`content_effectiveness`** - Template effectiveness metrics
- `effectiveness_id` (UUID, PK)
- `template_id` (UUID, FK)
- `action_type` (VARCHAR)
- `channel_code` (VARCHAR)
- `effectiveness_score` (DECIMAL) - computed metric
- `response_rate` (DECIMAL)
- `completion_rate` (DECIMAL)
- `total_sends` (INTEGER)
- `last_updated_at` (TIMESTAMP)

**`family_consent`** - Consent and preferences per family
- `consent_id` (UUID, PK)
- `family_id` (VARCHAR)
- `consent_given` (BOOLEAN)
- `preferred_language` (VARCHAR)
- `preferred_channels` (ARRAY)
- `opted_out_channels` (ARRAY)
- `last_updated_at` (TIMESTAMP)

**`nudge_audit_logs`** - Audit trail for compliance
- `log_id` (UUID, PK)
- `event_type` (VARCHAR) - NUDGE_SCHEDULED, NUDGE_SENT, FEEDBACK_RECEIVED, etc.
- `entity_type` (VARCHAR)
- `entity_id` (VARCHAR)
- `user_id` (VARCHAR)
- `event_data` (JSONB)
- `created_at` (TIMESTAMP)

### 3.2 Data Relationships

```
nudges (1) ──→ (N) nudge_history
nudges (N) ──→ (1) nudge_templates
nudges (N) ──→ (1) nudge_channels (via scheduled_channel)
fatigue_tracking (N) ──→ (1) family_consent (via family_id)
channel_preferences (N) ──→ (1) nudge_channels (via channel_code)
content_effectiveness (N) ──→ (1) nudge_templates (via template_id)
```

---

## 4. Component Design

### 4.1 NudgeOrchestrator

**Location**: `src/services/nudge_orchestrator.py`

**Responsibilities**:
- End-to-end nudge scheduling workflow
- Coordinates all optimization components
- Creates nudge records
- Processes feedback events
- Maintains audit trail

**Key Methods**:

```python
def schedule_nudge(
    action_type: str,
    family_id: str,
    urgency: str,
    expiry_date: Optional[datetime] = None,
    action_context: Optional[Dict[str, Any]] = None,
    scheduled_by: str = 'SYSTEM'
) -> Dict[str, Any]:
    """
    Main workflow:
    1. Check fatigue limits (FatigueModel)
    2. Get family preferences (consent, language)
    3. Select optimal channel (ChannelOptimizer)
    4. Select optimal send time (SendTimeOptimizer)
    5. Select and personalize content (ContentPersonalizer)
    6. Create nudge record
    7. Log audit trail
    """

def record_feedback(
    nudge_id: str,
    event_type: str,  # DELIVERED, OPENED, CLICKED, RESPONDED, COMPLETED, IGNORED
    timestamp: datetime
) -> Dict[str, Any]:
    """
    Updates nudge status and adds to history for learning.
    """

def get_nudge_history(
    family_id: str,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Retrieves nudge history for a family.
    """
```

### 4.2 FatigueModel

**Location**: `src/models/fatigue_model.py`

**Responsibilities**:
- Track nudge counts per family (daily/weekly/monthly)
- Enforce fatigue limits based on vulnerability category
- Check cooldown periods
- Update counters on nudge send

**Key Methods**:

```python
def check_fatigue_limits(
    family_id: str,
    urgency: str = 'MEDIUM'
) -> Dict[str, Any]:
    """
    Returns:
    {
        'allowed': bool,
        'reason': str,
        'counts': {
            'daily': int,
            'weekly': int,
            'monthly': int
        },
        'limits': {
            'daily': int,
            'weekly': int,
            'monthly': int
        }
    }
    """

def get_vulnerability_category(
    family_id: str
) -> str:
    """
    Returns: HIGH, MEDIUM, or LOW
    Based on family profile data.
    """

def increment_fatigue_counter(
    family_id: str,
    period_type: str  # DAY, WEEK, MONTH
):
    """
    Increments counter after nudge is sent.
    """
```

### 4.3 ChannelOptimizer

**Location**: `src/models/channel_optimizer.py`

**Responsibilities**:
- ML-based channel selection
- Fallback rule application
- Historical engagement analysis
- Consent/opt-out respect

**Key Methods**:

```python
def select_best_channel(
    family_id: str,
    action_type: str,
    urgency: str,
    context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Returns:
    {
        'channel_code': str,
        'confidence': float,
        'reason': str,
        'alternatives': [...]
    }
    """

def _calculate_channel_score(
    family_id: str,
    channel_code: str,
    action_type: str,
    urgency: str,
    context: Dict[str, Any]
) -> float:
    """
    Computes score based on:
    - Historical engagement rate
    - Channel capabilities
    - Urgency level
    - Cost considerations
    """
```

**ML Model**:
- Type: RandomForestClassifier (or GradientBoostingClassifier)
- Features:
  - Past engagement by channel (response_rate, completion_rate)
  - Scheme type
  - Urgency level
  - Geography
  - Demographics
  - Vulnerability category
  - Device usage pattern
  - Connectivity pattern

### 4.4 SendTimeOptimizer

**Location**: `src/models/send_time_optimizer.py`

**Responsibilities**:
- Predict optimal send time windows
- Learn from historical response patterns
- Apply time restrictions

**Key Methods**:

```python
def select_best_time(
    family_id: str,
    channel_code: str,
    action_type: str,
    urgency: str
) -> Dict[str, Any]:
    """
    Returns:
    {
        'scheduled_time': datetime,
        'time_window': str,  # MORNING, AFTERNOON, EVENING
        'confidence': float,
        'reason': str
    }
    """

def _predict_time_window_probability(
    family_id: str,
    channel_code: str,
    time_window: str
) -> float:
    """
    Predicts probability of response for a time window.
    Uses LogisticRegression model with historical data.
    """
```

**ML Model**:
- Type: LogisticRegression (probability prediction)
- Features:
  - Past engagement by time window
  - Day of week
  - Time of day bucket
  - Urgency level
  - Channel type

### 4.5 ContentPersonalizer

**Location**: `src/models/content_personalizer.py`

**Responsibilities**:
- Template selection based on effectiveness
- Bandit/A-B testing algorithms
- Content personalization with variables
- Template effectiveness tracking

**Key Methods**:

```python
def select_template(
    family_id: str,
    action_type: str,
    channel_code: str,
    urgency: str,
    language: str = 'en',
    action_context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Returns:
    {
        'template_id': uuid,
        'template_content': str,
        'personalized_content': str,
        'selection_strategy': str,
        'confidence': float
    }
    """

def _bandit_selection(
    templates: List[Dict],
    family_id: str,
    action_type: str,
    channel_code: str
) -> Dict[str, Any]:
    """
    Uses UCB, Thompson Sampling, or Epsilon-Greedy.
    Balances exploration vs exploitation.
    """
```

**Algorithms**:
- **UCB (Upper Confidence Bound)**: `score + exploration_bonus`
- **Thompson Sampling**: Beta distribution sampling
- **Epsilon-Greedy**: 10% random exploration, 90% best known

---

## 5. Channel Optimization

### 5.1 Channel Selection Process

1. **Get Available Channels**: Filter by consent/opt-out
2. **Apply Fallback Rules**:
   - No digital footprint → ASSISTED_VISIT
   - High vulnerability → ASSISTED_VISIT
   - Opted out of SMS → APP_PUSH
   - No app usage → SMS
3. **Calculate Channel Scores**:
   - Historical engagement rate (weight: 0.4)
   - Channel cost (weight: 0.2)
   - Urgency match (weight: 0.2)
   - Capability match (weight: 0.2)
4. **Select Best Channel**: Highest score

### 5.2 Channel Features

| Channel | Max Length | Rich Content | Tracking | Cost |
|---------|-----------|--------------|----------|------|
| SMS | 160 | No | Delivery | ₹0.10 |
| App Push | 200 | Yes | Open/Click | Free |
| Web Inbox | 1000 | Yes | Read/Click | Free |
| WhatsApp | 1000 | Yes | Delivery/Read | ₹0.15 |
| IVR | 120s | Audio | None | ₹2.00 |
| Assisted Visit | N/A | In-person | None | ₹50.00 |

### 5.3 Fallback Strategy

```
IF no digital footprint:
    → ASSISTED_VISIT
ELIF high vulnerability:
    → ASSISTED_VISIT
ELIF opted out SMS AND app available:
    → APP_PUSH
ELIF no app usage:
    → SMS
ELSE:
    → ML-based selection
```

---

## 6. Send Time Optimization

### 6.1 Time Windows

- **MORNING**: 9:00 - 12:00
- **AFTERNOON**: 12:00 - 17:00
- **EVENING**: 17:00 - 20:00
- **NIGHT**: 20:00 - 9:00 (restricted for SMS)

### 6.2 Time Restrictions

- No SMS after 8:00 PM
- No SMS before 8:00 AM
- Weekend/holiday SMS: configurable
- Urgent messages: can override restrictions

### 6.3 Learning Process

1. Track response rates by time window
2. Train LogisticRegression model
3. Predict probability for each time window
4. Select time with highest probability

---

## 7. Content Personalization

### 7.1 Template Selection

**Strategies**:
1. **BANDIT** (default): UCB/Thompson Sampling/Epsilon-Greedy
2. **AB_TEST**: Simple split (50/50)
3. **HEURISTIC**: Urgency-based selection

### 7.2 Template Variables

Common placeholders:
- `{family_name}` → Citizen
- `{scheme_name}` → Scheme name from context
- `{scheme_code}` → Scheme code
- `{deadline}` → Deadline date
- `{document_type}` → Document type
- `{upload_link}` → Upload URL
- `{consent_link}` → Consent URL
- `{portal_link}` → Portal URL
- `{action_description}` → Human-readable action

### 7.3 Template Effectiveness Tracking

Tracks:
- `response_rate` = responded / sent
- `completion_rate` = completed / responded
- `effectiveness_score` = (response_rate * 0.6) + (completion_rate * 0.4)

---

## 8. Fatigue Management

### 8.1 Frequency Limits

**Default Limits** (per family):
- Daily: 3 nudges
- Weekly: 10 nudges
- Monthly: 30 nudges

**Vulnerability Adjustments**:
- **HIGH**: 1/day, 3/week, 10/month
- **MEDIUM**: 2/day, 6/week, 20/month
- **LOW**: 3/day, 10/week, 30/month

### 8.2 Cooldown Periods

- After response: 7 days
- After opt-out request: 30 days
- After complaint: 14 days

### 8.3 Vulnerability Detection

Based on:
- Family income level
- Disability status
- Elderly members
- Remote geography
- Digital literacy indicators

---

## 9. API Design

### 9.1 REST Endpoints

#### POST /nudges/schedule

Schedule a new nudge.

**Request**:
```json
{
  "action_type": "renewal",
  "family_id": "FAM001",
  "urgency": "HIGH",
  "expiry_date": "2024-01-15T23:59:59Z",
  "action_context": {
    "scheme_name": "Old Age Pension",
    "scheme_code": "OAP001",
    "deadline": "2024-01-15"
  },
  "scheduled_by": "SYSTEM"
}
```

**Response**:
```json
{
  "success": true,
  "nudge_id": "uuid",
  "scheduled_channel": "SMS",
  "scheduled_time": "2024-01-10T09:00:00Z",
  "template_id": "uuid",
  "personalized_content": "Dear Citizen, your Old Age Pension renewal is due..."
}
```

#### GET /nudges/history?family_id=FAM001

Get nudge history for a family.

**Response**:
```json
{
  "success": true,
  "nudges": [
    {
      "nudge_id": "uuid",
      "action_type": "renewal",
      "channel": "SMS",
      "status": "DELIVERED",
      "scheduled_time": "2024-01-10T09:00:00Z",
      "sent_at": "2024-01-10T09:00:15Z",
      "delivered_at": "2024-01-10T09:00:30Z",
      "opened_at": null,
      "responded_at": null
    }
  ],
  "total": 10
}
```

#### POST /nudges/{nudge_id}/feedback

Record feedback event.

**Request**:
```json
{
  "event_type": "DELIVERED",
  "timestamp": "2024-01-10T09:00:30Z"
}
```

**Response**:
```json
{
  "success": true,
  "nudge_status": "DELIVERED",
  "updated_at": "2024-01-10T09:00:30Z"
}
```

### 9.2 Spring Boot Integration

**Controller**: `NudgeController`
- Handles HTTP requests
- Validates input
- Calls `NudgeService`

**Service**: `NudgeService`
- Business logic
- Calls Python backend via `PythonNudgeClient`

**Python Client**: `PythonNudgeClient`
- Executes Python orchestrator
- Returns results

---

## 10. Data Flow & Processing Pipeline

### 10.1 Nudge Scheduling Flow

```
1. Trigger Event (Application Created, Deadline Approaching, etc.)
   ↓
2. NudgeOrchestrator.schedule_nudge()
   ↓
3. FatigueModel.check_fatigue_limits()
   ├─→ If limit exceeded: Return error
   └─→ If allowed: Continue
   ↓
4. Get family preferences (consent, language)
   ↓
5. ChannelOptimizer.select_best_channel()
   ├─→ Load historical engagement
   ├─→ Apply fallback rules
   ├─→ Calculate scores
   └─→ Select best channel
   ↓
6. SendTimeOptimizer.select_best_time()
   ├─→ Predict time window probabilities
   ├─→ Apply time restrictions
   └─→ Select optimal time
   ↓
7. ContentPersonalizer.select_template()
   ├─→ Get available templates
   ├─→ Apply bandit algorithm
   ├─→ Personalize content
   └─→ Return template + content
   ↓
8. Create nudge record in database
   ↓
9. Log audit trail
   ↓
10. Return nudge details
```

### 10.2 Feedback Processing Flow

```
1. Channel sends feedback event (DELIVERED, OPENED, etc.)
   ↓
2. NudgeOrchestrator.record_feedback()
   ↓
3. Update nudge status in database
   ↓
4. Add to nudge_history table
   ↓
5. Update learning models:
   ├─→ ChannelPreferences (engagement_score, response_rate)
   ├─→ SendTimePreferences (response_probability)
   └─→ ContentEffectiveness (effectiveness_score)
   ↓
6. Update fatigue counter (if SENT)
   ↓
7. Return success
```

---

## 11. Integration Points

### 11.1 Input Sources

1. **AI-PLATFORM-02 (360° Profile)**
   - Family demographics
   - Vulnerability indicators
   - Device/app usage patterns
   - Connectivity patterns

2. **AI-PLATFORM-05 (Application Submission)**
   - Application events
   - Missing document triggers
   - Renewal reminders

3. **Golden Records**
   - Family ID mapping
   - Contact information
   - Language preferences

4. **Event Stream**
   - Consent given events
   - Deadline approaching events
   - Document uploaded events

### 11.2 Output Channels

1. **SMS Gateway** (DLT registered)
2. **App Push Service** (FCM/APNS)
3. **Web Portal** (Inbox API)
4. **WhatsApp Business API**
5. **IVR Service** (Voice call)
6. **Field Staff Scheduler** (Assisted visits)

---

## 12. Performance & Scalability

### 12.1 Performance Targets

- **Nudge Scheduling**: < 500ms per request
- **Feedback Processing**: < 200ms per event
- **History Retrieval**: < 300ms for 50 records

### 12.2 Scalability Considerations

- **Database Indexing**: On `family_id`, `nudge_id`, `scheduled_time`
- **Caching**: Template effectiveness scores, channel preferences
- **Batch Processing**: Feedback events (if high volume)
- **Async Processing**: Send actual messages (via queue)

---

## 13. Security & Governance

### 13.1 Consent Management

- All nudges require consent
- Opt-out preferences respected
- Consent logs maintained

### 13.2 Audit Trail

- All nudge actions logged
- Event data stored in JSONB
- Immutable logs (no updates/deletes)

### 13.3 Data Privacy

- Family data encrypted at rest
- PII masking in logs
- DPDP compliance

---

## 14. Compliance & Privacy

### 14.1 DPDP Compliance

- Explicit consent required
- Opt-out mechanism
- Data minimization (only necessary fields)

### 14.2 Ethical Nudging

- No manipulative content
- Transparent purpose
- Easy decline option
- Vulnerability-sensitive limits

### 14.3 Regulatory Requirements

- DLT registration for SMS
- WhatsApp template approval
- IVR consent recording

---

## 15. Deployment Architecture

### 15.1 Components

- **Python Services**: WSL2 Ubuntu 24.04, Python 3.12+
- **Spring Boot**: Java 17+, Maven
- **PostgreSQL**: Windows host, accessible from WSL
- **Web Viewer**: Flask, port 5001 (integrated with unified viewer)

### 15.2 Configuration

- Database connection: `config/db_config.yaml`
- Use case config: `config/use_case_config.yaml`

---

## 16. Monitoring & Observability

### 16.1 Metrics

- Total nudges scheduled
- Delivery rates by channel
- Response rates by channel/time
- Fatigue limit violations
- Consent opt-outs
- Error rates

### 16.2 Logging

- All nudge actions logged
- Error logging with stack traces
- Performance metrics

---

## 17. Success Metrics

### 17.1 Key Performance Indicators

1. **Response Rate Uplift**
   - Target: 20% increase vs baseline
   - Measure: responded / sent

2. **Completion Rate**
   - Target: 60% of responses complete action
   - Measure: completed / responded

3. **Missed Deadline Reduction**
   - Target: 30% reduction
   - Measure: deadlines missed vs total deadlines

4. **Opt-Out Rate**
   - Target: < 5%
   - Measure: opt-outs / total nudges

5. **Vulnerability Coverage**
   - Target: 100% of high-vulnerability families reached
   - Measure: nudges sent / eligible families

---

## 18. Implementation Status

### 18.1 Completed ✅

- ✅ Database schema (10 tables)
- ✅ Core Python services (FatigueModel, ChannelOptimizer, SendTimeOptimizer, ContentPersonalizer)
- ✅ NudgeOrchestrator (end-to-end workflow)
- ✅ Database setup and initialization scripts
- ✅ Channel and template initialization
- ✅ Template matching with fallback logic
- ✅ Spring Boot REST APIs (DTOs, Controller, Service)
- ✅ Test scripts (end-to-end workflow testing)
- ✅ Web viewer (dashboard at `/ai11`)
- ✅ UUID handling fixes
- ✅ Content personalization enhancements

### 18.2 Pending 📋

- ⏳ Portal/app integration (React components)
- ⏳ Real channel integration (SMS gateway, WhatsApp API, etc.)
- ⏳ Model training with real historical data
- ⏳ Performance optimization and caching
- ⏳ Advanced analytics dashboard

---

## 19. Web Interface

### 19.1 Web Viewer

**URL**: http://localhost:5001/ai11

**Features**:
- **Statistics Dashboard**:
  - Total nudges
  - Scheduled count
  - Delivered count
  - Responded count
  - Channels used

- **Tabbed Interface**:
  - All Nudges
  - Scheduled
  - Active (SENT, DELIVERED, OPENED, CLICKED)
  - Completed (RESPONDED, COMPLETED)

- **Nudge Cards**:
  - Action type and urgency badges
  - Channel and status badges
  - Nudge details (ID, family, scheduled time)
  - Timeline (sent, delivered, opened, responded)
  - Personalized content preview
  - Template name

- **Auto-refresh**: Every 30 seconds

**Integration**: Integrated into unified viewer at `ai-ml/use-cases/03_identification_beneficiary/scripts/view_rules_web.py`

---

## 20. Future Enhancements

### 20.1 Advanced ML Features

- Deep learning for channel selection
- Reinforcement learning for template selection
- Multi-armed bandit with context (contextual bandits)

### 20.2 Enhanced Personalization

- A/B testing framework
- Dynamic template generation (NLG)
- Multi-language support expansion

### 20.3 Analytics & Insights

- Channel effectiveness dashboards
- Time optimization insights
- Fatigue analysis reports
- ROI calculation (cost vs response)

### 20.4 Integration Enhancements

- Real-time WebSocket updates
- Event stream integration (Kafka/RabbitMQ)
- Multi-tenant support

---

**Last Updated**: 2024-12-30  
**Version**: 1.0  
**Status**: ✅ Complete - Core Implementation

