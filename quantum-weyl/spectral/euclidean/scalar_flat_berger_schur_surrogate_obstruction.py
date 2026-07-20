#!/usr/bin/env python3
"""Obstruct the one-inverse scalar surrogate for the Berger Schur operator."""

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
OUTPUT = (
    HERE
    / "certificates/SCALAR_FLAT_BERGER_SCHUR_SURROGATE_OBSTRUCTION.json"
)
SCHEMA = (
    HERE
    / "schema/scalar-flat-berger-schur-surrogate-obstruction-v1.schema.json"
)
DEPENDENCIES = {
    "receiver_shortfall": (
        HERE
        / "certificates/"
        "BACKGROUND_SPECIFIC_FIVE_FORM_FACTOR_SPECTRAL_REALIZATION_SHORTFALL.json"
    ),
    "normalized_Schur_operator": (
        HERE
        / "certificates/"
        "GENERIC_BACKGROUND_GHOST_LONGITUDINAL_SCHUR_RESUMMATION.json"
    ),
}
PINNED_HASHES = {
    "receiver_shortfall": (
        "45c0debd97f904f80d4454d69582515761a97eafb83e9babc69af91eadcab890"
    ),
    "normalized_Schur_operator": (
        "b40ec3a8bd3a21d8e0ece7c98f98e1776e8c47d557b8c8b5427e422b60c65a78"
    ),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(value: Fraction | int) -> dict[str, int]:
    rational = Fraction(value)
    return {
        "numerator": rational.numerator,
        "denominator": rational.denominator,
    }


def _reference(name: str, path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    actual = _sha256(path)
    if actual != PINNED_HASHES[name]:
        raise ValueError(f"{name} hash drifted: {actual}")
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": value["result_id"],
        "sha256": actual,
    }


def scalar_block(n: int, twice_j: int, twice_m: int) -> dict[str, Any]:
    """Exact scalar block in Fourier/SU(2) labels.

    The standard generators ``E_i`` obey ``[E_1,E_2]=E_3`` cyclically.
    The orthonormal Berger frame is ``e_1=E_1``, ``e_2=E_2``,
    ``e_3=E_3/2``.  Hence

      Delta_0 = n^2 + J^2 - 3 J_3^2/4,
      D_W = delta W d = 2 J^2 - 3 J_3^2

    for ``W=-2 Ric=diag(0,2,2,-4)``.
    """

    if twice_j < 0 or abs(twice_m) > twice_j:
        raise ValueError("invalid SU(2) weight")
    if (twice_j - twice_m) % 2:
        raise ValueError("SU(2) weight parity mismatch")
    casimir = Fraction(twice_j * (twice_j + 2), 4)
    weight_squared = Fraction(twice_m * twice_m, 4)
    delta = n * n + casimir - Fraction(3, 4) * weight_squared
    d_w = 2 * casimir - 3 * weight_squared
    if delta == 0:
        return {
            "n": n,
            "twice_j": twice_j,
            "twice_m": twice_m,
            "multiplicity": twice_j + 1,
            "Delta_0": _q(delta),
            "D_W": _q(d_w),
            "status": "PRIMED_CONSTANT_MODE",
        }
    surrogate_derivative = d_w / (3 * delta)
    true_schur_derivative = -d_w / (3 * delta * delta)
    return {
        "n": n,
        "twice_j": twice_j,
        "twice_m": twice_m,
        "multiplicity": twice_j + 1,
        "Delta_0": _q(delta),
        "D_W": _q(d_w),
        "one_inverse_surrogate_t_derivative": _q(surrogate_derivative),
        "true_normalized_Schur_t_derivative": _q(true_schur_derivative),
        "derivatives_agree": surrogate_derivative == true_schur_derivative,
        "status": "NONZERO_SCALAR_MODE",
    }


def _principal_symbol_witnesses() -> list[dict[str, Any]]:
    # W=-2 Ric in the orthonormal order (theta,e1,e2,e3).
    rows = [
        ("theta", 0),
        ("e1", 2),
        ("e2", 2),
        ("e3", -4),
    ]
    return [
        {
            "unit_covector": name,
            "W_xi_xi": _q(value),
            "surrogate_principal_symbol": _q(1 + Fraction(value, 3)),
        }
        for name, value in rows
    ]


def build() -> dict[str, Any]:
    values = {
        name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()
    }
    shortfall = values["receiver_shortfall"]
    schur = values["normalized_Schur_operator"]
    background = shortfall["candidate_background"]
    if (
        background["background_id"]
        != "EUCLIDEAN_SCALAR_FLAT_BERGER_S1_S3_A1_C2"
        or background["ricci_orthonormal_diagonal"]
        != [_q(0), _q(-1), _q(-1), _q(2)]
        or schur["exact_determinant_factorization"]["principal_symbol"] != (
            "sigma_0(S_L)=1"
        )
        or schur["exact_determinant_factorization"][
            "normalized_scalar_Schur_operator"
        ]
        != "S_L(W)=(2/3)I+(1/3)delta(F+W)^-1 d"
    ):
        raise ValueError("Berger or normalized-Schur dependency drifted")

    first_block = scalar_block(0, 1, 1)
    if (
        first_block["Delta_0"] != _q(Fraction(9, 16))
        or first_block["D_W"] != _q(Fraction(3, 4))
        or first_block["one_inverse_surrogate_t_derivative"]
        != _q(Fraction(4, 9))
        or first_block["true_normalized_Schur_t_derivative"]
        != _q(Fraction(-64, 81))
    ):
        raise AssertionError("lowest Berger representation block drifted")

    symbol_rows = _principal_symbol_witnesses()
    if [row["surrogate_principal_symbol"] for row in symbol_rows] != [
        _q(1),
        _q(Fraction(5, 3)),
        _q(Fraction(5, 3)),
        _q(Fraction(-1, 3)),
    ]:
        raise AssertionError("one-inverse principal-symbol witness drifted")

    result = {
        "$schema": "../schema/scalar-flat-berger-schur-surrogate-obstruction-v1.schema.json",
        "schema": (
            "quantum-weyl-scalar-flat-berger-schur-surrogate-"
            "obstruction-v1"
        ),
        "result_id": "SCALAR_FLAT_BERGER_SCHUR_SURROGATE_OBSTRUCTION",
        "result_state": (
            "REQUESTED_ONE_INVERSE_SCALAR_SURROGATE_IS_NOT_THE_"
            "NORMALIZED_SCHUR_OPERATOR"
        ),
        "lifecycle_state": "EXACT_FIRST_OPERATOR_BLOCK_OBSTRUCTION",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "input_commit": "384d46761",
        "scope": {
            "background": background,
            "carrier": "scalar Fourier/SU(2) blocks only",
            "deformation": "W -> t W at t=0",
            "priming": "remove only (n,j,m)=(0,0,0) from Delta_0^-1",
        },
        "exact_scalar_decomposition": {
            "orthonormal_frame_from_standard_SU2": (
                "e1=E1, e2=E2, e3=E3/2 with [E1,E2]=E3 cyclically"
            ),
            "labels": (
                "n in Z; j in {0,1/2,1,...}; m=-j,...,j; "
                "left multiplicity 2j+1"
            ),
            "Delta_0_eigenvalue": "n^2+j(j+1)-(3/4)m^2",
            "D_W_definition": "D_W=delta W d with W=-2 Ric",
            "D_W_eigenvalue": "2j(j+1)-3m^2",
            "commutator": "[Delta_0,D_W]=0 on scalar blocks",
            "constant_mode": scalar_block(0, 0, 0),
            "lowest_nonconstant_blocks": [
                scalar_block(0, 1, -1),
                first_block,
                scalar_block(1, 0, 0),
                scalar_block(0, 2, 0),
                scalar_block(0, 2, 2),
            ],
        },
        "operator_obstruction": {
            "requested_surrogate": (
                "S_tilde(t)=I+(t/3) Delta_0^-1 delta W d"
            ),
            "requested_surrogate_correction_order": 0,
            "surrogate_principal_symbol_witnesses": symbol_rows,
            "normalized_Schur": (
                "S_L(t)=(2/3)I+(1/3)delta(F+tW)^-1 d"
            ),
            "normalized_Schur_principal_symbol": "1",
            "normalized_Schur_correction_order": -2,
            "normalized_Schur_first_variation": (
                "-(1/3) Delta_0^-1 delta W d Delta_0^-1"
            ),
            "lowest_block": first_block,
            "verdict": (
                "THE_ONE_INVERSE_SURROGATE_FAILS_BOTH_PRINCIPAL_SYMBOL_"
                "AND_FIRST_BLOCK_TESTS"
            ),
        },
        "analytic_consequence": {
            "requested_complete_measure_constructible_as_written": False,
            "reason": (
                "the requested scalar operator is not the frozen normalized "
                "Schur operator and would compute a different order-zero "
                "determinant"
            ),
            "first_missing_correct_object": (
                "Fourier/SU(2) finite vector blocks of A(t)=F+tW, their "
                "primed inverses, and the coupled scalar Schur blocks "
                "(2/3)I+(1/3)delta A(t)^-1 d"
            ),
            "smaller_follow_on_request": (
                "planning/forge-requests/"
                "scalar-flat-berger-coupled-vector-schur-blocks.json"
            ),
        },
        "claim_flags": {
            "SCALAR_FOURIER_SU2_DELTA_AND_DW_BLOCKS_COMPUTED": True,
            "ONE_INVERSE_SURROGATE_OBSTRUCTED": True,
            "TRUE_COUPLED_VECTOR_SCHUR_BLOCKS_COMPUTED": False,
            "COMPLETE_PRIMED_SCHUR_RESOLVENT_COMPUTED": False,
            "INSERTION_EIGENPROJECTORS_THROUGH_THIRD_VARIATION_COMPUTED": False,
            "CERTIFIED_DET3_OR_WEIGHTED_TRACE_TAIL_COMPUTED": False,
            "FIVE_BACKGROUND_SPECIFIC_FUNCTIONS_COMPUTED": False,
            "QME_OR_LORENTZIAN_PROMOTED": False,
        },
        "dependencies": {
            name: _reference(name, path) for name, path in DEPENDENCIES.items()
        },
        "next_gate": (
            "DERIVE_THE_TRUE_COUPLED_VECTOR_A_EQUALS_F_PLUS_TW_BLOCK_PENCIL_"
            "BEFORE_ANY_GLOBAL_SPECTRAL_SUM"
        ),
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC/EUCLIDEAN-SPECTRAL result imports the exact "
            "scalar-flat Berger datum and the frozen normalized Schur "
            "factorization. It computes the exact scalar Fourier/SU(2) blocks "
            "of Delta_0 and delta W d and proves that the one-inverse scalar "
            "surrogate named by the successor request is not the normalized "
            "Schur operator: its correction has order zero and a "
            "direction-dependent principal symbol, while the true normalized "
            "Schur correction begins at order -2; their first j=1/2 block "
            "derivatives are 4/9 and -64/81. The complete coupled vector "
            "blocks, primed resolvent, insertion eigenprojectors, certified "
            "tails, five finite functions, Gamma1/Q1, QME, Lorentzian, "
            "Hadamard, state, particle, positivity, scattering and unitarity "
            "claims remain open."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    true_flags = {
        "SCALAR_FOURIER_SU2_DELTA_AND_DW_BLOCKS_COMPUTED",
        "ONE_INVERSE_SURROGATE_OBSTRUCTED",
    }
    for name, flag in value["claim_flags"].items():
        if flag is not (name in true_flags):
            raise ValueError(f"claim boundary crossed at {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale Berger Schur obstruction: {OUTPUT}")
    print(
        "SCALAR-FLAT BERGER SCHUR SURROGATE: "
        "EXACT FIRST-BLOCK OBSTRUCTION"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
