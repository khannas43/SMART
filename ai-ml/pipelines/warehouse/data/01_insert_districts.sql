-- Rajasthan Districts Master Data (33 districts)
-- Population and area data based on Rajasthan census

INSERT INTO districts (district_code, district_name, population, area_sqkm, is_urban) VALUES
('AJM', 'Ajmer', 2583052, 8481, false),
('ALW', 'Alwar', 3674179, 8380, false),
('BAN', 'Banswara', 1797485, 5037, false),
('BAR', 'Baran', 1222755, 6955, false),
('BARM', 'Barmer', 2603751, 28387, false),
('BHA', 'Bharatpur', 2548462, 5066, false),
('BHI', 'Bhilwara', 2408523, 10455, false),
('BIK', 'Bikaner', 2363937, 30247, false),
('BUN', 'Bundi', 1110906, 5550, false),
('CHI', 'Chittorgarh', 1544338, 7822, false),
('CHU', 'Churu', 2039547, 16393, false),
('DAU', 'Dausa', 1634409, 3429, false),
('DHO', 'Dholpur', 1206516, 3084, false),
('DUN', 'Dungarpur', 1388552, 3770, false),
('GAN', 'Ganganagar', 1969168, 10989, false),
('HAN', 'Hanumangarh', 1774692, 9670, false),
('JAI', 'Jaipur', 6626178, 11143, true), -- 12% of state population
('JAL', 'Jalore', 1830151, 10640, false),
('JOD', 'Jodhpur', 3687165, 22850, false), -- 8% of state population
('KAR', 'Karauli', 1458248, 5530, false),
('KOT', 'Kota', 1951014, 5217, false),
('NAG', 'Nagaur', 3307743, 17718, false),
('PAL', 'Pali', 2037573, 12387, false),
('PRAT', 'Pratapgarh', 867848, 4117, false),
('RAJ', 'Rajsamand', 1156597, 4768, false),
('SAWA', 'Sawai Madhopur', 1335551, 4500, false),
('SIK', 'Sikar', 2677333, 7732, false),
('SIRO', 'Sirohi', 1036346, 5136, false),
('TON', 'Tonk', 1421326, 7194, false),
('UDAI', 'Udaipur', 3068420, 17279, false),
('JHU', 'Jhunjhunu', 2137045, 5928, false),
('JUN', 'Jaisalmer', 669919, 38401, false),
('SRI', 'Sri Ganganagar', 1969168, 10989, false)
ON CONFLICT (district_code) DO NOTHING;

