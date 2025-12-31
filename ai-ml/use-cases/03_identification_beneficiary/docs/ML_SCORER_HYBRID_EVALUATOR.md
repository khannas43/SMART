# ML Scorer & Hybrid Evaluator Implementation

**Use Case ID:** AI-PLATFORM-03  
**Components:** ML Eligibility Scorer, Hybrid Evaluator  
**Status:** ✅ Implemented

## Overview

Two core components have been implemented to enable ML-powered eligibility scoring combined with rule-based evaluation:

1. **ML Eligibility Scorer** (`src/ml_scorer.py`) - XGBoost-based ML model for probabilistic eligibility scoring
2. **Hybrid Evaluator** (`src/hybrid_evaluator.py`) - Combines rule engine + ML scorer for comprehensive evaluation

## ML Eligibility Scorer

### Features

- ✅ **Model Loading**: Loads XGBoost models from MLflow Model Registry or local files
- ✅ **Feature Preparation**: Automatically prepares features from family/member data
- ✅ **Probability Prediction**: Returns eligibility probability (0-1) and confidence scores
- ✅ **SHAP Explainability**: Provides feature importance and explanations via SHAP values
- ✅ **Model Caching**: Caches loaded models for performance
- ✅ **Versioning**: Supports model version tracking and selection

### Key Methods

```python
# Initialize scorer
scorer = MLEligibilityScorer()

# Load model for a scheme
scorer.load_model('SCHEME_001')

# Predict eligibility
result = scorer.predict(
    scheme_id='SCHEME_001',
    family_data={...},
    member_data={...},  # optional
    return_explanations=True
)

# Result contains:
# - probability: float (0-1)
# - confidence: float (0-1)
# - top_features: List[Dict] with SHAP values
# - model_version: str
```

### Configuration

Configured in `config/model_config.yaml`:
- XGBoost hyperparameters
- Feature engineering settings
- SHAP explainability options
- MLflow tracking URI

## Hybrid Evaluator

### Features

- ✅ **Rule + ML Combination**: Seamlessly combines rule engine and ML scorer results
- ✅ **Confidence Weighting**: Configurable weights for rule vs ML (default: 60% rule, 40% ML)
- ✅ **Conflict Resolution**: Business rules for handling conflicts between rule and ML results
- ✅ **Status Determination**: Produces final eligibility status (RULE_ELIGIBLE, NOT_ELIGIBLE, POSSIBLE_ELIGIBLE, UNCERTAIN)
- ✅ **Comprehensive Explanations**: Human-readable explanations combining rule path and ML insights
- ✅ **Batch Processing**: Supports evaluation of multiple families

### Key Methods

```python
# Initialize evaluator
evaluator = HybridEvaluator()

# Evaluate eligibility
result = evaluator.evaluate(
    scheme_id='SCHEME_001',
    family_data={...},
    member_data={...},  # optional
    use_ml=True  # whether to use ML scorer if available
)

# Result contains:
# - evaluation_status: str (RULE_ELIGIBLE, NOT_ELIGIBLE, etc.)
# - eligibility_score: float (0-1 combined score)
# - confidence_score: float (0-1)
# - rule_result: Dict (rule engine results)
# - ml_result: Dict (ML scorer results)
# - explanation: str (human-readable)
# - rule_path: str
# - ml_top_features: List[Dict]
```

### Conflict Resolution Strategy

The hybrid evaluator uses a **conservative approach** to prevent leakage:

1. **Rules Pass + ML Low**: Use rules (rules take precedence for safety)
2. **Rules Fail + ML High**: Require review (never auto-identify if rules fail)
3. **Agreement**: Use combined score with high confidence
4. **Mixed Signals**: Mark as POSSIBLE_ELIGIBLE for review

### Configuration

Configured in `config/use_case_config.yaml`:
- `rule_weight`: 0.6 (default)
- `ml_weight`: 0.4 (default)
- `confidence_threshold`: 0.7 (minimum for auto-identification)

## Integration Example

```python
from hybrid_evaluator import HybridEvaluator

# Initialize
evaluator = HybridEvaluator()

# Family data (from Golden Record + 360° Profile)
family_data = {
    'family_id': 'FAM-001',
    'head_age': 65,
    'head_gender': 'M',
    'district_id': 101,
    'income_band': 'LOW',
    'family_size': 4,
    'schemes_enrolled_list': [],
    'benefits_received_total_1y': 0
}

# Evaluate
result = evaluator.evaluate('SCHEME_001', family_data)

# Access results
print(f"Status: {result['evaluation_status']}")
print(f"Score: {result['eligibility_score']:.3f}")
print(f"Confidence: {result['confidence_score']:.3f}")
print(f"Explanation: {result['explanation']}")

# Access detailed results
print(f"Rules passed: {result['rules_passed']}")
if result['ml_result']:
    print(f"ML probability: {result['ml_probability']:.3f}")
    print(f"Top features: {result['ml_top_features']}")
```

## Testing

A test script is available:

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
python scripts/test_hybrid_evaluator.py
```

This script tests:
- Elderly person (likely eligible for pension)
- Young person (likely not eligible)
- Widow (potentially eligible for widow pension)

## Dependencies

- **Rule Engine**: Required for rule-based evaluation
- **ML Models**: XGBoost models per scheme (must be trained first)
- **Database**: ML model registry for model metadata
- **MLflow**: For model registry and tracking
- **SHAP**: For explainability (optional but recommended)

## Next Steps

1. **Train ML Models**: Create training pipeline to train models per scheme
2. **Load Scheme Rules**: Define eligibility rules in database
3. **Test with Real Data**: Test with Golden Records and 360° Profile data
4. **Integrate with Service**: Use in main evaluation service for batch/event-driven evaluation

## Files Created

- `src/ml_scorer.py` - ML Eligibility Scorer implementation
- `src/hybrid_evaluator.py` - Hybrid Evaluator implementation
- `scripts/test_hybrid_evaluator.py` - Test script

---

**Status**: ✅ Core functionality implemented and ready for integration

