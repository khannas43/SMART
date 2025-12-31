"""
Check Eligibility Scores
Quick script to check eligibility scores in the database
"""

import sys
from pathlib import Path
import yaml

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


def check_eligibility_scores():
    """Check eligibility scores by scheme"""
    print("=" * 80)
    print("Checking Eligibility Scores")
    print("=" * 80)
    
    # Load config
    config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Connect to eligibility database
    eligibility_config = config.get('external_databases', {}).get('eligibility')
    if not eligibility_config:
        print("❌ Eligibility database not configured")
        return
    
    db = DBConnector(
        host=eligibility_config['host'],
        port=eligibility_config['port'],
        database=eligibility_config['name'],
        user=eligibility_config['user'],
        password=eligibility_config['password']
    )
    
    try:
        db.connect()
        
        query = """
            SELECT 
                scheme_code, 
                AVG(eligibility_score) as avg_score,
                MIN(eligibility_score) as min_score,
                MAX(eligibility_score) as max_score,
                COUNT(*) as count
            FROM eligibility.eligibility_snapshots
            WHERE evaluation_status IN ('RULE_ELIGIBLE', 'POSSIBLE_ELIGIBLE')
            GROUP BY scheme_code
            ORDER BY scheme_code
        """
        
        cursor = db.connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        
        if not rows:
            print("\n⚠️  No eligible families found")
            return
        
        print(f"\n📊 Eligibility Scores Summary (Threshold: 0.6)")
        print("-" * 80)
        print(f"{'Scheme':<20} {'Count':<8} {'Min':<10} {'Max':<10} {'Avg':<10} {'Status'}")
        print("-" * 80)
        
        for row in rows:
            scheme_code, avg_score, min_score, max_score, count = row
            avg_float = float(avg_score) if avg_score else 0.0
            min_float = float(min_score) if min_score else 0.0
            max_float = float(max_score) if max_score else 0.0
            
            # Determine if any families meet threshold
            if max_float >= 0.6:
                status = "✅ Eligible families available"
            elif avg_float >= 0.6:
                status = "⚠️  Some eligible (avg meets threshold)"
            else:
                status = "❌ Below threshold"
            
            print(f"{scheme_code:<20} {count:<8} {min_float:<10.4f} {max_float:<10.4f} {avg_float:<10.4f} {status}")
        
        print("-" * 80)
        
        # Check current threshold
        use_case_config_path = Path(__file__).parent.parent / "config" / "use_case_config.yaml"
        if use_case_config_path.exists():
            with open(use_case_config_path, 'r') as f:
                use_case_config = yaml.safe_load(f)
            current_threshold = use_case_config.get('application', {}).get('min_eligibility_score', 0.6)
            print(f"\n💡 Current threshold: {current_threshold}")
            print(f"   To lower for testing, edit: config/use_case_config.yaml")
            print(f"   Change: application.min_eligibility_score to a lower value (e.g., 0.3)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.disconnect()


if __name__ == '__main__':
    check_eligibility_scores()

