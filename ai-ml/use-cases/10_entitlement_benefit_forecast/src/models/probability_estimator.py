"""
ML-based Probability Estimator for Forecast Recommendations
Use Case ID: AI-PLATFORM-10

Estimates probability of recommendation acceptance based on historical data,
user behavior, and recommendation effectiveness.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
import yaml
from collections import defaultdict

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector

# ML imports
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, precision_score, recall_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️  scikit-learn not available. ML-based probability estimation will use heuristics.")


class ProbabilityEstimator:
    """
    ML-based Probability Estimator
    
    Estimates the probability that a citizen will act on a recommendation
    based on:
    1. Historical application rates
    2. User behavior patterns
    3. Recommendation effectiveness tracking
    4. Demographic and scheme-specific factors
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Probability Estimator"""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "use_case_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Database configuration
        db_config_path = Path(__file__).parent.parent.parent / "config" / "db_config.yaml"
        with open(db_config_path, 'r') as f:
            db_configs = yaml.safe_load(f)
        
        self.db = DBConnector(
            host=db_configs['database']['host'],
            port=db_configs['database']['port'],
            database=db_configs['database']['name'],
            user=db_configs['database']['user'],
            password=db_configs['database']['password']
        )
        
        # External database connections
        self.external_dbs = {}
        for db_alias, ext_config in db_configs.get('external_databases', {}).items():
            self.external_dbs[db_alias] = DBConnector(
                host=ext_config['host'],
                port=ext_config['port'],
                database=ext_config['name'],
                user=ext_config['user'],
                password=ext_config['password']
            )
        
        # ML model (will be trained/loaded)
        self.probability_model = None
        self.is_model_trained = False
        
        # Feature weights (for heuristic fallback)
        self.feature_weights = {
            'historical_rate': 0.4,
            'scheme_popularity': 0.2,
            'eligibility_score': 0.2,
            'user_engagement': 0.1,
            'time_since_recommendation': 0.1
        }
    
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
    
    def estimate_probability(
        self,
        family_id: str,
        scheme_code: str,
        eligibility_status: str,
        recommendation_rank: int,
        days_since_recommendation: int = 0
    ) -> float:
        """
        Estimate probability that family will act on recommendation
        
        Args:
            family_id: Family ID
            scheme_code: Recommended scheme code
            eligibility_status: ELIGIBLE or POSSIBLE_ELIGIBLE
            recommendation_rank: Rank of recommendation (1-10)
            days_since_recommendation: Days since recommendation was made
        
        Returns:
            Probability score (0.0 to 1.0)
        """
        # Extract features
        features = self._extract_features(
            family_id, scheme_code, eligibility_status, 
            recommendation_rank, days_since_recommendation
        )
        
        # Use ML model if available and trained
        if self.is_model_trained and self.probability_model:
            try:
                # Convert features to model input format
                feature_vector = self._features_to_vector(features)
                probability = self.probability_model.predict_proba([feature_vector])[0][1]
                return float(probability)
            except Exception as e:
                print(f"⚠️  ML model prediction failed, using heuristic: {e}")
        
        # Fallback to heuristic-based estimation
        return self._heuristic_probability(features)
    
    def _extract_features(
        self,
        family_id: str,
        scheme_code: str,
        eligibility_status: str,
        recommendation_rank: int,
        days_since_recommendation: int
    ) -> Dict[str, Any]:
        """Extract features for probability estimation"""
        features = {
            'scheme_code': scheme_code,
            'eligibility_status': eligibility_status,
            'recommendation_rank': recommendation_rank,
            'days_since_recommendation': days_since_recommendation
        }
        
        # 1. Historical application rate (family level)
        features['historical_application_rate'] = self._get_family_application_rate(family_id)
        
        # 2. Scheme popularity (historical acceptance rate)
        features['scheme_popularity'] = self._get_scheme_popularity(scheme_code)
        
        # 3. Eligibility score impact
        features['eligibility_score'] = 1.0 if eligibility_status == 'ELIGIBLE' else 0.7
        
        # 4. User engagement (how many recommendations they've acted on)
        features['user_engagement'] = self._get_user_engagement_score(family_id)
        
        # 5. Recommendation rank impact
        features['rank_score'] = max(0.5, 1.0 - (recommendation_rank - 1) * 0.1)
        
        # 6. Time decay (older recommendations less likely)
        features['time_decay'] = max(0.3, 1.0 - (days_since_recommendation / 90.0))
        
        # 7. Scheme type factors (from 360° profile if available)
        features['scheme_type_match'] = self._get_scheme_type_match(family_id, scheme_code)
        
        return features
    
    def _get_family_application_rate(self, family_id: str) -> float:
        """Get historical application rate for family"""
        try:
            conn = self.external_dbs.get('eligibility_checker')
            if not conn:
                return 0.5  # Default
            
            cursor = conn.connection.cursor()
            
            # Count recommendations made to this family
            cursor.execute("""
                SELECT COUNT(*) 
                FROM eligibility_checker.scheme_eligibility_results ser
                INNER JOIN eligibility_checker.eligibility_checks ec ON ser.check_id = ec.check_id
                WHERE ec.family_id = %s::uuid
                  AND ser.eligibility_status IN ('ELIGIBLE', 'POSSIBLE_ELIGIBLE')
                  AND ser.recommendation_rank IS NOT NULL
                  AND ec.check_timestamp >= CURRENT_TIMESTAMP - INTERVAL '180 days'
            """, (family_id,))
            
            total_recommendations = cursor.fetchone()[0] or 0
            
            # Count applications generated (proxy: check if they have benefit history)
            # This is simplified - in real system, would track application events
            cursor.execute("""
                SELECT COUNT(DISTINCT scheme_code)
                FROM profile_360.benefit_history bh
                JOIN golden_records.beneficiaries grb ON bh.beneficiary_id = grb.beneficiary_id
                WHERE grb.family_id = %s::uuid
                  AND bh.status IN ('ACTIVE', 'PAID')
                  AND bh.benefit_date >= CURRENT_DATE - INTERVAL '180 days'
            """, (family_id,))
            
            applications_count = cursor.fetchone()[0] or 0
            
            cursor.close()
            
            if total_recommendations > 0:
                return min(1.0, applications_count / total_recommendations)
            return 0.5  # Default if no history
        
        except Exception as e:
            print(f"⚠️  Error getting family application rate: {e}")
            return 0.5
    
    def _get_scheme_popularity(self, scheme_code: str) -> float:
        """Get scheme popularity (historical acceptance rate across all users)"""
        try:
            conn = self.external_dbs.get('eligibility_checker')
            if not conn:
                return 0.5  # Default
            
            cursor = conn.connection.cursor()
            
            # Count total recommendations for this scheme
            cursor.execute("""
                SELECT COUNT(*)
                FROM eligibility_checker.scheme_eligibility_results
                WHERE scheme_code = %s
                  AND eligibility_status IN ('ELIGIBLE', 'POSSIBLE_ELIGIBLE')
                  AND recommendation_rank IS NOT NULL
                  AND recommendation_rank <= 5
            """, (scheme_code,))
            
            total_recommendations = cursor.fetchone()[0] or 0
            
            # Count how many have this scheme in benefit history (proxy for acceptance)
            cursor.execute("""
                SELECT COUNT(DISTINCT beneficiary_id)
                FROM profile_360.benefit_history
                WHERE scheme_code = %s
                  AND status IN ('ACTIVE', 'PAID')
            """, (scheme_code,))
            
            enrolled_count = cursor.fetchone()[0] or 0
            
            cursor.close()
            
            # Normalize (assume ~30% of recommendations lead to enrollment)
            if total_recommendations > 10:
                popularity = min(1.0, enrolled_count / (total_recommendations * 0.3))
                return popularity
            return 0.5  # Default
        
        except Exception as e:
            print(f"⚠️  Error getting scheme popularity: {e}")
            return 0.5
    
    def _get_user_engagement_score(self, family_id: str) -> float:
        """Get user engagement score based on interaction history"""
        try:
            conn = self.external_dbs.get('eligibility_checker')
            if not conn:
                return 0.5  # Default
            
            cursor = conn.connection.cursor()
            
            # Count eligibility checks (engagement indicator)
            cursor.execute("""
                SELECT COUNT(*)
                FROM eligibility_checker.eligibility_checks
                WHERE family_id = %s::uuid
                  AND check_timestamp >= CURRENT_TIMESTAMP - INTERVAL '90 days'
            """, (family_id,))
            
            check_count = cursor.fetchone()[0] or 0
            
            cursor.close()
            
            # More checks = higher engagement
            engagement = min(1.0, check_count / 5.0)  # 5+ checks = full engagement
            return engagement
        
        except Exception as e:
            print(f"⚠️  Error getting user engagement: {e}")
            return 0.5
    
    def _get_scheme_type_match(self, family_id: str, scheme_code: str) -> float:
        """Get how well scheme type matches family profile"""
        # Simplified: Check if family has similar schemes enrolled
        try:
            conn = self.external_dbs.get('profile_360')
            if not conn:
                return 0.7  # Default
            
            cursor = conn.connection.cursor()
            
            # Get scheme category/type (simplified - assumes pension, education, health, etc.)
            scheme_type = self._categorize_scheme(scheme_code)
            
            # Check if family has schemes in same category
            cursor.execute("""
                SELECT COUNT(DISTINCT scheme_code)
                FROM profile_360.benefit_history bh
                JOIN golden_records.beneficiaries grb ON bh.beneficiary_id = grb.beneficiary_id
                WHERE grb.family_id = %s::uuid
                  AND bh.status IN ('ACTIVE', 'PAID')
            """, (family_id,))
            
            enrolled_count = cursor.fetchone()[0] or 0
            
            cursor.close()
            
            # If they have enrolled schemes, more likely to accept new ones
            return min(1.0, 0.5 + (enrolled_count * 0.1))
        
        except Exception as e:
            print(f"⚠️  Error getting scheme type match: {e}")
            return 0.7
    
    def _categorize_scheme(self, scheme_code: str) -> str:
        """Categorize scheme by type"""
        scheme_upper = scheme_code.upper()
        if 'PENSION' in scheme_upper:
            return 'PENSION'
        elif 'EDUCATION' in scheme_upper or 'SCHOLARSHIP' in scheme_upper:
            return 'EDUCATION'
        elif 'HEALTH' in scheme_upper:
            return 'HEALTH'
        elif 'CROP' in scheme_upper or 'AGRICULTURE' in scheme_upper:
            return 'AGRICULTURE'
        else:
            return 'OTHER'
    
    def _heuristic_probability(self, features: Dict[str, Any]) -> float:
        """Calculate probability using heuristic weights"""
        probability = (
            features.get('historical_application_rate', 0.5) * self.feature_weights['historical_rate'] +
            features.get('scheme_popularity', 0.5) * self.feature_weights['scheme_popularity'] +
            features.get('eligibility_score', 0.7) * self.feature_weights['eligibility_score'] +
            features.get('user_engagement', 0.5) * self.feature_weights['user_engagement'] +
            features.get('rank_score', 0.8) * 0.1 +
            features.get('time_decay', 0.8) * 0.1 +
            features.get('scheme_type_match', 0.7) * 0.1
        )
        
        # Ensure probability is in valid range
        return max(0.1, min(1.0, probability))
    
    def _features_to_vector(self, features: Dict[str, Any]) -> List[float]:
        """Convert features dict to numerical vector for ML model"""
        # This would be used when ML model is trained
        # For now, return heuristic-based vector
        return [
            features.get('historical_application_rate', 0.5),
            features.get('scheme_popularity', 0.5),
            features.get('eligibility_score', 0.7),
            features.get('user_engagement', 0.5),
            features.get('rank_score', 0.8),
            features.get('time_decay', 0.8),
            features.get('scheme_type_match', 0.7),
            features.get('recommendation_rank', 5) / 10.0,
            features.get('days_since_recommendation', 0) / 90.0
        ]
    
    def train_model(self, training_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Train ML model for probability estimation
        
        Args:
            training_data: DataFrame with historical recommendation data
        
        Returns:
            Training results and metrics
        """
        if not SKLEARN_AVAILABLE:
            return {
                'success': False,
                'message': 'scikit-learn not available. Install it to enable ML training.'
            }
        
        if training_data is None:
            # Load training data from database
            training_data = self._load_training_data()
        
        if training_data is None or training_data.empty:
            return {
                'success': False,
                'message': 'No training data available. Need historical recommendation data.'
            }
        
        try:
            # Prepare features and labels
            feature_columns = [
                'historical_application_rate', 'scheme_popularity', 'eligibility_score',
                'user_engagement', 'rank_score', 'time_decay', 'scheme_type_match',
                'normalized_rank', 'normalized_days'
            ]
            
            X = training_data[feature_columns].fillna(0.5)
            y = training_data['converted'].fillna(0)  # 1 if recommendation led to application, 0 otherwise
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Train model
            self.probability_model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
            
            self.probability_model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.probability_model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, zero_division=0)
            recall = recall_score(y_test, y_pred, zero_division=0)
            
            self.is_model_trained = True
            
            return {
                'success': True,
                'accuracy': float(accuracy),
                'precision': float(precision),
                'recall': float(recall),
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Training failed: {str(e)}'
            }
    
    def _load_training_data(self) -> Optional[pd.DataFrame]:
        """Load historical recommendation data for training"""
        # This would load historical data showing:
        # - Recommendations made
        # - Whether they led to applications/enrollments
        # - Features at time of recommendation
        
        # Placeholder - would need actual historical tracking table
        # For now, return None to indicate no training data
        return None
    
    def track_recommendation_effectiveness(
        self,
        family_id: str,
        scheme_code: str,
        recommendation_id: Optional[int] = None,
        converted: bool = False,
        conversion_date: Optional[datetime] = None
    ):
        """
        Track recommendation effectiveness for learning
        
        Args:
            family_id: Family ID
            scheme_code: Recommended scheme
            recommendation_id: Recommendation record ID
            converted: Whether recommendation led to application
            conversion_date: When conversion happened
        """
        try:
            conn = self.db.connection
            cursor = conn.cursor()
            
            # Insert or update effectiveness tracking
            # This would require a recommendation_effectiveness table
            # For now, log to audit or a future tracking table
            
            cursor.execute("""
                INSERT INTO forecast.forecast_audit_logs (
                    event_type, event_timestamp, actor_type, actor_id,
                    family_id, event_description, event_data
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                'RECOMMENDATION_EFFECTIVENESS',
                conversion_date or datetime.now(),
                'SYSTEM',
                None,
                family_id,
                f'Recommendation effectiveness: {scheme_code} - {"CONVERTED" if converted else "NOT_CONVERTED"}',
                f'{{"scheme_code": "{scheme_code}", "converted": {str(converted).lower()}, "recommendation_id": {recommendation_id}}}'
            ))
            
            conn.commit()
            cursor.close()
        
        except Exception as e:
            print(f"⚠️  Error tracking recommendation effectiveness: {e}")

