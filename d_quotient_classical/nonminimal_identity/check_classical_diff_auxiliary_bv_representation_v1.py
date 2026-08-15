#!/usr/bin/env python3
"""Independent component replay for the shifted auxiliary Diff actions."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "d_quotient_classical/certificates/CLASSICAL_DIFF_AUXILIARY_BV_REPRESENTATION_V1.json"
ACTION = ROOT / "covariant_completion/certificates/curved_auxiliary_action_definition.json"
SPLIT = ROOT / "covariant_completion/certificates/curved_auxiliary_canonical_split.json"
PREDECESSOR = ROOT / "d_quotient_classical/certificates/CLASSICAL_HH_HV_AUXILIARY_SHIFT_V1.json"
DIM = 4
ZERO = (0, 0, 0, 0)


def unit(axis: int) -> tuple[int, ...]:
    return tuple(int(index == axis) for index in range(DIM))


def symmetric(prefix: str, left: int, right: int) -> str:
    left, right = sorted((left, right))
    return f"{prefix}_{left}{right}"


def expected(field: str) -> dict[tuple[Any, ...], Fraction]:
    totals: dict[tuple[Any, ...], Fraction] = defaultdict(Fraction)
    components = tuple((mu, nu) for mu in range(DIM) for nu in range(mu, DIM)) if field == "f_hat" else tuple((mu,) for mu in range(DIM))
    for component in components:
        mu = component[0]
        output = symmetric(field, *component) if len(component) == 2 else f"{field}_{mu}"
        for rho in range(DIM):
            totals[(output, f"c_{rho}", ZERO, output, unit(rho))] += 1
            if len(component) == 1:
                totals[(output, f"c_{rho}", unit(mu), f"{field}_{rho}", ZERO)] += 1
            else:
                nu = component[1]
                totals[(output, f"c_{rho}", unit(mu), symmetric(field, rho, nu), ZERO)] += 1
                totals[(output, f"c_{rho}", unit(nu), symmetric(field, mu, rho), ZERO)] += 1
    return {key: coefficient for key, coefficient in totals.items() if coefficient}


def actual(entries: list[dict[str, Any]]) -> dict[tuple[Any, ...], Fraction]:
    return {
        (item["output_row"], item["ghost_row"], tuple(item["ghost_jet"]), item["field_row"], tuple(item["field_jet"])): Fraction(item["coefficient"])
        for item in entries
    }


def canonical_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    tables = value.get("representation_tables", [])
    by_symbol = {table.get("field_symbol"): table for table in tables}
    expected_counts = {"f_hat": 104, "v": 32, "eta": 32}
    if set(by_symbol) != set(expected_counts):
        errors.append("three-field table inventory mismatch")
    for symbol, count in expected_counts.items():
        table = by_symbol.get(symbol, {})
        entries = table.get("ordered_field_action_entries", [])
        if actual(entries) != expected(symbol):
            errors.append(f"{symbol} Lie-derivative component replay mismatch")
        if len(entries) != count or table.get("nonzero_ordered_field_coefficients") != count:
            errors.append(f"{symbol} component count mismatch")
        if table.get("sha256") != canonical_digest(entries):
            errors.append(f"{symbol} component digest mismatch")

    pins = {item.get("path"): item.get("sha256") for item in value.get("provenance", {}).get("inputs", [])}
    expected_pins = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in (ACTION, SPLIT, PREDECESSOR)}
    summary = value.get("component_summary", {})
    flags = value.get("claim_flags", {})
    if value.get("result_id") != "CLASSICAL_DIFF_AUXILIARY_BV_REPRESENTATION_V1":
        errors.append("result identity mismatch")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]:
        errors.append("dependency boundary mismatch")
    if pins != expected_pins:
        errors.append("source provenance pins mismatch")
    if summary != {"families": 3, "ordered_field_coefficients": 168, "by_family": {
        "DIFF_C_F_HAT_F_HAT_STAR": 104,
        "DIFF_C_V_V_STAR": 32,
        "DIFF_C_ETA_ETA_STAR": 32,
    }}:
        errors.append("component summary mismatch")
    if value.get("canonical_hashes", {}).get("representation_tables_sha256") != canonical_digest(tables):
        errors.append("representation-table digest mismatch")
    if value.get("naturality_derivation", {}).get("all_three_actions_source_forced") is not True:
        errors.append("source naturality boundary mismatch")
    expected_flags = {
        "THREE_DIFF_AUXILIARY_FIELD_ACTIONS_SOURCE_FORCED": True,
        "THREE_DIFF_AUXILIARY_FIELD_COMPONENT_TABLES_SERIALIZED": True,
        "THREE_DIFF_AUXILIARY_BV_COTANGENT_LIFTS_SERIALIZED": False,
        "FULL_SOURCE_Q2_PULLBACK_REPLAYED": False,
        "EXHAUSTIVE_FULL_NONLINEAR_BV_FAMILY_CENSUS": False,
        "CLASSICAL_IMPORT_GATE_PASSED": False,
        "HADAMARD_STATE_CONSTRUCTED": False,
        "QME_RESTORED": False,
    }
    for name, expected_value in expected_flags.items():
        if flags.get(name) is not expected_value:
            errors.append(f"claim flag drift: {name}")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("CLASSICAL_DIFF_AUXILIARY_BV_REPRESENTATION_V1_INDEPENDENT_COMPONENT_REPLAY: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print(json.dumps(value["component_summary"], sort_keys=True))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
