"""
End-to-End Test
Tests the complete application workflow from consent to submission
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))
from application_orchestrator import ApplicationOrchestrator
from form_mapper import FormMapper
from validation_engine import ValidationEngine
from submission_handler import SubmissionHandler


def test_end_to_end():
    """Test complete end-to-end workflow"""
    print("=" * 80)
    print("End-to-End Application Workflow Test")
    print("=" * 80)
    
    orchestrator = ApplicationOrchestrator()
    mapper = FormMapper()
    validator = ValidationEngine()
    handler = SubmissionHandler()
    
    try:
        # Connect all services
        orchestrator.connect()
        mapper.connect()
        validator.connect()
        handler.connect()
        
        # Step 1: Find consent
        print("\n📋 Step 1: Finding consent record...")
        query = """
            SELECT DISTINCT ON (family_id, scheme_code) 
                family_id, scheme_code, consent_id, created_at
            FROM intimation.consent_records
            WHERE status = 'valid'
                AND consent_value = true
            ORDER BY family_id, scheme_code, created_at DESC
            LIMIT 1
        """
        
        cursor = orchestrator.db.connection.cursor()
        cursor.execute(query)
        consent = cursor.fetchone()
        cursor.close()
        
        if not consent:
            print("   ⚠️  No consent records found")
            print("   Please run AI-PLATFORM-04 tests first")
            return
        
        family_id, scheme_code, consent_id, created_at = consent
        print(f"   ✅ Found consent:")
        print(f"      Family ID: {family_id}")
        print(f"      Scheme: {scheme_code}")
        print(f"      Consent ID: {consent_id}")
        
        # Step 2: Trigger application creation
        print(f"\n🔄 Step 2: Triggering application creation...")
        create_result = orchestrator.trigger_on_consent(
            family_id=str(family_id),
            scheme_code=scheme_code,
            consent_id=consent_id
        )
        
        if not create_result['success']:
            print(f"   ❌ Failed to create application: {create_result.get('error')}")
            return
        
        application_id = create_result['application_id']
        print(f"   ✅ Application created: {application_id}")
        
        # Step 3: Map form fields
        print(f"\n🔄 Step 3: Mapping form fields...")
        map_result = mapper.map_form_fields(
            application_id=application_id,
            family_id=str(family_id),
            scheme_code=scheme_code
        )
        
        if not map_result['success']:
            print(f"   ❌ Form mapping failed")
            return
        
        print(f"   ✅ Mapped {map_result['mapped_fields_count']} fields")
        
        # Step 4: Validate application
        print(f"\n🔍 Step 4: Validating application...")
        validation_result = validator.validate_application(
            application_id=application_id,
            scheme_code=scheme_code
        )
        
        print(f"   Validation: {'✅ PASSED' if validation_result['is_valid'] else '❌ FAILED'}")
        print(f"   Errors: {len(validation_result['errors'])}, Warnings: {len(validation_result['warnings'])}")
        
        if not validation_result['is_valid']:
            print(f"   ⚠️  Application has validation errors, but continuing...")
        
        # Step 5: Get submission mode
        print(f"\n📤 Step 5: Determining submission mode...")
        query = """
            SELECT submission_mode, status
            FROM application.applications
            WHERE application_id = %s
        """
        
        cursor = handler.db.connection.cursor()
        cursor.execute(query, [application_id])
        row = cursor.fetchone()
        cursor.close()
        
        if row:
            submission_mode, status = row
            print(f"   Submission Mode: {submission_mode}")
            print(f"   Current Status: {status}")
            
            # Step 6: Handle submission
            if submission_mode == 'auto' and validation_result['is_valid']:
                print(f"\n🔄 Step 6: Auto-submitting application...")
                submit_result = handler.handle_submission(
                    application_id=application_id,
                    scheme_code=scheme_code,
                    submission_mode=submission_mode
                )
                
                if submit_result['success']:
                    print(f"   ✅ Submission successful!")
                    if submit_result.get('department_application_number'):
                        print(f"   Department App Number: {submit_result['department_application_number']}")
                else:
                    print(f"   ⚠️  Submission failed: {submit_result.get('error')}")
            else:
                print(f"\n📋 Step 6: Application stored for {submission_mode}")
                submit_result = handler.handle_submission(
                    application_id=application_id,
                    scheme_code=scheme_code,
                    submission_mode=submission_mode
                )
                print(f"   Status: {submit_result.get('status', 'unknown')}")
        
        # Summary
        print("\n" + "=" * 80)
        print("✅ End-to-End Test Complete!")
        print("=" * 80)
        print(f"\n📊 Summary:")
        print(f"   Application ID: {application_id}")
        print(f"   Scheme: {scheme_code}")
        print(f"   Fields Mapped: {map_result['mapped_fields_count']}")
        print(f"   Validation: {'PASSED' if validation_result['is_valid'] else 'FAILED'}")
        print(f"   Submission Mode: {submission_mode}")
        print(f"   Final Status: {status}")
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        orchestrator.disconnect()
        mapper.disconnect()
        validator.disconnect()
        handler.disconnect()


if __name__ == '__main__':
    test_end_to_end()

