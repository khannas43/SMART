# NLP Training Data Generation Guide

**Purpose:** Generate 500+ dummy schemes with natural language criteria for training BERT/RoBERTa model  
**Created:** 2024-12-30  
**Status:** 📋 Data Generation Guide

---

## Overview

This guide provides instructions for generating 500+ training examples (schemes) with natural language eligibility criteria and their corresponding structured rules. The data will be used to train a fine-tuned BERT/RoBERTa model for automatic rule extraction.

---

## Data Generation Strategy

### Option 1: AI-Assisted Generation (Recommended)

Use Cursor, Perplexity, Claude, or GPT-4 to generate schemes in batches.

### Option 2: Script-Based Generation

Use Python script with templates to generate variations.

### Option 3: Hybrid Approach

Combine AI generation with script-based augmentation.

---

## Data Format Specification

### Required Fields

Each scheme must include:

1. **Scheme Metadata:**
   - `scheme_id`: Unique identifier
   - `scheme_code`: Scheme code (e.g., "PENSION_001")
   - `scheme_name`: Scheme name
   - `scheme_category`: Category (PENSION, HEALTH, EDUCATION, etc.)
   - `department`: Department name

2. **Natural Language Criteria:**
   - `natural_language_criteria`: Plain English eligibility criteria

3. **Structured Rules:**
   - `extracted_rules`: Array of structured rules

### Example Template

```json
{
  "scheme_id": "SCHEME_001",
  "scheme_code": "PENSION_001",
  "scheme_name": "Old Age Pension",
  "scheme_category": "PENSION",
  "department": "Social Welfare",
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

---

## AI Prompt Template for Data Generation

### Prompt for Cursor/Perplexity/Claude/GPT-4

```
Generate a comprehensive government welfare scheme with eligibility criteria in natural language and corresponding structured rules.

Requirements:
1. Create a realistic scheme name and code
2. Write eligibility criteria in natural, conversational English (2-4 sentences)
3. Extract 3-6 structured rules from the criteria
4. Include diverse rule types: AGE, INCOME_GROUP, GEOGRAPHY, DISABILITY, CATEGORY, etc.

Scheme Categories to Cover:
- PENSION (Old age, widow, disability)
- HEALTH (Health insurance, medical assistance)
- EDUCATION (Scholarships, school supplies)
- HOUSING (Housing assistance, home loans)
- FINANCIAL (Credit, loans, grants)
- FOOD (Ration cards, food assistance)
- EMPLOYMENT (Job training, employment schemes)
- AGRICULTURE (Farmer assistance, crop insurance)

Rule Types to Include:
- AGE (min/max/range)
- GENDER (male/female/any)
- INCOME_GROUP (BPL/APL/High Income)
- ANNUAL_INCOME (thresholds)
- DISTRICT/BLOCK/VILLAGE/STATE (geography)
- DISABILITY (status/type/percentage)
- FAMILY_SIZE (min/max)
- CATEGORY (SC/ST/OBC/General)
- RATION_CARD (yes/no)
- LAND_OWNERSHIP (yes/no)
- PRIOR_PARTICIPATION (exclusions)
- EDUCATION_LEVEL
- EMPLOYMENT_STATUS
- MARITAL_STATUS

Output Format: JSON with scheme_id, scheme_code, scheme_name, scheme_category, department, natural_language_criteria, and extracted_rules array.

Generate 10 different schemes covering different categories and rule types.
```

### Batch Generation Prompt

```
Generate 50 government welfare schemes with eligibility criteria. Each scheme should:

1. Have unique scheme_code (format: CATEGORY_XXX, e.g., PENSION_001, HEALTH_001)
2. Include natural language eligibility criteria (2-4 sentences)
3. Have 3-6 structured rules extracted from criteria
4. Cover diverse categories: PENSION, HEALTH, EDUCATION, HOUSING, FINANCIAL, FOOD, EMPLOYMENT, AGRICULTURE
5. Include various rule types: AGE, INCOME, GEOGRAPHY, DISABILITY, CATEGORY, etc.

Output as JSON array with 50 schemes.

Ensure diversity in:
- Age requirements (18-100+)
- Income thresholds (0-500000+)
- Geographic locations (different states/districts)
- Disability types and percentages
- Family sizes
- Education levels
- Employment statuses
```

---

## Rule Type Patterns

### Age Rules

**Natural Language Patterns:**
- "Citizen must be 60+ years old"
- "Age requirement: minimum 60 years"
- "Applicant should be at least 18 years of age"
- "Age between 18 and 60 years"
- "Senior citizens above 60 years"

**Structured Format:**
```json
{
  "rule_type": "AGE",
  "operator": ">=",  // or "<=", "==", "BETWEEN"
  "value": 60,       // or {"min": 18, "max": 60}
  "rule_expression": "age >= 60"
}
```

### Income Rules

**Natural Language Patterns:**
- "Below poverty line (BPL)"
- "Annual income less than ₹50,000"
- "Income group: BPL or APL"
- "Household income should not exceed ₹2,00,000"

**Structured Format:**
```json
{
  "rule_type": "INCOME_GROUP",
  "operator": "==",
  "value": "BPL",
  "rule_expression": "income_group == 'BPL'"
}
// OR
{
  "rule_type": "ANNUAL_INCOME",
  "operator": "<=",
  "value": 50000,
  "rule_expression": "annual_income <= 50000"
}
```

### Geography Rules

**Natural Language Patterns:**
- "Resident of Rajasthan"
- "Available only in selected districts"
- "Rural areas only"
- "Urban residents eligible"

**Structured Format:**
```json
{
  "rule_type": "STATE",
  "operator": "==",
  "value": "RAJASTHAN",
  "rule_expression": "state == 'RAJASTHAN'"
}
```

### Disability Rules

**Natural Language Patterns:**
- "Person with disability"
- "40% or more disability"
- "Physically disabled"
- "Mental disability required"

**Structured Format:**
```json
{
  "rule_type": "DISABILITY",
  "operator": "==",
  "value": true,
  "rule_expression": "disability_status == true"
}
// OR
{
  "rule_type": "DISABILITY_PERCENTAGE",
  "operator": ">=",
  "value": 40,
  "rule_expression": "disability_percentage >= 40"
}
```

---

## Data Generation Script

### Python Script Template

```python
import json
import random
from typing import List, Dict

def generate_scheme(scheme_id: int, category: str) -> Dict:
    """Generate a single scheme with eligibility criteria"""
    
    # Template-based generation
    schemes_templates = {
        "PENSION": {
            "name_patterns": ["Old Age Pension", "Widow Pension", "Disability Pension"],
            "age_ranges": [(60, 100), (18, 100)],
            "income_groups": ["BPL", "APL"],
            "geography": ["RAJASTHAN", "GUJARAT", "MADHYA_PRADESH"]
        },
        "HEALTH": {
            "name_patterns": ["Health Insurance", "Medical Assistance", "Health Card"],
            "age_ranges": [(0, 100)],
            "income_groups": ["BPL", "APL"],
            "geography": ["RAJASTHAN", "GUJARAT"]
        }
        # Add more categories...
    }
    
    template = schemes_templates.get(category, schemes_templates["PENSION"])
    
    # Generate natural language criteria
    criteria_parts = []
    
    # Age requirement
    if random.random() > 0.3:  # 70% have age requirements
        min_age = random.randint(18, 60)
        criteria_parts.append(f"Citizen must be {min_age}+ years old")
    
    # Income requirement
    if random.random() > 0.4:  # 60% have income requirements
        income_type = random.choice(["BPL", "APL", "annual income"])
        if income_type == "annual income":
            threshold = random.choice([30000, 50000, 100000, 200000])
            criteria_parts.append(f"Annual income less than ₹{threshold:,}")
        else:
            criteria_parts.append(f"Below poverty line ({income_type})")
    
    # Geography requirement
    if random.random() > 0.5:  # 50% have geography requirements
        state = random.choice(template["geography"])
        criteria_parts.append(f"Resident of {state}")
    
    # Disability requirement
    if category == "PENSION" and random.random() > 0.7:  # 30% for pension
        criteria_parts.append("Person with 40% or more disability")
    
    natural_language = ", ".join(criteria_parts) + "."
    
    # Generate structured rules
    rules = []
    # Extract rules from criteria_parts...
    
    return {
        "scheme_id": f"SCHEME_{scheme_id:03d}",
        "scheme_code": f"{category}_{scheme_id:03d}",
        "scheme_name": random.choice(template["name_patterns"]),
        "scheme_category": category,
        "department": "Social Welfare",
        "natural_language_criteria": natural_language,
        "extracted_rules": rules
    }

def generate_dataset(num_schemes: int = 500) -> List[Dict]:
    """Generate dataset of schemes"""
    categories = ["PENSION", "HEALTH", "EDUCATION", "HOUSING", 
                 "FINANCIAL", "FOOD", "EMPLOYMENT", "AGRICULTURE"]
    
    schemes = []
    for i in range(num_schemes):
        category = random.choice(categories)
        scheme = generate_scheme(i + 1, category)
        schemes.append(scheme)
    
    return schemes

if __name__ == "__main__":
    schemes = generate_dataset(500)
    
    # Save to file
    with open("data/training/schemes_raw.json", "w") as f:
        json.dump(schemes, f, indent=2)
    
    print(f"Generated {len(schemes)} schemes")
```

---

## Data Validation Checklist

### Quality Checks

- [ ] **Completeness:** All required fields present
- [ ] **Format:** Valid JSON structure
- [ ] **Uniqueness:** No duplicate scheme codes
- [ ] **Rule Consistency:** Rules match natural language
- [ ] **Rule Types:** Valid rule types only
- [ ] **Operators:** Valid operators (>=, <=, ==, IN, etc.)
- [ ] **Values:** Valid value types (numbers, strings, booleans)
- [ ] **Diversity:** Good coverage of categories and rule types

### Validation Script

```python
import json
from typing import List, Dict

VALID_RULE_TYPES = [
    "AGE", "GENDER", "INCOME_GROUP", "ANNUAL_INCOME",
    "DISTRICT", "BLOCK", "VILLAGE", "STATE",
    "DISABILITY", "DISABILITY_TYPE", "DISABILITY_PERCENTAGE",
    "FAMILY_SIZE", "CATEGORY", "RATION_CARD",
    "LAND_OWNERSHIP", "PROPERTY_OWNERSHIP",
    "PRIOR_PARTICIPATION", "EDUCATION_LEVEL",
    "EMPLOYMENT_STATUS", "MARITAL_STATUS"
]

VALID_OPERATORS = [">=", "<=", "==", "!=", "IN", "NOT_IN", "BETWEEN"]

def validate_scheme(scheme: Dict) -> List[str]:
    """Validate a single scheme"""
    errors = []
    
    # Check required fields
    required = ["scheme_id", "scheme_code", "scheme_name", 
                "natural_language_criteria", "extracted_rules"]
    for field in required:
        if field not in scheme:
            errors.append(f"Missing required field: {field}")
    
    # Validate rules
    for rule in scheme.get("extracted_rules", []):
        if "rule_type" not in rule:
            errors.append("Rule missing rule_type")
        elif rule["rule_type"] not in VALID_RULE_TYPES:
            errors.append(f"Invalid rule_type: {rule['rule_type']}")
        
        if "operator" in rule and rule["operator"] not in VALID_OPERATORS:
            errors.append(f"Invalid operator: {rule['operator']}")
    
    return errors

def validate_dataset(filepath: str) -> Dict:
    """Validate entire dataset"""
    with open(filepath, "r") as f:
        schemes = json.load(f)
    
    all_errors = []
    valid_count = 0
    
    for scheme in schemes:
        errors = validate_scheme(scheme)
        if errors:
            all_errors.append({
                "scheme_code": scheme.get("scheme_code", "UNKNOWN"),
                "errors": errors
            })
        else:
            valid_count += 1
    
    return {
        "total": len(schemes),
        "valid": valid_count,
        "invalid": len(all_errors),
        "errors": all_errors
    }
```

---

## Data Splitting

### Train/Validation/Test Split

```python
import json
import random

def split_dataset(input_file: str, train_ratio: float = 0.7, 
                  val_ratio: float = 0.15, test_ratio: float = 0.15):
    """Split dataset into train/val/test"""
    
    with open(input_file, "r") as f:
        schemes = json.load(f)
    
    # Shuffle
    random.shuffle(schemes)
    
    # Calculate splits
    n = len(schemes)
    train_end = int(n * train_ratio)
    val_end = train_end + int(n * val_ratio)
    
    train = schemes[:train_end]
    val = schemes[train_end:val_end]
    test = schemes[val_end:]
    
    # Save splits
    with open("data/training/train.json", "w") as f:
        json.dump(train, f, indent=2)
    
    with open("data/training/val.json", "w") as f:
        json.dump(val, f, indent=2)
    
    with open("data/training/test.json", "w") as f:
        json.dump(test, f, indent=2)
    
    print(f"Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")
```

---

## Data Augmentation (Optional)

### Paraphrasing

Generate variations of natural language criteria:

```python
def paraphrase_criteria(criteria: str) -> List[str]:
    """Generate paraphrased versions"""
    paraphrases = [
        criteria,  # Original
        criteria.replace("must be", "should be"),
        criteria.replace("Citizen", "Applicant"),
        criteria.replace("years old", "years of age"),
        # Add more patterns...
    ]
    return paraphrases
```

### Rule Variations

Generate variations of rule expressions:

```python
def generate_rule_variations(rule: Dict) -> List[Dict]:
    """Generate rule expression variations"""
    variations = []
    
    # Original
    variations.append(rule)
    
    # Different operators (if semantically equivalent)
    if rule["operator"] == ">=" and rule["rule_type"] == "AGE":
        variations.append({
            **rule,
            "rule_expression": f"age > {rule['value'] - 1}"
        })
    
    return variations
```

---

## Step-by-Step Generation Process

### Step 1: Generate Initial Batch (100 schemes)

1. Use AI prompt to generate 100 schemes
2. Save to `data/training/schemes_batch_1.json`
3. Validate using validation script
4. Fix any errors

### Step 2: Generate Additional Batches

1. Generate 4 more batches of 100 schemes each
2. Ensure diversity across categories
3. Validate each batch
4. Combine into `data/training/schemes_raw.json`

### Step 3: Data Cleaning

1. Remove duplicates
2. Fix validation errors
3. Standardize formats
4. Save to `data/training/schemes_processed.json`

### Step 4: Data Splitting

1. Split into train/val/test (70/15/15)
2. Ensure category distribution in each split
3. Save splits to separate files

### Step 5: Data Augmentation (Optional)

1. Generate paraphrases
2. Create rule variations
3. Expand dataset if needed

---

## Expected Output

### File Structure

```
data/training/
├── schemes_raw.json          # Raw generated schemes (500+)
├── schemes_processed.json     # Cleaned and validated
├── train.json                 # Training set (350 schemes)
├── val.json                   # Validation set (75 schemes)
└── test.json                  # Test set (75 schemes)
```

### Statistics

- **Total Schemes:** 500+
- **Categories:** 8+ categories
- **Rule Types:** 20+ rule types
- **Average Rules per Scheme:** 3-6 rules
- **Total Rules:** 2000+ rules

---

## Quality Metrics

### Target Metrics

- **Completeness:** 100% (all fields present)
- **Validity:** >95% (valid rule types/operators)
- **Diversity:** 
  - All 8 categories represented
  - All 20 rule types represented
  - Geographic diversity (multiple states)
  - Age range diversity (0-100+)
  - Income range diversity (0-500000+)

---

## Next Steps

1. **Generate Data:** Use AI tools to generate 500+ schemes
2. **Validate:** Run validation script
3. **Clean:** Fix any errors
4. **Split:** Create train/val/test splits
5. **Proceed:** Move to model training (see `NLP_MODEL_TRAINING_GUIDE.md`)

---

**Document Version:** 1.0  
**Last Updated:** 2024-12-30  
**Status:** 📋 Ready for Data Generation

