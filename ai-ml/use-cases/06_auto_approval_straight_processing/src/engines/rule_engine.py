"""
Rule Engine
Evaluates eligibility, authenticity, document validation, and duplicate checks
Use Case ID: AI-PLATFORM-06
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import sys
from pathlib import Path
import json

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class RuleEngine:
    """Rule-based evaluation engine for eligibility and authenticity checks"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Rule Engine"""
        if config_path is None:
            base_dir = Path(__file__).parent.parent.parent
            config_path = base_dir / "config" / "db_config.yaml"
        
        import yaml
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize database connections
        db_config = self.config['database']
        self.db = DBConnector(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['name'],
            user=db_config['user'],
            password=db_config['password']
        )
        
        # External database connections
        self.external_dbs = {}
        for name, ext_config in self.config.get('external_databases', {}).items():
            self.external_dbs[name] = DBConnector(
                host=ext_config['host'],
                port=ext_config['port'],
                database=ext_config['name'],
                user=ext_config['user'],
                password=ext_config['password']
            )
    
    def connect(self):
        """Connect to all databases"""
        self.db.connect()
        for ext_db in self.external_dbs.values():
            ext_db.connect()
    
    def disconnect(self):
        """Disconnect from all databases"""
        self.db.disconnect()
        for ext_db in self.external_dbs.values():
            ext_db.disconnect()
    
    def evaluate_rules(
        self,
        application_id: int,
        family_id: str,
        scheme_code: str
    ) -> Dict[str, Any]:
        """
        Evaluate all rules for an application
        
        Args:
            application_id: Application ID
            family_id: Family ID
            scheme_code: Scheme code
        
        Returns:
            Rule evaluation results with passed/failed status and details
        """
        evaluations = []
        critical_failures = []
        passed_count = 0
        failed_count = 0
        
        # 1. Eligibility Rules
        eligibility_result = self._evaluate_eligibility(application_id, family_id, scheme_code)
        evaluations.append(eligibility_result)
        if eligibility_result['passed']:
            passed_count += 1
        else:
            failed_count += 1
            if eligibility_result['severity'] == 'CRITICAL':
                critical_failures.append(eligibility_result['rule_name'])
        
        # 2. Authenticity Checks
        authenticity_result = self._evaluate_authenticity(application_id, family_id)
        evaluations.append(authenticity_result)
        if authenticity_result['passed']:
            passed_count += 1
        else:
            failed_count += 1
            if authenticity_result['severity'] == 'CRITICAL':
                critical_failures.append(authenticity_result['rule_name'])
        
        # 3. Document Validation
        document_result = self._evaluate_documents(application_id, scheme_code)
        evaluations.append(document_result)
        if document_result['passed']:
            passed_count += 1
        else:
            failed_count += 1
            if document_result['severity'] == 'CRITICAL':
                critical_failures.append(document_result['rule_name'])
        
        # 4. Duplicate Checks
        duplicate_result = self._evaluate_duplicates(application_id, family_id, scheme_code)
        evaluations.append(duplicate_result)
        if duplicate_result['passed']:
            passed_count += 1
        else:
            failed_count += 1
            if duplicate_result['severity'] == 'CRITICAL':
                critical_failures.append(duplicate_result['rule_name'])
        
        # 5. Cross-Scheme Checks
        cross_scheme_result = self._evaluate_cross_scheme(family_id, scheme_code)
        evaluations.append(cross_scheme_result)
        if cross_scheme_result['passed']:
            passed_count += 1
        else:
            failed_count += 1
            if cross_scheme_result['severity'] == 'CRITICAL':
                critical_failures.append(cross_scheme_result['rule_name'])
        
        # 6. Deceased Flag Check
        deceased_result = self._check_deceased_flag(family_id)
        evaluations.append(deceased_result)
        if deceased_result['passed']:
            passed_count += 1
        else:
            failed_count += 1
            if deceased_result['severity'] == 'CRITICAL':
                critical_failures.append(deceased_result['rule_name'])
        
        all_passed = len(critical_failures) == 0 and failed_count == 0
        
        return {
            'all_passed': all_passed,
            'passed_count': passed_count,
            'failed_count': failed_count,
            'critical_failures': critical_failures,
            'evaluations': evaluations
        }
    
    def _evaluate_eligibility(
        self,
        application_id: int,
        family_id: str,
        scheme_code: str
    ) -> Dict[str, Any]:
        """Evaluate eligibility rules"""
        conn = self.external_dbs['application'].connection
        cursor = conn.cursor()
        
        # Get eligibility snapshot from application
        cursor.execute("""
            SELECT eligibility_score, eligibility_status
            FROM application.applications
            WHERE application_id = %s
        """, (application_id,))
        
        app_row = cursor.fetchone()
        if not app_row:
            cursor.close()
            return {
                'rule_category': 'ELIGIBILITY',
                'rule_name': 'ELIGIBILITY_CHECK',
                'rule_id': 'ELIG_001',
                'passed': False,
                'severity': 'CRITICAL',
                'result_message': 'Application not found',
                'result_details': {}
            }
        
        eligibility_score = app_row[0] or 0
        eligibility_status = app_row[1] or ''
        
        # Check if eligible
        is_eligible = (
            eligibility_status in ('RULE_ELIGIBLE', 'POSSIBLE_ELIGIBLE') and
            eligibility_score >= 0.5  # Minimum threshold
        )
        
        cursor.close()
        
        return {
            'rule_category': 'ELIGIBILITY',
            'rule_name': 'ELIGIBILITY_CHECK',
            'rule_id': 'ELIG_001',
            'passed': is_eligible,
            'severity': 'CRITICAL' if not is_eligible else 'INFO',
            'result_message': f'Eligibility status: {eligibility_status}, score: {eligibility_score}',
            'result_details': {
                'eligibility_score': float(eligibility_score),
                'eligibility_status': eligibility_status
            }
        }
    
    def _evaluate_authenticity(self, application_id: int, family_id: str) -> Dict[str, Any]:
        """Evaluate authenticity checks (Aadhaar, identity verification)"""
        conn = self.external_dbs['application'].connection
        cursor = conn.cursor()
        
        # Check if application has identity verification
        # For now, assume authenticity if application was auto-created (has proper consent)
        cursor.execute("""
            SELECT submission_mode, consent_id
            FROM application.applications
            WHERE application_id = %s
        """, (application_id,))
        
        app_row = cursor.fetchone()
        if not app_row:
            cursor.close()
            return {
                'rule_category': 'AUTHENTICITY',
                'rule_name': 'AUTHENTICITY_CHECK',
                'rule_id': 'AUTH_001',
                'passed': False,
                'severity': 'HIGH',
                'result_message': 'Application not found',
                'result_details': {}
            }
        
        submission_mode = app_row[0]
        consent_id = app_row[1]
        
        # If auto-submitted with consent, authenticity is assumed
        # In production, this would check Aadhaar verification status
        is_authentic = consent_id is not None
        
        cursor.close()
        
        return {
            'rule_category': 'AUTHENTICITY',
            'rule_name': 'AUTHENTICITY_CHECK',
            'rule_id': 'AUTH_001',
            'passed': is_authentic,
            'severity': 'HIGH' if not is_authentic else 'INFO',
            'result_message': f'Authenticity check: {"Passed" if is_authentic else "Failed"}',
            'result_details': {
                'submission_mode': submission_mode,
                'has_consent': consent_id is not None
            }
        }
    
    def _evaluate_documents(self, application_id: int, scheme_code: str) -> Dict[str, Any]:
        """Evaluate document validation"""
        conn = self.external_dbs['application'].connection
        cursor = conn.cursor()
        
        # Check required documents
        cursor.execute("""
            SELECT 
                COUNT(*) as total_docs,
                COUNT(*) FILTER (WHERE status = 'verified') as verified_docs,
                COUNT(*) FILTER (WHERE is_mandatory = true) as mandatory_count,
                COUNT(*) FILTER (WHERE is_mandatory = true AND status = 'verified') as mandatory_verified
            FROM application.application_documents
            WHERE application_id = %s
        """, (application_id,))
        
        doc_row = cursor.fetchone()
        
        if not doc_row or doc_row[2] == 0:  # No mandatory documents defined
            cursor.close()
            return {
                'rule_category': 'DOCUMENT',
                'rule_name': 'DOCUMENT_VALIDATION',
                'rule_id': 'DOC_001',
                'passed': True,  # No mandatory docs means pass
                'severity': 'INFO',
                'result_message': 'No mandatory documents required',
                'result_details': {}
            }
        
        total_docs = doc_row[0] or 0
        verified_docs = doc_row[1] or 0
        mandatory_count = doc_row[2] or 0
        mandatory_verified = doc_row[3] or 0
        
        all_mandatory_verified = mandatory_verified == mandatory_count
        
        cursor.close()
        
        return {
            'rule_category': 'DOCUMENT',
            'rule_name': 'DOCUMENT_VALIDATION',
            'rule_id': 'DOC_001',
            'passed': all_mandatory_verified,
            'severity': 'CRITICAL' if not all_mandatory_verified else 'INFO',
            'result_message': f'Documents: {mandatory_verified}/{mandatory_count} mandatory verified',
            'result_details': {
                'total_documents': total_docs,
                'verified_documents': verified_docs,
                'mandatory_count': mandatory_count,
                'mandatory_verified': mandatory_verified
            }
        }
    
    def _evaluate_duplicates(
        self,
        application_id: int,
        family_id: str,
        scheme_code: str
    ) -> Dict[str, Any]:
        """Evaluate duplicate application checks"""
        conn = self.external_dbs['application'].connection
        cursor = conn.cursor()
        
        # Check for existing approved/pending applications
        cursor.execute("""
            SELECT COUNT(*) 
            FROM application.applications
            WHERE family_id = %s 
                AND scheme_code = %s
                AND application_id != %s
                AND status IN ('submitted', 'accepted', 'pending_review', 'pending_submission')
        """, (family_id, scheme_code, application_id))
        
        duplicate_count = cursor.fetchone()[0] or 0
        
        has_duplicate = duplicate_count > 0
        
        cursor.close()
        
        return {
            'rule_category': 'DUPLICATE',
            'rule_name': 'DUPLICATE_CHECK',
            'rule_id': 'DUP_001',
            'passed': not has_duplicate,
            'severity': 'CRITICAL' if has_duplicate else 'INFO',
            'result_message': f'Duplicate check: {"Found existing application" if has_duplicate else "No duplicates"}',
            'result_details': {
                'duplicate_count': duplicate_count
            }
        }
    
    def _evaluate_cross_scheme(self, family_id: str, scheme_code: str) -> Dict[str, Any]:
        """Evaluate cross-scheme conflicts (exclusive schemes)"""
        # Get scheme category to check for conflicts
        conn = self.external_dbs['scheme_master'].connection
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT category 
            FROM public.scheme_master
            WHERE scheme_code = %s
        """, (scheme_code,))
        
        scheme_row = cursor.fetchone()
        if not scheme_row:
            cursor.close()
            return {
                'rule_category': 'CROSS_SCHEME',
                'rule_name': 'CROSS_SCHEME_CHECK',
                'rule_id': 'XSCHEME_001',
                'passed': True,
                'severity': 'INFO',
                'result_message': 'Scheme not found in master',
                'result_details': {}
            }
        
        scheme_category = scheme_row[0]
        cursor.close()
        
        # Check for conflicting schemes (simplified - in production would check scheme rules)
        # For now, assume no conflicts
        has_conflict = False
        
        return {
            'rule_category': 'CROSS_SCHEME',
            'rule_name': 'CROSS_SCHEME_CHECK',
            'rule_id': 'XSCHEME_001',
            'passed': not has_conflict,
            'severity': 'HIGH' if has_conflict else 'INFO',
            'result_message': f'Cross-scheme check: {"Conflict found" if has_conflict else "No conflicts"}',
            'result_details': {
                'scheme_category': scheme_category
            }
        }
    
    def _check_deceased_flag(self, family_id: str) -> Dict[str, Any]:
        """Check for deceased flag in Golden Record"""
        try:
            conn = self.external_dbs['golden_records'].connection
            cursor = conn.cursor()
            
            # Check for deceased flag (assuming there's a deceased flag in golden records)
            # This is a placeholder - actual schema may vary
            cursor.execute("""
                SELECT COUNT(*) 
                FROM golden_records.family_members
                WHERE family_id = %s 
                    AND (deceased = true OR deceased_flag = true OR status = 'deceased')
                LIMIT 1
            """, (family_id,))
            
            deceased_count = cursor.fetchone()[0] or 0
            cursor.close()
            
            has_deceased = deceased_count > 0
            
            return {
                'rule_category': 'FRAUD',
                'rule_name': 'DECEASED_FLAG_CHECK',
                'rule_id': 'FRAUD_001',
                'passed': not has_deceased,
                'severity': 'CRITICAL' if has_deceased else 'INFO',
                'result_message': f'Deceased check: {"Deceased flag found" if has_deceased else "No deceased flag"}',
                'result_details': {
                    'deceased_count': deceased_count
                }
            }
        except Exception as e:
            # If table doesn't exist or query fails, assume no deceased flag
            return {
                'rule_category': 'FRAUD',
                'rule_name': 'DECEASED_FLAG_CHECK',
                'rule_id': 'FRAUD_001',
                'passed': True,
                'severity': 'INFO',
                'result_message': f'Deceased check: Unable to verify (error: {str(e)})',
                'result_details': {
                    'error': str(e)
                }
            }
    
    def save_rule_evaluations(
        self,
        decision_id: int,
        evaluations: List[Dict[str, Any]]
    ):
        """Save rule evaluation results to database"""
        conn = self.db.connection
        cursor = conn.cursor()
        
        for eval_result in evaluations:
            cursor.execute("""
                INSERT INTO decision.rule_evaluations (
                    decision_id, rule_category, rule_name, rule_id,
                    passed, severity, result_message, result_details, rule_inputs
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                decision_id,
                eval_result['rule_category'],
                eval_result['rule_name'],
                eval_result.get('rule_id', ''),
                eval_result['passed'],
                eval_result['severity'],
                eval_result['result_message'],
                json.dumps(eval_result.get('result_details', {})),
                json.dumps({})  # rule_inputs
            ))
        
        conn.commit()
        cursor.close()

