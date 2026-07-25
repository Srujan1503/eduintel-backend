# EduIntel AI — Backend (Phase 2, in progress)

## Modules built so far
- **Foundation**: config, DB session, security headers, logging, Alembic wiring
- **Auth**: Supabase JWT verification, `CurrentUser` resolution, `require_role`/`require_school` guards, `GET /api/v1/auth/me`

## Local setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your Supabase project's values
```

## Database
The full schema (all 18 tables, RLS, views, seed data) lives in `../02-schema.sql`
from Phase 1 — run it once in the Supabase SQL editor to provision a new project.
Alembic (`alembic.ini` / `migrations/`) is wired up to manage *incremental* schema
changes from here on, as each new module's models are added.

## Run
```bash
uvicorn main:app --reload
```
- Health check: `GET /health`
- Interactive docs: `/api/docs`

## Test
```bash
pytest app/tests -v
```

## Next modules (in order)
1. Schools (school profile CRUD, onboarding)
2. Competitors
3. Courses & Scholarships
4. Campaigns, Admissions, Admission Leads
5. Events, Parent Reviews, Social Media Posts
6. Marketing Analytics
7. AI (Predictions, Recommendations, Chat) — Gemini integration
8. Reports (PDF/CSV/XLSX export)
9. Notifications
10. Admin (users, roles, audit logs)
11. Background jobs (scheduled reports, prediction refresh)
