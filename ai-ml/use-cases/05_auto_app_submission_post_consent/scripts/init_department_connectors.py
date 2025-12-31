"""
Initialize Department Connectors
Creates placeholder connector configurations for departments
"""

import sys
from pathlib import Path
import yaml
import json
from datetime import datetime

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


# Default connector templates
CONNECTOR_TEMPLATES = {
    "REST": {
        "connector_type": "REST",
        "connector_version": "1.0",
        "payload_format": "JSON",
        "auth_type": "API_KEY",
        "max_retries": 3,
        "retry_delay_seconds": 5,
        "retry_on_status_codes": [500, 502, 503, 504, 408]
    },
    "SOAP": {
        "connector_type": "SOAP",
        "connector_version": "1.0",
        "payload_format": "XML",
        "auth_type": "WSS",
        "max_retries": 3,
        "retry_delay_seconds": 5,
        "retry_on_status_codes": [500, 502, 503, 504, 408]
    },
    "API_SETU": {
        "connector_type": "API_SETU",
        "connector_version": "1.0",
        "payload_format": "JSON",
        "auth_type": "OAUTH2",
        "max_retries": 3,
        "retry_delay_seconds": 5,
        "retry_on_status_codes": [500, 502, 503, 504, 408]
    }
}


def init_department_connectors():
    """Initialize placeholder department connectors"""
    print("=" * 80)
    print("Initializing Department Connectors")
    print("=" * 80)
    
    # Load configuration
    base_dir = Path(__file__).parent.parent
    config_path = base_dir / "config" / "db_config.yaml"
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
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
        
        # Create default REST connector (generic)
        connectors = [
            {
                "connector_name": "DEFAULT_REST",
                "department_name": "Generic REST API",
                "description": "Default REST connector for department APIs",
                **CONNECTOR_TEMPLATES["REST"],
                "base_url": "https://api.example.gov.in/v1",
                "endpoint_path": "/applications/submit",
                "auth_config": json.dumps({"api_key": "CHANGE_ME"}),
                "payload_template": json.dumps({
                    "application_id": "{{application_id}}",
                    "scheme_code": "{{scheme_code}}",
                    "beneficiary": "{{beneficiary_data}}"
                }),
                "response_schema": json.dumps({
                    "application_number": "string",
                    "status": "string",
                    "message": "string"
                })
            },
            {
                "connector_name": "DEFAULT_SOAP",
                "department_name": "Generic SOAP Service",
                "description": "Default SOAP connector for department web services",
                **CONNECTOR_TEMPLATES["SOAP"],
                "base_url": "https://services.example.gov.in",
                "wsdl_url": "https://services.example.gov.in/ApplicationService?wsdl",
                "auth_config": json.dumps({"username": "CHANGE_ME", "password": "CHANGE_ME"}),
                "payload_template": json.dumps({}),
                "response_schema": json.dumps({})
            },
            {
                "connector_name": "API_SETU_GENERIC",
                "department_name": "API Setu Gateway",
                "description": "Generic API Setu connector for government APIs",
                **CONNECTOR_TEMPLATES["API_SETU"],
                "base_url": "https://apisetu.gov.in/api",
                "endpoint_path": "/applications",
                "api_setu_config": json.dumps({
                    "api_key": "CHANGE_ME",
                    "client_id": "CHANGE_ME",
                    "client_secret": "CHANGE_ME"
                }),
                "auth_config": json.dumps({"client_id": "CHANGE_ME", "client_secret": "CHANGE_ME"}),
                "payload_template": json.dumps({}),
                "response_schema": json.dumps({})
            }
        ]
        
        created = 0
        skipped = 0
        
        for connector_data in connectors:
            connector_name = connector_data["connector_name"]
            print(f"\n📋 Processing connector: {connector_name}")
            
            # Check if connector already exists
            cursor.execute("""
                SELECT COUNT(*) 
                FROM application.department_connectors 
                WHERE connector_name = %s
            """, (connector_name,))
            
            if cursor.fetchone()[0] > 0:
                print(f"   ⚠️  Skipped (connector already exists)")
                skipped += 1
                continue
            
            # Insert connector
            cursor.execute("""
                INSERT INTO application.department_connectors (
                    connector_name,
                    department_name,
                    connector_type,
                    connector_version,
                    base_url,
                    endpoint_path,
                    wsdl_url,
                    api_setu_config,
                    auth_type,
                    auth_config,
                    payload_format,
                    payload_template,
                    response_schema,
                    max_retries,
                    retry_delay_seconds,
                    retry_on_status_codes,
                    is_active,
                    is_test_mode,
                    description,
                    created_by
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING connector_id
            """, (
                connector_data["connector_name"],
                connector_data.get("department_name"),
                connector_data["connector_type"],
                connector_data["connector_version"],
                connector_data.get("base_url"),
                connector_data.get("endpoint_path"),
                connector_data.get("wsdl_url"),
                connector_data.get("api_setu_config"),
                connector_data["auth_type"],
                connector_data.get("auth_config"),
                connector_data["payload_format"],
                connector_data.get("payload_template"),
                connector_data.get("response_schema"),
                connector_data["max_retries"],
                connector_data["retry_delay_seconds"],
                connector_data["retry_on_status_codes"],
                True,  # is_active
                True,  # is_test_mode (default to test mode)
                connector_data.get("description"),
                "init_department_connectors"
            ))
            
            connector_id = cursor.fetchone()[0]
            db.connection.commit()
            
            print(f"   ✅ Created connector (ID: {connector_id})")
            print(f"      Type: {connector_data['connector_type']}")
            print(f"      Auth: {connector_data['auth_type']}")
            created += 1
        
        cursor.close()
        
        print("\n" + "=" * 80)
        print(f"✅ Department connectors initialization complete!")
        print(f"   Created: {created}")
        print(f"   Skipped: {skipped}")
        print(f"   Total: {len(connectors)}")
        print("=" * 80)
        print("\n⚠️  Note: Please update connector configurations with actual:")
        print("   - API endpoints and URLs")
        print("   - Authentication credentials")
        print("   - Payload templates and response schemas")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.connection.rollback()
        raise
    finally:
        db.disconnect()


if __name__ == "__main__":
    init_department_connectors()

