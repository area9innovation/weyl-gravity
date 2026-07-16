"""Reduced quadratic-action Hessian for the generic axial Weyl--Maxwell block.

This certificate reconstructs the quadratic Fourier action from the exact
formally self-adjoint reduced Euler operator.  It closes the reduced Hessian
normalization triangle, while deliberately keeping a literal second expansion
of the four-dimensional action density as a separate stronger rail.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OPERATOR = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_operator.json"
GREEN_CURRENT = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_green_current.json"
LEE_WALD = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json"
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_reduced_action_hessian.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_reduced_action_hessian.schema.json"


class ReducedActionHessianError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ReducedActionHessianError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [
        [str(sp.factor(matrix[row, column])) for column in range(matrix.cols)]
        for row in range(matrix.rows)
    ]


def _reconstruction(operator: dict[str, Any]) -> dict[str, Any]:
    eigenvalue, momentum, frequency = sp.symbols("lambda k omega", real=True)
    local_symbols = {"lam": eigenvalue, "k": momentum, "omega": frequency, "I": sp.I}
    hessian = sp.Matrix(
        [
            [
                sp.sympify(value.replace("lambda", "lam"), locals=local_symbols)
                for value in row
            ]
            for row in operator["operator_algebra"]["gauge_fixed_Hessian_operator"]
        ]
    )
    adjoint = hessian.subs(
        {frequency: -frequency, momentum: -momentum}, simultaneous=True
    ).T
    _require(
        (hessian - adjoint).applyfunc(sp.factor) == sp.zeros(4),
        "reduced Hessian lost formal self-adjointness",
    )

    first = sp.Matrix(sp.symbols("u0:4"))
    second = sp.Matrix(sp.symbols("v0:4"))
    polarized_density = sp.expand((first.T * hessian * second)[0])
    mixed_hessian = sp.Matrix(
        4,
        4,
        lambda row, column: sp.diff(
            polarized_density, first[row], second[column]
        ),
    )
    _require(
        (mixed_hessian - hessian).applyfunc(sp.factor) == sp.zeros(4),
        "polarized quadratic density did not reproduce the operator",
    )

    return {
        "coefficient_order": ["H_t", "H_x", "Q_t", "Q_x"],
        "Fourier_convention": "partial_t -> -I*omega; partial_x -> I*k",
        "quadratic_action_kernel": _matrix_strings(hessian),
        "real_field_action": "S2_red=(1/2) integral Phi(-omega,-k)^T K(omega,k) Phi(omega,k)",
        "polarized_density": "B2_red(u,v)=u(-omega,-k)^T K(omega,k) v(omega,k)",
        "mixed_variation_equals_K": True,
        "formal_adjoint_involution": "K(omega,k)^dagger=K(-omega,-k)^T",
        "formal_self_adjoint": True,
        "row_normalization": operator["operator_algebra"]["equation_row_order"],
        "no_frequency_or_momentum_inverse": True,
    }


def build_certificate() -> dict[str, Any]:
    inputs = {
        "operator": OPERATOR,
        "green_current": GREEN_CURRENT,
        "lee_wald": LEE_WALD,
    }
    records = {
        name: json.loads(path.read_text(encoding="utf-8"))
        for name, path in inputs.items()
    }
    _require(records["operator"]["result_id"] == "EINSTEIN_MAXWELL_WEYL_AXIAL_OPERATOR", "operator input changed")
    _require(records["green_current"]["result_id"] == "EINSTEIN_MAXWELL_WEYL_AXIAL_GREEN_CURRENT", "Green-current input changed")
    _require(records["lee_wald"]["result_id"] == "EINSTEIN_MAXWELL_WEYL_AXIAL_LEE_WALD_COMPLETION", "Lee-Wald input changed")
    _require(records["lee_wald"]["direct_current_match"]["generic_direct_match"], "direct current match was not certified")
    return {
        "schema": "einstein-maxwell-weyl-axial-reduced-action-hessian-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_AXIAL_REDUCED_ACTION_HESSIAN",
        "result_state": "REDUCED_QUADRATIC_ACTION_HESSIAN_RECONSTRUCTED_DIRECT_4D_DENSITY_EXPANSION_OPEN",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_GENERIC_AXIAL_REDUCED_ACTION_HESSIAN",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for name, path in inputs.items()
            },
        },
        "domain": "generic axial ell>=2 Weyl-Maxwell reduced coefficient block at symbolic lambda and compact momentum k, before final residual quotient",
        "reconstruction": _reconstruction(records["operator"]),
        "normalization_triangle": {
            "equation_operator_equals_reduced_action_Hessian": True,
            "same_operator_generates_certified_local_Green_identity": True,
            "Green_current_equals_direct_integrated_four_dimensional_Lee_Wald_current": True,
            "literal_direct_four_dimensional_action_density_second_expansion": False,
        },
        "interpretation": "The exact formally self-adjoint axial operator is the mixed Hessian of a unique reduced quadratic Fourier action in the declared row normalization, and its Green current already matches the direct integrated four-dimensional Lee-Wald current. This closes the reduced normalization triangle but is not a literal second expansion of the four-dimensional action density.",
        "next_gate": "construct the extra-mode symplectic detector and compute the Hermitian-polarized quadratic Weyl-Maxwell sources; retain the literal four-dimensional density expansion as an independent normalization audit",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE reconstruction does not replace a direct four-dimensional action-density expansion and proves no nonlinear extension, residual, causal, particle, or quantum statement.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_reduced_action_hessian --verify bridge/certificates/einstein_maxwell_weyl_axial_reduced_action_hessian.json",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_reduced_action_hessian",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(
        json.loads(path.read_text(encoding="utf-8")) == build_certificate(),
        f"stale reduced action Hessian certificate: {path}",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(
            json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and args.verify is None:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
