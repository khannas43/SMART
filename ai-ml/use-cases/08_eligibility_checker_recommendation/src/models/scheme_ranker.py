"""
Scheme Ranker
Use Case ID: AI-PLATFORM-08

Ranks schemes based on eligibility score, impact, under-coverage, and time sensitivity.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
import json

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class SchemeRanker:
    """
    Scheme Ranking Service
    
    Ranks schemes based on:
    - Eligibility score and confidence
    - Impact score (benefit amount, criticality)
    - Under-coverage boost (similar families nearby enrolled but this one not)
    - Time sensitivity (urgency of scheme benefits)
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Scheme Ranker"""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "use_case_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Ranking weights
        self.ranking_weights = self.config.get('recommendation', {}).get('ranking_weights', {})
        self.eligibility_weight = self.ranking_weights.get('eligibility_score', 0.4)
        self.impact_weight = self.ranking_weights.get('impact_score', 0.3)
        self.under_coverage_weight = self.ranking_weights.get('under_coverage_boost', 0.2)
        self.time_sensitivity_weight = self.ranking_weights.get('time_sensitivity', 0.1)
        
        # Impact scores by category
        self.impact_scores = self.config.get('scheme_ranking', {}).get('impact_scores', {})
        self.urgency_weights = self.config.get('scheme_ranking', {}).get('urgency_weights', {})
        
        # Database for scheme metadata
        db_config_path = Path(__file__).parent.parent.parent / "config" / "db_config.yaml"
        with open(db_config_path, 'r') as f:
            db_config = yaml.safe_load(f)['database']
        
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
    
    def rank_schemes(
        self,
        evaluations: List[Dict[str, Any]],
        family_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Rank schemes based on eligibility and recommendation factors
        
        Args:
            evaluations: List of eligibility evaluation results
            family_id: Optional family ID for under-coverage calculation
            context: Additional context (location, preferences, etc.)
        
        Returns:
            List of evaluations with added ranking fields
        """
        ranked = []
        
        for eval_result in evaluations:
            scheme_code = eval_result.get('scheme_code')
            
            # Calculate priority score
            priority_score = self._calculate_priority_score(
                eval_result, family_id, context
            )
            
            # Get impact score
            impact_score = self._get_impact_score(scheme_code)
            
            # Get under-coverage boost
            under_coverage_boost = self._calculate_under_coverage_boost(
                scheme_code, family_id, context
            )
            
            # Add ranking fields
            ranked_result = eval_result.copy()
            ranked_result['priority_score'] = priority_score
            ranked_result['impact_score'] = impact_score
            ranked_result['under_coverage_boost'] = under_coverage_boost
            
            ranked.append(ranked_result)
        
        # Sort by priority score (descending)
        ranked.sort(key=lambda x: x.get('priority_score', 0.0), reverse=True)
        
        # Assign ranks
        for i, result in enumerate(ranked, 1):
            result['recommendation_rank'] = i
        
        return ranked
    
    def _calculate_priority_score(
        self,
        eval_result: Dict[str, Any],
        family_id: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate priority score for a scheme"""
        # Eligibility component
        eligibility_score = float(eval_result.get('eligibility_score', 0.0))
        confidence_multiplier = {
            'HIGH': 1.0,
            'MEDIUM': 0.8,
            'LOW': 0.6
        }.get(eval_result.get('confidence_level', 'LOW'), 0.6)
        
        eligibility_component = eligibility_score * confidence_multiplier * self.eligibility_weight
        
        # Impact component
        scheme_code = eval_result.get('scheme_code')
        impact_score = self._get_impact_score(scheme_code)
        impact_component = impact_score * self.impact_weight
        
        # Under-coverage component
        under_coverage_boost = self._calculate_under_coverage_boost(
            scheme_code, family_id, context
        )
        under_coverage_component = under_coverage_boost * self.under_coverage_weight
        
        # Time sensitivity component
        time_sensitivity = self._get_time_sensitivity(scheme_code)
        time_component = time_sensitivity * self.time_sensitivity_weight
        
        # Total priority score
        priority_score = (
            eligibility_component +
            impact_component +
            under_coverage_component +
            time_component
        )
        
        return min(1.0, max(0.0, priority_score))
    
    def _get_impact_score(self, scheme_code: str) -> float:
        """Get impact score for a scheme based on category"""
        try:
            conn = self.db.connection
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT scheme_category, benefit_type
                FROM public.scheme_master
                WHERE scheme_code = %s
            """, (scheme_code,))
            
            row = cursor.fetchone()
            cursor.close()
            
            if row:
                category = row[0] or 'OTHER'
                # Map category to impact score
                category_upper = category.upper()
                for key, score in self.impact_scores.items():
                    if key in category_upper:
                        return float(score)
            
            return float(self.impact_scores.get('OTHER', 0.5))
        
        except Exception:
            return 0.5  # Default impact score
    
    def _calculate_under_coverage_boost(
        self,
        scheme_code: str,
        family_id: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate under-coverage boost
        
        This would ideally check if similar families nearby are enrolled
        but this family is not. For now, return a default value.
        """
        # TODO: Implement actual under-coverage calculation
        # - Get location from family/context
        # - Find similar families in same area enrolled in scheme
        # - Calculate boost based on coverage gap
        
        # Default: Return 0.0 (no boost) for now
        return 0.0
    
    def _get_time_sensitivity(self, scheme_code: str) -> float:
        """Get time sensitivity weight for a scheme"""
        try:
            conn = self.db.connection
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT urgency_level
                FROM public.scheme_master
                WHERE scheme_code = %s
            """, (scheme_code,))
            
            row = cursor.fetchone()
            cursor.close()
            
            if row and row[0]:
                urgency = row[0].upper()
                return float(self.urgency_weights.get(urgency, 0.5))
            
            return 0.5  # Default time sensitivity
        
        except Exception:
            return 0.5

