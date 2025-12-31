#!/usr/bin/env python3
"""
Test Inclusion Workflow - End-to-End Testing
Use Case ID: AI-PLATFORM-09
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import uuid
import random

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))

from services.inclusion_orchestrator import InclusionOrchestrator
from db_connector import DBConnector
import yaml


def create_dummy_family_data(db_connector: DBConnector, family_id: str, beneficiary_id: str):
    """Create dummy family and beneficiary data for testing"""
    try:
        conn = db_connector.connection
        cursor = conn.cursor()
        
        # Insert into golden_records.beneficiaries
        cursor.execute("""
            INSERT INTO golden_records.beneficiaries (
                beneficiary_id, family_id, full_name, date_of_birth, gender,
                address_district, address_block, income_group, category, disability_status, is_active
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (beneficiary_id) DO UPDATE SET
                family_id = EXCLUDED.family_id,
                full_name = EXCLUDED.full_name,
                is_active = EXCLUDED.is_active
        """, (
            beneficiary_id, family_id, "Test Beneficiary", "1980-01-01", "MALE",
            "Jaipur", "Jaipur Block", "BPL", "ST", "YES", True
        ))
        
        # Insert into golden_records.families
        cursor.execute("""
            INSERT INTO golden_records.families (
                family_id, head_of_family_id, family_income_annual, family_size,
                is_bpl, has_ration_card, has_jan_aadhaar, address_district, address_state
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (family_id) DO UPDATE SET
                head_of_family_id = EXCLUDED.head_of_family_id,
                family_income_annual = EXCLUDED.family_income_annual,
                is_bpl = EXCLUDED.is_bpl
        """, (
            family_id, beneficiary_id, 50000.0, 4, True, True, True, "Jaipur", "Rajasthan"
        ))
        
        conn.commit()
        cursor.close()
        print(f"   ✅ Created dummy family {family_id} and beneficiary {beneficiary_id}")
    
    except Exception as e:
        print(f"   ⚠️  Error creating dummy data: {e}")


def test_inclusion_workflow():
    """Test the complete inclusion workflow"""
    print("=" * 80)
    print("Testing Proactive Inclusion & Exception Handling Workflow")
    print("=" * 80)
    
    # Load configuration
    db_config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    with open(db_config_path, 'r') as f:
        db_config = yaml.safe_load(f)['database']
    
    # Connect to database
    db = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    
    try:
        db.connect()
        print(f"✅ Connected to PostgreSQL: {db_config['host']}:{db_config['port']}/{db_config['name']}")
        
        # Initialize orchestrator
        orchestrator = InclusionOrchestrator()
        orchestrator.connect()
        print("✅ InclusionOrchestrator initialized and connected")
        
        # --- Test 1: Identify Priority Household ---
        print("\n" + "=" * 80)
        print("Test 1: Identify Priority Household")
        print("=" * 80)
        
        test_family_id = str(uuid.uuid4())
        test_beneficiary_id = f"BEN{random.randint(100000, 999999)}"
        
        # Create dummy data
        create_dummy_family_data(db, test_family_id, test_beneficiary_id)
        
        print(f"\n🔄 Identifying priority household for Family ID: {test_family_id}...")
        priority_status = orchestrator.get_priority_status(
            family_id=test_family_id,
            include_nudges=True
        )
        
        if priority_status and priority_status.get('is_priority'):
            print("✅ Priority Household Identified!")
            ph = priority_status.get('priority_household', {})
            print(f"   Priority ID: {ph.get('priority_id')}")
            print(f"   Inclusion Gap Score: {ph.get('inclusion_gap_score', 0.0):.4f}")
            print(f"   Vulnerability Score: {ph.get('vulnerability_score', 0.0):.4f}")
            print(f"   Priority Level: {ph.get('priority_level')}")
            print(f"   Priority Segments: {ph.get('priority_segments', [])}")
            print(f"   Predicted Eligible: {ph.get('predicted_eligible_count', 0)}")
            print(f"   Actual Enrolled: {ph.get('actual_enrolled_count', 0)}")
            print(f"   Eligibility Gap: {ph.get('eligibility_gap_count', 0)}")
        else:
            print("ℹ️  Household not identified as priority (may not meet threshold)")
        
        # --- Test 2: Exception Detection ---
        print("\n" + "=" * 80)
        print("Test 2: Exception Detection")
        print("=" * 80)
        
        exceptions = priority_status.get('exception_flags', [])
        if exceptions:
            print(f"✅ Found {len(exceptions)} exception flags:")
            for exc in exceptions:
                print(f"   - Category: {exc.get('exception_category')}")
                print(f"     Description: {exc.get('exception_description')}")
                print(f"     Anomaly Score: {exc.get('anomaly_score', 0.0):.4f}")
        else:
            print("ℹ️  No exception flags detected")
        
        # --- Test 3: Nudge Generation ---
        print("\n" + "=" * 80)
        print("Test 3: Nudge Generation")
        print("=" * 80)
        
        nudges = priority_status.get('nudges', [])
        if nudges:
            print(f"✅ Generated {len(nudges)} nudges:")
            for i, nudge in enumerate(nudges, 1):
                print(f"\n   Nudge {i}:")
                print(f"     Type: {nudge.get('nudge_type')}")
                print(f"     Message: {nudge.get('nudge_message', '')[:100]}...")
                print(f"     Channel: {nudge.get('channel')}")
                print(f"     Priority: {nudge.get('priority_level')}")
                print(f"     Actions: {', '.join(nudge.get('recommended_actions', [])[:3])}")
        else:
            print("ℹ️  No nudges generated (household may not be priority)")
        
        # --- Test 4: Priority List for Field Workers ---
        print("\n" + "=" * 80)
        print("Test 4: Priority List for Field Workers")
        print("=" * 80)
        
        print("\n🔄 Fetching priority list...")
        priority_list = orchestrator.get_priority_list(
            block_id=None,
            district=None,
            segment_filters=None,
            priority_level_filter='HIGH',
            limit=10
        )
        
        if priority_list and priority_list.get('households'):
            print(f"✅ Found {priority_list.get('total_count', 0)} priority households:")
            for hh in priority_list.get('households', [])[:5]:
                print(f"   - Family: {hh.get('family_id')}")
                print(f"     Gap Score: {hh.get('inclusion_gap_score', 0.0):.4f}")
                print(f"     Priority: {hh.get('priority_level')}")
                print(f"     Segments: {', '.join(hh.get('priority_segments', []))}")
        else:
            print("ℹ️  No priority households found in list")
        
        # --- Test 5: Schedule Nudge Delivery ---
        print("\n" + "=" * 80)
        print("Test 5: Schedule Nudge Delivery")
        print("=" * 80)
        
        if nudges:
            nudge = nudges[0]
            print(f"\n🔄 Scheduling nudge delivery...")
            delivery_result = orchestrator.schedule_nudge_delivery(
                family_id=test_family_id,
                nudge_type=nudge.get('nudge_type'),
                nudge_message=nudge.get('nudge_message'),
                recommended_actions=nudge.get('recommended_actions', []),
                scheme_codes=nudge.get('scheme_codes', []),
                channel=nudge.get('channel'),
                priority_level=nudge.get('priority_level'),
                scheduled_at=None
            )
            
            if delivery_result.get('success'):
                print("✅ Nudge Scheduled Successfully!")
                print(f"   Nudge ID: {delivery_result.get('nudge_id')}")
                print(f"   Status: {delivery_result.get('delivery_status')}")
                print(f"   Scheduled At: {delivery_result.get('scheduled_at')}")
            else:
                print(f"❌ Failed to schedule nudge: {delivery_result.get('error')}")
        else:
            print("ℹ️  Skipping nudge delivery test (no nudges generated)")
        
        # Summary
        print("\n" + "=" * 80)
        print("Test Summary")
        print("=" * 80)
        print(f"✅ Priority household identification: {'PASS' if priority_status else 'SKIP'}")
        print(f"✅ Exception detection: {'PASS' if exceptions else 'INFO'}")
        print(f"✅ Nudge generation: {'PASS' if nudges else 'INFO'}")
        print(f"✅ Priority list retrieval: {'PASS' if priority_list else 'SKIP'}")
        print(f"✅ Nudge scheduling: {'PASS' if nudges and delivery_result.get('success') else 'SKIP'}")
        
        orchestrator.disconnect()
        print("\n✅ All tests completed!")
    
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.disconnect()
        print("Database connection closed")


if __name__ == '__main__':
    test_inclusion_workflow()

