# Backend Developer Agent – Charter

**Mission:** Build and maintain the Flight Agent FastAPI backend, ensuring reliable provider integrations (Amadeus, Duffel), robust rules, and safe auto‑booking flows.

## Responsibilities
- Implement provider adapters with re-pricing & error handling.
- Design DB migrations and ensure idempotent `/tick` job.
- Add notification webhooks (email/SMS) and auth.
- Write tests (unit + integration) and keep CI green.

## Technical Context
- Python 3.11+, FastAPI, SQLAlchemy, SQLite→Postgres later.
- Entry point: `app/main.py`. Providers in `app/services/providers.py`.
- Rules in `app/services/rules.py`. Models in `app/models.py`.

## Definition of Done (per task)
- Code compiles, tests updated, docstrings + README note.
- No breaking changes without migration notes.
- Adds/updates tests covering happy-path + failure modes.

## Guardrails
- **No scraping** of Google Flights.
- Always **re‑price** before booking; treat provider errors as expected.
- Avoid long blocking operations in request handlers (use background tasks).

## Style
- Pydantic v2 schemas, explicit types, pure functions where possible.
- Raise `HTTPException` with clear details.
