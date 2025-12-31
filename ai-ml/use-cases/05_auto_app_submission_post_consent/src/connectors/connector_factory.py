"""
Connector Factory
Creates appropriate connector instances based on configuration
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

sys.path.append(str(Path(__file__).parent))
from department_connector import DepartmentConnector
from rest_connector import RESTConnector
from soap_connector import SOAPConnector
from api_setu_connector import APISetuConnector


class ConnectorFactory:
    """Factory for creating department connectors"""
    
    @staticmethod
    def create_connector(connector_config: Dict[str, Any]) -> DepartmentConnector:
        """
        Create connector instance based on configuration
        
        Args:
            connector_config: Connector configuration from database
        
        Returns:
            Connector instance
        """
        connector_type = connector_config.get('connector_type', '').upper()
        
        if connector_type == 'REST':
            return RESTConnector(connector_config)
        
        elif connector_type == 'SOAP':
            return SOAPConnector(connector_config)
        
        elif connector_type == 'API_SETU':
            return APISetuConnector(connector_config)
        
        else:
            raise ValueError(f"Unknown connector type: {connector_type}")
    
    @staticmethod
    def load_connector_from_db(
        db_connection,
        connector_name: str,
        scheme_code: Optional[str] = None
    ) -> Optional[DepartmentConnector]:
        """
        Load connector configuration from database and create instance
        
        Args:
            db_connection: Database connection
            connector_name: Connector name
            scheme_code: Optional scheme code (to find scheme-specific connector)
        
        Returns:
            Connector instance or None
        """
        try:
            cursor = db_connection.cursor()
            
            # Try to find scheme-specific connector first
            if scheme_code:
                query = """
                    SELECT 
                        connector_id,
                        connector_name,
                        department_name,
                        scheme_code,
                        connector_type,
                        connector_version,
                        base_url,
                        endpoint_path,
                        wsdl_url,
                        api_setu_config,
                        auth_type,
                        auth_config,
                        payload_format,
                        payload_template,
                        response_schema,
                        max_retries,
                        retry_delay_seconds,
                        retry_on_status_codes
                    FROM application.department_connectors
                    WHERE connector_name = %s
                        AND (scheme_code = %s OR scheme_code IS NULL)
                        AND is_active = true
                    ORDER BY 
                        CASE WHEN scheme_code IS NOT NULL THEN 0 ELSE 1 END
                    LIMIT 1
                """
                cursor.execute(query, [connector_name, scheme_code])
            else:
                query = """
                    SELECT 
                        connector_id,
                        connector_name,
                        department_name,
                        scheme_code,
                        connector_type,
                        connector_version,
                        base_url,
                        endpoint_path,
                        wsdl_url,
                        api_setu_config,
                        auth_type,
                        auth_config,
                        payload_format,
                        payload_template,
                        response_schema,
                        max_retries,
                        retry_delay_seconds,
                        retry_on_status_codes
                    FROM application.department_connectors
                    WHERE connector_name = %s
                        AND is_active = true
                    LIMIT 1
                """
                cursor.execute(query, [connector_name])
            
            row = cursor.fetchone()
            cursor.close()
            
            if not row:
                return None
            
            # Build config dict
            columns = [desc[0] for desc in cursor.description]
            config = dict(zip(columns, row))
            
            # Parse JSON fields
            import json
            if isinstance(config.get('api_setu_config'), str):
                config['api_setu_config'] = json.loads(config['api_setu_config'])
            if isinstance(config.get('auth_config'), str):
                config['auth_config'] = json.loads(config['auth_config'])
            if isinstance(config.get('payload_template'), str):
                config['payload_template'] = json.loads(config['payload_template'])
            if isinstance(config.get('response_schema'), str):
                config['response_schema'] = json.loads(config['response_schema'])
            if isinstance(config.get('retry_on_status_codes'), list):
                # Already a list
                pass
            elif config.get('retry_on_status_codes'):
                config['retry_on_status_codes'] = json.loads(config['retry_on_status_codes'])
            
            # Create connector
            return ConnectorFactory.create_connector(config)
        
        except Exception as e:
            print(f"⚠️  Error loading connector from database: {e}")
            return None

