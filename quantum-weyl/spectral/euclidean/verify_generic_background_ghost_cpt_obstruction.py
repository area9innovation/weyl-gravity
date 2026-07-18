#!/usr/bin/env python3
"""Independent replay of the generic-background Diff x Weyl ghost obstruction."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_DIFF_WEYL_GHOST_CPT_OBSTRUCTION.json"
SCHEMA = HERE / "schema/generic-background-diff-weyl-ghost-cpt-obstruction-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def verify(value: dict[str, Any] | None = None) -> dict[str, Any]:
    stored = json.loads(OUTPUT.read_text()) if value is None else value
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(stored)

    controls = stored["algebraic_Weyl_ghost_elimination"]["beta_controls"]
    if [_fraction(row["beta"]) for row in controls] != [Fraction(0), Fraction(1, 4), Fraction(1, 2)]:
        raise ValueError("ghost beta controls drifted")
    for row in controls:
        a = _fraction(row["vector_divergence_coefficient_before_elimination"])
        b = _fraction(row["gradient_weyl_coefficient"])
        c = _fraction(row["trace_divergence_coefficient"])
        d = _fraction(row["trace_weyl_coefficient"])
        if a - b * c / d != Fraction(1, 2):
            raise ValueError("independent ghost Schur replay failed")

    symbol = stored["nonminimal_principal_symbol"]
    eigenvalues = [_fraction(value) for value in symbol["eigenvalues_e0"]]
    if eigenvalues != [Fraction(3, 2), Fraction(1), Fraction(1), Fraction(1)]:
        raise ValueError("generic ghost principal spectrum drifted")
    scalarizer = symbol["fixed_two_sided_scalarizer_no_go"]
    if [_fraction(value) for value in scalarizer["relative_symbol_P0_inverse_P1_diagonal"]] != [
        Fraction(2, 3), Fraction(3, 2), Fraction(1), Fraction(1)
    ] or scalarizer["is_scalar"] is not False:
        raise ValueError("two-covector scalarizer no-go drifted")

    hodge = stored["generic_Hodge_mixing"]
    s = hodge["tracefree_Ricci_fixture"]
    k = hodge["gradient_covector_fixture"]
    mixing = [2 * sum(s[row][column] * k[column] for column in range(4)) for row in range(4)]
    if mixing != [0, 2, 0, 0] or mixing != hodge["transverse_mixing_term_2S_dot_k"]:
        raise ValueError("independent Hodge-mixing witness failed")
    if sum(s[index][index] for index in range(4)) != 0:
        raise ValueError("Hodge-mixing Ricci fixture is not tracefree")

    if stored["CPT_applicability_decision"]["verdict"] != "DIRECT_MINIMAL_CPT_SUBSTITUTION_FOR_THE_GENERIC_GHOST_SECTOR_IS_OBSTRUCTED":
        raise ValueError("generic ghost CPT verdict drifted")
    for reference in stored["dependencies"].values():
        path = ROOT / reference["path"]
        if not path.exists() or _sha256(path) != reference["sha256"]:
            raise ValueError(f"generic ghost CPT dependency drifted: {reference['path']}")

    flags = stored["claim_flags"]
    positive = [name for name, enabled in flags.items() if enabled]
    if positive != [
        "ALGEBRAIC_WEYL_GHOST_ELIMINATED",
        "EFFECTIVE_VECTOR_OPERATOR_BETA_INDEPENDENT",
        "EINSTEIN_SCALAR_GHOST_FACTOR_REPRODUCED",
        "GENERIC_DIFF_WEYL_FP_ROWS_DERIVED",
        "GENERIC_GHOST_HODGE_SPLIT_OBSTRUCTED",
        "GENERIC_GHOST_PRINCIPAL_SYMBOL_NONMINIMAL",
    ]:
        raise ValueError("generic ghost CPT claim boundary drifted")
    return stored


def main() -> int:
    verify()
    print("independent generic-background Diff-Weyl ghost CPT obstruction: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
