# CDC and Data Masking Strategy

**Document Version**: 1.0  
**Last Updated**: 2024-12-29  
**Status**: Planning Phase  
**Implementation Target**: Future Release

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture Overview](#2-architecture-overview)
3. [Key Design Decisions](#3-key-design-decisions)
4. [Debezium Configuration Strategy](#4-debezium-configuration-strategy)
5. [Data Masking Strategy with Apache Ranger](#5-data-masking-strategy-with-apache-ranger)
6. [Data Mapping & Transformation](#6-data-mapping--transformation)
7. [Conflict Resolution Strategy](#7-conflict-resolution-strategy)
8. [Data Filtering & Transformation Rules](#8-data-filtering--transformation-rules)
9. [Implementation Phases](#9-implementation-phases)
10. [Monitoring & Error Handling](#10-monitoring--error-handling)
11. [Security Considerations](#11-security-considerations)
12. [Next Steps](#12-next-steps)

---

## 1. Executive Summary

The SMART platform requires bidirectional Change Data Capture (CDC) between:
- **smart_warehouse**: AI/ML analytical database containing Golden Records, 360° Profiles, and eligibility data
- **smart_citizen**: Citizen portal database containing user profiles, applications, and documents

### Objectives

1. **Real-time Sync**: Capture and propagate data changes in near real-time
2. **Data Privacy**: Ensure PII is masked/encrypted during transit and at rest
3. **Bidirectional Flow**: Support data flow in both directions with conflict resolution
4. **Scalability**: Handle high-volume data changes efficiently
5. **Reliability**: Ensure data consistency and handle failures gracefully

### Technology Choices

- **CDC Engine**: Debezium (industry standard, PostgreSQL-native)
- **Message Broker**: Apache Kafka (high throughput, distributed)
- **Data Masking**: Apache Ranger (fine-grained access control and masking)

---

## 2. Architecture Overview

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    smart_warehouse DB                        │
│  (Source: ML models, 360° profiles, eligibility data)       │
│  - golden_records (public schema)                           │
│  - profile_360 (public schema)                              │
│  - eligibility.* (eligibility schema)                       │
│  - scheme_master (public schema)                            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ Debezium Connector #1
                        │ (smart_warehouse → smart_citizen)
                        │ Reads from PostgreSQL WAL
                        │
                        ▼
        ┌───────────────────────────────────────┐
        │      Apache Kafka Cluster              │
        │                                        │
        │  Topics:                                │
        │  - warehouse-to-citizen-cdc            │
        │    ├── eligibility_snapshots           │
        │    ├── profile_360                     │
        │    └── golden_records                  │
        │                                        │
        │  - citizen-to-warehouse-cdc            │
        │    ├── citizens                        │
        │    ├── service_applications            │
        │    └── documents                       │
        │                                        │
        │  - cdc-dlq (Dead Letter Queue)         │
        └───────────────┬───────────────────────┘
                        │
                        │ Debezium Connector #2
                        │ (smart_citizen → smart_warehouse)
                        │ Reads from PostgreSQL WAL
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                     smart_citizen DB                         │
│  (Source: Citizen portal changes)                           │
│  - citizens                                                 │
│  - service_applications                                     │
│  - documents                                                │
│  - eligibility_hints (synced from warehouse)               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  Apache Ranger                              │
│  - Data masking rules (PII protection)                      │
│  - Column-level access control                              │
│  - Field-level encryption policies                          │
│  - Audit logging                                            │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow Directions

#### Direction 1: Warehouse → Citizen (Read-Only View)
- **Purpose**: Deliver eligibility insights and profile summaries to citizens
- **Frequency**: Near real-time (< 1 minute latency)
- **Data Types**:
  - Eligibility hints (top 3-5 schemes)
  - Profile summaries (aggregated)
  - Notification triggers

#### Direction 2: Citizen → Warehouse (Feedback Loop)
- **Purpose**: Sync citizen updates back to warehouse for ML retraining
- **Frequency**: Near real-time (< 1 minute latency)
- **Data Types**:
  - Profile updates (name, address, contact)
  - Application submissions
  - Document metadata

---

## 3. Key Design Decisions

### 3.1 Direction 1: smart_warehouse → smart_citizen

**Purpose**: Sync eligibility results, profile updates, and ML-driven insights to citizen portal

**Tables to Sync**:

| Source Table (warehouse) | Target Table (citizen) | Sync Type | Masking Required |
|-------------------------|------------------------|-----------|------------------|
| `eligibility.eligibility_snapshots` | `eligibility_hints` | Transform & Aggregate | Partial |
| `public.profile_360` | `profile_summary` | Transform & Filter | Yes |
| `public.golden_records` | `profile_data` | Transform & Mask | Yes |
| `public.scheme_master` | `schemes` (cache) | Full Sync | No |

**Transformation Rules**:
- Eligibility snapshots → Only top 3-5 eligible schemes per family
- Profile 360 → Aggregated summary (exclude detailed ML features)
- Golden Records → Masked personal identifiers

### 3.2 Direction 2: smart_citizen → smart_warehouse

**Purpose**: Sync citizen-submitted updates back to warehouse for model retraining

**Tables to Sync**:

| Source Table (citizen) | Target Table (warehouse) | Sync Type | Conflict Resolution |
|------------------------|--------------------------|-----------|---------------------|
| `citizens` (updates only) | `public.golden_records` | Merge | Timestamp-based |
| `service_applications` | `application_events` | Transform | No conflicts |
| `documents` (metadata) | `document_metadata` | Transform | No conflicts |

**Transformation Rules**:
- Citizens → Update matching golden_records by jan_aadhaar
- Service applications → Transform to application_events format
- Documents → Extract metadata only (not file content)

---

## 4. Debezium Configuration Strategy

### 4.1 PostgreSQL WAL (Write-Ahead Log) Setup

Both databases must have logical replication enabled:

```sql
-- On smart_warehouse
ALTER SYSTEM SET wal_level = logical;
ALTER SYSTEM SET max_replication_slots = 10;
ALTER SYSTEM SET max_wal_senders = 10;

-- On smart_citizen  
ALTER SYSTEM SET wal_level = logical;
ALTER SYSTEM SET max_replication_slots = 10;
ALTER SYSTEM SET max_wal_senders = 10;

-- Restart PostgreSQL for changes to take effect
-- Then verify:
SHOW wal_level;  -- Should return 'logical'
```

### 4.2 Debezium User Setup

Create dedicated user with replication privileges:

```sql
-- On both databases
CREATE USER debezium_user WITH REPLICATION PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE smart_warehouse TO debezium_user;
GRANT CONNECT ON DATABASE smart_citizen TO debezium_user;
GRANT USAGE ON SCHEMA public TO debezium_user;
GRANT USAGE ON SCHEMA eligibility TO debezium_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO debezium_user;
GRANT SELECT ON ALL TABLES IN SCHEMA eligibility TO debezium_user;

-- Ensure future tables are also accessible
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO debezium_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA eligibility GRANT SELECT ON TABLES TO debezium_user;
```

### 4.3 Connector Configuration Files

See `config/` folder for detailed connector configurations:
- `warehouse-to-citizen-connector.json`
- `citizen-to-warehouse-connector.json`

---

## 5. Data Masking Strategy with Apache Ranger

### 5.1 PII Fields to Mask

#### High Sensitivity (Full Masking)
- Aadhaar numbers
- Jan Aadhaar numbers
- Financial data (income bands, bank details)

#### Medium Sensitivity (Partial Masking)
- Phone numbers (last 4 digits visible)
- Email addresses (domain visible)
- Addresses (city/district only)

#### Low Sensitivity (No Masking)
- Eligibility scores (aggregated)
- Scheme names
- District/city identifiers

### 5.2 Apache Ranger Policies

#### Policy 1: Mask Aadhaar Numbers
```json
{
  "name": "mask-aadhaar-in-cdc",
  "service": "kafka",
  "resources": {
    "topic": "warehouse-to-citizen-cdc.golden_records"
  },
  "maskingPolicy": {
    "accessTypes": ["consume"],
    "maskingConditions": [
      {
        "field": "after.jan_aadhaar",
        "maskType": "partial",
        "maskCharCount": 8,
        "unmaskCharCount": 4,
        "maskChar": "*",
        "unmaskCharPosition": "right"
      },
      {
        "field": "after.aadhaar_number",
        "maskType": "partial",
        "maskCharCount": 8,
        "unmaskCharCount": 4,
        "maskChar": "*",
        "unmaskCharPosition": "right"
      }
    ]
  }
}
```

#### Policy 2: Mask Income Data
```json
{
  "name": "mask-income-in-cdc",
  "service": "kafka",
  "resources": {
    "topic": "warehouse-to-citizen-cdc.profile_360"
  },
  "maskingPolicy": {
    "accessTypes": ["consume"],
    "maskingConditions": [
      {
        "field": "after.inferred_income_band",
        "maskType": "full",
        "maskValue": "CONFIDENTIAL"
      }
    ]
  }
}
```

### 5.3 Column-Level Access Control

**Citizen Portal Access Rules**:
- ✅ Eligibility scores (aggregated)
- ✅ Eligibility hints (top 3-5 schemes)
- ✅ Profile summary (aggregated, not detailed)
- ✅ Masked personal identifiers
- ❌ Raw ML features
- ❌ Detailed vulnerability scores
- ❌ Internal rule logic

---

## 6. Data Mapping & Transformation

### 6.1 Mapping: eligibility_snapshots → citizen portal

**Transformation Logic**:
```python
# Pseudo-code for transformation
def transform_eligibility_to_hint(snapshot):
    return {
        'family_id': snapshot.family_id,
        'scheme_code': snapshot.scheme_code,
        'eligibility_status': snapshot.evaluation_status,
        'eligibility_score': round(snapshot.eligibility_score, 2),
        'confidence': round(snapshot.confidence_score, 2),
        'explanation': snapshot.explanation[:500],  # Truncate
        'updated_at': snapshot.evaluation_timestamp
    }
```

**Kafka Consumer Implementation**:
```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'warehouse-to-citizen-cdc.eligibility_snapshots',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='citizen-portal-consumer'
)

def process_eligibility_update(message):
    value = message.value
    op = value.get('op')  # c, u, d (create, update, delete)
    
    if op in ['c', 'u']:
        after = value.get('after', {})
        
        # Transform to citizen portal format
        citizen_hint = {
            'family_id': after.get('family_id'),
            'scheme_code': after.get('scheme_code'),
            'eligibility_status': after.get('evaluation_status'),
            'eligibility_score': after.get('eligibility_score'),
            'confidence': after.get('confidence_score'),
            'explanation': after.get('explanation'),
            'updated_at': after.get('evaluation_timestamp')
        }
        
        # Only sync if eligibility_status is RULE_ELIGIBLE or POSSIBLE_ELIGIBLE
        if citizen_hint['eligibility_status'] in ['RULE_ELIGIBLE', 'POSSIBLE_ELIGIBLE']:
            upsert_citizen_eligibility_hint(citizen_hint)

for message in consumer:
    process_eligibility_update(message)
```

### 6.2 Mapping: citizens → warehouse (reverse sync)

**Transformation Logic**:
```python
def transform_citizen_to_golden_record(citizen_data):
    return {
        'jan_aadhaar': citizen_data.get('aadhaar_number'),
        'full_name': citizen_data.get('full_name'),
        'date_of_birth': citizen_data.get('date_of_birth'),
        'gender': citizen_data.get('gender'),
        'mobile_number': citizen_data.get('mobile_number'),
        'email': citizen_data.get('email'),
        'address_line1': citizen_data.get('address_line1'),
        'city': citizen_data.get('city'),
        'district': citizen_data.get('district'),
        'pincode': citizen_data.get('pincode'),
        'updated_by': 'citizen_portal',
        'updated_at': citizen_data.get('updated_at')
    }
```

**Kafka Consumer Implementation**:
```python
consumer = KafkaConsumer(
    'citizen-to-warehouse-cdc.citizens',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    group_id='warehouse-sync-consumer'
)

def process_citizen_update(message):
    value = message.value
    op = value.get('op')
    
    if op == 'u':  # Only sync updates, not creates
        after = value.get('after', {})
        before = value.get('before', {})
        
        # Check if critical fields changed
        changed_fields = []
        for field in ['full_name', 'date_of_birth', 'gender', 'mobile_number', 
                      'email', 'address_line1', 'city', 'district']:
            if after.get(field) != before.get(field):
                changed_fields.append(field)
        
        if changed_fields:
            # Update golden_records
            update_golden_record(
                jan_aadhaar=after.get('aadhaar_number'),
                data=transform_citizen_to_golden_record(after),
                updated_by='citizen_portal'
            )

for message in consumer:
    process_citizen_update(message)
```

---

## 7. Conflict Resolution Strategy

### 7.1 Conflict Scenarios

#### Scenario 1: Timestamp Conflict
- Both systems update the same record within the same second
- **Resolution**: Prefer smart_warehouse for ML data, smart_citizen for citizen-submitted data

#### Scenario 2: Data Conflict
- Same field updated differently in both systems
- **Resolution**: Compare timestamps, latest wins

#### Scenario 3: Deletion Conflict
- Record deleted in one system, updated in another
- **Resolution**: Log for manual review

### 7.2 Conflict Detection Table

```sql
CREATE TABLE cdc_conflict_resolution (
    conflict_id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    source_system VARCHAR(50) NOT NULL, -- 'warehouse' or 'citizen'
    conflict_type VARCHAR(50) NOT NULL, -- 'timestamp_conflict', 'data_conflict', 'deletion_conflict'
    warehouse_value JSONB,
    citizen_value JSONB,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_by VARCHAR(100),
    resolved_at TIMESTAMP,
    resolution_action VARCHAR(50), -- 'warehouse_wins', 'citizen_wins', 'manual_review', 'merged'
    resolution_notes TEXT
);

CREATE INDEX idx_conflict_resolution_unresolved 
ON cdc_conflict_resolution(resolved_at) 
WHERE resolved_at IS NULL;
```

### 7.3 Conflict Resolution Logic

```python
def resolve_conflict(conflict):
    if conflict['conflict_type'] == 'timestamp_conflict':
        # Compare timestamps (with microsecond precision if available)
        warehouse_ts = conflict['warehouse_value'].get('updated_at')
        citizen_ts = conflict['citizen_value'].get('updated_at')
        
        if warehouse_ts > citizen_ts:
            return 'warehouse_wins'
        elif citizen_ts > warehouse_ts:
            return 'citizen_wins'
        else:
            # Same timestamp - use priority rules
            table = conflict['table_name']
            if table in ['eligibility_snapshots', 'profile_360']:
                return 'warehouse_wins'  # Warehouse is authoritative for ML data
            elif table == 'citizens':
                return 'citizen_wins'  # Citizen portal is authoritative for user data
            else:
                return 'manual_review'
    
    elif conflict['conflict_type'] == 'deletion_conflict':
        return 'manual_review'  # Always review deletions
    
    else:
        return 'manual_review'
```

---

## 8. Data Filtering & Transformation Rules

### 8.1 Warehouse → Citizen Filtering

**Include**:
- ✅ Eligibility hints (top 3-5 schemes per family)
- ✅ Profile summary (aggregated data)
- ✅ Notification triggers (new eligible schemes)
- ✅ Scheme master data (for dropdowns)

**Exclude**:
- ❌ Raw ML features
- ❌ Internal rule logic
- ❌ Model confidence intervals (detailed)
- ❌ Detailed vulnerability scores
- ❌ Internal audit logs

**Filtering Query**:
```sql
-- Example: Only sync top eligible schemes
SELECT DISTINCT ON (family_id, scheme_code)
    family_id,
    scheme_code,
    evaluation_status,
    eligibility_score,
    confidence_score,
    explanation
FROM eligibility.eligibility_snapshots
WHERE evaluation_status IN ('RULE_ELIGIBLE', 'POSSIBLE_ELIGIBLE')
  AND evaluation_timestamp >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY family_id, scheme_code, eligibility_score DESC
LIMIT 5;  -- Top 5 per family
```

### 8.2 Citizen → Warehouse Filtering

**Include**:
- ✅ Citizen profile updates (name, address, contact)
- ✅ Application submissions (for training data)
- ✅ Document uploads (metadata only)
- ✅ Status changes

**Exclude**:
- ❌ Authentication credentials
- ❌ Session data
- ❌ Temporary application drafts
- ❌ Deleted records (soft deletes only)

**Filtering Query**:
```sql
-- Example: Only sync verified updates
SELECT 
    id,
    aadhaar_number,
    full_name,
    date_of_birth,
    gender,
    mobile_number,
    email,
    address_line1,
    city,
    district,
    pincode,
    updated_at
FROM citizens
WHERE verification_status = 'verified'
  AND status = 'active'
  AND updated_at >= CURRENT_TIMESTAMP - INTERVAL '1 day';
```

---

## 9. Implementation Phases

### Phase 1: Infrastructure Setup (Week 1-2)
1. ✅ Set up Apache Kafka cluster (3 brokers minimum)
2. ✅ Deploy Kafka Connect with Debezium
3. ✅ Configure PostgreSQL WAL on both databases
4. ✅ Create Debezium replication users
5. ✅ Deploy Apache Ranger (if not already available)

### Phase 2: Unidirectional Sync (Week 3-4)
1. ✅ Deploy warehouse-to-citizen connector
2. ✅ Create Kafka topics
3. ✅ Implement citizen portal consumer
4. ✅ Test with sample data
5. ✅ Configure basic data masking

### Phase 3: Bidirectional Sync (Week 5-6)
1. ✅ Deploy citizen-to-warehouse connector
2. ✅ Implement warehouse sync consumer
3. ✅ Add conflict detection logic
4. ✅ Test bidirectional scenarios
5. ✅ Implement conflict resolution

### Phase 4: Data Masking Enhancement (Week 7)
1. ✅ Configure comprehensive Apache Ranger policies
2. ✅ Test masking on all sensitive fields
3. ✅ Verify compliance requirements
4. ✅ Performance testing

### Phase 5: Production Hardening (Week 8)
1. ✅ Monitoring and alerting setup
2. ✅ Error handling and DLQ configuration
3. ✅ Load testing
4. ✅ Documentation and runbooks
5. ✅ Rollback procedures

---

## 10. Monitoring & Error Handling

### 10.1 CDC Health Monitoring

**Key Metrics to Monitor**:
- Debezium connector status (RUNNING, PAUSED, FAILED)
- Kafka consumer lag (messages behind)
- Message throughput (messages/second)
- Error rate (failed messages/total messages)
- Replication lag (seconds behind source)

**Monitoring Dashboard**:
```python
# Example monitoring script
def check_debezium_connector_status():
    connectors = [
        'warehouse-to-citizen-connector',
        'citizen-to-warehouse-connector'
    ]
    
    for connector in connectors:
        response = requests.get(
            f'http://kafka-connect:8083/connectors/{connector}/status'
        )
        status = response.json()
        
        if status['connector']['state'] != 'RUNNING':
            alert(f"Connector {connector} is {status['connector']['state']}")
        
        for task in status['tasks']:
            if task['state'] != 'RUNNING':
                alert(f"Task {task['id']} of {connector} is {task['state']}")
```

### 10.2 Error Handling & Dead Letter Queue

**DLQ Configuration**:
```json
{
  "errors.tolerance": "all",
  "errors.log.enable": true,
  "errors.log.include.messages": true,
  "errors.deadletterqueue.topic.name": "cdc-dlq",
  "errors.deadletterqueue.topic.replication.factor": 3,
  "errors.deadletterqueue.context.headers.enable": true
}
```

**DLQ Processing**:
- Monitor DLQ topic for failed messages
- Alert if DLQ message count > 100
- Implement retry mechanism with exponential backoff
- Manual review for persistent failures

### 10.3 Consumer Lag Monitoring

**Alert Thresholds**:
- **Warning**: Lag > 10,000 messages or > 5 minutes
- **Critical**: Lag > 100,000 messages or > 30 minutes

**Lag Monitoring**:
```python
from kafka.admin import KafkaAdminClient
from kafka import KafkaConsumer

def check_consumer_lag():
    consumer = KafkaConsumer(
        'warehouse-to-citizen-cdc.eligibility_snapshots',
        bootstrap_servers=['localhost:9092'],
        group_id='citizen-portal-consumer'
    )
    
    for partition in consumer.assignment():
        lag = consumer.get_lag(partition)
        if lag > 10000:
            alert(f"High consumer lag: {lag} messages for partition {partition}")
```

---

## 11. Security Considerations

### 11.1 Database Security

**Debezium User Permissions**:
- Minimal required permissions (read-only for CDC)
- Separate credentials for each database
- Rotate passwords regularly
- Use SSL/TLS for database connections

**Connection String with SSL**:
```
jdbc:postgresql://172.17.16.1:5432/smart_warehouse?ssl=true&sslmode=require
```

### 11.2 Kafka Security

**Authentication & Encryption**:
- SASL/SCRAM authentication for Kafka
- TLS/SSL encryption for data in transit
- ACLs (Access Control Lists) for topic-level permissions

**Kafka ACL Example**:
```
# Allow consumer group to read from topic
kafka-acls --bootstrap-server localhost:9092 \
  --add --allow-principal User:citizen-portal-consumer \
  --consumer --group citizen-portal-consumer-group \
  --topic warehouse-to-citizen-cdc.eligibility_snapshots
```

### 11.3 Data Masking Security

**Apache Ranger Policies**:
- Enforce masking at Kafka topic level
- Apply different masking rules based on consumer group
- Audit all data access through Ranger

### 11.4 Audit Logging

**Audit Requirements**:
- Log all CDC events (source, target, timestamp)
- Log all conflict resolutions
- Log all DLQ messages
- Log all data access through Ranger

**Audit Table**:
```sql
CREATE TABLE cdc_audit_log (
    audit_id SERIAL PRIMARY KEY,
    event_type VARCHAR(50), -- 'sync', 'conflict', 'error', 'mask'
    source_system VARCHAR(50),
    target_system VARCHAR(50),
    table_name VARCHAR(100),
    record_id UUID,
    operation VARCHAR(10), -- 'INSERT', 'UPDATE', 'DELETE'
    masked_fields TEXT[],
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(100),
    details JSONB
);
```

---

## 12. Next Steps

### Immediate Actions (Planning)
1. ✅ Document CDC strategy (this document)
2. ✅ Identify all tables requiring sync
3. ✅ Define data masking requirements
4. ✅ Plan infrastructure requirements

### Before Implementation
1. **Infrastructure Setup**:
   - Procure/allocate Kafka cluster resources
   - Plan Apache Ranger deployment
   - Network connectivity between databases and Kafka

2. **Database Preparation**:
   - Enable WAL on both databases
   - Create Debezium replication users
   - Grant required permissions

3. **Team Preparation**:
   - Train team on Debezium and Kafka
   - Define roles and responsibilities
   - Establish monitoring procedures

### Implementation Timeline
- **Phase 1-2**: 4 weeks (Infrastructure + Unidirectional)
- **Phase 3-4**: 3 weeks (Bidirectional + Masking)
- **Phase 5**: 1 week (Production Hardening)

**Total Estimated Time**: 8 weeks

---

## Appendix

### A. Glossary

- **CDC**: Change Data Capture - technique to identify and capture changes in source databases
- **WAL**: Write-Ahead Log - PostgreSQL transaction log used for replication
- **DLQ**: Dead Letter Queue - queue for messages that cannot be processed
- **PII**: Personally Identifiable Information - data that can identify an individual

### B. References

- [Debezium Documentation](https://debezium.io/documentation/)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Apache Ranger Documentation](https://ranger.apache.org/)
- [PostgreSQL Logical Replication](https://www.postgresql.org/docs/current/logical-replication.html)

### C. Contact

For questions or updates to this strategy:
- Technical Lead: [To be assigned]
- Data Architect: [To be assigned]
- Security Lead: [To be assigned]

---

**Document Status**: 📋 Planning Complete  
**Next Review**: Before implementation begins  
**Version History**:
- v1.0 (2024-12-29): Initial planning document created

