"""
Conflict Reconciliation Module
Uses XGBoost ensemble to rank attribute versions by recency, source authority, completeness
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from pathlib import Path
import yaml
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
import mlflow
import mlflow.xgboost

from features import GoldenRecordFeatureEngineer


class ConflictReconciliationModel:
    """
    XGBoost-based conflict reconciliation model
    Ranks conflicting attribute versions by recency, source authority, and completeness
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize conflict reconciliation model
        
        Args:
            config_path: Path to model_config.yaml
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "model_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)['conflict_reconciliation']
        
        self.params = self.config['params']
        self.ranking_factors = self.config['ranking_factors']
        
        # Initialize XGBoost model
        self.model = xgb.XGBClassifier(**self.params)
        self.label_encoder = LabelEncoder()
        
        # Source authority weights
        self.source_weights = self.ranking_factors['source_authority']['weights']
    
    def compute_features(self, attribute_versions: List[Dict]) -> pd.DataFrame:
        """
        Compute features for conflict reconciliation
        
        Args:
            attribute_versions: List of dicts with keys:
                - value: attribute value
                - source: source name
                - timestamp: when the value was recorded
                - completeness: completeness score (0-1)
                
        Returns:
            DataFrame with features for each version
        """
        features = []
        
        for version in attribute_versions:
            # Recency feature (days ago)
            if 'timestamp' in version:
                days_ago = (pd.Timestamp.now() - pd.Timestamp(version['timestamp'])).days
                recency_score = max(0, 1 - (days_ago / 365))  # Normalize to 0-1
            else:
                days_ago = 365
                recency_score = 0.0
            
            # Source authority score
            source = version.get('source', 'unknown')
            source_authority = self.source_weights.get(source, self.source_weights.get('unknown', 1.0))
            source_score = source_authority / max(self.source_weights.values())  # Normalize to 0-1
            
            # Completeness score
            completeness = version.get('completeness', 0.5)
            
            # Combined score (weighted)
            combined_score = (
                self.ranking_factors['recency']['weight'] * recency_score +
                self.ranking_factors['source_authority']['weight'] * source_score +
                self.ranking_factors['completeness']['weight'] * completeness
            )
            
            features.append({
                'recency_days': days_ago,
                'recency_score': recency_score,
                'source_authority': source_authority,
                'source_score': source_score,
                'completeness': completeness,
                'combined_score': combined_score,
                'source': source
            })
        
        return pd.DataFrame(features)
    
    def rank_versions(self, attribute_versions: List[Dict]) -> List[Dict]:
        """
        Rank attribute versions by confidence
        
        Args:
            attribute_versions: List of conflicting attribute versions
            
        Returns:
            Ranked list (best version first)
        """
        if len(attribute_versions) == 0:
            return []
        
        if len(attribute_versions) == 1:
            return [attribute_versions[0]]
        
        # Compute features
        features_df = self.compute_features(attribute_versions)
        
        # Use rule-based ranking (can be enhanced with ML model)
        # Sort by combined score (descending)
        ranked_indices = features_df['combined_score'].argsort()[::-1]
        
        ranked_versions = []
        for idx in ranked_indices:
            version = attribute_versions[idx].copy()
            version['confidence_score'] = float(features_df.iloc[idx]['combined_score'])
            version['rank'] = len(ranked_versions) + 1
            ranked_versions.append(version)
        
        return ranked_versions
    
    def select_best_version(self, attribute_versions: List[Dict]) -> Dict:
        """
        Select the best version from conflicting versions
        
        Args:
            attribute_versions: List of conflicting attribute versions
            
        Returns:
            Best version with confidence score
        """
        ranked = self.rank_versions(attribute_versions)
        return ranked[0] if ranked else None
    
    def train(self, training_data: pd.DataFrame, target_column: str = 'is_correct'):
        """
        Train XGBoost model on labeled conflict resolution data
        
        Args:
            training_data: DataFrame with features and target
            target_column: Column name for target (1 = correct version, 0 = incorrect)
        """
        # Prepare features
        feature_cols = ['recency_score', 'source_score', 'completeness']
        X = training_data[feature_cols]
        y = training_data[target_column]
        
        # Train model
        self.model.fit(X, y)
        
        # Log to MLflow
        mlflow.xgboost.log_model(self.model, "conflict_reconciliation_model")
        
        return self.model
    
    def predict_confidence(self, attribute_version: Dict) -> float:
        """
        Predict confidence score for an attribute version using trained model
        
        Args:
            attribute_version: Single attribute version
            
        Returns:
            Confidence score (0-1)
        """
        features_df = self.compute_features([attribute_version])
        
        # Use ML model if trained
        if hasattr(self.model, 'predict_proba'):
            X = features_df[['recency_score', 'source_score', 'completeness']]
            confidence = self.model.predict_proba(X)[0][1]  # Probability of being correct
            return float(confidence)
        else:
            # Fallback to rule-based
            return float(features_df.iloc[0]['combined_score'])


if __name__ == "__main__":
    # Example usage
    model = ConflictReconciliationModel()
    
    # Example conflicting versions
    versions = [
        {
            'value': 'Jaipur',
            'source': 'aadhaar',
            'timestamp': '2024-01-01',
            'completeness': 0.9
        },
        {
            'value': 'Jaipur',
            'source': 'scheme_data',
            'timestamp': '2023-06-01',
            'completeness': 0.7
        },
        {
            'value': 'Jaipur City',
            'source': 'self_declared',
            'timestamp': '2024-03-01',
            'completeness': 0.8
        }
    ]
    
    ranked = model.rank_versions(versions)
    print("Ranked versions:")
    for v in ranked:
        print(f"  Rank {v['rank']}: {v['value']} (confidence: {v['confidence_score']:.3f}, source: {v['source']})")
    
    best = model.select_best_version(versions)
    print(f"\nBest version: {best['value']} (confidence: {best['confidence_score']:.3f})")

