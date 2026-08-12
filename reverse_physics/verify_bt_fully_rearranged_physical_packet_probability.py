#!/usr/bin/env python3
"""Independent verifier for the fully rearranged BT packet probability."""
from __future__ import annotations

from fractions import Fraction
import hashlib
from itertools import combinations
import json
import os
import sys

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_PHYSICAL_PACKET_PROBABILITY_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-fully-rearranged-physical-packet-probability-v1.schema.json")


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
    return vector[0] ** 2 - sum(value ** 2 for value in vector[1:])


def add(left, right):
    return tuple(left[index] + right[index] for index in range(4))


def independent_partition_counts(n):
    # Stirling recurrence S(n,k)=k*S(n-1,k)+S(n-1,k-1).
    row = [1]
    for size in range(1, n + 1):
        new = [0] * (size + 1)
        for blocks in range(1, size + 1):
            new[blocks] = blocks * (row[blocks] if blocks < len(row) else 0) + row[blocks - 1]
        row = new
    return row


def integer_partition_profiles(total, minimum=1):
    if total == 0:
        return {()}
    rows = set()
    for first in range(minimum, total + 1):
        for rest in integer_partition_profiles(total - first, first):
            rows.add((first,) + rest)
    return rows


def verify(certificate):
    inputs = certificate["provenance"]["inputs"]
    witness = certificate["exact_detector_witness"]
    support = certificate["disconnected_support_classification"]
    probability = certificate["complete_leading_physical_probability"]
    interpretation = certificate["interpretation"]
    boundaries = certificate["does_not_establish"]
    incoming = [[Fraction(value) for value in row] for row in witness["incoming_momenta"]]
    outgoing = [[Fraction(value) for value in row] for row in witness["outgoing_momenta"]]
    pair_invariants = [square(add(rows[i], rows[j])) for rows in (incoming, outgoing) for i in range(3) for j in range(i + 1, 3)]
    distances = [sum((left[index] - right[index]) ** 2 for index in range(4)) for left in incoming for right in outgoing]
    all_incoming = incoming + [[-value for value in row] for row in outgoing]
    component_margins = {
        size: min(
            sum(sum(all_incoming[index][component] for index in subset) ** 2 for component in range(4))
            for subset in combinations(range(6), size)
        )
        for size in (1, 2, 3)
    }
    stirling = independent_partition_counts(6)
    profiles = integer_partition_profiles(6) - {(6,)}
    recorded_profiles = {tuple(row) for row in support["size_profiles"]}
    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "all_input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in inputs),
        "all_predecessor_certificates_pass": all(load(os.path.join(ROOT, row["path"]))["checks"]["ok"] for row in inputs if "/certificates/" in row["path"]),
        "three_incoming_and_three_outgoing_momenta": len(incoming) == len(outgoing) == 3,
        "all_momenta_are_independently_massless": all(square(row) == 0 for row in incoming + outgoing),
        "both_totals_are_independently_conserved": [sum(row[index] for row in incoming) for index in range(4)] == [Fraction(16, 5), 0, 0, 0] == [sum(row[index] for row in outgoing) for index in range(4)],
        "minimum_energy_is_rederived": min(row[0] for row in incoming + outgoing) == 1 and witness["minimum_external_energy"] == "1",
        "same_side_collinear_margin_is_rederived": min(pair_invariants) == Fraction(64, 25) and witness["minimum_same_side_pair_invariant"] == "64/25",
        "nine_spectator_separations_are_rederived": len(distances) == 9 and all(value > 0 for value in distances),
        "minimum_spectator_separation_is_rederived": min(distances) == Fraction(32, 625) and witness["minimum_cross_Euclidean_distance_squared"] == "32/625",
        "all_small_component_margins_are_rederived": component_margins == {1: Fraction(2), 2: Fraction(32, 625), 3: Fraction(17794, 10625)} and witness["minimum_component_momentum_sum_Euclidean_squares"] == {"1": "2", "2": "32/625", "3": "17794/10625"},
        "Bell_number_is_rederived_from_Stirling_recurrence": sum(stirling) == 203 and support["all_set_partitions"] == 203,
        "disconnected_partition_count_is_rederived": sum(stirling[2:]) == 202 and support["disconnected_set_partitions"] == 202,
        "ten_size_profiles_are_independently_rederived": profiles == recorded_profiles and len(profiles) == 10,
        "every_profile_has_a_small_component": all(min(row) <= 3 for row in profiles),
        "every_disconnected_profile_is_separated_by_a_component_delta": all(component_margins[min(row)] > 0 for row in profiles),
        "support_types_cover_every_profile": {tuple(row["profile"]) for row in support["profile_support_types"]} == profiles,
        "support_derivative_lemma_is_explicit": support["derivative_lemma"].startswith("support(partial^alpha T) is contained"),
        "vacuum_component_ledger_is_explicit": "positive coupling degree" in support["vacuum_component_ledger"] and "killed by P_Y P_X=0" in support["vacuum_component_ledger"] and "above lambda4" in support["vacuum_component_ledger"],
        "all_disconnected_pairings_are_zero": support["detector_pairing"] == "ZERO_FOR_EVERY_DISCONNECTED_PARTITION_THROUGH_ORDER_LAMBDA4",
        "orthogonal_input_output_support_is_explicit": probability["input_output_orthogonality"] == "P_out*P_in=0 on the separated packet supports",
        "leading_amplitude_order_is_explicit": probability["first_connected_six_leg_order"] == "lambda^4" and probability["restricted_connected_column"] == "A_YX=P_Y*A_full*P_X" and probability["complete_leading_amplitude"].startswith("P_Y*(U_T-I)*P_X=lambda^4*A_YX"),
        "leading_probability_order_is_explicit": probability["leading_click"].startswith("q_click=lambda^8"),
        "declared_scalar_coefficient_is_imported": probability["declared_scalar_coefficient"] == "q_click=16*lambda^8*||sum_(B=1)^9 P_Y*K_B,T*P_X F||^2",
        "global_bound_is_imported": probability["global_bound"] == "q_click<=81*lambda^8*T^2/(200*pi^6)",
        "forward_independence_is_preserved": interpretation["leading_forward_graph_needed_for_click"] == "NO" and "do not enter" in probability["forward_independence"],
        "selected_scope_is_preserved": any("detectors intersecting spectator or collinear supports" in row for row in boundaries) and interpretation["all_order_probability"] == "NOT_CONSTRUCTED",
        "Eq19_gravity_and_Lorentzian_boundaries_are_preserved": interpretation["general_Eq19"] == "NOT_PROVED" and "gravity or metric BV/BRST transfer" in boundaries and "anything LORENTZIAN-CAUSAL" in boundaries,
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
