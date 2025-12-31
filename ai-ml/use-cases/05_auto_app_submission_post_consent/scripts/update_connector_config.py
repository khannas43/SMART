"""
Update Department Connector Configuration
Helper script to update connector endpoints and credentials when API information is available
"""

import sys
from pathlib import Path
import yaml
import json

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


def update_connector():
    """Interactive script to update connector configuration"""
    print("=" * 80)
    print("Update Department Connector Configuration")
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
    
    try:
        db.connect()
        
        # List existing connectors
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT connector_id, connector_name, connector_type, endpoint_url, auth_type, is_active
            FROM application.department_connectors
            ORDER BY connector_id
        """)
        connectors = cursor.fetchall()
        cursor.close()
        
        if not connectors:
            print("\n⚠️  No connectors found")
            return
        
        print("\n📋 Available Connectors:")
        print("-" * 80)
        print(f"{'ID':<5} {'Name':<30} {'Type':<15} {'Current Endpoint'}")
        print("-" * 80)
        for conn_id, name, conn_type, endpoint, auth_type, is_active in connectors:
            endpoint_display = endpoint[:50] + "..." if endpoint and len(endpoint) > 50 else (endpoint or "Not set")
            status = "✅" if is_active else "❌"
            print(f"{conn_id:<5} {name:<30} {conn_type:<15} {endpoint_display}")
        
        # Get connector ID to update
        print("\n" + "-" * 80)
        connector_id = input("\nEnter connector ID to update (or 'q' to quit): ").strip()
        
        if connector_id.lower() == 'q':
            print("Cancelled.")
            return
        
        try:
            connector_id = int(connector_id)
        except ValueError:
            print("❌ Invalid connector ID")
            return
        
        # Get connector details
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT connector_name, connector_type, base_url, endpoint_path, 
                   wsdl_url, auth_type, auth_config, payload_template
            FROM application.department_connectors
            WHERE connector_id = %s
        """, [connector_id])
        row = cursor.fetchone()
        cursor.close()
        
        if not row:
            print(f"❌ Connector ID {connector_id} not found")
            return
        
        name, conn_type, current_base_url, current_endpoint_path, current_wsdl_url, auth_type, auth_config, payload_template = row
        
        current_endpoint = f"{current_base_url or ''}{current_endpoint_path or ''}" if current_base_url or current_endpoint_path else ""
        
        print(f"\n📝 Updating connector: {name} ({conn_type})")
        print(f"   Current base URL: {current_base_url or 'Not set'}")
        print(f"   Current endpoint path: {current_endpoint_path or 'Not set'}")
        if current_wsdl_url:
            print(f"   Current WSDL URL: {current_wsdl_url}")
        print(f"   Auth type: {auth_type}")
        
        # Get new values
        print("\n" + "-" * 80)
        print("Enter new values (press Enter to keep current value):")
        print("-" * 80)
        
        new_base_url = input(f"\nBase URL [{current_base_url or ''}]: ").strip()
        if not new_base_url:
            new_base_url = current_base_url
        
        new_endpoint_path = input(f"\nEndpoint Path [{current_endpoint_path or ''}]: ").strip()
        if not new_endpoint_path:
            new_endpoint_path = current_endpoint_path
        
        new_wsdl_url = None
        if conn_type == 'SOAP':
            new_wsdl_url = input(f"\nWSDL URL [{current_wsdl_url or ''}]: ").strip()
            if not new_wsdl_url:
                new_wsdl_url = current_wsdl_url
        
        # Auth config
        if auth_config:
            try:
                if isinstance(auth_config, str):
                    current_auth = json.loads(auth_config)
                else:
                    current_auth = auth_config
            except:
                current_auth = {}
        else:
            current_auth = {}
        
        print(f"\nCurrent auth config: {json.dumps(current_auth, indent=2)}")
        print("\nAuth configuration options:")
        print("  1. API Key: {\"api_key\": \"your_key\"}")
        print("  2. OAuth2: {\"client_id\": \"...\", \"client_secret\": \"...\", \"token_url\": \"...\"}")
        print("  3. Basic: {\"username\": \"...\", \"password\": \"...\"}")
        
        auth_input = input("\nNew auth config (JSON) or Enter to keep: ").strip()
        if auth_input:
            try:
                new_auth_config = json.loads(auth_input)
            except json.JSONDecodeError:
                print("❌ Invalid JSON format")
                return
        else:
            new_auth_config = current_auth
        
        # Confirm
        print("\n" + "-" * 80)
        print("Summary of changes:")
        print(f"  Base URL: {new_base_url}")
        print(f"  Endpoint Path: {new_endpoint_path}")
        if new_wsdl_url:
            print(f"  WSDL URL: {new_wsdl_url}")
        print(f"  Auth Config: {json.dumps(new_auth_config, indent=2)}")
        print("-" * 80)
        
        confirm = input("\nConfirm update? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("Cancelled.")
            return
        
        # Update
        cursor = db.connection.cursor()
        if conn_type == 'SOAP':
            cursor.execute("""
                UPDATE application.department_connectors
                SET 
                    base_url = %s,
                    endpoint_path = %s,
                    wsdl_url = %s,
                    auth_config = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE connector_id = %s
            """, [
                new_base_url if new_base_url else None,
                new_endpoint_path if new_endpoint_path else None,
                new_wsdl_url if new_wsdl_url else None,
                json.dumps(new_auth_config) if new_auth_config else None,
                connector_id
            ])
        else:
            cursor.execute("""
                UPDATE application.department_connectors
                SET 
                    base_url = %s,
                    endpoint_path = %s,
                    auth_config = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE connector_id = %s
            """, [
                new_base_url if new_base_url else None,
                new_endpoint_path if new_endpoint_path else None,
                json.dumps(new_auth_config) if new_auth_config else None,
                connector_id
            ])
        cursor.close()
        
        db.connection.commit()
        
        print("\n✅ Connector configuration updated successfully!")
        print(f"   Connector: {name}")
        print(f"   Base URL: {new_base_url}")
        print(f"   Endpoint Path: {new_endpoint_path}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.connection.rollback()
    finally:
        db.disconnect()


if __name__ == '__main__':
    update_connector()

