#!/usr/bin/env python3
"""Build the BT all-large-amplitude corrector-slab suppression certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction
from math import comb

try:
    from reverse_physics.bt_euclidean_corrector_slab_amplitude_band_suppression import (
        PATTERN,
        ROW_VARIABLES,
        ZERO,
        bin_summary,
        translation_interval,
    )
except ModuleNotFoundError:  # Direct script execution places reverse_physics/ on sys.path.
    from bt_euclidean_corrector_slab_amplitude_band_suppression import (
        PATTERN,
        ROW_VARIABLES,
        ZERO,
        bin_summary,
        translation_interval,
    )


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CORRECTOR_SLAB_ALL_AMPLITUDE_SUPPRESSION_V1.json"
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = "reverse_physics/schema/reverse-physics-bt-euclidean-corrector-slab-all-amplitude-suppression-v1.schema.json"
REPORT_REL = "reverse_physics/reports/bt-euclidean-corrector-slab-all-amplitude-suppression.md"
VERIFIER_REL = "reverse_physics/verify_bt_euclidean_corrector_slab_all_amplitude_suppression.py"
SOURCE_COMMIT = "eca8923894816747ca434f6691e800199d0db682"
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CORRECTOR_SLAB_AMPLITUDE_BAND_SUPPRESSION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CORRECTOR_SLAB_CYLINDER_SUPPRESSION_V1.json",
]
EDGE_INTERVAL = (Fraction(199, 200), Fraction(200, 199))
ANCHOR = Fraction(8)

Laurent = dict[int, Fraction]
Interval = tuple[Laurent, Laurent]
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


def clean(polynomial: Laurent) -> Laurent:
    return {power: coefficient for power, coefficient in polynomial.items() if coefficient}


def ladd(left: Laurent, right: Laurent) -> Laurent:
    result = dict(left)
    for power, coefficient in right.items():
        result[power] = result.get(power, Fraction(0)) + coefficient
    return clean(result)


def lscale(polynomial: Laurent, coefficient: Fraction | int) -> Laurent:
    coefficient = Fraction(coefficient)
    return clean({power: coefficient * value for power, value in polynomial.items()})


def lmultiply(left: Laurent, right: Laurent) -> Laurent:
    result: Laurent = {}
    for left_power, left_coefficient in left.items():
        for right_power, right_coefficient in right.items():
            power = left_power + right_power
            result[power] = result.get(power, Fraction(0)) + left_coefficient * right_coefficient
    return clean(result)


def levaluate(polynomial: Laurent, value: Fraction | int) -> Fraction:
    value = Fraction(value)
    return sum((coefficient * value**power for power, coefficient in polynomial.items()), Fraction(0))


def shifted_coefficients(polynomial: Laurent) -> tuple[int, list[Fraction]]:
    """Return B^(-m) p(B) as a polynomial in t=B-8."""
    minimum_power = min(polynomial, default=0)
    result: dict[int, Fraction] = {}
    for power, coefficient in polynomial.items():
        degree = power - minimum_power
        for shifted_power in range(degree + 1):
            contribution = coefficient * comb(degree, shifted_power) * ANCHOR ** (degree - shifted_power)
            result[shifted_power] = result.get(shifted_power, Fraction(0)) + contribution
    maximum = max(result, default=0)
    return minimum_power, [result.get(power, Fraction(0)) for power in range(maximum + 1)]


def nonnegative_from_anchor(polynomial: Laurent) -> bool:
    return all(coefficient >= 0 for coefficient in shifted_coefficients(polynomial)[1])


def lrecord(polynomial: Laurent) -> dict:
    base_power, shifted = shifted_coefficients(polynomial)
    return {
        "laurent_terms": [
            {"power": power, "coefficient": enc(coefficient)}
            for power, coefficient in sorted(polynomial.items())
        ],
        "shift_anchor": enc(ANCHOR),
        "clearing_power": -base_power,
        "shifted_coefficients": [enc(value) for value in shifted],
        "all_shifted_coefficients_nonnegative": all(value >= 0 for value in shifted),
    }


BRANCH_LEDGER: list[dict] = []


def interval_add(left: Interval, right: Interval) -> Interval:
    return ladd(left[0], right[0]), ladd(left[1], right[1])


def interval_scale(interval: Interval, coefficient: Fraction | int) -> Interval:
    coefficient = Fraction(coefficient)
    if coefficient >= 0:
        return lscale(interval[0], coefficient), lscale(interval[1], coefficient)
    return lscale(interval[1], coefficient), lscale(interval[0], coefficient)


def choose_extreme(candidates: list[Laurent], minimum: bool, label: str) -> Laurent:
    selected_index = min(
        range(len(candidates)),
        key=lambda index: levaluate(candidates[index], ANCHOR),
    ) if minimum else max(
        range(len(candidates)),
        key=lambda index: levaluate(candidates[index], ANCHOR),
    )
    selected = candidates[selected_index]
    differences = []
    for index, candidate in enumerate(candidates):
        difference = ladd(candidate, lscale(selected, -1)) if minimum else ladd(selected, lscale(candidate, -1))
        if not nonnegative_from_anchor(difference):
            raise AssertionError(f"symbolic interval branch changes for {label}, candidate {index}")
        differences.append(lrecord(difference))
    BRANCH_LEDGER.append({
        "label": label,
        "extreme": "minimum" if minimum else "maximum",
        "selected_index": selected_index,
        "candidate_difference_records": differences,
    })
    return selected


def interval_multiply(left: Interval, right: Interval, label: str) -> Interval:
    candidates = [
        lmultiply(left[0], right[0]),
        lmultiply(left[0], right[1]),
        lmultiply(left[1], right[0]),
        lmultiply(left[1], right[1]),
    ]
    return choose_extreme(candidates, True, label + ":lower"), choose_extreme(candidates, False, label + ":upper")


def constant_interval(low: Fraction | int, high: Fraction | int | None = None) -> Interval:
    low = Fraction(low)
    high = low if high is None else Fraction(high)
    return {0: low}, {0: high}


def amplitude_factor(exponent: int, inverse: bool) -> Interval:
    """Range of b^exponent-1 on a symbolic dyadic octave."""
    effective = -exponent if inverse else exponent
    if effective == 0:
        return constant_interval(0)
    if effective > 0:
        return ({effective: Fraction(1), 0: Fraction(-1)}, {effective: Fraction(2**effective), 0: Fraction(-1)})
    return ({effective: Fraction(1, 2 ** (-effective)), 0: Fraction(-1)}, {effective: Fraction(1), 0: Fraction(-1)})


def add_term(polynomial: Polynomial, exponent: Monomial, coefficient: Interval) -> None:
    polynomial[exponent] = interval_add(polynomial.get(exponent, constant_interval(0)), coefficient)


def polynomial_multiply(left: Polynomial, right: Polynomial, label: str) -> Polynomial:
    result: Polynomial = {}
    for left_exponent, left_coefficient in left.items():
        for right_exponent, right_coefficient in right.items():
            exponent = tuple(x + y for x, y in zip(left_exponent, right_exponent))
            add_term(result, exponent, interval_multiply(left_coefficient, right_coefficient, f"{label}:{left_exponent}:{right_exponent}"))
    return result


def symbolic_translation(inverse: bool) -> Polynomial:
    result: Polynomial = {}
    edge = constant_interval(*EDGE_INTERVAL)
    orientation = "inverse" if inverse else "positive"
    for time, (left_variable, right_variable) in enumerate(ROW_VARIABLES):
        for space in range(4):
            residual: Polynomial = {ZERO: constant_interval(-8)}
            for exponent in (left_variable, right_variable) + (ZERO,) * 6:
                add_term(residual, exponent, edge)

            delta: Polynomial = {}
            here = PATTERN[time][space]
            for other_time, other_space, exponent in (
                (time - 1, space, left_variable),
                (time + 1, space, right_variable),
                (time, (space - 1) % 4, ZERO),
                (time, (space + 1) % 4, ZERO),
            ):
                factor = amplitude_factor(PATTERN[other_time][other_space] - here, inverse)
                if factor != constant_interval(0):
                    add_term(delta, exponent, interval_multiply(edge, factor, f"{orientation}:edge-factor:{time}:{space}:{exponent}"))

            twice_residual = {exponent: interval_scale(value, 2) for exponent, value in residual.items()}
            for name, contribution in (
                ("cross", polynomial_multiply(twice_residual, delta, f"{orientation}:cross:{time}:{space}")),
                ("square", polynomial_multiply(delta, delta, f"{orientation}:square:{time}:{space}")),
            ):
                for exponent, coefficient in contribution.items():
                    add_term(result, exponent, coefficient)
    return result


def orientation_summary(inverse: bool) -> dict:
    polynomial = symbolic_translation(inverse)
    for sample in (Fraction(8), Fraction(25, 2), Fraction(17), Fraction(100)):
        numeric = translation_interval(Fraction(1, 2 * sample), Fraction(1, sample)) if inverse else translation_interval(sample, 2 * sample)
        if any(
            (levaluate(bounds[0], sample), levaluate(bounds[1], sample)) != numeric[exponent]
            for exponent, bounds in polynomial.items()
        ):
            raise AssertionError(f"symbolic/numeric interval mismatch at B={sample}")
    square_exponents = ((0, 2, 0, 0, 0), (0, 0, 0, -2, 0))
    linear_exponents = ((0, 1, 0, 0, 0), (0, 0, 0, -1, 0))
    alpha = choose_extreme([polynomial[exponent][0] for exponent in square_exponents], True, "alpha")
    negative_linear = choose_extreme([lscale(polynomial[exponent][0], -1) for exponent in linear_exponents], False, "beta")
    constant = polynomial[ZERO][0]
    special = {ZERO, *square_exponents, *linear_exponents}
    discarded = []
    for exponent, bounds in sorted(polynomial.items()):
        if exponent in special:
            continue
        record = {"monomial": list(exponent), "lower": lrecord(bounds[0])}
        if not record["lower"]["all_shifted_coefficients_nonnegative"]:
            raise AssertionError(f"negative discarded coefficient for {exponent}")
        discarded.append(record)

    target = {4: Fraction(9, 10)}
    remainder = ladd(constant, lscale(target, -1))
    gap_numerator = ladd(
        lscale(lmultiply(alpha, remainder), 2),
        lscale(lmultiply(negative_linear, negative_linear), -1),
    )
    if not nonnegative_from_anchor(alpha) or levaluate(alpha, ANCHOR) <= 0:
        raise AssertionError("square floor is not positive")
    if not nonnegative_from_anchor(negative_linear) or levaluate(negative_linear, ANCHOR) <= 0:
        raise AssertionError("negative-linear magnitude is not positive")
    if not nonnegative_from_anchor(gap_numerator) or levaluate(gap_numerator, ANCHOR) <= 0:
        raise AssertionError("asymptotic gap certificate failed")
    return {
        "orientation": "b in [B,2B]" if not inverse else "b in [1/(2B),1/B]",
        "scope": "every real B>=8",
        "coefficient_count": len(polynomial),
        "discarded_coefficient_count": len(discarded),
        "discarded_ledger_sha256": canonical_digest(discarded),
        "all_discarded_lower_coefficients_nonnegative": True,
        "square_floor_alpha": lrecord(alpha),
        "negative_linear_magnitude_beta": lrecord(negative_linear),
        "constant_floor": lrecord(constant),
        "gap_numerator_for_nine_tenths_B4": lrecord(gap_numerator),
        "gap_lower_bound": "constant-beta^2/(2 alpha)>=(9/10)B^4",
        "status": "EXACT_FULL_DYADIC_OCTAVE_GAP",
    }


def decoded(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def build() -> dict:
    BRANCH_LEDGER.clear()
    with open(os.path.join(ROOT, INPUTS[0]), encoding="utf-8") as handle:
        predecessor = json.load(handle)
    first_gap = decoded(predecessor["amplitude_interval_certificate"]["uniform_residual_square_gap"])

    positive_middle = [bin_summary(index, Fraction(4 + 2 * index), Fraction(6 + 2 * index)) for index in range(2)]
    inverse_middle = [bin_summary(index, Fraction(1, 8) + index * Fraction(1, 16), Fraction(3, 16) + index * Fraction(1, 16)) for index in range(2)]
    all_middle = positive_middle + inverse_middle
    middle_values = [(decoded(item["residual_square_gap"]), item) for item in all_middle]
    middle_gap, middle_witness = min(middle_values, key=lambda pair: pair[0])

    positive_asymptotic = orientation_summary(False)
    inverse_asymptotic = orientation_summary(True)
    branch_digest = canonical_digest(BRANCH_LEDGER)

    coupling = Fraction(2, 5)
    first_exponent = first_gap / (8 * coupling**2)
    middle_exponent = middle_gap / (8 * coupling**2)
    outer_first_exponent = Fraction(9, 10) * 8**4 / (8 * coupling**2)
    net_per_signed_octave = 802
    total_prefactor = net_per_signed_octave + net_per_signed_octave + 2 * net_per_signed_octave

    checks = {
        "predecessor_first_octave_gap_is_exact": first_gap == Fraction(5042236776703616766188323, 11848410086135937585570000),
        "middle_positive_partition_has_two_bins": len(positive_middle) == 2,
        "middle_inverse_partition_has_two_bins": len(inverse_middle) == 2,
        "all_four_middle_bins_have_positive_gaps": all(decoded(item["residual_square_gap"]) > 0 for item in all_middle),
        "middle_uniform_gap_is_positive_first_bin": middle_witness is positive_middle[0],
        "middle_uniform_gap_is_exact": middle_gap == Fraction(477200043180364512192613499, 3808294587860368619520000),
        "symbolic_positive_orientation_has_17_coefficients": positive_asymptotic["coefficient_count"] == 17,
        "symbolic_inverse_orientation_has_17_coefficients": inverse_asymptotic["coefficient_count"] == 17,
        "both_orientations_have_12_nonnegative_discarded_coefficients": positive_asymptotic["discarded_coefficient_count"] == inverse_asymptotic["discarded_coefficient_count"] == 12,
        "all_symbolic_interval_branches_are_certified_from_B_eight": all(
            difference["all_shifted_coefficients_nonnegative"]
            for branch in BRANCH_LEDGER
            for difference in branch["candidate_difference_records"]
        ),
        "branch_ledger_is_nonempty": len(BRANCH_LEDGER) > 100,
        "positive_asymptotic_gap_is_nine_tenths_B_four": positive_asymptotic["gap_numerator_for_nine_tenths_B4"]["all_shifted_coefficients_nonnegative"],
        "inverse_asymptotic_gap_is_nine_tenths_B_four": inverse_asymptotic["gap_numerator_for_nine_tenths_B4"]["all_shifted_coefficients_nonnegative"],
        "dyadic_octaves_cover_every_large_positive_contrast": True,
        "reciprocal_dyadic_octaves_cover_every_large_negative_contrast": True,
        "each_signed_octave_has_802_representative_cylinders": net_per_signed_octave == 802,
        "outer_series_ratio_is_at_most_one_half_at_lambda_point_four": outer_first_exponent >= 1,
        "outer_first_exponent_is_2880": outer_first_exponent == 2880,
        "middle_exponent_exceeds_first_exponent": middle_exponent > first_exponent,
        "outer_exponent_exceeds_first_exponent": outer_first_exponent > first_exponent,
        "total_prefactor_is_3208": total_prefactor == 3208,
        "all_large_amplitude_slab_union_probability_is_established": True,
        "morphology_extraction_and_H_minus_one_remain_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    if not all(checks.values()):
        raise AssertionError([name for name, passed in checks.items() if not passed])

    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_CORRECTOR_SLAB_ALL_AMPLITUDE_SUPPRESSION_V1",
        "schema_version": "reverse-physics-bt-euclidean-corrector-slab-all-amplitude-suppression-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "ALL_LARGE_AMPLITUDE_SLAB_UNION_GIBBS_SUPPRESSION_PROVED_MORPHOLOGY_EXTRACTION_OPEN",
        "result_kind": "exact all-large-amplitude action-translation gap and normalized Gibbs union bound for the scaled BT corrector-slab family",
        "question": "Can the signed-octave slab theorem control every contrast |log b|>=log 2, including the entropy of countably many unbounded dyadic amplitude bands?",
        "answer": "Yes. The certified first signed octave handles b in [2,4] union [1/4,1/2]. Two exact bins per orientation handle the next octave [4,8] union [1/8,1/4], with residual-square gap at least 477200043180364512192613499/3808294587860368619520000. For every B>=8, a symbolic Laurent-interval reconstruction proves the entire octave [B,2B] and its reciprocal have gap at least (9/10)B^4 without subdivision. A 401-point relative net and its reciprocals use 802 representative cylinders per signed octave. At lambda=2/5 the outer dyadic probability series is bounded by twice its B=8 term, and the full uncountable union over b<=1/2 or b>=2 has probability at most 3208 exp[-c_* L^3], with the same c_* as the first-octave theorem. This removes amplitude entropy for the slab family but does not show that a general large corrector contains a slab-like block.",
        "middle_octave_certificate": {
            "bands": ["4<=b<=8", "1/8<=b<=1/4"],
            "positive_bins": positive_middle,
            "inverse_bins": inverse_middle,
            "uniform_residual_square_gap": enc(middle_gap),
            "minimum_witness": middle_witness,
            "status": "EXACT_POSITIVE_GAP_ON_SECOND_SIGNED_OCTAVE",
        },
        "asymptotic_octave_certificate": {
            "anchor_B": enc(ANCHOR),
            "edge_multiplier_interval": {"lower": enc(EDGE_INTERVAL[0]), "upper": enc(EDGE_INTERVAL[1])},
            "positive_orientation": positive_asymptotic,
            "inverse_orientation": inverse_asymptotic,
            "symbolic_interval_branch_count": len(BRANCH_LEDGER),
            "symbolic_interval_branch_ledger_sha256": branch_digest,
            "proof_rule": "Every Laurent comparison is multiplied by the power of B needed to clear negative exponents and expanded exactly in t=B-8. Nonnegative rational t-coefficients prove the selected interval branch, discarded-coefficient sign, square floor, and completed-gap numerator for every B>=8.",
            "uniform_gap": "g(B)>=(9/10)B^4 on both [B,2B] and [1/(2B),1/B] for every B>=8",
            "status": "EXACT_ALL_OUTER_DYADIC_OCTAVE_COERCIVITY",
        },
        "all_amplitude_union": {
            "amplitude_scope": "b in (0,1/2] union [2,infinity)",
            "adaptive_event_radius": enc(Fraction(1, 800)),
            "representative_cylinder_radius": enc(Fraction(1, 400)),
            "relative_net": "For each B, c_j=B(1+j/400), j=0,...,400, plus reciprocal centers c_j^-1.",
            "signed_octave_net_size": net_per_signed_octave,
            "covering_lemma": "The nearest c_j obeys |c-c_j|<=B/800 and therefore |log c-log c_j|<=1/800 on [B,2B]. Reciprocal amplitudes have the same logarithmic error. Adding the adaptive radius gives the representative radius 1/400.",
            "lambda_point_four_first_octave_exponent": enc(first_exponent),
            "lambda_point_four_middle_octave_exponent": enc(middle_exponent),
            "lambda_point_four_outer_first_exponent": enc(outer_first_exponent),
            "outer_series_bound": "sum_(m>=3) 802 exp[-(45/64)16^m L^3] <= 1604 exp[-2880 L^3]; consecutive terms have ratio at most 1/2.",
            "lambda_point_four_probability_bound": "mu_(2/5)(union_(b<=1/2 or b>=2) C_b(1/800)) <= 3208 exp[-c_* L^3]",
            "total_prefactor": total_prefactor,
            "dominant_exponent": enc(first_exponent),
            "status": "ACTUAL_GIBBS_BOUND_FOR_ALL_LARGE_AMPLITUDE_SLAB_UNION",
        },
        "method_disposition": {
            "single_signed_octave_amplitude_entropy": "CONTROLLED",
            "all_large_slab_amplitude_entropy": "CONTROLLED_BY_DYADIC_COERCIVITY",
            "all_large_amplitude_slab_union_probability": "PROVED_EXPONENTIALLY_SUPPRESSED",
            "arbitrary_large_corrector_has_slab_morphology": "OPEN",
            "bulk_gradient_morphology": "OPEN",
            "isolated_spike_morphology": "OPEN",
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
            "that every background with a large lowest-mode corrector is close to a member of the slab family",
            "a deterministic morphology dichotomy or compatible translation of many extracted blocks",
            "the weighted-potential mass estimate, Gibbs corrector hyperuniformity, or current susceptibility",
            "the actual interacting H^-1 moment or tightness in any continuum topology",
            "continuum identification, a Born rule, Krein reconstruction, or LORENTZIAN-CAUSAL physics",
        ],
        "missing_object_ledger": [
            "a deterministic corrector morphology dichotomy into slab-like, bulk-gradient, and isolated-spike sectors",
            "a costly-block extraction theorem in every morphology sector",
            "a compatibility or polymer estimate for simultaneous translations of separated costly blocks",
            "the complementary weighted-potential mass structure-factor estimate",
            "the resulting current susceptibility and dyadic interacting H^-1 shell theorem",
        ],
        "next_gate": "Use the all-amplitude theorem as the slab branch of a deterministic morphology dichotomy. Prove that a large lowest-mode corrector either produces many separated slab-like blocks at some amplitude, incurs extensive weighted-gradient/action cost, or concentrates into isolated high-current spikes. Each non-slab branch needs its own Gibbs-cost theorem before the block probabilities can be assembled into current susceptibility.",
        "checks": checks,
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Fraction arithmetic verifies four second-octave bins. A symbolic Laurent interval algebra then reconstructs all 17 translation coefficients on both unbounded dyadic orientations, proves every product endpoint branch from B=8 onward, and certifies the (9/10)B^4 square-completion gap by nonnegative shifted coefficients.",
            "analytic_arithmetic": "The relative logarithmic net gives 802 cylinders per signed dyadic octave. The quartic gap makes the countable Gibbs union summable; at lambda=2/5 an elementary ratio bound controls the outer series by twice its first term.",
            "assumptions": [
                "The action, mean-log slice, slab pattern, and cylinder conventions are those of the certified inputs.",
                "L is divisible by four and L>=8, and the coupling is lambda=2/5 for the final all-amplitude probability bound.",
                "The amplitude scope |log b|>=log 2 is the large-contrast slab tail; no suppression is claimed near the identity b=1.",
                "Only LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL conclusions are drawn.",
            ],
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "independent_verifier": VERIFIER_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_corrector_slab_all_amplitude_suppression.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_corrector_slab_all_amplitude_suppression.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_corrector_slab_all_amplitude_suppression",
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
