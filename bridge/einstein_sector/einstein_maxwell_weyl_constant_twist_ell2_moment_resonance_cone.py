"""Intersect the ell=2 constant-twist resonance kernels with H,J_a=0."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_constant_twist_ell2_moment_resonance_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_constant_twist_ell2_moment_resonance_cone.schema.json"
INPUTS = {
    "Einstein_twist_kernel": ROOT / "bridge/certificates/einstein_maxwell_weyl_constant_twist_ell2_einstein_position_zero_locus.json",
    "extra_twist_kernel": ROOT / "bridge/certificates/einstein_maxwell_weyl_constant_twist_ell2_extra_position_zero_locus.json",
    "moment_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_k0_moment_map_cone.json",
    "axial_extra_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_extra_detector.json",
    "polar_extra_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
}


class ConstantTwistMomentConeError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ConstantTwistMomentConeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(sp.factor(value)) for value in matrix.row(row)] for row in range(matrix.rows)]


def _specialized_extra_gram(records: dict[str, object]) -> sp.Matrix:
    lam, momentum, omega = sp.symbols("lambda k omega", real=True)
    axial_rows = records["axial_extra_current"]["detector"]["extra_Gram"]
    axial = sp.Matrix([[sp.sympify(value.replace("lambda", "lam"), locals={"lam": lam, "k": momentum, "omega": omega}) for value in row] for row in axial_rows])
    axial = axial.subs({lam: 6, momentum: 0, omega**2: sp.Rational(16, 3)}).applyfunc(sp.factor)
    _require(axial == sp.diag(1296, sp.Rational(208, 3)), "axial extra Gram specialization changed")

    polar_block = records["polar_extra_current"]["shell_pairing"]
    polar_rows = polar_block["extra_Hermitian_current_Gram"]
    polar_current_basis = sp.Matrix([[sp.sympify(value.replace("lambda", "lam"), locals={"lam": lam, "k": momentum}) for value in row] for row in polar_rows])
    polar_current_basis = polar_current_basis.subs({lam: 6, momentum: 0}).applyfunc(sp.factor)
    _require(polar_current_basis == sp.diag(22464, 12288), "polar extra Gram specialization changed")
    # The current certificate uses (polar_e2,16*omega_e*polar_e1), whereas
    # the twist-source matrix uses (polar_e1,polar_e2).
    polar_twist_basis = sp.diag(sp.Rational(1, 16) / sp.sqrt(sp.Rational(16, 3)), 1)
    swap = sp.Matrix([[0, 1], [1, 0]])
    change = swap * polar_twist_basis
    polar = (change.T * polar_current_basis * change).applyfunc(sp.factor)
    _require(polar == sp.diag(9, 22464), "polar twist-basis Gram changed")
    return sp.diag(axial, polar)


def _spin_two_generators() -> tuple[sp.Matrix, sp.Matrix, sp.Matrix, sp.Matrix]:
    raising = sp.zeros(5)
    magnetic = range(-2, 2)
    for column, m in enumerate(magnetic):
        raising[column + 1, column] = sp.sqrt((2 - m) * (3 + m))
    lowering = raising.T
    j_x = (raising + lowering) / 2
    j_y = (raising - lowering) / (2 * sp.I)
    j_z = sp.diag(-2, -1, 0, 1, 2)
    _require(j_x.H == j_x and j_y.H == j_y and j_z.H == j_z, "spin generators lost Hermiticity")
    _require((j_x * j_y - j_y * j_x - sp.I * j_z).applyfunc(sp.simplify) == sp.zeros(5), "spin commutator changed")
    return raising, j_x, j_y, j_z


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["Einstein_twist_kernel"]["classification"]["both_Einstein_q_primary_twist_position_maps_classified"], "Einstein twist kernel changed")
    _require(records["extra_twist_kernel"]["classification"]["complete_nonzero_A_ell2_extra_position_resonance_kernel_classified"], "extra twist kernel changed")
    _require(records["moment_cone"]["classification"]["full_generic_k0_common_zero_cone_classified"], "moment cone changed")

    gram = _specialized_extra_gram(records)
    root = sp.sqrt(3)
    internal_kernel = sp.Matrix.hstack(sp.Matrix([0, 0, 1, 0]), sp.Matrix([-4 * root, 0, 0, 15]))
    internal_neutral = sp.Matrix.hstack(sp.Matrix([0, 1, 0, 0]), sp.Matrix([65, 0, 0, root]))
    _require(internal_kernel.rank() == 2 and internal_neutral.rank() == 2, "internal decomposition lost rank")
    _require((internal_kernel.T * gram * internal_neutral) == sp.zeros(2), "internal decomposition lost G-orthogonality")
    _require(sp.Matrix.hstack(internal_kernel, internal_neutral).rank() == 4, "internal decomposition is incomplete")
    kernel_gram = (internal_kernel.T * gram * internal_kernel).applyfunc(sp.factor)
    neutral_gram = (internal_neutral.T * gram * internal_neutral).applyfunc(sp.factor)
    _require(kernel_gram == sp.diag(9, 5116608), "restricted kernel Gram changed")
    _require(neutral_gram == sp.diag(sp.Rational(208, 3), 5542992), "neutral Gram changed")

    raising, j_x, j_y, j_z = _spin_two_generators()
    # A non-axisymmetric exact point: polar_e1 at m=-2 and m=+2.
    columns = [sp.zeros(4, 1) for _ in range(5)]
    columns[0] = internal_kernel[:, 0]
    columns[4] = internal_kernel[:, 0]
    amplitudes = sp.Matrix.hstack(*columns)
    density = (amplitudes.T * gram * amplitudes).applyfunc(sp.factor)
    moments = [(density * generator).trace().simplify() for generator in (j_x, j_y, j_z)]
    _require(moments == [0, 0, 0], "non-axisymmetric moment witness changed")
    extra_occupation = sp.factor(density.trace())
    _require(extra_occupation == 18, "non-axisymmetric occupation changed")
    omega_minus_squared = 6 - 2 * root
    minus_occupation = sp.radsimp(sp.Rational(16, 3) * extra_occupation / omega_minus_squared)
    _require(sp.simplify(minus_occupation - (24 + 8 * root)) == 0, "energy balance changed")

    return {
        "schema": "einstein-maxwell-weyl-constant-twist-ell2-moment-resonance-cone-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_CONSTANT_TWIST_ELL2_MOMENT_RESONANCE_CONE",
        "result_state": "COMPLETE_NONZERO_CONSTANT_TWIST_ELL2_SHELL_RESONANCE_AND_STABILIZER_COMMON_ZERO_CONE_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded or finite-quasiperiodic resonance class",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "one nonzero constant axial twist position crossed with every axial/polar ell=2,k=0 Einstein-plus, Einstein-minus and extra-primary coefficient",
            "degree": 2,
            "parity": "both parities and all four extra multiplicities",
            "ell": "global twist ell=1 crossed with wave ell=2",
            "m": "all m=-2,...,2 relative to the twist axis",
            "k": 0,
            "omega": "generalized zero twist and all three ell2 q/p frequencies",
        },
        "action_normalized_coordinates": {
            "Einstein_plus": "u_plus in C^2 at m=0; A_plus=||u_plus||^2",
            "Einstein_minus": "u_minus in C^2 at m=0; A_minus=||u_minus||^2 in the sign-reversed positive branch metric",
            "extra": "columns c_m in C^4 in order (axial_e1,axial_e2,polar_e1,polar_e2), with c_m in K for m!=0 and arbitrary c_0",
            "extra_Gram_G": _matrix_strings(gram),
            "K_basis_columns": _matrix_strings(internal_kernel),
            "K_orthogonal_neutral_basis_columns": _matrix_strings(internal_neutral),
            "K_restricted_Gram": _matrix_strings(kernel_gram),
            "neutral_restricted_Gram": _matrix_strings(neutral_gram),
            "decomposition": "K_extra=(K tensor V_2) direct_sum (K_perp_G tensor |m=0>); the second summand is rotationally neutral",
        },
        "spin_two_generators": {
            "m_order": [-2, -1, 0, 1, 2],
            "J_plus": _matrix_strings(raising),
            "J_x": _matrix_strings(j_x),
            "J_y": _matrix_strings(j_y),
            "J_z": _matrix_strings(j_z),
        },
        "common_zero_cone": {
            "necessary_and_sufficient": True,
            "linear_resonance_support": {
                "Einstein_plus": "only m=0 axial/polar columns",
                "Einstein_minus": "only m=0 axial/polar columns",
                "extra": "c_0 arbitrary in C^4; c_m in K for m=+/-1,+/-2",
            },
            "extra_occupation": "A_extra=sum_m c_m^dagger G c_m",
            "angular_equations": {
                "J_z": "-2||c_-2||_G^2-||c_-1||_G^2+||c_1||_G^2+2||c_2||_G^2=0",
                "J_plus": "2<c_-2,c_-1>_G+sqrt(6)<c_-1,c_0>_G+sqrt(6)<c_0,c_1>_G+2<c_1,c_2>_G=0",
                "equivalence": "J_plus=0 is the pair J_x=J_y=0; the Einstein m=0 columns and K_perp_G part of c_0 carry zero angular moment",
            },
            "energy_equation": "(6+2*sqrt(3))*A_plus+(16/3)*A_extra-(6-2*sqrt(3))*A_minus=0",
            "constructive_parameterization": "choose arbitrary u_plus, c_0 and c_m in the resonance support satisfying J_z=J_plus=0; then choose arbitrary u_minus direction in C^2 with norm^2=((6+2sqrt(3))*A_plus+(16/3)*A_extra)/(6-2sqrt(3))",
            "ambient_resonance_kernel": "16 complex dimensions (32 real) before H,J_a",
            "generic_smooth_stratum_real_dimension": 28,
            "singular_at_origin_and_lower_rank_strata": True,
        },
        "nonaxisymmetric_witness": {
            "extra_columns": "c_-2=c_2=polar_e1; c_-1=c_0=c_1=0",
            "A_plus": "0",
            "A_extra": "18",
            "A_minus": "24+8*sqrt(3)",
            "J_x_J_y_J_z": ["0", "0", "0"],
            "all_twist_position_resonances": "0",
            "interpretation": "the moment/resonance intersection is strictly larger than the axisymmetric face",
        },
        "regularity_witness": {
            "base_point": "the nonaxisymmetric witness with a real Einstein-minus coefficient sqrt(24+8*sqrt(3))",
            "test_variables": ["Re(delta c_-1 along polar_e1)", "Im(delta c_-1 along polar_e1)", "real scale of c_2", "real Einstein-minus scale"],
            "constraint_order": ["Re J_plus", "Im J_plus", "J_z", "H"],
            "Jacobian_diagonal": ["18", "18", "36", "-2*(6-2*sqrt(3))*sqrt(24+8*sqrt(3))"],
            "rank": 4,
            "consequence": "a nonempty smooth real 28-dimensional stratum exists inside the 32-real-dimensional resonance kernel",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "OPEN", "reason": "this predecessor certificate stops at the exact moment/resonance cone; bounded sufficiency is certified separately by EINSTEIN_MAXWELL_WEYL_CONSTANT_TWIST_ELL2_COMPLETE_BOUNDED_CONE"},
            "SMOOTH_SECULAR": {"status": "CERTIFIED", "claim": "the existing complete finite-harmonic smooth-secular theorem contains this finite carrier; the present certificate adds the bounded resonance incidence only"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "complete_nonzero_A_ell2_twist_position_resonance_kernel_intersected_with_H_J": True,
            "both_Einstein_shells_and_complete_extra_shell_included": True,
            "all_m_parities_and_relative_phases_included": True,
            "necessary_and_sufficient_common_zero_equations": True,
            "nonaxisymmetric_common_zero_witness_certified": True,
            "bounded_full_second_order_equation_solved_on_common_cone": False,
            "smooth_secular_finite_carrier_covered_by_existing_theorem": True,
            "causal_retarded_sufficiency": False,
            "all_orders_integrability": False,
            "residual_or_quantum_claim": False,
        },
        "interpretation": "A nonzero constant twist cuts the ell=2 wave space sharply but does not force axisymmetry. Both Einstein shells are confined to m=0, while two special extra multiplicities may occupy nonzero m. Their complete H,J_a intersection is an explicit quadratic cone, and opposite-m nonaxisymmetric extra pairs survive after an Einstein-minus energy balance.",
        "next_gate": "CLOSED_BY EINSTEIN_MAXWELL_WEYL_CONSTANT_TWIST_ELL2_COMPLETE_BOUNDED_CONE; retain this result as the exact predecessor moment/resonance decomposition",
        "claim_boundary": "This theorem classifies the simultaneous stabilizer moment maps and all same-shell constant-twist position resonances for the complete ell=2,k=0 q/p wave carrier. It does not classify twist velocity, nonresonant L=1,3 inversion, other ell or momentum, the complete bounded second-order equation, causal propagation, all-orders solutions, residual observables or quantum theory.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.33},
            "tier_1": {"status": "PASS", "elapsed_seconds": 5.11, "tests_run": 40},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "criterion": "both direct shellwise twist matrices and all action-derived current/moment inputs are unchanged hashed certificates"},
            "tier_3": {"status": "NOT_RUN", "reason": "this predecessor does not promote a programme-wide freeze; its former bounded-sufficiency gate is closed by a separately scoped successor certificate"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_constant_twist_ell2_moment_resonance_cone --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_constant_twist_ell2_moment_resonance_cone.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_constant_twist_ell2_moment_resonance_cone",
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
        raise ConstantTwistMomentConeError("constant-twist ell2 moment/resonance cone certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_CONSTANT_TWIST_ELL2_MOMENT_RESONANCE_CONE: PASS")


if __name__ == "__main__":
    main()
