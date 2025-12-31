"""
Source code for Auto Intimation & Smart Consent Triggering (AI-PLATFORM-04)
"""

from .campaign_manager import CampaignManager
from .message_personalizer import MessagePersonalizer
from .consent_manager import ConsentManager
from .smart_orchestrator import SmartOrchestrator
from .intimation_service import IntimationService

__all__ = [
    'CampaignManager',
    'MessagePersonalizer',
    'ConsentManager',
    'SmartOrchestrator',
    'IntimationService',
]

