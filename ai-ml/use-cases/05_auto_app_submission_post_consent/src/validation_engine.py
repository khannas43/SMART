"""
Validation Engine
Validates application forms for completeness, correctness, and compliance
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import sys
from pathlib import Path
import yaml
import json
import re
import pandas as pd
from dateutil import parser as date_parser

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class ValidationEngine:
    """Validates application forms"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Validation Engine"""
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
        
        self.validation_config = self.use_case_config.get('validation', {})
    
    def connect(self):
        """Connect to database"""
        self.db.connect()
    
    def disconnect(self):
        """Disconnect from database"""
        self.db.disconnect()
    
    def validate_application(
        self,
        application_id: int,
        scheme_code: str
    ) -> Dict[str, Any]:
        """
        Validate an application
        
        Args:
            application_id: Application ID
            scheme_code: Scheme code
        
        Returns:
            Validation results
        """
        print(f"\n🔍 Validating application {application_id}")
        
        # Load application fields
        fields = self._load_application_fields(application_id)
        form_schema = self._load_form_schema(scheme_code)
        
        validation_results = {
            'application_id': application_id,
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'passed_checks': [],
            'failed_checks': []
        }
        
        # 1. Syntactic Validation
        syntactic_results = self._validate_syntactic(fields, form_schema)
        validation_results['errors'].extend(syntactic_results['errors'])
        validation_results['warnings'].extend(syntactic_results['warnings'])
        validation_results['passed_checks'].extend(syntactic_results['passed'])
        validation_results['failed_checks'].extend(syntactic_results['failed'])
        
        # 2. Semantic Validation
        semantic_results = self._validate_semantic(fields, scheme_code)
        validation_results['errors'].extend(semantic_results['errors'])
        validation_results['warnings'].extend(semantic_results['warnings'])
        validation_results['passed_checks'].extend(semantic_results['passed'])
        validation_results['failed_checks'].extend(semantic_results['failed'])
        
        # 3. Completeness Check
        completeness_results = self._validate_completeness(fields, form_schema)
        validation_results['errors'].extend(completeness_results['errors'])
        validation_results['warnings'].extend(completeness_results['warnings'])
        validation_results['passed_checks'].extend(completeness_results['passed'])
        validation_results['failed_checks'].extend(completeness_results['failed'])
        
        # 4. Pre-Fraud Checks (optional, for high-risk schemes)
        if self.validation_config.get('enable_fraud_checks', False):
            fraud_results = self._validate_fraud_checks(application_id, fields, scheme_code)
            validation_results['warnings'].extend(fraud_results['warnings'])
            validation_results['passed_checks'].extend(fraud_results['passed'])
            validation_results['failed_checks'].extend(fraud_results['failed'])
        
        # Determine overall validity
        validation_results['is_valid'] = len(validation_results['errors']) == 0
        
        # Store validation results
        self._store_validation_results(application_id, validation_results)
        
        # Update application status if invalid
        if not validation_results['is_valid']:
            self._update_application_status(application_id, 'validation_failed')
        
        print(f"✅ Validation complete: {'PASSED' if validation_results['is_valid'] else 'FAILED'}")
        print(f"   Errors: {len(validation_results['errors'])}, Warnings: {len(validation_results['warnings'])}")
        
        return validation_results
    
    def _load_application_fields(self, application_id: int) -> Dict[str, Any]:
        """Load application fields"""
        try:
            query = """
                SELECT field_name, field_value, field_type
                FROM application.application_fields
                WHERE application_id = %s
            """
            
            cursor = self.db.connection.cursor()
            cursor.execute(query, [application_id])
            rows = cursor.fetchall()
            cursor.close()
            
            fields = {}
            for field_name, field_value, field_type in rows:
                if isinstance(field_value, str):
                    try:
                        fields[field_name] = json.loads(field_value)
                    except:
                        fields[field_name] = field_value
                else:
                    fields[field_name] = field_value
            
            return fields
        
        except Exception as e:
            print(f"⚠️  Error loading application fields: {e}")
            return {}
    
    def _load_form_schema(self, scheme_code: str) -> Dict[str, Any]:
        """Load form schema"""
        try:
            query = """
                SELECT schema_definition, mandatory_fields, validation_rules, semantic_rules
                FROM application.scheme_form_schemas
                WHERE scheme_code = %s
                    AND is_active = true
                ORDER BY created_at DESC
                LIMIT 1
            """
            
            cursor = self.db.connection.cursor()
            cursor.execute(query, [scheme_code])
            row = cursor.fetchone()
            cursor.close()
            
            if row:
                schema_def, mandatory, validation_rules, semantic_rules = row
                if isinstance(schema_def, str):
                    schema_def = json.loads(schema_def)
                if isinstance(validation_rules, str):
                    validation_rules = json.loads(validation_rules) if validation_rules else {}
                if isinstance(semantic_rules, str):
                    semantic_rules = json.loads(semantic_rules) if semantic_rules else {}
                
                return {
                    'schema': schema_def,
                    'mandatory_fields': mandatory or [],
                    'validation_rules': validation_rules,
                    'semantic_rules': semantic_rules
                }
            
            return {'schema': {}, 'mandatory_fields': [], 'validation_rules': {}, 'semantic_rules': {}}
        
        except Exception as e:
            print(f"⚠️  Error loading form schema: {e}")
            return {'schema': {}, 'mandatory_fields': [], 'validation_rules': {}, 'semantic_rules': {}}
    
    def _validate_syntactic(self, fields: Dict[str, Any], form_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Perform syntactic validation (type, length, format)"""
        results = {
            'errors': [],
            'warnings': [],
            'passed': [],
            'failed': []
        }
        
        schema_props = form_schema.get('schema', {}).get('properties', {})
        
        for field_name, field_value in fields.items():
            if field_name not in schema_props:
                continue
            
            field_def = schema_props[field_name]
            field_type = field_def.get('type')
            
            # Type validation
            type_valid = self._validate_type(field_value, field_type)
            if not type_valid:
                results['errors'].append({
                    'field': field_name,
                    'type': 'syntactic',
                    'category': 'type_check',
                    'error_code': 'INVALID_TYPE',
                    'message': f'Field {field_name}: expected {field_type}, got {type(field_value).__name__}'
                })
                results['failed'].append(f'{field_name}_type')
            else:
                results['passed'].append(f'{field_name}_type')
            
            # Format validation (for strings)
            if field_type == 'string' and field_value:
                format_check = self._validate_format(field_value, field_def)
                if not format_check['valid']:
                    if format_check.get('required'):
                        results['errors'].append({
                            'field': field_name,
                            'type': 'syntactic',
                            'category': 'format_check',
                            'error_code': 'INVALID_FORMAT',
                            'message': format_check['message']
                        })
                        results['failed'].append(f'{field_name}_format')
                    else:
                        results['warnings'].append({
                            'field': field_name,
                            'message': format_check['message']
                        })
                else:
                    results['passed'].append(f'{field_name}_format')
            
            # Length validation
            if field_type == 'string' and field_value:
                length_check = self._validate_length(field_value, field_def)
                if not length_check['valid']:
                    results['errors'].append({
                        'field': field_name,
                        'type': 'syntactic',
                        'category': 'length_check',
                        'error_code': 'INVALID_LENGTH',
                        'message': length_check['message']
                    })
                    results['failed'].append(f'{field_name}_length')
                else:
                    results['passed'].append(f'{field_name}_length')
        
        return results
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate field type"""
        if value is None:
            return True  # Null is allowed (handled by required check)
        
        type_map = {
            'string': str,
            'number': (int, float),
            'integer': int,
            'boolean': bool,
            'array': list,
            'object': dict
        }
        
        expected = type_map.get(expected_type)
        if expected is None:
            return True
        
        if isinstance(expected, tuple):
            return isinstance(value, expected)
        
        return isinstance(value, expected)
    
    def _validate_format(self, value: str, field_def: Dict[str, Any]) -> Dict[str, Any]:
        """Validate string format"""
        format_type = field_def.get('format')
        pattern = field_def.get('pattern')
        
        if format_type == 'email':
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, value):
                return {
                    'valid': False,
                    'required': True,
                    'message': f'Invalid email format: {value}'
                }
        
        elif format_type == 'date':
            try:
                date_parser.parse(value)
            except:
                return {
                    'valid': False,
                    'required': True,
                    'message': f'Invalid date format: {value}'
                }
        
        if pattern:
            if not re.match(pattern, value):
                return {
                    'valid': False,
                    'required': True,
                    'message': f'Value does not match required pattern: {pattern}'
                }
        
        return {'valid': True}
    
    def _validate_length(self, value: str, field_def: Dict[str, Any]) -> Dict[str, Any]:
        """Validate string length"""
        min_length = field_def.get('minLength')
        max_length = field_def.get('maxLength')
        
        length = len(value)
        
        if min_length and length < min_length:
            return {
                'valid': False,
                'message': f'Length {length} is less than minimum {min_length}'
            }
        
        if max_length and length > max_length:
            return {
                'valid': False,
                'message': f'Length {length} exceeds maximum {max_length}'
            }
        
        return {'valid': True}
    
    def _validate_semantic(self, fields: Dict[str, Any], scheme_code: str) -> Dict[str, Any]:
        """Perform semantic validation (business rules)"""
        results = {
            'errors': [],
            'warnings': [],
            'passed': [],
            'failed': []
        }
        
        # Load semantic rules from schema
        form_schema = self._load_form_schema(scheme_code)
        semantic_rules = form_schema.get('semantic_rules', {})
        
        # Common semantic validations
        # Age validation (for pension schemes)
        if 'date_of_birth' in fields and scheme_code in ['OLD_AGE_PENSION', 'DISABILITY_PENSION']:
            age = self._calculate_age(fields['date_of_birth'])
            if scheme_code == 'OLD_AGE_PENSION' and age < 60:
                results['errors'].append({
                    'field': 'date_of_birth',
                    'type': 'semantic',
                    'category': 'business_rule',
                    'error_code': 'AGE_REQUIREMENT_NOT_MET',
                    'message': f'Age {age} is less than required 60 for old age pension'
                })
                results['failed'].append('age_requirement')
            else:
                results['passed'].append('age_requirement')
        
        # Mobile number format (Indian)
        if 'mobile_number' in fields:
            mobile = str(fields['mobile_number'])
            if not re.match(r'^[0-9]{10}$', mobile):
                results['errors'].append({
                    'field': 'mobile_number',
                    'type': 'semantic',
                    'category': 'format_check',
                    'error_code': 'INVALID_MOBILE_FORMAT',
                    'message': 'Mobile number must be 10 digits'
                })
                results['failed'].append('mobile_format')
            else:
                results['passed'].append('mobile_format')
        
        # Aadhaar format
        if 'aadhaar_number' in fields:
            aadhaar = str(fields['aadhaar_number'])
            if not re.match(r'^[0-9]{12}$', aadhaar):
                results['errors'].append({
                    'field': 'aadhaar_number',
                    'type': 'semantic',
                    'category': 'format_check',
                    'error_code': 'INVALID_AADHAAR_FORMAT',
                    'message': 'Aadhaar number must be 12 digits'
                })
                results['failed'].append('aadhaar_format')
            else:
                results['passed'].append('aadhaar_format')
        
        return results
    
    def _validate_completeness(self, fields: Dict[str, Any], form_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate completeness (mandatory fields)"""
        results = {
            'errors': [],
            'warnings': [],
            'passed': [],
            'failed': []
        }
        
        mandatory_fields = form_schema.get('mandatory_fields', [])
        
        for field_name in mandatory_fields:
            if field_name not in fields or fields[field_name] is None or fields[field_name] == '':
                results['errors'].append({
                    'field': field_name,
                    'type': 'completeness',
                    'category': 'missing_field',
                    'error_code': 'MANDATORY_FIELD_MISSING',
                    'message': f'Mandatory field {field_name} is missing or empty'
                })
                results['failed'].append(f'{field_name}_required')
            else:
                results['passed'].append(f'{field_name}_required')
        
        return results
    
    def _validate_fraud_checks(self, application_id: int, fields: Dict[str, Any], scheme_code: str) -> Dict[str, Any]:
        """Perform pre-fraud checks"""
        results = {
            'warnings': [],
            'passed': [],
            'failed': []
        }
        
        fraud_config = self.validation_config.get('fraud_checks', {})
        
        # Duplicate bank account check
        if fraud_config.get('duplicate_bank_account') and 'bank_account_number' in fields:
            if self._check_duplicate_bank_account(application_id, fields['bank_account_number']):
                results['warnings'].append({
                    'field': 'bank_account_number',
                    'type': 'fraud_check',
                    'category': 'duplicate_account',
                    'message': 'Bank account number is used in another application'
                })
                results['failed'].append('duplicate_bank_account')
            else:
                results['passed'].append('duplicate_bank_account')
        
        return results
    
    def _check_duplicate_bank_account(self, application_id: int, bank_account: str) -> bool:
        """Check for duplicate bank account"""
        try:
            query = """
                SELECT COUNT(*) as count
                FROM application.application_fields af1
                JOIN application.applications a1 ON af1.application_id = a1.application_id
                WHERE af1.field_name = 'bank_account_number'
                    AND af1.field_value::text = %s
                    AND a1.application_id != %s
                    AND a1.status IN ('submitted', 'pending_submission')
            """
            
            cursor = self.db.connection.cursor()
            cursor.execute(query, [json.dumps(bank_account), application_id])
            count = cursor.fetchone()[0]
            cursor.close()
            
            return count > 0
        
        except:
            return False
    
    def _calculate_age(self, dob: Any) -> int:
        """Calculate age from date of birth"""
        try:
            if isinstance(dob, str):
                birth_date = date_parser.parse(dob).date()
            else:
                birth_date = dob
            
            today = datetime.now().date()
            age = today.year - birth_date.year
            if (today.month, today.day) < (birth_date.month, birth_date.day):
                age -= 1
            return age
        except:
            return 0
    
    def _store_validation_results(self, application_id: int, results: Dict[str, Any]):
        """Store validation results in database"""
        try:
            cursor = self.db.connection.cursor()
            
            # Store errors
            for error in results['errors']:
                query = """
                    INSERT INTO application.application_validation_results (
                        application_id,
                        validation_type,
                        validation_category,
                        is_valid,
                        severity,
                        field_name,
                        error_code,
                        error_message,
                        error_details
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    application_id,
                    error['type'],
                    error['category'],
                    False,
                    'error',
                    error.get('field'),
                    error['error_code'],
                    error['message'],
                    json.dumps(error)
                ))
            
            # Store warnings
            for warning in results['warnings']:
                query = """
                    INSERT INTO application.application_validation_results (
                        application_id,
                        validation_type,
                        validation_category,
                        is_valid,
                        severity,
                        field_name,
                        error_code,
                        error_message,
                        error_details
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    application_id,
                    warning.get('type', 'validation'),
                    warning.get('category', 'warning'),
                    True,  # Warning is not an error
                    'warning',
                    warning.get('field'),
                    warning.get('error_code', 'WARNING'),
                    warning['message'],
                    json.dumps(warning)
                ))
            
            self.db.connection.commit()
            cursor.close()
        
        except Exception as e:
            print(f"⚠️  Error storing validation results: {e}")
            self.db.connection.rollback()
    
    def _update_application_status(self, application_id: int, status: str):
        """Update application status"""
        try:
            query = """
                UPDATE application.applications
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE application_id = %s
            """
            
            cursor = self.db.connection.cursor()
            cursor.execute(query, [status, application_id])
            self.db.connection.commit()
            cursor.close()
        
        except Exception as e:
            print(f"⚠️  Error updating application status: {e}")
            self.db.connection.rollback()

