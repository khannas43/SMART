# Nginx Troubleshooting - Port 3000 Not Working

## Quick Diagnostic Commands

### 1. Check if port 3000 is listening (use `ss` instead of `netstat`)
```bash
sudo ss -tlnp | grep :3000
```

### 2. Check Nginx Configuration Structure
```bash
# Check if sites-enabled is included in main config
sudo grep -n "include.*sites-enabled" /etc/nginx/nginx.conf

# Check if our config file exists
sudo cat /etc/nginx/sites-available/smart-platform | head -30

# Check if symlink is correct
ls -la /etc/nginx/sites-enabled/
```

### 3. Check Nginx Error Logs
```bash
sudo tail -20 /var/log/nginx/error.log
```

### 4. Check What Ports Nginx is Actually Listening On
```bash
sudo ss -tlnp | grep nginx
```

### 5. Check Nginx Configuration Test Output in Detail
```bash
sudo nginx -T | grep -A 5 "listen"
```

## Likely Issue: sites-enabled Not Included

If `grep -n "include.*sites-enabled"` returns nothing, we need to add it to the main nginx.conf.

### Fix: Add sites-enabled to Main nginx.conf

```bash
# Backup the config first
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup

# Edit the config
sudo nano /etc/nginx/nginx.conf
```

In the `http` block, find the section that has other `include` directives (usually near the end), and add:

```
include /etc/nginx/sites-enabled/*;
```

Then:
```bash
# Test configuration
sudo nginx -t

# If test passes, reload
sudo service nginx reload
```

## Alternative: Check Default Port

Check what port the default nginx is listening on:
```bash
sudo ss -tlnp | grep nginx
```

You might see it's listening on port 80, not 3000. This means the sites-enabled config isn't being loaded.

## Quick Fix: Verify Main nginx.conf Structure

Run this to see the structure:
```bash
sudo cat /etc/nginx/nginx.conf
```

Look for an `http` block and see if it includes:
- `include /etc/nginx/conf.d/*.conf;`
- `include /etc/nginx/sites-enabled/*;`

If `sites-enabled` is missing, add it.

