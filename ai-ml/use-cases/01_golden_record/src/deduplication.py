"""
Deduplication Models for Golden Record
Implements Fellegi-Sunter probabilistic record linkage and Siamese NN
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Dict
from pathlib import Path
import yaml
import pickle
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_curve, roc_auc_score
import mlflow
import mlflow.sklearn

# Neural network imports (optional, for Siamese NN)
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from features import GoldenRecordFeatureEngineer


class FellegiSunterDeduplication:
    """
    Fellegi-Sunter Probabilistic Record Linkage Model
    Implements the classic probabilistic record linkage algorithm
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize Fellegi-Sunter model
        
        Args:
            config_path: Path to model_config.yaml
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "model_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)['deduplication']
        
        self.thresholds = self.config['thresholds']
        self.feature_weights = {}
        
        # Initialize feature engineer
        feature_config_path = Path(__file__).parent.parent / "config" / "feature_config.yaml"
        self.feature_engineer = GoldenRecordFeatureEngineer(feature_config_path)
        
        # Model parameters (will be learned from data)
        self.m_probs = {}  # Probability of agreement given that records match
        self.u_probs = {}  # Probability of agreement given that records don't match
    
    def compute_agreement_vectors(self, pairs: pd.DataFrame) -> pd.DataFrame:
        """
        Compute agreement vectors for record pairs
        
        Args:
            pairs: DataFrame with columns [record1, record2, ...]
            
        Returns:
            DataFrame with agreement features
        """
        agreement_features = []
        
        for idx, row in pairs.iterrows():
            record1 = row['record1']
            record2 = row['record2']
            
            features = self.feature_engineer.compute_match_features(record1, record2)
            agreement_features.append(features)
        
        return pd.DataFrame(agreement_features)
    
    def estimate_parameters(self, match_pairs: pd.DataFrame, nonmatch_pairs: pd.DataFrame):
        """
        Estimate m and u probabilities from training data
        
        Args:
            match_pairs: DataFrame of known matching pairs
            nonmatch_pairs: DataFrame of known non-matching pairs
        """
        # Compute agreement vectors
        match_agreements = self.compute_agreement_vectors(match_pairs)
        nonmatch_agreements = self.compute_agreement_vectors(nonmatch_pairs)
        
        # Estimate m and u probabilities for each feature
        for feature in match_agreements.columns:
            if match_agreements[feature].dtype in [np.float64, np.float32, np.int64]:
                # m_prob: probability of agreement given match
                self.m_probs[feature] = match_agreements[feature].mean()
                
                # u_prob: probability of agreement given non-match
                self.u_probs[feature] = nonmatch_agreements[feature].mean()
    
    def compute_match_score(self, record1: pd.Series, record2: pd.Series) -> float:
        """
        Compute Fellegi-Sunter match score
        
        Args:
            record1: First record
            record2: Second record
            
        Returns:
            Match probability score (0-1)
        """
        # Compute agreement features
        features = self.feature_engineer.compute_match_features(record1, record2)
        
        # Compute log-likelihood ratio
        log_likelihood = 0.0
        
        for feature, agreement_value in features.items():
            if feature not in self.m_probs:
                continue
            
            m_prob = self.m_probs[feature]
            u_prob = self.u_probs[feature]
            
            # Avoid division by zero
            if u_prob == 0:
                u_prob = 0.0001
            if m_prob == 0:
                m_prob = 0.0001
            
            # Agreement value (binary or continuous)
            if isinstance(agreement_value, (bool, np.bool_)):
                agreement = 1.0 if agreement_value else 0.0
            else:
                agreement = float(agreement_value)
            
            # Weighted log-likelihood ratio
            if agreement > 0.5:  # Consider as agreement
                log_likelihood += np.log(m_prob / u_prob) if m_prob > 0 and u_prob > 0 else 0
            else:
                log_likelihood += np.log((1 - m_prob) / (1 - u_prob)) if (1 - m_prob) > 0 and (1 - u_prob) > 0 else 0
        
        # Convert to probability using sigmoid
        match_score = 1 / (1 + np.exp(-log_likelihood))
        
        return min(1.0, max(0.0, match_score))
    
    def predict(self, record1: pd.Series, record2: pd.Series) -> Tuple[float, str]:
        """
        Predict if two records match
        
        Args:
            record1: First record
            record2: Second record
            
        Returns:
            (match_score, decision) where decision is 'auto_merge', 'manual_review', or 'reject'
        """
        match_score = self.compute_match_score(record1, record2)
        
        # Apply thresholds
        if match_score >= self.thresholds['auto_merge']:
            decision = 'auto_merge'
        elif match_score >= self.thresholds['manual_review']:
            decision = 'manual_review'
        else:
            decision = 'reject'
        
        return match_score, decision
    
    def find_duplicates(self, records: pd.DataFrame) -> pd.DataFrame:
        """
        Find duplicate pairs in a dataset
        
        Args:
            records: DataFrame of records to deduplicate
            
        Returns:
            DataFrame with columns [record1_id, record2_id, match_score, decision]
        """
        duplicates = []
        
        # Compare all pairs (can be optimized with blocking)
        n_records = len(records)
        for i in range(n_records):
            for j in range(i + 1, n_records):
                record1 = records.iloc[i]
                record2 = records.iloc[j]
                
                match_score, decision = self.predict(record1, record2)
                
                if decision != 'reject':
                    duplicates.append({
                        'record1_id': record1.name if hasattr(record1, 'name') else i,
                        'record2_id': record2.name if hasattr(record2, 'name') else j,
                        'match_score': match_score,
                        'decision': decision
                    })
        
        return pd.DataFrame(duplicates)
    
    def save_model(self, filepath: str):
        """Save model to file"""
        model_data = {
            'm_probs': self.m_probs,
            'u_probs': self.u_probs,
            'thresholds': self.thresholds
        }
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, filepath: str):
        """Load model from file"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.m_probs = model_data['m_probs']
        self.u_probs = model_data['u_probs']
        self.thresholds = model_data['thresholds']


class SiameseNeuralNetwork:
    """
    Siamese Neural Network for record similarity learning
    Uses deep learning to learn similarity representations
    """
    
    def __init__(self, input_dim: int = 50, hidden_dims: List[int] = [128, 64, 32]):
        """
        Initialize Siamese NN
        
        Args:
            input_dim: Dimension of input features
            hidden_dims: List of hidden layer dimensions
        """
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch not available. Install with: pip install torch")
        
        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        
        # Build Siamese network
        self.encoder = self._build_encoder()
        self.distance_layer = nn.Linear(hidden_dims[-1], 1)
        
    def _build_encoder(self) -> nn.Module:
        """Build encoder network (shared weights)"""
        layers = []
        prev_dim = self.input_dim
        
        for hidden_dim in self.hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(0.2))
            prev_dim = hidden_dim
        
        return nn.Sequential(*layers)
    
    def forward(self, x1: torch.Tensor, x2: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through Siamese network
        
        Args:
            x1: First record features
            x2: Second record features
            
        Returns:
            Similarity score (0-1)
        """
        # Encode both records
        enc1 = self.encoder(x1)
        enc2 = self.encoder(x2)
        
        # Compute distance
        distance = torch.abs(enc1 - enc2)
        similarity = torch.sigmoid(self.distance_layer(distance))
        
        return similarity
    
    def predict(self, x1: np.ndarray, x2: np.ndarray) -> float:
        """
        Predict similarity between two records
        
        Args:
            x1: First record features
            x2: Second record features
            
        Returns:
            Similarity score (0-1)
        """
        self.encoder.eval()
        
        with torch.no_grad():
            x1_tensor = torch.FloatTensor(x1).unsqueeze(0)
            x2_tensor = torch.FloatTensor(x2).unsqueeze(0)
            
            similarity = self.forward(x1_tensor, x2_tensor)
            
        return similarity.item()


# Factory function for creating deduplication models
def create_deduplication_model(model_type: str = 'fellegi_sunter', **kwargs):
    """
    Factory function to create deduplication model
    
    Args:
        model_type: 'fellegi_sunter' or 'siamese_nn'
        **kwargs: Additional arguments for model initialization
        
    Returns:
        Deduplication model instance
    """
    if model_type == 'fellegi_sunter':
        return FellegiSunterDeduplication(**kwargs)
    elif model_type == 'siamese_nn':
        return SiameseNeuralNetwork(**kwargs)
    else:
        raise ValueError(f"Unknown model type: {model_type}")


if __name__ == "__main__":
    # Example usage
    print("Testing Fellegi-Sunter deduplication model...")
    
    model = FellegiSunterDeduplication()
    print("✅ Model initialized")
    
    # Note: Model parameters need to be estimated from training data
    # This would typically be done in a training script

