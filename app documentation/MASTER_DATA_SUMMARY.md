# SMART Rajasthan Master Data Foundation - Summary

## ✅ Completed

All master tables and synthetic data have been created for the SMART Rajasthan platform.

## Master Tables Created (10 tables)

### Core Masters (6 tables)
1. ✅ **districts** - 33 Rajasthan districts with population
2. ✅ **castes** - GEN/OBC/SC/ST with realistic distribution (40%/29%/18%/13%)
3. ✅ **scheme_categories** - Health, Education, Housing, etc.
4. ✅ **education_levels** - Illiterate to Technical/Professional
5. ✅ **employment_types** - Unemployed to Government Employee
6. ✅ **house_types** - Kutcha, Semi-Pucca, Pucca

### Schemes & Eligibility (2 tables)
7. ✅ **schemes** - 12 real Rajasthan government schemes
8. ✅ **scheme_eligibility_criteria** - Detailed eligibility rules

### Transactional Data (2 tables)
9. ✅ **citizens** - 100,000 synthetic Rajasthan citizens
10. ✅ **applications** - 50,000 citizen-scheme application pairs

## Data Generated

### Rajasthan-Specific Distributions:
- ✅ **Districts**: Jaipur 12%, Jodhpur 8%, rural 75%
- ✅ **Income**: 60% below ₹2 lakhs
- ✅ **Caste**: SC/ST 31% (18% SC + 13% ST)
- ✅ **Age**: Peak 18-60 years (80%)
- ✅ **Gender**: Male 52%, Female 48%

### Files Generated:
- **Schema**: `02_master_tables.sql` (master tables definition)
- **Master Data**: 7 SQL files with reference data
- **Citizens**: 100K records (18MB SQL, 13MB CSV)
- **Applications**: 50K records (6.3MB SQL)

**Total Data**: ~38MB

## Files Location

```
ai-ml/pipelines/warehouse/
├── schemas/
│   └── 02_master_tables.sql          # Master tables schema
└── data/
    ├── 01_insert_districts.sql       # 33 districts
    ├── 02_insert_castes.sql          # Castes
    ├── 03_insert_scheme_categories.sql
    ├── 04_insert_education_levels.sql
    ├── 05_insert_employment_types.sql
    ├── 06_insert_house_types.sql
    ├── 07_insert_schemes.sql         # 12 schemes
    ├── 08_insert_citizens.sql        # 100K citizens (18MB)
    ├── 09_insert_applications.sql    # 50K applications (6.3MB)
    ├── citizens_100k.csv             # CSV export (13MB)
    ├── generate_citizens.py          # Generator script
    ├── generate_applications.py      # Generator script
    ├── load_all_master_data.sh       # Load script
    └── README.md                     # Documentation
```

## Loading Data

To load all data into `smart_warehouse` database:

```bash
cd /mnt/c/Projects/SMART/ai-ml/pipelines/warehouse/data
bash load_all_master_data.sh
```

## 12 Rajasthan Schemes Included

1. Mukhyamantri Chiranjeevi Yojana (Health)
2. Mukhyamantri Vishesh Labh Yojana (Education)
3. Mukhyamantri Gramin Awas Yojana (Housing)
4. SC/ST Post Matric Scholarship
5. Kisan Credit Card Scheme
6. Mukhyamantri Mahila Shakti Nidhi (Women)
7. Disability Pension Scheme
8. Old Age Pension
9. Mahatma Gandhi NREGA
10. BPL Family Assistance
11. Tribal Welfare Scheme
12. OBC Post Matric Scholarship

## Next Steps

1. ✅ Master tables schema created
2. ✅ All master data SQL files generated
3. ✅ 100K citizens generated with realistic distributions
4. ✅ 50K applications generated
5. ⏭️ Load data into `smart_warehouse` database
6. ⏭️ Verify data quality
7. ⏭️ Begin ML model training on eligibility scoring

## Commit

To commit all changes:

```bash
git add ai-ml/pipelines/warehouse/schemas/02_master_tables.sql
git add ai-ml/pipelines/warehouse/data/
git commit -m "data: master tables + 100k citizens"
```

