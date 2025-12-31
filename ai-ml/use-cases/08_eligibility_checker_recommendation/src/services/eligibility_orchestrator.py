"""
Eligibility Checker Orchestrator
Use Case ID: AI-PLATFORM-08

Main orchestrator service that coordinates eligibility checking, ranking, and explanation generation.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
import yaml

# Import services
from services.eligibility_checker import EligibilityChecker
from models.scheme_ranker import SchemeRanker
from generators.explanation_generator import ExplanationGenerator
from services.questionnaire_handler import QuestionnaireHandler


class EligibilityOrchestrator:
    """
    Eligibility Checker Orchestrator
    
    Coordinates:
    - Eligibility checking (logged-in and guest)
    - Scheme ranking and recommendations
    - Explanation generation
    - Recommendation set creation and caching
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Eligibility Orchestrator"""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "use_case_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize services
        self.eligibility_checker = EligibilityChecker(config_path)
        self.scheme_ranker = SchemeRanker(config_path)
        self.explanation_generator = ExplanationGenerator(config_path)
        self.questionnaire_handler = QuestionnaireHandler(config_path)
        
        # Configuration
        self.recommendation_config = self.config.get('recommendation', {})
        self.top_recommendations_count = self.recommendation_config.get('top_recommendations_count', 5)
    
    def connect(self):
        """Connect all services to databases"""
        self.eligibility_checker.connect()
        self.scheme_ranker.connect()
        self.explanation_generator.connect()
        self.questionnaire_handler.connect()
    
    def disconnect(self):
        """Disconnect all services from databases"""
        self.eligibility_checker.disconnect()
        self.scheme_ranker.disconnect()
        self.explanation_generator.disconnect()
        self.questionnaire_handler.disconnect()
    
    def check_and_recommend(
        self,
        family_id: Optional[str] = None,
        beneficiary_id: Optional[str] = None,
        questionnaire_responses: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        scheme_codes: Optional[List[str]] = None,
        check_type: str = 'FULL_CHECK',
        check_mode: str = 'WEB',
        generate_recommendations: bool = True,
        language: str = 'en'
    ) -> Dict[str, Any]:
        """
        Perform eligibility check and generate recommendations
        
        Args:
            family_id: Family ID for logged-in users
            beneficiary_id: Optional beneficiary ID
            questionnaire_responses: Guest user questionnaire
            session_id: Session ID
            scheme_codes: Schemes to check (None for all)
            check_type: Check type
            check_mode: Check mode
            generate_recommendations: Whether to generate recommendations
            language: Language for explanations
        
        Returns:
            Complete check result with recommendations
        """
        # 1. Perform eligibility check
        check_result = self.eligibility_checker.check_eligibility(
            family_id=family_id,
            beneficiary_id=beneficiary_id,
            questionnaire_responses=questionnaire_responses,
            session_id=session_id,
            scheme_codes=scheme_codes,
            check_type=check_type,
            check_mode=check_mode
        )
        
        evaluations = check_result.get('evaluations', [])
        
        # 2. Rank schemes
        ranked_evaluations = self.scheme_ranker.rank_schemes(
            evaluations=evaluations,
            family_id=family_id,
            context={'language': language}
        )
        
        # 3. Generate explanations
        for eval_result in ranked_evaluations:
            explanation = self.explanation_generator.generate_explanation(
                eval_result=eval_result,
                language=language
            )
            eval_result.update(explanation)
        
        # 4. Generate recommendations if requested
        recommendations = None
        recommendation_id = None
        
        if generate_recommendations and family_id:  # Only for logged-in users
            recommendations_result = self._generate_recommendation_set(
                family_id=family_id,
                beneficiary_id=beneficiary_id,
                ranked_evaluations=ranked_evaluations,
                check_id=check_result.get('check_id')
            )
            recommendations = recommendations_result.get('recommendations')
            recommendation_id = recommendations_result.get('recommendation_id')
        
        # 5. Separate into top recommendations and others
        top_recommendations = [
            e for e in ranked_evaluations
            if e.get('recommendation_rank', 999) <= self.top_recommendations_count
            and e.get('eligibility_status') in ['ELIGIBLE', 'POSSIBLE_ELIGIBLE']
        ]
        
        other_schemes = [
            e for e in ranked_evaluations
            if e.get('recommendation_rank', 999) > self.top_recommendations_count
            or e.get('eligibility_status') == 'NOT_ELIGIBLE'
        ]
        
        # Build result
        result = {
            'check_id': check_result.get('check_id'),
            'session_id': check_result.get('session_id'),
            'user_type': check_result.get('user_type'),
            'is_approximate': check_result.get('is_approximate', False),
            'total_schemes_checked': check_result.get('total_schemes_checked'),
            'eligible_count': check_result.get('eligible_count'),
            'possible_eligible_count': check_result.get('possible_eligible_count'),
            'not_eligible_count': check_result.get('not_eligible_count'),
            'processing_time_ms': check_result.get('processing_time_ms'),
            'top_recommendations': top_recommendations,
            'other_schemes': other_schemes,
            'all_evaluations': ranked_evaluations
        }
        
        if recommendation_id:
            result['recommendation_id'] = recommendation_id
        
        return result
    
    def get_recommendations(
        self,
        family_id: str,
        beneficiary_id: Optional[str] = None,
        refresh: bool = False,
        language: str = 'en'
    ) -> Dict[str, Any]:
        """
        Get recommendations for logged-in user
        
        Args:
            family_id: Family ID
            beneficiary_id: Optional beneficiary ID
            refresh: Whether to refresh recommendations
            language: Language for explanations
        
        Returns:
            Recommendations with explanations
        """
        # Check for existing recommendations
        if not refresh:
            existing = self._get_existing_recommendations(family_id, beneficiary_id)
            if existing:
                return existing
        
        # Generate new recommendations
        return self.check_and_recommend(
            family_id=family_id,
            beneficiary_id=beneficiary_id,
            generate_recommendations=True,
            language=language
        )
    
    def _generate_recommendation_set(
        self,
        family_id: str,
        beneficiary_id: Optional[str],
        ranked_evaluations: List[Dict[str, Any]],
        check_id: Optional[int]
    ) -> Dict[str, Any]:
        """Generate and save recommendation set"""
        from db_connector import DBConnector
        import json
        
        # Use eligibility_checker's db connection
        conn = self.eligibility_checker.db.connection
        cursor = conn.cursor()
        
        try:
            # Create recommendation set
            expires_at = datetime.now() + timedelta(days=30)  # Recommendations valid for 30 days
            
            cursor.execute("""
                INSERT INTO eligibility_checker.recommendation_sets (
                    family_id, beneficiary_id, recommendation_type,
                    total_schemes, top_recommendations_count,
                    expires_at, based_on_check_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING recommendation_id
            """, (
                family_id, beneficiary_id, 'TOP_RECOMMENDATIONS',
                len(ranked_evaluations), self.top_recommendations_count,
                expires_at, check_id
            ))
            
            recommendation_id = cursor.fetchone()[0]
            
            # Create recommendation items
            for eval_result in ranked_evaluations[:self.top_recommendations_count]:
                if eval_result.get('eligibility_status') in ['ELIGIBLE', 'POSSIBLE_ELIGIBLE']:
                    cursor.execute("""
                        INSERT INTO eligibility_checker.recommendation_items (
                            recommendation_id, scheme_code, scheme_name,
                            rank, priority_score, eligibility_status,
                            eligibility_score, recommendation_reasons,
                            benefit_summary
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        recommendation_id,
                        eval_result.get('scheme_code'),
                        eval_result.get('scheme_name'),
                        eval_result.get('recommendation_rank'),
                        eval_result.get('priority_score'),
                        eval_result.get('eligibility_status'),
                        eval_result.get('eligibility_score'),
                        eval_result.get('recommendation_reasons', []),
                        eval_result.get('explanation_text', '')[:100]
                    ))
            
            conn.commit()
            cursor.close()
            
            return {
                'recommendation_id': recommendation_id,
                'recommendations': ranked_evaluations[:self.top_recommendations_count]
            }
        
        except Exception as e:
            print(f"⚠️  Error generating recommendation set: {e}")
            conn.rollback()
            cursor.close()
            return {
                'recommendation_id': None,
                'recommendations': []
            }
    
    def _get_existing_recommendations(
        self,
        family_id: str,
        beneficiary_id: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Get existing active recommendations"""
        conn = self.eligibility_checker.db.connection
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT recommendation_id, generated_at, expires_at, total_schemes
                FROM eligibility_checker.recommendation_sets
                WHERE family_id = %s
                  AND (beneficiary_id = %s OR (beneficiary_id IS NULL AND %s IS NULL))
                  AND is_active = TRUE
                  AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
                ORDER BY generated_at DESC
                LIMIT 1
            """, (family_id, beneficiary_id, beneficiary_id))
            
            row = cursor.fetchone()
            if not row:
                cursor.close()
                return None
            
            recommendation_id, generated_at, expires_at, total_schemes = row
            
            # Get recommendation items
            cursor.execute("""
                SELECT scheme_code, scheme_name, rank, priority_score,
                       eligibility_status, eligibility_score, recommendation_reasons,
                       benefit_summary
                FROM eligibility_checker.recommendation_items
                WHERE recommendation_id = %s
                ORDER BY rank
            """, (recommendation_id,))
            
            items = []
            for item_row in cursor.fetchall():
                items.append({
                    'scheme_code': item_row[0],
                    'scheme_name': item_row[1],
                    'recommendation_rank': item_row[2],
                    'priority_score': float(item_row[3]),
                    'eligibility_status': item_row[4],
                    'eligibility_score': float(item_row[5]),
                    'recommendation_reasons': item_row[6] or [],
                    'benefit_summary': item_row[7]
                })
            
            cursor.close()
            
            return {
                'recommendation_id': recommendation_id,
                'generated_at': generated_at.isoformat() if generated_at else None,
                'expires_at': expires_at.isoformat() if expires_at else None,
                'top_recommendations': items,
                'other_schemes': []
            }
        
        except Exception as e:
            print(f"⚠️  Error fetching existing recommendations: {e}")
            cursor.close()
            return None

