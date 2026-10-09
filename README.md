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

## Local Setup

### 1. Running the Backend
Navigate to the `backend` directory, activate the virtual environment, and start the FastAPI server:

```powershell
cd backend
# Create virtual environment (if not already created)
# python -m venv .venv

# Activate virtual environment (Windows)
.\.venv\Scripts\activate
# For Linux/Mac use: source .venv/bin/activate

# Install dependencies (first time only)
# pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload
```
*(Alternatively on Windows, you can directly run `.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload`)*

### 2. Running the Frontend
In a separate terminal, navigate to the `frontend` directory, install dependencies, and start the development server:

```powershell
cd frontend
# Install dependencies (first time only)
# npm install

# Run the frontend server
npm run dev
```

---
See `docs/Agri_Beneficiary_Intelligence_Spec.md` and `docs/IMPLEMENTATION_PLAN.md` for full technical and architectural details.
