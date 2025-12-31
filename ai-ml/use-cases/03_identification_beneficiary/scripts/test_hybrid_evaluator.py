#!/usr/bin/env python3
"""
Test script for Hybrid Evaluator
Demonstrates rule engine + ML scorer combination
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from hybrid_evaluator import HybridEvaluator


def main():
    """Test hybrid evaluator with sample data"""
    
    print("=" * 80)
    print("Hybrid Eligibility Evaluator Test")
    print("=" * 80)
    print()
    
    # Initialize evaluator
    print("Initializing Hybrid Evaluator...")
    evaluator = HybridEvaluator()
    print("✅ Evaluator initialized")
    print()
    
    # Test Case 1: Elderly person (likely eligible for pension)
    print("Test Case 1: Elderly Person (Age 65, Low Income)")
    print("-" * 80)
    family_data_1 = {
        'family_id': 'test-family-001',
        'head_age': 65,
        'head_gender': 'M',
        'district_id': 101,
        'caste_id': 1,
        'income_band': 'LOW',
        'family_size': 2,
        'schemes_enrolled_list': [],
        'benefits_received_total_1y': 0,
        'education_level': 'PRIMARY',
        'employment_status': 'UNEMPLOYED',
        'has_disabled_member': False
    }
    
    result_1 = evaluator.evaluate('SCHEME_001', family_data_1, use_ml=False)
    print(f"Status: {result_1['evaluation_status']}")
    print(f"Eligibility Score: {result_1['eligibility_score']:.3f}")
    print(f"Confidence: {result_1['confidence_score']:.3f}")
    print(f"Rule Path: {result_1['rule_path']}")
    print(f"Explanation: {result_1['explanation']}")
    print()
    
    # Test Case 2: Young person (likely not eligible for pension)
    print("Test Case 2: Young Person (Age 30, Medium Income)")
    print("-" * 80)
    family_data_2 = {
        'family_id': 'test-family-002',
        'head_age': 30,
        'head_gender': 'F',
        'district_id': 101,
        'caste_id': 1,
        'income_band': 'MEDIUM',
        'family_size': 4,
        'schemes_enrolled_list': [],
        'benefits_received_total_1y': 5000,
        'education_level': 'SECONDARY',
        'employment_status': 'EMPLOYED',
        'has_disabled_member': False
    }
    
    result_2 = evaluator.evaluate('SCHEME_001', family_data_2, use_ml=False)
    print(f"Status: {result_2['evaluation_status']}")
    print(f"Eligibility Score: {result_2['eligibility_score']:.3f}")
    print(f"Confidence: {result_2['confidence_score']:.3f}")
    print(f"Rule Path: {result_2['rule_path']}")
    print(f"Explanation: {result_2['explanation']}")
    print()
    
    # Test Case 3: Widow (potentially eligible for widow pension)
    print("Test Case 3: Widow (Age 45, Low Income)")
    print("-" * 80)
    family_data_3 = {
        'family_id': 'test-family-003',
        'head_age': 45,
        'head_gender': 'F',
        'district_id': 101,
        'caste_id': 1,
        'income_band': 'LOW',
        'family_size': 3,
        'schemes_enrolled_list': [],
        'benefits_received_total_1y': 0,
        'education_level': 'PRIMARY',
        'employment_status': 'UNEMPLOYED',
        'marital_status': 'WIDOW',
        'has_disabled_member': False
    }
    
    result_3 = evaluator.evaluate('SCHEME_002', family_data_3, use_ml=False)
    print(f"Status: {result_3['evaluation_status']}")
    print(f"Eligibility Score: {result_3['eligibility_score']:.3f}")
    print(f"Confidence: {result_3['confidence_score']:.3f}")
    print(f"Rule Path: {result_3['rule_path']}")
    print(f"Explanation: {result_3['explanation']}")
    print()
    
    # Summary
    print("=" * 80)
    print("Test Summary")
    print("=" * 80)
    print(f"Test Case 1: {result_1['evaluation_status']}")
    print(f"Test Case 2: {result_2['evaluation_status']}")
    print(f"Test Case 3: {result_3['evaluation_status']}")
    print()
    
    # Close connections
    evaluator.close()
    print("✅ Test completed")


if __name__ == "__main__":
    main()

