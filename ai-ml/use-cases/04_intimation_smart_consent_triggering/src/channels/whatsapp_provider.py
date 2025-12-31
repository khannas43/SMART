"""
WhatsApp Provider Implementation using Twilio WhatsApp API
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

from .channel_provider import ChannelProvider, DeliveryResult, DeliveryStatus


class WhatsAppProvider(ChannelProvider):
    """WhatsApp provider using Twilio WhatsApp API"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize WhatsApp provider"""
        super().__init__(config)
        
        if not TWILIO_AVAILABLE:
            raise ImportError("twilio package not installed. Run: pip install twilio")
        
        account_sid = config.get('account_sid') or os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = config.get('auth_token') or os.getenv('TWILIO_AUTH_TOKEN')
        self.from_whatsapp = config.get('from_whatsapp') or os.getenv('TWILIO_WHATSAPP_FROM')
        
        if not account_sid or not auth_token:
            raise ValueError("Twilio credentials not configured")
        
        self.client = Client(account_sid, auth_token)
        self.template_namespace = config.get('template_namespace', 'default')
    
    def send_message(
        self,
        recipient: str,
        message_body: str,
        subject: Optional[str] = None,
        deep_link: Optional[str] = None,
        action_buttons: Optional[list] = None,
        template_name: Optional[str] = None,
        template_params: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> DeliveryResult:
        """Send WhatsApp message via Twilio"""
        try:
            # WhatsApp requires template messages (pre-approved)
            # For now, send as regular message (requires WhatsApp Business API)
            
            # Format recipient
            to_number = self._format_whatsapp_number(recipient)
            
            # Send WhatsApp message
            message = self.client.messages.create(
                body=message_body,
                from_=f'whatsapp:{self.from_whatsapp}',
                to=f'whatsapp:{to_number}'
            )
            
            # If action buttons provided, send interactive message
            # (Requires WhatsApp Business API interactive messages)
            
            return DeliveryResult(
                success=True,
                provider_message_id=message.sid,
                status=DeliveryStatus.SENT,
                delivered_at=datetime.now(),
                provider_response={
                    'sid': message.sid,
                    'status': message.status
                }
            )
            
        except Exception as e:
            return DeliveryResult(
                success=False,
                provider_message_id=None,
                status=DeliveryStatus.FAILED,
                error_code='SEND_ERROR',
                error_message=str(e)
            )
    
    def check_status(self, provider_message_id: str) -> DeliveryStatus:
        """Check WhatsApp delivery status"""
        try:
            message = self.client.messages(provider_message_id).fetch()
            
            status_map = {
                'queued': DeliveryStatus.QUEUED,
                'sending': DeliveryStatus.QUEUED,
                'sent': DeliveryStatus.SENT,
                'delivered': DeliveryStatus.DELIVERED,
                'undelivered': DeliveryStatus.FAILED,
                'failed': DeliveryStatus.FAILED
            }
            
            return status_map.get(message.status, DeliveryStatus.FAILED)
            
        except Exception:
            return DeliveryStatus.FAILED
    
    def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Twilio WhatsApp webhook"""
        return {
            'event_type': 'delivery_status_update',
            'provider_message_id': payload.get('MessageSid'),
            'status': payload.get('MessageStatus'),
            'recipient': payload.get('To'),
            'raw_payload': payload
        }
    
    def validate_recipient(self, recipient: str) -> bool:
        """Validate WhatsApp number format"""
        cleaned = ''.join(filter(str.isdigit, recipient))
        return len(cleaned) >= 10
    
    def _format_whatsapp_number(self, phone: str) -> str:
        """Format phone number for WhatsApp"""
        cleaned = ''.join(filter(str.isdigit, phone))
        if not cleaned.startswith('91') and len(cleaned) == 10:
            cleaned = '91' + cleaned
        return cleaned

