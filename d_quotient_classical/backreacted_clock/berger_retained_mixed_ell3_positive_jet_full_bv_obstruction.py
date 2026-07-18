#!/usr/bin/env python3
"""Exact full-BV first-page obstruction to removing retained mixed ell3.

The certificate consumed here is the terminal gate for the summed,
pre-reduction PBW filtration through order two.  A normalized functional on
the coupled zero/first-page target annihilates every admissible cyclic
super-cotangent column and evaluates to one on the residual.  Since filtered
higher-jet profiles cannot enter the first associated-graded page, this is an
order-one obstruction to an order-two removal, not a request to enlarge the
ansatz to q4.

Dependency tag: LOCAL-ALGEBRAIC.  Generality: G0.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Mapping

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_order_two_full_bv_redefinition as core,
)


ROOT = core.ROOT
OUTPUT = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_POSITIVE_JET_FULL_BV_OBSTRUCTION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-retained-mixed-ell3-positive-jet-full-bv-obstruction-v1.schema.json"
REPORT = ROOT / "d_quotient_classical/reports/berger-retained-mixed-ell3-positive-jet-full-bv-obstruction.md"
VERIFIER = ROOT / "d_quotient_classical/backreacted_clock/verify_berger_retained_mixed_ell3_positive_jet_full_bv_obstruction.py"
TESTS = ROOT / "d_quotient_classical/backreacted_clock/tests/test_berger_retained_mixed_ell3_positive_jet_full_bv_obstruction.py"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _coefficient(text: str) -> sp.Expr:
    return sp.sympify(text, locals={"sqrt": sp.sqrt})


def _actual_first_key(record: Mapping[str, object]) -> tuple[int, tuple]:
    axis = int(record["axis"])
    term = []
    for value in record["term"]:
        if isinstance(value, list):
            word = tuple(int(entry) for entry in value)
            term.append((axis,) if word == (0,) else word)
        else:
            term.append(int(value))
    return int(record["output"]), tuple(term)


def target_pairing(value: Mapping[str, object]) -> sp.Expr:
    """Replay the normalized functional on the native first-page residual."""

    targets = core.first_page_targets()
    pairing = sp.S(0)
    for record in value["obstruction_witness"]["weights"]:
        if int(record["page"]) != 1:
            continue
        key = _actual_first_key(record)
        pairing += _coefficient(str(record["coefficient"])) * targets[int(record["axis"])].get(key, 0)
    return sp.factor(pairing)


def validate(value: Mapping[str, object], *, verify_sources: bool = True) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    witness = value["obstruction_witness"]
    if len(witness["weights"]) != witness["support_count"]:
        raise ValueError("witness support count drifted")
    if target_pairing(value) != 1:
        raise ValueError("normalized obstruction pairing drifted")
    replay = witness["exhaustive_transpose_replay"]
    if replay["zero_label_columns_checked"] != 5984:
        raise ValueError("zero-page column ledger drifted")
    if replay["first_label_columns_checked_per_axis"] != 14998:
        raise ValueError("first-page column ledger drifted")
    if replay["zero_column_defects"] or replay["first_column_defects_per_axis"] != [0, 0, 0, 0]:
        raise ValueError("stored exhaustive transpose replay is not exact")
    flags = value["claim_flags"]
    if not flags["FILTERED_CYCLIC_REDEFINITION_OBSTRUCTED_AT_FIRST_PAGE"]:
        raise ValueError("certificate lost its terminal obstruction flag")
    if flags["RESIDUAL_COHOMOLOGY_OPERATION_NONZERO"] or flags["BRANCH_PROJECTION_DECIDED"]:
        raise ValueError("certificate crosses its residual-physics boundary")
    if verify_sources:
        for relative, digest in value["dependency_refs"].items():
            if _sha256(ROOT / relative) != digest:
                raise ValueError(f"dependency digest drifted: {relative}")
        for relative, digest in value["source_manifest"].items():
            if _sha256(ROOT / relative) != digest:
                raise ValueError(f"source digest drifted: {relative}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-source-check", action="store_true")
    args = parser.parse_args()
    value = json.loads(OUTPUT.read_text())
    validate(value, verify_sources=not args.no_source_check)
    print(f"{value['result_id']} verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
