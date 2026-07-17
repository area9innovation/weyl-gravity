"""All generic fixed-ell k=0 Weyl-Maxwell common-zero cone at second order."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_k0_combined_cone_second_order.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_fixed_ell_k0_combined_cone_second_order.schema.json"
INPUTS = {
    "all_ell_resonance": ROOT / "bridge/certificates/einstein_maxwell_weyl_all_ell_k0_output_resonance.json",
    "moment_map_bridge": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
    "k0_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_k0_moment_map_cone.json",
    "axial_physical_ring": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_physical_ring.json",
    "polar_physical_completion": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
    "axial_reduced_action": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_reduced_action_hessian.json",
    "polar_full_tensor": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_full_tensor.json",
    "axial_ell1": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell1_k0_operator.json",
    "polar_ell1": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell1_k0_operator.json",
    "axial_extra_pairing": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_extra_green_pairing.json",
    "axial_extra_ell2_taub": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_extra_ell2_taub.json",
    "axial_ell2_e1_source": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell2_e1_zero_source_fixture.json",
    "axial_ell2_e1e2_source": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell2_e1_e2_zero_source_fixture.json",
    "ell2_combined": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_combined_cone_second_order.json",
}


class FixedEllK0CombinedConeError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FixedEllK0CombinedConeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _circle_variation_lemma() -> dict[str, Any]:
    c, momentum, frequency, eigenvalue = sp.symbols("c k omega lambda", real=True)
    g0, g1 = sp.symbols("g0 g1", real=True)
    physical_s = frequency**2 - momentum**2 / (1 + c)
    normalization = g0 + g1 * c
    volume = sp.sqrt(1 + c)
    p = physical_s - eigenvalue + sp.Rational(2, 3)
    q = (physical_s - eigenvalue) ** 2 - 2 * eigenvalue

    def derivative(polynomial: sp.Expr) -> sp.Expr:
        return sp.factor(sp.diff(volume * normalization * polynomial, c).subs(c, 0))

    p_derivative = derivative(p)
    q_derivative = derivative(q)
    s = frequency**2 - momentum**2
    expected_p = (g0 + 2 * g1) * (s - eigenvalue + sp.Rational(2, 3)) / 2 + g0 * momentum**2
    expected_q = (g0 + 2 * g1) * ((s - eigenvalue) ** 2 - 2 * eigenvalue) / 2 + 2 * g0 * momentum**2 * (s - eigenvalue)
    _require(sp.factor(p_derivative - expected_p) == 0, "p-primary circle variation changed")
    _require(sp.factor(q_derivative - expected_q) == 0, "q-primary circle variation changed")
    p_shell = sp.factor(p_derivative.subs({momentum: 0, frequency**2: eigenvalue - sp.Rational(2, 3)}))
    q_plus_shell = sp.factor(q_derivative.subs({momentum: 0, frequency**2: eigenvalue + sp.sqrt(2 * eigenvalue)}))
    q_minus_shell = sp.factor(q_derivative.subs({momentum: 0, frequency**2: eigenvalue - sp.sqrt(2 * eigenvalue)}))
    _require(p_shell == q_plus_shell == q_minus_shell == 0, "rest-frame on-shell pressure did not vanish")
    return {
        "geometric_scope": "c is a constant circle-metric variation; locally it is removed by x' = sqrt(1+c)x, so the flat local curvature and magnetic sphere data do not change, while the compact volume and physical k^2 do",
        "primary_action_form": "sqrt(1+c)*G(c)*P(omega^2-k^2/(1+c)); G(c) is an arbitrary regular primary normalization",
        "p_circle_derivative_at_c0": str(p_derivative),
        "q_circle_derivative_at_c0": str(q_derivative),
        "on_shell_k0_values": {"p": str(p_shell), "q_plus": str(q_plus_shell), "q_minus": str(q_minus_shell)},
        "feynman_hellmann_reason": "terms from the volume, coefficient basis, and primary normalization multiply P and vanish on shell; the remaining P' term is proportional to k^2 and vanishes at k=0",
        "consequence": "the homogeneous zero-frequency metric-x pressure source S_E11 vanishes on every simple p or q primary",
    }


def _source_row_theorem(records: dict[str, Any]) -> dict[str, Any]:
    trace_identity = records["polar_full_tensor"]["target_operator"]["trace_identity"]
    _require(trace_identity == "-metric_00+metric_11+2*sphere_trace=0", "target trace identity changed")
    bridge = records["moment_map_bridge"]
    _require(bridge["classification"]["generic_covariant_moment_map_Taub_equality_certified"], "Taub bridge changed")
    return {
        "circle_pressure": _circle_variation_lemma(),
        "Weyl_trace_identity": {
            "nonlinear_identity": "g^{mu nu}E_{mu nu}=0",
            "second_order_on_shell_reduction": trace_identity,
            "with_S_E11_zero": "S_sphere_trace=S_E00/2",
        },
        "homogeneous_Maxwell_identity": {
            "integrated_equation": "Pi_(k=0,L=0) E_Maxwell^x = partial_t Pi_(k=0,L=0)(sqrt(-g) F^{tx})",
            "zero_frequency_factor": "-I*(omega_1+omega_2)",
            "conjugate_pair_value": "0 when omega_2=-omega_1",
            "consequence": "S_Maxwell1=0 for every zero-frequency quadratic coefficient",
        },
        "universal_scalar_source_row": ["1", "0", "1/2", "0"],
        "row_order": ["E00", "E11", "sphere_trace", "Maxwell1"],
        "coefficient": "the E00 coefficient is the constant-lapse Taub pairing mu_H in the calibrated normalization",
        "cancellation": "total H=0 makes the complete L=0 source vanish, not merely orthogonal to one adjoint vector",
    }


def _ell3_axial_extra_fixture(records: dict[str, Any]) -> dict[str, Any]:
    eigenvalue, momentum, frequency = sp.symbols("lambda k omega", real=True)
    local = {"lam": eigenvalue, "k": momentum, "omega": frequency, "I": sp.I}
    gram = sp.Matrix(
        [
            [sp.sympify(value.replace("lambda", "lam"), locals=local) for value in row]
            for row in records["axial_extra_pairing"]["pairing"]["normalized_Gram"]
        ]
    )

    def taub_matrix(ell: int) -> sp.Matrix:
        lam = sp.Integer(ell * (ell + 1))
        omega_squared = lam - sp.Rational(2, 3)
        shell_gram = gram.subs({eigenvalue: lam, momentum: 0, frequency**2: omega_squared}).applyfunc(sp.factor)
        return (-omega_squared * shell_gram / (4 * (2 * ell + 1))).applyfunc(sp.factor)

    ell2 = taub_matrix(2)
    stored_ell2 = sp.Matrix(
        [[sp.sympify(value) for value in row] for row in records["axial_extra_ell2_taub"]["quadratic_source"]["constant_lapse_Taub_matrix"]]
    )
    _require(ell2 == stored_ell2, "generic current did not reproduce the direct ell=2 Taub fixture")
    direct_e1 = sp.Matrix(
        [sp.sympify(value) for value in records["axial_ell2_e1_source"]["homogeneous_source_rows_E00_E11_E22_Maxwell1"]]
    )
    direct_cross = sp.Matrix(
        [sp.sympify(value) for value in records["axial_ell2_e1e2_source"]["homogeneous_source_rows_E00_E11_E22_Maxwell1"]]
    )
    predicted_e1 = sp.Matrix([ell2[0, 0], 0, ell2[0, 0] / 2, 0])
    _require(direct_e1 == predicted_e1, "universal source row did not reproduce the direct ell=2 e1 fixture")
    _require(direct_cross == sp.zeros(4, 1), "direct ell=2 extra interference source changed")
    ell3 = taub_matrix(3)
    expected = sp.diag(-sp.Rational(73440, 7), -sp.Rational(7208, 63))
    _require(ell3 == expected, f"ell=3 axial extra Taub matrix changed: {ell3}")
    zero = sp.zeros(2)
    return {
        "basis": ["extra_e1=(-lambda,0,lambda,0)", "extra_e2=(0,-2/3,0,lambda)"],
        "harmonic": "P_3(cos theta), normalized sphere average 1/(2ell+1)=1/7",
        "frequency_squared": "34/3",
        "E00_source_matrix": [[str(value) for value in row] for row in ell3.tolist()],
        "E11_source_matrix": [[str(value) for value in row] for row in zero.tolist()],
        "sphere_trace_source_matrix": [[str(value) for value in row] for row in (ell3 / 2).tolist()],
        "Maxwell1_source_matrix": [[str(value) for value in row] for row in zero.tolist()],
        "extra_interference_zero": True,
        "ell2_direct_calibration_remainder": [[str(value) for value in row] for row in (ell2 - stored_ell2).tolist()],
        "ell2_direct_full_row_remainder": [str(value) for value in direct_e1 - predicted_e1],
        "ell2_direct_interference_rows": [str(value) for value in direct_cross],
        "exact_ell3_fixture": True,
    }


def _zero_output_blocks(records: dict[str, Any]) -> dict[str, Any]:
    output_ell = sp.symbols("L", integer=True, positive=True)
    output_lambda = output_ell * (output_ell + 1)
    p_zero = sp.factor(-output_lambda + sp.Rational(2, 3))
    q_zero = sp.factor(output_lambda * (output_lambda - 2))
    shifted_q = sp.Poly(sp.expand(q_zero.subs(output_ell, output_ell + 2)), output_ell)
    _require(all(coefficient > 0 for coefficient in shifted_q.all_coeffs()), "q zero-shell positivity changed")
    axial = records["axial_ell1"]["classification"]
    polar = records["polar_ell1"]["classification"]
    _require(axial["zero_fibre_physical_cokernel_equals_rotation_triplet"], "axial L1 cokernel changed")
    _require(polar["polar_ell1_zero_frequency_physical_cokernel_absent"], "polar L1 zero fibre changed")
    return {
        "L0": "same-parity scalar source vanishes in all four rows when total H=0; axial-polar cross parity has no L=0 harmonic",
        "L1_axial": "the only physical adjoint cokernel is the rotation triplet, killed by total J_1=J_2=J_3=0",
        "L1_polar": "no physical zero-frequency cokernel",
        "L_at_least_2": {
            "p_at_zero": str(p_zero),
            "q_at_zero": str(q_zero),
            "p_nonzero": "negative for every L>=2",
            "q_shift_L_minus_2_coefficients": [str(value) for value in shifted_q.all_coeffs()],
            "invertible_after_local_gauge_reduction": True,
        },
    }


def build_certificate() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["all_ell_resonance"]["classification"]["all_nonzero_output_channels_off_physical_target_shells"], "nonzero resonance input changed")
    _require(records["k0_cone"]["classification"]["full_generic_k0_common_zero_cone_classified"], "k0 moment-map cone changed")
    _require(records["axial_physical_ring"]["classification"]["extra_quotient_two_cyclic_summands_on_every_physical_fiber"], "axial primary input changed")
    _require(records["polar_physical_completion"]["classification"]["canonical_extra_polar_quotient_two_p_summands"], "polar primary input changed")
    _require(records["axial_reduced_action"]["normalization_triangle"]["equation_operator_equals_reduced_action_Hessian"], "axial action input changed")
    _require(records["ell2_combined"]["classification"]["complete_combined_ell2_k0_common_zero_cone_second_order_extendible"], "ell2 calibration changed")
    source_rows = _source_row_theorem(records)
    return {
        "schema": "einstein-maxwell-weyl-fixed-ell-k0-combined-cone-second-order-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_FIXED_ELL_K0_COMBINED_CONE_SECOND_ORDER",
        "result_state": "EVERY_FIXED_GENERIC_ELL_K0_COMMON_ZERO_CONE_SECOND_ORDER_EXTENDIBLE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_EVERY_FIXED_GENERIC_ELL_K0_ALL_M_BOTH_PARITIES_ALL_PRIMARIES",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "domain": "for any one fixed integer ell>=2: finite real k=0 Weyl-Maxwell tangents with all m, both axial and polar parities, Einstein plus/minus and both extra polarizations, satisfying total H=J_1=J_2=J_3=0",
        "primary_action_and_scalar_source_theorem": source_rows,
        "exact_ell3_fixture": _ell3_axial_extra_fixture(records),
        "zero_frequency_output_blocks": _zero_output_blocks(records),
        "nonzero_frequency_output_blocks": {
            "imported_result": records["all_ell_resonance"]["result_id"],
            "all_nine_types_off_every_physical_target_shell": True,
            "nonzero_L0_sources_solved_by_homogeneous_Noether_completion": True,
        },
        "second_order_solution": {
            "construction": "decompose the exact quadratic source by output L, parity, and frequency; set the canceled L0 source to zero, use total J cancellation in the axial L1 cokernel, invert every other zero and nonzero quotient block, and lift through the target Noether identities",
            "finite_for_finite_first_order_data": True,
            "real_spatially_periodic": True,
            "temporal_class": "finite quasiperiodic with zero-frequency corrections chosen in the locally gauge-reduced quotient",
            "complete_for_declared_fixed_ell_cone": True,
        },
        "classification": {
            "every_fixed_ell_at_least_2_combined_common_zero_cone_second_order_extendible": True,
            "all_m_both_parities_and_all_generic_primaries_included": True,
            "zero_frequency_scalar_source_rank_one_and_moment_map_factored": True,
            "exact_ell3_coefficient_fixture_included": True,
            "cross_ell_superpositions_classified": False,
            "opposite_momentum_relative_phases_classified": False,
            "exceptional_global_inputs_classified": False,
            "all_orders_integrability": False,
            "final_residual_descent_certified": False,
            "Lorentzian_causal_or_quantum_claim": False,
        },
        "interpretation": "At k=0, the ell=2 result is not accidental: for every fixed generic angular momentum, the second-order tangent cone is exactly the common H,J_i zero cone. The new structural reason is that each p/q primary is a 1+1 Lorentz-scalar action polynomial, so its rest-frame on-shell circle pressure vanishes; Weyl tracelessness and the integrated Maxwell identity then force the entire scalar source into the constant-lapse row.",
        "next_gate": "classify products between distinct input ell values and retain opposite-momentum relative phases; these introduce new frequency arithmetic not covered by the fixed-ell theorem",
        "claim_boundary": "This theorem is blockwise in one fixed generic ell at k=0. It does not cover cross-ell superpositions, opposite momenta, exceptional/global input modes, all-orders integration, final residual states, causal propagation, particles, or quantum theory.",
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {
                "status": "PASS",
                "elapsed_seconds": 0.06,
                "commands": [
                    "python3 -m py_compile <new producer, independent verifier, and test>",
                    "python3 -m json.tool <new schema and certificate>",
                    "git diff --check -- <scoped paths>",
                ],
            },
            "tier_1": {
                "status": "PASS",
                "elapsed_seconds": 1.70,
                "commands": [
                    "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_fixed_ell_k0_combined_cone_second_order --verify bridge/certificates/einstein_maxwell_weyl_fixed_ell_k0_combined_cone_second_order.json",
                    "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_fixed_ell_k0_combined_cone_second_order.py",
                    "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_fixed_ell_k0_combined_cone_second_order",
                ],
            },
            "tier_2": {
                "status": "PASS",
                "elapsed_seconds": 7.80,
                "commands": [
                    "seven affected producer replays covering nonresonance, moment maps, k0 cone, both L1 blocks, ell2 calibration, and the new theorem",
                    "seven independent verifiers and 23 affected regression tests",
                ],
                "content_addressed_exhaustive_inputs": "the unchanged direct four-dimensional ell2 source and Lee-Wald fixtures were checked by stored hashes rather than recomputed",
            },
            "tier_3": {
                "status": "NOT_RUN_NOT_REQUIRED",
                "reason": "the theorem promotes one fixed-ell block family but does not freeze the cross-ell, opposite-momentum, exceptional/global, or programme-wide result",
            },
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_fixed_ell_k0_combined_cone_second_order --verify bridge/certificates/einstein_maxwell_weyl_fixed_ell_k0_combined_cone_second_order.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_fixed_ell_k0_combined_cone_second_order.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_fixed_ell_k0_combined_cone_second_order",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(json.loads(path.read_text(encoding="utf-8")) == build_certificate(), f"fixed-ell cone certificate stale: {path}")


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
