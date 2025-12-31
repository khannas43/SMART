# AI-PLATFORM-11: Personalized Communication & Nudging

**Use Case ID:** AI-PLATFORM-11  
**Version:** 1.0  
**Status:** 🚧 In Development

---

## Overview

The Personalized Communication & Nudging system optimizes reminders and informational messages for renewals, missing documents, pending consents/applications, and important deadlines by learning from citizen behavior and outcomes.

### Key Capabilities

1. **Channel and Send Time Optimization**
   - ML-based channel selection (SMS, App Push, Web Inbox, WhatsApp, IVR, Assisted Visit)
   - Time window optimization (morning/afternoon/evening, weekday/weekend)

2. **Content and Frequency Personalization**
   - Template selection based on past effectiveness
   - Bandit/A-B testing for continuous learning
   - Fatigue management with vulnerability adjustments

3. **Multi-Channel Support**
   - SMS (with DLT compliance)
   - App Push Notifications
   - Web Inbox Messages
   - WhatsApp Business API
   - IVR (Interactive Voice Response)
   - Assisted Field Visits

4. **Governance and Ethics**
   - Consent management
   - Opt-out respect
   - Frequency limits
   - Vulnerability-sensitive messaging

---

## Project Structure

```
11_personalized_communication_nudging/
├── config/
│   ├── db_config.yaml
│   └── use_case_config.yaml
├── src/
│   ├── services/
│   │   ├── nudge_orchestrator.py
│   │   └── feedback_processor.py
│   ├── models/
│   │   ├── channel_optimizer.py
│   │   ├── send_time_optimizer.py
│   │   ├── content_personalizer.py
│   │   └── fatigue_model.py
│   └── optimizers/
│       └── bandit_optimizer.py
├── spring_boot/
│   ├── controller/
│   ├── service/
│   └── dto/
├── scripts/
│   ├── setup_database.py
│   ├── initialize_templates.py
│   ├── test_nudge_workflow.py
│   └── view_nudges_web.py
├── docs/
│   └── TECHNICAL_DESIGN.md
└── README.md
```

---

## Database Schema

The system uses the `nudging` schema in PostgreSQL with the following tables:

- `nudges` - Main nudge records
- `nudge_channels` - Available communication channels
- `nudge_templates` - Message templates by action type
- `nudge_history` - Historical nudge sends and responses
- `fatigue_tracking` - Family-level fatigue counters
- `channel_preferences` - Learned channel preferences per family
- `content_effectiveness` - Template effectiveness metrics
- `nudge_audit_logs` - Audit trail for compliance

---

## Quick Start

### 1. Database Setup

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/11_personalized_communication_nudging
python scripts/setup_database.py
```

### 2. Initialize Templates

```bash
python scripts/initialize_templates.py
```

### 3. Test Nudge Workflow

```bash
python scripts/test_nudge_workflow.py
```

### 4. Start Web Viewer

```bash
python scripts/view_nudges_web.py
```

Access at: http://localhost:5001/ai11

---

## API Endpoints

### Schedule a Nudge

```bash
POST /nudges/schedule
{
  "action_type": "renewal",
  "family_id": "FAM001",
  "urgency": "HIGH",
  "expiry_date": "2024-01-15"
}
```

### Get Nudge History

```bash
GET /nudges/history?family_id=FAM001
```

---

## Configuration

Edit `config/use_case_config.yaml` to customize:
- Channel capabilities and costs
- Time restrictions
- Fatigue limits
- Vulnerability adjustments
- Learning parameters

---

## Documentation

- [Technical Design Document](docs/TECHNICAL_DESIGN.md)
- [API Documentation](docs/API_DOCUMENTATION.md)

---

## Status

🚧 **In Development** - Initial setup complete, core services in progress

---

**Last Updated:** 2024-12-30

