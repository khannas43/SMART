"""
Department Connector Abstract Base Class
Defines interface for all department connectors
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class SubmissionStatus(Enum):
    """Application submission status"""
    SUCCESS = "success"
    ERROR = "error"
    VALIDATION_ERROR = "validation_error"
    TIMEOUT = "timeout"
    RETRY_REQUIRED = "retry_required"


@dataclass
class SubmissionResult:
    """Result of application submission attempt"""
    success: bool
    department_application_number: Optional[str]
    status: SubmissionStatus
    status_code: Optional[int] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    submitted_at: Optional[datetime] = None
    response_data: Optional[Dict[str, Any]] = None
    retry_required: bool = False
    retry_after_seconds: Optional[int] = None


class DepartmentConnector(ABC):
    """Abstract base class for department connectors"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize department connector
        
        Args:
            config: Connector-specific configuration from database
        """
        self.config = config
        self.connector_name = config.get('connector_name', 'unknown')
        self.connector_type = config.get('connector_type', 'UNKNOWN')
        self.base_url = config.get('base_url', '')
        self.endpoint_path = config.get('endpoint_path', '')
        self.auth_config = config.get('auth_config', {})
        self.max_retries = config.get('max_retries', 3)
        self.retry_delay_seconds = config.get('retry_delay_seconds', 5)
        self.retry_on_status_codes = config.get('retry_on_status_codes', [500, 502, 503, 504, 408])
    
    @abstractmethod
    def submit_application(
        self,
        application_data: Dict[str, Any],
        scheme_code: str,
        **kwargs
    ) -> SubmissionResult:
        """
        Submit application to department
        
        Args:
            application_data: Formatted application data
            scheme_code: Scheme code
            **kwargs: Additional parameters
        
        Returns:
            Submission result
        """
        pass
    
    @abstractmethod
    def format_payload(
        self,
        application_data: Dict[str, Any],
        scheme_code: str
    ) -> Dict[str, Any]:
        """
        Format application data according to department's required schema
        
        Args:
            application_data: Raw application data
            scheme_code: Scheme code
        
        Returns:
            Formatted payload
        """
        pass
    
    @abstractmethod
    def parse_response(
        self,
        response: Any
    ) -> SubmissionResult:
        """
        Parse department response
        
        Args:
            response: Raw response from department
        
        Returns:
            Parsed submission result
        """
        pass
    
    def should_retry(
        self,
        result: SubmissionResult,
        attempt_number: int
    ) -> bool:
        """
        Determine if submission should be retried
        
        Args:
            result: Submission result
            attempt_number: Current attempt number
        
        Returns:
            True if should retry
        """
        if attempt_number >= self.max_retries:
            return False
        
        if result.retry_required:
            return True
        
        if result.status_code in self.retry_on_status_codes:
            return True
        
        if result.status == SubmissionStatus.TIMEOUT:
            return True
        
        return False
    
    def get_retry_delay(self, attempt_number: int) -> int:
        """
        Get retry delay in seconds (exponential backoff)
        
        Args:
            attempt_number: Current attempt number
        
        Returns:
            Delay in seconds
        """
        return self.retry_delay_seconds * (2 ** (attempt_number - 1))

