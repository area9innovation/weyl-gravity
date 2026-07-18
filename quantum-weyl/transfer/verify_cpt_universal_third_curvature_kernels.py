#!/usr/bin/env python3
"""Independent verifier for the five imported CPT third-curvature kernels."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "certificates/CPT_UNIVERSAL_THIRD_CURVATURE_KERNELS.json"
SCHEMA = HERE / "schema/cpt-universal-third-curvature-kernels-v1.schema.json"
EXPECTED_FORMULA_DIGEST = "39ae359ce36b4b7083b72fccfc50d554285956695a224a6700b4ca1ed2e31621"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(value: dict[str, Any] | None = None) -> dict[str, Any]:
    stored = json.loads(OUTPUT.read_text()) if value is None else value
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(stored)
    if stored["formula_digest"] != EXPECTED_FORMULA_DIGEST:
        raise ValueError("CPT formula digest drifted")
    rows = stored["universal_kernels"]
    if [row["carrier_id"] for row in rows] != ["I10", "I24", "I25", "I28", "I29"]:
        raise ValueError("CPT carrier order or coverage drifted")
    if [row["stabilizer_order"] for row in rows] != [6, 2, 2, 2, 3]:
        raise ValueError("CPT stabilizer orders drifted")
    if [row["gamma_box_homogeneity"] for row in rows] != [-1, -2, -2, -3, -4]:
        raise ValueError("CPT kernel homogeneities drifted")

    symbols = {name: sp.symbols(name) for name in ("a1", "a2", "a3", "d1", "d2", "d3", "L12", "L13", "L23")}
    parsed = {
        row["carrier_id"]: {
            key: sp.sympify(row[key], locals=symbols)
            for key in ("raw_alpha_numerator_dff", "raw_tree_term", "raw_log_term")
        }
        for row in rows
    }
    a1, a2, a3 = (symbols[name] for name in ("a1", "a2", "a3"))
    d1, d2, d3 = (symbols[name] for name in ("d1", "d2", "d3"))
    L12, L23 = symbols["L12"], symbols["L23"]
    exact_controls = {
        "I10_dff": parsed["I10"]["raw_alpha_numerator_dff"] - a1 * a2 * a3 / 3,
        "I10_tree": parsed["I10"]["raw_tree_term"] - (sp.Rational(1, 270) / d3 - d1 / (540 * d2 * d3)),
        "I24_log": parsed["I24"]["raw_log_term"] + L23 / (30 * d1),
        "I25_log": parsed["I25"]["raw_log_term"] + 2 * L12 / (15 * d3),
        "I28_dff": parsed["I28"]["raw_alpha_numerator_dff"] - 8 * a1**2 * a2**2 * a3 / (3 * d1 * d2),
        "I29_dff": parsed["I29"]["raw_alpha_numerator_dff"] - 8 * a1**2 * a2**2 * a3**2 / (3 * d1 * d2 * d3),
    }
    if any(sp.simplify(residual) != 0 for residual in exact_controls.values()):
        raise ValueError("one or more independently reconstructed CPT terms drifted")

    rows_digest = hashlib.sha256(
        json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if rows_digest != stored["formula_digest"]:
        raise ValueError("stored CPT row serialization does not match its digest")
    for reference in stored["dependencies"].values():
        path = ROOT / reference["path"]
        if not path.exists() or _sha256(path) != reference["sha256"]:
            raise ValueError(f"CPT dependency hash drifted: {reference['path']}")
    flags = stored["claim_flags"]
    if not all(
        flags[name]
        for name in (
            "FIVE_UNIVERSAL_CPT_KERNELS_IMPORTED",
            "SOURCE_SCALAR_FIXTURE_COEFFICIENTS_COMPUTED",
            "KERNEL_STABILIZERS_EXACTLY_VERIFIED",
            "KERNEL_HOMOGENEITIES_EXACTLY_VERIFIED",
        )
    ):
        raise ValueError("CPT positive claim flags drifted")
    if any(
        flags[name]
        for name in (
            "REPOSITORY_GENERIC_BACKGROUND_TRACE_SUBSTITUTION_SUPPLIED",
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED",
            "REPOSITORY_CUBIC_COEFFICIENTS_COMPUTED",
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED",
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED",
            "RESIDUAL_TRANSFER_AUTHORIZED",
            "LORENTZIAN_CERTIFIED",
        )
    ):
        raise ValueError("CPT import crossed its fail-closed boundary")
    if stored["repository_matching_audit"]["verdict"] != "NO_REPOSITORY_FORM_FACTOR_COEFFICIENT_CAN_BE_INFERRED_FROM_THE_CURRENT_SPECIAL_BACKGROUND_LEDGER":
        raise ValueError("repository matching verdict drifted")
    return stored


def main() -> int:
    verify()
    print("independent CPT universal third-curvature kernel verifier: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
