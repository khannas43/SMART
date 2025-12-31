"""
Initialize Scheme Intimation Configuration
Sets up default configuration for schemes
"""

import sys
import os
from pathlib import Path
import yaml
import pandas as pd

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


def init_scheme_config():
    """Initialize scheme intimation configuration"""
    print("=" * 80)
    print("Initializing Scheme Intimation Configuration")
    print("=" * 80)
    
    # Load config
    config_path = os.path.join(os.path.dirname(__file__), '../config/db_config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Connect to database
    db_config = config['database']
    db = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    db.connect()
    
    cursor = db.connection.cursor()
    
    # Get all schemes from scheme_master
    schemes_query = "SELECT scheme_code, category FROM public.scheme_master WHERE status = 'active'"
    schemes_df = pd.read_sql(schemes_query, db.connection)
    
    created = 0
    updated = 0
    
    try:
        for _, scheme in schemes_df.iterrows():
            scheme_code = scheme['scheme_code']
            category = scheme['category']
            
            # Determine consent type based on category
            if category in ['SOCIAL_SECURITY', 'PENSION', 'FINANCIAL']:
                consent_type = 'strong'
                require_otp = True
                require_e_sign = False
            else:
                consent_type = 'soft'
                require_otp = False
                require_e_sign = False
            
            # Check if config exists
            check_query = """
                SELECT config_id FROM intimation.scheme_intimation_config
                WHERE scheme_code = %s
            """
            cursor.execute(check_query, (scheme_code,))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing
                update_query = """
                    UPDATE intimation.scheme_intimation_config
                    SET 
                        auto_intimation_enabled = true,
                        min_eligibility_score = 0.6,
                        priority_threshold = 0.8,
                        consent_type_required = %s,
                        require_otp = %s,
                        require_e_sign = %s,
                        consent_validity_days = 365,
                        max_intimations_per_family = 3,
                        retry_enabled = true,
                        retry_schedule_days = ARRAY[1, 7, 30],
                        max_retries = 3,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE scheme_code = %s
                """
                cursor.execute(
                    update_query,
                    (consent_type, require_otp, require_e_sign, scheme_code)
                )
                print(f"  ✅ Updated: {scheme_code} ({consent_type})")
                updated += 1
            else:
                # Insert new
                insert_query = """
                    INSERT INTO intimation.scheme_intimation_config (
                        scheme_code, auto_intimation_enabled,
                        min_eligibility_score, priority_threshold,
                        consent_type_required, require_otp, require_e_sign,
                        consent_validity_days, max_intimations_per_family,
                        retry_enabled, retry_schedule_days, max_retries,
                        allowed_channels, preferred_channels,
                        created_at, updated_at
                    ) VALUES (
                        %s, true, 0.6, 0.8,
                        %s, %s, %s,
                        365, 3,
                        true, ARRAY[1, 7, 30], 3,
                        ARRAY['sms', 'mobile_app', 'web'], ARRAY['mobile_app', 'sms'],
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                """
                cursor.execute(
                    insert_query,
                    (scheme_code, consent_type, require_otp, require_e_sign)
                )
                print(f"  ✅ Created: {scheme_code} ({consent_type})")
                created += 1
        
        db.connection.commit()
        
        print("\n" + "=" * 80)
        print(f"✅ Scheme configuration initialization complete!")
        print(f"   Created: {created}")
        print(f"   Updated: {updated}")
        print(f"   Total: {len(schemes_df)}")
        print("=" * 80)
        
    except Exception as e:
        db.connection.rollback()
        print(f"\n❌ Error initializing scheme config: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        cursor.close()
        db.disconnect()


if __name__ == '__main__':
    init_scheme_config()

