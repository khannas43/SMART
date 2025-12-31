#!/usr/bin/env python3
"""
Create Sample Data for Inclusion Viewer
Use Case ID: AI-PLATFORM-09
Creates sample data directly in inclusion schema tables for testing
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import uuid
import random
import json
import yaml

# Add shared utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


def create_sample_data():
    """Create sample data for inclusion viewer"""
    print("=" * 80)
    print("Creating Sample Data for Proactive Inclusion & Exception Handling")
    print("=" * 80)
    
    # Load configuration
    db_config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    with open(db_config_path, 'r') as f:
        db_config = yaml.safe_load(f)['database']
    
    # Connect to database
    db = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    
    try:
        db.connect()
        conn = db.connection
        cursor = conn.cursor()
        
        print("✅ Connected to database")
        
        # Create sample priority households
        print("\n🔄 Creating sample priority households...")
        districts = ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer"]
        segments_list = [
            ["TRIBAL", "PWD"],
            ["SINGLE_WOMAN"],
            ["TRIBAL", "REMOTE_GEOGRAPHY"],
            ["PWD", "ELDERLY_ALONE"],
            ["UNEMPLOYED_YOUTH"]
        ]
        priority_levels = ["HIGH", "MEDIUM", "LOW"]
        
        for i in range(10):
            family_id = str(uuid.uuid4())
            household_head_id = f"BEN{random.randint(100000, 999999)}"
            district = random.choice(districts)
            block_id = f"{district}_BLOCK_{random.randint(1, 5)}"
            gp = f"GP_{random.randint(1, 20)}"
            
            inclusion_gap_score = round(random.uniform(0.6, 0.95), 4)
            vulnerability_score = round(random.uniform(0.4, 0.9), 4)
            coverage_gap_score = round(random.uniform(0.5, 0.9), 4)
            benchmark_score = round(random.uniform(0.3, 0.7), 4)
            
            priority_level = priority_levels[0] if inclusion_gap_score > 0.8 else (
                priority_levels[1] if inclusion_gap_score > 0.7 else priority_levels[2]
            )
            segments = random.choice(segments_list)
            
            predicted_count = random.randint(3, 8)
            enrolled_count = random.randint(0, 3)
            gap_count = predicted_count - enrolled_count
            
            try:
                cursor.execute("""
                    INSERT INTO inclusion.priority_households (
                        family_id, household_head_id, block_id, district, gram_panchayat,
                        inclusion_gap_score, vulnerability_score, coverage_gap_score,
                        benchmark_score, priority_level, priority_segments,
                        predicted_eligible_schemes_count, actual_enrolled_schemes_count,
                        eligibility_gap_count, is_active
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    family_id, household_head_id, block_id, district, gp,
                    inclusion_gap_score, vulnerability_score, coverage_gap_score,
                    benchmark_score, priority_level, segments,
                    predicted_count, enrolled_count, gap_count, True
                ))
                print(f"   ✅ Created priority household {i+1}: {family_id[:8]}... (Priority: {priority_level})")
            except Exception as e:
                print(f"   ⚠️  Error creating priority household {i+1}: {e}")
        
        conn.commit()
        
        # Create sample exception flags
        print("\n🔄 Creating sample exception flags...")
        exception_categories = [
            "RECENTLY_DISABLED",
            "MIGRANT_WORKER",
            "HOMELESS_INFORMAL_SETTLEMENT",
            "DROPOUT_STUDENT",
            "OTHER_ATYPICAL"
        ]
        
        # Get some family IDs from priority households
        cursor.execute("SELECT family_id FROM inclusion.priority_households LIMIT 5")
        family_ids = [row[0] for row in cursor.fetchall()]
        
        for i, family_id in enumerate(family_ids[:5]):
            category = exception_categories[i % len(exception_categories)]
            anomaly_score = round(random.uniform(0.7, 0.95), 4)
            description = f"Pattern detected: {category.replace('_', ' ').lower()}"
            
            try:
                cursor.execute("""
                    INSERT INTO inclusion.exception_flags (
                        family_id, exception_category, exception_description,
                        anomaly_score, review_status, detected_at
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    family_id, category, description,
                    anomaly_score, "PENDING_REVIEW", datetime.now() - timedelta(hours=random.randint(1, 48))
                ))
                print(f"   ✅ Created exception flag {i+1}: {category}")
            except Exception as e:
                print(f"   ⚠️  Error creating exception flag {i+1}: {e}")
        
        conn.commit()
        
        # Create sample nudge records
        print("\n🔄 Creating sample nudge records...")
        nudge_types = ["SCHEME_SUGGESTION", "ACTION_REMINDER", "UPDATE_REQUEST"]
        channels = ["PORTAL", "MOBILE_APP", "SMS", "FIELD_WORKER"]
        delivery_statuses = ["SCHEDULED", "DELIVERED", "FAILED"]
        
        cursor.execute("SELECT priority_id, family_id FROM inclusion.priority_households LIMIT 8")
        priority_households = cursor.fetchall()
        
        messages = [
            "You might be eligible for disability pension. Check your eligibility and apply if interested.",
            "Educational support schemes may be available for your family members. Consider checking scholarship eligibility.",
            "As a tribal household, you may be eligible for additional benefits. Please check your eligibility.",
            "Consider updating or obtaining your disability certificate to access disability-related benefits.",
            "You may be missing important support schemes. Check your eligibility for pension and health benefits."
        ]
        
        for i, (priority_id, family_id) in enumerate(priority_households):
            nudge_type = random.choice(nudge_types)
            channel = random.choice(channels)
            priority_level = random.choice(priority_levels)
            delivery_status = random.choice(delivery_statuses)
            message = random.choice(messages)
            actions = ["Apply for scheme", "Check eligibility", "Update documents"]
            scheme_codes = [f"SCHEME_{random.randint(1, 10)}"]
            
            scheduled_at = datetime.now() - timedelta(hours=random.randint(1, 72))
            delivered_at = scheduled_at + timedelta(minutes=random.randint(5, 120)) if delivery_status == "DELIVERED" else None
            
            try:
                cursor.execute("""
                    INSERT INTO inclusion.nudge_records (
                        family_id, household_head_id, nudge_type, nudge_message,
                        recommended_actions, scheme_codes, channel, priority_level,
                        scheduled_at, delivered_at, delivery_status, priority_household_id
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    family_id, f"BEN{random.randint(100000, 999999)}",
                    nudge_type, message, actions, scheme_codes,
                    channel, priority_level, scheduled_at, delivered_at,
                    delivery_status, priority_id
                ))
                print(f"   ✅ Created nudge record {i+1}: {nudge_type} via {channel}")
            except Exception as e:
                print(f"   ⚠️  Error creating nudge record {i+1}: {e}")
        
        conn.commit()
        cursor.close()
        
        print("\n" + "=" * 80)
        print("✅ Sample data creation complete!")
        print("=" * 80)
        print("\n📊 Created:")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM inclusion.priority_households WHERE is_active = TRUE")
        print(f"   Priority Households: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM inclusion.exception_flags WHERE review_status = 'PENDING_REVIEW'")
        print(f"   Exception Flags: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM inclusion.nudge_records")
        print(f"   Nudge Records: {cursor.fetchone()[0]}")
        
        cursor.close()
        print("\n🌐 View data at: http://localhost:5001/ai09")
    
    except Exception as e:
        print(f"\n❌ Error creating sample data: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.disconnect()
        print("\nDatabase connection closed")


if __name__ == '__main__':
    create_sample_data()

