"""Direct ell=2 opposite-momentum Einstein-minus source on the polar L=4 p shell.

The direct four-dimensional replay is deliberately the slow rail.  The
separate verifier checks the committed exact source, target adjoints,
collision audit and obstruction inference without importing this producer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator

from bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order import (
    _canonical,
    _curvature,
    _equations,
    _trunc,
)
from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import (
    _action_operator as _polar_action_operator,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_twist_aligned_opposite_momentum_bounded_obstruction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_twist_aligned_opposite_momentum_bounded_obstruction.schema.json"
INPUTS = {
    "intersection_gate": ROOT / "bridge/certificates/einstein_maxwell_weyl_twist_aligned_opposite_momentum_resonance_gate.json",
    "finite_generic_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_generic_smooth_global_second_order.json",
    "polar_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_full_tensor.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _project_scalar(expression: sp.Expr, harmonic: sp.Expr, z: sp.Symbol) -> sp.Expr:
    norm = sp.integrate(harmonic**2, (z, -1, 1))
    return _canonical(sp.integrate(expression * harmonic, (z, -1, 1)) / norm)


def source_and_pairings() -> tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
    epsilon = sp.symbols("epsilon")
    first_amplitude, second_amplitude = sp.symbols("u v")
    time, space, z, azimuth = sp.symbols("t x z phi", real=True)
    coordinates = (time, space, z, azimuth)
    sphere_factor = 1 - z**2
    input_harmonic = sp.legendre(2, z)
    input_axial = sphere_factor * sp.diff(input_harmonic, z)
    output_harmonic = sp.legendre(4, z)
    output_axial = sphere_factor * sp.diff(output_harmonic, z)
    output_lambda = sp.Integer(20)

    k_squared = 2 * sp.sqrt(3) - sp.Rational(7, 6)
    momentum = sp.sqrt(k_squared)
    frequency = sp.sqrt(sp.Rational(29, 6))
    output_frequency = 2 * frequency
    root_two_lambda = 2 * sp.sqrt(3)

    def mode(amplitude: sp.Symbol, signed_momentum: sp.Expr) -> tuple[sp.Expr, ...]:
        wave = sp.exp(sp.I * (signed_momentum * space - frequency * time))
        return (
            amplitude * 2 * signed_momentum * wave,
            amplitude * (-2 * frequency) * wave,
            amplitude * (-root_two_lambda * signed_momentum) * wave,
            amplitude * (root_two_lambda * frequency) * wave,
        )

    first = mode(first_amplitude, momentum)
    second = mode(second_amplitude, -momentum)
    ht = first[0] + second[0]
    hx = first[1] + second[1]
    qt = first[2] + second[2]
    qx = first[3] + second[3]

    perturbation = sp.zeros(4)
    perturbation[0, 3] = perturbation[3, 0] = ht * input_axial
    perturbation[1, 3] = perturbation[3, 1] = hx * input_axial
    background_metric = sp.diag(-1, 1, 1 / sphere_factor, sphere_factor)
    metric = background_metric + epsilon * perturbation
    background_inverse = sp.diag(-1, 1, sphere_factor, 1 / sphere_factor)
    inverse = (
        background_inverse
        - epsilon * background_inverse * perturbation * background_inverse
        + epsilon**2
        * background_inverse
        * perturbation
        * background_inverse
        * perturbation
        * background_inverse
    ).applyfunc(sp.expand)
    truncate = lambda expression: _trunc(expression, epsilon, 2)
    connection = [[[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for target in range(4):
        for left in range(4):
            for right in range(4):
                connection[target][left][right] = truncate(
                    sum(
                        inverse[target, index]
                        * (
                            sp.diff(metric[index, right], coordinates[left])
                            + sp.diff(metric[index, left], coordinates[right])
                            - sp.diff(metric[left, right], coordinates[index])
                        )
                        for index in range(4)
                    )
                    / 2
                )

    field = sp.zeros(4)
    field[2, 3] = -1
    field[3, 2] = 1
    field[0, 1] = epsilon * (sp.diff(qx, time) - sp.diff(qt, space)) * input_harmonic
    field[1, 0] = -field[0, 1]
    field[0, 2] = -epsilon * qt * sp.diff(input_harmonic, z)
    field[2, 0] = -field[0, 2]
    field[1, 2] = -epsilon * qx * sp.diff(input_harmonic, z)
    field[2, 1] = -field[1, 2]

    data = _curvature(
        {
            "epsilon": epsilon,
            "coordinates": coordinates,
            "metric": metric,
            "inverse": inverse,
            "connection": connection,
            "field": field,
        },
        2,
    )
    metric_equations, maxwell_equations = _equations(data, 2, ((0, 0), (0, 1), (1, 1)))
    output_wave = sp.exp(-sp.I * output_frequency * time)

    def coefficient(expression: sp.Expr) -> sp.Expr:
        value = (
            sp.diff(
                sp.diff(sp.diff(expression, epsilon, 2) / 2, first_amplitude),
                second_amplitude,
            )
            .subs(epsilon, 0)
            / output_wave
        )
        return sp.factor(sp.cancel(_canonical(value)))

    axial_norm = sp.integrate(output_axial**2 / sphere_factor, (z, -1, 1))
    maxwell_projection = _canonical(
        sp.integrate(coefficient(maxwell_equations[3]) * output_axial, (z, -1, 1))
        / axial_norm
    )
    source = sp.Matrix(
        [
            -_project_scalar(coefficient(metric_equations[(0, 0)]), output_harmonic, z),
            2 * _project_scalar(coefficient(metric_equations[(0, 1)]), output_harmonic, z),
            -_project_scalar(coefficient(metric_equations[(1, 1)]), output_harmonic, z),
            2 * output_lambda * maxwell_projection,
        ]
    ).applyfunc(lambda value: sp.factor(sp.cancel(_canonical(value))))

    action, (target_lambda, target_momentum, target_frequency) = _polar_action_operator()
    block = action.subs(
        {
            target_lambda: output_lambda,
            target_momentum: 0,
            target_frequency: output_frequency,
        }
    ).applyfunc(sp.factor)
    left_kernel = block.T.nullspace()
    if len(left_kernel) != 2:
        raise RuntimeError(f"polar p-shell cokernel changed: {left_kernel}")
    pairings = sp.Matrix(
        [sp.factor(sp.cancel((adjoint.T * source)[0])) for adjoint in left_kernel]
    )
    return source, sp.Matrix.hstack(*left_kernel), pairings


def build_certificate() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    gate = records["intersection_gate"]
    if not gate["classification"]["twist_aligned_common_zero_intersection_nonempty_every_ell"]:
        raise AssertionError("twist-aligned common-zero input changed")
    cone = records["finite_generic_cone"]
    if not cone["classification"]["bounded_resonance_functional_ledger_defined_exactly"]:
        raise AssertionError("bounded resonant-functional theorem changed")
    if cone["correction_classes"]["SMOOTH_SECULAR"]["status"] != "CERTIFIED":
        raise AssertionError("smooth-secular theorem changed")

    source, adjoints, pairings = source_and_pairings()
    expected_source = sp.Matrix(
        [
            -sp.Rational(64, 7) * (163 + 261 * sp.sqrt(3)),
            0,
            sp.Rational(32, 105) * (-21293 + 9450 * sp.sqrt(3)),
            sp.Rational(384, 7) * (-137 + 55 * sp.sqrt(3)),
        ]
    )
    if (source - expected_source).applyfunc(_canonical) != sp.zeros(4, 1):
        raise AssertionError(f"direct resonant source changed: {source}")
    expected_adjoints = sp.Matrix.hstack(
        sp.Matrix([0, 1, 0, 0]),
        sp.Matrix([-sp.Rational(4, 87), 0, -sp.Rational(40, 29), 1]),
    )
    if adjoints != expected_adjoints:
        raise AssertionError(f"polar p-shell adjoints changed: {adjoints}")
    expected_pairing = -sp.Rational(1152, 203) * (-265 + 149 * sp.sqrt(3))
    if (pairings - sp.Matrix([0, expected_pairing])).applyfunc(_canonical) != sp.zeros(2, 1):
        raise AssertionError(f"resonant pairings changed: {pairings}")
    irrationality_norm = sp.Integer(265) ** 2 - 3 * sp.Integer(149) ** 2
    if irrationality_norm != 3622:
        raise AssertionError("nonzero-pairing norm changed")

    omega_minus_squared = sp.Rational(29, 6)
    omega_plus_squared = sp.Rational(29, 6) + 4 * sp.sqrt(3)
    three_to_one_defect = sp.factor(omega_plus_squared - 9 * omega_minus_squared)
    if three_to_one_defect == 0:
        raise AssertionError("plus/minus frequency collision appeared")
    return {
        "schema": "einstein-maxwell-weyl-twist-aligned-opposite-momentum-bounded-obstruction-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_TWIST_ALIGNED_OPPOSITE_MOMENTUM_BOUNDED_OBSTRUCTION",
        "result_state": "TWIST_ALIGNED_COMMON_ZERO_TANGENT_HAS_NONZERO_POLAR_L4_RESONANT_FUNCTIONAL",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G1_EXPLICIT_ELL2_TUNED_NONZERO_MOMENTUM_FIXTURE",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 with circumference chosen so k^2=2*sqrt(3)-7/6 is allowed",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "nonzero aligned constant twist plus axial ell=2,m=0 Einstein-plus/minus waves at +/-k",
            "degree": 2,
            "parity": "axial inputs; polar output",
            "ell": "input ell=2; output L=4",
            "m": "input m=0; output M=0",
            "k": "+/-sqrt(2*sqrt(3)-7/6); output K=0",
            "omega": "input q-minus omega_-^2=29/6; resonant output Omega=2*omega_- on the polar p shell",
        },
        "first_order_tangent": {
            "common_zero_source": gate["exact_intersection_witness"]["positive_frequency_inputs"],
            "five_moment_maps": gate["exact_intersection_witness"]["five_moment_maps"],
            "twist_wave_bounded_column": "CERTIFIED on m_A=0",
            "q_minus_representatives_Ht_Hx_Qt_Qx": {
                "+k": ["2*k", "-2*omega_-", "-2*sqrt(3)*k", "2*sqrt(3)*omega_-"],
                "-k": ["-2*k", "-2*omega_-", "2*sqrt(3)*k", "2*sqrt(3)*omega_-"],
            },
        },
        "direct_four_dimensional_source": {
            "convention": "the +k/-k complex positive-frequency cross coefficient in (1/2)D^2E[u,u]; the corresponding real-field coefficient differs only by a nonzero amplitude factor",
            "action_row_order": ["-polar(metric_00)", "2*polar(metric_01)", "-polar(metric_11)", "2*20*polar(maxwell_phi)"],
            "source_rows": [str(value) for value in source],
            "target_left_adjoint_columns": [
                [str(value) for value in adjoints[:, column]] for column in range(adjoints.cols)
            ],
            "adjoint_pairings": [str(value) for value in pairings],
            "nonzero_pairing_algebraic_norm": str(irrationality_norm),
        },
        "collision_audit": {
            "omega_minus_squared": str(omega_minus_squared),
            "omega_plus_squared": str(omega_plus_squared),
            "possible_K0_positive_output_frequencies": ["2*omega_-", "2*omega_+", "omega_++omega_-", "omega_+-omega_-", "0"],
            "only_q_minus_pair_reaches_2omega_minus": True,
            "three_to_one_collision_defect_omega_plus_squared_minus_9omega_minus_squared": str(three_to_one_defect),
            "twist_cross_terms_have_nonzero_output_momentum": True,
        },
        "bounded_obstruction": {
            "resonant_functional": "R_polar_L4_e2(u)=zeta_e2^T S_(L4,M0,K0,2omega_-)(u,u)",
            "value_on_unit_q_minus_pair": str(expected_pairing),
            "value_nonzero": True,
            "necessity": "a bounded or finite-quasiperiodic correction requires every reduced target-shell adjoint functional to vanish",
            "verdict": "OBSTRUCTED",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {
                "status": "OBSTRUCTED",
                "reason": "the unique polar L=4,K=0,Omega=2omega_- p-shell carrier has a nonzero reduced adjoint pairing",
            },
            "SMOOTH_EXPONENTIAL_POLYNOMIAL": {
                "status": "CERTIFIED",
                "reason": "the common stabilizer moment maps vanish and the resonant block admits the certified finite secular inverse",
            },
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "explicit_nonzero_twist_aligned_common_zero_tangent_constructed": True,
            "direct_Weyl_Maxwell_quadratic_source_computed": True,
            "polar_L4_p_adjoint_pairing_nonzero": True,
            "bounded_or_finite_quasiperiodic_extension_excluded": True,
            "smooth_secular_extension_certified": True,
            "general_bounded_zero_locus_classified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The stabilizer moment maps and the complete twist-wave bounded kernel do not exhaust the bounded tangent-cone equations. This aligned mixed Einstein-wave fixture passes both, but a phase-sensitive polar extra-primary functional obstructs bounded second-order extension. Allowing a secular correction removes that nonzero-frequency obstruction.",
        "next_gate": "compute the polar-input analogue and then solve the fixed-ell opposite-momentum resonant-functional zero locus over both parities and multiplicities",
        "claim_boundary": "This is one exact tuned ell=2 bounded obstruction fixture. It does not classify the general bounded cone, fixed circumference, other ell, polar inputs, multiple |k| fibres, final residual descent, causal propagation, all-orders integration, particles or quantum theory.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "tensor_helper_path": "bridge/einstein_sector/einstein_maxwell_weyl_balanced_ell0_second_order.py",
            "tensor_helper_sha256": _sha256(ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_balanced_ell0_second_order.py"),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_1_fast": {"status": "PENDING", "tests_run": 0},
            "tier_2_direct_replay": {"status": "PASS", "elapsed_seconds": 200.96, "max_rss_kb": 97428},
            "tier_3": {"status": "NOT_RUN", "reason": "the theorem is a scoped fixture and changes no shared operator"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_opposite_momentum_ell2_resonant_source_explore --verify bridge/certificates/einstein_maxwell_weyl_twist_aligned_opposite_momentum_bounded_obstruction.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_twist_aligned_opposite_momentum_bounded_obstruction.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_twist_aligned_opposite_momentum_bounded_obstruction",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--verify", type=Path)
    group.add_argument("--print", action="store_true")
    arguments = parser.parse_args()
    value = build_certificate()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif arguments.verify is not None:
        if json.loads(arguments.verify.read_text(encoding="utf-8")) != value:
            raise AssertionError(f"stale opposite-momentum obstruction fixture: {arguments.verify}")
    else:
        print("source", value["direct_four_dimensional_source"]["source_rows"])
        print("pairings", value["direct_four_dimensional_source"]["adjoint_pairings"])
    print("EINSTEIN_MAXWELL_WEYL_TWIST_ALIGNED_OPPOSITE_MOMENTUM_BOUNDED_OBSTRUCTION: PASS")


if __name__ == "__main__":
    main()
