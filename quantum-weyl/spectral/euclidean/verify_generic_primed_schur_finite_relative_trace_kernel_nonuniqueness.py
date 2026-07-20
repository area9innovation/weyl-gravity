#!/usr/bin/env python3
"""Independent matrix/series audit of the finite Schur kernel nonuniqueness."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = (
    HERE
    / "certificates/"
    "GENERIC_PRIMED_SCHUR_FINITE_RELATIVE_TRACE_KERNEL_NONUNIQUENESS.json"
)
SCHEMA = (
    HERE
    / "schema/"
    "generic-primed-schur-finite-relative-trace-kernel-nonuniqueness-v1.schema.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def verify_value(value: dict[str, Any], *, validate_schema: bool = True) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    if validate_schema:
        Draft202012Validator(schema).validate(value)

    dependency = value["dependency"]
    dependency_path = ROOT / dependency["path"]
    if _sha256(dependency_path) != dependency["sha256"]:
        raise ValueError("predecessor dependency hash drifted")
    predecessor = json.loads(dependency_path.read_text())
    if (
        predecessor["result_id"] != dependency["result_id"]
        or predecessor["first_missing_analytic_datum"]["datum_id"]
        != "GENERIC_PRIMED_SCHUR_FINITE_RELATIVE_TRACE_KERNEL"
    ):
        raise ValueError("predecessor receiver contract drifted")

    # A two-component exact fixture independently carries the primed vector e
    # and a deleted zero mode z. The smoothing projector has no z component.
    k = sp.Rational(1, 2)
    t = sp.Rational(7, 11)
    K = sp.diag(k, 0)
    T = sp.diag(t, 0)
    Pi0 = sp.diag(0, 1)
    if T * Pi0 != sp.zeros(2) or Pi0 * T != sp.zeros(2):
        raise ValueError("smoothing perturbation moved a zero mode")
    if (sp.eye(2) + K)[0, 0] <= 0 or (sp.eye(2) + K + T)[0, 0] <= 0:
        raise ValueError("fixture lost invertibility")

    delta_rk = sp.trace(T)
    delta_rk2 = sp.trace(K * T + T * K + T * T)
    rows = value["rank_one_finite_value_witness"]["finite_trace_shifts"]
    if (
        _fraction(rows["Delta_R_mu0_K"]) != Fraction(delta_rk)
        or _fraction(rows["Delta_FP_R_mu0_K2"]) != Fraction(delta_rk2)
        or sp.cancel(delta_rk - delta_rk2 / 2 - sp.Rational(14, 121))
        != 0
    ):
        raise ValueError("independent finite weighted-trace reconstruction failed")
    if rows["Delta_log_det3"] != "log(47/33)-14/121":
        raise ValueError("det3 exact expression drifted")
    if not (
        sp.Rational(47, 33) > 1
        and sp.Rational(14, 47) > sp.Rational(14, 121)
    ):
        raise ValueError("exact logarithm lower-bound proof failed")

    # Method-distinct formal-series check of the cubic witness.
    x = sp.symbols("x")
    amplitude = sp.Rational(3, 2)
    delta_r = amplitude
    delta_r2 = 2 * k * amplitude
    delta_det3 = sp.expand(
        sp.series(
            sp.log(1 + k + amplitude * x)
            - (k + amplitude * x)
            + (k + amplitude * x) ** 2 / 2,
            x,
            0,
            2,
        ).removeO()
        - (
            sp.log(1 + k)
            - k
            + k**2 / 2
        )
    ).coeff(x)
    delta_full = sp.cancel(delta_r - delta_r2 / 2 + delta_det3)
    cubic = value["third_curvature_row_witness"][
        "mixed_third_variation_shifts"
    ]
    if (
        _fraction(cubic["Delta_d123_R_mu0_K"]) != Fraction(delta_r)
        or _fraction(cubic["Delta_d123_FP_R_mu0_K2"]) != Fraction(delta_r2)
        or _fraction(cubic["Delta_d123_log_det3"]) != Fraction(delta_det3)
        or _fraction(cubic["Delta_d123_log_Det_3_R"]) != Fraction(delta_full)
        or delta_full != 1
    ):
        raise ValueError("independent cubic finite-row series failed")

    ledger = value["invariance_ledger"]
    if (
        ledger["complete_symbol"] != "UNCHANGED_SMOOTHING_HAS_SYMBOL_ZERO"
        or ledger["Wodzicki_residues"]
        != "UNCHANGED_RESIDUE_VANISHES_ON_SMOOTHING"
        or ledger["zero_mode_projector"] != "UNCHANGED_P_T_EQUALS_ZERO"
        or ledger["reference_finite_rows"] != "CHANGED"
    ):
        raise ValueError("invariance/nonuniqueness ledger drifted")
    if not any(
        "primed resolvent" in row
        for row in value["minimal_additional_global_input"]["data"]
    ):
        raise ValueError("minimal global spectral receiver is incomplete")


def mutation_suite(stored: dict[str, Any]) -> int:
    schema = json.loads(SCHEMA.read_text())
    mutations: list[tuple[str, dict[str, Any]]] = []

    mutation = deepcopy(stored)
    mutation["rank_one_finite_value_witness"]["finite_trace_shifts"][
        "Delta_R_mu0_K"
    ]["numerator"] = -7
    mutations.append(("arithmetic", mutation))

    mutation = deepcopy(stored)
    mutation["third_curvature_row_witness"]["mixed_third_variation_shifts"][
        "Delta_d123_log_Det_3_R"
    ]["numerator"] = 0
    mutations.append(("arithmetic", mutation))

    mutation = deepcopy(stored)
    mutation["invariance_ledger"]["zero_mode_projector"] = "CHANGED"
    mutations.append(("schema", mutation))

    mutation = deepcopy(stored)
    mutation["claim_flags"]["SPECIAL_BACKGROUND_INTERPOLATION_USED"] = True
    mutations.append(("schema", mutation))

    mutation = deepcopy(stored)
    mutation["claim_flags"]["COMPLETE_GENERIC_BV_FIVE_FORM_FACTORS_COMPUTED"] = True
    mutations.append(("schema", mutation))

    rejected = 0
    for kind, mutation in mutations:
        try:
            Draft202012Validator(schema).validate(mutation)
            if kind == "arithmetic":
                verify_value(mutation, validate_schema=False)
        except Exception:
            rejected += 1
        else:
            raise ValueError("nonuniqueness mutation was accepted")
    return rejected


def main() -> int:
    stored = json.loads(CERTIFICATE.read_text())
    verify_value(stored)
    rejected = mutation_suite(stored)
    print(
        "GENERIC PRIMED SCHUR FINITE KERNEL INDEPENDENT AUDIT: "
        f"PASS ({rejected} mutations rejected)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
