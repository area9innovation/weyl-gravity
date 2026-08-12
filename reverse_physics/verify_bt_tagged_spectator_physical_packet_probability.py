#!/usr/bin/env python3
"""Independent verifier for the tagged-spectator BT probability."""
from __future__ import annotations

from fractions import Fraction
import hashlib
from itertools import combinations
import json
import os
import sys

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_SPECTATOR_PHYSICAL_PACKET_PROBABILITY_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-tagged-spectator-physical-packet-probability-v1.schema.json")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def file_hash(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def square(vector):
    return vector[0] ** 2 - sum(value**2 for value in vector[1:])


def esquare(vector):
    return sum(value**2 for value in vector)


def add(*vectors):
    return tuple(sum(vector[index] for vector in vectors) for index in range(4))


def independent_bell_number(n):
    stirling = [1]
    for size in range(1, n + 1):
        row = [0] * (size + 1)
        for blocks in range(1, size + 1):
            row[blocks] = blocks * (stirling[blocks] if blocks < len(stirling) else 0) + stirling[blocks - 1]
        stirling = row
    return sum(stirling)


def verify(certificate):
    witness = certificate["exact_tagged_spectator_witness"]
    classification = certificate["partition_and_order_classification"]
    jet = certificate["four_point_positive_jet_factorization"]
    probability = certificate["complete_leading_tagged_probability"]
    atlas = certificate["hard_nonforward_stratified_atlas"]
    incoming = [[Fraction(value) for value in row] for row in witness["incoming_momenta"]]
    outgoing = [[Fraction(value) for value in row] for row in witness["outgoing_momenta"]]
    all_incoming = incoming + [[-value for value in row] for row in outgoing]

    subset_rows = {
        size: [
            (subset, esquare(add(*(all_incoming[index] for index in subset))))
            for subset in combinations(range(6), size)
        ]
        for size in (1, 2, 3)
    }
    zeros = {
        str(size): [list(subset) for subset, value in rows if value == 0]
        for size, rows in subset_rows.items()
    }
    margins = {
        str(size): str(min(value for _, value in rows if value > 0))
        for size, rows in subset_rows.items()
    }

    # Method-distinct jet calculation: expand (2 sum x_i x_j)^2 and select
    # x0*x1*x2*x3 rather than using a complement matrix.
    pairs = list(combinations(range(4), 2))
    derivative_coefficient = sum(
        4
        for left in pairs
        for right in pairs
        if set(left).isdisjoint(right) and set(left) | set(right) == set(range(4))
    )
    born_coefficient = Fraction(derivative_coefficient, 256)

    active_s = square(add(incoming[1], incoming[2]))
    active_t = square(add(incoming[1], [-value for value in outgoing[1]]))
    active_u = square(add(incoming[1], [-value for value in outgoing[2]]))
    inputs = certificate["provenance"]["inputs"]
    boundaries = certificate["does_not_establish"]
    characteristic = load(os.path.join(ROOT, inputs[3]["path"]))

    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "all_input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in inputs),
        "all_predecessor_certificates_pass": all(load(os.path.join(ROOT, row["path"]))["checks"]["ok"] for row in inputs if "/certificates/" in row["path"]),
        "three_incoming_and_outgoing_momenta": len(incoming) == len(outgoing) == 3,
        "all_momenta_are_massless": all(square(row) == 0 for row in incoming + outgoing),
        "total_momentum_is_conserved": add(*incoming) == add(*outgoing) == (Fraction(16, 5), 0, 0, 0),
        "tagged_spectator_is_rederived": incoming[0] == outgoing[0],
        "zero_subsets_are_rederived": zeros == {"1": [], "2": [[0, 3]], "3": []} == witness["zero_subsets"],
        "positive_component_margins_are_rederived": margins == {"1": "2", "2": "32/25", "3": "2"} == witness["minimum_positive_subset_sum_Euclidean_squares"],
        "active_invariants_are_rederived": (active_s, active_t, active_u) == (Fraction(64, 25), Fraction(-32, 25), Fraction(-32, 25)),
        "Bell_number_is_rederived": independent_bell_number(6) == classification["all_set_partitions"] == 203,
        "unique_disconnected_partition_is_recorded": classification["supported_disconnected_partitions"] == [[[0, 3], [1, 2, 4, 5]]],
        "order_two_classification_is_explicit": "unique contribution" in classification["order_two"] and "four-point tree" in classification["order_two"],
        "connected_six_point_boundary_is_explicit": classification["order_four"].startswith("the connected six-point tree and one-loop active four-point corrections begin here"),
        "four_point_derivative_is_independently_24": derivative_coefficient == 24,
        "positive_jet_norm_is_recorded": jet["jet_norm"] == "r4^sharp*r4=24" and "+1" in jet["positive_direction"],
        "Born_coefficient_is_rederived": born_coefficient == Fraction(3, 32) and jet["Born_rate"] == "d_sigma/d_Omega=3*lambda^4/(32*pi^2*s)",
        "fixture_coefficient_is_rederived": born_coefficient / active_s == Fraction(75, 2048) and "75*lambda^4" in jet["fixture_rate"],
        "two_beam_area_normalization_is_imported": characteristic["public_two_particle_reconstruction"]["remainder"] == "1/(Lx*Ly)=1/Area",
        "complete_amplitude_order_is_recorded": probability["amplitude"].startswith("P_Y*(U-I)*P_X=lambda^2"),
        "complete_probability_order_is_recorded": probability["general_coefficient"].startswith("q_click=3*lambda^4"),
        "beam_area_normalization_is_recorded": probability["beam_normalization"] == "the declared BT two-beam characteristic gives probability=cross_section/Area for positive transverse beam area Area",
        "forward_independence_is_preserved": "do not enter" in probability["forward_independence"],
        "two_stratum_scope_is_preserved": atlas["status"] == "TWO_HARD_NONFORWARD_LOCAL_STRATA_COVERED" and atlas["cross_stratum_detector"] == "NOT_CONSTRUCTED",
        "source_dressing_remainder_is_lambda5": "lambda5" in classification["source_dressing_boundary"],
        "Eq19_gravity_and_Lorentzian_boundaries_are_preserved": "the standard scalar projector or general Eq. (19)" in boundaries and "gravity or metric BV/BRST transfer" in boundaries and "anything LORENTZIAN-CAUSAL" in boundaries,
    }
    return {name: bool(value) for name, value in checks.items()}


def main():
    checks = verify(load(CERT))
    failures = [name for name, ok in checks.items() if not ok]
    print("checks %d/%d" % (sum(checks.values()), len(checks)))
    print("RESULT:", "PASS" if not failures else "FAIL")
    if failures:
        print("failures:", ", ".join(failures))
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
