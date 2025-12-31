# Neo4j Quick Start - Step by Step

## ✅ Configuration Updated

Your Neo4j configuration has been updated:
- **Password**: `anjali143`
- **Database**: `smartgraohdb` (or you can use `neo4j` for default)
- **URI**: `bolt://localhost:7687`

## 🚀 Next Steps

### Step 1: Start Neo4j Desktop & Database

1. **Open Neo4j Desktop** (the application)
2. **Start your database**:
   - Find `smartgraohdb` in your list of databases
   - Click the **"Start"** button (play icon) next to it
   - Wait until status shows **"Active"** (green indicator)
   - **Note the port number** - it should be `7687` (default Bolt port)

**Alternative**: If you want to use the `neo4j` database instead:
- Start the `neo4j` database instead
- Update config: change `database: smartgraohdb` to `database: neo4j`

### Step 2: Verify Connection

Once the database is started, run:

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/02_eligibility_scoring_360_profile
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/check_neo4j.py
```

**Expected output:**
```
✅ Connected successfully!
   Nodes: 0 (or existing count)
   Relationships: 0 (or existing count)
```

### Step 3: Run Graph Clustering

Once connection is verified, run the graph clustering:

```bash
cd src
python graph_clustering_neo4j.py
```

This will:
1. Load relationships from PostgreSQL
2. Create graph in Neo4j
3. Detect communities (clusters)
4. Calculate centrality measures
5. Save results to PostgreSQL

## 🔍 Troubleshooting

### "Connection refused" Error

**Problem**: Neo4j database is not running

**Solution**:
1. Open Neo4j Desktop
2. Make sure your database shows "Active" status
3. If not, click "Start" button
4. Wait 10-15 seconds for it to fully start

### "Authentication failed" Error

**Problem**: Wrong password

**Solution**:
- Check password in `config/db_config.yaml` matches your Neo4j password
- Default is `anjali143` (already set)

### "Database not found" Error

**Problem**: Database name doesn't match

**Solutions**:
1. Check exact database name in Neo4j Desktop
2. Update `database: smartgraohdb` in `config/db_config.yaml` to match exactly
3. Or use `database: neo4j` for the default database

### Port Issues

**Problem**: Neo4j might be running on a different port

**Check port in Neo4j Desktop**:
1. Click on your database
2. Look at connection details (usually shows `bolt://localhost:XXXX`)
3. If different from 7687, update `uri` in config:
   ```yaml
   uri: bolt://localhost:XXXX  # Replace XXXX with actual port
   ```

## 📊 Optional: Install GDS Plugin (Recommended)

For better performance, install Graph Data Science plugin:

1. In Neo4j Desktop, click on `smartgraohdb` database
2. Click **"Plugins"** tab
3. Find **"Graph Data Science"**
4. Click **"Install"**
5. **Restart** the database after installation

**Benefits**:
- Faster community detection
- Better PageRank algorithm
- Advanced graph algorithms

**Without GDS**: Script will still work but use fallback methods (slower)

## ✅ Success Checklist

- [ ] Neo4j Desktop is installed
- [ ] Database (`smartgraohdb` or `neo4j`) is started and shows "Active"
- [ ] `check_neo4j.py` runs successfully
- [ ] Ready to run `graph_clustering_neo4j.py`

## 🎯 After Setup

Once everything is working, you can:

1. **View graph in Neo4j Browser**:
   - Click "Open" button next to your database
   - Run queries like: `MATCH (n) RETURN n LIMIT 25`

2. **Monitor clustering progress**:
   - Watch console output during `graph_clustering_neo4j.py`
   - Should complete in minutes (not hours like NetworkX)

3. **Query clusters in PostgreSQL**:
   ```sql
   SELECT cluster_id, COUNT(*) 
   FROM profile_360 
   WHERE cluster_id IS NOT NULL 
   GROUP BY cluster_id 
   ORDER BY COUNT(*) DESC 
   LIMIT 10;
   ```

---

**Ready?** Start your Neo4j database and run `check_neo4j.py`!

