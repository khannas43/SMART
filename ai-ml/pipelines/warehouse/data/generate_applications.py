#!/usr/bin/env python3
"""
Generate 50K citizen-scheme application pairs
"""

import random
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

def generate_application_number(citizen_id, scheme_id, app_date):
    """Generate unique application number"""
    date_str = app_date.strftime('%Y%m%d')
    return f"APP{date_str}{citizen_id:06d}{scheme_id:02d}"

def generate_application_data(num_apps, citizen_count, scheme_count):
    """Generate application data"""
    applications = []
    
    # Status distribution
    status_weights = {
        'pending': 0.15,
        'under_review': 0.20,
        'approved': 0.40,
        'rejected': 0.15,
        'disbursed': 0.08,
        'closed': 0.02
    }
    
    # Date range (last 2 years)
    start_date = datetime.now() - timedelta(days=730)
    
    for i in range(1, num_apps + 1):
        # Random citizen and scheme
        citizen_id = random.randint(1, citizen_count)
        scheme_id = random.randint(1, scheme_count)
        
        # Application date (weighted towards recent)
        days_ago = int(random.expovariate(1/100))  # Exponential distribution
        days_ago = min(days_ago, 730)
        application_date = (datetime.now() - timedelta(days=days_ago)).date()
        
        # Status
        status = random.choices(
            list(status_weights.keys()),
            weights=list(status_weights.values())
        )[0]
        
        # Eligibility score (0-100)
        # Higher scores for approved applications
        if status in ['approved', 'disbursed']:
            eligibility_score = random.uniform(70, 100)
            eligibility_status = 'eligible'
        elif status == 'rejected':
            eligibility_score = random.uniform(0, 50)
            eligibility_status = 'not_eligible'
        else:
            eligibility_score = random.uniform(40, 80)
            eligibility_status = random.choice(['eligible', 'conditional'])
        
        # Application number
        app_number = generate_application_number(citizen_id, scheme_id, application_date)
        
        # Approval and disbursement dates (if approved)
        approval_date = None
        disbursed_amount = None
        disbursement_date = None
        
        if status in ['approved', 'disbursed']:
            days_after = random.randint(5, 90)
            approval_date = application_date + timedelta(days=days_after)
            approved_amount = random.uniform(10000, 500000)
            
            if status == 'disbursed':
                days_disburse = random.randint(10, 120)
                disbursement_date = approval_date + timedelta(days=days_disburse)
                disbursed_amount = approved_amount * random.uniform(0.8, 1.0)  # 80-100% of approved
        else:
            approved_amount = None
        
        # Documents
        documents_verified = status in ['approved', 'disbursed']
        documents_count = random.randint(2, 8) if documents_verified else random.randint(0, 5)
        
        # Rejection reason (if rejected)
        rejection_reason = None
        if status == 'rejected':
            reasons = [
                'Income criteria not met',
                'Age limit exceeded',
                'Documents incomplete',
                'Caste category not eligible',
                'BPL card not available',
                'Duplicate application',
                'Invalid documents'
            ]
            rejection_reason = random.choice(reasons)
        
        app = {
            'application_number': app_number,
            'citizen_id': citizen_id,
            'scheme_id': scheme_id,
            'application_date': application_date,
            'application_status': status,
            'eligibility_score': round(eligibility_score, 2),
            'eligibility_status': eligibility_status,
            'approval_date': approval_date,
            'approved_amount': round(approved_amount, 2) if approved_amount else None,
            'disbursed_amount': round(disbursed_amount, 2) if disbursed_amount else None,
            'disbursement_date': disbursement_date,
            'documents_verified': documents_verified,
            'documents_count': documents_count,
            'rejection_reason': rejection_reason
        }
        
        applications.append(app)
    
    return applications

def write_insert_sql(applications, output_file):
    """Write INSERT statements to SQL file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- 50K Citizen-Scheme Application Pairs\n")
        f.write("-- Generated synthetic application data\n\n")
        
        # Batch insert in chunks of 1000
        batch_size = 1000
        for i in range(0, len(applications), batch_size):
            batch = applications[i:i+batch_size]
            f.write("INSERT INTO applications (\n")
            f.write("    application_number, citizen_id, scheme_id, application_date,\n")
            f.write("    application_status, eligibility_score, eligibility_status,\n")
            f.write("    approval_date, approved_amount, disbursed_amount, disbursement_date,\n")
            f.write("    documents_verified, documents_count, rejection_reason\n")
            f.write(") VALUES\n")
            
            values = []
            for a in batch:
                approval_date_val = f"'{a['approval_date']}'" if a['approval_date'] else 'NULL'
                approved_amount_val = str(a['approved_amount']) if a['approved_amount'] else 'NULL'
                disbursed_amount_val = str(a['disbursed_amount']) if a['disbursed_amount'] else 'NULL'
                disbursement_date_val = f"'{a['disbursement_date']}'" if a['disbursement_date'] else 'NULL'
                rejection_reason_val = f"'{a['rejection_reason'].replace("'", "''")}'" if a['rejection_reason'] else 'NULL'
                
                val = f"('{a['application_number']}', {a['citizen_id']}, {a['scheme_id']}, "
                val += f"'{a['application_date']}', '{a['application_status']}', {a['eligibility_score']}, "
                val += f"'{a['eligibility_status']}', {approval_date_val}, {approved_amount_val}, "
                val += f"{disbursed_amount_val}, {disbursement_date_val}, {str(a['documents_verified']).upper()}, "
                val += f"{a['documents_count']}, {rejection_reason_val})"
                values.append(val)
            
            f.write(',\n'.join(values))
            f.write(';\n\n')

def main():
    print("Generating 50K applications...")
    applications = generate_application_data(50000, 100000, 12)
    
    output_dir = Path(__file__).parent
    sql_file = output_dir / '09_insert_applications.sql'
    
    print(f"Writing SQL INSERT statements to {sql_file}...")
    write_insert_sql(applications, sql_file)
    
    print(f"\n✅ Generated {len(applications)} applications")
    print(f"   - SQL: {sql_file}")

if __name__ == '__main__':
    main()

