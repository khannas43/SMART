# Footer Implementation Guide - SMART Citizen Portal

**Created:** 2024-12-30  
**Purpose:** Guide for implementing footer with Terms & Conditions, Sitemap, and Website Policy links  
**Status:** Ready for Implementation

---

## Overview

The footer component appears on every page of the Citizen Portal and includes three essential links:

1. **Terms and Conditions** - Link to internal page with content from Rajasthan.gov.in
2. **Sitemap** - Link to internal sitemap page
3. **Website Policy** - External link to Rajasthan.gov.in (opens in new tab)

---

## Footer Links

### 1. Terms and Conditions

**Route:** `/citizen/terms-conditions`  
**Content Source:** https://rajasthan.gov.in/jankalyan-category-and-entry-type/0/51/88  
**Status:** Page structure created, content needs to be copied from source

**Implementation Steps:**
1. Visit https://rajasthan.gov.in/jankalyan-category-and-entry-type/0/51/88
2. Copy the Terms and Conditions content
3. Add content to translation files (`i18n/locales/en/termsConditions.json` and `hi/termsConditions.json`)
4. Format content appropriately with sections and subsections
5. Update `TermsAndConditions.tsx` component to display the content

### 2. Sitemap

**Route:** `/citizen/sitemap`  
**Status:** Page structure created, fully functional

**Features:**
- Displays all portal sections and pages
- Collapsible sections for better organization
- Direct links to all pages
- Descriptions for each page
- Responsive design
- Multi-language support (English/Hindi)

**Implementation:** Ready to use - just ensure all routes are registered in App.tsx

### 3. Website Policy

**External URL:** https://rajasthan.gov.in/pages/website-policies  
**Behavior:** Opens in new tab (`target="_blank"`)  
**Status:** Link configured in Footer component

**Implementation:** Already configured - no changes needed

---

## Files Created

### 1. Footer Component
- `frontend/src/components/layout/Footer.tsx.template`
- `frontend/src/components/layout/Footer.css`

### 2. Terms and Conditions Page
- `frontend/src/pages/TermsAndConditions.tsx.template`
- `frontend/src/pages/TermsAndConditions.css`

### 3. Sitemap Page
- `frontend/src/pages/Sitemap.tsx.template`
- `frontend/src/pages/Sitemap.css`

### 4. Updated Translation Files
- `i18n/locales/en/common.json` - Added footer translations
- `i18n/locales/hi/common.json` - Added Hindi footer translations

### 5. App Integration Template
- `frontend/src/App.tsx.template` - Shows how to integrate Header and Footer

---

## Implementation Checklist

### Step 1: Create Footer Component
- [ ] Copy `Footer.tsx.template` to `Footer.tsx` (remove `.template` extension)
- [ ] Copy `Footer.css` to component directory
- [ ] Verify translations are loaded

### Step 2: Create Terms and Conditions Page
- [ ] Copy `TermsAndConditions.tsx.template` to `TermsAndConditions.tsx`
- [ ] Copy `TermsAndConditions.css` to pages directory
- [ ] Visit https://rajasthan.gov.in/jankalyan-category-and-entry-type/0/51/88
- [ ] Copy content from the website
- [ ] Create translation files: `i18n/locales/en/termsConditions.json`
- [ ] Create translation files: `i18n/locales/hi/termsConditions.json`
- [ ] Add content to translation files with proper structure
- [ ] Update component to use translations
- [ ] Format content with proper sections and styling

### Step 3: Create Sitemap Page
- [ ] Copy `Sitemap.tsx.template` to `Sitemap.tsx`
- [ ] Copy `Sitemap.css` to pages directory
- [ ] Verify all routes match the sitemap structure
- [ ] Test collapsible sections functionality

### Step 4: Integrate Footer in App
- [ ] Update `App.tsx` to import Footer component
- [ ] Add Footer component after main content area
- [ ] Add routes for Terms and Conditions and Sitemap
- [ ] Test footer appears on all pages

### Step 5: Styling
- [ ] Verify footer styling matches design requirements
- [ ] Test responsive design (mobile, tablet, desktop)
- [ ] Test footer links functionality
- [ ] Verify external link opens in new tab

### Step 6: Testing
- [ ] Test Terms and Conditions page loads correctly
- [ ] Test Sitemap page loads correctly
- [ ] Test Website Policy link opens in new tab
- [ ] Test all footer links on different pages
- [ ] Test footer on mobile devices
- [ ] Test translations (English/Hindi)

---

## Footer Layout

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Terms and Conditions | Sitemap | Website Policy ↗         │
│                                                             │
│  © 2024 SMART Citizen Portal, Government of Rajasthan.     │
│  All rights reserved.                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Desktop:** Links displayed horizontally with separators (`|`)  
**Mobile:** Links displayed vertically (stacked), separators hidden

---

## Translation Keys

### English (`en/common.json`)
```json
{
  "footer": {
    "termsConditions": "Terms and Conditions",
    "sitemap": "Sitemap",
    "websitePolicy": "Website Policy",
    "copyright": "© {{year}} SMART Citizen Portal, Government of Rajasthan. All rights reserved."
  },
  "opensInNewTab": "(opens in new tab)"
}
```

### Hindi (`hi/common.json`)
```json
{
  "footer": {
    "termsConditions": "नियम और शर्तें",
    "sitemap": "साइटमैप",
    "websitePolicy": "वेबसाइट नीति",
    "copyright": "© {{year}} SMART नागरिक पोर्टल, राजस्थान सरकार। सभी अधिकार सुरक्षित।"
  },
  "opensInNewTab": "(नई टैब में खुलता है)"
}
```

---

## Terms and Conditions Content Structure

**Source URL:** https://rajasthan.gov.in/jankalyan-category-and-entry-type/0/51/88

**Recommended Structure:**
```json
{
  "termsConditions": {
    "title": "Terms and Conditions",
    "subtitle": "Terms of use for SMART Citizen Portal",
    "introduction": "...",
    "section1": {
      "title": "1. Acceptance of Terms",
      "content": "..."
    },
    "section2": {
      "title": "2. Use of Service",
      "content": "..."
    },
    // Add more sections as needed
    "lastUpdated": "Last Updated",
    "lastUpdatedDate": "December 30, 2024"
  }
}
```

**Note:** Content should be copied from the Rajasthan.gov.in website and formatted appropriately with proper headings, paragraphs, and lists.

---

## Sitemap Structure

The sitemap displays all portal sections:

1. Dashboard
2. My Profile
   - Profile Dashboard
   - Edit Profile
3. Schemes
   - Browse Schemes
   - Eligibility Checker
4. My Applications
   - Applications Hub
   - Consent & Clarifications
5. Documents
6. Benefits
   - Benefits & Entitlements
   - Payments & Ledger
7. Services
   - Service Catalog
   - Request Service
   - Service Status
8. Settings
   - Notifications
   - Opt-Out Schemes
   - Account & Security
9. Help & Support
   - Help Hub
   - My Tickets

---

## Accessibility Considerations

1. **Footer Links:**
   - Proper `aria-label` for external links
   - Keyboard navigation support
   - Focus indicators
   - Screen reader announcements

2. **Terms and Conditions:**
   - Proper heading hierarchy
   - Readable font sizes
   - Sufficient color contrast
   - Proper semantic HTML

3. **Sitemap:**
   - Keyboard navigation for collapsible sections
   - ARIA attributes for expand/collapse
   - Focus management
   - Screen reader support

---

## Next Steps

1. **Immediate:** Copy template files and remove `.template` extension
2. **Content:** Copy Terms and Conditions content from Rajasthan.gov.in
3. **Integration:** Add Footer to main App component
4. **Testing:** Test all footer links and pages
5. **Content Review:** Review and format Terms and Conditions content

---

**Status:** Templates created - Ready for implementation  
**References:**
- Terms & Conditions: https://rajasthan.gov.in/jankalyan-category-and-entry-type/0/51/88
- Website Policy: https://rajasthan.gov.in/pages/website-policies

