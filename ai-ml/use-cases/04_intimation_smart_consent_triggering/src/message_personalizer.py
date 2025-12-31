"""
Message Personalizer Service
Generates personalized messages for different channels and languages
"""

import sys
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import yaml
import pandas as pd
from jinja2 import Template, Environment, FileSystemLoader
import uuid

# Add shared utils to path
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


@dataclass
class RenderedMessage:
    """Represents a rendered message for a channel"""
    channel: str
    subject: Optional[str]
    body: str
    deep_link: str
    action_buttons: List[Dict[str, str]]
    template_id: str
    language: str


@dataclass
class ActionButton:
    """Represents an action button in a message"""
    label: str
    action: str
    url: Optional[str] = None


class MessagePersonalizer:
    """Personalizes messages for different channels and languages"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Message Personalizer
        
        Args:
            config_path: Path to configuration file
        """
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
        
        # Jinja2 environment
        self.jinja_env = Environment()
    
    def select_template(
        self,
        channel: str,
        language: str,
        message_type: str = 'intimation'
    ) -> Dict[str, Any]:
        """
        Select message template from database
        
        Args:
            channel: Channel (sms, mobile_app, web, whatsapp, email, ivr)
            language: Language code (hi, en)
            message_type: Message type (intimation, reminder, consent_request)
        
        Returns:
            Template dictionary
        """
        query = """
            SELECT * FROM intimation.message_templates
            WHERE channel = %s
            AND language = %s
            AND message_type = %s
            AND status = 'active'
            ORDER BY version DESC
            LIMIT 1
        """
        
        df = pd.read_sql(
            query,
            self.db.connection,
            params=(channel, language, message_type)
        )
        
        if df.empty:
            # Fallback to English
            df = pd.read_sql(
                query,
                self.db.connection,
                params=(channel, 'en', message_type)
            )
        
        if df.empty:
            raise ValueError(f"No template found for {channel}/{language}/{message_type}")
        
        return df.iloc[0].to_dict()
    
    def render_message(
        self,
        template: Dict[str, Any],
        context: Dict[str, Any]
    ) -> RenderedMessage:
        """
        Render message from template with context
        
        Args:
            template: Template dictionary from database
            context: Context variables for template
        
        Returns:
            Rendered message
        """
        # Render body template
        body_template = Template(template['body_template'])
        body = body_template.render(**context)
        
        # Render subject if present
        subject = None
        if template.get('subject_template'):
            subject_template = Template(template['subject_template'])
            subject = subject_template.render(**context)
        
        # Generate deep link
        deep_link = self._generate_deep_link(
            context.get('family_id'),
            context.get('scheme_code'),
            context.get('action', 'consent')
        )
        
        # Generate action buttons
        action_buttons = self._generate_action_buttons(
            template.get('default_action_buttons'),
            context.get('scheme_code'),
            context.get('consent_type', 'soft')
        )
        
        # Truncate SMS messages to 160 characters (SMS limit)
        if template['channel'] == 'sms' and len(body) > 160:
            # Truncate body, preserving message structure
            body = body[:157] + '...'
        
        return RenderedMessage(
            channel=template['channel'],
            subject=subject,
            body=body,
            deep_link=deep_link,
            action_buttons=action_buttons,
            template_id=template['template_code'],
            language=template['language']
        )
    
    def personalize_for_candidate(
        self,
        candidate: Dict[str, Any],
        scheme_info: Dict[str, Any],
        channel: str,
        language: Optional[str] = None
    ) -> RenderedMessage:
        """
        Personalize message for a candidate
        
        Args:
            candidate: Candidate data from campaign_candidates
            scheme_info: Scheme information from scheme_master
            channel: Target channel
            language: Language (auto-detect if None)
        
        Returns:
            Personalized rendered message
        """
        # Auto-detect language if not provided
        if not language:
            language = candidate.get('preferred_language', 'hi')
        
        # Select template
        template = self.select_template(channel, language, 'intimation')
        
        # Build context
        context = {
            'scheme_name': scheme_info.get('scheme_name', ''),
            'scheme_code': candidate['scheme_code'],
            'benefit_amount': self._format_benefit_amount(scheme_info),
            'eligibility_reason': candidate.get('eligibility_reason', ''),
            'family_id': candidate['family_id'],
            'short_code': 'SMART',
            'consent_type': self._get_consent_type(candidate['scheme_code'])
        }
        
        # Add channel-specific context
        if channel == 'sms':
            context['deep_link'] = self._generate_deep_link(
                candidate['family_id'],
                candidate['scheme_code'],
                'consent'
            )
        elif channel in ['mobile_app', 'web']:
            context['action_buttons'] = ['yes', 'no', 'more_info']
        
        # Render message
        return self.render_message(template, context)
    
    def generate_deep_link(
        self,
        family_id: str,
        scheme_code: str,
        action: str = 'consent'
    ) -> str:
        """Generate deep link URL"""
        base_url = self.use_case_config.get('deep_link_base_url', 'https://smart.rajasthan.gov.in')
        return f"{base_url}/consent?family_id={family_id}&scheme_code={scheme_code}&action={action}"
    
    def _generate_deep_link(self, family_id: str, scheme_code: str, action: str) -> str:
        """Internal helper for deep link generation"""
        return self.generate_deep_link(family_id, scheme_code, action)
    
    def generate_action_buttons(
        self,
        scheme_code: str,
        consent_type: str = 'soft'
    ) -> List[ActionButton]:
        """Generate action buttons for message"""
        buttons = []
        
        if consent_type == 'soft':
            buttons.append(ActionButton(
                label="हाँ, मेरी सहमति दें",
                action="consent_yes",
                url=self.generate_deep_link("{{ family_id }}", scheme_code, "consent_yes")
            ))
            buttons.append(ActionButton(
                label="अधिक जानकारी",
                action="more_info",
                url=self.generate_deep_link("{{ family_id }}", scheme_code, "more_info")
            ))
            buttons.append(ActionButton(
                label="नहीं",
                action="consent_no",
                url=self.generate_deep_link("{{ family_id }}", scheme_code, "consent_no")
            ))
        else:
            buttons.append(ActionButton(
                label="सहमति दें (OTP)",
                action="consent_yes_otp",
                url=self.generate_deep_link("{{ family_id }}", scheme_code, "consent_yes_otp")
            ))
            buttons.append(ActionButton(
                label="अधिक जानकारी",
                action="more_info",
                url=self.generate_deep_link("{{ family_id }}", scheme_code, "more_info")
            ))
        
        return buttons
    
    def _generate_action_buttons(
        self,
        default_buttons: Optional[List[Dict]],
        scheme_code: str,
        consent_type: str
    ) -> List[Dict[str, str]]:
        """Internal helper for action buttons"""
        if default_buttons:
            return default_buttons
        
        buttons = self.generate_action_buttons(scheme_code, consent_type)
        return [
            {
                'label': btn.label,
                'action': btn.action,
                'url': btn.url
            }
            for btn in buttons
        ]
    
    def _format_benefit_amount(self, scheme_info: Dict[str, Any]) -> str:
        """Format benefit amount for display"""
        benefit_amount = scheme_info.get('benefit_amount')
        if not benefit_amount:
            return "लाभ उपलब्ध"
        
        # Format as currency
        return f"₹{benefit_amount:,.0f}/माह"
    
    def _get_consent_type(self, scheme_code: str) -> str:
        """Get consent type for scheme"""
        query = """
            SELECT consent_type_required
            FROM intimation.scheme_intimation_config
            WHERE scheme_code = %s
        """
        
        try:
            df = pd.read_sql(query, self.db.connection, params=[scheme_code])
            if not df.empty:
                return df.iloc[0]['consent_type_required']
        except Exception:
            pass
        
        # Default based on scheme category
        category_query = """
            SELECT category FROM public.scheme_master
            WHERE scheme_code = %s
        """
        try:
            df = pd.read_sql(category_query, self.db.connection, params=[scheme_code])
            if not df.empty:
                category = df.iloc[0]['category']
                if category in ['SOCIAL_SECURITY', 'PENSION', 'FINANCIAL']:
                    return 'strong'
        except Exception:
            pass
        
        return 'soft'
    
    def disconnect(self):
        """Close database connection"""
        if self.db:
            self.db.disconnect()

