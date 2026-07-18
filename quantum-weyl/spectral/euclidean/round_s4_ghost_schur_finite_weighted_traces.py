#!/usr/bin/env python3
"""Compute the finite Schur weighted traces on the round unit four-sphere."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/ROUND_S4_GHOST_SCHUR_FINITE_WEIGHTED_TRACES.json"
SCHEMA = HERE / "schema/round-s4-ghost-schur-finite-weighted-traces-v1.schema.json"
DEPENDENCIES = {
    "Schur_resummation": HERE
    / "certificates/GENERIC_BACKGROUND_GHOST_LONGITUDINAL_SCHUR_RESUMMATION.json",
    "weighted_trace_scale": HERE
    / "certificates/GENERIC_BACKGROUND_GHOST_SCHUR_WEIGHTED_TRACE_SCALE.json",
    "round_S4_zero_modes": HERE
    / "certificates/ROUND_S4_STANDARD_FACTOR_ZERO_MODE_LEDGER.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": str(value.get("result_id") or value.get("schema")),
        "sha256": _sha256(path),
    }


def _decimal(value: sp.Expr, digits: int = 50) -> str:
    return str(sp.N(value, digits))


def _exact_rows() -> dict[str, Any]:
    q = sp.Rational(7, 2)
    a = sp.sqrt(33) / 2
    c = sp.Rational(3, 2)
    psi_sum = sp.digamma(q - a) + sp.digamma(q + a)
    trigamma_difference = sp.polygamma(1, q - a) - sp.polygamma(1, q + a)

    # Z_B(s)=sum_{ell>=2} d_ell [ell(ell+3)-6]^{-s}.  At s=1 the
    # asymptotic subtraction is x+8/x; at s=2 it is 1/x, x=ell+3/2.
    fp_zeta_b_1 = -sp.Rational(1, 9) - sp.Rational(4, 3) * psi_sum
    fp_zeta_b_2 = (
        -sp.Rational(1, 6) * psi_sum
        + sp.Rational(2, 3) * trigamma_difference / a
    )

    r_b_k = 2 * fp_zeta_b_1
    r_b_k2 = 4 * fp_zeta_b_2

    # Paycha's same-order weight-change formula gives
    # tr^Delta(K)-tr^B(K)=-1/2 Wres[K(log Delta-log B)].  On unit S4
    # the residue is 4.  K^2 times the logarithmic weight difference has
    # order -6, hence zero four-dimensional residue.
    weight_change_k = sp.Integer(-2)
    weight_change_k2 = sp.Integer(0)
    r_delta_k = sp.simplify(r_b_k + weight_change_k)
    r_delta_k2 = sp.simplify(r_b_k2 + weight_change_k2)
    low_order_split = sp.simplify(r_delta_k - r_delta_k2 / 2)

    if sp.simplify(q**2 - c**2 - 10) != 0:
        raise AssertionError("round-sphere spectral shift drifted")
    if sp.simplify(a**2 - sp.Rational(33, 4)) != 0:
        raise AssertionError("Schur denominator root drifted")
    if sp.simplify(r_delta_k - r_b_k + 2) != 0:
        raise AssertionError("weighted-trace change drifted")

    return {
        "parameters": {
            "q": "7/2",
            "a": "sqrt(33)/2",
            "q_minus_a_positive": True,
        },
        "shifted_zeta_finite_parts": {
            "FP_Z_B_at_1": {
                "exact": "-1/9-(4/3)[psi((7-sqrt(33))/2)+psi((7+sqrt(33))/2)]",
                "decimal": _decimal(fp_zeta_b_1),
            },
            "FP_Z_B_at_2": {
                "exact": "-(1/6)[psi((7-sqrt(33))/2)+psi((7+sqrt(33))/2)]+(4/(3sqrt(33)))[psi1((7-sqrt(33))/2)-psi1((7+sqrt(33))/2)]",
                "decimal": _decimal(fp_zeta_b_2),
            },
        },
        "weight_change": {
            "formula": "R_Delta(A)-R_B(A)=-(1/2)Wres[A(log Delta-log B)]",
            "Wres_K_log_weight_ratio": "4",
            "R_Delta_K_minus_R_B_K": "-2",
            "R_Delta_K2_minus_R_B_K2": "0",
        },
        "Delta_weighted_finite_rows": {
            "R_Delta_K": {
                "exact": "-20/9-(8/3)[psi((7-sqrt(33))/2)+psi((7+sqrt(33))/2)]",
                "decimal": _decimal(r_delta_k),
            },
            "FP_R_Delta_K2": {
                "exact": "-(2/3)[psi((7-sqrt(33))/2)+psi((7+sqrt(33))/2)]+(16/(3sqrt(33)))[psi1((7-sqrt(33))/2)-psi1((7+sqrt(33))/2)]",
                "decimal": _decimal(r_delta_k2),
            },
            "low_order_renormalized_split": {
                "definition": "R_Delta(K)-(1/2)FP R_Delta(K^2)",
                "exact": "-20/9-(7/3)[psi((7-sqrt(33))/2)+psi((7+sqrt(33))/2)]-(8/(3sqrt(33)))[psi1((7-sqrt(33))/2)-psi1((7+sqrt(33))/2)]",
                "decimal": _decimal(low_order_split),
            },
        },
    }


def build() -> dict[str, Any]:
    schur = json.loads(DEPENDENCIES["Schur_resummation"].read_text())
    scale = json.loads(DEPENDENCIES["weighted_trace_scale"].read_text())
    zeros = json.loads(DEPENDENCIES["round_S4_zero_modes"].read_text())
    if (
        schur.get("Einstein_specialization", {}).get("normalized_Schur_factor")
        != "(Delta0-R/3)/(Delta0-R/2)"
        or scale.get("claim_flags", {}).get("SCHUR_SCALE_COEFFICIENT_COMPUTED")
        is not True
    ):
        raise ValueError("Schur dependencies drifted")
    scalar_zero = next(
        row for row in zeros["factor_zero_mode_ledger"]
        if row["factor_id"] == "ghost_depth_0"
    )
    if scalar_zero["zero_mode_dimension"] != 5 or scalar_zero["spectrum"]["zero_levels"] != [1]:
        raise ValueError("round-S4 scalar ghost zero-mode policy drifted")

    result = {
        "schema": "quantum-weyl-round-s4-ghost-schur-finite-weighted-traces-v1",
        "result_id": "ROUND_S4_GHOST_SCHUR_FINITE_WEIGHTED_TRACES",
        "result_state": "ROUND_S4_SCHUR_REFERENCE_FINITE_WEIGHTED_TRACES_COMPUTED",
        "lifecycle_state": "SPECIAL_BACKGROUND_BENCHMARK_COMPLETE_GENERIC_FINITE_ROWS_OPEN",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL"],
        "classical_commit": scale["classical_commit"],
        "scope": {
            "background": "round unit S4",
            "curvature": "R=12, Ric=(R/4)g",
            "mode_domain": "scalar harmonics ell>=2",
            "excluded_modes": [
                "ell=0: absent from the longitudinal gradient carrier",
                "ell=1: five proper-conformal-Killing scalar ghost zero modes",
            ],
            "reference_weight": "Q=Delta_0 on ell>=2, equivalently Delta_0+Pi_0 before restriction",
            "reference_scale": "mu_0=1 in inverse unit-sphere-radius units",
            "comparison_weight": "B=Delta_0-6, positive on ell>=2",
        },
        "spectral_diagonalization": {
            "lambda_ell": "ell(ell+3)",
            "degeneracy": "(2ell+3)(ell+2)(ell+1)/6",
            "S_L_eigenvalue": "[lambda_ell-4]/[lambda_ell-6]",
            "K_eigenvalue": "2/[lambda_ell-6]",
            "shifted_zeta": "Z_B(s)=sum_(ell>=2) d_ell[lambda_ell-6]^-s",
        },
        "exact_finite_rows": _exact_rows(),
        "generic_missing_input_theorem": {
            "statement": "finite weighted traces are not determined by the complete classical symbol or Wodzicki residues",
            "smoothing_witness": "K -> K+T with arbitrary finite-rank smoothing T preserves every homogeneous symbol and Wodzicki residue but changes R_Q(K) by Tr(T)",
            "quadratic_witness": "R_Q((K+T)^2)-R_Q(K^2)=Tr(KT+TK+T^2)",
            "rank_one_fixture": "K e=(1/2)e, T=(7/11)|e><e| gives Delta R_Q(K)=7/11 and Delta R_Q(K^2)=126/121",
            "required_generic_input": "the full primed Green/resolvent kernel or equivalent complete spectral measure on the selected background",
            "status": "MINIMAL_MISSING_GLOBAL_CARRIER_THEOREM",
        },
        "claim_flags": {
            "ROUND_S4_R_DELTA_K_COMPUTED": True,
            "ROUND_S4_FINITE_R_DELTA_K2_COMPUTED": True,
            "ROUND_S4_LOW_ORDER_SCHUR_SPLIT_COMPUTED": True,
            "ROUND_S4_ZERO_MODE_POLICY_APPLIED": True,
            "GENERIC_BACKGROUND_R_K_COMPUTED": False,
            "GENERIC_BACKGROUND_FINITE_R_K2_COMPUTED": False,
            "GENERIC_MULTIPLICATIVE_ANOMALY_COMPUTED": False,
            "FULL_ROUND_S4_DET3_TAIL_COMPUTED": False,
            "FULL_GENERIC_SCHUR_DETERMINANT_COMPUTED": False,
            "PHYSICAL_FOURTH_ORDER_HESSIAN_KERNEL_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "dependencies": {
            name: _reference(path) for name, path in DEPENDENCIES.items()
        },
        "references": [
            {
                "title": "Weighted trace cochains; a geometric setup for anomalies",
                "authors": "S. Paycha",
                "arxiv": "math-ph/0503033",
                "role": "same-order weight-change formula in terms of the Wodzicki residue",
            },
            {
                "title": "Spectral analysis and zeta determinant on the deformed spheres",
                "authors": "M. Spreafico and S. Zerbini",
                "arxiv": "math-ph/0610046",
                "role": "sphere Laplacian spectral-zeta and analytic-continuation framework",
            },
        ],
        "next_gate": "SUPPLY_GENERIC_PRIMED_GREEN_OR_SPECTRAL_MEASURE_AND_PHYSICAL_FOURTH_ORDER_HESSIAN_THEN_COMPUTE_FINITE_SCHUR_ROWS_AND_MULTIPLICATIVE_TERM",
        "claim_boundary": (
            "This EUCLIDEAN-SPECTRAL certificate computes the two reference finite weighted traces of the longitudinal ghost Schur correction on the round unit four-sphere, after deleting the absent constant-gradient row and the five ell=1 conformal-Killing ghost zero modes. The answers are exact digamma/trigamma values for the declared Delta_0 weight. A finite-rank smoothing witness proves that no generic-background finite value follows from the existing complete-symbol and residue receipts: the full primed Green kernel or spectral measure is required. The result is a special-background benchmark, not a generic Schur determinant, multiplicative-anomaly coefficient, physical-Hessian result, complete Gamma1/Q1, Lorentzian QME, state, particle, positivity, scattering or unitarity theorem."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    true_flags = {
        "ROUND_S4_R_DELTA_K_COMPUTED",
        "ROUND_S4_FINITE_R_DELTA_K2_COMPUTED",
        "ROUND_S4_LOW_ORDER_SCHUR_SPLIT_COMPUTED",
        "ROUND_S4_ZERO_MODE_POLICY_APPLIED",
    }
    for name, flag in value["claim_flags"].items():
        if flag is not (name in true_flags):
            raise ValueError(f"claim flag crossed boundary: {name}")


def emit(*, check: bool) -> None:
    payload = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if check:
        if not OUTPUT.exists() or OUTPUT.read_text() != payload:
            raise SystemExit(f"stale certificate: {OUTPUT}")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(payload)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.emit:
        emit(check=False)
    if args.check:
        emit(check=True)
    if not args.emit and not args.check:
        print(json.dumps(build(), indent=2, sort_keys=True))
    print("ROUND S4 GHOST SCHUR FINITE WEIGHTED TRACES: EXACT SPECIAL-BACKGROUND PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
