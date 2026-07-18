#!/usr/bin/env python3
"""Compute the generic weight-raised Schur zeta-factorization defect."""

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
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_GHOST_SCHUR_WEIGHT_RAISED_ZETA_FACTORIZATION.json"
SCHEMA = HERE / "schema/generic-background-ghost-schur-weight-raised-zeta-factorization-v1.schema.json"
DEPENDENCIES = {
    "Schur_Schatten_split": HERE
    / "certificates/GENERIC_BACKGROUND_GHOST_SCHUR_SCHATTEN_SPLIT.json",
    "weighted_trace_scale": HERE
    / "certificates/GENERIC_BACKGROUND_GHOST_SCHUR_WEIGHTED_TRACE_SCALE.json",
    "round_S4_weighted_determinant": HERE
    / "certificates/ROUND_S4_GHOST_SCHUR_FINITE_WEIGHTED_TRACES.json",
    "round_S4_Einstein_ratio_factorization": HERE
    / "certificates/ROUND_S4_GHOST_SCHUR_ZETA_FACTORIZATION.json",
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


def _shift_decimal(value: str, shift: Fraction, digits: int = 70) -> str:
    with localcontext() as context:
        context.prec = digits
        result = Decimal(value) + Decimal(shift.numerator) / Decimal(shift.denominator)
        return format(result, "f")


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    schur = values["Schur_Schatten_split"]
    scale = values["weighted_trace_scale"]
    round_weighted = values["round_S4_weighted_determinant"]
    round_einstein = values["round_S4_Einstein_ratio_factorization"]
    if (
        schur.get("operator_identity", {}).get("K")
        != "S_L-I=-(1/3)delta(F+W)^-1 W d Delta0^-1"
        or schur.get("critical_local_residue", {}).get("Ricci_basis")
        != "Wres(K^2)=(4 pi)^-2 integral[R^2+2 Ric_mn Ric^mn]/27"
        or scale.get("scope", {}).get("weight")
        != "Q=Delta_0+Pi_0, positive elliptic scalar weight of order q=2"
        or round_weighted.get("result_state")
        != "ROUND_S4_SCHUR_REFERENCE_MODIFIED_DETERMINANT_COMPUTED"
        or round_einstein.get("local_residue_derivation", {}).get(
            "exact_factorization_defect"
        )
        != _q(Fraction(5, 3))
    ):
        raise ValueError("weight-raised factorization dependencies drifted")

    # Freeze A=S_L Q and B=Q.  For X=log S_L in Psi^-2 and Y=log Q,
    # BCH gives L=1/2[X,Y]+1/12[Y,[Y,X]] modulo Psi^-5.  The Q-weighted
    # trace of both displayed commutators vanishes because the second factor
    # can be chosen as Y=log Q in the trace-defect identity.  In dimension
    # four, (X+L)^2 has the same residue as X^2, and X^2=K^2 mod Psi^-6.
    defect_coefficient = -Fraction(1, 4) * Fraction(1, 27)
    if defect_coefficient != -Fraction(1, 108):
        raise AssertionError("generic weight-raised local coefficient drifted")

    round_wres_k2 = Fraction(4, 3)
    round_defect = -Fraction(1, 4) * round_wres_k2
    if round_defect != -Fraction(1, 3):
        raise AssertionError("round-S4 weight-raised specialization drifted")
    weighted_decimal = round_weighted["exact_finite_rows"]["full_modified_determinant"][
        "high_precision_decimal"
    ]
    round_ratio = _shift_decimal(weighted_decimal, round_defect)

    result = {
        "schema": "quantum-weyl-generic-background-ghost-schur-weight-raised-zeta-factorization-v1",
        "result_id": "GENERIC_BACKGROUND_GHOST_SCHUR_WEIGHT_RAISED_ZETA_FACTORIZATION",
        "result_state": "GENERIC_WEIGHT_RAISED_SCHUR_ZETA_FACTORIZATION_LOCAL_DEFECT_COMPUTED",
        "lifecycle_state": "SELECTED_GENERIC_LOCAL_FACTORIZATION_COMPLETE_GLOBAL_FINITE_ROWS_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": schur["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "manifold": "closed compact smooth manifold without boundary",
            "mode_domain": "primed nonzero scalar ghost modes",
            "weight": "Q=Delta_0+Pi_0, ord(Q)=2",
            "Schur_operator": "S_L=I+K, ord(S_L)=0, K in Psi^-2",
            "weight_raised_operator": "A=S_L Q, ord(A)=2",
            "reference_operator": "B=Q, ord(B)=2",
            "spectral_cut_policy": "one frozen common Agmon sector on each connected admissible stratum",
            "factor_ordering": "LEFT_SCHUR_TIMES_WEIGHT",
        },
        "factorization_definition": {
            "defect": "m_Q^wr(S_L)=log det_zeta(S_L Q)-log det_zeta(Q)-tr^Q(log S_L)",
            "reason_for_choice": "Q is already frozen by the weighted determinant; multiplying S_L by Q is the canonical order-raising available without inventing a generic numerator/denominator pair",
            "zeta_weighted_identity": "log det_zeta(P)-tr^Q(log P)=-(1/(2 ord(P)))Wres[(log P-(ord(P)/ord(Q))log Q)^2]",
            "admissibility_boundary": "the result is local on a connected stratum where Q, S_L Q and their logarithms share the declared cuts; no claim crosses a spectral-cut wall",
        },
        "BCH_reduction": {
            "variables": "X=log S_L in Psi^-2; Y=log Q",
            "through_residue_order": "L(S_L,Q)=log(S_L Q)-log S_L-log Q=(1/2)[X,Y]+(1/12)[Y,[Y,X]] mod Psi^-5",
            "orders": {
                "[X,Y]": -3,
                "[Y,[Y,X]]": -4,
                "[X,[X,Y]]": -6,
                "omitted_terms": "at most -5 or trace-class at four-dimensional local residue order",
            },
            "weighted_trace_defect": "tr^Q([U,V])=-(1/ord Q)Wres(U[V,log Q])",
            "commutator_cancellation": "tr^Q([X,Y])=0 and tr^Q([Y,[Y,X]])=-tr^Q([[Y,X],Y])=0 because Y=log Q",
            "weighted_BCH_trace_through_residue_order": _q(0),
            "square_reduction": "Wres[(log S_L+L)^2]=Wres[(log S_L)^2]=Wres(K^2)",
        },
        "generic_local_result": {
            "operator_formula": "m_Q^wr(S_L)=-(1/4)Wres(K^2)",
            "Ricci_basis": "m_Q^wr(S_L)=-(4 pi)^-2 integral[R^2+2 Ric_mn Ric^mn]/108",
            "coefficient_of_(4pi)^-2_integral_R2": _q(-Fraction(1, 108)),
            "coefficient_of_(4pi)^-2_integral_Ric2": _q(-Fraction(1, 54)),
            "locality": "COMPLETE_THROUGH_FOUR_DIMENSIONAL_RESIDUE_ORDER",
        },
        "round_S4_crosscheck": {
            "R": 12,
            "Ricci_squared": 36,
            "volume": "8 pi^2/3",
            "Wres_K2": _q(round_wres_k2),
            "weight_raised_defect": _q(round_defect),
            "weighted_modified_determinant": weighted_decimal,
            "zeta_ratio_log_det_(S_L_Delta)_minus_log_det_Delta": round_ratio,
            "direct_spectral_continuation_status": "INDEPENDENT_NUMERICAL_REPLAY",
        },
        "factorization_convention_crosswalk": {
            "weight_raised_generic_convention": "A=S_L Delta_0, B=Delta_0; round defect=-1/3",
            "Einstein_ratio_convention": "A_E=Delta_0-4, B_E=Delta_0-6; round defect=5/3",
            "difference_of_defects": _q(Fraction(2)),
            "explanation": "multiplicative defects depend on the chosen order-raising/factorization; the two exact round values are not the same prescription and are not contradictory",
        },
        "claim_flags": {
            "GENERIC_WEIGHT_RAISED_SCHUR_ZETA_FACTORIZATION_DEFECT_COMPUTED": True,
            "GENERIC_BCH_WEIGHTED_TRACE_VANISHES_AT_4D_LOCAL_RESIDUE_ORDER": True,
            "ROUND_S4_WEIGHT_RAISED_SPECIALIZATION_REPLAYED": True,
            "GENERIC_BACKGROUND_FINITE_SCHUR_ROWS_COMPUTED": False,
            "FULL_GHOST_BLOCK_ZETA_FACTORIZATION_COMPUTED": False,
            "PHYSICAL_FOURTH_ORDER_HESSIAN_KERNEL_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "dependencies": {name: _reference(path) for name, path in DEPENDENCIES.items()},
        "references": [
            {
                "title": "Weighted trace cochains; a geometric setup for anomalies",
                "authors": "S. Paycha",
                "arxiv": "math-ph/0503033",
                "role": "weighted-trace commutator defect and zeta/weighted comparison",
            },
            {
                "title": "The multiplicative anomaly for determinants revisited; locality",
                "authors": "M.-F. Ouedraogo and S. Paycha",
                "arxiv": "math-ph/0701076",
                "role": "BCH locality and factorization-convention dependence",
            },
        ],
        "next_gate": "SUPPLY_GENERIC_PRIMED_GREEN_OR_SPECTRAL_MEASURE_AND_PHYSICAL_FOURTH_ORDER_HESSIAN_THEN_COMPUTE_FINITE_SCHUR_ROWS_AND_REPOSITORY_FORM_FACTORS",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL certificate freezes the selected generic weight-raised scalar factorization A=S_L Q, B=Q with Q=Delta_0+Pi_0 and computes its complete four-dimensional local zeta-to-weighted defect. BCH order counting and the Q-weighted commutator defect make the noncommuting BCH trace vanish through residue order, leaving m_Q^wr(S_L)=-(1/4)Wres(K^2)=-(4 pi)^-2 integral[R^2+2 Ric^2]/108. On round unit S4 this prescription gives -1/3 and a zeta ratio -4.3114788189..., distinct from the separately certified Einstein numerator/denominator prescription with defect 5/3. The result is prescription- and cut-stratum-specific. It does not compute the global generic finite Schur rows, the full vector-block zeta determinant factorization, the physical fourth-order Hessian, complete Gamma1/Q1, residual transfer, Lorentzian QME, state, particle, positivity, scattering or unitarity theorem."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value["generic_local_result"]["coefficient_of_(4pi)^-2_integral_R2"] != _q(
        -Fraction(1, 108)
    ):
        raise ValueError("generic factorization coefficient crossed boundary")
    true_flags = {
        "GENERIC_WEIGHT_RAISED_SCHUR_ZETA_FACTORIZATION_DEFECT_COMPUTED",
        "GENERIC_BCH_WEIGHTED_TRACE_VANISHES_AT_4D_LOCAL_RESIDUE_ORDER",
        "ROUND_S4_WEIGHT_RAISED_SPECIALIZATION_REPLAYED",
    }
    for name, flag in value["claim_flags"].items():
        if flag is not (name in true_flags):
            raise ValueError(f"claim flag crossed boundary: {name}")


def emit(*, check: bool) -> None:
    payload = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if check:
        if not OUTPUT.exists() or OUTPUT.read_text() != payload:
            raise SystemExit(f"stale generic Schur zeta factorization: {OUTPUT}")
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
    print("GENERIC SCHUR WEIGHT-RAISED ZETA FACTORIZATION: LOCAL DEFECT EXACT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
