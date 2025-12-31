#!/usr/bin/env python3
"""
Unit Tests for Risk Scorer
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

from models.risk_scorer import RiskScorer


class TestRiskScorer(unittest.TestCase):
    """Test cases for Risk Scorer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.scorer = RiskScorer()
        # Mock database connections
        self.scorer.db = Mock()
        self.scorer.external_dbs = {
            'golden_records': Mock(),
            'profile_360': Mock(),
            'application': Mock(),
            'eligibility': Mock()
        }
    
    def test_score_with_rules_low_risk(self):
        """Test rule-based scoring for low risk case"""
        features = {
            'past_rejections': 0,
            'eligibility_score': 0.8,
            'unique_schemes': 2,
            'is_auto_submission': 1
        }
        
        risk_score, top_factors = self.scorer._score_with_rules(features)
        
        self.assertLessEqual(risk_score, 0.3)  # Should be low risk
        self.assertGreaterEqual(risk_score, 0.0)
    
    def test_score_with_rules_high_risk(self):
        """Test rule-based scoring for high risk case"""
        features = {
            'past_rejections': 3,
            'eligibility_score': 0.4,
            'unique_schemes': 0,
            'is_auto_submission': 0
        }
        
        risk_score, top_factors = self.scorer._score_with_rules(features)
        
        self.assertGreater(risk_score, 0.3)  # Should be medium/high risk
        self.assertLessEqual(risk_score, 1.0)
    
    def test_determine_risk_band_low(self):
        """Test risk band determination for low score"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (0.3, 0.7)  # low_risk_max, medium_risk_max
        mock_conn.cursor.return_value = mock_cursor
        self.scorer.db.connection = mock_conn
        
        band = self.scorer._determine_risk_band(0.2, 'CHIRANJEEVI')
        
        self.assertEqual(band, 'LOW')
    
    def test_determine_risk_band_medium(self):
        """Test risk band determination for medium score"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (0.3, 0.7)
        mock_conn.cursor.return_value = mock_cursor
        self.scorer.db.connection = mock_conn
        
        band = self.scorer._determine_risk_band(0.5, 'CHIRANJEEVI')
        
        self.assertEqual(band, 'MEDIUM')
    
    def test_determine_risk_band_high(self):
        """Test risk band determination for high score"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (0.3, 0.7)
        mock_conn.cursor.return_value = mock_cursor
        self.scorer.db.connection = mock_conn
        
        band = self.scorer._determine_risk_band(0.8, 'CHIRANJEEVI')
        
        self.assertEqual(band, 'HIGH')
    
    def test_extract_features(self):
        """Test feature extraction"""
        # Mock all feature extraction methods
        with patch.object(self.scorer, '_get_profile_features', return_value={
            'family_size': 4, 'avg_age': 35.0
        }):
            with patch.object(self.scorer, '_get_benefit_history', return_value={
                'total_benefits': 2, 'unique_schemes': 2
            }):
                with patch.object(self.scorer, '_get_application_features', return_value={
                    'is_auto_submission': 1, 'eligibility_score': 0.75, 'past_rejections': 0
                }):
                    with patch.object(self.scorer, '_get_eligibility_features', return_value={
                        'eligibility_score': 0.75, 'eligibility_status_rule': 1, 'eligibility_status_possible': 0
                    }):
                        features = self.scorer._extract_features(1, 'family-123', 'CHIRANJEEVI')
                        
                        self.assertIn('family_size', features)
                        self.assertIn('total_benefits', features)
                        self.assertIn('is_auto_submission', features)
                        self.assertIn('eligibility_score', features)


if __name__ == '__main__':
    unittest.main()

