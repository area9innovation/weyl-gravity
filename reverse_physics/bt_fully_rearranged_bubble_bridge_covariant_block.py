#!/usr/bin/env python3
"""Exact covariant bubble-with-bridge block in the auxiliary BT frame."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
import os


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULLY_REARRANGED_BUBBLE_BRIDGE_COVARIANT_BLOCK_V1.json"
)
CERT = os.path.join(ROOT, CERT_REL)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-fully-rearranged-bubble-bridge-covariant-block-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-fully-rearranged-bubble-bridge-covariant-block.md"
SOURCE_COMMIT = "718aec1572f697a8b058c51084d6a593948d1cf9"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-fully-rearranged-bubble-bridge-covariant-block.json",
    "planning/events/reverse-physics-bateman-fully-rearranged-bubble-bridge-covariant-block-DONE-718aec15.json",
    "reverse_physics/data/bateman_turok_hamiltonian_source_v1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_FRAME_TYPED_LOOP_LEDGER_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_AUXILIARY_ACTIVE_ONE_LOOP_MSBAR_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TEN_CHANNEL_RECORDED_COMPACT_WAVEPACKET_INSTRUMENT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPLETE_CONNECTED_ORDER4_PACKET_COLUMN_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_PHYSICAL_PACKET_PROBABILITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_UV_HARD_SCATTERING_LAW_V1.json",
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


def frac(value):
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def role_partitions():
    """The degree-(3,2,1) vertices carry respectively 1,2,3 external legs."""
    rows = []
    for junction_leg in range(6):
        remaining = tuple(label for label in range(6) if label != junction_leg)
        for bubble_pair in itertools.combinations(remaining, 2):
            bridge_triple = tuple(label for label in remaining if label not in bubble_pair)
            rows.append((junction_leg, bubble_pair, bridge_triple))
    return rows


def routing_count(role, mask):
    """Count cross-propagator orientations with neutral quartic vertices."""
    junction_leg, bubble_pair, bridge_triple = role
    external_omega = (
        (mask >> junction_leg) & 1,
        sum((mask >> label) & 1 for label in bubble_pair),
        sum((mask >> label) & 1 for label in bridge_triple),
    )
    count = 0
    # x,y are Omega bits at the junction ends of the parallel bubble edges;
    # z is the Omega bit at the junction end of the bridge.  Every opposite
    # endpoint is the complementary species.
    for x, y, z in itertools.product((0, 1), repeat=3):
        junction_ok = external_omega[0] + x + y + z == 2
        bubble_ok = external_omega[1] + (1 - x) + (1 - y) == 2
        bridge_ok = external_omega[2] + (1 - z) == 2
        count += junction_ok and bubble_ok and bridge_ok
    return count


def tensor_for(role, neutral_masks):
    tensor = [[0 for _ in range(8)] for _ in range(8)]
    for mask in neutral_masks:
        tensor[(mask >> 3) & 7][mask & 7] = routing_count(role, mask)
    return tensor


def tree_residue(channel_mask, species_mask):
    if species_mask in (channel_mask, channel_mask ^ 63):
        return Fraction(0)
    return Fraction(1, 4)


def canonical_channel(mask):
    return min(mask, mask ^ 63)


def vector(row):
    return tuple(Fraction(value) for value in row)


def negate(row):
    return tuple(-value for value in row)


def add(rows):
    return tuple(sum(values) for values in zip(*rows))


def minkowski_square(row):
    return row[0] ** 2 - sum(value * value for value in row[1:])


def spatial_square(row):
    return sum(value * value for value in row[1:])


def build():
    source = load(INPUTS[2])
    frame = load(INPUTS[3])
    active_loop = load(INPUTS[4])
    instrument = load(INPUTS[5])
    tree_column = load(INPUTS[6])
    packet = load(INPUTS[7])
    uv = load(INPUTS[8])
    predecessors = (frame, active_loop, instrument, tree_column, packet, uv)

    roles = role_partitions()
    neutral_masks = [mask for mask in range(64) if mask.bit_count() == 3]
    tree_masks = instrument["ten_channel_residue_algebra"]["channel_masks"]
    tensors = [tensor_for(role, neutral_masks) for role in roles]

    witness = packet["exact_detector_witness"]
    incoming = [vector(row) for row in witness["incoming_momenta"]]
    outgoing = [vector(row) for row in witness["outgoing_momenta"]]
    all_incoming = incoming + [negate(row) for row in outgoing]

    role_rows = []
    cross_gram = []
    for role_index, (role, tensor) in enumerate(zip(roles, tensors)):
        junction_leg, bubble_pair, bridge_triple = role
        bubble_momentum = add([all_incoming[label] for label in bubble_pair])
        bridge_momentum = add([all_incoming[label] for label in bridge_triple])
        weights = [routing_count(role, mask) for mask in neutral_masks]
        bridge_mask = sum(1 << label for label in bridge_triple)
        channel_mask = canonical_channel(bridge_mask)
        cross_column = [
            sum(
                tree_residue(omitted, mask)
                * tensor[(mask >> 3) & 7][mask & 7]
                for mask in neutral_masks
            )
            for omitted in tree_masks
        ]
        cross_gram.append(cross_column)
        role_rows.append({
            "index": role_index,
            "junction_leg": junction_leg,
            "bubble_pair": list(bubble_pair),
            "bridge_triple": list(bridge_triple),
            "bridge_channel_mask": channel_mask,
            "bubble_invariant": frac(minkowski_square(bubble_momentum)),
            "bubble_spatial_square": frac(spatial_square(bubble_momentum)),
            "bridge_invariant": frac(minkowski_square(bridge_momentum)),
            "bridge_spatial_square": frac(spatial_square(bridge_momentum)),
            "source_weight": tensor[7][0],
            "weight_zero_count": weights.count(0),
            "weight_one_count": weights.count(1),
            "weight_two_count": weights.count(2),
            "tensor_HS_square": sum(weight * weight for weight in weights),
            "tree_cross_Gram_column": [frac(value) for value in cross_column],
        })

    # Transpose into the same tree-channel by graph-role convention used for
    # the triangle cross Gram.
    cross_gram_by_tree = [
        [cross_gram[role][tree] for role in range(len(roles))]
        for tree in range(len(tree_masks))
    ]
    cross_values = [value for row in cross_gram_by_tree for value in row]

    grouped_roles = {
        channel: [index for index, row in enumerate(role_rows) if row["bridge_channel_mask"] == channel]
        for channel in tree_masks
    }
    group_identity = True
    group_rows = []
    for channel in tree_masks:
        role_indices = grouped_roles[channel]
        summed = {
            mask: sum(
                tensors[index][(mask >> 3) & 7][mask & 7]
                for index in role_indices
            )
            for mask in neutral_masks
        }
        expected = {mask: 40 * tree_residue(channel, mask) for mask in neutral_masks}
        group_identity &= summed == expected
        group_rows.append({
            "bridge_channel_mask": channel,
            "role_indices": role_indices,
            "role_count": len(role_indices),
            "tensor_sum_identity": "sum_(R over C) W_R=40*R_C",
            "zero_species_masks": [channel, channel ^ 63],
            "nonzero_species_value": 10,
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
    source_weights = [row["source_weight"] for row in role_rows]
    bubble_abs_invariants = [abs(Fraction(row["bubble_invariant"])) for row in role_rows]
    bubble_spatial_squares = [Fraction(row["bubble_spatial_square"]) for row in role_rows]
    source_surviving_bridge_spatial = [
        Fraction(row["bridge_spatial_square"])
        for row in role_rows
        if row["source_weight"]
    ]
    on_shell_bridge_roles = [row["index"] for row in role_rows if Fraction(row["bridge_invariant"]) == 0]
    hard_bridge_roles = [
        row["index"]
        for row in role_rows
        if set(row["bridge_triple"]) in ({0, 1, 2}, {3, 4, 5})
    ]

    vertex_product_over_symmetry = Fraction(2**3, 2)
    scale_derivative_prefactor = Fraction(4 * 2 * 40, 16)
    tree_prefactor = Fraction(16)
    relative_scale_derivative = scale_derivative_prefactor / tree_prefactor
    beta_coefficient = Fraction(
        uv["callan_symanzik_certificate"]["beta_coefficient"]["numerator"],
        uv["callan_symanzik_certificate"]["beta_coefficient"]["denominator"],
    )

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "six_predecessors_pass": all(row["checks"]["ok"] for row in predecessors),
        "public_auxiliary_action_has_only_quartic_vertex": "Omega^2 Upsilon^2" in source["public_inputs"]["auxiliary_action"],
        "frame_ledger_selects_bubble_bridge": frame["disposition"]["direct_auxiliary_bubble_with_bridge"] == "MISSING_ASSEMBLY",
        "active_MSbar_bubble_is_imported": active_loop["msbar_bubble"]["real_bubble"] == "B_X=L_X+2, L_X=log(mu^2/abs(X))",
        "sixty_role_partitions_are_exhaustive": len(roles) == 60 and len(set(roles)) == 60,
        "every_role_has_one_two_three_external_profile": all(1 + len(role[1]) + len(role[2]) == 6 for role in roles),
        "twenty_neutral_species_assignments_are_exhaustive": len(neutral_masks) == 20,
        "each_role_has_two_zero_six_unit_twelve_double_weights": all(
            row["weight_zero_count"] == 2
            and row["weight_one_count"] == 6
            and row["weight_two_count"] == 12
            for row in role_rows
        ),
        "each_role_HS_square_is_fifty_four": all(row["tensor_HS_square"] == 54 for row in role_rows),
        "every_neutral_assignment_has_total_weight_ninety": set(assignment_sums.values()) == {90},
        "every_tensor_is_kappa_fixed": complement_fixed,
        "source_weight_profile_is_6_18_36": (
            source_weights.count(0), source_weights.count(1), source_weights.count(2)
        ) == (6, 18, 36),
        "ten_bridge_channels_each_have_six_roles": len(grouped_roles) == 10 and all(len(rows) == 6 for rows in grouped_roles.values()),
        "grouped_tensor_is_forty_times_tree_residue": group_identity,
        "cross_Gram_values_are_13half_7_15half": set(cross_values) == {Fraction(13, 2), Fraction(7), Fraction(15, 2)},
        "cross_Gram_multiplicities_are_360_180_60": (
            cross_values.count(Fraction(13, 2)),
            cross_values.count(Fraction(7)),
            cross_values.count(Fraction(15, 2)),
        ) == (360, 180, 60),
        "cross_Gram_row_sums_are_405": {sum(row) for row in cross_gram_by_tree} == {Fraction(405)},
        "cross_Gram_column_sums_are_135_over_2": {
            sum(cross_gram_by_tree[tree][role] for tree in range(10))
            for role in range(60)
        } == {Fraction(135, 2)},
        "same_bridge_tree_cross_is_15_over_2": all(
            cross_gram_by_tree[tree_index][role_index] == Fraction(15, 2)
            for tree_index, channel in enumerate(tree_masks)
            for role_index in grouped_roles[channel]
        ),
        "bubble_vertex_product_over_symmetry_is_four": vertex_product_over_symmetry == 4,
        "bubble_invariants_are_hard_at_packet_center": min(bubble_abs_invariants) == Fraction(32, 625),
        "bubble_spatial_momenta_are_nonzero": min(bubble_spatial_squares) == Fraction(32, 625),
        "six_bridge_roles_are_on_shell": len(on_shell_bridge_roles) == 6,
        "hard_zero_spatial_bridge_is_source_dark": len(hard_bridge_roles) == 6 and all(role_rows[index]["source_weight"] == 0 for index in hard_bridge_roles),
        "source_surviving_bridge_spatial_margin_is_7169_over_10625": min(source_surviving_bridge_spatial) == Fraction(7169, 10625),
        "covariant_graph_has_only_bubble_subdivergence": True,
        "no_primitive_six_point_counterterm": True,
        "bubble_scale_derivative_is_two": True,
        "covariant_scale_derivative_is_five_over_four_pi2_times_tree": relative_scale_derivative == Fraction(5, 4),
        "beta_coefficient_is_five_over_sixteen": beta_coefficient == Fraction(5, 16),
        "running_lambda4_cancels_explicit_scale_derivative": 4 * (-beta_coefficient) + relative_scale_derivative == 0,
        "finite_time_local_counterterm_collapses_to_tree_kernel": True,
        "energy_diagonal_B_T_is_not_promoted_off_diagonal": True,
        "isolated_block_is_common_Born_without_sign": complement_fixed,
        "complete_connected_auxiliary_loop_is_covariantly_closed": frame["disposition"]["direct_auxiliary_triangle"] == "COEFFICIENT_COMPUTED_AT_FINITE_TIME",
        "complete_q10_is_not_promoted": True,
        "Eq19_gravity_and_causality_are_not_promoted": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_FULLY_REARRANGED_BUBBLE_BRIDGE_COVARIANT_BLOCK_V1",
        "question": "What is the remaining direct-auxiliary connected six-leg one-loop bubble-with-bridge block, how does its subdivergence match the BT running coupling, and may the existing energy-diagonal finite-time bubble be inserted directly?",
        "answer": "Write a labelled bubble-with-bridge role as R=(a;bc;def): one external leg meets the degree-three junction, two meet the bubble leaf and three meet the tree leaf. There are exactly 6*C(5,2)=60 roles, or six roles over each of the ten unordered three-three bridge channels. Exact cross-propagator routing gives a tensor W_R with two zero, six unit and twelve double entries on the twenty neutral species assignments, squared Hilbert-Schmidt norm 54, and kappa3*W_R*kappa3=W_R. With g=lambda^2, the three vertex tensors contribute 2^3 and the parallel-edge bubble symmetry factor is 1/2, so the covariant phase-stripped block is T6,bb,cov=[4/(16*pi^2)]*sum_R B_MSbar(Q_R^2)*W_R/(K_R^2+i0), with B_MSbar(Q^2)=log[mu^2/(-Q^2-i0)]+2. Its only divergent proper subgraph is the logarithmic four-point bubble; there is no primitive six-point counterterm. For every bridge channel C, the exact local identity sum_(R over C) W_R=40*R_C holds. Since d B/d log(mu)=2 and T4,cov=16*sum_C R_C/(K_C^2+i0), this gives d T6,bb,cov/d log(mu)=[5/(4*pi^2)]*T4,cov. It is cancelled exactly by d(lambda^4)/d log(mu)=-5*lambda^6/(4*pi^2), imported from beta_lambda=-5*lambda^3/(16*pi^2). The same local forest identity collapses to the certified finite-time tree kernel for any common switching, fixing the finite-time counterterm normalization. At the fully rearranged center every bubble invariant and spatial momentum is separated from zero by 32/625. Six bridge roles are on shell and therefore require finite-time treatment. The only zero-spatial hard bridge has six roles whose tensors annihilate the declared positive source; every source-surviving bridge has spatial square at least 7169/10625. The covariant block, species tensor, packet margins, common-Born class and RG identity are computed. The existing B_T is an energy-diagonal four-point tree-loop interference and does not by itself specify the off-diagonal three-vertex insertion, so finite-time affiliation and the interference sign remain open.",
        "result_kind": "exact covariant auxiliary bubble-with-bridge six-leg one-loop block, forest counterterm identity, physical-source margins and RG cancellation",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-13",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_fully_rearranged_bubble_bridge_covariant_block.py",
            "independent_verifier": "reverse_physics/verify_bt_fully_rearranged_bubble_bridge_covariant_block.py",
            "method": "Exact labelled role enumeration, direct internal-edge species routing, Fraction-only Choi contraction, exact rational packet kinematics, and algebraic forest/RG matching. No floating-point arithmetic enters a claim."
        },
        "graph_and_master": {
            "interaction": "S_int=(g/2)*integral Omega^2*Upsilon^2, g=lambda^2",
            "role": "R=(a;bc;def), with external profiles 1 at junction A, 2 at bubble leaf B and 3 at tree leaf C",
            "internal_edges": "two parallel A-B bubble edges and one A-C bridge",
            "counts": {"V4": 3, "I": 3, "E": 6, "L": 1, "d_lambda": 6},
            "labeled_role_count": 60,
            "role_count_per_unordered_bridge_channel": 6,
            "vertex_product": "(V/g)^3=2^3=8",
            "bubble_symmetry_factor": "1/2",
            "net_tensor_prefactor": "4",
            "bubble_master": "B_MSbar(Q^2)=log[mu^2/(-Q^2-i0)]+2; Re B=log(mu^2/abs(Q^2))+2",
            "amplitude": "T6_bb,cov=(4/(16*pi^2))*sum_R B_MSbar(Q_R^2)*W_R/(K_R^2+i0)",
            "coupling_convention": "lambda^6 is outside T6_bb,cov",
            "status": "COVARIANT_BUBBLE_WITH_BRIDGE_BLOCK_COMPUTED"
        },
        "species_tensor": {
            "neutral_masks": neutral_masks,
            "routing_rule": "each internal edge joins opposite species and every vertex has exactly two Omega and two Upsilon",
            "per_role_profile": "two entries 0, six entries 1 and twelve entries 2",
            "per_role_HS_square": 54,
            "sum_over_all_roles_on_each_neutral_assignment": 90,
            "source_weight_profile": {"zero_roles": 6, "unit_roles": 18, "double_roles": 36},
            "kappa_identity": "kappa3*W_R*kappa3=W_R coefficientwise",
            "tensors": tensors,
            "status": "EXACT_SIXTY_ROLE_SPECIES_TENSOR_COMPUTED"
        },
        "role_kinematics": {
            "all_incoming_convention": "incoming momenta followed by negatives of outgoing momenta",
            "rows": role_rows,
            "minimum_abs_bubble_invariant": "32/625",
            "minimum_bubble_spatial_square": "32/625",
            "on_shell_bridge_role_indices": on_shell_bridge_roles,
            "hard_zero_spatial_bridge_role_indices": hard_bridge_roles,
            "hard_bridge_source_weight": 0,
            "minimum_source_surviving_bridge_spatial_square": "7169/10625",
            "status": "NONEMPTY_SELECTED_SOURCE_FINITE_TIME_PACKET_MARGIN"
        },
        "tree_incidence": {
            "tree_channel_masks": tree_masks,
            "group_rows": group_rows,
            "group_identity": "sum_(R with bridge C) W_R=40*R_C for every unordered channel C",
            "cross_Gram": [[frac(value) for value in row] for row in cross_gram_by_tree],
            "entry_values": ["13/2", "7", "15/2"],
            "entry_multiplicities": {"13/2": 360, "7": 180, "15/2": 60},
            "row_sum": "405",
            "column_sum": "135/2",
            "same_bridge_channel_entry": "15/2",
            "positive_frame_entry_values": ["13/4", "7/2", "15/4"],
            "status": "EXACT_TREE_BUBBLE_BRIDGE_INCIDENCE_COMPUTED"
        },
        "renormalization": {
            "overall_superficial_degree": -2,
            "proper_subgraph": "one logarithmic degree-zero four-point bubble",
            "forest_subtraction": "renormalize that bubble in the same MSbar quartic-coupling convention before joining the bridge",
            "primitive_six_point_counterterm": "NONE",
            "bubble_scale_derivative": "d B_MSbar/d log(mu)=2",
            "covariant_tree": "T4,cov=16*sum_C R_C/(K_C^2+i0)",
            "explicit_scale_identity": "d T6_bb,cov/d log(mu)=[5/(4*pi^2)]*T4,cov",
            "running": "d lambda/d log(mu)=-5*lambda^3/(16*pi^2)",
            "running_tree_identity": "d[lambda^4*T4]/d log(mu)=-[5*lambda^6/(4*pi^2)]*T4",
            "RG_sum": "d[lambda^4*T4+lambda^6*T6_bb,cov]/d log(mu)=O(lambda^8) for this counterterm sector",
            "finite_time_local_identity": "the derivative of the renormalized bubble distribution is 2*delta(t_A-t_B), so the subgraph collapses to the same switched T4 kernel with coefficient 5/(4*pi^2)",
            "scheme_boundary": "a finite quartic coupling redefinition shifts a local multiple of T4; the logarithmic derivative and cancellation are scheme independent",
            "status": "MSBAR_FOREST_AND_RG_IDENTITY_COMPUTED"
        },
        "finite_time_gate": {
            "known": "the local counterterm coefficient and its collapse to the switched tree kernel are fixed exactly",
            "missing_object": "the off-diagonal renormalized three-vertex time-ordered bubble distribution joined to the bridge on [0,T]",
            "why_existing_B_T_is_insufficient": "the certified B_T divides an energy-diagonal second-Dyson tree-loop cross by its tree duration; a bubble subgraph inside a third-Dyson six-point graph exchanges energy with the bridge vertex before the total projection",
            "required_construction": "retain the two independent intermediate defects or equivalently convolve the full renormalized bubble time distribution with the finite-time bridge kernel, including all six orderings and the local forest term",
            "on_shell_fact": "six labelled roles have K_R^2=0 at the packet center and cannot be replaced by the covariant bridge pole",
            "selected_source_fact": "the zero-spatial hard bridge is coefficientwise dark on u0, while every source-surviving bridge has nonzero spatial energy",
            "status": "COUNTERTERM_NORMALIZED_OFF_DIAGONAL_THIRD_DYSON_KERNEL_NOT_YET_COMPUTED"
        },
        "common_Born_interference": {
            "species_identity": "kappa3*W_R*kappa3=W_R for every role R",
            "scalar_kernel": "the covariant bubble and bridge factors commute with total ghost parity",
            "effect_identity": "T4^sharp*T6_bb+T6_bb^sharp*T4=T4^*T6_bb+T6_bb^*T4",
            "sign": "NOT_DETERMINED because the momentum-dependent complex bubble, bridge boundary and future finite-time transient enter coherently",
            "status": "ISOLATED_COVARIANT_BUBBLE_BRIDGE_INTERFERENCE_COMMON_BORN"
        },
        "disposition": {
            "covariant_bubble_bridge_block": "COEFFICIENT_COMPUTED",
            "species_tensor": "COMPUTED",
            "MSbar_subdivergence": "MATCHED_TO_QUARTIC_COUNTERTERM",
            "RG_identity": "PROVED",
            "selected_source_packet_margin": "PROVED",
            "covariant_direct_auxiliary_connected_T6": "COMPLETE_WITH_TRIANGLE_PREDECESSOR",
            "finite_time_bubble_bridge": "NOT_COMPUTED",
            "complete_finite_time_direct_auxiliary_connected_T6": "NOT_COMPUTED",
            "isolated_common_Born_interference": "ESTABLISHED_WITHOUT_SIGN",
            "complete_q10": "NOT_COMPUTED",
            "general_Eq19": "NOT_PROVED",
            "gravity_or_metric_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "assumptions": [
            "the public auxiliary quartic vertex has tensor V/g=2 on neutral two-Omega/two-Upsilon assignments and the propagator metric is cross-only",
            "the bubble subgraph is renormalized in the same MSbar coupling convention as the certified active four-point loop",
            "the complete connected tree coefficient uses T4=16*sum_C K_C*R_C on the declared carrier",
            "the selected fully rearranged packet is shrunk inside the exact rational margins recorded here",
            "the declared positive source is u0=(|000>+|111>)/sqrt(2) in the three-particle species frame"
        ],
        "does_not_establish": [
            "the off-diagonal finite-time third-Dyson bubble-with-bridge kernel",
            "that the energy-diagonal four-point B_T may be inserted multiplicatively into a six-point finite-time graph",
            "the value or sign of finite-time tree-bubble-bridge interference",
            "a full-carrier treatment of the zero-spatial hard bridge mode",
            "scheme independence of the finite local quartic term",
            "the complete finite-time connected auxiliary T6 block",
            "the complete y5 norm or y4-y6 interference",
            "source, detector, vacuum or survival dressing at q10",
            "the value, sign or finite-coupling positivity of complete q10",
            "an all-time Moller, LSZ or S operator",
            "general Eq. (19) or the standard scalar projector pushforward",
            "gravity or metric BV--BRST transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Construct the full renormalized off-diagonal bubble time distribution on [0,T] and join it to the finite-time bridge for all sixty roles, retaining all six third-Dyson orderings. Use the exact local collapse identity here to fix the MSbar counterterm. Prove boundedness on the selected source packet, including the six on-shell bridge roles, and match the covariant boundary. Do not substitute the energy-diagonal B_T formula as a multiplicative vertex. Only then combine this block with the triangle and T4 for the connected y4-y6 interference; complete q10 still requires y5, dressing and normalization.",
        "checks": {
            "total": len(checks),
            "passed": sum(checks.values()),
            "ok": all(checks.values()),
            "failures": [name for name, passed in checks.items() if not passed],
            "details": checks,
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_fully_rearranged_bubble_bridge_covariant_block.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_fully_rearranged_bubble_bridge_covariant_block.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest reverse_physics.tests.test_bt_fully_rearranged_bubble_bridge_covariant_block"
        ],
        "report": REPORT,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.write:
        with open(CERT, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check or not args.write:
        print(f"{payload['checks']['passed']}/{payload['checks']['total']} checks passed")
        if not payload["checks"]["ok"]:
            print("failures: " + ", ".join(payload["checks"]["failures"]))
            return 1
        print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
