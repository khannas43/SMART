#!/usr/bin/env python3
"""
Data Validator for Eligibility Scoring & 360° Profiles
Validates data quality and completeness
"""

import sys
from pathlib import Path
import pandas as pd
import yaml

# Add paths
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


def validate_golden_records(db):
    """Validate Golden Records data"""
    print("📋 Validating Golden Records...")
    
    query = """
    SELECT 
        COUNT(*) as total,
        COUNT(*) FILTER (WHERE status = 'active') as active,
        COUNT(*) FILTER (WHERE family_id IS NOT NULL) as with_family,
        COUNT(*) FILTER (WHERE district_id IS NOT NULL) as with_district,
        COUNT(*) FILTER (WHERE caste_id IS NOT NULL) as with_caste,
        COUNT(*) FILTER (WHERE age IS NOT NULL) as with_age
    FROM golden_records
    """
    
    result = db.execute_query(query).iloc[0]
    
    print(f"   Total records: {result['total']:,}")
    
    # Handle division by zero
    if result['total'] > 0:
        print(f"   Active: {result['active']:,} ({result['active']/result['total']*100:.1f}%)")
        print(f"   With family_id: {result['with_family']:,} ({result['with_family']/result['total']*100:.1f}%)")
        print(f"   With district: {result['with_district']:,} ({result['with_district']/result['total']*100:.1f}%)")
        print(f"   With caste: {result['with_caste']:,} ({result['with_caste']/result['total']*100:.1f}%)")
        print(f"   With age: {result['with_age']:,} ({result['with_age']/result['total']*100:.1f}%)")
    else:
        print(f"   Active: {result['active']:,} (N/A - no records)")
        print(f"   With family_id: {result['with_family']:,} (N/A - no records)")
        print(f"   With district: {result['with_district']:,} (N/A - no records)")
        print(f"   With caste: {result['with_caste']:,} (N/A - no records)")
        print(f"   With age: {result['with_age']:,} (N/A - no records)")
    
    issues = []
    if result['total'] == 0:
        issues.append("No golden records found (run generate_synthetic.py)")
    elif result['active'] / result['total'] < 0.8:
        issues.append("Low active record percentage (<80%)")
    elif result['with_family'] / result['total'] < 0.5:
        issues.append("Low family_id coverage (<50%)")
    
    return len(issues) == 0, issues


def validate_relationships(db):
    """Validate relationships data"""
    print("\n🔗 Validating Relationships...")
    
    query = """
    SELECT 
        COUNT(*) as total,
        COUNT(DISTINCT from_gr_id) as unique_from,
        COUNT(DISTINCT to_gr_id) as unique_to,
        COUNT(DISTINCT relationship_type) as relationship_types
    FROM gr_relationships
    """
    
    result = db.execute_query(query).iloc[0]
    
    print(f"   Total relationships: {result['total']:,}")
    print(f"   Unique from_gr_id: {result['unique_from']:,}")
    print(f"   Unique to_gr_id: {result['unique_to']:,}")
    print(f"   Relationship types: {result['relationship_types']}")
    
    issues = []
    if result['total'] == 0:
        issues.append("No relationships found")
    if result['unique_from'] < 100:
        issues.append("Very few unique from_gr_id (<100)")
    
    return len(issues) == 0, issues


def validate_benefits(db):
    """Validate benefit events"""
    print("\n💰 Validating Benefit Events...")
    
    query = """
    SELECT 
        COUNT(*) as total,
        COUNT(DISTINCT gr_id) as unique_beneficiaries,
        COUNT(DISTINCT scheme_id) as unique_schemes,
        MIN(txn_date) as earliest_date,
        MAX(txn_date) as latest_date,
        AVG(amount) as avg_amount,
        SUM(amount) as total_amount
    FROM benefit_events
    """
    
    result = db.execute_query(query).iloc[0]
    
    print(f"   Total events: {result['total']:,}")
    print(f"   Unique beneficiaries: {result['unique_beneficiaries']:,}")
    print(f"   Unique schemes: {result['unique_schemes']}")
    
    # Handle None values for dates
    earliest = result['earliest_date'] if pd.notna(result['earliest_date']) else 'N/A'
    latest = result['latest_date'] if pd.notna(result['latest_date']) else 'N/A'
    print(f"   Date range: {earliest} to {latest}")
    
    # Handle None values for amounts
    if pd.notna(result['avg_amount']) and result['avg_amount'] is not None:
        print(f"   Avg amount: ₹{result['avg_amount']:,.2f}")
    else:
        print(f"   Avg amount: N/A")
    
    if pd.notna(result['total_amount']) and result['total_amount'] is not None:
        print(f"   Total amount: ₹{result['total_amount']:,.2f}")
    else:
        print(f"   Total amount: N/A")
    
    issues = []
    if result['total'] == 0:
        issues.append("No benefit events found")
    if result['unique_schemes'] < 5:
        issues.append("Very few schemes (<5)")
    
    return len(issues) == 0, issues


def validate_profiles(db):
    """Validate 360° profiles"""
    print("\n👤 Validating 360° Profiles...")
    
    query = """
    SELECT 
        COUNT(*) as total_profiles,
        COUNT(*) FILTER (WHERE inferred_income_band IS NOT NULL) as with_income_band,
        COUNT(*) FILTER (WHERE cluster_id IS NOT NULL) as with_cluster,
        COUNT(*) FILTER (WHERE risk_flags IS NOT NULL AND array_length(risk_flags, 1) > 0) as with_flags,
        AVG(income_band_confidence) as avg_confidence
    FROM profile_360
    """
    
    result = db.execute_query(query).iloc[0]
    
    print(f"   Total profiles: {result['total_profiles']:,}")
    print(f"   With income band: {result['with_income_band']:,} ({result['with_income_band']/max(result['total_profiles'],1)*100:.1f}%)")
    print(f"   With cluster: {result['with_cluster']:,} ({result['with_cluster']/max(result['total_profiles'],1)*100:.1f}%)")
    print(f"   With flags: {result['with_flags']:,} ({result['with_flags']/max(result['total_profiles'],1)*100:.1f}%)")
    if result['avg_confidence']:
        print(f"   Avg confidence: {result['avg_confidence']:.2f}")
    
    issues = []
    if result['total_profiles'] == 0:
        issues.append("No profiles found (run profile_recompute_service.py)")
    
    return len(issues) == 0, issues


def main():
    """Run all validations"""
    print("=" * 60)
    print("Data Validation for Eligibility Scoring & 360° Profiles")
    print("=" * 60)
    
    # Connect to database
    config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    db = DBConnector(
        host=config['database']['host'],
        port=config['database']['port'],
        database=config['database']['dbname'],
        user=config['database']['user'],
        password=config['database']['password']
    )
    db.connect()
    
    try:
        results = {
            "Golden Records": validate_golden_records(db),
            "Relationships": validate_relationships(db),
            "Benefits": validate_benefits(db),
            "Profiles": validate_profiles(db)
        }
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        all_valid = True
        for check, (valid, issues) in results.items():
            status = "✅ VALID" if valid else "⚠️  ISSUES"
            print(f"  {check}: {status}")
            if issues:
                for issue in issues:
                    print(f"    - {issue}")
                all_valid = False
        
        print("=" * 60)
        
        if all_valid:
            print("✅ All data validations passed!")
            return 0
        else:
            print("⚠️  Some data quality issues found. Review above.")
            return 1
            
    finally:
        db.disconnect()


if __name__ == "__main__":
    sys.exit(main())

