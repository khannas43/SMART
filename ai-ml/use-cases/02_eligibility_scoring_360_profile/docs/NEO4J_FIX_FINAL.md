# Final Neo4j Config Fix

## Problem

You have **TWO** Bolt configurations:
1. **Old format** (lines 41-42): `dbms.connector.bolt.*` - ❌ Remove this
2. **Correct format** (line 123): `server.bolt.listen_address=:7687` - ⚠️ But it's binding to localhost only

## Solution: Make These Two Changes

### Change 1: Remove Old Format (Lines 41-42)

Find and **DELETE or COMMENT OUT** these lines:
```properties
dbms.connector.bolt.enabled=true
dbms.connector.bolt.listen_address=0.0.0.0:7687
```

Or comment them:
```properties
#dbms.connector.bolt.enabled=true
#dbms.connector.bolt.listen_address=0.0.0.0:7687
```

### Change 2: Fix Line 123

Find line 123:
```properties
server.bolt.listen_address=:7687
```

**Change it to:**
```properties
server.bolt.listen_address=0.0.0.0:7687
```

The `:7687` binds only to localhost. `0.0.0.0:7687` binds to all interfaces (allows WSL access).

## After Making Changes

1. **Save** the config file
2. **Stop** Neo4j instance in Neo4j Desktop
3. **Wait 5 seconds**
4. **Start** Neo4j instance again
5. **Wait for "RUNNING" status**
6. **Test:**
   ```bash
   python scripts/check_neo4j.py
   ```

## Summary

**Remove:**
```properties
dbms.connector.bolt.enabled=true
dbms.connector.bolt.listen_address=0.0.0.0:7687
```

**Change:**
```properties
# FROM:
server.bolt.listen_address=:7687

# TO:
server.bolt.listen_address=0.0.0.0:7687
```

---

**Restart Neo4j after making these changes!**

