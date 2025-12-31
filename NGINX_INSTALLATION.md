# Nginx Installation Guide for SMART Platform

## Installation Steps for WSL (Ubuntu)

### Step 1: Update Package List
```bash
sudo apt update
```

### Step 2: Install Nginx
```bash
sudo apt install nginx -y
```

### Step 3: Verify Installation
```bash
nginx -v
```

You should see output like: `nginx version: nginx/1.xx.x`

### Step 4: Check Nginx Status
```bash
sudo systemctl status nginx
```

If you see "Active: active (running)", Nginx is running. If not, start it with:
```bash
sudo service nginx start
```

### Step 5: Verify Nginx is Running
```bash
curl http://localhost
```

You should see the default Nginx welcome page HTML.

---

## Configuration for SMART Platform

### Step 6: Copy Nginx Configuration

From your WSL terminal, navigate to the SMART project directory:

```bash
cd /mnt/c/Projects/SMART
```

Copy the nginx.conf to Nginx configuration directory:

```bash
# Backup default config (optional but recommended)
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup

# Copy SMART platform configuration
sudo cp nginx.conf /etc/nginx/sites-available/smart-platform

# Create symbolic link to enable the site
sudo ln -s /etc/nginx/sites-available/smart-platform /etc/nginx/sites-enabled/

# Remove default site (optional - to avoid conflicts)
sudo rm /etc/nginx/sites-enabled/default
```

### Step 7: Test Nginx Configuration

```bash
sudo nginx -t
```

You should see:
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### Step 8: Reload Nginx

```bash
sudo systemctl reload nginx
```

Or restart Nginx:

```bash
sudo systemctl restart nginx
```

### Step 9: Verify Configuration is Working

```bash
# Check Nginx status
sudo systemctl status nginx

# Test if port 3000 is listening
sudo netstat -tlnp | grep :3000
# or
sudo ss -tlnp | grep :3000
```

---

## Starting/Stopping Nginx

### Start Nginx
```bash
sudo service nginx start
# or
sudo systemctl start nginx
```

### Stop Nginx
```bash
sudo service nginx stop
# or
sudo systemctl stop nginx
```

### Restart Nginx
```bash
sudo service nginx restart
# or
sudo systemctl restart nginx
```

### Reload Configuration (without stopping)
```bash
sudo service nginx reload
# or
sudo systemctl reload nginx
```

---

## Troubleshooting

### If Nginx fails to start:

1. **Check error logs:**
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

2. **Check if port 3000 is already in use:**
   ```bash
   sudo lsof -i :3000
   # or
   sudo netstat -tlnp | grep :3000
   ```

3. **Check Nginx configuration syntax:**
   ```bash
   sudo nginx -t
   ```

### Common Issues:

1. **Port already in use**: Change the port in `nginx.conf` or stop the service using that port
2. **Permission denied**: Make sure you're using `sudo` for Nginx commands
3. **Config file not found**: Verify the path to nginx.conf is correct

---

## Alternative: Install on Windows (if preferred)

If you prefer to run Nginx on Windows instead of WSL:

### Option 1: Using Chocolatey
```powershell
# Install Chocolatey (if not installed)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Nginx
choco install nginx -y
```

### Option 2: Manual Installation
1. Download Nginx for Windows: http://nginx.org/en/download.html
2. Extract to `C:\nginx`
3. Copy `nginx.conf` to `C:\nginx\conf\`
4. Run: `C:\nginx\nginx.exe`

---

## Quick Reference

### Important Paths (WSL)
- Configuration: `/etc/nginx/nginx.conf`
- Sites available: `/etc/nginx/sites-available/`
- Sites enabled: `/etc/nginx/sites-enabled/`
- Logs: `/var/log/nginx/`
- Error log: `/var/log/nginx/error.log`
- Access log: `/var/log/nginx/access.log`

### Important Paths (Windows)
- Configuration: `C:\nginx\conf\nginx.conf`
- Logs: `C:\nginx\logs\`

---

## Next Steps

After installing and configuring Nginx:

1. Start all backend services on their respective ports (8080, 8081, 8082, 8083)
2. Start Nginx (port 3000)
3. Test portal URLs:
   - http://localhost:3000/citizen
   - http://localhost:3000/dept
   - http://localhost:3000/insight
   - http://localhost:3000/monitor

See [PORTAL_ROUTING.md](PORTAL_ROUTING.md) for more details.

