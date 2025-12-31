#!/usr/bin/env python3
"""
Initialize Scheme Exclusion Rules
Use Case ID: AI-PLATFORM-07

Initializes cross-scheme exclusion rules in the database.
"""

import sys
import os
import yaml
from pathlib import Path
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared', 'utils'))

from db_connector import DBConnector


def init_exclusion_rules():
    """Initialize scheme exclusion rules"""
    print("=" * 80)
    print("Initializing Scheme Exclusion Rules")
    print("=" * 80)
    
    # Load database configuration
    db_config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'db_config.yaml')
    
    with open(db_config_path, 'r') as f:
        db_config = yaml.safe_load(f)['database']
    
    # Connect to database
    connector = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    conn = connector.connect()
    cursor = conn.cursor()
    
    print(f"✅ Connected to PostgreSQL: {db_config['host']}:{db_config['port']}/{db_config['name']}")
    
    # Check existing rules
    cursor.execute("SELECT COUNT(*) FROM detection.scheme_exclusion_rules WHERE is_active = TRUE")
    existing_count = cursor.fetchone()[0]
    
    if existing_count > 0:
        print(f"\n⚠️  {existing_count} active exclusion rule(s) already exist")
        print("   Skipping initialization. Rules may have been created during schema setup.")
        cursor.close()
        connector.disconnect()
        return
    
    print("\n📝 Creating scheme exclusion rules...")
    
    # Default exclusion rules (examples)
    exclusion_rules = [
        {
            'scheme_code_1': 'OLD_AGE_PENSION',
            'scheme_code_2': 'DISABILITY_PENSION',
            'exclusion_type': 'MUTUALLY_EXCLUSIVE',
            'description': 'Cannot receive both old age and disability pension',
            'max_beneficiaries_per_family': None
        },
        {
            'scheme_code_1': 'OBC_SCHOLARSHIP',
            'scheme_code_2': 'SC_ST_SCHOLARSHIP',
            'exclusion_type': 'MUTUALLY_EXCLUSIVE',
            'description': 'Cannot receive both OBC and SC/ST scholarships',
            'max_beneficiaries_per_family': None
        },
        {
            'scheme_code_1': 'OBC_SCHOLARSHIP',
            'scheme_code_2': 'OBC_SCHOLARSHIP',
            'exclusion_type': 'LIMITED_OVERLAP',
            'description': 'Maximum 2 OBC scholarship beneficiaries per family',
            'max_beneficiaries_per_family': 2
        },
        {
            'scheme_code_1': 'SC_ST_SCHOLARSHIP',
            'scheme_code_2': 'SC_ST_SCHOLARSHIP',
            'exclusion_type': 'LIMITED_OVERLAP',
            'description': 'Maximum 2 SC/ST scholarship beneficiaries per family',
            'max_beneficiaries_per_family': 2
        },
    ]
    
    inserted_count = 0
    for rule in exclusion_rules:
        try:
            cursor.execute("""
                INSERT INTO detection.scheme_exclusion_rules (
                    scheme_code_1, scheme_code_2, exclusion_type,
                    description, max_beneficiaries_per_family,
                    effective_from, is_active
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (scheme_code_1, scheme_code_2) DO NOTHING
            """, (
                rule['scheme_code_1'],
                rule['scheme_code_2'],
                rule['exclusion_type'],
                rule['description'],
                rule['max_beneficiaries_per_family'],
                datetime.now().date(),
                True
            ))
            
            if cursor.rowcount > 0:
                inserted_count += 1
                print(f"   ✅ Created rule: {rule['scheme_code_1']} <-> {rule['scheme_code_2']}")
        
        except Exception as e:
            print(f"   ⚠️  Warning: Could not insert rule {rule['scheme_code_1']} <-> {rule['scheme_code_2']}: {str(e)}")
    
    conn.commit()
    cursor.close()
    connector.disconnect()
    
    print(f"\n✅ Exclusion rules initialization complete!")
    print(f"   Created: {inserted_count} exclusion rules")
    print("=" * 80)


if __name__ == '__main__':
    init_exclusion_rules()

