"""
Eligibility Engine — evaluates a farmer's facts against YAML scheme rules.

evaluate(scheme_rules, facts) -> EligibilityResult
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

SCHEMES_YAML = Path(__file__).parent / "rules" / "schemes.yaml"


@dataclass
class EligibilityResult:
    scheme: str
    eligible: bool
    reasons: list[str] = field(default_factory=list)


def _load_schemes() -> dict:
    with open(SCHEMES_YAML, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _check_rule(rule: dict, facts: dict) -> str | None:
    """Return error string if rule fails, else None."""
    f_field = rule["field"]
    operator = rule["operator"]
    value = rule["value"]
    fact_val = facts.get(f_field)

    if fact_val is None:
        return rule.get("error", f"Missing field: {f_field}")

    ops = {
        "<=": lambda a, b: a <= b,
        "<": lambda a, b: a < b,
        ">=": lambda a, b: a >= b,
        ">": lambda a, b: a > b,
        "==": lambda a, b: a == b,
        "!=": lambda a, b: a != b,
        "in": lambda a, b: a in b,
    }
    fn = ops.get(operator)
    if fn is None:
        return f"Unknown operator: {operator}"
    if not fn(fact_val, value):
        return rule.get("error", f"{f_field} {operator} {value} failed")
    return None


def evaluate(scheme_name: str, facts: dict[str, Any]) -> EligibilityResult:
    """Evaluate a single scheme against a farmer facts dict."""
    schemes = _load_schemes()
    cfg = schemes.get(scheme_name)
    if not cfg or not cfg.get("active", True):
        return EligibilityResult(
            scheme=scheme_name,
            eligible=False,
            reasons=["Scheme not active or not found"],
        )
    failures: list[str] = []
    for rule in cfg.get("rules", []):
        err = _check_rule(rule, facts)
        if err:
            failures.append(err)
    return EligibilityResult(
        scheme=scheme_name,
        eligible=len(failures) == 0,
        reasons=failures,
    )


def evaluate_all(facts: dict[str, Any]) -> list[EligibilityResult]:
    """Evaluate all active schemes against farmer facts."""
    schemes = _load_schemes()
    return [
        evaluate(name, facts)
        for name, cfg in schemes.items()
        if cfg.get("active", True)
    ]
