"""
Main Evaluation Service
Handles batch, event-driven, and on-demand eligibility evaluation
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import uuid
import yaml
import json
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

from hybrid_evaluator import HybridEvaluator
from prioritizer import Prioritizer

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class EligibilityEvaluationService:
    """
    Main service for eligibility evaluation
    
    Supports:
    1. Batch evaluation (weekly scans)
    2. Event-driven evaluation (on family changes)
    3. On-demand evaluation (API calls)
    """
    
    def __init__(self, config_path=None):
        """
        Initialize evaluation service
        
        Args:
            config_path: Path to configuration file
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "use_case_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Database connection
        db_config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
        with open(db_config_path, 'r') as f:
            db_config = yaml.safe_load(f)['database']
        
        self.db = DBConnector(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['name'],
            user=db_config['user'],
            password=db_config['password']
        )
        self.db.connect()
        
        # Initialize components
        self.evaluator = HybridEvaluator(config_path)
        self.prioritizer = Prioritizer(config_path)
        
        # Get evaluation config
        eval_config = self.config['evaluation']
        self.batch_enabled = eval_config['batch']['enabled']
        self.event_driven_enabled = eval_config['event_driven']['enabled']
        self.on_demand_enabled = eval_config['on_demand']['enabled']
    
    def evaluate_family(
        self,
        family_id: str,
        scheme_ids: Optional[List[str]] = None,
        use_ml: bool = True,
        save_results: bool = True
    ) -> Dict[str, Any]:
        """
        Evaluate eligibility for a single family
        
        Args:
            family_id: Family ID (UUID or string)
            scheme_ids: List of scheme IDs to evaluate (None for all active schemes)
            use_ml: Whether to use ML scorer if available
            save_results: Whether to save results to database
        
        Returns:
            Dictionary with evaluation results
        """
        # Load family data
        family_data = self._load_family_data(family_id)
        if not family_data:
            return {
                'error': f'Family {family_id} not found',
                'evaluations': []
            }
        
        # Get schemes to evaluate
        if scheme_ids is None:
            scheme_ids = self._get_active_schemes()
        
        # Evaluate for each scheme
        evaluations = []
        for scheme_id in scheme_ids:
            try:
                # Evaluate eligibility
                eval_result = self.evaluator.evaluate(
                    scheme_id, family_data, use_ml=use_ml
                )
                
                # Add metadata
                eval_result['evaluation_timestamp'] = datetime.now()
                eval_result['evaluation_type'] = 'ON_DEMAND'
                # Ensure scheme_code is set (scheme_id is actually scheme_code)
                eval_result['scheme_code'] = scheme_id
                eval_result['scheme_id'] = scheme_id  # Keep for backward compatibility
                
                # Record versions (rule set, dataset versions)
                eval_result['rule_set_version'] = self._get_current_rule_set_version(scheme_id)
                eval_result['dataset_version_golden_records'] = self._get_current_dataset_version('golden_records')
                eval_result['dataset_version_profile_360'] = self._get_current_dataset_version('profile_360')
                
                # Save to database if requested
                if save_results:
                    snapshot_id = self._save_evaluation_snapshot(eval_result)
                    eval_result['snapshot_id'] = snapshot_id
                
                evaluations.append(eval_result)
            
            except Exception as e:
                print(f"❌ Error evaluating {scheme_id} for family {family_id}: {e}")
                evaluations.append({
                    'scheme_id': scheme_id,
                    'family_id': family_id,
                    'evaluation_status': 'ERROR',
                    'error': str(e)
                })
        
        return {
            'family_id': family_id,
            'evaluated_at': datetime.now().isoformat(),
            'schemes_evaluated': len(scheme_ids),
            'evaluations': evaluations
        }
    
    def evaluate_batch(
        self,
        batch_id: Optional[str] = None,
        scheme_ids: Optional[List[str]] = None,
        district_ids: Optional[List[int]] = None,
        family_id_range: Optional[Tuple[str, str]] = None,
        max_families: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Batch evaluation for multiple families
        
        Args:
            batch_id: Batch ID (auto-generated if None)
            scheme_ids: Schemes to evaluate (None for all active)
            district_ids: Districts to evaluate (None for all)
            family_id_range: Tuple of (start_id, end_id) for range evaluation
            max_families: Maximum number of families to evaluate
        
        Returns:
            Batch evaluation results
        """
        if not self.batch_enabled:
            return {'error': 'Batch evaluation is disabled'}
        
        # Generate batch ID
        if batch_id is None:
            batch_id = f"BATCH_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Create batch job record
        job_id = self._create_batch_job(
            batch_id, scheme_ids, district_ids, family_id_range
        )
        
        # Load families to evaluate
        families = self._load_families_for_batch(
            district_ids, family_id_range, max_families
        )
        
        print(f"📊 Starting batch evaluation: {batch_id}")
        print(f"   Families to evaluate: {len(families)}")
        print(f"   Schemes: {scheme_ids or 'ALL'}")
        
        # Get schemes
        if scheme_ids is None:
            scheme_ids = self._get_active_schemes()
        
        total_evaluations = 0
        errors = 0
        
        # Evaluate families
        for idx, family in enumerate(families, 1):
            # Safely get family_id
            family_id = family.get('family_id') if family else None
            if not family_id:
                print(f"⚠️  Skipping family with missing family_id: {family}")
                errors += 1
                continue
            
            try:
                # Update progress
                if idx % 100 == 0:
                    self._update_batch_progress(
                        job_id, idx, len(families), total_evaluations
                    )
                    print(f"   Progress: {idx}/{len(families)} families ({idx*100//len(families)}%)")
                
                # Evaluate for each scheme
                for scheme_id in scheme_ids:
                    eval_result = self.evaluator.evaluate(
                        scheme_id, family, use_ml=True
                    )
                    
                    # Check if evaluation returned a result
                    if eval_result is None:
                        print(f"⚠️  Evaluation returned None for family {family_id}, scheme {scheme_id}")
                        errors += 1
                        continue
                    
                    # Save snapshot
                    eval_result['evaluation_type'] = 'BATCH'
                    eval_result['evaluation_timestamp'] = datetime.now()
                    # Ensure scheme_code is set (scheme_id is actually scheme_code)
                    eval_result['scheme_code'] = scheme_id
                    eval_result['scheme_id'] = scheme_id  # Keep for backward compatibility
                    # Ensure family_id is set
                    if 'family_id' not in eval_result:
                        eval_result['family_id'] = family_id
                    
                    # Record versions
                    eval_result['rule_set_version'] = self._get_current_rule_set_version(scheme_id)
                    eval_result['dataset_version_golden_records'] = self._get_current_dataset_version('golden_records')
                    eval_result['dataset_version_profile_360'] = self._get_current_dataset_version('profile_360')
                    
                    snapshot_id = self._save_evaluation_snapshot(eval_result)
                    if snapshot_id:
                        total_evaluations += 1
                    else:
                        errors += 1
            
            except Exception as e:
                errors += 1
                print(f"❌ Error evaluating family {family_id}: {e}")
                continue
        
        # Complete batch job
        self._complete_batch_job(job_id, len(families), total_evaluations, errors)
        
        print(f"✅ Batch evaluation complete: {batch_id}")
        print(f"   Families evaluated: {len(families)}")
        print(f"   Evaluations created: {total_evaluations}")
        print(f"   Errors: {errors}")
        
        return {
            'batch_id': batch_id,
            'job_id': job_id,
            'families_evaluated': len(families),
            'total_evaluations': total_evaluations,
            'errors': errors,
            'completed_at': datetime.now().isoformat()
        }
    
    def evaluate_event_driven(
        self,
        family_id: str,
        event_type: str,
        event_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Event-driven evaluation (triggered by family changes)
        
        Args:
            family_id: Family ID
            event_type: Event type (age_threshold_crossed, new_child_added, etc.)
            event_data: Additional event data
        
        Returns:
            Evaluation results
        """
        if not self.event_driven_enabled:
            return {'error': 'Event-driven evaluation is disabled'}
        
        # Check if event type should trigger evaluation
        trigger_events = self.config['evaluation']['event_driven']['triggers']
        if event_type not in trigger_events:
            return {
                'skipped': True,
                'reason': f'Event type {event_type} does not trigger evaluation'
            }
        
        # Determine which schemes to re-evaluate based on event
        scheme_ids = self._get_schemes_for_event(event_type)
        
        # Evaluate
        result = self.evaluate_family(
            family_id, scheme_ids=scheme_ids, use_ml=True, save_results=True
        )
        
        result['event_type'] = event_type
        result['evaluation_type'] = 'EVENT_DRIVEN'
        
        return result
    
    def get_precomputed_results(
        self,
        family_id: str,
        scheme_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get precomputed eligibility results from database
        
        Args:
            family_id: Family ID
            scheme_ids: Scheme IDs to get (None for all)
        
        Returns:
            Precomputed results
        """
        query = """
            SELECT 
                snapshot_id, scheme_code, evaluation_status,
                eligibility_score, confidence_score,
                rule_path, explanation, evaluation_timestamp
            FROM eligibility.eligibility_snapshots
            WHERE family_id = %s
                AND evaluation_timestamp >= CURRENT_DATE - INTERVAL '30 days'
        """
        
        params = [family_id]
        if scheme_ids:
            placeholders = ','.join(['%s'] * len(scheme_ids))
            query += f" AND scheme_code IN ({placeholders})"
            params.extend(scheme_ids)
        
        query += " ORDER BY evaluation_timestamp DESC"
        
        df = pd.read_sql(query, self.db.connection, params=params)
        
        results = []
        for _, row in df.iterrows():
            results.append({
                'scheme_id': row['scheme_code'],  # Return as scheme_id for API compatibility
                'status': row['evaluation_status'],
                'eligibility_score': float(row['eligibility_score']) if row['eligibility_score'] else 0.0,
                'confidence': float(row['confidence_score']) if row['confidence_score'] else 0.0,
                'rule_path': row['rule_path'],
                'explanation': row['explanation'],
                'evaluated_at': row['evaluation_timestamp'].isoformat() if row['evaluation_timestamp'] else None
            })
        
        return {
            'family_id': family_id,
            'results': results,
            'count': len(results)
        }
    
    def generate_citizen_hints(self, family_id: str) -> List[Dict]:
        """
        Generate citizen-facing eligibility hints
        
        Args:
            family_id: Family ID
        
        Returns:
            List of top N scheme hints
        """
        # Get precomputed results or evaluate on-demand
        precomputed = self.get_precomputed_results(family_id)
        
        if not precomputed['results']:
            # No precomputed results, evaluate on-demand
            evaluation_result = self.evaluate_family(
                family_id, use_ml=True, save_results=True
            )
            
            # Convert to scheme_evaluations format
            scheme_evaluations = {
                e['scheme_id']: e for e in evaluation_result['evaluations']
            }
        else:
            # Use precomputed results
            scheme_evaluations = {
                r['scheme_id']: r for r in precomputed['results']
            }
        
        # Generate hints using prioritizer
        hints = self.prioritizer.generate_citizen_hints(family_id, scheme_evaluations)
        
        return hints
    
    def generate_departmental_worklist(
        self,
        scheme_id: str,
        district_id: Optional[int] = None,
        min_score: float = 0.5,
        limit: int = 100
    ) -> List[Dict]:
        """
        Generate departmental worklist for a scheme
        
        Args:
            scheme_id: Scheme ID
            district_id: Optional district filter
            min_score: Minimum eligibility score
            limit: Maximum number of candidates
        
        Returns:
            Worklist (ranked candidates)
        """
        # Query recent evaluations
        query = """
            SELECT 
                snapshot_id, family_id, member_id, scheme_code,
                evaluation_status, eligibility_score, confidence_score,
                rule_path, explanation, reason_codes, evaluation_timestamp
            FROM eligibility.eligibility_snapshots
            WHERE scheme_code = %s
                AND evaluation_status IN ('RULE_ELIGIBLE', 'POSSIBLE_ELIGIBLE')
                AND eligibility_score >= %s
                AND evaluation_timestamp >= CURRENT_DATE - INTERVAL '7 days'
        """
        
        params = [scheme_id, min_score]
        
        if district_id:
            # Join with family data to filter by district
            query = """
                SELECT 
                    s.snapshot_id, s.family_id, s.member_id, s.scheme_code,
                    s.evaluation_status, s.eligibility_score, s.confidence_score,
                    s.rule_path, s.explanation, s.reason_codes, s.evaluation_timestamp,
                    f.district_id
                FROM eligibility.eligibility_snapshots s
                JOIN golden_records f ON s.family_id = f.gr_id
                WHERE s.scheme_code = %s
                    AND s.evaluation_status IN ('RULE_ELIGIBLE', 'POSSIBLE_ELIGIBLE')
                    AND s.eligibility_score >= %s
                    AND f.district_id = %s
                    AND s.evaluation_timestamp >= CURRENT_DATE - INTERVAL '7 days'
            """
            params.append(district_id)
        
        query += " ORDER BY eligibility_score DESC LIMIT %s"
        params.append(limit * 2)  # Get more, then rank and limit
        
        df = pd.read_sql(query, self.db.connection, params=params)
        
        # Convert to evaluation format
        evaluations = []
        for _, row in df.iterrows():
            evaluations.append({
                'snapshot_id': row['snapshot_id'],
                'family_id': str(row['family_id']),
                'member_id': str(row['member_id']) if pd.notna(row['member_id']) else None,
                'scheme_id': row['scheme_code'],  # Return as scheme_id for API compatibility
                'evaluation_status': row['evaluation_status'],
                'eligibility_score': float(row['eligibility_score']),
                'confidence_score': float(row['confidence_score']),
                'district_id': row.get('district_id'),
                'rule_path': row['rule_path'],
                'explanation': row['explanation'],
                'reason_codes': row['reason_codes'] if row['reason_codes'] else []
            })
        
        # Rank and generate worklist
        worklist = self.prioritizer.generate_departmental_worklist(
            scheme_id, evaluations, district_id, min_score, limit
        )
        
        # Save worklist to database
        self.prioritizer.save_candidate_list(scheme_id, worklist, 'DEPARTMENT_WORKLIST')
        
        return worklist
    
    def _load_family_data(self, family_id: str) -> Optional[Dict]:
        """
        Load family data from Golden Records + 360° Profile
        
        Args:
            family_id: Family ID (UUID string)
        
        Returns:
            Dictionary with combined family data
        """
        try:
            # Load external database configs
            db_config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
            with open(db_config_path, 'r') as f:
                db_config = yaml.safe_load(f)
            
            # Connect to Golden Records database
            # Use profile_360 config (golden_records are in smart_warehouse)
            gr_db_config = db_config['external_databases']['profile_360']
            gr_db = DBConnector(
                host=gr_db_config['host'],
                port=gr_db_config['port'],
                database=gr_db_config['name'],
                user=gr_db_config['user'],
                password=gr_db_config['password']
            )
            gr_db.connect()
            
            # Load Golden Record data (family head or member)
            gr_query = """
                SELECT 
                    gr_id, family_id, citizen_id, jan_aadhaar,
                    full_name, date_of_birth, age, gender, caste_id,
                    district_id, city_village, pincode, is_urban,
                    status
                FROM golden_records
                WHERE gr_id::text = %s OR family_id::text = %s
                ORDER BY 
                    CASE WHEN family_id IS NULL THEN 0 ELSE 1 END,
                    age DESC
                LIMIT 1
            """
            
            gr_df = pd.read_sql(gr_query, gr_db.connection, params=(family_id, family_id))
            
            if gr_df.empty:
                gr_db.disconnect()
                return None
            
            gr_data = gr_df.iloc[0]
            
            # Get family head data if this is a member
            actual_family_id = str(gr_data['family_id']) if pd.notna(gr_data['family_id']) else str(gr_data['gr_id'])
            
            # Load all family members for household composition
            family_query = """
                SELECT 
                    COUNT(*) as family_size,
                    MIN(age) as min_age,
                    MAX(age) as max_age,
                    COUNT(CASE WHEN age < 18 THEN 1 END) as children_count,
                    COUNT(CASE WHEN age >= 60 THEN 1 END) as elderly_count,
                    COUNT(CASE WHEN gender = 'Female' THEN 1 END) as female_count
                FROM golden_records
                WHERE family_id::text = %s OR (family_id IS NULL AND gr_id::text = %s)
            """
            
            family_stats = pd.read_sql(
                family_query, gr_db.connection, 
                params=(actual_family_id, actual_family_id)
            ).iloc[0]
            
            gr_db.disconnect()
            
            # Connect to 360° Profile database
            profile_db_config = db_config['external_databases']['profile_360']
            profile_db = DBConnector(
                host=profile_db_config['host'],
                port=profile_db_config['port'],
                database=profile_db_config['name'],
                user=profile_db_config['user'],
                password=profile_db_config['password']
            )
            profile_db.connect()
            
            # Load 360° Profile data
            profile_query = """
                SELECT 
                    profile_data,
                    inferred_income_band,
                    cluster_id
                FROM profile_360
                WHERE gr_id::text = %s OR family_id::text = %s
                ORDER BY updated_at DESC
                LIMIT 1
            """
            
            profile_df = pd.read_sql(
                profile_query, profile_db.connection,
                params=(actual_family_id, actual_family_id)
            )
            
            profile_data = {}
            income_band = None
            
            if not profile_df.empty:
                profile_row = profile_df.iloc[0]
                if pd.notna(profile_row.get('profile_data')):
                    import json
                    if isinstance(profile_row['profile_data'], dict):
                        profile_data = profile_row['profile_data']
                    elif isinstance(profile_row['profile_data'], str):
                        profile_data = json.loads(profile_row['profile_data'])
                
                income_band = profile_row.get('inferred_income_band')
            
            # Load benefit history
            benefit_query = """
                SELECT 
                    COUNT(*) as schemes_enrolled_count,
                    COUNT(DISTINCT scheme_id) as unique_schemes_count,
                    SUM(amount) as benefits_received_total_1y,
                    COUNT(*) FILTER (WHERE txn_date >= CURRENT_DATE - INTERVAL '3 years') as benefits_received_total_3y
                FROM benefit_events
                WHERE gr_id::text = %s OR gr_id IN (
                    SELECT gr_id FROM golden_records 
                    WHERE family_id::text = %s OR (family_id IS NULL AND gr_id::text = %s)
                )
            """
            
            benefits = pd.read_sql(
                benefit_query, profile_db.connection,
                params=(actual_family_id, actual_family_id, actual_family_id)
            ).iloc[0]
            
            # Load schemes enrolled
            schemes_query = """
                SELECT DISTINCT scheme_id
                FROM benefit_events
                WHERE gr_id::text = %s OR gr_id IN (
                    SELECT gr_id FROM golden_records 
                    WHERE family_id::text = %s OR (family_id IS NULL AND gr_id::text = %s)
                )
            """
            
            schemes_df = pd.read_sql(
                schemes_query, profile_db.connection,
                params=(actual_family_id, actual_family_id, actual_family_id)
            )
            schemes_enrolled_list = schemes_df['scheme_id'].tolist() if not schemes_df.empty else []
            
            profile_db.disconnect()
            
            # Combine all data
            combined_data = {
                # Family identifiers
                'family_id': actual_family_id,
                'gr_id': str(gr_data['gr_id']),
                'citizen_id': str(gr_data['citizen_id']) if pd.notna(gr_data['citizen_id']) else None,
                
                # Demographics (head of family)
                'head_age': int(gr_data['age']) if pd.notna(gr_data['age']) else None,
                'head_gender': str(gr_data['gender']) if pd.notna(gr_data['gender']) else None,
                'age': int(gr_data['age']) if pd.notna(gr_data['age']) else None,
                'gender': str(gr_data['gender']) if pd.notna(gr_data['gender']) else None,
                'full_name': str(gr_data['full_name']) if pd.notna(gr_data['full_name']) else None,
                
                # Location
                'district_id': int(gr_data['district_id']) if pd.notna(gr_data['district_id']) else None,
                'block_id': None,  # TODO: Add block_id if available
                'village_id': None,  # TODO: Add village_id if available
                'city_village': str(gr_data['city_village']) if pd.notna(gr_data['city_village']) else None,
                'pincode': str(gr_data['pincode']) if pd.notna(gr_data['pincode']) else None,
                'is_urban': bool(gr_data['is_urban']) if pd.notna(gr_data['is_urban']) else False,
                
                # Social
                'caste_id': int(gr_data['caste_id']) if pd.notna(gr_data['caste_id']) else None,
                
                # Household composition
                'family_size': int(family_stats['family_size']) if pd.notna(family_stats['family_size']) else 1,
                'children_count': int(family_stats['children_count']) if pd.notna(family_stats['children_count']) else 0,
                'elderly_count': int(family_stats['elderly_count']) if pd.notna(family_stats['elderly_count']) else 0,
                
                # Income (from 360° Profile)
                'income_band': income_band or profile_data.get('socio_economic', {}).get('inferred_income_band', 'UNKNOWN'),
                'inferred_income_band': income_band,
                
                # Benefits
                'schemes_enrolled_count': int(benefits['schemes_enrolled_count']) if pd.notna(benefits['schemes_enrolled_count']) else 0,
                'schemes_enrolled_list': schemes_enrolled_list,
                'benefits_received_total_1y': float(benefits['benefits_received_total_1y']) if pd.notna(benefits['benefits_received_total_1y']) else 0.0,
                'benefits_received_total_3y': float(benefits['benefits_received_total_3y']) if pd.notna(benefits['benefits_received_total_3y']) else 0.0,
                
                # Additional from 360° Profile
                'cluster_id': profile_data.get('cluster_id'),
                'vulnerability_level': profile_data.get('vulnerability_level', 'MEDIUM'),
                'under_coverage_indicator': profile_data.get('under_coverage_indicator', False),
            }
            
            return combined_data
        
        except Exception as e:
            print(f"❌ Error loading family data for {family_id}: {e}")
            return None
    
    def _load_families_for_batch(
        self,
        district_ids: Optional[List[int]],
        family_id_range: Optional[Tuple[str, str]],
        max_families: Optional[int]
    ) -> List[Dict]:
        """
        Load families for batch evaluation
        
        Args:
            district_ids: Optional district filter
            family_id_range: Optional family ID range
            max_families: Maximum number of families to load
        
        Returns:
            List of family data dictionaries
        """
        try:
            # Load external database config
            db_config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
            with open(db_config_path, 'r') as f:
                db_config = yaml.safe_load(f)
            
            # Use profile_360 config (golden_records are in smart_warehouse, not smart database)
            profile_db_config = db_config['external_databases']['profile_360']
            gr_db = DBConnector(
                host=profile_db_config['host'],
                port=profile_db_config['port'],
                database=profile_db_config['name'],
                user=profile_db_config['user'],
                password=profile_db_config['password']
            )
            gr_db.connect()
            
            # Build query
            query = """
                SELECT DISTINCT
                    COALESCE(family_id::text, gr_id::text) as family_id
                FROM golden_records
                WHERE status = 'active'
            """
            
            params = []
            
            if district_ids:
                placeholders = ','.join(['%s'] * len(district_ids))
                query += f" AND district_id IN ({placeholders})"
                params.extend(district_ids)
            
            if family_id_range:
                query += " AND gr_id >= %s::uuid AND gr_id <= %s::uuid"
                params.extend([family_id_range[0], family_id_range[1]])
            
            query += " ORDER BY family_id LIMIT %s"
            params.append(max_families if max_families else 1000000)
            
            # Execute query
            family_ids_df = pd.read_sql(query, gr_db.connection, params=params)
            gr_db.disconnect()
            
            # Load data for each family
            families = []
            for _, row in family_ids_df.iterrows():
                family_id = str(row['family_id'])
                family_data = self._load_family_data(family_id)
                if family_data:
                    families.append(family_data)
                
                # Progress indication
                if len(families) % 100 == 0:
                    print(f"   Loaded {len(families)} families...")
            
            return families
        
        except Exception as e:
            print(f"❌ Error loading families for batch: {e}")
            return []
    
    def _get_active_schemes(self) -> List[str]:
        """Get list of active schemes"""
        query = """
            SELECT scheme_code
            FROM scheme_master
            WHERE status = 'active' AND is_auto_id_enabled = true
        """
        df = pd.read_sql(query, self.db.connection)
        return df['scheme_code'].tolist()
    
    def _get_schemes_for_event(self, event_type: str) -> List[str]:
        """Get schemes that should be re-evaluated for an event type"""
        # Map event types to scheme categories
        event_scheme_map = {
            'age_threshold_crossed': ['PENSION'],
            'new_child_added': ['EDUCATION', 'PDS'],
            'disability_registered': ['PENSION', 'DISABILITY'],
            'calamity_tagged': ['HOUSING', 'PDS'],
            'income_band_changed': ['ALL'],
            'household_composition_changed': ['ALL']
        }
        
        categories = event_scheme_map.get(event_type, ['ALL'])
        
        if 'ALL' in categories:
            return self._get_active_schemes()
        
        query = """
            SELECT scheme_code
            FROM scheme_master
            WHERE status = 'active'
                AND is_auto_id_enabled = true
                AND category = ANY(%s)
        """
        df = pd.read_sql(query, self.db.connection, params=(categories,))
        return df['scheme_code'].tolist()
    
    def _get_current_rule_set_version(self, scheme_code: str) -> str:
        """
        Get current rule set version for a scheme
        
        Args:
            scheme_code: Scheme code
            
        Returns:
            Rule set version string (e.g., "v1.0") or "CURRENT" if no snapshot exists
        """
        try:
            query = """
                SELECT snapshot_version
                FROM eligibility.rule_set_snapshots
                WHERE scheme_code = %s
                ORDER BY snapshot_date DESC, created_at DESC
                LIMIT 1
            """
            df = pd.read_sql(query, self.db.connection, params=(scheme_code,))
            
            if not df.empty:
                return df.iloc[0]['snapshot_version']
            else:
                # No snapshot exists, return default
                return "CURRENT"
        except Exception as e:
            # If table doesn't exist or error occurs, return default
            return "CURRENT"
    
    def _get_current_dataset_version(self, dataset_name: str) -> str:
        """
        Get current dataset version
        
        Args:
            dataset_name: Name of dataset ('golden_records', 'profile_360', etc.)
            
        Returns:
            Dataset version string (e.g., "v2.1") or "CURRENT" if no version exists
        """
        try:
            query = """
                SELECT version
                FROM eligibility.dataset_versions
                WHERE dataset_name = %s
                ORDER BY version_date DESC, created_at DESC
                LIMIT 1
            """
            df = pd.read_sql(query, self.db.connection, params=(dataset_name,))
            
            if not df.empty:
                return df.iloc[0]['version']
            else:
                # No version exists, return default
                return "CURRENT"
        except Exception as e:
            # If table doesn't exist or error occurs, return default
            return "CURRENT"
    
    def _save_evaluation_snapshot(self, eval_result: Dict) -> Optional[int]:
        """Save evaluation result to database"""
        cursor = self.db.connection.cursor()
        
        # Helper function to convert list/dict to JSON string for PostgreSQL
        def to_json(val):
            if val is None:
                return None
            if isinstance(val, (list, dict)):
                return json.dumps(val)
            return val
        
        try:
            # Check if version columns exist (for backward compatibility)
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'eligibility' 
                AND table_name = 'eligibility_snapshots' 
                AND column_name = 'rule_set_version'
            """)
            
            has_version_columns = cursor.rowcount > 0
            
            if has_version_columns:
                insert_query = """
                    INSERT INTO eligibility.eligibility_snapshots (
                        family_id, member_id, scheme_code,
                        evaluation_status, eligibility_score, confidence_score,
                        rule_eligible, rules_passed, rules_failed, rule_path,
                        ml_probability, ml_model_version, ml_top_features,
                        priority_score, vulnerability_level, under_coverage_indicator,
                        reason_codes, explanation,
                        evaluation_timestamp, evaluation_type, evaluation_version,
                        rule_set_version, dataset_version_golden_records, dataset_version_profile_360
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1,
                        %s, %s, %s
                    )
                    RETURNING snapshot_id
                """
                
                # Get scheme_code from eval_result (may be 'scheme_id' or 'scheme_code')
                scheme_code = eval_result.get('scheme_code') or eval_result.get('scheme_id')
                
                cursor.execute(insert_query, (
                    eval_result.get('family_id'),
                    eval_result.get('member_id'),
                    scheme_code,
                    eval_result.get('evaluation_status'),
                    eval_result.get('eligibility_score'),
                    eval_result.get('confidence_score'),
                    eval_result.get('rule_eligible'),
                    eval_result.get('rules_passed', []),  # TEXT[] - pass as list
                    eval_result.get('rules_failed', []),  # TEXT[] - pass as list
                    eval_result.get('rule_path'),
                    eval_result.get('ml_probability'),
                    eval_result.get('ml_result', {}).get('model_version') if isinstance(eval_result.get('ml_result'), dict) else None,
                    to_json(eval_result.get('ml_top_features')),  # JSONB - convert to JSON string
                    eval_result.get('priority_score'),
                    eval_result.get('vulnerability_level'),
                    eval_result.get('under_coverage_indicator'),
                    eval_result.get('reason_codes', []),  # TEXT[] - pass as list
                    eval_result.get('explanation'),
                    eval_result.get('evaluation_timestamp'),
                    eval_result.get('evaluation_type', 'ON_DEMAND'),
                    eval_result.get('rule_set_version'),
                    eval_result.get('dataset_version_golden_records'),
                    eval_result.get('dataset_version_profile_360')
                ))
                
                result = cursor.fetchone()
                if result is None:
                    raise Exception("INSERT did not return snapshot_id")
                snapshot_id = result[0]
                self.db.connection.commit()
                cursor.close()
                
                return snapshot_id
            else:
                # Fallback for older schema
                insert_query = """
                    INSERT INTO eligibility.eligibility_snapshots (
                        family_id, member_id, scheme_code,
                        evaluation_status, eligibility_score, confidence_score,
                        rule_eligible, rules_passed, rules_failed, rule_path,
                        ml_probability, ml_model_version, ml_top_features,
                        priority_score, vulnerability_level, under_coverage_indicator,
                        reason_codes, explanation,
                        evaluation_timestamp, evaluation_type, evaluation_version
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1
                    )
                    RETURNING snapshot_id
                """
                
                # Get scheme_code from eval_result (may be 'scheme_id' or 'scheme_code')
                scheme_code_fallback = eval_result.get('scheme_code') or eval_result.get('scheme_id')
                
                cursor.execute(insert_query, (
                    eval_result.get('family_id'),
                    eval_result.get('member_id'),
                    scheme_code_fallback,
                    eval_result.get('evaluation_status'),
                    eval_result.get('eligibility_score'),
                    eval_result.get('confidence_score'),
                    eval_result.get('rule_eligible'),
                    eval_result.get('rules_passed', []),  # TEXT[] - pass as list
                    eval_result.get('rules_failed', []),  # TEXT[] - pass as list
                    eval_result.get('rule_path'),
                    eval_result.get('ml_probability'),
                    eval_result.get('ml_result', {}).get('model_version') if isinstance(eval_result.get('ml_result'), dict) else None,
                    to_json(eval_result.get('ml_top_features')),  # JSONB - convert to JSON string
                    eval_result.get('priority_score'),
                    eval_result.get('vulnerability_level'),
                    eval_result.get('under_coverage_indicator'),
                    eval_result.get('reason_codes', []),  # TEXT[] - pass as list
                    eval_result.get('explanation'),
                    eval_result.get('evaluation_timestamp'),
                    eval_result.get('evaluation_type', 'ON_DEMAND')
                ))
                
                result = cursor.fetchone()
                if result is None:
                    raise Exception("INSERT did not return snapshot_id")
                snapshot_id = result[0]
                self.db.connection.commit()
                cursor.close()
                
                return snapshot_id
        
        except Exception as e:
            print(f"❌ Error saving snapshot: {e}")
            self.db.connection.rollback()
            cursor.close()
            return None
    
    def _create_batch_job(
        self,
        batch_id: str,
        scheme_ids: Optional[List[str]],
        district_ids: Optional[List[int]],
        family_id_range: Optional[Tuple[str, str]]
    ) -> int:
        """Create batch job record"""
        cursor = self.db.connection.cursor()
        
        insert_query = """
            INSERT INTO eligibility.batch_evaluation_jobs (
                batch_id, job_type, scheme_ids, district_ids,
                family_id_range_start, family_id_range_end,
                status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, 'RUNNING', CURRENT_TIMESTAMP)
            RETURNING job_id
        """
        
        job_type = 'FULL_SCAN'
        if district_ids:
            job_type = 'INCREMENTAL'
        if family_id_range:
            job_type = 'SCHEME_SPECIFIC'
        
        cursor.execute(insert_query, (
            batch_id, job_type, scheme_ids, district_ids,
            family_id_range[0] if family_id_range else None,
            family_id_range[1] if family_id_range else None
        ))
        
        job_id = cursor.fetchone()[0]
        self.db.connection.commit()
        cursor.close()
        
        return job_id
    
    def _update_batch_progress(
        self,
        job_id: int,
        families_processed: int,
        total_families: int,
        evaluations_created: int
    ):
        """Update batch job progress"""
        cursor = self.db.connection.cursor()
        
        progress = int((families_processed / total_families) * 100) if total_families > 0 else 0
        
        update_query = """
            UPDATE eligibility.batch_evaluation_jobs
            SET families_processed = %s,
                evaluations_created = %s,
                progress_percentage = %s
            WHERE job_id = %s
        """
        
        cursor.execute(update_query, (families_processed, evaluations_created, progress, job_id))
        self.db.connection.commit()
        cursor.close()
    
    def _complete_batch_job(
        self,
        job_id: int,
        total_families: int,
        total_evaluations: int,
        errors: int
    ):
        """Mark batch job as completed"""
        cursor = self.db.connection.cursor()
        
        update_query = """
            UPDATE eligibility.batch_evaluation_jobs
            SET status = 'COMPLETED',
                total_families = %s,
                families_processed = %s,
                evaluations_created = %s,
                errors_count = %s,
                progress_percentage = 100,
                completed_at = CURRENT_TIMESTAMP
            WHERE job_id = %s
        """
        
        cursor.execute(update_query, (
            total_families, total_families, total_evaluations, errors, job_id
        ))
        self.db.connection.commit()
        cursor.close()
    
    def close(self):
        """Close all connections"""
        if self.evaluator:
            self.evaluator.close()
        if self.prioritizer:
            self.prioritizer.close()
        if self.db:
            self.db.disconnect()


def main():
    """Test evaluation service"""
    service = EligibilityEvaluationService()
    
    # Test on-demand evaluation
    print("Testing on-demand evaluation...")
    result = service.evaluate_family('test-family-001', use_ml=False)
    print(f"Evaluated {result.get('schemes_evaluated', 0)} schemes")
    
    service.close()


if __name__ == "__main__":
    main()

