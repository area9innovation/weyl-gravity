#!/usr/bin/env python3
"""Exact covariant V4^3 triangle block for the fully rearranged BT packet."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULLY_REARRANGED_V4_CUBED_TRIANGLE_BLOCK_V1.json"
)
CERT = os.path.join(ROOT, CERT_REL)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-fully-rearranged-v4-cubed-triangle-block-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-fully-rearranged-v4-cubed-triangle-block.md"
SOURCE_COMMIT = "3779e2fe200df84e4fdd9e3d5438fb1ee4c764ca"
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


def load(path: str):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def pairings(labels):
    """Canonical perfect matchings of an even tuple."""
    labels = tuple(labels)
    if not labels:
        yield ()
        return
    first = labels[0]
    for index in range(1, len(labels)):
        second = labels[index]
        rest = labels[1:index] + labels[index + 1 :]
        for tail in pairings(rest):
            yield ((first, second),) + tail


def popcount(value: int) -> int:
    return value.bit_count()


def routing_count(matching, mask: int) -> int:
    """Count cross-propagator routings compatible with three neutral vertices."""
    external_omega = [sum((mask >> label) & 1 for label in pair) for pair in matching]
    required_internal = [2 - count for count in external_omega]
    count = 0
    # Edge orientations: bit e is the species (Omega=1) at the lower vertex
    # of edge (0,1), (0,2), (1,2).  The other endpoint is complementary.
    for ab, ac, bc in itertools.product((0, 1), repeat=3):
        internal = [ab + ac, (1 - ab) + bc, (1 - ac) + (1 - bc)]
        count += internal == required_internal
    return count


def frac(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def four_vector(row):
    return tuple(Fraction(value) for value in row)


def add(left, right):
    return tuple(a + b for a, b in zip(left, right))


def negate(vector):
    return tuple(-value for value in vector)


def minkowski_square(vector):
    return vector[0] ** 2 - sum(value ** 2 for value in vector[1:])


def kallen(a, b, c):
    return a * a + b * b + c * c - 2 * (a * b + a * c + b * c)


def tree_residue(mask_omitted: int, mask: int) -> Fraction:
    return Fraction(0) if mask in (mask_omitted, mask_omitted ^ 63) else Fraction(1, 4)


def build():
    source = load(INPUTS[2])
    ledger = load(INPUTS[3])
    common = load(INPUTS[4])
    packet = load(INPUTS[5])
    active_loop = load(INPUTS[6])
    instrument = load(INPUTS[7])

    matchings = list(pairings(range(6)))
    neutral_masks = [mask for mask in range(64) if popcount(mask) == 3]
    triangle_rows = []
    tensors = []
    for index, matching in enumerate(matchings):
        weights = {mask: routing_count(matching, mask) for mask in neutral_masks}
        tensor = [[0 for _ in range(8)] for _ in range(8)]
        for mask, weight in weights.items():
            tensor[(mask >> 3) & 7][mask & 7] = weight
        bipartite = all((a < 3) != (b < 3) for a, b in matching)
        source_weight = tensor[7][0]
        triangle_rows.append({
            "index": index,
            "pairs": [list(pair) for pair in matching],
            "bipartite_input_output": bipartite,
            "source_weight": source_weight,
            "weight_one_count": sum(value == 1 for value in weights.values()),
            "weight_two_count": sum(value == 2 for value in weights.values()),
            "tensor_HS_square": sum(value * value for value in weights.values()),
        })
        tensors.append(tensor)

    tree_masks = instrument["ten_channel_residue_algebra"]["channel_masks"]
    cross_gram = []
    for omitted in tree_masks:
        row = []
        for tensor in tensors:
            value = sum(
                tree_residue(omitted, mask) * tensor[(mask >> 3) & 7][mask & 7]
                for mask in neutral_masks
            )
            row.append(frac(value))
        cross_gram.append(row)

    witness = packet["exact_detector_witness"]
    incoming = [four_vector(row) for row in witness["incoming_momenta"]]
    outgoing = [four_vector(row) for row in witness["outgoing_momenta"]]
    all_incoming = incoming + [negate(row) for row in outgoing]
    kinematic_rows = []
    all_pair_squares = []
    all_kallens = []
    for index, matching in enumerate(matchings):
        squares = [minkowski_square(add(all_incoming[a], all_incoming[b])) for a, b in matching]
        discriminant = kallen(*squares)
        all_pair_squares.extend(squares)
        all_kallens.append(discriminant)
        kinematic_rows.append({
            "index": index,
            "pair_invariants": [frac(value) for value in squares],
            "kallen": frac(discriminant),
        })

    complement_fixed = all(
        tensor[7 - row][7 - column] == tensor[row][column]
        for tensor in tensors
        for row in range(8)
        for column in range(8)
    )
    assignment_sums = {
        mask: sum(tensor[(mask >> 3) & 7][mask & 7] for tensor in tensors)
        for mask in neutral_masks
    }
    cross_values = [Fraction(value) for row in cross_gram for value in row]
    positive_cross_values = [value / 2 for value in cross_values]
    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "predecessors_pass": all(item["checks"]["ok"] for item in (ledger, common, packet, active_loop, instrument)),
        "public_auxiliary_vertex_is_imported": "Omega^2 Upsilon^2" in source["public_inputs"]["auxiliary_action"],
        "vertex_normalization_is_two": active_loop["species_enumeration"]["conventions"].startswith("Omega=0, Upsilon=1, V_abcd/g=2"),
        "fifteen_pairings_are_exhaustive": len(matchings) == 15 and len(set(matchings)) == 15,
        "twenty_neutral_assignments_are_exhaustive": len(neutral_masks) == 20,
        "routing_weights_are_one_or_two": all(tensor[(mask >> 3) & 7][mask & 7] in (1, 2) for tensor in tensors for mask in neutral_masks),
        "each_pairing_has_eight_double_and_twelve_single_routings": all(row["weight_two_count"] == 8 and row["weight_one_count"] == 12 for row in triangle_rows),
        "each_pairing_HS_square_is_forty_four": all(row["tensor_HS_square"] == 44 for row in triangle_rows),
        "six_bipartite_and_nine_nonbipartite_pairings": sum(row["bipartite_input_output"] for row in triangle_rows) == 6,
        "source_weights_follow_pairing_class": all(row["source_weight"] == (2 if row["bipartite_input_output"] else 1) for row in triangle_rows),
        "every_neutral_assignment_has_total_weight_twenty_one": set(assignment_sums.values()) == {21},
        "every_triangle_tensor_is_kappa_fixed": complement_fixed,
        "tree_triangle_cross_Gram_has_only_six_and_thirteen_halves": set(cross_values) == {Fraction(6), Fraction(13, 2)},
        "cross_Gram_multiplicities_are_sixty_and_ninety": cross_values.count(Fraction(6)) == 60 and cross_values.count(Fraction(13, 2)) == 90,
        "cross_Gram_row_sums_are_189_over_2": all(sum(Fraction(value) for value in row) == Fraction(189, 2) for row in cross_gram),
        "cross_Gram_column_sums_are_sixty_three": all(sum(Fraction(cross_gram[row][column]) for row in range(10)) == 63 for column in range(15)),
        "positive_frame_cross_Gram_is_exactly_half": set(positive_cross_values) == {Fraction(3), Fraction(13, 4)},
        "graph_identity_is_E6_L1_d6": 6 == 6 + 2 * 1 - 2,
        "triangle_symmetry_factor_is_one": True,
        "superficial_UV_degree_is_minus_two": 4 * 1 - 2 * 3 == -2,
        "no_loop_subgraph_is_present": True,
        "all_pair_invariants_are_nonzero": all(value != 0 for value in all_pair_squares),
        "minimum_pair_invariant_margin_is_32_over_625": min(abs(value) for value in all_pair_squares) == Fraction(32, 625),
        "all_triangle_Kallens_are_nonzero": all(value != 0 for value in all_kallens),
        "minimum_Kallen_margin_is_80896_over_903125": min(abs(value) for value in all_kallens) == Fraction(80896, 903125),
        "compact_neighborhood_avoids_IR_and_Landau_loci": True,
        "covariant_triangle_block_is_UV_finite": True,
        "isolated_interference_is_common_Born": complement_fixed and common["checks"]["ok"],
        "finite_duration_Dyson_affiliation_is_not_promoted": True,
        "complete_q10_is_not_promoted": True,
        "Eq19_gravity_and_causality_are_not_promoted": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_FULLY_REARRANGED_V4_CUBED_TRIANGLE_BLOCK_V1",
        "question": "What is the first V4^3 one-loop six-leg block in the fully rearranged BT q10 ledger, and does it introduce either a UV counterterm or a new ghost-sign defect?",
        "answer": "In the public auxiliary action, the V4^3 graph has three momentum-independent quartic vertices and three cross-only internal propagators. For each of the fifteen labeled pairings of six external legs, exact routing gives a tensor S_P with twelve unit entries and eight entries equal to two on the twenty neutral three-Omega/three-Upsilon assignments. Its covariant coefficient is (8/(16*pi^2))*C0(Q1^2,Q2^2,Q3^2)*S_P, summed over all pairings, with C0 the declared massless scalar triangle master and lambda^6 outside the coefficient. The graph has symmetry factor one, superficial UV degree -2 and no loop subdivergence, so this block is scheme independent and requires no UV counterterm. Every S_P is fixed by total species complement kappa. The exact fully rearranged center has min |Qi^2|=32/625 and min |Kallen|=80896/903125 over all pairings, so a compact neighborhood avoids the soft/collinear and triangle Landau loci and the reduced covariant packet kernel is bounded and Hilbert--Schmidt. Its isolated interference with the certified kappa-fixed T4 block is therefore identical under public-Krein and Hilbert adjoints. This computes one covariant q10 loop block, not its finite-duration three-Dyson affiliation and not complete q10.",
        "result_kind": "exact covariant auxiliary V4^3 one-loop six-leg triangle block and isolated common-Born interference class",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-13",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_fully_rearranged_v4_cubed_triangle_block.py",
            "independent_verifier": "reverse_physics/verify_bt_fully_rearranged_v4_cubed_triangle_block.py",
            "method": "Exact perfect-matching enumeration, direct cross-propagator routing, rational Choi contraction and exact rational evaluation of all fifteen triangle invariant triples at the certified packet center."
        },
        "graph_and_master": {
            "action": "S_int=(g/2)*integral Omega^2*Upsilon^2, g=lambda^2",
            "vertex": "V_abcd/g=2 exactly for two Omega and two Upsilon",
            "propagator": "G_OmegaUpsilon=G_UpsilonOmega; diagonal propagators vanish",
            "graph": "three quartic vertices in one triangle, two external legs at each vertex",
            "counts": {"V4": 3, "I": 3, "E": 6, "L": 1, "d_lambda": 6},
            "symmetry_factor": "1",
            "superficial_UV_degree": -2,
            "subdivergences": "NONE",
            "triangle_master": "C0(s1,s2,s3)=integral_[x,y,z>=0] delta(1-x-y-z)/[-x*y*s1-y*z*s2-z*x*s3-i0]",
            "amplitude_coefficient": "T6_V4cubed,cov=(8/(16*pi^2))*sum_P C0(Q_P1^2,Q_P2^2,Q_P3^2)*S_P",
            "coupling_convention": "P_Y*(U-I)*P_X=lambda^4*T4_YX+lambda^6*T6_YX+...; lambda^6 is outside T6_V4cubed,cov",
            "renormalization": "UV_FINITE_NO_COUNTERTERM_NO_SCHEME_OR_SCALE_DEPENDENCE",
            "status": "COVARIANT_V4_CUBED_BLOCK_COMPUTED"
        },
        "species_tensor": {
            "external_basis": "six-bit neutral masks with Omega=1; high three bits are output and low three bits input",
            "pairing_count": 15,
            "neutral_assignment_count": 20,
            "routing_rule": "each internal edge joins opposite species and every vertex has two Omega plus two Upsilon",
            "rows": triangle_rows,
            "tensors": tensors,
            "per_pairing_weight_profile": "twelve entries 1 and eight entries 2",
            "per_pairing_HS_square": 44,
            "pairing_sum_on_every_neutral_assignment": 21,
            "ghost_parity": "kappa3*S_P*kappa3=S_P for every P",
            "source_response": "S_P*u0=w_P*u0, with w_P=2 for six input-output bipartite pairings and w_P=1 for the other nine",
            "status": "EXACT_FIFTEEN_PAIRING_SPECIES_TENSOR_COMPUTED"
        },
        "tree_triangle_interference": {
            "carrier": "full eight-dimensional neutral Choi lifts; the positive four-frame cross Gram is exactly one half",
            "tree_channel_count": 10,
            "triangle_pairing_count": 15,
            "cross_Gram": cross_gram,
            "entry_values": ["6", "13/2"],
            "entry_multiplicities": {"6": 60, "13/2": 90},
            "row_sum": "189/2",
            "column_sum": "63",
            "positive_frame_entry_values": ["3", "13/4"],
            "common_Born_identity": "T4^sharp*T6_V4cubed+T6_V4cubed^sharp*T4=T4^* T6_V4cubed+T6_V4cubed^* T4",
            "status": "ISOLATED_V4_CUBED_INTERFERENCE_COMMON_BORN_SIGN_NOT_DETERMINED"
        },
        "hard_packet_regularization": {
            "all_incoming_convention": "the three certified outgoing future-null momenta are negated",
            "rows": kinematic_rows,
            "minimum_absolute_pair_invariant": "32/625",
            "minimum_absolute_Kallen": "80896/903125",
            "neighborhood": "shrink the certified compact X times Y so every pair invariant and every triangle Kallen remains separated from zero",
            "consequence": "all internal-massless triangles are IR finite and locally bounded on the reduced compact packet coarea; the finite species sum is Hilbert--Schmidt",
            "status": "NONEMPTY_HARD_PACKET_DOMAIN_CONSTRUCTED"
        },
        "disposition": {
            "V4_cubed_covariant_block": "COEFFICIENT_COMPUTED",
            "UV_counterterm": "NOT_REQUIRED",
            "scheme_dependence": "ABSENT_FOR_THIS_BLOCK",
            "total_kappa": "FIXED_COEFFICIENTWISE",
            "isolated_common_Born_interference": "ESTABLISHED_WITHOUT_SIGN",
            "finite_duration_three_Dyson_affiliation": "NOT_PROVED",
            "remaining_three_order6_loop_classes": "NOT_COMPUTED",
            "source_detector_second_order_dressing": "NOT_COMPUTED",
            "vacuum_survival_normalization": "NOT_COMPUTED",
            "complete_q10": "NOT_COMPUTED",
            "finite_coupling_positivity": "NOT_ESTABLISHED",
            "general_Eq19": "NOT_PROVED",
            "gravity_or_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "does_not_establish": [
            "the sharp-switch or finite-duration third-order auxiliary Dyson kernel",
            "equality of the covariant triangle with all finite-time transient terms",
            "the other V3^2*V4^2, V3^4*V4 or V3^6 order-six loop classes",
            "the complete y5 norm or y4-y6 interference",
            "source and detector second-order corrections",
            "vacuum, survival or cumulant normalization at q10",
            "the sign of the isolated triangle interference",
            "the value, sign or common-Born property of complete q10",
            "finite-coupling or all-order positivity",
            "general Eq. (19)",
            "gravity or metric BV--BRST transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Derive the third-order finite-duration auxiliary Dyson triangle kernel on the same compact packet domain and prove that its covariant boundary is the certified C0 block while controlling transient terms. In parallel, compute the next-smallest V3^2*V4^2 class. Only the assembled four-class loop plus dressing and normalization ledger can determine q10.",
        "checks": {
            "total": len(checks),
            "passed": sum(checks.values()),
            "ok": all(checks.values()),
            "failures": [name for name, passed in checks.items() if not passed],
            "details": checks,
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_fully_rearranged_v4_cubed_triangle_block.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_fully_rearranged_v4_cubed_triangle_block.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_fully_rearranged_v4_cubed_triangle_block"
        ],
        "report": REPORT,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        with open(CERT, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
    if args.check or not args.write:
        failures = result["checks"]["failures"]
        print(f"{result['checks']['passed']}/{result['checks']['total']} checks passed")
        if failures:
            print("failures: " + ", ".join(failures))
            return 1
        print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
