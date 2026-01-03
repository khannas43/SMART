# Hindi Localization Guide

This guide explains how to add Hindi (Devanagari script) support to entities and content throughout the Citizen Portal.

## Overview

The portal supports bilingual content (English and Hindi) for:
- **User Names** (`citizens.full_name_hindi`)
- **Scheme Names & Descriptions** (`schemes.name_hindi`, `schemes.description_hindi`)
- **Future entities** (applications, documents, etc.)

## Architecture Pattern

### 1. Database Layer

Add Hindi fields to the relevant table:

```sql
ALTER TABLE <table_name> 
ADD COLUMN <field_name>_hindi <data_type>;
```

**Example:**
```sql
-- For schemes
ALTER TABLE schemes 
ADD COLUMN name_hindi VARCHAR(255),
ADD COLUMN description_hindi TEXT;
```

### 2. Backend Layer

#### Entity (`*.java`)
Add the Hindi field to the entity class:

```java
@Column(name = "name_hindi", length = 255)
private String nameHindi;

@Column(name = "description_hindi", columnDefinition = "TEXT")
private String descriptionHindi;
```

#### DTO (`*Response.java`)
Add the Hindi field to the response DTO:

```java
private String nameHindi;
private String descriptionHindi;
```

**Note:** MapStruct will automatically map fields with matching names (e.g., `nameHindi` → `nameHindi`).

### 3. Frontend Layer

#### TypeScript Interface (`types/api.ts`)
Add Hindi fields to the interface:

```typescript
export interface EntityName {
  name: string;
  nameHindi?: string;
  description?: string;
  descriptionHindi?: string;
}
```

#### Localization Utility (`utils/localization.ts`)
Add helper functions if needed:

```typescript
export function getEntityName(
  entity: { name: string; nameHindi?: string },
  currentLanguage: string
): string {
  return getLocalizedName(entity.name, entity.nameHindi, currentLanguage);
}
```

#### Component Usage
Use the utility function in React components:

```typescript
import { getEntityName } from '@/utils/localization';
import { useTranslation } from 'react-i18next';

const MyComponent: React.FC = () => {
  const { i18n } = useTranslation();
  
  return (
    <Typography>
      {getEntityName(entity, i18n.language)}
    </Typography>
  );
};
```

## Current Implementation

### ✅ Completed

1. **Citizens (User Names)**
   - Database: `citizens.full_name_hindi`
   - Entity: `Citizen.fullNameHindi`
   - DTO: `CitizenResponse.fullNameHindi`
   - Frontend: `User.fullNameHindi`
   - Utility: `getUserName()`
   - Usage: Dashboard welcome message

2. **Schemes**
   - Database: `schemes.name_hindi`, `schemes.description_hindi`
   - Entity: `Scheme.nameHindi`, `Scheme.descriptionHindi`
   - DTO: `SchemeResponse.nameHindi`, `SchemeResponse.descriptionHindi`
   - Frontend: `Scheme.nameHindi`, `Scheme.descriptionHindi`
   - Utility: `getSchemeName()`, `getSchemeDescription()`
   - Usage: Schemes browse page, scheme details, eligibility checker, applications

### 🔄 To Be Implemented

1. **Service Applications**
   - Add `subject_hindi`, `description_hindi` fields
   - Update entity, DTO, and frontend

2. **Documents**
   - Add `document_name_hindi`, `description_hindi` fields

3. **Notifications**
   - Add `title_hindi`, `message_hindi` fields

4. **Categories & Departments**
   - Add `name_hindi` fields to master data tables

## Data Population

### Scripts Available

1. **`scripts/populate_hindi_names.sql`** - For populating citizen Hindi names
2. **`scripts/populate_hindi_schemes.sql`** - For populating scheme Hindi names/descriptions

### Manual Update Example

```sql
-- Update citizen name
UPDATE citizens 
SET full_name_hindi = 'रानी ठाकुर'
WHERE aadhaar_number = '123456789012';

-- Update scheme
UPDATE schemes 
SET 
    name_hindi = 'राजस्थान सरकार योजना',
    description_hindi = 'यह योजना नागरिकों के लिए है...'
WHERE code = 'SCHEME_CODE_001';
```

## Best Practices

1. **Always provide fallback**: If Hindi content is not available, display English content
2. **Use utility functions**: Don't manually check language in components - use `getLocalizedName()`, etc.
3. **Consistent naming**: Use `*Hindi` suffix for all Hindi fields (e.g., `nameHindi`, `descriptionHindi`)
4. **Database constraints**: Hindi fields should be nullable (optional) to allow gradual migration
5. **Migration strategy**: Populate Hindi content incrementally, starting with most-used entities

## Testing

1. Switch language to Hindi (`hi`)
2. Verify that Hindi content appears when available
3. Verify that English content appears as fallback when Hindi is not available
4. Test with mixed data (some records with Hindi, some without)

## Future Enhancements

- **Transliteration API**: Automatically transliterate English names to Hindi
- **Bulk import**: CSV/Excel import for Hindi translations
- **Admin interface**: UI for managing Hindi translations
- **Translation management**: Integration with translation management systems

