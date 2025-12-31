"""
Time-Series Forecasting Models for Aggregate Predictions
Use Case ID: AI-PLATFORM-10

Implements ARIMA and Prophet models for aggregate forecasting at
block/district/state level for planning use cases.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
import yaml

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector

# Time-series model imports
try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.seasonal import seasonal_decompose
    ARIMA_AVAILABLE = True
except ImportError:
    ARIMA_AVAILABLE = False
    print("⚠️  statsmodels not available. Install it for ARIMA forecasting: pip install statsmodels")

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("⚠️  Prophet not available. Install it for Prophet forecasting: pip install prophet")


class TimeSeriesForecaster:
    """
    Time-Series Forecaster for Aggregate Predictions
    
    Implements:
    - ARIMA models for trend and seasonality
    - Prophet models for complex seasonality
    - Aggregate forecasting at block/district/state level
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Time-Series Forecaster"""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "use_case_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        ts_config = self.config.get('time_series_forecast', {})
        self.enabled = ts_config.get('enable_time_series', False)
        self.models = ts_config.get('models', [])
        
        # Database configuration
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
        
        # External database connections
        self.external_dbs = {}
        for db_alias, ext_config in db_configs.get('external_databases', {}).items():
            self.external_dbs[db_alias] = DBConnector(
                host=ext_config['host'],
                port=ext_config['port'],
                database=ext_config['name'],
                user=ext_config['user'],
                password=ext_config['password']
            )
        
        # Trained models cache
        self.trained_models = {}
    
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
    
    def generate_aggregate_forecast(
        self,
        scheme_code: str,
        aggregation_level: str,
        block_id: Optional[str] = None,
        district: Optional[str] = None,
        state: Optional[str] = None,
        horizon_months: int = 12,
        model_type: str = 'ARIMA'
    ) -> Dict[str, Any]:
        """
        Generate aggregate forecast using time-series models
        
        Args:
            scheme_code: Scheme to forecast
            aggregation_level: BLOCK, DISTRICT, or STATE
            block_id: Block ID (if level is BLOCK)
            district: District name (if level is DISTRICT)
            state: State name (if level is STATE)
            horizon_months: Forecast horizon
            model_type: ARIMA or PROPHET
        
        Returns:
            Forecast results with projections
        """
        # Load historical data
        historical_data = self._load_aggregate_historical_data(
            scheme_code, aggregation_level, block_id, district, state
        )
        
        if historical_data is None or len(historical_data) < 12:
            return {
                'success': False,
                'message': 'Insufficient historical data for time-series forecasting'
            }
        
        # Prepare time series
        ts = self._prepare_time_series(historical_data)
        
        # Generate forecast based on model type
        if model_type == 'ARIMA' and ARIMA_AVAILABLE:
            forecast_result = self._forecast_arima(ts, horizon_months)
        elif model_type == 'PROPHET' and PROPHET_AVAILABLE:
            forecast_result = self._forecast_prophet(ts, horizon_months)
        else:
            # Fallback to simple trend projection
            forecast_result = self._forecast_simple_trend(ts, horizon_months)
        
        # Save aggregate forecast
        forecast_id = self._save_aggregate_forecast(
            scheme_code, aggregation_level, block_id, district, state,
            horizon_months, forecast_result, model_type
        )
        
        forecast_result['forecast_id'] = forecast_id
        forecast_result['success'] = True
        
        return forecast_result
    
    def _load_aggregate_historical_data(
        self,
        scheme_code: str,
        aggregation_level: str,
        block_id: Optional[str] = None,
        district: Optional[str] = None,
        state: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """Load historical aggregate benefit data"""
        try:
            conn = self.external_dbs.get('profile_360')
            if not conn:
                return None
            
            # Build query based on aggregation level
            if aggregation_level == 'BLOCK':
                query = f"""
                    SELECT 
                        DATE_TRUNC('month', benefit_date) as month,
                        COUNT(DISTINCT beneficiary_id) as beneficiaries_count,
                        SUM(benefit_amount) as total_amount,
                        AVG(benefit_amount) as avg_amount
                    FROM profile_360.benefit_history bh
                    JOIN golden_records.beneficiaries b ON bh.beneficiary_id = b.beneficiary_id
                    JOIN golden_records.families f ON b.family_id = f.family_id
                    WHERE bh.scheme_code = %s
                      AND f.address_block = %s
                      AND bh.status IN ('ACTIVE', 'PAID')
                      AND bh.benefit_date >= CURRENT_DATE - INTERVAL '24 months'
                    GROUP BY DATE_TRUNC('month', benefit_date)
                    ORDER BY month
                """
                params = (scheme_code, block_id)
            
            elif aggregation_level == 'DISTRICT':
                query = f"""
                    SELECT 
                        DATE_TRUNC('month', benefit_date) as month,
                        COUNT(DISTINCT beneficiary_id) as beneficiaries_count,
                        SUM(benefit_amount) as total_amount,
                        AVG(benefit_amount) as avg_amount
                    FROM profile_360.benefit_history bh
                    JOIN golden_records.beneficiaries b ON bh.beneficiary_id = b.beneficiary_id
                    JOIN golden_records.families f ON b.family_id = f.family_id
                    WHERE bh.scheme_code = %s
                      AND f.address_district = %s
                      AND bh.status IN ('ACTIVE', 'PAID')
                      AND bh.benefit_date >= CURRENT_DATE - INTERVAL '24 months'
                    GROUP BY DATE_TRUNC('month', benefit_date)
                    ORDER BY month
                """
                params = (scheme_code, district)
            
            else:  # STATE
                query = f"""
                    SELECT 
                        DATE_TRUNC('month', benefit_date) as month,
                        COUNT(DISTINCT beneficiary_id) as beneficiaries_count,
                        SUM(benefit_amount) as total_amount,
                        AVG(benefit_amount) as avg_amount
                    FROM profile_360.benefit_history bh
                    JOIN golden_records.beneficiaries b ON bh.beneficiary_id = b.beneficiary_id
                    JOIN golden_records.families f ON b.family_id = f.family_id
                    WHERE bh.scheme_code = %s
                      AND f.address_state = %s
                      AND bh.status IN ('ACTIVE', 'PAID')
                      AND bh.benefit_date >= CURRENT_DATE - INTERVAL '24 months'
                    GROUP BY DATE_TRUNC('month', benefit_date)
                    ORDER BY month
                """
                params = (scheme_code, state)
            
            df = pd.read_sql(query, conn.connection, params=params)
            return df
        
        except Exception as e:
            print(f"⚠️  Error loading aggregate historical data: {e}")
            return None
    
    def _prepare_time_series(self, data: pd.DataFrame) -> pd.Series:
        """Prepare time series from historical data"""
        # Use total_amount as the time series variable
        data['month'] = pd.to_datetime(data['month'])
        data = data.set_index('month').sort_index()
        
        # Fill missing months with 0 or interpolation
        full_range = pd.date_range(
            start=data.index.min(),
            end=data.index.max(),
            freq='MS'  # Month Start
        )
        
        ts = data.reindex(full_range, fill_value=0)['total_amount']
        
        # Handle any NaN values
        ts = ts.fillna(method='ffill').fillna(0)
        
        return ts
    
    def _forecast_arima(self, ts: pd.Series, horizon_months: int) -> Dict[str, Any]:
        """Forecast using ARIMA model"""
        try:
            # Auto ARIMA would be better, but for now use simple ARIMA(1,1,1)
            # In production, would use auto_arima to find best parameters
            
            model = ARIMA(ts, order=(1, 1, 1))
            fitted_model = model.fit()
            
            # Generate forecast
            forecast = fitted_model.forecast(steps=horizon_months)
            forecast_ci = fitted_model.get_forecast(steps=horizon_months).conf_int()
            
            # Prepare projections
            projections = []
            start_date = ts.index[-1] + relativedelta(months=1)
            
            for i in range(horizon_months):
                period_start = start_date + relativedelta(months=i)
                period_end = period_start + relativedelta(months=1) - timedelta(days=1)
                
                projections.append({
                    'period_start': period_start.strftime('%Y-%m-%d'),
                    'period_end': period_end.strftime('%Y-%m-%d'),
                    'forecasted_value': float(forecast.iloc[i]),
                    'lower_bound': float(forecast_ci.iloc[i, 0]),
                    'upper_bound': float(forecast_ci.iloc[i, 1]),
                    'confidence_level': 'MEDIUM'
                })
            
            total_forecast = float(forecast.sum())
            
            return {
                'model_type': 'ARIMA',
                'model_params': '(1,1,1)',
                'projections': projections,
                'total_forecast_value': total_forecast,
                'mean_absolute_error': None,  # Would calculate from validation
                'forecast_date': datetime.now().isoformat()
            }
        
        except Exception as e:
            print(f"⚠️  ARIMA forecasting failed: {e}")
            return self._forecast_simple_trend(ts, horizon_months)
    
    def _forecast_prophet(self, ts: pd.Series, horizon_months: int) -> Dict[str, Any]:
        """Forecast using Prophet model"""
        try:
            # Prepare data for Prophet (needs 'ds' and 'y' columns)
            prophet_data = pd.DataFrame({
                'ds': ts.index,
                'y': ts.values
            })
            
            # Initialize and fit Prophet model
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=False,
                daily_seasonality=False,
                seasonality_mode='multiplicative'
            )
            
            model.fit(prophet_data)
            
            # Create future dataframe
            future = model.make_future_dataframe(periods=horizon_months, freq='MS')
            
            # Generate forecast
            forecast_df = model.predict(future)
            
            # Extract future predictions only
            future_forecast = forecast_df.tail(horizon_months)
            
            # Prepare projections
            projections = []
            for _, row in future_forecast.iterrows():
                projections.append({
                    'period_start': row['ds'].strftime('%Y-%m-%d'),
                    'period_end': (row['ds'] + relativedelta(months=1) - timedelta(days=1)).strftime('%Y-%m-%d'),
                    'forecasted_value': float(row['yhat']),
                    'lower_bound': float(row['yhat_lower']),
                    'upper_bound': float(row['yhat_upper']),
                    'confidence_level': 'HIGH'  # Prophet provides confidence intervals
                })
            
            total_forecast = float(future_forecast['yhat'].sum())
            
            return {
                'model_type': 'PROPHET',
                'model_params': 'yearly_seasonality=True',
                'projections': projections,
                'total_forecast_value': total_forecast,
                'mean_absolute_error': None,
                'forecast_date': datetime.now().isoformat()
            }
        
        except Exception as e:
            print(f"⚠️  Prophet forecasting failed: {e}")
            return self._forecast_simple_trend(ts, horizon_months)
    
    def _forecast_simple_trend(self, ts: pd.Series, horizon_months: int) -> Dict[str, Any]:
        """Simple trend-based forecast (fallback)"""
        # Calculate average growth rate
        if len(ts) < 2:
            avg_value = float(ts.mean()) if len(ts) > 0 else 0.0
        else:
            # Simple linear trend
            values = ts.values
            growth_rate = (values[-1] - values[0]) / len(values) if len(values) > 1 else 0
            
            # Use last value as base
            last_value = float(values[-1]) if len(values) > 0 else 0.0
            avg_value = max(0, last_value + growth_rate)
        
        # Generate projections
        projections = []
        start_date = ts.index[-1] + relativedelta(months=1) if len(ts) > 0 else datetime.now()
        
        for i in range(horizon_months):
            period_start = start_date + relativedelta(months=i)
            period_end = period_start + relativedelta(months=1) - timedelta(days=1)
            
            projections.append({
                'period_start': period_start.strftime('%Y-%m-%d'),
                'period_end': period_end.strftime('%Y-%m-%d'),
                'forecasted_value': avg_value,
                'lower_bound': avg_value * 0.8,
                'upper_bound': avg_value * 1.2,
                'confidence_level': 'LOW'
            })
        
        return {
            'model_type': 'SIMPLE_TREND',
            'model_params': 'linear_trend',
            'projections': projections,
            'total_forecast_value': avg_value * horizon_months,
            'mean_absolute_error': None,
            'forecast_date': datetime.now().isoformat()
        }
    
    def _save_aggregate_forecast(
        self,
        scheme_code: str,
        aggregation_level: str,
        block_id: Optional[str],
        district: Optional[str],
        state: Optional[str],
        horizon_months: int,
        forecast_result: Dict[str, Any],
        model_type: str
    ) -> int:
        """Save aggregate forecast to database"""
        try:
            conn = self.db.connection
            cursor = conn.cursor()
            
            # Save main aggregate forecast record
            cursor.execute("""
                INSERT INTO forecast.aggregate_forecasts (
                    aggregation_level, block_id, district, state,
                    forecast_date, horizon_months, scenario_name,
                    scheme_code, scheme_name,
                    total_annual_value, total_forecast_value,
                    generated_at, generated_by
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING aggregate_id
            """, (
                aggregation_level,
                block_id,
                district,
                state,
                datetime.now().date(),
                horizon_months,
                None,  # scenario_name
                scheme_code,
                scheme_code,  # scheme_name (would fetch from master)
                forecast_result.get('total_forecast_value', 0) / (horizon_months / 12),  # annual
                forecast_result.get('total_forecast_value', 0),
                datetime.now(),
                'SYSTEM'
            ))
            
            aggregate_id = cursor.fetchone()[0]
            
            # Note: Aggregate forecasts table structure may need adjustment
            # to store individual projections if needed
            
            conn.commit()
            cursor.close()
            
            return aggregate_id
        
        except Exception as e:
            print(f"⚠️  Error saving aggregate forecast: {e}")
            if 'conn' in locals():
                conn.rollback()
            return 0

