## What does this PR do?

Implements **Phase 01 – Database Models & Migrations**.

- Creates all **15 SQLAlchemy ORM models** in `backend/app/models/` matching every table in Spec Sections 5 and 16.8:
  `source_records`, `clean_records`, `match_candidates`, `farmers`, `farmer_links`, `land_parcels`, `schemes`, `enrollments`, `flags`, `recommendations`, `users`, `audit_log`, `farmer_profiles`, `scheme_applications`, `email_log`
- Adds all **blocking indexes** from Spec Section 5:
  - `clean_records(district_code, name_phonetic)`
  - `clean_records(mobile10)`
  - `clean_records(village_code, survey_no)`
  - `flags(status, type)`
  - `farmer_links(farmer_id)`
- Adds a **generic `BaseRepository`** (`get / get_all / save`) and 8 table-specific repository classes in `backend/app/repositories/`.
- Wires **Alembic** `env.py` to read `DATABASE_URL` from `app.core.config.settings` and generates migration `0001_initial_schema.py` via autogenerate.
- Removes the temporary one-shot scaffolding script `generate_models.py`.

## How to test

```bash
# 1. Start Postgres (Docker or local instance)
docker compose up -d   # if docker-compose.yml is present, else use local pg

# 2. Apply migration
cd backend
alembic upgrade head

# 3. Run Phase 01 tests
PYTHONPATH=. DATABASE_URL=postgresql+psycopg2://<user>:<pass>@localhost:5432/<db> \
  pytest tests/phase_01/ -v
```

Expected output:
```
tests/phase_01/test_db_models.py::test_insert_and_retrieve_all_models PASSED
tests/phase_01/test_db_models.py::test_indexes_exist PASSED
2 passed in ~1.3s
```

- [x] Run `pytest tests/phase_01/test_db_models.py` — 2 tests pass
- [x] `alembic upgrade head` succeeds on a fresh DB
- [ ] UI tested (not applicable — backend-only phase)

## Screenshots

N/A — no UI changes in this phase.

## Checklist
- [x] Tests passed locally (`2 passed, 1 warning`)
- [x] `ruff check .` passes with 0 errors
- [x] `black --check .` passes
- [ ] CI is green (awaiting GitHub Actions run)
- [ ] My teammate has reviewed
