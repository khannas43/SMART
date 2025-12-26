-- Load All Master Data into SMART Warehouse
-- Run this script to populate all master tables
-- Database: smart_warehouse

\echo 'Loading Master Data into SMART Warehouse...'
\echo ''

-- 1. Districts (33 Rajasthan districts)
\echo 'Loading districts...'
\i 01_insert_districts.sql

-- 2. Castes
\echo 'Loading castes...'
\i 02_insert_castes.sql

-- 3. Scheme Categories
\echo 'Loading scheme categories...'
\i 03_insert_scheme_categories.sql

-- 4. Education Levels
\echo 'Loading education levels...'
\i 04_insert_education_levels.sql

-- 5. Employment Types
\echo 'Loading employment types...'
\i 05_insert_employment_types.sql

-- 6. House Types
\echo 'Loading house types...'
\i 06_insert_house_types.sql

-- 7. Schemes (12 Rajasthan schemes)
\echo 'Loading schemes...'
\i 07_insert_schemes.sql

-- 8. Citizens (100K synthetic citizens)
\echo 'Loading 100K citizens...'
\echo 'This may take a few minutes...'
\i 08_insert_citizens.sql

-- 9. Applications (50K applications)
\echo 'Loading 50K applications...'
\i 09_insert_applications.sql

\echo ''
\echo '✅ All master data loaded successfully!'
\echo ''
\echo 'Verification queries:'
\echo 'SELECT count(*) FROM districts; -- Should be 33'
\echo 'SELECT count(*) FROM castes; -- Should be ~32'
\echo 'SELECT count(*) FROM schemes; -- Should be 12'
\echo 'SELECT count(*) FROM citizens; -- Should be 100000'
\echo 'SELECT count(*) FROM applications; -- Should be 50000'

