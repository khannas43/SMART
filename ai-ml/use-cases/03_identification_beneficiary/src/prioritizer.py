"""
Prioritization Logic for Candidate Ranking
Ranks eligible candidates by eligibility score, vulnerability, and under-coverage indicators
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
import yaml
import warnings
warnings.filterwarnings('ignore')

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class Prioritizer:
    """
    Prioritization and ranking engine for eligible candidates
    
    Ranks candidates based on:
    1. Eligibility score (from hybrid evaluator)
    2. Vulnerability level (from 360° Profile)
    3. Under-coverage indicators (from 360° Profile)
    4. Geographic clustering
    5. Scheme-specific priorities
    """
    
    def __init__(self, config_path=None):
        """
        Initialize prioritizer
        
        Args:
            config_path: Path to configuration file
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "use_case_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Database connections
        db_config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
        with open(db_config_path, 'r') as f:
            db_config = yaml.safe_load(f)
        
        # Primary database
        primary_db = db_config['database']
        self.db = DBConnector(
            host=primary_db['host'],
            port=primary_db['port'],
            database=primary_db['name'],
            user=primary_db['user'],
            password=primary_db['password']
        )
        self.db.connect()
        
        # 360° Profile database (for vulnerability and under-coverage)
        profile_db = db_config['external_databases']['profile_360']
        self.profile_db = DBConnector(
            host=profile_db['host'],
            port=profile_db['port'],
            database=profile_db['name'],
            user=profile_db['user'],
            password=profile_db['password']
        )
        self.profile_db.connect()
        
        # Get prioritization config
        prioritization_config = self.config['components']['prioritization']
        self.consider_vulnerability = prioritization_config.get('consider_vulnerability', True)
        self.consider_under_coverage = prioritization_config.get('consider_under_coverage', True)
        self.max_citizen_hints = prioritization_config.get('max_citizen_hints', 5)
    
    def load_vulnerability_data(self, family_ids: List[str]) -> Dict[str, Dict]:
        """
        Load vulnerability and under-coverage data from 360° Profiles
        
        Args:
            family_ids: List of family IDs
        
        Returns:
            Dictionary mapping family_id to vulnerability data
        """
        if not family_ids:
            return {}
        
        # Query 360° Profile database
        placeholders = ','.join(['%s'] * len(family_ids))
        query = f"""
            SELECT 
                gr_id,
                family_id,
                profile_data->>'vulnerability_level' as vulnerability_level,
                profile_data->>'under_coverage_indicator' as under_coverage,
                profile_data->>'cluster_id' as cluster_id
            FROM smart_warehouse.profile_360
            WHERE family_id::text IN ({placeholders})
        """
        
        try:
            df = pd.read_sql(query, self.profile_db.connection, params=tuple(family_ids))
            
            result = {}
            for _, row in df.iterrows():
                family_id = str(row['family_id']) if pd.notna(row['family_id']) else str(row['gr_id'])
                result[family_id] = {
                    'vulnerability_level': row.get('vulnerability_level', 'MEDIUM'),
                    'under_coverage': row.get('under_coverage', 'false') == 'true',
                    'cluster_id': row.get('cluster_id')
                }
            
            return result
        
        except Exception as e:
            print(f"⚠️  Error loading vulnerability data: {e}")
            return {}
    
    def calculate_priority_score(
        self,
        eligibility_score: float,
        confidence_score: float,
        vulnerability_level: str = 'MEDIUM',
        under_coverage: bool = False,
        scheme_priority_weight: float = 1.0
    ) -> float:
        """
        Calculate priority score for ranking
        
        Args:
            eligibility_score: Eligibility score from hybrid evaluator (0-1)
            confidence_score: Confidence score (0-1)
            vulnerability_level: Vulnerability level (VERY_HIGH, HIGH, MEDIUM, LOW)
            under_coverage: Whether family is under-covered
            scheme_priority_weight: Scheme-specific priority multiplier
        
        Returns:
            Priority score (higher = higher priority)
        """
        # Base score: eligibility weighted by confidence
        base_score = eligibility_score * confidence_score
        
        # Vulnerability multiplier
        vulnerability_multiplier = {
            'VERY_HIGH': 1.5,
            'HIGH': 1.3,
            'MEDIUM': 1.0,
            'LOW': 0.8,
            'VERY_LOW': 0.6
        }.get(vulnerability_level.upper(), 1.0)
        
        # Under-coverage boost
        under_coverage_boost = 0.15 if under_coverage else 0.0
        
        # Calculate priority score
        priority_score = (
            base_score * vulnerability_multiplier +
            under_coverage_boost
        ) * scheme_priority_weight
        
        # Normalize to 0-1 range (can exceed 1 with multipliers)
        priority_score = min(1.0, priority_score)
        
        return priority_score
    
    def rank_candidates(
        self,
        evaluations: List[Dict],
        scheme_id: str,
        geographic_clustering: bool = True
    ) -> List[Dict]:
        """
        Rank candidates based on priority scores
        
        Args:
            evaluations: List of evaluation result dictionaries
            scheme_id: Scheme ID
            geographic_clustering: Whether to consider geographic clustering
        
        Returns:
            Ranked list of evaluations with priority scores and ranks
        """
        if not evaluations:
            return []
        
        # Extract family IDs
        family_ids = [e['family_id'] for e in evaluations if 'family_id' in e]
        
        # Load vulnerability data
        vulnerability_data = {}
        if self.consider_vulnerability or self.consider_under_coverage:
            vulnerability_data = self.load_vulnerability_data(family_ids)
        
        # Calculate priority scores
        ranked_evaluations = []
        
        for eval_result in evaluations:
            family_id = eval_result.get('family_id', 'unknown')
            
            # Get vulnerability data
            vuln_data = vulnerability_data.get(family_id, {})
            vulnerability_level = vuln_data.get('vulnerability_level', 'MEDIUM')
            under_coverage = vuln_data.get('under_coverage', False) if self.consider_under_coverage else False
            
            # Calculate priority score
            priority_score = self.calculate_priority_score(
                eligibility_score=eval_result.get('eligibility_score', 0.0),
                confidence_score=eval_result.get('confidence_score', 0.0),
                vulnerability_level=vulnerability_level,
                under_coverage=under_coverage
            )
            
            # Add to ranked list
            ranked_eval = eval_result.copy()
            ranked_eval['priority_score'] = priority_score
            ranked_eval['vulnerability_level'] = vulnerability_level
            ranked_eval['under_coverage_indicator'] = under_coverage
            ranked_eval['cluster_id'] = vuln_data.get('cluster_id')
            
            ranked_evaluations.append(ranked_eval)
        
        # Sort by priority score (descending)
        ranked_evaluations.sort(key=lambda x: x['priority_score'], reverse=True)
        
        # Assign ranks
        for idx, ranked_eval in enumerate(ranked_evaluations):
            ranked_eval['rank'] = idx + 1
        
        # Geographic clustering (optional)
        if geographic_clustering:
            ranked_evaluations = self._apply_geographic_clustering(ranked_evaluations)
        
        return ranked_evaluations
    
    def _apply_geographic_clustering(
        self,
        ranked_evaluations: List[Dict]
    ) -> List[Dict]:
        """
        Apply geographic clustering to prioritize areas with many candidates
        
        Args:
            ranked_evaluations: Ranked evaluation list
        
        Returns:
            Re-ranked list with geographic clustering applied
        """
        # Group by cluster/district
        cluster_counts = {}
        for eval_result in ranked_evaluations:
            cluster_id = eval_result.get('cluster_id')
            district_id = eval_result.get('district_id')  # From family data
            
            key = f"{cluster_id}_{district_id}" if cluster_id else str(district_id)
            cluster_counts[key] = cluster_counts.get(key, 0) + 1
        
        # Apply slight boost for clusters with many candidates
        # (Encourage batch processing in same geographic area)
        for eval_result in ranked_evaluations:
            cluster_id = eval_result.get('cluster_id')
            district_id = eval_result.get('district_id')
            
            key = f"{cluster_id}_{district_id}" if cluster_id else str(district_id)
            cluster_size = cluster_counts.get(key, 1)
            
            # Small boost for larger clusters (max 10% boost)
            cluster_boost = min(0.1, cluster_size * 0.01)
            eval_result['priority_score'] = min(1.0, eval_result['priority_score'] + cluster_boost)
        
        # Re-sort after clustering boost
        ranked_evaluations.sort(key=lambda x: x['priority_score'], reverse=True)
        
        # Update ranks
        for idx, ranked_eval in enumerate(ranked_evaluations):
            ranked_eval['rank'] = idx + 1
        
        return ranked_evaluations
    
    def generate_citizen_hints(
        self,
        family_id: str,
        scheme_evaluations: Dict[str, Dict]
    ) -> List[Dict]:
        """
        Generate top N scheme hints for citizen portal
        
        Args:
            family_id: Family ID
            scheme_evaluations: Dictionary mapping scheme_id to evaluation results
        
        Returns:
            List of top N scheme hints (sorted by priority)
        """
        # Convert to list and rank
        evaluations = list(scheme_evaluations.values())
        ranked = self.rank_candidates(evaluations, scheme_id=None)
        
        # Filter to eligible candidates only
        eligible = [
            e for e in ranked
            if e.get('evaluation_status') in ['RULE_ELIGIBLE', 'POSSIBLE_ELIGIBLE']
        ]
        
        # Take top N
        top_n = eligible[:self.max_citizen_hints]
        
        # Format for citizen portal
        hints = []
        for eval_result in top_n:
            hints.append({
                'scheme_id': eval_result['scheme_id'],
                'scheme_name': eval_result.get('scheme_name', eval_result['scheme_id']),
                'eligibility_status': eval_result['evaluation_status'],
                'eligibility_score': eval_result.get('eligibility_score', 0.0),
                'confidence': eval_result.get('confidence_score', 0.0),
                'explanation': eval_result.get('explanation', ''),
                'rank': eval_result.get('rank', 0)
            })
        
        return hints
    
    def generate_departmental_worklist(
        self,
        scheme_id: str,
        evaluations: List[Dict],
        district_id: Optional[int] = None,
        min_score: float = 0.5,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Generate departmental worklist for a scheme
        
        Args:
            scheme_id: Scheme ID
            evaluations: List of evaluation results
            district_id: Optional district filter
            min_score: Minimum eligibility score threshold
            limit: Maximum number of candidates
        
        Returns:
            Worklist (ranked list of candidates)
        """
        # Filter by scheme
        scheme_evaluations = [
            e for e in evaluations
            if e.get('scheme_id') == scheme_id
        ]
        
        # Filter by district if specified
        if district_id:
            scheme_evaluations = [
                e for e in scheme_evaluations
                if e.get('district_id') == district_id
            ]
        
        # Filter by minimum score
        scheme_evaluations = [
            e for e in scheme_evaluations
            if e.get('eligibility_score', 0.0) >= min_score
        ]
        
        # Rank candidates
        ranked = self.rank_candidates(scheme_evaluations, scheme_id)
        
        # Apply limit
        if limit:
            ranked = ranked[:limit]
        
        # Format for departmental worklist
        worklist = []
        for eval_result in ranked:
            worklist.append({
                'family_id': eval_result['family_id'],
                'member_id': eval_result.get('member_id'),
                'rank': eval_result.get('rank', 0),
                'priority_score': eval_result.get('priority_score', 0.0),
                'eligibility_score': eval_result.get('eligibility_score', 0.0),
                'confidence': eval_result.get('confidence_score', 0.0),
                'status': eval_result.get('evaluation_status'),
                'vulnerability_level': eval_result.get('vulnerability_level', 'MEDIUM'),
                'under_coverage': eval_result.get('under_coverage_indicator', False),
                'district_id': eval_result.get('district_id'),
                'cluster_id': eval_result.get('cluster_id'),
                'explanation': eval_result.get('explanation', ''),
                'rule_path': eval_result.get('rule_path', ''),
                'reason_codes': eval_result.get('reason_codes', [])
            })
        
        return worklist
    
    def save_candidate_list(
        self,
        scheme_id: str,
        worklist: List[Dict],
        list_type: str = 'DEPARTMENT_WORKLIST'
    ) -> int:
        """
        Save candidate list to database
        
        Args:
            scheme_id: Scheme ID
            worklist: Worklist data
            list_type: Type of list (CITIZEN_HINTS, DEPARTMENT_WORKLIST, AUTO_INTIMATION)
        
        Returns:
            Number of candidates saved
        """
        if not worklist:
            return 0
        
        cursor = self.db.connection.cursor()
        
        saved_count = 0
        for candidate in worklist:
            try:
                # Get snapshot_id from evaluation
                snapshot_id = candidate.get('snapshot_id')
                if not snapshot_id:
                    continue
                
                insert_query = """
                    INSERT INTO eligibility.candidate_lists (
                        scheme_code, family_id, member_id,
                        snapshot_id,
                        rank_in_scheme, district_id, cluster_id,
                        list_type, generated_at, is_active
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, true)
                    ON CONFLICT (scheme_code, family_id, member_id, list_type, generated_at) DO NOTHING
                """
                
                cursor.execute(insert_query, (
                    scheme_id,  # scheme_code
                    candidate['family_id'],
                    candidate.get('member_id'),
                    snapshot_id,
                    candidate.get('rank', 0) or 0,  # rank_in_scheme
                    candidate.get('district_id'),
                    candidate.get('cluster_id'),
                    list_type
                ))
                
                saved_count += 1
            
            except Exception as e:
                print(f"⚠️  Error saving candidate {candidate.get('family_id')}: {e}")
                continue
        
        self.db.connection.commit()
        cursor.close()
        
        return saved_count
    
    def close(self):
        """Close database connections"""
        if self.db:
            self.db.disconnect()
        if self.profile_db:
            self.profile_db.disconnect()


def main():
    """Test prioritizer"""
    prioritizer = Prioritizer()
    
    # Sample evaluations
    evaluations = [
        {
            'scheme_id': 'SCHEME_001',
            'family_id': 'FAM-001',
            'evaluation_status': 'RULE_ELIGIBLE',
            'eligibility_score': 0.85,
            'confidence_score': 0.90,
            'district_id': 101
        },
        {
            'scheme_id': 'SCHEME_001',
            'family_id': 'FAM-002',
            'evaluation_status': 'POSSIBLE_ELIGIBLE',
            'eligibility_score': 0.70,
            'confidence_score': 0.75,
            'district_id': 101
        },
        {
            'scheme_id': 'SCHEME_001',
            'family_id': 'FAM-003',
            'evaluation_status': 'RULE_ELIGIBLE',
            'eligibility_score': 0.90,
            'confidence_score': 0.95,
            'district_id': 102
        }
    ]
    
    # Rank candidates
    ranked = prioritizer.rank_candidates(evaluations, 'SCHEME_001')
    
    print("=" * 80)
    print("Prioritization Test Results")
    print("=" * 80)
    for candidate in ranked:
        print(f"Rank {candidate['rank']}: Family {candidate['family_id']}")
        print(f"  Priority Score: {candidate['priority_score']:.3f}")
        print(f"  Eligibility Score: {candidate['eligibility_score']:.3f}")
        print(f"  Status: {candidate['evaluation_status']}")
        print()
    
    prioritizer.close()


if __name__ == "__main__":
    main()

