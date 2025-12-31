"""
Add Scheme-Specific Validation Rules
Adds business validation rules based on known scheme requirements
"""

import sys
from pathlib import Path
import yaml
import json

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


def add_validation_rules():
    """Add scheme-specific validation rules"""
    print("=" * 80)
    print("Adding Scheme-Specific Validation Rules")
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
    
    # Scheme-specific validation rules
    validation_rules = {
        'OLD_AGE_PENSION': {
            'age_validation': {
                'field': 'age',
                'rule': 'age >= 60',
                'rule_type': 'python',
                'message': 'Applicant must be 60 years or above for old age pension',
                'severity': 'error'
            },
            'income_validation': {
                'field': 'income_band',
                'rule': 'income_band == "BELOW_POVERTY_LINE"',
                'rule_type': 'python',
                'message': 'Old age pension requires BPL status',
                'severity': 'warning'
            }
        },
        'DISABILITY_PENSION': {
            'disability_certificate': {
                'field': 'disability_certificate_number',
                'rule': 'disability_certificate_number is not None',
                'rule_type': 'python',
                'message': 'Disability certificate is required',
                'severity': 'error'
            },
            'disability_percentage': {
                'field': 'disability_percentage',
                'rule': 'disability_percentage >= 40',
                'rule_type': 'python',
                'message': 'Disability percentage must be 40% or above',
                'severity': 'error'
            }
        },
        'SC_ST_SCHOLARSHIP': {
            'caste_validation': {
                'field': 'caste_category',
                'rule': 'caste_category in ["SC", "ST"]',
                'rule_type': 'python',
                'message': 'SC/ST scholarship requires SC or ST category',
                'severity': 'error'
            },
            'age_validation': {
                'field': 'age',
                'rule': '18 <= age <= 30',
                'rule_type': 'python',
                'message': 'Age must be between 18 and 30 years',
                'severity': 'error'
            }
        },
        'OBC_SCHOLARSHIP': {
            'caste_validation': {
                'field': 'caste_category',
                'rule': 'caste_category == "OBC"',
                'rule_type': 'python',
                'message': 'OBC scholarship requires OBC category',
                'severity': 'error'
            },
            'age_validation': {
                'field': 'age',
                'rule': '18 <= age <= 30',
                'rule_type': 'python',
                'message': 'Age must be between 18 and 30 years',
                'severity': 'error'
            }
        },
        'NREGA': {
            'job_card_validation': {
                'field': 'job_card_number',
                'rule': 'job_card_number is not None and len(job_card_number) >= 10',
                'rule_type': 'python',
                'message': 'Valid NREGA job card number is required',
                'severity': 'error'
            },
            'bank_account_validation': {
                'field': 'bank_account_number',
                'rule': 'bank_account_number is not None',
                'rule_type': 'python',
                'message': 'Bank account is mandatory for wage payment',
                'severity': 'error'
            }
        },
        'KISAN_CREDIT': {
            'farmer_validation': {
                'field': 'is_farmer',
                'rule': 'is_farmer == True',
                'rule_type': 'python',
                'message': 'Kisan Credit Card requires farmer status',
                'severity': 'error'
            },
            'age_validation': {
                'field': 'age',
                'rule': '18 <= age <= 60',
                'rule_type': 'python',
                'message': 'Age must be between 18 and 60 years',
                'severity': 'error'
            }
        },
        'GRAMIN_AWAS': {
            'bpl_validation': {
                'field': 'bpl_status',
                'rule': 'bpl_status == "Yes"',
                'rule_type': 'python',
                'message': 'Gramin Awas scheme requires BPL status',
                'severity': 'error'
            },
            'address_validation': {
                'field': 'village',
                'rule': 'village is not None',
                'rule_type': 'python',
                'message': 'Rural address is required',
                'severity': 'error'
            }
        },
        'MAHILA_SHAKTI': {
            'gender_validation': {
                'field': 'gender',
                'rule': 'gender == "FEMALE"',
                'rule_type': 'python',
                'message': 'Mahila Shakti scheme is for women only',
                'severity': 'error'
            },
            'age_validation': {
                'field': 'age',
                'rule': '18 <= age <= 55',
                'rule_type': 'python',
                'message': 'Age must be between 18 and 55 years',
                'severity': 'error'
            }
        },
        'VISHESH_LABH': {
            'age_validation': {
                'field': 'age',
                'rule': '18 <= age <= 25',
                'rule_type': 'python',
                'message': 'Age must be between 18 and 25 years',
                'severity': 'error'
            },
            'merit_validation': {
                'field': 'marks_percentage',
                'rule': 'marks_percentage >= 75',
                'rule_type': 'python',
                'message': 'Minimum 75% marks required',
                'severity': 'error'
            }
        }
    }
    
    try:
        db.connect()
        
        print("\n📝 Adding validation rules...")
        rules_added = 0
        
        for scheme_code, rules in validation_rules.items():
            print(f"\n   Processing {scheme_code}...")
            
            # Get current schema
            cursor = db.connection.cursor()
            cursor.execute("""
                SELECT schema_id, semantic_rules
                FROM application.scheme_form_schemas
                WHERE scheme_code = %s AND is_active = true
            """, [scheme_code])
            row = cursor.fetchone()
            cursor.close()
            
            if not row:
                print(f"      ⚠️  Schema not found for {scheme_code}, skipping...")
                continue
            
            schema_id, current_rules = row
            
            # Merge with existing rules
            if current_rules:
                try:
                    if isinstance(current_rules, str):
                        existing_rules = json.loads(current_rules)
                    else:
                        existing_rules = current_rules
                except:
                    existing_rules = {}
            else:
                existing_rules = {}
            
            # Update with new rules
            updated_rules = existing_rules.copy()
            updated_rules.update(rules)
            
            # Update schema
            cursor = db.connection.cursor()
            cursor.execute("""
                UPDATE application.scheme_form_schemas
                SET semantic_rules = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE schema_id = %s
            """, [json.dumps(updated_rules), schema_id])
            cursor.close()
            
            rules_added += len(rules)
            print(f"      ✅ Added {len(rules)} validation rules")
        
        db.connection.commit()
        
        print("\n" + "=" * 80)
        print(f"✅ Validation rules addition complete!")
        print(f"   Total rules added: {rules_added}")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.connection.rollback()
    finally:
        db.disconnect()


if __name__ == '__main__':
    add_validation_rules()

