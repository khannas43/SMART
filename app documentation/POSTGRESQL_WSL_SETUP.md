# PostgreSQL WSL Connection Setup Guide

PostgreSQL is running on Windows, but WSL cannot connect to it. This guide helps you configure PostgreSQL to be accessible from WSL.

## Issue

When connecting from WSL, PostgreSQL connection fails with "Connection refused" even though PostgreSQL is running on Windows and port 5432 is accessible from Windows PowerShell.

## Solution Options

### Option 1: Configure PostgreSQL to Listen on All Interfaces (Recommended)

1. **Find PostgreSQL configuration directory:**
   ```powershell
   # Usually located at:
   # C:\Program Files\PostgreSQL\{version}\data\
   ```

2. **Edit `postgresql.conf`:**
   ```powershell
   # Open as Administrator
   notepad "C:\Program Files\PostgreSQL\{version}\data\postgresql.conf"
   ```
   
   Find and change:
   ```
   #listen_addresses = 'localhost'
   ```
   To:
   ```
   listen_addresses = '*'
   ```

3. **Edit `pg_hba.conf` to allow connections:**
   ```powershell
   notepad "C:\Program Files\PostgreSQL\{version}\data\pg_hba.conf"
   ```
   
   Add this line (or ensure it exists):
   ```
   host    all             all             127.0.0.1/32            md5
   host    all             all             ::1/128                 md5
   ```

4. **Restart PostgreSQL service:**
   ```powershell
   # Find service name
   Get-Service -Name postgresql*
   
   # Restart (run as Administrator)
   Restart-Service -Name postgresql-x64-{version}
   ```

5. **Get Windows IP address for WSL:**
   ```powershell
   # In PowerShell (Windows)
   ipconfig | findstr IPv4
   ```
   
   Or get the WSL host IP:
   ```bash
   # In WSL
   cat /etc/resolv.conf | grep nameserver | awk '{print $2}'
   ```

6. **Test connection from WSL:**
   ```bash
   # Use the Windows host IP
   psql -h <WINDOWS_IP> -p 5432 -U sameer -d smart
   ```

### Option 2: Use Windows Hostname (Easier)

If Option 1 doesn't work, try using the Windows hostname directly:

1. **Get Windows hostname:**
   ```bash
   # From WSL
   hostname.exe
   ```

2. **Use hostname in connection:**
   ```bash
   psql -h DESKTOP-BTUEFC0 -p 5432 -U sameer -d smart
   ```

3. **Update test script:**
   The updated `test-database-connection.py` already tries the Windows hostname automatically.

### Option 3: Install PostgreSQL in WSL (Alternative)

If you prefer to run PostgreSQL directly in WSL:

```bash
# In WSL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL
sudo service postgresql start

# Create database and user
sudo -u postgres psql
CREATE DATABASE smart;
CREATE USER sameer WITH PASSWORD 'anjali143';
GRANT ALL PRIVILEGES ON DATABASE smart TO sameer;
\q
```

Then update configuration files to use `localhost` (WSL localhost).

## Quick Test Commands

### From Windows PowerShell:
```powershell
$env:PGPASSWORD="anjali143"
psql -h localhost -p 5432 -U sameer -d smart -c "SELECT version();"
```

### From WSL (after configuration):
```bash
# Try Windows IP
export PGPASSWORD="anjali143"
psql -h $(cat /etc/resolv.conf | grep nameserver | awk '{print $2}') -p 5432 -U sameer -d smart

# Or try hostname
psql -h DESKTOP-BTUEFC0 -p 5432 -U sameer -d smart
```

### Using Python test script:
```bash
cd /mnt/c/Projects/SMART
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/test-database-connection.py
```

## Troubleshooting

### Firewall Issues
If connection still fails, check Windows Firewall:
```powershell
# Allow PostgreSQL through firewall (run as Administrator)
New-NetFirewallRule -DisplayName "PostgreSQL" -Direction Inbound -Protocol TCP -LocalPort 5432 -Action Allow
```

### Check PostgreSQL Status
```powershell
# Check if PostgreSQL is running
Get-Service -Name postgresql*

# Check listening ports
netstat -an | findstr 5432
```

### Verify PostgreSQL is Listening
PostgreSQL should be listening on `0.0.0.0:5432` or at least `127.0.0.1:5432`:
```powershell
netstat -an | findstr "5432"
# Should show: 0.0.0.0:5432 or 127.0.0.1:5432
```

## Recommended Configuration for Development

For local development, the easiest approach is:
1. Use PostgreSQL on Windows (already running)
2. Configure it to listen on all interfaces (`listen_addresses = '*'`)
3. Use Windows hostname or IP from WSL

This allows both Windows and WSL to connect to the same database instance.

