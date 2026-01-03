#!/usr/bin/env python3
"""
Validate training data for NLP model
"""

import json
from pathlib import Path

VALID_RULE_TYPES = [
    "AGE", "GENDER", "INCOME_GROUP", "ANNUAL_INCOME",
    "DISTRICT", "BLOCK", "VILLAGE", "STATE",
    "DISABILITY", "DISABILITY_TYPE", "DISABILITY_PERCENTAGE",
    "FAMILY_SIZE", "CATEGORY", "RATION_CARD",
    "LAND_OWNERSHIP", "PROPERTY_OWNERSHIP",
    "PRIOR_PARTICIPATION", "EDUCATION_LEVEL",
    "EMPLOYMENT_STATUS", "MARITAL_STATUS"
]

VALID_OPERATORS = [">=", "<=", "==", "!=", "IN", "NOT_IN", "BETWEEN"]

def validate_scheme(scheme: dict) -> list:
    """Validate a single scheme"""
    errors = []
    
    # Check required fields
    required = ["scheme_id", "scheme_code", "scheme_name", 
                "natural_language_criteria", "extracted_rules"]
    for field in required:
        if field not in scheme:
            errors.append(f"Missing required field: {field}")
    
    # Validate rules
    if "extracted_rules" in scheme:
        rules = scheme["extracted_rules"]
        if not isinstance(rules, list):
            errors.append("extracted_rules must be array")
        elif len(rules) < 3:
            errors.append("Need at least 3 rules")
        else:
            for i, rule in enumerate(rules):
                if "rule_type" not in rule:
                    errors.append(f"Rule {i+1} missing rule_type")
                elif rule["rule_type"] not in VALID_RULE_TYPES:
                    errors.append(f"Rule {i+1} invalid rule_type: {rule['rule_type']}")
                
                if "operator" in rule and rule["operator"] not in VALID_OPERATORS:
                    errors.append(f"Rule {i+1} invalid operator: {rule['operator']}")
    
    return errors

def validate_dataset(filepath: str) -> dict:
    """Validate entire dataset"""
    with open(filepath, "r", encoding="utf-8") as f:
        schemes = json.load(f)
    
    all_errors = []
    valid_count = 0
    
    for scheme in schemes:
        errors = validate_scheme(scheme)
        if errors:
            all_errors.append({
                "scheme_code": scheme.get("scheme_code", "UNKNOWN"),
                "errors": errors
            })
        else:
            valid_count += 1
    
    return {
        "total": len(schemes),
        "valid": valid_count,
        "invalid": len(all_errors),
        "errors": all_errors
    }

if __name__ == "__main__":
    filepath = "data/training/schemes_raw.json"
    
    if not Path(filepath).exists():
        print(f"Error: {filepath} not found")
        exit(1)
    
    result = validate_dataset(filepath)
    
    print(f"\nValidation Results:")
    print(f"Total schemes: {result['total']}")
    print(f"Valid: {result['valid']}")
    print(f"Invalid: {result['invalid']}")
    
    if result['errors']:
        print(f"\nFirst 10 errors:")
        for err in result['errors'][:10]:
            print(f"  {err['scheme_code']}: {', '.join(err['errors'])}")
    
    if result['invalid'] == 0:
        print("\n✓ All schemes are valid!")
    else:
        print(f"\n⚠ {result['invalid']} schemes need fixing")

