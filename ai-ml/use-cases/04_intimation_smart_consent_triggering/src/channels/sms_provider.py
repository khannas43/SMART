"""
SMS Provider Implementation using Twilio
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


class SMSProvider(ChannelProvider):
    """SMS provider using Twilio"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize SMS provider"""
        super().__init__(config)
        
        if not TWILIO_AVAILABLE:
            raise ImportError("twilio package not installed. Run: pip install twilio")
        
        account_sid = config.get('account_sid') or os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = config.get('auth_token') or os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = config.get('from_number') or os.getenv('TWILIO_FROM_NUMBER')
        self.short_code = config.get('short_code', 'SMART')
        
        if not account_sid or not auth_token:
            raise ValueError("Twilio credentials not configured")
        
        self.client = Client(account_sid, auth_token)
    
    def send_message(
        self,
        recipient: str,
        message_body: str,
        subject: Optional[str] = None,
        deep_link: Optional[str] = None,
        action_buttons: Optional[list] = None,
        **kwargs
    ) -> DeliveryResult:
        """Send SMS via Twilio"""
        try:
            # Append deep link if provided (shorten for SMS)
            if deep_link:
                # In production, use URL shortener
                message_body = f"{message_body}\n{deep_link}"
            
            # Truncate if too long (160 chars for SMS)
            max_length = self.get_max_length()
            if len(message_body) > max_length:
                message_body = message_body[:max_length-3] + "..."
            
            # Send SMS
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=self._format_phone_number(recipient)
            )
            
            return DeliveryResult(
                success=True,
                provider_message_id=message.sid,
                status=DeliveryStatus.SENT,
                delivered_at=datetime.now(),
                provider_response={
                    'sid': message.sid,
                    'status': message.status,
                    'date_created': str(message.date_created)
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
        """Check SMS delivery status"""
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
        """Handle Twilio SMS webhook"""
        event_type_map = {
            'status': 'delivery_status_update',
            'incoming': 'incoming_message'
        }
        
        return {
            'event_type': event_type_map.get(payload.get('MessageStatus'), 'unknown'),
            'provider_message_id': payload.get('MessageSid'),
            'status': payload.get('MessageStatus'),
            'recipient': payload.get('To'),
            'raw_payload': payload
        }
    
    def validate_recipient(self, recipient: str) -> bool:
        """Validate phone number format"""
        # Basic validation - 10+ digits
        cleaned = ''.join(filter(str.isdigit, recipient))
        return len(cleaned) >= 10
    
    def get_max_length(self) -> int:
        """SMS max length (160 characters)"""
        return 160
    
    def _format_phone_number(self, phone: str) -> str:
        """Format phone number for Twilio (E.164 format)"""
        # Remove non-digits
        cleaned = ''.join(filter(str.isdigit, phone))
        
        # Add country code if missing (assume India +91)
        if not cleaned.startswith('91') and len(cleaned) == 10:
            cleaned = '91' + cleaned
        
        return '+' + cleaned

