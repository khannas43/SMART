# Data Sync Frequency and Schedule

**Document Version**: 1.0  
**Created**: 2024-12-30  
**Purpose**: Detailed schedule and frequency specifications for data synchronization  
**Status**: Planning Phase

---

## Schedule Overview

### Summary Table

| Direction | Data Type | Sync Pattern | Frequency | Schedule | Peak Hours Avoided |
|-----------|-----------|--------------|-----------|----------|-------------------|
| Warehouse → Citizen | Scheme Master | Batch | Daily | 00:00 UTC | Yes |
| Warehouse → Citizen | Profile Summary | Hybrid | Event + Hourly | Continuous + :00 | - |
| Warehouse → Citizen | Golden Records | Hybrid | Event + Daily | Continuous + 01:00 UTC | Yes |
| Warehouse → Citizen | Eligibility Hints | Event | Real-time | Continuous | - |
| Warehouse → Citizen | Forecast Data | Event | On-demand | On generation | - |
| Warehouse → Citizen | Decision Updates | Event | Real-time | Continuous | - |
| Warehouse → Citizen | ML Alerts | Event | Real-time | Continuous | - |
| Citizen → Warehouse | Profile Updates | Event | Real-time | Continuous | - |
| Citizen → Warehouse | Application Submissions | Event | Real-time | Continuous | - |
| Citizen → Warehouse | Document Metadata | Event | Real-time | Continuous | - |
| Citizen → Warehouse | User Behavior | Batch | Daily | 02:00 UTC | Yes |
| Citizen → Warehouse | Feedback | Batch | Daily | 02:30 UTC | Yes |

---

## Direction 1: smart_warehouse → smart_citizen

### Batch Sync Schedules

#### 1. Scheme Master Sync

**Frequency**: Daily  
**Schedule**: 00:00 UTC (05:30 IST)  
**Duration**: ~5 minutes  
**Pattern**: Full refresh (replace all active schemes)

**Rationale**:
- Master data, changes infrequently
- Low volume (~200 records)
- Non-critical timing (schemes don't change daily)
- Scheduled during low-traffic hours (night in India)

**Dependencies**: None  
**Failure Impact**: Low (citizens see slightly outdated scheme info)  
**Recovery**: Rerun job manually if failed

---

#### 2. Profile Summary Full Sync

**Frequency**: Daily  
**Schedule**: 00:30 UTC (06:00 IST)  
**Duration**: ~30 minutes  
**Pattern**: Full sync (reconcile all records)

**Rationale**:
- Reconciliation for event-driven sync
- Ensures data consistency
- Catches any missed CDC events
- Low-traffic hours

**Dependencies**: Profile Summary Event Sync (primary source)  
**Failure Impact**: Medium (data consistency risk)  
**Recovery**: Rerun job, compare with event sync logs

---

#### 3. Golden Records Full Sync

**Frequency**: Daily  
**Schedule**: 01:00 UTC (06:30 IST)  
**Duration**: ~45 minutes  
**Pattern**: Incremental sync (only updated in last 24h)

**Rationale**:
- Reconciliation for event-driven sync
- Large volume (~100K records), incremental reduces load
- Catches missed CDC events
- Sequential with Profile Summary (reduces DB load)

**Dependencies**: Golden Records Event Sync (primary source)  
**Failure Impact**: Medium (profile data consistency)  
**Recovery**: Rerun job, compare with event sync logs

---

#### 4. Hourly Profile Summary Incremental

**Frequency**: Hourly  
**Schedule**: Every hour at :00 minutes (e.g., 00:00, 01:00, 02:00...)  
**Duration**: ~10 minutes  
**Pattern**: Incremental (only updated since last sync)

**Rationale**:
- Additional consistency check for critical profile data
- Catch missed events between daily full sync
- Low overhead (incremental)
- Frequent enough for data freshness

**Dependencies**: Profile Summary Event Sync (primary source)  
**Failure Impact**: Low (event sync is primary)  
**Recovery**: Next hourly sync will catch up

---

### Event-Driven Sync Schedules

#### 1. Eligibility Hints Sync

**Frequency**: Real-time (Event-driven)  
**Schedule**: Continuous (CDC)  
**Latency**: < 5 seconds  
**Pattern**: Event-driven (on INSERT/UPDATE of eligibility_snapshots)

**Rationale**:
- User-facing data (eligibility checker screen)
- Needs immediate visibility for citizens
- Critical for user experience
- Low latency required

**Trigger**: 
- New eligibility evaluation completed
- Eligibility score updated
- Status changed (eligible → not eligible)

**Volume**: ~50K events/day (filtered to ~10K after top-5 filtering)  
**Peak Hours**: Distributed (no specific peak)  
**Failure Impact**: High (users see stale eligibility data)

---

#### 2. Forecast Data Sync

**Frequency**: On-demand (Event-driven)  
**Schedule**: On forecast generation  
**Latency**: < 2 seconds  
**Pattern**: API callback (when forecast service generates forecast)

**Rationale**:
- Generated on-demand when user requests
- Needs immediate visibility
- User is waiting for result
- API callback more efficient than polling

**Trigger**: 
- Forecast API generates new forecast
- Forecast recomputed (on profile change)

**Volume**: ~50K forecasts/day  
**Peak Hours**: Business hours (09:00-18:00 IST)  
**Failure Impact**: High (user waiting for forecast)

---

#### 3. Decision Updates Sync

**Frequency**: Real-time (Event-driven)  
**Schedule**: Continuous (CDC)  
**Latency**: < 5 seconds  
**Pattern**: Event-driven (on UPDATE of decision.applications)

**Rationale**:
- Application status changes critical for users
- Users actively tracking applications
- Needs immediate notification
- High user expectation

**Trigger**:
- Application decision made (approved/rejected)
- Status changed (pending → in_review)
- Risk score updated

**Volume**: ~10K decisions/day  
**Peak Hours**: Business hours (09:00-18:00 IST)  
**Failure Impact**: High (users see stale application status)

---

#### 4. ML Alerts Sync

**Frequency**: Real-time (Event-driven)  
**Schedule**: Continuous (Event-driven via API)  
**Latency**: < 5 seconds  
**Pattern**: Event-driven (when ML service generates alert)

**Rationale**:
- Time-sensitive alerts (benefit expiry, verification needed)
- Users need immediate notification
- Proactive outreach critical
- API callback from ML services

**Trigger**:
- Beneficiary detection alert generated (AI-PLATFORM-07)
- Proactive inclusion alert generated (AI-PLATFORM-09)
- Predictive alert generated (AI-PLATFORM-14)

**Volume**: ~20K alerts/day  
**Peak Hours**: Distributed  
**Failure Impact**: Medium (alerts delayed but eventually synced)

---

## Direction 2: smart_citizen → smart_warehouse

### Batch Sync Schedules

#### 1. User Behavior Analytics Sync

**Frequency**: Daily  
**Schedule**: 02:00 UTC (07:30 IST)  
**Duration**: ~15 minutes  
**Pattern**: Batch aggregation and sync

**Rationale**:
- Analytics data, non-critical timing
- Large volume (~500K events/day)
- Aggregated to reduce volume
- Scheduled after peak hours

**Dependencies**: User behavior events collected in citizen portal  
**Failure Impact**: Low (analytics delayed by one day)  
**Recovery**: Rerun job, can reprocess from source

---

#### 2. Feedback Sync

**Frequency**: Daily  
**Schedule**: 02:30 UTC (08:00 IST)  
**Duration**: ~5 minutes  
**Pattern**: Full sync (all new feedback since last sync)

**Rationale**:
- Analytics data, non-critical timing
- Low volume (~1K/day)
- Sentiment analysis can wait
- Sequential with user behavior (reduces load)

**Dependencies**: Feedback table in citizen portal  
**Failure Impact**: Low (sentiment analysis delayed)  
**Recovery**: Rerun job

---

### Event-Driven Sync Schedules

#### 1. Profile Updates Sync

**Frequency**: Real-time (Event-driven)  
**Schedule**: Continuous (CDC)  
**Latency**: < 5 seconds  
**Pattern**: Event-driven (on UPDATE of citizens table)

**Rationale**:
- Profile changes needed for ML model training
- Real-time sync enables immediate ML updates
- Critical for ML accuracy
- Low latency required for training data freshness

**Trigger**:
- Citizen updates profile (name, DOB, address, etc.)
- Profile verification status changed
- Contact info updated (mobile, email)

**Volume**: ~20K updates/day  
**Peak Hours**: Evening hours (18:00-22:00 IST)  
**Failure Impact**: Medium (ML training data delayed)

---

#### 2. Application Submissions Sync

**Frequency**: Real-time (Event-driven)  
**Schedule**: Continuous (CDC)  
**Latency**: < 5 seconds  
**Pattern**: Event-driven (on INSERT/UPDATE of service_applications)

**Rationale**:
- New applications trigger ML workflows (auto-approval, risk scoring)
- Applications need immediate ML processing
- Critical for STP (Straight-Through Processing)
- Low latency required

**Trigger**:
- New application submitted
- Application status changed
- Application withdrawn

**Volume**: ~5K applications/day  
**Peak Hours**: Business hours (09:00-18:00 IST)  
**Failure Impact**: High (ML workflows delayed)

---

#### 3. Document Metadata Sync

**Frequency**: Real-time (Event-driven)  
**Schedule**: Continuous (CDC)  
**Latency**: < 5 seconds  
**Pattern**: Event-driven (on INSERT of documents table)

**Rationale**:
- Documents needed for ML processing (OCR, verification)
- Document metadata triggers ML workflows
- Real-time sync enables immediate processing
- Critical for document intelligence use cases

**Trigger**:
- New document uploaded
- Document verification status changed
- Document deleted

**Volume**: ~15K documents/day  
**Peak Hours**: Distributed  
**Failure Impact**: Medium (document processing delayed)

---

## Time Zone Considerations

### Primary Time Zone
- **IST (India Standard Time)**: UTC + 5:30
- Most batch jobs scheduled to avoid peak hours in India

### Peak Hours (IST)
- **Morning**: 09:00 - 12:00 IST
- **Evening**: 18:00 - 22:00 IST

### Low-Traffic Hours (IST)
- **Night**: 23:00 - 06:00 IST (when most batch jobs run)

---

## Schedule Optimization

### Load Balancing

1. **Batch Jobs**: Staggered to avoid concurrent load
   - 00:00 UTC: Scheme Master (light load)
   - 00:30 UTC: Profile Summary (medium load)
   - 01:00 UTC: Golden Records (heavy load)
   - 02:00 UTC: User Behavior (light load)
   - 02:30 UTC: Feedback (light load)

2. **Event Processing**: Distributed throughout day
   - No specific scheduling (handled by CDC/event system)
   - Consumer scaling handles peak loads

### Resource Allocation

1. **Database Connections**: 
   - Batch jobs: Limited connections (5-10 per job)
   - Event processing: Connection pool (20-50 connections)

2. **Kafka Partitions**:
   - Eligibility hints: 10 partitions (high volume)
   - Decisions: 5 partitions (medium volume)
   - Profile updates: 10 partitions (high volume)
   - Documents: 5 partitions (medium volume)

---

## Monitoring Schedule Compliance

### Metrics to Track

1. **Batch Jobs**:
   - Start time (should match schedule)
   - Duration (should be within estimates)
   - Completion status (success/failure)
   - Records processed (should match expectations)

2. **Event Processing**:
   - Consumer lag (should be < 5 seconds)
   - Processing rate (events/second)
   - Error rate (should be < 1%)

### Alerting

1. **Batch Job Delayed**: Alert if job starts > 15 minutes after schedule
2. **Batch Job Failed**: Immediate alert
3. **Consumer Lag > 60 seconds**: Warning alert
4. **Consumer Lag > 300 seconds**: Critical alert

---

## Maintenance Windows

### Planned Maintenance

**Schedule**: First Sunday of each month, 02:00-04:00 UTC (07:30-09:30 IST)

**Activities**:
- Database maintenance
- Index rebuilds
- Connection pool optimization
- CDC connector updates

**Impact**: 
- Batch jobs paused during window
- Event processing continues (buffered in Kafka)

---

## Disaster Recovery Schedule

### Backup Sync

**Frequency**: Weekly  
**Schedule**: Sunday 03:00 UTC (08:30 IST)  
**Purpose**: Full data reconciliation and validation

**Activities**:
- Compare record counts between databases
- Validate data integrity
- Identify and fix discrepancies
- Generate reconciliation report

---

**Next Steps**: 
- Implement schedules in orchestration tool (Airflow)
- Set up monitoring and alerting
- Configure CDC connectors
- Test sync schedules in staging environment

