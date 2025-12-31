"""
ML Anomaly Detector
Detects anomalies in beneficiary benefit patterns using ML models
Use Case ID: AI-PLATFORM-07
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import sys
from pathlib import Path
import json
import yaml
import numpy as np
import pandas as pd

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector

# ML Libraries (optional imports - fail gracefully if not available)
try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    import joblib
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("Warning: scikit-learn not available. ML anomaly detection will use rule-based fallback.")


class AnomalyDetector:
    """ML-based anomaly detection for benefit patterns"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Anomaly Detector"""
        if config_path is None:
            base_dir = Path(__file__).parent.parent.parent
            config_path = base_dir / "config" / "db_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize database connections
        db_config = self.config['database']
        self.db = DBConnector(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['name'],
            user=db_config['user'],
            password=db_config['password']
        )
        
        # External database connections
        self.external_dbs = {}
        for name, ext_config in self.config.get('external_databases', {}).items():
            self.external_dbs[name] = DBConnector(
                host=ext_config['host'],
                port=ext_config['port'],
                database=ext_config['name'],
                user=ext_config['user'],
                password=ext_config['password']
            )
        
        # Load use case config
        use_case_config_path = Path(config_path).parent / "use_case_config.yaml"
        if use_case_config_path.exists():
            with open(use_case_config_path, 'r') as f:
                self.use_case_config = yaml.safe_load(f)
        else:
            self.use_case_config = {}
        
        # ML model configuration
        ml_config = self.use_case_config.get('ml_detection', {})
        self.anomaly_threshold = ml_config.get('anomaly_score_threshold', 0.7)
        self.risk_threshold = ml_config.get('risk_score_threshold', 0.6)
        
        # Models (will be loaded when needed)
        self.models = {}
        self.scaler = None
        
        # Feature configuration
        self.feature_config = ml_config.get('features', {})
    
    def connect(self):
        """Connect to all databases"""
        self.db.connect()
        for ext_db in self.external_dbs.values():
            ext_db.connect()
    
    def disconnect(self):
        """Disconnect from all databases"""
        self.db.disconnect()
        for ext_db in self.external_dbs.values():
            ext_db.disconnect()
    
    def detect_anomalies(
        self,
        beneficiary_id: str,
        family_id: str,
        scheme_code: str,
        current_benefit_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Detect anomalies in beneficiary benefit patterns
        
        Args:
            beneficiary_id: Beneficiary identifier
            family_id: Family ID
            scheme_code: Scheme code
            current_benefit_data: Current benefit information
        
        Returns:
            Anomaly detection results with scores and explanations
        """
        if not ML_AVAILABLE:
            return self._rule_based_anomaly_detection(beneficiary_id, family_id, scheme_code, current_benefit_data)
        
        # Extract features
        features = self._extract_features(beneficiary_id, family_id, scheme_code, current_benefit_data)
        
        if not features:
            return {
                'anomaly_score': 0.0,
                'risk_score': 0.0,
                'anomaly_type': None,
                'top_anomalous_features': [],
                'feature_contributions': {},
                'behavioral_flags': [],
                'pattern_explanations': {},
                'model_name': 'fallback',
                'model_version': '1.0',
                'model_type': 'rule_based',
                'prediction_confidence': 0.0
            }
        
        # Load or train model
        model_name = f"anomaly_model_{scheme_code or 'general'}"
        model = self._load_or_create_model(model_name, scheme_code)
        
        if model is None:
            # Fallback to rule-based if model not available
            return self._rule_based_anomaly_detection(beneficiary_id, family_id, scheme_code, current_benefit_data)
        
        # Prepare feature vector
        feature_vector = self._prepare_feature_vector(features)
        
        # Get anomaly score
        anomaly_score = model.decision_function([feature_vector])[0]
        # Normalize to 0-1 range (Isolation Forest returns negative scores for anomalies)
        normalized_score = 1 / (1 + np.exp(-anomaly_score))  # Sigmoid normalization
        
        # Predict anomaly (1 = normal, -1 = anomaly)
        prediction = model.predict([feature_vector])[0]
        is_anomaly = prediction == -1
        
        # Calculate risk score (combination of anomaly score and other factors)
        risk_score = self._calculate_risk_score(normalized_score, features)
        
        # Determine anomaly type
        anomaly_type = self._determine_anomaly_type(normalized_score, features)
        
        # Extract top contributing features
        top_features = self._get_top_contributing_features(features, normalized_score)
        
        # Check behavioral patterns
        behavioral_flags = self._check_behavioral_patterns(features)
        
        return {
            'anomaly_score': float(normalized_score),
            'risk_score': float(risk_score),
            'anomaly_type': anomaly_type,
            'top_anomalous_features': top_features,
            'feature_contributions': self._calculate_feature_contributions(features, normalized_score),
            'behavioral_flags': behavioral_flags,
            'pattern_explanations': self._explain_patterns(behavioral_flags, features),
            'cluster_metrics': self._get_cluster_metrics(beneficiary_id, family_id, scheme_code),
            'model_name': model_name,
            'model_version': '1.0',
            'model_type': 'isolation_forest',
            'model_input_features': features,
            'prediction_confidence': abs(anomaly_score),
            'is_anomaly': bool(is_anomaly)
        }
    
    def _extract_features(
        self,
        beneficiary_id: str,
        family_id: str,
        scheme_code: str,
        current_benefit_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Extract features for anomaly detection"""
        features = {}
        
        try:
            # Profile features
            if self.feature_config.get('benefit_amount_vs_income', True):
                features.update(self._get_benefit_income_features(beneficiary_id, family_id, scheme_code))
            
            # Benefit mix patterns
            if self.feature_config.get('benefit_mix_patterns', True):
                features.update(self._get_benefit_mix_features(beneficiary_id, family_id))
            
            # Household composition
            if self.feature_config.get('household_size_vs_benefits', True):
                features.update(self._get_household_features(family_id, scheme_code))
            
            # Behavioral patterns
            if self.feature_config.get('behavioral_patterns', True):
                features.update(self._get_behavioral_features(beneficiary_id, family_id, scheme_code))
            
            # Cluster metrics (if enabled)
            if self.feature_config.get('cluster_outlier_analysis', True):
                features.update(self._get_cluster_features(beneficiary_id, family_id, scheme_code))
        
        except Exception as e:
            print(f"Error extracting features: {str(e)}")
            return {}
        
        return features
    
    def _get_benefit_income_features(
        self,
        beneficiary_id: str,
        family_id: str,
        scheme_code: str
    ) -> Dict[str, Any]:
        """Get features related to benefit amount vs income"""
        profile_conn = self.external_dbs['profile_360'].connection
        cursor = profile_conn.cursor()
        
        features = {}
        
        try:
            # Get current benefit amount
            cursor.execute("""
                SELECT benefit_amount, benefit_frequency
                FROM profile_360.benefit_history
                WHERE beneficiary_id = %s AND scheme_code = %s AND status = 'ACTIVE'
                LIMIT 1
            """, (beneficiary_id, scheme_code))
            
            benefit_result = cursor.fetchone()
            if benefit_result:
                benefit_amount, frequency = benefit_result
                monthly_benefit = float(benefit_amount or 0) * (12 if frequency == 'YEARLY' else (1 if frequency == 'MONTHLY' else 0))
                features['monthly_benefit'] = monthly_benefit
            else:
                features['monthly_benefit'] = 0.0
            
            # Get income band
            cursor.execute("""
                SELECT income_band, total_monthly_income
                FROM profile_360.family_profiles
                WHERE family_id = %s
                LIMIT 1
            """, (family_id,))
            
            income_result = cursor.fetchone()
            if income_result:
                income_band, total_income = income_result
                features['income_band_encoded'] = self._encode_income_band(income_band)
                features['total_monthly_income'] = float(total_income or 0)
                
                # Benefit to income ratio
                if features['total_monthly_income'] > 0:
                    features['benefit_income_ratio'] = features['monthly_benefit'] / features['total_monthly_income']
                else:
                    features['benefit_income_ratio'] = 0.0
            else:
                features['income_band_encoded'] = 0
                features['total_monthly_income'] = 0.0
                features['benefit_income_ratio'] = 0.0
        
        except Exception as e:
            print(f"Error getting benefit-income features: {str(e)}")
        
        return features
    
    def _get_benefit_mix_features(
        self,
        beneficiary_id: str,
        family_id: str
    ) -> Dict[str, Any]:
        """Get features related to benefit mix patterns"""
        profile_conn = self.external_dbs['profile_360'].connection
        cursor = profile_conn.cursor()
        
        features = {}
        
        try:
            # Total active schemes
            cursor.execute("""
                SELECT COUNT(DISTINCT scheme_code), SUM(benefit_amount)
                FROM profile_360.benefit_history
                WHERE beneficiary_id = %s AND status = 'ACTIVE'
            """, (beneficiary_id,))
            
            result = cursor.fetchone()
            if result:
                features['total_active_schemes'] = result[0] or 0
                features['total_benefit_amount'] = float(result[1] or 0)
            else:
                features['total_active_schemes'] = 0
                features['total_benefit_amount'] = 0.0
            
            # Family total benefits
            cursor.execute("""
                SELECT COUNT(DISTINCT scheme_code), SUM(benefit_amount)
                FROM profile_360.benefit_history
                WHERE family_id = %s AND status = 'ACTIVE'
            """, (family_id,))
            
            result = cursor.fetchone()
            if result:
                features['family_active_schemes'] = result[0] or 0
                features['family_total_benefits'] = float(result[1] or 0)
            else:
                features['family_active_schemes'] = 0
                features['family_total_benefits'] = 0.0
        
        except Exception as e:
            print(f"Error getting benefit mix features: {str(e)}")
        
        return features
    
    def _get_household_features(
        self,
        family_id: str,
        scheme_code: str
    ) -> Dict[str, Any]:
        """Get household composition features"""
        gr_conn = self.external_dbs['golden_records'].connection
        cursor = gr_conn.cursor()
        
        features = {}
        
        try:
            # Family size
            cursor.execute("""
                SELECT COUNT(*), AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, date_of_birth)))
                FROM golden_records.family_members
                WHERE family_id = %s
            """, (family_id,))
            
            result = cursor.fetchone()
            if result:
                features['family_size'] = result[0] or 0
                features['avg_family_age'] = float(result[1] or 0)
            else:
                features['family_size'] = 0
                features['avg_family_age'] = 0.0
            
            # Benefits per family member
            profile_conn = self.external_dbs['profile_360'].connection
            profile_cursor = profile_conn.cursor()
            
            profile_cursor.execute("""
                SELECT COUNT(DISTINCT beneficiary_id)
                FROM profile_360.benefit_history
                WHERE family_id = %s AND scheme_code = %s AND status = 'ACTIVE'
            """, (family_id, scheme_code))
            
            beneficiaries_count = profile_cursor.fetchone()[0] or 0
            profile_cursor.close()
            
            if features['family_size'] > 0:
                features['beneficiaries_per_family_member'] = beneficiaries_count / features['family_size']
            else:
                features['beneficiaries_per_family_member'] = 0.0
        
        except Exception as e:
            print(f"Error getting household features: {str(e)}")
        
        return features
    
    def _get_behavioral_features(
        self,
        beneficiary_id: str,
        family_id: str,
        scheme_code: str
    ) -> Dict[str, Any]:
        """Get behavioral pattern features"""
        features = {}
        
        try:
            # Scheme switching frequency (would need historical data)
            features['scheme_switching_count'] = 0  # Placeholder
            
            # Application rejection history (if available)
            features['past_rejections'] = 0  # Placeholder
        
        except Exception as e:
            print(f"Error getting behavioral features: {str(e)}")
        
        return features
    
    def _get_cluster_features(
        self,
        beneficiary_id: str,
        family_id: str,
        scheme_code: str
    ) -> Dict[str, Any]:
        """Get cluster/peer comparison features"""
        features = {}
        
        try:
            # This would compare with local peer group
            # For now, return empty dict - would need cluster analysis
            features['peer_group_avg_benefit'] = 0.0
            features['peer_group_benefit_std'] = 0.0
            features['deviation_from_peer'] = 0.0
        
        except Exception as e:
            print(f"Error getting cluster features: {str(e)}")
        
        return features
    
    def _encode_income_band(self, income_band: Optional[str]) -> int:
        """Encode income band to numeric"""
        encoding = {
            'BELOW_POVERTY_LINE': 1,
            'VERY_LOW_INCOME': 2,
            'LOW_INCOME': 3,
            'MIDDLE_INCOME': 4,
            'ABOVE_POVERTY_LINE': 5,
            'HIGH_INCOME': 6
        }
        return encoding.get(income_band, 0)
    
    def _prepare_feature_vector(self, features: Dict[str, Any]) -> List[float]:
        """Prepare feature vector for model input"""
        # Standard feature order
        feature_order = [
            'monthly_benefit',
            'income_band_encoded',
            'total_monthly_income',
            'benefit_income_ratio',
            'total_active_schemes',
            'total_benefit_amount',
            'family_active_schemes',
            'family_total_benefits',
            'family_size',
            'avg_family_age',
            'beneficiaries_per_family_member'
        ]
        
        vector = []
        for feature_name in feature_order:
            vector.append(float(features.get(feature_name, 0.0)))
        
        return vector
    
    def _load_or_create_model(self, model_name: str, scheme_code: Optional[str] = None):
        """Load existing model or create a new one"""
        if model_name in self.models:
            return self.models[model_name]
        
        # Try to load from database or file
        model_path = Path(__file__).parent.parent.parent / "models" / "trained" / f"{model_name}.pkl"
        
        if model_path.exists() and ML_AVAILABLE:
            try:
                model = joblib.load(model_path)
                self.models[model_name] = model
                return model
            except Exception as e:
                print(f"Error loading model: {str(e)}")
        
        # Create new model (would typically be trained on historical data)
        # For now, create a simple Isolation Forest
        if ML_AVAILABLE:
            model = IsolationForest(
                contamination=0.1,  # 10% expected anomalies
                random_state=42,
                n_estimators=100
            )
            # Note: Model should be trained on historical data before use
            self.models[model_name] = model
            return model
        
        return None
    
    def _calculate_risk_score(self, anomaly_score: float, features: Dict[str, Any]) -> float:
        """Calculate combined risk score"""
        # Combine anomaly score with other risk factors
        base_risk = anomaly_score
        
        # Adjust based on benefit amount (higher benefits = higher risk if anomalous)
        benefit_risk = min(1.0, features.get('monthly_benefit', 0) / 10000) * 0.2
        
        # Adjust based on number of schemes (more schemes = higher risk)
        scheme_risk = min(1.0, features.get('total_active_schemes', 0) / 5) * 0.1
        
        risk_score = min(1.0, base_risk + benefit_risk + scheme_risk)
        return risk_score
    
    def _determine_anomaly_type(self, anomaly_score: float, features: Dict[str, Any]) -> Optional[str]:
        """Determine type of anomaly"""
        if anomaly_score < 0.6:
            return None
        
        # Check for specific patterns
        if features.get('benefit_income_ratio', 0) > 0.5:
            return 'POSSIBLE_OVER_BENEFITTED'
        
        if features.get('total_active_schemes', 0) > 3:
            return 'POSSIBLE_DUPLICATE'
        
        if features.get('benefit_income_ratio', 0) < 0 and features.get('income_band_encoded', 0) >= 4:
            return 'POSSIBLE_INCOME_ABOVE_LIMIT'
        
        return 'ANOMALOUS_PATTERN'
    
    def _get_top_contributing_features(self, features: Dict[str, Any], anomaly_score: float) -> List[str]:
        """Get top contributing features to anomaly"""
        # Simple heuristic - features with highest absolute values contribute most
        feature_importance = []
        for name, value in features.items():
            if isinstance(value, (int, float)):
                feature_importance.append((name, abs(value)))
        
        feature_importance.sort(key=lambda x: x[1], reverse=True)
        return [name for name, _ in feature_importance[:5]]
    
    def _calculate_feature_contributions(self, features: Dict[str, Any], anomaly_score: float) -> Dict[str, float]:
        """Calculate contribution of each feature to anomaly score"""
        contributions = {}
        total_abs = sum(abs(v) for v in features.values() if isinstance(v, (int, float)))
        
        if total_abs > 0:
            for name, value in features.items():
                if isinstance(value, (int, float)):
                    contributions[name] = abs(value) / total_abs
        
        return contributions
    
    def _check_behavioral_patterns(self, features: Dict[str, Any]) -> List[str]:
        """Check for behavioral pattern flags"""
        flags = []
        
        if features.get('scheme_switching_count', 0) > 2:
            flags.append('FREQUENT_SWITCHING')
        
        if features.get('total_active_schemes', 0) > 3:
            flags.append('MULTIPLE_SCHEMES')
        
        if features.get('benefit_income_ratio', 0) > 0.8:
            flags.append('HIGH_BENEFIT_INCOME_RATIO')
        
        return flags
    
    def _explain_patterns(self, behavioral_flags: List[str], features: Dict[str, Any]) -> Dict[str, str]:
        """Generate explanations for behavioral patterns"""
        explanations = {}
        
        for flag in behavioral_flags:
            if flag == 'FREQUENT_SWITCHING':
                explanations[flag] = 'Beneficiary has switched schemes multiple times, indicating potential gaming behavior'
            elif flag == 'MULTIPLE_SCHEMES':
                explanations[flag] = f'Beneficiary is enrolled in {features.get("total_active_schemes", 0)} active schemes simultaneously'
            elif flag == 'HIGH_BENEFIT_INCOME_RATIO':
                explanations[flag] = f'Benefits represent {features.get("benefit_income_ratio", 0)*100:.1f}% of reported income'
        
        return explanations
    
    def _get_cluster_metrics(self, beneficiary_id: str, family_id: str, scheme_code: str) -> Dict[str, Any]:
        """Get cluster/peer comparison metrics"""
        # Placeholder - would need actual cluster analysis
        return {
            'peer_group_size': 0,
            'peer_avg_benefit': 0.0,
            'deviation_score': 0.0
        }
    
    def _rule_based_anomaly_detection(
        self,
        beneficiary_id: str,
        family_id: str,
        scheme_code: str,
        current_benefit_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Fallback rule-based anomaly detection when ML not available"""
        # Extract features
        features = self._extract_features(beneficiary_id, family_id, scheme_code, current_benefit_data)
        
        # Simple rule-based scoring
        anomaly_score = 0.0
        
        # Factor 1: High benefit to income ratio
        benefit_income_ratio = features.get('benefit_income_ratio', 0)
        if benefit_income_ratio > 0.5:
            anomaly_score += 0.3
        
        # Factor 2: Multiple active schemes
        total_schemes = features.get('total_active_schemes', 0)
        if total_schemes > 3:
            anomaly_score += 0.2
        
        # Factor 3: High total benefits
        total_benefits = features.get('total_benefit_amount', 0)
        if total_benefits > 50000:
            anomaly_score += 0.2
        
        anomaly_score = min(1.0, anomaly_score)
        risk_score = self._calculate_risk_score(anomaly_score, features)
        
        return {
            'anomaly_score': float(anomaly_score),
            'risk_score': float(risk_score),
            'anomaly_type': self._determine_anomaly_type(anomaly_score, features),
            'top_anomalous_features': self._get_top_contributing_features(features, anomaly_score),
            'feature_contributions': self._calculate_feature_contributions(features, anomaly_score),
            'behavioral_flags': self._check_behavioral_patterns(features),
            'pattern_explanations': self._explain_patterns(self._check_behavioral_patterns(features), features),
            'model_name': 'rule_based_fallback',
            'model_version': '1.0',
            'model_type': 'rule_based',
            'model_input_features': features,
            'prediction_confidence': 0.5,
            'is_anomaly': anomaly_score > 0.6
        }
    
    def save_ml_detection(
        self,
        case_id: int,
        detection_result: Dict[str, Any]
    ):
        """Save ML detection results to database"""
        conn = self.db.connection
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO detection.ml_detections (
                    case_id, model_name, model_version, model_type,
                    anomaly_score, risk_score, anomaly_type,
                    top_anomalous_features, feature_contributions,
                    behavioral_flags, pattern_explanations, cluster_metrics,
                    model_input_features, model_output_raw, prediction_confidence
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                case_id,
                detection_result['model_name'],
                detection_result['model_version'],
                detection_result['model_type'],
                detection_result['anomaly_score'],
                detection_result['risk_score'],
                detection_result['anomaly_type'],
                json.dumps(detection_result['top_anomalous_features']),
                json.dumps(detection_result['feature_contributions']),
                detection_result['behavioral_flags'],
                json.dumps(detection_result['pattern_explanations']),
                json.dumps(detection_result.get('cluster_metrics', {})),
                json.dumps(detection_result['model_input_features']),
                json.dumps(detection_result),
                detection_result.get('prediction_confidence', 0.0)
            ))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise Exception(f"Failed to save ML detection: {str(e)}")
        finally:
            cursor.close()

