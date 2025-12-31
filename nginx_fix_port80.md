# Fix: Nginx Still Listening on Port 80

## Problem
- Symlink exists ✅
- Config is loaded ✅ (we can see "listen 3000" in nginx -T)
- But Nginx is still listening on port 80 ❌

## Solution: Check for conflicting server blocks and restart

### Step 1: Check all server blocks in the configuration
```bash
sudo nginx -T | grep -E "listen|server_name" | head -20
```

### Step 2: Check if there are other config files
```bash
sudo ls -la /etc/nginx/conf.d/
```

### Step 3: Full restart (not just reload)
```bash
sudo service nginx stop
sudo service nginx start
```

### Step 4: Verify port 3000 is now listening
```bash
sudo ss -tlnp | grep :3000
```

### Step 5: Check what ports Nginx is using now
```bash
sudo ss -tlnp | grep nginx
```

## Alternative: Check if default site was fully removed

```bash
# Check if default still exists in sites-available
ls -la /etc/nginx/sites-available/default

# If it exists, make sure it's not enabled
ls -la /etc/nginx/sites-enabled/ | grep default
```

## If still not working: Check the actual loaded configuration

```bash
# See all server blocks
sudo nginx -T | grep -B 5 -A 10 "server {"

# See what's listening on port 80
sudo nginx -T | grep -B 5 "listen 80"
```

