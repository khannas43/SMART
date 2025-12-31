"""
Generate 45K Synthetic Rajasthan Records for AI-PLATFORM-02
Creates Golden Records, relationships, benefits, and socio-economic data
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid
import random
import yaml

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class SyntheticDataGenerator:
    """Generate synthetic data for 360° profiles"""
    
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        db_config = self.config['database']
        self.db = DBConnector(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['dbname'],
            user=db_config['user'],
            password=db_config['password']
        )
        self.db.connect()
        
        # Rajasthan distributions
        self.districts = list(range(1, 34))  # 33 districts
        self.castes = {
            'GEN': 0.40, 'OBC': 0.29, 'SC': 0.18, 'ST': 0.13
        }
        self.employment_types = [
            'UNEMPLOYED', 'CASUAL', 'SELF_EMPLOYED', 'REGULAR', 'GOVERNMENT'
        ]
        self.education_levels = [
            'ILLITERATE', 'PRIMARY', 'SECONDARY', 'HIGHER_SECONDARY', 'GRADUATE', 'POST_GRADUATE'
        ]
        self.house_types = ['KUTCHA', 'SEMI_PUCCA', 'PUCCA']
        self.scheme_categories = ['HEALTH', 'FOOD', 'EDUCATION', 'HOUSING', 'SOCIAL_SECURITY', 'LIVELIHOOD']
        
        # Load scheme IDs
        self.scheme_ids = self._load_scheme_ids()
        
    def _load_scheme_ids(self):
        """Load scheme IDs from database"""
        query = "SELECT scheme_id, scheme_code FROM scheme_master WHERE status = 'active'"
        df = self.db.execute_query(query)
        return dict(zip(df['scheme_code'], df['scheme_id']))
    
    def generate_golden_records(self, count=45000):
        """Generate 45K Golden Records"""
        print(f"Generating {count} Golden Records...")
        
        records = []
        family_heads = []  # Track family head gr_ids
        
        for i in range(count):
            # Decide if family head (30% are family heads)
            is_family_head = random.random() < 0.30
            family_id = None
            
            # Generate demographics
            gender = random.choice(['Male', 'Female', 'Other'])
            age = self._generate_age()
            dob = datetime.now() - timedelta(days=age*365 + random.randint(0, 365))
            
            # Generate gr_id first
            gr_id = str(uuid.uuid4())
            
            # Set family_id appropriately
            if is_family_head:
                # Family head: family_id points to their own gr_id (or NULL)
                # For simplicity, use NULL and let members reference the head's gr_id
                family_id = None
                family_heads.append(gr_id)
            else:
                # Family member: join existing family (70% chance)
                if random.random() < 0.70 and family_heads:
                    family_id = random.choice(family_heads)
                # Otherwise, family_id stays NULL (no family)
            
            # Caste distribution
            caste = np.random.choice(
                list(self.castes.keys()), 
                p=list(self.castes.values())
            )
            caste_id = {'GEN': 1, 'OBC': 2, 'SC': 3, 'ST': 4}[caste]
            
            # District (Jaipur 12%, Jodhpur 8%, others)
            if random.random() < 0.12:
                district_id = 1  # Jaipur
            elif random.random() < 0.20:
                district_id = 2  # Jodhpur
            else:
                district_id = random.choice(self.districts)
            
            # Urban/rural (75% rural)
            is_urban = random.random() > 0.75
            
            record = {
                'gr_id': gr_id,
                'family_id': family_id,  # NULL for heads, gr_id of head for members
                'citizen_id': f'RJ{str(i+1).zfill(8)}',
                'jan_aadhaar': f'{random.randint(100000000000, 999999999999)}',
                'full_name': self._generate_name(gender),
                'date_of_birth': dob.date(),
                'age': age,
                'gender': gender,
                'caste_id': caste_id,
                'district_id': district_id,
                'city_village': f'Village_{random.randint(1, 1000)}' if not is_urban else f'City_{random.randint(1, 50)}',
                'pincode': f'{random.randint(300000, 349999)}',
                'is_urban': is_urban,
                'status': 'active',
                'created_at': datetime.now() - timedelta(days=random.randint(0, 3650)),
                'updated_at': datetime.now()
            }
            records.append(record)
            
            if (i + 1) % 5000 == 0:
                print(f"  Generated {i+1}/{count} records...")
        
        df = pd.DataFrame(records)
        print(f"✅ Generated {len(df)} Golden Records")
        return df
    
    def generate_relationships(self, golden_records_df):
        """Generate relationships between Golden Records"""
        print("Generating relationships...")
        
        relationships = []
        gr_by_family = golden_records_df.groupby('family_id')
        
        rel_id = 0
        for family_id, family_members in gr_by_family:
            if family_id is None or len(family_members) < 2:
                continue
            
            members = family_members.to_dict('records')
            family_head = members[0]  # First is family head
            
            # Create relationships within family
            for i, member in enumerate(members[1:], 1):
                # Child relationship
                if member['age'] < family_head['age'] - 15:
                    relationships.append({
                        'from_gr_id': family_head['gr_id'],
                        'to_gr_id': member['gr_id'],
                        'relationship_type': 'CHILD',
                        'is_verified': True,
                        'inference_confidence': 1.0,
                        'source': 'family_structure',
                        'valid_from': member['created_at'].date() if hasattr(member['created_at'], 'date') else datetime.now().date()
                    })
                    relationships.append({
                        'from_gr_id': member['gr_id'],
                        'to_gr_id': family_head['gr_id'],
                        'relationship_type': 'PARENT',
                        'is_verified': True,
                        'inference_confidence': 1.0,
                        'source': 'family_structure',
                        'valid_from': member['created_at'].date() if hasattr(member['created_at'], 'date') else datetime.now().date()
                    })
                
                # Spouse relationship (similar age, opposite gender)
                elif abs(member['age'] - family_head['age']) < 10 and member['gender'] != family_head['gender']:
                    relationships.append({
                        'from_gr_id': family_head['gr_id'],
                        'to_gr_id': member['gr_id'],
                        'relationship_type': 'SPOUSE',
                        'is_verified': True,
                        'inference_confidence': 1.0,
                        'source': 'family_structure',
                        'valid_from': member['created_at'].date() if hasattr(member['created_at'], 'date') else datetime.now().date()
                    })
                    relationships.append({
                        'from_gr_id': member['gr_id'],
                        'to_gr_id': family_head['gr_id'],
                        'relationship_type': 'SPOUSE',
                        'is_verified': True,
                        'inference_confidence': 1.0,
                        'source': 'family_structure',
                        'valid_from': member['created_at'].date() if hasattr(member['created_at'], 'date') else datetime.now().date()
                    })
                
                # Sibling relationship
                else:
                    relationships.append({
                        'from_gr_id': family_head['gr_id'],
                        'to_gr_id': member['gr_id'],
                        'relationship_type': 'SIBLING',
                        'is_verified': True,
                        'inference_confidence': 1.0,
                        'source': 'family_structure',
                        'valid_from': member['created_at'].date() if hasattr(member['created_at'], 'date') else datetime.now().date()
                    })
            
            # Co-residence relationship
            for i in range(len(members)):
                for j in range(i+1, len(members)):
                    # Use the earlier created_at date for valid_from
                    valid_from_date = members[i]['created_at'].date() if hasattr(members[i]['created_at'], 'date') else datetime.now().date()
                    relationships.append({
                        'from_gr_id': members[i]['gr_id'],
                        'to_gr_id': members[j]['gr_id'],
                        'relationship_type': 'CO_RESIDENT',
                        'is_verified': True,
                        'inference_confidence': 1.0,
                        'source': 'family_id_match',
                        'valid_from': valid_from_date
                    })
        
        # Add some co-benefit relationships (people in same schemes)
        print("  Adding co-benefit relationships...")
        benefit_by_gr = {}  # Will be populated when we generate benefits
        
        df = pd.DataFrame(relationships)
        print(f"✅ Generated {len(df)} relationships")
        return df
    
    def generate_benefit_events(self, golden_records_df, count_per_person=3):
        """Generate benefit events (disbursements)"""
        print(f"Generating benefit events (avg {count_per_person} per person)...")
        
        benefits = []
        scheme_list = list(self.scheme_ids.values())
        
        for idx, record in golden_records_df.iterrows():
            # Number of benefits for this person (1-8)
            num_benefits = max(1, int(np.random.poisson(count_per_person)))
            
            for _ in range(num_benefits):
                scheme_id = random.choice(scheme_list)
                
                # Benefit amount based on scheme category
                amount = self._generate_benefit_amount(scheme_id)
                
                # Transaction date (within last 3 years)
                days_ago = random.randint(0, 1095)
                txn_date = datetime.now() - timedelta(days=days_ago)
                
                benefit = {
                    'gr_id': record['gr_id'],
                    'scheme_id': scheme_id,
                    'family_id': record['family_id'],
                    'txn_date': txn_date.date(),
                    'amount': amount,
                    'currency': 'INR',
                    'transaction_type': 'DISBURSEMENT',
                    'instalment_number': random.randint(1, 4) if random.random() < 0.3 else None,
                    'channel': random.choice(['BANK_TRANSFER', 'CASH', 'VOUCHER']),
                    'disbursing_agency': f'Agency_{random.randint(1, 20)}',
                    'transaction_reference': f'TXN{random.randint(100000, 999999)}',
                    'created_at': txn_date
                }
                benefits.append(benefit)
            
            if (idx + 1) % 5000 == 0:
                print(f"  Generated benefits for {idx+1}/{len(golden_records_df)} records...")
        
        df = pd.DataFrame(benefits)
        print(f"✅ Generated {len(df)} benefit events")
        return df
    
    def generate_application_events(self, golden_records_df, scheme_coverage=0.4):
        """Generate application events with eligibility scores"""
        print("Generating application events...")
        
        applications = []
        scheme_list = list(self.scheme_ids.values())
        
        for idx, record in golden_records_df.iterrows():
            # 40% of people have applications
            if random.random() > scheme_coverage:
                continue
            
            # Number of applications (1-5)
            num_apps = random.randint(1, 5)
            
            for _ in range(num_apps):
                scheme_id = random.choice(scheme_list)
                
                # Application date (within last 2 years)
                days_ago = random.randint(0, 730)
                app_date = datetime.now() - timedelta(days=days_ago)
                
                # Eligibility score (higher for eligible)
                eligibility_score = random.uniform(30, 95)
                
                # Application status based on score
                if eligibility_score >= 80:
                    status = 'APPROVED'
                    eligibility_probability = random.uniform(0.85, 0.95)
                elif eligibility_score >= 60:
                    status = random.choice(['APPROVED', 'PENDING'])
                    eligibility_probability = random.uniform(0.60, 0.85)
                else:
                    status = random.choice(['REJECTED', 'PENDING'])
                    eligibility_probability = random.uniform(0.30, 0.60)
                
                application = {
                    'gr_id': record['gr_id'],
                    'scheme_id': scheme_id,
                    'family_id': record['family_id'],
                    'application_date': app_date.date(),
                    'application_status': status,
                    'eligibility_score': round(eligibility_score, 2),
                    'eligibility_probability': round(eligibility_probability, 4),
                    'reviewed_by': f'Officer_{random.randint(1, 50)}' if status != 'PENDING' else None,
                    'reviewed_at': app_date + timedelta(days=random.randint(1, 30)) if status != 'PENDING' else None,
                    'rejection_reason': f'Reason_{random.randint(1, 10)}' if status == 'REJECTED' else None,
                    'created_at': app_date,
                    'updated_at': app_date + timedelta(days=random.randint(0, 30))
                }
                applications.append(application)
            
            if (idx + 1) % 5000 == 0:
                print(f"  Generated applications for {idx+1}/{len(golden_records_df)} records...")
        
        df = pd.DataFrame(applications)
        print(f"✅ Generated {len(df)} application events")
        return df
    
    def generate_socio_economic_facts(self, golden_records_df):
        """Generate socio-economic context data"""
        print("Generating socio-economic facts...")
        
        facts = []
        
        for idx, record in golden_records_df.iterrows():
            # Family size (1-8)
            family_size = random.randint(1, 8)
            dependents = max(0, family_size - 1)
            
            fact = {
                'gr_id': record['gr_id'],
                'education_level': random.choice(self.education_levels),
                'education_id': random.randint(1, 6),
                'employment_type': random.choice(self.employment_types),
                'employment_id': random.randint(1, 5),
                'occupation': f'Occupation_{random.randint(1, 20)}',
                'sector': random.choice(['AGRICULTURE', 'MANUFACTURING', 'SERVICES', 'GOVERNMENT']),
                'house_type': random.choice(self.house_types),
                'house_type_id': random.randint(1, 3),
                'land_holding_class': random.choice(['NONE', 'SMALL', 'MEDIUM', 'LARGE']),
                'utility_bill_avg': random.uniform(500, 5000) if random.random() < 0.6 else None,
                'property_tax_bracket': random.choice(['LOW', 'MEDIUM', 'HIGH', None]),
                'family_size': family_size,
                'dependents_count': dependents,
                'as_of_date': record['created_at'].date() if hasattr(record['created_at'], 'date') else datetime.now().date(),
                'source': 'synthetic_generation',
                'created_at': record['created_at'],
                'updated_at': datetime.now()
            }
            facts.append(fact)
        
        df = pd.DataFrame(facts)
        print(f"✅ Generated {len(df)} socio-economic facts")
        return df
    
    def generate_consent_flags(self, golden_records_df, consent_rate=0.7):
        """Generate consent flags (70% consent rate)"""
        print("Generating consent flags...")
        
        consents = []
        
        for idx, record in golden_records_df.iterrows():
            has_consent = random.random() < consent_rate
            
            consent = {
                'gr_id': record['gr_id'],
                'income_inference_consent': has_consent and random.random() < 0.9,
                'risk_analytics_consent': has_consent and random.random() < 0.8,
                'relationship_inference_consent': has_consent and random.random() < 0.85,
                'benefit_analytics_consent': has_consent and random.random() < 0.9,
                'consent_date': record['created_at'].date() if has_consent and hasattr(record['created_at'], 'date') else None,
                'consent_version': '1.0' if has_consent else None,
                'source': 'CITIZEN_PORTAL' if has_consent else None,
                'created_at': record['created_at'],
                'updated_at': datetime.now()
            }
            consents.append(consent)
        
        df = pd.DataFrame(consents)
        print(f"✅ Generated {len(df)} consent flags")
        return df
    
    def _generate_name(self, gender):
        """Generate synthetic name"""
        first_names_male = ['Rajesh', 'Kumar', 'Amit', 'Vikram', 'Sunil', 'Manoj', 'Ramesh', 'Suresh', 'Pankaj', 'Deepak']
        first_names_female = ['Priya', 'Anita', 'Sunita', 'Kavita', 'Meera', 'Reena', 'Seema', 'Neha', 'Pooja', 'Ritu']
        last_names = ['Sharma', 'Kumar', 'Gupta', 'Singh', 'Verma', 'Yadav', 'Meena', 'Choudhary', 'Pareek', 'Jain']
        
        if gender == 'Male':
            first = random.choice(first_names_male)
        elif gender == 'Female':
            first = random.choice(first_names_female)
        else:
            first = random.choice(first_names_male + first_names_female)
        
        last = random.choice(last_names)
        return f"{first} {last}"
    
    def _generate_age(self):
        """Generate age with Rajasthan distribution"""
        # Peak at 18-60 years (80%)
        if random.random() < 0.80:
            return random.randint(18, 60)
        elif random.random() < 0.90:
            return random.randint(0, 17)
        else:
            return random.randint(61, 85)
    
    def _generate_benefit_amount(self, scheme_id):
        """Generate benefit amount based on scheme"""
        # Different schemes have different amounts
        scheme_amounts = {
            1: (1000, 10000),   # Health
            2: (5000, 25000),   # Education
            3: (50000, 200000), # Housing
            4: (10000, 50000),  # Scholarship
            5: (50000, 300000), # Credit
            6: (2000, 12000),   # Women
            7: (12000, 24000),  # Disability
            8: (12000, 24000),  # Old Age
            9: (150, 300),      # NREGA (daily)
            10: (5000, 15000),  # BPL
            11: (10000, 30000), # Tribal
            12: (10000, 50000)  # OBC Scholarship
        }
        
        min_amount, max_amount = scheme_amounts.get(scheme_id, (1000, 10000))
        return round(random.uniform(min_amount, max_amount), 2)
    
    def insert_to_database(self, golden_records_df, relationships_df, benefits_df, 
                          applications_df, socio_df, consents_df):
        """Insert all data to database"""
        print("\nInserting data to database...")
        
        # Insert Golden Records - sort to insert family heads first
        print("Inserting Golden Records (family heads first)...")
        
        # Separate family heads (NULL family_id) from members (non-NULL family_id)
        family_heads = golden_records_df[golden_records_df['family_id'].isna()].copy()
        family_members = golden_records_df[golden_records_df['family_id'].notna()].copy()
        
        print(f"  Inserting {len(family_heads)} family heads (NULL family_id)...")
        if len(family_heads) > 0:
            self._insert_df(family_heads, 'golden_records', batch_size=1000)
        
        print(f"  Inserting {len(family_members)} family members (with family_id references)...")
        if len(family_members) > 0:
            # Insert members - their family_id should reference existing gr_ids
            self._insert_df(family_members, 'golden_records', batch_size=1000)
        
        # Insert Relationships
        if len(relationships_df) > 0:
            print("Inserting Relationships...")
            self._insert_df(relationships_df, 'gr_relationships', batch_size=1000)
        
        # Insert Benefits
        if len(benefits_df) > 0:
            print("Inserting Benefit Events...")
            self._insert_df(benefits_df, 'benefit_events', batch_size=1000)
        
        # Insert Applications
        if len(applications_df) > 0:
            print("Inserting Application Events...")
            self._insert_df(applications_df, 'application_events', batch_size=1000)
        
        # Insert Socio-Economic
        print("Inserting Socio-Economic Facts...")
        self._insert_df(socio_df, 'socio_economic_facts', batch_size=1000)
        
        # Insert Consents
        print("Inserting Consent Flags...")
        self._insert_df(consents_df, 'consent_flags', batch_size=1000)
        
        print("\n✅ All data inserted successfully!")
    
    def _insert_df(self, df, table_name, batch_size=1000):
        """Insert DataFrame to database in batches"""
        from io import StringIO
        import numpy as np
        
        # Replace NaN with None for proper NULL handling in database
        df_clean = df.replace({np.nan: None})
        
        for i in range(0, len(df_clean), batch_size):
            batch = df_clean.iloc[i:i+batch_size]
            
            # Create INSERT statements
            columns = ', '.join(batch.columns)
            placeholders = ', '.join(['%s'] * len(batch.columns))
            
            # Build INSERT statement
            insert_sql = f"""
                INSERT INTO {table_name} ({columns})
                VALUES ({placeholders})
                ON CONFLICT DO NOTHING
            """
            
            # Execute batch - convert each row, replacing None with None for SQL
            values = []
            for _, row in batch.iterrows():
                row_values = []
                for val in row:
                    # Convert pandas NaT and NaN to None
                    if pd.isna(val):
                        row_values.append(None)
                    else:
                        row_values.append(val)
                values.append(tuple(row_values))
            
            cursor = self.db.connection.cursor()
            cursor.executemany(insert_sql, values)
            self.db.connection.commit()
            cursor.close()
            
            if (i + batch_size) % 5000 == 0:
                print(f"  Inserted {min(i+batch_size, len(df_clean))}/{len(df_clean)} records...")
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.disconnect()


def main():
    """Main generation function"""
    print("="*80)
    print("AI-PLATFORM-02: Synthetic Data Generation")
    print("Generating 45K Rajasthan Records")
    print("="*80)
    print()
    
    generator = SyntheticDataGenerator()
    
    try:
        # Generate all data
        golden_records = generator.generate_golden_records(count=45000)
        relationships = generator.generate_relationships(golden_records)
        benefits = generator.generate_benefit_events(golden_records, count_per_person=3)
        applications = generator.generate_application_events(golden_records, scheme_coverage=0.4)
        socio = generator.generate_socio_economic_facts(golden_records)
        consents = generator.generate_consent_flags(golden_records, consent_rate=0.7)
        
        # Insert to database
        generator.insert_to_database(
            golden_records, relationships, benefits, 
            applications, socio, consents
        )
        
        # Summary
        print("\n" + "="*80)
        print("GENERATION SUMMARY")
        print("="*80)
        print(f"Golden Records:      {len(golden_records):,}")
        print(f"Relationships:       {len(relationships):,}")
        print(f"Benefit Events:      {len(benefits):,}")
        print(f"Application Events:  {len(applications):,}")
        print(f"Socio-Economic:      {len(socio):,}")
        print(f"Consent Flags:       {len(consents):,}")
        print("="*80)
        print("\n✅ Data generation complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        generator.close()


if __name__ == "__main__":
    main()

