#!/usr/bin/env python3
"""
Initialize Sample Data for Proactive Inclusion & Exception Handling
Use Case ID: AI-PLATFORM-09
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import uuid
import random
import yaml

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))

from services.inclusion_orchestrator import InclusionOrchestrator
from db_connector import DBConnector


def init_sample_data():
    """Initialize sample data for testing"""
    print("=" * 80)
    print("Initializing Sample Data for Proactive Inclusion & Exception Handling")
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
        print(f"✅ Connected to PostgreSQL: {db_config['host']}:{db_config['port']}/{db_config['name']}")
        
        # Initialize orchestrator
        orchestrator = InclusionOrchestrator()
        orchestrator.connect()
        print("✅ InclusionOrchestrator initialized")
        
        # Create sample families and identify as priority
        print("\n🔄 Creating sample priority households...")
        sample_families = []
        
        for i in range(5):
            family_id = str(uuid.uuid4())
            beneficiary_id = f"BEN{random.randint(100000, 999999)}"
            
            # Create dummy family data (this would normally be in golden_records)
            # For now, we'll just identify them as priority
            print(f"\n   Processing Family {i+1}: {family_id[:8]}...")
            
            try:
                priority_status = orchestrator.get_priority_status(
                    family_id=family_id,
                    include_nudges=True
                )
                
                if priority_status and priority_status.get('is_priority'):
                    sample_families.append({
                        'family_id': family_id,
                        'priority_household': priority_status.get('priority_household')
                    })
                    print(f"   ✅ Identified as priority household")
                else:
                    print(f"   ℹ️  Not identified as priority (may not meet threshold)")
            
            except Exception as e:
                print(f"   ⚠️  Error processing family: {e}")
        
        print(f"\n✅ Sample data initialization complete!")
        print(f"   Created {len(sample_families)} priority households")
        
        orchestrator.disconnect()
    
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.disconnect()
        print("Database connection closed")


if __name__ == '__main__':
    init_sample_data()

