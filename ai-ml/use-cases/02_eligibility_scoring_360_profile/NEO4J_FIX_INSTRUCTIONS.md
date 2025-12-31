# 🔧 Quick Fix: Enable Neo4j Access from WSL

## Current Issue

Neo4j is running but **not accessible from WSL** because it's only listening on `127.0.0.1` (localhost).

## ✅ Quick Fix Steps

### 1. Stop Neo4j Instance

In Neo4j Desktop:
- Click **"Stop"** button next to "SMART_GRAPH" instance

### 2. Edit Neo4j Configuration

1. Click on **"SMART_GRAPH"** instance in Neo4j Desktop
2. Click the **"..."** (three dots) menu at the top right
3. Select **"Settings"** or **"Open Folder"**
4. Navigate to **`conf`** folder
5. Open **`neo4j.conf`** file (or `neo4j-server.properties`)

### 3. Find and Update Bolt Settings

Search for `dbms.connector.bolt` and change:

**FIND:**
```properties
dbms.connector.bolt.listen_address=127.0.0.1:7687
```

**CHANGE TO:**
```properties
dbms.connector.bolt.listen_address=0.0.0.0:7687
```

If this line doesn't exist, **ADD these lines**:
```properties
dbms.connector.bolt.enabled=true
dbms.connector.bolt.listen_address=0.0.0.0:7687
```

### 4. Save and Restart

1. **Save** the configuration file
2. **Start** the "SMART_GRAPH" instance again in Neo4j Desktop
3. Wait for it to show **"RUNNING"** status

### 5. Test Connection

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/eligibility_scoring_360_profile
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/check_neo4j.py
```

You should see:
```
✅ Connected successfully!
   Nodes: 0
   Relationships: 0
```

## ⚠️ Windows Firewall (If Still Not Working)

If connection still fails, Windows Firewall might be blocking:

1. Open **Windows Defender Firewall**
2. **Allow an app or feature through Windows Firewall**
3. Or create inbound rule for **TCP port 7687**

---

**Once working, you can proceed with:**
```bash
cd src
python graph_clustering_neo4j.py
```

