# Neo4j WSL Access Setup

## Problem

Neo4j Desktop is running on Windows and accessible via `localhost:7687` from Windows, but **not accessible from WSL**. This is because Neo4j is configured to only listen on `127.0.0.1` (localhost), which doesn't work across WSL/Windows boundary.

## Solution: Configure Neo4j to Listen on All Interfaces

### Step 1: Enable Bolt to Listen on All Interfaces

1. **Stop** the Neo4j instance in Neo4j Desktop
   - Click "Stop" button next to "SMART_GRAPH" instance

2. **Open Configuration**:
   - Click on "SMART_GRAPH" instance
   - Click the **"..."** (three dots) menu button
   - Select **"Settings"** or **"Open Folder"** → **"conf"**
   - Or navigate to: `C:\Users\admin\AppData\Roaming\Neo4j Desktop\Application\relate-data\projects\<project-id>\instances\<instance-id>\`

3. **Edit Configuration File**:
   - Open `conf/neo4j.conf` (or similar)
   - Find the Bolt connector section (search for `dbms.connector.bolt`)
   - Change:
     ```properties
     # BEFORE (only localhost):
     dbms.connector.bolt.listen_address=127.0.0.1:7687
     
     # AFTER (all interfaces):
     dbms.connector.bolt.listen_address=0.0.0.0:7687
     ```
   - If the line doesn't exist, add it:
     ```properties
     dbms.connector.bolt.enabled=true
     dbms.connector.bolt.listen_address=0.0.0.0:7687
     ```

4. **Save** the file

5. **Start** the instance again in Neo4j Desktop

### Step 2: Configure Windows Firewall (if needed)

Windows Firewall might block the connection:

1. Open **Windows Defender Firewall**
2. Go to **"Advanced settings"**
3. Click **"Inbound Rules"** → **"New Rule"**
4. Rule Type: **Port**
5. Protocol: **TCP**
6. Port: **7687**
7. Action: **Allow the connection**
8. Apply to: **All profiles**
9. Name: **Neo4j Bolt**

### Step 3: Verify Connection

After making changes, test:

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/02_eligibility_scoring_360_profile
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/check_neo4j.py
```

## Alternative: Use Port Forwarding (Quick Workaround)

If you can't modify Neo4j config, use port forwarding:

**From WSL:**
```bash
# Install socat if needed
sudo apt-get install socat

# Forward WSL port to Windows localhost
socat TCP-LISTEN:7687,fork,reuseaddr TCP:$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):7687
```

Then use `bolt://localhost:7687` in config (from WSL's perspective).

## Alternative 2: Run from Windows (Not Recommended)

You could run the Python scripts directly from Windows instead of WSL, but this defeats the purpose of using WSL for the AI/ML environment.

## Quick Check: Can WSL Reach Windows?

Test if WSL can reach Windows services:

```bash
# From WSL, test if Windows host is reachable
ping 172.17.16.1

# Test if port is open (if telnet/netcat installed)
nc -zv 172.17.16.1 7687
```

---

**Recommended**: Configure Neo4j to listen on `0.0.0.0:7687` (Step 1) - this is the proper solution.

