#!/usr/bin/env python3
"""
Test Decision Workflow - End-to-End Test
Tests the complete decision evaluation workflow
Use Case ID: AI-PLATFORM-06
"""

import sys
import os
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared', 'utils'))

from decision_engine import DecisionEngine


def test_decision_workflow():
    """Test complete decision evaluation workflow"""
    print("=" * 80)
    print("Testing Decision Workflow - End-to-End")
    print("=" * 80)
    
    # Initialize engine
    engine = DecisionEngine()
    engine.connect()
    
    try:
        # Find applications to test
        print("\n📋 Finding applications to evaluate...")
        applications = find_applications_to_test(engine)
        
        if not applications:
            print("\n⚠️  No applications found to test")
            print("   Please create some applications in AI-PLATFORM-05 first")
            return
        
        print(f"   ✅ Found {len(applications)} application(s) to test\n")
        
        # Test each application
        results = []
        for i, app in enumerate(applications, 1):
            print(f"\n{'=' * 80}")
            print(f"Test {i}/{len(applications)}: Application ID {app['application_id']}")
            print(f"{'=' * 80}")
            print(f"Family ID: {app['family_id']}")
            print(f"Scheme: {app['scheme_code']}")
            print(f"Status: {app['status']}")
            
            try:
                # Evaluate application
                result = engine.evaluate_application(
                    application_id=app['application_id'],
                    family_id=app['family_id'],
                    scheme_code=app['scheme_code']
                )
                
                if result['success']:
                    decision = result['decision']
                    print(f"\n✅ Decision Evaluation Complete!")
                    print(f"   Decision ID: {result['decision_id']}")
                    print(f"   Decision Type: {decision['decision_type']}")
                    print(f"   Decision Status: {decision['decision_status']}")
                    print(f"   Risk Score: {decision['risk_score']:.4f}")
                    print(f"   Risk Band: {decision['risk_band']}")
                    print(f"   Reason: {decision.get('reason', 'N/A')}")
                    
                    # Rule results
                    rule_results = result['rule_results']
                    print(f"\n📊 Rule Evaluation:")
                    print(f"   All Passed: {rule_results['all_passed']}")
                    print(f"   Passed: {rule_results['passed_count']}")
                    print(f"   Failed: {rule_results['failed_count']}")
                    if rule_results['critical_failures']:
                        print(f"   Critical Failures: {', '.join(rule_results['critical_failures'])}")
                    
                    # Risk results
                    risk_results = result['risk_results']
                    print(f"\n🎯 Risk Assessment:")
                    print(f"   Score: {risk_results['risk_score']:.4f}")
                    print(f"   Band: {risk_results['risk_band']}")
                    print(f"   Model: {risk_results['model_type']} v{risk_results['model_version']}")
                    if risk_results['top_factors']:
                        print(f"   Top Factors:")
                        for factor in risk_results['top_factors']:
                            print(f"     - {factor}")
                    
                    # Routing
                    routing = result['routing']
                    print(f"\n🚦 Routing:")
                    print(f"   Action: {routing['action']}")
                    print(f"   Status: {routing['status']}")
                    print(f"   Message: {routing.get('message', 'N/A')}")
                    
                    results.append({
                        'application_id': app['application_id'],
                        'success': True,
                        'decision_type': decision['decision_type'],
                        'risk_score': decision['risk_score']
                    })
                else:
                    print(f"\n❌ Decision Evaluation Failed!")
                    print(f"   Error: {result.get('error', 'Unknown error')}")
                    results.append({
                        'application_id': app['application_id'],
                        'success': False,
                        'error': result.get('error', 'Unknown error')
                    })
            
            except Exception as e:
                print(f"\n❌ Error evaluating application: {e}")
                import traceback
                traceback.print_exc()
                results.append({
                    'application_id': app['application_id'],
                    'success': False,
                    'error': str(e)
                })
        
        # Summary
        print(f"\n{'=' * 80}")
        print("Test Summary")
        print(f"{'=' * 80}")
        successful = sum(1 for r in results if r.get('success', False))
        failed = len(results) - successful
        print(f"Total Applications: {len(results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        
        if successful > 0:
            print(f"\nDecision Types:")
            decision_types = {}
            for r in results:
                if r.get('success'):
                    dt = r.get('decision_type', 'UNKNOWN')
                    decision_types[dt] = decision_types.get(dt, 0) + 1
            
            for dt, count in decision_types.items():
                print(f"  {dt}: {count}")
        
        print(f"\n{'=' * 80}")
        print("✅ Test Complete!")
        print(f"{'=' * 80}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        engine.disconnect()


def find_applications_to_test(engine):
    """Find applications to test from application schema"""
    try:
        conn = engine.external_dbs['application'].connection
        cursor = conn.cursor()
        
        # Find applications that are submitted or pending
        cursor.execute("""
            SELECT 
                application_id, family_id, scheme_code, status,
                eligibility_score, eligibility_status
            FROM application.applications
            WHERE status IN ('submitted', 'pending_submission', 'draft')
            ORDER BY created_at DESC
            LIMIT 5
        """)
        
        rows = cursor.fetchall()
        cursor.close()
        
        applications = []
        for row in rows:
            applications.append({
                'application_id': row[0],
                'family_id': row[1],
                'scheme_code': row[2],
                'status': row[3],
                'eligibility_score': row[4],
                'eligibility_status': row[5]
            })
        
        return applications
    
    except Exception as e:
        print(f"   ⚠️  Error finding applications: {e}")
        return []


if __name__ == '__main__':
    test_decision_workflow()

