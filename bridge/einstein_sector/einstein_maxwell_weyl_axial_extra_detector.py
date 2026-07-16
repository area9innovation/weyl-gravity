"""Exact symplectic coefficient detector for the generic axial extra module."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_axial_lee_wald_completion import (
    _generic_current_matrix,
    _reduce_two_shells,
)


ROOT = Path(__file__).resolve().parents[2]
LEE_WALD = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json"
HESSIAN = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_reduced_action_hessian.json"
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_extra_detector.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_extra_detector.schema.json"


class AxialExtraDetectorError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AxialExtraDetectorError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [
        [str(sp.factor(matrix[row, column])) for column in range(matrix.cols)]
        for row in range(matrix.rows)
    ]


def _shell_reduce(
    expression: sp.Expr,
    frequency: sp.Symbol,
    momentum: sp.Symbol,
    eigenvalue: sp.Symbol,
) -> sp.Expr:
    shell = sp.Poly(
        frequency**2 - momentum**2 - eigenvalue + sp.Rational(2, 3),
        frequency,
    )
    numerator, denominator = sp.cancel(expression).as_numer_denom()
    reduced_numerator = sp.rem(
        sp.Poly(sp.expand(numerator), frequency), shell
    ).as_expr()
    reduced_denominator = sp.rem(
        sp.Poly(sp.expand(denominator), frequency), shell
    ).as_expr()
    return sp.factor(sp.cancel(reduced_numerator / reduced_denominator))


def _detector() -> dict[str, Any]:
    eigenvalue, momentum, frequency = sp.symbols("lambda k omega", real=True)
    representatives = sp.Matrix.hstack(
        sp.Matrix([-(momentum**2 + eigenvalue), momentum * frequency, eigenvalue, 0]),
        sp.Matrix([-momentum * frequency, momentum**2 - sp.Rational(2, 3), 0, eigenvalue]),
    )
    current = _generic_current_matrix(eigenvalue, momentum, frequency, frequency)
    pairing_rows = (representatives.T * current / (-sp.I * frequency)).applyfunc(
        lambda value: _shell_reduce(value, frequency, momentum, eigenvalue)
    )
    gram = (pairing_rows * representatives).applyfunc(
        lambda value: _shell_reduce(value, frequency, momentum, eigenvalue)
    )
    _require(gram == gram.T, "extra detector Gram matrix is not symmetric")
    determinant = _shell_reduce(gram.det(), frequency, momentum, eigenvalue)
    expected_determinant = eigenvalue**4 * (eigenvalue - 2) * (9 * eigenvalue - 2) / 3
    _require(
        sp.factor(determinant - expected_determinant) == 0,
        "extra detector determinant changed",
    )
    detector_rows = (gram.inv() * pairing_rows).applyfunc(
        lambda value: _shell_reduce(value, frequency, momentum, eigenvalue)
    )
    reconstruction = (detector_rows * representatives).applyfunc(
        lambda value: _shell_reduce(value, frequency, momentum, eigenvalue)
    )
    _require(reconstruction == sp.eye(2), "detector failed to recover extra coordinates")

    extra_frequency, einstein_frequency = sp.symbols("omega_e omega_E", real=True)
    extra_representatives = representatives.subs(frequency, extra_frequency)
    mixed_current = _generic_current_matrix(
        eigenvalue, momentum, extra_frequency, einstein_frequency
    )
    einstein_mass = einstein_frequency**2 - momentum**2
    einstein_representative = sp.Matrix(
        [
            2 * momentum,
            -2 * einstein_frequency,
            momentum * (einstein_mass - eigenvalue),
            -einstein_frequency * (einstein_mass - eigenvalue),
        ]
    )
    mixed = extra_representatives.T * mixed_current * einstein_representative
    mixed_remainders = [
        _reduce_two_shells(
            mixed[index],
            extra_frequency,
            einstein_frequency,
            momentum,
            eigenvalue,
        )
        for index in range(2)
    ]
    _require(mixed_remainders == [0, 0], "detector did not annihilate the Einstein image")

    return {
        "coefficient_order": ["H_t", "H_x", "Q_t", "Q_x"],
        "extra_coordinate_order": ["a_1", "a_2"],
        "extra_representative_columns": _matrix_strings(representatives),
        "extra_shell": "omega^2=k^2+lambda-2/3",
        "normalized_pairing_rows": _matrix_strings(pairing_rows),
        "extra_Gram": _matrix_strings(gram),
        "extra_Gram_determinant": str(sp.factor(determinant)),
        "detector_rows": _matrix_strings(detector_rows),
        "definition": "O_X(Phi)=G_X^(-1) Omega_WM(conjugate(e),Phi)/(-I*omega*N_(ell,m))",
        "extra_coordinate_reconstruction": _matrix_strings(reconstruction),
        "Einstein_image_pairing_remainders": [str(value) for value in mixed_remainders],
        "identity_on_extra_module": True,
        "annihilates_Einstein_image": True,
        "conserved_by_local_Green_identity_on_linear_solutions": True,
        "gauge_invariant_on_declared_reduced_Diff_x_U1_block": True,
        "no_frequency_difference_inverted": True,
    }


def build_certificate() -> dict[str, Any]:
    inputs = {"lee_wald": LEE_WALD, "reduced_action_hessian": HESSIAN}
    records = {
        name: json.loads(path.read_text(encoding="utf-8"))
        for name, path in inputs.items()
    }
    _require(records["lee_wald"]["result_id"] == "EINSTEIN_MAXWELL_WEYL_AXIAL_LEE_WALD_COMPLETION", "Lee-Wald input changed")
    _require(records["reduced_action_hessian"]["result_id"] == "EINSTEIN_MAXWELL_WEYL_AXIAL_REDUCED_ACTION_HESSIAN", "Hessian input changed")
    return {
        "schema": "einstein-maxwell-weyl-axial-extra-detector-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_DETECTOR",
        "result_state": "GENERIC_AXIAL_EXTRA_SYMPLECTIC_COEFFICIENT_DETECTOR_CERTIFIED_BEFORE_RESIDUAL_QUOTIENT",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_GENERIC_AXIAL_EXTRA_SYMPLECTIC_DETECTOR",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for name, path in inputs.items()
            },
        },
        "domain": "generic axial ell>=2 Weyl-Maxwell linear solution module at real compact momentum k, after local Diff x U(1) reduction and before final residual SO(4,2) quotient",
        "detector": _detector(),
        "classification": {
            "exact_linear_extra_branch_detector": True,
            "vanishes_on_certified_Einstein_image": True,
            "normalizes_both_extra_coordinates_to_one": True,
            "final_residual_invariance_computed": False,
            "relational_local_observer_constructed": False,
            "causal_or_asymptotic_observable_constructed": False,
            "particle_or_quantum_observable_constructed": False,
        },
        "interpretation": "The inverse nondegenerate extra Lee-Wald Gram matrix converts symplectic pairing with the two certified extra representatives into exact coefficient observables. They vanish on every certified generic axial Einstein-image mode and return the two extra coordinates. They are conserved reduced-mode observables before the final residual quotient, not yet relational, causal, asymptotic, or quantum observables.",
        "next_gate": "use the detector dual basis to project the Hermitian-polarized EE, EX, and XX quadratic Weyl-Maxwell sources, then prove removability by an explicit correction or non-removability by a complete adjoint-cokernel witness",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE detector is defined only on the compact generic axial linear solution block. Its descent under SO(4,2), nonlinear completion, boundary realization, and observer interpretation remain open.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_extra_detector --verify bridge/certificates/einstein_maxwell_weyl_axial_extra_detector.json",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_extra_detector",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(
        json.loads(path.read_text(encoding="utf-8")) == build_certificate(),
        f"stale axial extra detector certificate: {path}",
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
