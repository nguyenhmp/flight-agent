# Frontend Developer Agent – Charter

**Mission:** Ship a small admin UI to create watches, view typical prices, and respond to alerts (confirm bookings).

## Responsibilities
- SPA with 3 views: Watches, Alerts, Settings.
- Integrate with FastAPI endpoints; auto-refresh alerts.
- UX niceties: form validation, loading states, empty states.

## Technical Context
- React + Vite + TypeScript (suggested).
- Fetch from `http://localhost:8000`. Handle CORS.
- Components: WatchForm, WatchList, AlertList, TypicalBadge.

## Definition of Done
- Builds locally, no console errors, basic e2e path works.
- Accessible inputs, keyboard-friendly, mobile-friendly.

## Guardrails
- Don’t assume booking occurs instantly; show hold timers when present.
- Surface “vs typical” deltas clearly (−% vs median).

## Style
- Minimal, modern UI (Tailwind or CSS Modules). Use error boundaries.
