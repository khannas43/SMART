#!/usr/bin/env python3
"""
Create Sample Data for Detection Viewer
Use Case ID: AI-PLATFORM-07

Creates sample detection runs, cases, and related data for testing the viewer.
"""

import sys
import os
import yaml
from pathlib import Path
from datetime import datetime, timedelta
import uuid
import random

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared', 'utils'))

from db_connector import DBConnector


def create_sample_data():
    """Create sample detection data"""
    print("=" * 80)
    print("Creating Sample Detection Data")
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
    
    # Get scheme codes
    try:
        cursor.execute("SELECT scheme_code FROM public.scheme_master LIMIT 5")
        schemes = [row[0] for row in cursor.fetchall()]
    except Exception as e:
        # If scheme_master doesn't exist or has issues, use default schemes
        print(f"   ⚠️  Could not fetch schemes: {str(e)}")
        schemes = []
    
    if not schemes:
        print("⚠️  No active schemes found. Creating sample schemes...")
        schemes = ['CHIRANJEEVI', 'OLD_AGE_PENSION', 'DISABILITY_PENSION', 'BPL_ASSISTANCE', 'NREGA']
    
    print(f"\n📋 Using schemes: {', '.join(schemes)}")
    
    # 1. Create detection runs
    print("\n📊 Creating detection runs...")
    
    run_types = ['FULL', 'INCREMENTAL', 'SCHEME_SPECIFIC']
    run_statuses = ['COMPLETED', 'RUNNING', 'COMPLETED', 'COMPLETED']
    
    run_ids = []
    for i in range(4):
        run_id = i + 1
        run_type = random.choice(run_types)
        run_status = run_statuses[i]
        total_scanned = random.randint(500, 2000)
        total_flagged = random.randint(10, 50)
        
        run_date = datetime.now() - timedelta(days=random.randint(0, 30))
        
        cursor.execute("""
            INSERT INTO detection.detection_runs (
                run_id, run_type, run_status, total_beneficiaries_scanned,
                total_cases_flagged, started_by, run_date, completed_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (run_id) DO UPDATE SET
                run_type = EXCLUDED.run_type,
                run_status = EXCLUDED.run_status,
                total_beneficiaries_scanned = EXCLUDED.total_beneficiaries_scanned,
                total_cases_flagged = EXCLUDED.total_cases_flagged
        """, (
            run_id, run_type, run_status, total_scanned, total_flagged,
            'system', run_date.date(), run_date if run_status == 'COMPLETED' else None
        ))
        
        run_ids.append(run_id)
        print(f"   ✅ Created run {run_id}: {run_type} - {run_status} ({total_scanned} scanned, {total_flagged} flagged)")
    
    # 2. Create detected cases
    print("\n🚨 Creating detected cases...")
    
    case_types = ['HARD_INELIGIBLE', 'LIKELY_MIS_TARGETED', 'LOW_CONFIDENCE_FLAG']
    confidence_levels = ['HIGH', 'MEDIUM', 'LOW']
    case_statuses = ['FLAGGED', 'UNDER_VERIFICATION', 'VERIFIED_INELIGIBLE', 'VERIFIED_ELIGIBLE']
    
    case_ids = []
    for i in range(25):
        case_id = i + 1
        beneficiary_id = f"BEN{str(i+1).zfill(6)}"
        family_id = str(uuid.uuid4())
        scheme_code = random.choice(schemes)
        case_type = random.choice(case_types)
        confidence = confidence_levels[case_types.index(case_type)] if case_type != 'LOW_CONFIDENCE_FLAG' else 'LOW'
        case_status = random.choice(case_statuses)
        risk_score = round(random.uniform(0.3, 0.95), 3)
        financial_exposure = round(random.uniform(1000, 50000), 2)
        vulnerability_score = round(random.uniform(0.1, 0.9), 3)
        priority = random.randint(1, 10)
        
        detection_timestamp = datetime.now() - timedelta(days=random.randint(0, 20))
        
        detection_method = 'HYBRID' if case_type != 'LOW_CONFIDENCE_FLAG' else 'ML_ANOMALY'
        
        cursor.execute("""
            INSERT INTO detection.detected_cases (
                case_id, run_id, beneficiary_id, family_id, scheme_code,
                case_type, confidence_level, case_status, detection_method,
                risk_score, financial_exposure, vulnerability_score, priority,
                detection_rationale, recommended_action, action_urgency,
                detection_timestamp, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (case_id) DO UPDATE SET
                case_type = EXCLUDED.case_type,
                case_status = EXCLUDED.case_status,
                risk_score = EXCLUDED.risk_score,
                priority = EXCLUDED.priority
        """, (
            case_id, random.choice(run_ids), beneficiary_id, family_id, scheme_code,
            case_type, confidence, case_status, detection_method, risk_score,
            financial_exposure, vulnerability_score, priority,
            f"Detected via {case_type.replace('_', ' ').lower()} check",
            'VERIFY_AND_SUSPEND' if case_type == 'HARD_INELIGIBLE' else 'OFFICER_REVIEW' if case_type == 'LIKELY_MIS_TARGETED' else 'ANALYTICS_REVIEW',
            'HIGH' if priority <= 3 else 'MEDIUM' if priority <= 6 else 'LOW',
            detection_timestamp, detection_timestamp, detection_timestamp
        ))
        
        case_ids.append(case_id)
    
    print(f"   ✅ Created {len(case_ids)} detected cases")
    
    # 3. Create rule detections
    print("\n📋 Creating rule detections...")
    
    rule_categories = ['ELIGIBILITY', 'OVERLAP', 'DUPLICATE', 'STATUS_CHANGE', 'INCOME_THRESHOLD', 'DOCUMENT']
    rule_names = [
        'Age below threshold', 'Income above limit', 'Duplicate scheme benefit',
        'Deceased flag detected', 'Document expired', 'Overlapping benefits'
    ]
    severities = ['CRITICAL', 'HIGH', 'MEDIUM']
    
    for case_id in case_ids[:15]:  # Create rule detections for first 15 cases
        num_rules = random.randint(1, 3)
        for j in range(num_rules):
            rule_category = random.choice(rule_categories)
            rule_name = random.choice(rule_names)
            passed = random.choice([True, False])
            severity = random.choice(severities) if not passed else 'LOW'
            
            cursor.execute("""
                INSERT INTO detection.rule_detections (
                    case_id, rule_category, rule_name,
                    rule_passed, rule_severity, evaluation_result, detected_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                case_id, rule_category, rule_name, passed, severity,
                f"Rule {'passed' if passed else 'failed'}: {rule_name}",
                datetime.now() - timedelta(days=random.randint(0, 20))
            ))
    
    print(f"   ✅ Created rule detections for {min(15, len(case_ids))} cases")
    
    # 4. Create ML detections
    print("\n🤖 Creating ML detections...")
    
    anomaly_flags = ['ML_ANOMALY_DETECTED', 'RULE_BASED_ANOMALY', 'POSSIBLE_DUPLICATE', 'POSSIBLE_OVER_BENEFITTED']
    
    for case_id in case_ids[:15]:  # Create ML detections for first 15 cases
        anomaly_score = round(random.uniform(0.4, 0.95), 3)
        risk_score = round(random.uniform(0.3, 0.9), 3)
        model_version = 'isolation_forest-v1.0'
        anomaly_flag = random.choice(anomaly_flags)
        
        cursor.execute("""
            INSERT INTO detection.ml_detections (
                case_id, model_name, model_version, model_type,
                anomaly_score, risk_score, anomaly_type,
                model_input_features, detected_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            case_id, 'Isolation Forest', model_version, 'ISOLATION_FOREST',
            anomaly_score, risk_score, anomaly_flag,
            '{"benefit_amount": 15000, "income_band": "BPL", "scheme_count": 3}',
            datetime.now() - timedelta(days=random.randint(0, 20))
        ))
    
    print(f"   ✅ Created ML detections for {min(15, len(case_ids))} cases")
    
    # 5. Create worklist assignments
    print("\n📝 Creating worklist assignments...")
    
    officers = ['OFFICER001', 'OFFICER002', 'OFFICER003']
    queues = ['SCHEME_SPECIFIC', 'HIGH_PRIORITY', 'VERIFICATION']
    assignment_statuses = ['ASSIGNED', 'IN_PROGRESS', 'COMPLETED']
    
    for case_id in case_ids[:10]:  # Assign first 10 cases
        officer_id = random.choice(officers)
        queue = random.choice(queues)
        status = random.choice(assignment_statuses)
        assigned_at = datetime.now() - timedelta(days=random.randint(0, 15))
        
        cursor.execute("""
            INSERT INTO detection.worklist_assignments (
                case_id, assigned_to, assigned_by, worklist_queue,
                assignment_priority, status, assigned_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (
            case_id, officer_id, 'admin', queue,
            random.randint(1, 10), status, assigned_at
        ))
    
    print(f"   ✅ Created worklist assignments for {min(10, len(case_ids))} cases")
    
    # 6. Create verification history
    print("\n✅ Creating verification history...")
    
    verification_methods = ['FIELD_VERIFICATION', 'DOCUMENT_REVIEW', 'CROSS_CHECK', 'APPEAL_REVIEW']
    decision_types = ['CONFIRMED_INELIGIBLE', 'FALSE_POSITIVE', 'REQUIRES_RECALCULATION', 'APPEAL_GRANTED']
    officers = ['OFFICER001', 'OFFICER002', 'OFFICER003']  # Define officers here
    
    for case_id in case_ids[:8]:  # Create verification history for first 8 cases
        method = random.choice(verification_methods)
        decision = random.choice(decision_types)
        verified_by = random.choice(officers)
        event_timestamp = datetime.now() - timedelta(days=random.randint(0, 10))
        
        verification_result_text = f"Verification result: {decision.replace('_', ' ')}"
        decision_rationale_text = f"Decision: {decision.replace('_', ' ')}"
        
        cursor.execute("""
            INSERT INTO detection.case_verification_history (
                case_id, event_type, event_description, verification_method,
                verification_result, decision_type, decision_rationale,
                event_by, event_timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            case_id, 'VERIFICATION_COMPLETED',
            f"Case verified via {method.replace('_', ' ').lower()}",
            method, verification_result_text, decision, decision_rationale_text,
            verified_by, event_timestamp
        ))
    
    print(f"   ✅ Created verification history for {min(8, len(case_ids))} cases")
    
    # Commit all changes
    conn.commit()
    cursor.close()
    connector.disconnect()
    
    print("\n" + "=" * 80)
    print("✅ Sample data creation complete!")
    print("=" * 80)
    print(f"\n📊 Summary:")
    print(f"   - Detection Runs: {len(run_ids)}")
    print(f"   - Detected Cases: {len(case_ids)}")
    print(f"   - Rule Detections: {min(15, len(case_ids))} cases")
    print(f"   - ML Detections: {min(15, len(case_ids))} cases")
    print(f"   - Worklist Assignments: {min(10, len(case_ids))} cases")
    print(f"   - Verification History: {min(8, len(case_ids))} cases")
    print(f"\n🌐 View the data at: http://localhost:5001/ai07")
    print("=" * 80)


if __name__ == '__main__':
    create_sample_data()

