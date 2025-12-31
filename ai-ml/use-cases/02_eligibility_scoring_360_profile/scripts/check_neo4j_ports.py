#!/usr/bin/env python3
"""
Check Neo4j Ports and Protocols
"""

import socket
import sys

PORTS_TO_CHECK = [7687, 7474, 7473]

print("=" * 70)
print("Neo4j Port Availability Check")
print("=" * 70)

for port in PORTS_TO_CHECK:
    print(f"\nTesting port {port}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    
    if result == 0:
        print(f"  ✅ Port {port} is OPEN and accepting connections")
        
        # Try to identify what's on this port
        if port == 7687:
            print("     → This is the Bolt protocol port")
        elif port == 7474:
            print("     → This is the HTTP port")
        elif port == 7473:
            print("     → This is the HTTPS port")
    else:
        print(f"  ❌ Port {port} is CLOSED or not accessible")

print("\n" + "=" * 70)
print("Summary:")
print("=" * 70)
print("  • Port 7687 (Bolt) - Required for Python driver")
print("  • Port 7474 (HTTP) - Used by Neo4j Browser")
print("\nIf port 7687 is closed, Bolt protocol might be disabled in Neo4j Desktop.")
print("Check Neo4j Desktop settings → Configuration → Network settings")

