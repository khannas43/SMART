#!/bin/bash
# Add upstream blocks to nginx.conf

# Create temp file with upstream blocks
cat > /tmp/nginx_upstreams.txt << 'EOF'
    # SMART Platform Upstream Backends
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

EOF

# Read nginx.conf and insert upstream blocks after "http {"
sudo python3 << 'PYTHON'
import sys
import re

# Read the file
with open('/etc/nginx/nginx.conf', 'r') as f:
    lines = f.readlines()

# Find the line with "http {"
new_lines = []
upstream_added = False
with open('/tmp/nginx_upstreams.txt', 'r') as f:
    upstream_content = f.read()

for i, line in enumerate(lines):
    new_lines.append(line)
    # If we find "http {" and haven't added upstreams yet
    if line.strip() == 'http {' and not upstream_added:
        # Check if upstream already exists
        if 'upstream citizen_backend' not in ''.join(lines):
            new_lines.append(upstream_content)
            upstream_added = True

# Write back
with open('/etc/nginx/nginx.conf', 'w') as f:
    f.writelines(new_lines)

if upstream_added:
    print("✓ Upstream blocks added successfully!")
else:
    print("Upstream blocks may already exist or http block not found")
PYTHON

# Clean up
rm /tmp/nginx_upstreams.txt

