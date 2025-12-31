"""
Decision Router
Routes decisions to appropriate channels (payment, worklist, etc.)
Use Case ID: AI-PLATFORM-06
"""

from typing import Dict, Any, Optional
from datetime import datetime
import sys
from pathlib import Path
import json

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class DecisionRouter:
    """Routes decisions to appropriate channels based on decision type"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Decision Router"""
        if config_path is None:
            base_dir = Path(__file__).parent.parent.parent
            config_path = base_dir / "config" / "db_config.yaml"
        
        import yaml
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Load use case config
        use_case_config_path = Path(config_path).parent / "use_case_config.yaml"
        if use_case_config_path.exists():
            with open(use_case_config_path, 'r') as f:
                self.use_case_config = yaml.safe_load(f)
        else:
            self.use_case_config = {}
        
        # Initialize database connections
        db_config = self.config['database']
        self.db = DBConnector(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['name'],
            user=db_config['user'],
            password=db_config['password']
        )
    
    def connect(self):
        """Connect to database"""
        self.db.connect()
    
    def disconnect(self):
        """Disconnect from database"""
        self.db.disconnect()
    
    def route_decision(
        self,
        decision_id: int,
        decision: Dict[str, Any],
        application_id: int
    ) -> Dict[str, Any]:
        """
        Route decision to appropriate channel
        
        Args:
            decision_id: Decision ID
            decision: Decision details
            application_id: Application ID
        
        Returns:
            Routing result with action taken and status
        """
        decision_type = decision['decision_type']
        
        if decision_type == 'AUTO_APPROVE':
            return self._route_auto_approve(decision_id, decision, application_id)
        elif decision_type == 'ROUTE_TO_OFFICER':
            return self._route_to_officer(decision_id, decision, application_id)
        elif decision_type == 'ROUTE_TO_FRAUD':
            return self._route_to_fraud(decision_id, decision, application_id)
        elif decision_type == 'AUTO_REJECT':
            return self._route_auto_reject(decision_id, decision, application_id)
        else:
            return {
                'action': 'none',
                'status': 'completed',
                'message': f'Unknown decision type: {decision_type}'
            }
    
    def _route_auto_approve(
        self,
        decision_id: int,
        decision: Dict[str, Any],
        application_id: int
    ) -> Dict[str, Any]:
        """Route auto-approved decision to payment system"""
        conn = self.db.connection
        cursor = conn.cursor()
        
        # Get application details for payment
        # (In production, would fetch from application schema)
        
        # Create payment trigger record
        cursor.execute("""
            INSERT INTO decision.payment_triggers (
                decision_id, payment_status, payment_system,
                triggered_at
            ) VALUES (
                %s, %s, %s, %s
            )
            RETURNING trigger_id
        """, (
            decision_id,
            'pending',
            'JAN_AADHAAR_DBT',  # Default payment system
            datetime.now()
        ))
        
        trigger_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        
        # TODO: Trigger actual payment API call
        # payment_result = self._trigger_payment(application_id, decision_id)
        
        return {
            'action': 'payment_triggered',
            'status': 'pending',
            'trigger_id': trigger_id,
            'message': 'Payment trigger created, awaiting processing',
            'payment_system': 'JAN_AADHAAR_DBT'
        }
    
    def _route_to_officer(
        self,
        decision_id: int,
        decision: Dict[str, Any],
        application_id: int
    ) -> Dict[str, Any]:
        """Route decision to officer worklist"""
        # Update decision with routing information
        conn = self.db.connection
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE decision.decisions
            SET routed_to = 'OFFICER_WORKLIST',
                routing_reason = %s
            WHERE decision_id = %s
        """, (
            decision.get('reason', 'Requires officer review'),
            decision_id
        ))
        
        conn.commit()
        cursor.close()
        
        # TODO: Add to actual officer worklist system
        
        return {
            'action': 'routed_to_worklist',
            'status': 'completed',
            'queue': 'OFFICER_WORKLIST',
            'message': 'Decision routed to officer worklist for review'
        }
    
    def _route_to_fraud(
        self,
        decision_id: int,
        decision: Dict[str, Any],
        application_id: int
    ) -> Dict[str, Any]:
        """Route decision to fraud queue"""
        # Update decision with routing information
        conn = self.db.connection
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE decision.decisions
            SET routed_to = 'FRAUD_QUEUE',
                routing_reason = %s
            WHERE decision_id = %s
        """, (
            decision.get('reason', 'High risk, routed to fraud queue'),
            decision_id
        ))
        
        conn.commit()
        cursor.close()
        
        # TODO: Add to actual fraud investigation queue
        
        return {
            'action': 'routed_to_fraud',
            'status': 'completed',
            'queue': 'FRAUD_QUEUE',
            'message': 'Decision routed to fraud investigation queue'
        }
    
    def _route_auto_reject(
        self,
        decision_id: int,
        decision: Dict[str, Any],
        application_id: int
    ) -> Dict[str, Any]:
        """Handle auto-rejected decision"""
        # Update application status to rejected
        # (In production, would update application schema)
        
        return {
            'action': 'rejected',
            'status': 'completed',
            'message': 'Application auto-rejected based on rule failures'
        }

