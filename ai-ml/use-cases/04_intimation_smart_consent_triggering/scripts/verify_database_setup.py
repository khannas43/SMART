"""
Verify Database Setup
Comprehensive verification of database schema setup
"""

import sys
import os
from pathlib import Path
import yaml
import pandas as pd

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


def verify_database_setup():
    """Verify database setup is complete"""
    print("=" * 80)
    print("Database Setup Verification")
    print("=" * 80)
    
    # Load config
    config_path = os.path.join(os.path.dirname(__file__), '../config/db_config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Connect to database
    db_config = config['database']
    db = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    db.connect()
    
    cursor = db.connection.cursor()
    all_checks_passed = True
    
    try:
        # Check 1: Schema exists
        print("\n1️⃣ Checking schema exists...")
        cursor.execute("""
            SELECT schema_name FROM information_schema.schemata 
            WHERE schema_name = 'intimation'
        """)
        if cursor.fetchone():
            print("   ✅ Schema 'intimation' exists")
        else:
            print("   ❌ Schema 'intimation' does not exist")
            print("      Run: ./scripts/setup_database.sh")
            all_checks_passed = False
        
        # Check 2: Tables exist
        print("\n2️⃣ Checking tables...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'intimation'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = [
            'campaigns', 'campaign_candidates', 'consent_records',
            'consent_history', 'intimation_events', 'message_fatigue',
            'message_logs', 'message_templates', 'scheme_intimation_config',
            'user_preferences'
        ]
        
        missing_tables = set(expected_tables) - set(tables)
        if not missing_tables:
            print(f"   ✅ All {len(expected_tables)} tables exist")
            for table in expected_tables:
                print(f"      - {table}")
        else:
            print(f"   ❌ Missing tables: {', '.join(missing_tables)}")
            all_checks_passed = False
        
        # Check 3: Foreign keys
        print("\n3️⃣ Checking foreign keys...")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.table_constraints 
            WHERE constraint_type = 'FOREIGN KEY' 
            AND table_schema = 'intimation'
        """)
        fk_count = cursor.fetchone()[0]
        if fk_count >= 4:
            print(f"   ✅ Found {fk_count} foreign key constraints")
        else:
            print(f"   ⚠️  Only {fk_count} foreign keys found (expected at least 4)")
        
        # Check 4: Triggers
        print("\n4️⃣ Checking triggers...")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.triggers 
            WHERE trigger_schema = 'intimation'
        """)
        trigger_count = cursor.fetchone()[0]
        if trigger_count >= 5:
            print(f"   ✅ Found {trigger_count} triggers")
        else:
            print(f"   ⚠️  Only {trigger_count} triggers found (expected at least 5)")
        
        # Check 5: Functions
        print("\n5️⃣ Checking functions...")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.routines 
            WHERE routine_schema = 'intimation'
        """)
        func_count = cursor.fetchone()[0]
        if func_count >= 2:
            print(f"   ✅ Found {func_count} functions")
        else:
            print(f"   ⚠️  Only {func_count} functions found (expected at least 2)")
        
        # Check 6: Message templates
        print("\n6️⃣ Checking message templates...")
        cursor.execute("SELECT COUNT(*) FROM intimation.message_templates")
        template_count = cursor.fetchone()[0]
        if template_count > 0:
            print(f"   ✅ Found {template_count} message templates")
            
            cursor.execute("""
                SELECT template_code, channel, language 
                FROM intimation.message_templates
                ORDER BY template_code
            """)
            for row in cursor.fetchall():
                print(f"      - {row[0]} ({row[1]}/{row[2]})")
        else:
            print("   ⚠️  No message templates found")
            print("      Run: python scripts/init_message_templates.py")
        
        # Check 7: Scheme configuration
        print("\n7️⃣ Checking scheme configuration...")
        cursor.execute("SELECT COUNT(*) FROM intimation.scheme_intimation_config")
        scheme_config_count = cursor.fetchone()[0]
        if scheme_config_count > 0:
            print(f"   ✅ Found {scheme_config_count} scheme configurations")
        else:
            print("   ⚠️  No scheme configurations found")
            print("      Run: python scripts/init_scheme_config.py")
        
        # Check 8: Foreign key to scheme_master
        print("\n8️⃣ Checking foreign key to scheme_master...")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu
              ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'intimation'
            AND ccu.table_name = 'scheme_master'
        """)
        fk_to_scheme_count = cursor.fetchone()[0]
        if fk_to_scheme_count >= 4:
            print(f"   ✅ Found {fk_to_scheme_count} foreign keys to scheme_master")
        else:
            print(f"   ⚠️  Only {fk_to_scheme_count} foreign keys to scheme_master (expected at least 4)")
        
        # Summary
        print("\n" + "=" * 80)
        if all_checks_passed:
            print("✅ Database setup verification PASSED!")
            print("=" * 80)
            print("\nNext steps:")
            print("1. Initialize message templates: python scripts/init_message_templates.py")
            print("2. Initialize scheme config: python scripts/init_scheme_config.py")
            print("3. Run tests: python scripts/test_intake.py")
        else:
            print("⚠️  Database setup verification found issues")
            print("=" * 80)
            print("\nPlease review the issues above and fix them.")
            print("Then run this script again to verify.")
        
    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        db.disconnect()


if __name__ == '__main__':
    verify_database_setup()

