-- House Types Master Data

INSERT INTO house_types (type_code, type_name, description) VALUES
('KUTCHA', 'Kutcha', 'Mud or temporary house structure'),
('SEMI_PUCCA', 'Semi Pucca', 'Partially constructed permanent house'),
('PUCCA', 'Pucca', 'Fully constructed permanent house'),
('NO_HOUSE', 'No House', 'Does not own a house'),
('RENTED', 'Rented', 'Living in rented accommodation')
ON CONFLICT (type_code) DO NOTHING;

