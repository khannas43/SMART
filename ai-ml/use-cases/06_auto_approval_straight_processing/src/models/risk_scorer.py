"""
Risk Scorer
ML-based risk assessment for application evaluation
Use Case ID: AI-PLATFORM-06
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import sys
from pathlib import Path
import json
import pickle

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class RiskScorer:
    """ML-based risk scoring engine"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Risk Scorer"""
        if config_path is None:
            base_dir = Path(__file__).parent.parent.parent
            config_path = base_dir / "config" / "db_config.yaml"
        
        import yaml
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Load use case config
        use_case_config_path = Path(config_path).parent / "use_case_config.yaml"
        if use_case_config_path.exists():
            with open(use_case_config_path, 'r') as f:
                self.use_case_config = yaml.safe_load(f)
        else:
            self.use_case_config = {}
        
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
        
        # Model cache (will be loaded on demand)
        self.models = {}
    
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
    
    def calculate_risk_score(
        self,
        application_id: int,
        family_id: str,
        scheme_code: str
    ) -> Dict[str, Any]:
        """
        Calculate risk score for an application
        
        Args:
            application_id: Application ID
            family_id: Family ID
            scheme_code: Scheme code
        
        Returns:
            Risk score results with score, band, and contributing factors
        """
        # Step 1: Extract features
        features = self._extract_features(application_id, family_id, scheme_code)
        
        # Step 2: Load or use default model
        model = self._load_model(scheme_code)
        
        # Step 3: Calculate risk score
        if model:
            risk_score, top_factors = self._score_with_model(model, features)
        else:
            # Fallback to rule-based scoring if model not available
            risk_score, top_factors = self._score_with_rules(features)
        
        # Step 4: Determine risk band
        risk_band = self._determine_risk_band(risk_score, scheme_code)
        
        return {
            'risk_score': risk_score,
            'risk_band': risk_band,
            'model_version': model.get('version', '1.0') if model else '1.0',
            'model_type': model.get('type', 'xgboost') if model else 'rule-based',
            'model_id': model.get('model_id') if model else None,
            'top_factors': top_factors,
            'features_used': features
        }
    
    def _extract_features(
        self,
        application_id: int,
        family_id: str,
        scheme_code: str
    ) -> Dict[str, Any]:
        """Extract features for risk scoring"""
        features = {}
        
        # 1. Profile features from Golden Record
        profile_features = self._get_profile_features(family_id)
        features.update(profile_features)
        
        # 2. Benefit history from 360° Profile
        benefit_features = self._get_benefit_history(family_id)
        features.update(benefit_features)
        
        # 3. Application behavior
        app_features = self._get_application_features(application_id, family_id, scheme_code)
        features.update(app_features)
        
        # 4. Eligibility features
        eligibility_features = self._get_eligibility_features(application_id, scheme_code)
        features.update(eligibility_features)
        
        return features
    
    def _get_profile_features(self, family_id: str) -> Dict[str, Any]:
        """Get profile features from Golden Record"""
        try:
            conn = self.external_dbs['golden_records'].connection
            cursor = conn.cursor()
            
            # Get family demographics (placeholder - actual schema may vary)
            cursor.execute("""
                SELECT 
                    COUNT(*) as family_size,
                    AVG(EXTRACT(YEAR FROM AGE(COALESCE(date_of_birth, CURRENT_DATE)))) as avg_age
                FROM golden_records.family_members
                WHERE family_id = %s
            """, (family_id,))
            
            row = cursor.fetchone()
            cursor.close()
            
            if row:
                return {
                    'family_size': row[0] or 0,
                    'avg_age': float(row[1]) if row[1] else 0.0
                }
        except Exception:
            pass
        
        return {'family_size': 0, 'avg_age': 0.0}
    
    def _get_benefit_history(self, family_id: str) -> Dict[str, Any]:
        """Get benefit history from 360° Profile"""
        try:
            conn = self.external_dbs['profile_360'].connection
            cursor = conn.cursor()
            
            # Get benefit history (placeholder - actual schema may vary)
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_benefits,
                    COUNT(DISTINCT scheme_code) as unique_schemes
                FROM profile_360.benefit_history
                WHERE family_id = %s
            """, (family_id,))
            
            row = cursor.fetchone()
            cursor.close()
            
            if row:
                return {
                    'total_benefits': row[0] or 0,
                    'unique_schemes': row[1] or 0
                }
        except Exception:
            pass
        
        return {'total_benefits': 0, 'unique_schemes': 0}
    
    def _get_application_features(
        self,
        application_id: int,
        family_id: str,
        scheme_code: str
    ) -> Dict[str, Any]:
        """Get application behavior features"""
        conn = self.external_dbs['application'].connection
        cursor = conn.cursor()
        
        # Get application details
        cursor.execute("""
            SELECT 
                submission_mode,
                created_at,
                eligibility_score
            FROM application.applications
            WHERE application_id = %s
        """, (application_id,))
        
        app_row = cursor.fetchone()
        
        # Count past rejections
        cursor.execute("""
            SELECT COUNT(*) 
            FROM application.applications
            WHERE family_id = %s 
                AND status = 'rejected'
        """, (family_id,))
        
        rejection_count = cursor.fetchone()[0] or 0
        
        cursor.close()
        
        if app_row:
            submission_mode = app_row[0] or 'manual'
            is_auto = 1 if submission_mode == 'auto' else 0
            eligibility_score = float(app_row[2]) if app_row[2] else 0.0
            
            return {
                'is_auto_submission': is_auto,
                'eligibility_score': eligibility_score,
                'past_rejections': rejection_count
            }
        
        return {
            'is_auto_submission': 0,
            'eligibility_score': 0.0,
            'past_rejections': rejection_count
        }
    
    def _get_eligibility_features(self, application_id: int, scheme_code: str) -> Dict[str, Any]:
        """Get eligibility features"""
        try:
            conn = self.external_dbs['eligibility'].connection
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    eligibility_score,
                    evaluation_status
                FROM eligibility.eligibility_snapshots
                WHERE snapshot_id IN (
                    SELECT eligibility_snapshot_id 
                    FROM application.applications 
                    WHERE application_id = %s
                )
                LIMIT 1
            """, (application_id,))
            
            row = cursor.fetchone()
            cursor.close()
            
            if row:
                score = float(row[0]) if row[0] else 0.0
                status = row[1] or ''
                return {
                    'eligibility_score': score,
                    'eligibility_status_rule': 1 if status == 'RULE_ELIGIBLE' else 0,
                    'eligibility_status_possible': 1 if status == 'POSSIBLE_ELIGIBLE' else 0
                }
        except Exception:
            pass
        
        return {
            'eligibility_score': 0.0,
            'eligibility_status_rule': 0,
            'eligibility_status_possible': 0
        }
    
    def _load_model(self, scheme_code: str) -> Optional[Dict[str, Any]]:
        """Load risk model for scheme (placeholder - will load actual models later)"""
        conn = self.db.connection
        cursor = conn.cursor()
        
        # Get active production model for scheme
        cursor.execute("""
            SELECT 
                model_id, model_name, model_version, model_type,
                model_path, model_artifact_uri
            FROM decision.risk_models
            WHERE (scheme_code = %s OR scheme_code IS NULL)
                AND is_production = true
                AND is_active = true
            ORDER BY scheme_code NULLS LAST, created_at DESC
            LIMIT 1
        """, (scheme_code,))
        
        row = cursor.fetchone()
        cursor.close()
        
        if row:
            return {
                'model_id': row[0],
                'name': row[1],
                'version': row[2],
                'type': row[3],
                'path': row[4],
                'artifact_uri': row[5]
            }
        
        # No model found - return None to use rule-based scoring
        return None
    
    def _score_with_model(
        self,
        model: Dict[str, Any],
        features: Dict[str, Any]
    ) -> tuple:
        """
        Score using ML model (placeholder - will implement actual model loading/inference)
        
        Returns:
            (risk_score, top_factors)
        """
        # TODO: Load actual model and make prediction
        # For now, return rule-based fallback
        return self._score_with_rules(features)
    
    def _score_with_rules(self, features: Dict[str, Any]) -> tuple:
        """Rule-based risk scoring (fallback when model not available)"""
        risk_score = 0.0
        factors = []
        
        # Factor 1: Past rejections (higher risk)
        past_rejections = features.get('past_rejections', 0)
        if past_rejections > 0:
            risk_score += min(0.3, past_rejections * 0.1)
            factors.append(f'Past rejections: {past_rejections}')
        
        # Factor 2: Low eligibility score (higher risk)
        eligibility_score = features.get('eligibility_score', 0.0)
        if eligibility_score < 0.6:
            risk_score += 0.2
            factors.append(f'Low eligibility score: {eligibility_score:.2f}')
        
        # Factor 3: Multiple benefits (lower risk - established beneficiary)
        unique_schemes = features.get('unique_schemes', 0)
        if unique_schemes > 3:
            risk_score -= 0.1
            factors.append(f'Established beneficiary: {unique_schemes} schemes')
        
        # Factor 4: Auto submission (lower risk - verified data)
        if features.get('is_auto_submission', 0) == 1:
            risk_score -= 0.15
            factors.append('Auto-submitted (verified data)')
        
        # Normalize to 0-1 range
        risk_score = max(0.0, min(1.0, risk_score))
        
        # Get top factors
        top_factors = factors[:5] if len(factors) > 5 else factors
        
        return risk_score, top_factors
    
    def _determine_risk_band(self, risk_score: float, scheme_code: str) -> str:
        """Determine risk band based on score and scheme configuration"""
        conn = self.db.connection
        cursor = conn.cursor()
        
        # Get scheme-specific thresholds
        cursor.execute("""
            SELECT low_risk_max, medium_risk_max
            FROM decision.decision_config
            WHERE scheme_code = %s AND is_active = true
            ORDER BY effective_from DESC
            LIMIT 1
        """, (scheme_code,))
        
        row = cursor.fetchone()
        cursor.close()
        
        if row:
            low_max = float(row[0])
            medium_max = float(row[1])
            
            if risk_score <= low_max:
                return 'LOW'
            elif risk_score <= medium_max:
                return 'MEDIUM'
            else:
                return 'HIGH'
        
        # Default thresholds
        if risk_score <= 0.3:
            return 'LOW'
        elif risk_score <= 0.7:
            return 'MEDIUM'
        else:
            return 'HIGH'

