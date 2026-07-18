#!/usr/bin/env python3
"""Split the generic longitudinal Schur determinant at its sharp Schatten gate."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_GHOST_SCHUR_SCHATTEN_SPLIT.json"
SCHEMA = HERE / "schema/generic-background-ghost-schur-schatten-split-v1.schema.json"
DEPENDENCIES = {
    "Schur_resummation": HERE
    / "certificates/GENERIC_BACKGROUND_GHOST_LONGITUDINAL_SCHUR_RESUMMATION.json",
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


def _q(value: sp.Expr | Fraction | int) -> dict[str, int]:
    rational = sp.Rational(value)
    return {"numerator": int(rational.p), "denominator": int(rational.q)}


def _sphere_moment_replay() -> dict[str, Any]:
    """Contract the four-sphere moment against a generic symmetric W."""

    entries: dict[tuple[int, int], sp.Symbol] = {}
    for i in range(4):
        for j in range(i, 4):
            entries[(i, j)] = sp.Symbol(f"w{i}{j}")
    w = sp.Matrix(
        4,
        4,
        lambda i, j: entries[(min(i, j), max(i, j))],
    )
    delta = lambda i, j: sp.Integer(1 if i == j else 0)
    contraction = sp.Integer(0)
    for i in range(4):
        for j in range(4):
            for k in range(4):
                for ell in range(4):
                    moment = (
                        delta(i, j) * delta(k, ell)
                        + delta(i, k) * delta(j, ell)
                        + delta(i, ell) * delta(j, k)
                    ) / sp.Integer(24)
                    contraction += w[i, j] * w[k, ell] * moment
    target = ((sp.trace(w)) ** 2 + 2 * sp.trace(w * w)) / 24
    residual = sp.expand(contraction - target)
    if residual != 0:
        raise AssertionError("four-dimensional sphere moment contraction failed")
    return {
        "dimension": 4,
        "unit_sphere_volume": "2 pi^2",
        "normalized_fourth_moment": "(delta_ij delta_kl+delta_ik delta_jl+delta_il delta_jk)/24",
        "contraction": "[(tr W)^2+2 tr(W^2)]/24",
        "symbolic_residual": _q(residual),
    }


def _modified_determinant_fixture() -> dict[str, Any]:
    k = sp.Matrix(
        [
            [sp.Rational(1, 3), sp.Rational(1, 5), 0],
            [sp.Rational(1, 7), -sp.Rational(1, 4), sp.Rational(1, 6)],
            [sp.Rational(1, 8), 0, sp.Rational(1, 9)],
        ]
    )
    identity = sp.eye(3)
    determinant_prefactor = sp.factor((identity + k).det())
    trace_k = sp.trace(k)
    half_trace_k2 = sp.trace(k**2) / 2
    exponent = sp.factor(-trace_k + half_trace_k2)
    log_tail = [
        {
            "power": power,
            "coefficient": _q(
                sp.Rational((-1) ** (power + 1), power) * sp.trace(k**power)
            ),
        }
        for power in range(3, 7)
    ]
    if determinant_prefactor == 0:
        raise AssertionError("modified determinant fixture is not invertible")
    return {
        "dimension": 3,
        "det_I_plus_K": _q(determinant_prefactor),
        "Tr_K": _q(trace_k),
        "one_half_Tr_K2": _q(half_trace_k2),
        "det3_exponential_counterterm": _q(exponent),
        "det3_representation": "det(I+K) exp[-Tr K+(1/2)Tr(K^2)]",
        "log_det3_coefficients_power_3_to_6": log_tail,
    }


def build() -> dict[str, Any]:
    schur = json.loads(DEPENDENCIES["Schur_resummation"].read_text())
    if (
        schur.get("exact_determinant_factorization", {}).get(
            "normalized_scalar_Schur_operator"
        )
        != "S_L(W)=(2/3)I+(1/3)delta(F+W)^-1 d"
        or schur.get("regularization_boundary", {}).get(
            "generic_4d_trace_class_status"
        )
        != "ORDER_MINUS_TWO_DOES_NOT_PROVE_TRACE_CLASS_IN_DIMENSION_FOUR"
    ):
        raise ValueError("Schur resummation dependency drifted")

    result = {
        "schema": "quantum-weyl-generic-background-ghost-schur-schatten-split-v1",
        "result_id": "GENERIC_BACKGROUND_GHOST_SCHUR_SCHATTEN_SPLIT",
        "result_state": "SCHUR_CORRECTION_IN_S3_WITH_CANONICAL_DET3_TAIL_AND_EXACT_CRITICAL_K2_RESIDUE",
        "lifecycle_state": "REGULARIZATION_SPLIT_COMPUTED_FULL_SCHUR_DETERMINANT_UNEVALUATED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": schur["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "manifold": "closed compact smooth manifold without boundary",
            "mode_domain": "primed nonzero scalar ghost modes with elliptic inverses",
            "operator_scope": "normalized scalar Schur factor S_L=I+K",
        },
        "operator_identity": {
            "S_L": "(2/3)I+(1/3)delta(F+W)^-1 d",
            "K": "S_L-I=-(1/3)delta(F+W)^-1 W d Delta0^-1",
            "K_series": "K=sum_(n>=1)(-1)^n B_n/3",
            "principal_symbol_K": "sigma_-2(K)=-(1/3)<xi,W xi>/|xi|^4",
            "W_specialization": "W=-2 Ric",
        },
        "sharp_ideal_classification": {
            "singular_value_decay": "s_j(K)=O(j^-1/2)",
            "Schatten_membership": "K in S_p for every p>2; in particular K in S_3",
            "ordinary_trace_class": "NOT_PROVED_AND_NOT_GENERIC_FROM_ORDER_MINUS_TWO",
            "K_squared": "classical PsiDO of order -4; critical weak trace class in dimension four",
            "K_cubed": "classical PsiDO of order -6; ordinary trace class",
            "minimal_modified_determinant_order": 3,
        },
        "canonical_modified_determinant": {
            "definition": "det_3(I+K)=det[(I+K) exp(-K+K^2/2)]",
            "trace_class_remainder": "(I+K) exp(-K+K^2/2)-I is trace class",
            "small_norm_series": "log det_3(I+K)=sum_(m>=3)(-1)^(m+1)Tr(K^m)/m",
            "renormalized_split": "log Det_(3,R)(I+K)=R(K)-(1/2)R(K^2)+log det_3(I+K)",
            "regulator_dependence": "confined to extensions R(K), R(K^2), and any local multiplicative anomaly of a separately factorized zeta prescription",
        },
        "curvature_expansion_through_W3": {
            "K_components": ["K1=-B1/3", "K2=B2/3", "K3=-B3/3"],
            "W1": ["-(1/3)R(B1)"],
            "W2": ["+(1/3)R(B2)", "-(1/18)R(B1^2)"],
            "W3": [
                "-(1/3)R(B3)",
                "+(1/9)R(B1 B2)",
                "-(1/81)Tr(B1^3)",
            ],
            "canonical_cubic_tail": "-(1/81)Tr(B1^3)",
            "remaining_regularized_cubic_rows": ["R(B3)", "R(B1 B2)"],
        },
        "critical_local_residue": {
            "definition": "Wres(P)=(2 pi)^-4 integral_M integral_|xi|=1 sigma_-4(P) dS dvol",
            "sigma_minus_4_K2": "(1/9)<xi,W xi>^2/|xi|^8",
            "W_basis": "Wres(K^2)=(4 pi)^-2 integral[(tr W)^2+2 tr(W^2)]/108",
            "Ricci_basis": "Wres(K^2)=(4 pi)^-2 integral[R^2+2 Ric_mn Ric^mn]/27",
            "scalar_flat_basis": "Wres(K^2)=(4 pi)^-2 integral[2 Ric_mn Ric^mn]/27 when R=0",
            "conversion_boundary": "conversion of this residue into a zeta-pole or scale coefficient depends on the declared reference operator order and trace normalization",
            "sphere_moment_replay": _sphere_moment_replay(),
        },
        "exact_modified_determinant_fixture": _modified_determinant_fixture(),
        "analytic_disposition": {
            "canonical_nonlocal_tail": "det_3(I+K)",
            "renormalized_rows_still_required": ["R(K)", "R(K^2) finite part"],
            "computed_local_row": "Wres(K^2)",
            "uncomputed_local_rows": ["Wres(K)", "zeta multiplicative anomaly"],
            "physical_kernel": "same-gauge generic fourth-order Hessian remains open",
        },
        "claim_flags": {
            "SCHUR_CORRECTION_S3_CLASS_PROVED": True,
            "CANONICAL_DET3_TAIL_DEFINED": True,
            "CRITICAL_K2_WODZICKI_RESIDUE_COMPUTED": True,
            "ORDINARY_TRACE_CLASS_PROVED": False,
            "FULL_SCHUR_REGULARIZED_DETERMINANT_COMPUTED": False,
            "WODZICKI_RESIDUE_K_COMPUTED": False,
            "ZETA_MULTIPLICATIVE_ANOMALY_COMPUTED": False,
            "SCHUR_COVARIANT_FORM_FACTORS_COMPUTED": False,
            "PHYSICAL_FOURTH_ORDER_HESSIAN_KERNEL_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "dependencies": {
            name: _reference(path) for name, path in DEPENDENCIES.items()
        },
        "references": [
            {
                "title": "Derivatives of (Modified) Fredholm Determinants and Stability of Standing and Traveling Waves",
                "authors": "F. Gesztesy, Y. Latushkin, K. Zumbrun",
                "arxiv": "0802.1665",
                "role": "modified Fredholm determinant perturbation expansion",
            },
            {
                "title": "Schatten classes on compact manifolds: Kernel conditions",
                "authors": "J. Delgado, M. Ruzhansky",
                "arxiv": "1403.6158",
                "role": "compact-manifold Schatten criteria",
            },
        ],
        "next_gate": "COMPUTE_RENORMALIZED_R_K_AND_FINITE_R_K2_THEN_COMBINE_WITH_GENERIC_PHYSICAL_FOURTH_ORDER_HESSIAN",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL certificate upgrades the generic longitudinal ghost Schur factor from a merely formal order-zero determinant to its sharp four-dimensional trace-ideal disposition. On a closed compact manifold, K=S_L-I is a classical order-minus-two scalar pseudodifferential operator, hence lies in every Schatten S_p with p>2 and in S_3; K^3 is trace class. The canonical third modified Fredholm determinant det_3(I+K) is therefore defined and contains the trace-class tail beginning at cubic order. A regulator is still required for R(K) and the finite part of R(K^2). The exact order-minus-four symbol gives Wres(K^2)=(4 pi)^-2 integral[(R^2+2 Ric^2)/27], with the stated residue convention. This computes a critical local residue, not the full Schur determinant, Wres(K), the finite K/K^2 trace parts, a zeta multiplicative anomaly, covariant form factors, the physical fourth-order Hessian, complete Gamma1/Q1, residual transfer, Lorentzian QME, Hadamard state, particle, positivity, scattering or unitarity theorem. Conversion of the residue to a regulator pole or scale coefficient requires the declared reference-operator order and trace normalization."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    true_flags = {
        "SCHUR_CORRECTION_S3_CLASS_PROVED",
        "CANONICAL_DET3_TAIL_DEFINED",
        "CRITICAL_K2_WODZICKI_RESIDUE_COMPUTED",
    }
    for name, flag in value["claim_flags"].items():
        if flag is not (name in true_flags):
            raise ValueError(f"claim flag crossed boundary: {name}")
    if value["sharp_ideal_classification"]["minimal_modified_determinant_order"] != 3:
        raise ValueError("modified determinant order drifted")
    if value["critical_local_residue"]["sphere_moment_replay"]["symbolic_residual"] != _q(0):
        raise ValueError("sphere-moment certificate drifted")


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
        validate(build())
    print("GENERIC GHOST SCHUR SCHATTEN SPLIT: DET3 TAIL EXACT; RENORMALIZED K/K2 OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
