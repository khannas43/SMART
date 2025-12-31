"""
Exception Pattern Detector
Use Case ID: AI-PLATFORM-09

Detects households/individuals with atypical circumstances that may fall through
cracks of rigid rules (e.g., recently disabled, migrant workers, homeless).
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
import json
from datetime import datetime, timedelta
import numpy as np

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector

# Try to import sklearn for anomaly detection
try:
    from sklearn.ensemble import IsolationForest
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️  scikit-learn not available, using rule-based exception detection")


class ExceptionPatternDetector:
    """
    Exception Pattern Detector Service
    
    Detects atypical circumstances using:
    - Anomaly detection on 360° feature space
    - Rule-based pattern matching
    - Temporal pattern analysis (recent changes)
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Exception Pattern Detector"""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "use_case_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Configuration
        exception_config = self.config.get('exception_detection', {})
        self.enabled = exception_config.get('enable_exception_detection', True)
        self.anomaly_threshold = exception_config.get('anomaly_threshold', 0.75)
        self.require_human_review = exception_config.get('require_human_review', True)
        self.exception_categories = exception_config.get('exception_categories', [])
        
        # Database configuration
        db_config_path = Path(__file__).parent.parent.parent / "config" / "db_config.yaml"
        with open(db_config_path, 'r') as f:
            db_config = yaml.safe_load(f)['database']
        
        self.db = DBConnector(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['name'],
            user=db_config['user'],
            password=db_config['password']
        )
        
        # External database connections
        external_dbs = yaml.safe_load(open(db_config_path, 'r')).get('external_databases', {})
        self.external_dbs = {}
        for name, ext_config in external_dbs.items():
            self.external_dbs[name] = DBConnector(
                host=ext_config['host'],
                port=ext_config['port'],
                database=ext_config['name'],
                user=ext_config['user'],
                password=ext_config['password']
            )
    
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
    
    def detect_exceptions(
        self,
        family_id: str,
        beneficiary_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect exception patterns for a household/beneficiary
        
        Args:
            family_id: Family ID
            beneficiary_id: Optional beneficiary ID for specific beneficiary
        
        Returns:
            List of exception flags detected
        """
        exceptions = []
        
        if not self.enabled:
            return exceptions
        
        # 1. Rule-based pattern detection
        rule_exceptions = self._detect_rule_based_exceptions(family_id, beneficiary_id)
        exceptions.extend(rule_exceptions)
        
        # 2. Anomaly-based detection
        if SKLEARN_AVAILABLE:
            anomaly_exceptions = self._detect_anomaly_based_exceptions(family_id, beneficiary_id)
            exceptions.extend(anomaly_exceptions)
        
        # 3. Temporal pattern detection
        temporal_exceptions = self._detect_temporal_exceptions(family_id, beneficiary_id)
        exceptions.extend(temporal_exceptions)
        
        return exceptions
    
    def _detect_rule_based_exceptions(
        self,
        family_id: str,
        beneficiary_id: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Detect exceptions using rule-based patterns"""
        exceptions = []
        
        try:
            # Get household data
            conn = self.external_dbs['golden_records'].connection
            cursor = conn.cursor()
            
            if beneficiary_id:
                cursor.execute("""
                    SELECT 
                        beneficiary_id, full_name, date_of_birth, gender, category,
                        disability_status, address_district, address_block,
                        address_gram_panchayat, is_active
                    FROM golden_records.beneficiaries
                    WHERE beneficiary_id = %s AND family_id = %s::uuid
                """, (beneficiary_id, family_id))
            else:
                cursor.execute("""
                    SELECT 
                        beneficiary_id, full_name, date_of_birth, gender, category,
                        disability_status, address_district, address_block,
                        address_gram_panchayat, is_active
                    FROM golden_records.beneficiaries
                    WHERE family_id = %s::uuid AND is_active = TRUE
                    LIMIT 1
                """, (family_id,))
            
            row = cursor.fetchone()
            cursor.close()
            
            if not row:
                return exceptions
            
            ben_id, name, dob, gender, category, disability, district, block, gp, is_active = row
            
            # Check for recently disabled
            if disability and self._is_recently_disabled(ben_id, disability):
                exceptions.append({
                    'beneficiary_id': ben_id,
                    'exception_category': 'RECENTLY_DISABLED',
                    'exception_description': 'Disability status recently updated, may not be reflected in categorical databases',
                    'anomaly_score': 0.8,
                    'detected_features': {
                        'disability_status': disability,
                        'recent_update': True
                    },
                    'requires_human_review': True
                })
            
            # Check for migrant worker patterns
            if self._is_migrant_worker_pattern(family_id):
                exceptions.append({
                    'family_id': family_id,
                    'exception_category': 'MIGRANT_WORKER',
                    'exception_description': 'Pattern suggests migrant worker - may miss address-based eligibility',
                    'anomaly_score': 0.7,
                    'detected_features': {
                        'address_frequency': 'low',
                        'benefit_coverage': 'sparse'
                    },
                    'requires_human_review': True
                })
            
            # Check for homeless/informal settlement
            if self._is_homeless_informal_settlement(district, block, gp):
                exceptions.append({
                    'family_id': family_id,
                    'exception_category': 'HOMELESS_INFORMAL_SETTLEMENT',
                    'exception_description': 'Address pattern suggests informal settlement - may miss address-based eligibility',
                    'anomaly_score': 0.75,
                    'detected_features': {
                        'address_type': 'informal',
                        'location': f"{block}, {district}"
                    },
                    'requires_human_review': True
                })
            
            # Check for dropout student pattern
            if self._is_dropout_student_pattern(ben_id, dob):
                exceptions.append({
                    'beneficiary_id': ben_id,
                    'exception_category': 'DROPOUT_STUDENT',
                    'exception_description': 'Age pattern suggests student dropout - may miss education support schemes',
                    'anomaly_score': 0.65,
                    'detected_features': {
                        'age_range': 'student_age',
                        'education_benefits': 'none'
                    },
                    'requires_human_review': True
                })
        
        except Exception as e:
            print(f"⚠️  Error in rule-based exception detection: {e}")
        
        return exceptions
    
    def _is_recently_disabled(self, beneficiary_id: str, current_disability: str) -> bool:
        """Check if disability was recently added"""
        # TODO: Check disability status change history
        # For now, if disability exists but no benefits yet, consider recent
        try:
            conn = self.external_dbs['profile_360'].connection
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM profile_360.benefit_history
                WHERE beneficiary_id = %s
                  AND scheme_code LIKE '%DISABILITY%'
                  AND benefit_date >= CURRENT_DATE - INTERVAL '180 days'
            """, (beneficiary_id,))
            
            count = cursor.fetchone()[0]
            cursor.close()
            
            # If disabled but no recent disability benefits, likely recently disabled
            return current_disability and str(current_disability).upper() in ['YES', 'TRUE', '1'] and count == 0
        
        except Exception:
            return False
    
    def _is_migrant_worker_pattern(self, family_id: str) -> bool:
        """Check for migrant worker patterns"""
        try:
            conn = self.external_dbs['profile_360'].connection
            cursor = conn.cursor()
            
            # Check for sparse benefit coverage across locations
            cursor.execute("""
                SELECT COUNT(DISTINCT address_district) as district_count,
                       COUNT(*) as benefit_count
                FROM profile_360.benefit_history bh
                INNER JOIN golden_records.beneficiaries b 
                    ON bh.beneficiary_id = b.beneficiary_id
                WHERE b.family_id = %s::uuid
                  AND bh.benefit_date >= CURRENT_DATE - INTERVAL '365 days'
            """, (family_id,))
            
            row = cursor.fetchone()
            cursor.close()
            
            if row:
                district_count = row[0] or 0
                benefit_count = row[1] or 0
                # Multiple districts or very sparse coverage suggests migration
                return district_count > 1 or (benefit_count > 0 and benefit_count < 3)
        
        except Exception:
            pass
        
        return False
    
    def _is_homeless_informal_settlement(self, district: Optional[str], block: Optional[str], gp: Optional[str]) -> bool:
        """Check for homeless/informal settlement indicators"""
        # Check for common informal settlement indicators in address
        informal_keywords = ['slum', 'jhuggi', 'colony', 'basti', 'urban_village']
        
        address_parts = []
        if district:
            address_parts.append(district.lower())
        if block:
            address_parts.append(block.lower())
        if gp:
            address_parts.append(gp.lower())
        
        address_text = ' '.join(address_parts)
        
        # Simple keyword matching (can be enhanced)
        return any(keyword in address_text for keyword in informal_keywords)
    
    def _is_dropout_student_pattern(self, beneficiary_id: str, date_of_birth: Optional[datetime]) -> bool:
        """Check for dropout student pattern"""
        if not date_of_birth:
            return False
        
        try:
            # Calculate age
            age = (datetime.now().date() - date_of_birth).days // 365 if isinstance(date_of_birth, datetime) else None
            
            if age and 15 <= age <= 25:  # Student age range
                # Check for absence of education benefits
                conn = self.external_dbs['profile_360'].connection
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM profile_360.benefit_history
                    WHERE beneficiary_id = %s
                      AND (scheme_code LIKE '%SCHOLARSHIP%' 
                           OR scheme_code LIKE '%EDUCATION%'
                           OR scheme_code LIKE '%STUDENT%')
                """, (beneficiary_id,))
                
                count = cursor.fetchone()[0]
                cursor.close()
                
                # Student age but no education benefits suggests dropout
                return count == 0
        
        except Exception:
            pass
        
        return False
    
    def _detect_anomaly_based_exceptions(
        self,
        family_id: str,
        beneficiary_id: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Detect exceptions using anomaly detection"""
        exceptions = []
        
        if not SKLEARN_AVAILABLE:
            return exceptions
        
        try:
            # Extract features from 360° profile
            features = self._extract_features_for_anomaly(family_id, beneficiary_id)
            
            if not features or len(features) < 3:
                return exceptions
            
            # TODO: Train/load Isolation Forest model
            # For now, use simple threshold-based detection
            
            # Simple anomaly scoring based on feature combinations
            anomaly_score = self._calculate_simple_anomaly_score(features)
            
            if anomaly_score >= self.anomaly_threshold:
                exceptions.append({
                    'family_id': family_id,
                    'beneficiary_id': beneficiary_id,
                    'exception_category': 'OTHER_ATYPICAL',
                    'exception_description': 'Anomaly detection flagged atypical pattern in profile features',
                    'anomaly_score': anomaly_score,
                    'detected_features': features,
                    'requires_human_review': True
                })
        
        except Exception as e:
            print(f"⚠️  Error in anomaly-based exception detection: {e}")
        
        return exceptions
    
    def _extract_features_for_anomaly(
        self,
        family_id: str,
        beneficiary_id: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Extract features for anomaly detection"""
        features = {}
        
        try:
            # Get basic features
            conn = self.external_dbs['golden_records'].connection
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as family_size,
                    COUNT(CASE WHEN disability_status IS NOT NULL THEN 1 END) as disabled_count,
                    COUNT(CASE WHEN category IN ('SC', 'ST') THEN 1 END) as reserved_category_count
                FROM golden_records.beneficiaries
                WHERE family_id = %s::uuid AND is_active = TRUE
            """, (family_id,))
            
            row = cursor.fetchone()
            if row:
                features['family_size'] = row[0] or 0
                features['disabled_count'] = row[1] or 0
                features['reserved_category_count'] = row[2] or 0
            
            cursor.close()
            
            # Get benefit coverage features
            conn = self.external_dbs['profile_360'].connection
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT scheme_code) as scheme_count,
                    COUNT(*) as benefit_count,
                    AVG(benefit_amount) as avg_benefit
                FROM profile_360.benefit_history
                WHERE beneficiary_id IN (
                    SELECT beneficiary_id FROM golden_records.beneficiaries 
                    WHERE family_id = %s::uuid
                )
                  AND benefit_date >= CURRENT_DATE - INTERVAL '365 days'
            """, (family_id,))
            
            row = cursor.fetchone()
            if row:
                features['scheme_count'] = row[0] or 0
                features['benefit_count'] = row[1] or 0
                features['avg_benefit'] = float(row[2]) if row[2] else 0.0
            
            cursor.close()
        
        except Exception as e:
            print(f"⚠️  Error extracting features: {e}")
            return None
        
        return features
    
    def _calculate_simple_anomaly_score(self, features: Dict[str, Any]) -> float:
        """Calculate simple anomaly score (placeholder for ML model)"""
        score = 0.0
        
        # Simple heuristics
        family_size = features.get('family_size', 0)
        disabled_count = features.get('disabled_count', 0)
        scheme_count = features.get('scheme_count', 0)
        benefit_count = features.get('benefit_count', 0)
        
        # Large family with low benefits = anomaly
        if family_size > 5 and benefit_count < 2:
            score += 0.3
        
        # Disabled members but no disability benefits = anomaly
        if disabled_count > 0 and scheme_count == 0:
            score += 0.3
        
        # Very low benefit coverage relative to family size = anomaly
        if family_size > 0 and (benefit_count / family_size) < 0.2:
            score += 0.2
        
        return min(1.0, score)
    
    def _detect_temporal_exceptions(
        self,
        family_id: str,
        beneficiary_id: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Detect exceptions based on temporal patterns"""
        exceptions = []
        
        # Check for recent status changes that may not be reflected in eligibility
        # This is a placeholder - can be enhanced with actual change history
        
        return exceptions

