"""
Create Mock Department Connectors
Creates mock/test connectors for testing without real department APIs
"""

import sys
from pathlib import Path
import yaml
import json

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


def create_mock_connectors():
    """Create mock connectors for testing"""
    print("=" * 80)
    print("Creating Mock Department Connectors")
    print("=" * 80)
    
    # Load config
    config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    db_config = config['database']
    db = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    
    # Mock connector configurations
    mock_connectors = [
        {
            'connector_name': 'MOCK_REST_TEST',
            'connector_type': 'REST',
            'base_url': 'http://localhost:8080/mock-api',
            'endpoint_path': '/applications',
            'auth_type': 'API_KEY',
            'auth_config': {
                'api_key': 'mock_api_key_for_testing',
                'header_name': 'X-API-Key'
            },
            'payload_template': {
                'application_id': '{{application_id}}',
                'scheme_code': '{{scheme_code}}',
                'applicant': {
                    'name': '{{full_name}}',
                    'dob': '{{date_of_birth}}',
                    'aadhaar': '{{aadhaar_number}}'
                }
            },
            'payload_format': 'JSON',
            'description': 'Mock REST connector for testing (localhost)',
            'is_test_mode': True
        },
        {
            'connector_name': 'MOCK_SOAP_TEST',
            'connector_type': 'SOAP',
            'base_url': 'http://localhost:8080/mock-api',
            'endpoint_path': '/soap',
            'wsdl_url': 'http://localhost:8080/mock-api/soap?wsdl',
            'auth_type': 'WSS',
            'auth_config': {
                'username': 'mock_user',
                'password': 'mock_password'
            },
            'payload_template': {
                'soap_action': 'SubmitApplication',
                'body': {
                    'applicationId': '{{application_id}}',
                    'schemeCode': '{{scheme_code}}'
                }
            },
            'payload_format': 'XML',
            'description': 'Mock SOAP connector for testing (localhost)',
            'is_test_mode': True
        },
        {
            'connector_name': 'MOCK_API_SETU_TEST',
            'connector_type': 'API_SETU',
            'base_url': 'http://localhost:8080/mock-api',
            'endpoint_path': '/setu',
            'api_setu_config': {
                'api_version': '1.0',
                'gateway_id': 'MOCK_GATEWAY'
            },
            'auth_type': 'OAUTH2',
            'auth_config': {
                'token_url': 'http://localhost:8080/mock-api/oauth/token',
                'client_id': 'mock_client_id',
                'client_secret': 'mock_client_secret',
                'scope': 'application.submit'
            },
            'payload_template': {
                'api_version': '1.0',
                'application': {
                    'id': '{{application_id}}',
                    'scheme': '{{scheme_code}}'
                }
            },
            'payload_format': 'JSON',
            'description': 'Mock API Setu connector for testing (localhost)',
            'is_test_mode': True
        }
    ]
    
    try:
        db.connect()
        
        print("\n📝 Creating mock connectors...")
        created_count = 0
        skipped_count = 0
        
        for mock_conn in mock_connectors:
            # Check if already exists
            cursor = db.connection.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM application.department_connectors
                WHERE connector_name = %s
            """, [mock_conn['connector_name']])
            exists = cursor.fetchone()[0] > 0
            cursor.close()
            
            if exists:
                print(f"   ⚠️  {mock_conn['connector_name']} already exists, skipping...")
                skipped_count += 1
                continue
            
            # Create connector
            cursor = db.connection.cursor()
            cursor.execute("""
                INSERT INTO application.department_connectors (
                    connector_name, connector_type, base_url, endpoint_path,
                    wsdl_url, api_setu_config, auth_type, auth_config,
                    payload_format, payload_template, description,
                    is_active, is_test_mode
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                mock_conn['connector_name'],
                mock_conn['connector_type'],
                mock_conn.get('base_url'),
                mock_conn.get('endpoint_path'),
                mock_conn.get('wsdl_url'),
                json.dumps(mock_conn.get('api_setu_config')) if mock_conn.get('api_setu_config') else None,
                mock_conn['auth_type'],
                json.dumps(mock_conn['auth_config']),
                mock_conn.get('payload_format', 'JSON'),
                json.dumps(mock_conn['payload_template']),
                mock_conn.get('description', ''),
                True,  # Active for testing
                mock_conn.get('is_test_mode', True)
            ])
            cursor.close()
            created_count += 1
            print(f"   ✅ Created: {mock_conn['connector_name']} ({mock_conn['connector_type']})")
        
        db.connection.commit()
        
        print("\n" + "=" * 80)
        print(f"✅ Mock connector creation complete!")
        print(f"   Created: {created_count}")
        print(f"   Skipped: {skipped_count}")
        print("\n💡 Note: These are mock connectors for testing.")
        print("   They use localhost endpoints. For real testing,")
        print("   you'll need to update with actual department API endpoints.")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.connection.rollback()
    finally:
        db.disconnect()


if __name__ == '__main__':
    create_mock_connectors()

