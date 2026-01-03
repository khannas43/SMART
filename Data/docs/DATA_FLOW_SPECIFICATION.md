# Data Flow Specification: smart_warehouse ↔ smart_citizen

**Document Version**: 1.0  
**Created**: 2024-12-30  
**Purpose**: Detailed specification of data flows between warehouse and citizen portal  
**Status**: Planning Phase

---

## Direction 1: smart_warehouse → smart_citizen

### 1.1 Master Data Sync (Batch)

#### Scheme Master Data

**Source Table**: `eligibility.scheme_master`  
**Target Table**: `schemes`  
**Frequency**: Daily (Batch)  
**Sync Pattern**: Full refresh (replace all)  
**Trigger**: Scheduled job (00:00 UTC daily)

**Mapping**:
```sql
-- Source: eligibility.scheme_master
-- Target: schemes
INSERT INTO schemes (id, code, name, description, category, department, 
                     eligibility_criteria, benefits, documents_required, 
                     status, last_updated)
SELECT 
    scheme_id,
    scheme_code,
    scheme_name,
    description,
    category,
    department_name,
    eligibility_criteria_json,
    benefits_json,
    documents_required_json,
    status,
    updated_at
FROM eligibility.scheme_master
WHERE status = 'ACTIVE'
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    category = EXCLUDED.category,
    department = EXCLUDED.department,
    eligibility_criteria = EXCLUDED.eligibility_criteria,
    benefits = EXCLUDED.benefits,
    documents_required = EXCLUDED.documents_required,
    status = EXCLUDED.status,
    last_updated = EXCLUDED.last_updated;
```

**Fields**:
- All fields directly mapped (no masking required for master data)
- Filter: Only `status = 'ACTIVE'` schemes
- Conflict Resolution: Update on conflict (scheme code as key)

**Volume**: ~200 records per sync

---

### 1.2 Profile Data Sync (Event + Batch)

#### Golden Records → Profile Data

**Source Table**: `public.golden_records`  
**Target Table**: `profile_data` (denormalized for performance)  
**Frequency**: 
- Event-driven: Real-time via CDC (on UPDATE)
- Batch: Full sync daily (00:30 UTC)

**Sync Pattern**: Hybrid (CDC for updates + daily full sync for consistency)

**Mapping** (see DATA_MAPPING_REFERENCE.md for details):
- `gr_id` → `record_id`
- `family_id` → `family_id`
- `jan_aadhaar` → `jan_aadhaar` (PARTIAL MASK: last 4 digits only)
- `full_name` → `full_name` (direct)
- `date_of_birth` → `date_of_birth` (direct)
- `gender` → `gender` (direct)
- `district_id` → `district_id` (direct)
- `city_village` → `city` (direct)

**Masking Rules**:
- Jan Aadhaar: Partial mask (show last 4: `****-****-1234`)
- Mobile: Partial mask if included (show last 4: `******5678`)
- Email: Partial mask if included (show first char + domain: `u***@example.com`)

**CDC Event Filter**: Only sync if `updated_at` changed in last 30 days

**Volume**: 
- Event: ~100 updates/hour
- Batch: ~100K records daily

---

#### 360° Profile Summary

**Source Table**: `public.profile_360`  
**Target Table**: `profile_summary`  
**Frequency**: 
- Event-driven: Real-time via CDC (on UPDATE)
- Batch: Hourly full sync

**Mapping**:
- `gr_id` → `family_id`
- `vulnerability_level` → `vulnerability` (direct)
- `under_coverage_indicator` → `under_coverage` (direct)
- `inferred_income_band` → `income_category` (FULL MASK: "CONFIDENTIAL")
- `cluster_id` → `region` (direct)

**Exclusions**:
- All ML features (age_encoded, gender_encoded, etc.)
- Detailed `profile_data` JSON
- Model metadata

**Masking Rules**:
- Income band: FULL MASK → "CONFIDENTIAL"

**Volume**: 
- Event: ~500 updates/hour
- Batch: ~100K records hourly

---

### 1.3 Eligibility Data Sync (Event-Driven)

#### Eligibility Snapshots → Eligibility Hints

**Source Table**: `eligibility.eligibility_snapshots`  
**Target Table**: `eligibility_hints`  
**Frequency**: Real-time (CDC event-driven)  
**Sync Pattern**: Event-driven (only new/changed evaluations)

**Mapping**:
- `family_id` → `family_id` (direct)
- `scheme_code` → `scheme_code` (direct)
- `evaluation_status` → `eligibility_status` (direct)
- `eligibility_score` → `eligibility_score` (round to 2 decimals)
- `confidence_score` → `confidence` (round to 2 decimals)
- `explanation` → `explanation` (truncate to 500 chars)
- `evaluation_timestamp` → `updated_at` (direct)

**Filtering Rules**:
- Only sync if `evaluation_status` IN ('RULE_ELIGIBLE', 'POSSIBLE_ELIGIBLE')
- Only sync top 5 schemes per family (by `eligibility_score DESC`)
- Only sync records with `evaluation_timestamp` >= LAST_30_DAYS

**CDC Event Filter**: Only INSERT/UPDATE events

**Conflict Resolution**: 
- ON CONFLICT (`family_id`, `scheme_code`) DO UPDATE
- Only update if source `evaluation_timestamp` > target `updated_at`

**Volume**: ~50K records/day (after filtering)

---

### 1.4 Forecast Data Sync (Event-Driven)

**Source Table**: `forecast.benefit_forecasts`  
**Target Table**: `benefit_forecasts`  
**Frequency**: Real-time (Event-driven via API)  
**Sync Pattern**: Event-driven (when forecast is generated/updated)

**Mapping**:
- `forecast_id` → `forecast_id` (direct)
- `family_id` → `family_id` (direct)
- `horizon_months` → `horizon_months` (direct)
- `total_annual_value` → `total_annual_value` (direct)
- `scheme_count` → `scheme_count` (direct)
- `projections` → `projections` (JSON, direct)
- `generated_at` → `generated_at` (direct)

**Trigger**: 
- When new forecast generated via API
- When forecast updated (recomputed)

**API Integration**: Callback from forecast service → Citizen Portal API

**Volume**: ~50K forecasts/day

---

### 1.5 Decision Data Sync (Event-Driven)

**Source Table**: `decision.applications`  
**Target Table**: `application_decisions` (join with service_applications)  
**Frequency**: Real-time (CDC event-driven)  
**Sync Pattern**: Event-driven (on decision status change)

**Mapping**:
- `application_id` → `application_id` (match with service_applications.id)
- `decision` → `decision_status` (direct: AUTO_APPROVED, ROUTE_TO_OFFICER, etc.)
- `risk_score` → `risk_score` (direct)
- `confidence` → `confidence` (direct)
- `decision_timestamp` → `decision_date` (direct)
- `reasons` → `decision_reasons` (JSON array)

**Trigger**: On INSERT/UPDATE of decision status

**Volume**: ~10K decisions/day

---

### 1.6 Alert/Notification Data Sync (Event-Driven)

**Source**: Multiple AI/ML use cases (AI-PLATFORM-07, AI-PLATFORM-09, AI-PLATFORM-14)  
**Target Table**: `ml_alerts`  
**Frequency**: Real-time (Event-driven)  
**Sync Pattern**: Event-driven (when alerts generated)

**Examples**:
- Beneficiary detection alerts (AI-PLATFORM-07)
- Proactive inclusion alerts (AI-PLATFORM-09)
- Predictive alerts (AI-PLATFORM-14)

**Mapping**: Generic alert structure
- `alert_id` → `alert_id`
- `family_id` → `citizen_id` (map via family)
- `alert_type` → `alert_type`
- `severity` → `severity`
- `message` → `message`
- `action_url` → `action_url`
- `created_at` → `created_at`

**Volume**: ~20K alerts/day

---

## Direction 2: smart_citizen → smart_warehouse

### 2.1 Profile Updates (Event-Driven)

**Source Table**: `citizens`  
**Target Table**: `public.golden_records`  
**Frequency**: Real-time (CDC event-driven)  
**Sync Pattern**: Event-driven (on citizen profile UPDATE)

**Mapping** (see DATA_MAPPING_REFERENCE.md):
- `aadhaar_number` → `jan_aadhaar` (match key)
- `full_name` → `full_name` (direct)
- `date_of_birth` → `date_of_birth` (direct)
- `gender` → `gender` (direct)
- `mobile_number` → `mobile_number` (new field, if exists)
- `email` → `email` (new field, if exists)
- `city` → `city_village` (direct)
- `district` → `district_id` (map district name to ID)
- `pincode` → `pincode` (direct)
- `updated_at` → `updated_at` (direct)

**Matching Logic**:
- Match by `jan_aadhaar` = `aadhaar_number`
- If no match, create new record (flag for review)
- Only sync if `verification_status` = 'verified'

**Conflict Resolution**: 
- Timestamp-based: Latest wins
- Set `updated_by` = 'citizen_portal'

**Volume**: ~20K updates/day

---

### 2.2 Application Submissions (Event-Driven)

**Source Table**: `service_applications`  
**Target Table**: `decision.application_events`  
**Frequency**: Real-time (CDC event-driven)  
**Sync Pattern**: Event-driven (on application INSERT/UPDATE)

**Mapping**:
- `id` → `application_id` (direct)
- `citizen_id` → `citizen_id` (map via aadhaar to warehouse citizen_id)
- `scheme_id` → `scheme_code` (map scheme UUID to code)
- `status` → `event_type` (transform: 'submitted' → 'APPLICATION_SUBMITTED', etc.)
- `submitted_at` → `event_timestamp` (direct)
- `approved_at` → `approval_timestamp` (conditional, if approved)

**Event Type Mapping**:
- 'submitted' → 'APPLICATION_SUBMITTED'
- 'approved' → 'APPLICATION_APPROVED'
- 'rejected' → 'APPLICATION_REJECTED'
- 'withdrawn' → 'APPLICATION_WITHDRAWN'

**Trigger**: On INSERT/UPDATE of application status

**Volume**: ~5K applications/day

---

### 2.3 Document Metadata (Event-Driven)

**Source Table**: `documents`  
**Target Table**: `document_metadata` (warehouse schema TBD)  
**Frequency**: Real-time (CDC event-driven)  
**Sync Pattern**: Event-driven (on document INSERT)

**Mapping**:
- `id` → `document_id` (direct)
- `citizen_id` → `citizen_id` (map via aadhaar)
- `document_type` → `document_type` (direct)
- `file_name` → `file_name` (direct)
- `file_size` → `file_size` (direct)
- `uploaded_at` → `uploaded_at` (direct)
- `verification_status` → `verification_status` (direct)

**Note**: Only sync metadata, NOT file content (files stay in citizen portal storage)

**Volume**: ~15K documents/day

---

### 2.4 User Behavior Analytics (Batch)

**Source Tables**: Multiple (application views, scheme clicks, eligibility checks, etc.)  
**Target Table**: `analytics.user_behavior` (warehouse schema TBD)  
**Frequency**: Daily (Batch)  
**Sync Pattern**: Batch (aggregate and sync)

**Data Collected**:
- Page views
- Scheme clicks
- Eligibility check events
- Application starts/completions
- Document uploads
- Search queries

**Aggregation**: 
- Group by: citizen_id, event_type, date
- Aggregate: counts, durations, timestamps

**Volume**: ~500K events/day (aggregated to ~50K records/day)

---

### 2.5 Feedback Data (Batch)

**Source Table**: `feedback`  
**Target Table**: `feedback_analytics` (warehouse schema TBD)  
**Frequency**: Daily (Batch)  
**Sync Pattern**: Batch (full sync of new feedback)

**Mapping**:
- `id` → `feedback_id` (direct)
- `citizen_id` → `citizen_id` (map via aadhaar)
- `feedback_type` → `feedback_type` (direct)
- `rating` → `rating` (direct)
- `comment` → `comment` (direct, for sentiment analysis)
- `created_at` → `created_at` (direct)
- `scheme_id` → `scheme_code` (map if applicable)

**Purpose**: Sentiment analysis, feedback categorization, ML training

**Volume**: ~1K feedback/day

---

## Data Quality Rules

### Completeness
- Source data must have required fields (non-null constraints)
- Missing required fields → Skip sync, log error

### Accuracy
- Data type validation (date formats, UUIDs, etc.)
- Range validation (scores 0-1, dates valid, etc.)
- Enum validation (status values, types, etc.)

### Consistency
- Foreign key validation (citizen_id exists, scheme_code valid)
- Referential integrity checks
- Timestamp consistency (updated_at >= created_at)

### Timeliness
- Event-driven syncs: Process within 5 seconds
- Batch syncs: Complete within SLA window
- Stale data detection (if last_updated > threshold, flag for review)

---

## Error Handling

### Retry Strategy
- **Transient Errors**: Exponential backoff (1s, 2s, 4s, 8s, max 5 retries)
- **Permanent Errors**: Dead Letter Queue (DLQ) for manual review
- **Timeout Errors**: Retry with increased timeout

### Dead Letter Queue (DLQ)
- Store failed sync records
- Include error message, stack trace, source data
- Manual review and reprocessing

### Monitoring & Alerts
- Sync failure rate > 1% → Alert
- Sync latency > 10 seconds → Alert
- DLQ size > 1000 records → Alert
- Data volume drop > 50% → Alert

---

**Next Steps**: See:
- `BATCH_VS_EVENT_SYNC_PLAN.md` - Detailed sync patterns
- `DATA_FREQUENCY_SCHEDULE.md` - Schedule and timing details

