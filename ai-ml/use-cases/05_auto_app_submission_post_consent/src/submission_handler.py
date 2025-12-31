"""
Submission Handler
Handles application submission based on mode (auto/review/assisted)
"""

from typing import Dict, Any, Optional
from datetime import datetime
import sys
from pathlib import Path
import yaml
import json

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector

# Import connectors
sys.path.append(str(Path(__file__).parent / "connectors"))
from connector_factory import ConnectorFactory
from department_connector import SubmissionResult


class SubmissionHandler:
    """Handles application submission workflow"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Submission Handler"""
        if config_path is None:
            base_dir = Path(__file__).parent.parent
            config_path = base_dir / "config" / "db_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize database connection
        db_config = self.config['database']
        self.db = DBConnector(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['name'],
            user=db_config['user'],
            password=db_config['password']
        )
        
        # Load use case config
        use_case_config_path = Path(config_path).parent / "use_case_config.yaml"
        if use_case_config_path.exists():
            with open(use_case_config_path, 'r') as f:
                self.use_case_config = yaml.safe_load(f)
        else:
            self.use_case_config = {}
    
    def connect(self):
        """Connect to database"""
        self.db.connect()
    
    def disconnect(self):
        """Disconnect from database"""
        self.db.disconnect()
    
    def handle_submission(
        self,
        application_id: int,
        scheme_code: str,
        submission_mode: str
    ) -> Dict[str, Any]:
        """
        Handle application submission based on mode
        
        Args:
            application_id: Application ID
            scheme_code: Scheme code
            submission_mode: Submission mode (auto, review, assisted)
        
        Returns:
            Submission result
        """
        print(f"\n📤 Handling submission for application {application_id} (mode: {submission_mode})")
        
        if submission_mode == 'auto':
            return self._auto_submit(application_id, scheme_code)
        
        elif submission_mode == 'review':
            return self._store_for_review(application_id, scheme_code)
        
        elif submission_mode == 'assisted':
            return self._route_to_assisted(application_id, scheme_code)
        
        else:
            return {
                'success': False,
                'error': f'Unknown submission mode: {submission_mode}'
            }
    
    def _auto_submit(
        self,
        application_id: int,
        scheme_code: str
    ) -> Dict[str, Any]:
        """Auto-submit application directly to department"""
        try:
            # Load application data
            application_data = self._load_application_data(application_id)
            
            # Get connector
            connector = self._get_connector(scheme_code)
            if not connector:
                return {
                    'success': False,
                    'error': 'No connector configured for scheme'
                }
            
            # Submit application
            result = connector.submit_application(
                application_data=application_data,
                scheme_code=scheme_code
            )
            
            # Store submission record
            submission_id = self._store_submission_record(
                application_id=application_id,
                result=result,
                connector_name=connector.connector_name,
                connector_type=connector.connector_type
            )
            
            # Update application status
            if result.success:
                self._update_application_status(application_id, 'submitted', result.department_application_number)
                self._publish_event(application_id, 'APPLICATION_SUBMITTED', {
                    'department_application_number': result.department_application_number,
                    'submission_id': submission_id
                })
            else:
                self._update_application_status(application_id, 'submission_failed')
                self._publish_event(application_id, 'APPLICATION_SUBMISSION_FAILED', {
                    'error': result.error_message,
                    'submission_id': submission_id
                })
            
            return {
                'success': result.success,
                'submission_id': submission_id,
                'department_application_number': result.department_application_number,
                'error': result.error_message,
                'retry_required': result.retry_required
            }
        
        except Exception as e:
            print(f"❌ Error in auto submission: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _store_for_review(
        self,
        application_id: int,
        scheme_code: str
    ) -> Dict[str, Any]:
        """Store application as draft for citizen review"""
        try:
            # Update application status
            self._update_application_status(application_id, 'pending_review')
            
            # Publish event
            self._publish_event(application_id, 'APPLICATION_DRAFT_CREATED', {
                'scheme_code': scheme_code,
                'status': 'pending_review'
            })
            
            return {
                'success': True,
                'status': 'pending_review',
                'message': 'Application stored for citizen review'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _route_to_assisted(
        self,
        application_id: int,
        scheme_code: str
    ) -> Dict[str, Any]:
        """Route application to assisted channel (e-Mitra/field worker)"""
        try:
            # Update application status
            self._update_application_status(application_id, 'pending_assisted')
            
            # Publish event
            self._publish_event(application_id, 'APPLICATION_REQUIRES_ASSISTANCE', {
                'scheme_code': scheme_code,
                'status': 'pending_assisted'
            })
            
            return {
                'success': True,
                'status': 'pending_assisted',
                'message': 'Application routed to assisted channel'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def submit_reviewed_application(
        self,
        application_id: int,
        scheme_code: str
    ) -> Dict[str, Any]:
        """Submit application after citizen review"""
        # Same as auto_submit but for reviewed applications
        return self._auto_submit(application_id, scheme_code)
    
    def _load_application_data(self, application_id: int) -> Dict[str, Any]:
        """Load complete application data"""
        try:
            # Load application fields
            query = """
                SELECT field_name, field_value
                FROM application.application_fields
                WHERE application_id = %s
            """
            
            cursor = self.db.connection.cursor()
            cursor.execute(query, [application_id])
            rows = cursor.fetchall()
            cursor.close()
            
            # Build application data
            application_data = {
                'application_id': application_id,
                'beneficiary': {},
                'documents': []
            }
            
            for field_name, field_value in rows:
                if isinstance(field_value, str):
                    try:
                        value = json.loads(field_value)
                    except:
                        value = field_value
                else:
                    value = field_value
                
                # Organize fields
                if field_name.startswith('address'):
                    if 'address' not in application_data['beneficiary']:
                        application_data['beneficiary']['address'] = {}
                    application_data['beneficiary']['address'][field_name.replace('address_', '')] = value
                elif field_name in ['full_name', 'date_of_birth', 'gender', 'aadhaar_number', 
                                   'mobile_number', 'email', 'bank_account_number', 'ifsc_code']:
                    application_data['beneficiary'][field_name] = value
                else:
                    application_data['beneficiary'][field_name] = value
            
            # Load documents
            doc_query = """
                SELECT document_type, document_reference, document_url
                FROM application.application_documents
                WHERE application_id = %s
                    AND status = 'attached'
            """
            
            cursor = self.db.connection.cursor()
            cursor.execute(doc_query, [application_id])
            doc_rows = cursor.fetchall()
            cursor.close()
            
            for doc_type, doc_ref, doc_url in doc_rows:
                application_data['documents'].append({
                    'type': doc_type,
                    'reference': doc_ref,
                    'url': doc_url
                })
            
            return application_data
        
        except Exception as e:
            print(f"⚠️  Error loading application data: {e}")
            return {'application_id': application_id}
    
    def _get_connector(self, scheme_code: str):
        """Get connector for scheme"""
        try:
            # Try to find scheme-specific connector
            connector = ConnectorFactory.load_connector_from_db(
                self.db.connection,
                'DEFAULT_REST',  # Default connector name
                scheme_code
            )
            
            if not connector:
                # Fallback to default
                connector = ConnectorFactory.load_connector_from_db(
                    self.db.connection,
                    'DEFAULT_REST'
                )
            
            return connector
        
        except Exception as e:
            print(f"⚠️  Error getting connector: {e}")
            return None
    
    def _store_submission_record(
        self,
        application_id: int,
        result: SubmissionResult,
        connector_name: str,
        connector_type: str
    ) -> Optional[int]:
        """Store submission record in database"""
        try:
            query = """
                INSERT INTO application.application_submissions (
                    application_id,
                    submission_mode,
                    connector_type,
                    connector_name,
                    submission_payload,
                    payload_format,
                    department_response,
                    department_application_number,
                    response_status_code,
                    response_status,
                    response_message,
                    submitted_at,
                    responded_at,
                    submitted_by
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING submission_id
            """
            
            cursor = self.db.connection.cursor()
            cursor.execute(query, (
                application_id,
                'auto',
                connector_type,
                connector_name,
                json.dumps({}),  # Payload (can be stored separately)
                'JSON',
                json.dumps(result.response_data) if result.response_data else None,
                result.department_application_number,
                result.status_code,
                result.status.value if hasattr(result.status, 'value') else str(result.status),
                result.error_message,
                result.submitted_at or datetime.now(),
                datetime.now() if result.submitted_at else None,
                'submission_handler'
            ))
            
            submission_id = cursor.fetchone()[0]
            self.db.connection.commit()
            cursor.close()
            
            return submission_id
        
        except Exception as e:
            print(f"⚠️  Error storing submission record: {e}")
            self.db.connection.rollback()
            return None
    
    def _update_application_status(
        self,
        application_id: int,
        status: str,
        department_app_number: Optional[str] = None
    ):
        """Update application status"""
        try:
            query = """
                UPDATE application.applications
                SET status = %s,
                    updated_at = CURRENT_TIMESTAMP,
                    department_application_number = COALESCE(%s, department_application_number),
                    submitted_at = CASE WHEN %s = 'submitted' THEN CURRENT_TIMESTAMP ELSE submitted_at END
                WHERE application_id = %s
            """
            
            cursor = self.db.connection.cursor()
            cursor.execute(query, [status, department_app_number, status, application_id])
            self.db.connection.commit()
            cursor.close()
        
        except Exception as e:
            print(f"⚠️  Error updating application status: {e}")
            self.db.connection.rollback()
    
    def _publish_event(
        self,
        application_id: int,
        event_type: str,
        event_data: Dict[str, Any]
    ):
        """Publish application event"""
        try:
            query = """
                INSERT INTO application.application_events (
                    application_id,
                    event_type,
                    event_data,
                    event_status
                ) VALUES (%s, %s, %s, %s)
            """
            
            cursor = self.db.connection.cursor()
            cursor.execute(query, (
                application_id,
                event_type,
                json.dumps(event_data),
                'pending'
            ))
            self.db.connection.commit()
            cursor.close()
        
        except Exception as e:
            print(f"⚠️  Error publishing event: {e}")
            self.db.connection.rollback()

