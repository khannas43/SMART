"""
Initialize Scheme Form Schemas
Creates basic form schemas for schemes in scheme_master
"""

import sys
from pathlib import Path
import yaml
import json
from datetime import datetime

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


# Basic form schema template
BASE_SCHEMA = {
    "type": "object",
    "properties": {
        "full_name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 255,
            "description": "Full name of beneficiary"
        },
        "date_of_birth": {
            "type": "string",
            "format": "date",
            "description": "Date of birth (YYYY-MM-DD)"
        },
        "gender": {
            "type": "string",
            "enum": ["MALE", "FEMALE", "OTHER"],
            "description": "Gender"
        },
        "aadhaar_number": {
            "type": "string",
            "pattern": "^[0-9]{12}$",
            "description": "Aadhaar number (12 digits)"
        },
        "mobile_number": {
            "type": "string",
            "pattern": "^[0-9]{10}$",
            "description": "Mobile number (10 digits)"
        },
        "email": {
            "type": "string",
            "format": "email",
            "description": "Email address"
        },
        "address": {
            "type": "object",
            "properties": {
                "line1": {"type": "string"},
                "line2": {"type": "string"},
                "district": {"type": "string"},
                "block": {"type": "string"},
                "panchayat": {"type": "string"},
                "village": {"type": "string"},
                "pin_code": {
                    "type": "string",
                    "pattern": "^[0-9]{6}$"
                }
            },
            "required": ["line1", "district", "block", "pin_code"]
        },
        "bank_account_number": {
            "type": "string",
            "description": "Bank account number"
        },
        "ifsc_code": {
            "type": "string",
            "pattern": "^[A-Z]{4}0[A-Z0-9]{6}$",
            "description": "IFSC code"
        },
        "bank_name": {
            "type": "string",
            "description": "Bank name"
        }
    },
    "required": ["full_name", "date_of_birth", "gender", "mobile_number"]
}


def init_scheme_form_schemas():
    """Initialize form schemas for all schemes"""
    print("=" * 80)
    print("Initializing Scheme Form Schemas")
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
        
        for scheme_code, scheme_name, category in schemes:
            print(f"\n📋 Processing scheme: {scheme_code} ({scheme_name})")
            
            # Check if schema already exists
            cursor.execute("""
                SELECT COUNT(*) 
                FROM application.scheme_form_schemas 
                WHERE scheme_code = %s AND is_active = true
            """, (scheme_code,))
            
            if cursor.fetchone()[0] > 0:
                print(f"   ⚠️  Skipped (schema already exists)")
                skipped += 1
                continue
            
            # Create schema definition (can be customized per scheme later)
            schema_def = BASE_SCHEMA.copy()
            
            # Add scheme-specific required fields based on category
            if category == "PENSION":
                schema_def["required"].extend(["bank_account_number", "ifsc_code"])
            
            # Extract mandatory fields
            mandatory_fields = schema_def.get("required", [])
            optional_fields = [k for k in schema_def["properties"].keys() if k not in mandatory_fields]
            
            # Insert schema
            cursor.execute("""
                INSERT INTO application.scheme_form_schemas (
                    scheme_code,
                    schema_definition,
                    schema_version,
                    fields,
                    mandatory_fields,
                    optional_fields,
                    validation_rules,
                    semantic_rules,
                    is_active,
                    created_by
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING schema_id
            """, (
                scheme_code,
                json.dumps(schema_def),
                "1.0",
                json.dumps(list(schema_def["properties"].keys())),
                mandatory_fields,
                optional_fields,
                json.dumps({}),  # Empty validation rules for now
                json.dumps({}),  # Empty semantic rules for now
                True,
                "init_scheme_form_schemas"
            ))
            
            schema_id = cursor.fetchone()[0]
            db.connection.commit()
            
            print(f"   ✅ Created schema (ID: {schema_id})")
            print(f"      Mandatory fields: {len(mandatory_fields)}")
            print(f"      Optional fields: {len(optional_fields)}")
            created += 1
        
        cursor.close()
        
        print("\n" + "=" * 80)
        print(f"✅ Schema initialization complete!")
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
    init_scheme_form_schemas()

