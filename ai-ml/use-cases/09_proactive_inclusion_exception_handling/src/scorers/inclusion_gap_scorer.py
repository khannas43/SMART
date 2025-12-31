"""
Inclusion Gap Scorer
Use Case ID: AI-PLATFORM-09

Calculates inclusion gap scores by combining:
- Predicted eligibility vs actual enrolment
- Vulnerability indicators
- Local coverage benchmarks
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import yaml
import json
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class InclusionGapScorer:
    """
    Inclusion Gap Scorer Service
    
    Calculates inclusion gap score combining:
    - Predicted eligibility vs actual enrolment gap
    - Vulnerability indicators
    - Local coverage benchmarks
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Inclusion Gap Scorer"""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "use_case_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Scoring weights
        inclusion_config = self.config.get('inclusion_detection', {})
        self.vulnerability_weight = inclusion_config.get('vulnerability_boost_weight', 0.3)
        self.coverage_gap_weight = inclusion_config.get('coverage_gap_weight', 0.5)
        self.benchmark_weight = inclusion_config.get('benchmark_weight', 0.2)
        self.gap_threshold = inclusion_config.get('inclusion_gap_threshold', 0.6)
        
        # Database configuration
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
    
    def calculate_inclusion_gap(
        self,
        family_id: str,
        analysis_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculate inclusion gap score for a household
        
        Args:
            family_id: Family ID
            analysis_date: Date for analysis (default: today)
        
        Returns:
            Dictionary with inclusion gap score and components
        """
        if analysis_date is None:
            analysis_date = datetime.now()
        
        # 1. Get predicted eligibility (from AI-PLATFORM-03/08)
        predicted_schemes = self._get_predicted_eligible_schemes(family_id)
        
        # 2. Get actual enrolled schemes (from benefit history)
        enrolled_schemes = self._get_enrolled_schemes(family_id)
        
        # 3. Calculate eligibility vs uptake gap
        gap_schemes = [s for s in predicted_schemes if s not in enrolled_schemes]
        coverage_gap_score = self._calculate_coverage_gap_score(
            len(predicted_schemes), len(enrolled_schemes), len(gap_schemes)
        )
        
        # 4. Get vulnerability indicators (from AI-PLATFORM-02)
        vulnerability_data = self._get_vulnerability_indicators(family_id)
        vulnerability_score = self._calculate_vulnerability_score(vulnerability_data)
        
        # 5. Get local coverage benchmark
        location_data = self._get_location_data(family_id)
        benchmark_score = self._calculate_benchmark_score(location_data, len(enrolled_schemes))
        
        # 6. Calculate combined inclusion gap score
        inclusion_gap_score = (
            coverage_gap_score * self.coverage_gap_weight +
            vulnerability_score * self.vulnerability_weight +
            (1.0 - benchmark_score) * self.benchmark_weight  # Lower benchmark = higher gap
        )
        
        # Ensure score is between 0 and 1
        inclusion_gap_score = max(0.0, min(1.0, inclusion_gap_score))
        
        # 7. Identify priority segments
        priority_segments = self._identify_priority_segments(vulnerability_data)
        
        # 8. Determine priority level
        priority_level = self._determine_priority_level(inclusion_gap_score, vulnerability_score)
        
        return {
            'family_id': family_id,
            'analysis_date': analysis_date,
            'inclusion_gap_score': inclusion_gap_score,
            'vulnerability_score': vulnerability_score,
            'coverage_gap_score': coverage_gap_score,
            'benchmark_score': benchmark_score,
            'predicted_eligible_schemes': predicted_schemes,
            'actual_enrolled_schemes': enrolled_schemes,
            'gap_schemes': gap_schemes,
            'predicted_eligible_count': len(predicted_schemes),
            'actual_enrolled_count': len(enrolled_schemes),
            'eligibility_gap_count': len(gap_schemes),
            'priority_segments': priority_segments,
            'priority_level': priority_level,
            'vulnerability_flags': vulnerability_data.get('flags', []),
            'vulnerability_details': vulnerability_data,
            'location_data': location_data
        }
    
    def _get_predicted_eligible_schemes(self, family_id: str) -> List[str]:
        """Get predicted eligible schemes from eligibility engine"""
        schemes = []
        
        try:
            # Query eligibility snapshots or recommendations
            conn = self.external_dbs['eligibility'].connection
            cursor = conn.cursor()
            
            # Get recent eligibility evaluations
            cursor.execute("""
                SELECT DISTINCT scheme_code
                FROM eligibility.scheme_eligibility_snapshots
                WHERE family_id = %s::uuid
                  AND evaluation_status IN ('RULE_ELIGIBLE', 'POSSIBLE_ELIGIBLE')
                  AND snapshot_date >= CURRENT_DATE - INTERVAL '90 days'
                ORDER BY scheme_code
            """, (family_id,))
            
            schemes = [row[0] for row in cursor.fetchall()]
            cursor.close()
        
        except Exception as e:
            print(f"⚠️  Error fetching predicted eligible schemes: {e}")
            # Fallback: Try eligibility_checker recommendations
            try:
                conn = self.external_dbs['eligibility_checker'].connection
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT DISTINCT ser.scheme_code
                    FROM eligibility_checker.scheme_eligibility_results ser
                    INNER JOIN eligibility_checker.eligibility_checks ec ON ser.check_id = ec.check_id
                    WHERE ec.family_id = %s::uuid
                      AND ser.eligibility_status IN ('ELIGIBLE', 'POSSIBLE_ELIGIBLE')
                      AND ec.check_timestamp >= CURRENT_TIMESTAMP - INTERVAL '90 days'
                    ORDER BY ser.scheme_code
                """, (family_id,))
                
                schemes = [row[0] for row in cursor.fetchall()]
                cursor.close()
            except Exception as e2:
                print(f"⚠️  Error in fallback query: {e2}")
        
        return schemes
    
    def _get_enrolled_schemes(self, family_id: str) -> List[str]:
        """Get actually enrolled schemes from benefit history"""
        schemes = []
        
        try:
            conn = self.external_dbs['profile_360'].connection
            cursor = conn.cursor()
            
            # Get schemes with active benefits
            cursor.execute("""
                SELECT DISTINCT scheme_code
                FROM profile_360.benefit_history
                WHERE beneficiary_id IN (
                    SELECT beneficiary_id 
                    FROM golden_records.beneficiaries 
                    WHERE family_id = %s::uuid
                )
                  AND status IN ('ACTIVE', 'PAID', 'ENROLLED')
                  AND benefit_date >= CURRENT_DATE - INTERVAL '365 days'
                ORDER BY scheme_code
            """, (family_id,))
            
            schemes = [row[0] for row in cursor.fetchall()]
            cursor.close()
        
        except Exception as e:
            print(f"⚠️  Error fetching enrolled schemes: {e}")
        
        return schemes
    
    def _get_vulnerability_indicators(self, family_id: str) -> Dict[str, Any]:
        """Get vulnerability indicators from 360° profile"""
        vulnerability = {
            'flags': [],
            'details': {}
        }
        
        try:
            # Get from profile_360
            conn = self.external_dbs['profile_360'].connection
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT 
                    vulnerability_tags,
                    income_band,
                    is_tribal,
                    is_pwd,
                    is_single_woman_head,
                    is_elderly_alone
                FROM profile_360.household_profiles
                WHERE family_id = %s::uuid
                LIMIT 1
            """, (family_id,))
            
            row = cursor.fetchone()
            if row:
                tags = row[0] or []
                vulnerability['flags'] = tags if isinstance(tags, list) else []
                vulnerability['details'] = {
                    'income_band': row[1],
                    'is_tribal': row[2] or False,
                    'is_pwd': row[3] or False,
                    'is_single_woman_head': row[4] or False,
                    'is_elderly_alone': row[5] or False
                }
                
                # Add flags based on details
                if row[2]:
                    vulnerability['flags'].append('tribal')
                if row[3]:
                    vulnerability['flags'].append('pwd')
                if row[4]:
                    vulnerability['flags'].append('single_woman')
                if row[5]:
                    vulnerability['flags'].append('elderly_alone')
            
            cursor.close()
        
        except Exception as e:
            print(f"⚠️  Error fetching vulnerability indicators: {e}")
            # Fallback: Try golden_records
            try:
                conn = self.external_dbs['golden_records'].connection
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        category,
                        disability_status,
                        gender
                    FROM golden_records.beneficiaries
                    WHERE family_id = %s::uuid
                      AND is_active = TRUE
                    LIMIT 1
                """, (family_id,))
                
                row = cursor.fetchone()
                if row:
                    if row[0] and 'ST' in str(row[0]).upper():
                        vulnerability['flags'].append('tribal')
                    if row[1] and str(row[1]).upper() in ['YES', 'TRUE', '1']:
                        vulnerability['flags'].append('pwd')
                    if row[2] and str(row[2]).upper() == 'FEMALE':
                        vulnerability['flags'].append('female_headed')
            
            except Exception as e2:
                print(f"⚠️  Error in fallback vulnerability query: {e2}")
        
        return vulnerability
    
    def _get_location_data(self, family_id: str) -> Dict[str, Any]:
        """Get location data for benchmark comparison"""
        location = {
            'district': None,
            'block_id': None,
            'gram_panchayat': None
        }
        
        try:
            conn = self.external_dbs['golden_records'].connection
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT
                    address_district,
                    address_block,
                    address_gram_panchayat
                FROM golden_records.beneficiaries
                WHERE family_id = %s::uuid
                  AND is_active = TRUE
                LIMIT 1
            """, (family_id,))
            
            row = cursor.fetchone()
            if row:
                location['district'] = row[0]
                location['block_id'] = row[1]
                location['gram_panchayat'] = row[2]
            
            cursor.close()
        
        except Exception as e:
            print(f"⚠️  Error fetching location data: {e}")
        
        return location
    
    def _calculate_coverage_gap_score(
        self,
        predicted_count: int,
        enrolled_count: int,
        gap_count: int
    ) -> float:
        """Calculate coverage gap score (0-1, higher = larger gap)"""
        if predicted_count == 0:
            return 0.0  # No predicted eligibility, no gap
        
        # Gap ratio
        gap_ratio = gap_count / predicted_count if predicted_count > 0 else 0.0
        
        return min(1.0, gap_ratio)
    
    def _calculate_vulnerability_score(self, vulnerability_data: Dict[str, Any]) -> float:
        """Calculate vulnerability score based on indicators"""
        flags = vulnerability_data.get('flags', [])
        details = vulnerability_data.get('details', {})
        
        score = 0.0
        
        # Base vulnerability indicators
        if 'tribal' in flags or details.get('is_tribal'):
            score += 0.25
        if 'pwd' in flags or details.get('is_pwd'):
            score += 0.25
        if 'single_woman' in flags or details.get('is_single_woman_head'):
            score += 0.20
        if 'elderly_alone' in flags or details.get('is_elderly_alone'):
            score += 0.15
        if 'remote_hamlet' in flags:
            score += 0.15
        
        # Income-based vulnerability
        income_band = details.get('income_band', '')
        if income_band and 'BELOW' in income_band.upper():
            score += 0.10
        
        return min(1.0, score)
    
    def _calculate_benchmark_score(
        self,
        location_data: Dict[str, Any],
        enrolled_count: int
    ) -> float:
        """Calculate benchmark score based on local coverage"""
        # TODO: Implement actual benchmark calculation
        # For now, return a default value
        
        # In future: Compare enrolled_count to average in same block/GP
        return 0.5  # Default: assume average coverage
    
    def _identify_priority_segments(self, vulnerability_data: Dict[str, Any]) -> List[str]:
        """Identify priority segments based on vulnerability"""
        segments = []
        flags = vulnerability_data.get('flags', [])
        details = vulnerability_data.get('details', {})
        
        # Map flags to segments
        segment_mapping = {
            'tribal': 'TRIBAL',
            'pwd': 'PWD',
            'single_woman': 'SINGLE_WOMAN',
            'female_headed': 'SINGLE_WOMAN',
            'elderly_alone': 'ELDERLY_ALONE',
            'remote_hamlet': 'REMOTE_GEOGRAPHY',
            'unemployed': 'UNEMPLOYED_YOUTH',
            'youth': 'UNEMPLOYED_YOUTH'
        }
        
        for flag in flags:
            segment = segment_mapping.get(flag.lower())
            if segment and segment not in segments:
                segments.append(segment)
        
        # Check details
        if details.get('is_tribal') and 'TRIBAL' not in segments:
            segments.append('TRIBAL')
        if details.get('is_pwd') and 'PWD' not in segments:
            segments.append('PWD')
        if details.get('is_single_woman_head') and 'SINGLE_WOMAN' not in segments:
            segments.append('SINGLE_WOMAN')
        if details.get('is_elderly_alone') and 'ELDERLY_ALONE' not in segments:
            segments.append('ELDERLY_ALONE')
        
        return segments
    
    def _determine_priority_level(
        self,
        inclusion_gap_score: float,
        vulnerability_score: float
    ) -> str:
        """Determine priority level based on scores"""
        # Combined score
        combined = (inclusion_gap_score * 0.7) + (vulnerability_score * 0.3)
        
        if combined >= 0.75:
            return 'HIGH'
        elif combined >= 0.5:
            return 'MEDIUM'
        else:
            return 'LOW'

