"""
Forecast Orchestrator
Use Case ID: AI-PLATFORM-10

Main orchestrator service that coordinates baseline and scenario forecasting.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import yaml
import json

# Import forecasters
try:
    from ..forecasters.baseline_forecaster import BaselineForecaster
    from ..forecasters.scenario_forecaster import ScenarioForecaster
    from .aggregate_forecast_service import AggregateForecastService
    from ..models.probability_estimator import ProbabilityEstimator
    from .event_driven_forecast_refresh import EventDrivenForecastRefresh
except ImportError:
    # Fallback for script execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from forecasters.baseline_forecaster import BaselineForecaster
    from forecasters.scenario_forecaster import ScenarioForecaster
    from services.aggregate_forecast_service import AggregateForecastService
    from models.probability_estimator import ProbabilityEstimator
    from services.event_driven_forecast_refresh import EventDrivenForecastRefresh


class ForecastOrchestrator:
    """
    Forecast Orchestrator Service
    
    Coordinates:
    - Baseline forecast generation
    - Scenario forecast generation
    - Forecast persistence
    - Forecast retrieval
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Forecast Orchestrator"""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "use_case_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize forecasters and services
        self.baseline_forecaster = BaselineForecaster(config_path)
        self.scenario_forecaster = ScenarioForecaster(config_path)
        self.aggregate_service = AggregateForecastService(config_path)
        self.probability_estimator = ProbabilityEstimator(config_path)
        self.event_refresh = EventDrivenForecastRefresh(config_path)
        
        # Database
        db_config_path = Path(__file__).parent.parent.parent / "config" / "db_config.yaml"
        with open(db_config_path, 'r') as f:
            db_config = yaml.safe_load(f)['database']
        
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
        from db_connector import DBConnector
        self.db = DBConnector(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['name'],
            user=db_config['user'],
            password=db_config['password']
        )
    
    def connect(self):
        """Connect all services to databases"""
        self.baseline_forecaster.connect()
        self.scenario_forecaster.connect()
        self.aggregate_service.connect()
        self.probability_estimator.connect()
        self.event_refresh.connect()
        self.db.connect()
    
    def disconnect(self):
        """Disconnect all services from databases"""
        self.baseline_forecaster.disconnect()
        self.scenario_forecaster.disconnect()
        self.aggregate_service.disconnect()
        self.probability_estimator.disconnect()
        self.event_refresh.disconnect()
        self.db.disconnect()
    
    def generate_forecast(
        self,
        family_id: str,
        horizon_months: int = 12,
        scenario_name: Optional[str] = None,
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        Generate forecast for a household
        
        Args:
            family_id: Family ID
            horizon_months: Forecast horizon in months
            scenario_name: Scenario name (None for baseline, or STATUS_QUO, ACT_ON_RECOMMENDATIONS, etc.)
            save_to_db: Whether to save to database
        
        Returns:
            Forecast result
        """
        if scenario_name:
            forecast_result = self.scenario_forecaster.generate_scenario_forecast(
                family_id, scenario_name, horizon_months
            )
            forecast_type = 'SCENARIO'
        else:
            forecast_result = self.baseline_forecaster.generate_baseline_forecast(
                family_id, horizon_months
            )
            forecast_type = 'BASELINE'
            scenario_name = None
        
        # Save to database
        if save_to_db:
            forecast_id = self._save_forecast(forecast_result, forecast_type, scenario_name)
            forecast_result['forecast_id'] = forecast_id
            
            # Save projections
            self._save_projections(forecast_id, forecast_result.get('projections', []))
            
            # Save assumptions
            self._save_assumptions(forecast_id, forecast_result.get('assumptions', []))
        
        return forecast_result
    
    def get_forecast(
        self,
        family_id: str,
        forecast_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Get existing forecast from database"""
        conn = self.db.connection
        cursor = conn.cursor()
        
        try:
            if forecast_id:
                cursor.execute("""
                    SELECT 
                        forecast_id, family_id, horizon_months, forecast_date,
                        forecast_type, scenario_name, status,
                        total_annual_value, total_forecast_value, scheme_count,
                        uncertainty_level, generated_at
                    FROM forecast.forecast_records
                    WHERE forecast_id = %s
                """, (forecast_id,))
            else:
                cursor.execute("""
                    SELECT 
                        forecast_id, family_id, horizon_months, forecast_date,
                        forecast_type, scenario_name, status,
                        total_annual_value, total_forecast_value, scheme_count,
                        uncertainty_level, generated_at
                    FROM forecast.forecast_records
                    WHERE family_id = %s::uuid
                    ORDER BY generated_at DESC
                    LIMIT 1
                """, (family_id,))
            
            row = cursor.fetchone()
            
            if not row:
                cursor.close()
                return None
            
            forecast = {
                'forecast_id': row[0],
                'family_id': str(row[1]),
                'horizon_months': row[2],
                'forecast_date': row[3].isoformat() if row[3] else None,
                'forecast_type': row[4],
                'scenario_name': row[5],
                'status': row[6],
                'total_annual_value': float(row[7]) if row[7] else 0.0,
                'total_forecast_value': float(row[8]) if row[8] else 0.0,
                'scheme_count': row[9] or 0,
                'uncertainty_level': row[10],
                'generated_at': row[11].isoformat() if row[11] else None
            }
            
            # Get projections
            cursor.execute("""
                SELECT 
                    projection_id, scheme_code, scheme_name, projection_type,
                    period_start, period_end, period_type,
                    benefit_amount, benefit_frequency, probability, confidence_level,
                    assumptions, life_stage_event, event_date
                FROM forecast.forecast_projections
                WHERE forecast_id = %s
                ORDER BY period_start, scheme_code
            """, (forecast['forecast_id'],))
            
            projections = []
            for proj_row in cursor.fetchall():
                projections.append({
                    'projection_id': proj_row[0],
                    'scheme_code': proj_row[1],
                    'scheme_name': proj_row[2],
                    'projection_type': proj_row[3],
                    'period_start': proj_row[4].isoformat() if proj_row[4] else None,
                    'period_end': proj_row[5].isoformat() if proj_row[5] else None,
                    'period_type': proj_row[6],
                    'benefit_amount': float(proj_row[7]) if proj_row[7] else 0.0,
                    'benefit_frequency': proj_row[8],
                    'probability': float(proj_row[9]) if proj_row[9] else 1.0,
                    'confidence_level': proj_row[10],
                    'assumptions': proj_row[11] or [],
                    'life_stage_event': proj_row[12],
                    'event_date': proj_row[13].isoformat() if proj_row[13] else None
                })
            
            forecast['projections'] = projections
            
            # Get assumptions
            cursor.execute("""
                SELECT assumption_text, assumption_category, confidence_level
                FROM forecast.forecast_assumptions
                WHERE forecast_id = %s
            """, (forecast['forecast_id'],))
            
            assumptions = []
            for assump_row in cursor.fetchall():
                assumptions.append({
                    'text': assump_row[0],
                    'category': assump_row[1],
                    'confidence': assump_row[2]
                })
            
            forecast['assumptions'] = assumptions
            
            cursor.close()
            return forecast
        
        except Exception as e:
            print(f"⚠️  Error fetching forecast: {e}")
            cursor.close()
            return None
    
    def _save_forecast(
        self,
        forecast_result: Dict[str, Any],
        forecast_type: str,
        scenario_name: Optional[str]
    ) -> int:
        """Save forecast record to database"""
        conn = self.db.connection
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO forecast.forecast_records (
                    family_id, horizon_months, forecast_date, forecast_type, scenario_name,
                    status, total_annual_value, total_forecast_value, scheme_count,
                    uncertainty_level, assumptions
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING forecast_id
            """, (
                forecast_result['family_id'],
                forecast_result['horizon_months'],
                datetime.now().date(),
                forecast_type,
                scenario_name,
                'COMPLETED',
                forecast_result['total_annual_value'],
                forecast_result['total_forecast_value'],
                forecast_result['scheme_count'],
                forecast_result.get('uncertainty_level', 'MEDIUM'),
                json.dumps(forecast_result.get('assumptions', []))
            ))
            
            forecast_id = cursor.fetchone()[0]
            conn.commit()
            return forecast_id
        
        except Exception as e:
            print(f"⚠️  Error saving forecast: {e}")
            conn.rollback()
            return 0
    
    def _save_projections(
        self,
        forecast_id: int,
        projections: List[Dict[str, Any]]
    ):
        """Save forecast projections to database"""
        conn = self.db.connection
        cursor = conn.cursor()
        
        try:
            for proj in projections:
                cursor.execute("""
                    INSERT INTO forecast.forecast_projections (
                        forecast_id, scheme_code, scheme_name, projection_type,
                        period_start, period_end, period_type,
                        benefit_amount, benefit_frequency, probability, confidence_level,
                        assumptions, life_stage_event, event_date
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    forecast_id,
                    proj.get('scheme_code'),
                    proj.get('scheme_name'),
                    proj.get('projection_type', 'CURRENT_ENROLMENT'),
                    proj.get('period_start'),
                    proj.get('period_end'),
                    proj.get('period_type', 'MONTHLY'),
                    proj.get('benefit_amount', 0.0),
                    proj.get('benefit_frequency', 'MONTHLY'),
                    proj.get('probability', 1.0),
                    proj.get('confidence_level', 'MEDIUM'),
                    proj.get('assumptions', []),
                    proj.get('life_stage_event'),
                    proj.get('event_date')
                ))
            
            conn.commit()
        
        except Exception as e:
            print(f"⚠️  Error saving projections: {e}")
            conn.rollback()
    
    def _save_assumptions(
        self,
        forecast_id: int,
        assumptions: List[str]
    ):
        """Save forecast assumptions to database"""
        conn = self.db.connection
        cursor = conn.cursor()
        
        try:
            for assumption in assumptions:
                cursor.execute("""
                    INSERT INTO forecast.forecast_assumptions (
                        forecast_id, assumption_category, assumption_text,
                        assumption_source, confidence_level
                    ) VALUES (%s, %s, %s, %s, %s)
                """, (
                    forecast_id,
                    'GENERAL',
                    assumption,
                    'SYSTEM',
                    'MEDIUM'
                ))
            
            conn.commit()
        
        except Exception as e:
            print(f"⚠️  Error saving assumptions: {e}")
            conn.rollback()
    
    def get_aggregate_forecast(
        self,
        aggregation_level: str,
        block_id: Optional[str] = None,
        district: Optional[str] = None,
        state: Optional[str] = None,
        horizon_months: int = 12,
        scenario_name: Optional[str] = None,
        scheme_codes: Optional[List[str]] = None,
        model_type: str = 'ARIMA'
    ) -> Dict[str, Any]:
        """
        Get aggregate forecast for planning using time-series models
        
        Args:
            aggregation_level: BLOCK, DISTRICT, STATE
            block_id: Block ID (if level is BLOCK)
            district: District name (if level is DISTRICT)
            state: State name (if level is STATE)
            horizon_months: Forecast horizon
            scenario_name: Scenario name (for future use)
            scheme_codes: List of scheme codes (None = all active)
            model_type: ARIMA or PROPHET
        
        Returns:
            Aggregate forecast data
        """
        return self.aggregate_service.generate_aggregate_forecasts(
            aggregation_level=aggregation_level,
            block_id=block_id,
            district=district,
            state=state,
            scheme_codes=scheme_codes,
            horizon_months=horizon_months,
            model_type=model_type
        )
    
    def estimate_recommendation_probability(
        self,
        family_id: str,
        scheme_code: str,
        eligibility_status: str,
        recommendation_rank: int,
        days_since_recommendation: int = 0
    ) -> float:
        """
        Estimate probability that family will act on recommendation
        
        Args:
            family_id: Family ID
            scheme_code: Recommended scheme code
            eligibility_status: ELIGIBLE or POSSIBLE_ELIGIBLE
            recommendation_rank: Rank of recommendation (1-10)
            days_since_recommendation: Days since recommendation
        
        Returns:
            Probability score (0.0 to 1.0)
        """
        return self.probability_estimator.estimate_probability(
            family_id=family_id,
            scheme_code=scheme_code,
            eligibility_status=eligibility_status,
            recommendation_rank=recommendation_rank,
            days_since_recommendation=days_since_recommendation
        )
    
    def handle_event(
        self,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle event and trigger forecast refresh if needed
        
        Args:
            event_type: ELIGIBILITY_UPDATE, BENEFIT_CHANGE, POLICY_CHANGE, ENROLMENT_CHANGE
            event_data: Event data with family_id, scheme_code, etc.
        
        Returns:
            Refresh result
        """
        return self.event_refresh.handle_event(event_type, event_data)
    
    def refresh_stale_forecasts(
        self,
        days_stale: int = 30,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Refresh forecasts that are older than specified days
        
        Args:
            days_stale: Number of days after which forecast is considered stale
            limit: Maximum number of forecasts to refresh
        
        Returns:
            Refresh results
        """
        return self.event_refresh.refresh_stale_forecasts(days_stale, limit)

