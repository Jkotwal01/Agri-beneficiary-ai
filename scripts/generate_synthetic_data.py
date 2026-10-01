"""
Synthetic data generator for Agri Beneficiary Intelligence.

Spec Section 4.2:
  - 5,000 true farmers (configurable via N_FARMERS)
  - 5 source CSVs (~12,000 rows total)
  - Realistic noise injection
  - Planted duplicate/fraud problems
  - Separate ground_truth.csv
"""

from __future__ import annotations

import random
import re
import string
from pathlib import Path

import pandas as pd
from faker import Faker

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
N_FARMERS = 5_000
SAMPLE_ROWS = 50
SOURCES = ["agristack", "pmkisan", "pmfby", "nfsm", "kcc"]
DISTRICTS = [
    "Pune",
    "Nashik",
    "Aurangabad",
    "Nagpur",
    "Kolhapur",
    "Solapur",
    "Amravati",
    "Latur",
    "Jalgaon",
    "Satara",
]
DISTRICT_CODES = {d: f"MH{str(i).zfill(3)}" for i, d in enumerate(DISTRICTS, 1)}
CROPS = ["wheat", "rice", "soybean", "cotton", "sugarcane", "jowar", "bajra", "pulse"]
SEASONS = ["kharif_2023", "rabi_2023", "kharif_2024", "rabi_2024"]
CATEGORIES = ["marginal", "small", "other"]
IRRIGATION = ["rain_fed", "canal", "drip", "bore_well"]
OWNERSHIP = ["owned", "leased", "shared"]

fake = Faker("en_IN")
Faker.seed(42)
random.seed(42)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _village_code(district: str, idx: int) -> str:
    return f"{DISTRICT_CODES[district]}V{str(idx % 200).zfill(3)}"


def _survey_no() -> str:
    return f"{random.randint(1, 500)}/{random.randint(1, 9)}"


def _bank_last4() -> str:
    return str(random.randint(1000, 9999))


def _mobile() -> str:
    return f"{random.choice(['9', '8', '7'])}{random.randint(100000000, 999999999)}"


def _inject_name_noise(name: str) -> str:
    """Randomly corrupt a name to simulate data-entry noise."""
    choice = random.random()
    if choice < 0.10:
        # Swap first / last
        parts = name.split()
        if len(parts) >= 2:
            parts[0], parts[-1] = parts[-1], parts[0]
        return " ".join(parts)
    if choice < 0.20:
        # Truncate to initial
        parts = name.split()
        if len(parts) >= 2:
            parts[0] = parts[0][0] + "."
        return " ".join(parts)
    if choice < 0.28:
        # w <-> v substitution
        return re.sub(r"[wW]", lambda m: "v" if m.group().islower() else "V", name)
    if choice < 0.35:
        # aa -> a compression
        return name.replace("aa", "a").replace("AA", "A")
    if choice < 0.40:
        # Random char typo
        idx = random.randint(0, len(name) - 1)
        replacement = random.choice(string.ascii_lowercase)
        return name[:idx] + replacement + name[idx + 1 :]
    return name


def _maybe_blank(value: str, prob: float = 0.08) -> str | None:
    """Return None with given probability to simulate missing data."""
    return None if random.random() < prob else value


# ---------------------------------------------------------------------------
# Step 1 – Generate true farmers
# ---------------------------------------------------------------------------
def _generate_true_farmers(n: int) -> list[dict]:
    farmers = []
    for i in range(n):
        district = random.choice(DISTRICTS)
        land_ha = round(random.uniform(0.2, 8.0), 2)
        category = (
            "marginal" if land_ha <= 1.0 else "small" if land_ha <= 2.0 else "other"
        )
        farmers.append(
            {
                "true_farmer_id": f"TF{str(i).zfill(6)}",
                "name": fake.name(),
                "father_name": fake.name(),
                "dob": str(fake.date_of_birth(minimum_age=18, maximum_age=80)),
                "gender": random.choice(["M", "F"]),
                "mobile": _mobile(),
                "district": district,
                "district_code": DISTRICT_CODES[district],
                "village_code": _village_code(district, i),
                "survey_no": _survey_no(),
                "bank_last4": _bank_last4(),
                "land_ha": land_ha,
                "category": category,
                "crop": random.choice(CROPS),
                "crop_group": random.choice(["cereal", "pulse", "cash"]),
                "irrigation_type": random.choice(IRRIGATION),
                "ownership_type": random.choice(OWNERSHIP),
                "agristack_id": (
                    f"AS{str(i).zfill(8)}" if random.random() > 0.15 else None
                ),
                "season": random.choice(SEASONS),
                "credit_limit": round(random.uniform(10000, 200000), 2),
                "seed_subsidy_amt": round(random.uniform(500, 5000), 2),
                "enrolled_schemes": random.sample(SOURCES, k=random.randint(1, 4)),
            }
        )
    return farmers


# ---------------------------------------------------------------------------
# Step 2 – Build source CSVs with noise
# ---------------------------------------------------------------------------
def _build_agristack(farmer: dict, noise: bool = True) -> dict:
    name = _inject_name_noise(farmer["name"]) if noise else farmer["name"]
    return {
        "farmer_id": farmer["agristack_id"],
        "name": name,
        "father_name": _maybe_blank(farmer["father_name"]),
        "dob": farmer["dob"],
        "gender": farmer["gender"],
        "mobile": _maybe_blank(farmer["mobile"], prob=0.05),
        "village_code": farmer["village_code"],
        "district_code": farmer["district_code"],
        "_true_farmer_id": farmer["true_farmer_id"],
    }


def _build_pmkisan(farmer: dict, noise: bool = True) -> dict:
    name = _inject_name_noise(farmer["name"]) if noise else farmer["name"]
    return {
        "beneficiary_no": f"PMK{fake.unique.random_number(digits=8)}",
        "name": name,
        "father_name": _maybe_blank(farmer["father_name"]),
        "mobile": _maybe_blank(farmer["mobile"]),
        "bank_acct_last4": farmer["bank_last4"],
        "village": farmer["village_code"],
        "district": farmer["district"],
        "land_ha": farmer["land_ha"],
        "_true_farmer_id": farmer["true_farmer_id"],
    }


def _build_pmfby(farmer: dict, noise: bool = True) -> dict:
    name = _inject_name_noise(farmer["name"]) if noise else farmer["name"]
    return {
        "policy_no": f"FBY{fake.unique.random_number(digits=9)}",
        "name": name,
        "village": farmer["village_code"],
        "survey_no": farmer["survey_no"],
        "crop": farmer["crop"],
        "season": farmer["season"],
        "area_ha": round(farmer["land_ha"] * random.uniform(0.5, 1.0), 2),
        "bank_acct_last4": _maybe_blank(farmer["bank_last4"]),
        "_true_farmer_id": farmer["true_farmer_id"],
    }


def _build_nfsm(farmer: dict, noise: bool = True) -> dict:
    name = _inject_name_noise(farmer["name"]) if noise else farmer["name"]
    return {
        "app_id": f"NSM{fake.unique.random_number(digits=7)}",
        "name": name,
        "mobile": _maybe_blank(farmer["mobile"]),
        "survey_no": farmer["survey_no"],
        "crop": farmer["crop"],
        "seed_subsidy_amt": farmer["seed_subsidy_amt"],
        "season": farmer["season"],
        "_true_farmer_id": farmer["true_farmer_id"],
    }


def _build_kcc(farmer: dict, noise: bool = True) -> dict:
    name = _inject_name_noise(farmer["name"]) if noise else farmer["name"]
    return {
        "card_no": f"KCC{fake.unique.random_number(digits=10)}",
        "name": name,
        "dob": _maybe_blank(farmer["dob"]),
        "mobile": _maybe_blank(farmer["mobile"]),
        "village": farmer["village_code"],
        "land_ha": farmer["land_ha"],
        "credit_limit": farmer["credit_limit"],
        "_true_farmer_id": farmer["true_farmer_id"],
    }


_BUILDERS = {
    "agristack": _build_agristack,
    "pmkisan": _build_pmkisan,
    "pmfby": _build_pmfby,
    "nfsm": _build_nfsm,
    "kcc": _build_kcc,
}


# ---------------------------------------------------------------------------
# Step 3 – Plant problems
# ---------------------------------------------------------------------------
def _plant_duplicates(
    records: dict[str, list[dict]], farmers: list[dict]
) -> dict[str, list[dict]]:
    """
    3% duplicate enrolments (same scheme, same farmer).
    2% same-parcel double claims (pmfby, different farmers share survey_no+village).
    1% shared bank account (pmkisan, different farmers share bank_last4+district).
    """
    # 3% duplicate enrollments within the same scheme
    for rows in records.values():
        n_dups = max(1, int(len(rows) * 0.03))
        for _ in range(n_dups):
            original = random.choice(rows)
            dup = dict(original)
            # Give it a fresh ID key so it looks like a new record
            id_key = next(iter(dup.keys()))
            dup[id_key] = f"DUP{fake.unique.random_number(digits=7)}"
            rows.append(dup)

    # 2% same-parcel double-claim in pmfby
    pmfby_rows = records["pmfby"]
    n_parcel = max(1, int(len(pmfby_rows) * 0.02))
    donor_rows = random.sample(pmfby_rows, n_parcel)
    for donor in donor_rows:
        victim = dict(random.choice(farmers))
        row = _build_pmfby(victim, noise=True)
        row["survey_no"] = donor["survey_no"]
        row["village"] = donor["village"]
        pmfby_rows.append(row)

    # 1% shared bank account in pmkisan across different farmers
    pmkisan_rows = records["pmkisan"]
    n_bank = max(1, int(len(pmkisan_rows) * 0.01))
    donor_rows = random.sample(pmkisan_rows, n_bank)
    for donor in donor_rows:
        victim = dict(random.choice(farmers))
        row = _build_pmkisan(victim, noise=True)
        row["bank_acct_last4"] = donor["bank_acct_last4"]
        pmkisan_rows.append(row)

    return records


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
def generate(
    out_dir: str | Path = "data/synthetic",
    n_farmers: int = N_FARMERS,
    sample_rows: int = SAMPLE_ROWS,
) -> Path:
    """Generate all synthetic CSVs and ground_truth. Returns out_dir as Path."""
    out_dir = Path(out_dir)
    samples_dir = out_dir / "samples"
    out_dir.mkdir(parents=True, exist_ok=True)
    samples_dir.mkdir(parents=True, exist_ok=True)

    # 1. True farmers
    farmers = _generate_true_farmers(n_farmers)

    # 2. Source records
    records: dict[str, list[dict]] = {s: [] for s in SOURCES}
    truth_rows: list[dict] = []

    for farmer in farmers:
        for source in farmer["enrolled_schemes"]:
            row = _BUILDERS[source](farmer, noise=True)
            records[source].append(row)
            # Primary key column is first column
            pk_col = next(iter(row.keys()))
            truth_rows.append(
                {
                    "source": source,
                    "source_row_pk": row[pk_col],
                    "true_farmer_id": farmer["true_farmer_id"],
                }
            )

    # 3. Plant problems
    records = _plant_duplicates(records, farmers)

    # 4. Save full CSVs
    file_map = {
        "agristack": "agristack_farmers.csv",
        "pmkisan": "pmkisan.csv",
        "pmfby": "pmfby.csv",
        "nfsm": "nfsm.csv",
        "kcc": "kcc.csv",
    }
    for source, filename in file_map.items():
        df = pd.DataFrame(records[source]).drop(
            columns=["_true_farmer_id"], errors="ignore"
        )
        df.to_csv(out_dir / filename, index=False)
        # 50-row sample for CI (committed to git)
        df.head(sample_rows).to_csv(samples_dir / filename, index=False)

    # 5. Ground truth (never used by pipeline, only for training & evaluation)
    gt_df = pd.DataFrame(truth_rows)
    gt_df.to_csv(out_dir / "ground_truth.csv", index=False)
    gt_df.head(sample_rows).to_csv(samples_dir / "ground_truth.csv", index=False)

    print(f"[generate] Done. Output dir: {out_dir.resolve()}")
    for source, filename in file_map.items():
        df = pd.read_csv(out_dir / filename)
        print(f"  {filename}: {len(df)} rows")
    print(f"  ground_truth.csv: {len(gt_df)} rows")

    return out_dir


if __name__ == "__main__":
    generate()
