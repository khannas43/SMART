# Nginx Configuration Fix for WSL

## Issue: systemctl doesn't work in WSL

WSL doesn't use systemd by default, so use `service` commands instead of `systemctl`.

## Correct Commands for WSL

### Check Nginx Status
```bash
sudo service nginx status
```

### Start/Stop/Restart Nginx
```bash
sudo service nginx start
sudo service nginx stop
sudo service nginx restart
sudo service nginx reload
```

## Configuration Setup

Since you've already copied the config, let's verify and fix if needed:

### Step 1: Verify Main nginx.conf Includes sites-enabled

Check if the main nginx.conf includes sites-enabled:

```bash
cat /etc/nginx/nginx.conf | grep "include.*sites-enabled"
```

You should see something like:
```
include /etc/nginx/sites-enabled/*;
```

If you don't see this, we need to add it or use a different approach.

### Step 2: Check Current Configuration

```bash
# Check if symlink was created
ls -la /etc/nginx/sites-enabled/

# Check if the config file exists
cat /etc/nginx/sites-available/smart-platform | head -20
```

### Step 3: Test Configuration

```bash
sudo nginx -t
```

### Step 4: Reload Nginx (using service command)

```bash
sudo service nginx reload
```

Or restart:

```bash
sudo service nginx restart
```

### Step 5: Verify Nginx is Running

```bash
sudo service nginx status
```

### Step 6: Test Port 3000

```bash
curl http://localhost:3000
```

Or check if port is listening:

```bash
sudo netstat -tlnp | grep :3000
```

## Alternative: If Configuration Doesn't Work

If the sites-enabled approach doesn't work, we can:

### Option A: Include the config in main nginx.conf

Add this line to `/etc/nginx/nginx.conf` in the `http` block:

```bash
sudo nano /etc/nginx/nginx.conf
```

Add before the closing `}` of the `http` block:
```
    include /etc/nginx/sites-enabled/*;
```

### Option B: Replace main nginx.conf (Backup First!)

```bash
# Backup current config
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup

# Copy our config
sudo cp /mnt/c/Projects/SMART/nginx.conf /etc/nginx/nginx.conf
```

**Note**: Option B will replace the entire nginx.conf. Only do this if you're sure.

## Recommended Approach

The best approach is to ensure the main nginx.conf includes sites-enabled:

1. Check main nginx.conf:
   ```bash
   sudo cat /etc/nginx/nginx.conf
   ```

2. If it doesn't include sites-enabled, edit it:
   ```bash
   sudo nano /etc/nginx/nginx.conf
   ```
   
   In the `http` block, add:
   ```
   include /etc/nginx/sites-enabled/*;
   ```

3. Test and reload:
   ```bash
   sudo nginx -t
   sudo service nginx reload
   ```

## Quick Commands Summary

```bash
# Status
sudo service nginx status

# Test config
sudo nginx -t

# Reload (apply changes without downtime)
sudo service nginx reload

# Restart (full restart)
sudo service nginx restart

# Stop
sudo service nginx stop

# Start
sudo service nginx start

# Check if port 3000 is listening
sudo netstat -tlnp | grep :3000
# or
curl http://localhost:3000
```

