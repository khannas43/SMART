#!/usr/bin/env python3
"""
Initialize Detection Configuration
Use Case ID: AI-PLATFORM-07

Initializes detection configuration in the database with default thresholds and settings.
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


def init_detection_config():
    """Initialize detection configuration"""
    print("=" * 80)
    print("Initializing Detection Configuration")
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
    
    # Check existing config
    cursor.execute("SELECT COUNT(*) FROM detection.detection_config WHERE is_active = TRUE")
    existing_count = cursor.fetchone()[0]
    
    if existing_count > 0:
        print(f"\n⚠️  {existing_count} active configuration(s) already exist")
        print("   Skipping initialization. Use update scripts to modify configuration.")
        cursor.close()
        connector.disconnect()
        return
    
    print("\n📝 Creating detection configuration...")
    
    # Get configuration from use_case_config.yaml
    ml_config = use_case_config.get('ml_detection', {})
    classification_config = use_case_config.get('case_classification', {})
    prioritization_config = use_case_config.get('prioritization', {})
    detection_config = use_case_config.get('detection', {})
    
    # Insert global configurations
    configs = [
        # ML Thresholds
        ('ML_THRESHOLDS', 'anomaly_score_threshold', 
         str(ml_config.get('anomaly_score_threshold', 0.7)), 'DECIMAL',
         'Minimum anomaly score to flag as HIGH risk'),
        ('ML_THRESHOLDS', 'risk_score_threshold',
         str(ml_config.get('risk_score_threshold', 0.6)), 'DECIMAL',
         'Minimum risk score to flag as LIKELY_MIS_TARGETED'),
        
        # Classification Thresholds
        ('CASE_CLASSIFICATION', 'high_confidence_threshold',
         str(classification_config.get('high_confidence_threshold', 0.8)), 'DECIMAL',
         'High confidence threshold for case classification'),
        ('CASE_CLASSIFICATION', 'medium_confidence_threshold',
         str(classification_config.get('medium_confidence_threshold', 0.5)), 'DECIMAL',
         'Medium confidence threshold'),
        ('CASE_CLASSIFICATION', 'hard_ineligible_threshold',
         str(classification_config.get('hard_ineligible_threshold', 0.8)), 'DECIMAL',
         'Threshold for HARD_INELIGIBLE classification'),
        
        # Prioritization
        ('PRIORITIZATION', 'high_financial_exposure_threshold',
         str(prioritization_config.get('high_financial_exposure', 10000)), 'DECIMAL',
         'Minimum financial exposure for HIGH priority'),
        ('PRIORITIZATION', 'high_risk_score',
         str(prioritization_config.get('high_risk_score', 0.7)), 'DECIMAL',
         'High risk score threshold'),
        ('PRIORITIZATION', 'high_vulnerability_threshold',
         str(prioritization_config.get('high_vulnerability', 0.8)), 'DECIMAL',
         'High vulnerability threshold (handle with caution)'),
        
        # Re-scoring
        ('RE_SCORING', 'full_rescore_frequency',
         detection_config.get('full_rescore_frequency', 'QUARTERLY'), 'STRING',
         'Frequency of full re-scoring runs'),
        ('RE_SCORING', 'incremental_rescore_enabled',
         str(detection_config.get('incremental_rescore_enabled', True)), 'BOOLEAN',
         'Enable incremental re-scoring on data changes'),
    ]
    
    inserted_count = 0
    for scheme_code, category, key, value, config_type, description in configs:
        try:
            cursor.execute("""
                INSERT INTO detection.detection_config (
                    scheme_code, config_category, config_key, config_value,
                    config_type, description, is_active, effective_from
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                None,  # Global config
                category,
                key,
                value,
                config_type,
                description,
                True,
                datetime.now().date()
            ))
            inserted_count += 1
        except Exception as e:
            print(f"   ⚠️  Warning: Could not insert {category}.{key}: {str(e)}")
    
    # Insert scheme-specific configurations (from use_case_config)
    schemes_config = use_case_config.get('schemes', {})
    for scheme_code, scheme_config in schemes_config.items():
        scheme_detection = scheme_config.get('detection', {})
        
        if 'anomaly_threshold' in scheme_detection:
            try:
                cursor.execute("""
                    INSERT INTO detection.detection_config (
                        scheme_code, config_category, config_key, config_value,
                        config_type, description, is_active, effective_from
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    scheme_code,
                    'ML_THRESHOLDS',
                    'anomaly_score_threshold',
                    str(scheme_detection['anomaly_threshold']),
                    'DECIMAL',
                    f'Anomaly threshold for {scheme_code}',
                    True,
                    datetime.now().date()
                ))
                inserted_count += 1
            except Exception as e:
                print(f"   ⚠️  Warning: Could not insert {scheme_code} config: {str(e)}")
    
    conn.commit()
    cursor.close()
    connector.disconnect()
    
    print(f"\n✅ Detection configuration initialization complete!")
    print(f"   Inserted: {inserted_count} configuration entries")
    print("=" * 80)


if __name__ == '__main__':
    init_detection_config()

