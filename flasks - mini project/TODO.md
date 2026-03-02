# Landing Page Redesign - TODO

## Plan Approval: ✅ Confirmed

## Tasks:

- [x] 1. Update `templates/landing.html` - Complete redesign with all sections
- [x] 2. Update `static/landing.css` - New design system with exact color palette
- [x] 3. Verify changes work correctly

## Design System:
- **Colors:**
  - Primary Dark: #1E1A28
  - Primary Accent: #9F69C5
  - Secondary: #CCB6B8
  - Light: #ECD6CD
  - Muted: #827E9C
- **Typography:**
  - Headings: Space Grotesk
  - Body: Inter
- **Sections:**
  - Hero (video background + 3D scene)
  - Features Grid (glass-morphic cards)
  - Stats (animated counters + purple glow)
  - CTA
  - Footer

## Implementation Notes:
- Video background uses existing `static/background.mp4`
- CSS uses Framer Motion CDN for animations
- Glass-morphism effects with backdrop-filter
- Animated counters triggered on scroll via Intersection Observer
- Parallax mouse effects on 3D scene elements
- Fully responsive design for all breakpoints
