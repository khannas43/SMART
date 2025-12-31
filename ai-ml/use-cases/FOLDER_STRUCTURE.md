# Use Cases Folder Structure

## Naming Convention

All use case folders follow this naming pattern:
- `XX_use_case_name` where:
  - `XX` = Zero-padded number (01, 02, 03, ...)
  - `use_case_name` = Descriptive name in lowercase with underscores

## Current Use Cases

```
use-cases/
├── 01_golden_record/                    # AI-PLATFORM-01
│   ├── config/
│   ├── data/
│   ├── docs/
│   ├── models/
│   ├── notebooks/
│   ├── scripts/
│   ├── src/
│   └── README.md
│
└── 02_eligibility_scoring_360_profile/  # AI-PLATFORM-02
    ├── config/
    ├── database/
    ├── data/
    ├── docs/
    ├── models/
    ├── notebooks/
    ├── scripts/
    ├── src/
    ├── spring_boot/
    └── README.md
```

## Folder Organization Rules

1. **Numbering**: Sequential, zero-padded (01, 02, 03, ...)
2. **Naming**: Lowercase with underscores
3. **Descriptive**: Name should clearly indicate use case purpose
4. **Consistent**: All folders follow same structure (see README.md)

## Migration Notes

- `golden_record` → `01_golden_record` ✅
- `eligibility_scoring_360_profile` → `02_eligibility_scoring_360_profile` ✅
- `ai_platform_02` → Merged into `02_eligibility_scoring_360_profile` ✅

---

**Last Updated**: 2024-12-27

