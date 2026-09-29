# AI-Powered Integrated Beneficiary Intelligence System for Agricultural Welfare Schemes

**Implementation specification (written to be fed to an AI coding assistant).**
Stack: React (Vite, TypeScript) · FastAPI (Python 3.11) · PostgreSQL · scikit-learn / XGBoost.
Users: `admin`, `officer`, `farmer`. Team: 3 members, one monorepo.

## 0. How to Use This File With an AI Coding Assistant

**Context for the AI.** This file is the single source of truth for the project. It describes the goal, architecture, database, modules, API, frontend, team rules and build order. Generate code that follows it.

**Rules the AI must follow**

1. **Do not over-engineer.** Anything listed in Section 1.1 under "SKIP" must not be added (no microservices, Kafka, Celery, Neo4j, deep learning, Kubernetes).
2. **Respect the layers:** `router → service → repository → database`. Domain modules (ingestion, preprocessing, resolution, eligibility, duplicate rules) are pure Python with no database access. No SQL outside `repositories/`. No business logic in routers.
3. **Follow SOLID as described in Section 7.2.** Inject dependencies through constructors and wire them only in `api/deps.py`. Extend by adding files (new adapter, new rule class, new YAML block), not by editing existing ones.
4. **Build one module at a time,** in the order of Appendix A, and ship unit tests with each module (pytest).
5. **Use the exact table names, column names, endpoint paths and folder names in this file.** If something is missing or ambiguous, ask before inventing.
6. **Data is synthetic** (Section 4). Never store full Aadhaar or full bank account numbers.
7. **Scheme rules are illustrative.** Keep them in `schemes.yaml`, never hard-coded.
8. **Code style:** Python type hints everywhere, Ruff + Black, functions under about 30 lines, files under about 250 lines. TypeScript strict mode, ESLint + Prettier. Config through `.env`.
9. If you are helping **one team member**, only touch the folders that member owns (Sections 11.1 and 16.12). Agree on interfaces (tables + OpenAPI) instead of editing another member's folder.
10. Labels "Member A/B/C" only describe ownership. They do not change how the code is written.

**Fixed technical choices:** Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2.0 (sync), Alembic, PostgreSQL 16, pandas, RapidFuzz, jellyfish, scikit-learn, XGBoost, NetworkX, PyYAML, Jinja2, pytest. Frontend: React + Vite + TypeScript, React Router, TanStack Query, axios, Tailwind CSS, Recharts.

## Contents

- [1. Project at a Glance](#1-project-at-a-glance)
- [2. Technology Stack](#2-technology-stack)
- [3. System Architecture](#3-system-architecture)
- [4. Data Strategy (Hypothetical but Realistic)](#4-data-strategy-hypothetical-but-realistic)
- [5. Database Design (PostgreSQL)](#5-database-design-postgresql)
- [6. Module-by-Module Implementation Flow](#6-module-by-module-implementation-flow)
- [7. Backend Code Structure and SOLID Principles](#7-backend-code-structure-and-solid-principles)
- [8. REST API Design (Contract Between Backend and Frontend)](#8-rest-api-design-contract-between-backend-and-frontend)
- [9. Frontend Design (React)](#9-frontend-design-react)
- [10. ML Evaluation and Explainability](#10-ml-evaluation-and-explainability)
- [11. Team Collaboration Plan (3 Members)](#11-team-collaboration-plan-3-members)
- [12. Timeline Mapped to Your Synopsis Steps](#12-timeline-mapped-to-your-synopsis-steps)
- [13. Testing Strategy](#13-testing-strategy)
- [14. Setup and Run (README Quick Start)](#14-setup-and-run-readme-quick-start)
- [15. Risks and Viva Demo Script](#15-risks-and-viva-demo-script)
- [16. Farmer Portal – The Third Role (New)](#16-farmer-portal--the-third-role-new)
- [Appendix A – Build Order and Prompt Sequence](#appendix-a--build-order-and-prompt-sequence)
- [Appendix B – Dependencies, Environment and Docker](#appendix-b--dependencies-environment-and-docker)

## 1. Project at a Glance

**The problem.** Every agricultural welfare scheme (PM-KISAN, PMFBY, KCC, NFSM, state subsidies) keeps its own farmer list. The same farmer appears as “Ramesh Kotwal”, “Kotwal Ramesh S.” and “R. Kotval” in different lists. The result: duplicate subsidies, eligible farmers who never get a benefit, and slow manual verification.

**Our solution in one paragraph.** We build a web platform that (1) loads farmer records from several scheme databases, (2) cleans them, (3) uses fuzzy matching plus a small ML classifier to decide which records are the same real farmer, (4) merges each group into one “golden record”, (5) runs a rule engine to find duplicate claims, eligible schemes and excluded farmers, and (6) shows everything on a dashboard where a government officer can verify or reject the system’s findings. Farmers get their own **Farmer Portal** (Section 16): they build a profile once, receive matching scheme suggestions by email, and apply with an Autofill button.

### 1.1 What we build vs. what we deliberately skip

The biggest risk for a 3-person BE team is over-engineering. The table below is our scope contract: if it is in the “skip” column, nobody adds it without the whole team agreeing.

| We BUILD (core) | We SKIP (not needed for a strong BE project) |
|---|---|
| One FastAPI backend (modular monolith) | Microservices, Kafka, Celery, Kubernetes |
| One PostgreSQL database | Separate NoSQL / graph database (Neo4j). The “identity graph” is just linked tables |
| Fuzzy matching + XGBoost pair classifier | Deep learning, transformers, graph neural networks |
| Rule engine driven by a YAML file | Hard-coded if/else per scheme; complex ML for eligibility |
| React app: officer dashboard **and Farmer Portal** (profile, autofill apply, email suggestions, Section 16) | Real-time streaming, mobile app, SMS/WhatsApp, document OCR, payment gateway |
| Synthetic data with known ground truth | Real Aadhaar / AgriStack API access (not available to students) |
| Docker Compose for PostgreSQL (plus optional MailHog for the email demo) | Cloud deployment, CI/CD pipelines beyond a simple test workflow |

## 2. Technology Stack

Everything below matches what your synopsis already lists. We only made the choices concrete.

| Layer | Choice | Why this choice |
|---|---|---|
| Frontend | React + Vite + TypeScript, React Router, TanStack Query, Tailwind CSS, Recharts | Team already knows React. Vite is simpler than Next.js because we need no SEO or server rendering. **If the team prefers Next.js, the page and folder structure in Section 9 stays identical.** |
| Backend | Python 3.11, FastAPI, Pydantic, SQLAlchemy 2.0, Alembic | FastAPI generates OpenAPI docs automatically, which becomes our frontend-backend contract. Alembic keeps 3 people’s schema changes in sync. |
| Database | PostgreSQL only | Data is relational (farmers, records, links, flags). JSONB columns store raw source rows, so no separate NoSQL store is needed. |
| Matching / ML | pandas, RapidFuzz, jellyfish, scikit-learn, XGBoost, joblib, NetworkX | RapidFuzz gives fast string similarity; jellyfish gives phonetic codes; XGBoost scores pairs; NetworkX finds connected groups. |
| Rules | YAML file + a small Python evaluator | Adding or changing a scheme means editing YAML, not code. |
| Explainability | SHAP (optional, on the match model) | Your reference list already cites SHAP and XAI. One SHAP bar chart in the review screen is enough. |
| Auth | JWT login, three roles: `admin`, `officer`, `farmer` | Simple, standard, covers government verification and the farmer portal. |
| Email | Jinja2 templates, Python `smtplib` (any SMTP), MailHog/Mailtrap for dev, cron or APScheduler for the weekly job | No queue or third-party marketing tool needed. |
| Testing / tools | pytest, Postman, ESLint + Prettier, Ruff + Black, pre-commit | Same quality bar for every teammate. |
| Dev environment | VS Code, Git + GitHub, Docker Compose (PostgreSQL), Jupyter | One `docker compose up` gives every member the same database. |

## 3. System Architecture

```mermaid
flowchart LR
  FE["React app<br/>Dashboard, Review Queue, Farmer 360<br/>(axios + React Query)"] -->|REST/JSON| API
  subgraph BE["FastAPI backend (one deployable app)"]
    API["API layer: routers + Pydantic schemas + auth"] --> SVC["Service layer: one use-case service per module"]
    SVC --> DOM["Domain modules: ingestion, preprocessing, resolution (ML), eligibility, duplicate rules"]
    SVC --> REPO["Repository layer: SQLAlchemy queries only"]
    DOM --> REPO
  end
  REPO --> DB[("PostgreSQL")]
  SVC -.-> FILES["Files: synthetic CSVs, schemes.yaml, matcher.joblib"]
```

*Figure 1 – Layered architecture. One backend, one database, one frontend.*

### 3.1 The four backend layers (and their single job)

| Layer | Job | Must NOT do |
|---|---|---|
| API (routers) | Receive HTTP request, validate with Pydantic, call one service, return JSON | No business logic, no SQL |
| Service | One use-case per method, e.g. `ResolutionService.run()`; coordinates modules and repositories | No HTTP objects, no raw SQL |
| Domain modules | Pure Python logic: normalizers, blocking, feature builder, rule engine | No database access, so they are trivial to unit-test |
| Repository | All database reads and writes for one table group | No business rules |

### 3.2 End-to-end data flow

```mermaid
flowchart LR
  subgraph A["Identity pipeline - Member A"]
    S1["1 Ingest"] --> S2["2 Clean"] --> S3["3 Block"] --> S4["4 Score (features + XGBoost)"] --> S5["5 Decide: auto-link / review / no-match"] --> S6["6 Merge: golden record"]
  end
  subgraph B["Rules and insights - Member B"]
    S7["7 Duplicates"] --> S8["8 Eligibility (YAML)"] --> S9["9 Gaps: recommend + exclusion"]
  end
  subgraph C["Dashboard - Member C"]
    S10["10 Verify (officer)"] --> S11["11 Reports"]
  end
  S6 --> S7
  S9 --> S10
```

*Figure 2 – The 11 steps of your block diagram grouped into 3 ownership areas.*

Steps 1–6 produce the **golden farmer table**. Steps 7–9 read that table and produce **flags and recommendations**. Steps 10–11 are UI and reporting on top of those tables. Every stage reads from and writes to PostgreSQL, so a teammate can work on their stage by only knowing the table contracts in Section 5.

## 4. Data Strategy (Hypothetical but Realistic)

Real AgriStack and scheme databases are not accessible to students. We therefore **generate synthetic data with known ground truth**. This is actually better for an ML project because we can measure precision and recall exactly.

### 4.1 Source systems we simulate

| Source file | Simulates | Typical fields |
|---|---|---|
| `agristack_farmers.csv` | AgriStack Farmer Registry | farmer_id (sometimes missing), name, father_name, dob, gender, mobile, village_code, district_code |
| `pmkisan.csv` | PM-KISAN | beneficiary_no, name, father_name, mobile, bank_acct_last4, village, district, land_ha |
| `pmfby.csv` | PMFBY crop insurance | policy_no, name, village, survey_no, crop, season, area_ha, bank_acct_last4 |
| `nfsm.csv` | NFSM subsidy | app_id, name, mobile, survey_no, crop, seed_subsidy_amt, season |
| `kcc.csv` | Kisan Credit Card | card_no, name, dob, mobile, village, land_ha, credit_limit |

### 4.2 How the generator works (`scripts/generate_synthetic_data.py`)

1. Create **5,000 “true” farmers** with Faker (Indian locale) plus a Marathi/Hindi name list. Each gets a hidden `true_farmer_id`, land parcels and crops.
2. Randomly enrol each true farmer in 1–4 schemes. This yields roughly 12,000 source records.
3. **Inject realistic noise** into each copy: spelling variants (Kotwal / Kotval), initials (“Ramesh S.”), swapped first/last name, missing mobile, different village spelling, typo in one digit, blank AgriStack ID.
4. Plant known problems: 3% duplicate enrolments in the same scheme, 2% same-parcel double claims, 1% shared bank account across different farmers.
5. Save CSVs in `data/synthetic/`. Save the hidden mapping `ground_truth.csv` **separately**. It is used only for training and evaluation, never by the pipeline itself.

> **Privacy rule.** Never store a real or synthetic-looking full Aadhaar number. Keep only a masked value or last 4 digits. State this in your report: it shows awareness of the DPDP Act, and examiners like it.

## 5. Database Design (PostgreSQL)

Eleven core tables plus three farmer-portal tables (Section 16.8). The pipeline (Member A) writes the record, match and farmer tables; the API (Member B) writes flags, decisions, users and the audit log.

| Table | Purpose | Key columns |
|---|---|---|
| `source_records` | Raw rows exactly as received | id, source_name, source_row_id, raw_json (JSONB), loaded_at |
| `clean_records` | Normalized version of each raw row | id, source_record_id (FK), name_norm, father_norm, name_phonetic, mobile10, village_code, district_code, dob, survey_no, bank_last4, land_ha, crop, season |
| `match_candidates` | Scored record pairs | id, record_a, record_b, score, decision (auto_link / review / no_match), features_json, reviewed_by, reviewed_at |
| `farmers` | **Golden record**, one row per real farmer | id, name, father_name, dob, mobile, village_code, district_code, total_land_ha, category (marginal/small/other), confidence |
| `farmer_links` | Which clean record belongs to which farmer | farmer_id (FK), clean_record_id (FK), method (rule/model/manual), score |
| `land_parcels` | Parcels per farmer | id, farmer_id, village_code, survey_no, area_ha |
| `schemes` | Scheme master | id, code, name, description, benefit_score |
| `enrollments` | Farmer ↔ scheme participation | id, farmer_id, scheme_id, season, amount, source_record_id |
| `flags` | Duplicate / fraud / exclusion alerts | id, farmer_id, type, severity, reason, status (open / confirmed / dismissed), created_at, resolved_by |
| `recommendations` | Eligibility outcome per farmer per scheme | farmer_id, scheme_id, eligible (bool), reasons_json, already_enrolled (bool), priority |
| `users` and `audit_log` | Login accounts and who-did-what trail | users(id, email, password_hash, role: admin / officer / farmer); audit_log(id, user_id, action, entity, entity_id, at) |
| `farmer_profiles`, `scheme_applications`, `email_log` | **Farmer portal tables** (Section 16.8) | Profile fields, application form_data (JSONB), email history |

**Indexes that matter:** `clean_records(district_code, name_phonetic)`, `clean_records(mobile10)`, `clean_records(village_code, survey_no)`, `farmer_links(farmer_id)`, `flags(status, type)`. These make blocking fast without any extra infrastructure.

**Why not NoSQL?** Nothing here needs flexible schemas at scale. The only semi-structured data is the raw source row, and a JSONB column handles that.

## 6. Module-by-Module Implementation Flow

Each module has: **input → what it does → output → owner**. Build them in this order; each one only depends on the ones before it.

### Module 1 – Ingestion (Step 1: Data Collection)   [Member A]

- **Input:** CSV/Excel files in `data/synthetic/`.
- **What it does:** one adapter class per source reads the file and converts each row to a common `RawRecord` dictionary, then stores it in `source_records` with the untouched row in `raw_json`.
- **Output:** rows in `source_records`.

```python
# ingestion/base.py
from abc import ABC, abstractmethod
from typing import Iterable

class SourceAdapter(ABC):
    source_name: str

    @abstractmethod
    def read(self, path: str) -> Iterable[dict]:
        """Yield one dict per source row using the COMMON field names."""

# ingestion/adapters/pmfby.py
class PmfbyAdapter(SourceAdapter):
    source_name = "pmfby"
    COLUMN_MAP = {"Farmer Name": "name", "Village": "village", "Survey No": "survey_no"}

    def read(self, path):
        for row in pd.read_csv(path).to_dict("records"):
            yield {new: row.get(old) for old, new in self.COLUMN_MAP.items()}
```

A new source = one new adapter file registered in a dictionary. Nothing else changes.

### Module 2 – Preprocessing (Step 2: Data Preprocessing)   [Member A]

Small, single-purpose functions in `preprocessing/normalizers.py`. Each is pure (no database) and has 3–5 unit tests.

| Function | Rule |
|---|---|
| `normalize_name` | lowercase, remove honorifics (Shri, Smt, Mr), remove punctuation, collapse spaces, fold common transliteration variants (w↔v, aa→a, ee→i) |
| `phonetic_key` | Double Metaphone of the first name token (jellyfish) so “Kotwal” and “Kotval” share a key |
| `normalize_mobile` | keep last 10 digits; set invalid numbers to null |
| `normalize_village` | map spelling to an LGD-style `village_code` using a small lookup CSV; unknown → fuzzy nearest match |
| `parse_dob` | accept several date formats; keep only birth year if the day/month is unreliable |
| `fill_missing` | never invent values. Leave null and let the feature builder treat “missing” as neutral |

Output: one `clean_records` row per `source_records` row.

### Module 3 – Farmer Identity Resolution (Step 3)   [Member A – the core of the project]

This is the part that makes the project “AI”. It has five small stages, each a separate file in `resolution/`.

#### Stage 1 – Blocking (`blocking.py`)

Comparing every record with every other one is 12,000² = 144 million pairs. Blocking only compares records that share at least one cheap key:

- same `district_code` **and** same `name_phonetic`, or
- same `mobile10`, or
- same `village_code` **and** same `survey_no`.

This typically drops the candidate pairs to a few hundred thousand, which runs in seconds in pandas.

#### Stage 2 – Pair features (`features.py`)

For each candidate pair compute a fixed feature vector:

| Feature | How |
|---|---|
| `name_jw`, `name_token_sort` | Jaro-Winkler and token-sort ratio of normalized names (RapidFuzz) |
| `father_name_sim` | Jaro-Winkler of father’s name; −1 if either missing |
| `same_mobile` | 1 / 0 / −1 (missing) |
| `same_village`, `same_district` | 1 / 0 / −1 |
| `dob_year_diff` | absolute difference; −1 if missing |
| `same_survey_no`, `same_bank_last4` | 1 / 0 / −1 |
| `same_agristack_id` | 1 only when both have an ID and they are equal (strong signal) |

#### Stage 3 – Scoring (`matcher.py`)

- **Rule shortcut:** equal `agristack_id` → score 1.0, method = `rule`.
- **Model:** XGBoost classifier trained on labelled pairs. A pair is labelled “match” when both records share the same hidden `true_farmer_id` in `ground_truth.csv`. Output = match probability.
- **Baseline for your report:** logistic regression and a hand-weighted average. Showing XGBoost beats the baseline gives you a clean results table.
- The trained model is saved once as `models/matcher.joblib` by `scripts/train_matcher.py`; the API only loads it.

#### Stage 4 – Decision thresholds

| Score | Decision | What happens |
|---|---|---|
| ≥ 0.90 | `auto_link` | Records are linked automatically |
| 0.60 – 0.90 | `review` | Pair goes to the **Review Queue** page. An officer confirms or rejects |
| < 0.60 | `no_match` | Ignored |

Thresholds live in `config.py`, not in code, so they can be tuned from the evaluation results.

#### Stage 5 – Clustering and golden record (`clustering.py`, `golden_record.py`)

- Build a small NetworkX graph: nodes = clean records, edges = `auto_link` + officer-confirmed pairs. Each **connected component** is one farmer.
- Guard against chain errors (A~B, B~C but A≠C): if a component has more than 6 records or contains two different AgriStack IDs, send it to the review queue instead of merging.
- **Survivorship rules** for the golden record: for each field take the value from the most trusted non-null source (order: AgriStack > KCC > PM-KISAN > PMFBY > NFSM). Ties → most recent record. Store `confidence` = mean pair score in the cluster.
- Write `farmers`, `farmer_links`, `land_parcels`.

```python
# services/resolution_service.py  (orchestration only – no algorithm here)
class ResolutionService:
    def __init__(self, records: CleanRecordRepo, matches: MatchRepo,
                 farmers: FarmerRepo, blocker: Blocker, matcher: PairMatcher,
                 merger: GoldenRecordBuilder):
        ...

    def run(self) -> ResolutionSummary:
        pairs   = self.blocker.candidate_pairs(self.records.all())
        scored  = [self.matcher.score(a, b) for a, b in pairs]
        self.matches.save_all(scored)
        clusters = build_clusters(self.matches.linked_pairs())
        for c in clusters:
            self.farmers.upsert(self.merger.build(c))
        return ResolutionSummary.from_counts(...)
```

### Module 4 – Duplicate & Multi-Claim Detection (Step 4)   [Member B]

Purely rule-based, which is exactly right: these are policy checks, not statistical guesses. Each rule is a small class with a `check(farmer)` method returning zero or more `Flag` objects.

| Rule | Detects | Severity |
|---|---|---|
| `SameSchemeTwice` | Two records of the same scheme and season link to one farmer | High |
| `MutuallyExclusiveSchemes` | Farmer enrolled in two schemes that config says cannot be combined for the same crop/season | High |
| `ParcelOverclaim` | Total area claimed on one `village_code + survey_no` is larger than the parcel’s recorded area | Medium |
| `SharedBankAccount` | Same `bank_last4 + district` appears across different farmers | Medium |
| `LowConfidenceMerge` | Golden record confidence below threshold | Low |

Output: rows in `flags` with `status = open`. Officers later mark them `confirmed` or `dismissed`.

### Module 5 – Eligibility Verification (Step 5)   [Member B]

Scheme rules live in `eligibility/rules/schemes.yaml`. The engine is ~60 lines and never changes when a scheme is added.

```yaml
# eligibility/rules/schemes.yaml   (ILLUSTRATIVE rules – replace with official guidelines)
PM_KISAN:
  name: PM-KISAN Income Support
  benefit_score: 8
  all:
    - {field: total_land_ha, op: gt,  value: 0}
    - {field: category,      op: in,  value: [marginal, small, other]}
PMFBY:
  name: Crop Insurance
  benefit_score: 9
  all:
    - {field: has_notified_crop, op: eq, value: true}
    - {field: season_active,     op: eq, value: true}
NFSM:
  name: Food Security Mission - Seed Subsidy
  benefit_score: 6
  all:
    - {field: crop_group, op: in,  value: [cereal, pulse]}
    - {field: total_land_ha, op: lte, value: 5}
KCC:
  name: Kisan Credit Card
  benefit_score: 7
  all:
    - {field: total_land_ha, op: gte, value: 0.2}
```

```python
# eligibility/engine.py
OPS = {"eq": operator.eq, "gt": operator.gt, "gte": operator.ge,
       "lte": operator.le, "in": lambda a, b: a in b}

def evaluate(scheme_rules: dict, facts: dict) -> EligibilityResult:
    reasons, ok = [], True
    for r in scheme_rules["all"]:
        passed = OPS[r["op"]](facts[r["field"]], r["value"])
        reasons.append(f"{r['field']} {r['op']} {r['value']}: {passed}")
        ok &= passed
    return EligibilityResult(eligible=ok, reasons=reasons)
```

Because every rule returns a human-readable reason, the officer sees **why** a farmer is or is not eligible. That is your explainability story for the rules half of the system.

### Module 6 – Recommendation and Exclusion (Steps 6 and 7)   [Member B]

> **Simplification:** Steps 5, 6 and 7 are three views of one computation. We compute eligibility once for every farmer × scheme and store it in `recommendations`. Recommendation and exclusion are just different queries on that table.

| View | Query logic |
|---|---|
| **Scheme recommendation** (per farmer) | `eligible = true AND already_enrolled = false`, ordered by `priority`. Priority = scheme `benefit_score` + 2 for marginal farmers + 1 for small farmers |
| **Exclusion list** (per village / district) | Farmers in AgriStack with at least one `eligible = true AND already_enrolled = false` scheme. Grouped by scheme and area for the coverage-gap report |

This is transparent and easy to defend in a viva. If your guide wants “more ML” here, add an optional XGBoost model that predicts likelihood of uptake as a **stretch goal** only after everything else works.

### Module 7 – Dashboard, Verification and Reports (Steps 9–11)   [Member C, with Member B’s endpoints]

- **Verification workflow:** officer opens a flag or a review-queue pair → sees side-by-side records → clicks Confirm / Dismiss / Merge / Not-same. The API updates the table and writes `audit_log`.
- **Reports:** coverage by scheme and district, duplicate-claim counts, exclusion counts, top 10 villages by gap, trend of flags per month. Export as CSV (pandas `to_csv`).
- **Charts:** built in React with Recharts. Matplotlib and Plotly stay in Jupyter for your offline model analysis figures in the report.

## 7. Backend Code Structure and SOLID Principles

### 7.1 Repository layout (monorepo, one GitHub repo)

```text
agri-beneficiary-intelligence/
├─ backend/
│  ├─ app/
│  │  ├─ main.py                  # creates FastAPI app, includes routers
│  │  ├─ core/                    # config.py, db.py, security.py
│  │  ├─ api/
│  │  │  ├─ deps.py               # dependency wiring (Depends)
│  │  │  └─ routers/              # auth, farmers, matches, flags, reports
│  │  ├─ schemas/                 # Pydantic request/response models
│  │  ├─ models/                  # SQLAlchemy ORM tables
│  │  ├─ repositories/            # FarmerRepo, CleanRecordRepo, MatchRepo, FlagRepo ...
│  │  ├─ services/                # Ingestion/Resolution/Duplicate/Eligibility/Report
│  │  ├─ ingestion/               # base.py + adapters/ (one file per source)
│  │  ├─ preprocessing/           # normalizers.py, pipeline.py
│  │  ├─ resolution/              # blocking, features, matcher, clustering, golden_record
│  │  ├─ duplicates/              # base.py + rules/ (one file per rule)
│  │  └─ eligibility/             # engine.py + rules/schemes.yaml
│  ├─ scripts/                    # generate data, train model, seed db
│  ├─ tests/                      # mirrors app/ folders
│  ├─ alembic/                    # DB migrations
│  └─ requirements.txt
├─ frontend/                      # see Section 9
├─ notebooks/                     # EDA, model training experiments
├─ data/synthetic/                # generated CSVs (git-ignored except a tiny sample)
├─ models/                        # matcher.joblib (git-ignored, rebuilt by script)
├─ docs/                          # this document, API contract, report drafts
├─ docker-compose.yml             # PostgreSQL only
└─ README.md
```

### 7.2 How each SOLID principle appears in this project

| Principle | Where we apply it | Concrete example |
|---|---|---|
| **S** – Single Responsibility | Every file has one reason to change | `normalizers.py` only cleans text. `blocking.py` only picks candidate pairs. `FarmerRepo` only talks to the `farmers` table |
| **O** – Open/Closed | Extend by adding files, not editing old ones | New scheme source = new adapter class. New duplicate rule = new class in `duplicates/rules/`. New scheme = new YAML block |
| **L** – Liskov Substitution | Any subclass works wherever the base type is expected | The pipeline calls `adapter.read()` for every `SourceAdapter` and never checks which source it is. Every `DuplicateRule` returns a list of `Flag` |
| **I** – Interface Segregation | Small focused interfaces | `PairMatcher` has only `score(a, b)`. `Blocker` has only `candidate_pairs(records)`. No giant “DataProcessor” interface |
| **D** – Dependency Inversion | Services depend on abstractions injected from outside | `ResolutionService` receives repos and matcher in its constructor. Tests pass fakes, so no database is needed |

### 7.3 Dependency wiring in one place (`api/deps.py`)

```python
# api/deps.py – the ONLY file that knows which concrete classes are used
def get_resolution_service(db: Session = Depends(get_db)) -> ResolutionService:
    return ResolutionService(
        records=CleanRecordRepo(db),
        matches=MatchRepo(db),
        farmers=FarmerRepo(db),
        blocker=PhoneticVillageBlocker(),
        matcher=XGBoostPairMatcher(model_path=settings.MATCHER_PATH),
        merger=TrustOrderGoldenRecordBuilder(),
    )

# api/routers/pipeline.py
@router.post("/pipeline/resolve")
def run_resolution(svc: ResolutionService = Depends(get_resolution_service)):
    return svc.run()
```

### 7.4 Coding rules for all three members

- Type hints on every function. Ruff + Black enforced by pre-commit.
- Functions under ~30 lines; files under ~250 lines. If it grows, split it.
- No business logic in routers. No SQL outside `repositories/`.
- Every new module ships with tests in the same pull request.
- No secrets in Git: use `.env` (git-ignored) and commit `.env.example`.
- Names in English, snake_case in Python, camelCase in TypeScript.

## 8. REST API Design (Contract Between Backend and Frontend)

FastAPI auto-generates this at `/docs`. Member B and Member C agree on the list below **before** coding, and treat the OpenAPI JSON as the source of truth.

| Method and path | Purpose | Used by page |
|---|---|---|
| POST `/auth/login` | Returns JWT and role | Login |
| GET `/farmers?district=&scheme=&q=&page=` | Search and list golden farmers | Farmers |
| GET `/farmers/{id}` | Farmer 360: golden record, linked source records, enrollments, flags, recommendations | Farmer 360 |
| GET `/matches?decision=review` | Pairs waiting for officer decision | Review Queue |
| POST `/matches/{id}/decision` | Body: `{decision: "confirm" \| "reject"}` | Review Queue |
| GET `/flags?type=&status=&severity=` | Duplicate / fraud alerts | Flags |
| PATCH `/flags/{id}` | Set `confirmed` or `dismissed` with note | Flags |
| GET `/recommendations?farmer_id=` | Schemes to recommend for one farmer | Farmer 360 |
| GET `/exclusions?district=&scheme=` | Eligible-but-not-enrolled farmers | Exclusions |
| GET `/reports/summary` | Totals: records, farmers, duplicates removed, flags, exclusions | Dashboard |
| GET `/reports/coverage?group_by=district\|scheme` | Coverage numbers for charts | Dashboard |
| GET `/reports/export?type=exclusions` | CSV download | Reports |
| POST `/pipeline/ingest` · `/resolve` · `/evaluate` | Admin-only: run pipeline stages (FastAPI BackgroundTasks; also runnable as CLI scripts) | Admin |
| **Farmer portal endpoints** | Register, profile, scheme feed, autofill, applications, officer decisions: see Section 16.9 | Farmer / Officer |

Standard response envelope for lists: `{ items: [...], total: 123, page: 1 }`. Standard error body: `{ detail: "message" }`.

## 9. Frontend Design (React)

### 9.1 Officer pages (five are enough; farmer pages are in Section 16.10)

| Page | What the user sees | Main components |
|---|---|---|
| Dashboard | KPI cards (source records → unique farmers, duplicates found, open flags, excluded farmers); bar chart of coverage by scheme; line chart of flags per month | `KpiCard`, `CoverageBarChart`, `TrendLineChart` |
| Farmers | Searchable, filterable table of golden farmers | `FarmerTable`, `FilterBar`, `Pagination` |
| Farmer 360 | One farmer: merged profile, list of source records that were merged (with match score), schemes enrolled, eligibility reasons, recommendations, flags | `ProfileCard`, `LinkedRecordsList`, `EligibilityTable`, `FlagList` |
| Review Queue | Two records side by side with differences highlighted, score, top SHAP features, Confirm / Reject buttons | `RecordCompare`, `ScoreBadge`, `ShapBar`, `DecisionButtons` |
| Flags and Exclusions | Tabs for duplicate alerts and excluded farmers, with status update and CSV export | `FlagTable`, `ExclusionTable`, `ExportButton` |

### 9.2 Folder structure

```text
frontend/src/
├─ api/            # axios instance + one file per resource (farmers.ts, flags.ts ...)
├─ types/          # TypeScript types mirroring backend Pydantic schemas
├─ hooks/          # useFarmers(), useFlags() ... wrap TanStack Query
├─ components/     # small reusable UI pieces (KpiCard, DataTable, ScoreBadge)
├─ features/       # page-specific components grouped by page
├─ pages/          # DashboardPage.tsx, FarmersPage.tsx, ...
├─ routes.tsx      # React Router + protected routes by role
└─ main.tsx
```

### 9.3 Frontend rules

- Pages contain layout only; data fetching lives in `hooks/`; HTTP calls live in `api/`. Same separation as the backend.
- Until the real API is ready, use **mock JSON** (MSW or a `mock/` folder) shaped exactly like the API contract, so the frontend is never blocked.
- One UI kit (Tailwind, optionally shadcn/ui). No mixing of component libraries.
- Every table has loading, empty and error states.

## 10. ML Evaluation and Explainability

Because we generated the data, we know the right answers. This gives you strong, honest numbers for the report.

| What to measure | How | Target (realistic) |
|---|---|---|
| Pair-matching quality | Precision, recall, F1 on a held-out 20% of labelled pairs | F1 ≥ 0.95 on synthetic data |
| Model vs baselines | Rule-only vs logistic regression vs XGBoost, same test set | XGBoost best; show table |
| End-to-end farmer accuracy | Pairwise clustering precision/recall using `ground_truth.csv` | Report duplicates removed vs true |
| Blocking quality | Reduction ratio (pairs avoided) and pair completeness (true matches kept) | > 99% reduction, > 98% completeness |
| Threshold tuning | Plot precision and recall against the auto-link threshold | Choose the threshold from the curve |
| Flag detection | Compare flags raised with the planted problems from Section 4.2 | Recall on planted problems |

**Explainability (from your references).** For each review-queue pair show the top 3–4 features that pushed the score up or down (SHAP values from the XGBoost model). Eligibility already explains itself through the rule reasons. Together they satisfy the XAI point in your synopsis without extra complexity.

**Honest limitation to state in the report:** results on synthetic data are optimistic. Real data will have harder noise, so the pipeline is designed with the human review band (0.60–0.90) as a safety net.

## 11. Team Collaboration Plan (3 Members)

### 11.1 Roles and code ownership

Each person owns a set of folders. Owners review each other’s changes in their area. Assign names as you prefer; the split below balances ML, backend and frontend work.

| Role | Owns (folders) | Main deliverables |
|---|---|---|
| **Member A – Data & ML** | `scripts/`, `ingestion/`, `preprocessing/`, `resolution/`, `notebooks/`, `data/` | Synthetic data generator, adapters, normalizers, blocking, features, XGBoost matcher, golden record, evaluation and SHAP |
| **Member B – Backend & Database** | `core/`, `models/`, `repositories/`, `services/`, `api/`, `duplicates/`, `eligibility/`, `alembic/`, `docker-compose.yml` | Schema and migrations, auth, all REST endpoints, duplicate rules, eligibility engine, recommendation/exclusion queries, reports |
| **Member C – Frontend & Quality** | `frontend/`, `docs/`, `backend/tests/` (integration) | All React pages, charts, review UI, mock API, Postman collection, integration tests, README, final report assembly |

The Farmer Portal (Section 16) is split the same way: Member A links profiles to golden records, Member B builds the endpoints, autofill and email service, Member C builds the farmer pages. Details are in Section 16.12.

Everyone writes unit tests for their own code. Member C additionally owns end-to-end checks and documentation so quality work does not get forgotten.

### 11.2 The three hand-off contracts

| Between | Contract | How it keeps people unblocked |
|---|---|---|
| A → B | **Database tables** (Section 5). A writes `clean_records`, `match_candidates`, `farmers`, `farmer_links`; B reads them | Member B seeds the DB with `scripts/seed_db.py` fake rows in week 1 so nobody waits for the ML |
| B → C | **OpenAPI spec** (Section 8), exported to `docs/openapi.json` | Member C builds against mock JSON; switching to the real API is one config flag |
| A → B (code) | **Service call:** `ResolutionService.run()` is triggered by `POST /pipeline/resolve` | A can also run it from the command line with no API |

### 11.3 Git workflow (GitHub flow with a `dev` branch)

1. `main` = always demo-ready. `dev` = integration branch. Nobody pushes directly to either.
2. Create a branch from `dev`: `feature/<area>-<short-name>`, e.g. `feature/resolution-blocking`, `fix/api-flags-filter`.
3. Commit small and often with **Conventional Commits**: `feat:`, `fix:`, `test:`, `docs:`, `refactor:`.
4. Open a Pull Request into `dev`. Use the PR template: what changed, how to test, screenshots (for UI).
5. **At least one teammate reviews** (the folder owner if it is not their own). CI must be green: lint + pytest + frontend build.
6. Squash-merge, delete the branch. Merge `dev` into `main` at the end of each sprint after a quick demo run.

### 11.4 Working rhythm

- **Two-week sprints.** Planning on day 1 (30 min), stand-up twice a week (10 min, on chat), demo + retro on the last day (45 min).
- **GitHub Projects board** with columns: Backlog · In Progress · In Review · Done. Every task is an issue linked to its PR.
- **Definition of Done:** code merged to `dev`, tests pass, docstring on public functions, API contract or README updated, teammate has run it locally.
- **Shared conventions file** `docs/CONVENTIONS.md`: naming, folder rules, commit style. One page.
- **Pair once a sprint** on the risky integration (A+B for the pipeline trigger, B+C for a new endpoint) to avoid last-minute surprises.

### 11.5 Suggested repository hygiene files

```text
.github/
├─ workflows/ci.yml            # ruff, black --check, pytest, npm run lint, npm run build
├─ pull_request_template.md
└─ CODEOWNERS                  # /backend/app/resolution/ @member-a  etc.
.env.example                   # DATABASE_URL, JWT_SECRET, MATCHER_PATH
.pre-commit-config.yaml        # ruff, black, prettier
.gitignore                     # .env, data/synthetic/, models/, node_modules/, __pycache__/
```

## 12. Timeline Mapped to Your Synopsis Steps

Your synopsis already has a month-wise plan. Below, each step is split by owner so every member has a clear target each month.

| Synopsis step | Member A – Data & ML | Member B – Backend & DB | Member C – Frontend & QA |
|---|---|---|---|
| **Step 3** Sept | Synthetic data generator; adapters; normalizers with tests | Docker Compose, schema and Alembic, FastAPI skeleton, JWT auth, seed script | React + Vite skeleton, layout, routing, login page, mock API |
| **Step 4** Oct | Blocking, feature builder, baseline matcher (rules + fuzzy score) | Repositories; farmer list and detail endpoints; unified farmer tables working | Farmers page, Farmer 360 page on mock data; seminar report drafts |
| **Step 5** Dec | XGBoost matcher, thresholds, clustering, golden record, save model | Duplicate rules, YAML eligibility engine, recommendations, exclusion queries, match/flag endpoints | Review Queue and Flags pages connected to real API |
| **Step 6** Jan–Feb | Evaluation notebook, baselines, SHAP outputs | Report endpoints, CSV export, audit log, pipeline trigger endpoints | Dashboard charts, Exclusions page, CSV export button |
| **Step 7** Feb–Mar | Tune thresholds; ML validation results | Bug fixing, performance (indexes, batch inserts) | End-to-end tests, Postman collection, usability pass |
| **Step 8** Apr | Write ML chapters and result tables | Write architecture, DB and API chapters | Assemble report, screenshots, user manual |
| **Step 9** May | Demo of the pipeline | Demo of API and workflow | Demo of UI, viva rehearsal for all three |

**Farmer Portal placement:** build it after the core pipeline works (Section 16.12): profile, scheme feed and autofill apply in Step 5 (December), officer review of applications, profile linking and emails in Step 6 (Jan–Feb).

**Buffer rule:** finish the *vertical slice* (data → match → golden record → one dashboard page) by end of October. Everything after that only adds features to a working system.

## 13. Testing Strategy

| Level | Tool | What is tested | Owner |
|---|---|---|---|
| Unit | pytest | Normalizers, feature builder, rule engine, each duplicate rule, golden-record survivorship | Each author |
| Service (with fakes) | pytest | `ResolutionService` and `DuplicateService` with in-memory fake repos, no DB | A and B |
| API integration | pytest + FastAPI TestClient + test Postgres | Each endpoint status, filters, auth and role checks | B and C |
| ML quality | notebook + pytest threshold test | F1 on the held-out set does not drop below the agreed value | A |
| Frontend | Vitest + React Testing Library | Key components render and handle empty/error states | C |
| Manual E2E | Postman + browser | Login → run pipeline → review queue → resolve flag → export CSV | C |

## 14. Setup and Run (README Quick Start)

```bash
# 1. clone and configure
git clone <repo-url> && cd agri-beneficiary-intelligence
cp .env.example .env

# 2. database
docker compose up -d                     # PostgreSQL only

# 3. backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python scripts/generate_synthetic_data.py
python scripts/train_matcher.py          # creates models/matcher.joblib
uvicorn app.main:app --reload            # API docs at http://localhost:8000/docs

# 4. run the pipeline (or use the Admin button in the UI)
python -m app.cli ingest && python -m app.cli resolve && python -m app.cli evaluate

# 5. frontend
cd ../frontend && npm install && npm run dev   # http://localhost:5173
```

## 15. Risks and Viva Demo Script

### 15.1 Risks and simple mitigations

| Risk | Mitigation |
|---|---|
| No access to real AgriStack data | Use the synthetic generator; document the schema so real adapters can be plugged in later |
| Model looks too perfect on synthetic data | Increase noise levels; report human-review band; state the limitation openly |
| Wrong merges of different farmers with the same name | Use village, father’s name and mobile as features; cluster-size guard; officer review band |
| Team members blocked on each other | Contract-first (tables + OpenAPI), seed data and mock API from week 1 |
| Scope creep | Section 1.1 “skip” list; stretch goals only after the vertical slice works |
| Merge conflicts | Folder ownership, small PRs, branch from `dev` daily |
| Privacy concerns | No full Aadhaar or bank account stored in profiles; role-based access; audit log of every officer action |
| Email deliverability during the demo | Use `ConsoleEmailSender` or MailHog for the viva; keep real SMTP as an optional setting |
| Farmer portal delays the core work | Build it last (Section 16.12); the officer system is already a complete demo without it |

### 15.2 Seven-minute demo script

1. **Show the mess (1 min):** open two raw CSVs; find the same farmer spelled three ways.
2. **Run the pipeline (1 min):** click *Run Resolution*; KPI cards update from 12,000 records to about 5,000 unique farmers.
3. **Farmer 360 (1 min):** open one farmer; show the merged profile and the source records with match scores.
4. **Review Queue (1 min):** show an uncertain pair with the SHAP explanation; confirm it.
5. **Flags and Exclusions (1 min):** show a duplicate subsidy claim and an eligible-but-excluded farmer with reasons.
6. **Farmer Portal (1.5 min):** log in as a farmer, show the profile completeness bar, click **Autofill** on a scheme, fill the remaining fields, submit; switch to the officer inbox and approve; show the suggestion email.
7. **Results slide (1 min):** show the precision / recall table and baseline comparison.

> **Final checklist before starting to code:** (1) fix the title in the synopsis, (2) create the GitHub repo with the folder skeleton from Section 7.1, (3) agree the API list in Section 8, (4) each member creates their first branch and opens a small PR to test the review flow.

## 16. Farmer Portal – The Third Role (New)

Until now the platform served only government users. This section adds the **Farmer** role: a farmer creates a profile once (like an Internshala candidate profile), sees the schemes that match him or her, and applies with an **Autofill** button or by typing manually. The system also emails scheme suggestions. Everything reuses the modules already designed, so it adds only a few new tables and three small backend modules.

```mermaid
flowchart LR
  R1["1 Register"] --> R2["2 Profile wizard"] --> R3["3 Matched schemes"] --> R4["4 Apply: Autofill or manual"] --> R5["5 Officer review"] --> R6["6 Benefit / enrollment"]
  EM["Email engine: weekly digest, new-scheme alert, deadline reminder"] -.->|suggests schemes| R3
  EM -.->|link opens Apply page| R4
```

*Figure 3 – Farmer journey. Blue = farmer actions, green = system/officer, orange = email.*

### 16.1 Roles after this change

| Role | Can do |
|---|---|
| `farmer` | Register, edit own profile, see matched schemes, apply (autofill or manual), track applications, manage email preferences. Sees **only his or her own data** |
| `officer` | Everything from Section 6 **plus** review scheme applications (approve / reject with a note) |
| `admin` | Run pipeline, manage users, **publish or close schemes** (this triggers new-scheme emails) |

### 16.2 Farmer journey (step by step)

1. **Register:** email, password, mobile, and a consent tick-box for emails and data use. Role is set to `farmer` automatically.
2. **Build profile:** a 4-step wizard (Section 16.3) with a “Profile 70% complete” bar. Only the essentials are compulsory, everything else can be filled later.
3. **Link to golden record:** when the profile is saved, the system tries to connect it to an existing farmer in our identity database (Section 16.4). Farmers never see this technical step, they only see a “Verified” badge once it succeeds.
4. **Recommended schemes:** the dashboard shows “Recommended for you” (eligible and matching interests) and “Other schemes you qualify for”, each with status Ongoing or Upcoming and a deadline.
5. **Apply:** open a scheme, click **Autofill from profile**, correct anything, fill the remaining fields manually, save draft or submit.
6. **Track:** “My Applications” shows Draft → Submitted → Under review → Approved / Rejected, with the officer’s note.
7. **Email:** weekly suggestions and alerts bring the farmer back to step 4.

### 16.3 Profile design (Internshala-style, kept simple)

Four wizard steps. Each field is stored once in `farmer_profiles` and reused everywhere, which is what makes autofill trivial.

| Step | Fields | Required? | Autofills forms? |
|---|---|---|---|
| 1. Personal | Full name, father/husband name, date of birth, gender, mobile, email, category (marginal / small / other) | Name, DOB, mobile, email | Yes |
| 2. Address | Village, taluka, district, state, PIN code | Village, district | Yes |
| 3. Land & crops | Total land (ha), ownership type (owner / tenant), main crops (multi-select), irrigation type, survey number (optional) | Land area, main crops | Yes |
| 4. Interests | Tick the areas you want help with: crop insurance, credit/loan, seeds & inputs, irrigation, horticulture, farm machinery, organic farming, storage & marketing | At least one | No – used only for suggestions |
| Optional | AgriStack Farmer ID (if the farmer has one), bank name and IFSC | No | Farmer ID and bank name/IFSC yes |

**Profile completeness** is a simple weighted count: Personal 30%, Address 20%, Land & crops 30%, Interests 20%. The farmer can apply only when the fields that scheme requires are filled, not when the profile is 100% complete.

> **Sensitive data rule:** we do **not** autofill or store the full bank account number or Aadhaar number in the profile. If a scheme asks for them, the farmer types them in the application form. This keeps the design privacy-safe and avoids a security-heavy build.

### 16.4 Linking a farmer profile to the golden record

This is where the portal connects to your core AI work. A new profile is treated as a **sixth data source called `portal`** and goes through the same resolution logic as the other sources.

1. If the profile has an AgriStack Farmer ID that exists in `farmers` → link immediately (method = `rule`).
2. Otherwise build a `clean_record` from the profile and run the existing blocking + matcher against `farmers`.
3. Score ≥ 0.90 → link. Score 0.60–0.90 → officer Review Queue (profile shows “Verification pending”). Below 0.60 → create a new golden farmer.

Benefit: a farmer who already exists in PM-KISAN or PMFBY is recognised, so the portal shows the schemes he is **already enrolled in** and never recommends them again. It also means duplicate rules (Section 6, Module 4) protect against a farmer applying twice.

Profile values are self-declared. Eligibility is computed from them with the same YAML engine; after an officer verifies, the golden-record values take priority.

### 16.5 Scheme feed: “matched as per interest / domain”

No new AI is needed. Add two columns to `schemes`: `domain` (matches the interest tags) and `status`/`start_date`/`end_date`. The feed is a small query:

| Feed section | Rule |
|---|---|
| **Recommended for you** | Scheme is Ongoing or Upcoming AND farmer is eligible (Module 5 engine) AND scheme `domain` is in the farmer’s interests AND not already enrolled/applied. Sorted by deadline, then `benefit_score` |
| **Other schemes you qualify for** | Eligible, but domain not in interests |
| **Already applied / enrolled** | From `scheme_applications` and `enrollments` |

Not-eligible schemes are hidden by default. A “Why not eligible?” link can show the rule reasons the engine already returns.

### 16.6 Application form and the Autofill feature

**Design goal:** autofill must be trivial. The rule is one line: each form field may name one profile field to copy from; if it does not, the farmer types it. There is no mapping engine, no OCR, and no machine learning in autofill.

#### Step 1 – Describe each scheme’s form in YAML (next to its eligibility rules)

```yaml
# schemes.yaml (extended)
PMFBY:
  name: Crop Insurance
  domain: crop_insurance
  status: ongoing
  end_date: 2026-12-31
  all: [ ...eligibility rules as before... ]
  application_form:
    - {key: full_name, label: Full name, autofill: full_name}
    - {key: mobile,    label: Mobile,    autofill: mobile}
    - {key: village,   label: Village,   autofill: village}
    - {key: district,  label: District,  autofill: district}
    - {key: land_ha,   label: Land (ha), autofill: total_land_ha, type: number}
    - {key: survey_no, label: Survey number}                       # manual
    - {key: crop,      label: Crop to insure, type: select,
       options: [wheat, rice, soybean, cotton]}                     # manual
    - {key: bank_acct, label: Bank account no.}                     # manual
```

Fields with `autofill` are pre-filled; fields without it (survey number, crop to insure, bank account) are manual. Adding a scheme form means editing YAML only.

#### Step 2 – One tiny function does the autofill

```python
# applications/autofill.py
def autofill(form: list[FormField], profile: dict) -> AutofillResult:
    values, filled = {}, []
    for field in form:
        source = field.autofill                      # e.g. "total_land_ha" or None
        if source and profile.get(source) not in (None, ""):
            values[field.key] = profile[source]
            filled.append(field.key)
    return AutofillResult(values=values, autofilled_keys=filled)
```

#### Step 3 – Behaviour in the UI

- Application page opens with an **empty form** and two buttons: **Autofill from my profile** and **Fill manually**. The farmer chooses.
- After Autofill, copied fields get a light green highlight and a small “from profile” tag. **Every field stays editable**; edits affect only this application, not the profile.
- A banner lists what is still missing, e.g. “3 fields need your input: Survey number, Crop to insure, Bank account”.
- Buttons: **Save draft** (status `draft`) and **Submit** (validates required fields, status `submitted`).
- On submit, the backend stores a **snapshot** of the values in `scheme_applications.form_data` (JSONB). Later profile changes never alter an already submitted application.

#### Application status flow

| Status | Meaning | Who changes it |
|---|---|---|
| `draft` | Saved, not submitted | Farmer |
| `submitted` | Sent to officers. Duplicate rules run (e.g. already applied or already enrolled for the same scheme and season) | Farmer / system |
| `under_review` | Officer opened it | Officer |
| `approved` | Creates an `enrollments` row; farmer is emailed | Officer |
| `rejected` | Officer note explains why; farmer may re-apply | Officer |

### 16.7 Email suggestions

Kept deliberately simple: **one sender interface, one scheduled job, one log table.**

| Email | When | Content |
|---|---|---|
| **Weekly digest** | Every Monday 8:00 for opted-in farmers with at least one new match | Top 3 recommended schemes, deadline, “Apply now” button (deep link to the Apply page) |
| **New scheme alert** | When an admin publishes a scheme, for farmers who are eligible and interested | Scheme name, benefit, deadline, link |
| **Deadline reminder** (optional) | 3 days before `end_date`, only if the farmer has not applied | Short reminder with link |
| **Status update** | When an application is approved or rejected | Result and officer note |

```python
# notifications/sender.py
class EmailSender(ABC):
    @abstractmethod
    def send(self, to: str, subject: str, html: str) -> None: ...

class SmtpEmailSender(EmailSender):      # real emails (Gmail SMTP app-password / any SMTP)
    ...
class ConsoleEmailSender(EmailSender):   # dev + demo: prints the email, sends nothing
    ...

# services/notification_service.py
class NotificationService:
    def __init__(self, sender, farmers, recs, log, templates): ...

    def send_weekly_digest(self):
        for farmer in self.farmers.opted_in():
            recs = self.recs.for_farmer(farmer.id)
            fresh = [r for r in recs if not self.log.sent(farmer.id, r.scheme_id)]
            if fresh:
                top = fresh[:3]
                html = self.templates.digest(farmer, top)
                self.sender.send(farmer.email, "Schemes for you", html)
                self.log.record(farmer.id, [r.scheme_id for r in top], "digest")
```

- **Scheduling:** run `python -m app.cli send_digest` from a cron job or Windows Task Scheduler. Optionally use APScheduler inside FastAPI. No Celery or message queue.
- **No spam:** `email_log` stores (farmer, scheme, type, sent_at). A scheme is never emailed twice for the same type.
- **Consent:** `email_opt_in` flag on the profile, a settings toggle, and an unsubscribe link in every email.
- **Dev/demo setup:** use `ConsoleEmailSender` or **MailHog / Mailtrap** so you can show emails in the viva without sending real ones. Switch to SMTP with one line in `.env` (`EMAIL_BACKEND=smtp`).
- **Templates:** two Jinja2 HTML files (`digest.html`, `alert.html`) with the same look as the app.

Because `NotificationService` depends on the `EmailSender` abstraction, adding SMS or WhatsApp later means writing one new sender class and changing nothing else (Open/Closed and Dependency Inversion).

### 16.8 Database additions

| Table | Purpose | Key columns |
|---|---|---|
| `farmer_profiles` | One profile per farmer user | id, user_id (FK users), farmer_id (FK farmers, nullable until linked), full_name, father_name, dob, gender, mobile, email, category, village, taluka, district, state, pincode, total_land_ha, ownership_type, main_crops (array), irrigation_type, interests (array), agristack_id, bank_name, ifsc, email_opt_in, verified (bool), completeness (int) |
| `scheme_applications` | Applications | id, farmer_profile_id, scheme_id, status, form_data (JSONB), autofilled_keys (array), submitted_at, reviewed_by, officer_note, updated_at |
| `email_log` | Prevent duplicate emails, audit | id, farmer_profile_id, scheme_id, type (digest / alert / reminder / status), sent_at |
| `schemes` (add columns) | Support feed and forms | domain, status (upcoming / ongoing / closed), start_date, end_date |
| `users` (change) | New role value | role in (`admin`, `officer`, `farmer`) |

### 16.9 API additions

| Method and path | Purpose | Role |
|---|---|---|
| POST `/auth/register` | Farmer signup (role forced to `farmer`) | Public |
| GET / PUT `/me/profile` | Read and update own profile; response includes `completeness` | Farmer |
| GET `/me/schemes?section=recommended\|other` | Scheme feed (16.5) | Farmer |
| GET `/schemes/{id}` | Scheme details and required form fields | Farmer |
| POST `/applications/prefill` | Body `{scheme_id}` → returns `values` and `autofilled_keys` (autofill result) | Farmer |
| POST `/applications` | Create draft or submit application | Farmer |
| PUT `/applications/{id}` | Edit a draft | Farmer |
| GET `/me/applications` | My applications and statuses | Farmer |
| GET `/applications?status=&scheme=` | Officer inbox of applications | Officer |
| PATCH `/applications/{id}/decision` | Approve or reject with note (approve creates enrollment and sends status email) | Officer |
| POST `/schemes` · PATCH `/schemes/{id}` | Admin publishes or closes a scheme (publishing triggers new-scheme alerts) | Admin |
| PATCH `/me/notifications` | Toggle email opt-in | Farmer |

Access rule: every `/me/*` endpoint reads the farmer id from the JWT, never from the URL, so one farmer can never open another farmer’s data.

### 16.10 Frontend additions

| Page | Role | Notes |
|---|---|---|
| Register / Login | All | Shared login, redirect by role after login |
| Profile wizard | Farmer | 4 steps, progress bar, save per step, completeness % |
| My Dashboard | Farmer | Cards: “Recommended for you”, “Other schemes”, “My applications” summary |
| Scheme details | Farmer | Benefits, eligibility summary, deadline, **Apply** button |
| Apply | Farmer | Dynamic form built from the scheme’s `application_form`; Autofill and Save/Submit buttons |
| My Applications | Farmer | Status timeline and officer note |
| Settings | Farmer | Email opt-in toggle |
| Applications inbox | Officer | Table + detail view with **profile vs submitted values** side by side; approve or reject |
| Scheme management | Admin | Create or edit scheme, set dates and status (publishing sends alerts) |

The **Apply** page is one generic component. It receives the list of form fields, renders inputs by `type`, and applies the values returned by `/applications/prefill`. New schemes need no new frontend code.

### 16.11 Backend structure additions

```text
backend/app/
├─ profiles/          # completeness.py (weights), profile_linker.py (uses resolution/ modules)
├─ applications/      # form_loader.py (reads YAML), autofill.py, validators.py
├─ notifications/     # sender.py (EmailSender, Smtp, Console), templates/, digest_builder.py
├─ services/          # + ProfileService, ApplicationService, NotificationService
├─ repositories/      # + ProfileRepo, ApplicationRepo, EmailLogRepo
└─ api/routers/       # + me.py, applications.py, schemes.py
```

### 16.12 Team split and build order for the Farmer Portal

| Member | Farmer-portal tasks |
|---|---|
| **A – Data & ML** | `profile_linker.py` (reuse blocking + matcher for the `portal` source), completeness weights, test that a profile matches its golden record on synthetic data |
| **B – Backend** | New tables and migrations, `/me/*` and `/applications` endpoints, form loader and autofill function, officer decision endpoint, `NotificationService`, digest CLI job |
| **C – Frontend & QA** | Register, profile wizard, farmer dashboard, dynamic Apply page with Autofill, My Applications, officer inbox, email templates, tests |

**Recommended build order (each step is demo-ready):**

1. Register, login and role-based routing.
2. Profile wizard and completeness bar.
3. Scheme feed using the existing eligibility engine.
4. Apply page with **Autofill** and manual fill, then draft / submit.
5. Officer review of applications and status tracking.
6. Profile → golden record linking.
7. Weekly digest and new-scheme emails (start with `ConsoleEmailSender`).

> **Timeline fit:** build steps 1–4 during Synopsis Step 5 (December) once the core pipeline works, steps 5–7 during Step 6 (Jan–Feb). The system already works for officers without this portal, so the farmer portal is safe to build last without risking your core demo.

### 16.13 Privacy and safety checklist

- Passwords hashed with bcrypt; JWT expiry set; HTTPS in any real deployment.
- Farmers can view and edit only their own profile and applications.
- No full Aadhaar or bank account number stored in the profile; bank account typed per application.
- Explicit consent tick-box at signup; email opt-out and unsubscribe link.
- Every officer decision on an application is written to `audit_log`.
- Profile fields are marked self-declared until an officer verifies the linked golden record.

## Appendix A – Build Order and Prompt Sequence

Give the AI one step at a time. Each prompt assumes this file is attached. After each step, run the tests and commit before moving on.

| # | Step | Prompt to give the AI |
|---|---|---|
| 1 | Repo skeleton | "Using Section 7.1 and Appendix B, create the monorepo skeleton: backend (FastAPI app with a health endpoint, config, db session), frontend (Vite + React + TS), docker-compose for PostgreSQL, .env.example, .gitignore, pre-commit config, GitHub Actions CI." |
| 2 | Database | "Implement SQLAlchemy models and an Alembic migration for every table in Section 5 and Section 16.8. Add indexes listed in Section 5. Add repositories with basic CRUD." |
| 3 | Synthetic data | "Write scripts/generate_synthetic_data.py exactly as in Section 4.2 (5,000 true farmers, 5 source CSVs, noise injection, planted duplicate problems, separate ground_truth.csv)." |
| 4 | Ingestion | "Implement Module 1: SourceAdapter base class, one adapter per source in Section 4.1, and IngestionService that writes source_records." |
| 5 | Preprocessing | "Implement Module 2 normalizers with unit tests (name, phonetic key, mobile, village code, dob) and a pipeline that fills clean_records." |
| 6 | Matching baseline | "Implement Module 3 stages 1 and 2: blocking, pair features, and a baseline rule + fuzzy matcher. Add tests using the synthetic ground truth." |
| 7 | ML matcher | "Implement stages 3 to 5: train XGBoost in scripts/train_matcher.py, thresholds from config, connected-component clustering with the chain guard, golden-record survivorship, and ResolutionService.run()." |
| 8 | Rules | "Implement Module 4 duplicate rules (one class per rule) and Module 5 YAML eligibility engine, then Module 6 recommendation and exclusion queries." |
| 9 | Auth and core API | "Implement JWT auth with roles admin, officer, farmer and all officer endpoints in Section 8 with Pydantic schemas and tests. Export OpenAPI to docs/openapi.json." |
| 10 | Reports | "Implement /reports/summary, /reports/coverage and CSV export." |
| 11 | Officer frontend | "Build the officer pages in Section 9 against mock JSON that matches docs/openapi.json, then switch to the real API through one config flag." |
| 12 | Farmer backend | "Implement Section 16: registration, profile with completeness, scheme feed, form loader, autofill function and /applications/prefill, applications lifecycle, officer decision endpoint." |
| 13 | Farmer frontend | "Build the farmer pages in Section 16.10: register, 4-step profile wizard, dashboard feed, scheme details, dynamic Apply page with Autofill / Fill manually, My Applications, settings, and the officer applications inbox." |
| 14 | Linking and email | "Implement profile_linker (Section 16.4) reusing resolution modules, then NotificationService with EmailSender, ConsoleEmailSender, SmtpEmailSender, email_log, Jinja2 templates and the send_digest CLI job." |
| 15 | Evaluation | "Write the evaluation notebook and endpoint from Section 10: precision, recall, F1, baselines, blocking metrics, threshold curve, SHAP top features for the review queue." |

## Appendix B – Dependencies, Environment and Docker

**backend/requirements.txt (unpinned, pin after first install)**

```text
fastapi
uvicorn[standard]
sqlalchemy>=2.0
alembic
psycopg2-binary
pydantic>=2
pydantic-settings
pyjwt
passlib[bcrypt]
python-multipart
pandas
numpy
rapidfuzz
jellyfish
scikit-learn
xgboost
shap
networkx
joblib
pyyaml
faker
jinja2
apscheduler
pytest
httpx
ruff
black
```

**frontend dependencies**

```text
react, react-dom, react-router-dom, @tanstack/react-query, axios,
tailwindcss, recharts, typescript, vite,
vitest, @testing-library/react, msw, eslint, prettier
```

**.env.example**

```bash
DATABASE_URL=postgresql+psycopg2://agri:agri@localhost:5432/agri
JWT_SECRET=change-me
JWT_EXPIRE_MINUTES=120
MATCHER_PATH=models/matcher.joblib
AUTO_LINK_THRESHOLD=0.90
REVIEW_THRESHOLD=0.60
APP_BASE_URL=http://localhost:5173
EMAIL_BACKEND=console        # console | smtp
EMAIL_FROM=no-reply@agri.local
SMTP_HOST=localhost          # MailHog: localhost:1025
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
```

**docker-compose.yml (PostgreSQL, optional MailHog for email demo)**

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: agri
      POSTGRES_PASSWORD: agri
      POSTGRES_DB: agri
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]
  mailhog:
    image: mailhog/mailhog
    ports: ["1025:1025", "8025:8025"]   # SMTP and web UI
volumes:
  pgdata:
```
