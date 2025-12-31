# Fixes Applied - Testing Issues

## Issues Fixed

### 1. Missing `consent_purpose` Field ✅
**Problem**: Database schema requires `consent_purpose` but it wasn't being provided when creating consent records.

**Fix Applied**:
- Added `consent_purpose` parameter to `ConsentManager.create_consent()` method with default value `'enrollment'`
- Updated INSERT statement to include `consent_purpose` field
- Valid values: `enrollment`, `data_sharing`, `notification`

**File**: `src/consent_manager.py`

### 2. SMS Message Too Long ✅
**Problem**: SMS messages exceeded 160 character limit (actual: 276 chars).

**Fix Applied**:
- Added truncation logic in `MessagePersonalizer.render_message()` method
- SMS messages longer than 160 characters are truncated to 157 chars + "..."
- Only applies to SMS channel (other channels have no length limits)

**File**: `src/message_personalizer.py`

## Testing

Run the tests again:

```bash
# Test message personalization (SMS truncation)
python scripts/test_message_personalization.py

# Test consent management (consent_purpose)
python scripts/test_consent.py

# End-to-end test
python scripts/test_end_to_end.py --scheme-code CHIRANJEEVI --limit 10
```

## Notes

- SMS truncation is basic (hard cut at 160 chars). Future enhancement: truncate at word boundaries.
- `consent_purpose` defaults to `'enrollment'` which is appropriate for intimation scenarios.
- For other consent purposes (data_sharing, notification), pass the parameter explicitly.

