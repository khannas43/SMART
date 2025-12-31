"""
Rule-Based Detector
Performs rule-based mis-targeting checks for existing beneficiaries
Use Case ID: AI-PLATFORM-07
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import sys
from pathlib import Path
import json
import yaml

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class RuleDetector:
    """Rule-based detection engine for re-checking beneficiary eligibility"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Rule Detector"""
        if config_path is None:
            base_dir = Path(__file__).parent.parent.parent
            config_path = base_dir / "config" / "db_config.yaml"
        
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
        
        # Load use case config
        use_case_config_path = Path(config_path).parent / "use_case_config.yaml"
        if use_case_config_path.exists():
            with open(use_case_config_path, 'r') as f:
                self.use_case_config = yaml.safe_load(f)
        else:
            self.use_case_config = {}
    
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
    
    def detect_ineligibility(
        self,
        beneficiary_id: str,
        family_id: str,
        scheme_code: str,
        current_benefit_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform rule-based detection for a beneficiary
        
        Args:
            beneficiary_id: Beneficiary identifier (Jan Aadhaar/GR ID)
            family_id: Family ID
            scheme_code: Scheme code
            current_benefit_data: Current benefit information (optional)
        
        Returns:
            Detection results with all rule evaluations
        """
        detections = []
        critical_failures = []
        passed_count = 0
        failed_count = 0
        
        # 1. Eligibility Re-check
        eligibility_result = self._recheck_eligibility(beneficiary_id, family_id, scheme_code)
        detections.append(eligibility_result)
        if eligibility_result['passed']:
            passed_count += 1
        else:
            failed_count += 1
            if eligibility_result['severity'] == 'CRITICAL':
                critical_failures.append(eligibility_result['rule_name'])
        
        # 2. Overlap Check (mutually exclusive schemes)
        overlap_result = self._check_scheme_overlaps(beneficiary_id, family_id, scheme_code)
        detections.append(overlap_result)
        if overlap_result['passed']:
            passed_count += 1
        else:
            failed_count += 1
            if overlap_result['severity'] == 'CRITICAL':
                critical_failures.append(overlap_result['rule_name'])
        
        # 3. Duplicate Check
        duplicate_result = self._check_duplicates(beneficiary_id, family_id, scheme_code)
        detections.append(duplicate_result)
        if duplicate_result['passed']:
            passed_count += 1
        else:
            failed_count += 1
            if duplicate_result['severity'] == 'CRITICAL':
                critical_failures.append(duplicate_result['rule_name'])
        
        # 4. Status Change Check (deceased, migrated)
        status_result = self._check_status_changes(beneficiary_id, family_id)
        detections.append(status_result)
        if status_result['passed']:
            passed_count += 1
        else:
            failed_count += 1
            if status_result['severity'] == 'CRITICAL':
                critical_failures.append(status_result['rule_name'])
        
        # 5. Income/Asset Threshold Check
        income_result = self._check_income_threshold(beneficiary_id, family_id, scheme_code)
        detections.append(income_result)
        if income_result['passed']:
            passed_count += 1
        else:
            failed_count += 1
            if income_result['severity'] == 'CRITICAL':
                critical_failures.append(income_result['rule_name'])
        
        # 6. Family Limit Check (for schemes with family limits)
        family_limit_result = self._check_family_limits(family_id, scheme_code)
        detections.append(family_limit_result)
        if family_limit_result['passed']:
            passed_count += 1
        else:
            failed_count += 1
            if family_limit_result['severity'] == 'HIGH':
                critical_failures.append(family_limit_result['rule_name'])
        
        return {
            'all_passed': failed_count == 0,
            'passed_count': passed_count,
            'failed_count': failed_count,
            'critical_failures': critical_failures,
            'detections': detections,
            'detection_method': 'RULE_BASED',
            'detected_at': datetime.now().isoformat()
        }
    
    def _recheck_eligibility(
        self,
        beneficiary_id: str,
        family_id: str,
        scheme_code: str
    ) -> Dict[str, Any]:
        """Re-check eligibility with latest data"""
        conn = self.external_dbs['eligibility'].connection
        cursor = conn.cursor()
        
        try:
            # Get latest eligibility snapshot
            cursor.execute("""
                SELECT eligibility_status, eligibility_score, rule_evaluations
                FROM eligibility.eligibility_snapshots
                WHERE family_id = %s AND scheme_code = %s
                ORDER BY snapshot_date DESC
                LIMIT 1
            """, (family_id, scheme_code))
            
            result = cursor.fetchone()
            
            if not result:
                return {
                    'rule_category': 'ELIGIBILITY',
                    'rule_name': 'ELIGIBILITY_RECHECK',
                    'rule_description': 'Re-check eligibility status with latest data',
                    'rule_passed': False,
                    'rule_severity': 'HIGH',
                    'evaluation_result': 'No eligibility snapshot found',
                    'evaluation_details': {},
                    'change_detected': False
                }
            
            eligibility_status, eligibility_score, rule_evaluations = result
            threshold = self.use_case_config.get('rule_detection', {}).get('eligibility_failure_threshold', 0.5)
            
            passed = eligibility_status == 'ELIGIBLE' and (eligibility_score or 0) >= threshold
            
            return {
                'rule_category': 'ELIGIBILITY',
                'rule_name': 'ELIGIBILITY_RECHECK',
                'rule_description': 'Re-check eligibility status with latest data',
                'rule_passed': passed,
                'rule_severity': 'CRITICAL' if not passed else 'INFO',
                'evaluation_result': f'Eligibility status: {eligibility_status}, Score: {eligibility_score or 0:.2f}',
                'evaluation_details': {
                    'eligibility_status': eligibility_status,
                    'eligibility_score': float(eligibility_score) if eligibility_score else None,
                    'threshold': threshold,
                    'rule_evaluations': json.loads(rule_evaluations) if rule_evaluations else None
                },
                'previous_value': None,  # Would need to compare with previous snapshot
                'current_value': eligibility_status,
                'change_detected': False
            }
        except Exception as e:
            return {
                'rule_category': 'ELIGIBILITY',
                'rule_name': 'ELIGIBILITY_RECHECK',
                'rule_description': 'Re-check eligibility status with latest data',
                'rule_passed': False,
                'rule_severity': 'HIGH',
                'evaluation_result': f'Error checking eligibility: {str(e)}',
                'evaluation_details': {'error': str(e)},
                'change_detected': False
            }
        finally:
            cursor.close()
    
    def _check_scheme_overlaps(
        self,
        beneficiary_id: str,
        family_id: str,
        scheme_code: str
    ) -> Dict[str, Any]:
        """Check for mutually exclusive scheme overlaps"""
        conn = self.db.connection
        cursor = conn.cursor()
        
        try:
            # Get exclusion rules for this scheme
            cursor.execute("""
                SELECT scheme_code_2, exclusion_type, description
                FROM detection.scheme_exclusion_rules
                WHERE scheme_code_1 = %s AND is_active = TRUE
                UNION
                SELECT scheme_code_1, exclusion_type, description
                FROM detection.scheme_exclusion_rules
                WHERE scheme_code_2 = %s AND is_active = TRUE
            """, (scheme_code, scheme_code))
            
            exclusion_rules = cursor.fetchall()
            
            if not exclusion_rules:
                return {
                    'rule_category': 'OVERLAP',
                    'rule_name': 'SCHEME_OVERLAP_CHECK',
                    'rule_description': 'Check for mutually exclusive scheme overlaps',
                    'rule_passed': True,
                    'rule_severity': 'INFO',
                    'evaluation_result': 'No exclusion rules found for this scheme',
                    'evaluation_details': {},
                    'change_detected': False
                }
            
            # Check if beneficiary is enrolled in any excluded schemes
            # This would require querying beneficiary rosters from departments
            # For now, we'll check against profile_360 benefit_history
            gr_conn = self.external_dbs['profile_360'].connection
            gr_cursor = gr_conn.cursor()
            
            overlapping_schemes = []
            for excluded_scheme, exclusion_type, description in exclusion_rules:
                if exclusion_type == 'MUTUALLY_EXCLUSIVE':
                    # Check if beneficiary has benefits from excluded scheme
                    gr_cursor.execute("""
                        SELECT COUNT(*) 
                        FROM profile_360.benefit_history
                        WHERE beneficiary_id = %s 
                        AND scheme_code = %s
                        AND status = 'ACTIVE'
                    """, (beneficiary_id, excluded_scheme))
                    
                    count = gr_cursor.fetchone()[0]
                    if count > 0:
                        overlapping_schemes.append({
                            'scheme_code': excluded_scheme,
                            'exclusion_type': exclusion_type,
                            'description': description
                        })
            
            gr_cursor.close()
            
            passed = len(overlapping_schemes) == 0
            
            return {
                'rule_category': 'OVERLAP',
                'rule_name': 'SCHEME_OVERLAP_CHECK',
                'rule_description': 'Check for mutually exclusive scheme overlaps',
                'rule_passed': passed,
                'rule_severity': 'CRITICAL' if not passed else 'INFO',
                'evaluation_result': f'Found {len(overlapping_schemes)} overlapping mutually exclusive schemes' if not passed else 'No overlaps detected',
                'evaluation_details': {
                    'overlapping_schemes': overlapping_schemes,
                    'exclusion_rules_checked': len(exclusion_rules)
                },
                'previous_value': None,
                'current_value': f"{len(overlapping_schemes)} overlaps" if overlapping_schemes else 'None',
                'change_detected': False
            }
        except Exception as e:
            return {
                'rule_category': 'OVERLAP',
                'rule_name': 'SCHEME_OVERLAP_CHECK',
                'rule_description': 'Check for mutually exclusive scheme overlaps',
                'rule_passed': False,
                'rule_severity': 'HIGH',
                'evaluation_result': f'Error checking overlaps: {str(e)}',
                'evaluation_details': {'error': str(e)},
                'change_detected': False
            }
        finally:
            cursor.close()
    
    def _check_duplicates(
        self,
        beneficiary_id: str,
        family_id: str,
        scheme_code: str
    ) -> Dict[str, Any]:
        """Check for duplicate beneficiary identities"""
        gr_conn = self.external_dbs['golden_records'].connection
        cursor = gr_conn.cursor()
        
        try:
            # Check for duplicate GR IDs or Jan Aadhaar across multiple scheme enrollments
            # This is a simplified check - real implementation would check across all identifiers
            duplicate_indicators = []
            
            # Check if same beneficiary_id appears in multiple active benefits
            profile_conn = self.external_dbs['profile_360'].connection
            profile_cursor = profile_conn.cursor()
            
            profile_cursor.execute("""
                SELECT scheme_code, COUNT(*) as count
                FROM profile_360.benefit_history
                WHERE beneficiary_id = %s
                AND status = 'ACTIVE'
                GROUP BY scheme_code
                HAVING COUNT(*) > 1
            """, (beneficiary_id,))
            
            duplicates = profile_cursor.fetchall()
            
            if duplicates:
                for scheme, count in duplicates:
                    duplicate_indicators.append({
                        'type': 'DUPLICATE_ENROLLMENT',
                        'scheme_code': scheme,
                        'count': count,
                        'indicator': f'Beneficiary enrolled {count} times in {scheme}'
                    })
            
            profile_cursor.close()
            
            passed = len(duplicate_indicators) == 0
            
            return {
                'rule_category': 'DUPLICATE',
                'rule_name': 'DUPLICATE_CHECK',
                'rule_description': 'Check for duplicate beneficiary identities',
                'rule_passed': passed,
                'rule_severity': 'CRITICAL' if not passed else 'INFO',
                'evaluation_result': f'Found {len(duplicate_indicators)} duplicate indicators' if not passed else 'No duplicates detected',
                'evaluation_details': {
                    'duplicate_indicators': duplicate_indicators
                },
                'previous_value': None,
                'current_value': f"{len(duplicate_indicators)} duplicates" if duplicate_indicators else 'None',
                'change_detected': False
            }
        except Exception as e:
            return {
                'rule_category': 'DUPLICATE',
                'rule_name': 'DUPLICATE_CHECK',
                'rule_description': 'Check for duplicate beneficiary identities',
                'rule_passed': False,
                'rule_severity': 'HIGH',
                'evaluation_result': f'Error checking duplicates: {str(e)}',
                'evaluation_details': {'error': str(e)},
                'change_detected': False
            }
        finally:
            cursor.close()
    
    def _check_status_changes(
        self,
        beneficiary_id: str,
        family_id: str
    ) -> Dict[str, Any]:
        """Check for status changes (deceased, migrated)"""
        gr_conn = self.external_dbs['golden_records'].connection
        cursor = gr_conn.cursor()
        
        try:
            # Check for deceased flag
            cursor.execute("""
                SELECT is_deceased, is_migrated, migration_status
                FROM golden_records.family_members
                WHERE beneficiary_id = %s OR family_id = %s
                LIMIT 1
            """, (beneficiary_id, family_id))
            
            result = cursor.fetchone()
            
            if not result:
                return {
                    'rule_category': 'STATUS_CHANGE',
                    'rule_name': 'STATUS_CHANGE_CHECK',
                    'rule_description': 'Check for status changes (deceased, migrated)',
                    'rule_passed': True,
                    'rule_severity': 'INFO',
                    'evaluation_result': 'No status data found',
                    'evaluation_details': {},
                    'change_detected': False
                }
            
            is_deceased, is_migrated, migration_status = result
            status_issues = []
            
            if is_deceased:
                status_issues.append({
                    'type': 'DECEASED_FLAG',
                    'status': 'deceased',
                    'severity': 'CRITICAL'
                })
            
            if is_migrated:
                status_issues.append({
                    'type': 'MIGRATED',
                    'status': migration_status or 'migrated',
                    'severity': 'HIGH'
                })
            
            passed = len(status_issues) == 0
            
            return {
                'rule_category': 'STATUS_CHANGE',
                'rule_name': 'STATUS_CHANGE_CHECK',
                'rule_description': 'Check for status changes (deceased, migrated)',
                'rule_passed': passed,
                'rule_severity': 'CRITICAL' if any(issue['severity'] == 'CRITICAL' for issue in status_issues) else ('HIGH' if not passed else 'INFO'),
                'evaluation_result': f'Found {len(status_issues)} status issues: {[issue["type"] for issue in status_issues]}' if not passed else 'No status issues',
                'evaluation_details': {
                    'is_deceased': bool(is_deceased),
                    'is_migrated': bool(is_migrated),
                    'migration_status': migration_status,
                    'status_issues': status_issues
                },
                'previous_value': None,
                'current_value': 'deceased' if is_deceased else ('migrated' if is_migrated else 'active'),
                'change_detected': len(status_issues) > 0
            }
        except Exception as e:
            return {
                'rule_category': 'STATUS_CHANGE',
                'rule_name': 'STATUS_CHANGE_CHECK',
                'rule_description': 'Check for status changes (deceased, migrated)',
                'rule_passed': False,
                'rule_severity': 'HIGH',
                'evaluation_result': f'Error checking status: {str(e)}',
                'evaluation_details': {'error': str(e)},
                'change_detected': False
            }
        finally:
            cursor.close()
    
    def _check_income_threshold(
        self,
        beneficiary_id: str,
        family_id: str,
        scheme_code: str
    ) -> Dict[str, Any]:
        """Check if income/assets exceed scheme threshold"""
        gr_conn = self.external_dbs['golden_records'].connection
        cursor = gr_conn.cursor()
        
        try:
            # Get current income band from Golden Record or 360° Profile
            profile_conn = self.external_dbs['profile_360'].connection
            profile_cursor = profile_conn.cursor()
            
            profile_cursor.execute("""
                SELECT income_band, poverty_line_status
                FROM profile_360.family_profiles
                WHERE family_id = %s
                LIMIT 1
            """, (family_id,))
            
            result = profile_cursor.fetchone()
            profile_cursor.close()
            
            if not result:
                return {
                    'rule_category': 'ELIGIBILITY',
                    'rule_name': 'INCOME_THRESHOLD_CHECK',
                    'rule_description': 'Check if income/assets exceed scheme threshold',
                    'rule_passed': True,  # Pass if no data (uncertainty favors beneficiary)
                    'rule_severity': 'INFO',
                    'evaluation_result': 'No income data available for comparison',
                    'evaluation_details': {},
                    'change_detected': False
                }
            
            income_band, poverty_line_status = result
            
            # Get scheme eligibility rules for income threshold
            # This would typically come from eligibility rules
            # For now, we'll use a simple check
            passed = income_band in ['BELOW_POVERTY_LINE', 'VERY_LOW_INCOME'] or poverty_line_status == 'BELOW_POVERTY_LINE'
            
            return {
                'rule_category': 'ELIGIBILITY',
                'rule_name': 'INCOME_THRESHOLD_CHECK',
                'rule_description': 'Check if income/assets exceed scheme threshold',
                'rule_passed': passed,
                'rule_severity': 'CRITICAL' if not passed and income_band == 'ABOVE_POVERTY_LINE' else 'HIGH',
                'evaluation_result': f'Income band: {income_band}, Poverty line: {poverty_line_status}',
                'evaluation_details': {
                    'income_band': income_band,
                    'poverty_line_status': poverty_line_status
                },
                'previous_value': None,
                'current_value': income_band,
                'change_detected': False
            }
        except Exception as e:
            return {
                'rule_category': 'ELIGIBILITY',
                'rule_name': 'INCOME_THRESHOLD_CHECK',
                'rule_description': 'Check if income/assets exceed scheme threshold',
                'rule_passed': False,
                'rule_severity': 'HIGH',
                'evaluation_result': f'Error checking income: {str(e)}',
                'evaluation_details': {'error': str(e)},
                'change_detected': False
            }
        finally:
            cursor.close()
    
    def _check_family_limits(
        self,
        family_id: str,
        scheme_code: str
    ) -> Dict[str, Any]:
        """Check if family exceeds scheme beneficiary limits"""
        conn = self.db.connection
        cursor = conn.cursor()
        
        try:
            # Get family limit rule for this scheme
            cursor.execute("""
                SELECT max_beneficiaries_per_family
                FROM detection.scheme_exclusion_rules
                WHERE (scheme_code_1 = %s OR scheme_code_2 = %s)
                AND max_beneficiaries_per_family IS NOT NULL
                AND is_active = TRUE
                LIMIT 1
            """, (scheme_code, scheme_code))
            
            result = cursor.fetchone()
            
            if not result or not result[0]:
                return {
                    'rule_category': 'OVERLAP',
                    'rule_name': 'FAMILY_LIMIT_CHECK',
                    'rule_description': 'Check if family exceeds scheme beneficiary limits',
                    'rule_passed': True,
                    'rule_severity': 'INFO',
                    'evaluation_result': 'No family limit rules for this scheme',
                    'evaluation_details': {},
                    'change_detected': False
                }
            
            max_beneficiaries = result[0]
            
            # Count current beneficiaries from this family in this scheme
            profile_conn = self.external_dbs['profile_360'].connection
            profile_cursor = profile_conn.cursor()
            
            profile_cursor.execute("""
                SELECT COUNT(DISTINCT beneficiary_id)
                FROM profile_360.benefit_history
                WHERE family_id = %s
                AND scheme_code = %s
                AND status = 'ACTIVE'
            """, (family_id, scheme_code))
            
            current_count = profile_cursor.fetchone()[0] or 0
            profile_cursor.close()
            
            passed = current_count <= max_beneficiaries
            
            return {
                'rule_category': 'OVERLAP',
                'rule_name': 'FAMILY_LIMIT_CHECK',
                'rule_description': 'Check if family exceeds scheme beneficiary limits',
                'rule_passed': passed,
                'rule_severity': 'HIGH' if not passed else 'INFO',
                'evaluation_result': f'Family has {current_count} beneficiaries, limit is {max_beneficiaries}',
                'evaluation_details': {
                    'current_count': current_count,
                    'max_allowed': max_beneficiaries,
                    'exceeds_limit': not passed
                },
                'previous_value': None,
                'current_value': f"{current_count}/{max_beneficiaries}",
                'change_detected': False
            }
        except Exception as e:
            return {
                'rule_category': 'OVERLAP',
                'rule_name': 'FAMILY_LIMIT_CHECK',
                'rule_description': 'Check if family exceeds scheme beneficiary limits',
                'rule_passed': False,
                'rule_severity': 'HIGH',
                'evaluation_result': f'Error checking family limits: {str(e)}',
                'evaluation_details': {'error': str(e)},
                'change_detected': False
            }
        finally:
            cursor.close()
    
    def save_rule_detections(
        self,
        case_id: int,
        detections: List[Dict[str, Any]]
    ):
        """Save rule detection results to database"""
        conn = self.db.connection
        cursor = conn.cursor()
        
        try:
            for detection in detections:
                cursor.execute("""
                    INSERT INTO detection.rule_detections (
                        case_id, rule_category, rule_name, rule_description,
                        rule_passed, rule_severity, evaluation_result,
                        evaluation_details, previous_value, current_value,
                        change_detected, evidence_sources, evidence_data
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    case_id,
                    detection['rule_category'],
                    detection['rule_name'],
                    detection['rule_description'],
                    detection['rule_passed'],
                    detection['rule_severity'],
                    detection['evaluation_result'],
                    json.dumps(detection['evaluation_details']),
                    detection.get('previous_value'),
                    detection.get('current_value'),
                    detection.get('change_detected', False),
                    detection.get('evidence_sources', []),
                    json.dumps(detection.get('evidence_data', {}))
                ))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise Exception(f"Failed to save rule detections: {str(e)}")
        finally:
            cursor.close()

