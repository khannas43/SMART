# Starting the Nudge Management Viewer

The AI-PLATFORM-11 viewer is integrated into the unified web viewer.

## Quick Start

**Option 1: If server is already running, restart it:**

```bash
# Stop existing server
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
pkill -f view_rules_web.py

# Wait a moment
sleep 2

# Start server again
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/view_rules_web.py
```

**Option 2: Start server in background:**

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
nohup python scripts/view_rules_web.py > viewer.log 2>&1 &
```

**Option 3: Start server in foreground:**

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/view_rules_web.py
```

## Access URLs

Once the server is running, access the nudge management dashboard at:

**http://localhost:5001/ai11**

Other available endpoints:
- Eligibility Rules: http://localhost:5001/
- Campaign Results: http://localhost:5001/ai04
- Application Submission: http://localhost:5001/ai05
- Decision Evaluation: http://localhost:5001/ai06
- Beneficiary Detection: http://localhost:5001/ai07
- Eligibility Checker: http://localhost:5001/ai08
- Proactive Inclusion: http://localhost:5001/ai09
- Benefit Forecast: http://localhost:5001/ai10
- **Nudge Management: http://localhost:5001/ai11** ⭐

## Verify Server is Running

```bash
# Check if process is running
pgrep -f view_rules_web.py

# Check if port 5001 is listening
netstat -tuln | grep 5001 || ss -tuln | grep 5001
```

## Troubleshooting

### 404 Error on /ai11

If you get a 404 error, the server likely needs to be restarted:

1. Stop the server: `pkill -f view_rules_web.py`
2. Wait 2 seconds
3. Start it again using one of the methods above

### Port Already in Use

If port 5001 is already in use:

```bash
# Find process using port 5001
lsof -i :5001 || netstat -tulnp | grep 5001

# Kill the process (replace PID with actual process ID)
kill -9 <PID>
```

### Database Connection Error

If you see database connection errors, verify:
1. PostgreSQL is running
2. Database config is correct: `config/db_config.yaml`
3. Host IP is correct (172.17.16.1 for WSL to Windows)

---

**Last Updated**: 2024-12-30

