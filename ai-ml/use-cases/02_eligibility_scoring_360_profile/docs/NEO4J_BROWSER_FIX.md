# Fix Neo4j Browser Connection Error

## Problem

Getting error: "Instance connection URL is not valid" when trying to open Browser or Query tool.

This is because **HTTP connector** (used by Browser) might not be configured to listen on all interfaces.

## Solution: Enable HTTP on All Interfaces

### Step 1: Edit neo4j.conf

Find this section (around line 126-129):
```properties
# HTTP Connector. There can be zero or one HTTP connectors.
server.http.enabled=true
#server.http.listen_address=:7474
#server.http.advertised_address=:7474
```

**Uncomment and modify** the `listen_address` line:
```properties
# HTTP Connector. There can be zero or one HTTP connectors.
server.http.enabled=true
server.http.listen_address=0.0.0.0:7474
#server.http.advertised_address=:7474
```

**Important**: Use `0.0.0.0:7474` (not `:7474`) to listen on all interfaces.

### Step 2: Restart Neo4j

1. **Stop** the instance in Neo4j Desktop
2. **Wait 5 seconds**
3. **Start** the instance again
4. **Wait for "RUNNING" status**

### Step 3: Try Opening Browser Again

1. Click on **"SMART_GRAPH"** instance
2. Click **"Open"** button
3. Or click on **"smartgraphdb"** database → **"Open Browser"**

## Alternative: Manual Browser Access

If the "Open" button still doesn't work, try:

1. **Open your web browser**
2. **Navigate to**: `http://localhost:7474`
3. **Enter connection details**:
   - **Connect URL**: `bolt://localhost:7687`
   - **Username**: `neo4j`
   - **Password**: `anjali143`
4. Click **"Connect"**

## Verify HTTP is Working

From WSL, test HTTP port:
```bash
curl http://172.17.16.1:7474
```

Or test from Windows PowerShell:
```powershell
Invoke-WebRequest -Uri http://localhost:7474
```

You should see HTML response or connection succeed.

## Complete Network Configuration Summary

Your `neo4j.conf` should have:

```properties
# Bolt connector (for Python driver)
server.bolt.enabled=true
server.bolt.listen_address=0.0.0.0:7687

# HTTP connector (for Browser/Query tools)
server.http.enabled=true
server.http.listen_address=0.0.0.0:7474
```

Both should use `0.0.0.0` to accept connections from all interfaces (including localhost).

---

**After fixing HTTP config and restarting, Browser should work!**

