"""
Mobile App Push Notification Provider
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from firebase_admin import messaging, credentials, initialize_app
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

from .channel_provider import ChannelProvider, DeliveryResult, DeliveryStatus


class AppPushProvider(ChannelProvider):
    """Mobile app push notification provider using Firebase Cloud Messaging"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize App Push provider"""
        super().__init__(config)
        
        if not FIREBASE_AVAILABLE:
            raise ImportError("firebase-admin not installed. Run: pip install firebase-admin")
        
        # Initialize Firebase if not already initialized
        try:
            cred_path = config.get('firebase_credentials_path') or os.getenv('FIREBASE_CREDENTIALS_PATH')
            if cred_path:
                cred = credentials.Certificate(cred_path)
                initialize_app(cred)
        except:
            # May already be initialized
            pass
        
        self.default_topic = config.get('default_topic', 'intimations')
    
    def send_message(
        self,
        recipient: str,  # device_token (FCM token)
        message_body: str,
        subject: Optional[str] = None,
        deep_link: Optional[str] = None,
        action_buttons: Optional[list] = None,
        **kwargs
    ) -> DeliveryResult:
        """Send push notification via FCM"""
        try:
            # Build notification
            notification = messaging.Notification(
                title=subject or "SMART Platform",
                body=message_body
            )
            
            # Build data payload
            data = {
                'type': 'intimation',
                'deep_link': deep_link or '',
            }
            if action_buttons:
                data['action_buttons'] = str(action_buttons)
            
            # Create message
            message = messaging.Message(
                notification=notification,
                data=data,
                token=recipient  # FCM device token
            )
            
            # Send message
            response = messaging.send(message)
            
            return DeliveryResult(
                success=True,
                provider_message_id=response,
                status=DeliveryStatus.SENT,
                delivered_at=datetime.now(),
                provider_response={'fcm_message_id': response}
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
        """Check FCM delivery status"""
        # FCM doesn't provide status checking API
        # Status comes via app analytics or webhooks
        return DeliveryStatus.SENT
    
    def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle FCM webhook"""
        return {
            'event_type': 'delivery_status_update',
            'provider_message_id': payload.get('message_id'),
            'status': payload.get('status'),
            'raw_payload': payload
        }
    
    def validate_recipient(self, recipient: str) -> bool:
        """Validate FCM token format"""
        # FCM tokens are long strings (152+ characters)
        return len(recipient) > 100

