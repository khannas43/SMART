#!/usr/bin/env python3
"""
Initialize Benefit Schedules
Use Case ID: AI-PLATFORM-10

Populates benefit_schedules table with scheme benefit patterns.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared', 'utils'))
from db_connector import DBConnector
import yaml


def init_benefit_schedules():
    """Initialize benefit schedules"""
    print("=" * 80)
    print("Initializing Benefit Schedules")
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
        
        # Sample benefit schedules
        schedules = [
            {
                'scheme_code': 'OLD_AGE_PENSION',
                'scheme_name': 'Old Age Pension',
                'schedule_type': 'FIXED',
                'frequency': 'MONTHLY',
                'fixed_amount': 750.00,
                'effective_from': '2024-01-01'
            },
            {
                'scheme_code': 'DISABILITY_PENSION',
                'scheme_name': 'Disability Pension',
                'schedule_type': 'FIXED',
                'frequency': 'MONTHLY',
                'fixed_amount': 600.00,
                'effective_from': '2024-01-01'
            },
            {
                'scheme_code': 'WIDOW_PENSION',
                'scheme_name': 'Widow Pension',
                'schedule_type': 'FIXED',
                'frequency': 'MONTHLY',
                'fixed_amount': 600.00,
                'effective_from': '2024-01-01'
            },
            {
                'scheme_code': 'MATERNITY_BENEFIT',
                'scheme_name': 'Maternity Benefit',
                'schedule_type': 'FIXED',
                'frequency': 'ANNUAL',
                'fixed_amount': 6000.00,
                'effective_from': '2024-01-01'
            },
            {
                'scheme_code': 'EDUCATION_SCHOLARSHIP',
                'scheme_name': 'Education Scholarship',
                'schedule_type': 'CONDITIONAL',
                'frequency': 'ANNUAL',
                'fixed_amount': 12000.00,
                'conditional_on': 'ATTENDANCE',
                'effective_from': '2024-01-01'
            },
            {
                'scheme_code': 'MID_DAY_MEAL',
                'scheme_name': 'Mid-Day Meal',
                'schedule_type': 'FIXED',
                'frequency': 'MONTHLY',
                'fixed_amount': 450.00,  # Per child per month (approx)
                'effective_from': '2024-01-01'
            },
            {
                'scheme_code': 'RATION_CARD_SUBSIDY',
                'scheme_name': 'Ration Card Subsidy',
                'schedule_type': 'FIXED',
                'frequency': 'MONTHLY',
                'fixed_amount': 500.00,  # Approx monthly subsidy
                'effective_from': '2024-01-01'
            },
            {
                'scheme_code': 'CROP_INSURANCE',
                'scheme_name': 'Crop Insurance Support',
                'schedule_type': 'SEASONAL',
                'frequency': 'SEASONAL',
                'fixed_amount': 5000.00,
                'seasonal_months': [6, 7, 8, 11, 12, 1],  # Kharif and Rabi seasons
                'crop_season': 'BOTH',
                'effective_from': '2024-01-01'
            },
            {
                'scheme_code': 'HEALTH_INSURANCE',
                'scheme_name': 'Health Insurance Coverage',
                'schedule_type': 'FIXED',
                'frequency': 'ANNUAL',
                'fixed_amount': 500000.00,  # Coverage amount (not monthly benefit)
                'effective_from': '2024-01-01'
            },
            {
                'scheme_code': 'HOUSING_SUBSIDY',
                'scheme_name': 'Housing Subsidy',
                'schedule_type': 'FIXED',
                'frequency': 'ANNUAL',
                'fixed_amount': 150000.00,  # One-time or annual subsidy
                'effective_from': '2024-01-01'
            }
        ]
        
        print(f"\n📝 Inserting {len(schedules)} benefit schedules...")
        
        inserted = 0
        updated = 0
        
        for schedule in schedules:
            try:
                # First check if it exists
                cursor.execute("""
                    SELECT schedule_id FROM forecast.benefit_schedules
                    WHERE scheme_code = %s AND effective_from = %s
                """, (schedule['scheme_code'], schedule['effective_from']))
                
                exists = cursor.fetchone()
                
                if exists:
                    # Update existing
                    cursor.execute("""
                        UPDATE forecast.benefit_schedules SET
                            scheme_name = %s,
                            schedule_type = %s,
                            frequency = %s,
                            fixed_amount = %s,
                            conditional_on = %s,
                            seasonal_months = %s,
                            crop_season = %s,
                            is_active = TRUE,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE scheme_code = %s AND effective_from = %s
                    """, (
                        schedule['scheme_name'],
                        schedule['schedule_type'],
                        schedule['frequency'],
                        schedule['fixed_amount'],
                        schedule.get('conditional_on'),
                        schedule.get('seasonal_months'),
                        schedule.get('crop_season'),
                        schedule['scheme_code'],
                        schedule['effective_from']
                    ))
                    updated += 1
                    print(f"   ✅ Updated {schedule['scheme_code']}: {schedule['scheme_name']}")
                else:
                    # Insert new
                    cursor.execute("""
                        INSERT INTO forecast.benefit_schedules (
                            scheme_code, scheme_name, schedule_type, frequency,
                            fixed_amount, conditional_on, seasonal_months, crop_season,
                            effective_from, is_active
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                    """, (
                        schedule['scheme_code'],
                        schedule['scheme_name'],
                        schedule['schedule_type'],
                        schedule['frequency'],
                        schedule['fixed_amount'],
                        schedule.get('conditional_on'),
                        schedule.get('seasonal_months'),
                        schedule.get('crop_season'),
                        schedule['effective_from']
                    ))
                    inserted += 1
                    print(f"   ✅ Inserted {schedule['scheme_code']}: {schedule['scheme_name']}")
            
            except Exception as e:
                print(f"   ⚠️  Error inserting {schedule['scheme_code']}: {e}")
                conn.rollback()
                conn = db.connection
                cursor = conn.cursor()
        
        conn.commit()
        
        print(f"\n📊 Summary:")
        print(f"   ✅ Inserted: {inserted}")
        print(f"   ✅ Updated: {updated}")
        print(f"   ✅ Total: {len(schedules)}")
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM forecast.benefit_schedules WHERE is_active = TRUE")
        count = cursor.fetchone()[0]
        print(f"\n✅ Active benefit schedules in database: {count}")
        
        cursor.close()
        
        print("\n" + "=" * 80)
        print("✅ Benefit schedules initialization complete!")
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
    init_benefit_schedules()

