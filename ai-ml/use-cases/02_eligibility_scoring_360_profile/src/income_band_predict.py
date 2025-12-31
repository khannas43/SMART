"""
Predict Income Band for a Golden Record
Use Case: AI-PLATFORM-02
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import yaml
import joblib
import pickle
from uuid import UUID

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class IncomeBandPredictor:
    """Predict income band for a Golden Record"""
    
    def __init__(self, model_path=None, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "model_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Load model
        if model_path is None:
            model_path = Path(__file__).parent.parent / "models" / "checkpoints" / "income_band_model.pkl"
        
        self.model = joblib.load(model_path)
        
        # Load encoders
        encoders_path = Path(__file__).parent.parent / "models" / "checkpoints" / "encoders.pkl"
        with open(encoders_path, 'rb') as f:
            self.label_encoders = pickle.load(f)
        
        # Database connection
        db_config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
        with open(db_config_path, 'r') as f:
            db_config = yaml.safe_load(f)['database']
        
        self.db = DBConnector(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['dbname'],
            user=db_config['user'],
            password=db_config['password']
        )
        self.db.connect()
        
        # Confidence threshold
        self.confidence_threshold = self.config['income_band']['confidence_threshold']
        self.bands = self.config['income_band']['bands']
    
    def get_features_for_gr(self, gr_id):
        """Get features for a Golden Record"""
        query = """
        WITH benefit_totals AS (
            SELECT 
                gr.gr_id,
                COALESCE(SUM(CASE WHEN be.txn_date >= CURRENT_DATE - INTERVAL '1 year' THEN be.amount ELSE 0 END), 0) as benefit_total_1y,
                COALESCE(SUM(CASE WHEN be.txn_date >= CURRENT_DATE - INTERVAL '3 years' THEN be.amount ELSE 0 END), 0) as benefit_total_3y,
                COUNT(CASE WHEN be.txn_date >= CURRENT_DATE - INTERVAL '1 year' THEN 1 END) as benefit_count_1y,
                COUNT(CASE WHEN be.txn_date >= CURRENT_DATE - INTERVAL '3 years' THEN 1 END) as benefit_count_3y,
                COUNT(DISTINCT be.scheme_id) as schemes_enrolled_count
            FROM golden_records gr
            LEFT JOIN benefit_events be ON gr.gr_id = be.gr_id
            WHERE gr.gr_id = %s
            GROUP BY gr.gr_id
        ),
        socio_context AS (
            SELECT 
                gr.gr_id,
                sef.education_level,
                sef.employment_type,
                sef.house_type,
                sef.family_size,
                gr.is_urban,
                gr.district_id
            FROM golden_records gr
            LEFT JOIN socio_economic_facts sef ON gr.gr_id = sef.gr_id
            WHERE gr.gr_id = %s
        )
        SELECT 
            bt.gr_id,
            bt.benefit_total_1y,
            bt.benefit_total_3y,
            bt.benefit_count_1y,
            bt.benefit_count_3y,
            bt.schemes_enrolled_count,
            sc.education_level,
            sc.employment_type,
            sc.house_type,
            sc.family_size,
            sc.is_urban,
            sc.district_id
        FROM benefit_totals bt
        JOIN socio_context sc ON bt.gr_id = sc.gr_id
        """
        
        df = self.db.execute_query(query, params=(str(gr_id), str(gr_id)))
        return df.iloc[0] if len(df) > 0 else None
    
    def predict(self, gr_id):
        """Predict income band for a Golden Record"""
        # Get features
        features = self.get_features_for_gr(gr_id)
        if features is None:
            return None, None, "Record not found"
        
        # Prepare feature vector
        feature_vector = self._prepare_feature_vector(features)
        
        # Predict
        prediction = self.model.predict([feature_vector])[0]
        probabilities = self.model.predict_proba([feature_vector])[0]
        
        # Get band label
        income_band = self.label_encoders['target'].inverse_transform([prediction])[0]
        confidence = probabilities[prediction]
        
        # Check confidence threshold
        if confidence < self.confidence_threshold:
            income_band = 'UNCERTAIN'
        
        return income_band, confidence, None
    
    def _prepare_feature_vector(self, features):
        """Prepare feature vector from row"""
        feature_cols = [
            'benefit_total_1y', 'benefit_total_3y', 'benefit_count_1y', 
            'benefit_count_3y', 'schemes_enrolled_count', 'family_size', 'is_urban'
        ]
        
        # Encode categorical
        education_encoded = self.label_encoders['education'].transform([
            features['education_level'] if pd.notna(features['education_level']) else 'ILLITERATE'
        ])[0]
        
        employment_encoded = self.label_encoders['employment'].transform([
            features['employment_type'] if pd.notna(features['employment_type']) else 'UNEMPLOYED'
        ])[0]
        
        house_encoded = self.label_encoders['house'].transform([
            features['house_type'] if pd.notna(features['house_type']) else 'KUTCHA'
        ])[0]
        
        # Build feature vector
        vector = [
            features.get('benefit_total_1y', 0),
            features.get('benefit_total_3y', 0),
            features.get('benefit_count_1y', 0),
            features.get('benefit_count_3y', 0),
            features.get('schemes_enrolled_count', 0),
            features.get('family_size', 1),
            1 if features.get('is_urban', False) else 0,
            education_encoded,
            employment_encoded,
            house_encoded,
            features.get('district_id', 1)
        ]
        
        return vector
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.disconnect()


def main():
    """Test prediction"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python predict.py <gr_id>")
        sys.exit(1)
    
    gr_id = sys.argv[1]
    
    predictor = IncomeBandPredictor()
    
    try:
        income_band, confidence, error = predictor.predict(gr_id)
        
        if error:
            print(f"❌ Error: {error}")
        else:
            print(f"✅ Income Band: {income_band}")
            print(f"   Confidence: {confidence:.4f}")
    finally:
        predictor.close()


if __name__ == "__main__":
    main()


