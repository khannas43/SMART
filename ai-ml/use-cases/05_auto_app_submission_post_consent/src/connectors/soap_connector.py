"""
SOAP Connector for Department Web Services
Handles SOAP/XML submissions
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from zeep import Client, Settings
    ZEEP_AVAILABLE = True
except ImportError:
    ZEEP_AVAILABLE = False

sys.path.append(str(Path(__file__).parent))
from department_connector import DepartmentConnector, SubmissionResult, SubmissionStatus


class SOAPConnector(DepartmentConnector):
    """SOAP/XML web service connector for department submissions"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize SOAP connector"""
        super().__init__(config)
        self.wsdl_url = config.get('wsdl_url', '')
        
        if not ZEEP_AVAILABLE:
            raise ImportError("zeep library is required for SOAP connector. Install with: pip install zeep")
        
        # Setup SOAP client
        self._setup_client()
    
    def _setup_client(self):
        """Setup SOAP client"""
        if self.wsdl_url:
            settings = Settings(strict=False, xml_huge_tree=True)
            self.client = Client(wsdl=self.wsdl_url, settings=settings)
            
            # Setup authentication if needed
            if self.auth_type == 'WSS':
                # WS-Security authentication
                from zeep.wsse.username import UsernameToken
                username = self.auth_config.get('username', '')
                password = self.auth_config.get('password', '')
                if username and password:
                    self.client.set_wsse(UsernameToken(username, password))
        else:
            self.client = None
    
    def submit_application(
        self,
        application_data: Dict[str, Any],
        scheme_code: str,
        **kwargs
    ) -> SubmissionResult:
        """Submit application via SOAP web service"""
        try:
            if not self.client:
                return SubmissionResult(
                    success=False,
                    department_application_number=None,
                    status=SubmissionStatus.ERROR,
                    error_message='SOAP client not initialized. WSDL URL required.'
                )
            
            # Format payload
            payload = self.format_payload(application_data, scheme_code)
            
            # Get service and operation (default to 'submitApplication' if available)
            service = self.client.service
            operation_name = kwargs.get('operation_name', 'submitApplication')
            
            # Call SOAP operation
            if hasattr(service, operation_name):
                response = getattr(service, operation_name)(**payload)
            else:
                # Try default method
                response = service(**payload)
            
            # Parse response
            return self.parse_response(response)
        
        except Exception as e:
            return SubmissionResult(
                success=False,
                department_application_number=None,
                status=SubmissionStatus.ERROR,
                error_message=str(e),
                retry_required=False
            )
    
    def format_payload(
        self,
        application_data: Dict[str, Any],
        scheme_code: str
    ) -> Dict[str, Any]:
        """Format application data for SOAP service"""
        # Get payload template from config
        template = self.config.get('payload_template', {})
        
        if template:
            payload = template.copy()
            # Replace placeholders
            import json
            payload_str = json.dumps(payload)
            payload_str = payload_str.replace('{{application_id}}', str(application_data.get('application_id', '')))
            payload_str = payload_str.replace('{{scheme_code}}', scheme_code)
            payload_str = payload_str.replace('{{beneficiary_data}}', json.dumps(application_data.get('beneficiary', {})))
            payload = json.loads(payload_str)
        else:
            # Default format
            payload = {
                'applicationId': str(application_data.get('application_id', '')),
                'schemeCode': scheme_code,
                'beneficiary': application_data.get('beneficiary', {}),
                'documents': application_data.get('documents', []),
                'submittedAt': datetime.now().isoformat()
            }
        
        return payload
    
    def parse_response(
        self,
        response: Any
    ) -> SubmissionResult:
        """Parse SOAP service response"""
        try:
            # Convert SOAP response to dict
            if hasattr(response, '__dict__'):
                response_dict = response.__dict__
            elif hasattr(response, '_value_1'):
                # zeep response structure
                response_dict = {'value': response._value_1}
            else:
                response_dict = {'response': str(response)}
            
            # Extract application number
            app_number = response_dict.get('applicationNumber') or \
                        response_dict.get('application_number') or \
                        response_dict.get('referenceNumber') or \
                        response_dict.get('reference_number')
            
            # Check for errors
            error_message = response_dict.get('errorMessage') or \
                          response_dict.get('error_message') or \
                          response_dict.get('error')
            
            if error_message:
                return SubmissionResult(
                    success=False,
                    department_application_number=None,
                    status=SubmissionStatus.VALIDATION_ERROR,
                    error_message=str(error_message),
                    response_data=response_dict
                )
            
            return SubmissionResult(
                success=True,
                department_application_number=str(app_number) if app_number else None,
                status=SubmissionStatus.SUCCESS,
                submitted_at=datetime.now(),
                response_data=response_dict
            )
        
        except Exception as e:
            return SubmissionResult(
                success=False,
                department_application_number=None,
                status=SubmissionStatus.ERROR,
                error_message=f'Error parsing SOAP response: {str(e)}',
                retry_required=False
            )

