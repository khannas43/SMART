# Neo4j Configuration Fix - Correct Format

## Issue

You added these lines (which are the **old Neo4j 4.x format**):
```properties
dbms.connector.bolt.enabled=true
dbms.connector.bolt.listen_address=0.0.0.0:7687
```

But your Neo4j version (5.11.2) uses the **new format**: `server.bolt.*`

## ✅ Correct Fix

### Step 1: Remove the Old Lines

In your `neo4j.conf` file, **remove or comment out**:
```properties
dbms.connector.bolt.enabled=true
dbms.connector.bolt.listen_address=0.0.0.0:7687
```

### Step 2: Use the Correct Format

Find this section in your config (around line 163):
```properties
# Bolt connector
server.bolt.enabled=true
#server.bolt.tls_level=DISABLED
#server.bolt.listen_address=:7687
#server.bolt.advertised_address=:7687
```

**Uncomment and modify** the `listen_address` line:
```properties
# Bolt connector
server.bolt.enabled=true
#server.bolt.tls_level=DISABLED
server.bolt.listen_address=0.0.0.0:7687
#server.bolt.advertised_address=:7687
```

**Important**: Use `0.0.0.0:7687` (not `:7687`) to listen on all interfaces.

### Step 3: Also Check HTTP Settings (Optional)

If you want HTTP access from WSL too, find:
```properties
# HTTP Connector. There can be zero or one HTTP connectors.
server.http.enabled=true
#server.http.listen_address=:7474
#server.http.advertised_address=:7474
```

Uncomment and modify:
```properties
server.http.listen_address=0.0.0.0:7474
```

### Step 4: Restart Neo4j Instance

1. **Stop** the instance in Neo4j Desktop
2. **Wait 5 seconds**
3. **Start** the instance again
4. Wait for **"RUNNING"** status

### Step 5: Verify Port is Listening

From WSL, test:
```bash
# Test if port 7687 is now accessible
nc -zv 172.17.16.1 7687
```

Or run:
```bash
python scripts/check_neo4j_ports.py
```

You should see:
```
✅ Port 7687 is OPEN and accepting connections
```

### Step 6: Test Connection

```bash
python scripts/check_neo4j.py
```

## Summary

**Old format (4.x)** - ❌ Don't use:
```
dbms.connector.bolt.listen_address=0.0.0.0:7687
```

**New format (5.x)** - ✅ Use this:
```
server.bolt.listen_address=0.0.0.0:7687
```

---

**After fixing, restart Neo4j instance and test again!**

