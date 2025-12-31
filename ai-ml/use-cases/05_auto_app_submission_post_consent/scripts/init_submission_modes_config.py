"""
Initialize Submission Modes Configuration
Creates submission mode configurations for schemes
"""

import sys
from pathlib import Path
import yaml
import json
from datetime import datetime

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


def init_submission_modes_config():
    """Initialize submission modes configuration for all schemes"""
    print("=" * 80)
    print("Initializing Submission Modes Configuration")
    print("=" * 80)
    
    # Load configuration
    base_dir = Path(__file__).parent.parent
    config_path = base_dir / "config" / "db_config.yaml"
    use_case_config_path = base_dir / "config" / "use_case_config.yaml"
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    use_case_config = {}
    if use_case_config_path.exists():
        with open(use_case_config_path, 'r') as f:
            use_case_config = yaml.safe_load(f)
    
    # Connect to database
    db = DBConnector(
        host=config['database']['host'],
        port=config['database']['port'],
        database=config['database']['name'],
        user=config['database']['user'],
        password=config['database']['password']
    )
    
    try:
        db.connect()
        print(f"\n✅ Connected to PostgreSQL: {config['database']['host']}:{config['database']['port']}/{config['database']['name']}")
        
        cursor = db.connection.cursor()
        
        # Get all schemes from scheme_master
        cursor.execute("""
            SELECT scheme_code, scheme_name, category
            FROM public.scheme_master
            WHERE status = 'active'
            ORDER BY scheme_code
        """)
        
        schemes = cursor.fetchall()
        print(f"\n📋 Found {len(schemes)} active schemes")
        
        created = 0
        skipped = 0
        
        # Determine submission mode based on category (default rules)
        def get_default_mode(category):
            """Determine default submission mode based on category"""
            if category in ["HEALTH"]:
                return "auto"  # Low risk
            elif category in ["EDUCATION", "LIVELIHOOD"]:
                return "review"  # Moderate risk
            else:  # SOCIAL_SECURITY, PENSION, HOUSING
                return "review"  # Higher risk, require review
        
        for scheme_code, scheme_name, category in schemes:
            print(f"\n📋 Processing scheme: {scheme_code} ({scheme_name})")
            
            # Check if config already exists
            cursor.execute("""
                SELECT COUNT(*) 
                FROM application.submission_modes_config 
                WHERE scheme_code = %s AND is_active = true
            """, (scheme_code,))
            
            if cursor.fetchone()[0] > 0:
                print(f"   ⚠️  Skipped (config already exists)")
                skipped += 1
                continue
            
            # Get scheme-specific config from use_case_config if available
            scheme_config = use_case_config.get('schemes', {}).get(scheme_code, {})
            
            # Determine submission mode
            default_mode = scheme_config.get('submission_mode') or get_default_mode(category)
            
            # Auto submission conditions
            allow_auto = default_mode == "auto"
            auto_conditions = scheme_config.get('auto_submission', {})
            
            # Review mode settings
            require_review = default_mode in ["review", "assisted"]
            editable_fields = scheme_config.get('review_mode', {}).get('editable_fields', [
                "contact_mobile",
                "contact_email",
                "bank_account_number",
                "ifsc_code",
                "address_line1",
                "address_line2"
            ])
            
            # Insert config
            cursor.execute("""
                INSERT INTO application.submission_modes_config (
                    scheme_code,
                    default_mode,
                    allow_auto_submission,
                    auto_submission_conditions,
                    require_citizen_review,
                    editable_fields,
                    read_only_fields,
                    route_to_assisted_on_missing_data,
                    is_active,
                    created_by
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING config_id
            """, (
                scheme_code,
                default_mode,
                allow_auto,
                json.dumps(auto_conditions),
                require_review,
                editable_fields,
                [],  # Read-only fields (can be configured per scheme)
                True,  # Route to assisted on missing data
                True,
                "init_submission_modes_config"
            ))
            
            config_id = cursor.fetchone()[0]
            db.connection.commit()
            
            print(f"   ✅ Created config (ID: {config_id})")
            print(f"      Mode: {default_mode}")
            print(f"      Auto submission: {allow_auto}")
            print(f"      Require review: {require_review}")
            created += 1
        
        cursor.close()
        
        print("\n" + "=" * 80)
        print(f"✅ Submission modes initialization complete!")
        print(f"   Created: {created}")
        print(f"   Skipped: {skipped}")
        print(f"   Total: {len(schemes)}")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.connection.rollback()
        raise
    finally:
        db.disconnect()


if __name__ == "__main__":
    init_submission_modes_config()

