# Enable Bolt Protocol in Neo4j Desktop

## Issue

You can access Neo4j via HTTP (`localhost:7687` returns JSON), but Python connections via Bolt protocol are failing. This means **Bolt protocol might be disabled**.

## Solution: Enable Bolt Protocol

### Method 1: Via Neo4j Desktop UI

1. **In Neo4j Desktop**, click on your **"SMART_GRAPH"** instance
2. Look for **"Settings"** or **"Configuration"** tab/button
3. Find **"Network"** or **"Connection"** settings
4. Look for **"Bolt"** or **"Bolt Protocol"** setting
5. **Enable** Bolt on port **7687**
6. **Save** and restart the instance if needed

### Method 2: Edit Configuration File

1. **Stop** the Neo4j instance in Neo4j Desktop
2. **Navigate** to the instance path:
   - Path shown in Neo4j Desktop: `C:\Users\admin\...`
   - Open that folder in File Explorer
3. **Edit** the configuration file (usually `conf/neo4j.conf` or `conf/neo4j-server.properties`)
4. **Find** and **uncomment/modify** these lines:
   ```properties
   # Bolt connector
   dbms.connector.bolt.enabled=true
   dbms.connector.bolt.listen_address=0.0.0.0:7687
   ```
5. **Save** the file
6. **Start** the instance again in Neo4j Desktop

### Method 3: Check Neo4j Desktop Version

Some Neo4j Desktop versions have Bolt disabled by default.

1. **Check your version**: You're on 2.1.1 (shown in screenshot)
2. **Update** to latest version if possible
3. **Or** manually enable Bolt in settings

## Verify Bolt is Enabled

After enabling, test:

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/02_eligibility_scoring_360_profile
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/check_neo4j_ports.py
```

You should see:
```
✅ Port 7687 is OPEN and accepting connections
   → This is the Bolt protocol port
```

Then test connection:
```bash
python scripts/test_neo4j_direct.py
```

## Alternative: Use HTTP API (Not Recommended)

If Bolt can't be enabled, we can use HTTP API, but it's:
- ⚠️ Much slower
- ⚠️ More complex
- ⚠️ Not recommended for production

**Prefer fixing Bolt configuration instead.**

## Quick Check in Neo4j Desktop

1. Click on **"SMART_GRAPH"** instance
2. Look for **"Details"** or **"Info"** panel
3. Check if it shows:
   - `bolt://127.0.0.1:7687` (good!)
   - Or only `neo4j://127.0.0.1:7687` (Bolt might be disabled)

The connection URI in your screenshot shows `neo4j://127.0.0.1:7687`, which suggests the instance might be configured for the newer routing protocol but not the direct Bolt protocol.

---

**Most Likely Solution**: Enable Bolt protocol in Neo4j Desktop settings for your instance.

