# Ineligible/Mistargeted Beneficiary Detection

**Use Case ID:** AI-PLATFORM-07  
**Version:** 1.0  
**Status:** 🚧 In Development

## Overview

The Ineligible/Mistargeted Beneficiary Detection system periodically re-scores existing beneficiaries across schemes to identify:
- **Ineligible cases**: Beneficiaries who no longer meet scheme rules (income crossed threshold, status changed, moved away, deceased)
- **Mistargeted/leakage cases**: Beneficiaries receiving multiple overlapping or mutually exclusive benefits, or exhibiting unusual benefit levels compared to peers

The system uses Golden Records, 360° Profiles, and cross-departmental datasets to support data-driven cleanup while safeguarding genuine beneficiaries and minimizing wrongful exclusions.

## Key Capabilities

1. **Rule-Based Mis-targeting Checks**
   - Eligibility re-checks with latest data
   - Overlap and duplication detection
   - Cross-scheme conflict checks
   - Status change detection (deceased, migrated, etc.)

2. **ML-Based Leakage & Anomaly Detection**
   - Isolation Forest and Autoencoder models for anomaly detection
   - Supervised fraud models (where available)
   - Behavioral pattern analysis
   - Cluster-level outlier detection

3. **Periodic Re-scoring & Prioritization**
   - Full re-scoring runs (monthly/quarterly)
   - Incremental runs on major data changes
   - Risk-based prioritization
   - Financial exposure and vulnerability considerations

4. **Case Classification**
   - **HARD_INELIGIBLE**: High confidence rule failures
   - **LIKELY_MIS_TARGETED**: Overlapping benefits or unusual patterns
   - **LOW_CONFIDENCE_FLAG**: Anomalies for analytics/sample audits

5. **Worklists & Dashboards**
   - Departmental portal worklists
   - Admin/planning dashboards
   - Leakage analytics and savings tracking

6. **Governance & Safeguards**
   - No automatic benefit stoppage (requires human approval)
   - Right to appeal mechanisms
   - Fairness monitoring and bias detection
   - Comprehensive audit trails

## Quick Start

### 1. Setup Environment

```bash
# Activate virtual environment
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate

# Navigate to use case directory
cd /mnt/c/Projects/SMART/ai-ml/use-cases/07_ineligible_mistargeted_beneficiary_detection

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Create detection schema and tables
./scripts/setup_database.sh

# Initialize detection configuration
python scripts/init_detection_config.py

# Initialize scheme exclusion rules
python scripts/init_exclusion_rules.py
```

### 3. Verify Setup

```bash
# Check database connectivity and configuration
python scripts/check_config.py
```

## Architecture

```
Periodic Trigger / Data Change Event
    ↓
Detection Orchestrator
    ├── Rule-Based Detector → Eligibility, Overlap, Duplicate Checks
    ├── ML Anomaly Detector → Isolation Forest, Autoencoder, Supervised Models
    └── Case Classifier → HARD_INELIGIBLE, LIKELY_MIS_TARGETED, LOW_CONFIDENCE_FLAG
    ↓
Case Prioritization & Worklist Assignment
    ↓
Departmental Worklists / Admin Dashboards
    ↓
Verification → Human Review → Action (if confirmed)
```

## Components

1. **Detection Orchestrator** (`src/services/detection_orchestrator.py`)
   - Main orchestrator for detection runs
   - Coordinates rule-based and ML detection
   - Handles periodic and incremental runs

2. **Rule-Based Detector** (`src/detectors/rule_detector.py`)
   - Eligibility re-checks
   - Overlap and duplication detection
   - Status change checks
   - Cross-scheme conflict detection

3. **ML Anomaly Detector** (`src/models/anomaly_detector.py`)
   - Isolation Forest for anomaly detection
   - Autoencoder for deep learning anomalies
   - Supervised fraud models
   - Feature engineering and explainability

4. **Case Classifier** (`src/detectors/case_classifier.py`)
   - Classification logic (HARD_INELIGIBLE, etc.)
   - Confidence level assignment
   - Action recommendations

5. **Prioritizer** (`src/services/prioritizer.py`)
   - Risk-based prioritization
   - Financial exposure calculation
   - Vulnerability scoring
   - Worklist assignment

6. **Worklist Manager** (`src/services/worklist_manager.py`)
   - Worklist creation and assignment
   - Officer workload management
   - Status tracking

## Data Sources

- Current beneficiary rosters (all schemes)
- Golden Records (AI-PLATFORM-01)
- 360° Profiles (AI-PLATFORM-02)
- Eligibility snapshots (AI-PLATFORM-03)
- Cross-departmental data (income tax, land records, employment, etc.)
- Historical fraud/irregularity cases

## Database Schema

**Schema:** `detection` (in `smart_warehouse` database)

**Key Tables:**
- `detection_runs` - Periodic re-scoring runs
- `detected_cases` - Flagged beneficiaries
- `rule_detections` - Rule-based detection results
- `ml_detections` - ML anomaly detection results
- `eligibility_snapshots` - Eligibility state snapshots
- `worklist_assignments` - Officer worklist assignments
- `case_verification_history` - Verification and resolution history
- `scheme_exclusion_rules` - Cross-scheme exclusion matrix
- `detection_config` - Configuration and thresholds
- `leakage_analytics` - Aggregated metrics and analytics
- `detection_audit_logs` - Audit trail

## Technology Stack

- **Backend**: Spring Boot 3.x, Java 17+
- **Python Services**: Python 3.12+ for detection logic and ML models
- **ML Models**: Isolation Forest, Autoencoders, Supervised models (scikit-learn, TensorFlow)
- **Database**: PostgreSQL 14+ (`smart_warehouse.detection` schema)
- **Integration**: Golden Records, 360° Profiles, Eligibility Engine, Cross-departmental systems

## Governance & Safeguards

- **No Automatic Stoppage**: All benefit stoppages require human verification and approval
- **Right to Appeal**: Beneficiaries can appeal flagged cases
- **Fairness Monitoring**: Regular audits to detect bias
- **Transparency**: Clear explanations provided to beneficiaries
- **Auditability**: Comprehensive audit trails for all decisions

## Success Metrics

- **Leakage Reduction**: Number and value of confirmed ineligible beneficiaries removed
- **False Exclusion Control**: Rate of genuine beneficiaries wrongly flagged (< threshold)
- **Operational Performance**: Timeliness of re-scoring runs and case resolution
- **Savings Realized**: Budget saved through accurate detection

## Documentation

- **Quick Start**: See [QUICK_START.md](QUICK_START.md) (to be created)
- **Technical Design**: See [docs/TECHNICAL_DESIGN.md](docs/TECHNICAL_DESIGN.md) (to be created)
- **Testing Guide**: See [TESTING_GUIDE.md](TESTING_GUIDE.md) (to be created)

## Status

**Current Status**: ✅ **Core Implementation Complete**

- ✅ Database schema (11 tables)
- ✅ Configuration files
- ✅ Core services (Rule Detector, ML Detector, Classifier, Prioritizer, Orchestrator)
- ✅ Spring Boot REST APIs (10 endpoints, 7 DTOs)
- ✅ Python integration (PythonDetectionClient, DetectionService)
- ✅ Testing scripts (test_detection_workflow.py)
- ✅ Initialization scripts (init_detection_config.py, init_exclusion_rules.py, check_config.py)
- ✅ Documentation (README, QUICK_START, CORE_SERVICES_COMPLETE, SPRING_BOOT_APIS_COMPLETE)

---

**Last Updated**: 2024-12-30  
**Use Case Owner**: SMART Platform Team

