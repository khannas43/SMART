"""
Explanation Generator
Use Case ID: AI-PLATFORM-08

Generates human-readable explanations for eligibility status using NLG templates.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
import json

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class ExplanationGenerator:
    """
    Explanation Generator Service
    
    Generates human-readable explanations for:
    - Why a scheme is eligible/not eligible
    - What conditions are met/not met
    - Next steps and recommendations
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Explanation Generator"""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "use_case_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Configuration
        self.explanation_config = self.config.get('explanation', {})
        self.max_length = self.explanation_config.get('max_explanation_length', 200)
        self.include_rule_details = self.explanation_config.get('include_rule_details', True)
        self.include_next_steps = self.explanation_config.get('include_next_steps', True)
        self.supported_languages = self.explanation_config.get('supported_languages', ['en'])
        
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
    
    def generate_explanation(
        self,
        eval_result: Dict[str, Any],
        language: str = 'en'
    ) -> Dict[str, Any]:
        """
        Generate explanation for eligibility result
        
        Args:
            eval_result: Eligibility evaluation result
            language: Language code (en, hi, etc.)
        
        Returns:
            Dictionary with explanation text, template ID, and tokens
        """
        status = eval_result.get('eligibility_status')
        scheme_code = eval_result.get('scheme_code')
        met_rules = eval_result.get('met_rules', [])
        failed_rules = eval_result.get('failed_rules', [])
        rule_evaluations = eval_result.get('rule_evaluations', {})
        
        # Get template
        template = self._get_template(status, language)
        if not template:
            # Fallback template
            explanation_text = self._generate_fallback_explanation(eval_result)
            return {
                'explanation_text': explanation_text,
                'explanation_template_id': 'FALLBACK',
                'explanation_tokens': {},
                'next_steps': self._generate_next_steps(status, failed_rules)
            }
        
        # Extract tokens from rule evaluations
        tokens = self._extract_tokens(eval_result, met_rules, failed_rules)
        
        # Fill template
        explanation_text = self._fill_template(template.get('template_text', ''), tokens)
        
        # Generate next steps
        next_steps = self._generate_next_steps(status, failed_rules, scheme_code)
        
        return {
            'explanation_text': explanation_text[:self.max_length],
            'explanation_template_id': template.get('template_key', ''),
            'explanation_tokens': tokens,
            'next_steps': next_steps
        }
    
    def _get_template(self, status: str, language: str) -> Optional[Dict[str, Any]]:
        """Get explanation template"""
        conn = self.db.connection
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT template_key, template_text, placeholders
                FROM eligibility_checker.explanation_templates
                WHERE applies_to_status = %s
                  AND language = %s
                  AND is_active = TRUE
                ORDER BY version DESC
                LIMIT 1
            """, (status, language))
            
            row = cursor.fetchone()
            cursor.close()
            
            if row:
                return {
                    'template_key': row[0],
                    'template_text': row[1],
                    'placeholders': row[2]
                }
            
            # Try English fallback
            if language != 'en':
                cursor.execute("""
                    SELECT template_key, template_text, placeholders
                    FROM eligibility_checker.explanation_templates
                    WHERE applies_to_status = %s
                      AND language = 'en'
                      AND is_active = TRUE
                    ORDER BY version DESC
                    LIMIT 1
                """, (status,))
                
                row = cursor.fetchone()
                cursor.close()
                
                if row:
                    return {
                        'template_key': row[0],
                        'template_text': row[1],
                        'placeholders': row[2]
                    }
            
            return None
        
        except Exception as e:
            print(f"⚠️  Error fetching template: {e}")
            return None
    
    def _extract_tokens(
        self,
        eval_result: Dict[str, Any],
        met_rules: List[str],
        failed_rules: List[str]
    ) -> Dict[str, Any]:
        """Extract tokens/placeholders from rule evaluations"""
        tokens = {}
        
        # Extract from rule evaluations
        rule_evals = eval_result.get('rule_evaluations', {})
        if isinstance(rule_evals, dict):
            # Try to extract common tokens
            # Age
            for rule_name in met_rules + failed_rules:
                if 'age' in rule_name.lower():
                    tokens['age'] = 'your age'  # Would be extracted from actual data
            
            # Income
            for rule_name in met_rules + failed_rules:
                if 'income' in rule_name.lower():
                    tokens['income_band'] = 'your income level'  # Would be extracted from actual data
            
            # Category
            for rule_name in met_rules + failed_rules:
                if 'category' in rule_name.lower() or 'caste' in rule_name.lower():
                    tokens['category'] = 'your category'  # Would be extracted from actual data
        
        return tokens
    
    def _fill_template(self, template_text: str, tokens: Dict[str, Any]) -> str:
        """Fill template with tokens"""
        result = template_text
        
        for key, value in tokens.items():
            placeholder = '{' + key + '}'
            result = result.replace(placeholder, str(value))
        
        return result
    
    def _generate_fallback_explanation(self, eval_result: Dict[str, Any]) -> str:
        """Generate fallback explanation if template not found"""
        status = eval_result.get('eligibility_status')
        scheme_code = eval_result.get('scheme_code')
        
        if status == 'ELIGIBLE':
            return f"You are eligible for {scheme_code} based on the eligibility criteria."
        elif status == 'POSSIBLE_ELIGIBLE':
            return f"You might be eligible for {scheme_code}. Please verify with official documents."
        else:
            return f"You are not eligible for {scheme_code} based on the current eligibility criteria."
    
    def _generate_next_steps(
        self,
        status: str,
        failed_rules: List[str],
        scheme_code: Optional[str] = None
    ) -> List[str]:
        """Generate next steps based on eligibility status"""
        next_steps = []
        
        if status == 'ELIGIBLE':
            next_steps.append("You can apply for this scheme")
            next_steps.append("Gather required documents as per scheme guidelines")
            next_steps.append("Submit application through portal or office")
        
        elif status == 'POSSIBLE_ELIGIBLE':
            next_steps.append("Verify your details with official documents")
            next_steps.append("Contact scheme office for confirmation")
            next_steps.append("Consider logging in with Jan Aadhaar for accurate results")
        
        else:
            next_steps.append("Review the eligibility criteria")
            if failed_rules:
                next_steps.append(f"Address the following: {', '.join(failed_rules[:2])}")
            next_steps.append("Check again if your situation changes")
        
        return next_steps

