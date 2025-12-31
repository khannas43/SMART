"""
Test Intake Process
Tests the campaign intake and creation process
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))
from intimation_service import IntimationService


def test_intake():
    """Test intake process"""
    print("=" * 80)
    print("Testing Intake Process")
    print("=" * 80)
    
    service = IntimationService()
    
    try:
        # Test intake for a specific scheme
        scheme_code = 'CHIRANJEEVI'
        print(f"\n📋 Running intake for scheme: {scheme_code}")
        
        # Debug: Check candidates before filtering
        candidates = service.campaign_manager.intake_eligibility_signals(scheme_code=scheme_code)
        print(f"\n📊 Found {len(candidates)} candidates from eligibility snapshots")
        
        if candidates:
            print(f"   Sample candidate:")
            print(f"     Family ID: {candidates[0].family_id}")
            print(f"     Eligibility Score: {candidates[0].eligibility_score}")
            print(f"     Priority Score: {candidates[0].priority_score}")
            print(f"     Scheme: {candidates[0].scheme_code}")
        
        # Check filtered candidates
        filtered = service.campaign_manager.apply_campaign_policies(candidates, scheme_code)
        print(f"\n🔍 After applying campaign policies: {len(filtered)} candidates remain")
        
        if len(candidates) > 0 and len(filtered) == 0:
            print(f"   ⚠️  All candidates filtered out by campaign policies!")
            print(f"   Check: score thresholds, priority thresholds, fatigue limits")
        
        campaigns = service.run_intake_process(scheme_code=scheme_code)
        
        if campaigns:
            print(f"\n✅ Created {len(campaigns)} campaign(s):")
            for campaign in campaigns:
                print(f"   - Campaign ID: {campaign.campaign_id}")
                print(f"     Name: {campaign.campaign_name}")
                print(f"     Scheme: {campaign.scheme_code}")
                print(f"     Candidates: {campaign.total_candidates}")
                print(f"     Status: {campaign.status}")
        else:
            print(f"\n⚠️  No campaigns created (no eligible candidates found)")
        
        print("\n" + "=" * 80)
        print("✅ Intake test complete!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error during intake: {e}")
        import traceback
        traceback.print_exc()
    finally:
        service.disconnect()


if __name__ == '__main__':
    test_intake()

