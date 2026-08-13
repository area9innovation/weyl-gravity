#!/usr/bin/env python3
"""Independent verifier for the frame-typed fully rearranged q10 loop ledger."""
from __future__ import annotations

import hashlib
import itertools
import json
import os

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_FRAME_TYPED_LOOP_LEDGER_V1.json"
)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-fully-rearranged-q10-frame-typed-loop-ledger-v1.schema.json"
)
INPUTS = [
    "planning/work-items/reverse-physics-bateman-fully-rearranged-q10-frame-typed-loop-ledger.json",
    "planning/events/reverse-physics-bateman-fully-rearranged-q10-frame-typed-loop-ledger-DONE-978a336e.json",
    "reverse_physics/data/bateman_turok_hamiltonian_source_v1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_OBJECT_LEDGER_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_SHELL_TREE_NORMALIZATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_V4_CUBED_FINITE_TIME_AFFILIATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_TIME_ACTIVE_LOOP_AFFILIATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_PACKET_NORMAL_ORDERED_SPECTATOR_REDUCTION_V1.json",
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


def orbit(representative):
    return {
        tuple(
            tuple(representative[permutation[i]][permutation[j]] for j in range(3))
            for i in range(3)
        )
        for permutation in itertools.permutations(range(3))
    }


def independent_auxiliary_rows():
    """Classify by unicyclic core length, not by matrix search."""
    representatives = {
        "tadpole_at_tree_center": (
            (1, 1, 1),
            (1, 0, 0),
            (1, 0, 0),
        ),
        "bubble_with_bridge": (
            (0, 2, 1),
            (2, 0, 0),
            (1, 0, 0),
        ),
        "tadpole_at_tree_leaf": (
            (1, 1, 0),
            (1, 0, 1),
            (0, 1, 0),
        ),
        "triangle": (
            (0, 1, 1),
            (1, 0, 1),
            (1, 1, 0),
        ),
    }
    subgraphs = {
        "triangle": "NONE",
        "bubble_with_bridge": "FOUR_POINT_BUBBLE_DEGREE_ZERO",
        "tadpole_at_tree_center": "TWO_POINT_TADPOLE_LOCAL_MASS",
        "tadpole_at_tree_leaf": "TWO_POINT_TADPOLE_LOCAL_MASS",
    }
    rows = []
    all_labeled = set()
    for name, representative in representatives.items():
        members = orbit(representative)
        all_labeled.update(members)
        adjacency = min(members)
        internal = [
            2 * adjacency[vertex][vertex]
            + sum(adjacency[vertex][other] for other in range(3) if other != vertex)
            for vertex in range(3)
        ]
        self_loops = sum(adjacency[index][index] for index in range(3))
        rows.append({
            "topology": name,
            "canonical_adjacency": [list(row) for row in adjacency],
            "internal_degree_profile": sorted(internal),
            "external_leg_profile": sorted(4 - value for value in internal),
            "self_loop_count": self_loops,
            "labeled_orbit_size": len(members),
            "overall_superficial_degree": -2,
            "proper_loop_subgraph": subgraphs[name],
            "normal_ordered_massless_status": (
                "RETAINED"
                if self_loops == 0
                else "ZERO_IN_DECLARED_NORMAL_ORDERED_MASSLESS_SCHEME"
            ),
        })
    return sorted(rows, key=lambda row: row["canonical_adjacency"]), all_labeled


def independent_phi_rows():
    result = []
    # Eliminate V3=6-2*V4 before applying half-edge and Euler identities.
    for quartic in range(4):
        cubic = 6 - 2 * quartic
        internal = (3 * cubic + 4 * quartic - 6) // 2
        loops = internal - cubic - quartic + 1
        result.append({
            "V3": cubic,
            "V4": quartic,
            "I": internal,
            "E": 6,
            "L": loops,
            "lambda_degree": 6,
        })
    return sorted(result, key=lambda row: row["V3"])


def verify(certificate):
    checks = {}
    schema = load(SCHEMA_REL)
    checks["strict_schema"] = bool(schema) and not list(
        Draft202012Validator(schema).iter_errors(certificate)
    )
    checks["identity"] = certificate.get("certificate") == "REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_FRAME_TYPED_LOOP_LEDGER_V1"
    checks["schema"] = certificate.get("schema") == SCHEMA_REL
    checks["version"] = certificate.get("schema_version") == 1
    checks["lifecycle"] = certificate.get("lifecycle_state") == "CLASSIFIED"
    checks["tags"] = certificate.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]

    provenance = certificate.get("provenance", {})
    recorded_inputs = provenance.get("inputs", [])
    checks["source_commit"] = provenance.get("source_commit") == "978a336eaccbded0fcee39db58afbd946db8a2e2"
    checks["input_paths"] = [row.get("path") for row in recorded_inputs] == INPUTS
    checks["input_hashes"] = len(recorded_inputs) == len(INPUTS) and all(
        row.get("sha256") == sha256(path)
        for row, path in zip(recorded_inputs, INPUTS)
    )
    checks["producer_and_verifier"] = (
        provenance.get("generated_by") == "reverse_physics/bt_fully_rearranged_q10_frame_typed_loop_ledger.py"
        and provenance.get("independent_verifier") == "reverse_physics/verify_bt_fully_rearranged_q10_frame_typed_loop_ledger.py"
    )
    checks["predecessors"] = all(
        load(path).get("checks", {}).get("ok") for path in INPUTS[3:]
    )

    frame = certificate.get("frame_dictionary", {})
    checks["phi_action"] = frame.get("original_phi_action") == "S_phi=-1/2*integral (Box(phi)+lambda*(partial phi)^2)^2"
    checks["auxiliary_action"] = "Omega^2 Upsilon^2" in frame.get("auxiliary_action", "")
    checks["auxiliary_no_cubic"] = frame.get("auxiliary_vertices", "").endswith("no cubic vertex")
    checks["interaction_relation"] = frame.get("published_interaction_relation") == "S_phi=R_infinity^dagger S_OmegaUpsilon R_minus_infinity"
    checks["typing_rule"] = "not additive summands" in frame.get("typing_rule", "")
    checks["projector_rule"] = "R_t P_phi R_t^dagger" in frame.get("projector_rule", "")
    checks["frame_status"] = frame.get("status") == "TWO_ACTION_FRAMES_SEPARATED"

    expected_phi = independent_phi_rows()
    phi = certificate.get("original_phi_order6", {})
    checks["phi_rows"] = phi.get("rows") == expected_phi
    checks["phi_four_classes"] = phi.get("vertex_count_classes") == ["V4^3", "V3^2*V4^2", "V3^4*V4", "V3^6"]
    checks["phi_one_loop"] = all(row["L"] == 1 for row in expected_phi)
    checks["phi_status"] = phi.get("status") == "FOUR_ORIGINAL_PHI_VERTEX_COUNT_CLASSES_EXHAUSTIVE"

    expected_auxiliary, labeled = independent_auxiliary_rows()
    auxiliary = certificate.get("direct_auxiliary_order6", {})
    checks["auxiliary_rows"] = auxiliary.get("rows") == expected_auxiliary
    checks["auxiliary_labeled_count"] = len(labeled) == 16 and auxiliary.get("labeled_multigraph_count") == 16
    checks["auxiliary_orbits"] = auxiliary.get("orbit_count") == 4 and sorted(row["labeled_orbit_size"] for row in expected_auxiliary) == [1, 3, 6, 6]
    checks["auxiliary_edge_count"] = all(
        sum(row["canonical_adjacency"][i][i] for i in range(3))
        + sum(row["canonical_adjacency"][i][j] for i in range(3) for j in range(i + 1, 3))
        == 3
        for row in expected_auxiliary
    )
    checks["auxiliary_external_count"] = all(sum(row["external_leg_profile"]) == 6 for row in expected_auxiliary)
    checks["normal_ordered_survivors"] = auxiliary.get("normal_ordered_massless_survivors") == ["triangle", "bubble_with_bridge"]
    counterterms = auxiliary.get("counterterm_ledger", {})
    checks["triangle_counterterm"] = counterterms.get("triangle") == "UV finite, no proper loop subgraph and no counterterm"
    checks["bubble_counterterm"] = "degree-zero four-point bubble subdivergence" in counterterms.get("bubble_with_bridge", "")
    checks["tadpole_scheme"] = "declared normal-ordered massless scheme" in counterterms.get("tadpoles", "")
    checks["no_sixpoint_counterterm"] = counterterms.get("primitive_six_point") == "none because every overall six-point graph has degree -2"
    checks["auxiliary_status"] = auxiliary.get("status") == "FOUR_AUXILIARY_MULTIGRAPH_ORBITS_TWO_SURVIVE_SELECTED_NORMAL_ORDERING"

    correction = certificate.get("correction", {})
    checks["supersession"] = (
        correction.get("predecessor") == "REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_OBJECT_LEDGER_V1"
        and correction.get("status") == "SUPERSEDED_NEXT_GATE_FRAME_TYPING"
    )
    checks["invalid_interpretation"] = "other three V3 families" in correction.get("invalid_interpretation", "")
    checks["retained_triangle"] = "the isolated finite-time auxiliary triangle coefficient and common-Born class" in correction.get("retained_exact_results", [])
    checks["replacement"] = "bubble-with-bridge" in correction.get("replacement", "") and "scalar-phi experiment" in correction.get("replacement", "")

    disposition = certificate.get("disposition", {})
    checks["one_auxiliary_class_remains"] = (
        disposition.get("direct_auxiliary_triangle") == "COEFFICIENT_COMPUTED_AT_FINITE_TIME"
        and disposition.get("direct_auxiliary_bubble_with_bridge") == "MISSING_ASSEMBLY"
        and disposition.get("direct_auxiliary_connected_T6") == "INCOMPLETE_ONE_RENORMALIZED_CLASS_REMAINS"
    )
    checks["cross_frame_forbidden"] = disposition.get("cross_frame_addition_of_original_V3_classes") == "FORBIDDEN_DOUBLE_COUNTING"
    checks["not_complete_q10"] = disposition.get("complete_q10") == "NOT_COMPUTED"
    checks["not_promoted"] = (
        disposition.get("standard_scalar_projector_transfer") == "NOT_CONSTRUCTED"
        and disposition.get("general_Eq19") == "NOT_PROVED"
        and disposition.get("gravity_or_metric_BV_BRST_transfer") == "NOT_CONSTRUCTED"
        and disposition.get("Lorentzian_causal_claim") == "NOT_ESTABLISHED"
    )
    producer_check_names = {
        "inputs_are_content_pinned", "five_predecessors_pass",
        "public_auxiliary_action_has_only_quartic_interaction",
        "public_interaction_picture_relation_is_imported",
        "public_phi_cubic_and_quartic_rules_are_imported",
        "four_original_phi_vertex_count_solutions",
        "all_original_phi_classes_are_one_loop",
        "old_ledger_rows_are_original_phi_rows",
        "auxiliary_E6_L1_forces_three_quartic_vertices",
        "sixteen_labeled_auxiliary_multigraphs",
        "four_auxiliary_multigraph_orbits",
        "auxiliary_orbit_sizes_are_1_3_6_6",
        "auxiliary_topology_names_are_exhaustive",
        "every_auxiliary_graph_has_six_external_legs",
        "every_auxiliary_graph_has_overall_degree_minus_two",
        "normal_ordering_leaves_triangle_and_bubble_bridge",
        "triangle_block_is_already_finite_time_computed",
        "bubble_subgraph_is_already_renormalized_and_affiliated",
        "normal_ordering_is_selected_not_public_unique",
        "bubble_bridge_requires_quartic_counterterm",
        "no_primitive_six_point_counterterm",
        "original_V3_classes_are_not_auxiliary_addends",
        "frame_transfer_requires_Rt_projector_data",
        "previous_triangle_coefficient_is_retained",
        "previous_next_gate_is_superseded_only_in_frame_typing",
        "complete_auxiliary_connected_T6_remains_missing_bubble_bridge",
        "complete_q10_is_not_promoted",
        "Eq19_gravity_and_causality_are_not_promoted",
    }
    recorded_checks = certificate.get("checks", {})
    checks["producer_checks"] = (
        recorded_checks.get("total") == 28
        and recorded_checks.get("passed") == 28
        and recorded_checks.get("ok") is True
        and recorded_checks.get("failures") == []
        and set(recorded_checks.get("details", {})) == producer_check_names
        and all(recorded_checks.get("details", {}).values())
    )
    checks["boundaries"] = len(certificate.get("does_not_establish", [])) == 14 and "literature priority" in certificate.get("does_not_establish", [])
    checks["next_gate"] = all(
        term in certificate.get("next_gate", "")
        for term in ("bubble-with-bridge", "quartic counterterm", "Do not compute", "Eq. (19)")
    )
    checks["report"] = certificate.get("report") == "reverse_physics/reports/bt-fully-rearranged-q10-frame-typed-loop-ledger.md"
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
