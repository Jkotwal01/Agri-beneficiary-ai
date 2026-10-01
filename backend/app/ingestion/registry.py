"""Adapter registry — maps source_name → adapter class.

To add a new source: create a new adapter file and add one entry here.
Nothing else changes.
"""

from __future__ import annotations

from app.ingestion.adapters.agristack import AgriStackAdapter
from app.ingestion.adapters.kcc import KccAdapter
from app.ingestion.adapters.nfsm import NfsmAdapter
from app.ingestion.adapters.pmfby import PmfbyAdapter
from app.ingestion.adapters.pmkisan import PmKisanAdapter
from app.ingestion.base import SourceAdapter

ADAPTER_REGISTRY: dict[str, type[SourceAdapter]] = {
    "agristack": AgriStackAdapter,
    "pmkisan": PmKisanAdapter,
    "pmfby": PmfbyAdapter,
    "nfsm": NfsmAdapter,
    "kcc": KccAdapter,
}

SOURCE_FILES: dict[str, str] = {
    "agristack": "agristack_farmers.csv",
    "pmkisan": "pmkisan.csv",
    "pmfby": "pmfby.csv",
    "nfsm": "nfsm.csv",
    "kcc": "kcc.csv",
}
