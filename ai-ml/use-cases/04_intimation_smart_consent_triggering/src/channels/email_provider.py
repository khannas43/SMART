"""
Email Provider Implementation using SMTP
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from datetime import datetime

from .channel_provider import ChannelProvider, DeliveryResult, DeliveryStatus


class EmailProvider(ChannelProvider):
    """Email provider using SMTP"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Email provider"""
        super().__init__(config)
        
        self.smtp_host = config.get('smtp_host') or os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = config.get('smtp_port') or int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = config.get('smtp_user') or os.getenv('SMTP_USER')
        self.smtp_password = config.get('smtp_password') or os.getenv('SMTP_PASSWORD')
        self.from_email = config.get('from_email') or os.getenv('SMTP_FROM_EMAIL')
        self.use_tls = config.get('use_tls', True)
    
    def send_message(
        self,
        recipient: str,
        message_body: str,
        subject: Optional[str] = None,
        deep_link: Optional[str] = None,
        action_buttons: Optional[list] = None,
        html_body: Optional[str] = None,
        **kwargs
    ) -> DeliveryResult:
        """Send email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = recipient
            msg['Subject'] = subject or "SMART Platform - योजना सूचना"
            
            # Create HTML version if provided, otherwise use plain text
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Plain text version
            text_part = MIMEText(message_body, 'plain')
            msg.attach(text_part)
            
            # Add deep link and action buttons to HTML if provided
            if html_body and (deep_link or action_buttons):
                # In production, enhance HTML with buttons
                pass
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                
                server.send_message(msg)
            
            # Generate message ID (SMTP doesn't return one)
            message_id = f"email_{datetime.now().timestamp()}"
            
            return DeliveryResult(
                success=True,
                provider_message_id=message_id,
                status=DeliveryStatus.SENT,
                delivered_at=datetime.now(),
                provider_response={'message_id': message_id}
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
        """Check email delivery status (SMTP doesn't provide status)"""
        # SMTP doesn't provide delivery status tracking
        # In production, use email service like SendGrid, SES that provides webhooks
        return DeliveryStatus.SENT
    
    def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle email webhook (bounce, delivery, etc.)"""
        # Not supported for basic SMTP
        # In production, integrate with email service provider webhooks
        return {
            'event_type': 'unknown',
            'raw_payload': payload
        }
    
    def validate_recipient(self, recipient: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, recipient))
    
    def get_max_length(self) -> int:
        """Email has no practical limit"""
        return 50000

