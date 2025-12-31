"""
Aggregate Forecast Service
Use Case ID: AI-PLATFORM-10

Service for generating aggregate forecasts at block/district/state level
using time-series models for planning use cases.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector

from ..models.time_series_models import TimeSeriesForecaster


class AggregateForecastService:
    """
    Aggregate Forecast Service
    
    Coordinates aggregate forecasting using time-series models
    for planning and budget estimation.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Aggregate Forecast Service"""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "use_case_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize time-series forecaster
        self.ts_forecaster = TimeSeriesForecaster(config_path)
        
        # Database
        db_config_path = Path(__file__).parent.parent.parent / "config" / "db_config.yaml"
        with open(db_config_path, 'r') as f:
            db_configs = yaml.safe_load(f)
        
        self.db = DBConnector(
            host=db_configs['database']['host'],
            port=db_configs['database']['port'],
            database=db_configs['database']['name'],
            user=db_configs['database']['user'],
            password=db_configs['database']['password']
        )
    
    def connect(self):
        """Connect to databases"""
        self.ts_forecaster.connect()
        self.db.connect()
    
    def disconnect(self):
        """Disconnect from databases"""
        self.ts_forecaster.disconnect()
        self.db.disconnect()
    
    def generate_aggregate_forecasts(
        self,
        aggregation_level: str,
        block_id: Optional[str] = None,
        district: Optional[str] = None,
        state: Optional[str] = None,
        scheme_codes: Optional[List[str]] = None,
        horizon_months: int = 12,
        model_type: str = 'ARIMA'
    ) -> Dict[str, Any]:
        """
        Generate aggregate forecasts for multiple schemes
        
        Args:
            aggregation_level: BLOCK, DISTRICT, or STATE
            block_id: Block ID (if level is BLOCK)
            district: District name (if level is DISTRICT)
            state: State name (if level is STATE)
            scheme_codes: List of scheme codes to forecast (None = all active schemes)
            horizon_months: Forecast horizon
            model_type: ARIMA or PROPHET
        
        Returns:
            Dictionary with forecasts for each scheme
        """
        # Get scheme codes if not provided
        if scheme_codes is None:
            scheme_codes = self._get_active_scheme_codes()
        
        forecasts = {}
        total_value = 0.0
        
        for scheme_code in scheme_codes:
            try:
                forecast_result = self.ts_forecaster.generate_aggregate_forecast(
                    scheme_code=scheme_code,
                    aggregation_level=aggregation_level,
                    block_id=block_id,
                    district=district,
                    state=state,
                    horizon_months=horizon_months,
                    model_type=model_type
                )
                
                if forecast_result.get('success'):
                    forecasts[scheme_code] = forecast_result
                    total_value += forecast_result.get('total_forecast_value', 0)
            
            except Exception as e:
                print(f"⚠️  Error forecasting {scheme_code}: {e}")
                forecasts[scheme_code] = {
                    'success': False,
                    'error': str(e)
                }
        
        return {
            'success': True,
            'aggregation_level': aggregation_level,
            'block_id': block_id,
            'district': district,
            'state': state,
            'horizon_months': horizon_months,
            'model_type': model_type,
            'scheme_forecasts': forecasts,
            'total_forecast_value': total_value,
            'scheme_count': len([f for f in forecasts.values() if f.get('success')])
        }
    
    def _get_active_scheme_codes(self) -> List[str]:
        """Get list of active scheme codes"""
        try:
            conn = self.db.connection
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT scheme_code
                FROM forecast.benefit_schedules
                WHERE is_active = TRUE
                ORDER BY scheme_code
            """)
            
            schemes = [row[0] for row in cursor.fetchall()]
            cursor.close()
            
            return schemes if schemes else []
        
        except Exception as e:
            print(f"⚠️  Error getting active schemes: {e}")
            return []
    
    def get_aggregate_forecast_summary(
        self,
        aggregation_level: str,
        block_id: Optional[str] = None,
        district: Optional[str] = None,
        state: Optional[str] = None,
        horizon_months: int = 12
    ) -> Dict[str, Any]:
        """Get summary of aggregate forecasts for a region"""
        try:
            conn = self.db.connection
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    scheme_code, scheme_name,
                    SUM(total_annual_value) as total_annual,
                    SUM(total_forecast_value) as total_forecast,
                    COUNT(*) as forecast_count
                FROM forecast.aggregate_forecasts
                WHERE aggregation_level = %s
                  AND forecast_date >= CURRENT_DATE - INTERVAL '30 days'
                  AND horizon_months = %s
                  {}
                GROUP BY scheme_code, scheme_name
                ORDER BY total_forecast DESC
            """
            
            where_clause = ""
            params = [aggregation_level, horizon_months]
            
            if block_id:
                where_clause = "AND block_id = %s"
                params.append(block_id)
            elif district:
                where_clause = "AND district = %s"
                params.append(district)
            elif state:
                where_clause = "AND state = %s"
                params.append(state)
            
            query = query.format(where_clause)
            
            cursor.execute(query, params)
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'scheme_code': row[0],
                    'scheme_name': row[1],
                    'total_annual_value': float(row[2]) if row[2] else 0.0,
                    'total_forecast_value': float(row[3]) if row[3] else 0.0,
                    'forecast_count': row[4] or 0
                })
            
            cursor.close()
            
            return {
                'success': True,
                'aggregation_level': aggregation_level,
                'block_id': block_id,
                'district': district,
                'state': state,
                'horizon_months': horizon_months,
                'schemes': results,
                'total_schemes': len(results),
                'grand_total': sum(r['total_forecast_value'] for r in results)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

