"""
Test Consent Management
Tests consent creation and retrieval
"""

import sys
import os
from pathlib import Path
import uuid

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))
from consent_manager import ConsentManager


def test_consent():
    """Test consent management"""
    print("=" * 80)
    print("Testing Consent Management")
    print("=" * 80)
    
    manager = ConsentManager()
    
    try:
        # Test consent creation
        family_id = str(uuid.uuid4())
        scheme_code = 'CHIRANJEEVI'
        
        print(f"\n📋 Creating consent...")
        print(f"   Family ID: {family_id}")
        print(f"   Scheme: {scheme_code}")
        
        consent = manager.create_consent(
            family_id=family_id,
            scheme_code=scheme_code,
            consent_value=True,
            consent_method='click',
            channel='mobile_app',
            session_id='test_session_123',
            device_id='test_device_123',
            ip_address='127.0.0.1'
        )
        
        if consent:
            print(f"\n✅ Consent created:")
            print(f"   Consent ID: {consent.get('consent_id')}")
            print(f"   Status: {consent.get('status')}")
            print(f"   Type: {consent.get('consent_type')}")
            print(f"   LOA: {consent.get('level_of_assurance')}")
        
        # Test consent status retrieval
        print(f"\n📋 Retrieving consent status...")
        status = manager.get_consent_status(family_id, scheme_code)
        
        if status:
            print(f"✅ Consent status found:")
            print(f"   Status: {status.get('status')}")
            print(f"   Valid until: {status.get('valid_until')}")
        
        print("\n" + "=" * 80)
        print("✅ Consent test complete!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error during consent test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        manager.disconnect()


if __name__ == '__main__':
    test_consent()

