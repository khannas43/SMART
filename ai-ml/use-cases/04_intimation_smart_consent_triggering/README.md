# Auto Intimation & Smart Consent Triggering

**Use Case ID:** AI-PLATFORM-04  
**Tier:** Tier 1 (Foundational)  
**Status:** Development  
**MLflow Experiment:** `smart/intimation_consent/*`

## Overview

Automatically notify citizens/families about eligible welfare schemes using pre-computed eligibility signals from Auto Identification of Beneficiaries (AI-PLATFORM-03), and obtain explicit, auditable consent for enrolment or data use through personalized multi-channel notifications.

### Key Capabilities

1. **Auto Intimation Engine**: Automatically notify citizens about eligible schemes through SMS, mobile app, web, IVR, WhatsApp, and email
2. **Smart Consent Management**: Collect explicit, auditable consent with soft consent (low-risk) and strong consent (OTP/e-sign for high-risk schemes)
3. **Personalized Messaging**: Multi-language, context-aware messages with clear benefit summaries and simple action choices
4. **Multi-Channel Orchestration**: Intelligent scheduling, retry logic, fatigue management, and escalation
5. **Compliance & Governance**: DPDP-aligned consent practices, fairness monitoring, and comprehensive audit trails

## Key Technologies

- **PostgreSQL**: Campaigns, consent records, message logs, preferences (in `smart_warehouse` database, `intimation` schema)
- **Python**: Message personalization, campaign management, consent orchestration
- **Spring Boot**: REST APIs for intimation scheduling, consent capture, and status queries
- **Integration**: 
  - AI-PLATFORM-01 (Golden Records) - Contact information
  - AI-PLATFORM-02 (360° Profiles) - Vulnerability indicators, preferences
  - AI-PLATFORM-03 (Auto Identification) - Eligibility signals

## Architecture

```
Auto Identification (AI-PLATFORM-03)
         ↓
Eligibility Signals (POTENTIALLY_ELIGIBLE_IDENTIFIED)
         ↓
Auto Intimation Engine (AI-PLATFORM-04)
    ├── Campaign Manager (Intake, Scheduling, Batching)
    ├── Message Personalizer (Template Generation, Multi-Channel)
    ├── Consent Manager (Soft/Strong Consent, Audit Trails)
    └── Smart Orchestrator (Retries, Escalation, Fatigue)
         ↓
Multi-Channel Notifications
    ├── SMS (Short code responses, deep links)
    ├── Mobile App (Push notifications, in-app cards)
    ├── Web Portal (Inbox, consent widgets)
    ├── WhatsApp (Rich messages)
    ├── Email (Detailed information)
    └── IVR (Low-literacy users)
         ↓
Consent Records & Audit Trails
    ├── Soft Consent (Single click/tap)
    ├── Strong Consent (OTP/e-sign)
    └── Event Stream (INTIMATION_SENT, CONSENT_GIVEN, etc.)
         ↓
Auto Application (AI-PLATFORM-05)
```

## Components

### 1. Campaign Manager
- **Intake**: Pull eligibility signals from AI-PLATFORM-03
- **Policy Application**: Eligibility thresholds, segment targeting, fatigue limits
- **Batching**: Group candidates by scheme and geography
- **Scheduling**: Load management, time-of-day preferences

### 2. Message Personalizer
- **Language Selection**: Based on Jan Aadhaar profile and portal settings
- **Template Generation**: Scheme description, benefits, eligibility reasons
- **Multi-Channel Variants**: SMS (concise), App/Web (rich cards), IVR (voice-friendly)

### 3. Consent Manager
- **Soft Consent**: Single click/tap for low-risk schemes
- **Strong Consent**: OTP/e-sign for financial/high-risk schemes
- **Audit Trails**: Immutable logs with LOA (Level of Assurance), channel, device, timestamp
- **Consent Storage**: Scheme ID, GR/Jan Aadhaar ID, terms version, status

### 4. Smart Orchestrator
- **Retry Logic**: Configurable retry schedules (e.g., 3 attempts over 30 days)
- **Escalation**: Targeted reminders for incomplete flows
- **Fatigue Management**: Max messages per family per month
- **Personalization Rules**: Prioritize vulnerable/underserved families
- **Feedback Loop**: Response rate tracking, A/B testing

## Evaluation Modes

1. **Periodic Intake** (Daily, configurable)
   - Pull newly eligible candidates from AI-PLATFORM-03
   - Apply campaign policies and thresholds
   - Schedule batch sends

2. **Event-Driven** (Real-time)
   - Trigger on eligibility status changes
   - Immediate notification for high-priority cases
   - Respect fatigue limits

3. **On-Demand** (API calls)
   - Manual campaign triggers
   - Re-targeting requests
   - Consent status queries

## APIs

### Intimation APIs
- `POST /intimation/schedule` - Register eligible candidates for auto intimation
- `GET /intimation/status?family_id` - Get pending/completed intimations
- `POST /intimation/retry?campaign_id` - Trigger retry for pending intimations
- `GET /intimation/campaigns` - List active campaigns with metrics

### Consent APIs
- `POST /consent/capture` - Record citizen response (Yes/No/More info)
- `GET /consent/status?family_id&scheme_id` - Get consent status
- `POST /consent/revoke` - Revoke existing consent
- `GET /consent/history?family_id` - Get consent history

### Campaign Management APIs
- `POST /campaigns/create` - Create new campaign
- `GET /campaigns/{campaign_id}/metrics` - Get campaign performance metrics
- `PUT /campaigns/{campaign_id}/pause` - Pause campaign
- `PUT /campaigns/{campaign_id}/resume` - Resume campaign

## Data Sources

- **AI-PLATFORM-03 Output**: Eligibility status, score, reason codes, priority, timestamp
- **Golden Records**: Jan Aadhaar registered mobile, email, preferred language
- **360° Profiles**: Vulnerability indicators, under-coverage status, preferences
- **Consent Records**: Existing consents for analytics, communication, enrollment
- **Scheme Metadata**: Human-readable descriptions, benefit amounts, conditions, documents

## Events & Integrations

### Input Events
- `POTENTIALLY_ELIGIBLE_IDENTIFIED` - From AI-PLATFORM-03

### Output Events
- `INTIMATION_SENT` - Notification delivered to citizen
- `CONSENT_GIVEN` - Citizen provided consent
- `CONSENT_REJECTED` - Citizen declined
- `CONSENT_REVOKED` - Citizen revoked existing consent
- `CONSENT_EXPIRED` - Consent validity period ended

### Downstream Integrations
- **Auto Application (AI-PLATFORM-05)**: Triggered on `CONSENT_GIVEN`
- **Analytics Dashboards**: Feed consent rates, engagement metrics
- **Departmental Worklists**: Show pending consents for follow-up

## Governance & Compliance

### Legal Basis
- Jan Aadhaar and Aadhaar guidance on authentication and notification
- DPDP-aligned consent practices
- Scheme-specific legal constraints

### Informed Consent & Transparency
- Plain language explanations of why contacted
- Clear data usage disclosure
- Explicit acknowledgment that consent ≠ approval

### Fairness & Non-Discrimination
- Monitor outreach distribution vs target populations
- Ensure marginalized groups not under-reached
- Provide offline/assisted consent options via e-Mitra or field workers

### Auditability
- Immutable logs of all messages sent
- Complete consent lifecycle tracking
- Linkage to eligibility decisions and applications

## Success Metrics

### Reach & Engagement
- Delivery rate by channel
- Unique households reached
- Response rates (consent given vs ignored/declined) per scheme and segment

### Impact
- Increase in enrolment rate for auto-identified underserved households
- Reduction in time from eligibility identification to consent capture

### Quality & Trust
- Complaints or opt-out rates
- Audit results showing correct consent records
- Perceived spam/irrelevance metrics

## Quick Start

### Prerequisites
- Python 3.12+ (WSL venv at `/mnt/c/Projects/SMART/ai-ml/.venv`)
- PostgreSQL 14+ (smart_warehouse database)
- MLflow server running at `http://127.0.0.1:5000`

### Setup
```bash
# Activate venv
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate

# Install dependencies
cd /mnt/c/Projects/SMART/ai-ml/use-cases/04_intimation_smart_consent_triggering
pip install -r requirements.txt

# Setup database schema
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f database/intimation_schema.sql

# Validate configuration
python scripts/check_config.py
```

### Run Intake Process
```bash
# Pull eligibility signals and create campaigns
python scripts/run_intake.py --scheme-code CHIRANJEEVI --dry-run

# Schedule and send notifications
python scripts/run_campaign.py --campaign-id <campaign_id>
```

### Test Consent Flow
```bash
# Simulate consent capture
python scripts/test_consent_flow.py --family-id <family_id> --scheme-code CHIRANJEEVI
```

## Documentation

- [Technical Design Document](docs/TECHNICAL_DESIGN.md) - Comprehensive architecture and design
- [API Documentation](docs/API_DOCUMENTATION.md) - REST API specifications
- [Consent Management Guide](docs/CONSENT_MANAGEMENT.md) - Consent flows and governance
- [Campaign Configuration](docs/CAMPAIGN_CONFIGURATION.md) - Campaign setup and policies
- [Multi-Channel Integration](docs/CHANNEL_INTEGRATION.md) - SMS, WhatsApp, IVR setup

## Related Use Cases

- **AI-PLATFORM-01**: Golden Record extraction (contact information source)
- **AI-PLATFORM-02**: Eligibility Scoring & 360° Profiles (vulnerability indicators)
- **AI-PLATFORM-03**: Auto Identification of Beneficiaries (eligibility signals)
- **AI-PLATFORM-05**: Auto Application (triggered by consent)

---

**Last Updated**: 2024-12-29  
**Maintainer**: SMART Platform AI/ML Team

