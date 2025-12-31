"""
Enhance Form Schemas with Detailed Field Definitions
Adds comprehensive field definitions and validation rules to form schemas
"""

import sys
from pathlib import Path
import yaml
import json

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


def enhance_form_schemas():
    """Enhance form schemas with detailed field definitions"""
    print("=" * 80)
    print("Enhancing Form Schemas")
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
        
        # Standard form fields that most schemes need
        standard_fields = [
            {
                'field_name': 'full_name',
                'field_type': 'string',
                'required': True,
                'min_length': 3,
                'max_length': 100,
                'pattern': '^[a-zA-Z\\s]+$',
                'description': 'Full name of applicant'
            },
            {
                'field_name': 'date_of_birth',
                'field_type': 'date',
                'required': True,
                'format': 'YYYY-MM-DD',
                'description': 'Date of birth'
            },
            {
                'field_name': 'age',
                'field_type': 'integer',
                'required': True,
                'min': 0,
                'max': 120,
                'description': 'Age of applicant'
            },
            {
                'field_name': 'gender',
                'field_type': 'string',
                'required': True,
                'enum': ['MALE', 'FEMALE', 'OTHER'],
                'description': 'Gender'
            },
            {
                'field_name': 'aadhaar_number',
                'field_type': 'string',
                'required': True,
                'pattern': '^[0-9]{12}$',
                'description': '12-digit Aadhaar number'
            },
            {
                'field_name': 'jan_aadhaar',
                'field_type': 'string',
                'required': False,
                'pattern': '^[0-9]+$',
                'description': 'Jan Aadhaar number'
            },
            {
                'field_name': 'caste_category',
                'field_type': 'string',
                'required': True,
                'enum': ['GEN', 'OBC', 'SC', 'ST'],
                'description': 'Caste category'
            },
            {
                'field_name': 'address_line1',
                'field_type': 'string',
                'required': True,
                'max_length': 200,
                'description': 'Address line 1'
            },
            {
                'field_name': 'address_line2',
                'field_type': 'string',
                'required': False,
                'max_length': 200,
                'description': 'Address line 2'
            },
            {
                'field_name': 'village',
                'field_type': 'string',
                'required': True,
                'max_length': 100,
                'description': 'Village'
            },
            {
                'field_name': 'block',
                'field_type': 'string',
                'required': True,
                'max_length': 100,
                'description': 'Block/Taluka'
            },
            {
                'field_name': 'district',
                'field_type': 'string',
                'required': True,
                'max_length': 100,
                'description': 'District'
            },
            {
                'field_name': 'pincode',
                'field_type': 'string',
                'required': True,
                'pattern': '^[0-9]{6}$',
                'description': '6-digit PIN code'
            },
            {
                'field_name': 'contact_mobile',
                'field_type': 'string',
                'required': True,
                'pattern': '^[0-9]{10}$',
                'description': '10-digit mobile number'
            },
            {
                'field_name': 'contact_email',
                'field_type': 'string',
                'required': False,
                'format': 'email',
                'description': 'Email address'
            },
            {
                'field_name': 'bank_account_number',
                'field_type': 'string',
                'required': True,
                'pattern': '^[0-9]{9,18}$',
                'description': 'Bank account number'
            },
            {
                'field_name': 'ifsc_code',
                'field_type': 'string',
                'required': True,
                'pattern': '^[A-Z]{4}0[A-Z0-9]{6}$',
                'description': 'IFSC code'
            },
            {
                'field_name': 'bank_name',
                'field_type': 'string',
                'required': False,
                'max_length': 100,
                'description': 'Bank name'
            },
            {
                'field_name': 'bpl_status',
                'field_type': 'string',
                'required': False,
                'enum': ['Yes', 'No'],
                'description': 'Below Poverty Line status'
            },
            {
                'field_name': 'income_band',
                'field_type': 'string',
                'required': False,
                'enum': ['BELOW_POVERTY_LINE', 'ABOVE_POVERTY_LINE', 'MIDDLE_CLASS'],
                'description': 'Income band'
            }
        ]
        
        # Get existing schemas
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT schema_id, scheme_code, schema_definition
            FROM application.scheme_form_schemas
            WHERE is_active = true
        """)
        schemas = cursor.fetchall()
        cursor.close()
        
        if not schemas:
            print("⚠️  No active form schemas found. Run init_scheme_form_schemas.py first.")
            return
        
        print(f"\n📋 Found {len(schemas)} form schemas")
        
        updated_count = 0
        
        for schema_id, scheme_code, schema_def in schemas:
            print(f"\n   Processing {scheme_code}...")
            
            # Parse existing schema
            if isinstance(schema_def, str):
                try:
                    schema = json.loads(schema_def)
                except:
                    schema = {'type': 'object', 'properties': {}, 'required': []}
            else:
                schema = schema_def if schema_def else {'type': 'object', 'properties': {}, 'required': []}
            
            # Ensure structure exists
            if 'properties' not in schema:
                schema['properties'] = {}
            if 'required' not in schema:
                schema['required'] = []
            
            # Add/update standard fields
            fields_added = 0
            for field in standard_fields:
                field_name = field['field_name']
                
                # Build field definition
                field_def = {
                    'type': field['field_type'],
                    'title': field['field_name'].replace('_', ' ').title(),
                    'description': field.get('description', '')
                }
                
                # Add constraints
                if 'min_length' in field:
                    field_def['minLength'] = field['min_length']
                if 'max_length' in field:
                    field_def['maxLength'] = field['max_length']
                if 'min' in field:
                    field_def['minimum'] = field['min']
                if 'max' in field:
                    field_def['maximum'] = field['max']
                if 'pattern' in field:
                    field_def['pattern'] = field['pattern']
                if 'format' in field:
                    field_def['format'] = field['format']
                if 'enum' in field:
                    field_def['enum'] = field['enum']
                
                # Add to schema
                schema['properties'][field_name] = field_def
                
                # Add to required if needed
                if field.get('required', False):
                    if field_name not in schema['required']:
                        schema['required'].append(field_name)
                
                fields_added += 1
            
            # Update schema definition
            cursor = db.connection.cursor()
            cursor.execute("""
                UPDATE application.scheme_form_schemas
                SET schema_definition = %s,
                    fields = %s,
                    mandatory_fields = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE schema_id = %s
            """, [
                json.dumps(schema),
                json.dumps(list(schema['properties'].keys())),
                schema['required'],
                schema_id
            ])
            cursor.close()
            updated_count += 1
            print(f"      ✅ Updated schema with {fields_added} fields")
        
        db.connection.commit()
        
        print("\n" + "=" * 80)
        print(f"✅ Form schema enhancement complete!")
        print(f"   Updated: {updated_count} schemas")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.connection.rollback()
    finally:
        db.disconnect()


if __name__ == '__main__':
    enhance_form_schemas()

