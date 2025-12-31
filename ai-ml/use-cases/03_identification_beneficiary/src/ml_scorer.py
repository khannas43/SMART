"""
ML Eligibility Scorer
XGBoost-based ML model for eligibility probability scoring
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import yaml
import joblib
import warnings
warnings.filterwarnings('ignore')

import xgboost as xgb
from sklearn.preprocessing import LabelEncoder, StandardScaler
import shap
import mlflow

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class MLEligibilityScorer:
    """
    ML-based eligibility scorer using XGBoost
    
    Provides probability scores and confidence for eligibility,
    along with SHAP-based explainability.
    """
    
    def __init__(self, config_path=None):
        """
        Initialize ML scorer
        
        Args:
            config_path: Path to configuration file
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "model_config.yaml"
        
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
        
        # Model cache
        self._models = {}
        self._feature_lists = {}
        self._explainers = {}  # SHAP explainers
        
        # MLflow setup
        mlflow_config = self.config['mlflow']
        mlflow.set_tracking_uri(mlflow_config['tracking_uri'])
        mlflow.set_experiment(mlflow_config['experiment_name'])
    
    def load_model(self, scheme_id: str, model_version: Optional[str] = None) -> bool:
        """
        Load ML model for a scheme
        
        Args:
            scheme_id: Scheme ID
            model_version: Specific model version (None for latest active)
        
        Returns:
            True if model loaded successfully
        """
        try:
            # Query model registry
            if model_version:
                query = """
                    SELECT model_path, mlflow_run_id, feature_list, model_type
                    FROM eligibility.ml_model_registry
                    WHERE scheme_code = %s AND model_version = %s
                        AND is_active = true
                """
                params = (scheme_id, model_version)
            else:
                query = """
                    SELECT model_path, mlflow_run_id, feature_list, model_type
                    FROM eligibility.ml_model_registry
                    WHERE scheme_code = %s AND is_active = true
                    ORDER BY deployed_at DESC NULLS LAST, created_at DESC
                    LIMIT 1
                """
                params = (scheme_id,)
            
            df = pd.read_sql(query, self.db.connection, params=params)
            
            if df.empty:
                print(f"⚠️  No active model found for scheme {scheme_id}")
                return False
            
            model_info = df.iloc[0]
            model_path = model_info['model_path']
            
            # Load model - try multiple flavors for compatibility
            model = None
            if model_path.startswith('models:/'):
                # Load from MLflow Model Registry
                model_name = model_path.split('/')[1]
                # Try different loading methods (handle version compatibility)
                try:
                    # Method 1: Try xgboost.load_model first
                    model = mlflow.xgboost.load_model(model_path)
                except (Exception, TypeError, AttributeError) as e1:
                    try:
                        # Method 2: Try sklearn.load_model (XGBClassifier is sklearn-compatible)
                        model = mlflow.sklearn.load_model(model_path)
                    except Exception as e2:
                        # Method 3: Try pyfunc.load_model (generic loader)
                        try:
                            model = mlflow.pyfunc.load_model(model_path)
                        except Exception as e3:
                            print(f"⚠️  Failed to load model using xgboost, sklearn, and pyfunc methods")
                            print(f"   xgboost error: {e1}")
                            print(f"   sklearn error: {e2}")
                            print(f"   pyfunc error: {e3}")
                            return False
            else:
                # Load from local file
                full_path = Path(__file__).parent.parent / model_path
                if not full_path.exists():
                    print(f"⚠️  Model file not found: {full_path}")
                    return False
                model = joblib.load(full_path)
            
            # Store model and metadata
            self._models[scheme_id] = model
            self._feature_lists[scheme_id] = model_info['feature_list'] or []
            
            # Initialize SHAP explainer (tree explainer for XGBoost)
            # Check explainability config (can be at root or under eligibility_scoring)
            explainability_config = self.config.get('explainability') or self.config.get('eligibility_scoring', {}).get('explainability', {})
            if explainability_config.get('method') == 'shap':
                try:
                    # Use TreeExplainer for XGBoost models
                    self._explainers[scheme_id] = shap.TreeExplainer(model)
                    print(f"✅ Loaded model and SHAP explainer for scheme {scheme_id}")
                except Exception as e:
                    print(f"⚠️  Could not initialize SHAP explainer: {e}")
                    self._explainers[scheme_id] = None
            
            return True
        
        except Exception as e:
            print(f"❌ Error loading model for scheme {scheme_id}: {e}")
            return False
    
    def prepare_features(
        self,
        scheme_id: str,
        family_data: Dict,
        member_data: Optional[Dict] = None
    ) -> pd.DataFrame:
        """
        Prepare features for ML model prediction
        
        Args:
            scheme_id: Scheme ID
            family_data: Family-level data (Golden Record + 360° Profile)
            member_data: Member-level data (if applicable)
        
        Returns:
            DataFrame with features ready for model
        """
        # Get feature list for scheme
        feature_list = self._feature_lists.get(scheme_id, [])
        if not feature_list:
            # Fallback to default features from config
            feature_config = self.config['eligibility_scoring']['feature_engineering']
            feature_list = []
            for category, features in feature_config.items():
                if isinstance(features, list):
                    feature_list.extend(features)
        
        # Combine family and member data
        data = {**family_data}
        if member_data:
            data.update({f"member_{k}": v for k, v in member_data.items()})
        
        # Prepare feature vector
        feature_dict = {}
        for feature in feature_list:
            # Handle nested features (e.g., "demographics.age")
            if '.' in feature:
                category, feat_name = feature.split('.', 1)
                feature_dict[feature] = data.get(feat_name) or data.get(feature)
            else:
                feature_dict[feature] = data.get(feature)
        
        # Convert to DataFrame
        df = pd.DataFrame([feature_dict])
        
        # Handle missing values
        df = df.fillna(0)
        
        # Ensure all expected features are present
        for feature in feature_list:
            if feature not in df.columns:
                df[feature] = 0
        
        # Select only features used by model
        if feature_list:
            df = df[[f for f in feature_list if f in df.columns]]
        
        return df
    
    def predict(
        self,
        scheme_id: str,
        family_data: Dict,
        member_data: Optional[Dict] = None,
        return_explanations: bool = True
    ) -> Dict[str, Any]:
        """
        Predict eligibility probability for a scheme
        
        Args:
            scheme_id: Scheme ID
            family_data: Family-level data
            member_data: Member-level data (optional)
            return_explanations: Whether to return SHAP explanations
        
        Returns:
            Dictionary with prediction results:
            {
                'probability': float,  # 0-1
                'confidence': float,   # 0-1
                'model_version': str,
                'top_features': List[Dict],  # Top contributing features
                'shap_values': Optional[List[float]]
            }
        """
        # Load model if not cached
        if scheme_id not in self._models:
            if not self.load_model(scheme_id):
                return {
                    'probability': None,
                    'confidence': 0.0,
                    'model_version': None,
                    'top_features': [],
                    'error': 'Model not available'
                }
        
        model = self._models[scheme_id]
        feature_list = self._feature_lists[scheme_id]
        
        # Prepare features
        X = self.prepare_features(scheme_id, family_data, member_data)
        
        # Predict probability
        try:
            if hasattr(model, 'predict_proba'):
                probabilities = model.predict_proba(X)[0]
                # For binary classification, take positive class probability
                if len(probabilities) == 2:
                    probability = probabilities[1]
                else:
                    probability = probabilities[0]
            else:
                # Regression model - normalize to 0-1 if needed
                prediction = model.predict(X)[0]
                probability = max(0, min(1, prediction / 100.0))  # Assuming 0-100 scale
            
            # Calculate confidence based on probability
            # Higher confidence near 0 or 1, lower near 0.5
            confidence = 1.0 - abs(probability - 0.5) * 2.0
            
            result = {
                'probability': float(probability),
                'confidence': float(confidence),
                'model_version': 'latest',  # TODO: Get from registry
                'top_features': []
            }
            
            # Generate SHAP explanations if requested
            if return_explanations and scheme_id in self._explainers and self._explainers[scheme_id]:
                try:
                    explainer = self._explainers[scheme_id]
                    shap_values = explainer.shap_values(X)
                    
                    # Extract feature importance
                    if isinstance(shap_values, list):
                        shap_values = shap_values[1] if len(shap_values) > 1 else shap_values[0]
                    
                    # Get top features
                    feature_importance = pd.DataFrame({
                        'feature': X.columns,
                        'shap_value': shap_values[0] if len(shap_values.shape) > 1 else shap_values
                    })
                    feature_importance['abs_shap'] = feature_importance['shap_value'].abs()
                    feature_importance = feature_importance.sort_values('abs_shap', ascending=False)
                    
                    # Get top_features_count from config (can be at root or under eligibility_scoring)
                    explainability_config = self.config.get('explainability') or self.config.get('eligibility_scoring', {}).get('explainability', {})
                    top_n = explainability_config.get('top_features_count', 10)
                    top_features = feature_importance.head(top_n).to_dict('records')
                    
                    result['top_features'] = [
                        {
                            'feature': row['feature'],
                            'shap_value': float(row['shap_value']),
                            'importance': float(row['abs_shap'])
                        }
                        for row in top_features
                    ]
                    result['shap_values'] = shap_values.tolist() if hasattr(shap_values, 'tolist') else shap_values
                
                except Exception as e:
                    print(f"⚠️  Error generating SHAP explanations: {e}")
            
            return result
        
        except Exception as e:
            print(f"❌ Error during prediction: {e}")
            return {
                'probability': None,
                'confidence': 0.0,
                'model_version': None,
                'top_features': [],
                'error': str(e)
            }
    
    def get_model_info(self, scheme_id: str) -> Optional[Dict]:
        """
        Get information about the loaded model
        
        Args:
            scheme_id: Scheme ID
        
        Returns:
            Model information dictionary or None
        """
        if scheme_id not in self._models:
            return None
        
        query = """
            SELECT model_version, model_type, training_metrics, feature_list,
                   training_samples_count, deployed_at
            FROM eligibility.ml_model_registry
            WHERE scheme_code = %s AND is_active = true
            ORDER BY deployed_at DESC NULLS LAST, created_at DESC
            LIMIT 1
        """
        
        df = pd.read_sql(query, self.db.connection, params=(scheme_id,))
        if df.empty:
            return None
        
        return df.iloc[0].to_dict()
    
    def is_model_available(self, scheme_id: str) -> bool:
        """
        Check if ML model is available for a scheme
        
        Args:
            scheme_id: Scheme ID
        
        Returns:
            True if model is available
        """
        if scheme_id in self._models:
            return True
        
        # Try to load model
        return self.load_model(scheme_id)
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.disconnect()


def main():
    """Test ML scorer"""
    scorer = MLEligibilityScorer()
    
    # Sample family data
    family_data = {
        'family_id': 'test-123',
        'age': 65,
        'gender': 'M',
        'district_id': 101,
        'income_band': 'LOW',
        'family_size': 4,
        'head_age': 65,
        'head_gender': 'M',
        'caste_id': 1,
        'education_level': 'PRIMARY',
        'employment_status': 'UNEMPLOYED',
        'schemes_enrolled_count': 0,
        'benefits_received_total_1y': 0
    }
    
    # Test model availability (will fail if no model trained yet)
    scheme_id = 'SCHEME_001'
    if scorer.is_model_available(scheme_id):
        result = scorer.predict(scheme_id, family_data)
        print("Prediction Result:")
        print(result)
    else:
        print(f"Model not available for {scheme_id}")
        print("Train model first using train_eligibility_model.py")
    
    scorer.close()


if __name__ == "__main__":
    main()

