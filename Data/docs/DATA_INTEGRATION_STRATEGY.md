# Data Integration Strategy: smart_warehouse ↔ smart_citizen

**Document Version**: 1.0  
**Created**: 2024-12-30  
**Purpose**: Comprehensive data integration strategy between AI/ML warehouse and Citizen Portal databases  
**Status**: Planning Phase

---

## Executive Summary

This document defines the data integration strategy between:
- **smart_warehouse**: AI/ML use cases database (source of truth for ML models, predictions, golden records)
- **smart_citizen**: Citizen Portal database (operational database for citizen-facing features)

### Key Principles

1. **Data Ownership**: smart_warehouse is source of truth for ML-generated data; smart_citizen is source for citizen-submitted data
2. **Bidirectional Sync**: Data flows in both directions with different frequencies and triggers
3. **Privacy & Security**: Sensitive data must be masked during sync (per CDC_DATA_MASKING_STRATEGY.md)
4. **Performance**: Optimize sync frequency to balance real-time needs vs. system load
5. **Consistency**: Ensure data consistency between systems while maintaining autonomy

---

## Database Overview

### smart_warehouse Database

**Purpose**: AI/ML use cases, model training, predictions, golden records

**Key Schemas:**
- `public` (or `smart_warehouse`): Golden Records, 360° Profiles, relationships
- `eligibility`: Scheme master, eligibility rules, snapshots, candidate lists
- `decision`: Application decisions, approvals, risk scores
- `forecast`: Benefit forecasts, predictions
- `intimation`: Consent records, intimation campaigns
- `detection`: Beneficiary detection cases

**Key Tables:**
- `golden_records` - Master citizen identities
- `profile_360` - 360° profiles with ML features
- `eligibility.eligibility_snapshots` - Eligibility evaluations
- `eligibility.scheme_master` - Scheme definitions
- `decision.applications` - Application decisions
- `forecast.benefit_forecasts` - Benefit predictions

### smart_citizen Database

**Purpose**: Citizen Portal operational data

**Key Schemas:**
- `public`: Core citizen portal tables

**Key Tables:**
- `citizens` - Citizen accounts and profiles
- `schemes` - Scheme catalog (read-only copy)
- `service_applications` - Applications submitted via portal
- `documents` - Documents uploaded by citizens
- `notifications` - Portal notifications
- `payments` - Payment transactions
- `feedback` - Feedback and complaints
- `consents` - Citizen consent records
- `profile_summary` - Denormalized profile data for performance

---

## Data Flow Directions

### Direction 1: smart_warehouse → smart_citizen

**Purpose**: Sync ML-generated data, predictions, and master data to Citizen Portal

**Data Categories:**
1. **Master Data** (Batch) - Scheme catalog, reference data
2. **Profile Data** (Event + Batch) - Golden records, 360° profiles
3. **Eligibility Data** (Event) - Eligibility snapshots, hints
4. **Forecast Data** (Event) - Benefit forecasts
5. **Decision Data** (Event) - Application decisions, approvals
6. **Alerts/Notifications** (Event) - ML-driven alerts

### Direction 2: smart_citizen → smart_warehouse

**Purpose**: Sync citizen-submitted data back to warehouse for ML training and analysis

**Data Categories:**
1. **Profile Updates** (Event) - Citizen profile changes
2. **Application Submissions** (Event) - New applications
3. **Document Metadata** (Event) - Document uploads
4. **User Behavior** (Batch) - Analytics, clicks, interactions
5. **Feedback** (Batch) - Feedback and complaints

---

## Sync Patterns

### Pattern 1: Real-Time Event-Driven (CDC)

**When to Use:**
- Data that needs to be available immediately in portal
- Critical updates (application status, eligibility changes)
- User-facing data changes

**Technology**: Change Data Capture (CDC) via Debezium + Kafka

**Examples:**
- Eligibility score changes
- Application decision updates
- Profile confidence changes
- Benefit forecast updates

### Pattern 2: Near-Real-Time (Event-Driven API)

**When to Use:**
- Data that needs quick sync but not instant
- Updates triggered by user actions
- ML model predictions that need propagation

**Technology**: Event-driven APIs, message queues (RabbitMQ/Kafka)

**Examples:**
- Profile updates from warehouse
- New eligibility hints
- Forecast updates

### Pattern 3: Batch Synchronization

**When to Use:**
- Master data (scheme catalog, reference data)
- Large data sets (historical data)
- Non-critical updates
- Analytics data

**Technology**: ETL jobs (Apache Airflow, scheduled jobs)

**Examples:**
- Scheme catalog sync (daily)
- Historical eligibility data (weekly)
- User behavior analytics (daily)

### Pattern 4: On-Demand API Calls

**When to Use:**
- Data that's too large to sync
- Real-time queries needed
- Complex aggregations

**Technology**: REST APIs, GraphQL

**Examples:**
- Real-time eligibility checking
- Dynamic forecast generation
- On-demand profile queries

---

## Data Masking Requirements

Per **CDC_DATA_MASKING_STRATEGY.md**, sensitive data must be masked during sync:

**Full Masking:**
- Income bands → "CONFIDENTIAL"
- Full Aadhaar (if required) → "***MASKED***"

**Partial Masking:**
- Jan Aadhaar → "****-****-1234" (last 4 digits)
- Mobile → "******5678" (last 4 digits)
- Email → "u***@example.com" (first char + domain)

**No Masking:**
- Eligibility scores
- Scheme codes
- District IDs
- Aggregated vulnerability levels

---

## Data Volume Estimates

### smart_warehouse → smart_citizen

| Data Type | Volume | Frequency | Sync Pattern |
|-----------|--------|-----------|--------------|
| Scheme Master | ~200 records | Daily (batch) | Batch |
| Eligibility Hints | ~50K records/day | Real-time (event) | CDC |
| Profile Summary | ~100K records | Hourly (batch) + Event | Hybrid |
| Forecast Data | ~50K records/day | Event-driven | Event |
| Decision Updates | ~10K records/day | Real-time (event) | CDC |

### smart_citizen → smart_warehouse

| Data Type | Volume | Frequency | Sync Pattern |
|-----------|--------|-----------|--------------|
| Profile Updates | ~20K updates/day | Real-time (event) | CDC |
| Application Submissions | ~5K/day | Real-time (event) | CDC |
| Document Metadata | ~15K/day | Real-time (event) | CDC |
| User Behavior | ~500K events/day | Daily (batch) | Batch |
| Feedback | ~1K/day | Daily (batch) | Batch |

---

## Success Criteria

1. **Latency**: Event-driven syncs < 5 seconds
2. **Data Consistency**: 99.9% sync success rate
3. **Performance**: No impact on portal performance (<100ms overhead)
4. **Reliability**: Zero data loss
5. **Security**: All sensitive data properly masked

---

## Risk Mitigation

1. **Data Loss**: Implement idempotent syncs with deduplication
2. **Performance Impact**: Use async processing, batching where possible
3. **Data Conflicts**: Define conflict resolution strategies (timestamp-based, source priority)
4. **Network Failures**: Implement retry logic, dead letter queues
5. **Schema Changes**: Version schemas, backward compatibility checks

---

**Next Steps**: See detailed documents:
- `DATA_FLOW_SPECIFICATION.md` - Detailed data flow specifications
- `BATCH_VS_EVENT_SYNC_PLAN.md` - Batch vs event-based sync plan
- `DATA_FREQUENCY_SCHEDULE.md` - Sync frequency and schedule details
- `DATA_MAPPING_REFERENCE.md` - Field-level mappings (already exists)

