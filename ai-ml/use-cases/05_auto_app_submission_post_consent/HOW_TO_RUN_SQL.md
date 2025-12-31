# How to Run SQL Commands

**Note**: SQL commands need to be run in a PostgreSQL client, not directly in bash shell.

---

## Option 1: Using psql Command Line

```bash
# Connect to database
PGPASSWORD='anjali143' psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse

# Then run SQL commands
UPDATE application.department_connectors
SET endpoint_url = 'https://actual-dept-api.gov.in/...',
    auth_config = '{"api_key": "actual_key"}'::jsonb
WHERE connector_name = 'DEFAULT_REST';

# Exit psql
\q
```

---

## Option 2: Run SQL from File

```bash
# Create a SQL file
cat > update_connector.sql << 'EOF'
UPDATE application.department_connectors
SET endpoint_url = 'https://actual-dept-api.gov.in/...',
    auth_config = '{"api_key": "actual_key"}'::jsonb
WHERE connector_name = 'DEFAULT_REST';
EOF

# Run the SQL file
PGPASSWORD='anjali143' psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f update_connector.sql
```

---

## Option 3: Using Python Script

Create a Python script to run SQL:

```python
import sys
from pathlib import Path
import yaml

sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector

config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

db_config = config['database']
db = DBConnector(
    host=db_config['host'],
    port=db_config['port'],
    database=db_config['name'],
    user=db_config['user'],
    password=db_config['password']
)

db.connect()
cursor = db.connection.cursor()
cursor.execute("""
    UPDATE application.department_connectors
    SET endpoint_url = %s,
        auth_config = %s::jsonb
    WHERE connector_name = %s
""", [
    'https://actual-dept-api.gov.in/...',
    '{"api_key": "actual_key"}',
    'DEFAULT_REST'
])
db.connection.commit()
cursor.close()
db.disconnect()
```

---

## Common SQL Commands for Configuration

### View Current Connectors
```sql
SELECT connector_name, connector_type, endpoint_url, is_active
FROM application.department_connectors;
```

### Update Connector (When API Info Available)
```sql
UPDATE application.department_connectors
SET 
    endpoint_url = 'https://dept-api.rajasthan.gov.in/applications',
    auth_config = '{"api_key": "YOUR_KEY"}'::jsonb
WHERE connector_name = 'DEFAULT_REST';
```

### View Field Mappings
```sql
SELECT scheme_code, target_field_name, mapping_type, source_type
FROM application.scheme_field_mappings
WHERE scheme_code = 'CHIRANJEEVI'
ORDER BY priority;
```

### View Form Schemas
```sql
SELECT scheme_code, jsonb_array_length(fields) as field_count
FROM application.scheme_form_schemas
WHERE is_active = true;
```

---

**Note**: SQL examples in documentation are for reference. They need to be run in a PostgreSQL client when you have the actual API information.

