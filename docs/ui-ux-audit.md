## Phase 1 – UI/UX Audit & Modernization Plan

Date: 2025-11-25  
Author: Cursor assistant  
Scope: Frontend `Frontend/src` + UX pain-points reported by user

---

### 1. Navigation & Layout
- `routes/components/Navigation.svelte` couples layout + navigation. Sidebar is always rendered, causing:
  - Double scrollbars on small laptops; mobile overlay logic is brittle.
  - Notifications, search, and top-bar actions are embedded here, making reuse impossible (e.g., landing page, public routes).
- Action items lack keyboard handlers (`buttons in nav config`), generating repeated a11y warnings.
- Plan:
  1. Extract a `ShellLayout` component (header + sidebar) with slot-based regions.
  2. Build a responsive top-nav for public pages, and a collapsible left-nav for authenticated flows.
  3. Centralize design tokens (CSS vars for colors/spacing/typography).

### 2. Landing & Marketing Pages
- `routes/+page.svelte` is now a feature-rich hero but mixes content, layout, and animation logic in a single 700+ line file.
- No reusable typography scale; repeated inline classes (`text-3xl font-bold text-white` etc.).
- Plan:
  - Move hero/feature/FAQ sections into `lib/components/landing/*`.
  - Introduce Tailwind presets (via `app.css` or `tailwind.config.cjs` in future) to limit bespoke utility chains.
  - Add dark/light friendly palette (neutral background, accent tokens).

### 3. Discovery / Listing Grid
- `routes/discovery/+page.svelte` contains:
  - Console logging in production.
  - N+1 network operations (seed call on mount, then query).  
  - Intermixed search/filter UI + data fetching logic (700 lines).
  - “Contact owner” quick messaging duplicates logic from item page.
- Plan:
  - Extract hooks/services (e.g., `useDiscoveryData.ts`) for data + caching.
  - Create composable UI components: `SearchBar`, `CategoryChips`, `ItemCard`.
  - Remove seed call from runtime (move to CLI/DB migration).

### 4. Messaging Experience
- WebSocket upgrade done, but:
  - Conversation list still reuses stale styling; no presence indicator.
  - No optimistic status (sending/error).
  - Accessibility: message bubbles rely on color alone for direction.
- Plan:
  - Redesign chat UI with 2-column layout on desktop, single column on mobile (drawer for conversations).
  - Add optimistic bubble with status chips (sending/failed).
  - Provide improved timestamps + grouping.

### 5. Forms & Auth
- `routes/sign-in-up/+page.svelte` duplicates logic from root landing.
- Validation errors display but there’s no field-level success/neutral states.
- Plan:
  - Move auth forms into `lib/components/forms/AuthForm.svelte` with shared schema.
  - Add password strength indicator, progressive disclosure.

### 6. General Styling & Tokens
- Tailwind is imported via `@import 'tailwindcss';` without custom config.  
- No CSS variables for brand palette; repeated linear gradients.
- Plan:
  - Add `:root` token definitions in `app.css` (`--color-surface`, `--color-accent`, etc.).
  - Standardize spacing (4/8/12 px scale) + shadow levels.

### 7. Accessibility & Performance
- Many buttons without `aria-label` (see Vite console warnings).  
- Several lists rely on `div` + `on:click`.
- Plan:
  - Replace clickable divs with `<button>` or `<a>`.
  - Add focus outlines + skip links.
  - Lazy-load heavy sections (hero animations, testimonial data).

### 8. Bug Backlog (high-level)
| Feature | Issue | File |
|---------|-------|------|
| Notifications | Panel never closes on navigation; uses document click listeners without cleanup for SSR | `Navigation.svelte` |
| Discovery seeding | Calls `seedService.seedInitialData()` on every mount (expensive/insecure) | `routes/discovery/+page.svelte` |
| Messages | Conversation list shows self-user when trades created manually; duplicates exist | `messages/+page.svelte` |
| Item cards | Buttons (`Contact Owner`, `Trade Offer`) are divs with on:click warnings | `discovery/+page.svelte`, `item/[id]/+page.svelte` |

### 9. Modernization Roadmap (Phase 1 deliverables)
1. **Design tokens + typography**  
   - Update `app.css` with font stack, color vars, base body styles.
2. **Shell layout refactor**  
   - Create `ShellLayout.svelte` and update authenticated routes to use it.  
   - Move notifications/search into dedicated components.
3. **Component library pass**  
   - Buttons, cards, chips, badges defined in `lib/components/ui/*`.
4. **Page refreshes**  
   - Landing hero, Discovery grid, Messages view.
5. **Regression sweep**  
   - Navigate all routes, verify no console errors, run lint.

This document serves as the foundation for the modernization work. Each section above will map to follow-up tasks/PRs during Phase 1.

