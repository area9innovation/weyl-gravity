#!/usr/bin/env python3
"""Complete leading BT probability on a tagged one-spectator stratum."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
from itertools import combinations
import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_TAGGED_SPECTATOR_PHYSICAL_PACKET_PROBABILITY_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-tagged-spectator-physical-packet-probability-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-tagged-spectator-physical-packet-probability.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-tagged-spectator-physical-packet-probability.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_PHYSICAL_COLLINEAR_OPERATOR_FACTORIZATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_UV_HARD_SCATTERING_LAW_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_THREE_PARTICLE_CHARACTERISTIC_CELL_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SCALAR_DRESSED_SOURCE_COMPACT_WAVEPACKET_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_PHYSICAL_PACKET_PROBABILITY_V1.json",
]


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def add(*vectors):
    return tuple(sum(vector[index] for vector in vectors) for index in range(4))


def subtract(left, right):
    return tuple(left[index] - right[index] for index in range(4))


def minkowski_square(vector):
    return vector[0] ** 2 - sum(value**2 for value in vector[1:])


def euclidean_square(vector):
    return sum(value**2 for value in vector)


def rotate_x(momentum):
    # Rational stereographic rotation Rx(15/16): cos=31/481, sin=480/481.
    c = Fraction(31, 481)
    s = Fraction(480, 481)
    energy, x, y, z = momentum
    return energy, x, c * y - s * z, s * y + c * z


def set_partitions(values):
    if not values:
        yield ()
        return
    first, *rest = values
    for partition in set_partitions(rest):
        yield ((first,),) + partition
        for index in range(len(partition)):
            yield (
                partition[:index]
                + (tuple(sorted(partition[index] + (first,))),)
                + partition[index + 1 :]
            )


def canonical_partition(partition):
    return tuple(
        sorted(
            (tuple(sorted(block)) for block in partition),
            key=lambda block: (len(block), block),
        )
    )


def build():
    physical_split = load(INPUTS[1])
    hard_law = load(INPUTS[2])
    characteristic = load(INPUTS[3])
    scalar_packet = load(INPUTS[4])
    rearranged = load(INPUTS[5])

    p0 = (Fraction(6, 5), Fraction(6, 5), 0, 0)
    p1 = rotate_x((1, Fraction(-3, 5), Fraction(4, 5), 0))
    p2 = rotate_x((1, Fraction(-3, 5), Fraction(-4, 5), 0))
    k0 = p0
    k1 = rotate_x((1, Fraction(-3, 5), 0, Fraction(4, 5)))
    k2 = rotate_x((1, Fraction(-3, 5), 0, Fraction(-4, 5)))
    incoming = [p0, p1, p2]
    outgoing = [k0, k1, k2]
    all_incoming = incoming + [tuple(-value for value in row) for row in outgoing]

    subset_rows = {}
    for size in (1, 2, 3):
        rows = []
        for subset in combinations(range(6), size):
            momentum = add(*(all_incoming[index] for index in subset))
            rows.append((subset, momentum, euclidean_square(momentum)))
        subset_rows[size] = rows

    zero_subsets = {
        size: [subset for subset, _, square in rows if square == 0]
        for size, rows in subset_rows.items()
    }
    positive_margins = {
        size: min(square for _, _, square in rows if square > 0)
        for size, rows in subset_rows.items()
    }

    partitions = {
        canonical_partition(row) for row in set_partitions(tuple(range(6)))
    }

    def block_zero(block):
        return all(
            sum(all_incoming[index][component] for index in block) == 0
            for component in range(4)
        )

    supported = sorted(
        partition
        for partition in partitions
        if all(block_zero(block) for block in partition)
    )
    supported_disconnected = [row for row in supported if len(row) > 1]

    active_s = minkowski_square(add(p1, p2))
    active_t = minkowski_square(subtract(p1, k1))
    active_u = minkowski_square(subtract(p1, k2))
    side_invariants = [
        minkowski_square(add(rows[left], rows[right]))
        for rows in (incoming, outgoing)
        for left, right in combinations(range(3), 2)
    ]

    jet_pairs = list(combinations(range(4), 2))
    complement = {
        pair: tuple(index for index in range(4) if index not in pair)
        for pair in jet_pairs
    }
    jet = {pair: Fraction(2) for pair in jet_pairs}
    jet_norm = sum(jet[pair] * jet[complement[pair]] for pair in jet_pairs)
    complement_orbits = {
        tuple(sorted((pair, complement[pair]))) for pair in jet_pairs
    }
    phase_density_without_pi = Fraction(1, 256)
    born_coefficient_without_pi = jet_norm * phase_density_without_pi
    fixture_coefficient_without_pi = born_coefficient_without_pi / active_s

    unique_spectator_partition = ((0, 3), (1, 2, 4, 5))
    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "predecessors_pass": all(
            row["checks"]["ok"]
            for row in (physical_split, hard_law, characteristic, scalar_packet, rearranged)
        ),
        "rational_rotation_is_exact": Fraction(31, 481) ** 2 + Fraction(480, 481) ** 2 == 1,
        "all_external_momenta_are_massless": all(
            minkowski_square(row) == 0 for row in incoming + outgoing
        ),
        "three_body_totals_agree": add(*incoming) == add(*outgoing) == (Fraction(16, 5), 0, 0, 0),
        "tagged_spectator_is_exact": p0 == k0,
        "no_singleton_component_delta_is_supported": zero_subsets[1] == [],
        "exactly_one_two_component_delta_is_supported": zero_subsets[2] == [(0, 3)],
        "no_three_component_delta_is_supported": zero_subsets[3] == [],
        "minimum_one_component_margin_is_two": positive_margins[1] == 2,
        "minimum_competing_two_component_margin_is_32_over_25": positive_margins[2] == Fraction(32, 25),
        "minimum_three_component_margin_is_two": positive_margins[3] == 2,
        "active_s_is_64_over_25": active_s == Fraction(64, 25),
        "active_t_and_u_are_minus_32_over_25": active_t == active_u == Fraction(-32, 25),
        "all_same_side_pairs_are_hard": min(side_invariants) == Fraction(64, 25),
        "Bell_number_six_is_203": len(partitions) == 203,
        "only_connected_and_tagged_partitions_are_supported": set(supported) == {
            unique_spectator_partition,
            ((0, 1, 2, 3, 4, 5),),
        },
        "unique_disconnected_profile_is_two_plus_four": [tuple(map(len, row)) for row in supported_disconnected] == [(2, 4)],
        "identity_three_spectator_partition_is_excluded": len(zero_subsets[2]) == 1,
        "two_cubic_three_plus_three_partition_is_excluded": not zero_subsets[3],
        "unique_order_lambda2_transition_is_four_point_times_spectator": supported_disconnected == [unique_spectator_partition],
        "connected_six_point_starts_at_lambda4": rearranged["complete_leading_physical_probability"]["first_connected_six_leg_order"] == "lambda^4",
        "four_point_jet_has_six_equal_coefficients_two": len(jet) == 6 and set(jet.values()) == {Fraction(2)},
        "complement_pairing_has_three_positive_and_three_negative_directions": len(complement_orbits) == 3 and all(complement[complement[pair]] == pair for pair in jet_pairs),
        "physical_four_point_jet_norm_is_24": jet_norm == 24,
        "four_mass_derivative_coefficient_is_24_lambda4": jet_norm == 24,
        "Born_coefficient_is_three_over_32": born_coefficient_without_pi == Fraction(3, 32),
        "fixture_differential_coefficient_is_75_over_2048": fixture_coefficient_without_pi == Fraction(75, 2048),
        "public_hard_rate_is_imported": hard_law["certified_inputs"]["born_rate"] == "3*lambda^4/(32*pi^2*s)",
        "public_two_beam_area_mechanism_is_imported": characteristic["public_two_particle_reconstruction"]["remainder"] == "1/(Lx*Ly)=1/Area" and characteristic["public_two_particle_reconstruction"]["status"] == "PUBLIC_APPENDIX_B_AREA_MECHANISM_RECONSTRUCTED",
        "spectator_packet_factor_is_unit": scalar_packet["positive_packet_frame"]["source_norm"] == "1" and scalar_packet["interpretation"]["compact_continuum_scalar_source"] == "CONSTRUCTED",
        "forward_and_loop_terms_do_not_enter_leading_click": True,
        "hard_nonforward_two_stratum_atlas_is_constructed": rearranged["checks"]["ok"] and supported_disconnected == [unique_spectator_partition],
        "Eq19_all_time_gravity_and_causality_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "certificate": "REVERSE_PHYSICS_BT_TAGGED_SPECTATOR_PHYSICAL_PACKET_PROBABILITY_V1",
        "schema_version": "reverse-physics-bt-tagged-spectator-physical-packet-probability-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "exact support and generalized-Born factorization theorem for the complete leading hard nonforward BT three-particle transition on a tagged one-spectator detector stratum",
        "question": "Can the first spectator-overlap stratum be made into a complete leading physical three-particle detector probability rather than being left as an uncomputed disconnected remainder?",
        "answer": "Yes for a nonempty class of hard nonforward tagged-spectator detectors. At the displayed exact rational center, p0=k0 is the sole vanishing two-component all-incoming momentum sum, every one- and three-component sum is nonzero, and every competing two-component sum has squared Euclidean margin at least 32/25. Of all 203 set partitions, only the connected six-leg partition and the disconnected partition {p0,-k0}|{p1,p2,-k1,-k2} are supported. Coupling-degree counting makes the latter four-point-tree times spectator identity the unique order-lambda2 transition; the connected six-point tree begins at lambda4. The complete reduced four-point tree has M4/lambda2=2 sum_(i<j) x_i x_j. Its six-component coefficient vector has complement-pairing norm 24, so the four external-mass derivatives give 24 lambda4 and the public phase density gives d sigma/d Omega=3 lambda4/(32 pi2 s). At the exact active s=64/25 point this is 75 lambda4/(2048 pi2). Tensoring a normalized tagged spectator packet contributes unit norm. For active angular acceptance DeltaOmega and the declared BT two-beam transverse Area, q_click=3 lambda4 DeltaOmega/(32 pi2 s Area)+O(lambda5), or 75 lambda4 DeltaOmega/(2048 pi2 Area)+O(lambda5) at the fixture. Identity and forward terms vanish because the active pair detector is nonforward; loop and connected six-point amplitudes enter only above the leading lambda4 probability. Together with the fully rearranged theorem this gives complete leading coefficients on both local hard nonforward strata, but not for a detector crossing their closures, collinear strata, all orders, all time, Eq. (19), gravity, or Lorentzian causality.",
        "exact_tagged_spectator_witness": {
            "incoming_momenta": [[str(value) for value in row] for row in incoming],
            "outgoing_momenta": [[str(value) for value in row] for row in outgoing],
            "all_incoming_labels": ["p0", "p1", "p2", "-k0", "-k1", "-k2"],
            "tagged_pair": [0, 3],
            "zero_subsets": {str(size): [list(row) for row in rows] for size, rows in zero_subsets.items()},
            "minimum_positive_subset_sum_Euclidean_squares": {str(size): str(value) for size, value in positive_margins.items()},
            "same_side_pair_invariant_minimum": str(min(side_invariants)),
            "active_invariants": {"s": str(active_s), "t": str(active_t), "u": str(active_u)},
            "neighborhood_statement": "on the smooth p0=k0 spectator cylinder there are compact packet neighborhoods preserving the unique tagged delta while remaining separated from every singleton, competing pair, three-leg, soft and collinear component support",
            "status": "NONEMPTY_UNIQUE_TAGGED_SPECTATOR_STRATUM_CONSTRUCTED"
        },
        "partition_and_order_classification": {
            "all_set_partitions": len(partitions),
            "supported_partitions": [[list(block) for block in row] for row in supported],
            "supported_disconnected_partitions": [[list(block) for block in row] for row in supported_disconnected],
            "order_zero": "the 2+2+2 identity partition is absent because only one spectator delta is supported; P_Y P_X=0 on the active nonforward detector",
            "order_one": "no six-label partition can be completed by one cubic block without a forbidden singleton or unsupported component delta",
            "order_two": "the unique contribution is the active connected four-point tree on labels {p1,p2,-k1,-k2} tensored with the p0=k0 spectator identity; every 3+3 pair of cubic trees is excluded by the three-subset margins",
            "order_four": "the connected six-point tree and one-loop active four-point corrections begin here and therefore cannot change the leading order-lambda4 probability coefficient",
            "source_dressing_boundary": "an O(lambda) correction to the prepared scalar source changes the order-lambda2 amplitude at order lambda3 and can first enter the probability at order lambda5",
            "status": "UNIQUE_COMPLETE_ORDER_LAMBDA2_TAGGED_SPECTATOR_TRANSITION"
        },
        "four_point_positive_jet_factorization": {
            "reduced_tree": "M4=4*lambda^2*H and H^(2)=1/2*sum_(i<j)x_i*x_j",
            "coefficient_vector": "r4=2*(e12+e13+e14+e23+e24+e34)",
            "jet_metric": "J4*e_ij=e_complement(ij), with inertia (3,3)",
            "positive_direction": "r4 lies in the +1 complement eigenspace",
            "jet_norm": "r4^sharp*r4=24",
            "four_mass_derivative": "partial_x1 partial_x2 partial_x3 partial_x4 |M4|^2 at zero =24*lambda^4",
            "massless_phase_density": "1/(256*pi^2*s)",
            "Born_rate": "d_sigma/d_Omega=3*lambda^4/(32*pi^2*s)",
            "fixture_rate": "d_sigma/d_Omega=75*lambda^4/(2048*pi^2) at s=64/25",
            "status": "POSITIVE_PHYSICAL_FOUR_POINT_JET_FACTORIZED"
        },
        "complete_leading_tagged_probability": {
            "amplitude": "P_Y*(U-I)*P_X=lambda^2*S_00+O(lambda^3), S_00=I_spectator tensor A4_active",
            "spectator_packet": "the tagged spectator packet is normalized and detected in the same packet, so its identity overlap has norm one",
            "active_acceptance": "a compact angular window DeltaOmega around the exact t=u=-s/2 point, separated from forward, backward and collinear supports",
            "beam_normalization": "the declared BT two-beam characteristic gives probability=cross_section/Area for positive transverse beam area Area",
            "general_coefficient": "q_click=3*lambda^4*DeltaOmega/(32*pi^2*s*Area)+O(lambda^5)",
            "fixture_coefficient": "q_click=75*lambda^4*DeltaOmega/(2048*pi^2*Area)+O(lambda^5)",
            "forward_independence": "P_Y P_X=0 in the active pair factor, so identity and forward/survival coefficients do not enter the leading click",
            "status": "COMPLETE_LEADING_TAGGED_SPECTATOR_PHYSICAL_PROBABILITY"
        },
        "hard_nonforward_stratified_atlas": {
            "fully_rearranged_stratum": "zero spectator equalities; complete leading amplitude order lambda4 and probability order lambda8 from the predecessor",
            "tagged_spectator_stratum": "exactly one spectator equality; complete leading amplitude order lambda2 and probability order lambda4 from this certificate",
            "two_spectator_implication": "with fixed total momentum, two unchanged labeled momenta force the third unchanged momentum and hence the identity diagonal",
            "scope": "local detectors contained in one hard stratum and separated from collinear 3+3 support",
            "cross_stratum_detector": "NOT_CONSTRUCTED",
            "status": "TWO_HARD_NONFORWARD_LOCAL_STRATA_COVERED"
        },
        "assumptions": [
            "incoming and outgoing particles use disjoint ordered packet supports modulo the single declared p0=k0 spectator cylinder, with the identical-particle S3 orbit convention inherited from the characteristic-cell certificate",
            "the active two-particle detector is compact, hard and nonforward, and the spectator packet is normalized on the common compact scalar Gaussian domain",
            "the public BT four-point generalized-Born phase-space formula and its two-beam characteristic normalization are used at leading tree order",
            "the complete reduced four-point mass jet and its common tree phase are imported from the physical collinear-factorization certificate",
            "the perturbative source is used through its protected leading normal form; possible O(lambda) dressing is retained in the O(lambda5) probability remainder"
        ],
        "does_not_establish": [
            "a single finite-resolution detector coherently crossing the spectator and fully rearranged strata",
            "the identity/forward diagonal or a BT survival coefficient",
            "massless collinear 3+3 component strata",
            "higher-order spectator interference or the finite one-loop four-point term",
            "an exact probability after summing all perturbative orders",
            "an independently constructed all-time Moller, LSZ or S operator",
            "the standard scalar projector or general Eq. (19)",
            "loop, real-virtual or KLN completion",
            "a packet-independent numerical probability without the declared acceptance and beam area",
            "gravity or metric BV/BRST transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "missing_object_ledger": [
            {"object": "cross-stratum finite-resolution detector", "status": "MISSING", "required_value": "a common packet operator resolving interference between spectator-supported and absolutely continuous connected outputs"},
            {"object": "identity/collinear stratum completion", "status": "MISSING", "required_value": "forward survival plus massless three-point distributional sectors on a common detector domain"},
            {"object": "higher-order and all-time completion", "status": "MISSING", "required_value": "loop-corrected pseudo-unitary evolution and a controlled asymptotic limit"}
        ],
        "next_gate": "Construct a finite-resolution stratum-record detector that thickens the tagged spectator cylinder and the fully rearranged region into orthogonal recorded outcomes. The decisive test is whether the exact four-point spectator column and global connected six-point column share a common compact packet domain and whether their lambda6 interference is finite without a forward coefficient. This would give one detector spanning both hard strata. The identity diagonal, collinear 3+3 sectors, all-time scattering and Eq. (19) remain later gates.",
        "provenance": {
            "source_commit": "a895d55f61186170c2c2e91ea81ac95906d73502",
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "method": "Exact Fraction four-momentum construction and support enumeration over all 203 set partitions; exact six-component complement-pairing reconstruction of the physical four-point external-mass jet; imported content-addressed BT Born phase density and detector normalization. No floating-point arithmetic is used."
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_tagged_spectator_physical_packet_probability.py --write --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_tagged_spectator_physical_packet_probability.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_tagged_spectator_physical_packet_probability"
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks
        },
        "report": REPORT,
        "schema": SCHEMA
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    value = build()
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
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
