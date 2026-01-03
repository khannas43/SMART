# NLP Criteria Extraction API Documentation

**Use Case ID:** AI-PLATFORM-03  
**Feature:** Eligibility Criteria Extraction from Natural Language  
**API Version:** 1.0  
**Created:** 2024-12-30

---

## Overview

This document describes the REST API endpoints for extracting structured eligibility rules from natural language scheme criteria using a fine-tuned BERT/RoBERTa model.

---

## Base URL

```
http://localhost:8080/api/v1/admin/rules
```

---

## Authentication

All endpoints require authentication. Include JWT token in Authorization header:

```
Authorization: Bearer <token>
```

---

## Endpoints

### 1. Extract Criteria

Extract structured eligibility rules from natural language criteria.

**Endpoint:** `POST /api/v1/admin/rules/extract-criteria`

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer <token>
```

**Request Body:**
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

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `scheme_id` | UUID | No | Scheme unique identifier |
| `scheme_code` | String | Yes | Scheme code (e.g., "PENSION_001") |
| `natural_language_criteria` | String | Yes | Eligibility criteria in natural language |
| `scheme_context` | Object | No | Additional context (category, department, etc.) |

**Response (200 OK):**
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
        "question_text_hi": "आपकी उम्र क्या है?",
        "input_type": "NUMBER",
        "required": true,
        "validation": {
          "min": 18,
          "max": 120
        },
        "prefill_from": "GOLDEN_RECORD",
        "prefill_field": "date_of_birth"
      }
    },
    {
      "rule_id": "temp_002",
      "rule_name": "Income Group - BPL",
      "rule_type": "INCOME_GROUP",
      "rule_type_category": "MANDATORY",
      "operator": "==",
      "value": "BPL",
      "rule_expression": "income_group == 'BPL'",
      "confidence": 0.92,
      "validation_status": "VALID",
      "question_config": {
        "question_text": "What is your income group?",
        "input_type": "SELECT",
        "options": [
          {"value": "BPL", "label": "Below Poverty Line (BPL)"},
          {"value": "APL", "label": "Above Poverty Line (APL)"},
          {"value": "HIGH_INCOME", "label": "High Income"}
        ],
        "required": true,
        "prefill_from": "PROFILE",
        "prefill_field": "income_band"
      }
    },
    {
      "rule_id": "temp_003",
      "rule_name": "Geography - Rajasthan",
      "rule_type": "STATE",
      "rule_type_category": "MANDATORY",
      "operator": "==",
      "value": "RAJASTHAN",
      "rule_expression": "state == 'RAJASTHAN'",
      "confidence": 0.98,
      "validation_status": "VALID",
      "question_config": {
        "question_text": "Which state do you reside in?",
        "input_type": "SELECT",
        "options": ["RAJASTHAN", "GUJARAT", "MADHYA_PRADESH"],
        "required": true
      }
    },
    {
      "rule_id": "temp_004",
      "rule_name": "Exclusion - No Prior Pension",
      "rule_type": "PRIOR_PARTICIPATION",
      "rule_type_category": "EXCLUSION",
      "operator": "NOT_EXISTS",
      "scheme_category": "PENSION",
      "rule_expression": "NOT EXISTS(prior_schemes WHERE category == 'PENSION')",
      "confidence": 0.90,
      "validation_status": "VALID",
      "question_config": {
        "question_text": "Are you currently enrolled in any other pension scheme?",
        "input_type": "BOOLEAN",
        "required": true
      }
    }
  ],
  "warnings": [],
  "suggestions": [
    "Consider adding disability criteria for additional benefits",
    "You may want to specify district-level restrictions"
  ],
  "model_version": "1.0.0",
  "extraction_time_ms": 45
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | Boolean | Whether extraction was successful |
| `scheme_code` | String | Scheme code |
| `extracted_rules` | Array | Array of extracted rules |
| `warnings` | Array | Warnings about extraction |
| `suggestions` | Array | Suggestions for improvement |
| `model_version` | String | Model version used |
| `extraction_time_ms` | Integer | Extraction time in milliseconds |

**Rule Object Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `rule_id` | String | Temporary rule ID |
| `rule_name` | String | Human-readable rule name |
| `rule_type` | String | Rule type (AGE, INCOME_GROUP, etc.) |
| `rule_type_category` | String | MANDATORY, OPTIONAL, EXCLUSION |
| `operator` | String | Operator (>=, <=, ==, etc.) |
| `value` | Any | Rule value |
| `rule_expression` | String | Executable rule expression |
| `confidence` | Float | Confidence score (0-1) |
| `validation_status` | String | VALID, INVALID, WARNING |
| `question_config` | Object | Question configuration for citizen portal |

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "INVALID_REQUEST",
  "message": "natural_language_criteria is required",
  "timestamp": "2024-12-30T12:00:00Z"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "success": false,
  "error": "EXTRACTION_FAILED",
  "message": "Model inference failed",
  "timestamp": "2024-12-30T12:00:00Z"
}
```

---

### 2. Preview Criteria

Preview how extracted criteria will appear in citizen portal.

**Endpoint:** `GET /api/v1/admin/rules/preview-criteria`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `scheme_id` | UUID | No | Scheme ID |
| `scheme_code` | String | No | Scheme code |
| `workflow_id` | UUID | No | Approval workflow ID |

**Response (200 OK):**
```json
{
  "success": true,
  "scheme_code": "PENSION_001",
  "scheme_name": "Old Age Pension",
  "preview": {
    "citizen_portal_view": {
      "questionnaire": [
        {
          "step": 1,
          "question": "What is your age?",
          "question_hi": "आपकी उम्र क्या है?",
          "input_type": "NUMBER",
          "required": true,
          "validation": {
            "min": 18,
            "max": 120
          }
        },
        {
          "step": 2,
          "question": "What is your income group?",
          "input_type": "SELECT",
          "options": [
            {"value": "BPL", "label": "Below Poverty Line (BPL)"},
            {"value": "APL", "label": "Above Poverty Line (APL)"}
          ],
          "required": true
        },
        {
          "step": 3,
          "question": "Which state do you reside in?",
          "input_type": "SELECT",
          "options": ["RAJASTHAN", "GUJARAT"],
          "required": true
        },
        {
          "step": 4,
          "question": "Are you currently enrolled in any other pension scheme?",
          "input_type": "BOOLEAN",
          "required": true
        }
      ],
      "estimated_completion_time": "2-3 minutes",
      "total_questions": 4
    },
    "rule_summary": {
      "mandatory_rules": 3,
      "optional_rules": 0,
      "exclusion_rules": 1,
      "total_rules": 4
    }
  }
}
```

---

### 3. Get Model Info

Get information about the NLP model.

**Endpoint:** `GET /api/v1/admin/rules/model-info`

**Response (200 OK):**
```json
{
  "success": true,
  "model": {
    "name": "eligibility_criteria_extractor",
    "version": "1.0.0",
    "base_model": "roberta-base",
    "training_date": "2024-12-30",
    "training_data_size": 500,
    "accuracy": 0.92,
    "f1_score": 0.89
  },
  "capabilities": {
    "supported_rule_types": [
      "AGE", "GENDER", "INCOME_GROUP", "ANNUAL_INCOME",
      "DISTRICT", "BLOCK", "VILLAGE", "STATE",
      "DISABILITY", "DISABILITY_TYPE", "DISABILITY_PERCENTAGE",
      "FAMILY_SIZE", "CATEGORY", "RATION_CARD",
      "LAND_OWNERSHIP", "PROPERTY_OWNERSHIP",
      "PRIOR_PARTICIPATION", "EDUCATION_LEVEL",
      "EMPLOYMENT_STATUS", "MARITAL_STATUS"
    ],
    "supported_operators": [
      ">=", "<=", "==", "!=", "IN", "NOT_IN", "BETWEEN"
    ]
  }
}
```

---

## Rule Types

### Supported Rule Types

| Rule Type | Description | Example Value |
|-----------|-------------|---------------|
| `AGE` | Age requirement | 60 (number) |
| `GENDER` | Gender requirement | "MALE", "FEMALE", "OTHER" |
| `INCOME_GROUP` | Income group | "BPL", "APL", "HIGH_INCOME" |
| `ANNUAL_INCOME` | Annual income threshold | 50000 (number) |
| `DISTRICT` | District restriction | "JAIPUR", "UDAIPUR" |
| `BLOCK` | Block restriction | "BLOCK_001" |
| `VILLAGE` | Village restriction | "VILLAGE_001" |
| `STATE` | State restriction | "RAJASTHAN" |
| `DISABILITY` | Disability status | true/false |
| `DISABILITY_TYPE` | Disability type | "PHYSICAL", "MENTAL" |
| `DISABILITY_PERCENTAGE` | Disability percentage | 40 (number) |
| `FAMILY_SIZE` | Family size requirement | 4 (number) |
| `CATEGORY` | Caste category | "SC", "ST", "OBC", "GENERAL" |
| `RATION_CARD` | Ration card requirement | true/false |
| `LAND_OWNERSHIP` | Land ownership | true/false |
| `PROPERTY_OWNERSHIP` | Property ownership | true/false |
| `PRIOR_PARTICIPATION` | Prior scheme participation | Scheme category |
| `EDUCATION_LEVEL` | Education requirement | "PRIMARY", "SECONDARY" |
| `EMPLOYMENT_STATUS` | Employment status | "UNEMPLOYED", "EMPLOYED" |
| `MARITAL_STATUS` | Marital status | "SINGLE", "MARRIED", "WIDOWED" |

---

## Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Invalid request parameters |
| `MISSING_CRITERIA` | 400 | Natural language criteria missing |
| `EXTRACTION_FAILED` | 500 | Model extraction failed |
| `MODEL_NOT_LOADED` | 500 | Model not loaded |
| `VALIDATION_FAILED` | 400 | Rule validation failed |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Insufficient permissions |

---

## Rate Limiting

- **Rate Limit:** 100 requests per minute per user
- **Burst:** 10 requests per second
- **Headers:**
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset time (Unix timestamp)

---

## Examples

### cURL Example

```bash
curl -X POST http://localhost:8080/api/v1/admin/rules/extract-criteria \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "scheme_code": "PENSION_001",
    "natural_language_criteria": "Citizen must be 60+ years old, below poverty line, resident of Rajasthan"
  }'
```

### Python Example

```python
import requests

url = "http://localhost:8080/api/v1/admin/rules/extract-criteria"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer <token>"
}
data = {
    "scheme_code": "PENSION_001",
    "natural_language_criteria": "Citizen must be 60+ years old, below poverty line, resident of Rajasthan"
}

response = requests.post(url, json=data, headers=headers)
result = response.json()

print(f"Extracted {len(result['extracted_rules'])} rules")
for rule in result['extracted_rules']:
    print(f"- {rule['rule_name']}: {rule['rule_expression']}")
```

### Java Example

```java
RestTemplate restTemplate = new RestTemplate();

HttpHeaders headers = new HttpHeaders();
headers.setContentType(MediaType.APPLICATION_JSON);
headers.setBearerAuth(token);

ExtractCriteriaRequest request = new ExtractCriteriaRequest();
request.setSchemeCode("PENSION_001");
request.setNaturalLanguageCriteria("Citizen must be 60+ years old, below poverty line, resident of Rajasthan");

HttpEntity<ExtractCriteriaRequest> entity = new HttpEntity<>(request, headers);

ResponseEntity<ExtractCriteriaResponse> response = restTemplate.postForEntity(
    "http://localhost:8080/api/v1/admin/rules/extract-criteria",
    entity,
    ExtractCriteriaResponse.class
);

ExtractCriteriaResponse result = response.getBody();
System.out.println("Extracted " + result.getExtractedRules().size() + " rules");
```

---

## Integration with Departmental Portal

### Workflow

1. **User enters criteria** in scheme builder form
2. **Frontend calls API** with natural language criteria
3. **API returns extracted rules** with confidence scores
4. **User reviews/edits** extracted rules
5. **User approves** rules → Stored in `smart_dept.scheme_eligibility_rules`
6. **Rules synced** to `smart_warehouse` for execution

### Frontend Integration

```typescript
// Extract criteria
const extractCriteria = async (criteria: string) => {
  const response = await fetch('/api/v1/admin/rules/extract-criteria', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      scheme_code: schemeCode,
      natural_language_criteria: criteria
    })
  });
  
  const result = await response.json();
  return result.extracted_rules;
};

// Preview criteria
const previewCriteria = async (schemeCode: string) => {
  const response = await fetch(
    `/api/v1/admin/rules/preview-criteria?scheme_code=${schemeCode}`
  );
  return await response.json();
};
```

---

## Performance

### Expected Performance

- **Response Time:** <100ms (P50), <200ms (P95)
- **Throughput:** 100+ requests/second
- **Accuracy:** >90% rule extraction accuracy

### Optimization Tips

1. **Batch Processing:** Process multiple schemes in one request
2. **Caching:** Cache common patterns
3. **Model Optimization:** Use quantized model for faster inference

---

## Versioning

API version is included in the URL path: `/api/v1/...`

Future versions will use `/api/v2/...` while maintaining backward compatibility for v1.

---

**Document Version:** 1.0  
**Last Updated:** 2024-12-30  
**Status:** 📚 API Documentation

