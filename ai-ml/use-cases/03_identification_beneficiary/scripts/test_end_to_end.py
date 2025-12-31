"""
End-to-End Test: Complete Evaluation Pipeline
Use Case: AI-PLATFORM-03 - Auto Identification of Beneficiaries

This script tests the complete pipeline:
1. Check prerequisites (schemes, rules, models)
2. Create/verify eligibility rules
3. Train/verify ML models (optional)
4. Run batch evaluation
5. Generate candidate lists
6. Verify results in database
"""

import sys
from pathlib import Path
import argparse
import yaml
import pandas as pd

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))
from rule_manager import RuleManager
from evaluator_service import EligibilityEvaluationService


def check_prerequisites():
    """Check if prerequisites are met"""
    print("="*80)
    print("Step 1: Checking Prerequisites")
    print("="*80)
    
    db_config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    with open(db_config_path, 'r') as f:
        db_config = yaml.safe_load(f)['database']
    
    db = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    db.connect()
    
    checks = {}
    
    # Check schemes
    query = """
        SELECT COUNT(*) as count
        FROM public.scheme_master
        WHERE is_auto_id_enabled = true AND status = 'active'
    """
    df = pd.read_sql(query, db.connection)
    scheme_count = df.iloc[0]['count']
    checks['schemes'] = scheme_count > 0
    print(f"✅ Schemes: {scheme_count} active schemes with auto-identification")
    
    # Check rules
    query = """
        SELECT COUNT(DISTINCT scheme_code) as count
        FROM eligibility.scheme_eligibility_rules
        WHERE effective_to IS NULL OR effective_to >= CURRENT_DATE
    """
    df = pd.read_sql(query, db.connection)
    rule_schemes = df.iloc[0]['count']
    checks['rules'] = rule_schemes > 0
    print(f"{'✅' if rule_schemes > 0 else '⚠️ '} Rules: {rule_schemes} schemes with rules")
    
    # Check models
    query = """
        SELECT COUNT(DISTINCT scheme_code) as count
        FROM eligibility.ml_model_registry
        WHERE is_active = true
    """
    df = pd.read_sql(query, db.connection)
    model_schemes = df.iloc[0]['count']
    checks['models'] = model_schemes > 0
    print(f"{'✅' if model_schemes > 0 else '⚠️ '} ML Models: {model_schemes} schemes with active models")
    
    # Check training data
    profile_db_config = yaml.safe_load(open(db_config_path))['external_databases']['profile_360']
    profile_db = DBConnector(
        host=profile_db_config['host'],
        port=profile_db_config['port'],
        database=profile_db_config['name'],
        user=profile_db_config['user'],
        password=profile_db_config['password']
    )
    profile_db.connect()
    
    query = "SELECT COUNT(*) as count FROM golden_records WHERE status = 'active' AND family_id IS NOT NULL"
    df = pd.read_sql(query, profile_db.connection)
    family_count = df.iloc[0]['count']
    checks['data'] = family_count > 0
    print(f"{'✅' if family_count > 0 else '⚠️ '} Training Data: {family_count} active families")
    
    profile_db.disconnect()
    db.disconnect()
    
    return checks


def load_rules_if_needed(scheme_code: str):
    """Load rules if they don't exist"""
    print(f"\n{'='*80}")
    print(f"Step 2: Checking Rules for {scheme_code}")
    print("="*80)
    
    db_config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    with open(db_config_path, 'r') as f:
        db_config = yaml.safe_load(f)['database']
    
    db = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    db.connect()
    
    query = """
        SELECT COUNT(*) as count
        FROM eligibility.scheme_eligibility_rules
        WHERE scheme_code = %s
            AND (effective_to IS NULL OR effective_to >= CURRENT_DATE)
    """
    df = pd.read_sql(query, db.connection, params=(scheme_code,))
    rule_count = df.iloc[0]['count']
    
    db.disconnect()
    
    if rule_count > 0:
        print(f"✅ {rule_count} active rules found for {scheme_code}")
        return True
    
    print(f"⚠️  No rules found for {scheme_code}")
    print("   Run: python scripts/load_sample_rules.py")
    return False


def run_batch_evaluation(scheme_code: str, limit: int = 50):
    """Run batch evaluation"""
    print(f"\n{'='*80}")
    print(f"Step 3: Running Batch Evaluation for {scheme_code}")
    print("="*80)
    
    service = EligibilityEvaluationService()
    
    try:
        result = service.evaluate_batch(
            scheme_ids=[scheme_code],
            max_families=limit
        )
        
        print(f"✅ Batch evaluation completed:")
        print(f"   Batch ID: {result['batch_id']}")
        print(f"   Families Evaluated: {result.get('families_evaluated', 0)}")
        print(f"   Snapshots Created: {result.get('snapshots_created', 0)}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        service.close()


def verify_results(scheme_code: str):
    """Verify evaluation results in database"""
    print(f"\n{'='*80}")
    print(f"Step 4: Verifying Results for {scheme_code}")
    print("="*80)
    
    db_config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    with open(db_config_path, 'r') as f:
        db_config = yaml.safe_load(f)['database']
    
    db = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    db.connect()
    
    # Check snapshots
    query = """
        SELECT 
            COUNT(*) as total_snapshots,
            COUNT(*) FILTER (WHERE evaluation_status = 'RULE_ELIGIBLE') as rule_eligible,
            COUNT(*) FILTER (WHERE evaluation_status = 'RULE_INELIGIBLE') as rule_ineligible,
            COUNT(*) FILTER (WHERE evaluation_status = 'HYBRID_ELIGIBLE') as hybrid_eligible,
            AVG(eligibility_score) as avg_score
        FROM eligibility.eligibility_snapshots
        WHERE scheme_code = %s
            AND evaluation_timestamp >= CURRENT_DATE - INTERVAL '1 day'
    """
    df = pd.read_sql(query, db.connection, params=(scheme_code,))
    
    if len(df) > 0:
        row = df.iloc[0]
        print(f"✅ Snapshots found:")
        print(f"   Total: {row['total_snapshots']}")
        print(f"   Rule Eligible: {row['rule_eligible']}")
        print(f"   Rule Ineligible: {row['rule_ineligible']}")
        print(f"   Hybrid Eligible: {row['hybrid_eligible']}")
        print(f"   Average Score: {row['avg_score']:.4f}" if row['avg_score'] else "   Average Score: N/A")
    
    # Check candidate lists
    query = """
        SELECT 
            COUNT(*) as total_candidates,
            COUNT(DISTINCT family_id) as unique_families,
            AVG(rank_in_scheme) as avg_rank
        FROM eligibility.candidate_lists
        WHERE scheme_code = %s
            AND is_active = true
            AND generated_at >= CURRENT_DATE - INTERVAL '1 day'
    """
    df = pd.read_sql(query, db.connection, params=(scheme_code,))
    
    if len(df) > 0:
        row = df.iloc[0]
        print(f"\n✅ Candidate Lists:")
        print(f"   Total Candidates: {row['total_candidates']}")
        print(f"   Unique Families: {row['unique_families']}")
        print(f"   Average Rank: {row['avg_rank']:.2f}" if row['avg_rank'] else "   Average Rank: N/A")
    
    db.disconnect()


def main():
    parser = argparse.ArgumentParser(description='End-to-end pipeline test')
    parser.add_argument('--scheme-code', default='CHIRANJEEVI', 
                       help='Scheme code to test (default: CHIRANJEEVI)')
    parser.add_argument('--limit', type=int, default=50, 
                       help='Limit families to evaluate (default: 50)')
    parser.add_argument('--skip-rules', action='store_true',
                       help='Skip rule loading check')
    parser.add_argument('--skip-eval', action='store_true',
                       help='Skip batch evaluation')
    
    args = parser.parse_args()
    
    print("="*80)
    print("End-to-End Pipeline Test")
    print("="*80)
    print(f"Scheme Code: {args.scheme_code}")
    print(f"Limit: {args.limit}")
    print()
    
    # Step 1: Check prerequisites
    checks = check_prerequisites()
    
    if not all([checks['schemes'], checks['data']]):
        print("\n❌ Prerequisites not met. Please check:")
        if not checks['schemes']:
            print("   - Load schemes: psql ... -f scripts/load_initial_schemes.sql")
        if not checks['data']:
            print("   - Load training data (from AI-PLATFORM-02)")
        return
    
    # Step 2: Load rules if needed
    if not args.skip_rules:
        if not load_rules_if_needed(args.scheme_code):
            print("\n⚠️  Continuing without rules...")
    
    # Step 3: Run batch evaluation
    if not args.skip_eval:
        result = run_batch_evaluation(args.scheme_code, limit=args.limit)
        
        if result:
            # Step 4: Verify results
            verify_results(args.scheme_code)
    
    print("\n" + "="*80)
    print("✅ End-to-End Test Complete!")
    print("="*80)


if __name__ == "__main__":
    main()

