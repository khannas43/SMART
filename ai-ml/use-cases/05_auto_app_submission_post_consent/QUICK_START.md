# Quick Start Guide: Auto Application Submission Post-Consent

**Use Case ID:** AI-PLATFORM-05

## Prerequisites

1. **Install Python Dependencies**:
   ```bash
   cd /mnt/c/Projects/SMART/ai-ml/use-cases/05_auto_app_submission_post_consent
   source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Upstream Use Cases Completed**:
   - AI-PLATFORM-03: Eligibility snapshots created
   - AI-PLATFORM-04: Consent records created

3. **Database Setup**:
   ```bash
   cd /mnt/c/Projects/SMART/ai-ml/use-cases/05_auto_app_submission_post_consent
   ./scripts/setup_database.sh
   psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f scripts/fix_schema.sql
   python scripts/init_scheme_form_schemas.py
   python scripts/init_submission_modes_config.py
   ```

## Quick Test

### 1. Verify Setup

```bash
python scripts/check_config.py
```

### 2. Create Test Consent Records (If Needed)

If you don't have consent records from AI-PLATFORM-04, create test ones:

```bash
python scripts/create_test_consent.py
```

### 3. Test Application Creation

```bash
python scripts/test_application_creation.py
```

This will:
- Find a consent record
- Trigger application creation
- Create application record

### 4. Test Form Mapping

```bash
python scripts/test_form_mapping.py
```

This will:
- Load application
- Map fields from GR/360°
- Store mapped fields

### 5. Test Validation

```bash
python scripts/test_validation.py
```

This will:
- Validate application
- Check for errors/warnings
- Update status

### 6. End-to-End Test

```bash
python scripts/test_end_to_end.py
```

This tests the complete workflow from consent to submission.

## Expected Results

After running all tests, you should see:
- ✅ Applications created in database
- ✅ Fields mapped with source tracking
- ✅ Validation results stored
- ✅ Applications ready for submission (auto/review/assisted)

## Next Steps

1. Configure department connectors with actual API endpoints
2. Customize form schemas per scheme
3. Set up field mapping rules
4. Test with real department APIs

---

**For detailed information, see [TESTING_GUIDE.md](TESTING_GUIDE.md)**

