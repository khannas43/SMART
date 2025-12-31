"""
Test Script: Batch Evaluation Pipeline
Use Case: AI-PLATFORM-03 - Auto Identification of Beneficiaries

This script tests:
1. Batch evaluation for all schemes
2. Batch evaluation for specific scheme
3. Event-driven evaluation
4. Candidate list generation
"""

import sys
from pathlib import Path
import argparse
import uuid

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))
from evaluator_service import EligibilityEvaluationService


def test_batch_evaluation_all_schemes(service: EligibilityEvaluationService, limit: int = 10):
    """Test batch evaluation for all active schemes"""
    print("\n" + "="*80)
    print("Test: Batch Evaluation (All Schemes)")
    print("="*80)
    
    try:
        result = service.evaluate_batch(
            scheme_ids=None,  # All schemes
            district_ids=None,  # All districts
            max_families=limit
        )
        
        print(f"✅ Batch evaluation completed:")
        print(f"   Batch ID: {result['batch_id']}")
        print(f"   Families Evaluated: {result.get('families_evaluated', 0)}")
        print(f"   Snapshots Created: {result.get('snapshots_created', 0)}")
        print(f"   Errors: {result.get('errors_count', 0)}")
        
        if result.get('snapshots'):
            print(f"\n   Sample Snapshots:")
            for snapshot in result['snapshots'][:5]:
                print(f"      - Family: {snapshot.get('family_id', 'N/A')}")
                print(f"        Scheme: {snapshot.get('scheme_code', 'N/A')}")
                print(f"        Status: {snapshot.get('evaluation_status', 'N/A')}")
                print()
        
        return result
        
    except Exception as e:
        print(f"❌ Error in batch evaluation: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_batch_evaluation_scheme(service: EligibilityEvaluationService, scheme_code: str, limit: int = 10):
    """Test batch evaluation for a specific scheme"""
    print("\n" + "="*80)
    print(f"Test: Batch Evaluation (Scheme: {scheme_code})")
    print("="*80)
    
    try:
        result = service.evaluate_batch(
            scheme_ids=[scheme_code],
            district_ids=None,
            max_families=limit
        )
        
        print(f"✅ Batch evaluation completed:")
        print(f"   Batch ID: {result['batch_id']}")
        print(f"   Scheme: {scheme_code}")
        print(f"   Families Evaluated: {result.get('families_evaluated', 0)}")
        print(f"   Snapshots Created: {result.get('snapshots_created', 0)}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in batch evaluation: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_single_family_evaluation(service: EligibilityEvaluationService, family_id: str = None):
    """Test evaluating a single family"""
    print("\n" + "="*80)
    print("Test: Single Family Evaluation")
    print("="*80)
    
    # Use a test family_id if not provided
    if family_id is None:
        # Try to get a real family_id from database
        import yaml
        import pandas as pd
        from pathlib import Path
        
        sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
        from db_connector import DBConnector
        
        db_config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
        with open(db_config_path, 'r') as f:
            db_config = yaml.safe_load(f)
        
        profile_db_config = db_config['external_databases']['profile_360']
        
        db = DBConnector(
            host=profile_db_config['host'],
            port=profile_db_config['port'],
            database=profile_db_config['name'],
            user=profile_db_config['user'],
            password=profile_db_config['password']
        )
        db.connect()
        
        query = "SELECT DISTINCT family_id FROM golden_records WHERE family_id IS NOT NULL LIMIT 1"
        df = pd.read_sql(query, db.connection)
        db.disconnect()
        
        if len(df) > 0:
            family_id = str(df.iloc[0]['family_id'])
        else:
            print("⚠️  No family data available for testing")
            return None
    
    try:
        result = service.evaluate_family(
            family_id=family_id,
            scheme_ids=None,  # All schemes
            use_ml=True,
            save_results=True
        )
        
        print(f"✅ Family evaluation completed:")
        print(f"   Family ID: {family_id}")
        print(f"   Evaluations: {len(result.get('evaluations', []))}")
        
        if result.get('evaluations'):
            print(f"\n   Evaluation Results:")
            for eval_result in result['evaluations'][:5]:
                print(f"      - Scheme: {eval_result.get('scheme_code', 'N/A')}")
                print(f"        Status: {eval_result.get('evaluation_status', 'N/A')}")
                print(f"        Rule Score: {eval_result.get('rule_score', 'N/A')}")
                print(f"        ML Score: {eval_result.get('ml_score', 'N/A')}")
                print(f"        Final Score: {eval_result.get('final_eligibility_score', 'N/A')}")
                print()
        
        return result
        
    except Exception as e:
        print(f"❌ Error in family evaluation: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_generate_worklist(service: EligibilityEvaluationService, scheme_code: str):
    """Test generating departmental worklist"""
    print("\n" + "="*80)
    print(f"Test: Generate Departmental Worklist (Scheme: {scheme_code})")
    print("="*80)
    
    try:
        result = service.generate_departmental_worklist(
            scheme_code=scheme_code,
            district_id=None,  # All districts
            limit=50
        )
        
        print(f"✅ Worklist generated:")
        print(f"   Scheme: {scheme_code}")
        print(f"   Candidates: {result.get('candidates_count', 0)}")
        print(f"   List ID: {result.get('list_id', 'N/A')}")
        
        if result.get('candidates'):
            print(f"\n   Top 5 Candidates:")
            for i, candidate in enumerate(result['candidates'][:5], 1):
                print(f"      {i}. Family: {candidate.get('family_id', 'N/A')}")
                print(f"         Rank: {candidate.get('rank', 'N/A')}")
                print(f"         Priority Score: {candidate.get('priority_score', 'N/A')}")
                print()
        
        return result
        
    except Exception as e:
        print(f"❌ Error generating worklist: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    parser = argparse.ArgumentParser(description='Test batch evaluation pipeline')
    parser.add_argument('--scheme-code', help='Specific scheme code to test')
    parser.add_argument('--test', choices=['batch-all', 'batch-scheme', 'single-family', 'worklist', 'all'],
                       default='all', help='Which test to run')
    parser.add_argument('--limit', type=int, default=10, help='Limit families to evaluate (default: 10)')
    parser.add_argument('--family-id', help='Family ID for single family test')
    
    args = parser.parse_args()
    
    print("="*80)
    print("Batch Evaluation Test Suite")
    print("="*80)
    
    service = EligibilityEvaluationService()
    
    try:
        if args.test in ['batch-all', 'all']:
            test_batch_evaluation_all_schemes(service, limit=args.limit)
        
        if args.test in ['batch-scheme', 'all']:
            scheme = args.scheme_code or 'CHIRANJEEVI'
            test_batch_evaluation_scheme(service, scheme, limit=args.limit)
        
        if args.test in ['single-family', 'all']:
            test_single_family_evaluation(service, family_id=args.family_id)
        
        if args.test in ['worklist', 'all']:
            scheme = args.scheme_code or 'CHIRANJEEVI'
            test_generate_worklist(service, scheme)
        
        print("\n" + "="*80)
        print("✅ All tests completed!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        service.close()


if __name__ == "__main__":
    main()

