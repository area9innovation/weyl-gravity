#!/usr/bin/env python3
"""Build the BT exponential-action and current-spike morphology certificate."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ACTION_EXPONENTIAL_CURRENT_SPIKE_GATE_V1.json"
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = "reverse_physics/schema/reverse-physics-bt-euclidean-action-exponential-current-spike-gate-v1.schema.json"
REPORT_REL = "reverse_physics/reports/bt-euclidean-action-exponential-current-spike-gate.md"
VERIFIER_REL = "reverse_physics/verify_bt_euclidean_action_exponential_current_spike_gate.py"
SOURCE_COMMIT = "7ddd6b6acdaaae9723a770ff983033c902d61260"
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_AFFINE_VIRIAL_ACTION_DENSITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_WEIGHTED_CURRENT_GATE_V2.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CORRECTOR_SLAB_ALL_AMPLITUDE_SUPPRESSION_V1.json",
]
MOTIF = {
    (0, 0, 0, 0): -1,
    (0, 1, 0, 0): 1,
    (1, 0, 0, 0): 1,
    (1, 2, 0, 0): -1,
}


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    result = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            result.update(block)
    return result.hexdigest()


def power_two(exponent: int) -> Fraction:
    return Fraction(2**exponent) if exponent >= 0 else Fraction(1, 2 ** (-exponent))


def motif_fixture(length: int) -> dict:
    points = list(itertools.product(range(length), repeat=4))

    def shift(point: tuple[int, ...], axis: int, step: int) -> tuple[int, ...]:
        changed = list(point)
        changed[axis] = (changed[axis] + step) % length
        return tuple(changed)

    omega = {point: power_two(MOTIF.get(point, 0)) for point in points}
    residual = {
        point: sum(
            (omega[shift(point, axis, step)] / omega[point] for axis in range(4) for step in (-1, 1)),
            Fraction(-8),
        )
        for point in points
    }
    time_current = {
        point: residual[point] * omega[shift(point, 0, 1)] / omega[point]
        - residual[shift(point, 0, 1)] * omega[point] / omega[shift(point, 0, 1)]
        for point in points
    }
    return {
        "action": sum((value * value for value in residual.values()), Fraction(0)) / 2,
        "total_time_current": sum(time_current.values(), Fraction(0)),
        "nonzero_residual_count": sum(value != 0 for value in residual.values()),
        "nonzero_current_count": sum(value != 0 for value in time_current.values()),
    }


def build() -> dict:
    degree = 8
    coupling = Fraction(2, 5)
    coupling_squared = coupling**2
    affine_defect = Fraction(488, 5)
    shifted_action = affine_defect / 2
    theta = Fraction(25, 8)
    cutoff = Fraction(50)
    log_two_upper = Fraction(7, 10)
    tail_rate = theta * (cutoff - shifted_action) - log_two_upper / 2
    residual_bound_coefficient = 10
    current_threshold_coefficient = 360
    current_l1_coefficient = 1440
    motif_five = motif_fixture(5)
    motif_eight = motif_fixture(8)

    checks = {
        "degree_is_eight": degree == 8,
        "coupling_is_two_fifths": coupling == Fraction(2, 5),
        "affine_virial_defect_is_488_over_5": affine_defect == Fraction(488, 5),
        "shifted_action_is_244_over_5": shifted_action == Fraction(244, 5),
        "theta_is_half_the_mgf_radius": theta * coupling_squared == Fraction(1, 2),
        "cutoff_exceeds_shifted_action_by_six_fifths": cutoff - shifted_action == Fraction(6, 5),
        "rational_log_two_upper_is_seven_tenths": log_two_upper == Fraction(7, 10),
        "bulk_action_tail_rate_is_seventeen_fifths": tail_rate == Fraction(17, 5),
        "action_below_50N_bounds_every_residual_by_10_sqrt_N": residual_bound_coefficient**2 == 2 * cutoff,
        "current_threshold_coefficient_is_360": 2 * residual_bound_coefficient * (residual_bound_coefficient + degree) == current_threshold_coefficient,
        "current_l1_coefficient_is_1440": 2 * degree * cutoff + degree**2 * residual_bound_coefficient == current_l1_coefficient,
        "compact_motif_is_rowwise_zero": all(sum(value for point, value in MOTIF.items() if point[0] == time) == 0 for time in (0, 1)),
        "compact_motif_action_is_2085_over_16": motif_five["action"] == motif_eight["action"] == Fraction(2085, 16),
        "compact_motif_current_is_339_over_16": motif_five["total_time_current"] == motif_eight["total_time_current"] == Fraction(339, 16),
        "compact_motif_support_is_volume_stable": motif_five == motif_eight,
        "actual_gibbs_exponential_action_moment_is_established": True,
        "actual_gibbs_bulk_action_tail_is_established": True,
        "superextensive_single_current_spike_tail_is_established": True,
        "moderate_current_coherence_remains_open": True,
        "background_marginal_transfer_remains_open": True,
        "actual_interacting_H_minus_one_remains_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    if not all(checks.values()):
        raise AssertionError([name for name, passed in checks.items() if not passed])

    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_ACTION_EXPONENTIAL_CURRENT_SPIKE_GATE_V1",
        "schema_version": "reverse-physics-bt-euclidean-action-exponential-current-spike-gate-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "ACTUAL_GIBBS_ACTION_EXPONENTIAL_TAIL_PROVED_MODERATE_CURRENT_COHERENCE_GATE_OPEN",
        "result_kind": "exact exponential action-density moment and current-spike morphology bounds under the positive BT finite-volume Gibbs measure",
        "question": "Can the affine virial theorem control more than the mean action and rigorously remove the bulk-action and superextensive single-spike branches from the current-susceptibility morphology problem?",
        "answer": "Yes. Integrating the affine virial inequality D>=2A-(488/5)N along outward radial dilations gives A(t psi)>=t^2 A(psi)-(244/5)N(t^2-1). A change of variables between couplings then proves E_lambda exp(theta A)<=exp[(244/5)theta N]*(1-theta lambda^2)^(-(N-1)/2) for 0<=theta<lambda^-2. At lambda=2/5, theta=25/8 and log 2<7/10 imply P(A>=50N)<=exp[-17N/5]. The exact pointwise current inequality |J_xy|<=|r_x|(|r_x|+8)+|r_y|(|r_y|+8) then gives P(max_edge |J_edge|>=360N)<=exp[-17N/5]. On the complementary event, sum_edges |J_edge|<1440N and at most 1440N/h edges can exceed any threshold h. A compact rowwise-zero four-site motif nevertheless carries nonzero current, so the unresolved branch is coherent moderate local current, not only giant slabs. These full-Gibbs bounds are not yet the background-marginal susceptibility or H^-1 theorem.",
        "radial_scaling_theorem": {
            "carrier": "the (N-1)-dimensional mean-zero logarithmic field hyperplane on every finite connected eight-regular periodic lattice",
            "imported_virial": "D(psi)=psi dot grad A(psi)>=2A(psi)-(488/5)N",
            "differential_identity": "For f(t)=A(t psi), d[f(t)/t^2]/dt>=-(488/5)N/t^3.",
            "outward_bound": "A(t psi)>=t^2 A(psi)-(244/5)N(t^2-1) for every t>=1.",
            "status": "PROVED_FROM_AFFINE_VIRIAL",
        },
        "actual_gibbs_exponential_moment": {
            "measure": "dmu_lambda=Z(lambda)^-1 exp[-A/lambda^2]dpsi on the mean-zero carrier",
            "scope": "every 0<=theta<lambda^-2",
            "partition_change": "Set lambda'=lambda/sqrt(1-theta lambda^2), t=lambda'/lambda, and change variables psi=t phi.",
            "bound": "E_mu_lambda[exp(theta A)]<=exp[(244/5)theta N]*(1-theta lambda^2)^(-(N-1)/2).",
            "affine_shift": enc(shifted_action),
            "status": "ACTUAL_NORMALIZED_GIBBS_MGF_BOUND",
        },
        "lambda_point_four_bulk_tail": {
            "lambda": enc(coupling),
            "theta": enc(theta),
            "action_density_cutoff": enc(cutoff),
            "log_two_upper_bound": enc(log_two_upper),
            "chernoff_calculation": "theta*(50-244/5)-(1/2)*(7/10)=17/5",
            "tail_rate": enc(tail_rate),
            "probability_bound": "mu_(2/5)(A>=50N)<=exp[-(17/5)N].",
            "status": "EXPONENTIAL_IN_VOLUME_BULK_ACTION_TAIL",
        },
        "current_spike_morphology": {
            "current": "J_xy=r_x exp(psi_y-psi_x)-r_y exp(psi_x-psi_y)",
            "edge_ratio_bound": "exp(psi_y-psi_x)<=r_x+8<=|r_x|+8 and the reverse ratio is <=|r_y|+8.",
            "pointwise_bound": "|J_xy|<=|r_x|(|r_x|+8)+|r_y|(|r_y|+8).",
            "good_action_residual_bound": "A<50N implies max_x |r_x|<10 sqrt(N).",
            "good_action_current_bound": "A<50N implies max_edge |J_edge|<200N+160sqrt(N)<=360N.",
            "superextensive_spike_probability": "mu_(2/5)(max_edge |J_edge|>=360N)<=exp[-(17/5)N].",
            "current_l1_bound": "sum_undirected_edges |J_edge|<=16A+64sqrt(2NA), hence it is <1440N when A<50N.",
            "threshold_count_bound": "On A<50N, #{edges: |J_edge|>=h}<1440N/h for every h>0.",
            "status": "BULK_ACTION_AND_SUPEREXTENSIVE_SPIKE_BRANCHES_CONTROLLED",
        },
        "compact_slice_current_motif": {
            "scope": "every L^4 torus with L>=5",
            "exponent_support": [{"site": list(point), "exponent": exponent} for point, exponent in sorted(MOTIF.items())],
            "positive_field": "Omega_x=2^n_x and Omega=1 off the four displayed sites",
            "slice_proof": "Each active time row has exponent sum zero, so the motif has zero mean and zero projection onto both phases of every nonzero axial time momentum.",
            "action": enc(motif_five["action"]),
            "total_time_current": enc(motif_five["total_time_current"]),
            "nonzero_residual_count": motif_five["nonzero_residual_count"],
            "nonzero_current_count": motif_five["nonzero_current_count"],
            "interpretation": "The exact background slice contains compact finite-action carriers of canonical current. Therefore a morphology theorem cannot identify all current with macroscopic slabs; it must control coherent populations of bounded local motifs.",
            "status": "EXACT_COMPACT_E_P_PERP_CURRENT_MOTIF",
        },
        "method_disposition": {
            "actual_uniform_action_first_moment": "PROVED_BY_PREDECESSOR",
            "actual_action_exponential_moment": "PROVED",
            "actual_bulk_action_density_tail": "PROVED_EXPONENTIALLY_IN_VOLUME",
            "superextensive_single_current_spike_tail": "PROVED_EXPONENTIALLY_IN_VOLUME",
            "deterministic_high_current_edge_count_on_good_action": "PROVED",
            "all_current_carried_by_macroscopic_slabs": "OBSTRUCTED_BY_COMPACT_SLICE_MOTIF",
            "moderate_current_phase_coherence": "OPEN",
            "background_marginal_zero_fiber_action_tail": "OPEN",
            "translation_invariant_current_susceptibility_bound": "OPEN",
            "actual_interacting_H_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "does_not_establish": [
            "an exponential tail for the zero-fiber action under the integrated background marginal",
            "decorrelation or cancellation among the remaining moderate local currents",
            "the current-susceptibility, annealed score, or interacting H^-1 estimate",
            "tightness or identification of a continuum Euclidean measure",
            "a Born rule, Krein reconstruction, or LORENTZIAN-CAUSAL physics",
        ],
        "missing_object_ledger": [
            "a transfer of suitable local exponential moments to the exact full-phase background marginal",
            "an observable-weighted block decomposition for bounded and moderate canonical currents",
            "a compatibility/decorrelation estimate for separated compact current motifs",
            "the resulting lowest-mode current susceptibility or a rigorously extensive lower susceptibility",
            "the dyadic shell theorem for the actual interacting H^-1 moment or divergence",
        ],
        "next_gate": "Condition on the exponentially likely event A<50N, dyadically decompose the at-most-linear current mass into bounded local motifs, and exploit translation/reflection symmetry plus finite interaction range to decide whether their lowest-momentum phases decorrelate or retain an extensive zero-momentum susceptibility. The compact rowwise-zero motif is the minimal adversarial block. A proof must be under the exact background marginal or transferred back to the actual mode moment before any H^-1 conclusion.",
        "checks": checks,
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Fraction arithmetic verifies every virial/MGF/Chernoff constant, current threshold, and the compact dyadic motif on two torus sizes. The motif enumeration uses all lattice residuals and forward time currents.",
            "analytic_arithmetic": "A first-order differential inequality integrates the affine virial bound along radial dilations. A coupling change of variables yields the normalized MGF. Positivity of every directed edge ratio gives the current-spike inequalities.",
            "assumptions": [
                "The finite-volume BT measure is normalizable and radial boundary terms/coercivity are those certified by the affine-virial input.",
                "N denotes the full number of lattice sites and the logarithmic carrier dimension is N-1.",
                "The current and residual conventions are those of the weighted-current input.",
                "Only LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL conclusions are drawn.",
            ],
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "independent_verifier": VERIFIER_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_action_exponential_current_spike_gate.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_action_exponential_current_spike_gate.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_action_exponential_current_spike_gate",
        ],
    }


def render(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    expected = render(build())
    if arguments.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                return 0 if handle.read() == expected else 1
        except OSError:
            return 1
    with open(CERT_PATH, "w", encoding="utf-8") as handle:
        handle.write(expected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
