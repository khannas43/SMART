"""
Baseline Forecaster
Use Case ID: AI-PLATFORM-10

Projects current enrolled schemes forward based on known benefit schedules
and assumptions about eligibility continuation.
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


class BaselineForecaster:
    """
    Baseline Forecaster Service
    
    Projects current enrolled schemes forward assuming:
    - Eligibility continues (no major demographic/income change)
    - Known benefit schedules apply
    - Current enrolment status maintained
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Baseline Forecaster"""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "use_case_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Configuration
        baseline_config = self.config.get('baseline_forecast', {})
        self.enabled = baseline_config.get('enable_baseline', True)
        self.assumptions = baseline_config.get('assumptions', [])
        self.conservative_ranges = baseline_config.get('conservative_ranges', True)
        
        # Forecast config
        forecast_config = self.config.get('forecast', {})
        self.default_horizon = forecast_config.get('default_horizon_months', 12)
        self.granularity = forecast_config.get('forecast_granularity', 'MONTHLY')
        
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
        for ext_db in self.external_dbs.values():
            ext_db.connect()
    
    def disconnect(self):
        """Disconnect from databases"""
        self.db.disconnect()
        for ext_db in self.external_dbs.values():
            ext_db.disconnect()
    
    def generate_baseline_forecast(
        self,
        family_id: str,
        horizon_months: int = 12,
        start_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Generate baseline forecast for a household
        
        Args:
            family_id: Family ID
            horizon_months: Forecast horizon in months
            start_date: Start date for forecast (default: today)
        
        Returns:
            Dictionary with forecast projections
        """
        if start_date is None:
            start_date = datetime.now()
        
        # Get currently enrolled schemes
        enrolled_schemes = self._get_enrolled_schemes(family_id)
        
        if not enrolled_schemes:
            return {
                'family_id': family_id,
                'forecast_type': 'BASELINE',
                'horizon_months': horizon_months,
                'start_date': start_date.isoformat(),
                'scheme_count': 0,
                'projections': [],
                'total_annual_value': 0.0,
                'total_forecast_value': 0.0,
                'assumptions': self.assumptions
            }
        
        # Generate projections for each enrolled scheme
        projections = []
        total_annual_value = 0.0
        
        for scheme_code in enrolled_schemes:
            scheme_projections = self._project_scheme_benefits(
                family_id, scheme_code, start_date, horizon_months
            )
            projections.extend(scheme_projections)
            
            # Calculate annual value for this scheme
            annual_value = sum(
                p.get('benefit_amount', 0.0) 
                for p in scheme_projections 
                if p.get('period_type') == 'ANNUAL'
            )
            total_annual_value += annual_value
        
        # Calculate total forecast value
        total_forecast_value = sum(p.get('benefit_amount', 0.0) for p in projections)
        
        return {
            'family_id': family_id,
            'forecast_type': 'BASELINE',
            'horizon_months': horizon_months,
            'start_date': start_date.isoformat(),
            'scheme_count': len(enrolled_schemes),
            'projections': projections,
            'total_annual_value': round(total_annual_value, 2),
            'total_forecast_value': round(total_forecast_value, 2),
            'assumptions': self.assumptions,
            'uncertainty_level': self._calculate_uncertainty_level(projections)
        }
    
    def _get_enrolled_schemes(self, family_id: str) -> List[str]:
        """Get currently enrolled schemes from benefit history"""
        schemes = []
        
        try:
            conn = self.external_dbs['profile_360'].connection
            cursor = conn.cursor()
            
            # Get schemes with active benefits in last 12 months
            cursor.execute("""
                SELECT DISTINCT scheme_code
                FROM profile_360.benefit_history
                WHERE beneficiary_id IN (
                    SELECT beneficiary_id 
                    FROM golden_records.beneficiaries 
                    WHERE family_id = %s::uuid AND is_active = TRUE
                )
                  AND status IN ('ACTIVE', 'PAID', 'ENROLLED')
                  AND benefit_date >= CURRENT_DATE - INTERVAL '12 months'
                ORDER BY scheme_code
            """, (family_id,))
            
            schemes = [row[0] for row in cursor.fetchall()]
            cursor.close()
        
        except Exception as e:
            print(f"⚠️  Error fetching enrolled schemes: {e}")
        
        return schemes
    
    def _project_scheme_benefits(
        self,
        family_id: str,
        scheme_code: str,
        start_date: datetime,
        horizon_months: int
    ) -> List[Dict[str, Any]]:
        """Project benefits for a specific scheme"""
        projections = []
        
        # Get benefit schedule for scheme
        schedule = self._get_benefit_schedule(scheme_code)
        
        if not schedule:
            # Default: monthly benefit, average from history
            avg_benefit = self._get_average_benefit(family_id, scheme_code)
            if avg_benefit > 0:
                schedule = {
                    'frequency': 'MONTHLY',
                    'fixed_amount': avg_benefit
                }
            else:
                return projections  # No data, skip
        
        # Generate projections based on schedule
        frequency = schedule.get('frequency', 'MONTHLY')
        fixed_amount = schedule.get('fixed_amount', 0.0)
        formula = schedule.get('formula_expression')
        
        current_date = start_date
        end_date = start_date + relativedelta(months=horizon_months)
        
        if frequency == 'MONTHLY':
            while current_date < end_date:
                period_end = min(current_date + relativedelta(months=1) - timedelta(days=1), end_date)
                
                amount = fixed_amount
                if formula:
                    # TODO: Evaluate formula
                    amount = fixed_amount  # Placeholder
                
                projections.append({
                    'scheme_code': scheme_code,
                    'scheme_name': schedule.get('scheme_name', scheme_code),
                    'projection_type': 'CURRENT_ENROLMENT',
                    'period_start': current_date.date().isoformat(),
                    'period_end': period_end.date().isoformat(),
                    'period_type': 'MONTHLY',
                    'benefit_amount': round(amount, 2),
                    'benefit_frequency': 'MONTHLY',
                    'probability': 1.0,
                    'confidence_level': 'HIGH',
                    'assumptions': [f"Eligibility continues for {scheme_code}"]
                })
                
                current_date += relativedelta(months=1)
        
        elif frequency == 'ANNUAL':
            # Annual benefit (e.g., scholarship)
            annual_date = current_date.replace(month=1, day=1)  # Assume January
            if annual_date < start_date:
                annual_date = annual_date.replace(year=annual_date.year + 1)
            
            while annual_date < end_date:
                period_end = annual_date + relativedelta(years=1) - timedelta(days=1)
                
                projections.append({
                    'scheme_code': scheme_code,
                    'scheme_name': schedule.get('scheme_name', scheme_code),
                    'projection_type': 'CURRENT_ENROLMENT',
                    'period_start': annual_date.date().isoformat(),
                    'period_end': min(period_end.date(), end_date.date()).isoformat(),
                    'period_type': 'ANNUAL',
                    'benefit_amount': round(fixed_amount, 2),
                    'benefit_frequency': 'ANNUAL',
                    'probability': 1.0,
                    'confidence_level': 'HIGH',
                    'assumptions': [f"Eligibility continues for {scheme_code}"]
                })
                
                annual_date += relativedelta(years=1)
        
        elif frequency == 'SEASONAL':
            # Seasonal benefits (e.g., crop support)
            seasonal_months = schedule.get('seasonal_months', [])
            year = start_date.year
            
            for _ in range((horizon_months // 12) + 1):
                for month in seasonal_months:
                    if month >= start_date.month or year > start_date.year:
                        period_start = datetime(year, month, 1)
                        if period_start >= start_date and period_start < end_date:
                            period_end = period_start + relativedelta(months=1) - timedelta(days=1)
                            
                            projections.append({
                                'scheme_code': scheme_code,
                                'scheme_name': schedule.get('scheme_name', scheme_code),
                                'projection_type': 'CURRENT_ENROLMENT',
                                'period_start': period_start.date().isoformat(),
                                'period_end': min(period_end.date(), end_date.date()).isoformat(),
                                'period_type': 'SEASONAL',
                                'benefit_amount': round(fixed_amount, 2),
                                'benefit_frequency': 'SEASONAL',
                                'probability': 1.0,
                                'confidence_level': 'MEDIUM',
                                'assumptions': [f"Eligibility continues for {scheme_code}"]
                            })
                year += 1
        
        return projections
    
    def _get_benefit_schedule(self, scheme_code: str) -> Optional[Dict[str, Any]]:
        """Get benefit schedule for a scheme"""
        try:
            conn = self.db.connection
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    scheme_code, scheme_name, schedule_type, frequency,
                    fixed_amount, formula_expression, slab_config,
                    conditional_on, seasonal_months, crop_season,
                    effective_from, effective_to
                FROM forecast.benefit_schedules
                WHERE scheme_code = %s
                  AND is_active = TRUE
                  AND (effective_from IS NULL OR effective_from <= CURRENT_DATE)
                  AND (effective_to IS NULL OR effective_to >= CURRENT_DATE)
                ORDER BY effective_from DESC
                LIMIT 1
            """, (scheme_code,))
            
            row = cursor.fetchone()
            cursor.close()
            
            if row:
                return {
                    'scheme_code': row[0],
                    'scheme_name': row[1],
                    'schedule_type': row[2],
                    'frequency': row[3],
                    'fixed_amount': float(row[4]) if row[4] else 0.0,
                    'formula_expression': row[5],
                    'slab_config': json.loads(row[6]) if row[6] else None,
                    'conditional_on': row[7],
                    'seasonal_months': row[8] or [],
                    'crop_season': row[9],
                    'effective_from': row[10],
                    'effective_to': row[11]
                }
        
        except Exception as e:
            print(f"⚠️  Error fetching benefit schedule: {e}")
        
        return None
    
    def _get_average_benefit(self, family_id: str, scheme_code: str) -> float:
        """Get average benefit amount from history"""
        try:
            conn = self.external_dbs['profile_360'].connection
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT AVG(benefit_amount)
                FROM profile_360.benefit_history
                WHERE beneficiary_id IN (
                    SELECT beneficiary_id 
                    FROM golden_records.beneficiaries 
                    WHERE family_id = %s::uuid
                )
                  AND scheme_code = %s
                  AND benefit_amount > 0
                  AND benefit_date >= CURRENT_DATE - INTERVAL '24 months'
            """, (family_id, scheme_code))
            
            row = cursor.fetchone()
            cursor.close()
            
            return float(row[0]) if row[0] else 0.0
        
        except Exception:
            return 0.0
    
    def _calculate_uncertainty_level(self, projections: List[Dict[str, Any]]) -> str:
        """Calculate uncertainty level for forecast"""
        if not projections:
            return 'HIGH'
        
        # Check confidence levels
        confidence_levels = [p.get('confidence_level', 'MEDIUM') for p in projections]
        
        if all(c == 'HIGH' for c in confidence_levels):
            return 'LOW'
        elif any(c == 'LOW' for c in confidence_levels):
            return 'HIGH'
        else:
            return 'MEDIUM'

