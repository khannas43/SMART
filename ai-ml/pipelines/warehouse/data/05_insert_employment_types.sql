-- Employment Types Master Data

INSERT INTO employment_types (type_code, type_name, description) VALUES
('UNEMPLOYED', 'Unemployed', 'Not currently employed'),
('CASUAL', 'Casual Labor', 'Daily wage or casual labor'),
('SELF_EMP', 'Self Employed', 'Self-employed or own business'),
('AGRICULTURE', 'Agriculture', 'Farming or agricultural work'),
('REGULAR', 'Regular Job', 'Permanent or regular employment'),
('GOVT', 'Government Employee', 'Government or public sector employee'),
('PRIVATE', 'Private Employee', 'Private sector employee'),
('STUDENT', 'Student', 'Currently studying'),
('HOUSEWIFE', 'Housewife', 'Homemaker'),
('RETIRED', 'Retired', 'Retired from employment')
ON CONFLICT (type_code) DO NOTHING;

