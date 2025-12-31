"""
Create Sample Applications for Testing
Creates sample application data for viewing in the web interface
"""

import sys
from pathlib import Path
import yaml
from datetime import datetime, timedelta
import uuid
import json

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


def create_sample_applications():
    """Create sample applications with various statuses"""
    print("=" * 80)
    print("Creating Sample Applications")
    print("=" * 80)
    
    # Load config
    config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Connect to databases
    db_config = config['database']
    db = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    
    # Get eligibility database
    eligibility_config = config.get('external_databases', {}).get('eligibility')
    if eligibility_config:
        eligibility_db = DBConnector(
            host=eligibility_config['host'],
            port=eligibility_config['port'],
            database=eligibility_config['name'],
            user=eligibility_config['user'],
            password=eligibility_config['password']
        )
    else:
        eligibility_db = None
    
    try:
        db.connect()
        if eligibility_db:
            eligibility_db.connect()
        
        # Get consent records or create test family IDs
        print("\n📋 Getting test data...")
        
        # Try to get existing consent records
        consent_query = """
            SELECT DISTINCT ON (family_id, scheme_code)
                family_id, scheme_code, consent_id
            FROM intimation.consent_records
            WHERE status = 'valid' AND consent_value = true
            ORDER BY family_id, scheme_code, created_at DESC
            LIMIT 10
        """
        
        cursor = db.connection.cursor()
        cursor.execute(consent_query)
        consents = cursor.fetchall()
        cursor.close()
        
        if not consents:
            print("   ⚠️  No consent records found, creating test family IDs")
            # Create test data with fake family IDs
            test_data = [
                (str(uuid.uuid4()), 'CHIRANJEEVI', None),
                (str(uuid.uuid4()), 'NREGA', None),
                (str(uuid.uuid4()), 'MAHILA_SHAKTI', None),
                (str(uuid.uuid4()), 'CHIRANJEEVI', None),
                (str(uuid.uuid4()), 'OLD_AGE_PENSION', None),
            ]
        else:
            print(f"   ✅ Found {len(consents)} consent records")
            test_data = [(str(c[0]), c[1], c[2]) for c in consents]
            # Add some test data without consent
            for i in range(2):
                test_data.append((str(uuid.uuid4()), 'CHIRANJEEVI', None))
        
        # Create applications with different statuses
        statuses = [
            ('creating', 'auto', 0.75),
            ('mapped', 'auto', 0.82),
            ('validated', 'review', 0.65),
            ('submitted', 'auto', 0.90),
            ('submitted', 'review', 0.88),
            ('pending_review', 'review', 0.72),
            ('error', 'auto', 0.45),
            ('mapped', 'auto', 0.78),
        ]
        
        application_ids = []
        
        print("\n📝 Creating sample applications...")
        for i, (family_id, scheme_code, consent_id) in enumerate(test_data[:8]):
            status, mode, score = statuses[i % len(statuses)]
            
            # Get eligibility snapshot ID if available
            snapshot_id = None
            if eligibility_db:
                snapshot_query = """
                    SELECT snapshot_id
                    FROM eligibility.eligibility_snapshots
                    WHERE family_id::text = %s AND scheme_code = %s
                    ORDER BY evaluation_timestamp DESC
                    LIMIT 1
                """
                cursor = eligibility_db.connection.cursor()
                cursor.execute(snapshot_query, [family_id, scheme_code])
                row = cursor.fetchone()
                cursor.close()
                if row:
                    snapshot_id = row[0]
            
            # Create application
            app_query = """
                INSERT INTO application.applications (
                    family_id, scheme_code, consent_id, eligibility_snapshot_id,
                    eligibility_score, eligibility_status, status, submission_mode,
                    created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING application_id
            """
            
            created_at = datetime.now() - timedelta(hours=i)
            
            cursor = db.connection.cursor()
            cursor.execute(app_query, [
                family_id, scheme_code, consent_id, snapshot_id,
                score, 'RULE_ELIGIBLE', status, mode, created_at
            ])
            application_id = cursor.fetchone()[0]
            application_ids.append((application_id, status, mode))
            
            # Create some application fields
            if status in ['mapped', 'validated', 'submitted', 'pending_review']:
                fields = [
                    ('full_name', 'John Doe', 'GR'),
                    ('date_of_birth', '1980-01-15', 'GR'),
                    ('address_line1', '123 Main Street', 'GR'),
                    ('contact_mobile', '9876543210', 'CITIZEN'),
                    ('bank_account', '1234567890123456', 'GR'),
                ]
                
                for field_name, field_value, source_type in fields:
                    field_query = """
                        INSERT INTO application.application_fields (
                            application_id, field_name, field_value, 
                            field_type, source_type
                        ) VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(field_query, [
                        application_id, field_name, json.dumps(field_value), 
                        'string', source_type
                    ])
            
            cursor.close()
            print(f"   ✅ Created application {application_id}: {scheme_code} - {status} (score: {score:.2f})")
        
        db.connection.commit()
        
        # Create submissions for submitted applications
        print("\n📤 Creating sample submissions...")
        submission_count = 0
        
        for application_id, status, mode in application_ids:
            if status == 'submitted':
                # Get scheme code
                cursor = db.connection.cursor()
                cursor.execute("SELECT scheme_code FROM application.applications WHERE application_id = %s", [application_id])
                scheme_code = cursor.fetchone()[0]
                cursor.close()
                
                # Create submission record
                submission_query = """
                    INSERT INTO application.application_submissions (
                        application_id, submission_mode, connector_type,
                        submission_payload, payload_format,
                        department_application_number, response_status_code,
                        response_status, submitted_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                payload = {
                    'family_id': str(uuid.uuid4()),
                    'scheme_code': scheme_code,
                    'full_name': 'John Doe',
                    'application_date': datetime.now().isoformat()
                }
                
                response_status = 'success' if mode == 'auto' else 'pending'
                dept_app_number = f"DEPT-{scheme_code}-{application_id}" if mode == 'auto' else None
                response_code = 200 if mode == 'auto' else None
                
                cursor = db.connection.cursor()
                cursor.execute(submission_query, [
                    application_id, mode, 'REST',
                    json.dumps(payload), 'JSON',
                    dept_app_number, response_code, response_status,
                    datetime.now() - timedelta(hours=submission_count)
                ])
                cursor.close()
                submission_count += 1
                print(f"   ✅ Created submission for application {application_id}")
        
        db.connection.commit()
        
        print("\n" + "=" * 80)
        print("✅ Sample data creation complete!")
        print("=" * 80)
        print(f"\n📊 Summary:")
        print(f"   Applications created: {len(application_ids)}")
        print(f"   Submissions created: {submission_count}")
        print(f"\n🌐 View at: http://localhost:5001/ai05")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.connection.rollback()
    finally:
        db.disconnect()
        if eligibility_db:
            eligibility_db.disconnect()


if __name__ == '__main__':
    create_sample_applications()

