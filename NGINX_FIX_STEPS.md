# Fix Nginx Configuration - Step by Step

## Problem Identified

- Nginx is listening on port 80 (default site) instead of port 3000
- The `smart-platform` symlink is missing from `/etc/nginx/sites-enabled/`
- Only the `default` site is enabled

## Solution: Enable smart-platform and Disable default

Run these commands in WSL:

### Step 1: Remove default site
```bash
sudo rm /etc/nginx/sites-enabled/default
```

### Step 2: Create symlink for smart-platform
```bash
sudo ln -s /etc/nginx/sites-available/smart-platform /etc/nginx/sites-enabled/smart-platform
```

### Step 3: Verify symlink was created
```bash
ls -la /etc/nginx/sites-enabled/
```

You should now see:
```
smart-platform -> /etc/nginx/sites-available/smart-platform
```

### Step 4: Test Nginx configuration
```bash
sudo nginx -t
```

### Step 5: Reload Nginx
```bash
sudo service nginx reload
```

### Step 6: Verify port 3000 is listening
```bash
sudo ss -tlnp | grep :3000
```

You should see output like:
```
LISTEN 0  511  0.0.0.0:3000  0.0.0.0:*  users:(("nginx",...))
```

### Step 7: Test in browser or curl
```bash
curl http://localhost:3000
```

Or open in browser: `http://localhost:3000`

---

## Complete Command Sequence

Copy and paste this entire block:

```bash
# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Create symlink for smart-platform
sudo ln -s /etc/nginx/sites-available/smart-platform /etc/nginx/sites-enabled/smart-platform

# Verify
ls -la /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload nginx
sudo service nginx reload

# Check port 3000
sudo ss -tlnp | grep :3000

# Test
curl http://localhost:3000
```

