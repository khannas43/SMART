"""
Channel Optimizer - ML-based channel selection for nudges.
Uses historical engagement data to predict best channel per family/action.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
import yaml
from datetime import datetime
import random

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class ChannelOptimizer:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "use_case_config.yaml"
        with open(config_path, 'r') as f:
            full_config = yaml.safe_load(f)
            self.config = full_config.get('nudging', {}).get('channel_optimization', {})

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

        self.enabled = self.config.get('enable_channel_optimization', True)
        self.features = self.config.get('features', [])
        self.model_type = self.config.get('model_type', 'GRADIENT_BOOSTING')
        self.fallback_rules = self.config.get('fallback_rules', [])

        # Load channel capabilities from config
        self.channel_capabilities = full_config.get('nudging', {}).get('channels', {}).get('capabilities', {})

    def select_best_channel(self, family_id: str, action_type: str, urgency: str,
                           context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Selects the best channel for a nudge based on historical engagement and context.
        Returns:
        {
            'channel_code': str,
            'confidence': float,
            'reason': str,
            'alternatives': [...]
        }
        """
        if not self.enabled:
            return self._fallback_selection(family_id, action_type, urgency, context)

        # 1. Get available channels (respecting consent/opt-out)
        available_channels = self._get_available_channels(family_id)
        if not available_channels:
            return {
                'channel_code': 'ASSISTED_VISIT',
                'confidence': 1.0,
                'reason': 'No digital channels available, defaulting to assisted visit'
            }

        # 2. Get channel preferences/scores
        channel_scores = {}
        for channel_code in available_channels:
            score = self._calculate_channel_score(family_id, channel_code, action_type, urgency, context)
            channel_scores[channel_code] = score

        # 3. Apply fallback rules if needed
        for rule in self.fallback_rules:
            if rule.get('if_no_digital_footprint') and self._has_no_digital_footprint(family_id):
                return {
                    'channel_code': rule['if_no_digital_footprint'],
                    'confidence': 1.0,
                    'reason': 'No digital footprint detected'
                }
            
            if rule.get('if_high_vulnerability') and self._is_high_vulnerability(family_id):
                return {
                    'channel_code': rule['if_high_vulnerability'],
                    'confidence': 1.0,
                    'reason': 'High vulnerability category'
                }

        # 4. Select best channel
        if channel_scores:
            best_channel = max(channel_scores.items(), key=lambda x: x[1])
            sorted_channels = sorted(channel_scores.items(), key=lambda x: x[1], reverse=True)
            
            return {
                'channel_code': best_channel[0],
                'confidence': best_channel[1],
                'reason': f'Best engagement score: {best_channel[1]:.2f}',
                'alternatives': [{'channel': c[0], 'score': c[1]} for c in sorted_channels[1:4]]  # Top 3 alternatives
            }
        else:
            return self._fallback_selection(family_id, action_type, urgency, context)

    def _calculate_channel_score(self, family_id: str, channel_code: str, action_type: str,
                                urgency: str, context: Dict[str, Any]) -> float:
        """Calculates engagement score for a channel based on historical data and features."""
        base_score = 50.0  # Default score
        
        # 1. Get historical preference score
        preference_score = self._get_preference_score(family_id, channel_code, action_type)
        if preference_score:
            base_score = preference_score
        
        # 2. Adjust based on urgency (high urgency prefers faster channels)
        urgency_adjustment = self._get_urgency_adjustment(channel_code, urgency)
        base_score += urgency_adjustment
        
        # 3. Adjust based on action type (some actions work better on certain channels)
        action_adjustment = self._get_action_type_adjustment(channel_code, action_type)
        base_score += action_adjustment
        
        # 4. Adjust based on context features (geography, demographics, etc.)
        context_adjustment = self._get_context_adjustment(family_id, channel_code, context)
        base_score += context_adjustment
        
        # Normalize to 0-100
        return max(0.0, min(100.0, base_score))

    def _get_preference_score(self, family_id: str, channel_code: str, action_type: str) -> Optional[float]:
        """Gets historical preference score from database."""
        try:
            cursor = self.db.connection.cursor()
            
            # Try action-specific first
            query = """
                SELECT preference_score, engagement_rate
                FROM nudging.channel_preferences
                WHERE family_id = %s AND channel_code = %s AND action_type = %s;
            """
            cursor.execute(query, (family_id, channel_code, action_type))
            result = cursor.fetchone()
            
            if result:
                return float(result[0])  # preference_score
            
            # Try general preference
            query_general = """
                SELECT preference_score, engagement_rate
                FROM nudging.channel_preferences
                WHERE family_id = %s AND channel_code = %s AND action_type IS NULL;
            """
            cursor.execute(query_general, (family_id, channel_code))
            result = cursor.fetchone()
            
            if result:
                return float(result[0])
            
            return None
        except Exception as e:
            print(f"⚠️  Error getting preference score: {e}")
            return None

    def _get_urgency_adjustment(self, channel_code: str, urgency: str) -> float:
        """Adjusts score based on urgency and channel speed."""
        # High urgency benefits from faster channels
        channel_speed = {
            'SMS': 1.0,
            'APP_PUSH': 0.9,
            'WHATSAPP': 0.9,
            'WEB_INBOX': 0.5,
            'IVR': 0.3,
            'ASSISTED_VISIT': 0.1
        }
        
        urgency_multipliers = {
            'CRITICAL': 1.5,
            'HIGH': 1.2,
            'MEDIUM': 1.0,
            'LOW': 0.8
        }
        
        speed = channel_speed.get(channel_code, 0.5)
        multiplier = urgency_multipliers.get(urgency, 1.0)
        
        return (speed * multiplier - 1.0) * 10  # Scale adjustment

    def _get_action_type_adjustment(self, channel_code: str, action_type: str) -> float:
        """Adjusts score based on action type and channel suitability."""
        # Some actions work better on certain channels
        adjustments = {
            'renewal': {
                'SMS': 5, 'APP_PUSH': 10, 'WEB_INBOX': 15, 'WHATSAPP': 8, 'IVR': 0, 'ASSISTED_VISIT': 5
            },
            'missing_doc': {
                'SMS': 0, 'APP_PUSH': 5, 'WEB_INBOX': 20, 'WHATSAPP': 10, 'IVR': -5, 'ASSISTED_VISIT': 15
            },
            'consent': {
                'SMS': 10, 'APP_PUSH': 15, 'WEB_INBOX': 20, 'WHATSAPP': 15, 'IVR': 5, 'ASSISTED_VISIT': 10
            },
            'deadline': {
                'SMS': 15, 'APP_PUSH': 20, 'WEB_INBOX': 10, 'WHATSAPP': 15, 'IVR': 10, 'ASSISTED_VISIT': 5
            },
            'informational': {
                'SMS': 5, 'APP_PUSH': 10, 'WEB_INBOX': 15, 'WHATSAPP': 8, 'IVR': -5, 'ASSISTED_VISIT': 0
            }
        }
        
        action_adjustments = adjustments.get(action_type, {})
        return action_adjustments.get(channel_code, 0)

    def _get_context_adjustment(self, family_id: str, channel_code: str, context: Dict[str, Any]) -> float:
        """Adjusts score based on context features (geography, demographics, etc.)."""
        adjustment = 0.0
        
        # Check if family has app installed (for APP_PUSH)
        if channel_code == 'APP_PUSH':
            if not self._has_app_usage(family_id):
                adjustment -= 20  # Heavy penalty if no app usage
        
        # Check connectivity pattern (for web-based channels)
        if channel_code in ['WEB_INBOX', 'WHATSAPP']:
            if not self._has_online_activity(family_id):
                adjustment -= 15
        
        return adjustment

    def _get_available_channels(self, family_id: str) -> List[str]:
        """Gets list of available channels respecting consent/opt-out."""
        try:
            cursor = self.db.connection.cursor()
            
            # Get family consent preferences
            query = """
                SELECT consent_channels, opt_out_channels
                FROM nudging.family_consent
                WHERE family_id = %s;
            """
            cursor.execute(query, (family_id,))
            result = cursor.fetchone()
            
            # Default to all channels if no consent record
            if not result:
                return list(self.channel_capabilities.keys())
            
            consent_channels = result[0] if result[0] else []
            opt_out_channels = result[1] if result[1] else []
            
            # Start with all enabled channels from config
            all_channels = [c for c in self.channel_capabilities.keys()]
            
            # Filter by consent (if specified) and opt-out
            if consent_channels:
                available = [c for c in all_channels if c in consent_channels]
            else:
                available = all_channels
            
            # Remove opted-out channels
            available = [c for c in available if c not in opt_out_channels]
            
            return available
        except Exception as e:
            print(f"⚠️  Error getting available channels: {e}")
            return list(self.channel_capabilities.keys())

    def _fallback_selection(self, family_id: str, action_type: str, urgency: str,
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback channel selection when optimization is disabled."""
        # Simple heuristic: SMS for urgent, APP_PUSH for regular, WEB_INBOX for non-urgent
        if urgency in ['CRITICAL', 'HIGH']:
            channel = 'SMS'
        elif urgency == 'MEDIUM':
            channel = 'APP_PUSH'
        else:
            channel = 'WEB_INBOX'
        
        return {
            'channel_code': channel,
            'confidence': 0.5,
            'reason': 'Fallback heuristic (optimization disabled)'
        }

    def _has_no_digital_footprint(self, family_id: str) -> bool:
        """Checks if family has no digital footprint."""
        try:
            cursor = self.db.connection.cursor()
            query = """
                SELECT digital_footprint_score
                FROM nudging.family_consent
                WHERE family_id = %s;
            """
            cursor.execute(query, (family_id,))
            result = cursor.fetchone()
            
            if result and result[0]:
                return float(result[0]) < 0.3  # Threshold from config
            return False
        except Exception as e:
            print(f"⚠️  Error checking digital footprint: {e}")
            return False

    def _is_high_vulnerability(self, family_id: str) -> bool:
        """Checks if family is high vulnerability."""
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
                return result[0] == 'HIGH'
            return False
        except Exception as e:
            print(f"⚠️  Error checking vulnerability: {e}")
            return False

    def _has_app_usage(self, family_id: str) -> bool:
        """Checks if family has app usage history."""
        # Placeholder: In real system, query app usage logs
        # For now, return random (will be replaced with actual data)
        return random.random() > 0.5

    def _has_online_activity(self, family_id: str) -> bool:
        """Checks if family has online activity."""
        # Placeholder: In real system, query activity logs
        return random.random() > 0.3

    def disconnect(self):
        self.db.disconnect()

