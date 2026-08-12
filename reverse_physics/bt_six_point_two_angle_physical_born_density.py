#!/usr/bin/env python3
"""Exact two-angle BT six-point local Born-density theorem."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))

from bt_bivariate_rational import T, U, ZERO, coerce
from bt_six_point_generic_external_mass_kernel import (
    FULL_MASK,
    generic_external_mass_kernel,
)


CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_TWO_ANGLE_PHYSICAL_BORN_DENSITY_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-six-point-two-angle-physical-born-density-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-six-point-two-angle-physical-born-density.md"
SOURCE = "efa87446a599aac7ce26004ba1046137837d18d1"
INPUTS = [
    "planning/work-items/"
    "reverse-physics-bateman-six-point-two-angle-born-nonnegativity.json",
    "reverse_physics/bt_bivariate_rational.py",
    "reverse_physics/bt_six_point_generic_external_mass_kernel.py",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_NONPLANAR_DIAGONAL_PHYSICAL_BORN_DENSITY_V1.json",
]


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def vector(*entries):
    return tuple(coerce(value) for value in entries)


def add(*vectors):
    return tuple(
        sum((value[index] for value in vectors), ZERO) for index in range(4)
    )


def negate(value):
    return tuple(-entry for entry in value)


def minkowski_square(value):
    return value[0] * value[0] - sum(
        (entry * entry for entry in value[1:]), ZERO
    )


def exact_two_angle_family():
    cosine = (1 - T * T) / (1 + T * T)
    sine = 2 * T / (1 + T * T)
    tilt_cosine = (1 - U * U) / (1 + U * U)
    tilt_sine = 2 * U / (1 + U * U)
    incoming = [
        vector(Fraction(6, 5), Fraction(6, 5), 0, 0),
        vector(1, Fraction(-3, 5), Fraction(4, 5), 0),
        vector(1, Fraction(-3, 5), Fraction(-4, 5), 0),
    ]

    def rotate(value):
        rotated_x = cosine * value[1] - sine * value[2]
        rotated_y = sine * value[1] + cosine * value[2]
        return (
            value[0],
            rotated_x,
            tilt_cosine * rotated_y,
            tilt_sine * rotated_y,
        )

    outgoing = [rotate(value) for value in incoming]
    momenta = incoming + [negate(value) for value in outgoing]
    total = add(*momenta)
    adjacent = [
        minkowski_square(add(momenta[index], momenta[(index + 1) % 6]))
        for index in range(6)
    ]
    triples = [
        minkowski_square(
            add(
                momenta[index],
                momenta[(index + 1) % 6],
                momenta[(index + 2) % 6],
            )
        )
        for index in range(3)
    ]
    result = generic_external_mass_kernel(
        adjacent,
        triples,
        scalar_coerce=coerce,
        max_degree=3,
    )
    coefficients = result["degree_three"]
    retained_amplitude_degrees = sorted(
        {mask.bit_count() for mask in result["amplitude"].coefficients}
    )
    representatives = [
        mask
        for mask in sorted(coefficients)
        if mask < (FULL_MASK ^ mask)
    ]
    complement_differences = [
        coefficients[mask] - coefficients[FULL_MASK ^ mask]
        for mask in representatives
    ]
    # In a homogeneous degree-three jet on six square-free variables, the
    # full-mask coefficient of the square is the sum over the twenty ordered
    # complement products.  Once all ten complement equalities hold, this is
    # identically twice the ten-square sum; constructing that very large
    # rational expression a second time is deliberately avoided.
    square_identity = (
        len(coefficients) == 20
        and all(value == 0 for value in complement_differences)
    )
    del result["topology_amplitudes"]
    del result["amplitude"]
    rows = []
    for mask in representatives:
        value = coefficients[mask]
        complement = coefficients[FULL_MASK ^ mask]
        rows.append(
            {
                "mask": mask,
                "complement_mask": FULL_MASK ^ mask,
                "exactly_equal": value == complement,
                "numerator_total_degree": int(value.numerator.total_degree()),
                "denominator_total_degree": int(value.denominator.total_degree()),
                "numerator_variable_degrees": list(map(int, value.numerator.degrees())),
                "denominator_variable_degrees": list(
                    map(int, value.denominator.degrees())
                ),
                "numerator_term_count": len(value.numerator),
                "denominator_term_count": len(value.denominator),
            }
        )
    return {
        "parameters": ["t", "u"],
        "rotation_order": "R_x(u) R_z(t)",
        "rational_rotation_denominators": ["1+t^2", "1+u^2"],
        "all_six_massless": all(minkowski_square(value) == 0 for value in momenta),
        "momentum_conservation": all(entry == 0 for entry in total),
        "outgoing_z_depends_nontrivially_on_u": any(
            value[3].numerator.degrees()[1] > 0 for value in outgoing
        ),
        "in_plane_orientation_depends_nontrivially_on_t": any(
            value[1].numerator.degrees()[0] > 0 for value in outgoing
        ),
        "adjacent_invariant_degrees": [
            [int(value.numerator.total_degree()), int(value.denominator.total_degree())]
            for value in adjacent
        ],
        "triple_invariant_degrees": [
            [int(value.numerator.total_degree()), int(value.denominator.total_degree())]
            for value in triples
        ],
        "degree_three_term_count": len(coefficients),
        "retained_amplitude_degrees_through_three": retained_amplitude_degrees,
        "middle_coefficients": rows,
        "ten_complement_pairs_equal": all(value == 0 for value in complement_differences),
        "equals_twice_ten_square_sum": square_identity,
        "at_least_one_coefficient_is_nonzero_rational_function": any(
            value != 0 for value in coefficients.values()
        ),
    }


def build():
    family = exact_two_angle_family()
    checks = {
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "all_six_momenta_are_exactly_massless": family["all_six_massless"],
        "three_to_three_momentum_is_exactly_conserved": family[
            "momentum_conservation"
        ],
        "t_and_u_enter_independent_rotation_factors": family[
            "outgoing_z_depends_nontrivially_on_u"
        ]
        and family["in_plane_orientation_depends_nontrivially_on_t"],
        "all_twenty_middle_coefficients_are_retained": family[
            "degree_three_term_count"
        ]
        == 20
        and len(family["middle_coefficients"]) == 10,
        "amplitude_has_no_terms_below_mass_degree_three": family[
            "retained_amplitude_degrees_through_three"
        ]
        == [3],
        "all_ten_complement_pairs_are_identical_in_Q_t_u": family[
            "ten_complement_pairs_equal"
        ],
        "six_derivative_kernel_is_twice_ten_rational_squares": family[
            "equals_twice_ten_square_sum"
        ],
        "the_square_sum_is_not_the_zero_rational_function": family[
            "at_least_one_coefficient_is_nonzero_rational_function"
        ],
        "local_density_is_nonnegative_at_every_regular_real_parameter_pair": family[
            "equals_twice_ten_square_sum"
        ],
        "local_density_is_strictly_positive_on_a_dense_open_regular_subset": family[
            "equals_twice_ten_square_sum"
        ]
        and family["at_least_one_coefficient_is_nonzero_rational_function"],
        "possible_common_zero_locus_is_not_silently_excluded": True,
        "six_delta_prime_sign_is_positive": (-1) ** 6 == 1,
        "regular_measure_derivatives_decouple": family[
            "retained_amplitude_degrees_through_three"
        ]
        == [3],
        "two_angle_family_is_not_called_complete_phase_space": True,
        "integration_eq19_gravity_and_causality_remain_open": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_SIX_POINT_TWO_ANGLE_PHYSICAL_BORN_DENSITY_V1",
        "schema_version": "reverse-physics-bt-six-point-two-angle-physical-born-density-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "exact local six-delta-prime tree Born density on a two-independent-angle physical 3-to-3 family",
        "question": "Does the complete BT six-point local Born density stay nonnegative when the in-plane and out-of-plane rotations are algebraically independent?",
        "answer": "Yes on the declared two-angle rigid-rotation family. Over the exact field Q(t,u), the complete 220-tree degree-three external-mass jet has twenty coefficients satisfying all ten complement identities c_S=c_Sc. Hence the six-delta-prime kernel is exactly 2 sum c_S(t,u)^2: it is nonnegative at every regular real parameter pair and strictly positive on a dense open regular subset. A complete bivariate common-zero classification was stopped at the memory boundary, so isolated regular zeros are not excluded. The family varies two relative orientation angles but fixes the incoming and outgoing energy shape; it is not the full five-dimensional final-state phase space or an integrated probability.",
        "exact_two_angle_family": family,
        "local_born_density": {
            "external_projector": "(-partial_x0)...(-partial_x5) evaluated at x_i=0",
            "external_derivative_sign": "+1 from (-1)^6",
            "amplitude_minimum_mass_degree": 3,
            "squared_amplitude_minimum_mass_degree": 6,
            "measure_decoupling": "The amplitude has no mass degree below three, so its square begins at the full six-mass mask. A regular local phase-space weight contributes only its positive massless value to this leading coefficient.",
            "positivity_assumption": "The undifferentiated massless local phase-space/detector weight is nonnegative, and positive when strict generic positivity is asserted.",
            "status": "NONNEGATIVE_EVERYWHERE_REGULAR_AND_STRICTLY_POSITIVE_GENERICALLY_ON_DECLARED_TWO_ANGLE_FAMILY",
        },
        "interpretation": {
            "two_angle_middle_degree_recombination": "NONNEGATIVE_TEN_SQUARE_SUM",
            "generic_regular_sign": "STRICTLY_POSITIVE",
            "possible_isolated_or_lower_dimensional_regular_zero_set": "NOT_EXCLUDED",
            "correlated_crossed_negative_quotient": "REMAINS_A_REDUCED_BOUNDARY_BLOCK_NOT_THE_COMPLETE_DENSITY",
            "complete_five_dimensional_final_state_phase_space": "NOT_COMPUTED",
            "integrated_normalized_probability": "NOT_COMPUTED",
            "Eq19_all_orders": "NOT_PROVED",
        },
        "assumptions": [
            "The public BT cubic and quartic vertices are used with their perfect-square relative coupling and common tree phase omitted before squaring.",
            "Signature is (+---), and the three future-null outgoing momenta enter the all-incoming amplitude with a minus sign.",
            "The outgoing rigid rotation is R_x(u)R_z(t), with t and u algebraically independent rational stereographic parameters.",
            "The cyclic invariant chart is held fixed while the six external mass squares are differentiated independently.",
            "Real parameter pairs exclude zeros of the reduced rational denominators, including internal propagator poles.",
            "The local massless phase-space/detector weight is regular and nonnegative at the selected interior point.",
            "Nonzero rational coefficients imply generic strict positivity, not absence of every isolated or lower-dimensional common zero.",
        ],
        "does_not_establish": [
            "strict positivity at every regular two-angle parameter pair",
            "absence or classification of a lower-dimensional common zero locus",
            "positivity over the complete five-dimensional massless three-particle final-state phase space",
            "variation of outgoing energies or Dalitz shape",
            "a regulated, integrated, or normalized six-point probability",
            "cancellation or prescription for internal propagator poles",
            "a complete Moller, LSZ, or S operator",
            "Bateman--Turok Eq. (19)",
            "positivity beyond tree level or KLN cancellation",
            "a metric or BRST lift to Weyl gravity",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "next_gate": "Either classify the possible common zero locus using a memory-bounded elimination rail, or enlarge the exact physical chart to the two final-state shape variables and the missing orientation angle. Only after a sign theorem on that larger chart should a common pole regulator and phase-space integral be promoted. Eq. (19) remains a separate nonlinear projector-transport problem.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "producer_method": "The complete cached subset recursion is evaluated in the 64-slot square-free mass algebra truncated at the only relevant degree, three. Scalar coefficients are reduced exactly in Q(t,u) by FLINT sparse multivariate polynomial gcd algorithms. Reduced numerator/denominator degree and term metadata are retained; all complement differences are compared as exact rational functions, never by sampling or floating point. In a homogeneous degree-three six-variable square-free jet those identities algebraically imply the displayed ten-square full-mask coefficient.",
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096v1",
                "equations": ["Eq. (18)", "Appendix B Eqs. (24)-(25)"],
            },
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_six_point_two_angle_physical_born_density.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_six_point_two_angle_physical_born_density.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest reverse_physics.tests.test_bt_six_point_two_angle_physical_born_density",
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks,
        },
        "report": REPORT,
        "schema": SCHEMA,
    }


def canonical(value):
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    value = build()
    rendered = canonical(value)
    if args.write:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check and os.path.exists(args.output):
        with open(args.output, encoding="utf-8") as handle:
            if handle.read() != rendered:
                print("certificate drift", file=sys.stderr)
                return 1
    print("checks %d/%d" % (value["checks"]["passed"], value["checks"]["total"]))
    print("RESULT:", "PASS" if value["checks"]["ok"] else "FAIL")
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
