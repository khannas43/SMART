"""
REST Connector for Department APIs
Handles REST API submissions
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import requests
import json

sys.path.append(str(Path(__file__).parent))
from department_connector import DepartmentConnector, SubmissionResult, SubmissionStatus


class RESTConnector(DepartmentConnector):
    """REST API connector for department submissions"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize REST connector"""
        super().__init__(config)
        self.timeout = config.get('timeout', {}).get('read_timeout_seconds', 60)
        self.connection_timeout = config.get('timeout', {}).get('connection_timeout_seconds', 30)
        
        # Setup authentication
        self.auth_type = config.get('auth_type', 'NONE')
        self._setup_auth()
    
    def _setup_auth(self):
        """Setup authentication based on auth_type"""
        self.auth_headers = {}
        self.auth_params = {}
        
        if self.auth_type == 'API_KEY':
            api_key = self.auth_config.get('api_key', '')
            header_name = self.auth_config.get('header_name', 'X-API-Key')
            self.auth_headers[header_name] = api_key
        
        elif self.auth_type == 'OAUTH2':
            # For OAuth2, we'd need to get token first
            # This is a placeholder - actual implementation would handle token refresh
            token = self.auth_config.get('access_token', '')
            if token:
                self.auth_headers['Authorization'] = f'Bearer {token}'
        
        elif self.auth_type == 'BASIC':
            username = self.auth_config.get('username', '')
            password = self.auth_config.get('password', '')
            if username and password:
                import base64
                credentials = base64.b64encode(f'{username}:{password}'.encode()).decode()
                self.auth_headers['Authorization'] = f'Basic {credentials}'
    
    def submit_application(
        self,
        application_data: Dict[str, Any],
        scheme_code: str,
        **kwargs
    ) -> SubmissionResult:
        """Submit application via REST API"""
        try:
            # Format payload
            payload = self.format_payload(application_data, scheme_code)
            
            # Build URL
            url = f"{self.base_url.rstrip('/')}/{self.endpoint_path.lstrip('/')}"
            
            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                **self.auth_headers
            }
            
            # Make request
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=(self.connection_timeout, self.timeout),
                params=self.auth_params
            )
            
            # Parse response
            return self.parse_response(response)
        
        except requests.exceptions.Timeout:
            return SubmissionResult(
                success=False,
                department_application_number=None,
                status=SubmissionStatus.TIMEOUT,
                error_message='Request timeout',
                retry_required=True
            )
        
        except requests.exceptions.ConnectionError:
            return SubmissionResult(
                success=False,
                department_application_number=None,
                status=SubmissionStatus.ERROR,
                error_message='Connection error',
                retry_required=True
            )
        
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
        """Format application data for REST API"""
        # Get payload template from config
        template = self.config.get('payload_template', {})
        
        if template:
            # Use template if available
            payload = template.copy()
            # Replace placeholders (simple string replacement for now)
            payload_str = json.dumps(payload)
            payload_str = payload_str.replace('{{application_id}}', str(application_data.get('application_id', '')))
            payload_str = payload_str.replace('{{scheme_code}}', scheme_code)
            payload_str = payload_str.replace('{{beneficiary_data}}', json.dumps(application_data.get('beneficiary', {})))
            payload = json.loads(payload_str)
        else:
            # Default format
            payload = {
                'application_id': application_data.get('application_id'),
                'scheme_code': scheme_code,
                'beneficiary': application_data.get('beneficiary', {}),
                'documents': application_data.get('documents', []),
                'submitted_at': datetime.now().isoformat()
            }
        
        return payload
    
    def parse_response(
        self,
        response: requests.Response
    ) -> SubmissionResult:
        """Parse REST API response"""
        status_code = response.status_code
        
        try:
            response_data = response.json()
        except:
            response_data = {'raw_response': response.text}
        
        # Check for success
        if 200 <= status_code < 300:
            # Extract application number from response
            app_number = response_data.get('application_number') or \
                        response_data.get('application_id') or \
                        response_data.get('reference_number')
            
            return SubmissionResult(
                success=True,
                department_application_number=app_number,
                status=SubmissionStatus.SUCCESS,
                status_code=status_code,
                submitted_at=datetime.now(),
                response_data=response_data
            )
        
        elif 400 <= status_code < 500:
            # Client error (validation error, bad request, etc.)
            error_message = response_data.get('message') or \
                          response_data.get('error') or \
                          f'Client error: {status_code}'
            
            return SubmissionResult(
                success=False,
                department_application_number=None,
                status=SubmissionStatus.VALIDATION_ERROR,
                status_code=status_code,
                error_message=error_message,
                response_data=response_data,
                retry_required=False
            )
        
        else:
            # Server error (5xx) - retry
            error_message = response_data.get('message') or \
                          response_data.get('error') or \
                          f'Server error: {status_code}'
            
            return SubmissionResult(
                success=False,
                department_application_number=None,
                status=SubmissionStatus.ERROR,
                status_code=status_code,
                error_message=error_message,
                response_data=response_data,
                retry_required=True
            )

