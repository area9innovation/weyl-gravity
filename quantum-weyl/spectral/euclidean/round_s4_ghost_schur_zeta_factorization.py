#!/usr/bin/env python3
"""Compute the round-S4 zeta/weighted Schur factorization defect."""

from __future__ import annotations

import argparse
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/ROUND_S4_GHOST_SCHUR_ZETA_FACTORIZATION.json"
SCHEMA = HERE / "schema/round-s4-ghost-schur-zeta-factorization-v1.schema.json"
DEPENDENCIES = {
    "round_S4_weighted_determinant": HERE
    / "certificates/ROUND_S4_GHOST_SCHUR_FINITE_WEIGHTED_TRACES.json",
    "weighted_trace_scale": HERE
    / "certificates/GENERIC_BACKGROUND_GHOST_SCHUR_WEIGHTED_TRACE_SCALE.json",
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


def _q(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def _add_fraction_decimal(value: str, shift: Fraction, digits: int = 70) -> str:
    with localcontext() as context:
        context.prec = digits
        result = Decimal(value) + Decimal(shift.numerator) / Decimal(shift.denominator)
        return format(result, "f")


def build() -> dict[str, Any]:
    round_result = json.loads(DEPENDENCIES["round_S4_weighted_determinant"].read_text())
    scale = json.loads(DEPENDENCIES["weighted_trace_scale"].read_text())
    if (
        round_result.get("result_state")
        != "ROUND_S4_SCHUR_REFERENCE_MODIFIED_DETERMINANT_COMPUTED"
        or round_result.get("spectral_diagonalization", {}).get("S_L_eigenvalue")
        != "[lambda_ell-4]/[lambda_ell-6]"
        or scale.get("claim_flags", {}).get("ORDER_TWO_WEIGHTED_TRACE_DECLARED")
        is not True
    ):
        raise ValueError("round-S4 Schur dependencies drifted")

    # Paycha's zeta/weighted determinant comparison for same-order A and Q:
    # log det_zeta A - tr^Q log A
    #   = -(1/(2a)) Wres[(log A-(a/q)log Q)^2].
    # Here a=q=2.  For A=Q-4 and B=Q-6, only the square of the
    # order-minus-two leading logarithm contributes to the four-dimensional
    # residue.  The primed finite-rank projector is smoothing and invisible.
    order = 2
    a_shift = 4
    b_shift = 6
    wres_q_minus_2 = Fraction(1, 3)
    square_difference = Fraction(a_shift * a_shift - b_shift * b_shift)
    defect = -Fraction(1, 2 * order) * square_difference * wres_q_minus_2
    if defect != Fraction(5, 3):
        raise AssertionError("round-S4 zeta factorization defect drifted")

    weighted_decimal = round_result["exact_finite_rows"]["full_modified_determinant"][
        "high_precision_decimal"
    ]
    zeta_ratio_decimal = _add_fraction_decimal(weighted_decimal, defect)

    result = {
        "schema": "quantum-weyl-round-s4-ghost-schur-zeta-factorization-v1",
        "result_id": "ROUND_S4_GHOST_SCHUR_ZETA_FACTORIZATION",
        "result_state": "ROUND_S4_ZETA_TO_WEIGHTED_SCHUR_FACTORIZATION_DEFECT_COMPUTED",
        "lifecycle_state": "SPECIAL_BACKGROUND_ZETA_FACTORIZATION_COMPLETE_GENERIC_NONCOMMUTING_DEFECT_OPEN",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL"],
        "classical_commit": round_result["classical_commit"],
        "scope": {
            "background": "round unit S4",
            "mode_domain": "scalar harmonics ell>=2",
            "operators": {
                "Q": "Delta_0",
                "A": "Delta_0-4",
                "B": "Delta_0-6",
                "S_L": "A B^-1=(Delta_0-4)/(Delta_0-6)",
            },
            "orders": {"Q": 2, "A": 2, "B": 2, "S_L": 0},
            "commutators": "[Q,A]=[Q,B]=[A,B]=0",
            "spectral_cut": "positive real cut on the ell>=2 primed carrier",
            "zero_mode_policy": "ell=0 absent; five ell=1 conformal-Killing zero modes deleted",
        },
        "local_residue_derivation": {
            "zeta_weighted_comparison": "log det_zeta(P)-tr^Q(log P)=-(1/(2 ord(P)))Wres[(log P-(ord(P)/ord(Q))log Q)^2]",
            "ratio_defect_definition": "m_Q(A,B)=log det_zeta(A)-log det_zeta(B)-tr^Q log(A B^-1)",
            "logarithm_rows": {
                "A": "log(A Q^-1)=log(1-4 Q^-1)=-4 Q^-1+O(Psi^-4)",
                "B": "log(B Q^-1)=log(1-6 Q^-1)=-6 Q^-1+O(Psi^-4)",
            },
            "four_dimensional_residue_reduction": "m_Q=-(1/4)(4^2-6^2)Wres(Q^-2)",
            "Wres_Q_minus_2": _q(wres_q_minus_2),
            "Wres_Q_minus_2_derivation": "2 Res_(s=2) zeta_Q(s)=2 Vol(S4)/(4 pi)^2=1/3 for Vol(S4)=8 pi^2/3",
            "finite_rank_projector_effect": "ZERO_IN_WODZICKI_RESIDUE",
            "exact_factorization_defect": _q(defect),
        },
        "factorization_result": {
            "weighted_modified_determinant": weighted_decimal,
            "exact_relation": "log det_zeta(Delta_0-4)-log det_zeta(Delta_0-6)=log Det_(3,R_Delta)(S_L)+5/3",
            "zeta_determinant_ratio_decimal": zeta_ratio_decimal,
            "independent_spectral_representation": "-zeta'_(Delta_0-4)(0)+zeta'_(Delta_0-6)(0) on ell>=2",
            "status": "ROUND_S4_ZETA_FACTORIZED_SCHUR_RATIO_COMPUTED",
        },
        "generic_boundary": {
            "generic_commutator": "[Q,S_L(W)] need not vanish",
            "missing_local_carrier": "the order-minus-three and order-minus-four BCH symbols of L(Q,S_L)=log(Q S_L)-log Q-log S_L for the frozen generic factorization and cuts",
            "missing_global_carrier": "the generic finite weighted rows still require the full primed Green kernel or spectral measure",
            "separation": "the local factorization defect and the global finite weighted rows are distinct gates",
            "status": "GENERIC_NONCOMMUTING_ZETA_FACTORIZATION_NOT_COMPUTED",
        },
        "claim_flags": {
            "ROUND_S4_ZETA_WEIGHTED_FACTORIZATION_DEFECT_COMPUTED": True,
            "ROUND_S4_ZETA_FACTORIZED_SCHUR_RATIO_COMPUTED": True,
            "ROUND_S4_WEIGHTED_MODIFIED_DETERMINANT_IMPORTED": True,
            "GENERIC_NONCOMMUTING_ZETA_FACTORIZATION_DEFECT_COMPUTED": False,
            "GENERIC_BACKGROUND_FINITE_SCHUR_ROWS_COMPUTED": False,
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
                "role": "weighted trace and Wodzicki-residue normalization",
            },
            {
                "title": "The multiplicative anomaly for determinants revisited; locality",
                "authors": "M.-F. Ouedraogo and S. Paycha",
                "arxiv": "math-ph/0701076",
                "role": "local zeta/weighted determinant comparison and factorization anomalies",
            },
        ],
        "next_gate": "FREEZE_GENERIC_NONCOMMUTING_ZETA_FACTORIZATION_AND_COMPUTE_ITS_BCH_RESIDUE_SEPARATELY_FROM_THE_GLOBAL_FINITE_ROWS",
        "claim_boundary": (
            "This EUCLIDEAN-SPECTRAL certificate computes the exact zeta-to-weighted factorization defect of the normalized longitudinal ghost Schur factor on the round unit four-sphere. On the ell>=2 primed scalar carrier, A=Delta_0-4, B=Delta_0-6 and Q=Delta_0 commute. The same-order zeta/weighted determinant comparison reduces the defect to -(1/4)(4^2-6^2)Wres(Q^-2)=5/3, with Wres(Q^-2)=1/3. Adding this exact local term to the previously certified weighted modified determinant gives the zeta-factorized determinant ratio. The result is special-background and prescription-specific. It does not compute the generic noncommuting BCH residue, generic finite Schur rows, a physical fourth-order Hessian, complete Gamma1/Q1, residual transfer, Lorentzian QME, state, particle, positivity, scattering or unitarity theorem."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value["local_residue_derivation"]["exact_factorization_defect"] != _q(
        Fraction(5, 3)
    ):
        raise ValueError("zeta factorization defect crossed boundary")
    true_flags = {
        "ROUND_S4_ZETA_WEIGHTED_FACTORIZATION_DEFECT_COMPUTED",
        "ROUND_S4_ZETA_FACTORIZED_SCHUR_RATIO_COMPUTED",
        "ROUND_S4_WEIGHTED_MODIFIED_DETERMINANT_IMPORTED",
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
    print("ROUND S4 GHOST SCHUR ZETA FACTORIZATION: EXACT 5/3 DEFECT PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
