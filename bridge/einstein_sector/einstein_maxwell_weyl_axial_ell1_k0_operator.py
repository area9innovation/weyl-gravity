"""Exceptional axial ell=1,k=0 Weyl--Maxwell quotient operator."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_axial_operator import _generic_rows


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell1_k0_operator.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_ell1_k0_operator.schema.json"
INPUTS = {
    "axial_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_operator.json",
    "twist": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_twist_symplectic_restriction.json",
    "physical_ell1": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell1_physical_symplectic_restriction.json",
}


class AxialEll1K0OperatorError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AxialEll1K0OperatorError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_strings(matrix: sp.Matrix) -> list[list[str]]:
    return [[str(sp.factor(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]


def _operator_theorem() -> dict[str, Any]:
    rows, symbols = _generic_rows()
    coefficient_names = ("h_t", "h_x", "q_t", "q_x")
    coefficients = sp.Matrix([symbols[name] for name in coefficient_names])
    equations = sp.Matrix([rows[name] for name in ("metric_t", "metric_x", "maxwell_t", "maxwell_x")])
    raw = (
        sp.diag(symbols["lambda"], -symbols["lambda"], 1, 1)
        * equations
    ).jacobian(coefficients).subs({symbols["lambda"]: 2, symbols["k"]: 0}).applyfunc(sp.factor)
    frequency = symbols["omega"]
    gauge = sp.Matrix([-frequency, 0, frequency, 0])
    noether = sp.Matrix([-1, 0, 1, 0])
    _require(raw * gauge == sp.zeros(4, 1), "ell=1 gauge column changed")
    _require(raw.T * noether == sp.zeros(4, 1), "ell=1 Noether row changed")

    # For omega!=0 fix h_t=0.  Retain variables (q_t,h_x,q_x) and rows
    # (metric_t,metric_x,maxwell_x).  The omega=0 fibre is audited separately.
    reduced = raw.extract((0, 1, 3), (2, 1, 3))
    determinant = sp.factor(reduced.det())
    expected = frequency**2 * (frequency**2 - 4) * (3 * frequency**2 - 4)
    _require(sp.factor(determinant - expected) == 0, "ell=1 reduced determinant changed")
    representatives = {
        "twist_zero": sp.Matrix([0, 1, 0, -1]),
        "extra_fourth_order": sp.Matrix([0, 1, 0, -3]),
        "standard_physical": sp.Matrix([0, 1, 0, 1]),
    }
    shells = {
        "twist_zero": sp.Integer(0),
        "extra_fourth_order": sp.Rational(4, 3),
        "standard_physical": sp.Integer(4),
    }
    for name, representative in representatives.items():
        image = raw.subs(frequency**2, shells[name]) * representative
        _require(image.applyfunc(sp.factor) == sp.zeros(4, 1), f"{name} representative failed")

    zero = raw.subs(frequency, 0)
    left_zero = zero.T.nullspace()
    _require(zero.rank() == 2 and len(left_zero) == 2, "zero-frequency exceptional rank changed")
    twist_adjoint = sp.Matrix([0, -1, 0, 1])
    _require(zero.T * twist_adjoint == sp.zeros(4, 1), "twist adjoint changed")
    return {
        "raw_row_order": ["2*metric_t", "-2*metric_x", "maxwell_t", "maxwell_x"],
        "raw_coefficient_order": list(coefficient_names),
        "raw_matrix": _matrix_strings(raw),
        "polynomial_gauge_column": [str(value) for value in gauge],
        "Noether_left_null": [str(value) for value in noether],
        "nonzero_frequency_gauge_slice": {
            "condition": "omega!=0",
            "gauge_choice": "h_t=0",
            "coefficient_order": ["q_t", "h_x", "q_x"],
            "row_order": ["2*metric_t", "-2*metric_x", "maxwell_x"],
            "matrix": _matrix_strings(reduced),
            "determinant": str(determinant),
        },
        "primary_shells": {
            "zero_frequency_twist": "omega^2=0",
            "extra_fourth_order": "omega^2=4/3",
            "standard_Einstein_Maxwell": "omega^2=4",
        },
        "representatives_Ht_Hx_Qt_Qx": {name: [str(value) for value in vector] for name, vector in representatives.items()},
        "zero_frequency_fibre": {
            "raw_rank": zero.rank(),
            "left_cokernel_dimension": len(left_zero),
            "Noether_identity_direction": [str(value) for value in noether],
            "physical_twist_adjoint_direction": [str(value) for value in twist_adjoint],
            "interpretation": "after removing the universal Noether identity, one physical adjoint condition remains; its three SO(3) copies are the rotation/Taub constraints",
        },
    }


def build_certificate() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["twist"]["classification"]["axial_twist_restriction_computed"], "twist input changed")
    _require(records["physical_ell1"]["classification"]["physical_ell1_axial_restriction_computed"], "physical ell1 input changed")
    return {
        "schema": "einstein-maxwell-weyl-axial-ell1-k0-operator-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_AXIAL_ELL1_K0_OPERATOR",
        "result_state": "EXCEPTIONAL_AXIAL_ELL1_TARGET_PRIMARY_DECOMPOSITION_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_AXIAL_ELL1_K0_EXCEPTIONAL_OPERATOR",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "domain": "axial ell=1,k=0 Weyl-Maxwell coefficient complex, all three real m by SO(3), before stabilizer quotient",
        "operator_theorem": _operator_theorem(),
        "classification": {
            "standard_physical_shell_recovered": True,
            "zero_frequency_twist_recovered_without_frequency_inversion": True,
            "extra_fourth_order_ell1_shell_discovered": True,
            "extra_shell_frequency_squared": "4/3",
            "zero_fibre_physical_cokernel_equals_rotation_triplet": True,
            "ell1_positive_frequency_Lee_Wald_inertia_of_extra_mode": False,
            "polar_ell1_extra_modes_classified": False,
            "Lorentzian_causal_or_quantum_claim": False,
        },
        "interpretation": "The exceptional axial ell=1 target contains more than the standard Einstein-Maxwell oscillator and the global twist. A distinct fourth-order primary occurs at omega^2=4/3. At zero frequency the raw two-dimensional left cokernel splits into the universal Noether identity and one physical twist-adjoint direction per m, exactly the structure needed for rotation Taub descent.",
        "next_gate": "compute the direct Lee-Wald current on the omega^2=4/3 representative and classify the polar ell=1 fourth-order quotient",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE theorem classifies only the axial ell=1,k=0 operator. It does not compute the extra mode current, polar exceptional modes, nonlinear closure, causal propagation, particles, or quantum theory.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_ell1_k0_operator --verify bridge/certificates/einstein_maxwell_weyl_axial_ell1_k0_operator.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_axial_ell1_k0_operator.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_ell1_k0_operator",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(payload == build_certificate(), f"axial ell1 certificate stale: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
