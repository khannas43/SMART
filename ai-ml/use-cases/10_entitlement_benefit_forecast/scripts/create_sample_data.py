#!/usr/bin/env python3
"""
Create Sample Forecast Data
Use Case ID: AI-PLATFORM-10

Creates sample forecasts for demonstration and testing.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import uuid

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'services'))

from forecast_orchestrator import ForecastOrchestrator
import yaml
from db_connector import DBConnector


def create_sample_data():
    """Create sample forecast data"""
    print("=" * 80)
    print("Creating Sample Forecast Data")
    print("=" * 80)
    
    orchestrator = ForecastOrchestrator()
    
    try:
        orchestrator.connect()
        print("\n✅ Connected to databases")
        
        # Sample family IDs (using UUIDs)
        sample_families = [
            "00000000-0000-0000-0000-000000000001",
            "00000000-0000-0000-0000-000000000002",
            "00000000-0000-0000-0000-000000000003",
        ]
        
        print(f"\n📝 Generating forecasts for {len(sample_families)} families...")
        
        forecasts_created = 0
        
        for family_id in sample_families:
            try:
                # Generate baseline forecast
                print(f"\n   Family: {family_id}")
                print(f"   - Generating baseline forecast...")
                
                baseline = orchestrator.generate_forecast(
                    family_id=family_id,
                    horizon_months=12,
                    scenario_name=None,
                    save_to_db=True
                )
                
                if baseline.get('forecast_id'):
                    forecasts_created += 1
                    print(f"      ✅ Baseline forecast created (ID: {baseline.get('forecast_id')})")
                    print(f"         Schemes: {baseline.get('scheme_count', 0)}")
                    print(f"         Total Annual: ₹{baseline.get('total_annual_value', 0):,.2f}")
                else:
                    print(f"      ⚠️  Baseline forecast created but no ID returned")
                
                # Generate scenario forecast
                print(f"   - Generating scenario forecast (ACT_ON_RECOMMENDATIONS)...")
                
                scenario = orchestrator.generate_forecast(
                    family_id=family_id,
                    horizon_months=12,
                    scenario_name="ACT_ON_RECOMMENDATIONS",
                    save_to_db=True
                )
                
                if scenario.get('forecast_id'):
                    print(f"      ✅ Scenario forecast created (ID: {scenario.get('forecast_id')})")
                    print(f"         Schemes: {scenario.get('scheme_count', 0)}")
                    print(f"         Total Annual: ₹{scenario.get('total_annual_value', 0):,.2f}")
            
            except Exception as e:
                print(f"      ⚠️  Error creating forecast for {family_id}: {e}")
                # Continue with next family
        
        print(f"\n📊 Summary:")
        print(f"   ✅ Forecasts created: {forecasts_created}")
        
        # Verify forecasts in database
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
        db.connect()
        
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM forecast.forecast_records
            WHERE status = 'COMPLETED'
        """)
        total_forecasts = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM forecast.forecast_projections
        """)
        total_projections = cursor.fetchone()[0]
        
        cursor.close()
        db.disconnect()
        
        print(f"   ✅ Total forecasts in database: {total_forecasts}")
        print(f"   ✅ Total projections in database: {total_projections}")
        
        print("\n" + "=" * 80)
        print("✅ Sample data creation complete!")
        print("=" * 80)
        print("\n💡 Note: Forecasts are generated based on enrolled schemes.")
        print("   If families have no enrolled schemes, forecasts will be empty.")
        print("   You can view forecasts at http://localhost:5001/ai10")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        orchestrator.disconnect()
        print("\n✅ Disconnected from databases")


if __name__ == '__main__':
    create_sample_data()

