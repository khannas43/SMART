#!/usr/bin/env python3
"""
Unit Tests for Rule Engine
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

from engines.rule_engine import RuleEngine


class TestRuleEngine(unittest.TestCase):
    """Test cases for Rule Engine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = RuleEngine()
        # Mock database connections
        self.engine.db = Mock()
        self.engine.external_dbs = {
            'application': Mock(),
            'golden_records': Mock(),
            'scheme_master': Mock()
        }
    
    def test_evaluate_eligibility_pass(self):
        """Test eligibility check passes"""
        # Mock application with valid eligibility
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (0.75, 'RULE_ELIGIBLE')
        mock_conn.cursor.return_value = mock_cursor
        self.engine.external_dbs['application'].connection = mock_conn
        
        result = self.engine._evaluate_eligibility(1, 'family-123', 'CHIRANJEEVI')
        
        self.assertTrue(result['passed'])
        self.assertEqual(result['rule_category'], 'ELIGIBILITY')
        self.assertEqual(result['severity'], 'INFO')
    
    def test_evaluate_eligibility_fail(self):
        """Test eligibility check fails"""
        # Mock application with low eligibility
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (0.3, 'POSSIBLE_ELIGIBLE')
        mock_conn.cursor.return_value = mock_cursor
        self.engine.external_dbs['application'].connection = mock_conn
        
        result = self.engine._evaluate_eligibility(1, 'family-123', 'CHIRANJEEVI')
        
        self.assertFalse(result['passed'])
        self.assertEqual(result['severity'], 'CRITICAL')
    
    def test_evaluate_authenticity_pass(self):
        """Test authenticity check passes"""
        # Mock application with consent
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = ('auto', 123)  # submission_mode, consent_id
        mock_conn.cursor.return_value = mock_cursor
        self.engine.external_dbs['application'].connection = mock_conn
        
        result = self.engine._evaluate_authenticity(1, 'family-123')
        
        self.assertTrue(result['passed'])
        self.assertEqual(result['rule_category'], 'AUTHENTICITY')
    
    def test_evaluate_documents_all_verified(self):
        """Test document validation passes when all mandatory docs verified"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (5, 5, 3, 3)  # total, verified, mandatory, mandatory_verified
        mock_conn.cursor.return_value = mock_cursor
        self.engine.external_dbs['application'].connection = mock_conn
        
        result = self.engine._evaluate_documents(1, 'CHIRANJEEVI')
        
        self.assertTrue(result['passed'])
        self.assertEqual(result['rule_category'], 'DOCUMENT')
    
    def test_evaluate_documents_missing(self):
        """Test document validation fails when mandatory docs missing"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (5, 3, 3, 1)  # total, verified, mandatory, mandatory_verified
        mock_conn.cursor.return_value = mock_cursor
        self.engine.external_dbs['application'].connection = mock_conn
        
        result = self.engine._evaluate_documents(1, 'CHIRANJEEVI')
        
        self.assertFalse(result['passed'])
        self.assertEqual(result['severity'], 'CRITICAL')
    
    def test_evaluate_duplicates_no_duplicate(self):
        """Test duplicate check passes when no duplicates"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (0,)  # No duplicates
        mock_conn.cursor.return_value = mock_cursor
        self.engine.external_dbs['application'].connection = mock_conn
        
        result = self.engine._evaluate_duplicates(1, 'family-123', 'CHIRANJEEVI')
        
        self.assertTrue(result['passed'])
        self.assertEqual(result['rule_category'], 'DUPLICATE')
    
    def test_evaluate_duplicates_found(self):
        """Test duplicate check fails when duplicate found"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (2,)  # Duplicates found
        mock_conn.cursor.return_value = mock_cursor
        self.engine.external_dbs['application'].connection = mock_conn
        
        result = self.engine._evaluate_duplicates(1, 'family-123', 'CHIRANJEEVI')
        
        self.assertFalse(result['passed'])
        self.assertEqual(result['severity'], 'CRITICAL')
    
    def test_evaluate_rules_all_pass(self):
        """Test complete rule evaluation when all rules pass"""
        # Mock all rule checks to pass
        with patch.object(self.engine, '_evaluate_eligibility', return_value={
            'passed': True, 'severity': 'INFO', 'rule_name': 'ELIGIBILITY_CHECK',
            'rule_category': 'ELIGIBILITY', 'result_message': 'Passed'
        }):
            with patch.object(self.engine, '_evaluate_authenticity', return_value={
                'passed': True, 'severity': 'INFO', 'rule_name': 'AUTHENTICITY_CHECK',
                'rule_category': 'AUTHENTICITY', 'result_message': 'Passed'
            }):
                with patch.object(self.engine, '_evaluate_documents', return_value={
                    'passed': True, 'severity': 'INFO', 'rule_name': 'DOCUMENT_VALIDATION',
                    'rule_category': 'DOCUMENT', 'result_message': 'Passed'
                }):
                    with patch.object(self.engine, '_evaluate_duplicates', return_value={
                        'passed': True, 'severity': 'INFO', 'rule_name': 'DUPLICATE_CHECK',
                        'rule_category': 'DUPLICATE', 'result_message': 'Passed'
                    }):
                        with patch.object(self.engine, '_evaluate_cross_scheme', return_value={
                            'passed': True, 'severity': 'INFO', 'rule_name': 'CROSS_SCHEME_CHECK',
                            'rule_category': 'CROSS_SCHEME', 'result_message': 'Passed'
                        }):
                            with patch.object(self.engine, '_check_deceased_flag', return_value={
                                'passed': True, 'severity': 'INFO', 'rule_name': 'DECEASED_FLAG_CHECK',
                                'rule_category': 'FRAUD', 'result_message': 'Passed'
                            }):
                                result = self.engine.evaluate_rules(1, 'family-123', 'CHIRANJEEVI')
                                
                                self.assertTrue(result['all_passed'])
                                self.assertEqual(result['passed_count'], 6)
                                self.assertEqual(result['failed_count'], 0)
                                self.assertEqual(len(result['critical_failures']), 0)


if __name__ == '__main__':
    unittest.main()

