"""
Prioritizer
Prioritizes detected cases based on risk, financial exposure, and vulnerability
Use Case ID: AI-PLATFORM-07
"""

from typing import Dict, Any, Optional
import yaml
from pathlib import Path


class Prioritizer:
    """Prioritizes cases for worklist assignment"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Prioritizer"""
        if config_path is None:
            base_dir = Path(__file__).parent.parent.parent
            config_path = base_dir / "config" / "use_case_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Get prioritization configuration
        prioritization_config = self.config.get('prioritization', {})
        self.financial_exposure_weight = prioritization_config.get('financial_exposure_weight', 0.4)
        self.risk_score_weight = prioritization_config.get('risk_score_weight', 0.3)
        self.vulnerability_weight = prioritization_config.get('vulnerability_weight', 0.2)
        self.time_weight = prioritization_config.get('time_since_flag_weight', 0.1)
        
        self.high_financial_exposure = prioritization_config.get('high_financial_exposure', 10000)
        self.high_risk_score = prioritization_config.get('high_risk_score', 0.7)
        self.high_vulnerability = prioritization_config.get('high_vulnerability', 0.8)
    
    def prioritize_case(
        self,
        case_data: Dict[str, Any],
        rule_results: Dict[str, Any],
        ml_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Prioritize a detected case
        
        Args:
            case_data: Case data including benefit amounts, etc.
            rule_results: Rule-based detection results
            ml_results: ML detection results (optional)
        
        Returns:
            Prioritization result with priority score and level
        """
        # Calculate financial exposure
        financial_exposure = self._calculate_financial_exposure(case_data)
        
        # Get risk score
        risk_score = ml_results.get('risk_score', 0.5) if ml_results else 0.5
        
        # Calculate vulnerability score (higher = more vulnerable, handle with caution)
        vulnerability_score = self._calculate_vulnerability_score(case_data, rule_results)
        
        # Calculate priority score (higher = more urgent)
        priority_score = (
            self.financial_exposure_weight * self._normalize_financial_exposure(financial_exposure) +
            self.risk_score_weight * risk_score +
            self.vulnerability_weight * (1 - vulnerability_score) +  # Lower vulnerability = higher priority (can take action)
            self.time_weight * 0.5  # Placeholder for time since flag
        )
        
        # Determine priority level (1=highest, 10=lowest)
        priority_level = self._determine_priority_level(priority_score, financial_exposure, risk_score, vulnerability_score)
        
        return {
            'priority_score': float(priority_score),
            'priority_level': priority_level,
            'financial_exposure': financial_exposure,
            'risk_score': risk_score,
            'vulnerability_score': vulnerability_score,
            'priority_factors': {
                'financial_exposure': financial_exposure,
                'risk_score': risk_score,
                'vulnerability_score': vulnerability_score
            }
        }
    
    def _calculate_financial_exposure(self, case_data: Dict[str, Any]) -> float:
        """Calculate total financial exposure for the case"""
        # Get current benefit amount
        current_benefits = case_data.get('current_benefits', {})
        if isinstance(current_benefits, dict):
            benefit_amount = float(current_benefits.get('benefit_amount', 0) or 0)
            frequency = current_benefits.get('frequency', 'MONTHLY')
            
            # Convert to monthly
            if frequency == 'YEARLY':
                monthly_amount = benefit_amount / 12
            elif frequency == 'WEEKLY':
                monthly_amount = benefit_amount * 4.33
            else:
                monthly_amount = benefit_amount
            
            # Annual exposure (12 months)
            return monthly_amount * 12
        else:
            return 0.0
    
    def _calculate_vulnerability_score(
        self,
        case_data: Dict[str, Any],
        rule_results: Dict[str, Any]
    ) -> float:
        """
        Calculate vulnerability score (higher = more vulnerable)
        Vulnerable beneficiaries should be handled with more caution
        """
        score = 0.0
        
        # Factor 1: Income level (lower income = higher vulnerability)
        # This would come from profile data - placeholder for now
        income_band = case_data.get('income_band', 'MIDDLE_INCOME')
        if income_band in ['BELOW_POVERTY_LINE', 'VERY_LOW_INCOME']:
            score += 0.4
        elif income_band == 'LOW_INCOME':
            score += 0.2
        
        # Factor 2: Age (elderly = higher vulnerability)
        age = case_data.get('age', 0)
        if age >= 60:
            score += 0.3
        elif age >= 40:
            score += 0.1
        
        # Factor 3: Disability status
        if case_data.get('disability_status'):
            score += 0.2
        
        # Factor 4: Family size (larger families = higher vulnerability)
        family_size = case_data.get('family_size', 0)
        if family_size >= 5:
            score += 0.1
        
        return min(1.0, score)
    
    def _normalize_financial_exposure(self, exposure: float) -> float:
        """Normalize financial exposure to 0-1 range"""
        # Use threshold as midpoint
        if exposure <= 0:
            return 0.0
        elif exposure >= self.high_financial_exposure * 2:
            return 1.0
        else:
            return min(1.0, exposure / (self.high_financial_exposure * 2))
    
    def _determine_priority_level(
        self,
        priority_score: float,
        financial_exposure: float,
        risk_score: float,
        vulnerability_score: float
    ) -> int:
        """Determine priority level (1=highest, 10=lowest)"""
        # Immediate priority (1): High financial exposure + high risk + low vulnerability
        if (financial_exposure >= self.high_financial_exposure and
            risk_score >= self.high_risk_score and
            vulnerability_score < 0.3):
            return 1
        
        # High priority (3): High financial or high risk
        if (financial_exposure >= self.high_financial_exposure or
            risk_score >= self.high_risk_score):
            # Adjust for vulnerability (higher vulnerability = slightly lower priority)
            if vulnerability_score >= self.high_vulnerability:
                return 5
            else:
                return 3
        
        # Medium priority (5): Medium financial or medium risk
        if (financial_exposure >= self.high_financial_exposure / 2 or
            risk_score >= self.high_risk_score / 2):
            if vulnerability_score >= self.high_vulnerability:
                return 7
            else:
                return 5
        
        # Low priority (8): Everything else
        return 8

