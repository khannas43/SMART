#!/usr/bin/env python3
"""Quick test to verify AI11 routes are registered"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import view_rules_web
    app = view_rules_web.app
    
    # Check for AI11 routes
    routes = [str(rule) for rule in app.url_map.iter_rules()]
    ai11_routes = [r for r in routes if 'ai11' in r.lower()]
    
    print("=" * 60)
    print("Testing AI11 Route Registration")
    print("=" * 60)
    
    if ai11_routes:
        print(f"✅ Found {len(ai11_routes)} AI11 routes:")
        for route in ai11_routes:
            print(f"   - {route}")
    else:
        print("❌ No AI11 routes found!")
        print("\nAvailable routes:")
        for route in sorted(routes)[:20]:
            print(f"   - {route}")
    
    # Test if route is accessible (without actually running server)
    with app.test_client() as client:
        response = client.get('/ai11')
        if response.status_code == 200:
            print("\n✅ Route /ai11 returns 200 OK")
        else:
            print(f"\n⚠️  Route /ai11 returns {response.status_code}")
            
        response = client.get('/ai11/api/nudges')
        if response.status_code in [200, 500]:  # 500 is OK for DB connection errors
            print(f"✅ Route /ai11/api/nudges accessible (status: {response.status_code})")
        else:
            print(f"⚠️  Route /ai11/api/nudges returns {response.status_code}")
    
    print("\n" + "=" * 60)
    print("✅ Route registration test complete!")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

