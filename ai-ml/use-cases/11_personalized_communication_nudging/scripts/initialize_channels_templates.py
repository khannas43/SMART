#!/usr/bin/env python3
"""
Initialize Channels and Templates for AI-PLATFORM-11
Creates default channels and message templates.
"""

import sys
from pathlib import Path
import psycopg2
import yaml
import uuid

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


def initialize_channels_and_templates():
    """Initializes default channels and templates."""
    
    # Load database config
    config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    with open(config_path, 'r') as f:
        db_config = yaml.safe_load(f)['database']
    
    # Connect to database
    db = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    db.connect()
    cursor = db.connection.cursor()
    
    print("📦 Initializing channels and templates...")
    
    # 1. Initialize Channels
    channels = [
        {
            'channel_code': 'SMS',
            'channel_name': 'SMS',
            'channel_type': 'SMS',
            'max_length': 160,
            'template_required': True,
            'dlt_registered': True,
            'cost_per_unit': 0.1,
            'delivery_tracking': True
        },
        {
            'channel_code': 'APP_PUSH',
            'channel_name': 'Mobile App Push Notification',
            'channel_type': 'APP_PUSH',
            'max_length': 200,
            'template_required': False,
            'cost_per_unit': 0.0,
            'delivery_tracking': True,
            'open_tracking': True,
            'click_tracking': True
        },
        {
            'channel_code': 'WEB_INBOX',
            'channel_name': 'Web Portal Inbox',
            'channel_type': 'WEB_INBOX',
            'max_length': 1000,
            'template_required': False,
            'cost_per_unit': 0.0,
            'read_tracking': True,
            'click_tracking': True
        },
        {
            'channel_code': 'WHATSAPP',
            'channel_name': 'WhatsApp Business',
            'channel_type': 'WHATSAPP',
            'max_length': 1000,
            'template_required': True,
            'cost_per_unit': 0.05,
            'delivery_tracking': True,
            'read_receipts': True
        },
        {
            'channel_code': 'IVR',
            'channel_name': 'Interactive Voice Response',
            'channel_type': 'IVR',
            'max_duration_seconds': 120,
            'multilingual': True,
            'cost_per_call': 2.0
        },
        {
            'channel_code': 'ASSISTED_VISIT',
            'channel_name': 'Field Staff Visit',
            'channel_type': 'ASSISTED_VISIT',
            'field_staff_required': True,
            'cost_per_visit': 50.0
        }
    ]
    
    for channel in channels:
        cursor.execute("""
            INSERT INTO nudging.nudge_channels (
                channel_code, channel_name, channel_type, enabled,
                max_length, template_required, cost_per_unit
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (channel_code) DO UPDATE
            SET channel_name = EXCLUDED.channel_name,
                enabled = EXCLUDED.enabled;
        """, (
            channel['channel_code'], channel['channel_name'], channel['channel_type'], True,
            channel.get('max_length'), channel.get('template_required', False),
            channel.get('cost_per_unit', 0.0)
        ))
        print(f"✅ Initialized channel: {channel['channel_code']}")
    
    # 2. Initialize Templates
    templates = [
        # Renewal templates
        {
            'action_type': 'renewal',
            'template_name': 'Renewal Reminder - Urgent',
            'template_content': 'Dear {family_name}, your {scheme_name} renewal is due on {deadline}. Please renew to avoid benefit stoppage. Reply RENEW to start.',
            'channel_code': 'SMS',
            'language_code': 'en',
            'tone': 'urgent',
            'length_category': 'short'
        },
        {
            'action_type': 'renewal',
            'template_name': 'Renewal Reminder - Friendly',
            'template_content': 'Hi {family_name}, it\'s time to renew your {scheme_name} benefits. Renewal deadline: {deadline}. Visit the portal or reply RENEW.',
            'channel_code': 'SMS',
            'language_code': 'en',
            'tone': 'friendly',
            'length_category': 'medium'
        },
        {
            'action_type': 'renewal',
            'template_name': 'Renewal - App Push',
            'template_content': '🔔 Renewal Due: {scheme_name} expires on {deadline}. Tap to renew now and continue receiving benefits.',
            'channel_code': 'APP_PUSH',
            'language_code': 'en',
            'tone': 'friendly',
            'length_category': 'short'
        },
        # Missing document templates
        {
            'action_type': 'missing_doc',
            'template_name': 'Missing Document - Urgent',
            'template_content': 'Action Required: Please upload {document_type} for your {scheme_name} application. Upload now: {upload_link}',
            'channel_code': 'WEB_INBOX',
            'language_code': 'en',
            'tone': 'urgent',
            'length_category': 'medium'
        },
        {
            'action_type': 'missing_doc',
            'template_name': 'Missing Document - SMS',
            'template_content': 'Your {scheme_name} application requires {document_type}. Please submit via portal: {upload_link}',
            'channel_code': 'SMS',
            'language_code': 'en',
            'tone': 'formal',
            'length_category': 'short'
        },
        # Consent templates
        {
            'action_type': 'consent',
            'template_name': 'Consent Request - Friendly',
            'template_content': 'Hi {family_name}, you are eligible for {scheme_name}. Please provide consent to proceed. Consent here: {consent_link}',
            'channel_code': 'APP_PUSH',
            'language_code': 'en',
            'tone': 'friendly',
            'length_category': 'medium'
        },
        {
            'action_type': 'consent',
            'template_name': 'Consent Request - SMS',
            'template_content': 'You are eligible for {scheme_name}. Reply YES to consent or visit {portal_link}',
            'channel_code': 'SMS',
            'language_code': 'en',
            'tone': 'formal',
            'length_category': 'short'
        },
        # Deadline templates
        {
            'action_type': 'deadline',
            'template_name': 'Deadline Reminder - Critical',
            'template_content': '⏰ URGENT: {action_description} deadline is {deadline_date}. Complete now to avoid missing out.',
            'channel_code': 'SMS',
            'language_code': 'en',
            'tone': 'urgent',
            'length_category': 'short'
        },
        {
            'action_type': 'deadline',
            'template_name': 'Deadline Reminder - App',
            'template_content': '📅 Reminder: {action_description} due on {deadline_date}. Complete it now in the app.',
            'channel_code': 'APP_PUSH',
            'language_code': 'en',
            'tone': 'friendly',
            'length_category': 'short'
        },
        # Informational templates
        {
            'action_type': 'informational',
            'template_name': 'Informational - Friendly',
            'template_content': 'Good news! {information_message}. Learn more: {info_link}',
            'channel_code': 'WEB_INBOX',
            'language_code': 'en',
            'tone': 'friendly',
            'length_category': 'short'
        },
        {
            'action_type': 'informational',
            'template_name': 'Informational - SMS',
            'template_content': '{information_message}. For details, visit: {portal_link}',
            'channel_code': 'SMS',
            'language_code': 'en',
            'tone': 'formal',
            'length_category': 'short'
        }
    ]
    
    for template in templates:
        template_id = uuid.uuid4()
        cursor.execute("""
            INSERT INTO nudging.nudge_templates (
                template_id, action_type, template_name, template_content,
                language_code, channel_code, tone, length_category,
                approval_status, approved_by, approved_at
            ) VALUES (%s::uuid, %s, %s, %s, %s, %s, %s, %s, 'APPROVED', 'SYSTEM', CURRENT_TIMESTAMP)
            ON CONFLICT DO NOTHING;
        """, (
            str(template_id), template['action_type'], template['template_name'],
            template['template_content'], template['language_code'], template['channel_code'],
            template['tone'], template['length_category']
        ))
        print(f"✅ Initialized template: {template['template_name']} ({template['action_type']})")
    
    db.connection.commit()
    db.disconnect()
    
    print(f"\n✅ Initialization complete!")
    print(f"📊 Channels: {len(channels)}")
    print(f"📝 Templates: {len(templates)}")


if __name__ == "__main__":
    try:
        initialize_channels_and_templates()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

