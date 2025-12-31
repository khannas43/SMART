#!/usr/bin/env python3
"""
Create Sample Data for Eligibility Checker
Use Case ID: AI-PLATFORM-08
"""

import sys
from pathlib import Path
import yaml
import json
from datetime import datetime, timedelta
import random
import uuid

sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


def create_sample_data():
    """Create sample eligibility check data"""
    print("=" * 80)
    print("Creating Sample Eligibility Check Data")
    print("=" * 80)

    db_config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    with open(db_config_path, 'r') as f:
        db_configs = yaml.safe_load(f)
    
    primary_db_config = db_configs['database']
    
    connector = DBConnector(
        host=primary_db_config['host'],
        port=primary_db_config['port'],
        database=primary_db_config['name'],
        user=primary_db_config['user'],
        password=primary_db_config['password']
    )

    try:
        connector.connect()
        conn = connector.connection
        cursor = conn.cursor()
        print(f"✅ Connected to PostgreSQL: {connector.host}:{connector.port}/{connector.database}")

        # Get scheme codes
        scheme_master_config = db_configs.get('external_databases', {}).get('scheme_master', {})
        scheme_connector = DBConnector(
            host=scheme_master_config['host'],
            port=scheme_master_config['port'],
            database=scheme_master_config['name'],
            user=scheme_master_config['user'],
            password=scheme_master_config['password']
        )
        scheme_connector.connect()
        scheme_cursor = scheme_connector.connection.cursor()
        scheme_cursor.execute("SELECT scheme_code FROM public.scheme_master WHERE status = 'active' LIMIT 10")
        schemes = [row[0] for row in scheme_cursor.fetchall()]
        scheme_connector.disconnect()

        if not schemes:
            schemes = ['CHIRANJEEVI', 'OLD_AGE_PENSION', 'DISABILITY_PENSION', 'OBC_SCHOLARSHIP', 'SC_ST_SCHOLARSHIP']

        print(f"\n📋 Using schemes: {', '.join(schemes[:5])}")

        # Clear existing sample data
        cursor.execute("DELETE FROM eligibility_checker.scheme_eligibility_results")
        cursor.execute("DELETE FROM eligibility_checker.recommendation_items")
        cursor.execute("DELETE FROM eligibility_checker.recommendation_sets")
        cursor.execute("DELETE FROM eligibility_checker.eligibility_checks")
        conn.commit()
        print("✅ Cleared existing sample data")

        check_ids = []
        session_ids = []

        # Create eligibility checks
        print("\n📊 Creating eligibility checks...")
        
        user_types = ['LOGGED_IN', 'GUEST', 'ANONYMOUS']
        check_types = ['FULL_CHECK', 'SCHEME_SPECIFIC', 'QUICK_CHECK']
        check_modes = ['WEB', 'MOBILE_APP', 'CHATBOT']
        
        for i in range(15):
            check_id = i + 1
            check_ids.append(check_id)
            session_id = f"SESSION_{str(uuid.uuid4())[:8].upper()}"
            session_ids.append(session_id)
            
            user_type = random.choice(user_types)
            check_type = random.choice(check_types)
            check_mode = random.choice(check_modes)
            
            check_timestamp = datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
            
            total_schemes = random.randint(3, len(schemes))
            eligible_count = random.randint(1, min(5, total_schemes))
            possible_eligible_count = random.randint(0, min(3, total_schemes - eligible_count))
            not_eligible_count = total_schemes - eligible_count - possible_eligible_count
            
            family_id = str(uuid.uuid4()) if user_type == 'LOGGED_IN' else None
            questionnaire_responses = None
            if user_type in ['GUEST', 'ANONYMOUS']:
                questionnaire_responses = {
                    'age': random.randint(25, 75),
                    'gender': random.choice(['Male', 'Female']),
                    'district': random.choice(['Jaipur', 'Jodhpur', 'Udaipur', 'Kota']),
                    'income_band': random.choice(['Below 5000', '5000-10000', '10000-20000']),
                    'category': random.choice(['General', 'SC', 'ST', 'OBC'])
                }
            
            cursor.execute("""
                INSERT INTO eligibility_checker.eligibility_checks (
                    check_id, family_id, session_id, user_type, check_type, check_mode,
                    check_timestamp, questionnaire_responses,
                    total_schemes_checked, eligible_count, possible_eligible_count, not_eligible_count,
                    processing_time_ms, data_sources_used, consent_given
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                check_id, family_id, session_id, user_type, check_type, check_mode,
                check_timestamp,
                json.dumps(questionnaire_responses) if questionnaire_responses else None,
                total_schemes, eligible_count, possible_eligible_count, not_eligible_count,
                random.randint(100, 2000),
                ['eligibility_engine'] if user_type == 'LOGGED_IN' else ['questionnaire'],
                user_type == 'LOGGED_IN'
            ))
            
            # Create scheme eligibility results for this check
            schemes_for_check = random.sample(schemes, total_schemes)
            eligible_schemes = schemes_for_check[:eligible_count]
            possible_schemes = schemes_for_check[eligible_count:eligible_count + possible_eligible_count]
            not_eligible_schemes = schemes_for_check[eligible_count + possible_eligible_count:]
            
            for scheme_code in eligible_schemes:
                cursor.execute("""
                    INSERT INTO eligibility_checker.scheme_eligibility_results (
                        check_id, scheme_code, scheme_name, eligibility_status, eligibility_score,
                        confidence_level, recommendation_rank, priority_score, impact_score,
                        explanation_text, next_steps, met_rules, failed_rules, rule_path
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    check_id, scheme_code, f"{scheme_code} Scheme", 'ELIGIBLE',
                    round(random.uniform(0.75, 0.95), 4),
                    random.choice(['HIGH', 'MEDIUM']),
                    None,  # Will be set later for top recommendations
                    round(random.uniform(0.7, 0.9), 4),
                    round(random.uniform(0.6, 1.0), 4),
                    f"You are eligible for {scheme_code} based on your age and income level.",
                    ['Apply for this scheme', 'Gather required documents'],
                    ['AGE_ELIGIBLE', 'INCOME_ELIGIBLE'],
                    [],
                    'RULE_BASED'
                ))
            
            for scheme_code in possible_schemes:
                cursor.execute("""
                    INSERT INTO eligibility_checker.scheme_eligibility_results (
                        check_id, scheme_code, scheme_name, eligibility_status, eligibility_score,
                        confidence_level, recommendation_rank, priority_score, impact_score,
                        explanation_text, next_steps, met_rules, failed_rules, rule_path
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    check_id, scheme_code, f"{scheme_code} Scheme", 'POSSIBLE_ELIGIBLE',
                    round(random.uniform(0.5, 0.75), 4),
                    'MEDIUM',
                    None,
                    round(random.uniform(0.5, 0.7), 4),
                    round(random.uniform(0.5, 0.8), 4),
                    f"You might be eligible for {scheme_code}. Please verify with official documents.",
                    ['Verify your details', 'Contact scheme office'],
                    ['AGE_ELIGIBLE'],
                    ['INCOME_THRESHOLD_CLOSE'],
                    'QUESTIONNAIRE_BASED'
                ))
            
            for scheme_code in not_eligible_schemes:
                cursor.execute("""
                    INSERT INTO eligibility_checker.scheme_eligibility_results (
                        check_id, scheme_code, scheme_name, eligibility_status, eligibility_score,
                        confidence_level, recommendation_rank, priority_score, impact_score,
                        explanation_text, next_steps, met_rules, failed_rules, rule_path
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    check_id, scheme_code, f"{scheme_code} Scheme", 'NOT_ELIGIBLE',
                    round(random.uniform(0.1, 0.4), 4),
                    random.choice(['MEDIUM', 'LOW']),
                    None,
                    round(random.uniform(0.1, 0.4), 4),
                    round(random.uniform(0.3, 0.7), 4),
                    f"You are not eligible for {scheme_code} based on current criteria.",
                    ['Review eligibility criteria', 'Check again if situation changes'],
                    [],
                    ['AGE_NOT_ELIGIBLE', 'INCOME_ABOVE_LIMIT'],
                    'RULE_BASED'
                ))
            
            print(f"   ✅ Created check {check_id}: {user_type} - {check_type} ({total_schemes} schemes)")
        
        conn.commit()

        # Create recommendation sets for logged-in users
        print("\n📋 Creating recommendation sets...")
        logged_in_check_ids = []
        cursor.execute("""
            SELECT check_id, family_id FROM eligibility_checker.eligibility_checks 
            WHERE user_type = 'LOGGED_IN' AND family_id IS NOT NULL 
            LIMIT 5
        """)
        for row in cursor.fetchall():
            logged_in_check_ids.append((row[0], row[1]))
        
        for check_id, family_id in logged_in_check_ids:
            recommendation_id = len(check_ids) + check_id
            
            # Get top eligible schemes for this check
            cursor.execute("""
                SELECT scheme_code, scheme_name, eligibility_score, priority_score
                FROM eligibility_checker.scheme_eligibility_results
                WHERE check_id = %s AND eligibility_status IN ('ELIGIBLE', 'POSSIBLE_ELIGIBLE')
                ORDER BY priority_score DESC
                LIMIT 5
            """, (check_id,))
            
            top_schemes = cursor.fetchall()
            
            if top_schemes:
                cursor.execute("""
                    INSERT INTO eligibility_checker.recommendation_sets (
                        recommendation_id, family_id, recommendation_type,
                        total_schemes, top_recommendations_count,
                        generated_at, expires_at, is_active, based_on_check_id
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    recommendation_id, family_id, 'TOP_RECOMMENDATIONS',
                    len(top_schemes), len(top_schemes),
                    datetime.now() - timedelta(days=random.randint(0, 10)),
                    datetime.now() + timedelta(days=20),
                    True, check_id
                ))
                
                # Create recommendation items
                for rank, (scheme_code, scheme_name, eligibility_score, priority_score) in enumerate(top_schemes, 1):
                    cursor.execute("""
                        INSERT INTO eligibility_checker.recommendation_items (
                            recommendation_id, scheme_code, scheme_name, rank,
                            priority_score, eligibility_status, eligibility_score,
                            recommendation_reasons, benefit_summary
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        recommendation_id, scheme_code, scheme_name, rank,
                        float(priority_score),
                        'ELIGIBLE' if float(eligibility_score) >= 0.75 else 'POSSIBLE_ELIGIBLE',
                        float(eligibility_score),
                        ['High eligibility score', 'Matches your profile'],
                        f"Eligible for {scheme_name} benefits"
                    ))
                
                print(f"   ✅ Created recommendation set {recommendation_id} for family {family_id[:8]}... ({len(top_schemes)} items)")

        conn.commit()
        
        # Update recommendation ranks for top recommendations
        print("\n📊 Updating recommendation ranks...")
        for check_id in check_ids:
            cursor.execute("""
                UPDATE eligibility_checker.scheme_eligibility_results
                SET recommendation_rank = subq.rank
                FROM (
                    SELECT result_id, 
                           ROW_NUMBER() OVER (
                               PARTITION BY check_id 
                               ORDER BY priority_score DESC, eligibility_score DESC
                           ) as rank
                    FROM eligibility_checker.scheme_eligibility_results
                    WHERE check_id = %s 
                      AND eligibility_status IN ('ELIGIBLE', 'POSSIBLE_ELIGIBLE')
                ) subq
                WHERE eligibility_checker.scheme_eligibility_results.result_id = subq.result_id
                  AND subq.rank <= 5
            """, (check_id,))
        
        conn.commit()

        print("\n" + "=" * 80)
        print("✅ Sample data created successfully!")
        print(f"   - {len(check_ids)} eligibility checks")
        print(f"   - {len(logged_in_check_ids)} recommendation sets")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
    finally:
        if connector:
            connector.disconnect()


if __name__ == '__main__':
    create_sample_data()

