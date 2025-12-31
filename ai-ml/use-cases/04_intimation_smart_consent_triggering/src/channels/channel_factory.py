"""
Channel Factory
Creates appropriate channel provider instances
"""

import os
import yaml
from typing import Dict, Any, Optional

from .sms_provider import SMSProvider
from .whatsapp_provider import WhatsAppProvider
from .email_provider import EmailProvider
from .ivr_provider import IVRProvider
from .app_push_provider import AppPushProvider
from .channel_provider import ChannelProvider


class ChannelFactory:
    """Factory for creating channel provider instances"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize channel factory
        
        Args:
            config_path: Path to use case config file
        """
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__),
                '../../config/use_case_config.yaml'
            )
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.integrations_config = self.config.get('integrations', {})
        self._providers = {}
    
    def get_provider(self, channel: str) -> ChannelProvider:
        """
        Get channel provider instance
        
        Args:
            channel: Channel name (sms, whatsapp, email, ivr, mobile_app)
        
        Returns:
            Channel provider instance
        """
        if channel in self._providers:
            return self._providers[channel]
        
        channel_lower = channel.lower()
        
        if channel_lower == 'sms':
            provider = self._create_sms_provider()
        elif channel_lower == 'whatsapp':
            provider = self._create_whatsapp_provider()
        elif channel_lower == 'email':
            provider = self._create_email_provider()
        elif channel_lower == 'ivr':
            provider = self._create_ivr_provider()
        elif channel_lower in ['mobile_app', 'app_push', 'push']:
            provider = self._create_app_push_provider()
        else:
            raise ValueError(f"Unknown channel: {channel}")
        
        self._providers[channel] = provider
        return provider
    
    def _create_sms_provider(self) -> SMSProvider:
        """Create SMS provider"""
        sms_config = self.integrations_config.get('sms', {})
        config = {
            'account_sid': sms_config.get('endpoint'),  # Store in config
            'auth_token': sms_config.get('api_key'),
            'from_number': os.getenv('TWILIO_FROM_NUMBER'),
            'short_code': 'SMART'
        }
        return SMSProvider(config)
    
    def _create_whatsapp_provider(self) -> WhatsAppProvider:
        """Create WhatsApp provider"""
        whatsapp_config = self.integrations_config.get('whatsapp', {})
        config = {
            'account_sid': whatsapp_config.get('endpoint'),
            'auth_token': whatsapp_config.get('api_key'),
            'from_whatsapp': os.getenv('TWILIO_WHATSAPP_FROM'),
            'template_namespace': 'default'
        }
        return WhatsAppProvider(config)
    
    def _create_email_provider(self) -> EmailProvider:
        """Create Email provider"""
        email_config = self.integrations_config.get('email', {})
        config = {
            'smtp_host': email_config.get('smtp_host') or os.getenv('SMTP_HOST'),
            'smtp_port': email_config.get('smtp_port') or 587,
            'smtp_user': email_config.get('smtp_user') or os.getenv('SMTP_USER'),
            'smtp_password': email_config.get('smtp_password') or os.getenv('SMTP_PASSWORD'),
            'from_email': os.getenv('SMTP_FROM_EMAIL'),
            'use_tls': True
        }
        return EmailProvider(config)
    
    def _create_ivr_provider(self) -> IVRProvider:
        """Create IVR provider"""
        ivr_config = self.integrations_config.get('ivr', {})
        config = {
            'account_sid': ivr_config.get('endpoint'),
            'auth_token': ivr_config.get('api_key'),
            'from_number': os.getenv('TWILIO_VOICE_FROM'),
            'twiml_base_url': os.getenv('TWIML_BASE_URL')
        }
        return IVRProvider(config)
    
    def _create_app_push_provider(self) -> AppPushProvider:
        """Create App Push provider"""
        config = {
            'firebase_credentials_path': os.getenv('FIREBASE_CREDENTIALS_PATH'),
            'default_topic': 'intimations'
        }
        return AppPushProvider(config)
    
    def get_available_channels(self) -> list:
        """Get list of available channels"""
        available = []
        
        # Check which providers can be instantiated
        channels = ['sms', 'whatsapp', 'email', 'ivr', 'mobile_app']
        for channel in channels:
            try:
                self.get_provider(channel)
                available.append(channel)
            except:
                pass
        
        return available

