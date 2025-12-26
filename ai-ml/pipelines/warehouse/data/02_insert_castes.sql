-- Rajasthan Castes Master Data
-- GEN (General) ~40%, OBC ~29%, SC ~18%, ST ~13% (Rajasthan distribution)

INSERT INTO castes (caste_code, caste_name, category) VALUES
-- General Category (~40%)
('GEN_RAJPUT', 'Rajput', 'GEN'),
('GEN_BRAHMIN', 'Brahmin', 'GEN'),
('GEN_JAIN', 'Jain', 'GEN'),
('GEN_VAISHYA', 'Vaishya', 'GEN'),
('GEN_MAHESHWARI', 'Maheshwari', 'GEN'),
('GEN_AGARWAL', 'Agarwal', 'GEN'),
('GEN_KAYASTH', 'Kayasth', 'GEN'),
('GEN_OTHER', 'Other General', 'GEN'),

-- OBC Category (~29%)
('OBC_JAT', 'Jat', 'OBC'),
('OBC_GUJJAR', 'Gurjar/Guijar', 'OBC'),
('OBC_MEENA', 'Meena', 'OBC'),
('OBC_YADAV', 'Yadav', 'OBC'),
('OBC_KOIRI', 'Koiri', 'OBC'),
('OBC_KUMHAR', 'Kumhar', 'OBC'),
('OBC_LOHAR', 'Lohar', 'OBC'),
('OBC_TELI', 'Teli', 'OBC'),
('OBC_OTHER', 'Other OBC', 'OBC'),

-- SC Category (~18%)
('SC_MEGHWAL', 'Meghwal', 'SC'),
('SC_CHAMAR', 'Chamar', 'SC'),
('SC_KOLI', 'Koli', 'SC'),
('SC_BALAI', 'Balai', 'SC'),
('SC_REGAR', 'Regar', 'SC'),
('SC_KHATIK', 'Khatik', 'SC'),
('SC_RAIGAR', 'Raigar', 'SC'),
('SC_OTHER', 'Other SC', 'SC'),

-- ST Category (~13%)
('ST_BHIL', 'Bhil', 'ST'),
('ST_MINAS', 'Minas', 'ST'),
('ST_DAMOR', 'Damor', 'ST'),
('ST_KATHODI', 'Kathodi', 'ST'),
('ST_SAHARIYA', 'Sahariya', 'ST'),
('ST_OTHER', 'Other ST', 'ST')
ON CONFLICT (caste_code) DO NOTHING;

