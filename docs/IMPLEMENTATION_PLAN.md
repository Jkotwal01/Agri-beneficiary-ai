# Agri Beneficiary Intelligence – Implementation Plan

> **Source of truth:** `docs/Agri_Beneficiary_Intelligence_Spec.md`
> **Total budget:** ~20 days → 15 phases, each 1–2 days.
> **Branch naming:** `feature/phase-<NN>-<short-name>` from the latest `main`.
> **Never commit directly to `main`.** Every phase ends with a passing CI run before merge.

---

## Phase overview table

| # | Name | Days | Layer |
|---|------|------|-------|
| 00 | Base template | 1 | Infra |
| 01 | Database models & migrations | 1 | Backend |
| 02 | Synthetic data generator | 1 | Data |
| 03 | Ingestion module | 1 | Backend |
| 04 | Preprocessing / normalizers | 1 | Backend |
| 05 | Auth (JWT) + user endpoints | 1 | Backend + FE |
| 06 | Blocking & pair features | 1 | Backend |
| 07 | ML matcher + resolution service | 2 | Backend |
| 08 | Duplicate rules & eligibility engine | 1 | Backend |
| 09 | Recommendations, exclusions & report endpoints | 1 | Backend + FE |
| 10 | Officer dashboard + farmers pages | 2 | Frontend |
| 11 | Review queue & match decision backend | 1 | Backend + FE |
| 12 | Farmer portal – backend | 2 | Backend |
| 13 | Farmer portal – frontend | 2 | Frontend |
| 14 | Email notifications & profile linking | 1 | Backend |
| 15 | Evaluation, SHAP & final polish | 1 | Backend + FE |

---

## Phase 00 – Base Template (Step 1 from the prompt)

### Goal
Establish the monorepo skeleton that every subsequent phase builds on. This is the **last direct commit to `main`**.

### Files / modules created
```
backend/
  app/
    main.py              # FastAPI app, CORS, /health endpoint
    core/
      config.py          # Settings via pydantic-settings (.env)
      db.py              # SQLAlchemy engine + get_db dependency
  api/
    deps.py              # (empty shell, filled per phase)
  requirements.txt
  alembic/               # alembic.ini + env.py (no migrations yet)
frontend/
  package.json           # React + Vite + TS + Tailwind + Vitest
  src/
    main.tsx
    App.tsx              # placeholder "Hello Agri" page
    api/client.ts        # axios base instance
docker-compose.yml       # PostgreSQL 16 + MailHog
.env.example
.gitignore
README.md
.github/
  workflows/ci.yml       # ruff, black --check, pytest, npm run lint, vitest, npm run build
  pull_request_template.md
.pre-commit-config.yaml  # ruff, black, prettier
```

### Tests
- **Backend:** `pytest tests/test_health.py` → `GET /health` returns `{"status": "ok"}` (200).
- **Frontend:** `src/__tests__/App.test.tsx` – renders without crash, shows "Agri" text.
- **CI:** GitHub Actions workflow passes both.

### Done when
- `docker compose up -d` starts PostgreSQL with no errors.
- `uvicorn app.main:app --reload` serves `/health` → 200.
- `npm run dev` shows placeholder page.
- `npm run test` (Vitest) is green.
- `pytest` is green.
- GitHub Actions CI workflow passes on push to `main`.

---

## Phase 01 – Database Models & Migrations

**Branch:** `feature/phase-01-db-models`

### Goal
Define every SQLAlchemy ORM model and Alembic migration for all 14 tables in Sections 5 and 16.8. Add CRUD repositories with basic `get` / `list` / `save`.

### Files / modules created
```
backend/app/
  models/
    source_record.py
    clean_record.py
    match_candidate.py
    farmer.py
    farmer_link.py
    land_parcel.py
    scheme.py
    enrollment.py
    flag.py
    recommendation.py
    user.py
    audit_log.py
    farmer_profile.py
    scheme_application.py
    email_log.py
  repositories/
    base.py              # generic get/list/save helpers
    farmer_repo.py
    clean_record_repo.py
    match_repo.py
    flag_repo.py
    profile_repo.py
    application_repo.py
    email_log_repo.py
alembic/versions/
  0001_initial_schema.py
```

### Tests
- **Backend pytest E2E:** `tests/phase_01/test_db_models.py`
  1. Apply migration against a test PostgreSQL DB.
  2. Insert one row into each table via the repository.
  3. Assert the row is retrievable with the correct columns.
  4. Assert all indexes from Section 5 exist (`information_schema`).

### Done when
- `alembic upgrade head` succeeds on a fresh DB.
- All 15 table models exist in `models/`.
- All repository `save` + `get` operations pass.
- `pytest tests/phase_01/` is green.

---

## Phase 02 – Synthetic Data Generator

**Branch:** `feature/phase-02-synthetic-data`

### Goal
Implement `scripts/generate_synthetic_data.py` exactly as Section 4.2 describes: 5,000 true farmers, 5 source CSVs (≈12,000 rows total), realistic noise, planted duplicate/fraud problems, separate `ground_truth.csv`.

### Files / modules created
```
scripts/
  generate_synthetic_data.py
  seed_db.py              # loads CSVs into source_records (used in later phases)
data/synthetic/
  agristack_farmers.csv  (git-ignored except tiny 50-row sample)
  pmkisan.csv
  pmfby.csv
  nfsm.csv
  kcc.csv
  ground_truth.csv       (git-ignored)
data/synthetic/samples/  # 50-row samples committed for CI
```

### Tests
- **Backend pytest E2E:** `tests/phase_02/test_synthetic_data.py`
  1. Run the generator script via import.
  2. Assert all 5 CSV files exist.
  3. Assert total rows across all CSVs ≥ 10,000 and ≤ 15,000.
  4. Assert `ground_truth.csv` has exactly 5,000 rows.
  5. Assert planted duplicate count matches the 3% threshold (±1%).
  6. Assert no full Aadhaar or full bank account number columns exist.

### Done when
- Script runs in < 60 s.
- Output stats printed (farmer count, record count, duplicate count).
- All assertions in the test pass.

---

## Phase 03 – Ingestion Module

**Branch:** `feature/phase-03-ingestion`

### Goal
Implement Module 1 (Section 6): `SourceAdapter` ABC, one concrete adapter per source CSV, and `IngestionService` that writes rows to `source_records`.

### Files / modules created
```
backend/app/
  ingestion/
    base.py              # SourceAdapter ABC
    adapters/
      agristack.py
      pmkisan.py
      pmfby.py
      nfsm.py
      kcc.py
    registry.py          # {source_name: adapter_class}
  services/
    ingestion_service.py
  api/routers/
    pipeline.py          # POST /pipeline/ingest (admin only, BackgroundTasks)
  schemas/
    pipeline.py          # PipelineResponse
```

### Tests
- **Backend pytest E2E:** `tests/phase_03/test_ingestion.py`
  1. Load the 50-row sample CSVs.
  2. Instantiate `IngestionService` with a real test-DB session.
  3. Call `service.ingest_all(data_dir)`.
  4. Assert `source_records` has 250 rows (5 files × 50).
  5. Assert `raw_json` JSONB is populated for each row.
  6. Assert `source_name` matches the adapter's `source_name`.
  7. Hit `POST /pipeline/ingest` via `TestClient`, assert 202.

### Done when
- `POST /pipeline/ingest` returns 202.
- Full 12,000-row dataset ingested in < 30 s.
- All phase tests green.

---

## Phase 04 – Preprocessing / Normalizers

**Branch:** `feature/phase-04-preprocessing`

### Goal
Implement Module 2 (Section 6): all six normalizer functions in `preprocessing/normalizers.py`, a `PreprocessingPipeline`, and write rows to `clean_records`.

### Files / modules created
```
backend/app/
  preprocessing/
    normalizers.py        # normalize_name, phonetic_key, normalize_mobile,
                          # normalize_village, parse_dob, fill_missing
    pipeline.py           # PreprocessingPipeline: source_records → clean_records
  services/
    preprocessing_service.py
  api/routers/pipeline.py  # add POST /pipeline/preprocess
  data/
    village_lookup.csv     # small LGD-code lookup
```

### Tests
- **Backend pytest E2E:** `tests/phase_04/test_preprocessing.py`
  1. `normalize_name("Shri Ramesh Kotwal")` → `"ramesh kotwal"`.
  2. `phonetic_key("Kotwal")` == `phonetic_key("Kotval")`.
  3. `normalize_mobile("0 91 98765-43210")` → `"9876543210"`.
  4. `parse_dob("15-Aug-1985")` → `date(1985, 8, 15)`.
  5. `fill_missing` never replaces null with an invented value.
  6. Integration: run `PreprocessingPipeline` on 250 ingested sample rows → 250 `clean_records` rows with non-null `name_norm`.

### Done when
- All 6 normalizer unit tests pass.
- Integration test: 250 `clean_records` rows written.
- `POST /pipeline/preprocess` returns 202.

---

## Phase 05 – Auth (JWT) + User Endpoints

**Branch:** `feature/phase-05-auth`

### Goal
Implement JWT auth with three roles (`admin`, `officer`, `farmer`), `POST /auth/login`, `POST /auth/register` (farmer self-signup), and role-gated `Depends`. Wire up the React login page and role-based routing.

### Files / modules created
```
backend/app/
  core/
    security.py           # hash_password, verify_password, create_token, decode_token
  api/
    deps.py               # get_current_user, require_role(role)
  api/routers/
    auth.py               # POST /auth/login, POST /auth/register
  schemas/
    auth.py               # LoginRequest, TokenResponse, RegisterRequest

frontend/src/
  api/auth.ts
  types/auth.ts
  hooks/useAuth.ts
  pages/LoginPage.tsx
  pages/RegisterPage.tsx
  routes.tsx              # protected routes by role
  context/AuthContext.tsx
  __tests__/LoginPage.test.tsx
```

### Tests
- **Backend pytest E2E:** `tests/phase_05/test_auth.py`
  1. `POST /auth/register` with role=farmer → 201, user saved with hashed password.
  2. `POST /auth/login` with correct credentials → 200, token returned.
  3. `POST /auth/login` with wrong password → 401.
  4. `GET /farmers` without token → 401.
  5. `GET /farmers` with farmer-role token → 403.
  6. `GET /farmers` with officer-role token → 200 (empty list).
- **Frontend Vitest E2E:** `src/__tests__/LoginPage.test.tsx`
  1. Renders email + password inputs and submit button.
  2. Valid mock credentials → `useAuth` called with token.
  3. Bad credentials → error message displayed.
  4. After login, redirects to `/dashboard` (officer) or `/me` (farmer).

### Done when
- All 6 backend auth tests green.
- Frontend login test green.
- `GET /health` still works unauthenticated.

---

## Phase 06 – Blocking & Pair Features

**Branch:** `feature/phase-06-blocking-features`

### Goal
Implement `resolution/blocking.py` (three blocking keys from Section 6 Module 3 Stage 1) and `resolution/features.py` (8 pair-features from Stage 2). Pure Python, no database access.

### Files / modules created
```
backend/app/
  resolution/
    blocking.py           # PhoneticVillageBlocker: candidate_pairs(records) -> list[tuple]
    features.py           # build_feature_vector(a, b) -> dict
```

### Tests
- **Backend pytest E2E:** `tests/phase_06/test_blocking_features.py`
  1. Two records sharing `district_code + name_phonetic` → candidate pair.
  2. Two records sharing `mobile10` → candidate pair.
  3. Two records sharing `village_code + survey_no` → candidate pair.
  4. Two completely unrelated records → NOT a candidate pair.
  5. Reduction ratio: blocking on 250-row sample generates < 2,500 pairs.
  6. Pair completeness: all planted true-match pairs appear in candidate pairs.
  7. Feature vector: `name_jw` in [0,1]; `same_mobile` is 1/0/−1; `father_name_sim` is −1 when either is null.

### Done when
- All 7 tests green.
- Blocking on 5,000 clean records runs in < 10 s (measured in test).

---

## Phase 07 – ML Matcher + Resolution Service

**Branch:** `feature/phase-07-resolution`

### Goal
Implement `resolution/matcher.py` (XGBoost + rule shortcut), `resolution/clustering.py` (NetworkX + chain guard), `resolution/golden_record.py` (survivorship), `services/resolution_service.py` (orchestration), and the training script. Write `match_candidates`, `farmers`, `farmer_links`, `land_parcels`.

### Files / modules created
```
backend/app/
  resolution/
    matcher.py            # XGBoostPairMatcher, RuleShortcutMatcher
    clustering.py         # build_clusters(linked_pairs) -> List[List[id]]
    golden_record.py      # TrustOrderGoldenRecordBuilder
  services/
    resolution_service.py
  api/routers/pipeline.py  # add POST /pipeline/resolve
  schemas/
    resolution.py         # ResolutionSummary

scripts/
  train_matcher.py        # trains XGBoost, saves models/matcher.joblib

models/
  .gitkeep               # matcher.joblib is git-ignored
```

### Tests
- **Backend pytest E2E:** `tests/phase_07/test_resolution.py`
  1. Train script runs on sample ground truth and creates `matcher.joblib`.
  2. `XGBoostPairMatcher.score(a, b)` returns float in [0, 1].
  3. `build_clusters` on a 5-node graph with 3 edges → correct components.
  4. Chain guard: component with > 6 records → flagged for review, not merged.
  5. Chain guard: component with 2 different AgriStack IDs → not auto-merged.
  6. `GoldenRecordBuilder` prefers AgriStack name over NFSM name.
  7. Full `ResolutionService.run()` on 250-row sample DB → ≥ 40 farmers in `farmers`, `match_candidates` populated, `ResolutionSummary` returned.
  8. `POST /pipeline/resolve` via TestClient → 202.

### Done when
- Matcher F1 > 0.90 on the mini sample ground truth.
- Full pipeline produces a non-empty `farmers` table.
- All 8 tests green.

---

## Phase 08 – Duplicate Rules & Eligibility Engine

**Branch:** `feature/phase-08-rules-engine`

### Goal
Implement Module 4 (5 duplicate rule classes) and Module 5 (YAML eligibility engine with `schemes.yaml`). Write to `flags` and `recommendations`.

### Files / modules created
```
backend/app/
  duplicates/
    base.py               # DuplicateRule ABC: check(farmer) -> list[Flag]
    rules/
      same_scheme_twice.py
      mutually_exclusive.py
      parcel_overclaim.py
      shared_bank_account.py
      low_confidence_merge.py
  eligibility/
    engine.py             # evaluate(scheme_rules, facts) -> EligibilityResult
    rules/
      schemes.yaml        # PM_KISAN, PMFBY, NFSM, KCC blocks
  services/
    duplicate_service.py
    eligibility_service.py
  api/routers/
    flags.py              # GET /flags, PATCH /flags/{id}
    recommendations.py    # GET /recommendations?farmer_id=
  api/routers/pipeline.py # add POST /pipeline/evaluate
  schemas/
    flags.py
    recommendations.py
```

### Tests
- **Backend pytest E2E:** `tests/phase_08/test_rules_engine.py`
  1. `SameSchemeTwice` raises High-severity flag for farmer with two pmkisan enrollments same season.
  2. `ParcelOverclaim` raises Medium flag when claims exceed parcel area.
  3. `SharedBankAccount` detects planted shared-bank rows.
  4. `LowConfidenceMerge` fires only when confidence < threshold.
  5. Eligibility: farmer with 0 land → PM_KISAN not eligible, reason contains field check.
  6. Eligibility: marginal farmer with 0.5 ha → PM_KISAN eligible.
  7. `GET /flags?type=SameSchemeTwice&status=open` returns only matching flags.
  8. `PATCH /flags/{id}` with `{"status": "confirmed"}` updates DB and writes `audit_log`.
  9. Full E2E: run both services on sample data → at least one flag of each type, one eligible recommendation per scheme.

### Done when
- All 9 tests green.
- `POST /pipeline/evaluate` returns 202 and triggers both services.

---

## Phase 09 – Recommendations, Exclusions & Report Endpoints

**Branch:** `feature/phase-09-reports`

### Goal
Implement `GET /recommendations`, `GET /exclusions`, `GET /reports/summary`, `GET /reports/coverage`, and `GET /reports/export`. Build the React Dashboard KPI cards wired via MSW mock.

### Files / modules created
```
backend/app/
  services/
    report_service.py
  api/routers/
    reports.py
    exclusions.py
  schemas/
    reports.py

frontend/src/
  api/reports.ts
  api/farmers.ts
  hooks/useReports.ts
  hooks/useFarmers.ts
  types/farmer.ts
  types/report.ts
  pages/DashboardPage.tsx   # KpiCard grid + CoverageBarChart
  components/
    KpiCard.tsx
    CoverageBarChart.tsx
    TrendLineChart.tsx
  mocks/
    handlers.ts
    browser.ts
  __tests__/DashboardPage.test.tsx
```

### Tests
- **Backend pytest E2E:** `tests/phase_09/test_reports.py`
  1. `GET /reports/summary` returns `total_records`, `unique_farmers`, `open_flags`, `exclusions`.
  2. `GET /reports/coverage?group_by=district` returns list with `district` + `count` + `scheme_coverage`.
  3. `GET /reports/export?type=exclusions` returns CSV content-type.
  4. `GET /exclusions?district=PUNE&scheme=PM_KISAN` filters correctly.
  5. `GET /recommendations?farmer_id=<id>` returns eligible and not-enrolled schemes.
- **Frontend Vitest E2E:** `src/__tests__/DashboardPage.test.tsx`
  1. MSW returns mock summary; all 4 KpiCards render.
  2. CoverageBarChart renders without crash with mock data.
  3. Loading spinner shown while fetch in-progress.
  4. Error banner shown when MSW returns 500.

### Done when
- All 5 backend + 4 frontend tests green.
- Dashboard page visible at `localhost:5173/dashboard` with mock data.

---

## Phase 10 – Officer Dashboard + Farmers Pages (Full UI)

**Branch:** `feature/phase-10-officer-ui`

### Goal
Build all five officer-facing pages: Dashboard (complete), Farmers list, Farmer 360 detail, Review Queue, and Flags & Exclusions tabs. Wire to real backend via `VITE_API_URL`.

### Files / modules created
```
frontend/src/
  pages/
    FarmersPage.tsx
    Farmer360Page.tsx
    ReviewQueuePage.tsx
    FlagsPage.tsx
  features/
    farmers/
      FarmerTable.tsx
      FilterBar.tsx
      Pagination.tsx
    farmer360/
      ProfileCard.tsx
      LinkedRecordsList.tsx
      EligibilityTable.tsx
      FlagList.tsx
    review/
      RecordCompare.tsx
      ScoreBadge.tsx
      ShapBar.tsx
      DecisionButtons.tsx
    flags/
      FlagTable.tsx
      ExclusionTable.tsx
      ExportButton.tsx
  hooks/
    useMatches.ts
    useFlags.ts
  api/
    matches.ts
    flags.ts
  __tests__/
    FarmersPage.test.tsx
    Farmer360Page.test.tsx
    ReviewQueuePage.test.tsx
    FlagsPage.test.tsx
```

### Tests
- **Frontend Vitest E2E:** (one test file per page)
  1. **FarmersPage:** search input triggers MSW `GET /farmers?q=Ramesh` → table renders rows; empty state shown on empty result.
  2. **Farmer360Page:** all sections (profile, linked records, eligibility, flags) render; flag shows "HIGH" badge.
  3. **ReviewQueuePage:** two records side-by-side; "Confirm" calls `POST /matches/{id}/decision`; success toast shown.
  4. **FlagsPage:** duplicate-alert tab renders; "Dismiss" calls `PATCH /flags/{id}`; Exclusions tab renders; ExportButton triggers CSV download.

### Done when
- All 4 Vitest tests green.
- All pages render at `localhost:5173` with mock data.
- Switching `VITE_API_URL` to real backend shows real data.

---

## Phase 11 – Review Queue & Match Decision Backend

**Branch:** `feature/phase-11-matches-api`

### Goal
Implement `GET /matches?decision=review`, `POST /matches/{id}/decision`, SHAP explanation, and `GET /farmers/{id}` (full Farmer 360 payload). Wire Review Queue and Farmer 360 to real API.

### Files / modules created
```
backend/app/
  api/routers/
    matches.py
    farmers.py
  services/
    match_service.py
  schemas/
    matches.py
    farmer.py             # FarmerDetail with all nested fields
  resolution/
    explainability.py     # top_shap_features(pair_features) -> list[ShapFeature]
```

### Tests
- **Backend pytest E2E:** `tests/phase_11/test_matches.py`
  1. `GET /matches?decision=review` returns only review-decision pairs.
  2. `POST /matches/{id}/decision {confirm}` → decision updated to `manual_link`, `audit_log` written.
  3. `POST /matches/{id}/decision {reject}` → decision updated to `no_match`.
  4. Non-officer token → 403.
  5. `GET /farmers/{id}` returns full payload: linked records, enrollments, flags, recommendations.
  6. `top_shap_features(features)` returns ≤ 4 `ShapFeature` objects with `feature`, `value`, `shap_value`.
- **Frontend Vitest:** (added to `ReviewQueuePage.test.tsx`)
  7. ShapBar renders SHAP features; bars proportional to `shap_value`.

### Done when
- All 7 tests green.
- Review Queue fully functional: officer confirms/rejects; audit_log written.

---

## Phase 12 – Farmer Portal Backend

**Branch:** `feature/phase-12-farmer-portal-backend`

### Goal
Implement all backend additions for Section 16: profile with completeness, scheme feed, form loader from YAML, autofill function, applications lifecycle, officer application inbox, and admin scheme-management endpoints.

### Files / modules created
```
backend/app/
  profiles/
    completeness.py
    profile_linker.py
  applications/
    form_loader.py
    autofill.py
    validators.py
  services/
    profile_service.py
    application_service.py
  api/routers/
    me.py
    applications.py
    schemes.py
  schemas/
    profile.py
    application.py
    scheme.py

eligibility/rules/schemes.yaml  # extended with domain, status, end_date, application_form
```

### Tests
- **Backend pytest E2E:** `tests/phase_12/test_farmer_portal.py`
  1. `POST /auth/register` → farmer user created, role=farmer.
  2. `PUT /me/profile` → profile saved; `completeness` in range 0–100.
  3. `GET /me/schemes?section=recommended` → only eligible, not-enrolled, opted-in-domain schemes.
  4. `POST /applications/prefill {scheme_id: PMFBY}` → `values` dict + `autofilled_keys` list.
  5. `POST /applications` submit → status `submitted`; duplicate check fires if already applied.
  6. `PATCH /applications/{id}/decision {status: approved}` (officer) → `enrollments` row created, `audit_log` written.
  7. Farmer cannot read another farmer's applications → 403.
  8. `autofill` unit: 4 autofill fields + 2 manual → returns 4 filled keys.

### Done when
- All 8 tests green.
- `/applications/prefill` returns correctly autofilled values.

---

## Phase 13 – Farmer Portal Frontend

**Branch:** `feature/phase-13-farmer-portal-frontend`

### Goal
Build all farmer-facing pages (Section 16.10): Register, 4-step Profile Wizard, Farmer Dashboard (scheme feed), Scheme Details, Apply page with Autofill, My Applications with status timeline, Settings, and the Officer Applications Inbox.

### Files / modules created
```
frontend/src/
  pages/
    FarmerDashboardPage.tsx
    ProfileWizardPage.tsx
    SchemeDetailPage.tsx
    ApplyPage.tsx
    MyApplicationsPage.tsx
    SettingsPage.tsx
    OfficerApplicationsPage.tsx
  features/
    profile/
      Step1Personal.tsx
      Step2Address.tsx
      Step3Land.tsx
      Step4Interests.tsx
      CompletenessMeter.tsx
    schemes/
      SchemeFeedCard.tsx
      SchemeFilterTabs.tsx
    apply/
      DynamicFormField.tsx
      AutofillBanner.tsx
    applications/
      StatusTimeline.tsx
  api/
    profile.ts
    applications.ts
    schemes.ts
  hooks/
    useProfile.ts
    useApplications.ts
    useSchemes.ts
  __tests__/
    ProfileWizardPage.test.tsx
    ApplyPage.test.tsx
    MyApplicationsPage.test.tsx
    OfficerApplicationsPage.test.tsx
```

### Tests
- **Frontend Vitest E2E:**
  1. **ProfileWizardPage:** Step 1 renders; filling required fields + "Next" advances to step 2; completeness updates; "Save" on step 4 calls `PUT /me/profile`.
  2. **ApplyPage:** "Autofill" pre-fills 4 fields with green highlight; 2 remaining empty; "Submit" disabled until all required filled; calls `POST /applications`.
  3. **MyApplicationsPage:** StatusTimeline shows all statuses; officer note rendered.
  4. **OfficerApplicationsPage:** table shows applications; "Approve" calls `PATCH /applications/{id}/decision`; success toast shown.

### Done when
- All 4 frontend tests green.
- Full farmer journey works in browser: Register → Profile → Schemes → Autofill Apply → Submit → Officer approves.

---

## Phase 14 – Email Notifications & Profile Linking

**Branch:** `feature/phase-14-notifications`

### Goal
Implement `notifications/sender.py` (EmailSender ABC, SmtpEmailSender, ConsoleEmailSender), Jinja2 templates, `NotificationService`, `email_log` deduplication, and `profile_linker.py`.

### Files / modules created
```
backend/app/
  notifications/
    sender.py
    templates/
      digest.html
      alert.html
      status.html
    digest_builder.py
  services/
    notification_service.py
  profiles/
    profile_linker.py      # reuses Phase 06-07 blocking + matcher
  api/routers/
    schemes.py             # publishing triggers send_scheme_alert()
  cli.py                   # python -m app.cli send_digest
```

### Tests
- **Backend pytest E2E:** `tests/phase_14/test_notifications.py`
  1. `ConsoleEmailSender.send()` captures output without raising.
  2. `send_weekly_digest()` with 2 opted-in farmers → `email_log` has 2 rows; same call again → 0 new rows (deduplication).
  3. `profile_linker` with matching AgriStack ID → `method=rule`, linked.
  4. Profile linker score ≥ 0.90 → linked to golden farmer.
  5. Profile linker score < 0.60 → creates new farmer row.
  6. `PATCH /applications/{id}/decision {approved}` → status email logged.

### Done when
- All 6 tests green.
- `python -m app.cli send_digest` runs and prints emails to console.
- MailHog captures emails in dev.

---

## Phase 15 – Evaluation, SHAP & Final Polish

**Branch:** `feature/phase-15-evaluation`

### Goal
Implement the evaluation notebook (precision, recall, F1, baselines, blocking metrics, threshold curve), the SHAP endpoint, CSV export polish, and final clean-up (error states, loading states, audit-log visibility, README update).

### Files / modules created
```
notebooks/
  01_eda.ipynb
  02_model_evaluation.ipynb
  03_blocking_metrics.ipynb

backend/app/
  api/routers/
    evaluation.py         # GET /evaluation/metrics (admin/officer)
  schemas/
    evaluation.py         # EvaluationMetrics

frontend/src/
  pages/
    EvaluationPage.tsx
  features/
    evaluation/
      MetricsTable.tsx
      PrecisionRecallChart.tsx
  __tests__/
    EvaluationPage.test.tsx
```

### Tests
- **Backend pytest E2E:** `tests/phase_15/test_evaluation.py`
  1. `GET /evaluation/metrics` (admin token) returns `f1`, `precision`, `recall`, `auto_link_rate`, `review_rate`.
  2. All metrics are floats in [0, 1].
  3. F1 > 0.90 on sample ground truth (regression guard).
  4. `top_shap_features` returns ≤ 4 items with `feature`, `value`, `shap_value`.
  5. Non-admin token → 403.
- **Frontend Vitest E2E:** `src/__tests__/EvaluationPage.test.tsx`
  1. Renders MetricsTable with F1, precision, recall from mock.
  2. PrecisionRecallChart renders without crash.
  3. Non-admin user → "Access denied".

### Done when
- All 5 backend + 3 frontend tests green.
- Evaluation notebook runs end-to-end without error.
- Full demo script (spec Section 15.2) can be executed in the browser.
- README updated with quick-start steps.
- `ruff`, `black --check`, `pytest`, `vitest`, `npm run build` all pass in CI.

---

## Cross-cutting decisions (apply to every phase)

| Concern | Decision |
|---------|----------|
| Type hints | Python: every function. TypeScript: strict mode. |
| File size | ≤ 250 lines per file. Function ≤ 30 lines. Split if over. |
| SQL | Only inside `repositories/`. Zero SQL in services or routers. |
| Business logic | Only in services and domain modules. None in routers. |
| Dependency wiring | Only in `api/deps.py`. Constructor injection everywhere else. |
| Secrets | `.env` only. Never in code or Git. Commit `.env.example`. |
| Naming | Python: `snake_case`. TypeScript: `camelCase`. Folder/file names: exactly as in spec. |
| Test DB | Separate `TEST_DATABASE_URL` in `.env`. Each suite creates + tears down its own schema. |
| Mock API | MSW (`mocks/handlers.ts`) for frontend tests until the real endpoint exists. One env flag to switch. |
| Commit style | Conventional Commits: `feat:`, `fix:`, `test:`, `docs:`, `refactor:`. |
| PR rule | One teammate review required. CI must be green before merge. |
