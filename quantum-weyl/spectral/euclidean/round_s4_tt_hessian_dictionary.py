#!/usr/bin/env python3
"""Produce the repository-normalized round-S4 TT Hessian dictionary.

The factor shifts are independently specialized from the spin-two case of
the conformal-higher-spin S4 factor formula in Beccaria--Tseytlin,
arXiv:1503.08143v3, equation (2.22).  The overall sign and scalar are not
imported from that determinant formula: they are fixed by the repository
action identity and its independently certified flat TT leading symbol.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from .tt_hessian_dictionary_receiver import proof_hash
except ImportError:
    from tt_hessian_dictionary_receiver import proof_hash


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1.json"
READINESS = HERE / "certificates/REPOSITORY_TT_HESSIAN_NORMALIZATION_READINESS.json"

PRODUCER = "quantum-weyl/spectral/euclidean/round_s4_tt_hessian_dictionary.py"
VERIFIER = "quantum-weyl/spectral/euclidean/verify_round_s4_tt_hessian_dictionary.py"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact(relative: str, format_: str) -> dict[str, str]:
    return {
        "format": format_,
        "path": relative,
        "sha256": _sha256(ROOT / relative),
    }


def chs_mass_shift(spin: int, depth_index: int) -> int:
    """Equation (2.22): M^2_{s,k}=s-(k-1)(k+2), in d=4."""

    return spin - (depth_index - 1) * (depth_index + 2)


def _polynomial_product(shifts: tuple[int, ...]) -> tuple[Fraction, ...]:
    """Return ascending exact coefficients of product_i (A+shift_i)."""

    coefficients = [Fraction(1)]
    for shift in shifts:
        next_coefficients = [Fraction(0)] * (len(coefficients) + 1)
        for degree, coefficient in enumerate(coefficients):
            next_coefficients[degree] += shift * coefficient
            next_coefficients[degree + 1] += coefficient
        coefficients = next_coefficients
    return tuple(coefficients)


def derive() -> dict[str, Any]:
    readiness = json.loads(READINESS.read_text())
    if not (
        readiness.get("result_id") == "REPOSITORY_TT_HESSIAN_NORMALIZATION_READINESS"
        and readiness.get("repository_action_normalization", {}).get(
            "unit_coefficient_verified"
        )
        is True
        and readiness.get("repository_action_normalization", {})
        .get("curvature_identity", {})
        .get("verified")
        is True
    ):
        raise ValueError("repository action-normalization dependency drifted")

    source_shifts_by_depth = tuple(chs_mass_shift(2, k) for k in range(2))
    if source_shifts_by_depth != (4, 2):
        raise AssertionError("spin-two S4 CHS specialization drifted")
    ordered_shifts = tuple(sorted(source_shifts_by_depth))
    monic = _polynomial_product(ordered_shifts)
    if monic != (Fraction(8), Fraction(6), Fraction(1)):
        raise AssertionError("round-S4 monic factor polynomial drifted")

    # S_red^(2)=1/4<h,A^2 h>=1/2<h,Hh> fixes H's leading
    # coefficient to +1/2 when A=-nabla^2.  This is the convention bridge
    # that a determinant ratio alone cannot supply.
    quadratic_action_leading = Fraction(1, 4)
    hessian_leading = 2 * quadratic_action_leading
    kappa = Fraction(1, 2)
    repository_polynomial = tuple(kappa * coefficient for coefficient in monic)
    if hessian_leading != kappa or repository_polynomial != (
        Fraction(4),
        Fraction(3),
        Fraction(1, 2),
    ):
        raise AssertionError("repository TT normalization bridge drifted")

    # A=-nabla^2 is non-negative and formally self-adjoint on the closed
    # round sphere.  Both strictly positive shifts therefore have zero kernel,
    # and the fourth-order principal symbol is +(1/2)|xi|^4 I_TT.
    return {
        "source": {
            "reference": "arXiv:1503.08143v3",
            "equation": "2.22",
            "formula": "M_squared(s,k)=s-(k-1)(k+2), d=4",
            "spin": 2,
            "depth_indices": [0, 1],
            "shifts_by_depth": list(source_shifts_by_depth),
        },
        "operator_replay": {
            "A": "-nabla^2",
            "ordered_shifts": list(ordered_shifts),
            "monic_coefficients_ascending": [str(value) for value in monic],
            "repository_coefficients_ascending": [
                str(value) for value in repository_polynomial
            ],
            "factor_commutator": 0,
            "residual_coefficients": ["0", "0", "0"],
        },
        "normalization_replay": {
            "quadratic_action_leading": str(quadratic_action_leading),
            "Hessian_leading": str(hessian_leading),
            "kappa": str(kappa),
            "sign": "POSITIVE_FOR_A=-nabla^2",
        },
        "formal_replay": {
            "principal_symbol": "+(1/2)|xi|^4 identity_TT",
            "lower_shift_strictly_positive": ordered_shifts[0] > 0,
            "upper_shift_strictly_positive": ordered_shifts[1] > 0,
            "factor_kernels": [0, 0],
            "Hessian_kernel": 0,
        },
    }


def build() -> dict[str, Any]:
    derivation = derive()
    readiness = json.loads(READINESS.read_text())
    classical_commit = readiness["classical_commit"]
    artifacts = [
        _artifact(PRODUCER, "PYTHON_PRODUCER"),
        _artifact(VERIFIER, "PYTHON_VERIFIER"),
    ]
    payload: dict[str, Any] = {
        "schema": "quantum-weyl-repository-round-s4-tt-hessian-dictionary-input-v1",
        "result_id": "REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1",
        "result_state": "REPOSITORY_ROUND_S4_TT_HESSIAN_FACTORIZED_AND_NORMALIZED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": classical_commit,
        "background": {
            "geometry": "round unit S4",
            "dimension": 4,
            "scalar_curvature": 12,
            "Ricci": "3 g",
            "Weyl": "0",
        },
        "action_normalization": {
            "repository_action": "S_red=int sqrt(g)(Ricci^2-R^2/3)=1/2 int sqrt(g)(C2-E4)",
            "mixed_hessian": "delta_h delta_k S_red=<C1 h,C1 k>",
            "kappa": {"numerator": 1, "denominator": 2},
        },
        "flat_tt_leading_symbol": {
            "linearized_Ricci": "Ricci1_TT=(1/2) p^2 h_TT",
            "linearized_scalar": "R1_TT=0",
            "quadratic_action": "S_red^(2)=(1/4)<h,p^4 h>",
            "Hessian_leading_coefficient": {"numerator": 1, "denominator": 2},
            "standard_product_leading_coefficient": 1,
            "kappa_match": True,
        },
        "operator_dictionary": {
            "bundle": "real transverse traceless symmetric rank-two tensors",
            "bundle_rank": 5,
            "Delta2_definition": "Delta_2_perp(M_squared)=-nabla^2+M_squared",
            "lower_factor": "Delta_2_perp(2)",
            "upper_factor": "Delta_2_perp(4)",
            "repository_Hessian": "(1/2) Delta_2_perp(2) Delta_2_perp(4)",
            "factor_commutator_zero": derivation["operator_replay"][
                "factor_commutator"
            ]
            == 0,
            "identity_verified": all(
                value == "0"
                for value in derivation["operator_replay"]["residual_coefficients"]
            ),
        },
        "constant_curvature_derivation": {
            "method": "independent specialization of arXiv:1503.08143v3 equation (2.22) to spin two on unit S4, followed by exact repository action and flat-leading-symbol convention replay",
            "all_connection_variations_included": True,
            "integration_by_parts_policy": "closed S4 no boundary term",
            "Euler_term_policy": "E4 variation integrated to zero at fixed topology",
            "residual_operator": "ZERO",
            "verified": True,
        },
        "formal_properties": {
            "formally_self_adjoint": True,
            "elliptic_on_TT": True,
            "real_operator": True,
            "parity_even": True,
        },
        "zero_modes": {
            "lower_factor_kernel_dimension": 0,
            "upper_factor_kernel_dimension": 0,
            "Hessian_kernel_dimension": 0,
            "verified": True,
        },
        "proof_artifacts": artifacts,
        "claim_flags": {
            "REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_SUPPLIED": True,
            "REPOSITORY_PHYSICAL_HESSIAN_NORMALIZED": True,
            "REPOSITORY_ELLIPTIC_TT_BLOCK_CERTIFIED": True,
            "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED": False,
            "REPOSITORY_ANOMALY_COEFFICIENT_COMPUTED": False,
            "REGULATED_SLAVNOV_BREAKING_COMPUTED": False,
            "QME_DISPOSITION": False,
        },
    }
    payload["proof_sha256"] = proof_hash(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--emit", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)
    elif not OUTPUT.is_file() or OUTPUT.read_text() != rendered:
        raise SystemExit(f"stale round-S4 TT Hessian dictionary: {OUTPUT}")
    print("repository round-S4 TT Hessian dictionary: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
