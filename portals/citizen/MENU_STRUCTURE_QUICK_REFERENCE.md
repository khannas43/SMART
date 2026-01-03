# Citizen Portal - Menu Structure Quick Reference

**Draft Version** - For Quick Review

---

## Main Menu Structure (Visual)

```
┌─────────────────────────────────────────────────────────────┐
│  SMART Citizen Portal                                       │
├─────────────────────────────────────────────────────────────┤
│  [Logo]  Dashboard | My Profile ▼ | Schemes ▼ | Applications ▼ │
│  Documents | Benefits ▼ | Services ▼ | Settings ▼ | Help ▼   │
│  [🔍] [🔔] [👤] [EN/HI]                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Complete Menu Tree

```
📊 Dashboard
   └── Profile Dashboard & 360° View (CIT-PROF-03)

👤 My Profile
   ├── 📊 Profile Dashboard (CIT-PROF-03)
   │   ├── Summary Tab
   │   └── 360° View Tab
   └── ✏️ Edit Profile (CIT-PROF-04)
       ├── Edit Tab
       └── Verification Tab

📋 Schemes
   ├── 🔍 Browse Schemes (CIT-SCHEME-05)
   │   └── Scheme Catalog & Search
   ├── 📄 Scheme Details (CIT-SCHEME-06) [Dynamic Route]
   └── ✅ Eligibility Checker (CIT-SCHEME-07)
       ├── Questionnaire Zone
       └── Live Results Panel

📝 My Applications
   ├── 📋 Applications Hub (CIT-APP-09)
   │   ├── Active Applications
   │   └── Past Applications
   └── ✅ Consent & Clarifications (CIT-CONSENT-08)
       ├── Scheme Consents
       └── Application Clarifications

📁 Documents
   └── 📄 Document Center (CIT-DOC-10)
       ├── Required Documents
       ├── Personal Library
       ├── Signed Documents (Raj-e-Sign)
       ├── e-Vault
       └── Downloads

💰 Benefits
   ├── 💵 Benefits & Entitlements (CIT-BEN-11)
   │   ├── Current Benefits
   │   ├── Forecast
   │   └── History
   └── 💳 Payments & Ledger (CIT-BEN-12)
       ├── Transactions
       └── Ledger Summary

🛠️ Services
   ├── 📋 Service Catalog (CIT-SERV-13)
   ├── 📝 Request Service (CIT-SERV-14)
   └── 📊 Service Status (CIT-SERV-15)
       ├── Active Requests
       ├── Completed Requests
       └── Feedback

⚙️ Settings
   ├── 🔔 Notification Preferences (CIT-USER-16)
   ├── 🚫 Opt-Out Schemes (CIT-USER-17)
   └── 🔒 Account & Security (CIT-USER-18)
       ├── Profile & Contact
       ├── Notifications & Consent
       ├── Password & MFA
       └── Sessions & Security

❓ Help & Support
   ├── 📚 Help Hub (CIT-HELP-19)
   │   ├── FAQs
   │   ├── Search
   │   ├── Announcements
   │   ├── Contact Options
   │   └── Create Ticket
   └── 🎫 My Tickets (CIT-HELP-20)
       ├── Ticket Status
       ├── Ticket History
       └── Create New Ticket
```

---

## Route Mapping

| Menu Item | Route | Screen ID | Screen Name |
|-----------|-------|-----------|-------------|
| Dashboard | `/citizen/dashboard` | CIT-PROF-03 | Profile Dashboard & 360° View |
| My Profile → Dashboard | `/citizen/profile/dashboard` | CIT-PROF-03 | Profile Dashboard & 360° View |
| My Profile → Edit | `/citizen/profile/edit` | CIT-PROF-04 | Profile Edit & Verification |
| Schemes → Browse | `/citizen/schemes/browse` | CIT-SCHEME-05 | Scheme Catalog & Search |
| Schemes → Details | `/citizen/schemes/:schemeId` | CIT-SCHEME-06 | Scheme Details |
| Schemes → Eligibility | `/citizen/schemes/eligibility` | CIT-SCHEME-07 | Eligibility & Recommendations |
| Applications → Hub | `/citizen/applications` | CIT-APP-09 | Applications Hub |
| Applications → Consent | `/citizen/applications/consent` | CIT-CONSENT-08 | Consent & Clarifications |
| Documents | `/citizen/documents` | CIT-DOC-10 | Document Center |
| Benefits → Overview | `/citizen/benefits` | CIT-BEN-11 | Benefits & Entitlements |
| Benefits → Payments | `/citizen/benefits/payments` | CIT-BEN-12 | Payments & Ledger |
| Services → Catalog | `/citizen/services/catalog` | CIT-SERV-13 | Service Catalog |
| Services → Request | `/citizen/services/request` | CIT-SERV-14 | Service Request |
| Services → Status | `/citizen/services/status` | CIT-SERV-15 | Service Status & Feedback |
| Settings → Notifications | `/citizen/settings/notifications` | CIT-USER-16 | Notification Preferences |
| Settings → Opt-Out | `/citizen/settings/opt-out` | CIT-USER-17 | Opt-Out Schemes |
| Settings → Account | `/citizen/settings/account` | CIT-USER-18 | Account & Security Settings |
| Help → Hub | `/citizen/help` | CIT-HELP-19 | Help & Support Hub |
| Help → Tickets | `/citizen/help/tickets` | CIT-HELP-20 | Tickets & Status |

**Note:** Authentication screens (CIT-AUTH-01, CIT-AUTH-02) are not in the main menu - they are accessed via login flow.

---

## Menu Item Counts

- **Top-Level Menu Items:** 8 items
- **Submenu Items:** 12 items
- **Total Navigable Items:** 20 items (18 screens + Dashboard duplicate)
- **Authentication Screens (Not in Menu):** 2 items (Login, MFA)

---

## Mobile Menu Structure

For screens < 768px, menu collapses to hamburger menu:

```
☰ Menu
  ├── 📊 Dashboard
  ├── 👤 My Profile
  │   ├── Profile Dashboard
  │   └── Edit Profile
  ├── 📋 Schemes
  │   ├── Browse Schemes
  │   └── Eligibility Checker
  ├── 📝 My Applications
  │   ├── Applications Hub
  │   └── Consent & Clarifications
  ├── 📁 Documents
  ├── 💰 Benefits
  │   ├── Benefits & Entitlements
  │   └── Payments & Ledger
  ├── 🛠️ Services
  │   ├── Service Catalog
  │   ├── Request Service
  │   └── Service Status
  ├── ⚙️ Settings
  │   ├── Notifications
  │   ├── Opt-Out Schemes
  │   └── Account & Security
  └── ❓ Help & Support
      ├── Help Hub
      └── My Tickets
```

---

## Hindi Menu Labels

| English | Hindi (Devanagari) |
|---------|-------------------|
| Dashboard | डैशबोर्ड |
| My Profile | मेरी प्रोफ़ाइल |
| Schemes | योजनाएं |
| My Applications | मेरे आवेदन |
| Documents | दस्तावेज़ |
| Benefits | लाभ |
| Services | सेवाएं |
| Settings | सेटिंग्स |
| Help & Support | सहायता और समर्थन |
| Browse Schemes | योजनाएं ब्राउज़ करें |
| Eligibility Checker | पात्रता जांचकर्ता |
| Applications Hub | आवेदन हब |
| Consent & Clarifications | सहमति और स्पष्टीकरण |
| Benefits & Entitlements | लाभ और पात्रता |
| Payments & Ledger | भुगतान और खाता |
| Service Catalog | सेवा कैटलॉग |
| Request Service | सेवा अनुरोध करें |
| Service Status | सेवा स्थिति |
| Notification Preferences | अधिसूचना वरीयताएं |
| Opt-Out Schemes | योजनाएं से बाहर निकलें |
| Account & Security | खाता और सुरक्षा |
| Help Hub | सहायता हब |
| My Tickets | मेरे टिकट |

---

**For detailed information, see:** `MENU_STRUCTURE.md`

