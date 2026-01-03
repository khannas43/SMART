# Populate Hindi Names for Existing Schemes

## Overview
This guide explains how to populate Hindi names (`name_hindi`) and descriptions (`description_hindi`) for existing schemes in the database.

## Automatic Transliteration

The system automatically transliterates English text to Hindi when:
1. **Creating new schemes** - Hindi names are auto-populated
2. **Updating schemes** - Hindi names are updated if the English name changes, or populated if missing
3. **Scheduled task** - Runs daily at 3 AM to populate missing Hindi names

## Manual Population Methods

### Method 1: API Endpoint (Recommended)

Call the API endpoint to populate Hindi names for all existing schemes:

```bash
POST http://localhost:8080/api/v1/schemes/populate-hindi-names
```

**Using PowerShell:**
```powershell
cd C:\Projects\SMART\portals\citizen\backend\services\citizen-service\scripts
.\populate_scheme_hindi_names_api.ps1
```

**Using curl:**
```bash
curl -X POST http://localhost:8080/api/v1/schemes/populate-hindi-names
```

**Response:**
```json
{
  "success": true,
  "message": "Hindi names populated for 15 schemes",
  "data": 15
}
```

### Method 2: Update Individual Schemes

Update any scheme via the API, and Hindi names will be auto-populated if missing:

```bash
PUT http://localhost:8080/api/v1/schemes/{schemeId}
{
  "code": "SCHEME_CODE",
  "name": "Scheme Name",
  "description": "Scheme Description",
  ...
}
```

The `updateScheme` method will automatically populate `name_hindi` and `description_hindi` if they're missing.

### Method 3: Scheduled Task

The `SchemeTransliterationScheduler` runs daily at 10 AM and automatically populates Hindi names for all schemes that don't have them.

## Verification

Check which schemes are missing Hindi names:

```sql
SELECT id, code, name, name_hindi, description, description_hindi
FROM schemes
WHERE name_hindi IS NULL OR name_hindi = ''
ORDER BY name;
```

## Notes

- The transliteration service uses ICU4J library for automatic English-to-Hindi transliteration
- Transliteration works best for common words and names
- For complex technical terms, manual translation may be needed
- The scheduled task runs automatically, so missing Hindi names will be populated over time

