# Citizen Portal - Internationalization (i18n)

This directory contains translation files for the Citizen Portal.

## Supported Languages

- **English (en)** - Default language
- **Hindi (hi)** - Primary regional language
- **Rajasthani (rj)** - Optional (future enhancement)

## File Structure

```
i18n/locales/
├── en/                      # English translations
│   ├── common.json         # Common terms, buttons, labels, errors
│   ├── auth.json           # Authentication screens
│   ├── profile.json        # Profile screens
│   ├── schemes.json        # Scheme discovery screens
│   ├── applications.json   # Application screens
│   ├── documents.json      # Document screens
│   ├── benefits.json       # Benefits screens
│   ├── services.json       # Service delivery screens
│   ├── settings.json       # Settings screens
│   └── help.json           # Help & support screens
│
├── hi/                      # Hindi translations
│   └── [same structure]
│
└── rj/                      # Rajasthani (future)
    └── [same structure]
```

## Translation File Template

Each translation file follows this structure:

```json
{
  "key": "Translation text",
  "nested": {
    "key": "Nested translation"
  },
  "withVariable": "Text with {{variable}}"
}
```

## Usage in React Components

```typescript
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t, i18n } = useTranslation();
  
  return (
    <div>
      <h1>{t('common.appName')}</h1>
      <button>{t('buttons.login')}</button>
      <p>{t('messages.successSaved')}</p>
      <p>{t('validation.required', { field: 'Email' })}</p>
      
      {/* Language switcher */}
      <select onChange={(e) => i18n.changeLanguage(e.target.value)}>
        <option value="en">English</option>
        <option value="hi">हिंदी</option>
      </select>
    </div>
  );
}
```

## Date and Number Formatting

### Date Formatting (Indian Locale)

```typescript
import { format } from 'date-fns';
import { hi } from 'date-fns/locale';

// English: 30/12/2024
format(new Date(), 'dd/MM/yyyy');

// Hindi: 30/12/2024 (same format, different locale for day names)
format(new Date(), 'dd/MM/yyyy', { locale: hi });
```

### Number Formatting (Indian Numbering System)

```typescript
// Use Intl.NumberFormat for Indian locale
const formatter = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2
});

// Output: ₹1,23,456.78 (Indian format)
formatter.format(123456.78);
```

## Hindi Font Support

The frontend must include Hindi fonts. Recommended:

1. **Noto Sans Devanagari** (Google Fonts) - Recommended
2. **Mangal** (Windows system font) - Fallback
3. **Arial Unicode MS** - Fallback

Add to `frontend/src/styles/fonts.css`:

```css
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap');

body {
  font-family: 'Noto Sans Devanagari', 'Mangal', 'Arial Unicode MS', sans-serif;
}

.hindi {
  font-family: 'Noto Sans Devanagari', sans-serif;
}
```

## Translation Guidelines

1. **Keep keys consistent** across all language files
2. **Use descriptive keys** that indicate context (e.g., `auth.login` not just `login`)
3. **Handle pluralization** when needed
4. **Include variables** for dynamic content using `{{variable}}` syntax
5. **Test text length** - Hindi text may be longer/shorter than English
6. **Maintain context** - Keep related translations together
7. **Review with native speakers** - Ensure translations are accurate and culturally appropriate

## Adding New Translations

1. Add the key-value pair to English file first (`en/`)
2. Add the Hindi translation to Hindi file (`hi/`)
3. Use the translation in the component with `t('key')`
4. Test both languages in the UI

## Backend i18n Support

- APIs should accept `Accept-Language` header
- Error messages should be translated
- Email/SMS templates need separate versions for each language
- PDF/document generation needs Hindi font support

## Status

- ✅ Structure created
- ✅ Common translations (en, hi) - Template
- ✅ Auth translations (en, hi) - Template
- ⏳ Remaining module translations (profile, schemes, applications, etc.) - To be completed

