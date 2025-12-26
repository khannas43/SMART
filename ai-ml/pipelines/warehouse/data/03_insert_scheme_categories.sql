-- Scheme Categories Master Data

INSERT INTO scheme_categories (category_code, category_name, description) VALUES
('HEALTH', 'Health', 'Health and medical welfare schemes'),
('EDUCATION', 'Education', 'Educational support and scholarship schemes'),
('HOUSING', 'Housing', 'Housing and infrastructure schemes'),
('EMPLOYMENT', 'Employment', 'Employment and skill development schemes'),
('AGRICULTURE', 'Agriculture', 'Agricultural and farmer welfare schemes'),
('SOCIAL', 'Social Welfare', 'Social security and welfare schemes'),
('FINANCIAL', 'Financial Assistance', 'Direct benefit transfer and financial aid'),
('WOMEN', 'Women Empowerment', 'Women and child welfare schemes'),
('DISABILITY', 'Disability Support', 'Schemes for persons with disabilities'),
('ELDERLY', 'Senior Citizen', 'Schemes for elderly citizens')
ON CONFLICT (category_code) DO NOTHING;

