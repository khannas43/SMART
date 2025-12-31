# Testing Guide: Auto Intimation & Smart Consent Triggering

**Use Case ID:** AI-PLATFORM-04

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Database Setup](#database-setup)
3. [Testing Workflow](#testing-workflow)
4. [Test Scenarios](#test-scenarios)
5. [Expected Results](#expected-results)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### 1. Environment Setup

```bash
# Activate virtual environment
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate

# Navigate to use case directory
cd /mnt/c/Projects/SMART/ai-ml/use-cases/04_intimation_smart_consent_triggering

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Prerequisites

Ensure the following exist:
- ✅ `smart_warehouse` database exists
- ✅ `eligibility` schema exists (from AI-PLATFORM-03)
- ✅ `public.scheme_master` table exists with scheme data
- ✅ `eligibility.eligibility_snapshots` table has eligible candidates
- ✅ `golden_record.families` table has contact information

### 3. Required Data

**Minimum test data needed:**
- At least 1 scheme in `public.scheme_master` (e.g., `CHIRANJEEVI`)
- At least 10 eligible candidates in `eligibility.eligibility_snapshots` with:
  - `evaluation_status = 'POTENTIALLY_ELIGIBLE_IDENTIFIED'`
  - `eligibility_score >= 0.6`
- Contact information in `golden_record.families`:
  - `primary_mobile` or `email` for at least 5 families

---

## Database Setup

### Step 1: Create Database Schema

**Option A: Using Setup Script (Recommended)**
```bash
# From WSL/Ubuntu terminal
cd /mnt/c/Projects/SMART/ai-ml/use-cases/04_intimation_smart_consent_triggering
chmod +x scripts/setup_database.sh
./scripts/setup_database.sh
```

**Option B: Manual Setup (PgAdmin or psql)**
```bash
# Connect to database
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse

# Run schema script
\i database/intimation_schema.sql

# Verify schema
\dn intimation
\dt intimation.*
```

**Option C: Using Python Script**
```python
# Create scripts/run_schema_setup.py if needed
import subprocess
subprocess.run([
    'psql', '-h', '172.17.16.1', '-p', '5432', 
    '-U', 'sameer', '-d', 'smart_warehouse',
    '-f', 'database/intimation_schema.sql'
])
```

### Step 2: Verify Schema Creation

```bash
# Check schema exists
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -c "\dn intimation"

# List all tables
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -c "\dt intimation.*"

# Check table counts
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -c "
SELECT 
    schemaname, 
    tablename, 
    n_tup_ins as row_count
FROM pg_stat_user_tables 
WHERE schemaname = 'intimation'
ORDER BY tablename;
"
```

**Expected Output:**
```
         schemaname        |         tablename          | row_count
---------------------------+----------------------------+-----------
 intimation                | campaigns                  |         0
 intimation                | campaign_candidates        |         0
 intimation                | consent_records            |         0
 intimation                | consent_history            |         0
 intimation                | intimation_events          |         0
 intimation                | message_fatigue            |         0
 intimation                | message_logs               |         0
 intimation                | message_templates          |         0
 intimation                | scheme_intimation_config   |         0
 intimation                | user_preferences           |         0
```

### Step 3: Initialize Message Templates

```bash
python scripts/init_message_templates.py
```

**Expected Output:**
```
================================================================================
Initializing Message Templates
================================================================================
  ✅ Created: SMS_INTIMATION_HI
  ✅ Created: SMS_INTIMATION_EN
  ✅ Created: APP_INTIMATION_HI
  ✅ Created: EMAIL_INTIMATION_HI

================================================================================
✅ Template initialization complete!
   Created: 4
   Skipped: 0
   Total: 4
================================================================================
```

### Step 4: Configure Scheme Intimation Settings

```bash
# Create scripts/init_scheme_config.py (see below)
python scripts/init_scheme_config.py
```

---

## Testing Workflow

### Phase 1: Configuration Validation

**Test 1: Validate Configuration**
```bash
python scripts/check_config.py
```

**Expected Result:**
- ✅ All database connections successful
- ✅ Schema exists
- ✅ Configuration files loaded correctly

### Phase 2: Intake Process Testing

**Test 2: Test Intake Process**
```bash
python scripts/test_intake.py
```

**What it does:**
1. Queries `eligibility.eligibility_snapshots` for eligible candidates
2. Applies campaign policies (thresholds, fatigue limits)
3. Creates campaign records
4. Schedules candidate sends

**Expected Result:**
```
================================================================================
Testing Intake Process
================================================================================

📋 Running intake for scheme: CHIRANJEEVI

✅ Created 1 campaign(s):
   - Campaign ID: 1
     Name: CHIRANJEEVI_INITIAL_20241229_190000
     Scheme: CHIRANJEEVI
     Candidates: 25
     Status: scheduled

================================================================================
✅ Intake test complete!
================================================================================
```

**Verify in Database:**
```sql
-- Check campaign created
SELECT campaign_id, campaign_name, scheme_code, total_candidates, status
FROM intimation.campaigns;

-- Check candidates created
SELECT candidate_id, family_id, scheme_code, eligibility_score, status
FROM intimation.campaign_candidates
WHERE campaign_id = 1
LIMIT 10;
```

### Phase 3: Message Personalization Testing

**Test 3: Test Message Personalization**
```bash
python scripts/test_message_personalization.py
```

**What it does:**
1. Loads a candidate from campaign
2. Loads scheme information
3. Generates personalized message for different channels
4. Validates template rendering

### Phase 4: Consent Management Testing

**Test 4: Test Consent Creation**
```bash
python scripts/test_consent.py
```

**Expected Result:**
```
================================================================================
Testing Consent Management
================================================================================

📋 Creating consent...
   Family ID: <uuid>
   Scheme: CHIRANJEEVI

✅ Consent created:
   Consent ID: 1
   Status: given
   Type: soft
   LOA: LOA1

📋 Retrieving consent status...

✅ Consent status found:
   Status: given
   Valid until: 2025-12-29 00:00:00

================================================================================
✅ Consent test complete!
================================================================================
```

**Verify in Database:**
```sql
-- Check consent record
SELECT consent_id, family_id, scheme_code, consent_type, status, valid_until
FROM intimation.consent_records;

-- Check consent history
SELECT history_id, consent_id, action, old_status, new_status, changed_at
FROM intimation.consent_history
ORDER BY changed_at DESC
LIMIT 10;
```

### Phase 5: End-to-End Testing

**Test 5: End-to-End Flow**
```bash
python scripts/test_end_to_end.py --scheme-code CHIRANJEEVI --limit 10
```

**What it does:**
1. Runs intake process
2. Creates campaign
3. Generates personalized messages (simulated)
4. Creates consent records
5. Verifies complete flow

---

## Test Scenarios

### Scenario 1: Campaign Intake

**Setup:**
- Ensure eligibility snapshots exist with `POTENTIALLY_ELIGIBLE_IDENTIFIED`
- Minimum 5 eligible candidates for a scheme

**Test:**
```python
from src.intimation_service import IntimationService

service = IntimationService()
campaigns = service.run_intake_process(scheme_code='CHIRANJEEVI')

assert len(campaigns) > 0
assert campaigns[0].total_candidates > 0
```

**Verify:**
```sql
SELECT COUNT(*) FROM intimation.campaign_candidates
WHERE campaign_id = <campaign_id>;
```

### Scenario 2: Fatigue Limit Enforcement

**Setup:**
- Create message fatigue record with count = 10 (max limit)

**Test:**
```python
from src.campaign_manager import CampaignManager

manager = CampaignManager()
candidates = manager.intake_eligibility_signals(scheme_code='CHIRANJEEVI')
filtered = manager.apply_campaign_policies(candidates, 'CHIRANJEEVI')

# Should exclude candidates from families that exceeded limit
assert len(filtered) <= len(candidates)
```

### Scenario 3: Soft Consent Flow

**Test:**
```python
from src.consent_manager import ConsentManager

manager = ConsentManager()
consent = manager.create_consent(
    family_id='<family_uuid>',
    scheme_code='CHIRANJEEVI',
    consent_value=True,
    consent_method='click',
    channel='mobile_app'
)

assert consent['consent_type'] == 'soft'
assert consent['level_of_assurance'] == 'LOA1'
assert consent['status'] == 'given'
```

### Scenario 4: Strong Consent with OTP

**Test:**
```python
from src.consent_manager import ConsentManager

manager = ConsentManager()
consent = manager.create_consent(
    family_id='<family_uuid>',
    scheme_code='OLD_AGE_PENSION',  # High-risk scheme
    consent_value=True,
    consent_method='click',
    channel='mobile_app'
)

# Should require OTP verification
assert consent['consent_type'] == 'strong'
assert consent['level_of_assurance'] == 'LOA2'
assert consent['status'] == 'pending'

# Verify OTP
verified = manager.verify_otp(consent['consent_id'], '123456')
assert verified == True

# Check status updated
updated_consent = manager.get_consent(consent['consent_id'])
assert updated_consent['status'] == 'given'
```

### Scenario 5: Retry Scheduling

**Test:**
```python
from src.smart_orchestrator import SmartOrchestrator

orchestrator = SmartOrchestrator()
retries_scheduled = orchestrator.schedule_retries(campaign_id=1)

assert retries_scheduled > 0

# Verify retries scheduled
# Check campaign_candidates table for next_retry_at
```

---

## Database Verification Queries

### 1. Verify Campaign Creation

```sql
-- Check campaigns
SELECT 
    campaign_id,
    campaign_name,
    scheme_code,
    status,
    total_candidates,
    scheduled_at
FROM intimation.campaigns
ORDER BY created_at DESC
LIMIT 5;
```

### 2. Verify Candidates

```sql
-- Check candidates with eligibility context
SELECT 
    cc.candidate_id,
    cc.family_id,
    cc.scheme_code,
    cc.eligibility_score,
    cc.priority_score,
    cc.status,
    cc.scheduled_send_at
FROM intimation.campaign_candidates cc
WHERE cc.campaign_id = 1
ORDER BY cc.priority_score DESC
LIMIT 10;
```

### 3. Verify Message Logs

```sql
-- Check message delivery logs
SELECT 
    message_id,
    channel,
    status,
    sent_at,
    delivered_at,
    error_message
FROM intimation.message_logs
ORDER BY sent_at DESC
LIMIT 10;
```

### 4. Verify Consent Records

```sql
-- Check consent records
SELECT 
    consent_id,
    family_id,
    scheme_code,
    consent_type,
    status,
    valid_until,
    created_at
FROM intimation.consent_records
ORDER BY created_at DESC
LIMIT 10;
```

### 5. Verify Consent History (Audit Trail)

```sql
-- Check consent history
SELECT 
    history_id,
    consent_id,
    action,
    old_status,
    new_status,
    changed_at
FROM intimation.consent_history
ORDER BY changed_at DESC
LIMIT 10;
```

### 6. Verify Events

```sql
-- Check intimation events
SELECT 
    event_type,
    event_category,
    family_id,
    scheme_code,
    event_timestamp
FROM intimation.intimation_events
ORDER BY event_timestamp DESC
LIMIT 20;
```

---

## Complete Test Script

Create `scripts/test_complete.py`:

```python
"""
Complete End-to-End Test
Tests all components in sequence
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from intimation_service import IntimationService
from consent_manager import ConsentManager
from smart_orchestrator import SmartOrchestrator
import uuid

def test_complete():
    """Complete end-to-end test"""
    print("=" * 80)
    print("Complete End-to-End Test")
    print("=" * 80)
    
    service = IntimationService()
    
    try:
        # Step 1: Intake Process
        print("\n1️⃣ Testing Intake Process...")
        campaigns = service.run_intake_process(scheme_code='CHIRANJEEVI')
        assert len(campaigns) > 0, "No campaigns created"
        campaign = campaigns[0]
        print(f"   ✅ Campaign created: {campaign.campaign_id}")
        
        # Step 2: Get candidate for testing
        print("\n2️⃣ Getting test candidate...")
        from src.campaign_manager import CampaignManager
        manager = CampaignManager()
        manager.db.connect()
        cursor = manager.db.connection.cursor()
        cursor.execute("""
            SELECT family_id, scheme_code 
            FROM intimation.campaign_candidates 
            WHERE campaign_id = %s 
            LIMIT 1
        """, (campaign.campaign_id,))
        candidate = cursor.fetchone()
        cursor.close()
        
        if candidate:
            family_id, scheme_code = candidate
            print(f"   ✅ Test candidate: {family_id} for {scheme_code}")
            
            # Step 3: Create consent
            print("\n3️⃣ Testing Consent Creation...")
            consent = service.process_consent_response(
                family_id=family_id,
                scheme_code=scheme_code,
                consent_value=True,
                consent_method='click',
                channel='mobile_app'
            )
            print(f"   ✅ Consent created: {consent.get('consent_id')}")
            
            # Step 4: Verify consent status
            print("\n4️⃣ Verifying Consent Status...")
            consent_manager = ConsentManager()
            status = consent_manager.get_consent_status(family_id, scheme_code)
            assert status is not None, "Consent status not found"
            print(f"   ✅ Consent status: {status.get('status')}")
            consent_manager.disconnect()
            
        # Step 5: Test retry scheduling
        print("\n5️⃣ Testing Retry Scheduling...")
        orchestrator = SmartOrchestrator()
        retries = orchestrator.schedule_retries()
        print(f"   ✅ Retries scheduled: {retries}")
        orchestrator.disconnect()
        
        print("\n" + "=" * 80)
        print("✅ All tests passed!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        service.disconnect()

if __name__ == '__main__':
    test_complete()
```

---

## Troubleshooting

### Issue: Schema Creation Fails

**Error:** `ERROR: permission denied for schema intimation`

**Solution:**
```sql
-- Run as postgres superuser
psql -h 172.17.16.1 -p 5432 -U postgres -d smart_warehouse

-- Grant permissions
GRANT USAGE ON SCHEMA intimation TO sameer;
GRANT CREATE ON SCHEMA intimation TO sameer;
ALTER SCHEMA intimation OWNER TO sameer;
```

### Issue: No Eligible Candidates Found

**Error:** `No campaigns created (no eligible candidates found)`

**Solution:**
```sql
-- Check eligibility snapshots
SELECT COUNT(*) 
FROM eligibility.eligibility_snapshots 
WHERE evaluation_status = 'POTENTIALLY_ELIGIBLE_IDENTIFIED'
AND scheme_code = 'CHIRANJEEVI'
AND eligibility_score >= 0.6;

-- If empty, create test data or run AI-PLATFORM-03 evaluation
```

### Issue: Contact Information Missing

**Error:** `Could not load contact info for {family_id}`

**Solution:**
```sql
-- Verify contact info exists
SELECT family_id, primary_mobile, email
FROM golden_record.families
WHERE family_id IN (
    SELECT DISTINCT family_id 
    FROM eligibility.eligibility_snapshots
    WHERE evaluation_status = 'POTENTIALLY_ELIGIBLE_IDENTIFIED'
)
LIMIT 10;
```

### Issue: Template Not Found

**Error:** `No template found for {channel}/{language}/{type}`

**Solution:**
```bash
# Re-initialize templates
python scripts/init_message_templates.py

# Verify templates
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -c "
SELECT template_code, channel, language, status 
FROM intimation.message_templates;
"
```

---

## Test Data Preparation

### Create Test Eligibility Snapshots

```sql
-- Insert test eligibility snapshots
INSERT INTO eligibility.eligibility_snapshots (
    family_id, scheme_code, evaluation_status,
    eligibility_score, priority_score, 
    rule_eligible, evaluation_timestamp
)
SELECT 
    f.family_id,
    'CHIRANJEEVI',
    'POTENTIALLY_ELIGIBLE_IDENTIFIED',
    0.75,
    0.80,
    true,
    CURRENT_TIMESTAMP
FROM golden_record.families f
WHERE f.primary_mobile IS NOT NULL
LIMIT 20;
```

### Create Scheme Intimation Config

```sql
-- Insert scheme configuration
INSERT INTO intimation.scheme_intimation_config (
    scheme_code, auto_intimation_enabled,
    min_eligibility_score, priority_threshold,
    consent_type_required, max_intimations_per_family
)
VALUES (
    'CHIRANJEEVI',
    true,
    0.6,
    0.8,
    'soft',
    3
)
ON CONFLICT (scheme_code) DO UPDATE SET
    auto_intimation_enabled = true,
    min_eligibility_score = 0.6;
```

---

## Quick Test Checklist

- [ ] Database schema created
- [ ] Message templates initialized
- [ ] Configuration validated
- [ ] Test data prepared (eligibility snapshots)
- [ ] Intake process tested
- [ ] Message personalization tested
- [ ] Consent creation tested
- [ ] Consent status retrieval tested
- [ ] Retry scheduling tested
- [ ] End-to-end flow tested

---

**Last Updated**: 2024-12-29  
**Status**: Ready for Testing

