# Logo Assets - SMART Citizen Portal

## Logo Files

### Primary Logo: National Emblem of India

**File:** `smart-logo.png`

**Description:**
- National Emblem of India (Lion Capital of Ashoka)
- Official government logo for Rajasthan SMART Portal
- PNG format (currently in use)
- Transparent background

**Specifications:**
- **Format:** PNG (high resolution)
- **File Location:** `frontend/public/images/logos/smart-logo.png`
- **Display Size:** 120px width (desktop), 80px (mobile) - maintains aspect ratio
- **Aspect Ratio:** Maintains original emblem proportions
- **Background:** Transparent
- **Resolution:** High resolution recommended for crisp display on retina screens

**Usage:**
- Top-left corner of every page
- Clickable - links to Dashboard (`/citizen/dashboard`)
- Always visible in header navigation

### Logo Variants Needed

1. **Primary Logo (Header)**
   - Size: ~120-150px width
   - Format: SVG or PNG (high resolution)
   - Use: Main header navigation

2. **Favicon**
   - Size: 32x32px, 16x16px
   - Format: ICO or PNG
   - Use: Browser tab icon

3. **PWA App Icon** (referenced in manifest.json)
   - Size: 192x192px, 512x512px
   - Format: PNG
   - Use: "Add to Home Screen" app icon

4. **Mobile Logo** (optional - smaller version)
   - Size: ~80-100px width
   - Format: SVG or PNG
   - Use: Mobile header (smaller screens)

## File Structure

```
frontend/public/images/
├── logos/
│   ├── smart-logo.png           # Primary logo (PNG - currently in use)
│   ├── favicon.ico              # Browser favicon (optional)
│   ├── favicon-16x16.png        # 16x16 favicon (optional)
│   ├── favicon-32x32.png        # 32x32 favicon (optional)
│   ├── apple-touch-icon.png     # 180x180 for iOS (optional)
│   └── README.md                # This file
```

**Note:** Currently using PNG format. Logo file is located at:
`portals/citizen/frontend/public/images/logos/smart-logo.png`

## Logo Placement Guidelines

### Header Layout

```
┌─────────────────────────────────────────────────────────────┐
│ [Logo]  [Menu Items]           [Search] [🔔] [👤] [EN/HI] │
└─────────────────────────────────────────────────────────────┘
```

**Logo Position:**
- **Desktop:** Left side of header, ~20px padding from left edge
- **Mobile:** Left side, slightly smaller size (~80-100px width)
- **Height:** Should align with header height (~60-70px)

**Logo Behavior:**
- Clickable: Clicking logo navigates to Dashboard (`/citizen/dashboard`)
- Hover effect: Subtle scale or opacity change (optional)
- Always visible: Logo remains visible on all pages

## Implementation Notes

### React Component Usage

```tsx
import { Link } from 'react-router-dom';

<Link to="/citizen/dashboard" className="logo-link">
  <img 
    src="/images/logos/smart-logo.png" 
    alt="SMART Citizen Portal" 
    className="header-logo"
    height="60"
    width="auto"
  />
</Link>
```

**Note:** Using public path (`/images/logos/smart-logo.png`) since the logo is in the `public` directory.

### CSS Styling

```css
.header-logo {
  height: 60px;
  width: auto;
  padding: 10px 20px;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.header-logo:hover {
  opacity: 0.8;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .header-logo {
    height: 50px;
    padding: 10px 15px;
  }
}
```

## Image Repository Location

**Path:** `portals/citizen/frontend/public/images/logos/`

**Current Logo File:**
- **File:** `smart-logo.png`
- **Full Path:** `portals/citizen/frontend/public/images/logos/smart-logo.png`

**Access in React:**
- Use public path: `/images/logos/smart-logo.png`
- Since file is in `public` directory, use absolute path starting with `/`

## Brand Guidelines

1. **Never modify** the National Emblem
2. **Maintain aspect ratio** when resizing
3. **Use appropriate version** (light/dark) for background contrast
4. **Ensure minimum size** of 60px height for readability
5. **Keep adequate spacing** from other header elements

## Status

✅ **Logo Added:** Primary logo file is now in place
- ✅ Primary logo: `smart-logo.png` (PNG format)
- ⏳ Favicon files (optional - can be added later)
- ⏳ PWA app icons (optional - can be added later)

**Note:** The logo is currently in PNG format. If you need to use SVG in the future for better scalability, you can add `smart-logo.svg` and update the component accordingly.

---

**Note:** The National Emblem of India should be used with proper authorization and respect. Ensure compliance with government branding guidelines.

