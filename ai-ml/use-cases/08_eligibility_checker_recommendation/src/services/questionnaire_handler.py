"""
Questionnaire Handler
Use Case ID: AI-PLATFORM-08

Handles guest user questionnaires for eligibility checking.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
import json

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class QuestionnaireHandler:
    """
    Questionnaire Handler Service
    
    Manages questionnaire templates and processes guest user responses.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Questionnaire Handler"""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "use_case_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Database
        db_config_path = Path(__file__).parent.parent.parent / "config" / "db_config.yaml"
        with open(db_config_path, 'r') as f:
            db_config = yaml.safe_load(f)['database']
        
        self.db = DBConnector(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['name'],
            user=db_config['user'],
            password=db_config['password']
        )
    
    def connect(self):
        """Connect to database"""
        self.db.connect()
    
    def disconnect(self):
        """Disconnect from database"""
        self.db.disconnect()
    
    def get_questionnaire(self, template_name: str = 'default_guest_questionnaire') -> Dict[str, Any]:
        """Get questionnaire template"""
        conn = self.db.connection
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT template_id, template_name, template_version, questions, question_flow
                FROM eligibility_checker.questionnaire_templates
                WHERE template_name = %s
                  AND is_active = TRUE
                ORDER BY template_version DESC
                LIMIT 1
            """, (template_name,))
            
            row = cursor.fetchone()
            cursor.close()
            
            if row:
                return {
                    'template_id': row[0],
                    'template_name': row[1],
                    'template_version': row[2],
                    'questions': row[3] if isinstance(row[3], dict) else json.loads(row[3]) if row[3] else [],
                    'question_flow': row[4] if isinstance(row[4], dict) else json.loads(row[4]) if row[4] else None
                }
            
            return {
                'template_name': template_name,
                'questions': [],
                'question_flow': None
            }
        
        except Exception as e:
            print(f"⚠️  Error fetching questionnaire: {e}")
            return {
                'template_name': template_name,
                'questions': [],
                'question_flow': None
            }
    
    def validate_responses(
        self,
        responses: Dict[str, Any],
        questions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate questionnaire responses
        
        Returns:
            Dictionary with validation result and errors
        """
        errors = []
        validated = {}
        
        for question in questions:
            q_id = question.get('id')
            required = question.get('required', False)
            q_type = question.get('type', 'text')
            
            value = responses.get(q_id)
            
            # Check required fields
            if required and (value is None or value == ''):
                errors.append(f"{question.get('question', q_id)} is required")
                continue
            
            # Type validation
            if value is not None and value != '':
                if q_type == 'number':
                    try:
                        validated[q_id] = int(value)
                    except ValueError:
                        errors.append(f"{question.get('question', q_id)} must be a number")
                elif q_type == 'boolean':
                    validated[q_id] = bool(value) if isinstance(value, bool) else str(value).lower() in ['true', 'yes', '1']
                else:
                    validated[q_id] = str(value)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'validated_responses': validated
        }

