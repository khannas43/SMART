"""
Send Time Optimizer - Predicts optimal send time for nudges.
Uses historical response data to learn best time windows per family/channel.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
import yaml
from datetime import datetime, timedelta, time

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class SendTimeOptimizer:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "use_case_config.yaml"
        with open(config_path, 'r') as f:
            full_config = yaml.safe_load(f)
            self.config = full_config.get('nudging', {}).get('send_time_optimization', {})

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
        self.db.connect()

        self.enabled = self.config.get('enable_time_optimization', True)
        self.time_windows = self.config.get('time_windows', [])
        self.restrictions = self.config.get('restrictions', {})

    def select_best_time(self, family_id: str, channel_code: str, action_type: str,
                        urgency: str) -> Dict[str, Any]:
        """
        Selects the best send time for a nudge.
        Returns:
        {
            'scheduled_time': datetime,
            'time_window': str,
            'day_of_week': int,
            'confidence': float,
            'reason': str
        }
        """
        if not self.enabled:
            return self._fallback_time_selection(urgency)

        # Get preferred time window from historical data
        preferred_window = self._get_preferred_time_window(family_id, channel_code, action_type)
        
        # Get preferred day of week
        preferred_day = self._get_preferred_day(family_id, channel_code, action_type)
        
        # Calculate scheduled time
        scheduled_time = self._calculate_scheduled_time(preferred_window, preferred_day, urgency)
        
        # Apply restrictions
        scheduled_time = self._apply_restrictions(scheduled_time, channel_code)
        
        return {
            'scheduled_time': scheduled_time,
            'time_window': preferred_window or 'MORNING',
            'day_of_week': scheduled_time.weekday(),
            'is_weekend': scheduled_time.weekday() >= 5,
            'confidence': 0.75,  # Placeholder
            'reason': f'Optimized based on historical engagement for {preferred_window or "MORNING"}'
        }

    def _get_preferred_time_window(self, family_id: str, channel_code: str, action_type: str) -> Optional[str]:
        """Gets preferred time window from historical preferences."""
        try:
            cursor = self.db.connection.cursor()
            
            # Try action-specific first
            query = """
                SELECT time_window, preference_score, response_rate
                FROM nudging.send_time_preferences
                WHERE family_id = %s AND channel_code = %s AND action_type = %s
                ORDER BY preference_score DESC
                LIMIT 1;
            """
            cursor.execute(query, (family_id, channel_code, action_type))
            result = cursor.fetchone()
            
            if result:
                return result[0]  # time_window
            
            # Try general preference
            query_general = """
                SELECT time_window, preference_score, response_rate
                FROM nudging.send_time_preferences
                WHERE family_id = %s AND channel_code = %s AND action_type IS NULL
                ORDER BY preference_score DESC
                LIMIT 1;
            """
            cursor.execute(query_general, (family_id, channel_code))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            
            return None
        except Exception as e:
            print(f"⚠️  Error getting preferred time window: {e}")
            return None

    def _get_preferred_day(self, family_id: str, channel_code: str, action_type: str) -> Optional[int]:
        """Gets preferred day of week from historical data."""
        try:
            cursor = self.db.connection.cursor()
            
            # Query historical responses by day of week
            query = """
                SELECT day_of_week, AVG(CASE WHEN responded THEN 1.0 ELSE 0.0 END) as response_rate
                FROM nudging.nudge_history
                WHERE family_id = %s AND channel_code = %s
                AND action_type = %s
                GROUP BY day_of_week
                ORDER BY response_rate DESC
                LIMIT 1;
            """
            cursor.execute(query, (family_id, channel_code, action_type))
            result = cursor.fetchone()
            
            if result and result[1] > 0.3:  # Minimum threshold
                return result[0]
            
            return None
        except Exception as e:
            print(f"⚠️  Error getting preferred day: {e}")
            return None

    def _calculate_scheduled_time(self, time_window: str, day_of_week: Optional[int], urgency: str) -> datetime:
        """Calculates the scheduled datetime based on preferences."""
        now = datetime.now()
        today = now.date()
        
        # Determine target day
        if day_of_week is not None:
            # Calculate days until preferred day
            days_ahead = (day_of_week - today.weekday()) % 7
            if days_ahead == 0 and now.hour >= 20:  # If today but too late, use next week
                days_ahead = 7
            target_date = today + timedelta(days=days_ahead)
        else:
            # Default: today if before cutoff, else tomorrow
            if now.hour < 20:
                target_date = today
            else:
                target_date = today + timedelta(days=1)
        
        # Determine target time based on window
        window_config = next((w for w in self.time_windows if w['name'] == time_window), None)
        if window_config:
            # Use middle of the window
            start_hour = window_config['start_hour']
            end_hour = window_config['end_hour']
            target_hour = (start_hour + end_hour) // 2
        else:
            target_hour = 10  # Default 10 AM
        
        # Adjust for urgency (higher urgency = send sooner, even if not optimal time)
        if urgency in ['CRITICAL', 'HIGH']:
            # Send within next 2 hours if possible
            if now.hour < 20:
                target_hour = min(20, now.hour + 1)
                target_date = today
        
        scheduled_time = datetime.combine(target_date, time(target_hour, 0))
        
        # Don't schedule in the past
        if scheduled_time < now:
            scheduled_time = scheduled_time + timedelta(hours=1)
        
        return scheduled_time

    def _apply_restrictions(self, scheduled_time: datetime, channel_code: str) -> datetime:
        """Applies time restrictions based on channel and policy."""
        restrictions = self.restrictions
        
        # SMS restrictions
        if channel_code == 'SMS':
            no_after = restrictions.get('no_sms_after_hour', 20)
            no_before = restrictions.get('no_sms_before_hour', 8)
            
            if scheduled_time.hour >= no_after or scheduled_time.hour < no_before:
                # Move to next allowed window
                if scheduled_time.hour >= no_after:
                    scheduled_time = scheduled_time + timedelta(days=1)
                    scheduled_time = scheduled_time.replace(hour=no_before, minute=0)
                else:
                    scheduled_time = scheduled_time.replace(hour=no_before, minute=0)
            
            # Weekend restriction
            if restrictions.get('no_weekend_sms', False) and scheduled_time.weekday() >= 5:
                # Move to Monday
                days_until_monday = (7 - scheduled_time.weekday()) % 7
                if days_until_monday == 0:
                    days_until_monday = 7
                scheduled_time = scheduled_time + timedelta(days=days_until_monday)
        
        return scheduled_time

    def _fallback_time_selection(self, urgency: str) -> Dict[str, Any]:
        """Fallback time selection when optimization is disabled."""
        now = datetime.now()
        
        # High urgency: send within 1 hour
        if urgency in ['CRITICAL', 'HIGH']:
            scheduled_time = now + timedelta(hours=1)
        else:
            # Regular: send tomorrow morning
            scheduled_time = (now + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
        
        return {
            'scheduled_time': scheduled_time,
            'time_window': 'MORNING',
            'day_of_week': scheduled_time.weekday(),
            'is_weekend': scheduled_time.weekday() >= 5,
            'confidence': 0.5,
            'reason': 'Fallback heuristic (optimization disabled)'
        }

    def disconnect(self):
        self.db.disconnect()

