"""Exceptional polar ell=1,k=0 Weyl--Maxwell quotient operator."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import _action_operator


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell1_k0_operator.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_polar_ell1_k0_operator.schema.json"
INPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_full_tensor.json"


class PolarEll1OperatorError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PolarEll1OperatorError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(sp.factor(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]


def build_certificate() -> dict[str, Any]:
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    _require(source["classification"]["extra_polar_characteristic_certified"], "generic polar operator input changed")
    hessian, (eigenvalue, momentum, frequency) = _action_operator()
    exceptional = hessian.subs({eigenvalue: 2, momentum: 0}).applyfunc(sp.factor)

    # At ell=1 the tracefree polar tensor harmonic vanishes.  The scalar
    # diffeomorphism is therefore residual after h_A=0 and the Weyl K=0
    # slice.  Compensating xi_A=-partial_A xi and sigma=xi gives this column.
    gauge = sp.Matrix([2 * (frequency**2 - 1), 0, 2, -1])
    _require((exceptional * gauge).applyfunc(sp.factor) == sp.zeros(4, 1), "polar ell1 residual gauge ceased to be null")
    _require((gauge.T * exceptional).applyfunc(sp.factor) == sp.zeros(1, 4), "polar ell1 Noether row ceased to be null")

    # gauge_U=-1 makes U=0 a complete polynomial slice.  The first three
    # rows are then independent away from the two physical shells.
    reduced = exceptional[:3, :3]
    determinant = sp.factor(reduced.det())
    expected = sp.factor((frequency**2 - 4) * (3 * frequency**2 - 4) / 2)
    _require(determinant == expected, "polar ell1 reduced determinant changed")
    zero = reduced.subs(frequency, 0)
    _require(zero.det() != 0 and zero.rank() == 3, "polar ell1 zero fibre lost invertibility")

    extra = reduced.subs(frequency**2, sp.Rational(4, 3))
    standard = reduced.subs(frequency**2, 4)
    extra_null = extra.nullspace()
    standard_null = standard.nullspace()
    _require(extra_null == [sp.Matrix([0, 1, 0])], f"polar ell1 extra representative changed: {extra_null}")
    _require(standard_null == [sp.Matrix([1, 0, 1])], f"polar ell1 standard representative changed: {standard_null}")

    return {
        "schema": "einstein-maxwell-weyl-polar-ell1-k0-operator-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_POLAR_ELL1_K0_OPERATOR",
        "result_state": "EXCEPTIONAL_POLAR_ELL1_QUOTIENT_AND_COKERNEL_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_POLAR_ELL1_K0_ALL_M",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "input": {"path": str(INPUT.relative_to(ROOT)), "sha256": _sha256(INPUT)},
        },
        "domain": "polar ell=1,k=0 Weyl-Maxwell target after h_A=0 and Weyl K=0, before final residual quotient",
        "exceptional_harmonic_geometry": {
            "tracefree_tensor_harmonic": "D_aD_bY+lambda*g_ab*Y/2 vanishes at lambda=2",
            "residual_scalar_parameter": "xi Y with xi_A=-partial_A xi and sigma=xi",
            "field_order": ["A_t", "B", "C_t", "U"],
            "gauge_column": [str(value) for value in gauge],
            "complete_slice": "U=0 because delta U=-xi",
        },
        "operator_theorem": {
            "raw_action_Hessian": _matrix_strings(exceptional),
            "raw_rank_over_Q_omega": 3,
            "Noether_row": [str(value) for value in gauge],
            "reduced_field_order": ["A_t", "B", "C_t"],
            "reduced_Hessian": _matrix_strings(reduced),
            "reduced_determinant": str(determinant),
            "physical_shells": {
                "fourth_order": {"omega_squared": "4/3", "representative": ["0", "1", "0"]},
                "standard": {"omega_squared": "4", "representative": ["1", "0", "1"]},
            },
            "zero_frequency_fibre": {
                "rank": 3,
                "left_cokernel_dimension": 0,
                "physical_adjoint_obstruction": "none",
            },
        },
        "classification": {
            "polar_ell1_extra_fourth_order_shell_certified": True,
            "polar_ell1_standard_shell_certified": True,
            "polar_ell1_zero_frequency_physical_cokernel_absent": True,
            "all_m_by_SO3_equivariance": True,
            "Lee_Wald_current_classified": False,
            "final_residual_descent_certified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The odd-parity-output gate has no new zero-frequency polar ell=1 obstruction. The exceptional quotient contains only the omega^2=4/3 fourth-order and omega^2=4 standard shells, so cross-frequency solvability reduces to missing these two values.",
        "next_gate": "certify that every axial-polar ell=2 cross frequency misses 4/3 and 4, then compute the remaining zero and resonant source projections",
        "claim_boundary": "This is a local-gauge-reduced exceptional operator theorem. It does not compute the polar ell1 current, final residual states, nonlinear sources, causal propagation, particles, or quantum theory.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_polar_ell1_k0_operator --verify bridge/certificates/einstein_maxwell_weyl_polar_ell1_k0_operator.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_polar_ell1_k0_operator.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_polar_ell1_k0_operator",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(payload == build_certificate(), f"polar ell1 operator certificate stale: {path}")


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
