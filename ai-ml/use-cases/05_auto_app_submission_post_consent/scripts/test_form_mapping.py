"""
Test Form Mapping
Tests the form mapping service
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))
from form_mapper import FormMapper


def test_form_mapping():
    """Test form mapping for an application"""
    print("=" * 80)
    print("Testing Form Mapping")
    print("=" * 80)
    
    mapper = FormMapper()
    
    try:
        mapper.connect()
        
        # Find an application in 'creating' status
        print("\n📋 Finding application to map...")
        
        query = """
            SELECT application_id, family_id, scheme_code, member_id
            FROM application.applications
            WHERE status = 'creating'
            ORDER BY created_at DESC
            LIMIT 1
        """
        
        cursor = mapper.db.connection.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        cursor.close()
        
        if not row:
            print("   ⚠️  No applications in 'creating' status found")
            print("   Please run test_application_creation.py first")
            return
        
        application_id, family_id, scheme_code, member_id = row
        print(f"   ✅ Found application:")
        print(f"      Application ID: {application_id}")
        print(f"      Family ID: {family_id}")
        print(f"      Scheme: {scheme_code}")
        
        # Test mapping
        print(f"\n🔄 Mapping form fields...")
        result = mapper.map_form_fields(
            application_id=application_id,
            family_id=str(family_id),
            scheme_code=scheme_code,
            member_id=str(member_id) if member_id else None
        )
        
        if result['success']:
            print(f"\n✅ Form mapping successful!")
            print(f"   Mapped fields: {result['mapped_fields_count']}")
            print(f"\n   Sample mapped fields:")
            form_data = result.get('form_data', {})
            for i, (field, value) in enumerate(list(form_data.items())[:5]):
                print(f"      {field}: {value}")
                if i >= 4:
                    break
            
            print(f"\n   Field sources:")
            sources = result.get('field_sources', {})
            for i, (field, source_info) in enumerate(list(sources.items())[:5]):
                print(f"      {field}: {source_info.get('source_type', 'UNKNOWN')}")
                if i >= 4:
                    break
        else:
            print(f"\n❌ Form mapping failed")
        
        print("\n" + "=" * 80)
        print("✅ Form mapping test complete!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        mapper.disconnect()


if __name__ == '__main__':
    test_form_mapping()

