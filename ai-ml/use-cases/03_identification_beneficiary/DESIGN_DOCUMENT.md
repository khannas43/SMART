# Design Document: Auto Identification of Beneficiaries

**Use Case ID:** AI-PLATFORM-03  
**Version:** 1.0  
**Quick Reference Summary**

---

## Overview

Automatically identifies citizens/families potentially eligible for 157+ welfare schemes using rule-based + ML hybrid approach.

## Key Components

### 1. Rule Engine
- **Deterministic** eligibility evaluation
- **8 rule types**: Age, Income, Gender, Geography, Disability, Category, Household, Prior Participation
- **Output**: RULE_ELIGIBLE, NOT_ELIGIBLE, POSSIBLE_ELIGIBLE
- **Explainability**: Rule path generation

### 2. ML Scorer
- **XGBoost** classifier per scheme
- **Features**: Demographics, household, income, education, employment, prior participation
- **Output**: Eligibility probability (0-1) + confidence
- **Explainability**: SHAP values

### 3. Hybrid Evaluator
- **Combines** rule engine + ML scorer
- **Weights**: 60% rule, 40% ML (configurable)
- **Conflict Resolution**: Conservative (rules take precedence)
- **Output**: Final status with explanations

### 4. Prioritizer
- **Ranking** by priority score
- **Factors**: Eligibility score, vulnerability, under-coverage, geography
- **Output**: Ranked candidate lists, citizen hints, worklists

## Evaluation Modes

1. **Batch** (Weekly, 2 AM)
   - Full JRDR scan
   - Progress tracking
   - Error handling

2. **Event-Driven** (On family changes)
   - Age threshold crossed
   - New child added
   - Disability registered
   - Income band changed
   - etc.

3. **On-Demand** (API calls)
   - Real-time evaluation
   - <200ms latency target

## APIs

- `POST /eligibility/evaluate` - On-demand evaluation
- `GET /eligibility/precomputed` - Cached results
- `GET /eligibility/citizen-hints` - Top N schemes
- `GET /eligibility/candidate-list` - Departmental worklists
- `POST /eligibility/candidate-list/batch` - Trigger batch
- `GET /eligibility/config/scheme/{scheme_id}` - Scheme config

## Data Sources

- **Golden Records** (AI-PLATFORM-01): Demographics, family structure
- **360° Profiles** (AI-PLATFORM-02): Income band, vulnerability, under-coverage
- **JRDR**: Master household data
- **Departmental Systems**: Scheme rules, beneficiaries, historical data

## Success Metrics

- **Coverage**: 85% of eligible non-enrolled identified (recall)
- **Precision**: 90% of identified confirmed eligible
- **False Positive Rate**: <1%
- **Batch Completion**: <6 hours
- **API Latency**: <200ms

## Files Created

- **Python**: 10 files (2,500+ lines)
- **Java**: 4 files (400+ lines)
- **Database**: 12+ tables
- **Documentation**: 10+ files

---

**Full Details**: See `docs/TECHNICAL_DESIGN.md` (1,096 lines)

