# Routes Configuration - Citizen Portal

**Created:** 2024-12-30  
**Purpose:** Document all routes including footer pages  
**Status:** Draft

---

## Footer Page Routes

### Terms and Conditions
- **Route:** `/citizen/terms-conditions`
- **Component:** `TermsAndConditions`
- **Access:** Public (accessible without authentication)
- **Content Source:** https://rajasthan.gov.in/jankalyan-category-and-entry-type/0/51/88

### Sitemap
- **Route:** `/citizen/sitemap`
- **Component:** `Sitemap`
- **Access:** Public (accessible without authentication)
- **Description:** Displays all portal pages and sections

---

## Complete Route Structure

```
/citizen/
├── /login                          # CIT-AUTH-01 (Public)
├── /mfa                            # CIT-AUTH-02 (Authenticated)
│
├── /dashboard                      # CIT-PROF-03 (Authenticated)
│
├── /profile
│   ├── /dashboard                  # CIT-PROF-03
│   └── /edit                       # CIT-PROF-04
│
├── /schemes
│   ├── /browse                     # CIT-SCHEME-05
│   ├── /eligibility                # CIT-SCHEME-07
│   └── /:schemeId                  # CIT-SCHEME-06 (dynamic)
│
├── /applications
│   ├── /                           # CIT-APP-09
│   └── /consent                    # CIT-CONSENT-08
│
├── /documents                      # CIT-DOC-10
│
├── /benefits
│   ├── /                           # CIT-BEN-11
│   └── /payments                   # CIT-BEN-12
│
├── /services
│   ├── /catalog                    # CIT-SERV-13
│   ├── /request                    # CIT-SERV-14
│   └── /status                     # CIT-SERV-15
│
├── /settings
│   ├── /notifications              # CIT-USER-16
│   ├── /opt-out                    # CIT-USER-17
│   └── /account                    # CIT-USER-18
│
├── /help
│   ├── /                           # CIT-HELP-19
│   └── /tickets                    # CIT-HELP-20
│
└── Footer Pages (Public)
    ├── /terms-conditions           # Terms & Conditions
    └── /sitemap                    # Sitemap
```

---

## Route Configuration Example

```tsx
import { Routes, Route } from 'react-router-dom';
import TermsAndConditions from './pages/TermsAndConditions';
import Sitemap from './pages/Sitemap';
// ... other imports

<Routes>
  {/* Footer Pages - Public Access */}
  <Route path="/citizen/terms-conditions" element={<TermsAndConditions />} />
  <Route path="/citizen/sitemap" element={<Sitemap />} />
  
  {/* Other routes */}
  {/* ... */}
</Routes>
```

---

**Note:** Footer pages should be accessible without authentication for better user experience and compliance with government website standards.

