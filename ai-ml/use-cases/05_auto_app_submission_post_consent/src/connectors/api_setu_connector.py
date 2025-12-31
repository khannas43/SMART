"""
API Setu Connector for Government APIs
Handles API Setu gateway submissions
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import requests
import json

sys.path.append(str(Path(__file__).parent))
from department_connector import DepartmentConnector, SubmissionResult, SubmissionStatus


class APISetuConnector(DepartmentConnector):
    """API Setu gateway connector for government API submissions"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize API Setu connector"""
        super().__init__(config)
        self.api_setu_config = config.get('api_setu_config', {})
        self.api_key = self.api_setu_config.get('api_key', '')
        self.client_id = self.api_setu_config.get('client_id', '')
        self.client_secret = self.api_setu_config.get('client_secret', '')
        self.timeout = config.get('timeout', {}).get('read_timeout_seconds', 60)
        
        # OAuth2 token (would be refreshed in production)
        self.access_token = None
        self._get_access_token()
    
    def _get_access_token(self):
        """Get OAuth2 access token from API Setu"""
        try:
            token_url = f"{self.base_url.rstrip('/')}/oauth/token"
            
            response = requests.post(
                token_url,
                data={
                    'grant_type': 'client_credentials',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret
                },
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
            else:
                print(f"⚠️  Failed to get API Setu access token: {response.status_code}")
        
        except Exception as e:
            print(f"⚠️  Error getting API Setu access token: {e}")
    
    def submit_application(
        self,
        application_data: Dict[str, Any],
        scheme_code: str,
        **kwargs
    ) -> SubmissionResult:
        """Submit application via API Setu"""
        try:
            # Refresh token if needed
            if not self.access_token:
                self._get_access_token()
            
            if not self.access_token:
                return SubmissionResult(
                    success=False,
                    department_application_number=None,
                    status=SubmissionStatus.ERROR,
                    error_message='Failed to obtain API Setu access token'
                )
            
            # Format payload
            payload = self.format_payload(application_data, scheme_code)
            
            # Build URL
            url = f"{self.base_url.rstrip('/')}/{self.endpoint_path.lstrip('/')}"
            
            # Prepare headers (API Setu standard format)
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.access_token}',
                'X-API-Key': self.api_key,
                'Accept': 'application/json'
            }
            
            # Make request
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout
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
        """Format application data for API Setu"""
        # API Setu standard format
        payload = {
            'requestId': f"APP-{application_data.get('application_id', '')}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'schemeCode': scheme_code,
            'application': {
                'applicationId': str(application_data.get('application_id', '')),
                'beneficiary': application_data.get('beneficiary', {}),
                'documents': application_data.get('documents', [])
            }
        }
        
        return payload
    
    def parse_response(
        self,
        response: requests.Response
    ) -> SubmissionResult:
        """Parse API Setu response"""
        status_code = response.status_code
        
        try:
            response_data = response.json()
        except:
            response_data = {'raw_response': response.text}
        
        # API Setu standard response format
        if status_code == 200:
            result = response_data.get('result', {})
            app_number = result.get('applicationNumber') or \
                        result.get('application_number') or \
                        response_data.get('applicationNumber')
            
            return SubmissionResult(
                success=True,
                department_application_number=str(app_number) if app_number else None,
                status=SubmissionStatus.SUCCESS,
                status_code=status_code,
                submitted_at=datetime.now(),
                response_data=response_data
            )
        
        else:
            error_info = response_data.get('error', {})
            error_message = error_info.get('message') or \
                          error_info.get('description') or \
                          f'API Setu error: {status_code}'
            
            return SubmissionResult(
                success=False,
                department_application_number=None,
                status=SubmissionStatus.ERROR if status_code >= 500 else SubmissionStatus.VALIDATION_ERROR,
                status_code=status_code,
                error_message=error_message,
                response_data=response_data,
                retry_required=(status_code >= 500)
            )

