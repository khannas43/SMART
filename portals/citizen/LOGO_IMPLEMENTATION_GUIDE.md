# Logo Implementation Guide - SMART Citizen Portal

**Created:** 2024-12-30  
**Purpose:** Guide for adding and implementing the National Emblem of India logo  
**Status:** Ready for Logo Addition

---

## Logo File Location

**Directory:** `portals/citizen/frontend/public/images/logos/`

**Current Files:**
1. ✅ `smart-logo.png` (Primary - PNG format) - **Already added**
2. `favicon.ico` (Browser favicon - optional)
3. `favicon-16x16.png` (optional)
4. `favicon-32x32.png` (optional)

---

## Adding the Logo

### Step 1: Logo File Status ✅

**Current Status:** Logo file has been added successfully!
- **File:** `smart-logo.png`
- **Location:** `portals/citizen/frontend/public/images/logos/smart-logo.png`
- **Format:** PNG (high resolution)
- **Access:** `/images/logos/smart-logo.png`

### Step 2: Verify File Access

The logo should be accessible at:
- **Public URL:** `/images/logos/smart-logo.png`
- **Full Path:** `portals/citizen/frontend/public/images/logos/smart-logo.png`

### Step 3: Optional Files (Can be added later)

Optional files you can add:
- `favicon.ico` (Browser favicon)
- `favicon-16x16.png`
- `favicon-32x32.png`
- PWA app icons (192x192, 512x512)

---

## Logo Specifications

### Display Dimensions

| Context | Width | Height | Format |
|---------|-------|--------|--------|
| **Header (Desktop)** | ~120px | 60px | PNG ✅ |
| **Header (Mobile)** | ~80px | 50px | PNG ✅ |
| **Header (Small Mobile)** | ~70px | 45px | PNG ✅ |
| **Favicon** | 32px | 32px | ICO/PNG (optional) |
| **PWA Icon** | 192px | 192px | PNG (optional) |

**Note:** Logo is currently in PNG format. The component uses CSS to scale the image appropriately.

### Visual Specifications

- **Aspect Ratio:** Maintain original emblem proportions
- **Padding:** 10px vertical, 20px horizontal (desktop)
- **Alignment:** Top-left corner, vertically centered in header
- **Spacing:** 20px gap between logo and navigation menu

---

## Implementation Checklist

- [x] Add `smart-logo.png` to `frontend/public/images/logos/` ✅ **COMPLETED**
- [ ] Verify logo displays correctly in Header component
- [ ] Create favicon files (16x16, 32x32, .ico) - Optional
- [ ] Update `manifest.json` to reference logo for PWA icons - Optional
- [ ] Test logo display on desktop (> 1024px)
- [ ] Test logo display on tablet (768px - 1024px)
- [ ] Test logo display on mobile (< 768px)
- [ ] Verify logo click behavior (navigates to dashboard)
- [ ] Test logo hover effect
- [ ] Verify logo accessibility (alt text, keyboard navigation)
- [ ] Check logo contrast with header background
- [ ] Test logo in both light and dark themes (if applicable)

---

## Quick Implementation

Logo file has been added! ✅

1. **Header Component:** Logo is configured in `Header.tsx.template` (updated to use PNG)
2. **Styling:** CSS is ready in `Header.css`
3. **Routes:** Logo links to `/citizen/dashboard`

**Next Steps:**
1. Copy `Header.tsx.template` to `Header.tsx` (remove `.template` extension)
2. The logo will automatically load from `/images/logos/smart-logo.png`
3. Test the header to ensure logo displays correctly

---

## Testing

After adding logo files:

```bash
# Start development server
npm start

# Verify logo appears in header
# Test logo click (should navigate to dashboard)
# Test on different screen sizes
# Test hover effect
# Check browser console for any image loading errors
```

---

**Status:** ⏳ Waiting for logo files to be added to the repository

