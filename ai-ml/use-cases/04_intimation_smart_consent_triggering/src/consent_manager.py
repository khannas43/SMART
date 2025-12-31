"""
Consent Manager Service
Handles consent collection, validation, storage, and audit trails
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import yaml
import json
import pandas as pd
import uuid

# Add shared utils to path
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class ConsentManager:
    """Manages consent collection, validation, and storage"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Consent Manager"""
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__),
                '../config/db_config.yaml'
            )
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize database connection
        db_config = self.config['database']
        self.db = DBConnector(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['name'],
            user=db_config['user'],
            password=db_config['password']
        )
        self.db.connect()
        
        # Load use case config
        use_case_config_path = os.path.join(
            os.path.dirname(__file__),
            '../config/use_case_config.yaml'
        )
        with open(use_case_config_path, 'r') as f:
            self.use_case_config = yaml.safe_load(f)
    
    def create_consent(
        self,
        family_id: str,
        scheme_code: str,
        consent_value: bool,
        consent_method: str,
        channel: str,
        consent_purpose: str = 'enrollment',
        campaign_id: Optional[int] = None,
        candidate_id: Optional[int] = None,
        member_id: Optional[str] = None,
        session_id: Optional[str] = None,
        device_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a consent record
        
        Args:
            family_id: Family ID
            scheme_code: Scheme code
            consent_value: True for given, False for rejected
            consent_method: click, tap, otp, e_sign, offline
            channel: sms, mobile_app, web, whatsapp, ivr, offline
            consent_purpose: enrollment, data_sharing, notification (default: enrollment)
            campaign_id: Campaign ID (optional)
            candidate_id: Candidate ID (optional)
            member_id: Member ID (optional)
            session_id: Session ID
            device_id: Device ID
            ip_address: IP address
        
        Returns:
            Created consent record
        """
        # Determine consent type and LOA
        consent_type, loa = self._determine_consent_type(scheme_code)
        
        # Calculate validity period
        validity_days = self._get_consent_validity_days(scheme_code)
        valid_from = datetime.now()
        valid_until = valid_from + timedelta(days=validity_days) if validity_days > 0 else None
        
        # Get terms version
        terms_version = self._get_terms_version(scheme_code)
        
        # Determine status
        status = 'given' if consent_value else 'rejected'
        if consent_type == 'strong' and consent_method in ['click', 'tap']:
            status = 'pending'  # Pending OTP/e-sign verification
        
        # Create consent record
        query = """
            INSERT INTO intimation.consent_records (
                family_id, member_id, scheme_code, campaign_id, candidate_id,
                consent_type, level_of_assurance, consent_purpose, status, consent_value,
                consent_method, consent_channel, consent_device_id,
                consent_ip_address, consent_session_id,
                valid_from, valid_until, terms_version,
                created_at, updated_at, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING consent_id
        """
        
        cursor = self.db.connection.cursor()
        try:
            cursor.execute(
                query,
                (
                    family_id, member_id, scheme_code, campaign_id, candidate_id,
                    consent_type, loa, consent_purpose, status, consent_value,
                    consent_method, channel, device_id,
                    ip_address, session_id,
                    valid_from, valid_until, terms_version,
                    datetime.now(), datetime.now(), 'consent_manager'
                )
            )
            consent_id = cursor.fetchone()[0]
            self.db.connection.commit()
            
            # Publish event
            self._publish_event('CONSENT_GIVEN' if consent_value else 'CONSENT_REJECTED', {
                'consent_id': consent_id,
                'family_id': family_id,
                'scheme_code': scheme_code
            })
            
            # Return consent record
            return self.get_consent(consent_id)
            
        except Exception as e:
            self.db.connection.rollback()
            raise Exception(f"Error creating consent: {str(e)}")
        finally:
            cursor.close()
    
    def verify_otp(self, consent_id: int, otp: str) -> bool:
        """
        Verify OTP for strong consent
        
        Args:
            consent_id: Consent ID
            otp: OTP to verify
        
        Returns:
            True if verified successfully
        """
        # TODO: Integrate with Jan Aadhaar OTP service
        # For now, simple mock verification
        
        # Update consent record
        query = """
            UPDATE intimation.consent_records
            SET otp_verified = true,
                otp_verified_at = CURRENT_TIMESTAMP,
                status = 'given',
                updated_at = CURRENT_TIMESTAMP
            WHERE consent_id = %s
            AND consent_type = 'strong'
            AND status = 'pending'
            RETURNING consent_id
        """
        
        cursor = self.db.connection.cursor()
        try:
            cursor.execute(query, (consent_id,))
            if cursor.fetchone():
                self.db.connection.commit()
                self._publish_event('CONSENT_GIVEN', {
                    'consent_id': consent_id,
                    'verification_method': 'otp'
                })
                return True
            return False
        except Exception as e:
            self.db.connection.rollback()
            raise Exception(f"Error verifying OTP: {str(e)}")
        finally:
            cursor.close()
    
    def revoke_consent(
        self,
        consent_id: int,
        revocation_reason: str = 'user_request',
        revoked_by: str = 'user'
    ) -> bool:
        """
        Revoke a consent
        
        Args:
            consent_id: Consent ID
            revocation_reason: Reason for revocation
            revoked_by: Who revoked (user, admin, system)
        
        Returns:
            True if revoked successfully
        """
        query = """
            UPDATE intimation.consent_records
            SET status = 'revoked',
                consent_value = false,
                revoked_at = CURRENT_TIMESTAMP,
                revocation_reason = %s,
                revoked_by = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE consent_id = %s
            AND status = 'given'
            RETURNING consent_id
        """
        
        cursor = self.db.connection.cursor()
        try:
            cursor.execute(query, (revocation_reason, revoked_by, consent_id))
            if cursor.fetchone():
                self.db.connection.commit()
                self._publish_event('CONSENT_REVOKED', {
                    'consent_id': consent_id,
                    'reason': revocation_reason
                })
                return True
            return False
        except Exception as e:
            self.db.connection.rollback()
            raise Exception(f"Error revoking consent: {str(e)}")
        finally:
            cursor.close()
    
    def get_consent(self, consent_id: int) -> Dict[str, Any]:
        """Get consent record by ID"""
        query = "SELECT * FROM intimation.consent_records WHERE consent_id = %s"
        df = pd.read_sql(query, self.db.connection, params=[consent_id])
        return df.iloc[0].to_dict() if not df.empty else None
    
    def get_consent_status(self, family_id: str, scheme_code: str) -> Optional[Dict[str, Any]]:
        """Get active consent status for family and scheme"""
        query = """
            SELECT * FROM intimation.consent_records
            WHERE family_id = %s
            AND scheme_code = %s
            AND status = 'given'
            AND (valid_until IS NULL OR valid_until > CURRENT_TIMESTAMP)
            ORDER BY created_at DESC
            LIMIT 1
        """
        
        df = pd.read_sql(query, self.db.connection, params=[family_id, scheme_code])
        return df.iloc[0].to_dict() if not df.empty else None
    
    def _determine_consent_type(self, scheme_code: str) -> tuple:
        """Determine consent type and LOA for scheme"""
        query = """
            SELECT consent_type_required, require_otp, require_e_sign
            FROM intimation.scheme_intimation_config
            WHERE scheme_code = %s
        """
        
        try:
            df = pd.read_sql(query, self.db.connection, params=[scheme_code])
            if not df.empty:
                row = df.iloc[0]
                consent_type = row['consent_type_required']
                if row.get('require_e_sign'):
                    return (consent_type, 'LOA3')
                elif row.get('require_otp'):
                    return (consent_type, 'LOA2')
                else:
                    return (consent_type, 'LOA1')
        except Exception:
            pass
        
        # Default based on scheme category
        category_query = "SELECT category FROM public.scheme_master WHERE scheme_code = %s"
        try:
            df = pd.read_sql(category_query, self.db.connection, params=[scheme_code])
            if not df.empty:
                category = df.iloc[0]['category']
                if category in ['SOCIAL_SECURITY', 'PENSION', 'FINANCIAL']:
                    return ('strong', 'LOA2')
        except Exception:
            pass
        
        return ('soft', 'LOA1')
    
    def _get_consent_validity_days(self, scheme_code: str) -> int:
        """Get consent validity period for scheme"""
        query = """
            SELECT consent_validity_days
            FROM intimation.scheme_intimation_config
            WHERE scheme_code = %s
        """
        
        try:
            df = pd.read_sql(query, self.db.connection, params=[scheme_code])
            if not df.empty:
                return int(df.iloc[0]['consent_validity_days'])
        except Exception:
            pass
        
        return self.use_case_config['consent']['validity_period_days']
    
    def _get_terms_version(self, scheme_code: str) -> str:
        """Get current terms version for scheme"""
        # TODO: Implement terms versioning
        return "v1.0"
    
    def _publish_event(self, event_type: str, event_data: Dict[str, Any]):
        """Publish event to event log"""
        query = """
            INSERT INTO intimation.intimation_events (
                event_type, event_category, event_data, event_timestamp
            ) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
        """
        
        cursor = self.db.connection.cursor()
        try:
            cursor.execute(
                query,
                (event_type, 'consent', json.dumps(event_data))
            )
            self.db.connection.commit()
        except Exception as e:
            print(f"Warning: Could not publish event: {e}")
        finally:
            cursor.close()
    
    def disconnect(self):
        """Close database connection"""
        if self.db:
            self.db.disconnect()

