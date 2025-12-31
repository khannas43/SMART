"""
Case Classifier
Classifies detected cases based on confidence and detection results
Use Case ID: AI-PLATFORM-07
"""

from typing import Dict, Any, Optional
import yaml
from pathlib import Path


class CaseClassifier:
    """Classifies detected cases into categories with confidence levels"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Case Classifier"""
        if config_path is None:
            base_dir = Path(__file__).parent.parent.parent
            config_path = base_dir / "config" / "use_case_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Get classification thresholds
        classification_config = self.config.get('case_classification', {})
        self.high_confidence_threshold = classification_config.get('high_confidence_threshold', 0.8)
        self.medium_confidence_threshold = classification_config.get('medium_confidence_threshold', 0.5)
        self.low_confidence_threshold = classification_config.get('low_confidence_threshold', 0.3)
        self.hard_ineligible_threshold = classification_config.get('hard_ineligible_threshold', 0.8)
        self.likely_mistargeted_threshold = classification_config.get('likely_mistargeted_threshold', 0.6)
    
    def classify_case(
        self,
        rule_results: Dict[str, Any],
        ml_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Classify a detected case
        
        Args:
            rule_results: Results from rule-based detection
            ml_results: Results from ML anomaly detection (optional)
        
        Returns:
            Classification with case_type, confidence_level, and recommendations
        """
        # Determine confidence level
        confidence_level = self._determine_confidence(rule_results, ml_results)
        
        # Determine case type
        case_type = self._determine_case_type(rule_results, ml_results, confidence_level)
        
        # Generate rationale
        rationale = self._generate_rationale(rule_results, ml_results, case_type, confidence_level)
        
        # Recommend action
        recommended_action = self._recommend_action(case_type, confidence_level, rule_results, ml_results)
        action_urgency = self._determine_urgency(case_type, confidence_level, rule_results)
        
        return {
            'case_type': case_type,
            'confidence_level': confidence_level,
            'detection_rationale': rationale,
            'recommended_action': recommended_action,
            'action_urgency': action_urgency,
            'requires_human_review': case_type != 'LOW_CONFIDENCE_FLAG'
        }
    
    def _determine_confidence(
        self,
        rule_results: Dict[str, Any],
        ml_results: Optional[Dict[str, Any]]
    ) -> str:
        """Determine confidence level (HIGH, MEDIUM, LOW)"""
        # High confidence: Critical rule failures
        if rule_results.get('critical_failures'):
            return 'HIGH'
        
        # High confidence: High anomaly/risk scores
        if ml_results:
            if (ml_results.get('risk_score', 0) >= self.high_confidence_threshold or
                ml_results.get('anomaly_score', 0) >= self.high_confidence_threshold):
                return 'HIGH'
        
        # Medium confidence: Some rule failures or medium ML scores
        if (not rule_results.get('all_passed') or
            (ml_results and ml_results.get('risk_score', 0) >= self.medium_confidence_threshold)):
            return 'MEDIUM'
        
        # Low confidence: Only minor anomalies
        if ml_results and ml_results.get('anomaly_score', 0) >= self.low_confidence_threshold:
            return 'LOW'
        
        return 'LOW'
    
    def _determine_case_type(
        self,
        rule_results: Dict[str, Any],
        ml_results: Optional[Dict[str, Any]],
        confidence_level: str
    ) -> str:
        """Determine case type (HARD_INELIGIBLE, LIKELY_MIS_TARGETED, LOW_CONFIDENCE_FLAG)"""
        # Hard ineligible: Critical rule failures with high confidence
        if rule_results.get('critical_failures') and confidence_level == 'HIGH':
            return 'HARD_INELIGIBLE'
        
        # Hard ineligible: Very high risk/anomaly scores
        if ml_results:
            if (ml_results.get('risk_score', 0) >= self.hard_ineligible_threshold or
                (ml_results.get('anomaly_score', 0) >= self.hard_ineligible_threshold and
                 ml_results.get('anomaly_type') in ['POSSIBLE_DUPLICATE', 'POSSIBLE_FAKE_ID'])):
                return 'HARD_INELIGIBLE'
        
        # Likely mis-targeted: Rule failures or medium-high ML scores
        if (not rule_results.get('all_passed') or
            (ml_results and ml_results.get('risk_score', 0) >= self.likely_mistargeted_threshold)):
            return 'LIKELY_MIS_TARGETED'
        
        # Low confidence: Minor anomalies only
        if ml_results and ml_results.get('anomaly_score', 0) >= self.low_confidence_threshold:
            return 'LOW_CONFIDENCE_FLAG'
        
        return 'LOW_CONFIDENCE_FLAG'
    
    def _generate_rationale(
        self,
        rule_results: Dict[str, Any],
        ml_results: Optional[Dict[str, Any]],
        case_type: str,
        confidence_level: str
    ) -> str:
        """Generate human-readable rationale"""
        rationale_parts = []
        
        # Add rule-based findings
        if not rule_results.get('all_passed'):
            failed_rules = [d['rule_name'] for d in rule_results.get('detections', []) if not d.get('passed')]
            if failed_rules:
                rationale_parts.append(f"Rule checks failed: {', '.join(failed_rules)}")
            
            if rule_results.get('critical_failures'):
                rationale_parts.append(f"Critical failures: {', '.join(rule_results['critical_failures'])}")
        
        # Add ML findings
        if ml_results:
            anomaly_type = ml_results.get('anomaly_type')
            if anomaly_type:
                rationale_parts.append(f"ML detected: {anomaly_type}")
            
            risk_score = ml_results.get('risk_score', 0)
            if risk_score >= 0.7:
                rationale_parts.append(f"High risk score: {risk_score:.2f}")
        
        # Add confidence level
        rationale_parts.append(f"Confidence: {confidence_level}")
        
        # Combine into rationale
        if rationale_parts:
            return ". ".join(rationale_parts)
        else:
            return f"Case classified as {case_type} with {confidence_level} confidence"
    
    def _recommend_action(
        self,
        case_type: str,
        confidence_level: str,
        rule_results: Dict[str, Any],
        ml_results: Optional[Dict[str, Any]]
    ) -> str:
        """Recommend action based on case type and confidence"""
        actions_config = self.config.get('actions', {})
        
        if case_type == 'HARD_INELIGIBLE':
            # For hard ineligible, recommend verification then suspend/cancel
            if confidence_level == 'HIGH':
                return 'SUSPEND'  # After verification
            else:
                return 'VERIFY'
        
        elif case_type == 'LIKELY_MIS_TARGETED':
            # For likely mis-targeted, recommend verification and recalculation
            return 'VERIFY'
        
        else:  # LOW_CONFIDENCE_FLAG
            # For low confidence, recommend review or monitor
            if ml_results and ml_results.get('anomaly_score', 0) > 0.5:
                return 'REVIEW'
            else:
                return 'MONITOR'
    
    def _determine_urgency(
        self,
        case_type: str,
        confidence_level: str,
        rule_results: Dict[str, Any]
    ) -> str:
        """Determine action urgency"""
        # Immediate: Critical failures with high confidence
        if (case_type == 'HARD_INELIGIBLE' and
            confidence_level == 'HIGH' and
            rule_results.get('critical_failures')):
            return 'IMMEDIATE'
        
        # High: Hard ineligible or high confidence likely mis-targeted
        if (case_type == 'HARD_INELIGIBLE' or
            (case_type == 'LIKELY_MIS_TARGETED' and confidence_level == 'HIGH')):
            return 'HIGH'
        
        # Medium: Medium confidence likely mis-targeted
        if case_type == 'LIKELY_MIS_TARGETED':
            return 'MEDIUM'
        
        # Low: Low confidence flags
        return 'LOW'

