"""
Test Validation Engine
Tests application validation
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))
from validation_engine import ValidationEngine


def test_validation():
    """Test validation for an application"""
    print("=" * 80)
    print("Testing Validation Engine")
    print("=" * 80)
    
    validator = ValidationEngine()
    
    try:
        validator.connect()
        
        # Find an application with mapped fields
        print("\n📋 Finding application to validate...")
        
        query = """
            SELECT a.application_id, a.scheme_code
            FROM application.applications a
            WHERE EXISTS (
                SELECT 1 FROM application.application_fields af
                WHERE af.application_id = a.application_id
            )
            ORDER BY a.created_at DESC
            LIMIT 1
        """
        
        cursor = validator.db.connection.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        cursor.close()
        
        if not row:
            print("   ⚠️  No applications with mapped fields found")
            print("   Please run test_form_mapping.py first")
            return
        
        application_id, scheme_code = row
        print(f"   ✅ Found application:")
        print(f"      Application ID: {application_id}")
        print(f"      Scheme: {scheme_code}")
        
        # Test validation
        print(f"\n🔍 Validating application...")
        result = validator.validate_application(
            application_id=application_id,
            scheme_code=scheme_code
        )
        
        print(f"\n📊 Validation Results:")
        print(f"   Valid: {result['is_valid']}")
        print(f"   Errors: {len(result['errors'])}")
        print(f"   Warnings: {len(result['warnings'])}")
        print(f"   Passed Checks: {len(result['passed_checks'])}")
        print(f"   Failed Checks: {len(result['failed_checks'])}")
        
        if result['errors']:
            print(f"\n   ❌ Errors:")
            for error in result['errors'][:5]:
                print(f"      - {error.get('field_name', 'N/A')}: {error.get('error_message', 'N/A')}")
        
        if result['warnings']:
            print(f"\n   ⚠️  Warnings:")
            for warning in result['warnings'][:5]:
                print(f"      - {warning.get('field_name', 'N/A')}: {warning.get('message', 'N/A')}")
        
        if result['is_valid']:
            print(f"\n✅ Application validation passed!")
        else:
            print(f"\n❌ Application validation failed")
        
        print("\n" + "=" * 80)
        print("✅ Validation test complete!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        validator.disconnect()


if __name__ == '__main__':
    test_validation()

