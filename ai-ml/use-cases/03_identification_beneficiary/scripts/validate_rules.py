#!/usr/bin/env python3
"""
Rule Validator
Validates scheme eligibility rules and tests rule evaluation
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from rule_engine import RuleEngine


def validate_rule_syntax():
    """Validate rule syntax in database"""
    print("=" * 80)
    print("Scheme Eligibility Rules Validation")
    print("=" * 80)
    print()
    
    engine = RuleEngine()
    
    # Get all schemes
    query = "SELECT scheme_id, scheme_name FROM eligibility.scheme_master WHERE is_active = true"
    import pandas as pd
    schemes = pd.read_sql(query, engine.db.connection)
    
    print(f"Found {len(schemes)} active schemes\n")
    
    all_valid = True
    
    for _, scheme in schemes.iterrows():
        scheme_id = scheme['scheme_id']
        scheme_name = scheme['scheme_name']
        
        print(f"Scheme: {scheme_name} ({scheme_id})")
        print("-" * 80)
        
        # Load rules
        rules = engine.load_scheme_rules(scheme_id)
        exclusions = engine.load_exclusion_rules(scheme_id)
        
        print(f"  Eligibility Rules: {len(rules)}")
        print(f"  Exclusion Rules: {len(exclusions)}")
        
        # Validate each rule
        valid_rules = 0
        for rule in rules:
            rule_name = rule['rule_name']
            rule_type = rule['rule_type']
            rule_expression = rule['rule_expression']
            
            # Basic validation
            if rule_type and rule_expression:
                valid_rules += 1
                print(f"    ✅ {rule_name} ({rule_type})")
            else:
                print(f"    ❌ {rule_name}: Missing rule_type or rule_expression")
                all_valid = False
        
        if len(rules) == 0:
            print(f"    ⚠️  No eligibility rules defined")
        
        print()
    
    engine.close()
    
    if all_valid:
        print("✅ All rules are valid!")
    else:
        print("❌ Some rules have validation issues")
    
    return all_valid


def test_rule_evaluation():
    """Test rule evaluation with sample data"""
    print("\n" + "=" * 80)
    print("Rule Evaluation Test")
    print("=" * 80)
    print()
    
    engine = RuleEngine()
    
    # Sample family data
    test_cases = [
        {
            'name': 'Elderly Low-Income Person',
            'data': {
                'family_id': 'test-001',
                'head_age': 65,
                'head_gender': 'M',
                'district_id': 101,
                'income_band': 'LOW',
                'family_size': 2
            }
        },
        {
            'name': 'Young Medium-Income Person',
            'data': {
                'family_id': 'test-002',
                'head_age': 30,
                'head_gender': 'F',
                'district_id': 101,
                'income_band': 'MEDIUM',
                'family_size': 4
            }
        }
    ]
    
    schemes = ['SCHEME_001', 'SCHEME_002']
    
    for test_case in test_cases:
        print(f"Test Case: {test_case['name']}")
        print("-" * 80)
        
        for scheme_id in schemes:
            try:
                result = engine.evaluate_scheme_eligibility(
                    scheme_id, test_case['data']
                )
                
                status = result['status']
                eligible = result['eligible']
                rules_passed = len(result['rules_passed'])
                rules_failed = len(result['rules_failed'])
                
                print(f"  {scheme_id}: {status}")
                print(f"    Rules Passed: {rules_passed}, Failed: {rules_failed}")
                if eligible:
                    print(f"    ✅ Eligible")
                else:
                    print(f"    ❌ Not Eligible")
            
            except Exception as e:
                print(f"  {scheme_id}: ❌ Error - {e}")
        
        print()
    
    engine.close()


def main():
    """Run validation"""
    valid = validate_rule_syntax()
    test_rule_evaluation()
    
    return 0 if valid else 1


if __name__ == "__main__":
    sys.exit(main())

