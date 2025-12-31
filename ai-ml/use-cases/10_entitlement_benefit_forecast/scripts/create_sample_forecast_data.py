#!/usr/bin/env python3
"""
Create Sample Forecast Data
Use Case ID: AI-PLATFORM-10

Creates sample forecast records and projections directly in the database for testing.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import uuid
import random
import yaml

# Add shared utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


def create_sample_forecast_data():
    """Create sample forecast data directly in database"""
    print("=" * 80)
    print("Creating Sample Forecast Data")
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
        
        print("\n✅ Connected to database")
        
        # Sample scheme codes (from benefit_schedules)
        scheme_codes = [
            'OLD_AGE_PENSION',
            'DISABILITY_PENSION',
            'WIDOW_PENSION',
            'EDUCATION_SCHOLARSHIP',
            'MID_DAY_MEAL',
            'RATION_CARD_SUBSIDY',
            'CROP_INSURANCE',
            'MATERNITY_BENEFIT'
        ]
        
        scheme_names = {
            'OLD_AGE_PENSION': 'Old Age Pension',
            'DISABILITY_PENSION': 'Disability Pension',
            'WIDOW_PENSION': 'Widow Pension',
            'EDUCATION_SCHOLARSHIP': 'Education Scholarship',
            'MID_DAY_MEAL': 'Mid-Day Meal',
            'RATION_CARD_SUBSIDY': 'Ration Card Subsidy',
            'CROP_INSURANCE': 'Crop Insurance Support',
            'MATERNITY_BENEFIT': 'Maternity Benefit'
        }
        
        # Sample benefit amounts (monthly/annual)
        benefit_amounts = {
            'OLD_AGE_PENSION': 750.00,  # Monthly
            'DISABILITY_PENSION': 600.00,  # Monthly
            'WIDOW_PENSION': 600.00,  # Monthly
            'EDUCATION_SCHOLARSHIP': 12000.00,  # Annual
            'MID_DAY_MEAL': 450.00,  # Monthly per child
            'RATION_CARD_SUBSIDY': 500.00,  # Monthly
            'CROP_INSURANCE': 5000.00,  # Seasonal
            'MATERNITY_BENEFIT': 6000.00  # Annual/one-time
        }
        
        frequencies = {
            'OLD_AGE_PENSION': 'MONTHLY',
            'DISABILITY_PENSION': 'MONTHLY',
            'WIDOW_PENSION': 'MONTHLY',
            'EDUCATION_SCHOLARSHIP': 'ANNUAL',
            'MID_DAY_MEAL': 'MONTHLY',
            'RATION_CARD_SUBSIDY': 'MONTHLY',
            'CROP_INSURANCE': 'SEASONAL',
            'MATERNITY_BENEFIT': 'ANNUAL'
        }
        
        print("\n📝 Creating sample forecasts...")
        
        forecasts_created = 0
        projections_created = 0
        
        # Create 5 sample forecasts
        for i in range(5):
            family_id = str(uuid.uuid4())
            horizon_months = 12
            forecast_type = random.choice(['BASELINE', 'SCENARIO'])
            scenario_name = None
            if forecast_type == 'SCENARIO':
                scenario_name = random.choice(['STATUS_QUO', 'ACT_ON_RECOMMENDATIONS'])
            
            # Select 3-6 schemes for this forecast
            selected_schemes = random.sample(scheme_codes, random.randint(3, 6))
            
            # Calculate totals
            total_annual_value = 0.0
            total_forecast_value = 0.0
            
            # Insert forecast record
            cursor.execute("""
                INSERT INTO forecast.forecast_records (
                    family_id, horizon_months, forecast_date, forecast_type, scenario_name,
                    status, total_annual_value, total_forecast_value, scheme_count,
                    uncertainty_level, generated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING forecast_id
            """, (
                family_id,
                horizon_months,
                datetime.now().date(),
                forecast_type,
                scenario_name,
                'COMPLETED',
                0.0,  # Will update after calculating
                0.0,  # Will update after calculating
                len(selected_schemes),
                random.choice(['LOW', 'MEDIUM', 'HIGH']),
                datetime.now()
            ))
            
            forecast_id = cursor.fetchone()[0]
            forecasts_created += 1
            
            # Create projections for each scheme
            start_date = datetime.now()
            
            for scheme_code in selected_schemes:
                projection_type = random.choice(['CURRENT_ENROLMENT', 'FUTURE_ENROLMENT', 'CURRENT_ENROLMENT'])
                benefit_amount = benefit_amounts[scheme_code]
                frequency = frequencies[scheme_code]
                
                # Generate projections based on frequency
                if frequency == 'MONTHLY':
                    # Generate 12 monthly projections
                    for month_offset in range(12):
                        period_start = start_date + relativedelta(months=month_offset)
                        period_end = period_start + relativedelta(months=1) - timedelta(days=1)
                        
                        cursor.execute("""
                            INSERT INTO forecast.forecast_projections (
                                forecast_id, scheme_code, scheme_name, projection_type,
                                period_start, period_end, period_type,
                                benefit_amount, benefit_frequency, probability, confidence_level
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            forecast_id,
                            scheme_code,
                            scheme_names[scheme_code],
                            projection_type,
                            period_start.date(),
                            period_end.date(),
                            'MONTHLY',
                            benefit_amount,
                            'MONTHLY',
                            1.0 if projection_type == 'CURRENT_ENROLMENT' else 0.7,
                            'HIGH' if projection_type == 'CURRENT_ENROLMENT' else 'MEDIUM'
                        ))
                        
                        projections_created += 1
                        total_forecast_value += benefit_amount
                    
                    total_annual_value += benefit_amount * 12
                
                elif frequency == 'ANNUAL':
                    # Generate annual projections
                    period_start = start_date.replace(month=1, day=1)
                    period_end = period_start.replace(year=period_start.year + 1) - timedelta(days=1)
                    
                    cursor.execute("""
                        INSERT INTO forecast.forecast_projections (
                            forecast_id, scheme_code, scheme_name, projection_type,
                            period_start, period_end, period_type,
                            benefit_amount, benefit_frequency, probability, confidence_level
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        forecast_id,
                        scheme_code,
                        scheme_names[scheme_code],
                        projection_type,
                        period_start.date(),
                        period_end.date(),
                        'ANNUAL',
                        benefit_amount,
                        'ANNUAL',
                        1.0 if projection_type == 'CURRENT_ENROLMENT' else 0.7,
                        'HIGH' if projection_type == 'CURRENT_ENROLMENT' else 'MEDIUM'
                    ))
                    
                    projections_created += 1
                    total_forecast_value += benefit_amount
                    total_annual_value += benefit_amount
                
                elif frequency == 'SEASONAL':
                    # Generate seasonal projections (Kharif and Rabi)
                    # Kharif: Jun-Aug, Rabi: Nov-Jan
                    seasonal_periods = [
                        (start_date.replace(month=6, day=1), start_date.replace(month=9, day=1) - timedelta(days=1)),
                        (start_date.replace(month=11, day=1), start_date.replace(month=12, day=31))
                    ]
                    
                    for period_start, period_end in seasonal_periods:
                        cursor.execute("""
                            INSERT INTO forecast.forecast_projections (
                                forecast_id, scheme_code, scheme_name, projection_type,
                                period_start, period_end, period_type,
                                benefit_amount, benefit_frequency, probability, confidence_level
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            forecast_id,
                            scheme_code,
                            scheme_names[scheme_code],
                            projection_type,
                            period_start.date(),
                            period_end.date(),
                            'SEASONAL',
                            benefit_amount,
                            'SEASONAL',
                            1.0 if projection_type == 'CURRENT_ENROLMENT' else 0.7,
                            'MEDIUM'
                        ))
                        
                        projections_created += 1
                        total_forecast_value += benefit_amount
                    
                    total_annual_value += benefit_amount * 2
            
            # Update forecast totals
            cursor.execute("""
                UPDATE forecast.forecast_records
                SET total_annual_value = %s, total_forecast_value = %s
                WHERE forecast_id = %s
            """, (total_annual_value, total_forecast_value, forecast_id))
            
            print(f"   ✅ Forecast #{forecast_id}: {len(selected_schemes)} schemes, ₹{total_annual_value:,.2f} annual")
        
        conn.commit()
        
        print(f"\n📊 Summary:")
        print(f"   ✅ Forecasts created: {forecasts_created}")
        print(f"   ✅ Projections created: {projections_created}")
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM forecast.forecast_records WHERE status = 'COMPLETED'")
        total_forecasts = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM forecast.forecast_projections")
        total_projections = cursor.fetchone()[0]
        
        print(f"\n✅ Total forecasts in database: {total_forecasts}")
        print(f"✅ Total projections in database: {total_projections}")
        
        cursor.close()
        
        print("\n" + "=" * 80)
        print("✅ Sample forecast data creation complete!")
        print("=" * 80)
        print("\n💡 Refresh http://localhost:5001/ai10 to see the data")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
    
    finally:
        db.disconnect()


if __name__ == '__main__':
    create_sample_forecast_data()

