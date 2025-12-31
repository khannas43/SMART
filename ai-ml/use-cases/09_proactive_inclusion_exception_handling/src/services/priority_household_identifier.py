"""
Priority Household Identifier
Use Case ID: AI-PLATFORM-09

Identifies priority households and manages priority household records.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
import json
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector

from scorers.inclusion_gap_scorer import InclusionGapScorer


class PriorityHouseholdIdentifier:
    """
    Priority Household Identifier Service
    
    Identifies and manages priority households based on inclusion gap scores.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Priority Household Identifier"""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "use_case_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize gap scorer
        self.gap_scorer = InclusionGapScorer(config_path)
        
        # Configuration
        inclusion_config = self.config.get('inclusion_detection', {})
        self.gap_threshold = inclusion_config.get('inclusion_gap_threshold', 0.6)
        
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
        """Connect to databases"""
        self.db.connect()
        self.gap_scorer.connect()
    
    def disconnect(self):
        """Disconnect from databases"""
        self.db.disconnect()
        self.gap_scorer.disconnect()
    
    def identify_priority_household(
        self,
        family_id: str,
        save_to_db: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Identify if a household is priority and create/update record
        
        Args:
            family_id: Family ID
            save_to_db: Whether to save to database
        
        Returns:
            Priority household record or None if not priority
        """
        # Calculate inclusion gap
        gap_analysis = self.gap_scorer.calculate_inclusion_gap(family_id)
        
        inclusion_gap_score = gap_analysis.get('inclusion_gap_score', 0.0)
        
        # Check if meets threshold
        if inclusion_gap_score < self.gap_threshold:
            return None  # Not priority
        
        # Get location data
        location_data = gap_analysis.get('location_data', {})
        
        # Get household head
        household_head_id = self._get_household_head(family_id)
        
        # Create priority household record
        priority_record = {
            'family_id': family_id,
            'household_head_id': household_head_id,
            'block_id': location_data.get('block_id'),
            'district': location_data.get('district'),
            'gram_panchayat': location_data.get('gram_panchayat'),
            'inclusion_gap_score': inclusion_gap_score,
            'vulnerability_score': gap_analysis.get('vulnerability_score', 0.0),
            'coverage_gap_score': gap_analysis.get('coverage_gap_score', 0.0),
            'benchmark_score': gap_analysis.get('benchmark_score', 0.5),
            'priority_level': gap_analysis.get('priority_level', 'MEDIUM'),
            'priority_segments': gap_analysis.get('priority_segments', []),
            'predicted_eligible_count': gap_analysis.get('predicted_eligible_count', 0),
            'actual_enrolled_count': gap_analysis.get('actual_enrolled_count', 0),
            'eligibility_gap_count': gap_analysis.get('eligibility_gap_count', 0),
            'gap_analysis': gap_analysis
        }
        
        # Save to database
        if save_to_db:
            priority_id = self._save_priority_household(priority_record)
            priority_record['priority_id'] = priority_id
            
            # Save detailed gap analysis
            self._save_gap_analysis(family_id, gap_analysis, priority_id)
        
        return priority_record
    
    def get_priority_household(self, family_id: str) -> Optional[Dict[str, Any]]:
        """Get existing priority household record"""
        conn = self.db.connection
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    priority_id, family_id, household_head_id,
                    block_id, district, gram_panchayat,
                    inclusion_gap_score, vulnerability_score,
                    coverage_gap_score, benchmark_score,
                    priority_level, priority_segments,
                    predicted_eligible_schemes_count,
                    actual_enrolled_schemes_count,
                    eligibility_gap_count,
                    is_active, detected_at, last_updated_at
                FROM inclusion.priority_households
                WHERE family_id = %s::uuid
                  AND is_active = TRUE
                ORDER BY detected_at DESC
                LIMIT 1
            """, (family_id,))
            
            row = cursor.fetchone()
            cursor.close()
            
            if row:
                return {
                    'priority_id': row[0],
                    'family_id': str(row[1]),
                    'household_head_id': row[2],
                    'block_id': row[3],
                    'district': row[4],
                    'gram_panchayat': row[5],
                    'inclusion_gap_score': float(row[6]),
                    'vulnerability_score': float(row[7]),
                    'coverage_gap_score': float(row[8]),
                    'benchmark_score': float(row[9]) if row[9] else 0.5,
                    'priority_level': row[10],
                    'priority_segments': row[11] or [],
                    'predicted_eligible_count': row[12] or 0,
                    'actual_enrolled_count': row[13] or 0,
                    'eligibility_gap_count': row[14] or 0,
                    'is_active': row[15],
                    'detected_at': row[16],
                    'last_updated_at': row[17]
                }
        
        except Exception as e:
            print(f"⚠️  Error fetching priority household: {e}")
            cursor.close()
        
        return None
    
    def _get_household_head(self, family_id: str) -> Optional[str]:
        """Get household head beneficiary ID"""
        try:
            conn = self.gap_scorer.external_dbs['golden_records'].connection
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT beneficiary_id
                FROM golden_records.beneficiaries
                WHERE family_id = %s::uuid
                  AND is_active = TRUE
                  AND relationship_to_head IN ('SELF', 'HEAD', NULL)
                ORDER BY date_of_birth ASC
                LIMIT 1
            """, (family_id,))
            
            row = cursor.fetchone()
            cursor.close()
            
            return row[0] if row else None
        
        except Exception:
            return None
    
    def _save_priority_household(self, record: Dict[str, Any]) -> int:
        """Save priority household to database"""
        conn = self.db.connection
        cursor = conn.cursor()
        
        try:
            # Check if exists
            cursor.execute("""
                SELECT priority_id FROM inclusion.priority_households
                WHERE family_id = %s::uuid AND is_active = TRUE
            """, (record['family_id'],))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing
                cursor.execute("""
                    UPDATE inclusion.priority_households
                    SET 
                        household_head_id = %s,
                        block_id = %s,
                        district = %s,
                        gram_panchayat = %s,
                        inclusion_gap_score = %s,
                        vulnerability_score = %s,
                        coverage_gap_score = %s,
                        benchmark_score = %s,
                        priority_level = %s,
                        priority_segments = %s,
                        predicted_eligible_schemes_count = %s,
                        actual_enrolled_schemes_count = %s,
                        eligibility_gap_count = %s,
                        last_updated_at = CURRENT_TIMESTAMP
                    WHERE priority_id = %s
                    RETURNING priority_id
                """, (
                    record['household_head_id'],
                    record['block_id'],
                    record['district'],
                    record['gram_panchayat'],
                    record['inclusion_gap_score'],
                    record['vulnerability_score'],
                    record['coverage_gap_score'],
                    record['benchmark_score'],
                    record['priority_level'],
                    record['priority_segments'],
                    record['predicted_eligible_count'],
                    record['actual_enrolled_count'],
                    record['eligibility_gap_count'],
                    existing[0]
                ))
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO inclusion.priority_households (
                        family_id, household_head_id, block_id, district, gram_panchayat,
                        inclusion_gap_score, vulnerability_score, coverage_gap_score,
                        benchmark_score, priority_level, priority_segments,
                        predicted_eligible_schemes_count, actual_enrolled_schemes_count,
                        eligibility_gap_count
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING priority_id
                """, (
                    record['family_id'],
                    record['household_head_id'],
                    record['block_id'],
                    record['district'],
                    record['gram_panchayat'],
                    record['inclusion_gap_score'],
                    record['vulnerability_score'],
                    record['coverage_gap_score'],
                    record['benchmark_score'],
                    record['priority_level'],
                    record['priority_segments'],
                    record['predicted_eligible_count'],
                    record['actual_enrolled_count'],
                    record['eligibility_gap_count']
                ))
            
            priority_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            
            return priority_id
        
        except Exception as e:
            print(f"⚠️  Error saving priority household: {e}")
            conn.rollback()
            cursor.close()
            return 0
    
    def _save_gap_analysis(
        self,
        family_id: str,
        gap_analysis: Dict[str, Any],
        priority_id: int
    ):
        """Save detailed gap analysis"""
        conn = self.db.connection
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO inclusion.inclusion_gap_analysis (
                    family_id, analysis_date,
                    predicted_eligible_schemes, actual_enrolled_schemes,
                    gap_schemes, vulnerability_flags, vulnerability_details,
                    local_benchmark_coverage, household_coverage, coverage_deviation,
                    inclusion_gap_score, component_scores, priority_household_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                family_id,
                gap_analysis.get('analysis_date', datetime.now().date()),
                json.dumps(gap_analysis.get('predicted_eligible_schemes', [])),
                gap_analysis.get('actual_enrolled_schemes', []),
                gap_analysis.get('gap_schemes', []),
                gap_analysis.get('vulnerability_flags', []),
                json.dumps(gap_analysis.get('vulnerability_details', {})),
                gap_analysis.get('benchmark_score', 0.5),
                gap_analysis.get('actual_enrolled_count', 0) / max(1, gap_analysis.get('predicted_eligible_count', 1)),
                gap_analysis.get('coverage_gap_score', 0.0),
                gap_analysis.get('inclusion_gap_score', 0.0),
                json.dumps({
                    'vulnerability': gap_analysis.get('vulnerability_score', 0.0),
                    'coverage_gap': gap_analysis.get('coverage_gap_score', 0.0),
                    'benchmark': gap_analysis.get('benchmark_score', 0.5)
                }),
                priority_id
            ))
            
            conn.commit()
            cursor.close()
        
        except Exception as e:
            print(f"⚠️  Error saving gap analysis: {e}")
            conn.rollback()
            cursor.close()

