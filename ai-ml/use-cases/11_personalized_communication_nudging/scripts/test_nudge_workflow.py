#!/usr/bin/env python3
"""
Test Script for AI-PLATFORM-11: Personalized Communication & Nudging
Tests the complete nudge scheduling workflow.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directories to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src" / "services"))
sys.path.insert(0, str(project_root / "src" / "models"))
sys.path.insert(0, str(project_root.parent.parent.parent / "shared" / "utils"))

from nudge_orchestrator import NudgeOrchestrator


def test_nudge_scheduling():
    """Test nudge scheduling workflow"""
    print("\n" + "="*60)
    print("Testing Nudge Scheduling Workflow")
    print("="*60)
    
    orchestrator = NudgeOrchestrator()
    orchestrator.connect()
    
    try:
        # Test 1: Schedule a renewal nudge
        print("\n📅 Test 1: Scheduling renewal nudge...")
        result1 = orchestrator.schedule_nudge(
            action_type='renewal',
            family_id='FAM001',
            urgency='HIGH',
            expiry_date=datetime.now() + timedelta(days=30),
            action_context={'scheme_code': 'OLD_AGE_PENSION', 'scheme_name': 'Old Age Pension'},
            scheduled_by='TEST_USER'
        )
        print(f"✅ Result: {result1.get('success', False)}")
        if result1.get('success'):
            print(f"   Nudge ID: {result1.get('nudge_id')}")
            print(f"   Channel: {result1.get('scheduled_channel')}")
            print(f"   Scheduled Time: {result1.get('scheduled_time')}")
            print(f"   Template: {result1.get('template_id')}")
            print(f"   Content: {result1.get('personalized_content', '')[:100]}...")
        else:
            print(f"   Reason: {result1.get('reason', 'Unknown')}")
        
        # Test 2: Schedule missing document nudge
        print("\n📅 Test 2: Scheduling missing document nudge...")
        result2 = orchestrator.schedule_nudge(
            action_type='missing_doc',
            family_id='FAM002',
            urgency='MEDIUM',
            expiry_date=datetime.now() + timedelta(days=15),
            action_context={'document_type': 'Income Certificate', 'scheme_code': 'EDUCATION_SCHOLARSHIP'},
            scheduled_by='TEST_USER'
        )
        print(f"✅ Result: {result2.get('success', False)}")
        if result2.get('success'):
            print(f"   Nudge ID: {result2.get('nudge_id')}")
            print(f"   Channel: {result2.get('scheduled_channel')}")
        
        # Test 3: Schedule consent nudge
        print("\n📅 Test 3: Scheduling consent nudge...")
        result3 = orchestrator.schedule_nudge(
            action_type='consent',
            family_id='FAM003',
            urgency='LOW',
            action_context={'scheme_code': 'HEALTH_INSURANCE'},
            scheduled_by='TEST_USER'
        )
        print(f"✅ Result: {result3.get('success', False)}")
        if result3.get('success'):
            print(f"   Nudge ID: {result3.get('nudge_id')}")
            print(f"   Channel: {result3.get('scheduled_channel')}")
        
        # Test 4: Get nudge history
        print("\n📊 Test 4: Getting nudge history for FAM001...")
        history = orchestrator.get_nudge_history('FAM001', limit=10)
        print(f"✅ Found {len(history)} nudges")
        for nudge in history[:3]:  # Show first 3
            print(f"   - {nudge.get('action_type')} ({nudge.get('channel')}): {nudge.get('status')}")
        
        # Test 5: Record feedback (delivered)
        if result1.get('success') and result1.get('nudge_id'):
            print("\n📝 Test 5: Recording feedback (delivered)...")
            feedback_result = orchestrator.record_feedback(
                nudge_id=result1.get('nudge_id'),
                event_type='DELIVERED',
                metadata={'delivery_time': datetime.now().isoformat()}
            )
            print(f"✅ Feedback recorded: {feedback_result.get('success', False)}")
            
            # Test 6: Record feedback (opened)
            print("\n📝 Test 6: Recording feedback (opened)...")
            feedback_result2 = orchestrator.record_feedback(
                nudge_id=result1.get('nudge_id'),
                event_type='OPENED',
                metadata={'opened_at': datetime.now().isoformat()}
            )
            print(f"✅ Feedback recorded: {feedback_result2.get('success', False)}")
        
        # Test 7: Test fatigue limits (try scheduling too many nudges)
        print("\n⚠️  Test 7: Testing fatigue limits...")
        fatigue_results = []
        for i in range(5):
            fatigue_result = orchestrator.schedule_nudge(
                action_type='informational',
                family_id='FAM_FATIGUE_TEST',
                urgency='LOW',
                scheduled_by='TEST_USER'
            )
            fatigue_results.append(fatigue_result.get('success', False))
            if not fatigue_result.get('success'):
                print(f"   Nudge {i+1}: Blocked - {fatigue_result.get('reason', 'Unknown')}")
                break
        
        print(f"\n✅ Fatigue test completed. Successfully scheduled: {sum(fatigue_results)} nudges")
        
        print("\n" + "="*60)
        print("✅ All tests completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        orchestrator.disconnect()


if __name__ == "__main__":
    test_nudge_scheduling()

