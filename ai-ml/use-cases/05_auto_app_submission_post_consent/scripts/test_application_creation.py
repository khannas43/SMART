"""
Test Application Creation
Tests the application creation workflow from consent events

Note: If tests fail due to low eligibility scores, you can temporarily
lower the threshold in config/use_case_config.yaml:
  application:
    min_eligibility_score: 0.3  # Lower for testing
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))
from application_orchestrator import ApplicationOrchestrator


def test_application_creation():
    """Test application creation from consent"""
    print("=" * 80)
    print("Testing Application Creation from Consent")
    print("=" * 80)
    
    orchestrator = ApplicationOrchestrator()
    
    try:
        orchestrator.connect()
        
        # Get minimum eligibility score from config
        min_score = orchestrator.use_case_config.get('application', {}).get('min_eligibility_score', 0.6)
        print(f"\n📊 Minimum eligibility score threshold: {min_score}")
        
        # Test with a family that has given consent
        # First, find a family with consent
        print("\n📋 Finding families with consent...")
        
        # Query consent records
        query = """
            SELECT DISTINCT ON (family_id, scheme_code) 
                family_id, scheme_code, consent_id, created_at
            FROM intimation.consent_records
            WHERE status = 'valid'
                AND consent_value = true
            ORDER BY family_id, scheme_code, created_at DESC
            LIMIT 10
        """
        
        cursor = orchestrator.db.connection.cursor()
        cursor.execute(query)
        consents = cursor.fetchall()
        cursor.close()
        
        if not consents:
            print("   ⚠️  No consent records found")
            print("   Please run AI-PLATFORM-04 intake and consent tests first")
            return
        
        print(f"   ✅ Found {len(consents)} consent records")
        
        # Check eligibility scores for all consents
        print("\n📋 Checking eligibility scores...")
        eligible_consents = []
        eligibility_db = orchestrator.external_dbs.get('eligibility')
        
        if eligibility_db:
            for consent in consents:
                family_id, scheme_code, consent_id, created_at = consent
                # Check eligibility score
                eligibility_query = """
                    SELECT eligibility_score, evaluation_status
                    FROM eligibility.eligibility_snapshots
                    WHERE family_id::text = %s
                        AND scheme_code = %s
                        AND evaluation_status IN ('RULE_ELIGIBLE', 'POSSIBLE_ELIGIBLE')
                    ORDER BY evaluation_timestamp DESC
                    LIMIT 1
                """
                cursor = eligibility_db.connection.cursor()
                cursor.execute(eligibility_query, [str(family_id), scheme_code])
                row = cursor.fetchone()
                cursor.close()
                
                if row:
                    score, status = row
                    score_float = float(score) if score else 0.0
                    if score_float >= min_score:
                        eligible_consents.append((consent, score_float, status))
                        print(f"   ✅ {family_id[:8]}... / {scheme_code}: score {score_float:.4f} (eligible)")
                    else:
                        print(f"   ⚠️  {family_id[:8]}... / {scheme_code}: score {score_float:.4f} (below threshold {min_score})")
                else:
                    print(f"   ⚠️  {family_id[:8]}... / {scheme_code}: no eligibility snapshot found")
        else:
            print("   ⚠️  Eligibility database not available, will try first consent")
            eligible_consents = [(consents[0], None, None)]
        
        if not eligible_consents:
            print(f"\n❌ No families found with eligibility score >= {min_score}")
            print(f"   💡 Tip: You can lower the threshold in config/use_case_config.yaml")
            print(f"   Or run create_test_consent.py to create consents with higher scores")
            return
        
        # Test application creation for first eligible consent
        consent_data = eligible_consents[0]
        consent, score, status = consent_data
        family_id, scheme_code, consent_id, created_at = consent
        
        print(f"\n🔄 Testing application creation:")
        print(f"   Family ID: {family_id}")
        print(f"   Scheme: {scheme_code}")
        print(f"   Consent ID: {consent_id}")
        if score is not None:
            print(f"   Eligibility Score: {score:.4f}")
            print(f"   Eligibility Status: {status}")
        
        result = orchestrator.trigger_on_consent(
            family_id=str(family_id),
            scheme_code=scheme_code,
            consent_id=consent_id
        )
        
        if result['success']:
            print(f"\n✅ Application created successfully!")
            print(f"   Application ID: {result['application_id']}")
            print(f"   Status: {result['status']}")
            print(f"   Message: {result['message']}")
        else:
            print(f"\n❌ Application creation failed:")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            if 'details' in result:
                print(f"   Details: {result['details']}")
        
        print("\n" + "=" * 80)
        print("✅ Application creation test complete!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        orchestrator.disconnect()


if __name__ == '__main__':
    test_application_creation()

