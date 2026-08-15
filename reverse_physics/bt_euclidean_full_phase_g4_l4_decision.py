#!/usr/bin/env python3
"""Build the exact L=4 decision certificate for full-phase BT M4."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from reverse_physics.bt_euclidean_full_phase_g4_l4_exact import (
    ALLOWED,
    KERNEL_DENOMINATOR,
    OMEGA,
    PROPAGATOR_LCM,
    terms,
)


CERT_REL = "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_G4_L4_DECISION_V1.json"
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = "reverse_physics/schema/reverse-physics-bt-euclidean-full-phase-g4-l4-decision-v1.schema.json"
REPORT_REL = "reverse_physics/reports/bt-euclidean-full-phase-g4-l4-decision.md"
VERIFIER_REL = "reverse_physics/verify_bt_euclidean_full_phase_g4_l4_decision.py"
DATA_REL = "reverse_physics/data/bt_euclidean_full_phase_g4_l4_exact_v1.json"
EXACT_SOURCE_REL = "reverse_physics/bt_euclidean_full_phase_g4_l4_exact.py"
MODULAR_SOURCE_REL = "reverse_physics/bt_euclidean_full_phase_g4_l4_modular_verify.cpp"
SOURCE_COMMIT = "d0f09db4d46aa5a8198ef452f68443cf7380009f"
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_G6_CURRENT_RECONCILIATION_V1.json",
    EXACT_SOURCE_REL,
    DATA_REL,
    MODULAR_SOURCE_REL,
]
EXPECTED_M4 = Fraction(-2569186115493259, 716934758400000)
PRIMES = (2305843009213693951, 2305843009213693921, 2305843009213693907, 2305843009213693723)
KERNEL_ABSOLUTE_BOUNDS = {3: Fraction(1536, 6), 4: Fraction(7168, 24), 5: Fraction(30720, 120)}


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def dec(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def sha256(relative: str) -> str:
    value = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            value.update(block)
    return value.hexdigest()


def rational_residues(value: Fraction) -> list[int]:
    return [value.numerator % prime * pow(value.denominator, -1, prime) % prime for prime in PRIMES]


def modular_uniqueness_bound(m4: Fraction) -> dict:
    covariance_sum = sum((Fraction(1, OMEGA[momentum] ** 2) for momentum in ALLOWED), Fraction(0))
    expression_bound = Fraction(0)
    common_denominator = 1
    term_bounds = []
    for term in terms():
        edge_count = sum(item["degree"] - len(item["fixed"]) for item in term["vertices"]) // 2
        outer = abs(term["coefficient"])
        for item in term["vertices"]:
            outer *= item["prefactor"]
        denominator = outer.denominator * math.prod(
            KERNEL_DENOMINATOR[item["degree"]] for item in term["vertices"]
        ) * PROPAGATOR_LCM**edge_count
        common_denominator = math.lcm(common_denominator, denominator)
        pairing_count = math.prod(range(1, 2 * edge_count, 2)) if edge_count else 1
        bound = outer * pairing_count * covariance_sum**edge_count
        for item in term["vertices"]:
            bound *= KERNEL_ABSOLUTE_BOUNDS[item["degree"]]
        expression_bound += bound
        term_bounds.append({"name": term["name"], "edge_count": edge_count, "pairing_bound": pairing_count, "absolute_bound": enc(bound)})
    integer_difference_bound = m4.denominator * common_denominator * expression_bound + abs(m4.numerator) * common_denominator
    prime_product = math.prod(PRIMES)
    return {
        "allowed_covariance_absolute_sum": enc(covariance_sum),
        "common_expression_denominator": common_denominator,
        "expression_absolute_bound": enc(expression_bound),
        "term_bounds": term_bounds,
        "integer_difference_bound": integer_difference_bound.numerator,
        "integer_difference_bound_denominator": integer_difference_bound.denominator,
        "integer_difference_bound_bits": math.ceil(integer_difference_bound).bit_length(),
        "primes": list(PRIMES),
        "prime_product": prime_product,
        "prime_product_bits": prime_product.bit_length(),
        "uniqueness_inequality": prime_product > 2 * integer_difference_bound,
    }


def build() -> dict:
    with open(os.path.join(ROOT, DATA_REL), encoding="utf-8") as handle:
        data = json.load(handle)
    rows = [dec(row["value"]) for row in data["terms"]]
    m4 = dec(data["M4_full"])
    bound = modular_uniqueness_bound(m4)
    checks = {
        "eight_connected_families_are_present": len(rows) == 8,
        "term_ledger_sums_to_M4_full": sum(rows, Fraction(0)) == m4,
        "M4_full_equals_expected_negative_fraction": m4 == EXPECTED_M4,
        "M4_full_is_strictly_negative_nonzero": m4 < 0,
        "cubic_current_B_square_is_strictly_positive": rows[0] > 0,
        "Q_square_covariance_family_vanishes_at_L4": rows[-1] == 0,
        "four_prime_product_exceeds_twice_difference_bound": bound["uniqueness_inequality"],
        "modular_residues_are_recorded_for_every_term": True,
        "one_cosine_value_is_not_substituted": True,
        "large_volume_full_phase_scaling_remains_open": True,
        "nonperturbative_current_susceptibility_remains_open": True,
        "actual_interacting_H_minus_one_remains_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    if not all(checks.values()):
        raise AssertionError([name for name, passed in checks.items() if not passed])
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_G4_L4_DECISION_V1",
        "schema_version": "reverse-physics-bt-euclidean-full-phase-g4-l4-decision-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "FULL_PHASE_L4_M4_NEGATIVE_NONZERO_EXACT_LARGE_VOLUME_AND_INTERACTING_OPEN",
        "result_kind": "exact finite-volume decision of the complete full-cosine-sine BT order-g4 score coefficient",
        "question": "After integrating both lowest-mode phases and using the translation-invariant background with 0,+p,-p removed, does the complete full-phase M4 coefficient cancel at L=4?",
        "answer": "No. The two-dimensional fiber reduction leaves exactly eight connected Wick families. Exact rational momentum enumeration on the 4^4 torus gives M4_full=-2569186115493259/716934758400000, approximately -3.5835703115. The isolated cubic-current/quartic-score square is positive, 55147376933567/11202105600000, but the complete density, normalization, and cross terms overcancel it. An independent C++17 implementation reconstructs the kernels and topology ledger modulo four 61-bit primes. Its residues agree term by term, and their 244-bit product exceeds twice a rigorous 226-bit cleared-integer difference bound, proving the rational equality. This refutes an exact finite-volume full-phase cancellation identity. It does not decide the large-L scaling, the resummed interacting susceptibility, or H^-1.",
        "two_dimensional_fiber_reduction": {
            "complex_coordinate": "zeta=t_c-i*t_s with E[zeta^2]=0, E[|zeta|^2]=2v, and E[|zeta|^4]=8v^2",
            "W1": "W1=U30 because balanced U32 requires the removed zero background mode and same-sign U32 has zero isotropic fiber expectation",
            "W2_modulo_constants": "W2=U40+v*F42-(v/2)*|A|^2-(1/2)*E_fiber[Q^2] modulo background-independent constants",
            "connected_formula": "M4_full=E[|B|^2+2*A.C-2*U30*A.B]+Cov(|A|^2,U30^2/2-U40-v*F42+v*|A|^2/2+E[Q^2]/2)",
            "family_count": 8,
            "status": "EXACT_FULL_PHASE_CONNECTED_LEDGER",
        },
        "exact_L4_decision": {
            "lattice": data["lattice"],
            "terms": [
                {
                    **row,
                    "modular_residues": rational_residues(value),
                }
                for row, value in zip(data["terms"], rows)
            ],
            "M4_full": data["M4_full"],
            "M4_full_decimal": data["M4_full_decimal"],
            "M4_full_modular_residues": rational_residues(m4),
            "status": "PROVED_EXACT_NEGATIVE_NONZERO",
        },
        "independent_modular_verification": {
            "source": MODULAR_SOURCE_REL,
            "source_sha256": sha256(MODULAR_SOURCE_REL),
            "method": "Independent C++17 fixed-leg fiber ledger, labeled Wick topology enumeration, deleted-mode Z_4^4 momentum-flow solve, and four-prime residue evaluation",
            **bound,
            "status": "EXACT_BY_RESIDUES_PLUS_RIGOROUS_INTEGER_BOUND",
        },
        "interpretation": {
            "termwise_method": "The positive extensive cubic-current chaos is genuinely canceled by signed terms at this finite volume, confirming that no termwise lower bound can decide the complete susceptibility.",
            "fixed_order": "A negative perturbative coefficient is not a negative variance. It diagnoses strong nonuniform cancellation and cannot be promoted through the unbounded series remainder.",
            "scope": "This value uses the full cosine-sine background and does not import the older one-cosine sign.",
            "next_decision": "Derive the general-L translation-invariant eight-family kernels and decide whether M4_full is O(N*omega_p), subpower, or cancels at leading order.",
        },
        "method_disposition": {
            "finite_L4_complete_full_phase_M4": "NEGATIVE_NONZERO_EXACT",
            "all_volume_exact_full_phase_M4_zero_identity": "OBSTRUCTED_BY_L4_COUNTEREXAMPLE",
            "large_volume_full_phase_M4_sign_and_scaling": "OPEN",
            "uniform_perturbative_remainder": "OPEN",
            "nonperturbative_background_current_susceptibility": "OPEN",
            "actual_interacting_H_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "checks": checks,
        "does_not_establish": [
            "the sign, nonzero limit, or power/logarithmic scaling of full-phase M4 as L tends to infinity",
            "uniformity or validity of the perturbative expansion at fixed nonzero coupling",
            "divergence or boundedness of the nonperturbative current susceptibility or interacting H^-1 moment",
            "a continuum measure, Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
        ],
        "missing_object_ledger": [
            "a general-L affine momentum-flow atlas for the eight full-phase connected families",
            "combined large-volume bounds or asymptotic coefficients before absolute values",
            "a uniform nonperturbative current-susceptibility theorem or obstruction",
            "the dyadic interacting H^-1 shell theorem or obstruction",
            "tightness and continuum identification only after the H^-1 gate",
        ],
        "next_gate": "Generate the general-L affine atlas for the eight full-phase connected families using the translation-invariant propagator with 0,+p,-p removed. Combine common kernels before absolute values and determine whether the negative L=4 remainder retains an N*omega_p term or becomes subpower. Regardless of that fixed-order result, a uniform nonperturbative bridge remains mandatory before the interacting H^-1 gate.",
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Python arbitrary-precision integers, Fraction arithmetic, Gaussian-integer quarter-period kernels, and exact deleted-mode momentum flows; independent four-prime C++ arithmetic with a rational uniqueness bound",
            "assumptions": [
                "The full-phase vector M4 formula and coupling conventions are imported unchanged by content hash.",
                "The background Gaussian covariance vanishes exactly at 0,+p,-p and equals omega(k)^(-2) elsewhere.",
                "The finite-volume coefficient is not promoted to a large-volume, resummed, or nonperturbative theorem.",
                "Only LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL conclusions are drawn.",
            ],
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "independent_verifier": VERIFIER_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_full_phase_g4_l4_exact.py --check",
            "g++ -std=c++17 -O3 -Wall -Wextra -Werror reverse_physics/bt_euclidean_full_phase_g4_l4_modular_verify.cpp -o /tmp/bt-full-phase-g4-modverify && ulimit -v 500000; /tmp/bt-full-phase-g4-modverify",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_full_phase_g4_l4_decision.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_full_phase_g4_l4_decision",
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
