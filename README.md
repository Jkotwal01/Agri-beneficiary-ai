# Agri Beneficiary Intelligence

## The Problem
Every agricultural welfare scheme (PM-KISAN, PMFBY, KCC, NFSM, state subsidies) keeps its own disconnected farmer list. The same farmer appears under different name variations (e.g., "Ramesh Kotwal", "Kotwal Ramesh S.", and "R. Kotval") in different databases. The result is duplicate subsidies, eligible farmers who never receive their benefits due to coverage gaps, and an extremely slow manual verification process.

## Our Solution
We are building an AI-powered Integrated Beneficiary Intelligence System that:
1. **Ingests and Cleans:** Loads farmer records from various scheme databases and normalizes the data.
2. **Fuzzy Matching & ML:** Uses fuzzy string matching and an XGBoost machine learning classifier to determine which records belong to the same real farmer.
3. **Golden Records:** Merges matched groups into a single, reliable "golden record" for each farmer.
4. **Rule Engine:** Detects duplicate claims, identifies eligible schemes, and flags excluded farmers using a customizable YAML rule engine.
5. **Officer Dashboard & Farmer Portal:** Provides a dashboard for government officers to verify system findings and a dedicated portal for farmers to build a profile, discover matched schemes, and apply using 1-click autofill.

## Quick Start

### 0. Infrastructure
From the repo root, start PostgreSQL (and MailHog for dev email):

```powershell
docker compose up -d
cp .env.example .env   # adjust DATABASE_URL / JWT_SECRET etc. as needed
```

### 1. Running the Backend
Navigate to the `backend` directory, set up a virtual environment, and start the FastAPI server:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate          # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head               # apply migrations
uvicorn app.main:app --reload
```
*(Alternatively on Windows, you can directly run `.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload`)*

Run the backend test suite (uses `TEST_DATABASE_URL` from `.env`):

```powershell
pytest
```

### 2. Running the Frontend
In a separate terminal, navigate to the `frontend` directory, install dependencies, and start the dev server:

```powershell
cd frontend
npm install
npm run dev
```

Copy the relevant `VITE_*` keys from `.env.example` into `frontend/.env`:
- `VITE_API_URL` — backend origin (default `http://localhost:8000`)
- `VITE_USE_MOCKS` — `true` to run the UI against MSW mock data instead of the real backend

### 3. Synthetic data & resolution pipeline
```powershell
cd backend
python ../scripts/generate_synthetic_data.py   # writes data/synthetic/*.csv
python ../scripts/seed_db.py                   # loads them into source_records
python scripts/train_matcher.py                # trains the XGBoost matcher (optional — a heuristic fallback is used otherwise)
```
Then trigger the pipeline via the API (`POST /pipeline/ingest`, `/pipeline/preprocess`, `/pipeline/resolve`, `/pipeline/evaluate`) or run `notebooks/02_model_evaluation.ipynb` for an end-to-end walkthrough with blocking and resolution metrics.

### 4. Weekly digest emails
```powershell
cd backend
python -m app.cli send_digest
```
Prints to the console with `EMAIL_BACKEND=console` (default), or sends via the MailHog SMTP server started by `docker compose` when set to `smtp`.

---
See `docs/Agri_Beneficiary_Intelligence_Spec.md` and `docs/IMPLEMENTATION_PLAN.md` for full technical and architectural details.
