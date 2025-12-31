"""
View Field Mappings and Form Schemas
Quick script to see what mappings and schemas have been configured
"""

import sys
from pathlib import Path
import yaml
import json

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


def view_configurations():
    """View current field mappings and form schemas"""
    print("=" * 80)
    print("Field Mappings and Form Schemas Summary")
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
        
        # Get field mappings summary
        print("\n📋 Field Mappings Summary")
        print("-" * 80)
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT 
                scheme_code,
                COUNT(*) as mapping_count,
                COUNT(DISTINCT mapping_type) as mapping_types_count
            FROM application.scheme_field_mappings
            WHERE is_active = true
            GROUP BY scheme_code
            ORDER BY scheme_code
        """)
        mappings = cursor.fetchall()
        cursor.close()
        
        if mappings:
            print(f"{'Scheme Code':<30} {'Mappings':<15} {'Mapping Types'}")
            print("-" * 80)
            for scheme_code, count, types_count in mappings:
                print(f"{scheme_code:<30} {count:<15} {types_count}")
        else:
            print("   ⚠️  No field mappings found")
        
        # Get form schemas summary
        print("\n📋 Form Schemas Summary")
        print("-" * 80)
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT 
                scheme_code,
                schema_version,
                jsonb_array_length(fields) as field_count,
                array_length(mandatory_fields, 1) as mandatory_count,
                is_active
            FROM application.scheme_form_schemas
            WHERE is_active = true
            ORDER BY scheme_code
        """)
        schemas = cursor.fetchall()
        cursor.close()
        
        if schemas:
            print(f"{'Scheme Code':<30} {'Version':<10} {'Fields':<10} {'Mandatory':<12} {'Status'}")
            print("-" * 80)
            for scheme_code, version, field_count, mandatory_count, is_active in schemas:
                status = "✅ Active" if is_active else "❌ Inactive"
                mandatory = mandatory_count if mandatory_count else 0
                fields = field_count if field_count else 0
                print(f"{scheme_code:<30} {version or 'N/A':<10} {fields:<10} {mandatory:<12} {status}")
        else:
            print("   ⚠️  No form schemas found")
        
        # Get submission modes summary
        print("\n📋 Submission Modes Summary")
        print("-" * 80)
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT 
                scheme_code,
                default_mode,
                allow_auto_submission,
                require_citizen_review
            FROM application.submission_modes_config
            ORDER BY scheme_code
        """)
        modes = cursor.fetchall()
        cursor.close()
        
        if modes:
            print(f"{'Scheme Code':<30} {'Mode':<15} {'Auto Allowed':<15} {'Review Required'}")
            print("-" * 80)
            for scheme_code, mode, auto_allowed, review_required in modes:
                auto = "✅ Yes" if auto_allowed else "❌ No"
                review = "✅ Yes" if review_required else "❌ No"
                print(f"{scheme_code:<30} {mode:<15} {auto:<15} {review}")
        else:
            print("   ⚠️  No submission mode configurations found")
        
        # Get department connectors summary
        print("\n📋 Department Connectors Summary")
        print("-" * 80)
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT 
                connector_name,
                connector_type,
                auth_type,
                is_active
            FROM application.department_connectors
            ORDER BY connector_id
        """)
        connectors = cursor.fetchall()
        cursor.close()
        
        if connectors:
            print(f"{'Connector Name':<30} {'Type':<15} {'Auth Type':<15} {'Status'}")
            print("-" * 80)
            for name, conn_type, auth_type, is_active in connectors:
                status = "✅ Active" if is_active else "❌ Inactive"
                print(f"{name:<30} {conn_type:<15} {auth_type:<15} {status}")
        else:
            print("   ⚠️  No department connectors found")
        
        print("\n" + "=" * 80)
        print("✅ Configuration summary complete!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.disconnect()


if __name__ == '__main__':
    view_configurations()

