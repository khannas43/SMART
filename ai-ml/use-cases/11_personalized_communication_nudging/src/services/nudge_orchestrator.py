"""
Nudge Orchestrator - Main service that coordinates all nudge optimization components.
Handles the end-to-end workflow of scheduling and managing nudges.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import yaml
import uuid
import json

# Add shared utils to path
shared_utils_path = Path(__file__).parent.parent.parent.parent.parent / "shared" / "utils"
if str(shared_utils_path) not in sys.path:
    sys.path.insert(0, str(shared_utils_path))
from db_connector import DBConnector

# Import models
try:
    from ..models.fatigue_model import FatigueModel
    from ..models.channel_optimizer import ChannelOptimizer
    from ..models.send_time_optimizer import SendTimeOptimizer
    from ..models.content_personalizer import ContentPersonalizer
except ImportError:
    # Fallback for script execution
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from models.fatigue_model import FatigueModel
    from models.channel_optimizer import ChannelOptimizer
    from models.send_time_optimizer import SendTimeOptimizer
    from models.content_personalizer import ContentPersonalizer


class NudgeOrchestrator:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "use_case_config.yaml"
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

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

        # Initialize models
        self.fatigue_model = FatigueModel(config_path)
        self.channel_optimizer = ChannelOptimizer(config_path)
        self.send_time_optimizer = SendTimeOptimizer(config_path)
        self.content_personalizer = ContentPersonalizer(config_path)

    def connect(self):
        """Connects all models to the database."""
        # Models already connect in __init__, but this allows explicit connection
        if not self.db.connection:
            self.db.connect()

    def schedule_nudge(self, action_type: str, family_id: str, urgency: str,
                      expiry_date: Optional[datetime] = None,
                      action_context: Optional[Dict[str, Any]] = None,
                      scheduled_by: str = 'SYSTEM') -> Dict[str, Any]:
        """
        Main method to schedule a nudge.
        
        Args:
            action_type: Type of action (renewal, missing_doc, consent, deadline, informational)
            family_id: Family identifier
            urgency: Urgency level (LOW, MEDIUM, HIGH, CRITICAL)
            expiry_date: Optional expiry date for the action
            action_context: Additional context (scheme_code, document_type, etc.)
            scheduled_by: Who scheduled the nudge (USER, SYSTEM, ADMIN)
        
        Returns:
            Dict with nudge_id, scheduled_channel, scheduled_time, template_id, etc.
        """
        print(f"📅 Scheduling nudge: {action_type} for family {family_id} (urgency: {urgency})")
        
        # 1. Check fatigue limits
        fatigue_check = self.fatigue_model.check_fatigue(family_id)
        if not fatigue_check.get('allowed', True):
            return {
                'success': False,
                'reason': fatigue_check.get('reason', 'Fatigue limit exceeded'),
                'fatigue_details': fatigue_check
            }
        
        # 2. Get family preferences (consent, language, etc.)
        family_prefs = self._get_family_preferences(family_id)
        if not family_prefs.get('consent_given', True):
            return {
                'success': False,
                'reason': 'Consent not given for communications'
            }
        
        # 3. Select optimal channel
        channel_result = self.channel_optimizer.select_best_channel(
            family_id, action_type, urgency, action_context or {}
        )
        
        # 4. Select optimal send time
        time_result = self.send_time_optimizer.select_best_time(
            family_id, channel_result['channel_code'], action_type, urgency
        )
        
        # 5. Select and personalize content
        content_result = self.content_personalizer.select_template(
            family_id, action_type, channel_result['channel_code'], urgency,
            family_prefs.get('preferred_language', 'en')
        )
        
        if not content_result.get('template_id'):
            return {
                'success': False,
                'reason': 'No suitable template found',
                'details': content_result
            }
        
        # 6. Create nudge record
        nudge_id = self._create_nudge_record(
            family_id, action_type, action_context, urgency, expiry_date,
            channel_result['channel_code'], time_result['scheduled_time'],
            content_result['template_id'], content_result['personalized_content'],
            scheduled_by
        )
        
        # 7. Update fatigue tracking (pre-emptively, will be confirmed on send)
        # Note: We don't increment here, only on actual send
        
        # 8. Log audit
        self._log_audit(
            'NUDGE_SCHEDULED',
            'NUDGE',
            str(nudge_id),
            scheduled_by,
            {
                'family_id': family_id,
                'action_type': action_type,
                'urgency': urgency,
                'channel': channel_result['channel_code'],
                'scheduled_time': time_result['scheduled_time'].isoformat()
            }
        )
        
        return {
            'success': True,
            'nudge_id': str(nudge_id),
            'family_id': family_id,
            'action_type': action_type,
            'urgency': urgency,
            'scheduled_channel': channel_result['channel_code'],
            'scheduled_time': time_result['scheduled_time'].isoformat(),
            'time_window': time_result['time_window'],
            'template_id': str(content_result['template_id']),
            'personalized_content': content_result['personalized_content'],
            'channel_confidence': channel_result.get('confidence', 0.5),
            'time_confidence': time_result.get('confidence', 0.5),
            'content_strategy': content_result.get('selection_strategy', 'HEURISTIC'),
            'fatigue_status': fatigue_check
        }

    def get_nudge_history(self, family_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Gets nudge history for a family."""
        try:
            cursor = self.db.connection.cursor()
            query = """
                SELECT 
                    n.nudge_id, n.action_type, n.urgency, n.scheduled_channel,
                    n.scheduled_time, n.status, n.delivery_status,
                    n.sent_at, n.delivered_at, n.opened_at, n.clicked_at,
                    n.responded_at, n.completed_at, n.personalized_content,
                    t.template_name, t.tone
                FROM nudging.nudges n
                LEFT JOIN nudging.nudge_templates t ON n.template_id = t.template_id
                WHERE n.family_id = %s
                ORDER BY n.scheduled_time DESC
                LIMIT %s;
            """
            cursor.execute(query, (family_id, limit))
            results = cursor.fetchall()
            
            history = []
            for row in results:
                history.append({
                    'nudge_id': str(row[0]),
                    'action_type': row[1],
                    'urgency': row[2],
                    'channel': row[3],
                    'scheduled_time': row[4].isoformat() if row[4] else None,
                    'status': row[5],
                    'delivery_status': row[6],
                    'sent_at': row[7].isoformat() if row[7] else None,
                    'delivered_at': row[8].isoformat() if row[8] else None,
                    'opened_at': row[9].isoformat() if row[9] else None,
                    'clicked_at': row[10].isoformat() if row[10] else None,
                    'responded_at': row[11].isoformat() if row[11] else None,
                    'completed_at': row[12].isoformat() if row[12] else None,
                    'personalized_content': row[13],
                    'template_name': row[14],
                    'tone': row[15]
                })
            
            return history
        except Exception as e:
            print(f"⚠️  Error getting nudge history: {e}")
            return []

    def record_feedback(self, nudge_id: str, event_type: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Records feedback event for a nudge (delivered, opened, clicked, responded, etc.).
        Updates nudge status and triggers learning updates.
        """
        try:
            cursor = self.db.connection.cursor()
            
            # Get nudge details
            query = """
                SELECT family_id, action_type, scheduled_channel, template_id, status
                FROM nudging.nudges
                WHERE nudge_id = %s::uuid;
            """
            cursor.execute(query, (nudge_id,))
            nudge = cursor.fetchone()
            
            if not nudge:
                return {'success': False, 'reason': 'Nudge not found'}
            
            family_id, action_type, channel_code, template_id_str, current_status = nudge
            template_id = uuid.UUID(template_id_str) if template_id_str else None
            
            # Update nudge status based on event
            update_fields = []
            update_values = []
            
            now = datetime.now()
            
            if event_type == 'DELIVERED':
                update_fields.append('delivery_status = %s')
                update_values.append('DELIVERED')
                update_fields.append('delivered_at = %s')
                update_values.append(now)
                if current_status == 'SENT':
                    update_fields.append('status = %s')
                    update_values.append('DELIVERED')
            
            elif event_type == 'OPENED':
                update_fields.append('opened_at = %s')
                update_values.append(now)
                update_fields.append('status = %s')
                update_values.append('OPENED')
            
            elif event_type == 'CLICKED':
                update_fields.append('clicked_at = %s')
                update_values.append(now)
                update_fields.append('status = %s')
                update_values.append('CLICKED')
            
            elif event_type == 'RESPONDED':
                update_fields.append('responded_at = %s')
                update_values.append(now)
                update_fields.append('status = %s')
                update_values.append('RESPONDED')
            
            elif event_type == 'COMPLETED':
                update_fields.append('completed_at = %s')
                update_values.append(now)
                update_fields.append('status = %s')
                update_values.append('COMPLETED')
                
                # Record fatigue (only on completion)
                self.fatigue_model.record_nudge(family_id, channel_code, action_type)
            
            elif event_type == 'FAILED':
                update_fields.append('status = %s')
                update_values.append('FAILED')
                update_fields.append('failed_reason = %s')
                update_values.append(metadata.get('reason', 'Unknown') if metadata else 'Unknown')
            
            if update_fields:
                update_query = f"""
                    UPDATE nudging.nudges
                    SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                    WHERE nudge_id = %s;
                """
                update_values.append(nudge_id)
                cursor.execute(update_query, tuple(update_values))
                
                # Add to history (convert template_id to string)
                self._add_to_history(nudge_id, family_id, channel_code, action_type, str(template_id) if template_id else None, event_type, now)
                
                # Update learning models
                self._update_learning_models(family_id, channel_code, action_type, template_id, event_type)
            
            self.db.connection.commit()
            
            return {'success': True, 'event_type': event_type}
        except Exception as e:
            print(f"⚠️  Error recording feedback: {e}")
            self.db.connection.rollback()
            return {'success': False, 'error': str(e)}

    def _get_family_preferences(self, family_id: str) -> Dict[str, Any]:
        """Gets family consent and preferences."""
        try:
            cursor = self.db.connection.cursor()
            query = """
                SELECT consent_given, consent_channels, opt_out_channels,
                       preferred_language, preferred_time_windows, vulnerability_category
                FROM nudging.family_consent
                WHERE family_id = %s;
            """
            cursor.execute(query, (family_id,))
            result = cursor.fetchone()
            
            if result:
                return {
                    'consent_given': result[0],
                    'consent_channels': result[1] if result[1] else [],
                    'opt_out_channels': result[2] if result[2] else [],
                    'preferred_language': result[3] or 'en',
                    'preferred_time_windows': result[4] if result[4] else [],
                    'vulnerability_category': result[5] or 'MEDIUM'
                }
            
            # Default preferences
            return {
                'consent_given': True,
                'consent_channels': [],
                'opt_out_channels': [],
                'preferred_language': 'en',
                'preferred_time_windows': [],
                'vulnerability_category': 'MEDIUM'
            }
        except Exception as e:
            print(f"⚠️  Error getting family preferences: {e}")
            return {'consent_given': True, 'preferred_language': 'en', 'vulnerability_category': 'MEDIUM'}

    def _create_nudge_record(self, family_id: str, action_type: str, action_context: Dict[str, Any],
                            urgency: str, expiry_date: Optional[datetime], channel_code: str,
                            scheduled_time: datetime, template_id: uuid.UUID,
                            personalized_content: str, scheduled_by: str) -> uuid.UUID:
        """Creates a nudge record in the database."""
        try:
            cursor = self.db.connection.cursor()
            nudge_id = uuid.uuid4()
            
            insert_query = """
                INSERT INTO nudging.nudges (
                    nudge_id, family_id, action_type, action_context, urgency,
                    expiry_date, scheduled_channel, scheduled_time, template_id,
                    personalized_content, status, created_at
                ) VALUES (%s::uuid, %s, %s, %s, %s, %s, %s, %s, %s::uuid, %s, 'SCHEDULED', CURRENT_TIMESTAMP)
                RETURNING nudge_id;
            """
            cursor.execute(insert_query, (
                str(nudge_id), family_id, action_type,
                json.dumps(action_context) if action_context else None,
                urgency, expiry_date, channel_code, scheduled_time,
                str(template_id), personalized_content
            ))
            
            self.db.connection.commit()
            return nudge_id
        except Exception as e:
            print(f"⚠️  Error creating nudge record: {e}")
            self.db.connection.rollback()
            raise

    def _add_to_history(self, nudge_id: str, family_id: str, channel_code: str,
                       action_type: str, template_id: str, event_type: str, timestamp: datetime):
        """Adds event to nudge history for learning."""
        try:
            cursor = self.db.connection.cursor()
            
            # Determine which flags to set
            delivered = event_type == 'DELIVERED'
            opened = event_type == 'OPENED'
            clicked = event_type == 'CLICKED'
            responded = event_type == 'RESPONDED'
            completed = event_type == 'COMPLETED'
            ignored = event_type == 'IGNORED'
            
            # Get time window info
            hour = timestamp.hour
            if 9 <= hour < 12:
                time_window = 'MORNING'
            elif 12 <= hour < 17:
                time_window = 'AFTERNOON'
            elif 17 <= hour < 20:
                time_window = 'EVENING'
            else:
                time_window = 'NIGHT'
            
            insert_query = """
                INSERT INTO nudging.nudge_history (
                    nudge_id, family_id, channel_code, action_type, template_id,
                    sent_time, time_window, day_of_week, is_weekend,
                    delivered, opened, clicked, responded, completed, ignored
                ) VALUES (%s::uuid, %s, %s, %s, %s::uuid, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """
            
            cursor.execute(insert_query, (
                nudge_id, family_id, channel_code, action_type, template_id if template_id else None,
                timestamp, time_window, timestamp.weekday(), timestamp.weekday() >= 5,
                delivered, opened, clicked, responded, completed, ignored
            ))
            
            self.db.connection.commit()
        except Exception as e:
            print(f"⚠️  Error adding to history: {e}")
            self.db.connection.rollback()

    def _update_learning_models(self, family_id: str, channel_code: str, action_type: str,
                               template_id: uuid.UUID, event_type: str):
        """Updates learning models based on feedback (simplified for now)."""
        # In a full implementation, this would update:
        # - Channel preferences scores
        # - Send time preferences
        # - Content effectiveness metrics
        # For now, just a placeholder
        pass

    def _log_audit(self, action_type: str, entity_type: str, entity_id: str,
                  performed_by: str, details: Dict[str, Any]):
        """Logs audit record."""
        try:
            cursor = self.db.connection.cursor()
            insert_query = """
                INSERT INTO nudging.nudge_audit_logs (
                    action_type, entity_type, entity_id, performed_by, details
                ) VALUES (%s, %s, %s, %s, %s);
            """
            cursor.execute(insert_query, (
                action_type, entity_type, entity_id, performed_by, json.dumps(details)
            ))
            self.db.connection.commit()
        except Exception as e:
            print(f"⚠️  Error logging audit: {e}")
            self.db.connection.rollback()

    def disconnect(self):
        self.db.disconnect()
        self.fatigue_model.disconnect()
        self.channel_optimizer.disconnect()
        self.send_time_optimizer.disconnect()
        self.content_personalizer.disconnect()

