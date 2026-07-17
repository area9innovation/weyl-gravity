#!/usr/bin/env python3
"""Independent replay of the compact-source retarded Maxwell theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_RETARDED_COMPACT_SOURCE_MAXWELL_SIGNAL.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-retarded-compact-source-maxwell-signal-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _wedge(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, tuple[int, ...]] | None:
    if set(left) & set(right):
        return None
    inversions = sum(1 for a in left for b in right if a > b)
    return (-1 if inversions % 2 else 1), tuple(sorted(left + right))


def _independent_source_check(certificate: dict) -> None:
    chi0, chi3, chi03 = sp.symbols("chi_0 chi_3 chi_03")
    # d(chi dx1^dx2)
    current = {(0, 1, 2): chi0, (1, 2, 3): chi3}
    closure: dict[tuple[int, ...], sp.Expr] = {}
    for mu, basis, derivative in (
        (3, (0, 1, 2), chi03),
        (0, (1, 2, 3), chi03),
    ):
        product = _wedge((mu,), basis)
        if product is None:
            continue
        sign, target = product
        closure[target] = sp.expand(closure.get(target, 0) + sign * derivative)
    closure = {basis: value for basis, value in closure.items() if value != 0}
    if closure:
        raise AssertionError(f"independent d-squared check failed: {closure}")
    expected = certificate["source_class"]["exact_components"]
    if expected["current_three_form_components"] != {"012": "chi_0", "123": "chi_3"}:
        raise AssertionError("current components drifted")
    if expected["current_one_form_components"] != {"0": "-chi_3", "3": "-chi_0"}:
        raise AssertionError("Lorentzian Hodge signs drifted")
    if expected["closure_components"] != {}:
        raise AssertionError("persisted current is not closed")
    if current[(0, 1, 2)] == 0:
        raise AssertionError("nonzero source witness disappeared")


def main() -> int:
    certificate = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(certificate)
    for dependency in certificate["dependency_refs"].values():
        path = ROOT / dependency["path"]
        if _sha256(path) != dependency["sha256"]:
            raise AssertionError(f"dependency drift: {path}")
        data = json.loads(path.read_text())
        if data["result_id"] != dependency["result_id"]:
            raise AssertionError(f"dependency result mismatch: {path}")
    for source in certificate["provenance"]["source_manifest"]:
        if _sha256(ROOT / source["path"]) != source["sha256"]:
            raise AssertionError(f"source manifest drift: {source['path']}")
    _independent_source_check(certificate)
    if certificate["bv_source_injection"]["endpoint_36_rows"] != [31, 32, 33, 34]:
        raise AssertionError("source is not in all four endpoint Maxwell equation rows")
    if certificate["bv_source_injection"]["full_64_rows"] != [59, 60, 61, 62]:
        raise AssertionError("source is not in all four full Maxwell equation rows")
    if certificate["retarded_signal"]["support"] != "supp(F_ret) subset J_plus(supp j)":
        raise AssertionError("retarded support orientation drifted")
    if certificate["flags"]["BERGER_RETARDED_COMPACT_SOURCE_MAXWELL_SIGNAL"] is not True:
        raise AssertionError("retarded signal flag dropped")
    for flag in (
        "BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE",
        "BERGER_MAXWELL_BACKREACTION",
        "BERGER_G1_COMPLETE_SIGNAL_SECTOR",
        "BERGER_HADAMARD_DATA",
        "QUANTUM_CLAIM",
    ):
        if certificate["flags"][flag] is not False:
            raise AssertionError(f"downstream flag promoted: {flag}")
    print("BERGER_RETARDED_COMPACT_SOURCE_MAXWELL_SIGNAL independent replay: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
