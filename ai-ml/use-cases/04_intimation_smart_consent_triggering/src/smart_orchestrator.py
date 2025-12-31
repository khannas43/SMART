"""
Smart Orchestrator Service
Manages retries, escalation, fatigue management, and prioritization
"""

import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import yaml
import pandas as pd

# Add shared utils to path
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class SmartOrchestrator:
    """Manages retry logic, escalation, and fatigue management"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Smart Orchestrator"""
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__),
                '../config/db_config.yaml'
            )
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize database connection
        db_config = self.config['database']
        self.db = DBConnector(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['name'],
            user=db_config['user'],
            password=db_config['password']
        )
        self.db.connect()
        
        # Load use case config
        use_case_config_path = os.path.join(
            os.path.dirname(__file__),
            '../config/use_case_config.yaml'
        )
        with open(use_case_config_path, 'r') as f:
            self.use_case_config = yaml.safe_load(f)
    
    def schedule_retries(self, campaign_id: Optional[int] = None) -> int:
        """
        Schedule retries for candidates who haven't responded
        
        Args:
            campaign_id: Specific campaign (None = all eligible candidates)
        
        Returns:
            Number of retries scheduled
        """
        # Find candidates eligible for retry
        query = """
            SELECT 
                cc.candidate_id,
                cc.family_id,
                cc.scheme_code,
                cc.retry_count,
                cc.sent_at,
                c.campaign_type
            FROM intimation.campaign_candidates cc
            JOIN intimation.campaigns c ON cc.campaign_id = c.campaign_id
            WHERE cc.status = 'sent'
            AND cc.consent_status IS NULL
            AND cc.retry_count < (
                SELECT COALESCE(max_retries, 3)
                FROM intimation.scheme_intimation_config
                WHERE scheme_code = cc.scheme_code
            )
            AND (
                cc.sent_at IS NULL OR
                cc.sent_at < CURRENT_TIMESTAMP - INTERVAL '1 day'
            )
        """
        
        if campaign_id:
            query += " AND cc.campaign_id = %s"
            params = [campaign_id]
        else:
            params = []
        
        query += " ORDER BY cc.priority_score DESC, cc.sent_at ASC"
        
        df = pd.read_sql(query, self.db.connection, params=params)
        
        if df.empty:
            return 0
        
        # Get retry schedule for each scheme
        scheduled_count = 0
        cursor = self.db.connection.cursor()
        
        try:
            for _, row in df.iterrows():
                retry_schedule = self._get_retry_schedule(row['scheme_code'])
                retry_count = row['retry_count']
                
                if retry_count >= len(retry_schedule):
                    continue  # Max retries reached
                
                # Calculate next retry time
                days_offset = retry_schedule[retry_count]
                if row['sent_at']:
                    sent_time = pd.to_datetime(row['sent_at'])
                    next_retry = sent_time + timedelta(days=days_offset)
                else:
                    next_retry = datetime.now() + timedelta(days=days_offset)
                
                # Update candidate
                update_query = """
                    UPDATE intimation.campaign_candidates
                    SET status = 'pending',
                        retry_count = retry_count + 1,
                        next_retry_at = %s,
                        last_retry_at = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE candidate_id = %s
                """
                cursor.execute(update_query, (next_retry, row['candidate_id']))
                scheduled_count += 1
            
            self.db.connection.commit()
            return scheduled_count
            
        except Exception as e:
            self.db.connection.rollback()
            raise Exception(f"Error scheduling retries: {str(e)}")
        finally:
            cursor.close()
    
    def check_fatigue_limits(self, family_id: str, scheme_code: str) -> bool:
        """
        Check if family has exceeded fatigue limits
        
        Args:
            family_id: Family ID
            scheme_code: Scheme code
        
        Returns:
            True if limit exceeded, False otherwise
        """
        # Update or create fatigue record
        self._update_fatigue_tracking(family_id)
        
        # Check monthly limit
        query = """
            SELECT total_messages
            FROM intimation.message_fatigue
            WHERE family_id = %s
            AND period_type = 'month'
            AND period_start <= CURRENT_DATE
            AND period_end >= CURRENT_DATE
        """
        
        df = pd.read_sql(query, self.db.connection, params=[family_id])
        if not df.empty:
            total = df.iloc[0]['total_messages']
            max_per_month = self.use_case_config['fatigue']['max_messages_per_month']
            if total >= max_per_month:
                return True
        
        # Check scheme-specific limit
        query_scheme = """
            SELECT messages_by_scheme
            FROM intimation.message_fatigue
            WHERE family_id = %s
            AND period_type = 'month'
            AND period_start <= CURRENT_DATE
            AND period_end >= CURRENT_DATE
        """
        
        df_scheme = pd.read_sql(query_scheme, self.db.connection, params=[family_id])
        if not df_scheme.empty:
            messages_by_scheme = df_scheme.iloc[0].get('messages_by_scheme', {})
            if isinstance(messages_by_scheme, str):
                import json
                messages_by_scheme = json.loads(messages_by_scheme)
            scheme_count = messages_by_scheme.get(scheme_code, 0)
            max_per_scheme = self.use_case_config['fatigue']['max_messages_per_scheme_per_month']
            if scheme_count >= max_per_scheme:
                return True
        
        return False
    
    def flag_for_escalation(self, candidate_id: int, reason: str) -> bool:
        """
        Flag candidate for escalation (field worker follow-up)
        
        Args:
            candidate_id: Candidate ID
            reason: Escalation reason
        
        Returns:
            True if flagged successfully
        """
        query = """
            UPDATE intimation.campaign_candidates
            SET status = 'escalated',
                updated_at = CURRENT_TIMESTAMP
            WHERE candidate_id = %s
            RETURNING candidate_id
        """
        
        cursor = self.db.connection.cursor()
        try:
            cursor.execute(query, (candidate_id,))
            if cursor.fetchone():
                self.db.connection.commit()
                
                # Publish escalation event
                self._publish_event('CANDIDATE_ESCALATED', {
                    'candidate_id': candidate_id,
                    'reason': reason
                })
                
                return True
            return False
        except Exception as e:
            self.db.connection.rollback()
            raise Exception(f"Error flagging for escalation: {str(e)}")
        finally:
            cursor.close()
    
    def process_expired_consents(self) -> int:
        """
        Process expired consents and update status
        
        Returns:
            Number of consents expired
        """
        query = """
            UPDATE intimation.consent_records
            SET status = 'expired',
                expired_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE status = 'given'
            AND valid_until IS NOT NULL
            AND valid_until < CURRENT_TIMESTAMP
            RETURNING consent_id
        """
        
        cursor = self.db.connection.cursor()
        try:
            cursor.execute(query)
            expired = cursor.fetchall()
            count = len(expired)
            
            if count > 0:
                self.db.connection.commit()
                # Publish events
                for (consent_id,) in expired:
                    self._publish_event('CONSENT_EXPIRED', {
                        'consent_id': consent_id
                    })
            
            return count
        except Exception as e:
            self.db.connection.rollback()
            raise Exception(f"Error processing expired consents: {str(e)}")
        finally:
            cursor.close()
    
    def _get_retry_schedule(self, scheme_code: str) -> List[int]:
        """Get retry schedule for scheme"""
        query = """
            SELECT retry_schedule_days
            FROM intimation.scheme_intimation_config
            WHERE scheme_code = %s
        """
        
        try:
            df = pd.read_sql(query, self.db.connection, params=[scheme_code])
            if not df.empty:
                schedule = df.iloc[0].get('retry_schedule_days')
                if schedule:
                    if isinstance(schedule, str):
                        import json
                        schedule = json.loads(schedule)
                    return schedule
        except Exception:
            pass
        
        # Default schedule
        default_schedule = self.use_case_config['retry']['schedule']
        return [int(d) for d in default_schedule]
    
    def _update_fatigue_tracking(self, family_id: str):
        """Update fatigue tracking for family"""
        # Get or create fatigue record for current month
        period_start = datetime.now().replace(day=1).date()
        period_end = (period_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        query = """
            INSERT INTO intimation.message_fatigue (
                family_id, period_type, period_start, period_end, total_messages
            ) VALUES (%s, 'month', %s, %s, 1)
            ON CONFLICT DO NOTHING
        """
        
        cursor = self.db.connection.cursor()
        try:
            cursor.execute(query, (family_id, period_start, period_end))
            
            # Increment count
            update_query = """
                UPDATE intimation.message_fatigue
                SET total_messages = total_messages + 1,
                    last_message_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE family_id = %s
                AND period_type = 'month'
                AND period_start = %s
            """
            cursor.execute(update_query, (family_id, period_start))
            self.db.connection.commit()
        except Exception as e:
            self.db.connection.rollback()
            print(f"Warning: Could not update fatigue tracking: {e}")
        finally:
            cursor.close()
    
    def _publish_event(self, event_type: str, event_data: Dict[str, Any]):
        """Publish event to event log"""
        query = """
            INSERT INTO intimation.intimation_events (
                event_type, event_category, event_data, event_timestamp
            ) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
        """
        
        cursor = self.db.connection.cursor()
        try:
            import json
            cursor.execute(
                query,
                (event_type, 'orchestration', json.dumps(event_data))
            )
            self.db.connection.commit()
        except Exception as e:
            print(f"Warning: Could not publish event: {e}")
        finally:
            cursor.close()
    
    def disconnect(self):
        """Close database connection"""
        if self.db:
            self.db.disconnect()

