# Neo4j Connection Fix Guide

## Issue: Connection Refused

If you see "Connection refused" errors, the Neo4j database within the instance might not be started.

## Solution Steps

### Step 1: Start the Database in Neo4j Desktop

In Neo4j Desktop:

1. **Click on the `smartgraphdb` database** (not just the instance)
   - It should be listed under "SMART_GRAPH" instance → "Databases (3)"
   - Click directly on `smartgraphdb`

2. **Look for a "Start" or "Play" button** next to the database
   - Some versions show database status: "Inactive" or "Active"
   - If inactive, click "Start" to activate it

3. **Wait for database to start** (green indicator)

### Step 2: Verify Database is Active

After starting, you should see:
- ✅ Green status indicator
- ✅ "Active" status
- ✅ Connection details visible

### Step 3: Check Connection Details

In Neo4j Desktop, when you click on `smartgraphdb`:

1. Look for **"Connection Details"** or **"Connection URI"**
2. Note the exact URI shown (might be different format)
3. Verify the port number (usually 7687 for Bolt)

### Step 4: Test Connection Again

Once database is active, run:

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/02_eligibility_scoring_360_profile
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/check_neo4j.py
```

## Alternative: Use Neo4j Browser First

1. **Open Neo4j Browser**:
   - In Neo4j Desktop, click "Open" button next to `smartgraphdb`
   - Or click the database and select "Open Browser"

2. **Connect in Browser**:
   - Enter password: `anjali143`
   - If connection works here, Python should work too

3. **Test a query**:
   ```cypher
   RETURN 1 as test
   ```

If Browser works but Python doesn't, there might be a port/protocol issue.

## If Still Not Working: Check Neo4j Settings

### Enable Bolt Protocol

1. In Neo4j Desktop, click on your **instance** ("SMART_GRAPH")
2. Go to **"Settings"** or **"Configuration"**
3. Ensure **Bolt protocol is enabled** on port 7687
4. Check for any firewall/network restrictions

### Check Port Availability

From WSL, test if port is reachable:

```bash
# Test if port 7687 is open
nc -zv 127.0.0.1 7687

# Or using telnet (if available)
telnet 127.0.0.1 7687
```

If port is not reachable, Neo4j might not be accepting connections.

## Alternative Connection Method

If WSL can't connect directly, you might need to:

1. **Use Windows IP from WSL**:
   - Find Windows host IP: Look in Neo4j Desktop connection details
   - Update config with that IP instead of `127.0.0.1`

2. **Use Neo4j HTTP API** (not recommended, slower):
   - Change URI to: `http://127.0.0.1:7474`
   - Requires different connection method

## Quick Checklist

- [ ] Neo4j Desktop application is running
- [ ] "SMART_GRAPH" instance shows "RUNNING"
- [ ] `smartgraphdb` database is **started/active** (not just listed)
- [ ] Database shows green status indicator
- [ ] Can connect via Neo4j Browser
- [ ] Bolt protocol enabled on port 7687
- [ ] Firewall allows connections on port 7687

## Still Having Issues?

Try using the default `neo4j` database instead:

1. In Neo4j Desktop, start the `neo4j` database (under same instance)
2. Update config:
   ```yaml
   database: neo4j
   ```
3. Test connection again

---

**Most Common Issue**: The database itself needs to be started separately from the instance!

