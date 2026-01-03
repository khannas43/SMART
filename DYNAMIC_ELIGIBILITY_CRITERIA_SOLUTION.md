# Dynamic Eligibility Criteria Solution

**Purpose:** Solution for dynamic, AI/ML-driven eligibility criteria extraction and management  
**Created:** 2024-12-30  
**Status:** Proposal  
**Related:** CITIZEN_PORTAL_AI_ML_MAPPING.md, Scheme Builder (Departmental Portal)

---

## Current State Analysis

### Frontend Implementation (Citizen Portal)

**Current Eligibility Criteria Fields (Hardcoded - 8 points):**
1. Age
2. Gender
3. Income Group
4. District
5. Disability
6. Annual Income
7. Family Size
8. Do you have Ration Card

**Location:** `portals/citizen/frontend/src/pages/schemes/EligibilityCheckerPage.tsx`

**Limitations:**
- ❌ Hardcoded criteria fields (not dynamic)
- ❌ Cannot adapt to new schemes automatically
- ❌ No integration with AI/ML rule extraction
- ❌ No departmental approval workflow
- ❌ Limited to 8 predefined fields

---

## AI/ML Use Cases for Eligibility Checking

### Primary Use Cases

#### 1. AI-PLATFORM-03: Eligibility Identification ✅

**Purpose:** Auto-identify eligible beneficiaries using rule-based + ML evaluation

**Key Capabilities:**
- **Rule Engine:** Supports 8+ rule types:
  - Age rules (min/max age, age ranges)
  - Gender rules (male/female/other/any)
  - Income rules (BPL/APL, income thresholds, income bands)
  - Geography rules (district, block, village, state)
  - Disability rules (disability type, percentage)
  - Category rules (SC/ST/OBC/General)
  - Prior participation rules (exclusions)
  - Asset rules (land ownership, property)
- **ML Scorer:** XGBoost models per scheme for probabilistic scoring
- **Hybrid Evaluator:** Combines rule engine + ML scores
- **Explainability:** Rule paths, SHAP values

**API Endpoints:**
```java
POST /api/v1/eligibility/evaluate?family_id={id}&scheme_ids={list}
GET  /api/v1/eligibility/config/scheme/{scheme_id}  // Returns scheme rules
```

**Rule Storage:**
- Database: `eligibility.eligibility_rules` table
- Fields: `rule_id`, `scheme_code`, `rule_name`, `rule_expression`, `rule_type`, `priority`, `active`

**Current Rule Types Supported:**
- MANDATORY (must pass)
- OPTIONAL (nice to have)
- EXCLUSION (disqualifies if true)

---

#### 2. AI-PLATFORM-08: Eligibility Checker ✅

**Purpose:** Real-time eligibility checking with questionnaire support

**Key Capabilities:**
- Questionnaire-based eligibility for guest users
- Adaptive question flow
- Real-time eligibility updates
- Multi-language support

**API Endpoints:**
```java
POST /api/v1/eligibility/check
GET  /api/v1/eligibility/questionnaire?template_name={name}
```

**Questionnaire Support:**
- Dynamic questionnaire generation from scheme rules
- Pre-filling from Golden Records (AI-PLATFORM-01)
- Context from 360° Profiles (AI-PLATFORM-02)

---

### Supporting Use Cases

#### 3. AI-PLATFORM-01: Golden Records
- Provides baseline demographic data for eligibility
- Pre-fills questionnaire answers

#### 4. AI-PLATFORM-02: 360° Profiles
- Provides income inference, vulnerability data
- Family context for eligibility evaluation

---

## Proposed Solution: Dynamic Eligibility Criteria System

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│              Departmental Portal - Scheme Builder           │
│  Database: smart_dept                                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  1. Department User Creates/Edits Scheme            │   │
│  │  2. Defines Eligibility Criteria (Natural Language) │   │
│  │  3. Calls NLP Extraction API                        │   │
│  │  4. Preview & Approve Criteria                     │   │
│  │  5. Store in smart_dept.schemes + rules            │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ API: POST /api/v1/admin/rules/extract-criteria
                       │ (Departmental Portal Backend → AI-PLATFORM-03)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│         AI-PLATFORM-03: Rule Extraction Service              │
│  Database: smart_warehouse                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  • NLP Model: GPT-4/Claude API (or fine-tuned model) │   │
│  │  • Rule structure validation                         │   │
│  │  • Conflict detection                                │   │
│  │  • Rule expression generation                        │   │
│  │  • Returns structured rules (JSON)                   │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Return extracted rules to Departmental Portal
                       │ Store in smart_dept.schemes + approval workflow
                       ▼
┌─────────────────────────────────────────────────────────────┐
│         Departmental Portal - Approval & Storage            │
│  Database: smart_dept                                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  • Review extracted rules                            │   │
│  │  • Edit/Approve rules                                │   │
│  │  • Store in smart_dept.schemes table                 │   │
│  │  • Store in smart_dept.scheme_eligibility_rules     │   │
│  │  • Trigger sync to smart_warehouse                   │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ ETL/CDC Sync (Batch or Event)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│         smart_warehouse Database                            │
│  Schema: eligibility                                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  • eligibility.scheme_master (scheme metadata)       │   │
│  │  • eligibility.scheme_eligibility_rules (rules)     │   │
│  │  • Used by AI-PLATFORM-03 for evaluation            │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ ETL/CDC Sync (Daily Batch)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│         smart_citizen Database                              │
│  Schema: public                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  • schemes table (read-only copy)                   │   │
│  │  • Used by Citizen Portal for display              │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ API: GET /api/v1/eligibility/config/scheme/{id}
                       │ (Citizen Portal → AI-PLATFORM-03)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Citizen Portal - Eligibility Screen             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  • Fetch dynamic criteria from AI-PLATFORM-03       │   │
│  │  • Generate questionnaire dynamically                │   │
│  │  • Real-time eligibility checking                    │   │
│  │  • Adaptive question flow                            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Detailed Flow & Architecture Clarifications

### Question 1: Which AI/ML Use Case or Model for NLP Extraction?

**Answer:** **AI-PLATFORM-03 (Eligibility Identification)** - Enhanced with NLP extraction capability

**Implementation Details:**

1. **NLP Model Options:**
   - **Option A (Recommended):** GPT-4/Claude API for natural language understanding
     - High accuracy for rule extraction
     - No training required
     - Cost per API call
   - **Option B:** Fine-tuned BERT/RoBERTa model
     - Trained on scheme eligibility criteria corpus
     - Lower cost per call
     - Requires training data and model maintenance

2. **Service Location:**
   - **New Service:** `ai-ml/use-cases/03_identification_beneficiary/src/services/criteria_extractor.py`
   - **API Endpoint:** `POST /api/v1/admin/rules/extract-criteria` (Spring Boot controller in AI-PLATFORM-03)
   - **Database:** Uses `smart_warehouse` database (same as AI-PLATFORM-03)

3. **Why AI-PLATFORM-03?**
   - Already has rule engine infrastructure
   - Understands rule structure and validation
   - Can validate extracted rules against existing rule types
   - Natural fit for eligibility-related functionality

**API Implementation:**
```java
// Location: ai-ml/use-cases/03_identification_beneficiary/spring_boot/controller/RuleExtractionController.java
@RestController
@RequestMapping("/api/v1/admin/rules")
public class RuleExtractionController {
    
    @PostMapping("/extract-criteria")
    public ResponseEntity<ExtractCriteriaResponse> extractCriteria(
            @RequestBody ExtractCriteriaRequest request) {
        // Calls Python service: criteria_extractor.py
        // Uses GPT-4/Claude API for NLP
        // Returns structured rules
    }
}
```

---

### Question 2: Rules Executed on smart_dept Schema

**Answer:** **Partially Correct** - Rules are **stored** in `smart_dept` initially, but **executed** in `smart_warehouse`

**Clarification:**

1. **Storage Flow:**
   ```
   Departmental Portal (smart_dept)
   ├── schemes table (scheme metadata)
   └── scheme_eligibility_rules table (rules for approval workflow)
   ```

2. **Execution Flow:**
   ```
   smart_warehouse.eligibility.scheme_eligibility_rules
   └── Used by AI-PLATFORM-03 Rule Engine for evaluation
   ```

3. **Database Schema in smart_dept:**
   ```sql
   -- In smart_dept database
   CREATE TABLE schemes (
       id UUID PRIMARY KEY,
       code VARCHAR(50) UNIQUE,
       name VARCHAR(255),
       description TEXT,
       eligibility_criteria_natural_language TEXT,  -- Original input
       status VARCHAR(20),
       created_at TIMESTAMP,
       updated_at TIMESTAMP
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
       status VARCHAR(20),  -- PENDING, APPROVED, REJECTED
       created_at TIMESTAMP
   );
   ```

4. **Why Store in smart_dept First?**
   - Departmental users need to review and approve
   - Approval workflow happens in departmental portal
   - Rules are then synced to `smart_warehouse` for execution

---

### Question 3: Data Flow: smart_dept → smart_warehouse → smart_citizen

**Answer:** **Multi-step sync process with ETL/CDC**

**Detailed Flow:**

#### Step 1: smart_dept → smart_warehouse

**Trigger:** When scheme is approved in departmental portal

**Sync Method:** 
- **Option A:** Event-driven (CDC) - Real-time sync when approved
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

**Trigger:** Daily batch sync (00:00 UTC) or event-driven

**Sync Method:** Batch (Daily) - As per existing data flow specification

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

**Note:** Citizen portal gets a **read-only copy** of scheme data. Rules are stored in `smart_warehouse` and accessed via API.

---

### Question 4: API Placement & Automatic Usage by Citizen Portal

**Answer:** **APIs in AI-PLATFORM-03, Citizen Portal calls them dynamically**

**API Architecture:**

#### 1. Rule Management APIs (Departmental Portal)

**Location:** `ai-ml/use-cases/03_identification_beneficiary/spring_boot/controller/`

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

**Location:** `ai-ml/use-cases/03_identification_beneficiary/spring_boot/controller/`

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

## Complete Data Flow Summary

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Departmental Portal (smart_dept)                         │
│    • User enters natural language criteria                  │
│    • Calls: POST /api/v1/admin/rules/extract-criteria       │
│    • Stores in smart_dept.schemes + scheme_eligibility_rules│
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ ETL/CDC Sync
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

## Solution Components

### 1. AI-Powered Criteria Extraction (New Component)

**Purpose:** Extract structured eligibility rules from natural language scheme definitions

**Technology Stack:**
- **NLP:** GPT-4/Claude for natural language understanding
- **Rule Parser:** Custom parser for rule expression generation
- **Validation:** Rule structure and logic validation

**Process Flow:**

1. **Input:** Department user enters eligibility criteria in natural language
   ```
   Example: "Citizen must be 60+ years old, below poverty line, 
   resident of Rajasthan, and have no other pension scheme"
   ```

2. **NLP Extraction:** AI extracts structured criteria
   ```json
   {
     "criteria": [
       {
         "type": "AGE",
         "operator": ">=",
         "value": 60,
         "rule_type": "MANDATORY"
       },
       {
         "type": "INCOME_GROUP",
         "operator": "==",
         "value": "BPL",
         "rule_type": "MANDATORY"
       },
       {
         "type": "GEOGRAPHY",
         "operator": "==",
         "value": "RAJASTHAN",
         "rule_type": "MANDATORY"
       },
       {
         "type": "PRIOR_PARTICIPATION",
         "operator": "NOT_EXISTS",
         "scheme_category": "PENSION",
         "rule_type": "EXCLUSION"
       }
     ]
   }
   ```

3. **Rule Expression Generation:** Convert to executable rule expression
   ```python
   rule_expression = """
   (age >= 60) AND 
   (income_group == 'BPL') AND 
   (state == 'RAJASTHAN') AND 
   (NOT EXISTS(prior_schemes WHERE category == 'PENSION'))
   """
   ```

4. **Validation:** Check for conflicts, completeness, syntax errors

5. **Preview:** Show extracted rules to department user for approval

**API Design:**
```java
POST /api/v1/admin/rules/extract-criteria
{
  "scheme_id": "uuid",
  "natural_language_criteria": "Citizen must be 60+ years old...",
  "scheme_context": {
    "category": "PENSION",
    "department": "SOCIAL_WELFARE"
  }
}
Response: {
  "extracted_rules": [
    {
      "rule_id": "temp_001",
      "rule_name": "Age Requirement",
      "rule_type": "MANDATORY",
      "rule_expression": "age >= 60",
      "criteria_type": "AGE",
      "confidence": 0.95,
      "validation_status": "VALID"
    }
  ],
  "warnings": [],
  "suggestions": [
    "Consider adding disability criteria for additional benefits"
  ]
}
```

---

### 2. Departmental Approval Workflow

**Purpose:** Allow departmental users to review and approve extracted criteria

**Workflow Steps:**

1. **Extraction:** AI extracts criteria from scheme definition
2. **Review:** Department user reviews extracted rules
3. **Edit:** User can modify/delete/add rules manually
4. **Preview:** Preview how criteria will appear in citizen portal
5. **Approve:** Approve criteria → Rules become active
6. **Publish:** Published rules available in citizen portal

**Database Schema:**
```sql
CREATE TABLE eligibility.rule_approval_workflow (
    workflow_id UUID PRIMARY KEY,
    scheme_code VARCHAR(50) NOT NULL,
    extracted_rules JSONB,  -- AI-extracted rules
    edited_rules JSONB,     -- User-edited rules
    status VARCHAR(20),     -- PENDING, APPROVED, REJECTED
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,
    version INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**API Design:**
```java
// Get pending approvals
GET /api/v1/admin/rules/pending-approvals

// Approve criteria
POST /api/v1/admin/rules/approve-criteria
{
  "workflow_id": "uuid",
  "approved_rules": [...],
  "comments": "Approved with minor edits"
}

// Preview criteria in citizen portal format
GET /api/v1/admin/rules/preview-criteria?scheme_id={id}
```

---

### 3. Dynamic Questionnaire Generation (Citizen Portal)

**Purpose:** Generate questionnaire dynamically from approved eligibility rules

**Process:**

1. **Fetch Scheme Rules:** Get approved rules for scheme
   ```java
   GET /api/v1/eligibility/config/scheme/{scheme_id}
   Response: {
     "scheme_code": "PENSION_001",
     "rules": [
       {
         "rule_id": 1,
         "rule_name": "Age Requirement",
         "criteria_type": "AGE",
         "rule_expression": "age >= 60",
         "question_config": {
           "question_text": "What is your age?",
           "input_type": "NUMBER",
           "required": true,
           "validation": {
             "min": 18,
             "max": 120
           }
         }
       },
       {
         "rule_id": 2,
         "criteria_type": "INCOME_GROUP",
         "question_config": {
           "question_text": "What is your income group?",
           "input_type": "SELECT",
           "options": ["BPL", "APL", "HIGH_INCOME"],
           "required": true
         }
       }
     ]
   }
   ```

2. **Generate Questionnaire:** Create dynamic form fields
   - Map criteria types to input types
   - Generate question text from rule names
   - Add validation based on rule expressions

3. **Adaptive Flow:** Show only relevant questions
   - Skip questions if answer can be inferred from Golden Record
   - Conditional questions based on previous answers
   - Progress: "Answer 3 more questions to see results"

**Frontend Implementation:**
```typescript
interface DynamicCriteria {
  criteriaId: string;
  criteriaType: CriteriaType;
  questionText: string;
  inputType: 'NUMBER' | 'SELECT' | 'TEXT' | 'BOOLEAN' | 'MULTI_SELECT';
  options?: string[];
  required: boolean;
  validation?: ValidationRules;
  prefillFrom?: 'GOLDEN_RECORD' | 'PROFILE';
  conditionalLogic?: ConditionalRule[];
}

enum CriteriaType {
  AGE = 'AGE',
  GENDER = 'GENDER',
  INCOME_GROUP = 'INCOME_GROUP',
  ANNUAL_INCOME = 'ANNUAL_INCOME',
  DISTRICT = 'DISTRICT',
  BLOCK = 'BLOCK',
  VILLAGE = 'VILLAGE',
  DISABILITY = 'DISABILITY',
  DISABILITY_TYPE = 'DISABILITY_TYPE',
  DISABILITY_PERCENTAGE = 'DISABILITY_PERCENTAGE',
  FAMILY_SIZE = 'FAMILY_SIZE',
  CATEGORY = 'CATEGORY',  // SC/ST/OBC/General
  RATION_CARD = 'RATION_CARD',
  LAND_OWNERSHIP = 'LAND_OWNERSHIP',
  PROPERTY_OWNERSHIP = 'PROPERTY_OWNERSHIP',
  PRIOR_PARTICIPATION = 'PRIOR_PARTICIPATION',
  EDUCATION_LEVEL = 'EDUCATION_LEVEL',
  EMPLOYMENT_STATUS = 'EMPLOYMENT_STATUS',
  MARITAL_STATUS = 'MARITAL_STATUS',
  // ... extensible for new criteria types
}
```

---

### 4. Enhanced Rule Engine (AI-PLATFORM-03)

**Current Capabilities:**
- ✅ 8 rule types supported
- ✅ Rule expression evaluation
- ✅ Rule path generation

**Enhancements Needed:**

1. **Extended Criteria Types:**
   - Add support for new criteria types (education, employment, marital status, etc.)
   - Custom criteria types per scheme
   - Complex criteria (nested conditions)

2. **Rule Versioning:**
   - Track rule changes over time
   - Support rule rollback
   - A/B testing of rule versions

3. **Rule Analytics:**
   - Track which criteria are most common
   - Identify criteria patterns across schemes
   - Suggest criteria based on scheme category

**Database Enhancement:**
```sql
-- Add new criteria types table
CREATE TABLE eligibility.criteria_types (
    criteria_type_id SERIAL PRIMARY KEY,
    type_code VARCHAR(50) UNIQUE NOT NULL,
    type_name VARCHAR(100) NOT NULL,
    input_type VARCHAR(20) NOT NULL,  -- NUMBER, SELECT, TEXT, BOOLEAN
    validation_rules JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert standard criteria types
INSERT INTO eligibility.criteria_types (type_code, type_name, input_type) VALUES
('AGE', 'Age', 'NUMBER'),
('GENDER', 'Gender', 'SELECT'),
('INCOME_GROUP', 'Income Group', 'SELECT'),
('ANNUAL_INCOME', 'Annual Income', 'NUMBER'),
('DISTRICT', 'District', 'SELECT'),
('DISABILITY', 'Disability Status', 'BOOLEAN'),
('FAMILY_SIZE', 'Family Size', 'NUMBER'),
('RATION_CARD', 'Ration Card', 'BOOLEAN'),
('EDUCATION_LEVEL', 'Education Level', 'SELECT'),
('EMPLOYMENT_STATUS', 'Employment Status', 'SELECT'),
('MARITAL_STATUS', 'Marital Status', 'SELECT'),
('LAND_OWNERSHIP', 'Land Ownership', 'BOOLEAN'),
('PROPERTY_OWNERSHIP', 'Property Ownership', 'BOOLEAN');
```

---

## Implementation Plan

### Phase 1: Foundation (Weeks 1-4)

#### Week 1-2: Criteria Extraction Service
- [ ] Develop NLP-based criteria extraction (AI-PLATFORM-03 enhancement)
- [ ] Create rule expression parser
- [ ] Build validation engine
- [ ] API: `POST /api/v1/admin/rules/extract-criteria`

#### Week 3-4: Approval Workflow
- [ ] Database schema for approval workflow
- [ ] Departmental portal UI for rule review/approval
- [ ] API: Approval endpoints
- [ ] Preview functionality

**Deliverables:**
- Criteria extraction service
- Approval workflow backend
- Departmental portal approval UI

---

### Phase 2: Dynamic Questionnaire (Weeks 5-8)

#### Week 5-6: Backend Enhancement
- [ ] Enhance AI-PLATFORM-03 rule engine (extended criteria types)
- [ ] API: `GET /api/v1/eligibility/config/scheme/{scheme_id}` (returns dynamic criteria)
- [ ] Question generation logic
- [ ] Pre-fill logic from Golden Records

#### Week 7-8: Frontend Implementation
- [ ] Replace hardcoded 8 fields with dynamic questionnaire
- [ ] Dynamic form field generation
- [ ] Conditional question logic
- [ ] Pre-fill from Golden Records
- [ ] Real-time eligibility updates

**Deliverables:**
- Dynamic questionnaire in citizen portal
- Integration with AI-PLATFORM-03/08
- Pre-fill from Golden Records

---

### Phase 3: Integration & Testing (Weeks 9-12)

#### Week 9-10: Scheme Builder Integration
- [ ] Integrate criteria extraction into scheme builder
- [ ] End-to-end workflow: Create scheme → Extract criteria → Approve → Publish
- [ ] Testing with real schemes

#### Week 11-12: Testing & Refinement
- [ ] User acceptance testing
- [ ] Performance testing
- [ ] Bug fixes and refinements
- [ ] Documentation

**Deliverables:**
- Complete integrated system
- Tested and documented
- Ready for production

---

## API Specifications

### 1. Extract Criteria from Natural Language

```java
POST /api/v1/admin/rules/extract-criteria
Content-Type: application/json

Request:
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

Response:
{
  "success": true,
  "extracted_rules": [
    {
      "rule_id": "temp_001",
      "rule_name": "Age Requirement - 60+",
      "rule_type": "MANDATORY",
      "criteria_type": "AGE",
      "rule_expression": "age >= 60",
      "question_config": {
        "question_text": "What is your age?",
        "input_type": "NUMBER",
        "required": true,
        "validation": {"min": 18, "max": 120}
      },
      "confidence": 0.95,
      "validation_status": "VALID"
    },
    {
      "rule_id": "temp_002",
      "rule_name": "Income Group - BPL",
      "rule_type": "MANDATORY",
      "criteria_type": "INCOME_GROUP",
      "rule_expression": "income_group == 'BPL'",
      "question_config": {
        "question_text": "What is your income group?",
        "input_type": "SELECT",
        "options": ["BPL", "APL", "HIGH_INCOME"],
        "required": true
      },
      "confidence": 0.92,
      "validation_status": "VALID"
    },
    {
      "rule_id": "temp_003",
      "rule_name": "Geography - Rajasthan",
      "rule_type": "MANDATORY",
      "criteria_type": "DISTRICT",
      "rule_expression": "state == 'RAJASTHAN'",
      "question_config": {
        "question_text": "Which state do you reside in?",
        "input_type": "SELECT",
        "options": ["RAJASTHAN", "GUJARAT", "..."],
        "required": true
      },
      "confidence": 0.98,
      "validation_status": "VALID"
    },
    {
      "rule_id": "temp_004",
      "rule_name": "Exclusion - No Prior Pension",
      "rule_type": "EXCLUSION",
      "criteria_type": "PRIOR_PARTICIPATION",
      "rule_expression": "NOT EXISTS(prior_schemes WHERE category == 'PENSION')",
      "question_config": {
        "question_text": "Are you currently enrolled in any other pension scheme?",
        "input_type": "BOOLEAN",
        "required": true
      },
      "confidence": 0.90,
      "validation_status": "VALID"
    }
  ],
  "warnings": [],
  "suggestions": [
    "Consider adding disability criteria for additional benefits",
    "You may want to specify district-level restrictions"
  ]
}
```

---

### 2. Get Dynamic Criteria for Scheme

```java
GET /api/v1/eligibility/config/scheme/{scheme_id}?include_questions=true

Response:
{
  "scheme_id": "uuid",
  "scheme_code": "PENSION_001",
  "scheme_name": "Old Age Pension",
  "rules": [
    {
      "rule_id": 1,
      "rule_name": "Age Requirement - 60+",
      "rule_type": "MANDATORY",
      "criteria_type": "AGE",
      "rule_expression": "age >= 60",
      "priority": 1,
      "active": true,
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
        "prefill_field": "date_of_birth"  // Calculate age from DOB
      }
    },
    {
      "rule_id": 2,
      "criteria_type": "INCOME_GROUP",
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
    }
  ],
  "total_criteria": 4,
  "mandatory_criteria": 3,
  "optional_criteria": 0,
  "exclusion_criteria": 1
}
```

---

### 3. Preview Criteria (Departmental Portal)

```java
GET /api/v1/admin/rules/preview-criteria?scheme_id={id}&workflow_id={id}

Response:
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
        },
        {
          "step": 2,
          "question": "What is your income group?",
          "input_type": "SELECT",
          "options": ["BPL", "APL", "HIGH_INCOME"]
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

## Frontend Changes Required

### Current Implementation (EligibilityCheckerPage.tsx)

**Replace:**
```typescript
// OLD: Hardcoded 8 fields
interface EligibilityQuestionnaire {
  age?: number;
  gender?: string;
  district?: string;
  annualIncome?: number;
  incomeGroup?: string;
  familySize?: number;
  disability?: boolean;
  hasRationCard?: boolean;
}
```

**With:**
```typescript
// NEW: Dynamic criteria from API
interface DynamicCriteria {
  criteriaId: string;
  criteriaType: CriteriaType;
  questionText: string;
  questionTextHi?: string;  // Hindi translation
  inputType: 'NUMBER' | 'SELECT' | 'TEXT' | 'BOOLEAN' | 'MULTI_SELECT';
  options?: Array<{value: string, label: string}>;
  required: boolean;
  validation?: ValidationRules;
  prefillFrom?: 'GOLDEN_RECORD' | 'PROFILE';
  prefillField?: string;
  conditionalLogic?: ConditionalRule[];
  step?: number;
}

interface EligibilityQuestionnaire {
  [criteriaId: string]: any;  // Dynamic based on scheme criteria
}
```

**Component Changes:**
1. Fetch dynamic criteria on component mount
2. Generate form fields dynamically
3. Handle pre-filling from Golden Records
4. Implement conditional question logic
5. Real-time eligibility updates as user answers

---

## Benefits

### For Citizens
- ✅ **Dynamic Criteria:** Questionnaire adapts to each scheme
- ✅ **Fewer Questions:** Only relevant questions shown
- ✅ **Pre-filled Data:** Less manual entry
- ✅ **Better Accuracy:** More comprehensive eligibility checking

### For Departmental Users
- ✅ **Easy Scheme Creation:** Natural language input
- ✅ **AI Assistance:** Automatic rule extraction
- ✅ **Approval Control:** Review and edit before publishing
- ✅ **Consistency:** Standardized criteria format

### For System
- ✅ **Scalability:** New schemes automatically supported
- ✅ **Maintainability:** Centralized rule management
- ✅ **Extensibility:** Easy to add new criteria types
- ✅ **Analytics:** Track criteria patterns and effectiveness

---

## Next Steps

### Immediate (Before Scheme Builder Development)
1. ✅ **Document Current State:** This document
2. ⏳ **Review with Stakeholders:** Get approval for approach
3. ⏳ **Design Database Schema:** Finalize rule storage structure
4. ⏳ **API Design Review:** Finalize API contracts

### After Scheme Builder Development
1. ⏳ **Implement Criteria Extraction:** AI-PLATFORM-03 enhancement
2. ⏳ **Build Approval Workflow:** Departmental portal integration
3. ⏳ **Enhance Rule Engine:** Extended criteria types support
4. ⏳ **Update Citizen Portal:** Dynamic questionnaire implementation
5. ⏳ **Testing:** End-to-end testing with real schemes
6. ⏳ **Documentation:** User guides and API documentation

---

## Recommendations

### 1. Revisit Eligibility Screen After Scheme Builder
✅ **Agreed** - This is the right approach because:
- Scheme builder will define the source of truth for criteria
- Criteria extraction can be tested with real scheme definitions
- Approval workflow can be integrated into scheme builder UI
- Citizen portal can be updated once criteria structure is finalized

### 2. Phased Rollout
- **Phase 1:** Keep current 8 fields as fallback
- **Phase 2:** Add dynamic criteria for new schemes
- **Phase 3:** Migrate existing schemes to dynamic criteria
- **Phase 4:** Remove hardcoded fields

### 3. Backward Compatibility
- Maintain support for schemes with old criteria format
- Gradual migration path
- No breaking changes to existing functionality

---

**Document Version:** 1.0  
**Created:** 2024-12-30  
**Status:** ✅ Proposal Complete - Ready for Review  
**Next Review:** After Scheme Builder development


