"""
Load Sample Eligibility Rules for Testing
Use Case: AI-PLATFORM-03 - Auto Identification of Beneficiaries
"""

import sys
from pathlib import Path
from datetime import date
import yaml

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector

# Add src to path for rule_manager
sys.path.append(str(Path(__file__).parent.parent / "src"))
from rule_manager import RuleManager


def load_sample_rules():
    """Load sample eligibility rules for common schemes"""
    
    print("="*80)
    print("Loading Sample Eligibility Rules")
    print("="*80)
    
    manager = RuleManager()
    
    # Sample rules for different schemes
    sample_rules = [
        # CHIRANJEEVI - Health Insurance Scheme
        {
            'scheme_code': 'CHIRANJEEVI',
            'rules': [
                {
                    'rule_name': 'Universal Coverage',
                    'rule_type': 'AGE',
                    'rule_expression': 'age >= 0',
                    'rule_operator': '>=',
                    'rule_value': '0',
                    'is_mandatory': True,
                    'priority': 10,
                    'description': 'All ages eligible'
                },
                {
                    'rule_name': 'Resident Status',
                    'rule_type': 'GEOGRAPHY',
                    'rule_expression': 'district_id IS NOT NULL',
                    'rule_operator': 'EXISTS',
                    'rule_value': '',
                    'is_mandatory': True,
                    'priority': 9,
                    'description': 'Must be a resident of Rajasthan'
                }
            ]
        },
        
        # OLD_AGE_PENSION
        {
            'scheme_code': 'OLD_AGE_PENSION',
            'rules': [
                {
                    'rule_name': 'Age Requirement',
                    'rule_type': 'AGE',
                    'rule_expression': 'age >= 60',
                    'rule_operator': '>=',
                    'rule_value': '60',
                    'is_mandatory': True,
                    'priority': 10,
                    'description': 'Must be 60 years or older'
                },
                {
                    'rule_name': 'Income Limit',
                    'rule_type': 'INCOME',
                    'rule_expression': 'income_band IN (VERY_LOW, LOW)',
                    'rule_operator': 'IN',
                    'rule_value': 'VERY_LOW,LOW',
                    'is_mandatory': True,
                    'priority': 9,
                    'description': 'Must be in low income band'
                }
            ]
        },
        
        # DISABILITY_PENSION
        {
            'scheme_code': 'DISABILITY_PENSION',
            'rules': [
                {
                    'rule_name': 'Disability Status',
                    'rule_type': 'DISABILITY',
                    'rule_expression': 'disability_status = true',
                    'rule_operator': '=',
                    'rule_value': 'true',
                    'is_mandatory': True,
                    'priority': 10,
                    'description': 'Must have disability'
                },
                {
                    'rule_name': 'Age Requirement',
                    'rule_type': 'AGE',
                    'rule_expression': 'age >= 18',
                    'rule_operator': '>=',
                    'rule_value': '18',
                    'is_mandatory': True,
                    'priority': 9,
                    'description': 'Must be 18 years or older'
                }
            ]
        },
        
        # GRAMIN_AWAS - Housing Scheme
        {
            'scheme_code': 'GRAMIN_AWAS',
            'rules': [
                {
                    'rule_name': 'Age Requirement',
                    'rule_type': 'AGE',
                    'rule_expression': 'age >= 18',
                    'rule_operator': '>=',
                    'rule_value': '18',
                    'is_mandatory': True,
                    'priority': 10,
                    'description': 'Must be 18 years or older'
                },
                {
                    'rule_name': 'BPL Requirement',
                    'rule_type': 'BPL',
                    'rule_expression': 'bpl_status = true',
                    'rule_operator': '=',
                    'rule_value': 'true',
                    'is_mandatory': True,
                    'priority': 9,
                    'description': 'Must be BPL'
                },
                {
                    'rule_name': 'Income Limit',
                    'rule_type': 'INCOME',
                    'rule_expression': 'family_income <= 300000',
                    'rule_operator': '<=',
                    'rule_value': '300000',
                    'is_mandatory': True,
                    'priority': 8,
                    'description': 'Family income must be less than 3 lakhs'
                }
            ]
        },
        
        # SC_ST_SCHOLARSHIP
        {
            'scheme_code': 'SC_ST_SCHOLARSHIP',
            'rules': [
                {
                    'rule_name': 'Caste Requirement',
                    'rule_type': 'CASTE',
                    'rule_expression': 'caste_id IN (SC, ST)',
                    'rule_operator': 'IN',
                    'rule_value': 'SC,ST',
                    'is_mandatory': True,
                    'priority': 10,
                    'description': 'Must belong to SC or ST category'
                },
                {
                    'rule_name': 'Age Range',
                    'rule_type': 'AGE',
                    'rule_expression': 'age >= 16 AND age <= 25',
                    'rule_operator': 'BETWEEN',
                    'rule_value': '16,25',
                    'is_mandatory': True,
                    'priority': 9,
                    'description': 'Must be between 16 and 25 years'
                },
                {
                    'rule_name': 'Education Level',
                    'rule_type': 'EDUCATION',
                    'rule_expression': 'education_level >= POST_MATRIC',
                    'rule_operator': '>=',
                    'rule_value': 'POST_MATRIC',
                    'is_mandatory': True,
                    'priority': 8,
                    'description': 'Must have post-matric education'
                }
            ]
        },
        
        # KISAN_CREDIT - Farmer Credit Scheme
        {
            'scheme_code': 'KISAN_CREDIT',
            'rules': [
                {
                    'rule_name': 'Age Requirement',
                    'rule_type': 'AGE',
                    'rule_expression': 'age >= 18',
                    'rule_operator': '>=',
                    'rule_value': '18',
                    'is_mandatory': True,
                    'priority': 10,
                    'description': 'Must be 18 years or older'
                },
                {
                    'rule_name': 'Farmer Status',
                    'rule_type': 'OCCUPATION',
                    'rule_expression': 'occupation = FARMER',
                    'rule_operator': '=',
                    'rule_value': 'FARMER',
                    'is_mandatory': True,
                    'priority': 9,
                    'description': 'Must be a farmer'
                }
            ]
        },
        
        # NREGA - Mahatma Gandhi National Rural Employment Guarantee Act
        {
            'scheme_code': 'NREGA',
            'rules': [
                {
                    'rule_name': 'Age Requirement',
                    'rule_type': 'AGE',
                    'rule_expression': 'age >= 18',
                    'rule_operator': '>=',
                    'rule_value': '18',
                    'is_mandatory': True,
                    'priority': 10,
                    'description': 'Must be 18 years or older'
                },
                {
                    'rule_name': 'Rural Residence',
                    'rule_type': 'GEOGRAPHY',
                    'rule_expression': 'is_urban = false',
                    'rule_operator': '=',
                    'rule_value': 'false',
                    'is_mandatory': True,
                    'priority': 9,
                    'description': 'Must be a rural resident'
                }
            ]
        },
        
        # BPL_ASSISTANCE - BPL Family Assistance
        {
            'scheme_code': 'BPL_ASSISTANCE',
            'rules': [
                {
                    'rule_name': 'BPL Status',
                    'rule_type': 'BPL',
                    'rule_expression': 'bpl_status = true',
                    'rule_operator': '=',
                    'rule_value': 'true',
                    'is_mandatory': True,
                    'priority': 10,
                    'description': 'Must have BPL status'
                },
                {
                    'rule_name': 'Income Limit',
                    'rule_type': 'INCOME',
                    'rule_expression': 'family_income <= 120000',
                    'rule_operator': '<=',
                    'rule_value': '120000',
                    'is_mandatory': True,
                    'priority': 9,
                    'description': 'Annual family income must be less than 1.2 lakhs'
                }
            ]
        },
        
        # MAHILA_SHAKTI - Women Empowerment Scheme
        {
            'scheme_code': 'MAHILA_SHAKTI',
            'rules': [
                {
                    'rule_name': 'Gender Requirement',
                    'rule_type': 'GENDER',
                    'rule_expression': 'gender = Female',
                    'rule_operator': '=',
                    'rule_value': 'Female',
                    'is_mandatory': True,
                    'priority': 10,
                    'description': 'Must be female'
                },
                {
                    'rule_name': 'Age Range',
                    'rule_type': 'AGE',
                    'rule_expression': 'age >= 18 AND age <= 65',
                    'rule_operator': 'BETWEEN',
                    'rule_value': '18,65',
                    'is_mandatory': True,
                    'priority': 9,
                    'description': 'Must be between 18 and 65 years'
                }
            ]
        },
        
        # OBC_SCHOLARSHIP - OBC Post Matric Scholarship
        {
            'scheme_code': 'OBC_SCHOLARSHIP',
            'rules': [
                {
                    'rule_name': 'Caste Requirement',
                    'rule_type': 'CASTE',
                    'rule_expression': 'caste_id IN (OBC)',
                    'rule_operator': 'IN',
                    'rule_value': 'OBC',
                    'is_mandatory': True,
                    'priority': 10,
                    'description': 'Must belong to OBC category'
                },
                {
                    'rule_name': 'Age Range',
                    'rule_type': 'AGE',
                    'rule_expression': 'age >= 16 AND age <= 25',
                    'rule_operator': 'BETWEEN',
                    'rule_value': '16,25',
                    'is_mandatory': True,
                    'priority': 9,
                    'description': 'Must be between 16 and 25 years'
                }
            ]
        },
        
        # VISHESH_LABH - Special Benefits Scheme
        {
            'scheme_code': 'VISHESH_LABH',
            'rules': [
                {
                    'rule_name': 'Age Requirement',
                    'rule_type': 'AGE',
                    'rule_expression': 'age >= 18',
                    'rule_operator': '>=',
                    'rule_value': '18',
                    'is_mandatory': True,
                    'priority': 10,
                    'description': 'Must be 18 years or older'
                },
                {
                    'rule_name': 'Income Limit',
                    'rule_type': 'INCOME',
                    'rule_expression': 'income_band IN (VERY_LOW, LOW)',
                    'rule_operator': 'IN',
                    'rule_value': 'VERY_LOW,LOW',
                    'is_mandatory': True,
                    'priority': 9,
                    'description': 'Must be in low income band'
                }
            ]
        },
        
        # TRIBAL_WELFARE - Tribal Welfare Scheme
        {
            'scheme_code': 'TRIBAL_WELFARE',
            'rules': [
                {
                    'rule_name': 'Caste Requirement',
                    'rule_type': 'CASTE',
                    'rule_expression': 'caste_id IN (ST)',
                    'rule_operator': 'IN',
                    'rule_value': 'ST',
                    'is_mandatory': True,
                    'priority': 10,
                    'description': 'Must belong to ST (Scheduled Tribe) category'
                },
                {
                    'rule_name': 'Residence Requirement',
                    'rule_type': 'GEOGRAPHY',
                    'rule_expression': 'district_id IN (tribal_districts)',
                    'rule_operator': 'IN',
                    'rule_value': '',
                    'is_mandatory': True,
                    'priority': 9,
                    'description': 'Must reside in designated tribal area'
                }
            ]
        }
    ]
    
    rules_created = 0
    rules_skipped = 0
    
    for scheme_group in sample_rules:
        scheme_code = scheme_group['scheme_code']
        print(f"\n📋 Loading rules for scheme: {scheme_code}")
        
        for rule_data in scheme_group['rules']:
            try:
                rule = manager.create_rule(
                    scheme_code=scheme_code,
                    rule_name=rule_data['rule_name'],
                    rule_type=rule_data['rule_type'],
                    rule_expression=rule_data['rule_expression'],
                    rule_operator=rule_data['rule_operator'],
                    rule_value=rule_data['rule_value'],
                    is_mandatory=rule_data['is_mandatory'],
                    priority=rule_data['priority'],
                    created_by='system'
                )
                
                print(f"  ✅ Created: {rule_data['rule_name']} (Rule ID: {rule['rule_id']})")
                rules_created += 1
                
            except Exception as e:
                error_msg = str(e).lower()
                # Rule might already exist (various possible error messages)
                if any(keyword in error_msg for keyword in ['duplicate', 'unique', 'already exists', 'violates unique']):
                    print(f"  ⚠️  Skipped (already exists): {rule_data['rule_name']}")
                    rules_skipped += 1
                else:
                    print(f"  ❌ Error creating {rule_data['rule_name']}: {e}")
                    # Continue with next rule even if one fails
    
    manager.disconnect()
    
    print(f"\n{'='*80}")
    print(f"✅ Rules Loading Complete!")
    print(f"   Created: {rules_created}")
    print(f"   Skipped: {rules_skipped}")
    print(f"   Total: {rules_created + rules_skipped}")
    print(f"{'='*80}")


if __name__ == "__main__":
    load_sample_rules()

