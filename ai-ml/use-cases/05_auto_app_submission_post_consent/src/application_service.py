"""
Main Application Service
Orchestrates the complete application creation and submission workflow
"""

from typing import Dict, Any, Optional
from datetime import datetime

try:
    # Try relative imports first (when used as package)
    from .application_orchestrator import ApplicationOrchestrator
    from .form_mapper import FormMapper
    from .validation_engine import ValidationEngine
    from .submission_handler import SubmissionHandler
except ImportError:
    # Fall back to absolute imports (when run directly)
    from application_orchestrator import ApplicationOrchestrator
    from form_mapper import FormMapper
    from validation_engine import ValidationEngine
    from submission_handler import SubmissionHandler


class ApplicationService:
    """Main service orchestrating application workflow"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Application Service"""
        self.orchestrator = ApplicationOrchestrator(config_path)
        self.form_mapper = FormMapper(config_path)
        self.validator = ValidationEngine(config_path)
        self.submission_handler = SubmissionHandler(config_path)
    
    def process_consent_event(
        self,
        family_id: str,
        scheme_code: str,
        consent_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process consent event and create/submit application
        
        Args:
            family_id: Family ID
            scheme_code: Scheme code
            consent_id: Consent record ID (optional)
        
        Returns:
            Complete workflow result
        """
        print(f"\n🔄 Processing consent event for {family_id} - {scheme_code}")
        
        # Step 1: Trigger application creation
        create_result = self.orchestrator.trigger_on_consent(
            family_id=family_id,
            scheme_code=scheme_code,
            consent_id=consent_id
        )
        
        if not create_result['success']:
            return create_result
        
        application_id = create_result['application_id']
        
        # Step 2: Map form fields
        map_result = self.form_mapper.map_form_fields(
            application_id=application_id,
            family_id=family_id,
            scheme_code=scheme_code
        )
        
        if not map_result['success']:
            return {
                'success': False,
                'error': 'Form mapping failed',
                'application_id': application_id
            }
        
        # Step 3: Validate application
        validation_result = self.validator.validate_application(
            application_id=application_id,
            scheme_code=scheme_code
        )
        
        # Step 4: Get submission mode and handle
        query = """
            SELECT submission_mode, status
            FROM application.applications
            WHERE application_id = %s
        """
        
        cursor = self.submission_handler.db.connection.cursor()
        cursor.execute(query, [application_id])
        row = cursor.fetchone()
        cursor.close()
        
        if row:
            submission_mode, status = row
            
            # Handle submission based on mode
            if submission_mode == 'auto' and validation_result['is_valid']:
                submit_result = self.submission_handler.handle_submission(
                    application_id=application_id,
                    scheme_code=scheme_code,
                    submission_mode=submission_mode
                )
            else:
                submit_result = self.submission_handler.handle_submission(
                    application_id=application_id,
                    scheme_code=scheme_code,
                    submission_mode=submission_mode
                )
        else:
            submit_result = {'success': False, 'error': 'Application not found'}
        
        return {
            'success': True,
            'application_id': application_id,
            'mapping': map_result,
            'validation': validation_result,
            'submission': submit_result
        }
    
    def get_application_draft(
        self,
        family_id: str,
        scheme_code: str
    ) -> Dict[str, Any]:
        """
        Get application draft for citizen review
        
        Args:
            family_id: Family ID
            scheme_code: Scheme code
        
        Returns:
            Application draft data
        """
        try:
            query = """
                SELECT application_id, status, submission_mode
                FROM application.applications
                WHERE family_id::text = %s
                    AND scheme_code = %s
                    AND status = 'pending_review'
                ORDER BY created_at DESC
                LIMIT 1
            """
            
            cursor = self.form_mapper.db.connection.cursor()
            cursor.execute(query, [family_id, scheme_code])
            row = cursor.fetchone()
            cursor.close()
            
            if not row:
                return {
                    'success': False,
                    'error': 'No draft application found'
                }
            
            application_id, status, submission_mode = row
            
            # Load application fields
            fields_query = """
                SELECT field_name, field_value, source_type, mapping_type
                FROM application.application_fields
                WHERE application_id = %s
            """
            
            cursor = self.form_mapper.db.connection.cursor()
            cursor.execute(fields_query, [application_id])
            fields = cursor.fetchall()
            cursor.close()
            
            # Build form data and sources
            form_data = {}
            field_sources = {}
            
            import json
            for field_name, field_value, source_type, mapping_type in fields:
                if isinstance(field_value, str):
                    try:
                        form_data[field_name] = json.loads(field_value)
                    except:
                        form_data[field_name] = field_value
                else:
                    form_data[field_name] = field_value
                
                field_sources[field_name] = {
                    'source_type': source_type,
                    'mapping_type': mapping_type
                }
            
            return {
                'success': True,
                'application_id': application_id,
                'scheme_code': scheme_code,
                'form_data': form_data,
                'field_sources': field_sources,
                'status': status
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def confirm_application(
        self,
        application_id: int,
        scheme_code: str
    ) -> Dict[str, Any]:
        """
        Confirm and submit reviewed application
        
        Args:
            application_id: Application ID
            scheme_code: Scheme code
        
        Returns:
            Submission result
        """
        return self.submission_handler.submit_reviewed_application(
            application_id=application_id,
            scheme_code=scheme_code
        )
    
    def disconnect(self):
        """Close all connections"""
        self.orchestrator.disconnect()
        self.form_mapper.disconnect()
        self.validator.disconnect()
        self.submission_handler.disconnect()

