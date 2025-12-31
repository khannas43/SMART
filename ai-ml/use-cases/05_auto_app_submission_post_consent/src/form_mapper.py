"""
Form Mapper Service
Maps data from Golden Records and 360° Profiles to scheme-specific form fields
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import sys
from pathlib import Path
import yaml
import json
import pandas as pd
from jinja2 import Template

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class FormMapper:
    """Maps data from GR/360° to form fields using mapping rules"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Form Mapper"""
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
    
    def map_form_fields(
        self,
        application_id: int,
        family_id: str,
        scheme_code: str,
        member_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Map data to form fields for an application
        
        Args:
            application_id: Application ID
            family_id: Family ID
            scheme_code: Scheme code
            member_id: Member ID (for individual-centric schemes)
        
        Returns:
            Mapping result with mapped fields and source tracking
        """
        print(f"\n🔄 Mapping form fields for application {application_id}")
        
        # Load data sources
        gr_data = self._load_golden_record(family_id, member_id)
        profile_data = self._load_360_profile(family_id)
        eligibility_data = self._load_eligibility_snapshot(family_id, scheme_code)
        
        # Load form schema and mappings
        form_schema = self._load_form_schema(scheme_code)
        mappings = self._load_field_mappings(scheme_code)
        
        # Build context for mapping
        context = {
            'GR': gr_data,
            'PROFILE_360': profile_data,
            'ELIGIBILITY': eligibility_data,
            'family_id': family_id,
            'member_id': member_id,
            'scheme_code': scheme_code
        }
        
        # Apply mappings
        mapped_fields = {}
        field_sources = {}
        
        for mapping in sorted(mappings, key=lambda x: x['priority']):
            target_field = mapping['target_field_name']
            
            # Skip if already mapped (lower priority mappings come first)
            if target_field in mapped_fields:
                continue
            
            try:
                value, source = self._apply_mapping(mapping, context)
                if value is not None:
                    mapped_fields[target_field] = value
                    field_sources[target_field] = {
                        'source_type': source,
                        'mapping_id': mapping['mapping_id'],
                        'mapping_type': mapping['mapping_type']
                    }
            except Exception as e:
                print(f"⚠️  Error mapping field {target_field}: {e}")
        
        # Store mapped fields in database
        self._store_application_fields(application_id, mapped_fields, field_sources)
        
        # Build complete form data
        form_data = self._build_form_data(mapped_fields, form_schema)
        
        print(f"✅ Mapped {len(mapped_fields)} fields")
        
        return {
            'success': True,
            'application_id': application_id,
            'mapped_fields_count': len(mapped_fields),
            'form_data': form_data,
            'field_sources': field_sources
        }
    
    def _load_golden_record(self, family_id: str, member_id: Optional[str] = None) -> Dict[str, Any]:
        """Load Golden Record data"""
        try:
            if 'golden_records' not in self.external_dbs:
                return {}
            
            gr_db = self.external_dbs['golden_records']
            
            # Query Golden Records table
            query = """
                SELECT *
                FROM golden_records
                WHERE family_id::text = %s
                    AND status = 'active'
                ORDER BY updated_at DESC
                LIMIT 1
            """
            
            cursor = gr_db.connection.cursor()
            cursor.execute(query, [family_id])
            row = cursor.fetchone()
            
            if row:
                columns = [desc[0] for desc in cursor.description]
                gr_data = dict(zip(columns, row))
            else:
                gr_data = {}
            
            cursor.close()
            return gr_data
        
        except Exception as e:
            print(f"⚠️  Error loading Golden Record: {e}")
            return {}
    
    def _load_360_profile(self, family_id: str) -> Dict[str, Any]:
        """Load 360° Profile data"""
        try:
            if 'profile_360' not in self.external_dbs:
                return {}
            
            profile_db = self.external_dbs['profile_360']
            
            query = """
                SELECT 
                    profile_data,
                    income_band,
                    cluster_id,
                    vulnerability_level
                FROM profile_360
                WHERE family_id::text = %s
                ORDER BY updated_at DESC
                LIMIT 1
            """
            
            cursor = profile_db.connection.cursor()
            cursor.execute(query, [family_id])
            row = cursor.fetchone()
            cursor.close()
            
            if row:
                profile_data, income_band, cluster_id, vulnerability_level = row
                
                # Parse profile_data if it's JSON
                if isinstance(profile_data, str):
                    try:
                        profile_dict = json.loads(profile_data)
                    except:
                        profile_dict = {}
                elif isinstance(profile_data, dict):
                    profile_dict = profile_data
                else:
                    profile_dict = {}
                
                return {
                    **profile_dict,
                    'income_band': income_band,
                    'cluster_id': cluster_id,
                    'vulnerability_level': vulnerability_level
                }
            
            return {}
        
        except Exception as e:
            print(f"⚠️  Error loading 360° Profile: {e}")
            return {}
    
    def _load_eligibility_snapshot(self, family_id: str, scheme_code: str) -> Dict[str, Any]:
        """Load eligibility snapshot data"""
        try:
            if 'eligibility' not in self.external_dbs:
                return {}
            
            eligibility_db = self.external_dbs['eligibility']
            
            query = """
                SELECT 
                    eligibility_score,
                    evaluation_status,
                    rules_passed,
                    rules_failed,
                    reason_codes
                FROM eligibility.eligibility_snapshots
                WHERE family_id::text = %s
                    AND scheme_code = %s
                ORDER BY evaluation_timestamp DESC
                LIMIT 1
            """
            
            cursor = eligibility_db.connection.cursor()
            cursor.execute(query, [family_id, scheme_code])
            row = cursor.fetchone()
            cursor.close()
            
            if row:
                score, status, rules_passed, rules_failed, reason_codes = row
                return {
                    'eligibility_score': float(score) if score else 0.0,
                    'evaluation_status': status,
                    'rules_passed': rules_passed or [],
                    'rules_failed': rules_failed or [],
                    'reason_codes': reason_codes or []
                }
            
            return {}
        
        except Exception as e:
            print(f"⚠️  Error loading eligibility snapshot: {e}")
            return {}
    
    def _load_form_schema(self, scheme_code: str) -> Dict[str, Any]:
        """Load form schema for scheme"""
        try:
            query = """
                SELECT schema_definition, mandatory_fields, optional_fields
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
                schema_def, mandatory, optional = row
                if isinstance(schema_def, str):
                    schema_def = json.loads(schema_def)
                return {
                    'schema': schema_def,
                    'mandatory_fields': mandatory or [],
                    'optional_fields': optional or []
                }
            
            return {'schema': {}, 'mandatory_fields': [], 'optional_fields': []}
        
        except Exception as e:
            print(f"⚠️  Error loading form schema: {e}")
            return {'schema': {}, 'mandatory_fields': [], 'optional_fields': []}
    
    def _load_field_mappings(self, scheme_code: str) -> List[Dict[str, Any]]:
        """Load field mappings for scheme"""
        try:
            query = """
                SELECT 
                    mapping_id,
                    target_field_name,
                    target_field_path,
                    mapping_type,
                    priority,
                    source_type,
                    source_field,
                    source_fields,
                    transformation_expression,
                    transformation_type,
                    condition_expression,
                    condition_type,
                    default_value
                FROM application.scheme_field_mappings
                WHERE scheme_code = %s
                    AND is_active = true
                ORDER BY priority ASC, mapping_id
            """
            
            cursor = self.db.connection.cursor()
            cursor.execute(query, [scheme_code])
            
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            cursor.close()
            
            mappings = []
            for row in rows:
                mapping = dict(zip(columns, row))
                # Parse JSON fields
                if mapping.get('source_fields') and isinstance(mapping['source_fields'], str):
                    mapping['source_fields'] = json.loads(mapping['source_fields'])
                if mapping.get('default_value') and isinstance(mapping['default_value'], str):
                    mapping['default_value'] = json.loads(mapping['default_value'])
                mappings.append(mapping)
            
            return mappings
        
        except Exception as e:
            print(f"⚠️  Error loading field mappings: {e}")
            return []
    
    def _apply_mapping(self, mapping: Dict[str, Any], context: Dict[str, Any]) -> tuple:
        """Apply a single mapping rule"""
        mapping_type = mapping['mapping_type']
        source_type = mapping['source_type']
        
        # Check condition if present
        if mapping.get('condition_expression'):
            if not self._evaluate_condition(mapping['condition_expression'], context):
                return None, None
        
        # Get source value based on mapping type
        if mapping_type == 'direct':
            value = self._get_direct_value(mapping, context)
        
        elif mapping_type == 'derived':
            value = self._get_derived_value(mapping, context)
        
        elif mapping_type == 'concatenated':
            value = self._get_concatenated_value(mapping, context)
        
        elif mapping_type == 'relationship':
            value = self._get_relationship_value(mapping, context)
        
        elif mapping_type == 'conditional':
            value = self._get_conditional_value(mapping, context)
        
        else:
            value = None
        
        # Apply transformation if needed
        if value is not None and mapping.get('transformation_expression'):
            value = self._apply_transformation(mapping['transformation_expression'], value, context)
        
        # Use default if value is None
        if value is None and mapping.get('default_value'):
            value = mapping['default_value']
        
        return value, source_type
    
    def _get_direct_value(self, mapping: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Get direct mapped value"""
        source_field = mapping['source_field']
        source_type = mapping['source_type']
        
        # Navigate to source
        source_data = context.get(source_type, {})
        if not source_data:
            return None
        
        # Handle nested field paths (e.g., "GR.first_name" or "PROFILE_360.income_band")
        if '.' in source_field:
            parts = source_field.split('.', 1)
            if parts[0] == source_type:
                field_path = parts[1] if len(parts) > 1 else parts[0]
            else:
                field_path = source_field
        else:
            field_path = source_field
        
        # Navigate nested structure
        value = source_data
        for part in field_path.split('.'):
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None
            if value is None:
                return None
        
        return value
    
    def _get_derived_value(self, mapping: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Get derived value using transformation"""
        # For derived, we still get the source value first
        source_value = self._get_direct_value(mapping, context)
        
        if source_value is None:
            return None
        
        # Apply transformation
        transformation = mapping.get('transformation_expression')
        if transformation:
            return self._apply_transformation(transformation, source_value, context)
        
        return source_value
    
    def _get_concatenated_value(self, mapping: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Get concatenated value from multiple sources"""
        source_fields = mapping.get('source_fields', [])
        if not source_fields:
            return None
        
        values = []
        for field in source_fields:
            # Parse source field (e.g., "GR.first_name")
            if '.' in field:
                source_type, field_path = field.split('.', 1)
            else:
                source_type = mapping['source_type']
                field_path = field
            
            source_data = context.get(source_type, {})
            if isinstance(source_data, dict):
                value = source_data.get(field_path)
                if value:
                    values.append(str(value))
        
        if not values:
            return None
        
        # Join with space (can be customized)
        return ' '.join(values)
    
    def _get_relationship_value(self, mapping: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Get relationship-based value (e.g., select beneficiary from family)"""
        # This would require family structure analysis
        # For now, return the member_id if available
        return context.get('member_id')
    
    def _get_conditional_value(self, mapping: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Get conditional value based on conditions"""
        # Evaluate condition and return appropriate value
        condition = mapping.get('condition_expression')
        if condition and self._evaluate_condition(condition, context):
            return self._get_direct_value(mapping, context)
        return None
    
    def _apply_transformation(self, expression: str, value: Any, context: Dict[str, Any]) -> Any:
        """Apply transformation expression"""
        try:
            # Simple Jinja2 template transformation
            template = Template(expression)
            return template.render(value=value, context=context, **context)
        except:
            # Fallback to Python eval for simple expressions (use with caution)
            try:
                safe_dict = {'value': value, 'context': context, **context}
                return eval(expression, {"__builtins__": {}}, safe_dict)
            except:
                return value
    
    def _evaluate_condition(self, expression: str, context: Dict[str, Any]) -> bool:
        """Evaluate condition expression"""
        try:
            # Simple Python eval (use with caution in production)
            safe_dict = {**context}
            result = eval(expression, {"__builtins__": {}}, safe_dict)
            return bool(result)
        except:
            return False
    
    def _store_application_fields(
        self,
        application_id: int,
        mapped_fields: Dict[str, Any],
        field_sources: Dict[str, Any]
    ):
        """Store mapped fields in database with source tracking"""
        try:
            cursor = self.db.connection.cursor()
            
            for field_name, field_value in mapped_fields.items():
                source_info = field_sources.get(field_name, {})
                
                # Determine field type
                if isinstance(field_value, bool):
                    field_type = 'boolean'
                elif isinstance(field_value, (int, float)):
                    field_type = 'number'
                elif isinstance(field_value, list):
                    field_type = 'array'
                elif isinstance(field_value, dict):
                    field_type = 'object'
                else:
                    field_type = 'string'
                
                query = """
                    INSERT INTO application.application_fields (
                        application_id,
                        field_name,
                        field_value,
                        field_type,
                        source_type,
                        source_detail,
                        mapping_type,
                        mapping_rule_id
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(query, (
                    application_id,
                    field_name,
                    json.dumps(field_value),
                    field_type,
                    source_info.get('source_type', 'UNKNOWN'),
                    json.dumps(source_info),
                    source_info.get('mapping_type'),
                    source_info.get('mapping_id')
                ))
            
            self.db.connection.commit()
            cursor.close()
        
        except Exception as e:
            print(f"⚠️  Error storing application fields: {e}")
            self.db.connection.rollback()
    
    def _build_form_data(self, mapped_fields: Dict[str, Any], form_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Build complete form data structure"""
        # For now, return flat structure
        # Can be enhanced to match schema structure if needed
        return mapped_fields

