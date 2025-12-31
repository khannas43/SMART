# View Eligibility Rules in Browser

This guide shows you how to view all eligibility rules in a web browser using a simple Flask web application.

## Quick Start

### 1. Install Flask (if not already installed)

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
pip install flask>=3.0.0
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### 2. Start the Web Server

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/view_rules_web.py
```

### 3. Open in Browser

Once the server starts, you'll see:
```
🌐 Starting web server...
📋 Open your browser and navigate to:
   http://localhost:5001
```

Open your browser and go to: **http://localhost:5001**

## Features

The web interface displays:

- **Statistics Dashboard**: Total schemes, total rules, and active rules
- **Scheme-wise Organization**: All schemes with auto-identification enabled
- **Detailed Rule Information**: 
  - Rule ID
  - Rule Name
  - Rule Type (MANDATORY, OPTIONAL, etc.)
  - Rule Expression (the actual rule logic)
  - Mandatory Status
  - Priority
  - Effective Dates

## Interface Details

- **Expandable Sections**: Click on any scheme header to expand/collapse rules
- **Color-coded**: Rules are color-coded by type and mandatory status
- **Responsive Design**: Works on desktop and mobile browsers
- **Refresh Button**: Click the refresh button to reload rules from database

## Stopping the Server

Press `Ctrl+C` in the terminal to stop the web server.

## Troubleshooting

### Port 5001 Already in Use

If port 5001 is already in use, you can modify the port in `scripts/view_rules_web.py`:

```python
app.run(host='0.0.0.0', port=5002, debug=False)  # Change port number
```

### Database Connection Error

Make sure:
1. PostgreSQL is running
2. Database credentials in `config/db_config.yaml` are correct
3. Database `smart_warehouse` exists and has the `eligibility` schema

### No Rules Displayed

If no rules are displayed:
1. Check if rules are loaded: `python scripts/load_sample_rules.py`
2. Verify schemes have `is_auto_id_enabled = true` in `public.scheme_master`
3. Check rule effective dates (rules must be currently effective)

## Alternative: View Rules via API

If you prefer using the REST API instead:

### Using curl:
```bash
# Get rules for a specific scheme
curl "http://localhost:8080/api/v1/admin/rules/scheme/CHIRANJEEVI"
```

### Using Python:
```python
import requests
response = requests.get("http://localhost:8080/api/v1/admin/rules/scheme/CHIRANJEEVI")
rules = response.json()
print(rules)
```

## Notes

- The web interface reads directly from the database
- Changes made via the API or Python scripts will be reflected immediately after refresh
- The interface is read-only (viewing only)
- For editing rules, use the Rule Management API endpoints (documented in TECHNICAL_DESIGN.md)

