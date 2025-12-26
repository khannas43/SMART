#!/usr/bin/env python3
"""
Generate 100K synthetic Rajasthan citizens with realistic distributions
Generates INSERT statements and CSV files
"""

import random
import csv
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

# Rajasthan-specific distributions
DISTRICT_DISTRIBUTION = {
    'Jaipur': 0.12,      # 12%
    'Jodhpur': 0.08,     # 8%
    'Udaipur': 0.07,
    'Ajmer': 0.05,
    'Alwar': 0.05,
    'Sikar': 0.05,
    'Nagaur': 0.05,
    'Bhilwara': 0.04,
    'Other': 0.49        # Remaining 33 districts
}

CASTE_DISTRIBUTION = {
    'GEN': 0.40,  # 40%
    'OBC': 0.29,  # 29%
    'SC': 0.18,   # 18%
    'ST': 0.13    # 13% (total SC+ST = 31%)
}

INCOME_DISTRIBUTION = {
    'low': (50000, 200000, 0.60),      # 60% below 2L
    'medium': (200000, 500000, 0.30),  # 30% between 2L-5L
    'high': (500000, 2000000, 0.10)    # 10% above 5L
}

GENDER_DISTRIBUTION = {'Male': 0.52, 'Female': 0.48}

# Age distribution (peak 18-60)
def generate_age():
    """Generate age with peak in 18-60 range"""
    rand = random.random()
    if rand < 0.05:  # 5% below 18
        return random.randint(1, 17)
    elif rand < 0.85:  # 80% between 18-60
        return random.randint(18, 60)
    else:  # 15% above 60
        return random.randint(61, 85)

# First names (Rajasthani/Hindi)
MALE_NAMES = [
    'Ram', 'Shyam', 'Krishna', 'Vishnu', 'Ramesh', 'Suresh', 'Mahesh', 'Rajesh',
    'Amit', 'Ankit', 'Arjun', 'Ravi', 'Kumar', 'Lal', 'Dev', 'Om', 'Yash',
    'Rahul', 'Aman', 'Vikas', 'Pankaj', 'Naresh', 'Mukesh', 'Dinesh'
]

FEMALE_NAMES = [
    'Priya', 'Rekha', 'Sunita', 'Kavita', 'Neeta', 'Geeta', 'Sita', 'Radha',
    'Anita', 'Meera', 'Pooja', 'Deepika', 'Anjali', 'Kiran', 'Madhu', 'Sarita',
    'Jyoti', 'Shanti', 'Kamla', 'Usha', 'Rama', 'Leela', 'Maya', 'Asha'
]

LAST_NAMES = [
    'Kumar', 'Singh', 'Sharma', 'Verma', 'Yadav', 'Gupta', 'Meena', 'Kumawat',
    'Meghwal', 'Jain', 'Rajput', 'Gurjar', 'Jat', 'Khatik', 'Choudhary', 'Patel',
    'Shekhawat', 'Rathore', 'Chauhan', 'Tanwar', 'Saini', 'Bohra', 'Modi', 'Garg'
]

def generate_jan_aadhaar():
    """Generate 12-digit Jan Aadhaar number"""
    return ''.join([str(random.randint(0, 9)) for _ in range(12)])

def generate_date_of_birth(age):
    """Generate date of birth from age"""
    today = datetime.now()
    birth_year = today.year - age
    birth_date = datetime(birth_year, random.randint(1, 12), random.randint(1, 28))
    return birth_date.date()

def generate_income():
    """Generate family income based on distribution"""
    rand = random.random()
    if rand < 0.60:  # 60% below 2L
        return random.randint(50000, 200000)
    elif rand < 0.90:  # 30% between 2L-5L
        return random.randint(200000, 500000)
    else:  # 10% above 5L
        return random.randint(500000, 2000000)

def get_district_id(district_name, district_map):
    """Get district_id from district name"""
    # Map actual district names to codes
    district_code_map = {
        'Jaipur': 'JAI', 'Jodhpur': 'JOD', 'Udaipur': 'UDAI',
        'Ajmer': 'AJM', 'Alwar': 'ALW', 'Sikar': 'SIK',
        'Nagaur': 'NAG', 'Bhilwara': 'BHI'
    }
    if district_name in district_code_map:
        return district_map.get(district_code_map[district_name], 1)
    return random.randint(1, 33)  # Other districts

def get_caste_id(caste_category, caste_map):
    """Get caste_id based on category"""
    # Sample a caste from the category
    category_castes = [c for c, cat in caste_map.items() if cat == caste_category]
    if category_castes:
        caste_code = random.choice(category_castes)
        return caste_map.get(caste_code, 1)
    return 1

def generate_citizen_data(num_citizens, district_map, caste_map):
    """Generate citizen data"""
    citizens = []
    
    # District distribution (Jaipur 12%, Jodhpur 8%, etc.)
    district_weights = list(DISTRICT_DISTRIBUTION.values())
    district_names = list(DISTRICT_DISTRIBUTION.keys())
    
    for i in range(1, num_citizens + 1):
        # Gender
        gender = random.choices(
            list(GENDER_DISTRIBUTION.keys()),
            weights=list(GENDER_DISTRIBUTION.values())
        )[0]
        
        # Name
        if gender == 'Male':
            first_name = random.choice(MALE_NAMES)
        else:
            first_name = random.choice(FEMALE_NAMES)
        
        middle_name = random.choice(MALE_NAMES) if random.random() < 0.3 else None
        last_name = random.choice(LAST_NAMES)
        
        # Age and DOB
        age = generate_age()
        date_of_birth = generate_date_of_birth(age)
        
        # District (Jaipur 12%, Jodhpur 8%, rural 75%)
        district_name = random.choices(district_names, weights=district_weights)[0]
        district_id = get_district_id(district_name, district_map)
        is_urban = district_name in ['Jaipur', 'Jodhpur'] and random.random() < 0.4
        
        # Caste (SC/ST 31%)
        caste_category = random.choices(
            list(CASTE_DISTRIBUTION.keys()),
            weights=list(CASTE_DISTRIBUTION.values())
        )[0]
        caste_id = get_caste_id(caste_category, caste_map)
        
        # Income (60% <2L)
        family_income = generate_income()
        
        # Education (correlated with age and income)
        if age < 18:
            education_id = random.randint(1, 3)  # Primary to Middle
        elif family_income < 200000:
            education_id = random.randint(1, 6)  # Illiterate to Diploma
        else:
            education_id = random.randint(4, 9)  # Secondary to Technical
        
        # Employment
        if age < 18:
            employment_id = 8  # Student
        elif age > 60:
            employment_id = 10  # Retired
        elif gender == 'Female' and random.random() < 0.3:
            employment_id = 9  # Housewife
        else:
            if family_income < 200000:
                employment_id = random.choice([1, 2, 3, 4])  # Unemployed, Casual, Self, Agriculture
            else:
                employment_id = random.choice([2, 5, 6, 7])  # Casual, Regular, Govt, Private
        
        # Family size (2-8, average 4)
        family_size = random.choices([2, 3, 4, 5, 6, 7, 8], weights=[5, 10, 30, 25, 15, 10, 5])[0]
        
        # BPL (correlated with income - 60% <2L are likely BPL)
        bpl_card = family_income < 200000 and random.random() < 0.7
        
        # House type (correlated with income)
        if family_income < 150000:
            house_type_id = random.choice([1, 2])  # Kutcha or Semi-Pucca
        elif family_income < 300000:
            house_type_id = random.choice([2, 3])  # Semi-Pucca or Pucca
        else:
            house_type_id = 3  # Pucca
        
        # Farmer (rural areas more likely)
        farmer = not is_urban and random.random() < 0.4
        
        # Contact
        mobile_number = ''.join([str(random.randint(6, 9))] + [str(random.randint(0, 9)) for _ in range(9)])
        
        # Jan Aadhaar
        jan_aadhaar = generate_jan_aadhaar()
        aadhaar = generate_jan_aadhaar() if random.random() < 0.8 else None
        
        citizen = {
            'jan_aadhaar': jan_aadhaar,
            'aadhaar_number': aadhaar,
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'date_of_birth': date_of_birth,
            'gender': gender,
            'district_id': district_id,
            'city_village': f"{'City' if is_urban else 'Village'} {random.randint(1, 100)}",
            'pincode': str(random.randint(300000, 349999)),
            'is_urban': is_urban,
            'caste_id': caste_id,
            'family_income': family_income,
            'family_size': family_size,
            'education_id': education_id,
            'employment_id': employment_id,
            'bpl_card': bpl_card,
            'house_type_id': house_type_id,
            'farmer': farmer,
            'disabled': random.random() < 0.03,  # 3% disabled
            'mobile_number': mobile_number,
            'status': 'active'
        }
        
        citizens.append(citizen)
    
    return citizens

def write_insert_sql(citizens, output_file):
    """Write INSERT statements to SQL file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- 100K Synthetic Rajasthan Citizens\n")
        f.write("-- Generated with realistic distributions\n\n")
        
        # Batch insert in chunks of 1000
        batch_size = 1000
        for i in range(0, len(citizens), batch_size):
            batch = citizens[i:i+batch_size]
            f.write("INSERT INTO citizens (\n")
            f.write("    jan_aadhaar, aadhaar_number, first_name, middle_name, last_name,\n")
            f.write("    date_of_birth, gender, district_id, city_village, pincode, is_urban,\n")
            f.write("    caste_id, family_income, family_size, education_id, employment_id,\n")
            f.write("    bpl_card, house_type_id, farmer, disabled, mobile_number, status\n")
            f.write(") VALUES\n")
            
            values = []
            for c in batch:
                middle_name_val = f"'{c['middle_name']}'" if c['middle_name'] else 'NULL'
                aadhaar_val = f"'{c['aadhaar_number']}'" if c['aadhaar_number'] else 'NULL'
                
                val = f"('{c['jan_aadhaar']}', {aadhaar_val}, '{c['first_name']}', {middle_name_val}, '{c['last_name']}', "
                val += f"'{c['date_of_birth']}', '{c['gender']}', {c['district_id']}, '{c['city_village']}', "
                val += f"'{c['pincode']}', {str(c['is_urban']).upper()}, {c['caste_id']}, {c['family_income']}, "
                val += f"{c['family_size']}, {c['education_id']}, {c['employment_id']}, {str(c['bpl_card']).upper()}, "
                val += f"{c['house_type_id']}, {str(c['farmer']).upper()}, {str(c['disabled']).upper()}, "
                val += f"'{c['mobile_number']}', '{c['status']}')"
                values.append(val)
            
            f.write(',\n'.join(values))
            f.write(';\n\n')

def write_csv(citizens, output_file):
    """Write citizens to CSV file"""
    fieldnames = [
        'jan_aadhaar', 'aadhaar_number', 'first_name', 'middle_name', 'last_name',
        'date_of_birth', 'gender', 'district_id', 'city_village', 'pincode', 'is_urban',
        'caste_id', 'family_income', 'family_size', 'education_id', 'employment_id',
        'bpl_card', 'house_type_id', 'farmer', 'disabled', 'mobile_number', 'status'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for c in citizens:
            writer.writerow(c)

def main():
    # These would be loaded from database in real scenario
    # For now, using reasonable defaults
    district_map = {'JAI': 17, 'JOD': 19, 'UDAI': 30, 'AJM': 1, 'ALW': 2, 'SIK': 27, 'NAG': 22, 'BHI': 7}
    caste_map = {
        'GEN_RAJPUT': 1, 'GEN_BRAHMIN': 2, 'GEN_JAIN': 3, 'GEN_VAISHYA': 4,
        'OBC_JAT': 9, 'OBC_GUJJAR': 10, 'OBC_MEENA': 11,
        'SC_MEGHWAL': 17, 'SC_CHAMAR': 18, 'SC_KOLI': 19,
        'ST_BHIL': 25, 'ST_MINAS': 26, 'ST_DAMOR': 27
    }
    
    print("Generating 100K synthetic Rajasthan citizens...")
    citizens = generate_citizen_data(100000, district_map, caste_map)
    
    output_dir = Path(__file__).parent
    sql_file = output_dir / '08_insert_citizens.sql'
    csv_file = output_dir / 'citizens_100k.csv'
    
    print(f"Writing SQL INSERT statements to {sql_file}...")
    write_insert_sql(citizens, sql_file)
    
    print(f"Writing CSV file to {csv_file}...")
    write_csv(citizens, csv_file)
    
    print(f"\n✅ Generated {len(citizens)} citizens")
    print(f"   - SQL: {sql_file}")
    print(f"   - CSV: {csv_file}")

if __name__ == '__main__':
    main()

