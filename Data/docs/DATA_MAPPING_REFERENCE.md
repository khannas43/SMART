# Data Mapping Reference

**Document Version**: 1.0  
**Last Updated**: 2024-12-29

This document provides detailed table-to-table and field-level mapping references for CDC synchronization.

## Direction 1: Warehouse → Citizen

### Mapping: eligibility_snapshots → eligibility_hints

| Source (warehouse) | Target (citizen) | Transformation |
|-------------------|------------------|----------------|
| `eligibility.eligibility_snapshots.family_id` | `eligibility_hints.family_id` | Direct |
| `eligibility.eligibility_snapshots.scheme_code` | `eligibility_hints.scheme_code` | Direct |
| `eligibility.eligibility_snapshots.evaluation_status` | `eligibility_hints.eligibility_status` | Direct |
| `eligibility.eligibility_snapshots.eligibility_score` | `eligibility_hints.eligibility_score` | Round to 2 decimals |
| `eligibility.eligibility_snapshots.confidence_score` | `eligibility_hints.confidence` | Round to 2 decimals |
| `eligibility.eligibility_snapshots.explanation` | `eligibility_hints.explanation` | Truncate to 500 chars |
| `eligibility.eligibility_snapshots.evaluation_timestamp` | `eligibility_hints.updated_at` | Direct |

**Filtering Rules**:
- Only sync if `evaluation_status` IN ('RULE_ELIGIBLE', 'POSSIBLE_ELIGIBLE')
- Only sync top 5 schemes per family (by eligibility_score DESC)
- Only sync records with `evaluation_timestamp` >= LAST_30_DAYS

### Mapping: profile_360 → profile_summary

| Source (warehouse) | Target (citizen) | Transformation | Masking |
|-------------------|------------------|----------------|---------|
| `public.profile_360.gr_id` | `profile_summary.family_id` | Map via family_id | No |
| `public.profile_360.vulnerability_level` | `profile_summary.vulnerability` | Direct | No |
| `public.profile_360.under_coverage_indicator` | `profile_summary.under_coverage` | Direct | No |
| `public.profile_360.inferred_income_band` | `profile_summary.income_category` | **MASKED** | Yes - Full mask |
| `public.profile_360.cluster_id` | `profile_summary.region` | Direct | No |

**Excluded Fields**:
- All ML features (age, gender_encoded, etc.)
- Detailed profile_data JSON
- Model metadata

### Mapping: golden_records → profile_data

| Source (warehouse) | Target (citizen) | Transformation | Masking |
|-------------------|------------------|----------------|---------|
| `public.golden_records.gr_id` | `profile_data.record_id` | Direct | No |
| `public.golden_records.family_id` | `profile_data.family_id` | Direct | No |
| `public.golden_records.jan_aadhaar` | `profile_data.jan_aadhaar` | **MASKED** | Yes - Partial (show last 4) |
| `public.golden_records.full_name` | `profile_data.full_name` | Direct | No |
| `public.golden_records.date_of_birth` | `profile_data.date_of_birth` | Direct | No |
| `public.golden_records.gender` | `profile_data.gender` | Direct | No |
| `public.golden_records.district_id` | `profile_data.district_id` | Direct | No |
| `public.golden_records.city_village` | `profile_data.city` | Direct | No |

## Direction 2: Citizen → Warehouse

### Mapping: citizens → golden_records

| Source (citizen) | Target (warehouse) | Transformation | Conflict Resolution |
|-----------------|-------------------|----------------|---------------------|
| `citizens.aadhaar_number` | `public.golden_records.jan_aadhaar` | Match key | Timestamp-based |
| `citizens.full_name` | `public.golden_records.full_name` | Direct | Latest wins |
| `citizens.date_of_birth` | `public.golden_records.date_of_birth` | Direct | Latest wins |
| `citizens.gender` | `public.golden_records.gender` | Direct | Latest wins |
| `citizens.mobile_number` | `public.golden_records.mobile_number` | New field (if exists) | Latest wins |
| `citizens.email` | `public.golden_records.email` | New field (if exists) | Latest wins |
| `citizens.city` | `public.golden_records.city_village` | Direct | Latest wins |
| `citizens.district` | `public.golden_records.district_id` | Map district name to ID | Latest wins |
| `citizens.pincode` | `public.golden_records.pincode` | Direct | Latest wins |
| `citizens.updated_at` | `public.golden_records.updated_at` | Direct | Compare field |
| N/A | `public.golden_records.updated_by` | Set to 'citizen_portal' | N/A |

**Matching Logic**:
- Match by `jan_aadhaar` = `aadhaar_number`
- If no match, create new record (but flag for review)
- Only sync if `verification_status` = 'verified'

### Mapping: service_applications → application_events

| Source (citizen) | Target (warehouse) | Transformation |
|-----------------|-------------------|----------------|
| `service_applications.id` | `application_events.application_id` | Direct |
| `service_applications.citizen_id` | `application_events.citizen_id` | Map via aadhaar |
| `service_applications.scheme_id` | `application_events.scheme_code` | Map scheme UUID to code |
| `service_applications.status` | `application_events.event_type` | Transform status to event |
| `service_applications.submitted_at` | `application_events.event_timestamp` | Direct |
| `service_applications.approved_at` | `application_events.approval_timestamp` | Conditional (if approved) |

**Event Type Mapping**:
- 'submitted' → 'APPLICATION_SUBMITTED'
- 'approved' → 'APPLICATION_APPROVED'
- 'rejected' → 'APPLICATION_REJECTED'

### Mapping: documents → document_metadata

| Source (citizen) | Target (warehouse) | Transformation |
|-----------------|-------------------|----------------|
| `documents.id` | `document_metadata.document_id` | Direct |
| `documents.citizen_id` | `document_metadata.citizen_id` | Map via aadhaar |
| `documents.document_type` | `document_metadata.document_type` | Direct |
| `documents.file_name` | `document_metadata.file_name` | Direct |
| `documents.file_size` | `document_metadata.file_size` | Direct |
| `documents.uploaded_at` | `document_metadata.uploaded_at` | Direct |

**Note**: Only sync metadata, NOT file content.

---

## Field-Level Transformation Rules

### Data Type Conversions

| Source Type | Target Type | Rule |
|------------|------------|------|
| DECIMAL(5,4) | DECIMAL(3,2) | Round to 2 decimals |
| TEXT | VARCHAR(500) | Truncate if > 500 chars |
| UUID | UUID | Direct |
| TIMESTAMP | TIMESTAMP | Direct |
| JSONB | TEXT | Extract specific fields only |

### Aggregation Rules

#### Eligibility Hints Aggregation
- Group by: `family_id`, `scheme_code`
- Order by: `eligibility_score DESC`
- Limit: Top 5 per family
- Only include: `evaluation_status` IN ('RULE_ELIGIBLE', 'POSSIBLE_ELIGIBLE')

#### Profile Summary Aggregation
- Group by: `family_id`
- Aggregate: Latest record per family (by `updated_at DESC`)

### Default Values

If source field is NULL:

| Field | Default Value |
|-------|--------------|
| `eligibility_score` | 0.0 |
| `confidence_score` | 0.0 |
| `explanation` | 'No explanation available' |
| `gender` | 'UNKNOWN' |

---

## Data Masking Reference

### Full Masking (Replaced with constant)
- `inferred_income_band` → "CONFIDENTIAL"
- `aadhaar_number` (if full masking required) → "***MASKED***"

### Partial Masking
- `jan_aadhaar` → "****-****-1234" (show last 4 digits)
- `mobile_number` → "******5678" (show last 4 digits)
- `email` → "u***@example.com" (show first char and domain)

### No Masking
- `eligibility_score`
- `scheme_code`
- `district_id`
- `vulnerability_level` (aggregated)

---

## Version History

- v1.0 (2024-12-29): Initial mapping reference created

