# Commit Instructions

## Files Created

All master data tables and synthetic data have been generated. To commit:

```bash
cd /mnt/c/Projects/SMART

# Set git identity if not set
git config user.email "your@email.com"
git config user.name "Your Name"

# Stage files
git add ai-ml/pipelines/warehouse/schemas/02_master_tables.sql
git add ai-ml/pipelines/warehouse/data/

# Commit
git commit -m "data: master tables + 100k citizens"
```

## What Was Created

### Schema
- `schemas/02_master_tables.sql` - Master tables schema (10 tables)

### Master Data SQL Files
- `01_insert_districts.sql` - 33 Rajasthan districts
- `02_insert_castes.sql` - Caste master data
- `03_insert_scheme_categories.sql` - Scheme categories
- `04_insert_education_levels.sql` - Education levels
- `05_insert_employment_types.sql` - Employment types
- `06_insert_house_types.sql` - House types
- `07_insert_schemes.sql` - 12 Rajasthan schemes

### Generated Data
- `08_insert_citizens.sql` - 100,000 citizens (18MB)
- `09_insert_applications.sql` - 50,000 applications (6.3MB)
- `citizens_100k.csv` - Citizens CSV (13MB)

### Scripts
- `generate_citizens.py` - Python generator for citizens
- `generate_applications.py` - Python generator for applications
- `load_all_master_data.sh` - Load script
- `load_all_master_data.sql` - SQL load script
- `README.md` - Documentation

**Total: ~38MB of data files**

