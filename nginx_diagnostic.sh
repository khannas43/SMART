#!/bin/bash
# Nginx Diagnostic Script

echo "=== Step 1: Check symlink ==="
ls -la /etc/nginx/sites-enabled/

echo ""
echo "=== Step 2: Check what ports Nginx is listening on ==="
sudo ss -tlnp | grep nginx

echo ""
echo "=== Step 3: Check Nginx error log ==="
sudo tail -10 /var/log/nginx/error.log

echo ""
echo "=== Step 4: Test Nginx configuration ==="
sudo nginx -t

echo ""
echo "=== Step 5: Check if config file is readable ==="
sudo head -30 /etc/nginx/sites-available/smart-platform

echo ""
echo "=== Step 6: Check Nginx status ==="
sudo service nginx status

