"""
Event-Driven Forecast Refresh Service
Use Case ID: AI-PLATFORM-10

Handles automatic forecast refresh when relevant events occur
(e.g., eligibility updates, benefit changes, policy changes).
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import yaml
import json

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector

from .forecast_orchestrator import ForecastOrchestrator


class EventDrivenForecastRefresh:
    """
    Event-Driven Forecast Refresh Service
    
    Monitors events and automatically refreshes forecasts when:
    - Eligibility status changes
    - Benefit amounts change
    - Policy changes occur
    - New enrolments happen
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Event-Driven Refresh Service"""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "use_case_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        event_config = self.config.get('event_driven', {})
        self.enabled = event_config.get('enable_event_driven_refresh', False)
        self.refresh_triggers = event_config.get('refresh_triggers', [])
        self.auto_refresh_threshold = event_config.get('auto_refresh_threshold', 0.1)
        
        # Initialize orchestrator
        self.orchestrator = ForecastOrchestrator(config_path)
        
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
        self.orchestrator.connect()
        self.db.connect()
    
    def disconnect(self):
        """Disconnect from databases"""
        self.orchestrator.disconnect()
        self.db.disconnect()
    
    def handle_event(
        self,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle event and trigger forecast refresh if needed
        
        Args:
            event_type: Type of event (ELIGIBILITY_UPDATE, BENEFIT_CHANGE, etc.)
            event_data: Event data (family_id, scheme_code, etc.)
        
        Returns:
            Refresh result
        """
        if not self.enabled:
            return {
                'success': False,
                'message': 'Event-driven refresh is disabled'
            }
        
        if event_type not in self.refresh_triggers:
            return {
                'success': False,
                'message': f'Event type {event_type} not configured for auto-refresh'
            }
        
        family_id = event_data.get('family_id')
        if not family_id:
            return {
                'success': False,
                'message': 'family_id required for forecast refresh'
            }
        
        # Check if refresh is needed
        if not self._should_refresh(family_id, event_type, event_data):
            return {
                'success': True,
                'refreshed': False,
                'message': 'No refresh needed (change below threshold)'
            }
        
        # Get existing forecast
        existing_forecast = self.orchestrator.get_forecast(family_id=family_id, forecast_id=None)
        
        # Generate new forecast
        horizon_months = existing_forecast.get('horizon_months', 12) if existing_forecast else 12
        scenario_name = existing_forecast.get('scenario_name') if existing_forecast else None
        
        new_forecast = self.orchestrator.generate_forecast(
            family_id=family_id,
            horizon_months=horizon_months,
            scenario_name=scenario_name,
            save_to_db=True
        )
        
        # Compare and log change
        if existing_forecast:
            change = self._calculate_change(existing_forecast, new_forecast)
            
            # Log event
            self._log_refresh_event(
                event_type=event_type,
                family_id=family_id,
                existing_forecast_id=existing_forecast.get('forecast_id'),
                new_forecast_id=new_forecast.get('forecast_id'),
                change_percentage=change,
                event_data=event_data
            )
        
        return {
            'success': True,
            'refreshed': True,
            'new_forecast_id': new_forecast.get('forecast_id'),
            'message': f'Forecast refreshed due to {event_type}'
        }
    
    def _should_refresh(
        self,
        family_id: str,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> bool:
        """Determine if forecast should be refreshed"""
        # For now, always refresh on eligible events
        # In future, could check change magnitude
        
        if event_type in ['ELIGIBILITY_UPDATE', 'ENROLMENT_CHANGE']:
            return True
        
        if event_type == 'POLICY_CHANGE':
            # Check if policy affects this family's schemes
            scheme_code = event_data.get('scheme_code')
            if scheme_code:
                # Check if family has this scheme
                existing_forecast = self.orchestrator.get_forecast(family_id=family_id, forecast_id=None)
                if existing_forecast:
                    projections = existing_forecast.get('projections', [])
                    for proj in projections:
                        if proj.get('scheme_code') == scheme_code:
                            return True
        
        return False
    
    def _calculate_change(
        self,
        old_forecast: Dict[str, Any],
        new_forecast: Dict[str, Any]
    ) -> float:
        """Calculate percentage change between forecasts"""
        old_value = old_forecast.get('total_annual_value', 0) or 0
        new_value = new_forecast.get('total_annual_value', 0) or 0
        
        if old_value == 0:
            return 1.0 if new_value > 0 else 0.0
        
        return abs((new_value - old_value) / old_value)
    
    def _log_refresh_event(
        self,
        event_type: str,
        family_id: str,
        existing_forecast_id: Optional[int],
        new_forecast_id: Optional[int],
        change_percentage: float,
        event_data: Dict[str, Any]
    ):
        """Log forecast refresh event"""
        try:
            conn = self.db.connection
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO forecast.forecast_audit_logs (
                    event_type, event_timestamp, actor_type, actor_id,
                    family_id, forecast_id, event_description, event_data
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                'FORECAST_REFRESH',
                datetime.now(),
                'SYSTEM',
                None,
                family_id,
                new_forecast_id,
                f'Auto-refreshed due to {event_type}. Change: {change_percentage:.2%}',
                json.dumps({
                    'event_type': event_type,
                    'existing_forecast_id': existing_forecast_id,
                    'new_forecast_id': new_forecast_id,
                    'change_percentage': change_percentage,
                    'event_data': event_data
                })
            ))
            
            conn.commit()
            cursor.close()
        
        except Exception as e:
            print(f"⚠️  Error logging refresh event: {e}")
    
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
        try:
            conn = self.db.connection
            cursor = conn.cursor()
            
            # Find stale forecasts
            cursor.execute("""
                SELECT DISTINCT family_id, MAX(forecast_id) as latest_forecast_id
                FROM forecast.forecast_records
                WHERE generated_at < CURRENT_TIMESTAMP - INTERVAL '%s days'
                  AND status = 'COMPLETED'
                GROUP BY family_id
                ORDER BY MAX(generated_at) ASC
                LIMIT %s
            """, (days_stale, limit))
            
            stale_forecasts = cursor.fetchall()
            cursor.close()
            
            refreshed = 0
            failed = 0
            
            for family_id, forecast_id in stale_forecasts:
                try:
                    # Get forecast details
                    forecast = self.orchestrator.get_forecast(
                        family_id=str(family_id),
                        forecast_id=forecast_id
                    )
                    
                    if forecast:
                        horizon_months = forecast.get('horizon_months', 12)
                        scenario_name = forecast.get('scenario_name')
                        
                        # Generate new forecast
                        new_forecast = self.orchestrator.generate_forecast(
                            family_id=str(family_id),
                            horizon_months=horizon_months,
                            scenario_name=scenario_name,
                            save_to_db=True
                        )
                        
                        refreshed += 1
                except Exception as e:
                    print(f"⚠️  Error refreshing forecast for {family_id}: {e}")
                    failed += 1
            
            return {
                'success': True,
                'refreshed': refreshed,
                'failed': failed,
                'total': len(stale_forecasts)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

