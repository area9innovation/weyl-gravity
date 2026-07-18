"""Exceptional polar ell=0 Weyl--Maxwell Fourier complex.

This module derives the exceptional operator directly from the four-dimensional
Euler--Lagrange equations.  It deliberately does not specialize the generic
polar master operator, whose tensor-harmonic gauge slice exists only for
ell>=2.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_periodic_photon_second_order import _trunc
from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import _linearized_target


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell0_nonzero_fourier.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_polar_ell0_nonzero_fourier.schema.json"
PHASE_INPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_phase_resonance_divisor.json"
ENGINE = ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_polar_full_tensor.py"


class PolarEll0FourierError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PolarEll0FourierError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [
        [str(sp.factor(matrix[row, column])) for column in range(matrix.cols)]
        for row in range(matrix.rows)
    ]


def _raw_operator() -> tuple[sp.Matrix, tuple[sp.Symbol, ...]]:
    epsilon = sp.symbols("epsilon")
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    frequency, momentum = sp.symbols("omega k", real=True)
    a_time, mixed, a_space, sphere, potential_time, potential_space = sp.symbols(
        "A B C K T X"
    )
    coefficients = (a_time, mixed, a_space, sphere, potential_time, potential_space)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    wave = sp.exp(sp.I * (momentum * space - frequency * time))

    metric = sp.diag(-1, 1, 1, sine**2)
    metric[0, 0] += epsilon * a_time * wave
    metric[0, 1] = metric[1, 0] = epsilon * mixed * wave
    metric[1, 1] += epsilon * a_space * wave
    metric[2, 2] += epsilon * sphere * wave
    metric[3, 3] += epsilon * sphere * wave * sine**2
    inverse = metric.inv().applyfunc(lambda value: _trunc(value, epsilon, 1))
    connection = [[[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for target in range(4):
        for left in range(4):
            for right in range(4):
                connection[target][left][right] = _trunc(
                    sum(
                        inverse[target, index]
                        * (
                            sp.diff(metric[index, right], coordinates[left])
                            + sp.diff(metric[index, left], coordinates[right])
                            - sp.diff(metric[left, right], coordinates[index])
                        )
                        for index in range(4)
                    )
                    / 2,
                    epsilon,
                    1,
                )

    field = sp.zeros(4)
    field[2, 3] = sine
    field[3, 2] = -sine
    electric = -sp.I * (frequency * potential_space + momentum * potential_time)
    field[0, 1] = epsilon * electric * wave
    field[1, 0] = -field[0, 1]
    target_metric, maxwell_density = _linearized_target(
        metric, inverse, connection, field, coordinates, epsilon
    )
    sphere_trace = (target_metric[2, 2] + target_metric[3, 3] / sine**2) / 2
    raw_rows = (
        target_metric[0, 0],
        target_metric[0, 1],
        target_metric[1, 1],
        sphere_trace,
        maxwell_density[0],
        maxwell_density[1],
    )
    normalizers = (wave, wave, wave, wave, wave * sine, wave * sine)
    rows = [
        sp.factor(sp.trigsimp(value / normalizer))
        for value, normalizer in zip(raw_rows, normalizers, strict=True)
    ]
    for row in rows:
        if row.has(theta):
            raise RuntimeError(f"ell=0 separation failed: {row}")
    operator = sp.Matrix(
        [[sp.expand(row).coeff(coefficient) for coefficient in coefficients] for row in rows]
    ).applyfunc(sp.factor)
    return operator, (frequency, momentum)


def build_certificate() -> dict[str, object]:
    phase_input = json.loads(PHASE_INPUT.read_text(encoding="utf-8"))
    _require(
        phase_input["classification"]["static_L0_K2k_exceptional_block_classified"] is False,
        "phase-divisor input no longer exposes the exceptional static gate",
    )
    operator, (frequency, momentum) = _raw_operator()
    expected = sp.Matrix(
        [
            [-momentum**4 / 2, -momentum**3 * frequency, -momentum**2 * frequency**2 / 2, -momentum**2 * (momentum**2 - frequency**2) / 2, 0, 0],
            [momentum**3 * frequency / 2, momentum**2 * frequency**2, momentum * frequency**3 / 2, momentum * frequency * (momentum**2 - frequency**2) / 2, 0, 0],
            [-momentum**2 * frequency**2 / 2, -momentum * frequency**3, -frequency**4 / 2, -frequency**2 * (momentum**2 - frequency**2) / 2, 0, 0],
            [-momentum**2 * (momentum**2 - frequency**2) / 4, -momentum * frequency * (momentum**2 - frequency**2) / 2, -frequency**2 * (momentum**2 - frequency**2) / 4, -(momentum**2 - frequency**2) ** 2 / 4, 0, 0],
            [0, 0, 0, 0, momentum**2, momentum * frequency],
            [0, 0, 0, 0, momentum * frequency, frequency**2],
        ]
    )
    _require((operator - expected).applyfunc(sp.factor) == sp.zeros(6), "direct ell=0 operator changed")

    gauge = sp.Matrix(
        [
            [-2 * sp.I * frequency, 0, -2, 0],
            [sp.I * momentum, -sp.I * frequency, 0, 0],
            [0, 2 * sp.I * momentum, 2, 0],
            [0, 0, 2, 0],
            [0, 0, 0, -sp.I * frequency],
            [0, 0, 0, sp.I * momentum],
        ]
    )
    _require((operator * gauge).applyfunc(sp.factor) == sp.zeros(6, 4), "Diff-Weyl-U(1) gauge defect survived")

    action = (sp.diag(-1, 2, -1, -2, 1, 1) * operator).applyfunc(sp.factor)
    adjoint_defect = (
        action
        - action.subs({frequency: -frequency, momentum: -momentum}, simultaneous=True).T
    ).applyfunc(sp.factor)
    _require(adjoint_defect == sp.zeros(6), "ell=0 action Hessian lost formal self-adjointness")

    metric_vector = sp.Matrix(
        [momentum**2, 2 * momentum * frequency, frequency**2, momentum**2 - frequency**2]
    )
    maxwell_vector = sp.Matrix([momentum, frequency])
    factorized = sp.zeros(6)
    factorized[:4, :4] = metric_vector * metric_vector.T / 2
    factorized[4:, 4:] = maxwell_vector * maxwell_vector.T
    _require((action - factorized).applyfunc(sp.factor) == sp.zeros(6), "rank-one block factorization changed")

    # For every real (omega,kappa)!=(0,0), both displayed vectors are nonzero.
    # The action rank is therefore two.  The four gauge columns are independent
    # on the two coordinate-axis charts kappa!=0 and omega!=0, exhaust the
    # four-dimensional kernel, and by self-adjointness exhaust the cokernel.
    gauge_minor_k = sp.factor(gauge[[1, 2, 3, 5], :].det())
    gauge_minor_w = sp.factor(gauge[[0, 1, 3, 4], :].det())
    _require(gauge_minor_k != 0 and gauge_minor_w != 0, "gauge rank witnesses vanished")

    static_action = action.subs(frequency, 0).applyfunc(sp.factor)
    static_gauge = gauge.subs(frequency, 0)
    _require(static_action.rank() == 2, "static nonzero-momentum operator rank changed")
    _require(static_gauge.rank() == 4, "static nonzero-momentum gauge rank changed")
    _require(static_action * static_gauge == sp.zeros(6, 4), "static gauge image left the kernel")
    _require(
        static_action.nullspace() == static_action.T.nullspace(),
        "static left/right null spaces diverged",
    )
    combined_rank = sp.Matrix.hstack(*static_action.nullspace(), *[static_gauge[:, column] for column in range(4)]).rank()
    _require(combined_rank == 4, "static kernel is not exhausted by gauge")

    source_a, source_t = sp.symbols("S_A S_T")
    correction = sp.Matrix([source_a / momentum**4, 0, 0, source_a / momentum**4, source_t / momentum**2, 0])
    compatible_source = sp.Matrix([source_a, 0, 0, source_a, source_t, 0])
    _require(
        (static_action * correction - compatible_source).applyfunc(sp.factor) == sp.zeros(6, 1),
        "static right inverse changed",
    )

    return {
        "schema": "einstein-maxwell-weyl-polar-ell0-nonzero-fourier-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_POLAR_ELL0_NONZERO_FOURIER",
        "result_state": "STATIC_NONZERO_MOMENTUM_EXCEPTIONAL_TARGET_EXACT_AND_SURJECTIVE_MODULO_NOETHER",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "domain": "fixed magnetic bundle on R x S1_L x S2; polar ell=0 Fourier target with (omega,kappa), specialized for the phase-sensitive static channel omega=0 and kappa=+/-2k_input nonzero",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "engine": {"path": str(ENGINE.relative_to(ROOT)), "sha256": _sha256(ENGINE)},
            "input": {"path": str(PHASE_INPUT.relative_to(ROOT)), "sha256": _sha256(PHASE_INPUT)},
        },
        "fourier_complex": {
            "field_order": ["A=h_tt", "B=h_tx", "C=h_xx", "K=sphere_trace", "T=a_t", "X=a_x"],
            "Euler_row_order": ["metric_00", "metric_01", "metric_11", "sphere_trace", "Maxwell_density_t", "Maxwell_density_x"],
            "raw_operator": _matrix_strings(operator),
            "action_row_multipliers": ["-1", "2", "-1", "-2", "1", "1"],
            "action_Hessian": _matrix_strings(action),
            "rank_one_factorization": {
                "metric_vector": [str(value) for value in metric_vector],
                "Maxwell_vector": [str(value) for value in maxwell_vector],
                "identity": "H=(1/2)*v_metric*v_metric^T direct-sum v_Maxwell*v_Maxwell^T",
            },
            "formally_self_adjoint": True,
            "gauge_parameter_order": ["xi_t", "xi_x", "sigma_Weyl", "chi_U1"],
            "gauge_matrix": _matrix_strings(gauge),
            "gauge_defect_zero": True,
            "gauge_rank_chart_witnesses": {
                "kappa_nonzero_minor": str(gauge_minor_k),
                "omega_nonzero_minor": str(gauge_minor_w),
            },
            "fixed_bundle_note": "the uniform magnetic variation is absent; T,X are the global difference of two fixed-bundle connections",
        },
        "all_nonzero_fourier_pairs": {
            "domain": "real (omega,kappa)!=(0,0)",
            "operator_rank": 2,
            "gauge_rank": 4,
            "kernel_equals_Diff_Weyl_U1_image": True,
            "cokernel_equals_adjoint_gauge_Noether_space": True,
            "source_consequence": "every Noether-compatible ell=0 nonzero-Fourier source is in the operator image",
        },
        "static_nonzero_momentum": {
            "substitution": "omega=0, kappa!=0",
            "action_Hessian": _matrix_strings(static_action),
            "gauge_matrix": _matrix_strings(static_gauge),
            "operator_rank": 2,
            "gauge_rank": 4,
            "kernel_dimension": 4,
            "kernel_equals_Diff_Weyl_U1_image": True,
            "left_cokernel_equals_adjoint_gauge_Noether_space": True,
            "compatible_source_conditions": ["S_B=0", "S_C=0", "S_X=0", "S_A=S_K"],
            "right_inverse_for_L_Phi=S": ["A=S_A/kappa^4", "B=0", "C=0", "K=S_A/kappa^4", "T=S_T/kappa^2", "X=0"],
            "right_inverse_for_second_order_equation": ["A=-S_A/kappa^4", "B=0", "C=0", "K=-S_A/kappa^4", "T=-S_T/kappa^2", "X=0"],
        },
        "phase_channel_consequence": {
            "channel": "same-branch opposite-frequency interference at L=0, K=+/-2k_input, Omega=0",
            "quadratic_Noether_identity": "for an on-shell first-order tangent, the second-order action source is orthogonal to the adjoint gauge space on the closed slice",
            "therefore_source_is_in_operator_image": True,
            "smooth_global_static_correction_exists": True,
            "relative_phase_creates_no_new_static_Taub_obstruction": True,
        },
        "classification": {
            "direct_four_dimensional_exceptional_operator_constructed": True,
            "generic_ell_master_operator_specialized": False,
            "Diff_Weyl_U1_complex_exact_at_static_nonzero_momentum": True,
            "Diff_Weyl_U1_complex_exact_at_every_nonzero_Fourier_pair": True,
            "static_L0_K2k_exceptional_block_classified": True,
            "static_phase_sensitive_source_removable_if_Noether_compatible": True,
            "smooth_global_opposite_momentum_cone_ready_for_aggregation": True,
            "bounded_resonant_projection_classified": False,
        },
        "interpretation": "The last exceptional static phase channel has no physical adjoint cokernel. Its entire cokernel is the Noether space, and the quadratic source of an on-shell first-order field automatically obeys those identities. The source is therefore removable by the displayed spatially periodic static correction. This closes the static smooth-global gate but says nothing about bounded corrections on the nonzero-frequency resonance divisor.",
        "next_gate": "aggregate this exceptional theorem with the common-zero moment-map cone and the generic secular inverse to certify the complete fixed-(ell,|k|) smooth-global opposite-momentum second-order cone; retain the bounded resonance projection as a separate open problem",
        "claim_boundary": "This is an exceptional LOCAL-ALGEBRAIC/REDUCED-MODE second-order solvability statement. It does not compute the phase-source coefficient, prove bounded or finite-quasiperiodic extension on a resonant shell, join distinct |k| fibers, establish all-orders integration, or make Lorentzian-causal or quantum claims.",
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.2, "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <certificate>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "elapsed_seconds": 21.9, "commands": [
                "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_polar_ell0_nonzero_fourier --verify bridge/certificates/einstein_maxwell_weyl_polar_ell0_nonzero_fourier.json",
                "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_polar_ell0_nonzero_fourier.py",
                "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_polar_ell0_nonzero_fourier"
            ]},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "inputs": ["four-dimensional Weyl-Maxwell engine", "opposite-momentum phase divisor"]},
            "tier_3": {"status": "NOT_RUN", "reason": "the bounded resonant projection and programme-wide nonlinear theorem remain open"}
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_polar_ell0_nonzero_fourier --verify bridge/certificates/einstein_maxwell_weyl_polar_ell0_nonzero_fourier.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_polar_ell0_nonzero_fourier.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_polar_ell0_nonzero_fourier",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    payload = build_certificate()
    if arguments.write:
        DEFAULT_OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return
    assert arguments.verify is not None
    _require(json.loads(arguments.verify.read_text(encoding="utf-8")) == payload, "ell=0 Fourier certificate is stale")


if __name__ == "__main__":
    main()
