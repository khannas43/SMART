#!/bin/bash
# Script to create Nginx symlink for smart-platform

echo "Creating symlink for smart-platform..."
sudo ln -s /etc/nginx/sites-available/smart-platform /etc/nginx/sites-enabled/smart-platform

echo "Verifying symlink creation..."
ls -la /etc/nginx/sites-enabled/

echo "Testing Nginx configuration..."
sudo nginx -t

echo "Reloading Nginx..."
sudo service nginx reload

echo "Checking if port 3000 is listening..."
sudo ss -tlnp | grep :3000

echo "Testing with curl..."
curl http://localhost:3000

