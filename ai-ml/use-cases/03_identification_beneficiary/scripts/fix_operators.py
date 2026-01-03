#!/usr/bin/env python3
"""
Fix operator issues in training data
Converts "=" to "==" for equality operators
"""

import json
from pathlib import Path

def fix_operators(scheme: dict) -> dict:
    """Fix operators and rule types in a scheme"""
    if "extracted_rules" in scheme:
        # Filter out invalid rules and fix valid ones
        valid_rules = []
        for rule in scheme["extracted_rules"]:
            # Fix "=" to "==" for equality
            if "operator" in rule:
                if rule["operator"] == "=":
                    rule["operator"] = "=="
                    # Also fix rule_expression if it exists
                    if "rule_expression" in rule:
                        rule["rule_expression"] = rule["rule_expression"].replace(" = ", " == ")
                        rule["rule_expression"] = rule["rule_expression"].replace("='", "=='")
                        rule["rule_expression"] = rule["rule_expression"].replace("=\"", "==\"")
            
            # Fix LAND_SIZE to LAND_OWNERSHIP (or remove if not fixable)
            if "rule_type" in rule:
                if rule["rule_type"] == "LAND_SIZE":
                    # Convert LAND_SIZE to LAND_OWNERSHIP with appropriate logic
                    rule["rule_type"] = "LAND_OWNERSHIP"
                    rule["operator"] = "=="
                    rule["value"] = True
                    if "rule_expression" in rule:
                        rule["rule_expression"] = "land_ownership == true"
            
            # Only keep rules with valid rule_type
            if "rule_type" in rule and rule["rule_type"] in [
                "AGE", "GENDER", "INCOME_GROUP", "ANNUAL_INCOME",
                "DISTRICT", "BLOCK", "VILLAGE", "STATE",
                "DISABILITY", "DISABILITY_TYPE", "DISABILITY_PERCENTAGE",
                "FAMILY_SIZE", "CATEGORY", "RATION_CARD",
                "LAND_OWNERSHIP", "PROPERTY_OWNERSHIP",
                "PRIOR_PARTICIPATION", "EDUCATION_LEVEL",
                "EMPLOYMENT_STATUS", "MARITAL_STATUS"
            ]:
                valid_rules.append(rule)
        
        # Update extracted_rules
        scheme["extracted_rules"] = valid_rules
    
    return scheme

def fix_dataset(filepath: str):
    """Fix operators and rule types in entire dataset"""
    with open(filepath, "r", encoding="utf-8") as f:
        schemes = json.load(f)
    
    fixed = []
    removed = 0
    
    for s in schemes:
        fixed_scheme = fix_operators(s)
        # Only keep schemes with at least 3 rules
        if len(fixed_scheme.get("extracted_rules", [])) >= 3:
            fixed.append(fixed_scheme)
        else:
            removed += 1
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(fixed, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Fixed {len(fixed)} schemes")
    if removed > 0:
        print(f"⚠ Removed {removed} schemes with less than 3 rules")

if __name__ == "__main__":
    fix_dataset("data/training/schemes_raw.json")
    print("\nRe-run validation to check:")

