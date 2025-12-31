"""
Test Message Personalization
Tests message template selection and rendering
"""

import sys
import os
from pathlib import Path
import uuid

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))
from message_personalizer import MessagePersonalizer


def test_message_personalization():
    """Test message personalization"""
    print("=" * 80)
    print("Testing Message Personalization")
    print("=" * 80)
    
    personalizer = MessagePersonalizer()
    
    try:
        # Test data
        candidate = {
            'family_id': str(uuid.uuid4()),
            'scheme_code': 'CHIRANJEEVI',
            'eligibility_reason': 'आयु 60 वर्ष और BPL परिवार',
            'preferred_language': 'hi'
        }
        
        scheme_info = {
            'scheme_name': 'Mukhyamantri Chiranjeevi Yojana',
            'scheme_code': 'CHIRANJEEVI',
            'benefit_amount': 5000
        }
        
        # Test SMS message
        print(f"\n📱 Testing SMS Message (Hindi)...")
        sms_message = personalizer.personalize_for_candidate(
            candidate, scheme_info, 'sms', 'hi'
        )
        print(f"   Template: {sms_message.template_id}")
        print(f"   Body length: {len(sms_message.body)} chars")
        print(f"   Preview: {sms_message.body[:100]}...")
        assert len(sms_message.body) <= 160, "SMS message too long"
        
        # Test Mobile App message
        print(f"\n📱 Testing Mobile App Message (Hindi)...")
        app_message = personalizer.personalize_for_candidate(
            candidate, scheme_info, 'mobile_app', 'hi'
        )
        print(f"   Template: {app_message.template_id}")
        print(f"   Action buttons: {len(app_message.action_buttons)}")
        print(f"   Deep link: {app_message.deep_link}")
        assert len(app_message.action_buttons) > 0, "No action buttons"
        
        # Test Email message
        print(f"\n📧 Testing Email Message (Hindi)...")
        email_message = personalizer.personalize_for_candidate(
            candidate, scheme_info, 'email', 'hi'
        )
        print(f"   Template: {email_message.template_id}")
        print(f"   Subject: {email_message.subject}")
        print(f"   Body length: {len(email_message.body)} chars")
        
        # Test English template
        print(f"\n📱 Testing SMS Message (English)...")
        candidate['preferred_language'] = 'en'
        en_message = personalizer.personalize_for_candidate(
            candidate, scheme_info, 'sms', 'en'
        )
        print(f"   Template: {en_message.template_id}")
        print(f"   Preview: {en_message.body[:100]}...")
        
        print("\n" + "=" * 80)
        print("✅ Message personalization test complete!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error during message personalization test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        personalizer.disconnect()


if __name__ == '__main__':
    test_message_personalization()

