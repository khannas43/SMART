#!/usr/bin/env python3
"""
Step 3: Test Python Code Updates
Verify that all database queries use scheme_code correctly
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root / "shared" / "utils"))
sys.path.append(str(Path(__file__).parent.parent / "src"))

import yaml
import pandas as pd
from db_connector import DBConnector

def test_scheme_master_columns():
    """Test that scheme_master has the new columns"""
    print("=" * 60)
    print("Test 1: Verify scheme_master has eligibility columns")
    print("=" * 60)
    
    # Load config
    config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    with open(config_path, 'r') as f:
        db_config = yaml.safe_load(f)['database']
    
    db = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    db.connect()
    
    try:
        # Check columns
        query = """
            SELECT column_name, data_type, column_default
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'scheme_master'
            AND column_name IN ('is_auto_id_enabled', 'scheme_type')
            ORDER BY column_name
        """
        
        df = pd.read_sql(query, db.connection)
        
        if len(df) == 2:
            print("✅ Both columns exist:")
            for _, row in df.iterrows():
                print(f"   - {row['column_name']}: {row['data_type']} (default: {row['column_default']})")
            return True
        else:
            print(f"❌ Expected 2 columns, found {len(df)}")
            print("   Run: database/extend_scheme_master.sql")
            return False
    finally:
        db.disconnect()


def test_scheme_code_queries():
    """Test queries using scheme_code"""
    print("\n" + "=" * 60)
    print("Test 2: Query schemes using scheme_code")
    print("=" * 60)
    
    config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    with open(config_path, 'r') as f:
        db_config = yaml.safe_load(f)['database']
    
    db = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    db.connect()
    
    try:
        # Query using scheme_code
        query = """
            SELECT scheme_code, scheme_name, category, is_auto_id_enabled, scheme_type
            FROM scheme_master
            WHERE status = 'active' AND is_auto_id_enabled = true
            LIMIT 5
        """
        
        df = pd.read_sql(query, db.connection)
        
        if len(df) > 0:
            print(f"✅ Found {len(df)} schemes with auto-identification enabled:")
            for _, row in df.iterrows():
                print(f"   - {row['scheme_code']}: {row['scheme_name']} ({row['category']})")
            return True
        else:
            print("⚠️  No schemes found with auto-identification enabled")
            print("   Run: database/extend_scheme_master.sql to update existing schemes")
            return False
    finally:
        db.disconnect()


def test_eligibility_tables_use_scheme_code():
    """Test that eligibility tables have scheme_code column"""
    print("\n" + "=" * 60)
    print("Test 3: Verify eligibility tables use scheme_code")
    print("=" * 60)
    
    config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    with open(config_path, 'r') as f:
        db_config = yaml.safe_load(f)['database']
    
    db = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    db.connect()
    
    try:
        # Check which tables have scheme_code
        query = """
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'eligibility'
            AND column_name = 'scheme_code'
            ORDER BY table_name
        """
        
        df = pd.read_sql(query, db.connection)
        
        expected_tables = [
            'scheme_eligibility_rules',
            'eligibility_snapshots',
            'candidate_lists',
            'ml_model_registry'
        ]
        
        found_tables = df['table_name'].unique().tolist()
        
        if len(found_tables) > 0:
            print(f"✅ Found scheme_code in {len(found_tables)} tables:")
            for table in found_tables:
                print(f"   - {table}")
        else:
            print("⚠️  No eligibility tables found with scheme_code column")
        
        missing = set(expected_tables) - set(found_tables)
        if missing:
            print(f"⚠️  Missing scheme_code in: {missing}")
            print("   ACTION REQUIRED: Run eligibility_schema.sql to create eligibility tables")
            print("   Command: psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f database/eligibility_schema.sql")
            return False
        
        return True
    finally:
        db.disconnect()


def test_no_duplicate_scheme_master():
    """Test that there's no duplicate scheme_master table"""
    print("\n" + "=" * 60)
    print("Test 4: Verify no duplicate scheme_master")
    print("=" * 60)
    
    config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    with open(config_path, 'r') as f:
        db_config = yaml.safe_load(f)['database']
    
    db = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    db.connect()
    
    try:
        query = """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_name = 'scheme_master'
            ORDER BY table_schema
        """
        
        df = pd.read_sql(query, db.connection)
        
        if len(df) == 1 and df.iloc[0]['table_schema'] == 'public':
            print("✅ Only one scheme_master table exists: public.scheme_master")
            return True
        else:
            print(f"❌ Found {len(df)} scheme_master tables:")
            for _, row in df.iterrows():
                print(f"   - {row['table_schema']}.{row['table_name']}")
            print("   This indicates duplicate table. Remove eligibility.scheme_master if exists.")
            return False
    finally:
        db.disconnect()


def test_foreign_keys():
    """Test foreign key constraints"""
    print("\n" + "=" * 60)
    print("Test 5: Verify foreign key constraints")
    print("=" * 60)
    
    config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    with open(config_path, 'r') as f:
        db_config = yaml.safe_load(f)['database']
    
    db = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    db.connect()
    
    try:
        query = """
            SELECT 
                tc.table_schema, 
                tc.table_name, 
                kcu.column_name,
                ccu.table_schema AS foreign_table_schema,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND ccu.table_name = 'scheme_master'
                AND tc.table_schema = 'eligibility'
            ORDER BY tc.table_name, kcu.column_name
        """
        
        df = pd.read_sql(query, db.connection)
        
        if len(df) > 0:
            print(f"✅ Found {len(df)} foreign keys to scheme_master:")
            for _, row in df.iterrows():
                print(f"   - {row['table_schema']}.{row['table_name']}.{row['column_name']} → "
                      f"{row['foreign_table_schema']}.{row['foreign_table_name']}.{row['foreign_column_name']}")
            
            # Check if all use scheme_code
            code_fks = df[df['column_name'] == 'scheme_code']
            if len(code_fks) == len(df):
                print("   ✅ All foreign keys use scheme_code")
                return True
            else:
                print(f"   ⚠️  Only {len(code_fks)}/{len(df)} foreign keys use scheme_code")
                return False
        else:
            print("⚠️  No foreign keys found.")
            print("   This could mean:")
            print("   1. Eligibility tables haven't been created yet")
            print("   2. Foreign keys haven't been set up")
            print("   ACTION: Run eligibility_schema.sql to create tables with foreign keys")
            print("   Command: psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f database/eligibility_schema.sql")
            return False
    finally:
        db.disconnect()


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("STEP 3: Testing Python Code Updates")
    print("=" * 60)
    print()
    
    tests = [
        ("scheme_master columns", test_scheme_master_columns),
        ("scheme_code queries", test_scheme_code_queries),
        ("eligibility tables", test_eligibility_tables_use_scheme_code),
        ("no duplicate tables", test_no_duplicate_scheme_master),
        ("foreign keys", test_foreign_keys),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed! Python code updates are working correctly.")
    else:
        print("\n⚠️  Some tests failed. Review the output above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

