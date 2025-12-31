"""
Eligibility Checker Service
Use Case ID: AI-PLATFORM-08

Main service for performing eligibility checks for both logged-in and guest users.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import json
import yaml

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "03_identification_beneficiary" / "src"))

from db_connector import DBConnector

# Import from AI-PLATFORM-03 (Eligibility Engine)
try:
    from evaluator_service import EligibilityEvaluationService
except ImportError:
    # Fallback if direct import fails
    EligibilityEvaluationService = None


class EligibilityChecker:
    """
    Eligibility Checker Service
    
    Supports:
    - Logged-in users: Direct evaluation using Golden Record + 360° Profile
    - Guest users: Questionnaire-based evaluation with approximate results
    - Anonymous mode: Basic checks with limited accuracy
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Eligibility Checker"""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "use_case_config.yaml"
        
        with open(config_path, 'r') as f:
            self.use_case_config = yaml.safe_load(f)
        
        # Database configuration
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
        
        # External database connections
        external_dbs = yaml.safe_load(open(db_config_path, 'r')).get('external_databases', {})
        self.external_dbs = {}
        for name, ext_config in external_dbs.items():
            self.external_dbs[name] = DBConnector(
                host=ext_config['host'],
                port=ext_config['port'],
                database=ext_config['name'],
                user=ext_config['user'],
                password=ext_config['password']
            )
        
        # Initialize eligibility evaluation service (AI-PLATFORM-03)
        eval_config_path = Path(__file__).parent.parent.parent.parent / "03_identification_beneficiary" / "config" / "use_case_config.yaml"
        if eval_config_path.exists() and EligibilityEvaluationService:
            try:
                self.evaluator_service = EligibilityEvaluationService(str(eval_config_path))
            except Exception as e:
                print(f"⚠️  Could not initialize EligibilityEvaluationService: {e}")
                self.evaluator_service = None
        else:
            self.evaluator_service = None
        
        # Configuration
        self.checker_config = self.use_case_config.get('eligibility_checker', {})
        self.guest_mode_enabled = self.checker_config.get('guest_mode_enabled', True)
        self.anonymous_allowed = self.checker_config.get('anonymous_checks_allowed', True)
    
    def connect(self):
        """Connect to databases"""
        self.db.connect()
        for ext_db in self.external_dbs.values():
            ext_db.connect()
    
    def disconnect(self):
        """Disconnect from databases"""
        self.db.disconnect()
        for ext_db in self.external_dbs.values():
            ext_db.disconnect()
    
    def check_eligibility(
        self,
        family_id: Optional[str] = None,
        beneficiary_id: Optional[str] = None,
        questionnaire_responses: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        scheme_codes: Optional[List[str]] = None,
        check_type: str = 'FULL_CHECK',
        check_mode: str = 'WEB'
    ) -> Dict[str, Any]:
        """
        Perform eligibility check
        
        Args:
            family_id: Family ID for logged-in users
            beneficiary_id: Optional beneficiary ID for specific beneficiary
            questionnaire_responses: Guest user questionnaire answers
            session_id: Session ID for guest/anonymous users
            scheme_codes: List of scheme codes to check (None for all active)
            check_type: 'FULL_CHECK', 'SCHEME_SPECIFIC', 'QUICK_CHECK'
            check_mode: 'WEB', 'MOBILE_APP', 'CHATBOT', 'ASSISTED'
        
        Returns:
            Dictionary with eligibility check results
        """
        start_time = datetime.now()
        
        # Determine user type
        if family_id:
            user_type = 'LOGGED_IN'
            if not session_id:
                session_id = str(uuid.uuid4())
        elif questionnaire_responses:
            user_type = 'GUEST'
            if not session_id:
                session_id = str(uuid.uuid4())
        else:
            user_type = 'ANONYMOUS'
            if not session_id:
                session_id = str(uuid.uuid4())
            # Create minimal questionnaire from empty responses
            questionnaire_responses = {}
        
        # Get schemes to check
        if scheme_codes is None:
            scheme_codes = self._get_active_scheme_codes()
        
        # Perform eligibility evaluation
        if user_type == 'LOGGED_IN':
            # Use eligibility engine (AI-PLATFORM-03)
            evaluations = self._check_logged_in_user(family_id, scheme_codes)
        else:
            # Use questionnaire-based evaluation
            evaluations = self._check_guest_user(questionnaire_responses, scheme_codes)
        
        # Process results
        eligible_count = sum(1 for e in evaluations if e.get('eligibility_status') == 'ELIGIBLE')
        possible_eligible_count = sum(1 for e in evaluations if e.get('eligibility_status') == 'POSSIBLE_ELIGIBLE')
        not_eligible_count = sum(1 for e in evaluations if e.get('eligibility_status') == 'NOT_ELIGIBLE')
        
        processing_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Record check in database
        check_id = self._record_eligibility_check(
            family_id=family_id,
            beneficiary_id=beneficiary_id,
            session_id=session_id,
            user_type=user_type,
            check_type=check_type,
            check_mode=check_mode,
            questionnaire_responses=questionnaire_responses if user_type != 'LOGGED_IN' else None,
            total_schemes_checked=len(scheme_codes),
            eligible_count=eligible_count,
            possible_eligible_count=possible_eligible_count,
            not_eligible_count=not_eligible_count,
            processing_time_ms=processing_time_ms
        )
        
        # Record individual scheme results
        for eval_result in evaluations:
            self._record_scheme_result(check_id, eval_result)
        
        return {
            'check_id': check_id,
            'session_id': session_id,
            'user_type': user_type,
            'check_type': check_type,
            'total_schemes_checked': len(scheme_codes),
            'eligible_count': eligible_count,
            'possible_eligible_count': possible_eligible_count,
            'not_eligible_count': not_eligible_count,
            'processing_time_ms': processing_time_ms,
            'evaluations': evaluations,
            'is_approximate': user_type != 'LOGGED_IN'  # Guest/anonymous results are approximate
        }
    
    def _check_logged_in_user(self, family_id: str, scheme_codes: List[str]) -> List[Dict[str, Any]]:
        """Check eligibility for logged-in user using eligibility engine"""
        evaluations = []
        
        if not self.evaluator_service:
            # Fallback: Basic rule-based evaluation
            return self._fallback_evaluation(family_id, scheme_codes)
        
        try:
            # Use AI-PLATFORM-03 eligibility engine
            result = self.evaluator_service.evaluate_family(
                family_id=family_id,
                scheme_ids=scheme_codes,
                use_ml=True,
                save_results=False  # We'll save separately in our schema
            )
            
            # Convert to our format
            for eval_data in result.get('evaluations', []):
                evaluation = {
                    'scheme_code': eval_data.get('scheme_code') or eval_data.get('scheme_id'),
                    'scheme_name': self._get_scheme_name(eval_data.get('scheme_code') or eval_data.get('scheme_id')),
                    'eligibility_status': self._map_status(eval_data.get('evaluation_status')),
                    'eligibility_score': float(eval_data.get('eligibility_score', 0.0)),
                    'confidence_level': self._calculate_confidence(eval_data),
                    'rule_evaluations': eval_data.get('rule_evaluations', {}),
                    'met_rules': eval_data.get('met_rules', []),
                    'failed_rules': eval_data.get('failed_rules', []),
                    'rule_path': eval_data.get('rule_path', ''),
                }
                evaluations.append(evaluation)
        
        except Exception as e:
            print(f"⚠️  Error using eligibility engine: {e}")
            evaluations = self._fallback_evaluation(family_id, scheme_codes)
        
        return evaluations
    
    def _check_guest_user(self, questionnaire_responses: Dict[str, Any], scheme_codes: List[str]) -> List[Dict[str, Any]]:
        """Check eligibility for guest user using questionnaire"""
        evaluations = []
        
        # Get basic attributes from questionnaire
        age = questionnaire_responses.get('age')
        gender = questionnaire_responses.get('gender')
        district = questionnaire_responses.get('district')
        income_band = questionnaire_responses.get('income_band')
        category = questionnaire_responses.get('category', 'General')
        disability = questionnaire_responses.get('disability', False)
        
        # For each scheme, evaluate based on questionnaire
        for scheme_code in scheme_codes:
            try:
                # Get scheme rules
                rules = self._get_scheme_rules(scheme_code)
                
                # Evaluate rules against questionnaire responses
                rule_results = []
                met_rules = []
                failed_rules = []
                all_mandatory_passed = True
                
                for rule in rules:
                    passed = self._evaluate_rule_against_questionnaire(rule, questionnaire_responses)
                    rule_results.append({
                        'rule_name': rule.get('rule_name'),
                        'rule_category': rule.get('rule_category'),
                        'passed': passed,
                        'severity': 'CRITICAL' if rule.get('is_mandatory') else 'MEDIUM'
                    })
                    
                    if passed:
                        met_rules.append(rule.get('rule_name'))
                    else:
                        failed_rules.append(rule.get('rule_name'))
                        if rule.get('is_mandatory'):
                            all_mandatory_passed = False
                
                # Determine eligibility status
                if all_mandatory_passed:
                    # Check if we have high confidence (all mandatory + most optional passed)
                    optional_passed = sum(1 for r in rule_results if not rules[rule_results.index(r)].get('is_mandatory') and r['passed'])
                    optional_total = sum(1 for r in rules if not r.get('is_mandatory'))
                    
                    if optional_total == 0 or (optional_passed / optional_total) >= 0.7:
                        status = 'ELIGIBLE'
                        score = 0.85
                    else:
                        status = 'POSSIBLE_ELIGIBLE'
                        score = 0.6
                else:
                    status = 'NOT_ELIGIBLE'
                    score = 0.2
                
                evaluation = {
                    'scheme_code': scheme_code,
                    'scheme_name': self._get_scheme_name(scheme_code),
                    'eligibility_status': status,
                    'eligibility_score': score,
                    'confidence_level': 'LOW',  # Guest results are always low confidence
                    'rule_evaluations': {'results': rule_results},
                    'met_rules': met_rules,
                    'failed_rules': failed_rules,
                    'rule_path': 'QUESTIONNAIRE_BASED'
                }
                evaluations.append(evaluation)
            
            except Exception as e:
                print(f"⚠️  Error evaluating {scheme_code}: {e}")
                evaluations.append({
                    'scheme_code': scheme_code,
                    'scheme_name': self._get_scheme_name(scheme_code),
                    'eligibility_status': 'NOT_ELIGIBLE',
                    'eligibility_score': 0.0,
                    'confidence_level': 'LOW',
                    'error': str(e)
                })
        
        return evaluations
    
    def _fallback_evaluation(self, family_id: str, scheme_codes: List[str]) -> List[Dict[str, Any]]:
        """Fallback evaluation when eligibility engine unavailable"""
        evaluations = []
        
        # Basic fallback: Return NOT_ELIGIBLE for all schemes
        for scheme_code in scheme_codes:
            evaluations.append({
                'scheme_code': scheme_code,
                'scheme_name': self._get_scheme_name(scheme_code),
                'eligibility_status': 'NOT_ELIGIBLE',
                'eligibility_score': 0.0,
                'confidence_level': 'LOW',
                'met_rules': [],
                'failed_rules': [],
                'rule_path': 'FALLBACK'
            })
        
        return evaluations
    
    def _evaluate_rule_against_questionnaire(self, rule: Dict[str, Any], responses: Dict[str, Any]) -> bool:
        """Evaluate a single rule against questionnaire responses"""
        rule_expr = rule.get('rule_expression', '')
        rule_type = rule.get('rule_type', '')
        
        # Simple rule evaluation (can be enhanced)
        if 'age' in rule_expr.lower() and 'age' in responses:
            # Extract age requirement from rule
            age_val = responses.get('age')
            if '>=' in rule_expr or '>=' in rule.get('rule_value', ''):
                required_age = int(rule.get('rule_value', '0').replace('>=', '').strip())
                return age_val >= required_age
            elif '<=' in rule_expr or '<=' in rule.get('rule_value', ''):
                required_age = int(rule.get('rule_value', '0').replace('<=', '').strip())
                return age_val <= required_age
        
        if 'income' in rule_expr.lower() and 'income_band' in responses:
            income_band = responses.get('income_band', '')
            # Map income bands to levels
            income_levels = {'Below 5000': 1, '5000-10000': 2, '10000-20000': 3, 'Above 20000': 4}
            user_level = income_levels.get(income_band, 4)
            # Assume rules require low income (level 1-2)
            return user_level <= 2
        
        if 'category' in rule_expr.lower() and 'category' in responses:
            required_category = rule.get('rule_value', '').upper()
            user_category = responses.get('category', 'General').upper()
            if required_category in ['SC', 'ST', 'OBC']:
                return user_category == required_category
        
        if 'disability' in rule_expr.lower() and 'disability' in responses:
            return responses.get('disability', False) == True
        
        # Default: Assume passed if we can't evaluate
        return True
    
    def _get_scheme_rules(self, scheme_code: str) -> List[Dict[str, Any]]:
        """Get rules for a scheme"""
        try:
            conn = self.external_dbs['eligibility'].connection
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT rule_id, scheme_code, rule_name, rule_type, rule_expression,
                       rule_operator, rule_value, is_mandatory, priority
                FROM eligibility.scheme_eligibility_rules
                WHERE scheme_code = %s
                  AND (effective_to IS NULL OR effective_to >= CURRENT_DATE)
                  AND (effective_from <= CURRENT_DATE)
                ORDER BY priority DESC, rule_id
            """, (scheme_code,))
            
            rules = []
            for row in cursor.fetchall():
                rules.append({
                    'rule_id': row[0],
                    'scheme_code': row[1],
                    'rule_name': row[2],
                    'rule_type': row[3],
                    'rule_expression': row[4],
                    'rule_operator': row[5],
                    'rule_value': row[6],
                    'is_mandatory': row[7],
                    'priority': row[8],
                    'rule_category': 'ELIGIBILITY'
                })
            
            cursor.close()
            return rules
        
        except Exception as e:
            print(f"⚠️  Error fetching rules for {scheme_code}: {e}")
            return []
    
    def _get_active_scheme_codes(self) -> List[str]:
        """Get list of active scheme codes"""
        try:
            conn = self.external_dbs['scheme_master'].connection
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT scheme_code
                FROM public.scheme_master
                WHERE is_active = TRUE OR is_active IS NULL
                ORDER BY scheme_code
            """)
            
            schemes = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return schemes if schemes else ['CHIRANJEEVI', 'OLD_AGE_PENSION', 'DISABILITY_PENSION']
        
        except Exception as e:
            print(f"⚠️  Error fetching schemes: {e}")
            return ['CHIRANJEEVI', 'OLD_AGE_PENSION', 'DISABILITY_PENSION']
    
    def _get_scheme_name(self, scheme_code: str) -> str:
        """Get scheme name"""
        try:
            conn = self.external_dbs['scheme_master'].connection
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT scheme_name
                FROM public.scheme_master
                WHERE scheme_code = %s
            """, (scheme_code,))
            
            row = cursor.fetchone()
            cursor.close()
            return row[0] if row else scheme_code
        
        except Exception:
            return scheme_code
    
    def _map_status(self, status: str) -> str:
        """Map eligibility engine status to our status"""
        mapping = {
            'RULE_ELIGIBLE': 'ELIGIBLE',
            'POSSIBLE_ELIGIBLE': 'POSSIBLE_ELIGIBLE',
            'NOT_ELIGIBLE': 'NOT_ELIGIBLE',
            'UNCERTAIN': 'POSSIBLE_ELIGIBLE'
        }
        return mapping.get(status, 'NOT_ELIGIBLE')
    
    def _calculate_confidence(self, eval_data: Dict[str, Any]) -> str:
        """Calculate confidence level from evaluation data"""
        score = float(eval_data.get('eligibility_score', 0.0))
        status = eval_data.get('evaluation_status', '')
        
        if status == 'RULE_ELIGIBLE' and score >= 0.8:
            return 'HIGH'
        elif status in ['RULE_ELIGIBLE', 'POSSIBLE_ELIGIBLE'] and score >= 0.5:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _record_eligibility_check(
        self,
        family_id: Optional[str],
        beneficiary_id: Optional[str],
        session_id: str,
        user_type: str,
        check_type: str,
        check_mode: str,
        questionnaire_responses: Optional[Dict[str, Any]],
        total_schemes_checked: int,
        eligible_count: int,
        possible_eligible_count: int,
        not_eligible_count: int,
        processing_time_ms: int
    ) -> int:
        """Record eligibility check in database"""
        conn = self.db.connection
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO eligibility_checker.eligibility_checks (
                    family_id, beneficiary_id, session_id, user_type,
                    check_type, check_mode, questionnaire_responses,
                    total_schemes_checked, eligible_count, possible_eligible_count,
                    not_eligible_count, processing_time_ms, data_sources_used,
                    consent_given
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING check_id
            """, (
                family_id, beneficiary_id, session_id, user_type,
                check_type, check_mode,
                json.dumps(questionnaire_responses) if questionnaire_responses else None,
                total_schemes_checked, eligible_count, possible_eligible_count,
                not_eligible_count, processing_time_ms,
                ['eligibility_engine'] if user_type == 'LOGGED_IN' else ['questionnaire'],
                user_type == 'LOGGED_IN'  # Assume logged-in users have given consent
            ))
            
            check_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            return check_id
        
        except Exception as e:
            print(f"⚠️  Error recording eligibility check: {e}")
            conn.rollback()
            cursor.close()
            return 0
    
    def _record_scheme_result(self, check_id: int, eval_result: Dict[str, Any]):
        """Record individual scheme eligibility result"""
        conn = self.db.connection
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO eligibility_checker.scheme_eligibility_results (
                    check_id, scheme_code, scheme_name, eligibility_status,
                    eligibility_score, confidence_level, rule_evaluations,
                    met_rules, failed_rules, rule_path
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                check_id,
                eval_result.get('scheme_code'),
                eval_result.get('scheme_name'),
                eval_result.get('eligibility_status'),
                eval_result.get('eligibility_score'),
                eval_result.get('confidence_level'),
                json.dumps(eval_result.get('rule_evaluations', {})),
                eval_result.get('met_rules', []),
                eval_result.get('failed_rules', []),
                eval_result.get('rule_path', '')
            ))
            
            conn.commit()
            cursor.close()
        
        except Exception as e:
            print(f"⚠️  Error recording scheme result: {e}")
            conn.rollback()
            cursor.close()

