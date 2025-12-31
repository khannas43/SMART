#!/bin/bash
# Script to fix Nginx configuration by adding upstream blocks to main nginx.conf

echo "=== Fixing Nginx Configuration ==="

# Backup main nginx.conf
echo "Step 1: Backing up main nginx.conf..."
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup.$(date +%Y%m%d_%H%M%S)

# Create temporary file with upstream blocks
UPSTREAM_BLOCKS=$(cat <<'EOF'
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
)

# Check if upstream blocks already exist
if sudo grep -q "upstream citizen_backend" /etc/nginx/nginx.conf; then
    echo "Upstream blocks already exist in nginx.conf, skipping..."
else
    echo "Step 2: Adding upstream blocks to main nginx.conf..."
    
    # Use sed to insert upstream blocks after "http {"
    # Create a temporary file with the upstream blocks
    echo "$UPSTREAM_BLOCKS" | sudo tee /tmp/nginx_upstreams.txt > /dev/null
    
    # Insert after "http {" line
    sudo sed -i '/^http {/r /tmp/nginx_upstreams.txt' /etc/nginx/nginx.conf
    
    # Clean up temp file
    sudo rm /tmp/nginx_upstreams.txt
    
    echo "Upstream blocks added successfully."
fi

# Copy updated smart-platform config (without upstream blocks)
echo "Step 3: Updating smart-platform config..."
sudo cp /mnt/c/Projects/SMART/nginx.conf /etc/nginx/sites-available/smart-platform

# Test configuration
echo "Step 4: Testing Nginx configuration..."
if sudo nginx -t; then
    echo "✓ Configuration test passed!"
    echo ""
    echo "Step 5: Reloading Nginx..."
    sudo service nginx reload
    echo "✓ Nginx reloaded!"
    echo ""
    echo "Step 6: Checking ports..."
    sudo ss -tlnp | grep -E "nginx|:3000" || echo "No nginx processes found on port 3000"
else
    echo "✗ Configuration test failed! Please check the error above."
    exit 1
fi

echo ""
echo "=== Done ==="
echo "Check if port 3000 is listening:"
echo "  sudo ss -tlnp | grep :3000"
echo ""
echo "Test the configuration:"
echo "  curl http://localhost:3000"

