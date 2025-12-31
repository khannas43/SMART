"""
Content Personalizer - Selects best message template based on effectiveness.
Uses bandit/A-B testing for continuous learning.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
import yaml
from datetime import datetime
import random
import uuid

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class ContentPersonalizer:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "use_case_config.yaml"
        with open(config_path, 'r') as f:
            full_config = yaml.safe_load(f)
            self.config = full_config.get('nudging', {}).get('content_personalization', {})

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

        self.enabled = self.config.get('enable_content_personalization', True)
        self.strategy = self.config.get('template_selection_strategy', 'BANDIT')
        self.bandit_algorithm = self.config.get('bandit_algorithm', 'UCB')
        self.ab_test_split = self.config.get('ab_test_split', 0.5)
        
        # Fix missing bandit_algorithm key
        if not hasattr(self, 'bandit_algorithm') or not self.bandit_algorithm:
            self.bandit_algorithm = 'UCB'

    def select_template(self, family_id: str, action_type: str, channel_code: str,
                       urgency: str, language: str = 'en', action_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Selects the best template for a nudge.
        Returns:
        {
            'template_id': uuid,
            'template_content': str,
            'personalized_content': str,
            'selection_strategy': str,
            'confidence': float
        }
        """
        # Get available templates
        templates = self._get_available_templates(action_type, channel_code, language)
        if not templates:
            return {
                'template_id': None,
                'template_content': 'Default message',
                'personalized_content': 'Default message',
                'selection_strategy': 'DEFAULT',
                'confidence': 0.0,
                'error': 'No templates available'
            }

        # Select template based on strategy
        if self.strategy == 'BANDIT' and self.enabled:
            selected_template = self._bandit_selection(templates, family_id, action_type, channel_code)
        elif self.strategy == 'AB_TEST' and self.enabled:
            selected_template = self._ab_test_selection(templates, family_id)
        else:
            selected_template = self._heuristic_selection(templates, urgency)

        # Personalize content
        personalized_content = self._personalize_content(
            selected_template['template_content'],
            family_id,
            action_type,
            action_context
        )

        return {
            'template_id': selected_template['template_id'],
            'template_content': selected_template['template_content'],
            'personalized_content': personalized_content,
            'selection_strategy': self.strategy if self.enabled else 'HEURISTIC',
            'confidence': selected_template.get('confidence', 0.7)
        }

    def _get_available_templates(self, action_type: str, channel_code: str, language: str) -> List[Dict[str, Any]]:
        """Gets available templates for action type, channel, and language with fallback logic."""
        try:
            cursor = self.db.connection.cursor()
            
            # Try exact match first (action_type, channel_code, language)
            query = """
                SELECT template_id, template_name, template_content, tone, length_category
                FROM nudging.nudge_templates
                WHERE action_type = %s
                AND channel_code = %s
                AND language_code = %s
                AND approval_status = 'APPROVED'
                ORDER BY created_at DESC;
            """
            cursor.execute(query, (action_type, channel_code, language))
            results = cursor.fetchall()
            
            if results:
                templates = []
                for row in results:
                    templates.append({
                        'template_id': row[0],
                        'template_name': row[1],
                        'template_content': row[2],
                        'tone': row[3],
                        'length_category': row[4]
                    })
                return templates
            
            # Fallback 1: Try with action_type and channel_code, any language
            query_fallback1 = """
                SELECT template_id, template_name, template_content, tone, length_category
                FROM nudging.nudge_templates
                WHERE action_type = %s
                AND channel_code = %s
                AND approval_status = 'APPROVED'
                ORDER BY created_at DESC
                LIMIT 5;
            """
            cursor.execute(query_fallback1, (action_type, channel_code))
            results = cursor.fetchall()
            
            if results:
                templates = []
                for row in results:
                    templates.append({
                        'template_id': row[0],
                        'template_name': row[1],
                        'template_content': row[2],
                        'tone': row[3],
                        'length_category': row[4]
                    })
                return templates
            
            # Fallback 2: Try with action_type only, any channel and language
            query_fallback2 = """
                SELECT template_id, template_name, template_content, tone, length_category
                FROM nudging.nudge_templates
                WHERE action_type = %s
                AND approval_status = 'APPROVED'
                ORDER BY created_at DESC
                LIMIT 5;
            """
            cursor.execute(query_fallback2, (action_type,))
            results = cursor.fetchall()
            
            if results:
                templates = []
                for row in results:
                    templates.append({
                        'template_id': row[0],
                        'template_name': row[1],
                        'template_content': row[2],
                        'tone': row[3],
                        'length_category': row[4]
                    })
                return templates
            
            # Fallback 3: Try any template for this channel
            query_fallback3 = """
                SELECT template_id, template_name, template_content, tone, length_category
                FROM nudging.nudge_templates
                WHERE channel_code = %s
                AND approval_status = 'APPROVED'
                ORDER BY created_at DESC
                LIMIT 3;
            """
            cursor.execute(query_fallback3, (channel_code,))
            results = cursor.fetchall()
            
            if results:
                templates = []
                for row in results:
                    templates.append({
                        'template_id': row[0],
                        'template_name': row[1],
                        'template_content': row[2],
                        'tone': row[3],
                        'length_category': row[4]
                    })
                return templates
            
            return []
        except Exception as e:
            print(f"⚠️  Error getting templates: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _bandit_selection(self, templates: List[Dict], family_id: str, action_type: str, channel_code: str) -> Dict[str, Any]:
        """Selects template using bandit algorithm (UCB, Thompson Sampling, or Epsilon-Greedy)."""
        # Get effectiveness scores for each template
        template_scores = []
        for template in templates:
            effectiveness = self._get_template_effectiveness(
                template['template_id'], action_type, channel_code, family_id
            )
            template_scores.append({
                **template,
                'effectiveness_score': effectiveness,
                'confidence': effectiveness / 100.0
            })
        
        # UCB (Upper Confidence Bound) algorithm
        if self.bandit_algorithm == 'UCB':
            selected = self._ucb_selection(template_scores)
        # Thompson Sampling
        elif self.bandit_algorithm == 'THOMPSON_SAMPLING':
            selected = self._thompson_sampling_selection(template_scores)
        # Epsilon-Greedy
        elif self.bandit_algorithm == 'EPSILON_GREEDY':
            selected = self._epsilon_greedy_selection(template_scores)
        else:
            selected = self._ucb_selection(template_scores)  # Default to UCB
        
        return selected

    def _get_template_effectiveness(self, template_id: uuid.UUID, action_type: str,
                                   channel_code: str, family_id: str) -> float:
        """Gets effectiveness score for a template."""
        try:
            cursor = self.db.connection.cursor()
            
            # Get overall effectiveness
            query = """
                SELECT effectiveness_score, response_rate, completion_rate
                FROM nudging.content_effectiveness
                WHERE template_id = %s AND action_type = %s AND channel_code = %s
                ORDER BY last_updated_at DESC
                LIMIT 1;
            """
            cursor.execute(query, (str(template_id), action_type, channel_code))
            result = cursor.fetchone()
            
            if result and result[0]:
                return float(result[0])
            
            # Default score if no data
            return 50.0
        except Exception as e:
            print(f"⚠️  Error getting template effectiveness: {e}")
            return 50.0

    def _ucb_selection(self, template_scores: List[Dict]) -> Dict[str, Any]:
        """Upper Confidence Bound selection."""
        if not template_scores:
            return template_scores[0] if template_scores else {}
        
        # Simple UCB: score + exploration bonus
        import math
        total_trials = sum(t.get('total_sends', 10) for t in template_scores)
        
        best_template = None
        best_ucb = -1
        
        for template in template_scores:
            effectiveness = template.get('effectiveness_score', 50)
            trials = template.get('total_sends', 1)
            
            # UCB = mean + confidence_bound
            exploration = math.sqrt(2 * math.log(max(total_trials, 1)) / max(trials, 1))
            ucb = effectiveness + exploration * 10  # Scale exploration
            
            if ucb > best_ucb:
                best_ucb = ucb
                best_template = template
        
        return best_template or template_scores[0]

    def _thompson_sampling_selection(self, template_scores: List[Dict]) -> Dict[str, Any]:
        """Thompson Sampling selection (simplified)."""
        # Simplified: Sample from beta distribution based on success/failure
        # For now, use effectiveness as proxy
        import random
        
        scores_with_samples = []
        for template in template_scores:
            effectiveness = template.get('effectiveness_score', 50) / 100.0
            # Sample from beta distribution (simplified)
            sample = random.betavariate(
                max(1, int(effectiveness * 10) + 1),
                max(1, int((1 - effectiveness) * 10) + 1)
            )
            scores_with_samples.append((sample, template))
        
        # Select highest sample
        scores_with_samples.sort(key=lambda x: x[0], reverse=True)
        return scores_with_samples[0][1]

    def _epsilon_greedy_selection(self, template_scores: List[Dict]) -> Dict[str, Any]:
        """Epsilon-Greedy selection."""
        epsilon = 0.1  # 10% exploration
        
        if random.random() < epsilon:
            # Explore: random selection
            return random.choice(template_scores)
        else:
            # Exploit: best known
            return max(template_scores, key=lambda x: x.get('effectiveness_score', 50))

    def _ab_test_selection(self, templates: List[Dict], family_id: str) -> Dict[str, Any]:
        """A-B test selection (simple split)."""
        # Simple: hash family_id to consistently assign to A or B
        import hashlib
        hash_val = int(hashlib.md5(family_id.encode()).hexdigest(), 16)
        group = 'A' if (hash_val % 100) < (self.ab_test_split * 100) else 'B'
        
        # Select template based on group
        if len(templates) >= 2:
            return templates[0] if group == 'A' else templates[1]
        return templates[0]

    def _heuristic_selection(self, templates: List[Dict], urgency: str) -> Dict[str, Any]:
        """Heuristic selection based on urgency and tone."""
        # Urgent messages prefer urgent tone, short length
        if urgency in ['CRITICAL', 'HIGH']:
            # Find urgent, short template
            for template in templates:
                if template.get('tone') == 'urgent' and template.get('length_category') == 'short':
                    return template
        
        # Default: first template
        return templates[0] if templates else {}

    def _personalize_content(self, template_content: str, family_id: str, action_type: str, action_context: Dict[str, Any] = None) -> str:
        """Personalizes template content with family-specific variables."""
        personalized = template_content
        
        # Replace common placeholders
        personalized = personalized.replace('{family_name}', 'Citizen')
        personalized = personalized.replace('{action_type}', action_type.replace('_', ' ').title())
        
        # Replace action context variables if provided
        if action_context:
            for key, value in action_context.items():
                placeholder = '{' + key + '}'
                personalized = personalized.replace(placeholder, str(value))
        
        # Replace common scheme/document variables
        if '{scheme_name}' in personalized:
            personalized = personalized.replace('{scheme_name}', action_context.get('scheme_name', 'Scheme') if action_context else 'Scheme')
        if '{scheme_code}' in personalized:
            personalized = personalized.replace('{scheme_code}', action_context.get('scheme_code', 'SCHEME') if action_context else 'SCHEME')
        if '{document_type}' in personalized:
            personalized = personalized.replace('{document_type}', action_context.get('document_type', 'Document') if action_context else 'Document')
        if '{deadline}' in personalized:
            personalized = personalized.replace('{deadline}', 'deadline date')
        if '{deadline_date}' in personalized:
            personalized = personalized.replace('{deadline_date}', 'deadline date')
        if '{upload_link}' in personalized:
            personalized = personalized.replace('{upload_link}', 'https://portal.gov.in/upload')
        if '{consent_link}' in personalized:
            personalized = personalized.replace('{consent_link}', 'https://portal.gov.in/consent')
        if '{portal_link}' in personalized:
            personalized = personalized.replace('{portal_link}', 'https://portal.gov.in')
        if '{info_link}' in personalized:
            personalized = personalized.replace('{info_link}', 'https://portal.gov.in/info')
        if '{information_message}' in personalized:
            personalized = personalized.replace('{information_message}', 'You have an important update')
        if '{action_description}' in personalized:
            personalized = personalized.replace('{action_description}', action_type.replace('_', ' ').title())
        
        return personalized

    def disconnect(self):
        self.db.disconnect()

