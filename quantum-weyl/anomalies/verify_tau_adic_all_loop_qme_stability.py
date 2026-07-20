#!/usr/bin/env python3
"""Independent verifier for the conditional tau-adic all-loop theorem."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

try:
    from local_bv.schema_validation import validate_instance
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from local_bv.schema_validation import validate_instance


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPO = ROOT.parents[1]
OUTPUT = HERE / "certificates/TAU_ADIC_ALL_LOOP_LOCAL_QME_STABILITY.json"
SCHEMA = HERE / "schema/tau-adic-all-loop-local-qme-stability-v1.schema.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rank(matrix: list[list[dict[str, int]]]) -> int:
    rows = [
        [Fraction(cell["numerator"], cell["denominator"]) for cell in row]
        for row in matrix
    ]
    rank = 0
    for column in range(len(rows[0]) if rows else 0):
        pivot = next(
            (row for row in range(rank, len(rows)) if rows[row][column]),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [entry / scale for entry in rows[rank]]
        for row in range(len(rows)):
            if row != rank and rows[row][column]:
                factor = rows[row][column]
                rows[row] = [
                    entry - factor * pivot_entry
                    for entry, pivot_entry in zip(rows[row], rows[rank])
                ]
        rank += 1
    return rank


def verify_payload(value: dict[str, Any]) -> None:
    errors = validate_instance(value, _load(SCHEMA))
    if errors:
        raise ValueError(f"tau-adic all-loop schema failed: {errors}")

    for pin in value["input_pins"].values():
        current = ROOT / pin["path"]
        if hashlib.sha256(current.read_bytes()).hexdigest() != pin["sha256"]:
            raise ValueError("tau-adic all-loop current pin failed")
        historical = subprocess.run(
            [
                "git",
                "show",
                f"{pin['source_commit']}:physics/symplectic-reconstruction/"
                f"{pin['path']}",
            ],
            cwd=REPO,
            check=True,
            capture_output=True,
        ).stdout
        if hashlib.sha256(historical).hexdigest() != pin["sha256"]:
            raise ValueError("tau-adic all-loop historical pin failed")

    extended = _load(
        ROOT / value["input_pins"]["extended_local_BV"]["path"]
    )
    if (
        _rank(extended["H14"]["boundary_matrix"]) != 4
        or extended["H14"]["even_quotient_dimension"] != 0
        or extended["H14"]["odd_quotient_dimension"] != 0
        or "R(g_hat)^2" not in extended["H04"]["even_classes"]
        or extended["quartet_reduction"]["minimal_positive_afn"]
        != "acyclic on the regular Bach locus"
    ):
        raise ValueError("independent H04/H14/positive-afn replay failed")

    coefficients = value["filtered_deformation_stability"][
        "inverse_coefficients_through_order_12"
    ]
    product = coefficients[:] + [0]
    for degree, coefficient in enumerate(coefficients):
        product[degree + 1] += coefficient
    if (
        coefficients != [1 if degree % 2 == 0 else -1 for degree in range(13)]
        or product
        != value["filtered_deformation_stability"][
            "truncated_product_coefficients"
        ]
        or product[:-1] != [1] + [0] * 12
    ):
        raise ValueError("independent filtered Neumann replay failed")

    if (
        value["quantum_action_principle"]["status"]
        != "DECLARED_HYPOTHESIS_NOT_CONSTRUCTED_REGULATOR"
        or value["lifecycle"]["constructed_all_loop_regulator"] != "OPEN"
        or value["lifecycle"]["Lorentzian_QME"] != "OPEN"
        or any(value["claim_flags"].values())
    ):
        raise ValueError("conditional all-loop claim was over-promoted")


def verify() -> dict[str, Any]:
    value = _load(OUTPUT)
    verify_payload(value)
    print("Tau-adic all-loop QME independent cohomology/induction replay: PASS")
    return value


if __name__ == "__main__":
    verify()
