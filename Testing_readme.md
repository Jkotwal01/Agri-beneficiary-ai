# Master Testing Plan & Verification Guide: Agri Beneficiary AI

> **Target Audience:** Engineering Team, QA Engineers, Project Leads, and Client Stakeholders.  
> **Scope:** Full-stack verification of Frontend, Backend REST APIs, ML/Entity Resolution Pipeline, and Database Integrity across all three core user roles: **Admin**, **Officer**, and **Farmer**.  
> **Environment:** Real Data & Real Backend Execution (PostgreSQL + FastAPI + Vite/React + MailHog dev SMTP).

---

## Table of Contents
1. [Executive Summary & Objectives](#1-executive-summary--objectives)
2. [Role Architecture & Access Matrix](#2-role-architecture--access-matrix)
3. [Environment & Real-Data Preparation (Prerequisites)](#3-environment--real-data-preparation-prerequisites)
4. [Data Pipeline Execution & Staging](#4-data-pipeline-execution--staging)
5. [Role 1: Administrator Testing Plan](#5-role-1-administrator-testing-plan)
6. [Role 2: Government Officer Testing Plan](#6-role-2-government-officer-testing-plan)
7. [Role 3: Farmer (Client) Testing Plan](#7-role-3-farmer-client-testing-plan)
8. [Cross-Role Integrated End-to-End Scenarios](#8-cross-role-integrated-end-to-end-scenarios)
9. [Defect Register & Known Disconnects (Root Cause Analysis)](#9-defect-register--known-disconnects-root-cause-analysis)
10. [Test Execution Checklist & Sign-Off Matrix](#10-test-execution-checklist--sign-off-matrix)

---

## 1. Executive Summary & Objectives

The **Agri Beneficiary Intelligence System** is an AI-powered data platform designed to resolve identity fragmentation, eliminate duplicate welfare claims, and streamline welfare scheme distribution across disconnected agricultural schemes (PM-KISAN, PMFBY, KCC, NFSM, and AgriStack).

### Current Project Status
- **Codebase Completion:** ~95% across backend models, pipeline services, and React views.
- **Problem Statement:** Several modules fail or show empty states when connected to real data because:
  1. Core tables (`schemes`, `users`) lack automated database seed data.
  2. Edge cases in profile initialization return HTTP 404 instead of graceful defaults.
  3. Frontend buttons on specific officer views (e.g., Flags, Application notes) lack bound event handlers.
  4. Role-based routing distinctions between Admin and Officer need explicit verification.

### Core Objectives of this Plan
1. **Real-Data Testing:** Run tests against the actual 5-source synthetic datasets (`data/synthetic/*.csv`) loaded into PostgreSQL rather than in-memory mocks.
2. **Multi-Role Perspective:** Verify every screen and endpoint from the explicit viewpoint of:
   - **Administrator:** System ingestion, ML pipeline orchestration, scheme publishing, model metrics.
   - **Officer:** Beneficiary verification, fuzzy match resolution (0.60–0.90 uncertainty band), fraud flag investigation, application approval/rejection.
   - **Farmer:** Self-signup, profile completion, AI golden-record linking, scheme discovery, 1-click autofill application, lifecycle tracking.
3. **Traceability:** Provide clear inputs, reproduction steps, expected outputs, database queries, and fix recommendations.

---

## 2. Role Architecture & Access Matrix

| Feature / Endpoint | Farmer | Officer | Admin | Expected Access Behavior |
|---|:---:|:---:|:---:|---|
| **Public Sign-in / Sign-up** (`/login`, `/register`) | Yes | Yes | Yes | Public guest access; redirects to role dashboard |
| **Farmer Dashboard & Feed** (`/me`, `GET /me/schemes`) | **Yes** | No | No | Returns farmer-specific recommended schemes |
| **Profile Wizard** (`/me/profile`, `PUT /me/profile`) | **Yes** | No | No | 4-step wizard; calculates completeness; auto-links to golden record |
| **Autofill & Apply** (`/me/schemes/:code/apply`) | **Yes** | No | No | Prefills from profile; validates mandatory fields; submits application |
| **Application Tracking** (`/me/applications`) | **Yes** | No | No | Farmer sees only their own applications with status timeline |
| **Email Preferences** (`/me/settings`) | **Yes** | No | No | Toggles weekly digest opt-in |
| **Officer Dashboard** (`/dashboard`, `GET /reports/summary`) | No | **Yes** | **Yes** | Summary KPIs & Master Beneficiary table |
| **Review Queue** (`/dashboard/review`, `GET /matches`) | No | **Yes** | **Yes** | Fuzzy matching split-screen for confidence [0.60, 0.90] |
| **Rule Engine & Flags** (`/dashboard/flags`, `GET /flags`) | No | **Yes** | **Yes** | Investigates duplicate claims & exclusion violations |
| **Applications Inbox** (`/dashboard/applications`) | No | **Yes** | **Yes** | Approves/rejects farmer submissions; writes audit log |
| **Coverage & Reports** (`GET /reports/coverage`, `/reports/export`) | No | **Yes** | **Yes** | Aggregates data by district/village; exports CSV |
| **Resolution Evaluation** (`/dashboard/evaluation`, `GET /evaluation/metrics`) | No | No | **Yes** | Precision, recall, F1, reduction ratio, SHAP explainability |
| **Pipeline Triggering** (`POST /pipeline/*`) | No | No | **Yes** | Ingest, preprocess, resolve, evaluate |
| **Scheme Publishing** (`POST /schemes/:code/publish`) | No | No | **Yes** | Marks scheme active; dispatches alert emails |

---

## 3. Environment & Real-Data Preparation (Prerequisites)

To test with real data, mock modes must be disabled and all infrastructure components initialized.

### 3.1 Infrastructure Setup (PostgreSQL & MailHog)
Ensure `docker-compose.yml` is present in the repository root:

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:16
    container_name: agri_postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: agri
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  mailhog:
    image: mailhog/mailhog
    container_name: agri_mailhog
    ports:
      - "1025:1025"   # SMTP port
      - "8025:8025"   # Web UI for reading emails
volumes:
  pgdata:
```

Start the containers:
```powershell
docker compose up -d
```
Verify containers are running:
- PostgreSQL: `localhost:5432`
- MailHog Web UI: http://localhost:8025

---

### 3.2 Environment Configurations

#### 1. Backend (`backend/.env` and `.env` in root)
```ini
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/agri
TEST_DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/agri_test
JWT_SECRET=agri-test-secret-key-32chars-min!!
JWT_EXPIRE_MINUTES=480
MATCHER_PATH=models/matcher.joblib
AUTO_LINK_THRESHOLD=0.90
REVIEW_THRESHOLD=0.60
APP_BASE_URL=http://localhost:5173
EMAIL_BACKEND=smtp          # Set to smtp so outgoing emails appear in MailHog
EMAIL_FROM=no-reply@agri.gov.in
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
```

#### 2. Frontend (`frontend/.env`)
Ensure `frontend/.env` disables mocks and targets the real backend:
```ini
VITE_API_URL=http://localhost:8000
VITE_USE_MOCKS=false
```

---

### 3.3 Database Migrations & Seeding

#### Step 1: Run Alembic Migrations
```powershell
cd backend
alembic upgrade head
```

#### Step 2: Generate Synthetic Real-World Scheme Records
```powershell
python ../scripts/generate_synthetic_data.py
```
*Output: Generates realistic farmer records with transliteration variants, typos, shared land parcels, and mobile numbers across `agristack_farmers.csv`, `pmkisan.csv`, `pmfby.csv`, `nfsm.csv`, `kcc.csv`.*

#### Step 3: Seed Source Records
```powershell
python ../scripts/seed_db.py
```

#### Step 4: Master Seed for Schemes & Users (Crucial Fix for Real Testing)
Create and run a unified seed script `scripts/seed_master.py` to ensure core reference data exists:
```python
# scripts/seed_master.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.core.db import SessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.models.scheme import Scheme

def seed_master():
    db = SessionLocal()
    try:
        # 1. Seed Schemes
        schemes = [
            Scheme(code="PM_KISAN", name="PM-KISAN", domain="AGRICULTURE", description="Income support of Rs. 6000/yr for small & marginal farmers.", status="active", benefit_score=10),
            Scheme(code="PMFBY", name="PMFBY (Crop Insurance)", domain="INSURANCE", description="Pradhan Mantri Fasal Bima Yojana crop loss protection.", status="active", benefit_score=8),
            Scheme(code="KCC", name="Kisan Credit Card", domain="CREDIT", description="Concessional institutional credit for agriculture.", status="active", benefit_score=9),
            Scheme(code="NFSM", name="National Food Security Mission", domain="AGRICULTURE", description="Subsidized high-yield seeds and nutrient management.", status="active", benefit_score=6),
        ]
        for s in schemes:
            if not db.query(Scheme).filter(Scheme.code == s.code).first():
                db.add(s)

        # 2. Seed Default Test Accounts
        users = [
            User(email="admin@agri.gov.in", password_hash=hash_password("Admin@123"), role="admin"),
            User(email="officer@agri.gov.in", password_hash=hash_password("Officer@123"), role="officer"),
            User(email="farmer@agri.gov.in", password_hash=hash_password("Farmer@123"), role="farmer"),
        ]
        for u in users:
            if not db.query(User).filter(User.email == u.email).first():
                db.add(u)

        db.commit()
        print("[seed_master] Successfully seeded schemes and default role accounts.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_master()
```
Execute:
```powershell
python scripts/seed_master.py
```

---

## 4. Data Pipeline Execution & Staging

Before testing the frontend UI, trigger the 4-stage data pipeline to transform raw ingested data into resolved entities and fraud flags.

### Pipeline Execution Order

```
1. /pipeline/ingest (Raw CSVs -> source_records)
   │
   ▼
2. /pipeline/preprocess (Clean, normalize, phonetic keys -> clean_records)
   │
   ▼
3. /pipeline/resolve (Blocking -> Pair Scoring -> Clustering -> Golden Farmers & Review Pairs)
   │
   ▼
4. /pipeline/evaluate (Duplicate Rules -> Flags & Scheme Recommendations)
```

#### Step 1: Preprocess Records
- **Endpoint:** `POST http://localhost:8000/pipeline/preprocess`
- **Action:** Normalizes names, phone numbers, and computes Double Metaphone phonetic keys.
- **Verification Query:**
  ```sql
  SELECT count(*) FROM clean_records;
  -- Should match total rows in source_records
  ```

#### Step 2: Execute Identity Resolution & ML Clustering
- **Endpoint:** `POST http://localhost:8000/pipeline/resolve`
- **Action:** 
  - Runs `PhoneticVillageBlocker` to generate candidate pairs.
  - Scores pairs via `XGBoostPairMatcher` (or heuristic fallback).
  - Classifies pairs: Auto-link (>= 0.90), Review ([0.60, 0.90)), No match (< 0.60).
  - Clusters connected components into golden records in table `farmers`.
- **Verification Query:**
  ```sql
  SELECT count(*) FROM farmers;          -- Unique golden records
  SELECT count(*) FROM farmer_links;     -- Links from source records
  SELECT count(*) FROM match_candidates WHERE decision = 'review'; -- Review queue rows
  ```

#### Step 3: Evaluate Duplicate Claims & Scheme Recommendations
- **Endpoint:** `POST http://localhost:8000/pipeline/evaluate`
- **Action:** 
  - Detects duplicate claims, land parcel overclaims, and shared bank accounts.
  - Generates recommendations based on land size and crops.
- **Verification Query:**
  ```sql
  SELECT type, count(*) FROM flags GROUP BY type;
  SELECT count(*) FROM recommendations WHERE eligible = true;
  ```

---

## 5. Role 1: Administrator Testing Plan

### Perspective
The **Platform Administrator** oversees data governance, monitors machine learning resolution quality, triggers ingestion pipelines, manages schemes, and audits system-wide operational actions.

---

### Test Cases: Administrator

#### ADM-01: Admin Authentication & Guard Verification
- **Objective:** Verify admin login, JWT claims, and unauthorized route access.
- **Preconditions:** Admin seeded (`admin@agri.gov.in` / `Admin@123`).
- **Steps:**
  1. Open [http://localhost:5173/login](http://localhost:5173/login).
  2. Enter admin credentials and submit.
  3. Verify automatic redirection to `/dashboard`.
  4. Inspect `localStorage.getItem("agri_access_token")`.
  5. Attempt to navigate directly to farmer route `/me`.
- **Expected Outcome:** 
  - Login succeeds; JWT payload contains `"role": "admin"`.
  - Redirected to `/dashboard`.
  - Visiting `/me` redirects back to `/dashboard` (protected route RBAC guard).

#### ADM-02: Pipeline Ingestion & Orchestration Triggering
- **Objective:** Trigger ingestion and processing endpoints via API and verify background task execution.
- **Preconditions:** Server running; Admin JWT obtained.
- **Execution (PowerShell / cURL):**
  ```powershell
  $token = "<ADMIN_JWT_TOKEN>"
  Invoke-RestMethod -Uri "http://localhost:8000/pipeline/ingest" -Method Post -Headers @{ Authorization = "Bearer $token" }
  Invoke-RestMethod -Uri "http://localhost:8000/pipeline/preprocess" -Method Post -Headers @{ Authorization = "Bearer $token" }
  Invoke-RestMethod -Uri "http://localhost:8000/pipeline/resolve" -Method Post -Headers @{ Authorization = "Bearer $token" }
  Invoke-RestMethod -Uri "http://localhost:8000/pipeline/evaluate" -Method Post -Headers @{ Authorization = "Bearer $token" }
  ```
- **Expected Outcome:** All endpoints return HTTP 202 Accepted `{"status": "accepted"}`. Database tables populate asynchronously.

#### ADM-03: Machine Learning Model Evaluation & Metrics
- **Objective:** Verify resolution performance metrics and explainability graphs.
- **Preconditions:** Pipeline resolution executed; ground truth available.
- **Steps:**
  1. Login as Admin and navigate to `/dashboard/evaluation`.
  2. Verify that **MetricsTable** loads:
     - Total pairs compared
     - Precision (>= 0.85 expected)
     - Recall (>= 0.80 expected)
     - F1-Score (>= 0.82 expected)
     - Reduction Ratio (> 0.95 expected)
  3. Verify **PrecisionRecallChart** visualizes the harmonic mean curves properly.
- **Backend API Verification:**
  ```powershell
  Invoke-RestMethod -Uri "http://localhost:8000/evaluation/metrics" -Headers @{ Authorization = "Bearer $token" }
  ```
- **Expected Outcome:** Returns JSON object with numeric scores; UI displays green metrics cards without errors.

#### ADM-04: Scheme Management & Alert Email Broadcasting
- **Objective:** Publish an agricultural scheme and verify email dispatch to farmers.
- **Preconditions:** Schemes seeded; at least one farmer profile with `email_opt_in = true`.
- **Execution:**
  ```powershell
  Invoke-RestMethod -Uri "http://localhost:8000/schemes/PM_KISAN/publish" -Method Post -Headers @{ Authorization = "Bearer $token" }
  ```
- **Verification Steps:**
  1. Open MailHog UI at [http://localhost:8025](http://localhost:8025).
  2. Check inbox for subject line: *"New Scheme Alert: PM-KISAN"*.
  3. Verify recipient address matches opted-in farmers.
  4. Inspect `email_log` database table:
     ```sql
     SELECT * FROM email_log WHERE email_type = 'scheme_alert';
     ```
- **Expected Outcome:** Scheme status updates to `active`; email arrives in MailHog.

#### ADM-05: Audit Log Trail Verification
- **Objective:** Ensure all administrative and officer actions write immutable audit trail entries.
- **Verification Query:**
  ```sql
  SELECT al.id, u.email, al.action, al.entity, al.entity_id, al.at 
  FROM audit_log al
  JOIN users u ON u.id = al.user_id
  ORDER BY al.at DESC LIMIT 10;
  ```
- **Expected Outcome:** Entries logged for `match_decision`, `flag_status`, and `application_decision`.

---

## 6. Role 2: Government Officer Testing Plan

### Perspective
The **Government Verification Officer** audits the data, resolves borderline identity matches, investigates fraud flags, and processes submitted farmer scheme applications.

---

### Test Cases: Officer

#### OFF-01: Officer Portal Authentication
- **Objective:** Verify officer login and navigation.
- **Credentials:** `officer@agri.gov.in` / `Officer@123`.
- **Steps:**
  1. Navigate to `/login`, enter credentials, and log in.
  2. Verify landing on `/dashboard`.
  3. Verify sidebar navigation elements:
     - Dashboard (`/dashboard`)
     - Review Queue (`/dashboard/review`)
     - Rule Engine (`/dashboard/flags`)
     - Applications (`/dashboard/applications`)
     - Evaluation (`/dashboard/evaluation`)

#### OFF-02: Dashboard KPIs & Master Beneficiary Datagrid
- **Objective:** Verify aggregate metric cards and data table against real PostgreSQL records.
- **Steps:**
  1. Inspect Top Counters:
     - **Total Records:** Must match `count(*) FROM source_records`.
     - **Unique Farmers:** Must match `count(*) FROM farmers`.
     - **Open Flags:** Must match `count(*) FROM flags WHERE status = 'open'`.
     - **Exclusions:** Must match calculated non-eligible or flagged count.
  2. Test Datagrid:
     - Verify columns: ID, Name, Mobile, District/Village, Land (Ha), Category, Confidence, Status.
     - Verify status tags: `Golden` (confidence >= 0.90) in emerald vs `Review` in amber.

#### OFF-03: Fuzzy Matching Review Queue (Borderline Resolution)
- **Objective:** Manually verify and resolve candidate record pairs falling in the uncertainty band [0.60, 0.90).
- **Steps:**
  1. Click **Review Queue** in sidebar (`/dashboard/review`).
  2. Verify queue counter shows `Queue: 1 / N`.
  3. Inspect the Split-Pane comparison:
     - **Record A (Source 1):** Name, Father's Name, Mobile, District, Village, Survey No.
     - **Record B (Source 2):** Corresponding fields from second source.
  4. Inspect the **SHAP Feature Attribution**:
     - Check contribution bars (e.g. `name_jw: +0.34`, `same_mobile: +0.45`, `same_village: -0.12`).
  5. Click **Confirm Match (Merge)** button.
- **Expected Outcome:**
  - Candidate advances to next pair in queue.
  - Backend updates `match_candidates.decision = 'manual_link'`.
  - Database verification:
    ```sql
    SELECT decision, reviewed_by FROM match_candidates WHERE id = <match_id>;
    -- decision must be 'manual_link'
    ```

#### OFF-04: Rejecting Disconnected Match Pair
- **Objective:** Confirm rejection of a false match candidate pair.
- **Steps:**
  1. On `/dashboard/review`, locate a pair with differing fathers' names or distinct villages.
  2. Click **Reject (Different Farmers)**.
- **Expected Outcome:**
  - Backend updates `match_candidates.decision = 'no_match'`.
  - Records are separated into independent golden records.

#### OFF-05: Rule Engine & Fraud Flags Investigation
- **Objective:** Review rule engine flags and mark them investigated or dismissed.
- **Steps:**
  1. Navigate to `/dashboard/flags`.
  2. Verify list of active flags under **Active Engine Flags**:
     - `SAME_SCHEME_TWICE` (e.g., claiming PM-KISAN in two states)
     - `PARCEL_OVERCLAIM` (sum of claimed parcel shares > 100%)
     - `MUTUALLY_EXCLUSIVE`
     - `SHARED_BANK_ACCOUNT`
  3. Locate a flag and inspect target farmer name and reason text.
  4. Click **Dismiss** or **Investigate**.
- **Expected Outcome:** Flag status updates to `dismissed` or `confirmed` in backend; row updates dynamically.

#### OFF-06: Scheme Applications Review & Approval Workflow
- **Objective:** Review a submitted farmer application and approve it.
- **Preconditions:** A farmer has submitted an application for PM-KISAN (via Step 7).
- **Steps:**
  1. Navigate to `/dashboard/applications`.
  2. Verify submitted applications table shows: ID, Scheme Name, Status (`submitted`), Submission Date.
  3. Click **Approve** on the pending application.
- **Expected Outcome:**
  - Status badge changes to green `APPROVED`.
  - Backend creates a corresponding entry in `enrollments`:
    ```sql
    SELECT * FROM enrollments WHERE farmer_id = <farmer_id> AND scheme_id = <scheme_id>;
    ```
  - An approval confirmation email is dispatched to the farmer via MailHog.

#### OFF-07: Scheme Applications Rejection with Mandatory Officer Note
- **Objective:** Reject an ineligible application with an explanatory feedback note.
- **Steps:**
  1. On `/dashboard/applications`, locate a pending application.
  2. Click **Reject**.
  3. Enter officer rejection note: *"Total land holding exceeds maximum ceiling for marginal farmer subsidy."*
  4. Confirm rejection.
- **Expected Outcome:**
  - Status updates to `REJECTED`.
  - Backend updates `scheme_applications.officer_note` with the entered explanation.
  - Farmer's application view displays this note.

#### OFF-08: Exporting Reports & District Analytics
- **Objective:** Export CSV reports of system findings.
- **Steps:**
  1. Make API call or click export button:
     ```powershell
     Invoke-RestMethod -Uri "http://localhost:8000/reports/export?type=flags" -Headers @{ Authorization = "Bearer $token" } -OutFile "flags_export.csv"
     ```
  2. Open `flags_export.csv`.
- **Expected Outcome:** Valid CSV file containing all flagged records and reasons.

---

## 7. Role 3: Farmer (Client) Testing Plan

### Perspective
The **Farmer** represents the primary citizen beneficiary who signs up, builds a 4-step farm profile, discovers tailored schemes, applies via 1-click autofill, and tracks application approvals.

---

### Test Cases: Farmer

#### FAR-01: Farmer Self-Signup & Mobile Validation
- **Objective:** Test citizen registration workflow.
- **Steps:**
  1. Navigate to [http://localhost:5173/register](http://localhost:5173/register).
  2. Enter:
     - Email: `ramesh.farmer@example.com`
     - Password: `FarmerPassword123!`
     - Role: Select `Farmer`
  3. Submit the registration form.
- **Expected Outcome:**
  - HTTP 201 Created; JWT token stored in `localStorage`.
  - Automatically redirects to Farmer Home `/me`.

#### FAR-02: Zero-State Dashboard & Completeness Prompt
- **Objective:** Verify dashboard behavior when profile is not yet completed.
- **Steps:**
  1. As a newly registered farmer, inspect `/me`.
  2. Verify:
     - Welcome greeting: *"Welcome"*
     - Completeness banner: Meter shows `0%`
     - Call to Action: *"Build your profile to unlock scheme recommendations →"*
- **Expected Outcome:** No 404 crash; UI prompts user to complete their profile.

#### FAR-03: 4-Step Profile Wizard Completion
- **Objective:** Complete all steps of the profile wizard.
- **Steps:**
  1. Navigate to `/me/profile`.
  2. **Step 1 (Personal):**
     - Full Name: `Ramesh Chandra Kotwal`
     - Father's Name: `Suresh Kotwal`
     - Date of Birth: `1982-05-14`
     - Gender: `Male`
     - Mobile: `9876543210` (use a number matching one in `data/synthetic/pmkisan.csv` to test auto-linking)
     - Click *Next*.
  3. **Step 2 (Address):**
     - Village: `Sonapur`
     - Taluka: `Haveli`
     - District: `Pune`
     - State: `Maharashtra`
     - Pincode: `411028`
     - Click *Next*.
  4. **Step 3 (Land & Agriculture):**
     - Total Land (Ha): `1.5`
     - Ownership Type: `Owner`
     - Main Crops: Select `wheat`, `soybean`
     - Irrigation: `Well / Borewell`
     - Click *Next*.
  5. **Step 4 (Interests & Consent):**
     - Domain Interests: Check `AGRICULTURE`, `CREDIT`, `INSURANCE`
     - Weekly Digest Opt-in: Check `Yes`
     - Click **Save & Finish**.
- **Expected Outcome:**
  - Profile saved via `PUT /me/profile`.
  - Completeness updates to `100%`.
  - Redirects to `/me`.

#### FAR-04: AI Golden Record Auto-Linking Verification
- **Objective:** Verify whether the self-declared profile matches an existing golden record.
- **Verification Query:**
  ```sql
  SELECT fp.user_id, fp.full_name, fp.mobile, fp.farmer_id, f.name AS golden_name, f.confidence
  FROM farmer_profiles fp
  LEFT JOIN farmers f ON f.id = fp.farmer_id
  WHERE fp.mobile = '9876543210';
  ```
- **Expected Outcome:** `fp.farmer_id` is populated; profile links to existing golden record.

#### FAR-05: Dynamic Scheme Feed & Recommendation Verification
- **Objective:** Ensure recommended schemes match the farmer's land size and crops.
- **Steps:**
  1. On `/me`, inspect the **Recommended for you** feed.
  2. Verify:
     - **PM-KISAN:** Shown (Land 1.5 Ha <= 2.0 Ha requirement satisfied).
     - **PMFBY:** Shown (Crops include `wheat` which is covered under PMFBY insurance).
     - **KCC:** Shown (Credit domain opted in).
  3. Click on **PM-KISAN** card to view Scheme Details (`/me/schemes/PM_KISAN`).
- **Expected Outcome:** Cards display scheme name, domain tag, and "Apply Now" button.

#### FAR-06: 1-Click Autofill Application
- **Objective:** Verify profile data pre-populates application form fields.
- **Steps:**
  1. From Scheme Details, click **Apply Now** (`/me/schemes/PM_KISAN/apply`).
  2. Inspect the **Autofill Banner**:
     - Verifies: *"Autofilled 4 fields from your profile"*.
  3. Check prefilled values:
     - Full Name: `Ramesh Chandra Kotwal` (prefilled)
     - Mobile: `9876543210` (prefilled)
     - Total Land: `1.5` (prefilled)
  4. Verify un-autofilled mandatory fields:
     - Bank Name: enter `State Bank of India`
     - Self Declaration Accepted: toggle checkbox to `Checked`
  5. Click **Submit Application**.
- **Expected Outcome:**
  - Form validates successfully.
  - HTTP 201 Created via `POST /applications`.
  - User redirected to `/me/applications`.

#### FAR-07: Application Lifecycle & Status Timeline Tracking
- **Objective:** Monitor application progress through various officer decision stages.
- **Steps:**
  1. Navigate to `/me/applications`.
  2. Verify status timeline indicates `Submitted`.
  3. Switch browser session to Officer and mark the application as `Approved` (via Test Case OFF-06).
  4. Refresh `/me/applications` as Farmer.
- **Expected Outcome:**
  - Status timeline advances to `Approved`.
  - Officer note (if any) is displayed inside a highlighted feedback card.

#### FAR-08: Notification Preferences & Weekly Digest Delivery
- **Objective:** Verify email settings toggle and digest generation.
- **Steps:**
  1. Navigate to `/me/settings`.
  2. Toggle **Weekly scheme digest email** off, then on again.
  3. Confirm green indicator: *"Preference saved."*
  4. Trigger digest CLI command from backend:
     ```powershell
     cd backend
     python -m app.cli send_digest
     ```
  5. Check MailHog (http://localhost:8025) for digest email.
- **Expected Outcome:** Digest email received with list of active matching schemes.

---

## 8. Cross-Role Integrated End-to-End Scenarios

### Scenario A: Ingestion to Golden Record to Borderline Review
1. **Admin** executes preprocessing and resolution pipeline on ingested scheme datasets.
2. Pair with match confidence 0.74 (borderline name variation) is saved to `match_candidates` with decision `review`.
3. **Officer** opens `/dashboard/review`, inspects side-by-side records and SHAP features, and clicks **Confirm Match**.
4. Entity resolution consolidates records into a single Golden Record in table `farmers`.
5. **Farmer** registers with matching mobile/name. System runs profile linking and attaches profile to the newly confirmed golden record.
6. Farmer receives verified badge on their dashboard.

---

### Scenario B: Scheme Publishing to 1-Click Autofill to Benefit Approval
1. **Admin** triggers `POST /schemes/PM_KISAN/publish`.
2. System identifies eligible opted-in farmers and sends scheme alert emails via MailHog.
3. **Farmer** logs into `/me`, sees PM-KISAN recommended, and clicks **Apply Now**.
4. Application form autofills 4 fields directly from farmer profile (`/applications/prefill`).
5. Farmer completes remaining bank details and submits application.
6. **Officer** opens `/dashboard/applications`, verifies application details, and clicks **Approve**.
7. Backend inserts row into `enrollments` and dispatches approval email.
8. Farmer visits `/me/applications` and sees status updated to `Approved`.

---

### Scenario C: Duplicate Welfare Claim Detection & Prevention
1. Ineligible farmer attempts to register and submit a duplicate claim for PM-KISAN despite already receiving benefits under another record.
2. System executes `/pipeline/evaluate` rule engine checks: `SameSchemeTwice` flags the duplicate.
3. System logs high-severity flag in `flags` table.
4. **Officer** inspects `/dashboard/flags`, investigates the flag, and rejects the fraudulent application with note *"Duplicate claim identified under linked Aadhaar/bank account"*.
5. Audit log records officer's rejection decision.

---

## 9. Defect Register & Known Disconnects (Root Cause Analysis)

During real-data audit, the following technical disconnects were identified. Each item includes the root cause and required fix.

| Defect ID | Severity | Module / Location | Root Cause | Required Code Fix |
|---|---|---|---|---|
| **DEF-01** | **CRITICAL** | Backend Database / `scripts/seed_db.py` | The database seed script only populates `source_records`. Table `schemes` and table `users` remain empty in a clean database, causing `/schemes`, `/me/schemes`, and login to fail. | Create `scripts/seed_master.py` to insert standard schemes (`PM_KISAN`, `PMFBY`, `KCC`, `NFSM`) and default role users (`admin`, `officer`, `farmer`). |
| **DEF-02** | **CRITICAL** | Backend `/me/profile` & `/me/schemes` (`app/api/routers/me.py`) | Function `_get_or_create_profile` throws HTTP 404 when profile is not yet created. Newly registered farmers visiting `/me` immediately receive a red 404 error banner. | Update `_get_or_create_profile` to either return an empty profile schema or make frontend hooks gracefully treat 404 as `profile = null` without error. |
| **DEF-03** | **HIGH** | Frontend Flags Page (`frontend/src/pages/FlagsPage.tsx`) | The "Dismiss" and "Investigate" buttons in the active flags list have **no `onClick` handlers**. The visual rule builder on the left has un-wired static form inputs. | Attach `onClick={() => handleUpdateStatus(flag.id, 'dismissed')}` calling `PATCH /flags/{id}`. |
| **DEF-04** | **HIGH** | Frontend Officer Applications (`frontend/src/pages/OfficerApplicationsPage.tsx`) | The "Reject" button calls `handleDecision(app.id, "rejected")` without prompting the officer for an explanatory note, leaving `officer_note` null. | Add a rejection modal / input dialog where the officer inputs the reason before dispatching the `PATCH` request. |
| **DEF-05** | **MEDIUM** | Frontend Farmer Layout (`frontend/src/layouts/FarmerLayout.tsx`) | The sidebar navigation lacks a direct link to **Profile** (`/me/profile`). Once a farmer reaches 100% profile completeness, the prompt on the dashboard disappears, leaving no way to re-edit profile. | Add `{ name: "My Profile", to: "/me/profile", icon: User }` to `navItems` in `FarmerLayout.tsx`. |
| **DEF-06** | **MEDIUM** | Frontend Register Page (`frontend/src/pages/RegisterPage.tsx`) | The role dropdown only contains `Farmer` and `Officer`. There is no way to create an Admin account from UI. | Allow role selection or document that Admin accounts must be created via seed scripts / API. |
| **DEF-07** | **MEDIUM** | Root Repo Infra | `docker-compose.yml` was referenced in the spec and `README.md` but was missing from root workspace. | Ensure `docker-compose.yml` is committed to the repository root. |
| **DEF-08** | **LOW** | Frontend Evaluation Page (`frontend/src/pages/EvaluationPage.tsx`) | Evaluation tab is visible in sidebar to both Officer and Admin, but `GET /evaluation/metrics` backend dependency enforces `require_role("admin")`. Officers clicking it see "Access denied". | Either allow officers read-only access to evaluation metrics or hide the sidebar link when `role === "officer"`. |

---

## 10. Test Execution Checklist & Sign-Off Matrix

Use this checklist during manual or automated test execution. Mark each test as **PASS**, **FAIL**, or **BLOCKED**.

### 10.1 System Setup & Data Pipeline
- [ ] **TC-SYS-01:** PostgreSQL and MailHog Docker containers start cleanly.
- [ ] **TC-SYS-02:** Alembic migrations apply schema without errors (`alembic upgrade head`).
- [ ] **TC-SYS-03:** Synthetic data generated (`generate_synthetic_data.py`).
- [ ] **TC-SYS-04:** Source records, schemes, and users seeded into database.
- [ ] **TC-SYS-05:** Ingestion & Preprocessing pipelines execute (`clean_records` populated).
- [ ] **TC-SYS-06:** Identity Resolution executes (`farmers` golden records & `match_candidates` generated).
- [ ] **TC-SYS-07:** Duplicate & Eligibility Engine executes (`flags` & `recommendations` generated).

### 10.2 Role: Administrator
- [ ] **TC-ADM-01:** Admin login succeeds; redirects to `/dashboard`.
- [ ] **TC-ADM-02:** Admin restricted from farmer-only routes (`/me` redirects to `/dashboard`).
- [ ] **TC-ADM-03:** Resolution Evaluation view displays precision, recall, F1, and curves.
- [ ] **TC-ADM-04:** Triggering `POST /schemes/{code}/publish` marks scheme active and dispatches MailHog alert email.
- [ ] **TC-ADM-05:** Audit log table records administrative actions.

### 10.3 Role: Government Officer
- [ ] **TC-OFF-01:** Officer login succeeds; redirects to `/dashboard`.
- [ ] **TC-OFF-02:** Summary counters (Total Records, Unique Farmers, Flags, Exclusions) match DB counts.
- [ ] **TC-OFF-03:** Master Beneficiary Datagrid loads golden records with confidence scores.
- [ ] **TC-OFF-04:** Review Queue displays borderline candidate pairs with SHAP feature explanations.
- [ ] **TC-OFF-05:** Confirm Match merges pair into golden record and writes audit log.
- [ ] **TC-OFF-06:** Reject Match marks pair `no_match`.
- [ ] **TC-OFF-07:** Active Flags view shows duplicate claims and overclaims.
- [ ] **TC-OFF-08:** Officer inbox displays submitted scheme applications.
- [ ] **TC-OFF-09:** Approving application creates `enrollments` record and sends email.
- [ ] **TC-OFF-10:** Rejecting application stores officer note and updates status.

### 10.4 Role: Farmer (Client)
- [ ] **TC-FAR-01:** Farmer registration creates user account with role `farmer`.
- [ ] **TC-FAR-02:** Login redirects to Farmer Portal (`/me`).
- [ ] **TC-FAR-03:** Initial dashboard shows 0% completeness prompt without 404 error.
- [ ] **TC-FAR-04:** Step 1 (Personal) saves full name, father's name, DOB, and mobile.
- [ ] **TC-FAR-05:** Step 2 (Address) saves village, taluka, district, and pincode.
- [ ] **TC-FAR-06:** Step 3 (Land) saves land area and selected crops.
- [ ] **TC-FAR-07:** Step 4 (Interests) saves domain preferences and opt-in flag.
- [ ] **TC-FAR-08:** Saving profile calculates completeness to 100%.
- [ ] **TC-FAR-09:** AI profile linker connects farmer to existing golden record.
- [ ] **TC-FAR-10:** Recommended scheme feed displays eligible schemes based on land and crops.
- [ ] **TC-FAR-11:** Scheme Detail page loads correct scheme description and "Apply Now" button.
- [ ] **TC-FAR-12:** 1-Click Autofill populates application form with profile data.
- [ ] **TC-FAR-13:** Submitting application sends form data and redirects to `/me/applications`.
- [ ] **TC-FAR-14:** My Applications timeline displays `Submitted` -> `Under Review` -> `Approved` / `Rejected`.
- [ ] **TC-FAR-15:** Officer feedback note appears on rejected application.
- [ ] **TC-FAR-16:** Weekly digest toggle updates opt-in setting in database.

---

### Verification Sign-Off Table

| Test Suite | Total Tests | Passed | Failed | Blocked | Tester Name | Sign-Off Date |
|---|:---:|:---:|:---:|:---:|---|---|
| Infrastructure & Pipeline | 7 | | | | | |
| Role: Administrator | 5 | | | | | |
| Role: Government Officer | 10 | | | | | |
| Role: Farmer | 16 | | | | | |
| Cross-Role Scenarios | 3 | | | | | |
| **Total** | **41** | | | | | |
