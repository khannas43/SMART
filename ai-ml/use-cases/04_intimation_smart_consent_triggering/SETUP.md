# Setup Guide: Auto Intimation & Smart Consent Triggering

**Use Case ID:** AI-PLATFORM-04

## Prerequisites

1. **Python 3.12+** (WSL venv at `/mnt/c/Projects/SMART/ai-ml/.venv`)
2. **PostgreSQL 14+** (`smart_warehouse` database)
3. **Dependencies** installed

## Quick Setup

### 1. Activate Virtual Environment

```bash
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
```

### 2. Install Dependencies

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/04_intimation_smart_consent_triggering
pip install -r requirements.txt
```

### 3. Setup Database Schema

**📖 For detailed database setup instructions, see [DATABASE_SETUP.md](DATABASE_SETUP.md)**

```bash
# Option 1: Using script (WSL/Ubuntu)
./scripts/setup_database.sh

# Option 2: Manual (PgAdmin or psql)
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f database/intimation_schema.sql

# Option 3: Manual (PgAdmin GUI)
# Open PgAdmin → Connect to smart_warehouse → Execute SQL from database/intimation_schema.sql
```

### 4. Validate Configuration

```bash
python scripts/check_config.py
```

### 5. Initialize Message Templates

```bash
python scripts/init_message_templates.py
```

### 6. Test Intake Process

```bash
python scripts/test_intake.py
```

### 7. Test Consent Management

```bash
python scripts/test_consent.py
```

## Configuration

### Database Configuration

Edit `config/db_config.yaml`:
- Database connection details
- External database connections (eligibility, golden_records, etc.)

### Use Case Configuration

Edit `config/use_case_config.yaml`:
- Campaign policies
- Channel settings
- Fatigue limits
- Retry schedules
- Consent rules

### Channel Provider Configuration

Set environment variables for channel providers:

```bash
# Twilio (SMS/WhatsApp/IVR)
export TWILIO_ACCOUNT_SID="your_account_sid"
export TWILIO_AUTH_TOKEN="your_auth_token"
export TWILIO_FROM_NUMBER="+1234567890"
export TWILIO_WHATSAPP_FROM="whatsapp:+1234567890"

# Email (SMTP)
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="your_email@gmail.com"
export SMTP_PASSWORD="your_password"
export SMTP_FROM_EMAIL="noreply@smart.rajasthan.gov.in"

# Firebase (App Push)
export FIREBASE_CREDENTIALS_PATH="/path/to/firebase-credentials.json"
```

## Database Schema

The schema creates the following tables in `smart_warehouse.intimation`:

- `campaigns` - Intimation campaigns
- `campaign_candidates` - Individual candidates
- `message_logs` - Message delivery logs
- `consent_records` - Consent records
- `consent_history` - Consent audit trail
- `user_preferences` - Communication preferences
- `message_fatigue` - Fatigue tracking
- `scheme_intimation_config` - Per-scheme configuration
- `message_templates` - Message templates
- `intimation_events` - Event log

## Testing

**📖 For comprehensive testing instructions, see [TESTING_GUIDE.md](TESTING_GUIDE.md)**

Quick test commands:
```bash
# Validate configuration
python scripts/check_config.py

# Test intake process
python scripts/test_intake.py

# Test consent management
python scripts/test_consent.py

# Test message personalization
python scripts/test_message_personalization.py

# End-to-end test
python scripts/test_end_to_end.py --scheme-code CHIRANJEEVI --limit 10
```

## Next Steps

1. **Configure Channel Providers**: Set up Twilio, SMTP, Firebase credentials
2. **Create Message Templates**: Templates initialized automatically (customize as needed)
3. **Configure Scheme Settings**: Run `python scripts/init_scheme_config.py` to initialize
4. **Test End-to-End**: Follow [TESTING_GUIDE.md](TESTING_GUIDE.md)
5. **Deploy Scheduled Jobs**: Set up cron jobs for intake and retry processing

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running
- Check connection credentials in `config/db_config.yaml`
- Ensure user has permissions on `smart_warehouse` database

### Schema Creation Issues

- Run as `postgres` superuser or ensure user has CREATE SCHEMA permission
- Check for existing schema conflicts

### Channel Provider Issues

- Verify environment variables are set
- Check provider API credentials
- Review provider-specific logs

## Support

See [README.md](README.md) for more information and [docs/TECHNICAL_DESIGN.md](docs/TECHNICAL_DESIGN.md) for detailed architecture.

