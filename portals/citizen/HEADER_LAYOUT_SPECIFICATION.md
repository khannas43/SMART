# Citizen Portal - Header Layout Specification

**Created:** 2024-12-30  
**Purpose:** Detailed specification for portal header with logo placement  
**Status:** Draft - Pending Design Review

---

## Header Structure

### Desktop Header Layout (> 1024px)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  [Logo]    [Dashboard] [My Profile ▼] [Schemes ▼] [Applications ▼] ...     │
│  (120px)                                                                     │
│                                                                              │
│                        [🔍 Search Bar]    [🔔] [👤] [EN/HI]                 │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Mobile Header Layout (< 768px)

```
┌─────────────────────────────────────┐
│ [Logo]          [🔍] [🔔] [☰ Menu] │
│ (80px)                              │
└─────────────────────────────────────┘
```

---

## Header Components Layout

### Component Positioning

| Component | Desktop Position | Mobile Position | Width/Size |
|-----------|-----------------|-----------------|------------|
| **Logo** | Top-left, 20px padding | Top-left, 15px padding | 120px (desktop), 80px (mobile) |
| **Main Menu** | Left of center, after logo | Hidden (hamburger menu) | Auto |
| **Search Bar** | Center-right | Top-right (icon only) | 300px (desktop), 40px icon (mobile) |
| **Notifications** | Right, before user menu | Right, before hamburger | 40px icon |
| **User Menu** | Right, before language | Hidden (in hamburger) | Auto |
| **Language Switcher** | Far right | In hamburger menu | 100px (desktop) |
| **Hamburger Menu** | Hidden | Far right | 40px icon (mobile) |

---

## Logo Specifications

### Logo Details

**Image:** National Emblem of India (Lion Capital of Ashoka)  
**Location:** Top-left corner of header  
**File Path:** `/images/logos/smart-logo.png` (PNG format)

**Dimensions:**
- **Desktop:** Height: 60px, Width: Auto (maintains aspect ratio, ~120px)
- **Mobile:** Height: 50px, Width: Auto (~80px)
- **Padding:** 10px vertical, 20px horizontal (desktop), 10px/15px (mobile)

**Behavior:**
- **Clickable:** Yes - Links to Dashboard (`/citizen/dashboard`)
- **Hover Effect:** Slight opacity change (0.8) or scale (1.05)
- **Alt Text:** "SMART Citizen Portal - Rajasthan Government"
- **Always Visible:** Logo remains visible on all pages

### Logo Styling

```css
.header-logo {
  height: 60px;
  width: auto;
  padding: 10px 20px;
  cursor: pointer;
  transition: opacity 0.2s ease, transform 0.2s ease;
  display: flex;
  align-items: center;
}

.header-logo:hover {
  opacity: 0.8;
  transform: scale(1.02);
}

.header-logo img {
  height: 100%;
  width: auto;
  object-fit: contain;
}

/* Mobile adjustments */
@media (max-width: 768px) {
  .header-logo {
    height: 50px;
    padding: 10px 15px;
  }
}

@media (max-width: 480px) {
  .header-logo {
    height: 45px;
    padding: 8px 12px;
  }
}
```

---

## Header Design Specifications

### Header Container

**Height:**
- Desktop: 70px
- Mobile: 60px

**Background:**
- Primary: White (#FFFFFF) or Light Gray (#F5F5F5)
- Alternative: Dark theme option (Dark Blue #1a237e or Black #1a1a1a)
- Border: Bottom border 1px solid #e0e0e0 (subtle separator)

**Padding:**
- Desktop: 0px vertical, 0px horizontal (padding on child elements)
- Mobile: 0px vertical, 0px horizontal

**Shadow (Optional):**
- Subtle box-shadow for depth: `0 2px 4px rgba(0,0,0,0.1)`

### Header CSS Structure

```css
.header {
  height: 70px;
  background-color: #ffffff;
  border-bottom: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-left {
  display: flex;
  align-items: center;
  flex: 0 0 auto;
}

.header-center {
  display: flex;
  align-items: center;
  flex: 1 1 auto;
  justify-content: center;
  padding: 0 20px;
}

.header-right {
  display: flex;
  align-items: center;
  flex: 0 0 auto;
  gap: 15px;
  padding-right: 20px;
}

/* Mobile */
@media (max-width: 768px) {
  .header {
    height: 60px;
  }
  
  .header-center {
    display: none; /* Hide main menu on mobile */
  }
}
```

---

## Complete Header Component Structure

```
Header (70px height, sticky)
├── Header Left
│   ├── Logo (Link to Dashboard)
│   │   └── Logo Image
│   └── Main Navigation Menu (Desktop only)
│       ├── Dashboard
│       ├── My Profile (with dropdown)
│       ├── Schemes (with dropdown)
│       ├── Applications (with dropdown)
│       ├── Documents
│       ├── Benefits (with dropdown)
│       ├── Services (with dropdown)
│       ├── Settings (with dropdown)
│       └── Help (with dropdown)
│
├── Header Center (Optional - for search or announcements)
│   └── Global Search Bar (Desktop)
│
└── Header Right
    ├── Search Icon (Mobile only)
    ├── Notifications Icon (with badge)
    ├── User Menu (Desktop)
    │   └── Avatar/Name Dropdown
    ├── Language Switcher (Desktop)
    │   └── EN/HI Dropdown
    └── Hamburger Menu (Mobile only)
        └── Mobile Menu Drawer
```

---

## Logo Implementation Example

### React Component

```tsx
// components/layout/Header.tsx
import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const Header: React.FC = () => {
  const { t } = useTranslation();

  return (
    <header className="header">
      <div className="header-left">
        {/* Logo */}
        <Link to="/citizen/dashboard" className="logo-link" aria-label={t('common.appName')}>
          <img 
            src="/images/logos/smart-logo.png" 
            alt={t('common.appName')}
            className="header-logo"
            height="60"
            width="auto"
          />
        </Link>
        
        {/* Main Navigation - Desktop Only */}
        <nav className="main-navigation desktop-only">
          {/* Menu items here */}
        </nav>
      </div>

      <div className="header-center">
        {/* Global Search - Desktop */}
        <SearchBar className="global-search desktop-only" />
      </div>

      <div className="header-right">
        {/* Notifications, User Menu, Language Switcher, Hamburger */}
      </div>
    </header>
  );
};

export default Header;
```

---

## Responsive Breakpoints

### Desktop (> 1024px)
- Full menu visible
- Logo: 120px width
- Search bar visible
- All header elements visible

### Tablet (768px - 1024px)
- Full menu visible (may collapse if space needed)
- Logo: 100px width
- Search bar visible
- All elements visible (may need adjustments)

### Mobile (< 768px)
- Logo: 80px width
- Hamburger menu replaces main navigation
- Search icon replaces search bar
- Language switcher in hamburger menu
- User menu in hamburger menu

---

## Accessibility Requirements

1. **Logo Link:**
   - Proper `aria-label` for screen readers
   - Keyboard accessible (focusable)
   - Clear focus indicator

2. **Semantic HTML:**
   - Use `<header>` element
   - Use `<nav>` for navigation
   - Use proper heading hierarchy

3. **Contrast:**
   - Logo should have sufficient contrast with background
   - Text in header should meet WCAG AA standards

---

## Visual Design Guidelines

### Color Scheme

**Light Theme (Recommended):**
- Background: #FFFFFF (White)
- Border: #E0E0E0 (Light Gray)
- Logo: Dark/Black version
- Text: #1A1A1A (Dark Gray)

**Dark Theme (Optional):**
- Background: #1A237E (Dark Blue) or #1A1A1A (Black)
- Border: #424242 (Dark Gray)
- Logo: Light/White version
- Text: #FFFFFF (White)

### Typography

- Font: System fonts or Noto Sans (English + Hindi support)
- Logo area: No text overlay on logo
- Menu items: 14-16px font size
- Clear, readable labels

### Spacing

- Logo padding: 20px left, 10px top/bottom (desktop)
- Menu item spacing: 20-30px between items
- Right section spacing: 15px gap between icons
- Overall header padding: Balanced margins

---

## Implementation Checklist

- [ ] Add logo file to `frontend/public/images/logos/`
- [ ] Create Header component
- [ ] Implement logo placement (top-left)
- [ ] Add logo click handler (navigate to dashboard)
- [ ] Style logo with hover effects
- [ ] Make logo responsive (different sizes for mobile)
- [ ] Test logo visibility on all pages
- [ ] Test logo accessibility (keyboard, screen reader)
- [ ] Test logo on different screen sizes
- [ ] Verify logo alignment with menu items

---

**Status:** Draft - Ready for Design Implementation  
**Next Steps:**
1. Add actual logo files to `frontend/public/images/logos/`
2. Implement Header component with logo
3. Test across different screen sizes
4. Get design review and approval

