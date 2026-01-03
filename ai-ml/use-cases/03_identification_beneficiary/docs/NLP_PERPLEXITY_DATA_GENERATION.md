# Perplexity Data Generation Guide - Token-Efficient

**Purpose:** Generate 500+ training schemes using Perplexity with minimal token usage  
**Tool:** Perplexity AI  
**Strategy:** Batch generation with optimized prompts  
**Created:** 2024-12-30

---

## Overview

This guide provides **token-efficient prompts** for Perplexity to generate 500+ training schemes. Each prompt generates **20-25 schemes** per request, minimizing total token usage.

**Estimated Token Usage:**
- **Per Request:** ~2,000-3,000 tokens (input + output)
- **Total Requests:** 20-25 requests for 500 schemes
- **Total Estimated:** ~50,000-75,000 tokens

---

## Strategy: Batch Generation

### Approach
1. Generate **20-25 schemes per Perplexity request**
2. Use **concise, structured prompts**
3. Request **JSON output only** (no explanations)
4. **20 batches** = 500 schemes

---

## Perplexity Prompts (Copy-Paste Ready)

### Batch 1: PENSION Schemes (25 schemes)

**Copy this prompt to Perplexity:**

```
Generate 25 government pension schemes in JSON array format. Each scheme must have:
- scheme_id: "SCHEME_XXX" (001-025)
- scheme_code: "PENSION_XXX"
- scheme_name: realistic pension scheme name
- scheme_category: "PENSION"
- department: "Social Welfare" or "Women & Child Development"
- natural_language_criteria: 2-4 sentence eligibility criteria
- extracted_rules: array of 3-6 rules with rule_type, operator, value, rule_expression, rule_type_category, confidence

Rule types: AGE (>=60), INCOME_GROUP (BPL/APL), STATE (RAJASTHAN/GUJARAT/MADHYA_PRADESH), DISABILITY (true/40+%), PRIOR_PARTICIPATION (exclusions), GENDER (FEMALE for widow), MARITAL_STATUS (WIDOWED)

Vary: age (60-100), income groups, states, disability types, widow requirements.

Output ONLY JSON array, no explanations.
```

### Batch 2: HEALTH Schemes (25 schemes)

```
Generate 25 government health schemes in JSON array format. Each scheme must have:
- scheme_id: "SCHEME_XXX" (026-050)
- scheme_code: "HEALTH_XXX"
- scheme_name: realistic health scheme name
- scheme_category: "HEALTH"
- department: "Health" or "Medical"
- natural_language_criteria: 2-4 sentence eligibility criteria
- extracted_rules: array of 3-6 rules

Rule types: AGE (0-100), INCOME_GROUP, DISTRICT, FAMILY_SIZE (2-10), DISABILITY, CATEGORY (SC/ST/OBC), RATION_CARD

Vary: age ranges, income thresholds (30000-200000), family sizes, districts, categories.

Output ONLY JSON array, no explanations.
```

### Batch 3: EDUCATION Schemes (25 schemes)

```
Generate 25 government education schemes in JSON array format. Each scheme must have:
- scheme_id: "SCHEME_XXX" (051-075)
- scheme_code: "EDUCATION_XXX"
- scheme_name: realistic education scheme name
- scheme_category: "EDUCATION"
- department: "Education"
- natural_language_criteria: 2-4 sentence eligibility criteria
- extracted_rules: array of 3-6 rules

Rule types: AGE (5-25), EDUCATION_LEVEL (PRIMARY/SECONDARY/GRADUATE), CATEGORY (SC/ST/OBC), INCOME_GROUP, GENDER, DISTRICT

Vary: age ranges, education levels, categories, income groups, gender requirements.

Output ONLY JSON array, no explanations.
```

### Batch 4: HOUSING Schemes (25 schemes)

```
Generate 25 government housing schemes in JSON array format. Each scheme must have:
- scheme_id: "SCHEME_XXX" (076-100)
- scheme_code: "HOUSING_XXX"
- scheme_name: realistic housing scheme name
- scheme_category: "HOUSING"
- department: "Housing" or "Urban Development"
- natural_language_criteria: 2-4 sentence eligibility criteria
- extracted_rules: array of 3-6 rules

Rule types: INCOME_GROUP, ANNUAL_INCOME (50000-300000), LAND_OWNERSHIP (false), PROPERTY_OWNERSHIP (false), FAMILY_SIZE (3-8), CATEGORY, DISTRICT, RATION_CARD

Vary: income thresholds, family sizes, categories, districts, property ownership requirements.

Output ONLY JSON array, no explanations.
```

### Batch 5: FINANCIAL Schemes (25 schemes)

```
Generate 25 government financial schemes in JSON array format. Each scheme must have:
- scheme_id: "SCHEME_XXX" (101-125)
- scheme_code: "FINANCIAL_XXX"
- scheme_name: realistic financial scheme name
- scheme_category: "FINANCIAL"
- department: "Finance" or "Rural Development"
- natural_language_criteria: 2-4 sentence eligibility criteria
- extracted_rules: array of 3-6 rules

Rule types: INCOME_GROUP, ANNUAL_INCOME, EMPLOYMENT_STATUS (UNEMPLOYED/SELF_EMPLOYED), GENDER (FEMALE), AGE (18-60), CATEGORY, DISTRICT

Vary: income thresholds, employment status, gender, age ranges, categories.

Output ONLY JSON array, no explanations.
```

### Batch 6: FOOD Schemes (25 schemes)

```
Generate 25 government food schemes in JSON array format. Each scheme must have:
- scheme_id: "SCHEME_XXX" (126-150)
- scheme_code: "FOOD_XXX"
- scheme_name: realistic food scheme name
- scheme_category: "FOOD"
- department: "Food & Civil Supplies"
- natural_language_criteria: 2-4 sentence eligibility criteria
- extracted_rules: array of 3-6 rules

Rule types: RATION_CARD (true), INCOME_GROUP (BPL), FAMILY_SIZE (1-10), CATEGORY, DISTRICT, BLOCK

Vary: ration card types, income groups, family sizes, categories, districts, blocks.

Output ONLY JSON array, no explanations.
```

### Batch 7: EMPLOYMENT Schemes (25 schemes)

```
Generate 25 government employment schemes in JSON array format. Each scheme must have:
- scheme_id: "SCHEME_XXX" (151-175)
- scheme_code: "EMPLOYMENT_XXX"
- scheme_name: realistic employment scheme name
- scheme_category: "EMPLOYMENT"
- department: "Labour" or "Skill Development"
- natural_language_criteria: 2-4 sentence eligibility criteria
- extracted_rules: array of 3-6 rules

Rule types: AGE (18-45), EMPLOYMENT_STATUS (UNEMPLOYED), EDUCATION_LEVEL, GENDER, CATEGORY, DISTRICT, INCOME_GROUP

Vary: age ranges, employment status, education levels, gender, categories.

Output ONLY JSON array, no explanations.
```

### Batch 8: AGRICULTURE Schemes (25 schemes)

```
Generate 25 government agriculture schemes in JSON array format. Each scheme must have:
- scheme_id: "SCHEME_XXX" (176-200)
- scheme_code: "AGRICULTURE_XXX"
- scheme_name: realistic agriculture scheme name
- scheme_category: "AGRICULTURE"
- department: "Agriculture" or "Rural Development"
- natural_language_criteria: 2-4 sentence eligibility criteria
- extracted_rules: array of 3-6 rules

Rule types: LAND_OWNERSHIP (true), LAND_SIZE (0.5-10 acres), INCOME_GROUP, DISTRICT, BLOCK, VILLAGE, CATEGORY, AGE (18-65)

Vary: land ownership, land sizes, income groups, districts, blocks, villages.

Output ONLY JSON array, no explanations.
```

### Batch 9: Mixed Category Schemes (25 schemes)

```
Generate 25 government schemes across multiple categories in JSON array format. Each scheme must have:
- scheme_id: "SCHEME_XXX" (201-225)
- scheme_code: "CATEGORY_XXX" (mix: PENSION, HEALTH, EDUCATION, HOUSING, FINANCIAL, FOOD, EMPLOYMENT, AGRICULTURE)
- scheme_name: realistic scheme name
- scheme_category: one of the above
- department: appropriate department
- natural_language_criteria: 2-4 sentence eligibility criteria
- extracted_rules: array of 3-6 rules

Use diverse rule combinations: AGE, GENDER, INCOME_GROUP, ANNUAL_INCOME, DISTRICT, STATE, DISABILITY, FAMILY_SIZE, CATEGORY, RATION_CARD, LAND_OWNERSHIP, EDUCATION_LEVEL, EMPLOYMENT_STATUS, MARITAL_STATUS, PRIOR_PARTICIPATION

Vary all rule types and values.

Output ONLY JSON array, no explanations.
```

### Batch 10: Complex Schemes (25 schemes)

```
Generate 25 government schemes with complex eligibility criteria (4-6 rules each) in JSON array format. Each scheme must have:
- scheme_id: "SCHEME_XXX" (226-250)
- scheme_code: "CATEGORY_XXX" (any category)
- scheme_name: realistic scheme name
- scheme_category: any category
- department: appropriate department
- natural_language_criteria: 3-5 sentence eligibility criteria with multiple conditions
- extracted_rules: array of 4-6 rules

Include complex combinations:
- Multiple age ranges (18-60 AND 60+)
- Income AND category requirements
- Geography AND disability requirements
- Prior participation exclusions
- Family size AND income requirements
- Education AND employment status

Output ONLY JSON array, no explanations.
```

### Batches 11-20: Additional Batches (250 more schemes)

**Repeat batches 1-10** with different scheme IDs (251-500) and variations:

**Template for Batch 11-20:**

```
Generate 25 government [CATEGORY] schemes in JSON array format. Each scheme must have:
- scheme_id: "SCHEME_XXX" ([START_ID]-[END_ID])
- scheme_code: "[CATEGORY]_XXX"
- scheme_name: realistic scheme name (different from previous batches)
- scheme_category: "[CATEGORY]"
- department: appropriate department
- natural_language_criteria: 2-4 sentence eligibility criteria (use different phrasing)
- extracted_rules: array of 3-6 rules

Vary: [SPECIFIC_VARIATIONS_FOR_CATEGORY]

Output ONLY JSON array, no explanations.
```

**Example for Batch 11 (PENSION, IDs 251-275):**

```
Generate 25 government pension schemes in JSON array format. Each scheme must have:
- scheme_id: "SCHEME_XXX" (251-275)
- scheme_code: "PENSION_XXX"
- scheme_name: realistic pension scheme name (different from batch 1)
- scheme_category: "PENSION"
- department: "Social Welfare" or "Women & Child Development"
- natural_language_criteria: 2-4 sentence eligibility criteria (use different wording than batch 1)
- extracted_rules: array of 3-6 rules

Rule types: AGE (>=60, vary 60-100), INCOME_GROUP (BPL/APL), STATE (different states), DISABILITY, PRIOR_PARTICIPATION, GENDER, MARITAL_STATUS

Use different age ranges, income thresholds, states, and rule combinations than batch 1.

Output ONLY JSON array, no explanations.
```

---

## Step-by-Step Instructions for Perplexity

### Step 1: Prepare Your Workspace

1. **Create directory structure:**
   ```bash
   mkdir -p ai-ml/use-cases/03_identification_beneficiary/data/training/batches
   ```

2. **Open Perplexity AI:**
   - Go to https://www.perplexity.ai
   - Sign in (if needed)

3. **Open a text editor** to save responses

### Step 2: Generate Batch 1

1. **Copy the Batch 1 prompt** (PENSION schemes) from above
2. **Paste into Perplexity** search box
3. **Click search/submit**
4. **Wait for response** (usually 10-30 seconds)
5. **Copy the JSON response** (look for JSON array `[...]`)
6. **Save to file:** `data/training/batches/batch_01_pension.json`

**Tip:** If Perplexity adds explanations, look for the JSON array in the response and copy only that part.

### Step 3: Generate Remaining Batches

1. **Repeat Step 2** for each batch (2-20)
2. **Save each response** as:
   - `batch_02_health.json`
   - `batch_03_education.json`
   - `batch_04_housing.json`
   - `batch_05_financial.json`
   - `batch_06_food.json`
   - `batch_07_employment.json`
   - `batch_08_agriculture.json`
   - `batch_09_mixed.json`
   - `batch_10_complex.json`
   - `batch_11_pension.json` (repeat with variations)
   - ... continue to `batch_20.json`

### Step 4: Clean Responses (if needed)

If Perplexity adds markdown or explanations, use this script:

```python
import json
import re
from pathlib import Path

def clean_perplexity_response(text: str) -> list:
    """Extract JSON from Perplexity response"""
    
    # Try to find JSON array
    json_match = re.search(r'\[.*\]', text, re.DOTALL)
    if json_match:
        json_str = json_match.group(0)
        try:
            return json.loads(json_str)
        except:
            pass
    
    # Try to parse entire response
    try:
        return json.loads(text)
    except:
        pass
    
    # Try to extract between ```json and ```
    code_block = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if code_block:
        try:
            return json.loads(code_block.group(1))
        except:
            pass
    
    # Try to extract between ``` and ```
    code_block = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
    if code_block:
        try:
            return json.loads(code_block.group(1))
        except:
            pass
    
    return []

# Process all batch files
batch_dir = Path("data/training/batches")
for batch_file in sorted(batch_dir.glob("batch_*.json")):
    with open(batch_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Try to parse as JSON first
    try:
        json.loads(content)
        print(f"✓ {batch_file.name} is already valid JSON")
        continue
    except:
        pass
    
    # Clean and extract JSON
    schemes = clean_perplexity_response(content)
    if schemes:
        with open(batch_file, "w", encoding="utf-8") as f:
            json.dump(schemes, f, indent=2)
        print(f"✓ Cleaned {batch_file.name}: {len(schemes)} schemes")
    else:
        print(f"✗ Failed to extract JSON from {batch_file.name}")
```

### Step 5: Combine All Batches

Run this script to combine all batches:

```python
import json
from pathlib import Path

def combine_batches(batch_dir: str = "data/training/batches", 
                   output_file: str = "data/training/schemes_raw.json"):
    """Combine all batch JSON files into one"""
    
    all_schemes = []
    batch_files = sorted(Path(batch_dir).glob("batch_*.json"))
    
    if not batch_files:
        print(f"No batch files found in {batch_dir}")
        return []
    
    for batch_file in batch_files:
        print(f"Loading {batch_file.name}...")
        try:
            with open(batch_file, "r", encoding="utf-8") as f:
                schemes = json.load(f)
                if isinstance(schemes, list):
                    all_schemes.extend(schemes)
                    print(f"  ✓ Added {len(schemes)} schemes")
                else:
                    print(f"  ✗ Warning: {batch_file.name} is not a JSON array")
        except json.JSONDecodeError as e:
            print(f"  ✗ Error parsing {batch_file.name}: {e}")
        except Exception as e:
            print(f"  ✗ Error reading {batch_file.name}: {e}")
    
    # Save combined
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_schemes, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Combined {len(all_schemes)} schemes into {output_file}")
    return all_schemes

if __name__ == "__main__":
    combine_batches()
```

**Run the script:**
```bash
cd ai-ml/use-cases/03_identification_beneficiary
python scripts/combine_batches.py
```

### Step 6: Validate Data

Run validation script:

```python
import json
from pathlib import Path

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

def validate_scheme(scheme: dict) -> list:
    """Validate a single scheme"""
    errors = []
    
    # Check required fields
    required = ["scheme_id", "scheme_code", "scheme_name", 
                "natural_language_criteria", "extracted_rules"]
    for field in required:
        if field not in scheme:
            errors.append(f"Missing required field: {field}")
    
    # Validate rules
    if "extracted_rules" in scheme:
        rules = scheme["extracted_rules"]
        if not isinstance(rules, list):
            errors.append("extracted_rules must be array")
        elif len(rules) < 3:
            errors.append("Need at least 3 rules")
        else:
            for i, rule in enumerate(rules):
                if "rule_type" not in rule:
                    errors.append(f"Rule {i+1} missing rule_type")
                elif rule["rule_type"] not in VALID_RULE_TYPES:
                    errors.append(f"Rule {i+1} invalid rule_type: {rule['rule_type']}")
                
                if "operator" in rule and rule["operator"] not in VALID_OPERATORS:
                    errors.append(f"Rule {i+1} invalid operator: {rule['operator']}")
    
    return errors

def validate_dataset(filepath: str) -> dict:
    """Validate entire dataset"""
    with open(filepath, "r", encoding="utf-8") as f:
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

if __name__ == "__main__":
    result = validate_dataset("data/training/schemes_raw.json")
    
    print(f"\nValidation Results:")
    print(f"Total schemes: {result['total']}")
    print(f"Valid: {result['valid']}")
    print(f"Invalid: {result['invalid']}")
    
    if result['errors']:
        print(f"\nFirst 10 errors:")
        for err in result['errors'][:10]:
            print(f"  {err['scheme_code']}: {', '.join(err['errors'])}")
```

**Run validation:**
```bash
python scripts/validate_training_data.py
```

### Step 7: Fix Common Issues

If validation finds errors, use this fix script:

```python
import json
from pathlib import Path

def fix_missing_fields(scheme: dict) -> dict:
    """Fix common missing fields"""
    
    # Add default department if missing
    if "department" not in scheme:
        category = scheme.get("scheme_category", "GENERAL")
        departments = {
            "PENSION": "Social Welfare",
            "HEALTH": "Health",
            "EDUCATION": "Education",
            "HOUSING": "Housing",
            "FINANCIAL": "Finance",
            "FOOD": "Food & Civil Supplies",
            "EMPLOYMENT": "Labour",
            "AGRICULTURE": "Agriculture"
        }
        scheme["department"] = departments.get(category, "General")
    
    # Ensure confidence in rules
    if "extracted_rules" in scheme:
        for rule in scheme["extracted_rules"]:
            if "confidence" not in rule:
                rule["confidence"] = 1.0
            if "rule_type_category" not in rule:
                rule["rule_type_category"] = "MANDATORY"
    
    return scheme

def fix_dataset(filepath: str):
    """Fix common issues in dataset"""
    with open(filepath, "r", encoding="utf-8") as f:
        schemes = json.load(f)
    
    fixed = [fix_missing_fields(s) for s in schemes]
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(fixed, f, indent=2, ensure_ascii=False)
    
    print(f"Fixed {len(fixed)} schemes")

if __name__ == "__main__":
    fix_dataset("data/training/schemes_raw.json")
```

### Step 8: Create Train/Val/Test Splits

```python
import json
import random
from pathlib import Path

def split_dataset(input_file: str, 
                 train_ratio: float = 0.7,
                 val_ratio: float = 0.15,
                 test_ratio: float = 0.15):
    """Split dataset into train/val/test"""
    
    with open(input_file, "r", encoding="utf-8") as f:
        schemes = json.load(f)
    
    # Shuffle
    random.seed(42)  # For reproducibility
    random.shuffle(schemes)
    
    # Calculate splits
    n = len(schemes)
    train_end = int(n * train_ratio)
    val_end = train_end + int(n * val_ratio)
    
    train = schemes[:train_end]
    val = schemes[train_end:val_end]
    test = schemes[val_end:]
    
    # Save splits
    output_dir = Path("data/training")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "train.json", "w", encoding="utf-8") as f:
        json.dump(train, f, indent=2, ensure_ascii=False)
    
    with open(output_dir / "val.json", "w", encoding="utf-8") as f:
        json.dump(val, f, indent=2, ensure_ascii=False)
    
    with open(output_dir / "test.json", "w", encoding="utf-8") as f:
        json.dump(test, f, indent=2, ensure_ascii=False)
    
    print(f"Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")

if __name__ == "__main__":
    split_dataset("data/training/schemes_raw.json")
```

---

## Quick Reference: All Batch Prompts

| Batch | Category | Scheme IDs | File Name |
|-------|----------|------------|-----------|
| 1 | PENSION | 001-025 | `batch_01_pension.json` |
| 2 | HEALTH | 026-050 | `batch_02_health.json` |
| 3 | EDUCATION | 051-075 | `batch_03_education.json` |
| 4 | HOUSING | 076-100 | `batch_04_housing.json` |
| 5 | FINANCIAL | 101-125 | `batch_05_financial.json` |
| 6 | FOOD | 126-150 | `batch_06_food.json` |
| 7 | EMPLOYMENT | 151-175 | `batch_07_employment.json` |
| 8 | AGRICULTURE | 176-200 | `batch_08_agriculture.json` |
| 9 | MIXED | 201-225 | `batch_09_mixed.json` |
| 10 | COMPLEX | 226-250 | `batch_10_complex.json` |
| 11-20 | Various | 251-500 | `batch_11.json` to `batch_20.json` |

---

## Troubleshooting

### Issue: Perplexity adds explanations

**Solution:** 
1. Look for JSON array `[...]` in the response
2. Copy only the JSON part
3. Or use the `clean_perplexity_response()` script above

### Issue: JSON format errors

**Solution:** 
1. Use the cleaning script (Step 4)
2. Manually fix any syntax errors
3. Validate using validation script

### Issue: Missing fields

**Solution:** 
1. Run the fix script (Step 7)
2. Manually add missing fields if needed

### Issue: Not enough schemes

**Solution:**
1. Generate additional batches (21-25)
2. Or regenerate batches with fewer schemes per batch

---

## Token Usage Summary

- **20 batches × 25 schemes = 500 schemes**
- **~2,000-3,000 tokens per batch**
- **Total: ~50,000-75,000 tokens** (much less than generating one-by-one!)

---

## Next Steps

After generating all batches:

1. ✅ **Combine batches** → `schemes_raw.json`
2. ✅ **Validate data** → Fix any errors
3. ✅ **Create splits** → `train.json`, `val.json`, `test.json`
4. ✅ **Proceed to training** → See `NLP_MODEL_TRAINING_GUIDE.md`

---

**Document Version:** 1.0  
**Last Updated:** 2024-12-30  
**Status:** ✅ Ready for Perplexity Generation

