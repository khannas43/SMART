# Batch vs Event-Based Data Sync Plan

**Document Version**: 1.0  
**Created**: 2024-12-30  
**Purpose**: Detailed plan for batch and event-based data synchronization  
**Status**: Planning Phase

---

## Overview

This document defines when to use batch vs event-based synchronization for data flows between `smart_warehouse` and `smart_citizen` databases.

---

## Decision Matrix

| Data Type | Sync Pattern | Reason | Technology |
|-----------|--------------|--------|------------|
| Scheme Master | Batch (Daily) | Master data, changes infrequently | ETL Job (Airflow) |
| Profile Summary | Hybrid (Event + Batch) | Balance real-time needs with consistency | CDC + Scheduled Job |
| Eligibility Hints | Event (Real-time) | User-facing, needs immediate updates | CDC (Debezium) |
| Forecast Data | Event (Real-time) | Generated on-demand, immediate visibility | API Callback |
| Decision Updates | Event (Real-time) | Application status changes critical | CDC (Debezium) |
| Profile Updates | Event (Real-time) | Citizen edits need immediate ML sync | CDC (Debezium) |
| Application Submissions | Event (Real-time) | New applications trigger ML workflows | CDC (Debezium) |
| Document Metadata | Event (Real-time) | Documents needed for ML processing | CDC (Debezium) |
| User Behavior | Batch (Daily) | Analytics, non-critical, large volume | ETL Job (Airflow) |
| Feedback | Batch (Daily) | Analytics, non-critical | ETL Job (Airflow) |

---

## Batch Synchronization

### When to Use Batch

1. **Master/Reference Data**: Data that changes infrequently
   - Scheme catalog
   - Reference tables
   - Lookup data

2. **Large Volume Data**: Data with high volume, non-critical timing
   - Historical data
   - Analytics data
   - Aggregated data

3. **Non-Critical Updates**: Data where slight delay is acceptable
   - User behavior analytics
   - Feedback aggregation
   - Reporting data

4. **Cost Optimization**: Reduce system load by batching

### Batch Sync Schedule

#### Daily Batches

| Job Name | Source → Target | Schedule | Duration Estimate |
|----------|----------------|----------|-------------------|
| Scheme Master Sync | `eligibility.scheme_master` → `schemes` | 00:00 UTC Daily | 5 minutes |
| Profile Summary Full Sync | `public.profile_360` → `profile_summary` | 00:30 UTC Daily | 30 minutes |
| Golden Records Full Sync | `public.golden_records` → `profile_data` | 01:00 UTC Daily | 45 minutes |
| User Behavior Sync | `analytics.*` → `analytics.user_behavior` | 02:00 UTC Daily | 15 minutes |
| Feedback Sync | `feedback` → `feedback_analytics` | 02:30 UTC Daily | 5 minutes |

#### Hourly Batches

| Job Name | Source → Target | Schedule | Duration Estimate |
|----------|----------------|----------|-------------------|
| Profile Summary Incremental | `public.profile_360` → `profile_summary` | Every hour (:00) | 10 minutes |

### Batch Job Implementation

#### Technology Stack

- **Orchestration**: Apache Airflow
- **Execution**: Python scripts / Java Spring Batch
- **Monitoring**: Airflow UI + Prometheus
- **Alerting**: Slack/Email on failures

#### Sample Airflow DAG

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'warehouse_to_citizen_batch_sync',
    default_args=default_args,
    description='Daily batch sync from warehouse to citizen portal',
    schedule_interval='0 0 * * *',  # Daily at midnight UTC
    catchup=False,
)

# Scheme Master Sync
scheme_sync = PythonOperator(
    task_id='sync_scheme_master',
    python_callable=sync_scheme_master,
    dag=dag,
)

# Profile Summary Sync
profile_sync = PythonOperator(
    task_id='sync_profile_summary',
    python_callable=sync_profile_summary,
    dag=dag,
)

scheme_sync >> profile_sync
```

#### Batch Job Features

1. **Idempotency**: Jobs can be rerun safely
2. **Incremental Loading**: Only sync changed records (based on `updated_at`)
3. **Full Refresh Option**: Parameter to force full sync
4. **Error Handling**: Log errors, continue processing, report at end
5. **Performance**: Parallel processing where possible
6. **Validation**: Post-sync data validation checks

---

## Event-Based Synchronization

### When to Use Event-Driven

1. **User-Facing Data**: Data displayed to users that needs real-time updates
   - Eligibility scores
   - Application status
   - Profile confidence badges

2. **Critical Workflows**: Data that triggers important workflows
   - New application submissions
   - Profile updates for ML training
   - Document uploads for verification

3. **Low Latency Required**: Data where delay is unacceptable
   - Decision updates
   - Forecast generation
   - Alert notifications

4. **Low Volume, High Frequency**: Small updates that happen frequently

### Event-Driven Sync Implementation

#### Technology Stack

- **CDC**: Debezium (PostgreSQL connector)
- **Message Queue**: Apache Kafka
- **Processing**: Kafka Consumers (Java/Spring)
- **Monitoring**: Kafka Metrics + Prometheus
- **Alerting**: On consumer lag or errors

#### CDC Setup (Debezium)

**Connector Configuration**: `warehouse-to-citizen-connector.json`

```json
{
  "name": "warehouse-to-citizen-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "warehouse-db-host",
    "database.port": "5432",
    "database.user": "debezium_user",
    "database.password": "secure_password",
    "database.dbname": "smart_warehouse",
    "database.server.name": "warehouse",
    "table.include.list": "public.golden_records,public.profile_360,eligibility.eligibility_snapshots,decision.applications",
    "topic.prefix": "warehouse-cdc",
    "slot.name": "warehouse_citizen_slot",
    "publication.name": "warehouse_citizen_publication",
    "plugin.name": "pgoutput",
    "snapshot.mode": "never",
    "transforms": "route",
    "transforms.route.type": "org.apache.kafka.connect.transforms.RegexRouter",
    "transforms.route.regex": "warehouse-cdc.public.(.*)",
    "transforms.route.replacement": "warehouse-to-citizen.$1"
  }
}
```

#### Event Processing Flow

```
PostgreSQL (smart_warehouse)
    ↓ (WAL)
Debezium Connector
    ↓ (Kafka Topic)
Kafka Consumer (Citizen Portal Service)
    ↓ (Transform + Mask)
PostgreSQL (smart_citizen)
```

#### Event Types Handled

1. **INSERT Events**: New records created
2. **UPDATE Events**: Existing records modified
3. **DELETE Events**: Records deleted (soft delete preferred)

#### Event Processing Rules

1. **Deduplication**: Use event ID to prevent duplicate processing
2. **Ordering**: Process events in order (within partition)
3. **Idempotency**: Handle duplicate events gracefully
4. **Error Handling**: Dead Letter Queue for failed events
5. **Monitoring**: Track consumer lag, processing rate

#### Sample Consumer Code (Java Spring)

```java
@KafkaListener(topics = "warehouse-to-citizen.eligibility_snapshots")
public void processEligibilitySnapshot(ConsumerRecord<String, String> record) {
    try {
        EligibilitySnapshotEvent event = objectMapper.readValue(
            record.value(), 
            EligibilitySnapshotEvent.class
        );
        
        // Apply filtering rules
        if (!shouldSync(event)) {
            return;
        }
        
        // Apply masking
        EligibilityHint hint = transformAndMask(event);
        
        // Insert/update in citizen database
        eligibilityHintRepository.save(hint);
        
        // Commit offset
        acknowledgment.acknowledge();
        
    } catch (Exception e) {
        log.error("Error processing eligibility snapshot", e);
        // Send to DLQ
        dlqProducer.send("dlq-eligibility-snapshots", record.value());
    }
}
```

---

## Hybrid Synchronization

### Profile Summary (Example)

**Why Hybrid?**
- Need real-time updates for user-facing changes
- Need full sync for data consistency and catching missed events

**Implementation**:
1. **Event-Driven (Primary)**: CDC for real-time updates
2. **Batch (Backup)**: Hourly full sync for consistency
3. **Reconciliation**: Daily comparison to identify discrepancies

**Schedule**:
- Event-driven: Continuous (CDC)
- Batch: Hourly at :00 minutes
- Reconciliation: Daily at 03:00 UTC

---

## Performance Considerations

### Batch Optimization

1. **Parallel Processing**: Process multiple tables in parallel
2. **Incremental Loading**: Only sync changed records (`updated_at > last_sync`)
3. **Batching**: Process records in batches (1000-5000 per batch)
4. **Connection Pooling**: Reuse database connections
5. **Indexing**: Ensure indexes on join/where columns

### Event-Driven Optimization

1. **Partitioning**: Partition Kafka topics by key (citizen_id, family_id)
2. **Consumer Scaling**: Scale consumers horizontally
3. **Batch Processing**: Process multiple events in batch
4. **Async Processing**: Don't block on individual events
5. **Caching**: Cache reference data (scheme codes, etc.)

---

## Monitoring & Alerting

### Key Metrics

**Batch Jobs**:
- Job execution time
- Records processed
- Success/failure rate
- Data quality metrics (validation failures)

**Event Processing**:
- Consumer lag (seconds behind)
- Processing rate (events/second)
- Error rate
- DLQ size

### Alert Thresholds

1. **Batch Job Failure**: Immediate alert
2. **Consumer Lag > 60 seconds**: Warning
3. **Consumer Lag > 300 seconds**: Critical alert
4. **Error Rate > 1%**: Warning
5. **DLQ Size > 1000**: Critical alert
6. **Sync Success Rate < 99%**: Warning

---

## Rollback & Recovery

### Batch Jobs

1. **Failed Job**: Rerun failed job (idempotent)
2. **Partial Failure**: Identify failed records, rerun only those
3. **Data Corruption**: Restore from backup, rerun sync

### Event Processing

1. **Consumer Failure**: Restart consumer (will resume from last committed offset)
2. **Message Processing Error**: Send to DLQ, process separately
3. **Data Corruption**: Replay events from Kafka (if retention allows)

---

**Next Steps**: See:
- `DATA_FREQUENCY_SCHEDULE.md` - Detailed schedules and timing
- `DATA_MAPPING_REFERENCE.md` - Field-level mappings
- `CDC_DATA_MASKING_STRATEGY.md` - Data masking during sync

