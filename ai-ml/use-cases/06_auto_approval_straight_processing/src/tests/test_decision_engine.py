#!/usr/bin/env python3
"""
Unit Tests for Decision Engine
Use Case ID: AI-PLATFORM-06
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared', 'utils'))

from decision_engine import DecisionEngine


class TestDecisionEngine(unittest.TestCase):
    """Test cases for Decision Engine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = DecisionEngine()
        # Mock database connections
        self.engine.db = Mock()
        self.engine.external_dbs = {
            'application': Mock()
        }
    
    def test_make_decision_auto_approve(self):
        """Test decision logic for auto-approve"""
        rule_results = {
            'all_passed': True,
            'critical_failures': []
        }
        risk_results = {
            'risk_score': 0.25,
            'risk_band': 'LOW'
        }
        decision_config = {
            'low_risk_max': 0.3,
            'medium_risk_max': 0.7,
            'enable_auto_approval': True
        }
        
        decision = self.engine._make_decision(
            1, 'family-123', 'CHIRANJEEVI',
            rule_results, risk_results, decision_config
        )
        
        self.assertEqual(decision['decision_type'], 'AUTO_APPROVE')
        self.assertEqual(decision['decision_status'], 'approved')
        self.assertEqual(decision['risk_score'], 0.25)
    
    def test_make_decision_auto_reject(self):
        """Test decision logic for auto-reject on critical failure"""
        rule_results = {
            'all_passed': False,
            'critical_failures': ['DECEASED_FLAG']
        }
        risk_results = {
            'risk_score': 0.25,
            'risk_band': 'LOW'
        }
        decision_config = {
            'low_risk_max': 0.3,
            'medium_risk_max': 0.7
        }
        
        decision = self.engine._make_decision(
            1, 'family-123', 'CHIRANJEEVI',
            rule_results, risk_results, decision_config
        )
        
        self.assertEqual(decision['decision_type'], 'AUTO_REJECT')
        self.assertEqual(decision['decision_status'], 'rejected')
    
    def test_make_decision_route_to_officer(self):
        """Test decision logic for routing to officer"""
        rule_results = {
            'all_passed': True,
            'critical_failures': []
        }
        risk_results = {
            'risk_score': 0.5,
            'risk_band': 'MEDIUM'
        }
        decision_config = {
            'low_risk_max': 0.3,
            'medium_risk_max': 0.7,
            'require_human_review_medium': True
        }
        
        decision = self.engine._make_decision(
            1, 'family-123', 'CHIRANJEEVI',
            rule_results, risk_results, decision_config
        )
        
        self.assertEqual(decision['decision_type'], 'ROUTE_TO_OFFICER')
        self.assertEqual(decision['decision_status'], 'under_review')
    
    def test_make_decision_route_to_fraud(self):
        """Test decision logic for routing to fraud queue"""
        rule_results = {
            'all_passed': True,
            'critical_failures': []
        }
        risk_results = {
            'risk_score': 0.8,
            'risk_band': 'HIGH'
        }
        decision_config = {
            'low_risk_max': 0.3,
            'medium_risk_max': 0.7,
            'route_high_risk_to_fraud': True
        }
        
        decision = self.engine._make_decision(
            1, 'family-123', 'CHIRANJEEVI',
            rule_results, risk_results, decision_config
        )
        
        self.assertEqual(decision['decision_type'], 'ROUTE_TO_FRAUD')
        self.assertEqual(decision['decision_status'], 'under_review')


if __name__ == '__main__':
    unittest.main()

