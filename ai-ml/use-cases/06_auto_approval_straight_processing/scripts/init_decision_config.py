#!/usr/bin/env python3
"""
Initialize Decision Configuration for Auto Approval & Straight-through Processing
Use Case ID: AI-PLATFORM-06
"""

import sys
import os
import yaml

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared', 'utils'))

from db_connector import DBConnector


def init_decision_config():
    """Initialize decision configuration for all active schemes."""
    print("=" * 80)
    print("Initializing Decision Configuration")
    print("=" * 80)
    
    # Load configurations
    db_config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'db_config.yaml')
    use_case_config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'use_case_config.yaml')
    
    with open(db_config_path, 'r') as f:
        db_config = yaml.safe_load(f)['database']
    
    with open(use_case_config_path, 'r') as f:
        use_case_config = yaml.safe_load(f)
    
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
    
    # Get all active schemes
    cursor.execute("""
        SELECT scheme_code, scheme_name, category
        FROM public.scheme_master
        WHERE status = 'active'
        ORDER BY scheme_code
    """)
    
    schemes = cursor.fetchall()
    print(f"\n📋 Found {len(schemes)} active schemes")
    
    # Default thresholds from config
    default_thresholds = use_case_config['decision']['default_risk_thresholds']
    default_scheme_config = use_case_config.get('schemes', {})
    
    created = 0
    skipped = 0
    
    print("\n📝 Creating decision configurations...")
    
    for scheme_code, scheme_name, category in schemes:
        print(f"\nProcessing {scheme_code} ({scheme_name})...")
        
        # Check if config already exists
        cursor.execute("""
            SELECT config_id FROM decision.decision_config
            WHERE scheme_code = %s AND is_active = true
            LIMIT 1
        """, (scheme_code,))
        
        if cursor.fetchone():
            print(f"   ⏭️  Configuration already exists, skipping")
            skipped += 1
            continue
        
        # Get scheme-specific config if available
        scheme_config = default_scheme_config.get(scheme_code, {})
        risk_thresholds = scheme_config.get('risk_thresholds', default_thresholds)
        
        # Insert configuration
        cursor.execute("""
            INSERT INTO decision.decision_config (
                scheme_code,
                low_risk_max,
                medium_risk_min,
                medium_risk_max,
                high_risk_min,
                enable_auto_approval,
                require_document_verification,
                require_bank_validation,
                route_medium_risk_to_officer,
                route_high_risk_to_fraud,
                require_human_review_medium,
                require_human_review_high,
                is_active,
                created_by
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING config_id
        """, (
            scheme_code,
            risk_thresholds.get('low_risk_max', default_thresholds['low_risk_max']),
            risk_thresholds.get('medium_risk_min', default_thresholds['medium_risk_min']),
            risk_thresholds.get('medium_risk_max', default_thresholds['medium_risk_max']),
            risk_thresholds.get('high_risk_min', default_thresholds['high_risk_min']),
            scheme_config.get('enable_auto_approval', True),
            scheme_config.get('require_document_verification', True),
            scheme_config.get('require_bank_validation', True),
            True,  # route_medium_risk_to_officer
            True,  # route_high_risk_to_fraud
            scheme_config.get('require_human_review_medium', True),
            scheme_config.get('require_human_review_high', True),
            True,  # is_active
            'system'  # created_by
        ))
        
        config_id = cursor.fetchone()[0]
        print(f"   ✅ Created configuration (ID: {config_id})")
        print(f"      Low risk max: {risk_thresholds.get('low_risk_max', default_thresholds['low_risk_max'])}")
        print(f"      Auto approval: {scheme_config.get('enable_auto_approval', True)}")
        created += 1
    
    conn.commit()
    cursor.close()
    connector.disconnect()
    
    print("\n" + "=" * 80)
    print(f"✅ Decision configuration initialization complete!")
    print(f"   Created: {created}")
    print(f"   Skipped: {skipped}")
    print(f"   Total: {len(schemes)}")
    print("=" * 80)
    print("Database connection closed")


if __name__ == '__main__':
    init_decision_config()

