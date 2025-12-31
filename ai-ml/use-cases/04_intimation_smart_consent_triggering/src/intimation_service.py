"""
Main Intimation Service
Orchestrates campaign management, message delivery, and consent management
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    # Try relative imports first (when used as package)
    from .campaign_manager import CampaignManager, Candidate, Campaign
    from .message_personalizer import MessagePersonalizer, RenderedMessage
    from .consent_manager import ConsentManager
    from .smart_orchestrator import SmartOrchestrator
except ImportError:
    # Fall back to absolute imports (when run directly)
    from campaign_manager import CampaignManager, Candidate, Campaign
    from message_personalizer import MessagePersonalizer, RenderedMessage
    from consent_manager import ConsentManager
    from smart_orchestrator import SmartOrchestrator


class IntimationService:
    """Main service orchestrating intimation workflow"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Intimation Service"""
        self.campaign_manager = CampaignManager(config_path)
        self.message_personalizer = MessagePersonalizer(config_path)
        self.consent_manager = ConsentManager(config_path)
        self.orchestrator = SmartOrchestrator(config_path)
    
    def run_intake_process(self, scheme_code: Optional[str] = None) -> List[Campaign]:
        """
        Run intake process: pull eligibility signals and create campaigns
        
        Args:
            scheme_code: Specific scheme (None = all schemes)
        
        Returns:
            List of created campaigns
        """
        # Intake eligibility signals
        candidates = self.campaign_manager.intake_eligibility_signals(
            scheme_code=scheme_code
        )
        
        # Group by scheme
        campaigns_created = []
        schemes = set(c.scheme_code for c in candidates)
        
        for scheme in schemes:
            scheme_candidates = [c for c in candidates if c.scheme_code == scheme]
            
            # Apply campaign policies
            filtered = self.campaign_manager.apply_campaign_policies(
                scheme_candidates, scheme
            )
            
            if not filtered:
                continue
            
            # Create campaign
            campaign = self.campaign_manager.create_campaign(
                scheme_code=scheme,
                candidates=filtered,
                campaign_type='INITIAL'
            )
            
            # Schedule sends
            self.campaign_manager.schedule_campaign_sends(campaign.campaign_id)
            
            campaigns_created.append(campaign)
        
        return campaigns_created
    
    def execute_campaign(self, campaign_id: int) -> Dict[str, Any]:
        """
        Execute campaign: send messages to all candidates
        
        Args:
            campaign_id: Campaign ID
        
        Returns:
            Execution results
        """
        # TODO: Implement message delivery via channel providers
        # This is a placeholder - actual implementation would integrate
        # with Twilio, email providers, etc.
        
        return {
            'campaign_id': campaign_id,
            'status': 'executed',
            'messages_sent': 0,
            'messages_failed': 0
        }
    
    def process_consent_response(
        self,
        family_id: str,
        scheme_code: str,
        consent_value: bool,
        consent_method: str,
        channel: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process consent response from user
        
        Args:
            family_id: Family ID
            scheme_code: Scheme code
            consent_value: True for given, False for rejected
            consent_method: click, tap, otp, e_sign
            channel: Channel used
            **kwargs: Additional parameters (session_id, device_id, etc.)
        
        Returns:
            Consent record
        """
        return self.consent_manager.create_consent(
            family_id=family_id,
            scheme_code=scheme_code,
            consent_value=consent_value,
            consent_method=consent_method,
            channel=channel,
            **kwargs
        )
    
    def disconnect(self):
        """Close all connections"""
        self.campaign_manager.disconnect()
        self.message_personalizer.disconnect()
        self.consent_manager.disconnect()
        self.orchestrator.disconnect()

