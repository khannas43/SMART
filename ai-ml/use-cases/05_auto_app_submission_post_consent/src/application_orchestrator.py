"""
Application Orchestrator
Main orchestrator for creating and submitting applications post-consent
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import sys
from pathlib import Path
import yaml

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class ApplicationOrchestrator:
    """Main orchestrator for application creation and submission workflow"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Application Orchestrator"""
        if config_path is None:
            base_dir = Path(__file__).parent.parent
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
    
    def trigger_on_consent(
        self,
        family_id: str,
        scheme_code: str,
        consent_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Trigger application creation when consent is given
        
        Args:
            family_id: Family ID
            scheme_code: Scheme code
            consent_id: Consent record ID (optional)
        
        Returns:
            Application creation result
        """
        print(f"\n🔄 Triggering application creation for {family_id} - {scheme_code}")
        
        # Step 1: Verify consent
        consent_valid = self._verify_consent(family_id, scheme_code, consent_id)
        if not consent_valid['valid']:
            return {
                'success': False,
                'error': 'Consent verification failed',
                'details': consent_valid
            }
        
        # Step 2: Check eligibility
        eligibility_check = self._check_eligibility(family_id, scheme_code)
        if not eligibility_check['eligible']:
            return {
                'success': False,
                'error': 'Eligibility check failed',
                'details': eligibility_check
            }
        
        # Step 3: Check for duplicate applications
        duplicate_check = self._check_duplicate_application(family_id, scheme_code)
        if duplicate_check['exists']:
            return {
                'success': False,
                'error': 'Duplicate application exists',
                'details': duplicate_check
            }
        
        # Step 4: Create application record
        application_id = self._create_application_record(
            family_id=family_id,
            scheme_code=scheme_code,
            consent_id=consent_valid.get('consent_id'),
            eligibility_snapshot_id=eligibility_check.get('snapshot_id'),
            eligibility_score=eligibility_check.get('score'),
            eligibility_status=eligibility_check.get('status')
        )
        
        if not application_id:
            return {
                'success': False,
                'error': 'Failed to create application record'
            }
        
        print(f"✅ Application record created: {application_id}")
        
        # Step 5: Load form mapper and validation engine (to be implemented)
        # For now, return success with application_id
        
        return {
            'success': True,
            'application_id': application_id,
            'status': 'creating',
            'message': 'Application creation initiated'
        }
    
    def _verify_consent(
        self,
        family_id: str,
        scheme_code: str,
        consent_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Verify consent record exists and has sufficient LOA"""
        try:
            if 'intimation' not in self.external_dbs:
                return {'valid': False, 'error': 'Intimation database not configured'}
            
            intimation_db = self.external_dbs['intimation']
            
            if consent_id:
                query = """
                    SELECT 
                        consent_id,
                        family_id,
                        scheme_code,
                        consent_type,
                        level_of_assurance,
                        status,
                        consent_value,
                        valid_from,
                        valid_until
                    FROM intimation.consent_records
                    WHERE consent_id = %s
                        AND family_id::text = %s
                        AND scheme_code = %s
                        AND status = 'valid'
                        AND consent_value = true
                """
                params = [consent_id, family_id, scheme_code]
            else:
                query = """
                    SELECT 
                        consent_id,
                        family_id,
                        scheme_code,
                        consent_type,
                        level_of_assurance,
                        status,
                        consent_value,
                        valid_from,
                        valid_until
                    FROM intimation.consent_records
                    WHERE family_id::text = %s
                        AND scheme_code = %s
                        AND status = 'valid'
                        AND consent_value = true
                    ORDER BY created_at DESC
                    LIMIT 1
                """
                params = [family_id, scheme_code]
            
            cursor = intimation_db.connection.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            cursor.close()
            
            if not row:
                return {'valid': False, 'error': 'No valid consent found'}
            
            consent_id, _, _, consent_type, loa, status, _, valid_from, valid_until = row
            
            # Check if consent is still valid
            now = datetime.now()
            if valid_until and valid_until < now:
                return {'valid': False, 'error': 'Consent has expired'}
            
            # Check LOA for high-risk schemes
            scheme_config = self.use_case_config.get('schemes', {}).get(scheme_code, {})
            required_loa = scheme_config.get('required_loa', 'MEDIUM')
            
            loa_levels = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'VERY_HIGH': 4}
            if loa_levels.get(loa, 0) < loa_levels.get(required_loa, 1):
                return {
                    'valid': False,
                    'error': f'Insufficient LOA: required {required_loa}, got {loa}'
                }
            
            return {
                'valid': True,
                'consent_id': consent_id,
                'consent_type': consent_type,
                'loa': loa
            }
        
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def _check_eligibility(
        self,
        family_id: str,
        scheme_code: str
    ) -> Dict[str, Any]:
        """Check eligibility from eligibility snapshots"""
        try:
            if 'eligibility' not in self.external_dbs:
                return {'eligible': False, 'error': 'Eligibility database not configured'}
            
            eligibility_db = self.external_dbs['eligibility']
            
            query = """
                SELECT 
                    snapshot_id,
                    family_id,
                    scheme_code,
                    eligibility_score,
                    evaluation_status,
                    evaluation_timestamp
                FROM eligibility.eligibility_snapshots
                WHERE family_id::text = %s
                    AND scheme_code = %s
                    AND evaluation_status IN ('RULE_ELIGIBLE', 'POSSIBLE_ELIGIBLE')
                ORDER BY evaluation_timestamp DESC
                LIMIT 1
            """
            
            cursor = eligibility_db.connection.cursor()
            cursor.execute(query, [family_id, scheme_code])
            row = cursor.fetchone()
            cursor.close()
            
            if not row:
                return {'eligible': False, 'error': 'No eligibility snapshot found'}
            
            snapshot_id, _, _, score, status, timestamp = row
            
            # Check minimum score threshold
            min_score = self.use_case_config.get('application', {}).get('min_eligibility_score', 0.6)
            if score < min_score:
                return {
                    'eligible': False,
                    'error': f'Score {score} below minimum {min_score}',
                    'score': score
                }
            
            return {
                'eligible': True,
                'snapshot_id': snapshot_id,
                'score': float(score),
                'status': status,
                'timestamp': timestamp
            }
        
        except Exception as e:
            return {'eligible': False, 'error': str(e)}
    
    def _check_duplicate_application(
        self,
        family_id: str,
        scheme_code: str
    ) -> Dict[str, Any]:
        """Check if an active application already exists"""
        try:
            query = """
                SELECT 
                    application_id,
                    status,
                    created_at
                FROM application.applications
                WHERE family_id::text = %s
                    AND scheme_code = %s
                    AND status IN ('creating', 'draft', 'pending_review', 
                                  'pending_submission', 'submitted')
                ORDER BY created_at DESC
                LIMIT 1
            """
            
            cursor = self.db.connection.cursor()
            cursor.execute(query, [family_id, scheme_code])
            row = cursor.fetchone()
            cursor.close()
            
            if row:
                app_id, status, created_at = row
                return {
                    'exists': True,
                    'application_id': app_id,
                    'status': status,
                    'created_at': created_at
                }
            
            return {'exists': False}
        
        except Exception as e:
            return {'exists': False, 'error': str(e)}
    
    def _create_application_record(
        self,
        family_id: str,
        scheme_code: str,
        consent_id: Optional[int],
        eligibility_snapshot_id: Optional[int],
        eligibility_score: Optional[float],
        eligibility_status: Optional[str]
    ) -> Optional[int]:
        """Create application record in database"""
        try:
            # Determine submission mode from config
            submission_mode = self._get_submission_mode(scheme_code)
            
            query = """
                INSERT INTO application.applications (
                    family_id,
                    scheme_code,
                    consent_id,
                    eligibility_snapshot_id,
                    eligibility_score,
                    eligibility_status,
                    status,
                    submission_mode,
                    created_by
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING application_id
            """
            
            cursor = self.db.connection.cursor()
            cursor.execute(query, (
                family_id,
                scheme_code,
                consent_id,
                eligibility_snapshot_id,
                eligibility_score,
                eligibility_status,
                'creating',
                submission_mode,
                'application_orchestrator'
            ))
            
            application_id = cursor.fetchone()[0]
            self.db.connection.commit()
            cursor.close()
            
            # Log audit event
            self._log_audit_event(
                application_id=application_id,
                event_type='CREATED',
                event_description=f'Application created via orchestrator'
            )
            
            return application_id
        
        except Exception as e:
            print(f"❌ Error creating application record: {e}")
            self.db.connection.rollback()
            return None
    
    def _get_submission_mode(self, scheme_code: str) -> str:
        """Get submission mode for scheme"""
        try:
            query = """
                SELECT default_mode
                FROM application.submission_modes_config
                WHERE scheme_code = %s
                    AND is_active = true
                LIMIT 1
            """
            
            cursor = self.db.connection.cursor()
            cursor.execute(query, [scheme_code])
            row = cursor.fetchone()
            cursor.close()
            
            if row:
                return row[0]
            
            # Default from use case config
            return self.use_case_config.get('application', {}).get('default_submission_mode', 'review')
        
        except Exception as e:
            print(f"⚠️  Error getting submission mode: {e}")
            return 'review'
    
    def _log_audit_event(
        self,
        application_id: int,
        event_type: str,
        event_description: str,
        field_name: Optional[str] = None,
        old_value: Optional[Any] = None,
        new_value: Optional[Any] = None
    ):
        """Log audit event"""
        try:
            query = """
                INSERT INTO application.application_audit_logs (
                    application_id,
                    event_type,
                    event_description,
                    field_name,
                    old_value,
                    new_value,
                    triggered_by,
                    actor_type,
                    actor_name
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            import json
            cursor = self.db.connection.cursor()
            cursor.execute(query, (
                application_id,
                event_type,
                event_description,
                field_name,
                json.dumps(old_value) if old_value is not None else None,
                json.dumps(new_value) if new_value is not None else None,
                'system',
                'system',
                'application_orchestrator'
            ))
            self.db.connection.commit()
            cursor.close()
        
        except Exception as e:
            print(f"⚠️  Error logging audit event: {e}")

