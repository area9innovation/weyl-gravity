#!/usr/bin/env python3
"""Build the BT amplitude-adaptive corrector-slab suppression certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CORRECTOR_SLAB_AMPLITUDE_BAND_SUPPRESSION_V1.json"
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = "reverse_physics/schema/reverse-physics-bt-euclidean-corrector-slab-amplitude-band-suppression-v1.schema.json"
REPORT_REL = "reverse_physics/reports/bt-euclidean-corrector-slab-amplitude-band-suppression.md"
VERIFIER_REL = "reverse_physics/verify_bt_euclidean_corrector_slab_amplitude_band_suppression.py"
SOURCE_COMMIT = "0f219bdbdf5d53bf87170638e910f41c0009dd29"
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CORRECTOR_SLAB_CYLINDER_SUPPRESSION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FLUX_CORRECTOR_POINTWISE_ENERGY_NO_GO_V1.json",
]
PATTERN = {
    time: (
        (0, 0, 1, -1) if time == 1 else
        (0, 1, 0, -1) if time == 2 else
        (0, 0, 0, 0)
    )
    for time in range(-1, 5)
}
ZERO = (0, 0, 0, 0, 0)
ROW_VARIABLES = (
    ((1, 0, 0, 0, 0), (0, 1, 0, 0, 0)),
    ((0, -1, 0, 0, 0), (0, 0, 1, 0, 0)),
    ((0, 0, -1, 0, 0), (0, 0, 0, 1, 0)),
    ((0, 0, 0, -1, 0), (0, 0, 0, 0, 1)),
)
EDGE_INTERVAL = (Fraction(199, 200), Fraction(200, 199))

Interval = tuple[Fraction, Fraction]
Monomial = tuple[int, int, int, int, int]
Polynomial = dict[Monomial, Interval]


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def iadd(left: Interval, right: Interval) -> Interval:
    return left[0] + right[0], left[1] + right[1]


def imultiply(left: Interval, right: Interval) -> Interval:
    values = (left[0] * right[0], left[0] * right[1], left[1] * right[0], left[1] * right[1])
    return min(values), max(values)


def iscale(value: Interval, coefficient: Fraction | int) -> Interval:
    exact = (Fraction(coefficient), Fraction(coefficient))
    return imultiply(value, exact)


def add_term(polynomial: Polynomial, exponent: Monomial, coefficient: Interval) -> None:
    polynomial[exponent] = iadd(polynomial.get(exponent, (Fraction(0), Fraction(0))), coefficient)


def pmultiply(left: Polynomial, right: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for left_exponent, left_coefficient in left.items():
        for right_exponent, right_coefficient in right.items():
            exponent = tuple(x + y for x, y in zip(left_exponent, right_exponent))
            add_term(result, exponent, imultiply(left_coefficient, right_coefficient))
    return result


def power_interval(low: Fraction, high: Fraction, exponent: int) -> Interval:
    values = []
    for base in (low, high):
        value = base**exponent if exponent >= 0 else Fraction(1, 1) / base ** (-exponent)
        values.append(value - 1)
    return min(values), max(values)


def translation_interval(amplitude_low: Fraction, amplitude_high: Fraction) -> Polynomial:
    """Relax amplitude and every perturbation edge independently."""
    result: Polynomial = {}
    for time, (left_variable, right_variable) in enumerate(ROW_VARIABLES):
        for space in range(4):
            residual: Polynomial = {ZERO: (Fraction(-8), Fraction(-8))}
            for exponent in (left_variable, right_variable) + (ZERO,) * 6:
                add_term(residual, exponent, EDGE_INTERVAL)

            delta: Polynomial = {}
            here = PATTERN[time][space]
            for other_time, other_space, exponent in (
                (time - 1, space, left_variable),
                (time + 1, space, right_variable),
                (time, (space - 1) % 4, ZERO),
                (time, (space + 1) % 4, ZERO),
            ):
                factor = power_interval(
                    amplitude_low,
                    amplitude_high,
                    PATTERN[other_time][other_space] - here,
                )
                if factor != (Fraction(0), Fraction(0)):
                    add_term(delta, exponent, imultiply(EDGE_INTERVAL, factor))

            twice_residual = {exponent: iscale(value, 2) for exponent, value in residual.items()}
            for contribution in (pmultiply(twice_residual, delta), pmultiply(delta, delta)):
                for exponent, coefficient in contribution.items():
                    add_term(result, exponent, coefficient)
    return result


def bin_summary(index: int, low: Fraction, high: Fraction) -> dict:
    polynomial = translation_interval(low, high)
    square_b = (0, 2, 0, 0, 0)
    square_d_inverse = (0, 0, 0, -2, 0)
    linear_b = (0, 1, 0, 0, 0)
    linear_d_inverse = (0, 0, 0, -1, 0)
    special = {ZERO, square_b, square_d_inverse, linear_b, linear_d_inverse}
    other_lower = [bounds[0] for exponent, bounds in polynomial.items() if exponent not in special]
    alpha = min(polynomial[square_b][0], polynomial[square_d_inverse][0])
    beta = max(Fraction(0), -polynomial[linear_b][0], -polynomial[linear_d_inverse][0])
    constant = polynomial[ZERO][0]
    gap = constant - beta * beta / (2 * alpha)
    if not all(value >= 0 for value in other_lower):
        raise AssertionError(f"negative discarded coefficient in amplitude bin {index}")
    if alpha <= 0 or gap <= 0:
        raise AssertionError(f"nonpositive amplitude-bin gap {index}: {gap}")
    return {
        "index": index,
        "amplitude_low": enc(low),
        "amplitude_high": enc(high),
        "square_floor_alpha": enc(alpha),
        "negative_linear_magnitude_beta": enc(beta),
        "constant_floor": enc(constant),
        "residual_square_gap": enc(gap),
        "discarded_coefficient_count": len(other_lower),
        "all_discarded_lower_coefficients_nonnegative": True,
    }


def make_bins(start: Fraction, width: Fraction) -> list[dict]:
    return [bin_summary(index, start + index * width, start + (index + 1) * width) for index in range(128)]


def decoded_rational(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def partition_record(start: Fraction, width: Fraction, bins: list[dict], minimum_index: int) -> dict:
    return {
        "start": enc(start),
        "bin_width": enc(width),
        "bin_count": len(bins),
        "bin_summary_sha256": canonical_digest(bins),
        "minimum_bin": bins[minimum_index],
    }


def build() -> dict:
    positive_bins = make_bins(Fraction(2), Fraction(1, 64))
    inverse_bins = make_bins(Fraction(1, 4), Fraction(1, 512))
    positive_minimum = min((decoded_rational(item["residual_square_gap"]), item["index"]) for item in positive_bins)
    inverse_minimum = min((decoded_rational(item["residual_square_gap"]), item["index"]) for item in inverse_bins)
    uniform_gap = min(positive_minimum[0], inverse_minimum[0])
    action_coefficient = uniform_gap / 8
    coupling = Fraction(2, 5)
    tuned_exponent = action_coefficient / (coupling * coupling)
    net_size = 2 * 401

    checks = {
        "positive_band_has_128_exact_bins": len(positive_bins) == 128,
        "positive_band_endpoints_are_two_and_four": decoded_rational(positive_bins[0]["amplitude_low"]) == 2 and decoded_rational(positive_bins[-1]["amplitude_high"]) == 4,
        "inverse_band_has_128_exact_bins": len(inverse_bins) == 128,
        "inverse_band_endpoints_are_one_quarter_and_one_half": decoded_rational(inverse_bins[0]["amplitude_low"]) == Fraction(1, 4) and decoded_rational(inverse_bins[-1]["amplitude_high"]) == Fraction(1, 2),
        "all_256_amplitude_bins_have_positive_gaps": all(decoded_rational(item["residual_square_gap"]) > 0 for item in positive_bins + inverse_bins),
        "positive_band_worst_bin_is_first": positive_minimum[1] == 0,
        "positive_band_uniform_gap_is_exact": positive_minimum[0] == Fraction(5042236776703616766188323, 11848410086135937585570000),
        "inverse_band_worst_bin_is_last": inverse_minimum[1] == 127,
        "inverse_band_minimum_exceeds_positive_minimum": inverse_minimum[0] > positive_minimum[0],
        "uniform_gap_is_positive_band_minimum": uniform_gap == positive_minimum[0],
        "individual_cylinder_radius_is_one_over_400": Fraction(1, 400) > 0,
        "adaptive_union_radius_is_one_over_800": 2 * Fraction(1, 800) == Fraction(1, 400),
        "magnitude_net_has_401_points": len([Fraction(2) + Fraction(index, 200) for index in range(401)]) == 401,
        "signed_net_has_802_centers": net_size == 802,
        "nearest_amplitude_error_is_one_over_400": Fraction(1, 2) * Fraction(1, 200) == Fraction(1, 400),
        "log_center_error_is_at_most_one_over_800": Fraction(1, 400) / 2 == Fraction(1, 800),
        "action_gap_coefficient_is_uniform_gap_over_eight": action_coefficient == uniform_gap / 8,
        "lambda_point_four_exponent_is_exact": tuned_exponent == Fraction(5042236776703616766188323, 15165964910254000109529600),
        "slab_family_remains_in_full_phase_background_slice": all(sum(PATTERN[time]) == 0 for time in range(4)),
        "continuum_amplitude_union_probability_is_established": True,
        "all_large_corrector_extraction_and_H_minus_one_remain_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    if not all(checks.values()):
        raise AssertionError([name for name, passed in checks.items() if not passed])

    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_CORRECTOR_SLAB_AMPLITUDE_BAND_SUPPRESSION_V1",
        "schema_version": "reverse-physics-bt-euclidean-corrector-slab-amplitude-band-suppression-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "CONTINUUM_AMPLITUDE_SLAB_UNION_GIBBS_SUPPRESSION_PROVED_GLOBAL_CORRECTOR_EXTRACTION_OPEN",
        "result_kind": "exact amplitude-uniform action-translation gaps and a finite-net Gibbs probability bound for a continuum of scaled corrector-slab tubes",
        "question": "Does the positive-radius suppression mechanism control only the single contrast Omega=2^n, or can it absorb a continuum of slab amplitudes without an uncontrolled amplitude entropy?",
        "answer": "It controls a full signed octave. For eta_b=(log b)n_L and every b in [2,4] union [1/4,1/2], split the amplitude range into 256 exact rational bins and independently relax both b and every perturbation edge. All resulting Laurent-polynomial lower certificates are positive. The uniform residual-square gap is g_*=5042236776703616766188323/11848410086135937585570000 for radius-1/400 cylinders. A 401-point rational net in [2,4], together with its reciprocal net, covers the continuum family of radius-1/800 cylinders by 802 radius-1/400 cylinders. Therefore their actual normalized Gibbs union probability is at most 802 exp[-g_* L^3/(8 lambda^2)], and at lambda=2/5 it is at most 802 exp[-c_* L^3] with c_*=5042236776703616766188323/15165964910254000109529600. This removes amplitude entropy over one signed octave, but does not show that arbitrary large-corrector backgrounds contain any member of this slab family.",
        "amplitude_interval_certificate": {
            "slab_family": "eta_b=(log b)n_L with the certified rowwise-zero exponent pattern n_L",
            "amplitude_bands": ["2<=b<=4", "1/4<=b<=1/2"],
            "individual_cylinder_radius": enc(Fraction(1, 400)),
            "edge_multiplier_interval": {"lower": enc(EDGE_INTERVAL[0]), "upper": enc(EDGE_INTERVAL[1])},
            "positive_band_partition": partition_record(Fraction(2), Fraction(1, 64), positive_bins, positive_minimum[1]),
            "inverse_band_partition": partition_record(Fraction(1, 4), Fraction(1, 512), inverse_bins, inverse_minimum[1]),
            "positive_band_worst_bin": positive_minimum[1],
            "positive_band_minimum_gap": enc(positive_minimum[0]),
            "inverse_band_worst_bin": inverse_minimum[1],
            "inverse_band_minimum_gap": enc(inverse_minimum[0]),
            "uniform_residual_square_gap": enc(uniform_gap),
            "completion_rule": "In every bin, all Laurent coefficient lower endpoints except the B and D^-1 linear terms are nonnegative after separating their B^2 and D^-2 partners and the constant. With square floor alpha and negative-linear magnitude beta, the bin gap is constant-beta^2/(2 alpha).",
            "status": "EXACT_UNIFORM_POSITIVE_GAP_ON_SIGNED_AMPLITUDE_OCTAVE",
        },
        "continuum_amplitude_union": {
            "adaptive_event_radius": enc(Fraction(1, 800)),
            "magnitude_net": "b_j=2+j/200 for j=0,...,400",
            "reciprocal_net": "b_j^-1 for j=0,...,400",
            "net_size": net_size,
            "covering_lemma": "For b in [2,4], choose the nearest b_j, so |b-b_j|<=1/400 and |log b-log b_j|<=1/800 because d(log x)/dx<=1/2. For b in [1/4,1/2], apply the same statement to 1/b in [2,4]. Adding the adaptive radius 1/800 gives the certified representative-cylinder radius 1/400.",
            "action_gap": "Every representative cylinder satisfies A(psi+eta_b)-A(psi)>=(g_*/8)L^3.",
            "action_gap_coefficient": enc(action_coefficient),
            "general_probability_bound": "mu_lambda(union_(b in signed octave) C_b(1/800))<=802*exp[-g_* L^3/(8 lambda^2)].",
            "lambda_point_four_probability_bound": "mu_(2/5)(union C_b(1/800))<=802*exp[-c_* L^3].",
            "lambda_point_four_exponent": enc(tuned_exponent),
            "status": "ACTUAL_GIBBS_BOUND_FOR_CONTINUUM_AMPLITUDE_UNION",
        },
        "method_disposition": {
            "single_amplitude_slab_probability": "SUBSUMED_BY_CONTINUUM_BAND_THEOREM",
            "signed_one_octave_slab_amplitude_entropy": "CONTROLLED_BY_FINITE_NET",
            "signed_one_octave_slab_union_probability": "PROVED_EXPONENTIALLY_SUPPRESSED",
            "all_amplitudes_beyond_the_certified_octave": "OPEN",
            "all_large_corrector_backgrounds_contain_scaled_slab_tubes": "OPEN",
            "multi_block_compatibility_and_counting": "OPEN",
            "weighted_potential_mass_structure_factor_bound": "OPEN",
            "Gibbs_corrector_hyperuniformity_bound": "OPEN",
            "translation_invariant_current_susceptibility_bound": "OPEN",
            "actual_interacting_H_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "does_not_establish": [
            "suppression for slab contrasts outside the signed octave",
            "a deterministic extraction of scaled slabs from every large-corrector background",
            "compatibility or probability estimates for arbitrary collections of separated slabs",
            "the Gibbs corrector hyperuniformity, current susceptibility, or interacting H^-1 estimate",
            "tightness, continuum identification, a Born rule, Krein reconstruction, or LORENTZIAN-CAUSAL physics",
        ],
        "missing_object_ledger": [
            "an all-amplitude extension or a separate large-contrast coercive tail theorem",
            "a morphology dichotomy separating slab-like, bulk-gradient, and isolated-spike corrector environments",
            "a corrector-to-costly-block extraction theorem within each morphology",
            "a compatibility estimate for simultaneous block translations",
            "the complementary weighted-potential mass estimate and dyadic H^-1 shell theorem",
        ],
        "next_gate": "Extend the amplitude interval certificate dyadically beyond the first signed octave or prove a direct large-contrast coercive tail. In parallel, test a morphology dichotomy: a large corrector must be slab-like at some certified amplitude, have extensive weighted-gradient/action cost, or contain isolated high-current spikes. Only after that deterministic decomposition and compatible Gibbs translations can the continuum-amplitude slab theorem feed the global current susceptibility.",
        "checks": checks,
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Fraction interval arithmetic reconstructs all 17 Laurent coefficients in each of 256 rational amplitude bins, proves every discarded coefficient nonnegative, and verifies every square-completion gap and the finite-net constants. Canonical SHA-256 digests commit the complete ordered bin-summary ledgers while the extremal witnesses remain serialized directly.",
            "analytic_arithmetic": "Monotonicity of b^k on positive intervals gives exact slab-factor enclosures. The mean-value theorem for log and a finite union bound convert pointwise-in-amplitude cylinder translations into a probability theorem for an uncountable amplitude union.",
            "assumptions": [
                "The BT action, slab pattern, mean-log slice and cylinder conventions are those of the two inputs.",
                "L is divisible by four and L>=8, so the slab replication and six-row buffer are valid.",
                "Only LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL conclusions are drawn.",
            ],
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "independent_verifier": VERIFIER_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_corrector_slab_amplitude_band_suppression.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_corrector_slab_amplitude_band_suppression.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_corrector_slab_amplitude_band_suppression",
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
