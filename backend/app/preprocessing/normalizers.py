"""
Six pure normalizer functions — Module 2 (Spec Section 6, Module 2).

All functions are stateless and have no database dependency.
Each can be unit-tested in complete isolation.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path

import jellyfish

# ---------------------------------------------------------------------------
# 1. normalize_name
# ---------------------------------------------------------------------------
_HONORIFICS = re.compile(
    r"\b(shri|smt|mr|mrs|ms|dr|prof|kumari|km|sh|late)\b\.?",
    re.IGNORECASE,
)
_PUNCT = re.compile(r"[^\w\s]")
_SPACES = re.compile(r"\s+")

# Common transliteration variants (Indian names)
_TRANSLITERATION = [
    (re.compile(r"w"), "v"),  # w → v everywhere (Kotwal→Kotval, Wagh→Vagh)
    (re.compile(r"aa"), "a"),  # aa → a (Raam → Ram)
    (re.compile(r"ee"), "i"),  # ee → i (Deevi → Divi)
    (re.compile(r"oo"), "u"),  # oo → u
]


def normalize_name(name: str | None) -> str | None:
    """
    Lowercase, remove honorifics, strip punctuation, collapse whitespace,
    fold common transliteration variants.
    Returns None if the result is empty.
    """
    if not name or not name.strip():
        return None
    s = name.strip().lower()
    s = _HONORIFICS.sub("", s)
    s = _PUNCT.sub(" ", s)
    for pattern, replacement in _TRANSLITERATION:
        s = pattern.sub(replacement, s)
    s = _SPACES.sub(" ", s).strip()
    return s if s else None


# ---------------------------------------------------------------------------
# 2. phonetic_key
# ---------------------------------------------------------------------------
def phonetic_key(token: str | None) -> str | None:
    """
    Metaphone of the first name token so Kotwal and Kotval share a key.
    We normalise w→v first so that transliteration variants converge.
    Uses jellyfish.metaphone (jellyfish >= 1.x dropped double_metaphone).
    """
    if not token or not token.strip():
        return None
    first_token = token.strip().split()[0].lower()
    # Normalise common transliteration before phonetic encoding
    first_token = re.sub(r"w", "v", first_token)  # w → v (Kotwal → Kotval)
    first_token = re.sub(r"aa", "a", first_token)  # aa → a
    first_token = re.sub(r"ee", "i", first_token)  # ee → i
    return jellyfish.metaphone(first_token) or None


# ---------------------------------------------------------------------------
# 3. normalize_mobile
# ---------------------------------------------------------------------------
_NON_DIGIT = re.compile(r"\D")
_INVALID_MOBILE = re.compile(r"^(0{10}|1{10}|9{10})$")


def normalize_mobile(mobile: str | None) -> str | None:
    """
    Strip non-digits, keep last 10 digits, validate Indian mobile prefix.
    Returns None for invalid/missing numbers.
    """
    if not mobile:
        return None
    digits = _NON_DIGIT.sub("", mobile)
    if len(digits) > 10:
        digits = digits[-10:]
    if len(digits) != 10:
        return None
    if _INVALID_MOBILE.match(digits):
        return None
    # Indian mobiles start with 6, 7, 8, or 9
    if digits[0] not in "6789":
        return None
    return digits


# ---------------------------------------------------------------------------
# 4. normalize_village
# ---------------------------------------------------------------------------
_VILLAGE_LOOKUP: dict[str, str] = {}  # populated lazily on first call


def _load_village_lookup(csv_path: Path | None = None) -> dict[str, str]:
    """Load village name → LGD code mapping from CSV."""
    if _VILLAGE_LOOKUP:
        return _VILLAGE_LOOKUP
    default = Path(__file__).parent / "data" / "village_lookup.csv"
    path = csv_path or default
    if not path.exists():
        return {}
    import csv

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("village_name", "").strip().lower()
            code = row.get("village_code", "").strip()
            if name and code:
                _VILLAGE_LOOKUP[name] = code
    return _VILLAGE_LOOKUP


def normalize_village(
    village: str | None,
    lookup_path: Path | None = None,
) -> str | None:
    """
    Map village spelling → LGD village_code via lookup CSV.
    Unknown names: fuzzy nearest match (Jaro-Winkler ≥ 0.88) else return as-is.
    """
    if not village or not village.strip():
        return None
    raw = village.strip().lower()
    lookup = _load_village_lookup(lookup_path)

    # Exact match
    if raw in lookup:
        return lookup[raw]

    # If it already looks like a code (alphanum with no spaces) return it
    if re.match(r"^[A-Z0-9]+$", village.strip()):
        return village.strip()

    # Fuzzy nearest
    best_score = 0.0
    best_code = village.strip()  # fallback: return as-is
    for name, code in lookup.items():
        score = jellyfish.jaro_winkler_similarity(raw, name)
        if score > best_score:
            best_score = score
            best_code = code
    if best_score >= 0.88:
        return best_code
    return village.strip()  # unknown → return raw value unchanged


# ---------------------------------------------------------------------------
# 5. parse_dob
# ---------------------------------------------------------------------------
_DOB_FORMATS = [
    "%d-%m-%Y",
    "%d/%m/%Y",
    "%Y-%m-%d",
    "%d-%b-%Y",
    "%d %b %Y",
    "%B %d %Y",
    "%d-%B-%Y",
    "%Y/%m/%d",
]


def parse_dob(dob_str: str | None) -> date | None:
    """
    Accept common date formats. Returns a date object or None.
    If only the year is reliable the caller can use .year.
    """
    if not dob_str or not dob_str.strip():
        return None
    s = dob_str.strip()
    # Try known formats
    for fmt in _DOB_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()  # noqa: DTZ007
        except ValueError:
            continue
    # Last resort: try to extract a 4-digit year
    match = re.search(r"\b(19|20)\d{2}\b", s)
    if match:
        return date(int(match.group()), 1, 1)  # year-only placeholder
    return None


# ---------------------------------------------------------------------------
# 6. fill_missing
# ---------------------------------------------------------------------------
def fill_missing(value: object) -> object:
    """
    Policy: never invent values. Return the value unchanged.
    None stays None; the feature builder handles missing as neutral.
    """
    return value
