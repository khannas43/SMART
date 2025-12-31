#!/bin/bash
echo "=== Checking Nginx Configuration ==="
echo ""

echo "1. Checking if upstream blocks exist in nginx.conf:"
sudo grep -A 5 "upstream citizen_backend" /etc/nginx/nginx.conf || echo "Upstream blocks NOT found"
echo ""

echo "2. Testing Nginx configuration:"
sudo nginx -t
echo ""

echo "3. Checking what ports Nginx is listening on:"
sudo ss -tlnp | grep nginx || echo "No nginx processes found"
echo ""

echo "4. Checking specifically for port 3000:"
sudo ss -tlnp | grep :3000 || echo "Port 3000 NOT listening"
echo ""

echo "5. Testing curl on port 3000:"
curl -v http://localhost:3000 2>&1 | head -20
echo ""

echo "6. Checking smart-platform symlink:"
ls -la /etc/nginx/sites-enabled/ | grep smart-platform
echo ""

echo "=== Done ==="

