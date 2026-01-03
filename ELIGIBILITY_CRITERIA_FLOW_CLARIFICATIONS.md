# Eligibility Criteria Flow - Clarifications & Validations

**Created:** 2024-12-30  
**Purpose:** Direct answers to 4 key questions about eligibility criteria flow  
**Related:** DYNAMIC_ELIGIBILITY_CRITERIA_SOLUTION.md

---

## Question 1: Which AI/ML Use Case or Model for NLP Extraction?

### Answer: **AI-PLATFORM-03 (Eligibility Identification)** - Enhanced with NLP extraction

### Details:

1. **Use Case:** AI-PLATFORM-03 (Eligibility Identification)
   - Already has rule engine infrastructure
   - Understands rule structure and validation
   - Natural fit for eligibility-related functionality

2. **NLP Model Options:**
   - **Option A:** GPT-4/Claude API
     - High accuracy, no training required
     - Cost per API call
     - ❌ **Not Available:** Private data center - no external API access
   - **Option B (Selected):** Fine-tuned BERT/RoBERTa ✅
     - On-premise deployment
     - No external dependencies
     - Training data: 500+ dummy schemes
     - Expected accuracy: >90%

3. **Service Location:**
   - **New Python Service:** `ai-ml/use-cases/03_identification_beneficiary/src/services/criteria_extractor.py`
   - **Spring Boot Controller:** `ai-ml/use-cases/03_identification_beneficiary/spring_boot/controller/RuleExtractionController.java`
   - **API Endpoint:** `POST /api/v1/admin/rules/extract-criteria`
   - **Database:** Uses `smart_warehouse` (same as AI-PLATFORM-03)

4. **Implementation:**
   ```java
   // Departmental Portal calls this API
   POST /api/v1/admin/rules/extract-criteria
   {
     "scheme_id": "uuid",
     "natural_language_criteria": "Citizen must be 60+ years old, BPL, resident of Rajasthan..."
   }
   
   // AI-PLATFORM-03 service:
   // 1. Uses fine-tuned BERT/RoBERTa model (on-premise)
   // 2. Extracts structured rules from natural language
   // 3. Validates against rule types
   // 4. Returns JSON with extracted rules
   ```

---

## Question 2: Rules Executed on smart_dept Schema?

### Answer: **Partially Correct** - Rules are **stored** in `smart_dept` initially, but **executed** in `smart_warehouse`

### Clarification:

1. **Storage in smart_dept:**
   ```sql
   -- smart_dept database
   CREATE TABLE schemes (
       id UUID PRIMARY KEY,
       code VARCHAR(50) UNIQUE,
       name VARCHAR(255),
       eligibility_criteria_natural_language TEXT,  -- Original input
       status VARCHAR(20)
   );

   CREATE TABLE scheme_eligibility_rules (
       id UUID PRIMARY KEY,
       scheme_id UUID REFERENCES schemes(id),
       rule_name VARCHAR(200),
       rule_type VARCHAR(50),
       rule_expression TEXT,
       extracted_by_ai BOOLEAN DEFAULT true,
       approved_by VARCHAR(100),
       approved_at TIMESTAMP,
       status VARCHAR(20)  -- PENDING, APPROVED, REJECTED
   );
   ```
   - Used for: **Approval workflow** in departmental portal
   - Purpose: Department users review/edit/approve rules

2. **Execution in smart_warehouse:**
   ```sql
   -- smart_warehouse database
   -- Schema: eligibility
   CREATE TABLE eligibility.scheme_eligibility_rules (
       rule_id SERIAL PRIMARY KEY,
       scheme_code VARCHAR(50),
       rule_expression TEXT,
       rule_type VARCHAR(50),
       is_mandatory BOOLEAN,
       priority INTEGER
   );
   ```
   - Used by: **AI-PLATFORM-03 Rule Engine** for evaluation
   - Purpose: Actual eligibility checking

3. **Flow:**
   ```
   smart_dept (storage for approval)
       ↓ ETL/CDC Sync (when approved)
   smart_warehouse (execution)
       ↓ Used by AI-PLATFORM-03
   Eligibility Evaluation
   ```

---

## Question 3: Data Flow: smart_dept → smart_warehouse → smart_citizen

### Answer: **Multi-step sync with ETL/CDC**

### Detailed Flow:

#### Step 1: smart_dept → smart_warehouse

**Trigger:** When scheme is approved in departmental portal

**Sync Method:**
- **Option A:** Event-driven (CDC) - Real-time when approved
- **Option B:** Batch sync - Daily at 00:00 UTC

**Implementation:**
```sql
-- ETL Job or CDC Connector
-- Source: smart_dept.schemes + scheme_eligibility_rules
-- Target: smart_warehouse.eligibility.scheme_master + scheme_eligibility_rules

-- Sync scheme metadata
INSERT INTO smart_warehouse.eligibility.scheme_master (
    scheme_code, scheme_name, description, category, 
    department_name, status, created_at, updated_at
)
SELECT 
    code, name, description, category, department, 
    status, created_at, updated_at
FROM smart_dept.schemes
WHERE status = 'APPROVED'  -- Only approved schemes
ON CONFLICT (scheme_code) DO UPDATE SET
    scheme_name = EXCLUDED.scheme_name,
    description = EXCLUDED.description,
    status = EXCLUDED.status,
    updated_at = EXCLUDED.updated_at;

-- Sync eligibility rules
INSERT INTO smart_warehouse.eligibility.scheme_eligibility_rules (
    scheme_code, rule_name, rule_type, rule_expression,
    rule_operator, rule_value, is_mandatory, priority,
    effective_from, effective_to
)
SELECT 
    s.code, r.rule_name, r.rule_type, r.rule_expression,
    r.rule_operator, r.rule_value, r.is_mandatory, r.priority,
    CURRENT_DATE, NULL
FROM smart_dept.scheme_eligibility_rules r
JOIN smart_dept.schemes s ON r.scheme_id = s.id
WHERE r.status = 'APPROVED'  -- Only approved rules
ON CONFLICT (scheme_code, rule_name, version) DO UPDATE SET
    rule_expression = EXCLUDED.rule_expression,
    rule_value = EXCLUDED.rule_value;
```

**Technology:**
- **CDC:** Debezium + Kafka (for real-time)
- **Batch:** Airflow ETL job (for scheduled sync)

#### Step 2: smart_warehouse → smart_citizen

**Trigger:** Daily batch sync (00:00 UTC) - As per existing data flow specification

**Sync Method:** Batch (Daily)

**Implementation:**
```sql
-- ETL Job (Daily at 00:00 UTC)
-- Source: smart_warehouse.eligibility.scheme_master
-- Target: smart_citizen.schemes

INSERT INTO smart_citizen.schemes (
    id, code, name, description, category, department,
    eligibility_criteria, status, created_at, updated_at
)
SELECT 
    scheme_id::uuid,
    scheme_code,
    scheme_name,
    description,
    category,
    department_name,
    -- Aggregate rules into JSON format for citizen portal
    jsonb_build_object(
        'rules', jsonb_agg(
            jsonb_build_object(
                'rule_name', rule_name,
                'criteria_type', rule_type,
                'question_text', question_config->>'question_text'
            )
        )
    ) as eligibility_criteria,
    status,
    created_at,
    updated_at
FROM smart_warehouse.eligibility.scheme_master sm
LEFT JOIN smart_warehouse.eligibility.scheme_eligibility_rules sr
    ON sm.scheme_code = sr.scheme_code
WHERE sm.status = 'ACTIVE'
GROUP BY sm.scheme_id, sm.scheme_code, sm.scheme_name, 
         sm.description, sm.category, sm.department_name,
         sm.status, sm.created_at, sm.updated_at
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    eligibility_criteria = EXCLUDED.eligibility_criteria,
    status = EXCLUDED.status,
    updated_at = EXCLUDED.updated_at;
```

**Note:** 
- Citizen portal gets a **read-only copy** of scheme metadata
- **Rules are NOT stored in smart_citizen** - accessed via API instead

---

## Question 4: API Placement & Automatic Usage by Citizen Portal

### Answer: **APIs in AI-PLATFORM-03, Citizen Portal calls them dynamically**

### API Architecture:

#### 1. Rule Management APIs (Departmental Portal)

**Location:** `ai-ml/use-cases/03_identification_beneficiary/spring_boot/controller/RuleExtractionController.java`

**APIs:**
```java
// Rule Extraction API
POST /api/v1/admin/rules/extract-criteria
{
  "scheme_id": "uuid",
  "natural_language_criteria": "Citizen must be 60+ years old..."
}
Response: {
  "extracted_rules": [...],
  "warnings": [],
  "suggestions": []
}

// Rule Approval API (Departmental Portal Backend)
POST /api/v1/admin/rules/approve-criteria
{
  "workflow_id": "uuid",
  "approved_rules": [...]
}

// Preview Criteria API
GET /api/v1/admin/rules/preview-criteria?scheme_id={id}
```

**Called By:** Departmental Portal Backend (Spring Boot service)

---

#### 2. Dynamic Criteria API (Citizen Portal)

**Location:** `ai-ml/use-cases/03_identification_beneficiary/spring_boot/controller/EligibilityController.java`

**API:**
```java
// Get Dynamic Criteria for Scheme
GET /api/v1/eligibility/config/scheme/{scheme_id}?include_questions=true

Response: {
  "scheme_id": "uuid",
  "scheme_code": "PENSION_001",
  "rules": [
    {
      "rule_id": 1,
      "criteria_type": "AGE",
      "question_config": {
        "question_text": "What is your age?",
        "input_type": "NUMBER",
        "required": true,
        "validation": {"min": 18, "max": 120}
      }
    }
  ]
}
```

**Called By:** Citizen Portal Frontend (React component)

---

#### 3. How Citizen Portal Uses APIs Automatically

**Implementation in EligibilityCheckerPage.tsx:**

```typescript
// Step 1: On component mount or scheme selection
useEffect(() => {
  if (selectedScheme) {
    loadDynamicCriteria(selectedScheme.id);
  }
}, [selectedScheme]);

// Step 2: Fetch dynamic criteria from AI-PLATFORM-03
const loadDynamicCriteria = async (schemeId: string) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/eligibility/config/scheme/${schemeId}?include_questions=true`
    );
    const data = await response.json();
    
    // Step 3: Generate dynamic form fields
    setDynamicCriteria(data.rules.map(rule => ({
      criteriaId: `criteria_${rule.rule_id}`,
      criteriaType: rule.criteria_type,
      questionText: rule.question_config.question_text,
      inputType: rule.question_config.input_type,
      options: rule.question_config.options,
      required: rule.question_config.required,
      validation: rule.question_config.validation
    })));
  } catch (error) {
    console.error('Failed to load dynamic criteria:', error);
    // Fallback to hardcoded 8 fields
    setUseFallbackCriteria(true);
  }
};

// Step 4: Render dynamic form fields
{dynamicCriteria.map((criteria) => (
  <FormField
    key={criteria.criteriaId}
    type={criteria.inputType}
    label={criteria.questionText}
    required={criteria.required}
    validation={criteria.validation}
    options={criteria.options}
    value={questionnaireData[criteria.criteriaId]}
    onChange={(value) => handleInputChange(criteria.criteriaId, value)}
  />
))}
```

**Automatic Behavior:**
1. ✅ **On Scheme Selection:** Automatically fetches criteria for selected scheme
2. ✅ **Dynamic Rendering:** Generates form fields based on API response
3. ✅ **Fallback:** Uses hardcoded 8 fields if API fails
4. ✅ **Real-time Updates:** Re-fetches when scheme changes

---

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Departmental Portal (smart_dept)                        │
│    • User enters natural language criteria                  │
│    • Calls: POST /api/v1/admin/rules/extract-criteria     │
│    • Stores in smart_dept.schemes + scheme_eligibility_rules│
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ ETL/CDC Sync (when approved)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. smart_warehouse (eligibility schema)                    │
│    • eligibility.scheme_master                              │
│    • eligibility.scheme_eligibility_rules                   │
│    • Used by AI-PLATFORM-03 for evaluation                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Daily Batch Sync (00:00 UTC)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. smart_citizen (public schema)                           │
│    • schemes table (read-only copy)                         │
│    • Used for scheme listing/display                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ API Call (On-demand)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Citizen Portal Eligibility Screen                      │
│    • Fetches: GET /api/v1/eligibility/config/scheme/{id}    │
│    • Generates dynamic questionnaire                        │
│    • Real-time eligibility checking                         │
└─────────────────────────────────────────────────────────────┘
```

---

## API Endpoint Summary

| API Endpoint | Method | Called By | Purpose |
|-------------|--------|-----------|---------|
| `/api/v1/admin/rules/extract-criteria` | POST | Departmental Portal | Extract rules from natural language |
| `/api/v1/admin/rules/approve-criteria` | POST | Departmental Portal | Approve extracted rules |
| `/api/v1/admin/rules/preview-criteria` | GET | Departmental Portal | Preview criteria in citizen format |
| `/api/v1/eligibility/config/scheme/{id}` | GET | Citizen Portal | Get dynamic criteria for scheme |
| `/api/v1/eligibility/check` | POST | Citizen Portal | Perform eligibility check |
| `/api/v1/eligibility/evaluate` | POST | Citizen Portal | Evaluate eligibility with ML |

---

## Database Schema Locations

| Data | Database | Schema | Table | Purpose |
|------|----------|--------|-------|---------|
| Scheme Metadata (Dept) | `smart_dept` | `public` | `schemes` | Departmental scheme management |
| Rules (Dept Approval) | `smart_dept` | `public` | `scheme_eligibility_rules` | Approval workflow |
| Scheme Master (ML) | `smart_warehouse` | `eligibility` | `scheme_master` | ML evaluation source |
| Rules (ML Execution) | `smart_warehouse` | `eligibility` | `scheme_eligibility_rules` | Rule engine execution |
| Scheme Catalog (Citizen) | `smart_citizen` | `public` | `schemes` | Citizen portal display |

---

## Key Takeaways

1. **NLP Extraction:** AI-PLATFORM-03 handles NLP extraction using GPT-4/Claude API
2. **Rule Storage:** Rules stored in `smart_dept` for approval, synced to `smart_warehouse` for execution
3. **Data Flow:** smart_dept → smart_warehouse (ETL/CDC) → smart_citizen (Daily batch)
4. **API Usage:** Citizen portal automatically calls AI-PLATFORM-03 APIs to fetch dynamic criteria on scheme selection

---

**Document Version:** 1.0  
**Status:** ✅ Complete - Ready for Implementation

