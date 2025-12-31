"""
Channel Provider Abstract Base Class
Defines interface for all channel providers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class DeliveryStatus(Enum):
    """Message delivery status"""
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    UNSUBSCRIBED = "unsubscribed"


@dataclass
class DeliveryResult:
    """Result of message delivery attempt"""
    success: bool
    provider_message_id: Optional[str]
    status: DeliveryStatus
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    delivered_at: Optional[datetime] = None
    provider_response: Optional[Dict[str, Any]] = None


class ChannelProvider(ABC):
    """Abstract base class for channel providers"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize channel provider
        
        Args:
            config: Provider-specific configuration
        """
        self.config = config
        self.channel_name = self.__class__.__name__.replace('Provider', '').lower()
    
    @abstractmethod
    def send_message(
        self,
        recipient: str,
        message_body: str,
        subject: Optional[str] = None,
        deep_link: Optional[str] = None,
        action_buttons: Optional[list] = None,
        **kwargs
    ) -> DeliveryResult:
        """
        Send message via this channel
        
        Args:
            recipient: Recipient identifier (phone, email, device_id, etc.)
            message_body: Message content
            subject: Subject (for email/web)
            deep_link: Deep link URL
            action_buttons: Action buttons (for rich channels)
            **kwargs: Additional channel-specific parameters
        
        Returns:
            Delivery result
        """
        pass
    
    @abstractmethod
    def check_status(self, provider_message_id: str) -> DeliveryStatus:
        """
        Check delivery status of a message
        
        Args:
            provider_message_id: Provider's message ID
        
        Returns:
            Delivery status
        """
        pass
    
    @abstractmethod
    def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle webhook callback from provider
        
        Args:
            payload: Webhook payload
        
        Returns:
            Parsed event data
        """
        pass
    
    def validate_recipient(self, recipient: str) -> bool:
        """
        Validate recipient format for this channel
        
        Args:
            recipient: Recipient identifier
        
        Returns:
            True if valid
        """
        return True  # Default: accept any format
    
    def get_max_length(self) -> int:
        """Get maximum message length for this channel"""
        return 1000  # Default

