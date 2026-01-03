# Data Flow Summary - Quick Reference

**Document Version**: 1.0  
**Created**: 2024-12-30  
**Purpose**: Quick reference summary of data flows  
**Status**: Reference Document

---

## Data Flow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    smart_warehouse (AI/ML)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Golden       │  │ Eligibility  │  │ Decisions    │        │
│  │ Records      │  │ Snapshots    │  │ Forecasts    │        │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘        │
│         │                  │                  │                 │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          │  (Event/CDC)     │  (Event/CDC)     │  (Event/API)
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    smart_citizen (Portal)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Profile      │  │ Eligibility  │  │ Benefits     │        │
│  │ Data         │  │ Hints        │  │ Forecasts    │        │
│  └──────▲───────┘  └──────▲───────┘  └──────▲───────┘        │
│         │                  │                  │                 │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          │  (Event/CDC)     │  (Event/CDC)     │  (Batch)
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
┌─────────▼───────┐  ┌───────▼───────┐  ┌───────▼───────┐
│ Applications    │  │ Documents     │  │ Analytics     │
│ Submissions     │  │ Metadata      │  │ Feedback      │
└─────────────────┘  └───────────────┘  └───────────────┘
```

---

## Direction 1: smart_warehouse → smart_citizen

### Batch Syncs

| Data | Source Table | Target Table | Frequency | Schedule |
|------|--------------|--------------|-----------|----------|
| **Scheme Master** | `eligibility.scheme_master` | `schemes` | Daily | 00:00 UTC |
| **Profile Summary** | `public.profile_360` | `profile_summary` | Daily | 00:30 UTC |
| **Golden Records** | `public.golden_records` | `profile_data` | Daily | 01:00 UTC |

### Event-Driven Syncs (Real-time)

| Data | Source Table | Target Table | Latency | Volume/Day |
|------|--------------|--------------|---------|------------|
| **Eligibility Hints** | `eligibility.eligibility_snapshots` | `eligibility_hints` | < 5s | ~10K |
| **Forecast Data** | `forecast.benefit_forecasts` | `benefit_forecasts` | < 2s | ~50K |
| **Decision Updates** | `decision.applications` | `application_decisions` | < 5s | ~10K |
| **ML Alerts** | Various | `ml_alerts` | < 5s | ~20K |

### Hybrid Syncs

| Data | Source Table | Target Table | Pattern |
|------|--------------|--------------|---------|
| **Profile Summary** | `public.profile_360` | `profile_summary` | Event (primary) + Hourly Batch (backup) |

---

## Direction 2: smart_citizen → smart_warehouse

### Event-Driven Syncs (Real-time)

| Data | Source Table | Target Table | Latency | Volume/Day |
|------|--------------|--------------|---------|------------|
| **Profile Updates** | `citizens` | `public.golden_records` | < 5s | ~20K |
| **Application Submissions** | `service_applications` | `decision.application_events` | < 5s | ~5K |
| **Document Metadata** | `documents` | `document_metadata` | < 5s | ~15K |

### Batch Syncs

| Data | Source Table | Target Table | Frequency | Schedule |
|------|--------------|--------------|-----------|----------|
| **User Behavior** | Various | `analytics.user_behavior` | Daily | 02:00 UTC |
| **Feedback** | `feedback` | `feedback_analytics` | Daily | 02:30 UTC |

---

## Sync Patterns Quick Reference

### Pattern Selection Guide

**Use Batch When:**
- ✅ Master/reference data (changes infrequently)
- ✅ Large volume, non-critical timing
- ✅ Analytics/aggregated data
- ✅ Cost optimization needed

**Use Event-Driven When:**
- ✅ User-facing data (needs immediate visibility)
- ✅ Critical workflows (triggers important processes)
- ✅ Low latency required (< 5 seconds)
- ✅ Low volume, high frequency updates

**Use Hybrid When:**
- ✅ Need real-time updates + data consistency guarantee
- ✅ Critical data with high reliability requirements

---

## Schedule Summary

### Daily Batch Jobs (UTC)

| Time | Job | Duration | Impact |
|------|-----|----------|--------|
| 00:00 | Scheme Master Sync | 5 min | Low |
| 00:30 | Profile Summary Full Sync | 30 min | Medium |
| 01:00 | Golden Records Full Sync | 45 min | Medium |
| 02:00 | User Behavior Sync | 15 min | Low |
| 02:30 | Feedback Sync | 5 min | Low |

### Hourly Batch Jobs (UTC)

| Schedule | Job | Duration |
|----------|-----|----------|
| Every :00 | Profile Summary Incremental | 10 min |

### Event-Driven (Continuous)

- Eligibility Hints (real-time)
- Decision Updates (real-time)
- Forecast Data (on-demand)
- ML Alerts (real-time)
- Profile Updates (real-time)
- Application Submissions (real-time)
- Document Metadata (real-time)

---

## Data Masking Summary

### Full Masking
- Income bands → "CONFIDENTIAL"
- Full Aadhaar (if required) → "***MASKED***"

### Partial Masking
- Jan Aadhaar → "****-****-1234" (last 4 digits)
- Mobile → "******5678" (last 4 digits)
- Email → "u***@example.com" (first char + domain)

### No Masking
- Eligibility scores
- Scheme codes
- District IDs
- Aggregated vulnerability levels

**For details, see**: [CDC_DATA_MASKING_STRATEGY.md](./CDC_DATA_MASKING_STRATEGY.md)

---

## Technology Stack

- **Batch**: Apache Airflow + Python/Java
- **Event-Driven**: Debezium + Apache Kafka + Java/Spring Consumers
- **Monitoring**: Prometheus + Grafana
- **Alerting**: Slack/Email

---

## Key Metrics

### Performance Targets

- **Event-Driven Latency**: < 5 seconds (95th percentile)
- **Batch Job Duration**: Within estimates (see schedules)
- **Consumer Lag**: < 60 seconds
- **Sync Success Rate**: > 99%

### Data Volume Estimates

- **Total Event-Driven**: ~100K events/day
- **Total Batch**: ~600K records/day (various tables)
- **Peak Hour Events**: ~10K events/hour

---

**For detailed information, refer to:**
- [DATA_INTEGRATION_STRATEGY.md](./DATA_INTEGRATION_STRATEGY.md) - Overall strategy
- [DATA_FLOW_SPECIFICATION.md](./DATA_FLOW_SPECIFICATION.md) - Detailed specifications
- [BATCH_VS_EVENT_SYNC_PLAN.md](./BATCH_VS_EVENT_SYNC_PLAN.md) - Sync pattern details
- [DATA_FREQUENCY_SCHEDULE.md](./DATA_FREQUENCY_SCHEDULE.md) - Schedule details

