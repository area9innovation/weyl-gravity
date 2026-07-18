#!/usr/bin/env python3
"""Independent checks for the jet-aware transverse Nariai middle gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-jet-aware-middle-schur-variation-v1.schema.json"


def verify() -> None:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if not all(value["exact_checks"].values()):
        raise AssertionError("a jet-aware middle check failed")
    defects = value["exact_data"]["identity_defects"]
    for name in ("corrected_first_square_variation", "parent_YM_variation"):
        if defects[name]["nonzero_coefficients"] != 0:
            raise AssertionError(f"identity defect survived: {name}")
    if defects["shifted_chain_variation"]["nonzero_coefficients"] == 0:
        raise AssertionError("shifted-chain obstruction disappeared")
    comparison = value["exact_data"]["frozen_parallel_comparison"]
    if not comparison["coefficients_differ"]:
        raise AssertionError("jet-aware result collapsed to frozen shortcut")
    operators = value["exact_data"]["operator_variations"]
    if operators["unsupported_parent_identity_curvature_jet_words"]:
        raise AssertionError("parent identity has incomplete curvature-jet coverage")
    if not operators["unsupported_requested_curvature_jet_words"]:
        raise AssertionError("endpoint higher-jet limitation was not recorded")
    gate = value["exact_data"]["differential_schur_gate"]
    if gate["algebraic_qdot_sufficient"] is not False:
        raise AssertionError("algebraic Schur ansatz was not rejected")
    if not any(len(word) != 1 for word in gate["non_algebraically_repairable_orders"]):
        raise AssertionError("non-algebraic PBW order witness missing")
    for flag in (
        "TRANSVERSE_SHIFTED_CHAIN_VARIATION",
        "TRANSVERSE_ALGEBRAIC_SCHUR_VARIATION",
        "TRANSVERSE_COMPLETE_CURVATURE_JET_COVERAGE",
        "TRANSVERSE_ACTION_DERIVED_SCHUR_VARIATION",
        "TRANSVERSE_CYCLIC_SCHUR_VARIATION",
        "TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION",
        "TRANSVERSE_CAUSAL_TRANSFER",
    ):
        if value["flags"][flag] is not False:
            raise AssertionError(f"downstream flag promoted: {flag}")
    for path, digest in value["source_manifest"].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != digest:
            raise AssertionError(f"source drift: {path}")


if __name__ == "__main__":
    verify()
    print("NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1 independent verification: PASS")
