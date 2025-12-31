# Fix: Nginx Configuration Structure

## Problem Found

The `upstream` directive cannot be in a site-specific config file. It must be in the main `nginx.conf` file's `http` block.

Error: `"upstream" directive is not allowed here`

## Solution: Move Upstream Blocks to Main nginx.conf

### Step 1: Edit main nginx.conf

```bash
sudo nano /etc/nginx/nginx.conf
```

Find the `http {` block and add the upstream definitions right after the opening `http {` brace, before any other directives:

```nginx
http {
    # Add these upstream blocks here
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

    # ... rest of existing http block content ...
```

### Step 2: Update smart-platform config

The `smart-platform` config file should now only contain the `server {}` block (no upstream blocks).

The file `/etc/nginx/sites-available/smart-platform` should start with `server {` not `upstream`.

### Step 3: Test Configuration

```bash
sudo nginx -t
```

### Step 4: Reload Nginx

```bash
sudo service nginx reload
```

### Step 5: Verify Port 3000

```bash
sudo ss -tlnp | grep :3000
```

## Quick Fix Commands

```bash
# 1. Backup main nginx.conf
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup2

# 2. Edit main nginx.conf
sudo nano /etc/nginx/nginx.conf

# 3. In nano, find the line: http {
# 4. Right after that line, add the upstream blocks from nginx_upstreams.conf
# 5. Save (Ctrl+O, Enter, Ctrl+X)

# 6. Test
sudo nginx -t

# 7. Reload
sudo service nginx reload

# 8. Check port 3000
sudo ss -tlnp | grep :3000
```

## Alternative: Use Separate Include File

Instead of editing main nginx.conf directly, you can:

1. Create `/etc/nginx/upstreams.conf` with the upstream blocks
2. In main `nginx.conf`, inside `http {}`, add: `include /etc/nginx/upstreams.conf;`

This keeps the configuration more modular.

