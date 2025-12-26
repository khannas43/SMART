-- Education Levels Master Data

INSERT INTO education_levels (level_code, level_name, level_order, description) VALUES
('ILLITERATE', 'Illiterate', 1, 'No formal education'),
('PRIMARY', 'Primary (1-5)', 2, 'Completed primary education'),
('MIDDLE', 'Middle (6-8)', 3, 'Completed middle school'),
('SECONDARY', 'Secondary (9-10)', 4, 'Completed secondary education'),
('SENIOR_SEC', 'Senior Secondary (11-12)', 5, 'Completed higher secondary'),
('DIPLOMA', 'Diploma', 6, 'Diploma or certificate course'),
('GRADUATE', 'Graduate', 7, 'Bachelor degree'),
('POST_GRAD', 'Post Graduate', 8, 'Master degree or higher'),
('TECHNICAL', 'Technical/Professional', 9, 'Technical or professional degree')
ON CONFLICT (level_code) DO NOTHING;

