#!/usr/bin/env python3
"""
SMART Platform - Database Connection Test Script

Tests PostgreSQL database connection using the configured credentials.
Can be run from Windows PowerShell or WSL terminal.
"""

import sys
import os
import socket

def test_postgresql_connection():
    """Test PostgreSQL database connection"""
    print("=" * 60)
    print("SMART Platform - Database Connection Test")
    print("=" * 60)
    
    # Database configuration - try both localhost and Windows hostname
    configs = [
        {
            'host': 'localhost',
            'port': 5432,
            'database': 'smart',
            'user': 'sameer',
            'password': 'anjali143',
            'name': 'localhost'
        }
    ]
    
    # Try Windows hostname if in WSL
    try:
        import subprocess
        windows_hostname = subprocess.check_output(['hostname.exe'], stderr=subprocess.DEVNULL).decode().strip()
        if windows_hostname:
            configs.append({
                'host': windows_hostname,
                'port': 5432,
                'database': 'smart',
                'user': 'sameer',
                'password': 'anjali143',
                'name': f'Windows hostname ({windows_hostname})'
            })
    except:
        pass
    
    # Try 127.0.0.1 as well
    configs.append({
        'host': '127.0.0.1',
        'port': 5432,
        'database': 'smart',
        'user': 'sameer',
        'password': 'anjali143',
        'name': '127.0.0.1'
    })
    
    try:
        # Try to import psycopg2
        try:
            import psycopg2
            from psycopg2 import sql
        except ImportError:
            print("\n❌ ERROR: psycopg2 not installed")
            print("   Install with: pip install psycopg2-binary")
            print("   Or from WSL venv: /mnt/c/Projects/SMART/ai-ml/.venv/bin/pip install psycopg2-binary")
            return False
        
        print("\n✅ psycopg2 imported successfully")
        
        # Try each configuration
        for config in configs:
            print(f"\n{'='*60}")
            print(f"Trying connection via {config['name']}...")
            print(f"  Host: {config['host']}")
            print(f"  Port: {config['port']}")
            print(f"  Database: {config['database']}")
            print(f"  Username: {config['user']}")
            
            # Test if port is accessible
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((config['host'], config['port']))
                sock.close()
                if result != 0:
                    print(f"  ⚠️  Port {config['port']} is not accessible on {config['host']}")
                    continue
            except Exception as e:
                print(f"  ⚠️  Cannot test port: {e}")
                continue
            
            # Attempt connection
            try:
                print("\nAttempting to connect to PostgreSQL...")
                conn = psycopg2.connect(
                    host=config['host'],
                    port=config['port'],
                    database=config['database'],
                    user=config['user'],
                    password=config['password'],
                    connect_timeout=5
                )
                
                print("✅ Connection established successfully!")
                
                # Get database version
                cursor = conn.cursor()
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                print(f"\n📊 PostgreSQL Version:")
                print(f"   {version}")
                
                # Get current database name
                cursor.execute("SELECT current_database();")
                db_name = cursor.fetchone()[0]
                print(f"\n📂 Current Database: {db_name}")
                
                # Get current user
                cursor.execute("SELECT current_user;")
                db_user = cursor.fetchone()[0]
                print(f"👤 Current User: {db_user}")
                
                # List all databases
                cursor.execute("""
                    SELECT datname 
                    FROM pg_database 
                    WHERE datistemplate = false 
                    ORDER BY datname;
                """)
                databases = cursor.fetchall()
                print(f"\n📚 Available Databases:")
                for db in databases:
                    print(f"   - {db[0]}")
                
                # Test table creation/query (if permissions allow)
                try:
                    cursor.execute("""
                        SELECT table_schema, table_name 
                        FROM information_schema.tables 
                        WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
                        ORDER BY table_schema, table_name
                        LIMIT 10;
                    """)
                    tables = cursor.fetchall()
                    if tables:
                        print(f"\n📋 Sample Tables (first 10):")
                        for schema, table in tables:
                            print(f"   {schema}.{table}")
                    else:
                        print(f"\n📋 No user tables found in database")
                except Exception as e:
                    print(f"\n⚠️  Could not list tables: {e}")
                
                # Close connection
                cursor.close()
                conn.close()
                
                print("\n" + "=" * 60)
                print(f"✅ Database connection test PASSED (via {config['name']})")
                print("=" * 60)
                return True
                
            except psycopg2.OperationalError as e:
                print(f"  ❌ Connection failed: {e}")
                continue
            except psycopg2.Error as e:
                print(f"  ❌ Database error: {e}")
                continue
        
        print("\n" + "=" * 60)
        print("❌ All connection attempts failed")
        print("\nTroubleshooting:")
        print("  1. Ensure PostgreSQL is running on Windows")
        print("  2. Check PostgreSQL pg_hba.conf allows connections")
        print("  3. Verify PostgreSQL is listening on all interfaces (0.0.0.0)")
        print("  4. Check Windows Firewall settings")
        print("  5. Try connecting from Windows PowerShell:")
        print("     psql -h localhost -p 5432 -U sameer -d smart")
        print("=" * 60)
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_postgresql_connection()
    sys.exit(0 if success else 1)
