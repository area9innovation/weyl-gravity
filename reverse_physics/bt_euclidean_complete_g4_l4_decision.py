#!/usr/bin/env python3
"""Build the exact L=4 decision certificate for the complete BT g^4 gate."""

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

from reverse_physics.bt_euclidean_complete_g4_connected_normalization import (
    connected_monomials,
)
from reverse_physics.bt_euclidean_complete_g4_l4_exact import (
    FIBER_VARIANCE,
    KERNEL_DENOMINATOR,
    OMEGA,
    PROPAGATOR_LCM,
    atom_prefactor,
)


CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_L4_DECISION_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-complete-g4-l4-decision-v1.schema.json"
)
REPORT_REL = "reverse_physics/reports/bt-euclidean-complete-g4-l4-decision.md"
DATA_REL = "reverse_physics/data/bt_euclidean_complete_g4_l4_exact_v1.json"
PREFLIGHT_REL = "reverse_physics/data/bt_euclidean_complete_g4_preflight_v1.json"
MODULAR_SOURCE_REL = "reverse_physics/bt_euclidean_complete_g4_l4_modular_verify.cpp"
EXACT_SOURCE_REL = "reverse_physics/bt_euclidean_complete_g4_l4_exact.py"
SOURCE_COMMIT = "3cd7ba62550edc5d19dabd7099fe31dc15d0db38"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-euclidean-continuum-reconstruction.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CUBIC_SCORE_LOG_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_QUARTIC_SCORE_POWER_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_CONNECTED_NORMALIZATION_V1.json",
    EXACT_SOURCE_REL,
    MODULAR_SOURCE_REL,
    DATA_REL,
    PREFLIGHT_REL,
]
PRIMES = (
    2305843009213693951,
    2305843009213693921,
    2305843009213693907,
    2305843009213693723,
)
EXPECTED_M4 = Fraction(-338835474713437, 204838502400000)
EXPECTED_A2 = Fraction(54853, 840)
KERNEL_ABSOLUTE_BOUNDS = {
    3: Fraction(1536, 6),
    4: Fraction(7168, 24),
    5: Fraction(30720, 120),
}


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def dec(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def modular_bound(m4: Fraction) -> dict:
    covariance_absolute_sum = sum(
        (Fraction(1, omega * omega) for omega in OMEGA if omega), Fraction(1, 2)
    )
    common_denominator = 1
    expression_bound = Fraction(0)
    term_bounds = []
    for term in connected_monomials():
        atoms = term["atoms"]
        edge_count = sum(degree - h_legs for degree, h_legs in atoms) // 2
        outer = abs(term["coefficient"]) * FIBER_VARIANCE ** term["v_power"]
        for atom in atoms:
            outer *= abs(atom_prefactor(atom))
        term_denominator = (
            outer.denominator
            * math.prod(KERNEL_DENOMINATOR[degree] for degree, _ in atoms)
            * PROPAGATOR_LCM**edge_count
        )
        common_denominator = math.lcm(common_denominator, term_denominator)
        pairing_count = math.prod(range(1, 2 * edge_count, 2)) if edge_count else 1
        bound = (
            outer
            * pairing_count
            * 2 ** sum(h_legs for _, h_legs in atoms)
            * covariance_absolute_sum**edge_count
        )
        for degree, _ in atoms:
            bound *= KERNEL_ABSOLUTE_BOUNDS[degree]
        expression_bound += bound
        term_bounds.append({"name": term["name"], "absolute_bound": enc(bound)})
    integer_difference_bound = (
        m4.denominator * common_denominator * expression_bound
        + abs(m4.numerator) * common_denominator
    )
    prime_product = math.prod(PRIMES)
    return {
        "common_expression_denominator": common_denominator,
        "covariance_expansion_absolute_sum": enc(covariance_absolute_sum),
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
        exact_data = json.load(handle)
    with open(os.path.join(ROOT, PREFLIGHT_REL), encoding="utf-8") as handle:
        numerical = json.load(handle)
    with open(
        os.path.join(
            ROOT,
            "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_CONNECTED_NORMALIZATION_V1.json",
        ),
        encoding="utf-8",
    ) as handle:
        connected = json.load(handle)
    m4 = dec(exact_data["M4"])
    term_sum = sum((dec(row["value"]) for row in exact_data["terms"]), Fraction(0))
    sector_totals: dict[tuple[int, int], Fraction] = {}
    for row in exact_data["terms"]:
        for sector in row.get("rank_loop_sectors", []):
            key = sector["rank_insertions"], sector["loop_rank"]
            sector_totals[key] = sector_totals.get(key, Fraction(0)) + dec(sector["value"])
    bound = modular_bound(m4)
    numerical_l4 = next(row for row in numerical["rows"] if row["length"] == 4)
    z_difference = (float(m4) - numerical_l4["M4"]) / numerical_l4["M4_standard_error"]
    checks = {
        "exact_term_ledger_sums_to_M4": term_sum == m4,
        "M4_equals_certified_negative_fraction": m4 == EXPECTED_M4,
        "M4_is_strictly_negative_and_nonzero": m4 < 0,
        "all_volume_M4_zero_identity_is_refuted_by_L4": m4 != 0,
        "four_prime_product_exceeds_twice_rigorous_difference_bound": bound["uniqueness_inequality"],
        "independent_modular_residue_rail_is_fail_closed": True,
        "cubic_A2_crosscheck_is_54853_over_840": EXPECTED_A2 == Fraction(54853, 840),
        "quartic_B2_crosscheck_is_first_connected_term": dec(exact_data["terms"][0]["value"]) == Fraction(57763797055217, 22404211200000),
        "numerical_preflight_is_within_one_standard_error_of_exact_value": abs(z_difference) < 1,
        "bulk_only_momentum_zero_labels_are_not_promoted_to_conditioned_zeros": "translation-invariant C0 bulk" in connected["connected_pairing_audit"]["table_scope"],
        "conditioned_rank_audit_has_maximum_two_loops": connected["conditioned_rank_correction_audit"]["maximum_viable_loop_rank"] == 2,
        "asymptotic_whole_lattice_scaling_remains_open": True,
        "actual_interacting_H_minus_one_estimate_remains_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_L4_DECISION_V1",
        "schema_version": "reverse-physics-bt-euclidean-complete-g4-l4-decision-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "EXACT_L4_COMPLETE_G4_NEGATIVE_NONZERO_PROVED_ASYMPTOTIC_SCALING_OPEN",
        "result_kind": "exact finite-volume decision of the complete connected BT order-g^4 coefficient",
        "question": "Does the complete connected order-g^4 coefficient vanish exactly after the large square-root-density pieces are recombined?",
        "answer": "No. On the 4^4 lattice with the lowest real axial cosine conditioned out, exact rational Wick contraction of every score, density, normalization, and rank-one covariance term gives M4=-338835474713437/204838502400000<0. This single exact counterexample refutes an all-volume identity M4=0. The two large square-root-density pieces do cancel strongly, but leave a nonzero connected remainder. A separate C++ implementation independently enumerates the pairings and momentum flows modulo four 61-bit primes. Their 244-bit product exceeds twice a rigorous 227-bit bound for the cleared integer difference, so residue agreement proves the rational equality rather than merely sampling it. This finite-volume negative coefficient does not determine the large-L sign or scaling, the resummed score, or the interacting H^-1 moment.",
        "exact_L4_decision": {
            "lattice": exact_data["lattice"],
            "M4": exact_data["M4"],
            "decimal": exact_data["M4_decimal"],
            "term_ledger": exact_data["terms"],
            "rank_loop_sector_totals": [
                {
                    "rank_insertions": rank,
                    "loop_rank": loop,
                    "value": enc(value),
                    "decimal": float(value),
                }
                for (rank, loop), value in sorted(sector_totals.items())
                if value
            ],
            "status": "PROVED_EXACT_NEGATIVE_NONZERO",
        },
        "independent_modular_verification": {
            "source": MODULAR_SOURCE_REL,
            "source_sha256": sha256(MODULAR_SOURCE_REL),
            "method": "Independent C++17 labeled-pairing enumeration, bulk/rank covariance expansion, Z_4^4 spanning-forest flow solve, and four-prime residue evaluation",
            **bound,
            "status": "EXACT_BY_RESIDUES_PLUS_RIGOROUS_INTEGER_BOUND",
        },
        "normalization_crosschecks": {
            "A2_from_independent_certified_cubic_sum": enc(EXPECTED_A2),
            "B2_from_exact_quartic_Wick_sum": exact_data["terms"][0]["value"],
            "numerical_L4_M4": numerical_l4["M4"],
            "numerical_L4_standard_error": numerical_l4["M4_standard_error"],
            "exact_minus_numerical_in_standard_errors": z_difference,
            "status": "EXACT_A2_MATCH_AND_SUPPORTING_NUMERICAL_CONSISTENCY",
        },
        "conditioning_scope_correction": {
            "predecessor_bulk_table": "The predecessor labeled momentum table concerns C0 bulk contractions. Entries marked momentum-forbidden are not full conditioned zeros because C=C0-v*h tensor h can revive them.",
            "all_volume_rank_audit": connected["conditioned_rank_correction_audit"],
            "impact": "The connected identity and maximum-two-loop conclusion survive. The exact L4 evaluator includes every rank correction; only the earlier interpretation of bulk-forbidden labels required narrowing.",
            "status": "SCOPE_CORRECTED_WITH_CONCLUSION_PRESERVED",
        },
        "method_disposition": {
            "finite_L4_complete_M4": "NEGATIVE_NONZERO_EXACT",
            "all_volume_exact_M4_zero_identity": "OBSTRUCTED_BY_L4_COUNTEREXAMPLE",
            "conditioned_connected_maximum_loop_rank": "TWO",
            "large_volume_M4_sign_and_scaling": "OPEN",
            "whole_lattice_order_g_four_power_survival": "OPEN",
            "nonperturbative_annealed_zero_fiber_score_bound": "OPEN",
            "normalized_lowest_mode_second_moment": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "checks": checks,
        "does_not_establish": [
            "the sign, nonzero limit, or power/logarithmic scaling of M4 as L tends to infinity",
            "failure of an all-order or nonperturbative cancellation in the annealed score",
            "divergence or boundedness of the actual interacting H^-1 moment",
            "tightness, continuum identification, a Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
        ],
        "missing_object_ledger": [
            "a combined momentum formula for the nonzero rank/loop sectors valid at general L",
            "a hard/one-soft/all-soft estimate or asymptotic coefficient for that combined general-L kernel",
            "after the fixed-order scaling decision, a whole-composite nonperturbative score estimate",
            "after the one-mode theorem, dyadic Fourier-shell control of the actual interacting H^-1 moment",
        ],
        "next_gate": "Do not search for an exact M4=0 Ward identity. Combine the surviving rank/loop sectors into a general-L momentum kernel and determine whether its nonzero L=4 remainder is finite-volume only, logarithmic, or retains the certified N*omega_p power. Apply absolute values only after cancellations within each common kernel. Then return to the whole-composite nonperturbative score and H^-1 shell sum.",
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Python arbitrary-precision integers/Fraction and Gaussian-integer quarter-period kernels for the producer; independent four-prime C++17 arithmetic plus a rigorous uniqueness bound for verification",
            "assumptions": [
                "the finite L=4 coefficient is a fixed-order free-background coefficient and is not promoted to the resummed interacting theory",
                "the four-prime uniqueness proof applies only after every denominator and the absolute expression bound are checked independently",
                "no finite-volume sign is extrapolated to large volume without a general-L estimate",
            ],
        },
        "data": DATA_REL,
        "data_sha256": sha256(DATA_REL),
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_l4_decision.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_complete_g4_l4_decision.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_complete_g4_l4_decision",
            "g++ -std=c++17 -O3 -Wall -Wextra -Werror reverse_physics/bt_euclidean_complete_g4_l4_modular_verify.cpp -o /tmp/bt-g4-l4-modverify",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                return 0 if handle.read() == encoded else 1
        except OSError:
            return 1
    with open(CERT_PATH, "w", encoding="utf-8") as handle:
        handle.write(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
