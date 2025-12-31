"""
End-to-End Test
Tests complete intimation flow from intake to consent
"""

import sys
import os
from pathlib import Path
import argparse

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))
from intimation_service import IntimationService
from consent_manager import ConsentManager


def test_end_to_end(scheme_code: str = 'CHIRANJEEVI', limit: int = 10):
    """Test end-to-end flow"""
    print("=" * 80)
    print("End-to-End Test")
    print("=" * 80)
    print(f"Scheme: {scheme_code}")
    print(f"Limit: {limit} candidates")
    
    service = IntimationService()
    consent_manager = ConsentManager()
    
    try:
        # Step 1: Intake Process
        print(f"\n1️⃣ Running intake process for {scheme_code}...")
        campaigns = service.run_intake_process(scheme_code=scheme_code)
        
        if not campaigns:
            print("   ⚠️  No campaigns created - check eligibility data")
            return
        
        campaign = campaigns[0]
        print(f"   ✅ Campaign created: {campaign.campaign_id}")
        print(f"      Candidates: {campaign.total_candidates}")
        print(f"      Status: {campaign.status}")
        
        # Step 2: Get candidates
        print(f"\n2️⃣ Fetching candidates (limit: {limit})...")
        from campaign_manager import CampaignManager
        import pandas as pd
        
        manager = CampaignManager()
        manager.db.connect()
        
        query = """
            SELECT candidate_id, family_id, scheme_code, eligibility_score,
                   primary_mobile, email, preferred_language
            FROM intimation.campaign_candidates
            WHERE campaign_id = %s
            LIMIT %s
        """
        candidates_df = pd.read_sql(query, manager.db.connection, params=[campaign.campaign_id, limit])
        manager.db.disconnect()
        
        if candidates_df.empty:
            print("   ⚠️  No candidates found")
            return
        
        print(f"   ✅ Found {len(candidates_df)} candidates")
        
        # Step 3: Test message personalization for each candidate
        print(f"\n3️⃣ Testing message personalization...")
        from message_personalizer import MessagePersonalizer
        personalizer = MessagePersonalizer()
        
        scheme_query = """
            SELECT scheme_code, scheme_name, category
            FROM public.scheme_master
            WHERE scheme_code = %s
        """
        scheme_df = pd.read_sql(scheme_query, personalizer.db.connection, params=[scheme_code])
        scheme_info = scheme_df.iloc[0].to_dict() if not scheme_df.empty else {}
        
        messages_created = 0
        for _, candidate in candidates_df.head(3).iterrows():
            try:
                message = personalizer.personalize_for_candidate(
                    candidate.to_dict(),
                    scheme_info,
                    'mobile_app',
                    candidate.get('preferred_language', 'hi')
                )
                messages_created += 1
                print(f"   ✅ Message created for {candidate['family_id'][:8]}...")
            except Exception as e:
                print(f"   ⚠️  Error creating message: {e}")
        
        personalizer.disconnect()
        print(f"   ✅ Created {messages_created} messages")
        
        # Step 4: Test consent creation
        print(f"\n4️⃣ Testing consent creation...")
        consents_created = 0
        for _, candidate in candidates_df.head(3).iterrows():
            try:
                consent = consent_manager.create_consent(
                    family_id=candidate['family_id'],
                    scheme_code=candidate['scheme_code'],
                    consent_value=True,
                    consent_method='click',
                    channel='mobile_app',
                    session_id=f'test_session_{consents_created}',
                    device_id='test_device'
                )
                consents_created += 1
                print(f"   ✅ Consent created: {consent.get('consent_id')}")
            except Exception as e:
                print(f"   ⚠️  Error creating consent: {e}")
        
        print(f"   ✅ Created {consents_created} consents")
        
        # Step 5: Verify consent status
        print(f"\n5️⃣ Verifying consent status...")
        verified = 0
        for _, candidate in candidates_df.head(3).iterrows():
            status = consent_manager.get_consent_status(
                candidate['family_id'],
                candidate['scheme_code']
            )
            if status:
                verified += 1
                print(f"   ✅ Consent verified for {candidate['family_id'][:8]}...")
        
        print(f"   ✅ Verified {verified} consents")
        
        # Summary
        print("\n" + "=" * 80)
        print("✅ End-to-End Test Summary")
        print("=" * 80)
        print(f"   Campaigns created: {len(campaigns)}")
        print(f"   Candidates processed: {len(candidates_df)}")
        print(f"   Messages created: {messages_created}")
        print(f"   Consents created: {consents_created}")
        print(f"   Consents verified: {verified}")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error during end-to-end test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        service.disconnect()
        consent_manager.disconnect()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='End-to-end test for intimation system')
    parser.add_argument('--scheme-code', default='CHIRANJEEVI', help='Scheme code to test')
    parser.add_argument('--limit', type=int, default=10, help='Limit number of candidates')
    args = parser.parse_args()
    
    test_end_to_end(args.scheme_code, args.limit)

