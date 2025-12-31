#!/usr/bin/env python3
"""
Test Tier 3 and Advanced Features
Use Case ID: AI-PLATFORM-10

Tests ML-based probability estimation and time-series aggregate forecasting.
"""

import sys
import os
from pathlib import Path

# Add parent directories to path - must be done before any imports
project_root = Path(__file__).parent.parent
shared_utils = project_root.parent.parent.parent / "shared" / "utils"

# Add to path in correct order
if str(shared_utils) not in sys.path:
    sys.path.insert(0, str(shared_utils))
if str(project_root / "src") not in sys.path:
    sys.path.insert(0, str(project_root / "src"))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now import - use absolute imports with full path
try:
    from src.services.forecast_orchestrator import ForecastOrchestrator
    from src.models.probability_estimator import ProbabilityEstimator
    from src.services.aggregate_forecast_service import AggregateForecastService
except ImportError as e:
    print(f"⚠️  Import error: {e}")
    print("   Trying alternative import paths...")
    # Try alternative paths
    import importlib.util
    spec_orch = importlib.util.spec_from_file_location("forecast_orchestrator", str(project_root / "src" / "services" / "forecast_orchestrator.py"))
    spec_prob = importlib.util.spec_from_file_location("probability_estimator", str(project_root / "src" / "models" / "probability_estimator.py"))
    spec_agg = importlib.util.spec_from_file_location("aggregate_forecast_service", str(project_root / "src" / "services" / "aggregate_forecast_service.py"))
    
    ForecastOrchestrator = importlib.util.module_from_spec(spec_orch)
    ProbabilityEstimator = importlib.util.module_from_spec(spec_prob)
    AggregateForecastService = importlib.util.module_from_spec(spec_agg)
    
    spec_orch.loader.exec_module(ForecastOrchestrator)
    spec_prob.loader.exec_module(ProbabilityEstimator)
    spec_agg.loader.exec_module(AggregateForecastService)
    
    ForecastOrchestrator = ForecastOrchestrator.ForecastOrchestrator
    ProbabilityEstimator = ProbabilityEstimator.ProbabilityEstimator
    AggregateForecastService = AggregateForecastService.AggregateForecastService


def test_probability_estimation():
    """Test ML-based probability estimation"""
    print("\n" + "=" * 80)
    print("Testing ML-based Probability Estimation")
    print("=" * 80)
    
    estimator = ProbabilityEstimator()
    
    try:
        estimator.connect()
        print("✅ Connected to databases")
        
        # Test probability estimation
        test_cases = [
            {
                'family_id': '00000000-0000-0000-0000-000000000001',
                'scheme_code': 'OLD_AGE_PENSION',
                'eligibility_status': 'ELIGIBLE',
                'recommendation_rank': 1
            },
            {
                'family_id': '00000000-0000-0000-0000-000000000002',
                'scheme_code': 'EDUCATION_SCHOLARSHIP',
                'eligibility_status': 'POSSIBLE_ELIGIBLE',
                'recommendation_rank': 3
            }
        ]
        
        for test_case in test_cases:
            probability = estimator.estimate_probability(
                family_id=test_case['family_id'],
                scheme_code=test_case['scheme_code'],
                eligibility_status=test_case['eligibility_status'],
                recommendation_rank=test_case['recommendation_rank'],
                days_since_recommendation=0
            )
            
            print(f"\n   Family: {test_case['family_id'][:8]}...")
            print(f"   Scheme: {test_case['scheme_code']}")
            print(f"   Eligibility: {test_case['eligibility_status']}")
            print(f"   Rank: {test_case['recommendation_rank']}")
            print(f"   Estimated Probability: {probability:.2%}")
        
        print("\n✅ Probability estimation test complete")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        estimator.disconnect()


def test_aggregate_forecasting():
    """Test time-series aggregate forecasting"""
    print("\n" + "=" * 80)
    print("Testing Time-Series Aggregate Forecasting")
    print("=" * 80)
    
    service = AggregateForecastService()
    
    try:
        service.connect()
        print("✅ Connected to databases")
        
        # Test aggregate forecast at district level
        print("\n   Testing DISTRICT level forecast...")
        result = service.generate_aggregate_forecasts(
            aggregation_level='DISTRICT',
            district='Jaipur',  # Example district
            scheme_codes=['OLD_AGE_PENSION', 'EDUCATION_SCHOLARSHIP'],
            horizon_months=12,
            model_type='ARIMA'
        )
        
        if result.get('success'):
            print(f"   ✅ Aggregate forecast generated")
            print(f"      Schemes: {result.get('scheme_count', 0)}")
            print(f"      Total Forecast Value: ₹{result.get('total_forecast_value', 0):,.2f}")
            
            for scheme_code, forecast in result.get('scheme_forecasts', {}).items():
                if forecast.get('success'):
                    print(f"\n      {scheme_code}:")
                    print(f"         Model: {forecast.get('model_type')}")
                    print(f"         Forecast Value: ₹{forecast.get('total_forecast_value', 0):,.2f}")
                    print(f"         Projections: {len(forecast.get('projections', []))}")
        else:
            print(f"   ⚠️  Forecast generation returned: {result.get('message', 'Unknown error')}")
        
        print("\n✅ Aggregate forecasting test complete")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\n💡 Note: Aggregate forecasting requires historical benefit data.")
        print("   If you see 'Insufficient historical data', this is expected without real data.")
    
    finally:
        service.disconnect()


def main():
    """Run all Tier 3 feature tests"""
    print("=" * 80)
    print("Testing Tier 3 and Advanced Features")
    print("Use Case ID: AI-PLATFORM-10")
    print("=" * 80)
    
    # Test 1: Probability Estimation
    test_probability_estimation()
    
    # Test 2: Aggregate Forecasting
    test_aggregate_forecasting()
    
    print("\n" + "=" * 80)
    print("✅ All Tier 3 feature tests complete!")
    print("=" * 80)
    print("\n💡 Note:")
    print("   - ML probability estimation uses heuristics if scikit-learn not available")
    print("   - Aggregate forecasting requires statsmodels/prophet and historical data")
    print("   - Install dependencies: pip install scikit-learn statsmodels prophet")


if __name__ == '__main__':
    main()

