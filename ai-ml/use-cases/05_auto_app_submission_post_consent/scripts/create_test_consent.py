"""
Create Test Consent Records
Creates test consent records for testing application creation
"""

import sys
from pathlib import Path
import uuid
from datetime import datetime, timedelta
import yaml

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


def create_test_consent():
    """Create test consent records"""
    print("=" * 80)
    print("Creating Test Consent Records")
    print("=" * 80)
    
    # Load configuration
    config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    intimation_db_config = config['external_databases']['intimation']
    eligibility_db_config = config['external_databases']['eligibility']
    
    # Connect to eligibility DB to find eligible families
    eligibility_db = DBConnector(
        host=eligibility_db_config['host'],
        port=eligibility_db_config['port'],
        database=eligibility_db_config['name'],
        user=eligibility_db_config['user'],
        password=eligibility_db_config['password']
    )
    eligibility_db.connect()
    
    # Connect to intimation DB to create consents
    intimation_db = DBConnector(
        host=intimation_db_config['host'],
        port=intimation_db_config['port'],
        database=intimation_db_config['name'],
        user=intimation_db_config['user'],
        password=intimation_db_config['password']
    )
    intimation_db.connect()
    
    try:
        # Find families with eligibility
        print("\n📋 Finding eligible families...")
        query = """
            SELECT DISTINCT family_id, scheme_code
            FROM eligibility.eligibility_snapshots
            WHERE evaluation_status IN ('RULE_ELIGIBLE', 'POSSIBLE_ELIGIBLE')
            LIMIT 5
        """
        
        cursor = eligibility_db.connection.cursor()
        cursor.execute(query)
        families = cursor.fetchall()
        cursor.close()
        
        if not families:
            print("   ⚠️  No eligible families found")
            print("   Please run AI-PLATFORM-03 batch evaluation first:")
            print("   cd ../03_identification_beneficiary")
            print("   python scripts/test_batch_evaluation.py --test batch-all --limit 50")
            return
        
        print(f"   ✅ Found {len(families)} eligible families")
        
        created = 0
        skipped = 0
        
        for family_id, scheme_code in families:
            print(f"\n📋 Processing {scheme_code} for family {str(family_id)[:8]}...")
            
            try:
                # Check if consent already exists
                check_query = """
                    SELECT COUNT(*) 
                    FROM intimation.consent_records
                    WHERE family_id::text = %s
                        AND scheme_code = %s
                        AND status = 'valid'
                        AND consent_value = true
                """
                
                cursor = intimation_db.connection.cursor()
                cursor.execute(check_query, [str(family_id), scheme_code])
                exists = cursor.fetchone()[0] > 0
                
                if exists:
                    print(f"   ⚠️  Consent already exists, skipping")
                    cursor.close()
                    skipped += 1
                    continue
                
                # Create consent
                insert_query = """
                    INSERT INTO intimation.consent_records (
                        family_id,
                        scheme_code,
                        consent_type,
                        level_of_assurance,
                        consent_purpose,
                        status,
                        consent_value,
                        consent_method,
                        consent_channel,
                        valid_from,
                        valid_until,
                        terms_version,
                        created_at,
                        updated_at,
                        created_by
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING consent_id
                """
                
                now = datetime.now()
                cursor.execute(insert_query, (
                    str(family_id),
                    scheme_code,
                    'soft',  # consent_type
                    'MEDIUM',  # level_of_assurance
                    'enrollment',  # consent_purpose
                    'valid',  # status
                    True,  # consent_value
                    'click',  # consent_method
                    'mobile_app',  # consent_channel
                    now,  # valid_from
                    now + timedelta(days=365),  # valid_until (1 year)
                    '1.0',  # terms_version
                    now,  # created_at
                    now,  # updated_at
                    'test_script'  # created_by
                ))
                
                consent_id = cursor.fetchone()[0]
                intimation_db.connection.commit()
                cursor.close()
                
                print(f"   ✅ Consent created (ID: {consent_id})")
                created += 1
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                intimation_db.connection.rollback()
        
        print("\n" + "=" * 80)
        print(f"✅ Consent creation complete!")
        print(f"   Created: {created}")
        print(f"   Skipped: {skipped}")
        print(f"   Total: {len(families)}")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        eligibility_db.disconnect()
        intimation_db.disconnect()


if __name__ == '__main__':
    create_test_consent()
