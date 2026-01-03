# Automatic English-to-Hindi Transliteration

## Overview

The system now automatically transliterates English text to Hindi (Devanagari script) for:
- **Citizen Names** (`full_name` → `full_name_hindi`)
- **Scheme Names** (`name` → `name_hindi`)
- **Scheme Descriptions** (`description` → `description_hindi`)

This happens automatically when records are **created** or **updated** through the API.

## How It Works

### 1. Automatic Transliteration on Create/Update

When you create or update a citizen or scheme:
- The `TransliterationService` automatically converts English text to Hindi
- The Hindi version is stored in the `*_hindi` fields
- Both English and Hindi versions are stored in the database

### 2. Transliteration Service

The `TransliterationServiceImpl` uses a mapping-based approach:
- **Common name patterns**: Ram → राम, Kumar → कुमार, Thakur → ठाकुर, etc.
- **Common words**: Government → सरकार, Scheme → योजना, Rajasthan → राजस्थान, etc.
- **Fallback**: Character-by-character transliteration for unmatched text

### 3. Migration for Existing Records

Migration `V16__transliterate_existing_records.sql` transliterates existing records:
- Updates all citizens with common name patterns
- Updates all schemes with common word patterns
- Runs automatically when backend starts (via Flyway)

## Testing

### Test Automatic Transliteration

1. **Create a new citizen** via API:
```bash
POST /citizens
{
  "fullName": "Rani Thakur",
  "mobileNumber": "9876543210",
  ...
}
```

The `full_name_hindi` field will automatically be set to "रानी ठाकुर"

2. **Update a citizen**:
```bash
PUT /citizens/{id}
{
  "fullName": "Priya Sharma",
  ...
}
```

The `full_name_hindi` will be updated to "प्रिया शर्मा"

3. **Create a new scheme**:
```bash
POST /schemes
{
  "name": "Rajasthan Government Scheme",
  "description": "This scheme is for citizens",
  ...
}
```

Both `name_hindi` and `description_hindi` will be automatically transliterated.

### Verify Transliteration

Check the database:
```sql
-- Check citizens
SELECT full_name, full_name_hindi FROM citizens LIMIT 10;

-- Check schemes
SELECT name, name_hindi, description, description_hindi FROM schemes LIMIT 10;
```

### Test in Frontend

1. Switch language to Hindi (हिंदी)
2. View dashboard - names should show in Hindi
3. View schemes - names and descriptions should show in Hindi

## Current Limitations

1. **Basic Transliteration**: The current implementation uses pattern matching. For production, consider:
   - ICU4J library for more accurate transliteration
   - Google Translate API (for better accuracy but requires internet)
   - Custom transliteration engine

2. **Not All Words**: Only common patterns are transliterated. Unmatched text may remain in English or use basic character mapping.

3. **Manual Override**: You can still manually set Hindi fields if automatic transliteration is not accurate enough.

## Future Enhancements

1. **ICU4J Integration**: Use ICU4J library for more accurate transliteration
2. **Machine Learning**: Train a model for better transliteration accuracy
3. **Admin Interface**: Allow admins to review and correct transliterations
4. **Batch Processing**: Background job to re-transliterate all records periodically

## Files Modified

- `TransliterationService.java` - Service interface
- `TransliterationServiceImpl.java` - Service implementation
- `CitizenServiceImpl.java` - Auto-transliterate on create/update
- `SchemeServiceImpl.java` - Auto-transliterate on create/update
- `V16__transliterate_existing_records.sql` - Migration for existing records

## Notes

- Transliteration happens **automatically** - no manual intervention needed
- Both English and Hindi versions are stored
- Frontend automatically shows Hindi when language is set to Hindi
- If Hindi field is empty, frontend falls back to English (graceful degradation)

