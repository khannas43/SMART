"""
Create Field Mapping Rules Template
Generates field mapping configurations for schemes based on standard mappings
"""

import sys
from pathlib import Path
import yaml
import json

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


def create_field_mappings():
    """Create field mapping rules for common schemes"""
    print("=" * 80)
    print("Creating Field Mapping Rules")
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
        
        # Get active schemes
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT scheme_code, scheme_name, category
            FROM public.scheme_master
            WHERE status = 'active'
            ORDER BY scheme_code
        """)
        schemes = cursor.fetchall()
        cursor.close()
        
        if not schemes:
            print("⚠️  No active schemes found")
            return
        
        print(f"\n📋 Found {len(schemes)} active schemes")
        
        # Standard field mappings (common to most schemes)
        standard_mappings = [
            {
                'target_field': 'full_name',
                'source_type': 'GR',
                'source_path': 'GR.first_name + " " + GR.last_name',
                'mapping_type': 'concatenated',
                'priority': 1,
                'description': 'Full name from first and last name'
            },
            {
                'target_field': 'date_of_birth',
                'source_type': 'GR',
                'source_path': 'GR.date_of_birth',
                'mapping_type': 'direct',
                'priority': 1,
                'description': 'Date of birth from Golden Record'
            },
            {
                'target_field': 'gender',
                'source_type': 'GR',
                'source_path': 'GR.gender',
                'mapping_type': 'direct',
                'priority': 1,
                'description': 'Gender from Golden Record'
            },
            {
                'target_field': 'age',
                'source_type': 'DERIVED',
                'source_path': 'calculate_age(GR.date_of_birth)',
                'mapping_type': 'derived',
                'priority': 1,
                'description': 'Age calculated from date of birth'
            },
            {
                'target_field': 'aadhaar_number',
                'source_type': 'GR',
                'source_path': 'GR.aadhaar_number',
                'mapping_type': 'direct',
                'priority': 1,
                'description': 'Aadhaar number from Golden Record'
            },
            {
                'target_field': 'jan_aadhaar',
                'source_type': 'GR',
                'source_path': 'GR.jan_aadhaar',
                'mapping_type': 'direct',
                'priority': 1,
                'description': 'Jan Aadhaar number from Golden Record'
            },
            {
                'target_field': 'caste_category',
                'source_type': 'GR',
                'source_path': 'GR.caste_category',
                'mapping_type': 'direct',
                'priority': 1,
                'description': 'Caste category (GEN/OBC/SC/ST) from Golden Record'
            },
            {
                'target_field': 'address_line1',
                'source_type': 'GR',
                'source_path': 'GR.address_line1',
                'mapping_type': 'direct',
                'priority': 1,
                'description': 'Address line 1 from Golden Record'
            },
            {
                'target_field': 'address_line2',
                'source_type': 'GR',
                'source_path': 'GR.address_line2',
                'mapping_type': 'direct',
                'priority': 2,
                'description': 'Address line 2 from Golden Record'
            },
            {
                'target_field': 'village',
                'source_type': 'GR',
                'source_path': 'GR.village',
                'mapping_type': 'direct',
                'priority': 1,
                'description': 'Village from Golden Record'
            },
            {
                'target_field': 'block',
                'source_type': 'GR',
                'source_path': 'GR.block',
                'mapping_type': 'direct',
                'priority': 1,
                'description': 'Block from Golden Record'
            },
            {
                'target_field': 'district',
                'source_type': 'GR',
                'source_path': 'GR.district',
                'mapping_type': 'direct',
                'priority': 1,
                'description': 'District from Golden Record'
            },
            {
                'target_field': 'pincode',
                'source_type': 'GR',
                'source_path': 'GR.pincode',
                'mapping_type': 'direct',
                'priority': 1,
                'description': 'PIN code from Golden Record'
            },
            {
                'target_field': 'contact_mobile',
                'source_type': 'GR',
                'source_path': 'GR.mobile_number',
                'mapping_type': 'direct',
                'priority': 1,
                'description': 'Mobile number from Golden Record'
            },
            {
                'target_field': 'contact_email',
                'source_type': 'GR',
                'source_path': 'GR.email',
                'mapping_type': 'direct',
                'priority': 2,
                'description': 'Email from Golden Record'
            },
            {
                'target_field': 'bank_account_number',
                'source_type': 'GR',
                'source_path': 'GR.bank_account_number',
                'mapping_type': 'direct',
                'priority': 1,
                'description': 'Bank account number from Golden Record'
            },
            {
                'target_field': 'ifsc_code',
                'source_type': 'GR',
                'source_path': 'GR.ifsc_code',
                'mapping_type': 'direct',
                'priority': 1,
                'description': 'IFSC code from Golden Record'
            },
            {
                'target_field': 'bank_name',
                'source_type': 'GR',
                'source_path': 'GR.bank_name',
                'mapping_type': 'direct',
                'priority': 2,
                'description': 'Bank name from Golden Record'
            },
            {
                'target_field': 'bpl_status',
                'source_type': 'PROFILE_360',
                'source_path': 'PROFILE_360.income_band',
                'mapping_type': 'derived',
                'transformation_expression': '"Yes" if income_band == "BELOW_POVERTY_LINE" else "No"',
                'priority': 1,
                'description': 'BPL status derived from income band'
            },
            {
                'target_field': 'income_band',
                'source_type': 'PROFILE_360',
                'source_path': 'PROFILE_360.income_band',
                'mapping_type': 'direct',
                'priority': 2,
                'description': 'Income band from 360° Profile'
            },
        ]
        
        # Scheme-specific mappings
        scheme_specific = {
            'CHIRANJEEVI': [
                {
                    'target_field': 'family_head_name',
                    'source_type': 'GR',
                    'source_path': 'GR.family_head.full_name',
                    'mapping_type': 'relationship',
                    'priority': 1,
                    'description': 'Family head name for health scheme'
                }
            ],
            'OLD_AGE_PENSION': [
                {
                    'target_field': 'age',
                    'source_type': 'DERIVED',
                    'source_path': 'calculate_age(GR.date_of_birth)',
                    'mapping_type': 'derived',
                    'priority': 1,
                    'description': 'Age must be >= 60 for old age pension'
                },
                {
                    'target_field': 'marital_status',
                    'source_type': 'GR',
                    'source_path': 'GR.marital_status',
                    'mapping_type': 'direct',
                    'priority': 1,
                    'description': 'Marital status from Golden Record'
                }
            ],
            'WIDOW_PENSION': [
                {
                    'target_field': 'marital_status',
                    'source_type': 'GR',
                    'source_path': 'GR.marital_status',
                    'mapping_type': 'conditional',
                    'transformation_expression': 'Must be "WIDOWED"',
                    'priority': 1,
                    'description': 'Marital status must be widowed'
                },
                {
                    'target_field': 'beneficiary_id',
                    'source_type': 'RELATIONSHIP',
                    'source_path': 'select_widowed_member(GR.family_members)',
                    'mapping_type': 'relationship',
                    'priority': 1,
                    'description': 'Select widowed family member as beneficiary'
                }
            ],
            'NREGA': [
                {
                    'target_field': 'job_card_number',
                    'source_type': 'GR',
                    'source_path': 'GR.job_card_number',
                    'mapping_type': 'direct',
                    'priority': 1,
                    'description': 'NREGA job card number'
                },
                {
                    'target_field': 'bank_account_number',
                    'source_type': 'GR',
                    'source_path': 'GR.bank_account_number',
                    'mapping_type': 'direct',
                    'priority': 1,
                    'description': 'Bank account for wage payment (mandatory)'
                }
            ]
        }
        
        mappings_created = 0
        
        print("\n📝 Creating field mappings...")
        for scheme_code, scheme_name, category in schemes:
            print(f"\n   Processing {scheme_code} ({scheme_name})...")
            
            # Combine standard and scheme-specific mappings
            all_mappings = standard_mappings.copy()
            if scheme_code in scheme_specific:
                all_mappings.extend(scheme_specific[scheme_code])
            
            for mapping in all_mappings:
                # Check if mapping already exists
                cursor = db.connection.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM application.scheme_field_mappings
                    WHERE scheme_code = %s AND target_field_name = %s
                """, [scheme_code, mapping['target_field']])
                exists = cursor.fetchone()[0] > 0
                cursor.close()
                
                if not exists:
                    cursor = db.connection.cursor()
                    cursor.execute("""
                        INSERT INTO application.scheme_field_mappings (
                            scheme_code, target_field_name, source_type, source_field,
                            mapping_type, transformation_expression, priority,
                            description, is_active
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                        scheme_code,
                        mapping['target_field'],
                        mapping['source_type'],
                        mapping.get('source_path', ''),
                        mapping['mapping_type'],
                        mapping.get('transformation_expression'),
                        mapping['priority'],
                        mapping.get('description', ''),
                        True
                    ])
                    cursor.close()
                    mappings_created += 1
                    print(f"      ✅ Created mapping: {mapping['target_field']} ({mapping['mapping_type']})")
        
        db.connection.commit()
        
        print("\n" + "=" * 80)
        print(f"✅ Field mapping rules creation complete!")
        print(f"   Created: {mappings_created} new mappings")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.connection.rollback()
    finally:
        db.disconnect()


if __name__ == '__main__':
    create_field_mappings()

