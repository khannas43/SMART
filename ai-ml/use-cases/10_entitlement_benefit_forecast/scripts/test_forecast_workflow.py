#!/usr/bin/env python3
"""
Test Forecast Workflow
Use Case ID: AI-PLATFORM-10
"""

import sys
import os
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'services'))

from forecast_orchestrator import ForecastOrchestrator


def test_forecast_workflow():
    """Test forecast generation workflow"""
    print("=" * 80)
    print("Testing Forecast Workflow")
    print("=" * 80)
    
    orchestrator = ForecastOrchestrator()
    
    try:
        orchestrator.connect()
        print("\n✅ Connected to databases")
        
        # Test family ID (use a real family ID from your data)
        test_family_id = "00000000-0000-0000-0000-000000000001"  # Replace with actual family ID
        
        print(f"\n1. Testing Baseline Forecast for family: {test_family_id}")
        print("-" * 80)
        
        baseline_forecast = orchestrator.generate_forecast(
            family_id=test_family_id,
            horizon_months=12,
            scenario_name=None,
            save_to_db=True
        )
        
        print(f"   ✅ Baseline forecast generated")
        print(f"      Forecast ID: {baseline_forecast.get('forecast_id')}")
        print(f"      Scheme Count: {baseline_forecast.get('scheme_count', 0)}")
        print(f"      Total Annual Value: ₹{baseline_forecast.get('total_annual_value', 0):,.2f}")
        print(f"      Total Forecast Value: ₹{baseline_forecast.get('total_forecast_value', 0):,.2f}")
        print(f"      Uncertainty Level: {baseline_forecast.get('uncertainty_level', 'MEDIUM')}")
        print(f"      Projections: {len(baseline_forecast.get('projections', []))}")
        
        # Test scenario forecast
        print(f"\n2. Testing Scenario Forecast (ACT_ON_RECOMMENDATIONS)")
        print("-" * 80)
        
        scenario_forecast = orchestrator.generate_forecast(
            family_id=test_family_id,
            horizon_months=12,
            scenario_name="ACT_ON_RECOMMENDATIONS",
            save_to_db=True
        )
        
        print(f"   ✅ Scenario forecast generated")
        print(f"      Forecast ID: {scenario_forecast.get('forecast_id')}")
        print(f"      Scenario: {scenario_forecast.get('scenario_name')}")
        print(f"      Scheme Count: {scenario_forecast.get('scheme_count', 0)}")
        print(f"      Total Annual Value: ₹{scenario_forecast.get('total_annual_value', 0):,.2f}")
        print(f"      Total Forecast Value: ₹{scenario_forecast.get('total_forecast_value', 0):,.2f}")
        
        # Test retrieval
        if baseline_forecast.get('forecast_id'):
            print(f"\n3. Testing Forecast Retrieval")
            print("-" * 80)
            
            retrieved = orchestrator.get_forecast(
                family_id=test_family_id,
                forecast_id=baseline_forecast.get('forecast_id')
            )
            
            if retrieved:
                print(f"   ✅ Forecast retrieved")
                print(f"      Forecast ID: {retrieved.get('forecast_id')}")
                print(f"      Status: {retrieved.get('status')}")
                print(f"      Projections: {len(retrieved.get('projections', []))}")
            else:
                print(f"   ⚠️  Forecast not found")
        
        print("\n" + "=" * 80)
        print("✅ Forecast workflow test complete!")
        print("=" * 80)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        orchestrator.disconnect()
        print("\n✅ Disconnected from databases")


if __name__ == '__main__':
    test_forecast_workflow()

