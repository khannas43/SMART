"""
Detection Orchestrator
Main orchestrator for beneficiary detection runs
Use Case ID: AI-PLATFORM-07
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import sys
from pathlib import Path
import yaml
import json
import uuid

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector

# Import detectors
sys.path.append(str(Path(__file__).parent.parent))
from detectors.rule_detector import RuleDetector
from detectors.case_classifier import CaseClassifier
from models.anomaly_detector import AnomalyDetector
from services.prioritizer import Prioritizer


class DetectionOrchestrator:
    """Main orchestrator for beneficiary detection workflow"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Detection Orchestrator"""
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
        
        # Initialize sub-components
        self.rule_detector = RuleDetector(config_path)
        self.ml_detector = AnomalyDetector(config_path)
        self.case_classifier = CaseClassifier()
        self.prioritizer = Prioritizer()
        
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
        self.rule_detector.connect()
        self.ml_detector.connect()
    
    def disconnect(self):
        """Disconnect from all databases"""
        self.rule_detector.disconnect()
        self.ml_detector.disconnect()
        self.db.disconnect()
    
    def run_detection(
        self,
        run_type: str = 'FULL',
        scheme_codes: Optional[List[str]] = None,
        beneficiary_ids: Optional[List[str]] = None,
        started_by: str = 'system'
    ) -> Dict[str, Any]:
        """
        Run beneficiary detection
        
        Args:
            run_type: 'FULL', 'INCREMENTAL', 'SCHEME_SPECIFIC', 'PRIORITY_BATCH'
            scheme_codes: List of scheme codes to process (None = all)
            beneficiary_ids: List of specific beneficiary IDs (None = all active)
            started_by: User/system that started the run
        
        Returns:
            Detection run results
        """
        # Create detection run record
        run_id = self._create_detection_run(run_type, scheme_codes, started_by)
        
        try:
            # Get beneficiaries to check
            beneficiaries = self._get_beneficiaries_to_check(scheme_codes, beneficiary_ids)
            
            flagged_cases = []
            processed_count = 0
            
            # Process each beneficiary
            for beneficiary in beneficiaries:
                try:
                    result = self.detect_beneficiary(
                        beneficiary_id=beneficiary['beneficiary_id'],
                        family_id=beneficiary['family_id'],
                        scheme_code=beneficiary['scheme_code'],
                        current_benefit_data=beneficiary.get('benefit_data')
                    )
                    
                    if result and result.get('case_id'):
                        flagged_cases.append(result['case_id'])
                    
                    processed_count += 1
                    
                    # Update progress periodically
                    if processed_count % 100 == 0:
                        self._update_run_progress(run_id, processed_count, len(flagged_cases))
                
                except Exception as e:
                    print(f"Error processing beneficiary {beneficiary['beneficiary_id']}: {str(e)}")
                    continue
            
            # Complete run
            self._complete_detection_run(run_id, processed_count, len(flagged_cases))
            
            return {
                'run_id': run_id,
                'status': 'COMPLETED',
                'total_processed': processed_count,
                'cases_flagged': len(flagged_cases),
                'flagged_case_ids': flagged_cases
            }
        
        except Exception as e:
            self._fail_detection_run(run_id, str(e))
            raise
    
    def detect_beneficiary(
        self,
        beneficiary_id: str,
        family_id: str,
        scheme_code: str,
        current_benefit_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Detect ineligibility/mis-targeting for a single beneficiary
        
        Args:
            beneficiary_id: Beneficiary identifier
            family_id: Family ID
            scheme_code: Scheme code
            current_benefit_data: Current benefit information
        
        Returns:
            Detection result with case_id if flagged, None otherwise
        """
        # 1. Rule-based detection
        rule_results = self.rule_detector.detect_ineligibility(
            beneficiary_id, family_id, scheme_code, current_benefit_data
        )
        
        # 2. ML anomaly detection (if enabled)
        ml_results = None
        if self.use_case_config.get('detection', {}).get('enable_ml_anomaly_detection', True):
            try:
                ml_results = self.ml_detector.detect_anomalies(
                    beneficiary_id, family_id, scheme_code, current_benefit_data
                )
            except Exception as e:
                print(f"ML detection failed: {str(e)}")
                ml_results = None
        
        # 3. Classify case
        classification = self.case_classifier.classify_case(rule_results, ml_results)
        
        # 4. Only create case if flagged (not all rules passed or ML detected anomaly)
        if rule_results.get('all_passed') and (not ml_results or ml_results.get('anomaly_score', 0) < 0.6):
            return None  # Not flagged
        
        # 5. Get beneficiary data for prioritization
        beneficiary_data = self._get_beneficiary_data(beneficiary_id, family_id, scheme_code)
        
        # 6. Prioritize case
        prioritization = self.prioritizer.prioritize_case(
            beneficiary_data, rule_results, ml_results
        )
        
        # 7. Calculate financial exposure and vulnerability
        financial_exposure = prioritization['financial_exposure']
        vulnerability_score = prioritization['vulnerability_score']
        
        # 8. Create detected case record
        case_id = self._create_detected_case(
            beneficiary_id=beneficiary_id,
            family_id=family_id,
            scheme_code=scheme_code,
            case_type=classification['case_type'],
            confidence_level=classification['confidence_level'],
            detection_rationale=classification['detection_rationale'],
            rule_results=rule_results,
            ml_results=ml_results,
            prioritization=prioritization,
            financial_exposure=financial_exposure,
            vulnerability_score=vulnerability_score,
            current_benefit_data=current_benefit_data
        )
        
        # 9. Save rule detections
        if rule_results.get('detections'):
            self.rule_detector.save_rule_detections(case_id, rule_results['detections'])
        
        # 10. Save ML detection
        if ml_results:
            self.ml_detector.save_ml_detection(case_id, ml_results)
        
        # 11. Create eligibility snapshot
        self._create_eligibility_snapshot(beneficiary_id, family_id, scheme_code)
        
        return {
            'case_id': case_id,
            'beneficiary_id': beneficiary_id,
            'scheme_code': scheme_code,
            'case_type': classification['case_type'],
            'confidence_level': classification['confidence_level'],
            'priority': prioritization['priority_level']
        }
    
    def _create_detection_run(
        self,
        run_type: str,
        scheme_codes: Optional[List[str]],
        started_by: str
    ) -> int:
        """Create detection run record"""
        conn = self.db.connection
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO detection.detection_runs (
                    run_type, run_status, schemes_processed, started_by
                ) VALUES (%s, %s, %s, %s)
                RETURNING run_id
            """, (run_type, 'RUNNING', scheme_codes, started_by))
            
            run_id = cursor.fetchone()[0]
            conn.commit()
            return run_id
        except Exception as e:
            conn.rollback()
            raise Exception(f"Failed to create detection run: {str(e)}")
        finally:
            cursor.close()
    
    def _get_beneficiaries_to_check(
        self,
        scheme_codes: Optional[List[str]],
        beneficiary_ids: Optional[List[str]]
    ) -> List[Dict[str, Any]]:
        """Get list of beneficiaries to check"""
        profile_conn = self.rule_detector.external_dbs['profile_360'].connection
        cursor = profile_conn.cursor()
        
        try:
            if beneficiary_ids:
                # Specific beneficiaries
                query = """
                    SELECT DISTINCT beneficiary_id, family_id, scheme_code
                    FROM profile_360.benefit_history
                    WHERE beneficiary_id = ANY(%s) AND status = 'ACTIVE'
                """
                cursor.execute(query, (beneficiary_ids,))
            elif scheme_codes:
                # Specific schemes
                query = """
                    SELECT DISTINCT beneficiary_id, family_id, scheme_code
                    FROM profile_360.benefit_history
                    WHERE scheme_code = ANY(%s) AND status = 'ACTIVE'
                """
                cursor.execute(query, (scheme_codes,))
            else:
                # All active beneficiaries
                query = """
                    SELECT DISTINCT beneficiary_id, family_id, scheme_code
                    FROM profile_360.benefit_history
                    WHERE status = 'ACTIVE'
                """
                cursor.execute(query)
            
            results = cursor.fetchall()
            beneficiaries = []
            for row in results:
                beneficiaries.append({
                    'beneficiary_id': row[0],
                    'family_id': row[1],
                    'scheme_code': row[2]
                })
            
            return beneficiaries
        finally:
            cursor.close()
    
    def _get_beneficiary_data(
        self,
        beneficiary_id: str,
        family_id: str,
        scheme_code: str
    ) -> Dict[str, Any]:
        """Get beneficiary data for prioritization"""
        # Get from profile_360
        profile_conn = self.rule_detector.external_dbs['profile_360'].connection
        cursor = profile_conn.cursor()
        
        try:
            cursor.execute("""
                SELECT benefit_amount, benefit_frequency
                FROM profile_360.benefit_history
                WHERE beneficiary_id = %s AND scheme_code = %s AND status = 'ACTIVE'
                LIMIT 1
            """, (beneficiary_id, scheme_code))
            
            result = cursor.fetchone()
            if result:
                return {
                    'current_benefits': {
                        'benefit_amount': float(result[0] or 0),
                        'frequency': result[1]
                    },
                    'income_band': 'MIDDLE_INCOME',  # Would come from profile
                    'age': 0,  # Would come from GR
                    'family_size': 0  # Would come from GR
                }
            else:
                return {}
        finally:
            cursor.close()
    
    def _create_detected_case(
        self,
        beneficiary_id: str,
        family_id: str,
        scheme_code: str,
        case_type: str,
        confidence_level: str,
        detection_rationale: str,
        rule_results: Dict[str, Any],
        ml_results: Optional[Dict[str, Any]],
        prioritization: Dict[str, Any],
        financial_exposure: float,
        vulnerability_score: float,
        current_benefit_data: Optional[Dict[str, Any]]
    ) -> int:
        """Create detected case record"""
        conn = self.db.connection
        cursor = conn.cursor()
        
        try:
            # Get eligibility status
            eligibility_status = 'INELIGIBLE' if not rule_results.get('all_passed') else 'ELIGIBLE'
            eligibility_score = None
            if rule_results.get('detections'):
                for det in rule_results['detections']:
                    if det['rule_category'] == 'ELIGIBILITY':
                        eligibility_score = det.get('evaluation_details', {}).get('eligibility_score')
                        break
            
            # Get risk score
            risk_score = ml_results.get('risk_score') if ml_results else None
            
            cursor.execute("""
                INSERT INTO detection.detected_cases (
                    beneficiary_id, family_id, scheme_code,
                    case_type, confidence_level,
                    detection_method, risk_score, financial_exposure, vulnerability_score,
                    current_eligibility_status, eligibility_score,
                    detection_rationale,
                    rule_evaluations, ml_explanations,
                    current_benefits, cross_scheme_overlaps,
                    recommended_action, action_urgency,
                    case_status, priority
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING case_id
            """, (
                beneficiary_id,
                family_id,
                scheme_code,
                case_type,
                confidence_level,
                'HYBRID' if ml_results else 'RULE_BASED',
                risk_score,
                financial_exposure,
                vulnerability_score,
                eligibility_status,
                eligibility_score,
                detection_rationale,
                json.dumps(rule_results),
                json.dumps(ml_results) if ml_results else None,
                json.dumps(current_benefit_data) if current_benefit_data else None,
                json.dumps({}),  # cross_scheme_overlaps
                prioritization.get('recommended_action'),
                prioritization.get('action_urgency'),
                'FLAGGED',
                prioritization['priority_level']
            ))
            
            case_id = cursor.fetchone()[0]
            conn.commit()
            return case_id
        except Exception as e:
            conn.rollback()
            raise Exception(f"Failed to create detected case: {str(e)}")
        finally:
            cursor.close()
    
    def _create_eligibility_snapshot(
        self,
        beneficiary_id: str,
        family_id: str,
        scheme_code: str
    ):
        """Create eligibility snapshot for comparison"""
        conn = self.db.connection
        cursor = conn.cursor()
        
        try:
            # Get eligibility data
            eligibility_conn = self.rule_detector.external_dbs['eligibility'].connection
            elig_cursor = eligibility_conn.cursor()
            
            elig_cursor.execute("""
                SELECT eligibility_status, eligibility_score, rule_evaluations
                FROM eligibility.eligibility_snapshots
                WHERE family_id = %s AND scheme_code = %s
                ORDER BY snapshot_date DESC
                LIMIT 1
            """, (family_id, scheme_code))
            
            elig_result = elig_cursor.fetchone()
            elig_cursor.close()
            
            if elig_result:
                cursor.execute("""
                    INSERT INTO detection.eligibility_snapshots (
                        beneficiary_id, family_id, scheme_code,
                        snapshot_type, trigger_reason,
                        eligibility_status, eligibility_score, eligibility_rules_evaluated
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    beneficiary_id, family_id, scheme_code,
                    'RE_SCORE', 'Periodic re-scoring',
                    elig_result[0], elig_result[1], elig_result[2]
                ))
                
                conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Warning: Failed to create eligibility snapshot: {str(e)}")
        finally:
            cursor.close()
    
    def _update_run_progress(self, run_id: int, processed: int, flagged: int):
        """Update detection run progress"""
        conn = self.db.connection
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE detection.detection_runs
                SET total_beneficiaries_scanned = %s,
                    total_cases_flagged = %s
                WHERE run_id = %s
            """, (processed, flagged, run_id))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Warning: Failed to update run progress: {str(e)}")
        finally:
            cursor.close()
    
    def _complete_detection_run(self, run_id: int, processed: int, flagged: int):
        """Complete detection run"""
        conn = self.db.connection
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE detection.detection_runs
                SET run_status = 'COMPLETED',
                    total_beneficiaries_scanned = %s,
                    total_cases_flagged = %s,
                    completed_at = CURRENT_TIMESTAMP
                WHERE run_id = %s
            """, (processed, flagged, run_id))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise Exception(f"Failed to complete detection run: {str(e)}")
        finally:
            cursor.close()
    
    def _fail_detection_run(self, run_id: int, error_message: str):
        """Mark detection run as failed"""
        conn = self.db.connection
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE detection.detection_runs
                SET run_status = 'FAILED',
                    error_message = %s,
                    completed_at = CURRENT_TIMESTAMP
                WHERE run_id = %s
            """, (error_message, run_id))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Warning: Failed to mark run as failed: {str(e)}")
        finally:
            cursor.close()

