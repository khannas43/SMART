-- 12 Real Rajasthan Government Schemes

INSERT INTO schemes (scheme_code, scheme_name, category_id, description, min_age, max_age, max_income, target_caste, bpl_required, farmer_required, benefit_amount, benefit_type, status) VALUES
-- 1. Health Scheme
('MUKHYAMANTRI_CHIRANJEEVI_YOJANA', 'Mukhyamantri Chiranjeevi Yojana', 
 (SELECT category_id FROM scheme_categories WHERE category_code = 'HEALTH'),
 'Free health insurance up to 5 lakh rupees', NULL, NULL, NULL, NULL, false, false, 500000, 'Health Insurance', 'active'),

-- 2. Education Scheme
('MUKHYAMANTRI_VISHESH_LABH_YOJANA', 'Mukhyamantri Vishesh Labh Yojana',
 (SELECT category_id FROM scheme_categories WHERE category_code = 'EDUCATION'),
 'Financial assistance for meritorious students', 18, 25, 250000, NULL, false, false, 50000, 'Scholarship', 'active'),

-- 3. Housing Scheme
('MUKHYAMANTRI_GRAMIN_AWAS_YOJANA', 'Mukhyamantri Gramin Awas Yojana',
 (SELECT category_id FROM scheme_categories WHERE category_code = 'HOUSING'),
 'Rural housing scheme for BPL families', 21, NULL, 200000, NULL, true, false, 150000, 'Housing Grant', 'active'),

-- 4. SC/ST Scheme
('SC_ST_SCHOLARSHIP', 'SC/ST Post Matric Scholarship',
 (SELECT category_id FROM scheme_categories WHERE category_code = 'EDUCATION'),
 'Scholarship for SC/ST students', 18, 30, 250000, 'SC', false, false, 75000, 'Scholarship', 'active'),

-- 5. Agriculture Scheme
('KISAN_CREDIT_CARD', 'Kisan Credit Card Scheme',
 (SELECT category_id FROM scheme_categories WHERE category_code = 'AGRICULTURE'),
 'Credit facility for farmers', 18, 60, NULL, NULL, false, true, 300000, 'Credit Facility', 'active'),

-- 6. Women Scheme
('MUKHYAMANTRI_MAHILA_SHAKTI_NIDHI', 'Mukhyamantri Mahila Shakti Nidhi',
 (SELECT category_id FROM scheme_categories WHERE category_code = 'WOMEN'),
 'Financial assistance for women entrepreneurs', 18, 55, 300000, NULL, false, false, 100000, 'Financial Aid', 'active'),

-- 7. Disability Scheme
('DISABILITY_PENSION', 'Disability Pension Scheme',
 (SELECT category_id FROM scheme_categories WHERE category_code = 'DISABILITY'),
 'Monthly pension for persons with disabilities', NULL, NULL, 100000, NULL, false, false, 36000, 'Pension', 'active'),

-- 8. Elderly Scheme
('OLD_AGE_PENSION', 'Old Age Pension',
 (SELECT category_id FROM scheme_categories WHERE category_code = 'ELDERLY'),
 'Monthly pension for senior citizens', 60, NULL, 48000, NULL, true, false, 18000, 'Pension', 'active'),

-- 9. Employment Scheme
('MAHATMA_GANDHI_NREGA', 'Mahatma Gandhi NREGA',
 (SELECT category_id FROM scheme_categories WHERE category_code = 'EMPLOYMENT'),
 '100 days guaranteed employment', 18, 60, NULL, NULL, true, false, 25000, 'Employment', 'active'),

-- 10. BPL Scheme
('BPL_FAMILY_ASSISTANCE', 'BPL Family Assistance',
 (SELECT category_id FROM scheme_categories WHERE category_code = 'SOCIAL'),
 'Financial assistance for BPL families', NULL, NULL, 100000, NULL, true, false, 24000, 'Financial Aid', 'active'),

-- 11. ST Scheme
('TRIBAL_WELFARE', 'Tribal Welfare Scheme',
 (SELECT category_id FROM scheme_categories WHERE category_code = 'SOCIAL'),
 'Welfare scheme for tribal communities', 18, 60, 200000, 'ST', false, false, 50000, 'Welfare Grant', 'active'),

-- 12. Education Scheme (OBC)
('OBC_SCHOLARSHIP', 'OBC Post Matric Scholarship',
 (SELECT category_id FROM scheme_categories WHERE category_code = 'EDUCATION'),
 'Scholarship for OBC students', 18, 30, 250000, 'OBC', false, false, 60000, 'Scholarship', 'active')
ON CONFLICT (scheme_code) DO NOTHING;

