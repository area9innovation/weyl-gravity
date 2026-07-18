#!/usr/bin/env python3
"""Compute the remaining Wodzicki residues of the scalar ghost Schur factor."""

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
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_GHOST_SCHUR_WODZICKI_RESIDUE.json"
SCHEMA = HERE / "schema/generic-background-ghost-schur-wodzicki-residue-v1.schema.json"
DEPENDENCIES = {
    "Schatten_split": HERE
    / "certificates/GENERIC_BACKGROUND_GHOST_SCHUR_SCHATTEN_SPLIT.json",
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


def _derive_coefficients() -> dict[str, Any]:
    """Replay the heat-insertion, angular, and Einstein coefficient algebra."""

    # Wres(B1)=(4pi)^-2 int[-W.Ric/3+(tr W)R/6].
    # K contains -B1/3 and +B2/3; Wres(B2) has coefficient tr(W^2)/2.
    linear_w_ric = -sp.Rational(1, 3)
    linear_trw_r = sp.Rational(1, 6)
    k_b1_weight = -sp.Rational(1, 3)
    b2_trw2 = sp.Rational(1, 2)
    k_b2_weight = sp.Rational(1, 3)

    k_w_ric = sp.factor(k_b1_weight * linear_w_ric)
    k_trw_r = sp.factor(k_b1_weight * linear_trw_r)
    k_trw2 = sp.factor(k_b2_weight * b2_trw2)

    # W=-2 Ric, tr(W)=-2R, tr(W^2)=4 Ric^2.
    k_r2 = sp.factor(-2 * k_trw_r)
    k_ric2 = sp.factor(-2 * k_w_ric + 4 * k_trw2)
    if (k_r2, k_ric2) != (sp.Rational(1, 9), sp.Rational(4, 9)):
        raise AssertionError("Schur K residue reduction drifted")

    k2_r2 = sp.Rational(1, 27)
    k2_ric2 = sp.Rational(2, 27)
    log_r2 = sp.factor(k_r2 - k2_r2 / 2)
    log_ric2 = sp.factor(k_ric2 - k2_ric2 / 2)
    if (log_r2, log_ric2) != (sp.Rational(5, 54), sp.Rational(11, 27)):
        raise AssertionError("Schur logarithm residue reduction drifted")

    # Exact Einstein cross-check: S_L=(Delta-R/3)/(Delta-R/2), hence
    # K=(R/6)(Delta-R/2)^-1.  For L=-nabla^2-R/2,
    # Wres(L^-1)=2(4pi)^-2 int(R/2+R/6)=4R/3.
    einstein_direct = sp.factor(sp.Rational(1, 6) * sp.Rational(4, 3))
    einstein_general = sp.factor(k_r2 + k_ric2 / 4)
    if einstein_direct != einstein_general:
        raise AssertionError("Einstein residue cross-check failed")

    # If W=w I is covariantly constant, B1=w Delta_0^-1.  The scalar
    # Wres(Delta_0^-1) coefficient is R/3 in four dimensions.
    isotropic_b1_direct = sp.Rational(1, 3)
    isotropic_b1_general = sp.factor(linear_w_ric + 4 * linear_trw_r)
    if isotropic_b1_direct != isotropic_b1_general:
        raise AssertionError("isotropic-W B1 cross-check failed")

    return {
        "B1_residue_coefficients": {
            "W_dot_Ric": _q(linear_w_ric),
            "trW_times_R": _q(linear_trw_r),
        },
        "B2_residue_coefficient_trW2": _q(b2_trw2),
        "K_W_basis_coefficients": {
            "W_dot_Ric": _q(k_w_ric),
            "trW_times_R": _q(k_trw_r),
            "trW2": _q(k_trw2),
        },
        "K_Ricci_basis_coefficients": {
            "R2": _q(k_r2),
            "Ric2": _q(k_ric2),
        },
        "log_S_Ricci_basis_coefficients": {
            "R2": _q(log_r2),
            "Ric2": _q(log_ric2),
        },
        "Einstein_crosscheck": {
            "direct_R2": _q(einstein_direct),
            "general_R2": _q(einstein_general),
            "residual": _q(sp.factor(einstein_direct - einstein_general)),
        },
        "isotropic_W_B1_crosscheck": {
            "direct_wR": _q(isotropic_b1_direct),
            "general_wR": _q(isotropic_b1_general),
            "residual": _q(sp.factor(isotropic_b1_direct - isotropic_b1_general)),
        },
    }


def build() -> dict[str, Any]:
    schatten = json.loads(DEPENDENCIES["Schatten_split"].read_text())
    if (
        schatten.get("claim_flags", {}).get("CANONICAL_DET3_TAIL_DEFINED")
        is not True
        or schatten.get("critical_local_residue", {}).get("Ricci_basis")
        != "Wres(K^2)=(4 pi)^-2 integral[R^2+2 Ric_mn Ric^mn]/27"
    ):
        raise ValueError("Schur Schatten dependency drifted")

    replay = _derive_coefficients()
    result = {
        "schema": "quantum-weyl-generic-background-ghost-schur-wodzicki-residue-v1",
        "result_id": "GENERIC_BACKGROUND_GHOST_SCHUR_WODZICKI_RESIDUE",
        "result_state": "SCHUR_K_AND_LOGARITHM_WODZICKI_RESIDUES_COMPUTED",
        "lifecycle_state": "LOCAL_RESIDUES_COMPLETE_FINITE_TRACE_ROWS_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": schatten["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "manifold": "closed compact smooth manifold without boundary",
            "mode_domain": "primed nonzero scalar ghost modes with elliptic inverses",
            "operator_scope": "normalized scalar Schur factor S_L=I+K",
            "reference_operator": "positive scalar Laplacian Delta_0 of order two",
        },
        "residue_truncation": {
            "Schur_series": "K=-(1/3)B1+(1/3)B2+O(Psi^-6)",
            "B1_order": -2,
            "B2_order": -4,
            "higher_Bn": "B_n has order -2n, so n>=3 has zero four-dimensional Wodzicki residue",
            "logarithm": "Wres(log(I+K))=Wres(K)-(1/2)Wres(K^2)",
        },
        "linear_heat_insertion": {
            "P": "P=delta W d",
            "cyclic_identity": "Wres(B1)=Wres(P Delta_0^-2)",
            "mixed_heat_kernel": "Tr(P exp(-t Delta_0))=(4 pi t)^-2 integral W^mn[g_mn/(2t)-Ric_mn/6+g_mn R/12+O(t)]",
            "coincidence_inputs": [
                "[a1]=R/6",
                "[(Delta_VVM^1/2)_;m n_prime]=-Ric_mn/6",
            ],
            "residue_heat_relation": "Wres(P Delta_0^-2)=2 coefficient_[t^-2] Tr(P exp(-t Delta_0))",
            "B1_result": "Wres(B1)=(4 pi)^-2 integral[-W^mn Ric_mn/3+(tr W)R/6]",
        },
        "quadratic_principal_insertion": {
            "B2_principal_symbol": "sigma_-4(B2)=<xi,W^2 xi>/|xi|^6",
            "sphere_second_moment": "average_S3(n_i n_j)=delta_ij/4",
            "B2_result": "Wres(B2)=(4 pi)^-2 integral tr(W^2)/2",
        },
        "exact_residues": {
            "K_W_basis": "Wres(K)=(4 pi)^-2 integral[W.Ric/9-(tr W)R/18+tr(W^2)/6]",
            "K_Ricci_basis": "Wres(K)=(4 pi)^-2 integral[R^2+4 Ric_mn Ric^mn]/9",
            "K_scalar_flat_basis": "Wres(K)=(4 pi)^-2 integral[4 Ric_mn Ric^mn]/9 when R=0",
            "K2_Ricci_basis": schatten["critical_local_residue"]["Ricci_basis"],
            "log_S_Ricci_basis": "Wres(log S_L)=(4 pi)^-2 integral[5 R^2+22 Ric_mn Ric^mn]/54",
            "Einstein_basis": "Wres(K)=(4 pi)^-2 integral[2 R^2/9] when Ric=(R/4)g and nabla R=0",
            "coefficient_replay": replay,
        },
        "regularization_boundary": {
            "computed": ["Wres(K)", "Wres(K^2)", "Wres(log S_L)", "canonical det_3 tail"],
            "still_required": [
                "renormalized finite value R(K)",
                "finite part of R(K^2)",
                "reference-specific conversion of residues to pole or scale coefficients",
                "zeta multiplicative anomaly for any separately factorized prescription",
            ],
            "full_Schur_determinant": "NOT_COMPUTED",
        },
        "claim_flags": {
            "WODZICKI_RESIDUE_K_COMPUTED": True,
            "WODZICKI_RESIDUE_K2_IMPORTED": True,
            "WODZICKI_RESIDUE_LOG_S_COMPUTED": True,
            "EINSTEIN_SPECIALIZATION_REPLAYED": True,
            "FULL_SCHUR_REGULARIZED_DETERMINANT_COMPUTED": False,
            "RENORMALIZED_R_K_COMPUTED": False,
            "FINITE_PART_R_K2_COMPUTED": False,
            "ZETA_SCALE_COEFFICIENT_COMPUTED": False,
            "ZETA_MULTIPLICATIVE_ANOMALY_COMPUTED": False,
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
                "title": "A Note on the Wodzicki Residue",
                "authors": "T. Ackermann",
                "arxiv": "funct-an/9506006",
                "role": "heat-kernel/Wodzicki-residue normalization",
            },
            {
                "title": "Heat kernel expansion: user's manual",
                "authors": "D. V. Vassilevich",
                "arxiv": "hep-th/0306138",
                "role": "scalar heat-kernel coefficient convention",
            },
            {
                "title": "Transport Equation Approach to Calculations of Hadamard Green functions and non-coincident DeWitt coefficients",
                "authors": "A. C. Ottewill and B. Wardell",
                "arxiv": "0906.0005",
                "role": "noncoincident Van Vleck/DeWitt transport convention",
            },
        ],
        "next_gate": "COMPUTE_RENORMALIZED_R_K_AND_FINITE_R_K2_THEN_COMBINE_WITH_GENERIC_PHYSICAL_FOURTH_ORDER_HESSIAN",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL certificate computes the two remaining canonical local residues of the normalized generic longitudinal ghost Schur factor. Cyclicity reduces the linear B1 row to a scalar heat-kernel insertion, the B2 row needs only its principal symbol, and all B_n with n>=3 lie below the four-dimensional residue order. The result is Wres(K)=(4 pi)^-2 integral[(R^2+4 Ric^2)/9] and Wres(log S_L)=(4 pi)^-2 integral[(5 R^2+22 Ric^2)/54]. The exact Einstein Schur ratio independently reproduces 2 R^2/9. These are regulator-independent local residues. They do not compute the renormalized finite value R(K), the finite part of R(K^2), a reference-specific pole or scale coefficient, a zeta multiplicative anomaly, the full Schur determinant, covariant form factors, the physical fourth-order Hessian, complete Gamma1/Q1, residual transfer, Lorentzian QME, state, particle, positivity, scattering or unitarity theorem."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    true_flags = {
        "WODZICKI_RESIDUE_K_COMPUTED",
        "WODZICKI_RESIDUE_K2_IMPORTED",
        "WODZICKI_RESIDUE_LOG_S_COMPUTED",
        "EINSTEIN_SPECIALIZATION_REPLAYED",
    }
    for name, flag in value["claim_flags"].items():
        if flag is not (name in true_flags):
            raise ValueError(f"claim flag crossed boundary: {name}")
    if value["exact_residues"]["coefficient_replay"]["Einstein_crosscheck"]["residual"] != _q(0):
        raise ValueError("Einstein cross-check drifted")


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
    print("GENERIC GHOST SCHUR WODZICKI RESIDUE: K AND LOG S EXACT; FINITE ROWS OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
