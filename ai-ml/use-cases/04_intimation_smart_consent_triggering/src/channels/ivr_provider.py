"""
IVR Provider Implementation using Twilio Voice API
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


class IVRProvider(ChannelProvider):
    """IVR provider using Twilio Voice API"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize IVR provider"""
        super().__init__(config)
        
        if not TWILIO_AVAILABLE:
            raise ImportError("twilio package not installed. Run: pip install twilio")
        
        account_sid = config.get('account_sid') or os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = config.get('auth_token') or os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = config.get('from_number') or os.getenv('TWILIO_VOICE_FROM')
        self.base_url = config.get('twiml_base_url') or os.getenv('TWIML_BASE_URL')
        
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
        twiml_url: Optional[str] = None,
        **kwargs
    ) -> DeliveryResult:
        """Initiate IVR call via Twilio"""
        try:
            # Generate TwiML URL for voice message
            # In production, host TwiML on server or use Twilio Functions
            if not twiml_url:
                twiml_url = f"{self.base_url}/twiml/intimation?message={message_body[:100]}"
            
            # Make call
            call = self.client.calls.create(
                twiml=f'<Response><Say language="hi-IN">{message_body}</Say></Response>',
                to=self._format_phone_number(recipient),
                from_=self.from_number
            )
            
            return DeliveryResult(
                success=True,
                provider_message_id=call.sid,
                status=DeliveryStatus.SENT,
                delivered_at=datetime.now(),
                provider_response={
                    'call_sid': call.sid,
                    'status': call.status
                }
            )
            
        except Exception as e:
            return DeliveryResult(
                success=False,
                provider_message_id=None,
                status=DeliveryStatus.FAILED,
                error_code='CALL_ERROR',
                error_message=str(e)
            )
    
    def check_status(self, provider_message_id: str) -> DeliveryStatus:
        """Check IVR call status"""
        try:
            call = self.client.calls(provider_message_id).fetch()
            
            status_map = {
                'queued': DeliveryStatus.QUEUED,
                'ringing': DeliveryStatus.QUEUED,
                'in-progress': DeliveryStatus.SENT,
                'completed': DeliveryStatus.DELIVERED,
                'busy': DeliveryStatus.FAILED,
                'no-answer': DeliveryStatus.FAILED,
                'failed': DeliveryStatus.FAILED,
                'canceled': DeliveryStatus.FAILED
            }
            
            return status_map.get(call.status, DeliveryStatus.FAILED)
            
        except Exception:
            return DeliveryStatus.FAILED
    
    def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Twilio Voice webhook"""
        return {
            'event_type': 'call_status_update',
            'provider_message_id': payload.get('CallSid'),
            'status': payload.get('CallStatus'),
            'digits': payload.get('Digits'),  # User input from keypad
            'raw_payload': payload
        }
    
    def validate_recipient(self, recipient: str) -> bool:
        """Validate phone number format"""
        cleaned = ''.join(filter(str.isdigit, recipient))
        return len(cleaned) >= 10
    
    def _format_phone_number(self, phone: str) -> str:
        """Format phone number for Twilio"""
        cleaned = ''.join(filter(str.isdigit, phone))
        if not cleaned.startswith('91') and len(cleaned) == 10:
            cleaned = '91' + cleaned
        return '+' + cleaned

