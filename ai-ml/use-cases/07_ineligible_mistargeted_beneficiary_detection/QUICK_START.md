# Quick Start Guide - AI-PLATFORM-07

**Use Case ID:** AI-PLATFORM-07  
**Ineligible/Mistargeted Beneficiary Detection**

## Prerequisites

1. **Virtual Environment**: Ensure Python virtual environment is activated
   ```bash
   source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
   ```

2. **Database**: PostgreSQL should be running and accessible

## Setup Steps

### 1. Install Dependencies

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/07_ineligible_mistargeted_beneficiary_detection
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

### 4. Test the System

```bash
# Test detection workflow
python scripts/test_detection_workflow.py
```

## Running Detection

### Single Beneficiary Detection

```python
from services.detection_orchestrator import DetectionOrchestrator

orchestrator = DetectionOrchestrator()
orchestrator.connect()

result = orchestrator.detect_beneficiary(
    beneficiary_id="beneficiary-123",
    family_id="family-uuid",
    scheme_code="CHIRANJEEVI"
)

orchestrator.disconnect()
```

### Full Detection Run

```python
from services.detection_orchestrator import DetectionOrchestrator

orchestrator = DetectionOrchestrator()
orchestrator.connect()

result = orchestrator.run_detection(
    run_type="FULL",  # or "INCREMENTAL", "SCHEME_SPECIFIC"
    scheme_codes=["CHIRANJEEVI", "OLD_AGE_PENSION"],  # Optional
    beneficiary_ids=None,  # Optional: specific beneficiaries
    started_by="admin_user"
)

print(f"Run ID: {result['run_id']}")
print(f"Cases Flagged: {result['cases_flagged']}")

orchestrator.disconnect()
```

## API Endpoints

**Base URL:** `/detection`

### Key Endpoints

- `POST /detection/run` - Start detection run
- `GET /detection/runs` - List detection runs
- `GET /detection/cases` - List detected cases
- `GET /detection/case/{caseId}` - Get case details
- `POST /detection/case/{caseId}/verify` - Verify a case
- `GET /detection/worklist` - Get officer worklist
- `GET /detection/analytics` - Get leakage analytics

## Next Steps

1. Review detected cases in database
2. Assign cases to officers via worklist
3. Verify cases and take actions
4. Monitor analytics and metrics

---

**Last Updated:** 2024-12-30

