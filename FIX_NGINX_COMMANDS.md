# Commands to Fix Nginx Configuration

## Run These Commands in WSL Terminal (One by One)

### Step 1: Backup main nginx.conf
```bash
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup
```

### Step 2: Copy updated smart-platform config (without upstream blocks)
```bash
sudo cp /mnt/c/Projects/SMART/nginx.conf /etc/nginx/sites-available/smart-platform
```

### Step 3: Add upstream blocks to main nginx.conf using sed

This command will add the upstream blocks right after the `http {` line:

```bash
sudo sed -i '/^http {/a\
    # SMART Platform Upstream Backends\
    upstream citizen_backend {\
        server localhost:8080;\
    }\
\
    upstream dept_backend {\
        server localhost:8081;\
    }\
\
    upstream aiml_backend {\
        server localhost:8082;\
    }\
\
    upstream monitor_backend {\
        server localhost:8083;\
    }\
' /etc/nginx/nginx.conf
```

**OR** use a simpler approach with a temporary file:

```bash
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

# Insert after "http {" line
sudo sed -i '/^http {/r /tmp/upstreams.txt' /etc/nginx/nginx.conf

# Clean up
rm /tmp/upstreams.txt
```

### Step 4: Test configuration
```bash
sudo nginx -t
```

### Step 5: If test passes, reload Nginx
```bash
sudo service nginx reload
```

### Step 6: Check if port 3000 is listening
```bash
sudo ss -tlnp | grep :3000
```

### Step 7: Test it
```bash
curl http://localhost:3000
```

---

## Alternative: Manual Edit (If sed doesn't work)

If the sed command doesn't work, you can edit manually:

```bash
# Edit the file
sudo nano /etc/nginx/nginx.conf

# Find the line that says: http {
# Right after that line, paste these upstream blocks:

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

# Save with Ctrl+O, Enter, Ctrl+X
```

Then continue with Step 4 above.

