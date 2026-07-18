#!/usr/bin/env python3
"""Convert the Schur Wodzicki residues to one declared weighted-trace scale row."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_GHOST_SCHUR_WEIGHTED_TRACE_SCALE.json"
SCHEMA = HERE / "schema/generic-background-ghost-schur-weighted-trace-scale-v1.schema.json"
DEPENDENCIES = {
    "Wodzicki_residue": HERE
    / "certificates/GENERIC_BACKGROUND_GHOST_SCHUR_WODZICKI_RESIDUE.json",
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


def _derive_rows(residue: dict[str, Any]) -> dict[str, Any]:
    replay = residue["exact_residues"]["coefficient_replay"]
    k = {
        name: Fraction(value["numerator"], value["denominator"])
        for name, value in replay["K_Ricci_basis_coefficients"].items()
    }
    k2 = {"R2": Fraction(1, 27), "Ric2": Fraction(2, 27)}
    log_s = {name: k[name] - k2[name] / 2 for name in ("R2", "Ric2")}
    expected_log_s = {
        name: Fraction(value["numerator"], value["denominator"])
        for name, value in replay["log_S_Ricci_basis_coefficients"].items()
    }
    if log_s != expected_log_s:
        raise AssertionError("Schur weighted-trace logarithm row drifted")

    weight_order = 2
    scale_power = 2
    pole = {
        "K": {name: _q(value / weight_order) for name, value in k.items()},
        "K2": {name: _q(value / weight_order) for name, value in k2.items()},
        "log_S": {
            name: _q(value / weight_order) for name, value in log_s.items()
        },
    }
    scale_factor = Fraction(scale_power, weight_order)
    scale = {
        "K": {name: _q(scale_factor * value) for name, value in k.items()},
        "K2": {name: _q(scale_factor * value) for name, value in k2.items()},
        "log_S": {
            name: _q(scale_factor * value) for name, value in log_s.items()
        },
    }
    return {
        "weight_order": weight_order,
        "dimensionful_scale_power": scale_power,
        "scale_to_weight_order_ratio": _q(scale_factor),
        "pole_coefficients_Ricci_basis": pole,
        "scale_coefficients_Ricci_basis": scale,
    }


def build() -> dict[str, Any]:
    residue = json.loads(DEPENDENCIES["Wodzicki_residue"].read_text())
    if (
        residue.get("claim_flags", {}).get("WODZICKI_RESIDUE_K_COMPUTED")
        is not True
        or residue.get("claim_flags", {}).get("WODZICKI_RESIDUE_LOG_S_COMPUTED")
        is not True
        or residue.get("exact_residues", {}).get("log_S_Ricci_basis")
        != "Wres(log S_L)=(4 pi)^-2 integral[5 R^2+22 Ric_mn Ric^mn]/54"
    ):
        raise ValueError("Schur Wodzicki dependency drifted")

    rows = _derive_rows(residue)
    result = {
        "schema": "quantum-weyl-generic-background-ghost-schur-weighted-trace-scale-v1",
        "result_id": "GENERIC_BACKGROUND_GHOST_SCHUR_WEIGHTED_TRACE_SCALE",
        "result_state": "ORDER_TWO_WEIGHTED_TRACE_POLE_AND_SCALE_RESPONSE_COMPUTED",
        "lifecycle_state": "SCALE_ROW_COMPLETE_REFERENCE_FINITE_VALUES_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": residue["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "manifold": "closed compact smooth manifold without boundary",
            "mode_domain": "primed nonzero scalar ghost modes with the zero-mode projector restored only to make the weight invertible",
            "operator_scope": "normalized scalar Schur factor S_L=I+K",
            "weight": "Q=Delta_0+Pi_0, positive elliptic scalar weight of order q=2",
            "dimensionless_weight": "Q_mu=Q/mu^2",
        },
        "weighted_trace_definition": {
            "trace": "R_mu(A)=FP_[z=0] TR_prime[A (Q/mu^2)^(-z)]",
            "Laurent_expansion": "TR_prime(A Q^(-z))=Wres(A)/(2z)+R_Q(A)+O(z)",
            "constant_weight_change": "tr^(cQ)(A)-tr^Q(A)=-(log c/2) Wres(A)",
            "scale_identity": "R_(exp(t)mu)(A)-R_mu(A)=t Wres(A)",
            "zero_mode_policy": "Pi_0 makes Q invertible and is smoothing, so it does not alter any Wodzicki residue",
        },
        "exact_conversion": rows,
        "Schur_determinant_scale_row": {
            "renormalized_split": "log Det_(3,R_mu)(I+K)=R_mu(K)-(1/2)R_mu(K^2)+log det_3(I+K)",
            "pole": "Res_[z=0] TR_prime[log(S_L) Q^(-z)]=(1/2)Wres(log S_L)",
            "scale_response": "d/dlog(mu) log Det_(3,R_mu)(S_L)=Wres(log S_L)",
            "Ricci_basis": "d/dlog(mu) log Det_(3,R_mu)(S_L)=(4 pi)^-2 integral[5 R^2+22 Ric_mn Ric^mn]/54",
            "finite_scale_transport": "log Det_(3,R_mu1)-log Det_(3,R_mu0)=log(mu1/mu0) Wres(log S_L)",
        },
        "regularization_boundary": {
            "computed": [
                "order-two weighted-trace pole coefficients for K, K^2 and log S_L",
                "mu-scale transport of R_mu(K), R_mu(K^2) and the renormalized Schur split",
            ],
            "still_required": [
                "reference-scale finite constant R_mu0(K)",
                "reference-scale finite part R_mu0(K^2)",
                "local multiplicative anomaly for any separately factorized zeta prescription",
                "same-gauge generic physical fourth-order Hessian kernel",
            ],
            "full_Schur_determinant": "NOT_COMPUTED",
        },
        "claim_flags": {
            "ORDER_TWO_WEIGHTED_TRACE_DECLARED": True,
            "K_WEIGHTED_TRACE_POLE_COMPUTED": True,
            "K2_WEIGHTED_TRACE_POLE_COMPUTED": True,
            "SCHUR_SCALE_COEFFICIENT_COMPUTED": True,
            "REFERENCE_FINITE_R_K_COMPUTED": False,
            "REFERENCE_FINITE_R_K2_COMPUTED": False,
            "ZETA_MULTIPLICATIVE_ANOMALY_COMPUTED": False,
            "FULL_SCHUR_REGULARIZED_DETERMINANT_COMPUTED": False,
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
                "title": "Weighted trace cochains; a geometric setup for anomalies",
                "authors": "S. Paycha",
                "arxiv": "math-ph/0503033",
                "role": "weighted trace finite part, weight-change formula and Wodzicki residue normalization",
            },
            {
                "title": "Determinants of elliptic pseudo-differential operators",
                "authors": "M. Kontsevich and S. Vishik",
                "arxiv": "hep-th/9404046",
                "role": "zeta determinants, canonical traces and local multiplicative anomalies",
            },
        ],
        "next_gate": "SUPPLY_GENERIC_PRIMED_GREEN_OR_SPECTRAL_MEASURE_AND_PHYSICAL_FOURTH_ORDER_HESSIAN_THEN_COMPUTE_FINITE_SCHUR_ROWS_AND_MULTIPLICATIVE_TERM",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL certificate chooses the explicit primed scalar weight Q=Delta_0+Pi_0 of order two and converts the already certified Schur Wodzicki residues into exact weighted-trace pole and renormalization-scale rows. With Q_mu=Q/mu^2, the scale response of the renormalized Schur split is Wres(log S_L)=(4 pi)^-2 integral[(5 R^2+22 Ric^2)/54]. This fixes scale transport, not the reference-scale finite constants R_mu0(K) and FP R_mu0(K^2), and it does not compute a separately factorized zeta multiplicative anomaly, the full Schur determinant, the physical fourth-order Hessian, complete Gamma1/Q1, residual transfer, Lorentzian QME, state, particle, positivity, scattering or unitarity theorem."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    true_flags = {
        "ORDER_TWO_WEIGHTED_TRACE_DECLARED",
        "K_WEIGHTED_TRACE_POLE_COMPUTED",
        "K2_WEIGHTED_TRACE_POLE_COMPUTED",
        "SCHUR_SCALE_COEFFICIENT_COMPUTED",
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
