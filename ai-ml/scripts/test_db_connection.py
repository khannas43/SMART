#!/usr/bin/env python3
"""Test database connection for eligibility scoring"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared', 'utils'))

from db_connector import DBConnector

def test_connection():
    print("=" * 60)
    print("Testing PostgreSQL Connection for Eligibility Scoring")
    print("=" * 60)
    
    try:
        db = DBConnector(
            host="172.17.16.1",
            port=5432,
            database="smart",
            user="sameer",
            password="anjali143"
        )
        
        db.connect()
        
        # Test queries
        print("\n📊 Testing queries...")
        tables = db.list_tables()
        print(f"✅ Found {len(tables)} tables")
        
        if 'schemes' in tables:
            count = db.get_table_count('schemes')
            print(f"✅ Schemes table: {count:,} rows")
            
            info = db.get_table_info('schemes')
            print(f"✅ Schemes table columns: {len(info)}")
            
            # Show first few columns
            print("\n📋 Column names:")
            for col in info['column_name'].head(10):
                print(f"  - {col}")
        else:
            print("⚠️  'schemes' table not found")
            print(f"Available tables: {tables[:10]}")
        
        db.disconnect()
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

