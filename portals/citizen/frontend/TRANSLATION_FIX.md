# Dashboard Translation Fix

## Issue
Dashboard page showing mixed languages - some text in English, some in Hindi.

## Solution Applied

1. ✅ Created `dashboard.json` translation files for English and Hindi
2. ✅ Added dashboard namespace to i18n config
3. ✅ Updated `useTranslation` hook to include dashboard namespace

## To Fix the Issue

### Option 1: Hard Refresh Browser (Recommended)
1. Press `Ctrl + Shift + R` (Windows/Linux) or `Cmd + Shift + R` (Mac)
2. This will clear the browser cache and reload the page

### Option 2: Clear Browser Cache
1. Open browser DevTools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

### Option 3: Restart Frontend Dev Server
1. Stop the frontend (Ctrl+C in the terminal)
2. Clear Vite cache:
   ```bash
   cd portals/citizen/frontend
   rm -rf node_modules/.vite
   ```
3. Restart:
   ```bash
   npm run dev
   ```

### Option 4: Clear localStorage
1. Open browser console (F12)
2. Run:
   ```javascript
   localStorage.clear();
   location.reload();
   ```

## Verification

After applying the fix, check:
- "Here's an overview of your account" → Should show in selected language
- "Recent Applications" → Should show in selected language
- "Recent Notifications" → Should show in selected language
- "No applications yet" → Should show in selected language
- "No notifications" → Should show in selected language
- "Browse Schemes" → Should show in selected language
- "View All" → Should show in selected language

## Current Language Detection

The app detects language from:
1. URL query parameter (`?lng=hi`)
2. Cookie (`i18next`)
3. localStorage (`i18nextLng`)
4. Browser language
5. HTML lang attribute

To force a language, add `?lng=hi` or `?lng=en` to the URL.

