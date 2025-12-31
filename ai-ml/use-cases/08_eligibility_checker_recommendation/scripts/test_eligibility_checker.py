#!/usr/bin/env python3
"""
Test Eligibility Checker Workflow
Use Case ID: AI-PLATFORM-08
"""

import sys
from pathlib import Path
import yaml
import json
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "03_identification_beneficiary" / "src"))

from services.eligibility_orchestrator import EligibilityOrchestrator
from services.questionnaire_handler import QuestionnaireHandler


def test_eligibility_checker():
    """Test eligibility checker workflow"""
    print("=" * 80)
    print("Testing Eligibility Checker Workflow")
    print("=" * 80)
    
    config_path = Path(__file__).parent.parent / "config" / "use_case_config.yaml"
    
    # Initialize orchestrator
    orchestrator = EligibilityOrchestrator(str(config_path))
    
    try:
        orchestrator.connect()
        print("✅ Connected to databases")
        
        # Test 1: Get questionnaire
        print("\n" + "=" * 80)
        print("Test 1: Get Questionnaire Template")
        print("=" * 80)
        
        questionnaire_handler = QuestionnaireHandler(str(config_path))
        questionnaire_handler.connect()
        
        questionnaire = questionnaire_handler.get_questionnaire('default_guest_questionnaire')
        print(f"✅ Questionnaire retrieved:")
        print(f"   Template: {questionnaire.get('template_name')}")
        print(f"   Version: {questionnaire.get('template_version')}")
        print(f"   Questions: {len(questionnaire.get('questions', []))}")
        for q in questionnaire.get('questions', [])[:3]:
            print(f"     - {q.get('question')} ({q.get('type')}, required: {q.get('required')})")
        
        questionnaire_handler.disconnect()
        
        # Test 2: Guest user check
        print("\n" + "=" * 80)
        print("Test 2: Guest User Eligibility Check")
        print("=" * 80)
        
        guest_responses = {
            'age': 65,
            'gender': 'Male',
            'district': 'Jaipur',
            'income_band': 'Below 5000',
            'category': 'General',
            'disability': False
        }
        
        print(f"📋 Guest responses: {json.dumps(guest_responses, indent=2)}")
        
        guest_result = orchestrator.check_and_recommend(
            family_id=None,
            questionnaire_responses=guest_responses,
            session_id='test_session_guest_001',
            check_type='FULL_CHECK',
            check_mode='WEB',
            generate_recommendations=False,
            language='en'
        )
        
        print(f"✅ Guest check complete:")
        print(f"   Check ID: {guest_result.get('check_id')}")
        print(f"   User Type: {guest_result.get('user_type')}")
        print(f"   Total Schemes: {guest_result.get('total_schemes_checked')}")
        print(f"   Eligible: {guest_result.get('eligible_count')}")
        print(f"   Possible Eligible: {guest_result.get('possible_eligible_count')}")
        print(f"   Not Eligible: {guest_result.get('not_eligible_count')}")
        print(f"   Is Approximate: {guest_result.get('is_approximate')}")
        
        if guest_result.get('top_recommendations'):
            print(f"\n   Top Recommendations ({len(guest_result.get('top_recommendations', []))}):")
            for i, rec in enumerate(guest_result.get('top_recommendations', [])[:3], 1):
                print(f"     {i}. {rec.get('scheme_code')} - {rec.get('eligibility_status')} "
                      f"(score: {rec.get('eligibility_score', 0):.2f})")
        
        # Test 3: Logged-in user check (if family_id available)
        print("\n" + "=" * 80)
        print("Test 3: Logged-in User Eligibility Check")
        print("=" * 80)
        
        # Try to find a test family_id from golden_records
        try:
            from db_connector import DBConnector
            db_config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
            with open(db_config_path, 'r') as f:
                db_configs = yaml.safe_load(f)
            
            ext_db_config = db_configs['external_databases']['golden_records']
            gr_db = DBConnector(
                host=ext_db_config['host'],
                port=ext_db_config['port'],
                database=ext_db_config['name'],
                user=ext_db_config['user'],
                password=ext_db_config['password']
            )
            gr_db.connect()
            cursor = gr_db.connection.cursor()
            
            cursor.execute("""
                SELECT DISTINCT family_id 
                FROM golden_records.beneficiaries 
                WHERE family_id IS NOT NULL 
                LIMIT 1
            """)
            row = cursor.fetchone()
            cursor.close()
            gr_db.disconnect()
            
            if row:
                test_family_id = str(row[0])
                print(f"📋 Using test family_id: {test_family_id[:8]}...")
                
                logged_in_result = orchestrator.check_and_recommend(
                    family_id=test_family_id,
                    beneficiary_id=None,
                    session_id='test_session_logged_in_001',
                    check_type='FULL_CHECK',
                    check_mode='WEB',
                    generate_recommendations=True,
                    language='en'
                )
                
                print(f"✅ Logged-in check complete:")
                print(f"   Check ID: {logged_in_result.get('check_id')}")
                print(f"   User Type: {logged_in_result.get('user_type')}")
                print(f"   Total Schemes: {logged_in_result.get('total_schemes_checked')}")
                print(f"   Eligible: {logged_in_result.get('eligible_count')}")
                print(f"   Is Approximate: {logged_in_result.get('is_approximate')}")
                
                if logged_in_result.get('top_recommendations'):
                    print(f"\n   Top Recommendations ({len(logged_in_result.get('top_recommendations', []))}):")
                    for i, rec in enumerate(logged_in_result.get('top_recommendations', [])[:5], 1):
                        print(f"     {i}. {rec.get('scheme_code')} - {rec.get('eligibility_status')} "
                              f"(score: {rec.get('eligibility_score', 0):.2f}, "
                              f"priority: {rec.get('priority_score', 0):.2f})")
                        if rec.get('explanation_text'):
                            print(f"        Explanation: {rec.get('explanation_text')[:80]}...")
            else:
                print("⚠️  No test family_id found in golden_records. Skipping logged-in test.")
        
        except Exception as e:
            print(f"⚠️  Could not perform logged-in user test: {e}")
        
        # Test 4: Get recommendations
        print("\n" + "=" * 80)
        print("Test 4: Get Recommendations")
        print("=" * 80)
        
        try:
            if row:
                recommendations = orchestrator.get_recommendations(
                    family_id=test_family_id,
                    refresh=False,
                    language='en'
                )
                
                print(f"✅ Recommendations retrieved:")
                if recommendations.get('top_recommendations'):
                    print(f"   Found {len(recommendations.get('top_recommendations', []))} recommendations")
                else:
                    print(f"   No recommendations found (may need to run check first)")
            else:
                print("⚠️  Skipping - no test family_id")
        
        except Exception as e:
            print(f"⚠️  Error getting recommendations: {e}")
        
        print("\n" + "=" * 80)
        print("✅ Testing complete!")
        print("=" * 80)
    
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        orchestrator.disconnect()
        print("\n✅ Disconnected from databases")


if __name__ == '__main__':
    test_eligibility_checker()

