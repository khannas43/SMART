"""
Fatigue Model - Tracks and enforces nudge fatigue limits per family.
Respects vulnerability categories and cooldown periods.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, date
import pandas as pd
import yaml
from dateutil.relativedelta import relativedelta

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class FatigueModel:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "use_case_config.yaml"
        with open(config_path, 'r') as f:
            full_config = yaml.safe_load(f)
            self.config = full_config.get('nudging', {}).get('fatigue_management', {})

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

        self.enabled = self.config.get('enable_fatigue_tracking', True)
        self.vulnerability_adjustments = self.config.get('vulnerability_adjustments', {})
        self.cooldown_periods = self.config.get('cooldown_periods', {})

    def check_fatigue(self, family_id: str, proposed_channel: str = None) -> Dict[str, Any]:
        """
        Checks if a family can receive a nudge based on fatigue limits.
        Returns:
        {
            'allowed': bool,
            'reason': str,
            'cooldown_until': datetime,
            'current_counts': {...},
            'limits': {...}
        }
        """
        if not self.enabled:
            return {'allowed': True, 'reason': 'Fatigue tracking disabled'}

        today = date.today()
        now = datetime.now()

        # 1. Check cooldown periods
        cooldown_check = self._check_cooldown(family_id, now)
        if not cooldown_check['allowed']:
            return cooldown_check

        # 2. Get vulnerability category
        vulnerability = self._get_vulnerability_category(family_id)
        limits = self._get_limits_for_vulnerability(vulnerability)

        # 3. Get current counts for today, this week, this month
        current_counts = self._get_current_counts(family_id, today)

        # 4. Check limits
        checks = {
            'daily': current_counts['day'] < limits['max_per_day'],
            'weekly': current_counts['week'] < limits['max_per_week'],
            'monthly': current_counts['month'] < limits['max_per_month']
        }

        if all(checks.values()):
            return {
                'allowed': True,
                'reason': 'Within fatigue limits',
                'vulnerability_category': vulnerability,
                'current_counts': current_counts,
                'limits': limits,
                'remaining': {
                    'day': max(0, limits['max_per_day'] - current_counts['day']),
                    'week': max(0, limits['max_per_week'] - current_counts['week']),
                    'month': max(0, limits['max_per_month'] - current_counts['month'])
                }
            }
        else:
            failed_checks = [k for k, v in checks.items() if not v]
            return {
                'allowed': False,
                'reason': f'Fatigue limit exceeded: {", ".join(failed_checks)}',
                'vulnerability_category': vulnerability,
                'current_counts': current_counts,
                'limits': limits,
                'failed_checks': failed_checks
            }

    def record_nudge(self, family_id: str, channel_code: str, action_type: str):
        """Records a nudge send to update fatigue counters."""
        if not self.enabled:
            return

        today = date.today()
        now = datetime.now()

        # Update daily, weekly, monthly counters
        self._increment_counter(family_id, 'DAY', today, today, channel_code, action_type)
        
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        self._increment_counter(family_id, 'WEEK', week_start, week_end, channel_code, action_type)
        
        month_start = today.replace(day=1)
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1) - timedelta(days=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1) - timedelta(days=1)
        self._increment_counter(family_id, 'MONTH', month_start, month_end, channel_code, action_type)

    def set_cooldown(self, family_id: str, reason: str, days: int):
        """Sets a cooldown period for a family."""
        cooldown_until = datetime.now() + timedelta(days=days)
        
        try:
            cursor = self.db.connection.cursor()
            
            # Update or insert fatigue tracking record
            today = date.today()
            update_query = """
                UPDATE nudging.fatigue_tracking
                SET cooldown_until = %s, cooldown_reason = %s, updated_at = CURRENT_TIMESTAMP
                WHERE family_id = %s AND period_type = 'DAY' AND period_start = %s
                RETURNING fatigue_id;
            """
            cursor.execute(update_query, (cooldown_until, reason, family_id, today))
            
            if cursor.rowcount == 0:
                # Insert new record
                insert_query = """
                    INSERT INTO nudging.fatigue_tracking (
                        family_id, period_type, period_start, period_end,
                        cooldown_until, cooldown_reason
                    ) VALUES (%s, 'DAY', %s, %s, %s, %s);
                """
                cursor.execute(insert_query, (family_id, today, today, cooldown_until, reason))
            
            self.db.connection.commit()
            print(f"✅ Set cooldown for family {family_id}: {reason} until {cooldown_until}")
        except Exception as e:
            print(f"⚠️  Error setting cooldown: {e}")
            self.db.connection.rollback()

    def _check_cooldown(self, family_id: str, now: datetime) -> Dict[str, Any]:
        """Checks if family is in a cooldown period."""
        try:
            cursor = self.db.connection.cursor()
            query = """
                SELECT cooldown_until, cooldown_reason
                FROM nudging.fatigue_tracking
                WHERE family_id = %s
                AND cooldown_until IS NOT NULL
                AND cooldown_until > %s
                ORDER BY cooldown_until DESC
                LIMIT 1;
            """
            cursor.execute(query, (family_id, now))
            result = cursor.fetchone()
            
            if result:
                cooldown_until, reason = result
                return {
                    'allowed': False,
                    'reason': f'Cooldown period active: {reason}',
                    'cooldown_until': cooldown_until,
                    'cooldown_reason': reason
                }
            
            return {'allowed': True, 'reason': 'No active cooldown'}
        except Exception as e:
            print(f"⚠️  Error checking cooldown: {e}")
            return {'allowed': True, 'reason': 'Error checking cooldown, allowing'}

    def _get_vulnerability_category(self, family_id: str) -> str:
        """Gets vulnerability category for a family."""
        try:
            cursor = self.db.connection.cursor()
            query = """
                SELECT vulnerability_category
                FROM nudging.family_consent
                WHERE family_id = %s;
            """
            cursor.execute(query, (family_id,))
            result = cursor.fetchone()
            
            if result and result[0]:
                return result[0]
            
            # Default to MEDIUM if not set
            return 'MEDIUM'
        except Exception as e:
            print(f"⚠️  Error getting vulnerability category: {e}")
            return 'MEDIUM'

    def _get_limits_for_vulnerability(self, vulnerability: str) -> Dict[str, int]:
        """Gets fatigue limits for a vulnerability category."""
        default_limits = {
            'max_per_day': self.config.get('max_nudges_per_family_per_day', 3),
            'max_per_week': self.config.get('max_nudges_per_family_per_week', 10),
            'max_per_month': self.config.get('max_nudges_per_family_per_month', 30)
        }
        
        vuln_config = self.vulnerability_adjustments.get(f'{vulnerability.lower()}_vulnerability', {})
        
        return {
            'max_per_day': vuln_config.get('max_per_day', default_limits['max_per_day']),
            'max_per_week': vuln_config.get('max_per_week', default_limits['max_per_week']),
            'max_per_month': vuln_config.get('max_per_month', default_limits['max_per_month'])
        }

    def _get_current_counts(self, family_id: str, today: date) -> Dict[str, int]:
        """Gets current nudge counts for day, week, month."""
        try:
            cursor = self.db.connection.cursor()
            
            # Day count
            day_query = """
                SELECT COALESCE(SUM(nudge_count), 0)
                FROM nudging.fatigue_tracking
                WHERE family_id = %s AND period_type = 'DAY' AND period_start = %s;
            """
            cursor.execute(day_query, (family_id, today))
            day_count = cursor.fetchone()[0] or 0
            
            # Week count
            week_start = today - timedelta(days=today.weekday())
            week_query = """
                SELECT COALESCE(SUM(nudge_count), 0)
                FROM nudging.fatigue_tracking
                WHERE family_id = %s AND period_type = 'WEEK' 
                AND period_start = %s;
            """
            cursor.execute(week_query, (family_id, week_start))
            week_count = cursor.fetchone()[0] or 0
            
            # Month count
            month_start = today.replace(day=1)
            month_query = """
                SELECT COALESCE(SUM(nudge_count), 0)
                FROM nudging.fatigue_tracking
                WHERE family_id = %s AND period_type = 'MONTH' 
                AND period_start = %s;
            """
            cursor.execute(month_query, (family_id, month_start))
            month_count = cursor.fetchone()[0] or 0
            
            return {
                'day': int(day_count),
                'week': int(week_count),
                'month': int(month_count)
            }
        except Exception as e:
            print(f"⚠️  Error getting current counts: {e}")
            return {'day': 0, 'week': 0, 'month': 0}

    def _increment_counter(self, family_id: str, period_type: str, period_start: date,
                          period_end: date, channel_code: str, action_type: str):
        """Increments fatigue counter for a period."""
        try:
            cursor = self.db.connection.cursor()
            
            # Try to update existing record
            update_query = """
                UPDATE nudging.fatigue_tracking
                SET nudge_count = nudge_count + 1,
                    channel_counts = COALESCE(channel_counts, '{}'::jsonb) || jsonb_build_object(%s, COALESCE((channel_counts->%s)::int, 0) + 1),
                    action_type_counts = COALESCE(action_type_counts, '{}'::jsonb) || jsonb_build_object(%s, COALESCE((action_type_counts->%s)::int, 0) + 1),
                    last_nudge_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE family_id = %s AND period_type = %s AND period_start = %s
                RETURNING fatigue_id;
            """
            cursor.execute(update_query, (
                channel_code, channel_code, action_type, action_type,
                family_id, period_type, period_start
            ))
            
            if cursor.rowcount == 0:
                # Insert new record
                insert_query = """
                    INSERT INTO nudging.fatigue_tracking (
                        family_id, period_type, period_start, period_end,
                        nudge_count, channel_counts, action_type_counts, last_nudge_at
                    ) VALUES (%s, %s, %s, %s, 1, %s, %s, CURRENT_TIMESTAMP);
                """
                channel_counts = {channel_code: 1}
                action_counts = {action_type: 1}
                cursor.execute(insert_query, (
                    family_id, period_type, period_start, period_end,
                    str(channel_counts).replace("'", '"'), str(action_counts).replace("'", '"')
                ))
            
            self.db.connection.commit()
        except Exception as e:
            print(f"⚠️  Error incrementing counter: {e}")
            self.db.connection.rollback()

    def disconnect(self):
        self.db.disconnect()

