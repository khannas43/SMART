"""
Nudge Generator
Use Case ID: AI-PLATFORM-09

Generates context-aware nudges and recommendations for priority households.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class NudgeGenerator:
    """
    Nudge Generator Service
    
    Generates context-aware nudges:
    - Scheme suggestions
    - Action reminders
    - Update requests
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Nudge Generator"""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "use_case_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Configuration
        nudge_config = self.config.get('nudge_generation', {})
        self.max_nudges = nudge_config.get('max_nudges_per_household', 3)
        self.priority_levels = nudge_config.get('nudge_priority_levels', ['HIGH', 'MEDIUM', 'LOW'])
        self.channel_config = self.config.get('nudge_channels', {})
        
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
        
        # External database connections
        external_dbs = yaml.safe_load(open(db_config_path, 'r')).get('external_databases', {})
        self.external_dbs = {}
        for name, ext_config in external_dbs.items():
            self.external_dbs[name] = DBConnector(
                host=ext_config['host'],
                port=ext_config['port'],
                database=ext_config['name'],
                user=ext_config['user'],
                password=ext_config['password']
            )
    
    def connect(self):
        """Connect to databases"""
        self.db.connect()
        for ext_db in self.external_dbs.values():
            ext_db.connect()
    
    def disconnect(self):
        """Disconnect from databases"""
        self.db.disconnect()
        for ext_db in self.external_dbs.values():
            ext_db.disconnect()
    
    def generate_nudges(
        self,
        family_id: str,
        gap_analysis: Dict[str, Any],
        priority_segments: List[str],
        location_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate nudges for a priority household
        
        Args:
            family_id: Family ID
            gap_analysis: Inclusion gap analysis results
            priority_segments: Priority segments identified
            location_data: Location information
        
        Returns:
            List of nudge recommendations
        """
        nudges = []
        
        # Get gap schemes (eligible but not enrolled)
        gap_schemes = gap_analysis.get('gap_schemes', [])
        
        # Generate scheme-specific nudges
        for scheme_code in gap_schemes[:self.max_nudges]:
            nudge = self._generate_scheme_nudge(
                family_id, scheme_code, gap_analysis, priority_segments
            )
            if nudge:
                nudges.append(nudge)
        
        # Generate action-based nudges
        action_nudges = self._generate_action_nudges(
            family_id, gap_analysis, priority_segments
        )
        nudges.extend(action_nudges[:max(1, self.max_nudges - len(nudges))])
        
        # Select channel for each nudge
        for nudge in nudges:
            nudge['channel'] = self._select_channel(nudge, priority_segments, location_data)
        
        return nudges[:self.max_nudges]
    
    def _generate_scheme_nudge(
        self,
        family_id: str,
        scheme_code: str,
        gap_analysis: Dict[str, Any],
        priority_segments: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Generate nudge for a specific scheme"""
        try:
            # Get scheme name
            scheme_name = self._get_scheme_name(scheme_code)
            
            # Determine priority based on scheme impact and vulnerability
            priority = self._determine_nudge_priority(scheme_code, priority_segments)
            
            # Generate message
            message = self._generate_nudge_message(scheme_code, scheme_name, priority_segments)
            
            # Generate recommended actions
            actions = self._generate_recommended_actions(scheme_code, priority_segments)
            
            return {
                'nudge_type': 'SCHEME_SUGGESTION',
                'nudge_message': message,
                'recommended_actions': actions,
                'scheme_codes': [scheme_code],
                'priority_level': priority,
                'family_id': family_id
            }
        
        except Exception as e:
            print(f"⚠️  Error generating scheme nudge: {e}")
            return None
    
    def _generate_action_nudges(
        self,
        family_id: str,
        gap_analysis: Dict[str, Any],
        priority_segments: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate action-based nudges"""
        nudges = []
        
        # Check for disability-related actions
        if 'PWD' in priority_segments:
            nudges.append({
                'nudge_type': 'ACTION_REMINDER',
                'nudge_message': 'Consider updating or obtaining your disability certificate to access disability-related benefits',
                'recommended_actions': ['Update disability certificate', 'Apply for disability pension'],
                'priority_level': 'HIGH',
                'family_id': family_id
            })
        
        # Check for education-related actions
        if any('EDUCATION' in s or 'STUDENT' in s for s in priority_segments):
            nudges.append({
                'nudge_type': 'ACTION_REMINDER',
                'nudge_message': 'Educational support schemes may be available for your family members',
                'recommended_actions': ['Check scholarship eligibility', 'Enroll in education schemes'],
                'priority_level': 'MEDIUM',
                'family_id': family_id
            })
        
        return nudges
    
    def _get_scheme_name(self, scheme_code: str) -> str:
        """Get scheme name"""
        try:
            conn = self.external_dbs['golden_records'].connection
            cursor = conn.cursor()
            
            # Try to get from scheme_master (if accessible via public schema)
            cursor.execute("""
                SELECT scheme_name
                FROM public.scheme_master
                WHERE scheme_code = %s
                LIMIT 1
            """, (scheme_code,))
            
            row = cursor.fetchone()
            cursor.close()
            
            return row[0] if row else scheme_code
        
        except Exception:
            return scheme_code
    
    def _determine_nudge_priority(
        self,
        scheme_code: str,
        priority_segments: List[str]
    ) -> str:
        """Determine nudge priority level"""
        # High priority for critical schemes (health, disability) or high vulnerability
        critical_schemes = ['DISABILITY', 'HEALTH', 'PENSION']
        is_critical = any(keyword in scheme_code.upper() for keyword in critical_schemes)
        
        high_priority_segments = ['PWD', 'ELDERLY_ALONE', 'TRIBAL']
        is_high_vulnerability = any(seg in high_priority_segments for seg in priority_segments)
        
        if is_critical or is_high_vulnerability:
            return 'HIGH'
        elif len(priority_segments) > 0:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_nudge_message(
        self,
        scheme_code: str,
        scheme_name: str,
        priority_segments: List[str]
    ) -> str:
        """Generate nudge message"""
        # Personalized message based on segments
        if 'PWD' in priority_segments:
            return f"You might be eligible for {scheme_name}. Based on your situation, this scheme may provide important support."
        elif 'SINGLE_WOMAN' in priority_segments:
            return f"{scheme_name} may be available for your household. Consider checking your eligibility."
        elif 'TRIBAL' in priority_segments:
            return f"As a tribal household, you may be eligible for {scheme_name}. Please check your eligibility."
        else:
            return f"You may be eligible for {scheme_name}. Check your eligibility and apply if interested."
    
    def _generate_recommended_actions(
        self,
        scheme_code: str,
        priority_segments: List[str]
    ) -> List[str]:
        """Generate recommended actions"""
        actions = []
        
        # Scheme-specific actions
        if 'DISABILITY' in scheme_code.upper():
            actions.append('Apply for disability pension')
            actions.append('Update disability certificate')
        elif 'EDUCATION' in scheme_code.upper() or 'SCHOLARSHIP' in scheme_code.upper():
            actions.append('Enroll in education scholarship')
            actions.append('Submit education documents')
        elif 'PENSION' in scheme_code.upper():
            actions.append('Apply for pension scheme')
            actions.append('Complete pension application')
        else:
            actions.append(f'Apply for {scheme_code}')
            actions.append('Check eligibility requirements')
        
        return actions[:3]  # Limit to 3 actions
    
    def _select_channel(
        self,
        nudge: Dict[str, Any],
        priority_segments: List[str],
        location_data: Dict[str, Any]
    ) -> str:
        """Select delivery channel based on nudge and context"""
        priority = nudge.get('priority_level', 'MEDIUM')
        block_id = location_data.get('block_id', '')
        
        # High priority: Use multiple channels
        if priority == 'HIGH':
            # Prefer portal/app, fallback to SMS
            if self.channel_config.get('portal', {}).get('enabled'):
                return 'PORTAL'
            elif self.channel_config.get('mobile_app', {}).get('enabled'):
                return 'MOBILE_APP'
            else:
                return 'SMS'
        
        # Remote areas: Field worker
        if 'REMOTE_GEOGRAPHY' in priority_segments or 'TRIBAL' in priority_segments:
            if self.channel_config.get('field_worker', {}).get('enabled'):
                return 'FIELD_WORKER'
        
        # Elderly alone: Prefer field worker
        if 'ELDERLY_ALONE' in priority_segments:
            if self.channel_config.get('field_worker', {}).get('enabled'):
                return 'FIELD_WORKER'
        
        # Default: Portal
        if self.channel_config.get('portal', {}).get('enabled'):
            return 'PORTAL'
        elif self.channel_config.get('mobile_app', {}).get('enabled'):
            return 'MOBILE_APP'
        else:
            return 'SMS'

