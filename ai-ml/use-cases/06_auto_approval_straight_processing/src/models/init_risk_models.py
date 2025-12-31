#!/usr/bin/env python3
"""
Initialize Risk Models Metadata
Use Case ID: AI-PLATFORM-06

Creates placeholder risk model records in the database.
Actual models should be trained using train_risk_model.py
"""

import sys
import os
import yaml
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared', 'utils'))

from db_connector import DBConnector


def init_risk_models():
    """Initialize placeholder risk model records"""
    print("=" * 80)
    print("Initializing Risk Models Metadata")
    print("=" * 80)
    
    # Load configurations
    db_config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'db_config.yaml')
    
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
    
    # Check if models already exist
    cursor.execute("SELECT COUNT(*) FROM decision.risk_models")
    existing_count = cursor.fetchone()[0]
    
    if existing_count > 0:
        print(f"\n⚠️  {existing_count} risk model(s) already exist")
        print("   Skipping initialization. Use train_risk_model.py to train actual models.")
        cursor.close()
        connector.disconnect()
        return
    
    # Create placeholder general model
    print("\n📝 Creating placeholder risk model records...")
    
    cursor.execute("""
        INSERT INTO decision.risk_models (
            model_name, model_type, model_version, scheme_code,
            model_path, is_active, is_production, created_by, trained_at
        ) VALUES (
            'risk_model_general_rule_based', 'rule-based', '1.0', NULL,
            'N/A - Using rule-based scoring', true, true, 'system', CURRENT_TIMESTAMP
        )
        RETURNING model_id
    """)
    
    model_id = cursor.fetchone()[0]
    print(f"   ✅ Created placeholder model (ID: {model_id})")
    print(f"      Model: rule-based (fallback when ML models unavailable)")
    
    conn.commit()
    cursor.close()
    connector.disconnect()
    
    print("\n" + "=" * 80)
    print("✅ Risk models initialization complete!")
    print("=" * 80)
    print("\n💡 Note: This creates placeholder records.")
    print("   To train actual ML models, run:")
    print("   python src/models/train_risk_model.py --model-type xgboost")
    print("=" * 80)


if __name__ == '__main__':
    init_risk_models()

