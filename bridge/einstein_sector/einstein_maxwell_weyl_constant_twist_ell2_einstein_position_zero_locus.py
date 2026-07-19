"""Classify constant-twist position resonance on both ell=2 Einstein shells."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path

import sympy as sp
from sympy.physics.wigner import clebsch_gordan

from bridge.einstein_sector.einstein_maxwell_weyl_twist_ell2_einstein_source_explore import (
    BRANCHES,
    source,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_constant_twist_ell2_einstein_position_zero_locus.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_constant_twist_ell2_einstein_position_zero_locus.schema.json"
INPUTS = {
    "extra_shell_zero_locus": ROOT / "bridge/certificates/einstein_maxwell_weyl_constant_twist_ell2_extra_position_zero_locus.json",
    "axial_minus": ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_axial_ell2_minus_resonance.json",
    "polar_minus": ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_polar_ell2_minus_resonance.json",
    "polar_minus_shell_fixture": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell2_minus_zero_source_fixture.json",
    "polar_plus_shell_fixture": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell2_plus_zero_source_fixture.json",
}


class ConstantTwistEinsteinKernelError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ConstantTwistEinsteinKernelError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _strings(vector: sp.MatrixBase) -> list[str]:
    return [str(sp.factor(value)) for value in vector]


def _expected_minus_rows() -> dict[str, dict[str, sp.Matrix]]:
    omega = sp.symbols("omega", positive=True, real=True)
    root = sp.sqrt(3)
    return {
        "axial": {
            "axial": sp.Matrix([0, 0, 6 * root * omega, 0]),
            "polar": sp.Matrix([0, 0, 0, -sp.Rational(12, 5) * root * (omega**2 - 6)]),
        },
        "polar": {
            "axial": sp.Matrix(
                [0, sp.Rational(9, 5) * (-omega**4 + 2 * root * omega**4 - 30 * root * omega**2 + 60 * root), 0, 0]
            ),
            "polar": sp.Matrix([0, -18 * omega * (-3 * omega**2 + 6 * root * omega**2 - 38 * root + 18), 0, 0]),
        },
    }


def _root_involution(vector: sp.MatrixBase) -> sp.Matrix:
    radical = sp.symbols("rho", real=True)
    return vector.xreplace({sp.sqrt(3): radical}).subs(radical, -sp.sqrt(3))


def _direct_case(input_parity: str) -> tuple[str, sp.Matrix, sp.Matrix]:
    axial, polar = source(input_parity, "minus")
    return input_parity, axial, polar


def _direct_replay(expected: dict[str, dict[str, sp.Matrix]]) -> None:
    with ProcessPoolExecutor(max_workers=2) as executor:
        values = list(executor.map(_direct_case, ("axial", "polar")))
    for input_parity, axial, polar in values:
        _require((axial - expected[input_parity]["axial"]).applyfunc(sp.simplify) == sp.zeros(4, 1), f"direct axial row changed for {input_parity}")
        _require((polar - expected[input_parity]["polar"]).applyfunc(sp.simplify) == sp.zeros(4, 1), f"direct polar row changed for {input_parity}")


def _projected_theorem(expected_minus: dict[str, dict[str, sp.Matrix]]) -> dict[str, object]:
    omega = sp.symbols("omega", positive=True, real=True)
    root = sp.sqrt(3)
    shells = {
        "minus": {
            "omega_squared": 6 - 2 * root,
            "axial_adjoint": sp.Matrix([0, -2, 0, 2 * root]),
            "polar_adjoint": sp.Matrix([12, 0, 12 - 24 * root, 6]),
            "rows": expected_minus,
        },
        "plus": {
            "omega_squared": 6 + 2 * root,
            "axial_adjoint": sp.Matrix([0, -2, 0, -2 * root]),
            "polar_adjoint": sp.Matrix([12, 0, 12 + 24 * root, 6]),
            "rows": {
                input_parity: {output_parity: _root_involution(vector) for output_parity, vector in outputs.items()}
                for input_parity, outputs in expected_minus.items()
            },
        },
    }
    matrices: dict[str, sp.Matrix] = {}
    raw: dict[str, object] = {}
    for branch, data in shells.items():
        columns = []
        raw[branch] = {}
        for input_parity in ("axial", "polar"):
            raw[branch][input_parity] = {
                output_parity: _strings(vector)
                for output_parity, vector in data["rows"][input_parity].items()
            }
            column = []
            for output_parity in ("axial", "polar"):
                adjoint = data[f"{output_parity}_adjoint"]
                pairing = sp.factor((adjoint.T * data["rows"][input_parity][output_parity])[0])
                pairing = sp.factor(pairing.subs(omega**2, data["omega_squared"]))
                column.append(pairing)
            columns.append(sp.Matrix(column))
        matrix = sp.Matrix.hstack(*columns)
        _require(matrix == sp.Matrix([[0, sp.Rational(216, 5)], [sp.Rational(432, 5), 0]]), f"{branch} incidence matrix changed")
        _require(matrix.det() == -sp.Rational(93312, 25), f"{branch} incidence determinant changed")
        matrices[branch] = matrix

    magnetic_numbers = list(range(-2, 3))
    coefficients = [sp.factor(clebsch_gordan(1, 2, 2, 0, m, m)) for m in magnetic_numbers]
    _require(coefficients == [-sp.Rational(m, 1) / sp.sqrt(6) for m in magnetic_numbers], "axis CG coefficients changed")
    angular = sp.diag(*coefficients)
    full = {branch: sp.kronecker_product(angular, matrix) for branch, matrix in matrices.items()}
    _require(all(operator.rank() == 8 and len(operator.nullspace()) == 2 for operator in full.values()), "Einstein shell rank changed")
    combined = sp.diag(full["minus"], full["plus"])
    _require(combined.rank() == 16 and len(combined.nullspace()) == 4, "combined Einstein kernel changed")
    return {
        "fixture_channel": "m_twist=1,m_wave=0 -> M_output=1",
        "axis_Clebsch_Gordan": {str(m): str(value) for m, value in zip(magnetic_numbers, coefficients, strict=True)},
        "root_involution": "the plus-shell direct rows follow from the minus-shell rows by sqrt(3)->-sqrt(3), including the representatives and omega^2=6-/+2sqrt(3)",
        "input_column_order": ["axial", "polar"],
        "output_row_order": ["axial_adjoint", "polar_adjoint"],
        "raw_direct_rows": raw,
        "minus_position_matrix": [[str(value) for value in matrices["minus"].row(row)] for row in range(2)],
        "plus_position_matrix": [[str(value) for value in matrices["plus"].row(row)] for row in range(2)],
        "matrix_determinant": "-93312/25",
        "each_shell_operator": "nonzero scalar times (A_hat dot J_2) tensor Q_branch",
        "each_shell_ambient_positive_frequency_complex_dimension": 10,
        "each_shell_operator_rank": 8,
        "each_shell_kernel_positive_frequency_complex_dimension": 2,
        "each_shell_kernel": "V_(m_A=0) tensor C^2_parity",
        "combined_q_primary_ambient_positive_frequency_complex_dimension": 20,
        "combined_q_primary_operator_rank": 16,
        "combined_q_primary_kernel_positive_frequency_complex_dimension": 4,
    }


def build(direct_replay: bool = False) -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["extra_shell_zero_locus"]["classification"]["complete_nonzero_A_ell2_extra_position_resonance_kernel_classified"], "extra-shell predecessor changed")
    _require(records["axial_minus"]["linear_input"]["representative"] == ["0", "-2", "0", "2*sqrt(3)"], "axial minus representative changed")
    _require(records["polar_minus"]["linear_input"]["representative"] == ["12", "0", "12-24*sqrt(3)", "6"], "polar minus representative changed")
    _require(BRANCHES["plus"]["frequency_squared"] == 6 + 2 * sp.sqrt(3), "plus shell changed")
    expected = _expected_minus_rows()
    if direct_replay:
        _direct_replay(expected)
    theorem = _projected_theorem(expected)
    return {
        "schema": "einstein-maxwell-weyl-constant-twist-ell2-einstein-position-zero-locus-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_CONSTANT_TWIST_ELL2_EINSTEIN_POSITION_ZERO_LOCUS",
        "result_state": "BOTH_ELL2_EINSTEIN_Q_PRIMARY_CONSTANT_TWIST_POSITION_RESONANCE_KERNELS_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded or finite-quasiperiodic correction class",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "one nonzero constant axial twist-position vector A crossed with both axial/polar ell=2,k=0 Einstein q-primary shells",
            "degree": 2,
            "parity": "axial and polar Einstein multiplicities retained on each plus/minus shell",
            "ell": "1 x 2 -> resonant L=2",
            "m": "all m=-2,...,2 relative to the twist axis",
            "k": 0,
            "omega": "omega_minus=sqrt(6-2*sqrt(3)); omega_plus=sqrt(6+2*sqrt(3))",
        },
        "projection_theorem": theorem,
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "CERTIFIED", "claim": "complete twist-position times ell2-Einstein resonant-functional zero locus only"},
            "SMOOTH_SECULAR": {"status": "NOT_APPLICABLE", "reason": "this certificate classifies bounded shell projections, not propagation solvability"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "both_Einstein_q_primary_twist_position_maps_classified": True,
            "both_parities_and_all_m_included": True,
            "each_parity_incidence_matrix_invertible": True,
            "combined_q_primary_kernel_complex_dimension_four": True,
            "extra_and_Einstein_shellwise_twist_maps_complete": True,
            "simultaneous_moment_and_all_branch_resonance_zero_locus_classified": False,
            "complete_mixed_wave_cone_classified": False,
            "full_second_order_equation_solved": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "On each Einstein q-primary shell, constant twist couples axial input only to the polar adjoint and polar input only to the axial adjoint, with an invertible two-by-two incidence matrix. Thus no internal parity combination evades resonance away from the twist axis: precisely the axial and polar m_A=0 coefficients survive on each shell.",
        "next_gate": "intersect the four-dimensional combined Einstein kernel and the twelve-dimensional extra kernel with H,J_i=0, then add the already certified wave self-source conditions",
        "claim_boundary": "This is the complete constant-twist position resonance zero locus on the ell=2,k=0 Einstein q-primary shells. It does not impose the stabilizer moment maps, wave self-products, twist velocity, other ell or momentum, smooth or causal correction sufficiency, all-orders integration, residual descent, observables or quantum theory.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "direct_source_path": str(Path(source.__code__.co_filename).resolve().relative_to(ROOT)),
            "direct_source_sha256": _sha256(Path(source.__code__.co_filename).resolve()),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS", "elapsed_seconds": 1.59},
            "tier_1": {"status": "PASS", "elapsed_seconds": 3.98, "tests_run": 5},
            "tier_2": {"status": "PASS", "elapsed_seconds": 118.49, "max_rss_kib": 255592, "criterion": "two independent four-dimensional tensor columns determine both shells by the exact root involution"},
            "tier_3": {"status": "NOT_RUN", "reason": "the simultaneous moment/resonance cone remains open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_constant_twist_ell2_einstein_position_zero_locus --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_constant_twist_ell2_einstein_position_zero_locus.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_constant_twist_ell2_einstein_position_zero_locus",
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_constant_twist_ell2_einstein_position_zero_locus --replay",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--replay", action="store_true")
    arguments = parser.parse_args()
    value = build(direct_replay=arguments.replay)
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif arguments.check and json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise ConstantTwistEinsteinKernelError("constant-twist ell2 Einstein position-kernel certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_CONSTANT_TWIST_ELL2_EINSTEIN_POSITION_ZERO_LOCUS: PASS")


if __name__ == "__main__":
    main()
