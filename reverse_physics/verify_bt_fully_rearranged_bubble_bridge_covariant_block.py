#!/usr/bin/env python3
"""Independent verifier for the covariant BT bubble-with-bridge block."""
from __future__ import annotations

from fractions import Fraction
from math import comb
import hashlib
import itertools
import json
import os

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULLY_REARRANGED_BUBBLE_BRIDGE_COVARIANT_BLOCK_V1.json"
)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-fully-rearranged-bubble-bridge-covariant-block-v1.schema.json"
)
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


def frac(value):
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def channel_roles(channel_masks):
    """Generate from ten unordered bridge cuts, not from 1|2|3 partitions."""
    result = set()
    for channel in channel_masks:
        for oriented_bridge in (channel, channel ^ 63):
            bridge = tuple(label for label in range(6) if (oriented_bridge >> label) & 1)
            complement = tuple(label for label in range(6) if not ((oriented_bridge >> label) & 1))
            for junction in complement:
                bubble = tuple(label for label in complement if label != junction)
                result.add((junction, bubble, bridge))
    return sorted(result)


def analytic_weight(role, species_mask):
    """Closed contraction: the parallel-edge multiplicity is C(2,n_B)."""
    _, bubble_pair, bridge_triple = role
    bubble_omega = sum((species_mask >> label) & 1 for label in bubble_pair)
    bridge_omega = sum((species_mask >> label) & 1 for label in bridge_triple)
    if bridge_omega not in (1, 2):
        return 0
    return comb(2, bubble_omega)


def tensor_for(role, neutral_masks):
    tensor = [[0 for _ in range(8)] for _ in range(8)]
    for mask in neutral_masks:
        tensor[(mask >> 3) & 7][mask & 7] = analytic_weight(role, mask)
    return tensor


def residue(channel, mask):
    return Fraction(0) if mask in (channel, channel ^ 63) else Fraction(1, 4)


def vector(row):
    return tuple(Fraction(value) for value in row)


def negate(row):
    return tuple(-value for value in row)


def add(rows):
    return tuple(sum(values) for values in zip(*rows))


def square(row):
    return row[0] ** 2 - sum(value * value for value in row[1:])


def spatial_square(row):
    return sum(value * value for value in row[1:])


def independent_data():
    instrument = load(INPUTS[5])
    packet = load(INPUTS[7])
    channel_masks = instrument.get("ten_channel_residue_algebra", {}).get("channel_masks", [])
    neutral_masks = [mask for mask in range(64) if mask.bit_count() == 3]
    roles = channel_roles(channel_masks)
    tensors = [tensor_for(role, neutral_masks) for role in roles]

    witness = packet.get("exact_detector_witness", {})
    all_incoming = [vector(row) for row in witness.get("incoming_momenta", [])]
    all_incoming += [negate(vector(row)) for row in witness.get("outgoing_momenta", [])]
    rows = []
    cross = [[Fraction(0) for _ in roles] for _ in channel_masks]
    for role_index, (role, tensor) in enumerate(zip(roles, tensors)):
        junction, bubble, bridge = role
        bubble_q = add([all_incoming[label] for label in bubble])
        bridge_q = add([all_incoming[label] for label in bridge])
        bridge_mask = sum(1 << label for label in bridge)
        canonical = min(bridge_mask, bridge_mask ^ 63)
        weights = [analytic_weight(role, mask) for mask in neutral_masks]
        for tree_index, tree_mask in enumerate(channel_masks):
            cross[tree_index][role_index] = sum(
                residue(tree_mask, mask) * analytic_weight(role, mask)
                for mask in neutral_masks
            )
        rows.append({
            "index": role_index,
            "junction_leg": junction,
            "bubble_pair": list(bubble),
            "bridge_triple": list(bridge),
            "bridge_channel_mask": canonical,
            "bubble_invariant": frac(square(bubble_q)),
            "bubble_spatial_square": frac(spatial_square(bubble_q)),
            "bridge_invariant": frac(square(bridge_q)),
            "bridge_spatial_square": frac(spatial_square(bridge_q)),
            "source_weight": analytic_weight(role, 56),
            "weight_zero_count": weights.count(0),
            "weight_one_count": weights.count(1),
            "weight_two_count": weights.count(2),
            "tensor_HS_square": sum(value * value for value in weights),
            "tree_cross_Gram_column": [frac(cross[index][role_index]) for index in range(10)],
        })
    return channel_masks, neutral_masks, roles, tensors, rows, cross


def verify(certificate):
    checks = {}
    schema = load(SCHEMA_REL)
    checks["strict_schema"] = bool(schema) and not list(
        Draft202012Validator(schema).iter_errors(certificate)
    )
    checks["identity"] = certificate.get("certificate") == "REVERSE_PHYSICS_BT_FULLY_REARRANGED_BUBBLE_BRIDGE_COVARIANT_BLOCK_V1"
    checks["schema"] = certificate.get("schema") == SCHEMA_REL
    checks["version"] = certificate.get("schema_version") == 1
    checks["lifecycle"] = certificate.get("lifecycle_state") == "COEFFICIENT_COMPUTED"
    checks["tags"] = certificate.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"]

    provenance = certificate.get("provenance", {})
    recorded_inputs = provenance.get("inputs", [])
    checks["source_commit"] = provenance.get("source_commit") == SOURCE_COMMIT
    checks["input_paths"] = [row.get("path") for row in recorded_inputs] == INPUTS
    checks["input_hashes"] = len(recorded_inputs) == len(INPUTS) and all(
        row.get("sha256") == sha256(path)
        for row, path in zip(recorded_inputs, INPUTS)
    )
    checks["producer_verifier"] = (
        provenance.get("generated_by") == "reverse_physics/bt_fully_rearranged_bubble_bridge_covariant_block.py"
        and provenance.get("independent_verifier") == "reverse_physics/verify_bt_fully_rearranged_bubble_bridge_covariant_block.py"
    )
    checks["predecessors"] = all(load(path).get("checks", {}).get("ok") for path in INPUTS[3:])

    channel_masks, neutral_masks, roles, tensors, rows, cross = independent_data()
    graph = certificate.get("graph_and_master", {})
    checks["graph_counts"] = graph.get("counts") == {"V4": 3, "I": 3, "E": 6, "L": 1, "d_lambda": 6}
    checks["role_count"] = len(roles) == 60 and graph.get("labeled_role_count") == 60
    checks["normalization"] = graph.get("vertex_product") == "(V/g)^3=2^3=8" and graph.get("bubble_symmetry_factor") == "1/2" and graph.get("net_tensor_prefactor") == "4"
    checks["master"] = graph.get("bubble_master") == "B_MSbar(Q^2)=log[mu^2/(-Q^2-i0)]+2; Re B=log(mu^2/abs(Q^2))+2"
    checks["amplitude"] = graph.get("amplitude") == "T6_bb,cov=(4/(16*pi^2))*sum_R B_MSbar(Q_R^2)*W_R/(K_R^2+i0)"

    species = certificate.get("species_tensor", {})
    checks["neutral_masks"] = species.get("neutral_masks") == neutral_masks
    checks["analytic_tensors"] = species.get("tensors") == tensors
    checks["weight_profile"] = all(
        row["weight_zero_count"] == 2 and row["weight_one_count"] == 6 and row["weight_two_count"] == 12
        for row in rows
    ) and species.get("per_role_profile") == "two entries 0, six entries 1 and twelve entries 2"
    checks["HS_profile"] = all(row["tensor_HS_square"] == 54 for row in rows) and species.get("per_role_HS_square") == 54
    checks["assignment_sum"] = all(
        sum(analytic_weight(role, mask) for role in roles) == 90
        for mask in neutral_masks
    ) and species.get("sum_over_all_roles_on_each_neutral_assignment") == 90
    checks["source_profile"] = sorted(row["source_weight"] for row in rows) == [0] * 6 + [1] * 18 + [2] * 36
    checks["kappa"] = all(
        analytic_weight(role, mask) == analytic_weight(role, mask ^ 63)
        for role in roles for mask in neutral_masks
    )

    kinematics = certificate.get("role_kinematics", {})
    recorded_rows = kinematics.get("rows", [])
    checks["role_rows"] = recorded_rows == rows
    checks["bubble_margin"] = min(abs(Fraction(row["bubble_invariant"])) for row in rows) == Fraction(32, 625)
    checks["bubble_spatial_margin"] = min(Fraction(row["bubble_spatial_square"]) for row in rows) == Fraction(32, 625)
    on_shell = [row["index"] for row in rows if Fraction(row["bridge_invariant"]) == 0]
    checks["on_shell_roles"] = len(on_shell) == 6 and kinematics.get("on_shell_bridge_role_indices") == on_shell
    hard = [row["index"] for row in rows if set(row["bridge_triple"]) in ({0, 1, 2}, {3, 4, 5})]
    checks["hard_source_dark"] = len(hard) == 6 and all(rows[index]["source_weight"] == 0 for index in hard) and kinematics.get("hard_zero_spatial_bridge_role_indices") == hard
    checks["surviving_bridge_margin"] = min(
        Fraction(row["bridge_spatial_square"]) for row in rows if row["source_weight"]
    ) == Fraction(7169, 10625)

    incidence = certificate.get("tree_incidence", {})
    checks["tree_masks"] = incidence.get("tree_channel_masks") == channel_masks
    expected_cross = [[frac(value) for value in row] for row in cross]
    checks["cross_Gram"] = incidence.get("cross_Gram") == expected_cross
    values = [value for row in cross for value in row]
    checks["cross_values"] = set(values) == {Fraction(13, 2), Fraction(7), Fraction(15, 2)}
    checks["cross_multiplicities"] = (values.count(Fraction(13, 2)), values.count(Fraction(7)), values.count(Fraction(15, 2))) == (360, 180, 60)
    checks["cross_sums"] = {sum(row) for row in cross} == {405} and {
        sum(cross[tree][role] for tree in range(10)) for role in range(60)
    } == {Fraction(135, 2)}
    group_ok = True
    for channel in channel_masks:
        group = [role for role in roles if min(sum(1 << x for x in role[2]), sum(1 << x for x in role[2]) ^ 63) == channel]
        group_ok &= len(group) == 6
        for mask in neutral_masks:
            group_ok &= sum(analytic_weight(role, mask) for role in group) == 40 * residue(channel, mask)
    checks["group_identity"] = group_ok and incidence.get("group_identity") == "sum_(R with bridge C) W_R=40*R_C for every unordered channel C"
    checks["same_channel"] = all(
        cross[tree_index][role_index] == Fraction(15, 2)
        for tree_index, channel in enumerate(channel_masks)
        for role_index, role in enumerate(roles)
        if min(sum(1 << x for x in role[2]), sum(1 << x for x in role[2]) ^ 63) == channel
    )

    renormalization = certificate.get("renormalization", {})
    checks["power_count"] = renormalization.get("overall_superficial_degree") == -2 and "degree-zero" in renormalization.get("proper_subgraph", "")
    checks["counterterm"] = renormalization.get("primitive_six_point_counterterm") == "NONE"
    checks["RG_explicit"] = renormalization.get("explicit_scale_identity") == "d T6_bb,cov/d log(mu)=[5/(4*pi^2)]*T4,cov"
    checks["RG_running"] = renormalization.get("running") == "d lambda/d log(mu)=-5*lambda^3/(16*pi^2)"
    checks["RG_cancellation"] = renormalization.get("RG_sum") == "d[lambda^4*T4+lambda^6*T6_bb,cov]/d log(mu)=O(lambda^8) for this counterterm sector"
    checks["finite_time_collapse"] = "2*delta(t_A-t_B)" in renormalization.get("finite_time_local_identity", "")

    gate = certificate.get("finite_time_gate", {})
    checks["off_diagonal_gate"] = gate.get("status") == "COUNTERTERM_NORMALIZED_OFF_DIAGONAL_THIRD_DYSON_KERNEL_NOT_YET_COMPUTED"
    checks["no_BT_substitution"] = all(
        phrase in gate.get("why_existing_B_T_is_insufficient", "")
        for phrase in ("energy-diagonal", "third-Dyson", "exchanges energy")
    )
    disposition = certificate.get("disposition", {})
    checks["covariant_complete"] = disposition.get("covariant_bubble_bridge_block") == "COEFFICIENT_COMPUTED" and disposition.get("covariant_direct_auxiliary_connected_T6") == "COMPLETE_WITH_TRIANGLE_PREDECESSOR"
    checks["finite_time_open"] = disposition.get("finite_time_bubble_bridge") == "NOT_COMPUTED" and disposition.get("complete_finite_time_direct_auxiliary_connected_T6") == "NOT_COMPUTED"
    checks["not_promoted"] = (
        disposition.get("complete_q10") == "NOT_COMPUTED"
        and disposition.get("general_Eq19") == "NOT_PROVED"
        and disposition.get("gravity_or_metric_BV_BRST_transfer") == "NOT_CONSTRUCTED"
        and disposition.get("Lorentzian_causal_claim") == "NOT_ESTABLISHED"
    )
    checks["common_Born"] = certificate.get("common_Born_interference", {}).get("status") == "ISOLATED_COVARIANT_BUBBLE_BRIDGE_INTERFERENCE_COMMON_BORN"
    checks["boundaries"] = len(certificate.get("does_not_establish", [])) == 14 and "literature priority" in certificate.get("does_not_establish", [])
    checks["next_gate"] = all(term in certificate.get("next_gate", "") for term in ("off-diagonal", "all sixty roles", "Do not substitute", "complete q10"))
    checks["report"] = certificate.get("report") == "reverse_physics/reports/bt-fully-rearranged-bubble-bridge-covariant-block.md"

    producer_names = {
        "inputs_are_content_pinned", "six_predecessors_pass",
        "public_auxiliary_action_has_only_quartic_vertex", "frame_ledger_selects_bubble_bridge",
        "active_MSbar_bubble_is_imported", "sixty_role_partitions_are_exhaustive",
        "every_role_has_one_two_three_external_profile", "twenty_neutral_species_assignments_are_exhaustive",
        "each_role_has_two_zero_six_unit_twelve_double_weights", "each_role_HS_square_is_fifty_four",
        "every_neutral_assignment_has_total_weight_ninety", "every_tensor_is_kappa_fixed",
        "source_weight_profile_is_6_18_36", "ten_bridge_channels_each_have_six_roles",
        "grouped_tensor_is_forty_times_tree_residue", "cross_Gram_values_are_13half_7_15half",
        "cross_Gram_multiplicities_are_360_180_60", "cross_Gram_row_sums_are_405",
        "cross_Gram_column_sums_are_135_over_2", "same_bridge_tree_cross_is_15_over_2",
        "bubble_vertex_product_over_symmetry_is_four", "bubble_invariants_are_hard_at_packet_center",
        "bubble_spatial_momenta_are_nonzero", "six_bridge_roles_are_on_shell",
        "hard_zero_spatial_bridge_is_source_dark", "source_surviving_bridge_spatial_margin_is_7169_over_10625",
        "covariant_graph_has_only_bubble_subdivergence", "no_primitive_six_point_counterterm",
        "bubble_scale_derivative_is_two", "covariant_scale_derivative_is_five_over_four_pi2_times_tree",
        "beta_coefficient_is_five_over_sixteen", "running_lambda4_cancels_explicit_scale_derivative",
        "finite_time_local_counterterm_collapses_to_tree_kernel", "energy_diagonal_B_T_is_not_promoted_off_diagonal",
        "isolated_block_is_common_Born_without_sign", "complete_connected_auxiliary_loop_is_covariantly_closed",
        "complete_q10_is_not_promoted", "Eq19_gravity_and_causality_are_not_promoted",
    }
    recorded_checks = certificate.get("checks", {})
    checks["producer_checks"] = (
        recorded_checks.get("total") == 38
        and recorded_checks.get("passed") == 38
        and recorded_checks.get("ok") is True
        and recorded_checks.get("failures") == []
        and set(recorded_checks.get("details", {})) == producer_names
        and all(recorded_checks.get("details", {}).values())
    )
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
