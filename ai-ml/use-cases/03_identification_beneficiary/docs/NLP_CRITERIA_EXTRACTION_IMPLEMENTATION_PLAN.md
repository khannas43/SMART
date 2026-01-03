# NLP Criteria Extraction - Implementation Plan

**Use Case ID:** AI-PLATFORM-03  
**Feature:** Dynamic Eligibility Criteria Extraction from Natural Language  
**Model:** Fine-tuned BERT/RoBERTa  
**Training Data:** 500+ dummy schemes  
**Status:** 🚧 Implementation Plan  
**Created:** 2024-12-30

---

## Executive Summary

This document outlines the complete implementation plan for adding NLP-based eligibility criteria extraction capability to AI-PLATFORM-03. The system will extract structured eligibility rules from natural language scheme definitions using a fine-tuned BERT/RoBERTa model trained on 500+ dummy schemes.

### Key Objectives

1. **Extract structured rules** from natural language eligibility criteria
2. **Train custom BERT/RoBERTa model** on 500+ schemes
3. **Integrate with existing rule engine** for validation
4. **Provide API endpoints** for departmental portal integration
5. **Support approval workflow** for extracted rules

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│         Departmental Portal - Scheme Builder               │
│  • User enters natural language criteria                    │
│  • Calls: POST /api/v1/admin/rules/extract-criteria         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│         AI-PLATFORM-03: Criteria Extraction Service         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. NLP Model (Fine-tuned BERT/RoBERTa)              │  │
│  │  2. Rule Extraction & Structuring                    │  │
│  │  3. Rule Validation                                  │  │
│  │  4. Confidence Scoring                               │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│         Response: Extracted Rules (JSON)                     │
│  • Structured rules with confidence scores                  │
│  • Validation status                                        │
│  • Suggestions and warnings                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: Data Generation & Preparation (Week 1-2)

**Objective:** Generate 500+ dummy schemes with natural language criteria and structured rules

**Tasks:**
1. ✅ Create data generation script/template
2. ✅ Generate 500+ schemes using AI (Cursor/Perplexity/Claude)
3. ✅ Validate and clean generated data
4. ✅ Split into train/validation/test sets (70/15/15)

**Deliverables:**
- `data/training/schemes_raw.json` - Raw generated schemes
- `data/training/schemes_processed.json` - Processed and validated
- `data/training/train.json` - Training set (350 schemes)
- `data/training/val.json` - Validation set (75 schemes)
- `data/training/test.json` - Test set (75 schemes)

**See:** `NLP_DATA_GENERATION_GUIDE.md`

---

### Phase 2: Model Development (Week 3-4)

**Objective:** Develop and train fine-tuned BERT/RoBERTa model

**Tasks:**
1. ✅ Set up model architecture
2. ✅ Implement data preprocessing pipeline
3. ✅ Train initial model
4. ✅ Evaluate and tune hyperparameters
5. ✅ Save best model to MLflow

**Deliverables:**
- `src/services/criteria_extractor.py` - Main extraction service
- `src/models/nlp_criteria_model.py` - Model architecture
- `src/utils/nlp_preprocessing.py` - Data preprocessing
- `config/nlp_model_config.yaml` - Model configuration
- Trained model in MLflow registry

**See:** `NLP_MODEL_TRAINING_GUIDE.md`

---

### Phase 3: Integration & API Development (Week 5-6)

**Objective:** Integrate NLP model with existing rule engine and create APIs

**Tasks:**
1. ✅ Integrate with rule validation
2. ✅ Create Spring Boot controller
3. ✅ Implement confidence scoring
4. ✅ Add error handling and fallbacks
5. ✅ Unit and integration tests

**Deliverables:**
- `spring_boot/controller/RuleExtractionController.java`
- `spring_boot/service/RuleExtractionService.java`
- `spring_boot/dto/ExtractCriteriaRequest.java`
- `spring_boot/dto/ExtractCriteriaResponse.java`
- Integration tests

---

### Phase 4: Testing & Validation (Week 7)

**Objective:** Comprehensive testing and validation

**Tasks:**
1. ✅ Test on real scheme examples
2. ✅ Validate rule extraction accuracy
3. ✅ Performance testing
4. ✅ Edge case handling
5. ✅ Documentation

**Deliverables:**
- Test results report
- Performance benchmarks
- API documentation
- User guide

---

### Phase 5: Deployment & Monitoring (Week 8)

**Objective:** Deploy to production and set up monitoring

**Tasks:**
1. ✅ Deploy model to production
2. ✅ Set up monitoring and logging
3. ✅ Create admin dashboard (optional)
4. ✅ User training and documentation

**Deliverables:**
- Production deployment
- Monitoring dashboard
- User documentation
- Training materials

---

## Technical Architecture

### 1. Model Architecture

**Base Model:** `roberta-base` (or `bert-base-uncased`)

**Task:** Named Entity Recognition (NER) + Sequence Classification

**Output Format:**
```json
{
  "rules": [
    {
      "rule_type": "AGE",
      "operator": ">=",
      "value": 60,
      "rule_expression": "age >= 60",
      "confidence": 0.95
    }
  ]
}
```

**Model Structure:**
```
Input: Natural Language Text
  ↓
Tokenization (RoBERTa Tokenizer)
  ↓
BERT/RoBERTa Encoder
  ↓
NER Head (Rule Type Detection)
  ↓
Value Extraction Head (Rule Values)
  ↓
Rule Expression Generator
  ↓
Output: Structured Rules
```

### 2. File Structure

```
ai-ml/use-cases/03_identification_beneficiary/
├── src/
│   ├── services/
│   │   └── criteria_extractor.py          # Main extraction service
│   ├── models/
│   │   └── nlp_criteria_model.py          # Model architecture
│   └── utils/
│       ├── nlp_preprocessing.py           # Data preprocessing
│       └── rule_expression_generator.py   # Rule expression builder
├── data/
│   └── training/
│       ├── schemes_raw.json
│       ├── schemes_processed.json
│       ├── train.json
│       ├── val.json
│       └── test.json
├── config/
│   └── nlp_model_config.yaml              # Model configuration
├── scripts/
│   ├── generate_training_data.py          # Data generation script
│   ├── train_nlp_model.py                 # Training script
│   └── evaluate_nlp_model.py              # Evaluation script
├── spring_boot/
│   ├── controller/
│   │   └── RuleExtractionController.java
│   ├── service/
│   │   └── RuleExtractionService.java
│   └── dto/
│       ├── ExtractCriteriaRequest.java
│       └── ExtractCriteriaResponse.java
└── docs/
    ├── NLP_CRITERIA_EXTRACTION_IMPLEMENTATION_PLAN.md (this file)
    ├── NLP_DATA_GENERATION_GUIDE.md
    ├── NLP_MODEL_TRAINING_GUIDE.md
    └── NLP_API_DOCUMENTATION.md
```

---

## Data Requirements

### Training Data Format

Each training example should contain:

```json
{
  "scheme_id": "PENSION_001",
  "scheme_name": "Old Age Pension",
  "scheme_category": "PENSION",
  "natural_language_criteria": "Citizen must be 60+ years old, below poverty line, resident of Rajasthan, and have no other pension scheme",
  "extracted_rules": [
    {
      "rule_type": "AGE",
      "operator": ">=",
      "value": 60,
      "rule_expression": "age >= 60",
      "rule_type_category": "MANDATORY",
      "confidence": 1.0
    },
    {
      "rule_type": "INCOME_GROUP",
      "operator": "==",
      "value": "BPL",
      "rule_expression": "income_group == 'BPL'",
      "rule_type_category": "MANDATORY",
      "confidence": 1.0
    },
    {
      "rule_type": "GEOGRAPHY",
      "operator": "==",
      "value": "RAJASTHAN",
      "rule_expression": "state == 'RAJASTHAN'",
      "rule_type_category": "MANDATORY",
      "confidence": 1.0
    },
    {
      "rule_type": "PRIOR_PARTICIPATION",
      "operator": "NOT_EXISTS",
      "scheme_category": "PENSION",
      "rule_expression": "NOT EXISTS(prior_schemes WHERE category == 'PENSION')",
      "rule_type_category": "EXCLUSION",
      "confidence": 0.9
    }
  ]
}
```

### Rule Types to Support

1. **AGE** - Age requirements (min/max/range)
2. **GENDER** - Gender requirements
3. **INCOME_GROUP** - BPL/APL/High Income
4. **ANNUAL_INCOME** - Income thresholds
5. **DISTRICT** - District-level restrictions
6. **BLOCK** - Block-level restrictions
7. **VILLAGE** - Village-level restrictions
8. **STATE** - State-level restrictions
9. **DISABILITY** - Disability status
10. **DISABILITY_TYPE** - Specific disability types
11. **DISABILITY_PERCENTAGE** - Disability percentage
12. **FAMILY_SIZE** - Family size requirements
13. **CATEGORY** - SC/ST/OBC/General
14. **RATION_CARD** - Ration card requirements
15. **LAND_OWNERSHIP** - Land ownership requirements
16. **PROPERTY_OWNERSHIP** - Property ownership
17. **PRIOR_PARTICIPATION** - Prior scheme participation
18. **EDUCATION_LEVEL** - Education requirements
19. **EMPLOYMENT_STATUS** - Employment requirements
20. **MARITAL_STATUS** - Marital status requirements

---

## API Design

### 1. Extract Criteria API

**Endpoint:** `POST /api/v1/admin/rules/extract-criteria`

**Request:**
```json
{
  "scheme_id": "uuid",
  "scheme_code": "PENSION_001",
  "natural_language_criteria": "Citizen must be 60+ years old, below poverty line, resident of Rajasthan, and have no other pension scheme",
  "scheme_context": {
    "category": "PENSION",
    "department": "SOCIAL_WELFARE",
    "benefit_type": "CASH"
  }
}
```

**Response:**
```json
{
  "success": true,
  "scheme_code": "PENSION_001",
  "extracted_rules": [
    {
      "rule_id": "temp_001",
      "rule_name": "Age Requirement - 60+",
      "rule_type": "AGE",
      "rule_type_category": "MANDATORY",
      "operator": ">=",
      "value": 60,
      "rule_expression": "age >= 60",
      "confidence": 0.95,
      "validation_status": "VALID",
      "question_config": {
        "question_text": "What is your age?",
        "input_type": "NUMBER",
        "required": true,
        "validation": {
          "min": 18,
          "max": 120
        }
      }
    }
  ],
  "warnings": [],
  "suggestions": [
    "Consider adding disability criteria for additional benefits"
  ],
  "model_version": "1.0.0",
  "extraction_time_ms": 45
}
```

### 2. Preview Criteria API

**Endpoint:** `GET /api/v1/admin/rules/preview-criteria?scheme_id={id}`

**Response:**
```json
{
  "scheme_code": "PENSION_001",
  "preview": {
    "citizen_portal_view": {
      "questionnaire": [
        {
          "step": 1,
          "question": "What is your age?",
          "input_type": "NUMBER",
          "required": true
        }
      ],
      "estimated_completion_time": "2-3 minutes",
      "total_questions": 4
    },
    "rule_summary": {
      "mandatory_rules": 3,
      "optional_rules": 0,
      "exclusion_rules": 1
    }
  }
}
```

---

## Model Training Details

### Hyperparameters

```yaml
model:
  base_model: "roberta-base"  # or "bert-base-uncased"
  max_length: 512
  learning_rate: 2e-5
  batch_size: 16
  num_epochs: 10
  warmup_steps: 100
  weight_decay: 0.01
  gradient_accumulation_steps: 2

training:
  train_split: 0.7
  val_split: 0.15
  test_split: 0.15
  early_stopping_patience: 3
  save_best_model: true
```

### Training Metrics

- **Accuracy:** Target >90%
- **Precision:** Target >85%
- **Recall:** Target >85%
- **F1-Score:** Target >85%
- **Rule-level Accuracy:** Target >95%

---

## Integration Points

### 1. Rule Engine Integration

- Extracted rules validated against existing rule types
- Rule expressions validated for syntax
- Conflicts detected and reported

### 2. Database Integration

- Extracted rules stored in `smart_dept.scheme_eligibility_rules` (approval workflow)
- Approved rules synced to `smart_warehouse.eligibility.scheme_eligibility_rules`

### 3. MLflow Integration

- Model versioning and tracking
- Experiment tracking
- Model registry for production deployment

---

## Performance Requirements

### Response Time
- **Target:** <100ms per extraction
- **Acceptable:** <200ms per extraction

### Throughput
- **Target:** 100+ extractions per second
- **Acceptable:** 50+ extractions per second

### Accuracy
- **Target:** >90% rule extraction accuracy
- **Target:** >95% rule type classification accuracy

---

## Security & Privacy

### Data Privacy
- All processing happens on-premise
- No data sent to external services
- Model trained on dummy/synthetic data

### Access Control
- API requires admin authentication
- Role-based access control
- Audit logging for all extractions

---

## Monitoring & Observability

### Metrics to Track
1. **Extraction Accuracy:** % of correctly extracted rules
2. **Confidence Scores:** Distribution of confidence scores
3. **Response Time:** P50, P95, P99 latencies
4. **Error Rate:** % of failed extractions
5. **Model Performance:** F1, Precision, Recall

### Logging
- All extraction requests logged
- Low-confidence extractions flagged
- Errors logged with full context

---

## Success Criteria

### Phase 1: Data Generation ✅
- [ ] 500+ schemes generated
- [ ] Data validated and cleaned
- [ ] Train/val/test splits created

### Phase 2: Model Development ✅
- [ ] Model trained with >90% accuracy
- [ ] Model saved to MLflow
- [ ] Evaluation metrics documented

### Phase 3: Integration ✅
- [ ] API endpoints implemented
- [ ] Integration tests passing
- [ ] Documentation complete

### Phase 4: Testing ✅
- [ ] Test on 50+ real schemes
- [ ] Accuracy >90%
- [ ] Performance targets met

### Phase 5: Deployment ✅
- [ ] Production deployment complete
- [ ] Monitoring set up
- [ ] User training completed

---

## Risk Mitigation

### Risk 1: Low Model Accuracy
**Mitigation:**
- Start with rule-based extraction as fallback
- Use active learning to improve over time
- Manual review for low-confidence extractions

### Risk 2: Training Data Quality
**Mitigation:**
- Multiple validation passes
- Domain expert review
- Automated validation checks

### Risk 3: Performance Issues
**Mitigation:**
- Model optimization (quantization, pruning)
- Caching for common patterns
- Batch processing support

---

## Next Steps

1. **Immediate:** Generate 500+ training schemes (see `NLP_DATA_GENERATION_GUIDE.md`)
2. **Week 3:** Start model development
3. **Week 5:** Begin API integration
4. **Week 7:** Start testing phase
5. **Week 8:** Production deployment

---

## References

- `NLP_DATA_GENERATION_GUIDE.md` - Data generation instructions
- `NLP_MODEL_TRAINING_GUIDE.md` - Model training guide
- `NLP_API_DOCUMENTATION.md` - API documentation
- `TECHNICAL_DESIGN.md` - Overall technical design
- `RULE_MANAGEMENT.md` - Rule management documentation

---

**Document Version:** 1.0  
**Last Updated:** 2024-12-30  
**Status:** 🚧 Implementation Plan - Ready to Execute

