# SMART Rajasthan Master Data Foundation

This directory contains master data tables and synthetic data generation scripts for the SMART Rajasthan platform.

## Master Tables Created

### Core Masters
1. **districts** - 33 Rajasthan districts with population data
2. **castes** - GEN/OBC/SC/ST categories with sub-categories
3. **scheme_categories** - Health, Education, Housing, etc.
4. **education_levels** - Illiterate to Technical/Professional
5. **employment_types** - Unemployed to Government Employee
6. **house_types** - Kutcha, Semi-Pucca, Pucca

### Schemes & Eligibility
7. **schemes** - 12 real Rajasthan government schemes with eligibility criteria
8. **scheme_eligibility_criteria** - Detailed eligibility rules

### Transactional Data
9. **citizens** - 100,000 synthetic Rajasthan citizens
10. **applications** - 50,000 citizen-scheme application pairs

## Data Distributions

### Rajasthan-Specific Realistic Distributions:

**Districts:**
- Jaipur: 12% of population
- Jodhpur: 8% of population
- Rural: 75% of total population
- Urban: 25% of total population

**Income:**
- 60% below ₹2 lakhs annually
- 30% between ₹2-5 lakhs
- 10% above ₹5 lakhs

**Caste:**
- GEN (General): 40%
- OBC: 29%
- SC: 18%
- ST: 13%
- **Total SC/ST: 31%**

**Age:**
- Peak distribution: 18-60 years (80%)
- Below 18: 5%
- Above 60: 15%

**Other Demographics:**
- Gender: Male 52%, Female 48%
- BPL Card holders: Correlated with income (60% <2L likely BPL)
- Farmers: 40% in rural areas
- Disabled: 3%

## Files

### Schema
- `../schemas/02_master_tables.sql` - Master tables schema

### Data Files
- `01_insert_districts.sql` - 33 districts
- `02_insert_castes.sql` - Caste master data
- `03_insert_scheme_categories.sql` - Scheme categories
- `04_insert_education_levels.sql` - Education levels
- `05_insert_employment_types.sql` - Employment types
- `06_insert_house_types.sql` - House types
- `07_insert_schemes.sql` - 12 Rajasthan schemes
- `08_insert_citizens.sql` - 100K citizens (18MB)
- `09_insert_applications.sql` - 50K applications (6.3MB)

### Generated Files
- `citizens_100k.csv` - Citizens data in CSV format (13MB)

### Scripts
- `generate_citizens.py` - Python script to generate 100K citizens
- `generate_applications.py` - Python script to generate 50K applications
- `load_all_master_data.sh` - Bash script to load all data
- `load_all_master_data.sql` - SQL script to load all data

## Loading Data

### Option 1: Automated Script (Recommended)

```bash
cd /mnt/c/Projects/SMART/ai-ml/pipelines/warehouse/data
bash load_all_master_data.sh
```

### Option 2: Manual Loading

```bash
export PGPASSWORD="anjali143"
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse

-- Create tables first
\i ../schemas/02_master_tables.sql

-- Load master data
\i 01_insert_districts.sql
\i 02_insert_castes.sql
\i 03_insert_scheme_categories.sql
\i 04_insert_education_levels.sql
\i 05_insert_employment_types.sql
\i 06_insert_house_types.sql
\i 07_insert_schemes.sql
\i 08_insert_citizens.sql
\i 09_insert_applications.sql
```

## Regenerating Data

If you need to regenerate citizens or applications:

```bash
# Generate 100K citizens
python3 generate_citizens.py

# Generate 50K applications
python3 generate_applications.py
```

## Verification

After loading, verify data:

```sql
-- Count records
SELECT 'districts' as table_name, count(*) FROM districts
UNION ALL SELECT 'castes', count(*) FROM castes
UNION ALL SELECT 'schemes', count(*) FROM schemes
UNION ALL SELECT 'citizens', count(*) FROM citizens
UNION ALL SELECT 'applications', count(*) FROM applications;

-- Expected:
-- districts: 33
-- castes: ~32
-- schemes: 12
-- citizens: 100,000
-- applications: 50,000
```

## 12 Rajasthan Schemes Included

1. Mukhyamantri Chiranjeevi Yojana (Health Insurance)
2. Mukhyamantri Vishesh Labh Yojana (Education)
3. Mukhyamantri Gramin Awas Yojana (Rural Housing)
4. SC/ST Post Matric Scholarship
5. Kisan Credit Card Scheme
6. Mukhyamantri Mahila Shakti Nidhi (Women)
7. Disability Pension Scheme
8. Old Age Pension
9. Mahatma Gandhi NREGA
10. BPL Family Assistance
11. Tribal Welfare Scheme
12. OBC Post Matric Scholarship

## Data Quality

- All data follows Rajasthan demographic distributions
- Relationships maintained (citizens → districts, castes, etc.)
- Realistic eligibility scores for applications
- Proper foreign key constraints
- Jan Aadhaar numbers generated (12-digit unique IDs)
- Application numbers follow standard format

## Notes

- Citizens data includes calculated age from date_of_birth
- Applications include eligibility scores (0-100) for ML training
- Income, education, and employment are correlated for realism
- BPL status correlated with income distribution
- Rural/urban split maintained at 75/25

