"""
Initialize Message Templates
Loads default message templates into database
"""

import sys
import os
from pathlib import Path
import yaml
import pandas as pd

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


TEMPLATES = [
    # SMS Templates (Hindi)
    {
        'template_code': 'SMS_INTIMATION_HI',
        'template_name': 'SMS Intimation - Hindi',
        'message_type': 'intimation',
        'channel': 'sms',
        'language': 'hi',
        'body_template': '''[SMART] आप {{ scheme_name }} के लिए पात्र हो सकते हैं।
मासिक लाभ: {{ benefit_amount }}
कारण: {{ eligibility_reason }}
हाँ/नहीं भेजें: {{ short_code }}
विवरण: {{ deep_link }}''',
        'status': 'active',
        'version': 1
    },
    # SMS Templates (English)
    {
        'template_code': 'SMS_INTIMATION_EN',
        'template_name': 'SMS Intimation - English',
        'message_type': 'intimation',
        'channel': 'sms',
        'language': 'en',
        'body_template': '''[SMART] You may be eligible for {{ scheme_name }}.
Monthly benefit: {{ benefit_amount }}
Reason: {{ eligibility_reason }}
Reply YES/NO to {{ short_code }}
Details: {{ deep_link }}''',
        'status': 'active',
        'version': 1
    },
    # Mobile App Templates
    {
        'template_code': 'APP_INTIMATION_HI',
        'template_name': 'Mobile App Intimation - Hindi',
        'message_type': 'intimation',
        'channel': 'mobile_app',
        'language': 'hi',
        'subject_template': '{{ scheme_name }} - आपके लिए एक योजना',
        'body_template': '''आप {{ scheme_name }} के लिए पात्र हो सकते हैं।

लाभ: {{ benefit_amount }}
कारण: {{ eligibility_reason }}

कृपया अपनी सहमति दें।''',
        'default_action_buttons': [
            {'label': 'हाँ, मेरी सहमति दें', 'action': 'consent_yes'},
            {'label': 'अधिक जानकारी', 'action': 'more_info'},
            {'label': 'नहीं', 'action': 'consent_no'}
        ],
        'status': 'active',
        'version': 1
    },
    # Email Templates
    {
        'template_code': 'EMAIL_INTIMATION_HI',
        'template_name': 'Email Intimation - Hindi',
        'message_type': 'intimation',
        'channel': 'email',
        'language': 'hi',
        'subject_template': 'SMART Platform - {{ scheme_name }} योजना के लिए आप पात्र हो सकते हैं',
        'body_template': '''नमस्ते,

आप {{ scheme_name }} योजना के लिए पात्र हो सकते हैं।

योजना विवरण:
- योजना: {{ scheme_name }}
- मासिक लाभ: {{ benefit_amount }}
- पात्रता कारण: {{ eligibility_reason }}

अपनी सहमति देने या अधिक जानकारी प्राप्त करने के लिए नीचे दिए गए लिंक पर क्लिक करें:
{{ deep_link }}

धन्यवाद,
SMART Platform Team''',
        'status': 'active',
        'version': 1
    },
]


def init_templates():
    """Initialize message templates in database"""
    print("=" * 80)
    print("Initializing Message Templates")
    print("=" * 80)
    
    # Load config
    config_path = os.path.join(os.path.dirname(__file__), '../config/db_config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Connect to database
    db_config = config['database']
    db = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    db.connect()
    
    cursor = db.connection.cursor()
    
    created = 0
    skipped = 0
    
    try:
        for template in TEMPLATES:
            # Check if template exists
            check_query = """
                SELECT template_id FROM intimation.message_templates
                WHERE template_code = %s
            """
            cursor.execute(check_query, (template['template_code'],))
            if cursor.fetchone():
                print(f"  ⚠️  Skipped (already exists): {template['template_code']}")
                skipped += 1
                continue
            
            # Insert template
            insert_query = """
                INSERT INTO intimation.message_templates (
                    template_code, template_name, message_type, channel, language,
                    subject_template, body_template, default_action_buttons,
                    status, version, created_by
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            import json
            cursor.execute(
                insert_query,
                (
                    template['template_code'],
                    template['template_name'],
                    template['message_type'],
                    template['channel'],
                    template['language'],
                    template.get('subject_template'),
                    template['body_template'],
                    json.dumps(template.get('default_action_buttons', [])) if template.get('default_action_buttons') else None,
                    template['status'],
                    template['version'],
                    'init_script'
                )
            )
            print(f"  ✅ Created: {template['template_code']}")
            created += 1
        
        db.connection.commit()
        
        print("\n" + "=" * 80)
        print(f"✅ Template initialization complete!")
        print(f"   Created: {created}")
        print(f"   Skipped: {skipped}")
        print(f"   Total: {created + skipped}")
        print("=" * 80)
        
    except Exception as e:
        db.connection.rollback()
        print(f"\n❌ Error initializing templates: {e}")
        raise
    finally:
        cursor.close()
        db.disconnect()


if __name__ == '__main__':
    init_templates()

