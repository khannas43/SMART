#!/bin/bash
# Script to add upstream blocks to nginx.conf

# Create the upstream blocks file
cat > /tmp/upstreams.txt << 'EOF'
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

# Check if upstream blocks already exist
if sudo grep -q "upstream citizen_backend" /etc/nginx/nginx.conf; then
    echo "Upstream blocks already exist, skipping..."
else
    # Insert after "http {" line
    sudo sed -i '/^http {/r /tmp/upstreams.txt' /etc/nginx/nginx.conf
    echo "Upstream blocks added successfully!"
fi

# Clean up
rm /tmp/upstreams.txt

