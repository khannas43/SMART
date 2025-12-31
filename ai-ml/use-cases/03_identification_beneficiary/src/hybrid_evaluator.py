"""
Hybrid Eligibility Evaluator
Combines rule engine and ML scorer for comprehensive eligibility evaluation
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import yaml
import warnings
warnings.filterwarnings('ignore')

from rule_engine import RuleEngine
from ml_scorer import MLEligibilityScorer

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class HybridEvaluator:
    """
    Hybrid eligibility evaluator combining rule engine and ML scorer
    
    Provides final eligibility determination by:
    1. Running rule engine (deterministic)
    2. Running ML scorer (probabilistic)
    3. Combining results with confidence weighting
    4. Resolving conflicts
    5. Determining final eligibility status
    """
    
    def __init__(self, config_path=None):
        """
        Initialize hybrid evaluator
        
        Args:
            config_path: Path to configuration file
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "use_case_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize components
        self.rule_engine = RuleEngine(config_path)
        self.ml_scorer = MLEligibilityScorer()
        
        # Get hybrid configuration
        hybrid_config = self.config['components']['hybrid_evaluator']
        self.rule_weight = hybrid_config.get('rule_weight', 0.6)
        self.ml_weight = hybrid_config.get('ml_weight', 0.4)
        self.confidence_threshold = hybrid_config.get('confidence_threshold', 0.7)
    
    def evaluate(
        self,
        scheme_id: str,
        family_data: Dict,
        member_data: Optional[Dict] = None,
        use_ml: bool = True
    ) -> Dict[str, Any]:
        """
        Evaluate eligibility using hybrid approach
        
        Args:
            scheme_id: Scheme ID
            family_data: Family-level data (Golden Record + 360° Profile)
            member_data: Member-level data (if applicable)
            use_ml: Whether to use ML scorer (if model available)
        
        Returns:
            Comprehensive evaluation result:
            {
                'scheme_id': str,
                'family_id': str,
                'evaluation_status': str,  # RULE_ELIGIBLE, NOT_ELIGIBLE, POSSIBLE_ELIGIBLE, UNCERTAIN
                'eligibility_score': float,  # Combined score 0-1
                'confidence_score': float,  # Confidence 0-1
                'rule_result': Dict,  # Rule engine results
                'ml_result': Dict,  # ML scorer results (if used)
                'rule_eligible': bool,
                'ml_probability': Optional[float],
                'rules_passed': List[str],
                'rules_failed': List[str],
                'rule_path': str,
                'ml_top_features': List[Dict],
                'reason_codes': List[str],
                'explanation': str,
                'conflict_resolved': bool,
                'final_reason': str
            }
        """
        family_id = family_data.get('family_id', 'unknown')
        
        # Step 1: Run rule engine
        rule_result = self.rule_engine.evaluate_scheme_eligibility(
            scheme_id, family_data, member_data
        )
        
        # Step 2: Run ML scorer (if available and enabled)
        ml_result = None
        ml_available = False
        
        if use_ml:
            ml_available = self.ml_scorer.is_model_available(scheme_id)
            if ml_available:
                ml_result = self.ml_scorer.predict(
                    scheme_id, family_data, member_data, return_explanations=True
                )
        
        # Step 3: Combine results
        combined_result = self._combine_results(
            scheme_id, family_id, rule_result, ml_result, ml_available
        )
        
        return combined_result
    
    def _combine_results(
        self,
        scheme_id: str,
        family_id: str,
        rule_result: Dict,
        ml_result: Optional[Dict],
        ml_available: bool
    ) -> Dict[str, Any]:
        """
        Combine rule engine and ML scorer results
        
        Args:
            scheme_id: Scheme ID
            family_id: Family ID
            rule_result: Rule engine results
            ml_result: ML scorer results (None if not available)
            ml_available: Whether ML model was available
        
        Returns:
            Combined evaluation result
        """
        rule_eligible = rule_result['eligible']
        rule_status = rule_result['status']
        rule_confidence = 1.0 if rule_status == 'RULE_ELIGIBLE' else 0.5
        
        # Initialize result structure
        result = {
            'scheme_id': scheme_id,
            'family_id': family_id,
            'rule_result': rule_result,
            'ml_result': ml_result,
            'rule_eligible': rule_eligible,
            'ml_probability': None,
            'ml_confidence': None,
            'ml_available': ml_available,
            'rules_passed': rule_result['rules_passed'],
            'rules_failed': rule_result['rules_failed'],
            'rule_path': rule_result['rule_path'],
            'ml_top_features': [],
            'reason_codes': rule_result['reason_codes'].copy(),
            'conflict_resolved': False,
            'final_reason': ''
        }
        
        # If ML model available, incorporate ML results
        if ml_result and ml_available and ml_result.get('probability') is not None:
            ml_probability = ml_result['probability']
            ml_confidence = ml_result['confidence']
            
            result['ml_probability'] = ml_probability
            result['ml_confidence'] = ml_confidence
            result['ml_top_features'] = ml_result.get('top_features', [])
            
            # Add ML reason codes
            if ml_probability >= 0.7:
                result['reason_codes'].append('ML_HIGH_PROBABILITY')
            elif ml_probability >= 0.5:
                result['reason_codes'].append('ML_MEDIUM_PROBABILITY')
            else:
                result['reason_codes'].append('ML_LOW_PROBABILITY')
            
            # Combine scores
            eligibility_score = self._calculate_combined_score(
                rule_eligible, rule_confidence, ml_probability, ml_confidence
            )
            
            # Calculate overall confidence
            confidence_score = self._calculate_confidence(
                rule_confidence, ml_confidence, rule_status
            )
            
            result['eligibility_score'] = eligibility_score
            result['confidence_score'] = confidence_score
            
            # Determine final status with conflict resolution
            final_status, conflict_resolved, final_reason = self._determine_final_status(
                rule_eligible, rule_status, ml_probability, ml_confidence,
                eligibility_score, confidence_score
            )
            
            result['evaluation_status'] = final_status
            result['conflict_resolved'] = conflict_resolved
            result['final_reason'] = final_reason
        
        else:
            # ML not available - use rule engine results only
            result['eligibility_score'] = 1.0 if rule_eligible else 0.0
            result['confidence_score'] = rule_confidence
            
            if rule_status == 'RULE_ELIGIBLE':
                result['evaluation_status'] = 'RULE_ELIGIBLE'
                result['final_reason'] = 'Rule-based eligibility confirmed (ML not available)'
            elif rule_status == 'POSSIBLE_ELIGIBLE':
                result['evaluation_status'] = 'POSSIBLE_ELIGIBLE'
                result['final_reason'] = 'Some rules passed (ML not available for confirmation)'
            else:
                result['evaluation_status'] = 'NOT_ELIGIBLE'
                result['final_reason'] = 'Rules not met (ML not available)'
        
        # Generate comprehensive explanation
        result['explanation'] = self._generate_explanation(result)
        
        return result
    
    def _calculate_combined_score(
        self,
        rule_eligible: bool,
        rule_confidence: float,
        ml_probability: float,
        ml_confidence: float
    ) -> float:
        """
        Calculate combined eligibility score
        
        Args:
            rule_eligible: Whether rules passed
            rule_confidence: Rule confidence (0-1)
            ml_probability: ML probability (0-1)
            ml_confidence: ML confidence (0-1)
        
        Returns:
            Combined score (0-1)
        """
        rule_score = 1.0 if rule_eligible else 0.0
        
        # Weighted combination
        combined = (
            self.rule_weight * rule_score * rule_confidence +
            self.ml_weight * ml_probability * ml_confidence
        )
        
        # Normalize to 0-1
        return max(0.0, min(1.0, combined))
    
    def _calculate_confidence(
        self,
        rule_confidence: float,
        ml_confidence: float,
        rule_status: str
    ) -> float:
        """
        Calculate overall confidence score
        
        Args:
            rule_confidence: Rule confidence
            ml_confidence: ML confidence
            rule_status: Rule status
        
        Returns:
            Combined confidence (0-1)
        """
        # Higher confidence when both agree
        if rule_status == 'RULE_ELIGIBLE':
            # Rules are certain, ML adds validation
            base_confidence = 0.8
            ml_boost = ml_confidence * 0.2
            return min(1.0, base_confidence + ml_boost)
        else:
            # Rules uncertain, rely more on ML
            return (rule_confidence * self.rule_weight + ml_confidence * self.ml_weight)
    
    def _determine_final_status(
        self,
        rule_eligible: bool,
        rule_status: str,
        ml_probability: float,
        ml_confidence: float,
        eligibility_score: float,
        confidence_score: float
    ) -> Tuple[str, bool, str]:
        """
        Determine final eligibility status with conflict resolution
        
        Args:
            rule_eligible: Whether rules passed
            rule_status: Rule status
            ml_probability: ML probability
            ml_confidence: ML confidence
            eligibility_score: Combined score
            confidence_score: Combined confidence
        
        Returns:
            Tuple of (status, conflict_resolved, reason)
        """
        conflict = False
        conflict_resolved = False
        reason = ""
        
        # Check for conflicts
        if rule_eligible and ml_probability < 0.3:
            conflict = True
            reason = "Conflict: Rules passed but ML predicts low eligibility"
        elif not rule_eligible and ml_probability > 0.7:
            conflict = True
            reason = "Conflict: Rules failed but ML predicts high eligibility"
        
        # Resolve conflicts using business rules
        if conflict:
            # Business rule: Never auto-identify if rules fail but ML says eligible
            # (Prevent leakage - be conservative)
            if not rule_eligible and ml_probability > 0.7:
                conflict_resolved = True
                if rule_status == 'NOT_ELIGIBLE':
                    return 'NOT_ELIGIBLE', conflict_resolved, \
                           f"Rules not met (ML suggests eligible but rules take precedence for safety)"
                else:
                    return 'POSSIBLE_ELIGIBLE', conflict_resolved, \
                           f"Some rules passed, ML suggests eligible - requires review"
            
            # If rules pass but ML says not eligible, use rules but flag for review
            elif rule_eligible and ml_probability < 0.3:
                conflict_resolved = True
                if confidence_score >= self.confidence_threshold:
                    return 'RULE_ELIGIBLE', conflict_resolved, \
                           f"Rules passed (ML suggests not eligible - flagged for review)"
                else:
                    return 'POSSIBLE_ELIGIBLE', conflict_resolved, \
                           f"Rules passed but ML suggests not eligible - requires review"
        
        # No conflict - determine status based on combined score
        if eligibility_score >= self.confidence_threshold:
            if rule_status == 'RULE_ELIGIBLE':
                return 'RULE_ELIGIBLE', conflict_resolved, \
                       f"Rules and ML both indicate eligibility (score: {eligibility_score:.2f})"
            else:
                return 'POSSIBLE_ELIGIBLE', conflict_resolved, \
                       f"ML suggests eligibility despite some rule failures (score: {eligibility_score:.2f})"
        
        elif eligibility_score >= 0.5:
            return 'POSSIBLE_ELIGIBLE', conflict_resolved, \
                   f"Mixed signals - moderate eligibility score ({eligibility_score:.2f})"
        
        else:
            return 'NOT_ELIGIBLE', conflict_resolved, \
                   f"Low eligibility score ({eligibility_score:.2f})"
    
    def _generate_explanation(self, result: Dict) -> str:
        """
        Generate human-readable explanation
        
        Args:
            result: Evaluation result dictionary
        
        Returns:
            Explanation string
        """
        parts = []
        
        # Rule engine explanation
        parts.append(f"Rule Engine: {result['rule_result']['explanation']}")
        
        # ML explanation
        if result['ml_available'] and result['ml_probability'] is not None:
            ml_prob = result['ml_probability']
            parts.append(f"ML Model: {ml_prob*100:.1f}% probability of eligibility")
            
            # Top features
            if result['ml_top_features']:
                top_feat = result['ml_top_features'][0]
                parts.append(f"Key factor: {top_feat['feature']} "
                           f"({'increases' if top_feat['shap_value'] > 0 else 'decreases'} eligibility)")
        else:
            parts.append("ML Model: Not available")
        
        # Final status
        parts.append(f"Final Status: {result['evaluation_status']}")
        parts.append(f"Confidence: {result['confidence_score']*100:.1f}%")
        
        return " | ".join(parts)
    
    def evaluate_batch(
        self,
        scheme_id: str,
        families_data: List[Dict],
        use_ml: bool = True
    ) -> List[Dict]:
        """
        Evaluate eligibility for multiple families
        
        Args:
            scheme_id: Scheme ID
            families_data: List of family data dictionaries
            use_ml: Whether to use ML scorer
        
        Returns:
            List of evaluation results
        """
        results = []
        
        for family_data in families_data:
            try:
                result = self.evaluate(scheme_id, family_data, use_ml=use_ml)
                results.append(result)
            except Exception as e:
                print(f"❌ Error evaluating family {family_data.get('family_id', 'unknown')}: {e}")
                results.append({
                    'scheme_id': scheme_id,
                    'family_id': family_data.get('family_id', 'unknown'),
                    'evaluation_status': 'ERROR',
                    'error': str(e)
                })
        
        return results
    
    def close(self):
        """Close all connections"""
        if self.rule_engine:
            self.rule_engine.close()
        if self.ml_scorer:
            self.ml_scorer.close()


def main():
    """Test hybrid evaluator"""
    evaluator = HybridEvaluator()
    
    # Sample family data
    family_data = {
        'family_id': 'test-123',
        'head_age': 65,
        'head_gender': 'M',
        'district_id': 101,
        'caste_id': 1,
        'income_band': 'LOW',
        'family_size': 4,
        'schemes_enrolled_list': [],
        'benefits_received_total_1y': 0,
        'education_level': 'PRIMARY',
        'employment_status': 'UNEMPLOYED'
    }
    
    # Evaluate
    result = evaluator.evaluate('SCHEME_001', family_data, use_ml=False)
    
    print("=" * 80)
    print("Hybrid Eligibility Evaluation Result")
    print("=" * 80)
    print(f"Scheme: {result['scheme_id']}")
    print(f"Family: {result['family_id']}")
    print(f"Status: {result['evaluation_status']}")
    print(f"Eligibility Score: {result['eligibility_score']:.3f}")
    print(f"Confidence: {result['confidence_score']:.3f}")
    print(f"\nRule Engine:")
    print(f"  Eligible: {result['rule_eligible']}")
    print(f"  Rules Passed: {len(result['rules_passed'])}")
    print(f"  Rule Path: {result['rule_path']}")
    if result['ml_available']:
        print(f"\nML Model:")
        print(f"  Probability: {result['ml_probability']:.3f}" if result['ml_probability'] else "  Not available")
    print(f"\nExplanation: {result['explanation']}")
    print("=" * 80)
    
    evaluator.close()


if __name__ == "__main__":
    main()

