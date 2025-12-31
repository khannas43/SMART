"""
Scenario Forecaster
Use Case ID: AI-PLATFORM-10

Adds future enrolments from recommendations and policy changes to baseline forecast.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import yaml
import json

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector

try:
    from .baseline_forecaster import BaselineForecaster
    from ..models.probability_estimator import ProbabilityEstimator
except ImportError:
    # Fallback for script execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from forecasters.baseline_forecaster import BaselineForecaster
    from models.probability_estimator import ProbabilityEstimator


class ScenarioForecaster:
    """
    Scenario Forecaster Service
    
    Adds future enrolments from:
    - Eligibility recommendations (AI-PLATFORM-08)
    - Policy changes (new schemes, rate changes)
    - Life stage events (age-based eligibility)
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Scenario Forecaster"""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "use_case_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Configuration
        scenario_config = self.config.get('scenario_forecast', {})
        self.enabled = scenario_config.get('enable_scenarios', True)
        self.scenarios = scenario_config.get('scenarios', [])
        
        # Initialize baseline forecaster and probability estimator
        self.baseline_forecaster = BaselineForecaster(config_path)
        self.probability_estimator = ProbabilityEstimator(config_path)
        
        # Database configuration
        db_config_path = Path(__file__).parent.parent.parent / "config" / "db_config.yaml"
        with open(db_config_path, 'r') as f:
            db_config = yaml.safe_load(f)['database']
        
        self.db = DBConnector(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['name'],
            user=db_config['user'],
            password=db_config['password']
        )
        
        # External database connections
        external_dbs = yaml.safe_load(open(db_config_path, 'r')).get('external_databases', {})
        self.external_dbs = {}
        for name, ext_config in external_dbs.items():
            self.external_dbs[name] = DBConnector(
                host=ext_config['host'],
                port=ext_config['port'],
                database=ext_config['name'],
                user=ext_config['user'],
                password=ext_config['password']
            )
    
    def connect(self):
        """Connect to databases"""
        self.db.connect()
        self.baseline_forecaster.connect()
        self.probability_estimator.connect()
        for ext_db in self.external_dbs.values():
            ext_db.connect()
    
    def disconnect(self):
        """Disconnect from databases"""
        self.db.disconnect()
        self.baseline_forecaster.disconnect()
        self.probability_estimator.disconnect()
        for ext_db in self.external_dbs.values():
            ext_db.disconnect()
    
    def generate_scenario_forecast(
        self,
        family_id: str,
        scenario_name: str,
        horizon_months: int = 12,
        start_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Generate scenario-based forecast
        
        Args:
            family_id: Family ID
            scenario_name: Scenario name (STATUS_QUO, ACT_ON_RECOMMENDATIONS, POLICY_CHANGE)
            horizon_months: Forecast horizon
            start_date: Start date
        
        Returns:
            Dictionary with scenario forecast
        """
        if start_date is None:
            start_date = datetime.now()
        
        # Get scenario config
        scenario_config = self._get_scenario_config(scenario_name)
        if not scenario_config:
            raise ValueError(f"Scenario '{scenario_name}' not found")
        
        # Start with baseline forecast
        baseline = self.baseline_forecaster.generate_baseline_forecast(
            family_id, horizon_months, start_date
        )
        
        projections = baseline.get('projections', []).copy()
        assumptions = baseline.get('assumptions', []).copy()
        
        # Add scenario-specific projections
        if scenario_config.get('include_recommendations'):
            # Add future enrolments from recommendations
            recommendation_projections = self._add_recommendation_projections(
                family_id, start_date, horizon_months,
                scenario_config.get('recommendation_horizon_months', 3),
                scenario_config.get('recommendation_probability', 0.7)
            )
            projections.extend(recommendation_projections)
            assumptions.append("Includes probable future enrolments from recommendations")
        
        if scenario_config.get('include_policy_changes'):
            # Add policy change effects
            policy_projections = self._add_policy_change_projections(
                family_id, start_date, horizon_months, scenario_config.get('policy_change_ids', [])
            )
            projections.extend(policy_projections)
            assumptions.append("Includes proposed policy changes")
        
        # Add life stage event projections
        life_stage_projections = self._add_life_stage_projections(
            family_id, start_date, horizon_months
        )
        projections.extend(life_stage_projections)
        
        # Calculate totals
        total_annual_value = baseline.get('total_annual_value', 0.0)
        total_forecast_value = sum(p.get('benefit_amount', 0.0) for p in projections)
        
        # Add annual value from new projections
        for proj in projections:
            if proj.get('projection_type') != 'CURRENT_ENROLMENT' and proj.get('period_type') == 'ANNUAL':
                total_annual_value += proj.get('benefit_amount', 0.0)
        
        return {
            'family_id': family_id,
            'forecast_type': 'SCENARIO',
            'scenario_name': scenario_name,
            'scenario_description': scenario_config.get('description', ''),
            'horizon_months': horizon_months,
            'start_date': start_date.isoformat(),
            'scheme_count': len(set(p.get('scheme_code') for p in projections)),
            'projections': projections,
            'total_annual_value': round(total_annual_value, 2),
            'total_forecast_value': round(total_forecast_value, 2),
            'assumptions': assumptions,
            'uncertainty_level': self._calculate_scenario_uncertainty(projections)
        }
    
    def _get_scenario_config(self, scenario_name: str) -> Optional[Dict[str, Any]]:
        """Get scenario configuration"""
        # First try from config file
        for scenario in self.scenarios:
            if scenario.get('name') == scenario_name:
                return scenario
        
        # Then try database
        try:
            conn = self.db.connection
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    scenario_name, description, scenario_type,
                    include_recommendations, recommendation_horizon_months, recommendation_probability,
                    include_policy_changes, policy_change_ids, assumptions
                FROM forecast.forecast_scenarios
                WHERE scenario_name = %s AND is_active = TRUE
            """, (scenario_name,))
            
            row = cursor.fetchone()
            cursor.close()
            
            if row:
                return {
                    'name': row[0],
                    'description': row[1],
                    'scenario_type': row[2],
                    'include_recommendations': row[3],
                    'recommendation_horizon_months': row[4],
                    'recommendation_probability': float(row[5]) if row[5] else 0.7,
                    'include_policy_changes': row[6],
                    'policy_change_ids': row[7] or []
                }
        
        except Exception as e:
            print(f"⚠️  Error fetching scenario config: {e}")
        
        return None
    
    def _add_recommendation_projections(
        self,
        family_id: str,
        start_date: datetime,
        horizon_months: int,
        recommendation_horizon: int,
        probability: float
    ) -> List[Dict[str, Any]]:
        """Add projections from eligibility recommendations"""
        projections = []
        
        try:
            # Get recommendations from AI-PLATFORM-08 (eligibility_checker)
            conn = self.external_dbs['eligibility_checker'].connection
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT ser.scheme_code, ser.eligibility_status, ser.eligibility_score, ser.recommendation_rank
                FROM eligibility_checker.scheme_eligibility_results ser
                INNER JOIN eligibility_checker.eligibility_checks ec ON ser.check_id = ec.check_id
                WHERE ec.family_id = %s::uuid
                  AND ser.eligibility_status IN ('ELIGIBLE', 'POSSIBLE_ELIGIBLE')
                  AND ser.recommendation_rank IS NOT NULL
                  AND ser.recommendation_rank <= 5
                  AND ec.check_timestamp >= CURRENT_TIMESTAMP - INTERVAL '90 days'
                ORDER BY ser.recommendation_rank
                LIMIT 10
            """, (family_id,))
            
            recommendations = cursor.fetchall()
            cursor.close()
            
            # Calculate days since recommendation (simplified - use check_timestamp)
            days_since = (datetime.now() - start_date).days
            
            # Assume recommendations are acted upon within recommendation_horizon
            enrolment_date = start_date + relativedelta(months=recommendation_horizon)
            
            for scheme_code, eligibility_status, eligibility_score, rec_rank in recommendations:
                # Get benefit schedule
                schedule = self.baseline_forecaster._get_benefit_schedule(scheme_code)
                if not schedule:
                    avg_benefit = self.baseline_forecaster._get_average_benefit(family_id, scheme_code)
                    if avg_benefit > 0:
                        schedule = {'frequency': 'MONTHLY', 'fixed_amount': avg_benefit}
                    else:
                        continue  # Skip if no schedule or history
                
                # Use ML-based probability estimation if available
                ml_probability = self.probability_estimator.estimate_probability(
                    family_id=family_id,
                    scheme_code=scheme_code,
                    eligibility_status=eligibility_status,
                    recommendation_rank=rec_rank or 5,
                    days_since_recommendation=days_since
                )
                
                # Use ML probability if better, otherwise use configured probability
                final_probability = max(probability, ml_probability)
                
                # Generate projections from enrolment_date forward
                if enrolment_date < start_date + relativedelta(months=horizon_months):
                    scheme_projections = self._project_future_scheme(
                        scheme_code, schedule, enrolment_date,
                        start_date + relativedelta(months=horizon_months),
                        final_probability, eligibility_status
                    )
                    projections.extend(scheme_projections)
        
        except Exception as e:
            print(f"⚠️  Error adding recommendation projections: {e}")
        
        return projections
    
    def _project_future_scheme(
        self,
        scheme_code: str,
        schedule: Dict[str, Any],
        start_enrolment: datetime,
        end_date: datetime,
        probability: float,
        eligibility_status: str
    ) -> List[Dict[str, Any]]:
        """Project benefits for a future-enrolled scheme"""
        projections = []
        frequency = schedule.get('frequency', 'MONTHLY')
        fixed_amount = schedule.get('fixed_amount', 0.0)
        
        current_date = start_enrolment
        confidence = 'HIGH' if eligibility_status == 'ELIGIBLE' else 'MEDIUM'
        
        if frequency == 'MONTHLY':
            while current_date < end_date:
                period_end = min(current_date + relativedelta(months=1) - timedelta(days=1), end_date)
                
                projections.append({
                    'scheme_code': scheme_code,
                    'scheme_name': schedule.get('scheme_name', scheme_code),
                    'projection_type': 'FUTURE_ENROLMENT',
                    'period_start': current_date.date().isoformat(),
                    'period_end': period_end.date().isoformat(),
                    'period_type': 'MONTHLY',
                    'benefit_amount': round(fixed_amount * probability, 2),
                    'benefit_frequency': 'MONTHLY',
                    'probability': probability,
                    'confidence_level': confidence,
                    'assumptions': [f"Assumes application and approval for {scheme_code}"]
                })
                
                current_date += relativedelta(months=1)
        
        elif frequency == 'ANNUAL':
            annual_date = current_date.replace(month=1, day=1)
            if annual_date < current_date:
                annual_date = annual_date.replace(year=annual_date.year + 1)
            
            while annual_date < end_date:
                period_end = annual_date + relativedelta(years=1) - timedelta(days=1)
                
                projections.append({
                    'scheme_code': scheme_code,
                    'scheme_name': schedule.get('scheme_name', scheme_code),
                    'projection_type': 'FUTURE_ENROLMENT',
                    'period_start': annual_date.date().isoformat(),
                    'period_end': min(period_end.date(), end_date.date()).isoformat(),
                    'period_type': 'ANNUAL',
                    'benefit_amount': round(fixed_amount * probability, 2),
                    'benefit_frequency': 'ANNUAL',
                    'probability': probability,
                    'confidence_level': confidence,
                    'assumptions': [f"Assumes application and approval for {scheme_code}"]
                })
                
                annual_date += relativedelta(years=1)
        
        return projections
    
    def _add_policy_change_projections(
        self,
        family_id: str,
        start_date: datetime,
        horizon_months: int,
        policy_change_ids: List[int]
    ) -> List[Dict[str, Any]]:
        """Add projections based on policy changes"""
        projections = []
        
        if not policy_change_ids:
            return projections
        
        try:
            conn = self.db.connection
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    change_id, change_type, scheme_code, scheme_name,
                    change_description, effective_date, old_value, new_value
                FROM forecast.policy_changes
                WHERE change_id = ANY(%s)
                  AND is_confirmed = TRUE
                  AND effective_date >= %s
                  AND effective_date < %s
            """, (
                policy_change_ids,
                start_date.date(),
                (start_date + relativedelta(months=horizon_months)).date()
            ))
            
            changes = cursor.fetchall()
            cursor.close()
            
            # For each policy change, adjust projections
            # This is simplified - real implementation would adjust existing projections
            for change in changes:
                change_id, change_type, scheme_code, scheme_name, description, effective_date, old_value, new_value = change
                
                if change_type == 'RATE_CHANGE' and new_value:
                    # Add projection showing rate change effect
                    projections.append({
                        'scheme_code': scheme_code or 'UNKNOWN',
                        'scheme_name': scheme_name or 'Unknown Scheme',
                        'projection_type': 'POLICY_CHANGE',
                        'period_start': effective_date.isoformat(),
                        'period_end': (start_date + relativedelta(months=horizon_months)).date().isoformat(),
                        'period_type': 'MONTHLY',
                        'benefit_amount': round(float(new_value) if new_value else 0.0, 2),
                        'benefit_frequency': 'MONTHLY',
                        'probability': 1.0,
                        'confidence_level': 'MEDIUM',
                        'assumptions': [description or f"Policy change: {change_type}"]
                    })
        
        except Exception as e:
            print(f"⚠️  Error adding policy change projections: {e}")
        
        return projections
    
    def _add_life_stage_projections(
        self,
        family_id: str,
        start_date: datetime,
        horizon_months: int
    ) -> List[Dict[str, Any]]:
        """Add projections based on life stage events"""
        projections = []
        
        try:
            conn = self.db.connection
            cursor = conn.cursor()
            
            end_date = start_date + relativedelta(months=horizon_months)
            
            cursor.execute("""
                SELECT 
                    event_type, event_date, eligible_scheme_codes, eligibility_trigger_date
                FROM forecast.life_stage_events
                WHERE family_id = %s::uuid
                  AND event_date >= %s
                  AND event_date < %s
                  AND is_processed = FALSE
            """, (family_id, start_date.date(), end_date.date()))
            
            events = cursor.fetchall()
            cursor.close()
            
            for event_type, event_date, eligible_schemes, trigger_date in events:
                if eligible_schemes:
                    for scheme_code in eligible_schemes:
                        schedule = self.baseline_forecaster._get_benefit_schedule(scheme_code)
                        if schedule:
                            trigger_dt = datetime.combine(trigger_date or event_date, datetime.min.time())
                            
                            scheme_projections = self._project_future_scheme(
                                scheme_code, schedule, trigger_dt, end_date,
                                0.8, 'POSSIBLE_ELIGIBLE'  # 80% probability, medium confidence
                            )
                            
                            # Add life stage event info
                            for proj in scheme_projections:
                                proj['life_stage_event'] = event_type
                                proj['event_date'] = event_date.isoformat()
                            
                            projections.extend(scheme_projections)
        
        except Exception as e:
            print(f"⚠️  Error adding life stage projections: {e}")
        
        return projections
    
    def _calculate_scenario_uncertainty(self, projections: List[Dict[str, Any]]) -> str:
        """Calculate uncertainty level for scenario forecast"""
        if not projections:
            return 'HIGH'
        
        # Higher uncertainty if many future enrolments or policy changes
        future_count = sum(1 for p in projections if p.get('projection_type') != 'CURRENT_ENROLMENT')
        total_count = len(projections)
        
        if future_count / max(1, total_count) > 0.5:
            return 'HIGH'
        elif future_count / max(1, total_count) > 0.2:
            return 'MEDIUM'
        else:
            return 'LOW'

