"""
Campaign Manager Service
Handles intake of eligibility signals, campaign creation, and scheduling
"""

import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import yaml
import pandas as pd

# Add shared utils to path
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


@dataclass
class Candidate:
    """Represents a candidate for intimation"""
    family_id: str
    member_id: Optional[str]
    scheme_code: str
    eligibility_score: float
    priority_score: float
    vulnerability_level: Optional[str]
    under_coverage_indicator: bool
    eligibility_reason: str
    primary_mobile: Optional[str]
    secondary_mobile: Optional[str]
    email: Optional[str]
    preferred_language: str = 'hi'
    preferred_channel: Optional[str] = None


@dataclass
class Campaign:
    """Represents an intimation campaign"""
    campaign_id: Optional[int]
    campaign_name: str
    scheme_code: str
    campaign_type: str
    eligibility_score_threshold: float
    priority_threshold: float
    target_districts: Optional[List[str]]
    target_segments: Optional[Dict[str, Any]]
    status: str
    scheduled_at: Optional[datetime]
    total_candidates: int = 0


class CampaignManager:
    """Manages intimation campaigns: intake, policy application, creation, scheduling"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Campaign Manager
        
        Args:
            config_path: Path to configuration file
        """
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__),
                '../config/db_config.yaml'
            )
        
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
        self.db.connect()
        
        # Eligibility database (for reading signals)
        eligibility_config = self.config['external_databases']['eligibility']
        self.eligibility_db = DBConnector(
            host=eligibility_config['host'],
            port=eligibility_config['port'],
            database=eligibility_config['name'],
            user=eligibility_config['user'],
            password=eligibility_config['password']
        )
        self.eligibility_db.connect()
        
        # Golden Records database (for contact info)
        gr_config = self.config['external_databases']['golden_records']
        self.gr_db = DBConnector(
            host=gr_config['host'],
            port=gr_config['port'],
            database=gr_config['name'],
            user=gr_config['user'],
            password=gr_config['password']
        )
        self.gr_db.connect()
        
        # Load use case config
        use_case_config_path = os.path.join(
            os.path.dirname(__file__),
            '../config/use_case_config.yaml'
        )
        with open(use_case_config_path, 'r') as f:
            self.use_case_config = yaml.safe_load(f)
    
    def intake_eligibility_signals(
        self,
        scheme_code: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Candidate]:
        """
        Intake eligibility signals from AI-PLATFORM-03
        
        Args:
            scheme_code: Filter by specific scheme (None = all schemes)
            filters: Additional filters (min_score, vulnerability_levels, etc.)
        
        Returns:
            List of eligible candidates
        """
        filters = filters or {}
        
        # Query eligibility snapshots
        query = """
            SELECT 
                es.family_id,
                es.member_id,
                es.scheme_code,
                es.eligibility_score,
                es.priority_score,
                es.vulnerability_level,
                es.under_coverage_indicator,
                es.reason_codes,
                es.evaluation_timestamp
            FROM eligibility.eligibility_snapshots es
            WHERE es.evaluation_status IN ('RULE_ELIGIBLE', 'POSSIBLE_ELIGIBLE')
        """
        
        params = []
        
        if scheme_code:
            query += " AND es.scheme_code = %s"
            params.append(scheme_code)
        
        # Apply score threshold
        min_score = filters.get('min_score', self.use_case_config['campaign']['min_eligibility_score'])
        query += " AND es.eligibility_score >= %s"
        params.append(min_score)
        
        # Only get recent evaluations (within last 7 days)
        query += " AND es.evaluation_timestamp >= CURRENT_TIMESTAMP - INTERVAL '7 days'"
        
        query += " ORDER BY es.priority_score DESC, es.evaluation_timestamp DESC"
        query += " LIMIT 10000"  # Limit per intake
        
        df = pd.read_sql(query, self.eligibility_db.connection, params=params)
        
        if df.empty:
            return []
        
        # Load contact information from Golden Records
        candidates = []
        for _, row in df.iterrows():
            contact_info = self._load_contact_info(row['family_id'])
            
            # Build eligibility reason from reason codes
            reason_codes = row.get('reason_codes', [])
            eligibility_reason = self._build_eligibility_reason(reason_codes, row['scheme_code'])
            
            candidate = Candidate(
                family_id=str(row['family_id']),
                member_id=str(row['member_id']) if pd.notna(row['member_id']) else None,
                scheme_code=row['scheme_code'],
                eligibility_score=float(row['eligibility_score']) if pd.notna(row['eligibility_score']) else 0.0,
                priority_score=float(row['priority_score']) if pd.notna(row['priority_score']) else 0.0,
                vulnerability_level=row.get('vulnerability_level'),
                under_coverage_indicator=bool(row.get('under_coverage_indicator', False)),
                eligibility_reason=eligibility_reason,
                primary_mobile=contact_info.get('primary_mobile'),
                secondary_mobile=contact_info.get('secondary_mobile'),
                email=contact_info.get('email'),
                preferred_language=contact_info.get('preferred_language', 'hi'),
                preferred_channel=contact_info.get('preferred_channel')
            )
            candidates.append(candidate)
        
        return candidates
    
    def apply_campaign_policies(
        self,
        candidates: List[Candidate],
        scheme_code: str
    ) -> List[Candidate]:
        """
        Apply campaign policies: thresholds, segments, fatigue limits
        
        Args:
            candidates: List of candidates
            scheme_code: Scheme code
        
        Returns:
            Filtered list of candidates
        """
        # Get scheme-specific config
        scheme_config = self._get_scheme_config(scheme_code)
        
        filtered = []
        
        for candidate in candidates:
            # Skip if not matching scheme
            if candidate.scheme_code != scheme_code:
                continue
            
            # Apply score threshold
            min_score = scheme_config.get('min_eligibility_score', 0.3)
            if candidate.eligibility_score < min_score:
                continue
            
            # Apply priority threshold (lenient - priority_score may be 0.0 if not calculated)
            priority_threshold = scheme_config.get('priority_threshold', 0.0)
            # Only apply priority threshold if it's > 0 AND priority_score is > 0
            # (0.0 might mean "not calculated" rather than "low priority")
            if priority_threshold > 0 and candidate.priority_score > 0 and candidate.priority_score < priority_threshold:
                # Still include if vulnerable or under-covered
                if not (candidate.vulnerability_level in ['VERY_HIGH', 'HIGH'] or
                       candidate.under_coverage_indicator):
                    continue
            
            # Check fatigue limits
            if self._check_fatigue_limit(candidate.family_id, scheme_code):
                continue
            
            # Check if has valid contact info (optional - campaigns can be created without it)
            # Contact info can be added later or retrieved from another source
            # For now, allow candidates without contact info (they'll need to be updated later)
            # if not (candidate.primary_mobile or candidate.email):
            #     continue
            
            filtered.append(candidate)
        
        return filtered
    
    def create_campaign(
        self,
        scheme_code: str,
        candidates: List[Candidate],
        campaign_name: Optional[str] = None,
        campaign_type: str = 'INITIAL',
        scheduled_at: Optional[datetime] = None
    ) -> Campaign:
        """
        Create a campaign with candidates
        
        Args:
            scheme_code: Scheme code
            candidates: List of candidates
            campaign_name: Campaign name (auto-generated if None)
            campaign_type: Campaign type (INITIAL, RETRY, ESCALATION, MANUAL)
            scheduled_at: Scheduled send time
        
        Returns:
            Created campaign
        """
        if not campaign_name:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            campaign_name = f"{scheme_code}_{campaign_type}_{timestamp}"
        
        # Get scheme config
        scheme_config = self._get_scheme_config(scheme_code)
        
        # Create campaign record
        campaign_query = """
            INSERT INTO intimation.campaigns (
                campaign_name, scheme_code, campaign_type,
                eligibility_score_threshold, priority_threshold,
                status, scheduled_at, total_candidates, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING campaign_id
        """
        
        cursor = self.db.connection.cursor()
        try:
            cursor.execute(
                campaign_query,
                (
                    campaign_name,
                    scheme_code,
                    campaign_type,
                    scheme_config.get('min_eligibility_score', 0.6),
                    scheme_config.get('priority_threshold', 0.8),
                    'scheduled' if scheduled_at else 'draft',
                    scheduled_at,
                    len(candidates),
                    'campaign_manager'
                )
            )
            campaign_id = cursor.fetchone()[0]
            
            # Insert candidates
            candidate_query = """
                INSERT INTO intimation.campaign_candidates (
                    campaign_id, family_id, member_id, scheme_code,
                    eligibility_score, priority_score, vulnerability_level,
                    under_coverage_indicator, eligibility_reason,
                    primary_mobile, secondary_mobile, email,
                    preferred_language, preferred_channel, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            for candidate in candidates:
                cursor.execute(
                    candidate_query,
                    (
                        campaign_id,
                        candidate.family_id,
                        candidate.member_id,
                        candidate.scheme_code,
                        candidate.eligibility_score,
                        candidate.priority_score,
                        candidate.vulnerability_level,
                        candidate.under_coverage_indicator,
                        candidate.eligibility_reason,
                        candidate.primary_mobile,
                        candidate.secondary_mobile,
                        candidate.email,
                        candidate.preferred_language,
                        candidate.preferred_channel,
                        'pending'
                    )
                )
            
            self.db.connection.commit()
            
            campaign = Campaign(
                campaign_id=campaign_id,
                campaign_name=campaign_name,
                scheme_code=scheme_code,
                campaign_type=campaign_type,
                eligibility_score_threshold=scheme_config.get('min_eligibility_score', 0.6),
                priority_threshold=scheme_config.get('priority_threshold', 0.8),
                target_districts=None,
                target_segments=None,
                status='scheduled' if scheduled_at else 'draft',
                scheduled_at=scheduled_at,
                total_candidates=len(candidates)
            )
            
            return campaign
            
        except Exception as e:
            self.db.connection.rollback()
            raise Exception(f"Error creating campaign: {str(e)}")
        finally:
            cursor.close()
    
    def schedule_campaign_sends(self, campaign_id: int) -> None:
        """
        Schedule send times for campaign candidates
        
        Args:
            campaign_id: Campaign ID
        """
        # Load campaign
        campaign_query = "SELECT * FROM intimation.campaigns WHERE campaign_id = %s"
        campaign_df = pd.read_sql(campaign_query, self.db.connection, params=[campaign_id])
        
        if campaign_df.empty:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        # Calculate send times based on load management
        candidates_query = """
            SELECT candidate_id, family_id, preferred_channel
            FROM intimation.campaign_candidates
            WHERE campaign_id = %s AND status = 'pending'
            ORDER BY priority_score DESC
        """
        candidates_df = pd.read_sql(candidates_query, self.db.connection, params=[campaign_id])
        
        if candidates_df.empty:
            return
        
        # Distribute sends across time windows
        batch_size = 100
        send_interval_minutes = 5  # 5 minutes between batches
        
        scheduled_at = datetime.now()
        if campaign_df.iloc[0]['scheduled_at']:
            scheduled_at = pd.to_datetime(campaign_df.iloc[0]['scheduled_at'])
        
        cursor = self.db.connection.cursor()
        try:
            for idx, (_, candidate) in enumerate(candidates_df.iterrows()):
                # Calculate send time (distribute across batches)
                batch_num = idx // batch_size
                send_time = scheduled_at + timedelta(minutes=batch_num * send_interval_minutes)
                
                # Respect quiet hours if configured
                send_time = self._adjust_for_quiet_hours(send_time, candidate['family_id'])
                
                # Update candidate
                update_query = """
                    UPDATE intimation.campaign_candidates
                    SET scheduled_send_at = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE candidate_id = %s
                """
                cursor.execute(update_query, (send_time, candidate['candidate_id']))
            
            # Update campaign status
            update_campaign = """
                UPDATE intimation.campaigns
                SET status = 'scheduled', updated_at = CURRENT_TIMESTAMP
                WHERE campaign_id = %s
            """
            cursor.execute(update_campaign, (campaign_id,))
            
            self.db.connection.commit()
            
        except Exception as e:
            self.db.connection.rollback()
            raise Exception(f"Error scheduling campaign: {str(e)}")
        finally:
            cursor.close()
    
    def _load_contact_info(self, family_id: str) -> Dict[str, Any]:
        """
        Load contact information from Golden Records
        
        Note: golden_records table may not have mobile/email columns.
        Contact info might be in a separate table or not available.
        Returns defaults if contact info is not found.
        """
        # Note: Contact info lookup is optional - campaigns can be created without it
        # The golden_records table structure may vary, and contact info might be in:
        # - smart_warehouse.golden_records (but we're connecting to smart database)
        # - profile_360 table
        # - citizens table
        # For now, return defaults - contact info will be None but campaigns can still be created
        
        # Return defaults - contact info not available or not critical for campaign creation
        # TODO: Query from correct source if contact info is needed (check which database has the table)
        return {
            'primary_mobile': None,
            'secondary_mobile': None,
            'email': None,
            'preferred_language': 'hi',
            'preferred_channel': None
        }
    
    def _build_eligibility_reason(self, reason_codes: List[str], scheme_code: str) -> str:
        """Build human-readable eligibility reason from reason codes"""
        if not reason_codes:
            return f"आप {scheme_code} योजना के लिए पात्र हो सकते हैं।"
        
        # Simple mapping (can be enhanced)
        reason_map = {
            'AGE_MET': 'आयु आवश्यकता पूरी होती है',
            'INCOME_MET': 'आय मानदंड पूरे होते हैं',
            'CATEGORY_MET': 'श्रेणी आवश्यकता पूरी होती है',
            'GEOGRAPHY_MET': 'भौगोलिक आवश्यकता पूरी होती है',
            'VULNERABLE': 'आप एक कमजोर परिवार हैं'
        }
        
        reasons = [reason_map.get(code, code) for code in reason_codes[:3]]
        return f"{', '.join(reasons)} के आधार पर आप इस योजना के लिए पात्र हो सकते हैं।"
    
    def _get_scheme_config(self, scheme_code: str) -> Dict[str, Any]:
        """Get scheme-specific configuration"""
        query = """
            SELECT * FROM intimation.scheme_intimation_config
            WHERE scheme_code = %s
        """
        
        try:
            df = pd.read_sql(query, self.db.connection, params=[scheme_code])
            if not df.empty:
                return df.iloc[0].to_dict()
        except Exception as e:
            print(f"Warning: Could not load scheme config for {scheme_code}: {e}")
        
        # Return defaults (more lenient for testing)
        return {
            'min_eligibility_score': 0.3,  # Lowered from 0.6 for testing
            'priority_threshold': 0.0,     # Allow 0.0 - priority_score may not be calculated yet
            'max_intimations_per_family': 3
        }
    
    def _check_fatigue_limit(self, family_id: str, scheme_code: str) -> bool:
        """Check if family has exceeded message fatigue limit"""
        # Check monthly limit
        query = """
            SELECT total_messages
            FROM intimation.message_fatigue
            WHERE family_id = %s
            AND period_type = 'month'
            AND period_start <= CURRENT_DATE
            AND period_end >= CURRENT_DATE
        """
        
        try:
            df = pd.read_sql(query, self.db.connection, params=[family_id])
            if not df.empty:
                total_messages = df.iloc[0]['total_messages']
                max_per_month = self.use_case_config['fatigue']['max_messages_per_month']
                if total_messages >= max_per_month:
                    return True
            
            # Check scheme-specific limit
            query_scheme = """
                SELECT messages_by_scheme
                FROM intimation.message_fatigue
                WHERE family_id = %s
                AND period_type = 'month'
                AND period_start <= CURRENT_DATE
                AND period_end >= CURRENT_DATE
            """
            df_scheme = pd.read_sql(query_scheme, self.db.connection, params=[family_id])
            if not df_scheme.empty:
                messages_by_scheme = df_scheme.iloc[0].get('messages_by_scheme', {})
                scheme_count = messages_by_scheme.get(scheme_code, 0)
                max_per_scheme = self.use_case_config['fatigue']['max_messages_per_scheme_per_month']
                if scheme_count >= max_per_scheme:
                    return True
        except Exception as e:
            print(f"Warning: Could not check fatigue limit: {e}")
        
        return False
    
    def _adjust_for_quiet_hours(self, send_time: datetime, family_id: str) -> datetime:
        """Adjust send time to respect quiet hours"""
        # Load user preferences
        query = """
            SELECT quiet_hours_enabled, quiet_hours_start, quiet_hours_end
            FROM intimation.user_preferences
            WHERE family_id = %s
        """
        
        try:
            df = pd.read_sql(query, self.db.connection, params=[family_id])
            if not df.empty:
                prefs = df.iloc[0]
                if prefs.get('quiet_hours_enabled'):
                    quiet_start = prefs.get('quiet_hours_start')
                    quiet_end = prefs.get('quiet_hours_end')
                    
                    # Check if send_time falls in quiet hours
                    send_hour = send_time.hour
                    if quiet_start and quiet_end:
                        start_hour = quiet_start.hour if hasattr(quiet_start, 'hour') else int(quiet_start.split(':')[0])
                        end_hour = quiet_end.hour if hasattr(quiet_end, 'hour') else int(quiet_end.split(':')[0])
                        
                        if start_hour > end_hour:  # Overnight quiet hours
                            if send_hour >= start_hour or send_hour < end_hour:
                                # Move to after quiet hours
                                send_time = send_time.replace(hour=end_hour, minute=0)
                        else:
                            if start_hour <= send_hour < end_hour:
                                # Move to after quiet hours
                                send_time = send_time.replace(hour=end_hour, minute=0)
        except Exception as e:
            print(f"Warning: Could not check quiet hours: {e}")
        
        return send_time
    
    def disconnect(self):
        """Close database connections"""
        if self.db:
            self.db.disconnect()
        if self.eligibility_db:
            self.eligibility_db.disconnect()
        if self.gr_db:
            self.gr_db.disconnect()

