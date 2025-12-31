"""
Inclusion Orchestrator
Use Case ID: AI-PLATFORM-09

Main orchestrator service that coordinates inclusion detection, exception flagging,
and nudge generation.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import yaml

# Import services
from services.priority_household_identifier import PriorityHouseholdIdentifier
from detectors.exception_pattern_detector import ExceptionPatternDetector
from generators.nudge_generator import NudgeGenerator


class InclusionOrchestrator:
    """
    Inclusion Orchestrator Service
    
    Coordinates:
    - Priority household identification
    - Exception pattern detection
    - Nudge generation and delivery
    - Priority list generation for field workers
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Inclusion Orchestrator"""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "use_case_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize services
        self.priority_identifier = PriorityHouseholdIdentifier(config_path)
        self.exception_detector = ExceptionPatternDetector(config_path)
        self.nudge_generator = NudgeGenerator(config_path)
        
        # Database (for direct queries)
        db_config_path = Path(__file__).parent.parent.parent / "config" / "db_config.yaml"
        with open(db_config_path, 'r') as f:
            db_config = yaml.safe_load(f)['database']
        
        from db_connector import DBConnector
        self.db = DBConnector(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['name'],
            user=db_config['user'],
            password=db_config['password']
        )
    
    def connect(self):
        """Connect all services to databases"""
        self.priority_identifier.connect()
        self.exception_detector.connect()
        self.nudge_generator.connect()
        self.db.connect()
    
    def disconnect(self):
        """Disconnect all services from databases"""
        self.priority_identifier.disconnect()
        self.exception_detector.disconnect()
        self.nudge_generator.disconnect()
        self.db.disconnect()
    
    def get_priority_status(
        self,
        family_id: str,
        include_nudges: bool = True
    ) -> Dict[str, Any]:
        """
        Get priority status and nudges for a family
        
        Args:
            family_id: Family ID
            include_nudges: Whether to include nudge recommendations
        
        Returns:
            Priority status with gap scores and nudges
        """
        # Check if already identified as priority
        priority_household = self.priority_identifier.get_priority_household(family_id)
        
        # If not found, try to identify
        if not priority_household:
            priority_household = self.priority_identifier.identify_priority_household(family_id)
        
        # Get exception flags
        exceptions = self.exception_detector.detect_exceptions(family_id)
        
        # Get nudges if requested
        nudges = []
        if include_nudges and priority_household:
            gap_analysis = priority_household.get('gap_analysis', {})
            location_data = gap_analysis.get('location_data', {})
            nudges = self.nudge_generator.generate_nudges(
                family_id=family_id,
                gap_analysis=gap_analysis,
                priority_segments=priority_household.get('priority_segments', []),
                location_data=location_data
            )
        
        return {
            'family_id': family_id,
            'is_priority': priority_household is not None,
            'priority_household': priority_household,
            'exception_flags': exceptions,
            'nudges': nudges,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_priority_list(
        self,
        block_id: Optional[str] = None,
        district: Optional[str] = None,
        segment_filters: Optional[List[str]] = None,
        priority_level_filter: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get priority household list for field workers
        
        Args:
            block_id: Filter by block ID
            district: Filter by district
            segment_filters: Filter by segments (e.g., ['TRIBAL', 'PWD'])
            priority_level_filter: Filter by priority level
            limit: Maximum households to return
        
        Returns:
            List of priority households with details
        """
        conn = self.db.connection
        cursor = conn.cursor()
        
        try:
            query = """
                SELECT 
                    priority_id, family_id, household_head_id,
                    block_id, district, gram_panchayat,
                    inclusion_gap_score, vulnerability_score,
                    priority_level, priority_segments,
                    predicted_eligible_schemes_count,
                    actual_enrolled_schemes_count,
                    eligibility_gap_count,
                    detected_at
                FROM inclusion.priority_households
                WHERE is_active = TRUE
            """
            
            params = []
            
            if block_id:
                query += " AND block_id = %s"
                params.append(block_id)
            
            if district:
                query += " AND district = %s"
                params.append(district)
            
            if segment_filters:
                query += " AND priority_segments && %s"
                params.append(segment_filters)
            
            if priority_level_filter:
                query += " AND priority_level = %s"
                params.append(priority_level_filter)
            
            query += " ORDER BY inclusion_gap_score DESC, vulnerability_score DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            
            households = []
            for row in cursor.fetchall():
                households.append({
                    'priority_id': row[0],
                    'family_id': str(row[1]),
                    'household_head_id': row[2],
                    'block_id': row[3],
                    'district': row[4],
                    'gram_panchayat': row[5],
                    'inclusion_gap_score': float(row[6]),
                    'vulnerability_score': float(row[7]),
                    'priority_level': row[8],
                    'priority_segments': row[9] or [],
                    'predicted_eligible_count': row[10] or 0,
                    'actual_enrolled_count': row[11] or 0,
                    'eligibility_gap_count': row[12] or 0,
                    'detected_at': row[13].isoformat() if row[13] else None
                })
            
            cursor.close()
            
            return {
                'total_count': len(households),
                'households': households,
                'filters': {
                    'block_id': block_id,
                    'district': district,
                    'segments': segment_filters,
                    'priority_level': priority_level_filter
                }
            }
        
        except Exception as e:
            print(f"⚠️  Error fetching priority list: {e}")
            cursor.close()
            return {
                'total_count': 0,
                'households': [],
                'error': str(e)
            }
    
    def schedule_nudge_delivery(
        self,
        family_id: str,
        nudge_type: str,
        nudge_message: str,
        recommended_actions: List[str],
        scheme_codes: List[str],
        channel: str,
        priority_level: str,
        scheduled_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Schedule and record nudge delivery
        
        Args:
            family_id: Family ID
            nudge_type: Type of nudge
            nudge_message: Nudge message text
            recommended_actions: List of recommended actions
            scheme_codes: Related scheme codes
            channel: Delivery channel
            priority_level: Priority level
            scheduled_at: Scheduled delivery time (default: now)
        
        Returns:
            Nudge delivery record
        """
        if scheduled_at is None:
            scheduled_at = datetime.now()
        
        conn = self.db.connection
        cursor = conn.cursor()
        
        try:
            # Get priority household ID if exists
            priority_household = self.priority_identifier.get_priority_household(family_id)
            priority_household_id = priority_household.get('priority_id') if priority_household else None
            
            # Get household head
            household_head_id = self.priority_identifier._get_household_head(family_id)
            
            cursor.execute("""
                INSERT INTO inclusion.nudge_records (
                    family_id, household_head_id, nudge_type, nudge_message,
                    recommended_actions, scheme_codes, channel, priority_level,
                    scheduled_at, delivery_status, priority_household_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING nudge_id
            """, (
                family_id,
                household_head_id,
                nudge_type,
                nudge_message,
                recommended_actions,
                scheme_codes,
                channel,
                priority_level,
                scheduled_at,
                'SCHEDULED',
                priority_household_id
            ))
            
            nudge_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            
            return {
                'success': True,
                'nudge_id': nudge_id,
                'delivery_status': 'SCHEDULED',
                'scheduled_at': scheduled_at.isoformat()
            }
        
        except Exception as e:
            print(f"⚠️  Error scheduling nudge: {e}")
            conn.rollback()
            cursor.close()
            return {
                'success': False,
                'error': str(e)
            }

