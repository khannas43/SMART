#!/usr/bin/env python3
"""
Database Setup Script for AI-PLATFORM-11: Personalized Communication & Nudging
Creates all required tables in the 'nudging' schema.
"""

import sys
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import yaml

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector

def setup_database():
    """Creates the nudging schema and all required tables."""
    
    # Load database config
    config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    with open(config_path, 'r') as f:
        db_config = yaml.safe_load(f)['database']
    
    # Try multiple hosts if first fails (for WSL/Windows compatibility)
    hosts_to_try = [db_config['host']]
    if db_config['host'] != 'localhost':
        hosts_to_try.append('localhost')
    if db_config['host'] != '127.0.0.1':
        hosts_to_try.append('127.0.0.1')
    
    conn = None
    last_error = None
    for host in hosts_to_try:
        try:
            print(f"🔌 Attempting connection to {host}:{db_config['port']}...")
            conn = psycopg2.connect(
                host=host,
                port=db_config['port'],
                database=db_config['name'],
                user=db_config['user'],
                password=db_config['password'],
                connect_timeout=5
            )
            print(f"✅ Connected to PostgreSQL at {host}:{db_config['port']}")
            break
        except psycopg2.OperationalError as e:
            last_error = e
            print(f"❌ Connection to {host} failed: {e}")
            continue
    
    if conn is None:
        print(f"\n❌ Could not connect to PostgreSQL. Tried hosts: {hosts_to_try}")
        print(f"Last error: {last_error}")
        raise ConnectionError("Failed to connect to PostgreSQL with any of the tried hosts")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    print("📦 Setting up database for AI-PLATFORM-11: Personalized Communication & Nudging...")
    
    # Create schema
    cursor.execute("CREATE SCHEMA IF NOT EXISTS nudging;")
    print("✅ Created schema 'nudging'")
    
    # 1. Nudge Channels (available communication channels)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nudging.nudge_channels (
            channel_code VARCHAR(50) PRIMARY KEY,
            channel_name VARCHAR(100) NOT NULL,
            channel_type VARCHAR(50) NOT NULL, -- SMS, APP_PUSH, WEB_INBOX, WHATSAPP, IVR, ASSISTED_VISIT
            enabled BOOLEAN DEFAULT true,
            max_length INTEGER,
            template_required BOOLEAN DEFAULT false,
            cost_per_unit DECIMAL(10, 2),
            delivery_tracking BOOLEAN DEFAULT false,
            open_tracking BOOLEAN DEFAULT false,
            click_tracking BOOLEAN DEFAULT false,
            metadata JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("✅ Created table 'nudge_channels'")
    
    # 2. Nudge Templates (message templates by action type)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nudging.nudge_templates (
            template_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            action_type VARCHAR(50) NOT NULL, -- renewal, missing_doc, consent, deadline, informational
            template_name VARCHAR(100) NOT NULL,
            template_content TEXT NOT NULL,
            language_code VARCHAR(10) DEFAULT 'en',
            channel_code VARCHAR(50) NOT NULL,
            tone VARCHAR(50), -- formal, friendly, urgent, supportive
            length_category VARCHAR(20), -- short, medium, long
            variables JSONB, -- List of variables to substitute
            approval_status VARCHAR(20) DEFAULT 'APPROVED', -- APPROVED, PENDING, REJECTED
            approved_by VARCHAR(100),
            approved_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (channel_code) REFERENCES nudging.nudge_channels(channel_code)
        );
    """)
    print("✅ Created table 'nudge_templates'")
    
    # 3. Nudges (main nudge records)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nudging.nudges (
            nudge_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            family_id VARCHAR(100) NOT NULL,
            action_type VARCHAR(50) NOT NULL,
            action_context JSONB, -- Additional context about the action (scheme_code, document_type, etc.)
            urgency VARCHAR(20) NOT NULL, -- LOW, MEDIUM, HIGH, CRITICAL
            expiry_date DATE,
            scheduled_channel VARCHAR(50) NOT NULL,
            scheduled_time TIMESTAMP NOT NULL,
            template_id UUID NOT NULL,
            personalized_content TEXT, -- Final personalized message content
            status VARCHAR(20) DEFAULT 'SCHEDULED', -- SCHEDULED, SENT, DELIVERED, OPENED, CLICKED, RESPONDED, COMPLETED, FAILED, CANCELLED
            delivery_status VARCHAR(20), -- PENDING, DELIVERED, FAILED, BOUNCED
            opened_at TIMESTAMP,
            clicked_at TIMESTAMP,
            responded_at TIMESTAMP,
            completed_at TIMESTAMP,
            failed_reason TEXT,
            sent_at TIMESTAMP,
            delivered_at TIMESTAMP,
            metadata JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (scheduled_channel) REFERENCES nudging.nudge_channels(channel_code),
            FOREIGN KEY (template_id) REFERENCES nudging.nudge_templates(template_id)
        );
    """)
    print("✅ Created table 'nudges'")
    
    # 4. Nudge History (historical tracking for learning)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nudging.nudge_history (
            history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            nudge_id UUID NOT NULL,
            family_id VARCHAR(100) NOT NULL,
            channel_code VARCHAR(50) NOT NULL,
            action_type VARCHAR(50) NOT NULL,
            template_id UUID,
            sent_time TIMESTAMP NOT NULL,
            time_window VARCHAR(20), -- MORNING, AFTERNOON, EVENING, NIGHT
            day_of_week INTEGER, -- 0=Monday, 6=Sunday
            is_weekend BOOLEAN,
            delivered BOOLEAN DEFAULT false,
            opened BOOLEAN DEFAULT false,
            clicked BOOLEAN DEFAULT false,
            responded BOOLEAN DEFAULT false,
            completed BOOLEAN DEFAULT false,
            ignored BOOLEAN DEFAULT false,
            response_time_seconds INTEGER, -- Time from sent to responded
            engagement_score DECIMAL(5, 2), -- Computed engagement score (0-100)
            context_features JSONB, -- Features used for optimization (urgency, demographics, etc.)
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (nudge_id) REFERENCES nudging.nudges(nudge_id),
            FOREIGN KEY (channel_code) REFERENCES nudging.nudge_channels(channel_code)
        );
    """)
    print("✅ Created table 'nudge_history'")
    
    # 5. Fatigue Tracking (family-level fatigue counters)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nudging.fatigue_tracking (
            fatigue_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            family_id VARCHAR(100) NOT NULL,
            period_type VARCHAR(20) NOT NULL, -- DAY, WEEK, MONTH
            period_start DATE NOT NULL,
            period_end DATE NOT NULL,
            nudge_count INTEGER DEFAULT 0,
            channel_counts JSONB, -- Counts per channel
            action_type_counts JSONB, -- Counts per action type
            last_nudge_at TIMESTAMP,
            vulnerability_category VARCHAR(20), -- HIGH, MEDIUM, LOW
            adjusted_limits JSONB, -- Adjusted limits based on vulnerability
            cooldown_until TIMESTAMP, -- Cooldown period end
            cooldown_reason VARCHAR(100), -- Reason for cooldown
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(family_id, period_type, period_start)
        );
    """)
    print("✅ Created table 'fatigue_tracking'")
    
    # 6. Channel Preferences (learned preferences per family)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nudging.channel_preferences (
            preference_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            family_id VARCHAR(100) NOT NULL,
            channel_code VARCHAR(50) NOT NULL,
            action_type VARCHAR(50), -- NULL means general preference
            preference_score DECIMAL(5, 2) NOT NULL, -- 0-100, higher is better
            engagement_rate DECIMAL(5, 2), -- Historical engagement rate (0-100)
            total_sends INTEGER DEFAULT 0,
            total_opens INTEGER DEFAULT 0,
            total_clicks INTEGER DEFAULT 0,
            total_responses INTEGER DEFAULT 0,
            total_completions INTEGER DEFAULT 0,
            last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (channel_code) REFERENCES nudging.nudge_channels(channel_code),
            UNIQUE(family_id, channel_code, action_type)
        );
    """)
    print("✅ Created table 'channel_preferences'")
    
    # 7. Send Time Preferences (learned optimal send times)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nudging.send_time_preferences (
            time_preference_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            family_id VARCHAR(100) NOT NULL,
            channel_code VARCHAR(50) NOT NULL,
            action_type VARCHAR(50),
            time_window VARCHAR(20) NOT NULL, -- MORNING, AFTERNOON, EVENING, NIGHT
            day_of_week INTEGER, -- NULL means applies to all days, 0=Monday, 6=Sunday
            is_weekend BOOLEAN, -- NULL means applies to both
            preference_score DECIMAL(5, 2) NOT NULL, -- 0-100
            response_rate DECIMAL(5, 2), -- Historical response rate (0-100)
            total_sends INTEGER DEFAULT 0,
            total_responses INTEGER DEFAULT 0,
            last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (channel_code) REFERENCES nudging.nudge_channels(channel_code),
            UNIQUE(family_id, channel_code, action_type, time_window, day_of_week, is_weekend)
        );
    """)
    print("✅ Created table 'send_time_preferences'")
    
    # 8. Content Effectiveness (template effectiveness metrics)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nudging.content_effectiveness (
            effectiveness_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            template_id UUID NOT NULL,
            action_type VARCHAR(50) NOT NULL,
            channel_code VARCHAR(50) NOT NULL,
            demographic_segment VARCHAR(100), -- Age group, income level, etc.
            total_sends INTEGER DEFAULT 0,
            total_opens INTEGER DEFAULT 0,
            total_clicks INTEGER DEFAULT 0,
            total_responses INTEGER DEFAULT 0,
            total_completions INTEGER DEFAULT 0,
            open_rate DECIMAL(5, 2), -- Percentage
            click_rate DECIMAL(5, 2), -- Percentage
            response_rate DECIMAL(5, 2), -- Percentage
            completion_rate DECIMAL(5, 2), -- Percentage
            average_response_time_seconds INTEGER,
            effectiveness_score DECIMAL(5, 2), -- Computed effectiveness score
            last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (template_id) REFERENCES nudging.nudge_templates(template_id),
            FOREIGN KEY (channel_code) REFERENCES nudging.nudge_channels(channel_code)
        );
    """)
    print("✅ Created table 'content_effectiveness'")
    
    # 9. Family Consent & Preferences
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nudging.family_consent (
            consent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            family_id VARCHAR(100) NOT NULL UNIQUE,
            consent_given BOOLEAN DEFAULT true,
            consent_channels JSONB, -- Allowed channels: ["SMS", "APP_PUSH", ...]
            opt_out_channels JSONB, -- Opted-out channels: ["WHATSAPP", ...]
            preferred_language VARCHAR(10) DEFAULT 'en',
            preferred_time_windows JSONB, -- ["MORNING", "AFTERNOON"]
            do_not_disturb_until TIMESTAMP,
            vulnerability_category VARCHAR(20), -- HIGH, MEDIUM, LOW
            digital_footprint_score DECIMAL(5, 2), -- 0-100
            last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("✅ Created table 'family_consent'")
    
    # 10. Nudge Audit Logs (compliance and audit trail)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nudging.nudge_audit_logs (
            audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            action_type VARCHAR(50) NOT NULL, -- NUDGE_SCHEDULED, NUDGE_SENT, CONSENT_UPDATED, OPT_OUT, etc.
            entity_type VARCHAR(50) NOT NULL, -- NUDGE, CONSENT, TEMPLATE, etc.
            entity_id VARCHAR(255) NOT NULL,
            performed_by VARCHAR(100), -- USER, SYSTEM, ADMIN
            details JSONB,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("✅ Created table 'nudge_audit_logs'")
    
    # Create indexes
    indexes = [
        ("CREATE INDEX IF NOT EXISTS idx_nudges_family_id ON nudging.nudges(family_id);", "nudges.family_id"),
        ("CREATE INDEX IF NOT EXISTS idx_nudges_status ON nudging.nudges(status);", "nudges.status"),
        ("CREATE INDEX IF NOT EXISTS idx_nudges_scheduled_time ON nudging.nudges(scheduled_time);", "nudges.scheduled_time"),
        ("CREATE INDEX IF NOT EXISTS idx_nudge_history_family_id ON nudging.nudge_history(family_id);", "nudge_history.family_id"),
        ("CREATE INDEX IF NOT EXISTS idx_nudge_history_sent_time ON nudging.nudge_history(sent_time);", "nudge_history.sent_time"),
        ("CREATE INDEX IF NOT EXISTS idx_fatigue_tracking_family_id ON nudging.fatigue_tracking(family_id);", "fatigue_tracking.family_id"),
        ("CREATE INDEX IF NOT EXISTS idx_channel_preferences_family_id ON nudging.channel_preferences(family_id);", "channel_preferences.family_id"),
        ("CREATE INDEX IF NOT EXISTS idx_family_consent_family_id ON nudging.family_consent(family_id);", "family_consent.family_id"),
    ]
    
    for index_sql, index_name in indexes:
        cursor.execute(index_sql)
        print(f"✅ Created index '{index_name}'")
    
    conn.close()
    print("\n✅ Database setup completed successfully!")
    print("📊 Schema: nudging")
    print("📋 Tables created: 10")
    print("📇 Indexes created: 8")

if __name__ == "__main__":
    try:
        setup_database()
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        sys.exit(1)

