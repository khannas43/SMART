# Testing Summary & Next Steps

**Status**: ✅ Database Setup Complete!

## ✅ What's Done

1. ✅ Database schema created (10 tables)
2. ✅ Message templates initialized (4 templates)
3. ✅ Scheme configurations initialized (12 schemes)
4. ✅ All imports fixed

## 🧪 Next: Run Tests

### Test 1: Configuration Validation

```bash
python scripts/check_config.py
```

**Expected**: All database connections successful, config files loaded

---

### Test 2: Intake Process

```bash
python scripts/test_intake.py
```

**What it does:**
- Queries `eligibility.eligibility_snapshots` for eligible candidates
- Creates campaign with candidates
- Schedules sends

**Expected Output:**
```
✅ Created 1 campaign(s):
   - Campaign ID: <id>
     Name: CHIRANJEEVI_INITIAL_<timestamp>
     Scheme: CHIRANJEEVI
     Candidates: <number>
     Status: scheduled
```

**If No Campaigns Created:**
- Check if eligibility data exists:
```sql
SELECT COUNT(*) FROM eligibility.eligibility_snapshots 
WHERE evaluation_status = 'POTENTIALLY_ELIGIBLE_IDENTIFIED'
AND scheme_code = 'CHIRANJEEVI';
```

---

### Test 3: Message Personalization

```bash
python scripts/test_message_personalization.py
```

**What it does:**
- Tests template selection
- Tests message rendering for different channels
- Validates message formatting

**Expected**: Messages generated for SMS, App, Email

---

### Test 4: Consent Management

```bash
python scripts/test_consent.py
```

**What it does:**
- Creates test consent record
- Retrieves consent status
- Verifies audit trail

**Expected**: Consent created and retrieved successfully

---

### Test 5: End-to-End Flow

```bash
python scripts/test_end_to_end.py --scheme-code CHIRANJEEVI --limit 10
```

**What it does:**
- Complete flow: Intake → Campaign → Messages → Consent
- Validates entire workflow

**Expected**: All steps complete successfully

---

## 📊 Verify Results in Database

### Check Campaign Created

```sql
-- View campaigns
SELECT campaign_id, campaign_name, scheme_code, total_candidates, status
FROM intimation.campaigns
ORDER BY created_at DESC
LIMIT 5;
```

### Check Candidates

```sql
-- View candidates
SELECT candidate_id, family_id, scheme_code, eligibility_score, status
FROM intimation.campaign_candidates
WHERE campaign_id = <latest_campaign_id>
LIMIT 10;
```

### Check Consent Records

```sql
-- View consents
SELECT consent_id, family_id, scheme_code, consent_type, status
FROM intimation.consent_records
ORDER BY created_at DESC
LIMIT 10;
```

### Check Events

```sql
-- View events
SELECT event_type, family_id, scheme_code, event_timestamp
FROM intimation.intimation_events
ORDER BY event_timestamp DESC
LIMIT 20;
```

---

## 🐛 Troubleshooting

### Issue: No Eligible Candidates Found

**Check:**
```sql
-- Verify eligibility data exists
SELECT COUNT(*) 
FROM eligibility.eligibility_snapshots 
WHERE evaluation_status = 'POTENTIALLY_ELIGIBLE_IDENTIFIED'
AND eligibility_score >= 0.6;
```

**Solution:** Run AI-PLATFORM-03 evaluation first to generate eligibility snapshots

### Issue: Contact Information Missing

**Check:**
```sql
-- Verify contact info exists
SELECT family_id, primary_mobile, email
FROM golden_record.families
WHERE family_id IN (
    SELECT DISTINCT family_id 
    FROM eligibility.eligibility_snapshots
    LIMIT 10
);
```

**Solution:** Ensure Golden Records have contact information

### Issue: Import Errors

If you see import errors, verify:
```bash
# Check virtual environment
which python
# Should show: /mnt/c/Projects/SMART/ai-ml/.venv/bin/python

# Check path
ls ../../shared/utils/db_connector.py
# Should exist
```

---

## ✅ Success Criteria

After running all tests, you should have:

- ✅ At least 1 campaign created
- ✅ Multiple candidates in campaign_candidates table
- ✅ At least 1 consent record created
- ✅ Events logged in intimation_events table
- ✅ No errors in test execution

---

## 📝 Quick Test Sequence

```bash
# 1. Configuration check
python scripts/check_config.py

# 2. Database verification
python scripts/verify_database_setup.py

# 3. Test intake
python scripts/test_intake.py

# 4. Test message personalization
python scripts/test_message_personalization.py

# 5. Test consent
python scripts/test_consent.py

# 6. End-to-end test
python scripts/test_end_to_end.py --scheme-code CHIRANJEEVI --limit 10
```

---

**Ready to Test!** 🚀

Run the tests above and let me know the results!

