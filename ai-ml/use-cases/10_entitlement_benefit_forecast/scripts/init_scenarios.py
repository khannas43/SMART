#!/usr/bin/env python3
"""
Initialize Forecast Scenarios
Use Case ID: AI-PLATFORM-10

Initializes scenario configurations in the database.
"""

import sys
import os
from pathlib import Path
import yaml
import json

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared', 'utils'))
from db_connector import DBConnector


def init_scenarios():
    """Initialize forecast scenarios"""
    print("=" * 80)
    print("Initializing Forecast Scenarios")
    print("=" * 80)
    
    # Load database configuration
    db_config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    with open(db_config_path, 'r') as f:
        db_config = yaml.safe_load(f)['database']
    
    db = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    
    try:
        db.connect()
        conn = db.connection
        cursor = conn.cursor()
        
        # Scenarios from config
        scenarios = [
            {
                'scenario_name': 'STATUS_QUO',
                'description': 'No new schemes / status quo',
                'scenario_type': 'CITIZEN_FACING',
                'include_recommendations': False,
                'include_policy_changes': False,
                'assumptions': json.dumps(['Current enrolment status maintained', 'No new scheme applications'])
            },
            {
                'scenario_name': 'ACT_ON_RECOMMENDATIONS',
                'description': 'If you act on all top recommendations in next 3 months',
                'scenario_type': 'CITIZEN_FACING',
                'include_recommendations': True,
                'recommendation_horizon_months': 3,
                'recommendation_probability': 0.7,
                'include_policy_changes': False,
                'assumptions': json.dumps(['70% probability of applying for recommended schemes', 'Applications processed within 3 months'])
            },
            {
                'scenario_name': 'POLICY_CHANGE',
                'description': 'Under proposed policy changes',
                'scenario_type': 'PLANNER_FACING',
                'include_recommendations': False,
                'include_policy_changes': True,
                'policy_change_ids': [],
                'assumptions': json.dumps(['Proposed policy changes are implemented', 'Effective dates as per policy announcements'])
            }
        ]
        
        print(f"\n📝 Inserting {len(scenarios)} scenarios...")
        
        inserted = 0
        updated = 0
        
        for scenario in scenarios:
            try:
                # Check if exists
                cursor.execute("""
                    SELECT scenario_id FROM forecast.forecast_scenarios
                    WHERE scenario_name = %s
                """, (scenario['scenario_name'],))
                
                exists = cursor.fetchone()
                
                if exists:
                    # Update
                    cursor.execute("""
                        UPDATE forecast.forecast_scenarios SET
                            description = %s,
                            scenario_type = %s,
                            include_recommendations = %s,
                            recommendation_horizon_months = %s,
                            recommendation_probability = %s,
                            include_policy_changes = %s,
                            policy_change_ids = %s,
                            assumptions = %s::jsonb,
                            is_active = TRUE,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE scenario_name = %s
                    """, (
                        scenario['description'],
                        scenario['scenario_type'],
                        scenario.get('include_recommendations', False),
                        scenario.get('recommendation_horizon_months'),
                        scenario.get('recommendation_probability', 1.0),
                        scenario.get('include_policy_changes', False),
                        scenario.get('policy_change_ids', []),
                        scenario.get('assumptions', json.dumps([])),
                        scenario['scenario_name']
                    ))
                    updated += 1
                    print(f"   ✅ Updated {scenario['scenario_name']}")
                else:
                    # Insert
                    cursor.execute("""
                        INSERT INTO forecast.forecast_scenarios (
                            scenario_name, description, scenario_type,
                            include_recommendations, recommendation_horizon_months, recommendation_probability,
                            include_policy_changes, policy_change_ids, assumptions, is_active
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, TRUE)
                    """, (
                        scenario['scenario_name'],
                        scenario['description'],
                        scenario['scenario_type'],
                        scenario.get('include_recommendations', False),
                        scenario.get('recommendation_horizon_months'),
                        scenario.get('recommendation_probability', 1.0),
                        scenario.get('include_policy_changes', False),
                        scenario.get('policy_change_ids', []),
                        scenario.get('assumptions', json.dumps([]))
                    ))
                    inserted += 1
                    print(f"   ✅ Inserted {scenario['scenario_name']}")
            
            except Exception as e:
                print(f"   ⚠️  Error inserting {scenario['scenario_name']}: {e}")
                conn.rollback()
                conn = db.connection
                cursor = conn.cursor()
        
        conn.commit()
        
        print(f"\n📊 Summary:")
        print(f"   ✅ Inserted: {inserted}")
        print(f"   ✅ Updated: {updated}")
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM forecast.forecast_scenarios WHERE is_active = TRUE")
        count = cursor.fetchone()[0]
        print(f"\n✅ Active scenarios in database: {count}")
        
        cursor.close()
        
        print("\n" + "=" * 80)
        print("✅ Scenario initialization complete!")
        print("=" * 80)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
    
    finally:
        db.disconnect()


if __name__ == '__main__':
    init_scenarios()

