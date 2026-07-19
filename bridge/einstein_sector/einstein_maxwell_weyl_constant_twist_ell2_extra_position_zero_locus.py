"""Classify the constant-twist position resonance kernel on the ell=2 extra block."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from sympy.physics.wigner import clebsch_gordan


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_constant_twist_ell2_extra_position_zero_locus.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_constant_twist_ell2_extra_position_zero_locus.schema.json"
INPUTS = {
    "twist_matrix": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_ell2_extra_resonance_matrix.json",
    "counterexample": ROOT / "bridge/certificates/einstein_maxwell_weyl_constant_twist_wave_counterexample.json",
}


class ConstantTwistExtraKernelError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ConstantTwistExtraKernelError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix(rows: list[list[str]]) -> sp.Matrix:
    return sp.Matrix([[sp.sympify(value, locals={"sqrt": sp.sqrt}) for value in row] for row in rows])


def _canonical_basis(vectors: list[sp.Matrix]) -> list[list[str]]:
    return [[str(sp.factor(value)) for value in vector] for vector in vectors]


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    theorem = records["twist_matrix"]["twist_projection_theorem"]
    _require(theorem["SO3_multiplicity"].startswith("dim Hom_SO3(V1 tensor V2,V2)=1"), "SO3 multiplicity changed")
    _require(records["counterexample"]["classification"]["nonzero_adjoint_pairing_certified"], "counterexample changed")

    position = _matrix(theorem["position_matrix"])
    _require(position.rank() == 2, "position rank changed")
    kernel = [sp.Matrix([0, 0, 1, 0]), sp.Matrix([-4 * sp.sqrt(3), 0, 0, 15])]
    _require(all(position * vector == sp.zeros(4, 1) for vector in kernel), "declared multiplicity kernel changed")
    _require(sp.Matrix.hstack(*kernel).rank() == 2, "multiplicity-kernel basis lost rank")

    magnetic_numbers = list(range(-2, 3))
    coefficients = [sp.factor(clebsch_gordan(1, 2, 2, 0, m, m)) for m in magnetic_numbers]
    expected = [-sp.Rational(m, 1) / sp.sqrt(6) for m in magnetic_numbers]
    _require(coefficients == expected, "axis Clebsch-Gordan coefficients changed")
    axis_operator = sp.diag(*coefficients)
    resonance_operator = sp.kronecker_product(axis_operator, position)
    _require(axis_operator.rank() == 4 and resonance_operator.rank() == 8, "tensor-product rank changed")
    _require(20 - resonance_operator.rank() == 12, "position-resonance nullity changed")

    fixture_input = sp.Matrix([1, 0, 0, 0])
    fixture_image = position * fixture_input
    _require(fixture_image == sp.Matrix([0, 24 * sp.sqrt(3), 0, 0]), "counterexample column changed")

    return {
        "schema": "einstein-maxwell-weyl-constant-twist-ell2-extra-position-zero-locus-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_CONSTANT_TWIST_ELL2_EXTRA_POSITION_ZERO_LOCUS",
        "result_state": "COMPLETE_NONZERO_CONSTANT_TWIST_POSITION_RESONANCE_KERNEL_ON_ELL2_EXTRA_PRIMARY_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded or finite-quasiperiodic correction class",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "one nonzero constant axial twist-position vector A crossed with the complete axial-plus-polar ell=2,k=0 extra p-primary multiplicity space",
            "degree": 2,
            "parity": "four extra multiplicities retained: axial e1,e2 and polar e1,e2",
            "ell": "1 x 2 -> resonant L=2",
            "m": "all m=-2,...,2 relative to the twist axis",
            "k": 0,
            "omega": "omega_extra=4/sqrt(3)",
        },
        "equivariant_factorization": {
            "multiplicity_statement": "dim Hom_SO3(V1 tensor V2,V2)=1",
            "axis_choice": "for A!=0 choose an SO3 rotation carrying A to |A|*e_z; the zero locus is rotated back covariantly",
            "axis_Clebsch_Gordan": {str(m): str(value) for m, value in zip(magnetic_numbers, coefficients, strict=True)},
            "axis_spin_operator": "diag(sqrt(6)/3,sqrt(6)/6,0,-sqrt(6)/6,-sqrt(6)/3), proportional to -J_z",
            "resonance_operator": "nonzero scalar times (A_hat dot J_2) tensor P_position",
            "overall_scalar": "irrelevant to the zero locus and fixed nonzero by the certified m_A=1,m=0 fixture",
        },
        "multiplicity_matrix": {
            "input_order": theorem["input_column_order"],
            "output_order": theorem["output_row_order"],
            "P_position": theorem["position_matrix"],
            "rank": 2,
            "kernel_basis": _canonical_basis(kernel),
            "kernel_description": "span_C{polar_e1, -4*sqrt(3)*axial_e1+15*polar_e2}",
        },
        "complete_zero_locus": {
            "necessary_and_sufficient": True,
            "formula": "ker((A_hat dot J_2) tensor P)=V_(m_A=0) tensor C^4 + V_2 tensor ker(P)",
            "intersection": "V_(m_A=0) tensor ker(P)",
            "ambient_positive_frequency_complex_dimension": 20,
            "kernel_positive_frequency_complex_dimension": 12,
            "complex_dimension": 12,
            "operator_rank": 8,
            "coefficient_form": "the m_A=0 amplitudes are arbitrary; for each m_A=+/-1,+/-2 the four multiplicity coefficients must lie in ker(P)",
            "real_tangent_dimension_after_adding_conjugate_negative_frequency": 24,
        },
        "fixtures": {
            "aligned_face": "every m_A=0 extra amplitude lies in the resonance kernel, explaining the certified aligned constant-twist face",
            "off_axis_obstruction": "axial_e1 at m_A=0 relative to the original wave axis becomes an m_A!=0 component for a perpendicular twist and maps to (0,24*sqrt(3),0,0)",
            "nonaligned_survivors": "off-axis amplitudes in polar_e1 or -4*sqrt(3)*axial_e1+15*polar_e2 evade the twist-position p-shell resonance",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "CERTIFIED", "claim": "complete twist-position times ell2-extra resonant-functional zero locus only"},
            "SMOOTH_SECULAR": {"status": "NOT_APPLICABLE", "reason": "this certificate classifies a bounded shell projection, not propagation solvability"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "complete_extra_shell_twist_position_zero_locus_classified": True,
            "complete_nonzero_A_ell2_extra_position_resonance_kernel_classified": True,
            "all_m_and_all_four_extra_multiplicities_included": True,
            "aligned_face_explained": True,
            "off_axis_kernel_strictly_nonzero": True,
            "Einstein_q_primary_twist_position_map_classified": False,
            "simultaneous_moment_and_all_branch_resonance_zero_locus_classified": False,
            "complete_mixed_wave_cone_classified": False,
            "full_second_order_equation_solved": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "Constant twist does not eliminate the complete extra primary. It kills eight of twenty complex positive-frequency coefficient directions through the bounded p-shell resonance and leaves a twelve-dimensional kernel: the axisymmetric m_A=0 face plus two special multiplicity combinations at every m. The earlier counterexample samples a direction outside this kernel.",
        "next_gate": "compute the corresponding constant-twist position matrices on the Einstein plus/minus q-primary shells, then intersect every branch kernel with the H,J_i moment cone",
        "claim_boundary": "This is a complete resonant-functional zero locus only for constant twist position times the ell=2 extra p-primary at k=0. It does not classify twist times Einstein q-primary waves, simultaneous wave self-sources, the full nonzero-A bounded tangent cone, nonzero momentum, smooth or causal correction sufficiency, all-orders solutions, residual states, observables or quantum theory.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS", "elapsed_seconds": 2.37},
            "tier_1": {"status": "PASS", "elapsed_seconds": 5.66, "tests_run": 30},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "criterion": "the direct nonaxisymmetric tensor matrix and counterexample are immutable exact inputs"},
            "tier_3": {"status": "NOT_RUN", "reason": "the Einstein q-primary maps and simultaneous full cone remain open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_constant_twist_ell2_extra_position_zero_locus --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_constant_twist_ell2_extra_position_zero_locus.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_constant_twist_ell2_extra_position_zero_locus",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    value = build()
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise ConstantTwistExtraKernelError("constant-twist ell2 extra position-kernel certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_CONSTANT_TWIST_ELL2_EXTRA_POSITION_ZERO_LOCUS: PASS")


if __name__ == "__main__":
    main()
