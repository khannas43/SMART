"""
Rule Engine for Eligibility Evaluation
Deterministic rule-based eligibility checking
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, date
import yaml
import warnings
warnings.filterwarnings('ignore')

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class RuleEngine:
    """
    Deterministic rule engine for scheme eligibility evaluation
    
    Evaluates machine-readable eligibility rules against Golden Records
    and 360° Profile data to determine rule-based eligibility.
    """
    
    def __init__(self, config_path=None):
        """
        Initialize rule engine
        
        Args:
            config_path: Path to configuration file
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "use_case_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Database connection
        db_config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
        with open(db_config_path, 'r') as f:
            db_config = yaml.safe_load(f)['database']
        
        self.db = DBConnector(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['name'],
            user=db_config['user'],
            password=db_config['password']
        )
        self.db.connect()
        
        # Cache for rules (to avoid repeated DB queries)
        self._rules_cache = {}
        self._cache_ttl = self.config['components']['rule_engine'].get('cache_ttl_hours', 24) * 3600
        self._cache_timestamps = {}
    
    def load_scheme_rules(self, scheme_id: str, force_reload: bool = False) -> List[Dict]:
        """
        Load eligibility rules for a scheme
        
        Args:
            scheme_id: Scheme ID
            force_reload: Force reload from database
        
        Returns:
            List of rule dictionaries
        """
        # Check cache
        if not force_reload and scheme_id in self._rules_cache:
            cache_age = (datetime.now() - self._cache_timestamps[scheme_id]).total_seconds()
            if cache_age < self._cache_ttl:
                return self._rules_cache[scheme_id]
        
        query = """
            SELECT 
                rule_id, rule_name, rule_type, rule_expression,
                rule_operator, rule_value, is_mandatory, priority,
                version, effective_from, effective_to
            FROM eligibility.scheme_eligibility_rules
            WHERE scheme_code = %s
                AND (effective_to IS NULL OR effective_to >= CURRENT_DATE)
                AND (effective_from <= CURRENT_DATE)
            ORDER BY priority DESC, rule_id
        """
        
        df = pd.read_sql(query, self.db.connection, params=(scheme_id,))
        rules = df.to_dict('records')
        
        # Cache rules
        self._rules_cache[scheme_id] = rules
        self._cache_timestamps[scheme_id] = datetime.now()
        
        return rules
    
    def load_exclusion_rules(self, scheme_id: str) -> List[Dict]:
        """
        Load exclusion rules for a scheme
        
        Args:
            scheme_id: Scheme ID
        
        Returns:
            List of exclusion rule dictionaries
        """
        query = """
            SELECT exclusion_id, exclusion_condition, exclusion_type, version
            FROM eligibility.scheme_exclusion_rules
            WHERE scheme_code = %s
                AND (effective_to IS NULL OR effective_to >= CURRENT_DATE)
                AND (effective_from <= CURRENT_DATE)
        """
        
        df = pd.read_sql(query, self.db.connection, params=(scheme_id,))
        return df.to_dict('records')
    
    def evaluate_rule(
        self,
        rule: Dict,
        family_data: Dict,
        member_data: Optional[Dict] = None
    ) -> Tuple[bool, str]:
        """
        Evaluate a single rule against family/member data
        
        Args:
            rule: Rule dictionary
            family_data: Family-level data (Golden Record + 360° Profile)
            member_data: Member-level data (if applicable)
        
        Returns:
            Tuple of (passed: bool, reason: str)
        """
        rule_type = rule['rule_type']
        rule_operator = rule['rule_operator']
        rule_value = rule['rule_value']
        rule_expression = rule['rule_expression']
        
        # Determine data source (family vs member)
        data = member_data if member_data is not None else family_data
        
        try:
            # Age-based rules
            if rule_type == 'AGE':
                age = data.get('age') or family_data.get('head_age')
                if age is None:
                    return False, f"Age not available"
                
                if rule_operator == '>=':
                    passed = age >= float(rule_value)
                    return passed, f"Age {age} {'>=' if passed else '<'} {rule_value}"
                
                elif rule_operator == '<=':
                    passed = age <= float(rule_value)
                    return passed, f"Age {age} {'<=' if passed else '>'} {rule_value}"
                
                elif rule_operator == '=':
                    passed = age == float(rule_value)
                    return passed, f"Age {age} {'==' if passed else '!='} {rule_value}"
            
            # Income-based rules
            elif rule_type == 'INCOME':
                income_band = data.get('income_band') or family_data.get('inferred_income_band')
                if income_band is None:
                    return False, "Income band not available"
                
                if rule_operator == 'IN':
                    allowed_bands = [b.strip() for b in rule_value.split(',')]
                    passed = income_band in allowed_bands
                    return passed, f"Income band {income_band} {'in' if passed else 'not in'} {allowed_bands}"
                
                elif rule_operator == 'NOT_IN':
                    excluded_bands = [b.strip() for b in rule_value.split(',')]
                    passed = income_band not in excluded_bands
                    return passed, f"Income band {income_band} {'not in' if passed else 'in'} {excluded_bands}"
            
            # Gender-based rules
            elif rule_type == 'GENDER':
                gender = data.get('gender') or family_data.get('head_gender')
                if gender is None:
                    return False, "Gender not available"
                
                allowed_genders = [g.strip().upper() for g in rule_value.split(',')]
                passed = gender.upper() in allowed_genders
                return passed, f"Gender {gender} {'in' if passed else 'not in'} {allowed_genders}"
            
            # Geography-based rules
            elif rule_type == 'GEOGRAPHY':
                if rule_operator == 'DISTRICT_IN':
                    district_id = family_data.get('district_id')
                    allowed_districts = [int(d.strip()) for d in rule_value.split(',')]
                    passed = district_id in allowed_districts if district_id else False
                    return passed, f"District {district_id} {'in' if passed else 'not in'} {allowed_districts}"
                
                elif rule_operator == 'BLOCK_IN':
                    block_id = family_data.get('block_id')
                    allowed_blocks = [int(b.strip()) for b in rule_value.split(',')]
                    passed = block_id in allowed_blocks if block_id else False
                    return passed, f"Block {block_id} {'in' if passed else 'not in'} {allowed_blocks}"
            
            # Category/Caste-based rules
            elif rule_type == 'CATEGORY':
                caste_id = family_data.get('caste_id')
                if rule_operator == 'IN':
                    allowed_castes = [int(c.strip()) for c in rule_value.split(',')]
                    passed = caste_id in allowed_castes if caste_id else False
                    return passed, f"Caste {caste_id} {'in' if passed else 'not in'} {allowed_castes}"
            
            # Disability-based rules
            elif rule_type == 'DISABILITY':
                disability_status = data.get('disability_status') or family_data.get('has_disabled_member')
                if rule_operator == '=':
                    passed = (disability_status == True) if rule_value.upper() == 'TRUE' else (disability_status == False)
                    return passed, f"Disability status {disability_status} {'matches' if passed else 'does not match'} {rule_value}"
            
            # Household composition rules
            elif rule_type == 'HOUSEHOLD':
                if rule_expression and 'family_size' in rule_expression:
                    family_size = family_data.get('family_size', 1)
                    # Simple evaluation: family_size >= value
                    if '>=' in rule_expression:
                        value = float(rule_value)
                        passed = family_size >= value
                        return passed, f"Family size {family_size} {'>=' if passed else '<'} {value}"
            
            # Marital status rules
            elif rule_type == 'MARITAL_STATUS':
                marital_status = data.get('marital_status')
                if rule_operator == '=':
                    passed = (marital_status or '').upper() == rule_value.upper()
                    return passed, f"Marital status {marital_status} {'matches' if passed else 'does not match'} {rule_value}"
            
            # Prior participation rules
            elif rule_type == 'PRIOR_PARTICIPATION':
                if rule_operator == 'NOT_IN':
                    schemes_enrolled = family_data.get('schemes_enrolled_list', [])
                    excluded_schemes = [s.strip() for s in rule_value.split(',')]
                    passed = not any(s in excluded_schemes for s in schemes_enrolled)
                    return passed, f"Not enrolled in excluded schemes: {passed}"
            
            # Custom expression evaluation (fallback)
            else:
                # Try to evaluate rule_expression as Python expression
                # This is a simplified version - in production, use a proper expression parser
                try:
                    # Safe evaluation context
                    context = {**family_data, **(member_data or {})}
                    # Convert rule_expression to safe evaluation
                    # Example: "age >= 60" -> eval("age >= 60", {"__builtins__": {}}, context)
                    # For production, use ast.literal_eval or a proper expression parser
                    passed = eval(rule_expression, {"__builtins__": {}}, context)
                    return passed, f"Expression {rule_expression} evaluated to {passed}"
                except Exception as e:
                    return False, f"Rule evaluation error: {str(e)}"
        
        except Exception as e:
            return False, f"Error evaluating rule: {str(e)}"
    
    def evaluate_scheme_eligibility(
        self,
        scheme_id: str,
        family_data: Dict,
        member_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Evaluate eligibility for a scheme using rule engine
        
        Args:
            scheme_id: Scheme ID
            family_data: Family-level data (Golden Record + 360° Profile)
            member_data: Member-level data (if applicable)
        
        Returns:
            Dictionary with evaluation results:
            {
                'eligible': bool,
                'status': str,  # RULE_ELIGIBLE, NOT_ELIGIBLE, POSSIBLE_ELIGIBLE
                'rules_passed': List[str],
                'rules_failed': List[str],
                'rule_path': str,
                'reason_codes': List[str],
                'explanation': str
            }
        """
        # Load rules
        rules = self.load_scheme_rules(scheme_id)
        exclusion_rules = self.load_exclusion_rules(scheme_id)
        
        if not rules:
            return {
                'eligible': False,
                'status': 'NOT_ELIGIBLE',
                'rules_passed': [],
                'rules_failed': [],
                'rule_path': 'No rules defined',
                'reason_codes': ['NO_RULES_DEFINED'],
                'explanation': 'No eligibility rules defined for this scheme'
            }
        
        # Check exclusion rules first
        for exclusion in exclusion_rules:
            try:
                # Evaluate exclusion condition
                context = {**family_data, **(member_data or {})}
                # Simplified exclusion check - in production, use proper expression parser
                excluded = eval(exclusion['exclusion_condition'], {"__builtins__": {}}, context)
                if excluded:
                    return {
                        'eligible': False,
                        'status': 'NOT_ELIGIBLE',
                        'rules_passed': [],
                        'rules_failed': [f"EXCLUSION: {exclusion['exclusion_condition']}"],
                        'rule_path': f"Excluded by: {exclusion['exclusion_type']}",
                        'reason_codes': [f"EXCLUDED_{exclusion['exclusion_type']}"],
                        'explanation': f"Family excluded by {exclusion['exclusion_type']} rule"
                    }
            except Exception:
                pass  # Skip exclusion if evaluation fails
        
        # Evaluate eligibility rules
        rules_passed = []
        rules_failed = []
        reason_codes = []
        rule_path_parts = []
        mandatory_failed = False
        
        for rule in rules:
            try:
                result = self.evaluate_rule(rule, family_data, member_data)
                if result is None:
                    print(f"⚠️  evaluate_rule returned None for rule {rule.get('rule_id')}")
                    rules_failed.append(str(rule['rule_id']))
                    reason_codes.append(f"FAILED_{rule.get('rule_type', 'UNKNOWN')}")
                    continue
                
                passed, reason = result
            except Exception as e:
                print(f"⚠️  Error evaluating rule {rule.get('rule_id')}: {e}")
                rules_failed.append(str(rule['rule_id']))
                reason_codes.append(f"FAILED_{rule.get('rule_type', 'UNKNOWN')}")
                continue
            
            if passed:
                rules_passed.append(str(rule['rule_id']))
                rule_path_parts.append(rule['rule_name'])
                reason_codes.append(f"PASSED_{rule['rule_type']}")
            else:
                rules_failed.append(str(rule['rule_id']))
                reason_codes.append(f"FAILED_{rule['rule_type']}")
                
                if rule['is_mandatory']:
                    mandatory_failed = True
                    rule_path_parts.append(f"❌ {rule['rule_name']} ({reason})")
        
        # Determine eligibility status
        if mandatory_failed:
            eligible = False
            status = 'NOT_ELIGIBLE'
        elif len(rules_passed) == len(rules):
            eligible = True
            status = 'RULE_ELIGIBLE'
        elif len(rules_passed) > 0:
            eligible = True  # Some rules passed, might be eligible
            status = 'POSSIBLE_ELIGIBLE'
        else:
            eligible = False
            status = 'NOT_ELIGIBLE'
        
        rule_path = " | ".join(rule_path_parts) if rule_path_parts else "No rules evaluated"
        explanation = f"Passed {len(rules_passed)}/{len(rules)} rules. {status}"
        
        return {
            'eligible': eligible,
            'status': status,
            'rules_passed': rules_passed,
            'rules_failed': rules_failed,
            'rule_path': rule_path,
            'reason_codes': reason_codes,
            'explanation': explanation
        }
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.disconnect()


def main():
    """Test rule engine"""
    engine = RuleEngine()
    
    # Sample family data
    family_data = {
        'family_id': 'test-123',
        'head_age': 65,
        'head_gender': 'M',
        'district_id': 101,
        'caste_id': 1,
        'income_band': 'LOW',
        'family_size': 4,
        'schemes_enrolled_list': []
    }
    
    # Test evaluation
    result = engine.evaluate_scheme_eligibility('SCHEME_001', family_data)
    print("Evaluation Result:")
    print(result)
    
    engine.close()


if __name__ == "__main__":
    main()

