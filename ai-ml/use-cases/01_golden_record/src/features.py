"""
Feature Engineering for Golden Record Deduplication
Implements fuzzy matching, phonetic encoding, geospatial distance
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, List
from pathlib import Path
import yaml

# Fuzzy string matching
try:
    from rapidfuzz import fuzz, distance
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    # Fallback to basic string matching
    import difflib

# Phonetic encoding
try:
    from phonetics import metaphone, soundex
    PHONETICS_AVAILABLE = True
except ImportError:
    PHONETICS_AVAILABLE = False
    # Simple soundex implementation fallback
    def soundex(name):
        """Simple soundex implementation"""
        if not name:
            return ''
        name = name.upper()
        first_letter = name[0]
        rest = name[1:]
        soundex_code = first_letter
        # Simplified soundex
        return soundex_code + '000'[:4-len(soundex_code)]
    
    def metaphone(name):
        """Simple metaphone fallback"""
        return name[:4].upper() if name else ''

# Geospatial
try:
    from geopy.distance import geodesic
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False
    # Fallback haversine calculation
    import math
    def geodesic(point1, point2):
        """Simple haversine distance calculation"""
        lat1, lon1 = point1
        lat2, lon2 = point2
        R = 6371  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance_km = R * c
        class Distance:
            def __init__(self, km):
                self.kilometers = km
        return Distance(distance_km)


class GoldenRecordFeatureEngineer:
    """Feature engineering for Golden Record deduplication and matching"""
    
    def __init__(self, config_path: str = None):
        """
        Initialize feature engineer
        
        Args:
            config_path: Path to feature_config.yaml
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "feature_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.attributes = self.config['attributes']
        self.feature_config = self.config['feature_engineering']
    
    def compute_name_similarity(self, name1: str, name2: str) -> Dict[str, float]:
        """
        Compute multiple name similarity scores
        
        Args:
            name1: First name
            name2: Second name
            
        Returns:
            Dictionary with similarity scores
        """
        if pd.isna(name1) or pd.isna(name2):
            return {
                'jaro_winkler': 0.0,
                'jaro': 0.0,
                'levenshtein': 0.0,
                'ratio': 0.0,
                'partial_ratio': 0.0
            }
        
        name1 = str(name1).lower().strip()
        name2 = str(name2).lower().strip()
        
        if RAPIDFUZZ_AVAILABLE:
            return {
                'jaro_winkler': fuzz.ratio(name1, name2) / 100.0,
                'jaro': distance.Jaro.similarity(name1, name2),
                'levenshtein': 1 - (distance.Levenshtein.normalized_distance(name1, name2)),
                'ratio': fuzz.ratio(name1, name2) / 100.0,
                'partial_ratio': fuzz.partial_ratio(name1, name2) / 100.0
            }
        else:
            # Fallback to difflib
            ratio = difflib.SequenceMatcher(None, name1, name2).ratio()
            return {
                'jaro_winkler': ratio,
                'jaro': ratio,
                'levenshtein': ratio,
                'ratio': ratio,
                'partial_ratio': ratio
            }
    
    def compute_phonetic_match(self, name1: str, name2: str) -> Dict[str, bool]:
        """
        Compute phonetic encoding matches
        
        Args:
            name1: First name
            name2: Second name
            
        Returns:
            Dictionary with phonetic match results
        """
        if pd.isna(name1) or pd.isna(name2):
            return {
                'soundex_match': False,
                'metaphone_match': False
            }
        
        name1 = str(name1).lower().strip()
        name2 = str(name2).lower().strip()
        
        return {
            'soundex_match': soundex(name1) == soundex(name2),
            'metaphone_match': metaphone(name1) == metaphone(name2)
        }
    
    def compute_date_similarity(self, date1: pd.Timestamp, date2: pd.Timestamp) -> float:
        """
        Compute date similarity (exact match = 1.0, else 0.0)
        
        Args:
            date1: First date
            date2: Second date
            
        Returns:
            Similarity score (0.0 or 1.0)
        """
        if pd.isna(date1) or pd.isna(date2):
            return 0.0
        
        return 1.0 if date1 == date2 else 0.0
    
    def compute_geospatial_distance(self, 
                                   lat1: float, lon1: float,
                                   lat2: float, lon2: float) -> Dict[str, float]:
        """
        Compute geospatial distance between two coordinates
        
        Args:
            lat1, lon1: First coordinates
            lat2, lon2: Second coordinates
            
        Returns:
            Dictionary with distance metrics
        """
        if any(pd.isna(x) for x in [lat1, lon1, lat2, lon2]):
            return {
                'distance_km': float('inf'),
                'similarity_score': 0.0
            }
        
        try:
            point1 = (lat1, lon1)
            point2 = (lat2, lon2)
            dist_km = geodesic(point1, point2).kilometers
            
            # Convert distance to similarity score (0-1)
            # Using max_distance from config (default 5km)
            max_dist = self.feature_config['geospatial']['max_distance_km']
            similarity = max(0.0, 1.0 - (dist_km / max_dist))
            
            return {
                'distance_km': dist_km,
                'similarity_score': similarity
            }
        except:
            return {
                'distance_km': float('inf'),
                'similarity_score': 0.0
            }
    
    def compute_numeric_similarity(self, value1: float, value2: float,
                                   tolerance_percent: float = 10.0) -> float:
        """
        Compute numeric similarity (for income, age, etc.)
        
        Args:
            value1: First value
            value2: Second value
            tolerance_percent: Tolerance percentage
            
        Returns:
            Similarity score (0-1)
        """
        if pd.isna(value1) or pd.isna(value2):
            return 0.0
        
        if value1 == 0 and value2 == 0:
            return 1.0
        
        if value1 == 0 or value2 == 0:
            return 0.0
        
        percent_diff = abs(value1 - value2) / max(abs(value1), abs(value2)) * 100
        
        if percent_diff <= tolerance_percent:
            return 1.0 - (percent_diff / tolerance_percent)
        else:
            return 0.0
    
    def compute_match_features(self, record1: pd.Series, record2: pd.Series) -> Dict[str, float]:
        """
        Compute all matching features between two records
        
        Args:
            record1: First record (pandas Series)
            record2: Second record (pandas Series)
            
        Returns:
            Dictionary with all feature scores
        """
        features = {}
        
        # Name matching
        if 'full_name' in record1.index and 'full_name' in record2.index:
            name_sim = self.compute_name_similarity(
                record1['full_name'], record2['full_name']
            )
            features.update({f'name_{k}': v for k, v in name_sim.items()})
            
            phonetic = self.compute_phonetic_match(
                record1['full_name'], record2['full_name']
            )
            features.update({f'phonetic_{k}': float(v) for k, v in phonetic.items()})
        
        # Date of birth matching
        if 'date_of_birth' in record1.index and 'date_of_birth' in record2.index:
            dob_sim = self.compute_date_similarity(
                record1['date_of_birth'], record2['date_of_birth']
            )
            features['dob_exact_match'] = dob_sim
        
        # Income similarity
        if 'family_income' in record1.index and 'family_income' in record2.index:
            income_sim = self.compute_numeric_similarity(
                record1['family_income'], record2['family_income'],
                tolerance_percent=10.0
            )
            features['income_similarity'] = income_sim
        
        # Exact matches for categorical
        for field in ['gender', 'caste_id', 'district_id', 'pincode']:
            if field in record1.index and field in record2.index:
                features[f'{field}_match'] = float(
                    record1[field] == record2[field] if not pd.isna(record1[field]) and not pd.isna(record2[field]) else False
                )
        
        return features


if __name__ == "__main__":
    # Example usage
    engineer = GoldenRecordFeatureEngineer()
    
    # Test name similarity
    name1 = "Ram Kumar"
    name2 = "Ramesh Kumar"
    
    sim = engineer.compute_name_similarity(name1, name2)
    print(f"Name similarity: {sim}")
    
    phonetic = engineer.compute_phonetic_match(name1, name2)
    print(f"Phonetic match: {phonetic}")

