# i18n Import Path Fix

## Issue
The i18n config file was using incorrect relative paths to import translation JSON files.

## File Structure
```
portals/citizen/
├── i18n/
│   └── locales/
│       ├── en/
│       │   ├── common.json
│       │   └── auth.json
│       └── hi/
│           ├── common.json
│           └── auth.json
└── frontend/
    └── src/
        └── i18n/
            └── config.ts  ← This file imports from above
```

## Path Calculation
From: `frontend/src/i18n/config.ts`
To: `citizen/i18n/locales/en/common.json`

Relative path:
- `.` = `frontend/src/i18n/`
- `..` = `frontend/src/`
- `../..` = `frontend/`
- `../../..` = `citizen/`
- `../../../../i18n/locales/en/common.json` = ✅ Correct path

## Fix Applied
Changed all import paths from:
```typescript
import enCommon from '../../i18n/locales/en/common.json';
```

To:
```typescript
import enCommon from '../../../../i18n/locales/en/common.json';
```

## Files Updated
- `frontend/src/i18n/config.ts`

This fix ensures Vite can correctly resolve the JSON import paths during development and build.

