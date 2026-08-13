#!/usr/bin/env python3
"""Independent verifier for the fully rearranged BT V4^3 triangle block."""
from __future__ import annotations

from fractions import Fraction
import hashlib
import itertools
import json
import os


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULLY_REARRANGED_V4_CUBED_TRIANGLE_BLOCK_V1.json"
)
INPUTS = [
    "planning/work-items/reverse-physics-bateman-fully-rearranged-v4-cubed-triangle-block.json",
    "planning/events/reverse-physics-bateman-fully-rearranged-v4-cubed-triangle-block-DONE-3779e2fe.json",
    "reverse_physics/data/bateman_turok_hamiltonian_source_v1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_OBJECT_LEDGER_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_COMMON_BORN_PHYSICAL_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_PHYSICAL_PACKET_PROBABILITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_AUXILIARY_ACTIVE_ONE_LOOP_MSBAR_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TEN_CHANNEL_RECORDED_COMPACT_WAVEPACKET_INSTRUMENT_V1.json",
]


def load(path):
    try:
        with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def sha256(path):
    digest = hashlib.sha256()
    try:
        with open(os.path.join(ROOT, path), "rb") as handle:
            for block in iter(lambda: handle.read(65536), b""):
                digest.update(block)
    except OSError:
        return ""
    return digest.hexdigest()


def all_matchings():
    """Generate matchings as a permutation quotient, unlike the producer recursion."""
    result = set()
    for permutation in itertools.permutations(range(6)):
        pairs = tuple(sorted(tuple(sorted(permutation[index:index + 2])) for index in (0, 2, 4)))
        result.add(pairs)
    return sorted(result)


def independent_weight(matching, mask):
    """Enumerate all six internal half-edge species, then impose edge constraints."""
    count = 0
    for half_species in itertools.product((0, 1), repeat=6):
        # Half edges 2v and 2v+1 connect v to the other two vertices.
        if not (
            half_species[0] != half_species[2]
            and half_species[1] != half_species[4]
            and half_species[3] != half_species[5]
        ):
            continue
        valid = True
        for vertex, external_pair in enumerate(matching):
            external = sum((mask >> label) & 1 for label in external_pair)
            internal = half_species[2 * vertex] + half_species[2 * vertex + 1]
            valid &= external + internal == 2
        count += valid
    return count


def vector(row):
    return tuple(Fraction(value) for value in row)


def invariant(left, right):
    total = tuple(a + b for a, b in zip(left, right))
    return total[0] ** 2 - sum(value ** 2 for value in total[1:])


def kallen(row):
    a, b, c = row
    return a * a + b * b + c * c - 2 * (a * b + a * c + b * c)


def verify(certificate):
    checks = {}
    checks["identity"] = certificate.get("certificate") == "REVERSE_PHYSICS_BT_FULLY_REARRANGED_V4_CUBED_TRIANGLE_BLOCK_V1"
    checks["schema"] = certificate.get("schema") == "reverse_physics/schema/reverse-physics-bt-fully-rearranged-v4-cubed-triangle-block-v1.schema.json"
    checks["version"] = certificate.get("schema_version") == 1
    checks["lifecycle"] = certificate.get("lifecycle_state") == "COEFFICIENT_COMPUTED"
    checks["tags"] = certificate.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"]

    provenance = certificate.get("provenance", {})
    recorded_inputs = provenance.get("inputs", [])
    checks["source_commit"] = provenance.get("source_commit") == "3779e2fe200df84e4fdd9e3d5438fb1ee4c764ca"
    checks["input_paths"] = [row.get("path") for row in recorded_inputs] == INPUTS
    checks["input_hashes"] = len(recorded_inputs) == len(INPUTS) and all(
        row.get("sha256") == sha256(path) for row, path in zip(recorded_inputs, INPUTS)
    )
    checks["producer_and_verifier"] = (
        provenance.get("generated_by") == "reverse_physics/bt_fully_rearranged_v4_cubed_triangle_block.py"
        and provenance.get("independent_verifier") == "reverse_physics/verify_bt_fully_rearranged_v4_cubed_triangle_block.py"
    )
    predecessors = [load(path) for path in INPUTS[3:]]
    checks["predecessors"] = all(row.get("checks", {}).get("ok") for row in predecessors)

    matchings = all_matchings()
    neutral = [mask for mask in range(64) if bin(mask).count("1") == 3]
    expected_tensors = []
    expected_rows = []
    for index, matching in enumerate(matchings):
        tensor = [[0] * 8 for _ in range(8)]
        weights = []
        for mask in neutral:
            weight = independent_weight(matching, mask)
            tensor[(mask >> 3) & 7][mask & 7] = weight
            weights.append(weight)
        bipartite = all((a < 3) != (b < 3) for a, b in matching)
        expected_tensors.append(tensor)
        expected_rows.append({
            "index": index,
            "pairs": [list(pair) for pair in matching],
            "bipartite_input_output": bipartite,
            "source_weight": tensor[7][0],
            "weight_one_count": weights.count(1),
            "weight_two_count": weights.count(2),
            "tensor_HS_square": sum(value * value for value in weights),
        })

    species = certificate.get("species_tensor", {})
    checks["matching_count"] = len(matchings) == 15 and species.get("pairing_count") == 15
    checks["neutral_count"] = len(neutral) == 20 and species.get("neutral_assignment_count") == 20
    checks["tensor_rows"] = species.get("rows") == expected_rows
    checks["tensor_entries"] = species.get("tensors") == expected_tensors
    checks["weight_profile"] = all(row["weight_one_count"] == 12 and row["weight_two_count"] == 8 for row in expected_rows)
    checks["HS_square"] = all(row["tensor_HS_square"] == 44 for row in expected_rows)
    checks["source_split"] = sum(row["source_weight"] == 2 for row in expected_rows) == 6 and sum(row["source_weight"] == 1 for row in expected_rows) == 9
    checks["kappa_fixed"] = all(
        tensor[7 - row][7 - column] == tensor[row][column]
        for tensor in expected_tensors for row in range(8) for column in range(8)
    )
    checks["pairing_sum"] = all(
        sum(tensor[(mask >> 3) & 7][mask & 7] for tensor in expected_tensors) == 21
        for mask in neutral
    )

    tree_masks = load(INPUTS[7]).get("ten_channel_residue_algebra", {}).get("channel_masks", [])
    expected_cross = []
    for omitted in tree_masks:
        row = []
        for tensor in expected_tensors:
            value = sum(
                (Fraction(0) if mask in (omitted, omitted ^ 63) else Fraction(1, 4))
                * tensor[(mask >> 3) & 7][mask & 7]
                for mask in neutral
            )
            row.append(str(value))
        expected_cross.append(row)
    interference = certificate.get("tree_triangle_interference", {})
    checks["cross_Gram"] = interference.get("cross_Gram") == expected_cross
    flat_cross = [Fraction(value) for row in expected_cross for value in row]
    checks["cross_design"] = flat_cross.count(6) == 60 and flat_cross.count(Fraction(13, 2)) == 90
    checks["cross_carrier"] = (
        interference.get("carrier") == "full eight-dimensional neutral Choi lifts; the positive four-frame cross Gram is exactly one half"
        and interference.get("positive_frame_entry_values") == ["3", "13/4"]
    )
    checks["common_Born_boundary"] = (
        interference.get("status") == "ISOLATED_V4_CUBED_INTERFERENCE_COMMON_BORN_SIGN_NOT_DETERMINED"
        and "T4^sharp" in interference.get("common_Born_identity", "")
    )

    packet = load(INPUTS[5]).get("exact_detector_witness", {})
    incoming = [vector(row) for row in packet.get("incoming_momenta", [])]
    outgoing = [tuple(-entry for entry in vector(row)) for row in packet.get("outgoing_momenta", [])]
    momenta = incoming + outgoing
    expected_kinematics = []
    invariant_values = []
    discriminants = []
    for index, matching in enumerate(matchings):
        values = [invariant(momenta[a], momenta[b]) for a, b in matching]
        discriminant = kallen(values)
        invariant_values.extend(values)
        discriminants.append(discriminant)
        expected_kinematics.append({
            "index": index,
            "pair_invariants": [str(value) for value in values],
            "kallen": str(discriminant),
        })
    hard = certificate.get("hard_packet_regularization", {})
    checks["kinematic_rows"] = hard.get("rows") == expected_kinematics
    checks["pair_margin"] = min(map(abs, invariant_values)) == Fraction(32, 625) and hard.get("minimum_absolute_pair_invariant") == "32/625"
    checks["Kallen_margin"] = min(map(abs, discriminants)) == Fraction(80896, 903125) and hard.get("minimum_absolute_Kallen") == "80896/903125"

    graph = certificate.get("graph_and_master", {})
    checks["graph_counts"] = graph.get("counts") == {"V4": 3, "I": 3, "E": 6, "L": 1, "d_lambda": 6}
    checks["symmetry_and_degree"] = graph.get("symmetry_factor") == "1" and graph.get("superficial_UV_degree") == -2
    checks["master_and_normalization"] = (
        graph.get("triangle_master") == "C0(s1,s2,s3)=integral_[x,y,z>=0] delta(1-x-y-z)/[-x*y*s1-y*z*s2-z*x*s3-i0]"
        and graph.get("amplitude_coefficient") == "T6_V4cubed,cov=(8/(16*pi^2))*sum_P C0(Q_P1^2,Q_P2^2,Q_P3^2)*S_P"
    )
    checks["renormalization"] = graph.get("renormalization") == "UV_FINITE_NO_COUNTERTERM_NO_SCHEME_OR_SCALE_DEPENDENCE"

    disposition = certificate.get("disposition", {})
    checks["not_complete_q10"] = disposition.get("complete_q10") == "NOT_COMPUTED"
    checks["not_Dyson"] = disposition.get("finite_duration_three_Dyson_affiliation") == "NOT_PROVED"
    checks["not_promoted"] = (
        disposition.get("finite_coupling_positivity") == "NOT_ESTABLISHED"
        and disposition.get("general_Eq19") == "NOT_PROVED"
        and disposition.get("Lorentzian_causal_claim") == "NOT_ESTABLISHED"
    )
    checks["boundaries"] = len(certificate.get("does_not_establish", [])) == 13
    checks["next_gate"] = all(term in certificate.get("next_gate", "") for term in ("third-order", "finite-duration", "V3^2*V4^2", "q10"))
    checks["report"] = certificate.get("report") == "reverse_physics/reports/bt-fully-rearranged-v4-cubed-triangle-block.md"
    return checks


def main():
    checks = verify(load(CERT_REL))
    failures = [name for name, passed in checks.items() if not passed]
    print(f"{len(checks) - len(failures)}/{len(checks)} checks passed")
    if failures:
        print("failures: " + ", ".join(failures))
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
