#!/usr/bin/env python3
"""
Script to add upstream blocks to nginx.conf
Run with: sudo python3 fix_nginx_upstream.py
"""

import sys
import os

NGINX_CONF = '/etc/nginx/nginx.conf'

UPSTREAM_BLOCKS = """    # SMART Platform Upstream Backends
    upstream citizen_backend {
        server localhost:8080;
    }

    upstream dept_backend {
        server localhost:8081;
    }

    upstream aiml_backend {
        server localhost:8082;
    }

    upstream monitor_backend {
        server localhost:8083;
    }

"""

def add_upstream_blocks():
    # Check if we have write permissions
    if not os.access(NGINX_CONF, os.W_OK):
        print(f"Error: No write permission for {NGINX_CONF}")
        print("Please run this script with sudo: sudo python3 fix_nginx_upstream.py")
        sys.exit(1)
    
    # Read the current config
    with open(NGINX_CONF, 'r') as f:
        content = f.read()
    
    # Check if upstream blocks already exist
    if 'upstream citizen_backend' in content:
        print("✓ Upstream blocks already exist in nginx.conf")
        return
    
    # Find "http {" and add upstream blocks after it
    if 'http {' not in content:
        print("Error: Could not find 'http {' in nginx.conf")
        sys.exit(1)
    
    # Split by "http {" and reconstruct
    parts = content.split('http {', 1)
    if len(parts) != 2:
        print("Error: Unexpected nginx.conf structure")
        sys.exit(1)
    
    # Reconstruct with upstream blocks
    new_content = parts[0] + 'http {' + '\n' + UPSTREAM_BLOCKS + parts[1]
    
    # Backup original
    backup_file = NGINX_CONF + '.backup.' + str(os.getpid())
    with open(backup_file, 'w') as f:
        f.write(content)
    print(f"✓ Created backup: {backup_file}")
    
    # Write new content
    with open(NGINX_CONF, 'w') as f:
        f.write(new_content)
    
    print("✓ Upstream blocks added successfully to nginx.conf")

if __name__ == '__main__':
    try:
        add_upstream_blocks()
        print("\nNext steps:")
        print("1. Test configuration: sudo nginx -t")
        print("2. Start/reload nginx: sudo service nginx start")
        print("3. Check port 3000: sudo ss -tlnp | grep :3000")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

