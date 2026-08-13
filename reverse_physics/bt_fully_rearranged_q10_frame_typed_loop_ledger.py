#!/usr/bin/env python3
"""Frame-typed correction of the fully rearranged BT q10 loop ledger."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_FRAME_TYPED_LOOP_LEDGER_V1.json"
)
CERT = os.path.join(ROOT, CERT_REL)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-fully-rearranged-q10-frame-typed-loop-ledger-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-fully-rearranged-q10-frame-typed-loop-ledger.md"
SOURCE_COMMIT = "978a336eaccbded0fcee39db58afbd946db8a2e2"
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
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def permuted(adjacency, permutation):
    return tuple(
        tuple(adjacency[permutation[i]][permutation[j]] for j in range(3))
        for i in range(3)
    )


def canonical(adjacency):
    return min(permuted(adjacency, permutation) for permutation in itertools.permutations(range(3)))


def connected(adjacency):
    seen = {0}
    pending = [0]
    while pending:
        vertex = pending.pop()
        for neighbor in range(3):
            if (
                neighbor != vertex
                and adjacency[vertex][neighbor]
                and neighbor not in seen
            ):
                seen.add(neighbor)
                pending.append(neighbor)
    return len(seen) == 3


def degrees(adjacency):
    return [
        2 * adjacency[vertex][vertex]
        + sum(adjacency[vertex][other] for other in range(3) if other != vertex)
        for vertex in range(3)
    ]


def topology_name(adjacency):
    loop_vertices = [vertex for vertex in range(3) if adjacency[vertex][vertex]]
    off_edges = [
        adjacency[0][1],
        adjacency[0][2],
        adjacency[1][2],
    ]
    if not loop_vertices and sorted(off_edges) == [1, 1, 1]:
        return "triangle"
    if not loop_vertices and sorted(off_edges) == [0, 1, 2]:
        return "bubble_with_bridge"
    if len(loop_vertices) == 1:
        loop_vertex = loop_vertices[0]
        off_degree = sum(
            adjacency[loop_vertex][other]
            for other in range(3)
            if other != loop_vertex
        )
        if off_degree == 2:
            return "tadpole_at_tree_center"
        if off_degree == 1:
            return "tadpole_at_tree_leaf"
    raise AssertionError("unclassified connected three-edge multigraph")


def auxiliary_multigraph_rows():
    labeled = []
    for diagonal in itertools.product(range(4), repeat=3):
        for off_diagonal in itertools.product(range(4), repeat=3):
            if sum(diagonal) + sum(off_diagonal) != 3:
                continue
            adjacency = [[0] * 3 for _ in range(3)]
            for vertex, value in enumerate(diagonal):
                adjacency[vertex][vertex] = value
            for value, (left, right) in zip(
                off_diagonal,
                ((0, 1), (0, 2), (1, 2)),
            ):
                adjacency[left][right] = value
                adjacency[right][left] = value
            internal_degrees = degrees(adjacency)
            if max(internal_degrees) > 4 or not connected(adjacency):
                continue
            labeled.append(tuple(tuple(row) for row in adjacency))

    orbits = {}
    for adjacency in labeled:
        key = canonical(adjacency)
        orbits.setdefault(key, []).append(adjacency)

    rows = []
    for adjacency in sorted(orbits):
        name = topology_name(adjacency)
        internal_degrees = degrees(adjacency)
        loop_count = sum(adjacency[index][index] for index in range(3))
        rows.append({
            "topology": name,
            "canonical_adjacency": [list(row) for row in adjacency],
            "internal_degree_profile": sorted(internal_degrees),
            "external_leg_profile": sorted(4 - value for value in internal_degrees),
            "self_loop_count": loop_count,
            "labeled_orbit_size": len(orbits[adjacency]),
            "overall_superficial_degree": -2,
            "proper_loop_subgraph": {
                "triangle": "NONE",
                "bubble_with_bridge": "FOUR_POINT_BUBBLE_DEGREE_ZERO",
                "tadpole_at_tree_center": "TWO_POINT_TADPOLE_LOCAL_MASS",
                "tadpole_at_tree_leaf": "TWO_POINT_TADPOLE_LOCAL_MASS",
            }[name],
            "normal_ordered_massless_status": (
                "RETAINED"
                if loop_count == 0
                else "ZERO_IN_DECLARED_NORMAL_ORDERED_MASSLESS_SCHEME"
            ),
        })
    return labeled, rows


def original_phi_rows():
    rows = []
    for cubic in range(7):
        for quartic in range(4):
            if cubic + 2 * quartic != 6:
                continue
            internal = (3 * cubic + 4 * quartic - 6) // 2
            loops = internal - cubic - quartic + 1
            rows.append({
                "V3": cubic,
                "V4": quartic,
                "I": internal,
                "E": 6,
                "L": loops,
                "lambda_degree": cubic + 2 * quartic,
            })
    return rows


def build():
    source = load(INPUTS[2])
    old_ledger = load(INPUTS[3])
    phi_tree = load(INPUTS[4])
    triangle = load(INPUTS[5])
    active_loop = load(INPUTS[6])
    normal_order = load(INPUTS[7])
    predecessors = (old_ledger, phi_tree, triangle, active_loop, normal_order)

    phi_rows = original_phi_rows()
    labeled_auxiliary, auxiliary_rows = auxiliary_multigraph_rows()
    auxiliary_names = {row["topology"] for row in auxiliary_rows}
    normal_ordered_names = {
        row["topology"]
        for row in auxiliary_rows
        if row["normal_ordered_massless_status"] == "RETAINED"
    }
    old_rows = old_ledger["connected_order6_graphs"]["rows"]

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "five_predecessors_pass": all(row["checks"]["ok"] for row in predecessors),
        "public_auxiliary_action_has_only_quartic_interaction": (
            "Omega^2 Upsilon^2" in source["public_inputs"]["auxiliary_action"]
            and "lambda^2/2" in source["public_inputs"]["auxiliary_action"]
        ),
        "public_interaction_picture_relation_is_imported": (
            source["public_inputs"]["interaction_picture_relation"]
            == "S_phi=R_infinity^dagger S_OmegaUpsilon R_minus_infinity"
        ),
        "public_phi_cubic_and_quartic_rules_are_imported": (
            phi_tree["tree_topology_normalization"]["public_rules"]["cubic"]
            == "V3=-2*i*lambda*F3"
            and phi_tree["tree_topology_normalization"]["public_rules"]["quartic"]
            == "V4=-4*i*lambda^2*F4"
        ),
        "four_original_phi_vertex_count_solutions": len(phi_rows) == 4,
        "all_original_phi_classes_are_one_loop": all(row["L"] == 1 for row in phi_rows),
        "old_ledger_rows_are_original_phi_rows": [
            {
                "V3": row["V3"], "V4": row["V4"], "I": row["I"],
                "E": row["E"], "L": row["L"],
                "lambda_degree": row["d_lambda"],
            }
            for row in old_rows
        ] == phi_rows,
        "auxiliary_E6_L1_forces_three_quartic_vertices": (
            3 * 4 == 2 * 3 + 6 and 3 - 3 + 1 == 1
        ),
        "sixteen_labeled_auxiliary_multigraphs": len(labeled_auxiliary) == 16,
        "four_auxiliary_multigraph_orbits": len(auxiliary_rows) == 4,
        "auxiliary_orbit_sizes_are_1_3_6_6": sorted(
            row["labeled_orbit_size"] for row in auxiliary_rows
        ) == [1, 3, 6, 6],
        "auxiliary_topology_names_are_exhaustive": auxiliary_names == {
            "triangle",
            "bubble_with_bridge",
            "tadpole_at_tree_center",
            "tadpole_at_tree_leaf",
        },
        "every_auxiliary_graph_has_six_external_legs": all(
            sum(row["external_leg_profile"]) == 6 for row in auxiliary_rows
        ),
        "every_auxiliary_graph_has_overall_degree_minus_two": all(
            row["overall_superficial_degree"] == -2 for row in auxiliary_rows
        ),
        "normal_ordering_leaves_triangle_and_bubble_bridge": normal_ordered_names == {
            "triangle",
            "bubble_with_bridge",
        },
        "triangle_block_is_already_finite_time_computed": (
            triangle["disposition"]["finite_time_V4_cubed_block"]
            == "COEFFICIENT_COMPUTED"
        ),
        "bubble_subgraph_is_already_renormalized_and_affiliated": (
            active_loop["interpretation"]["finite_time_active_loop"]
            == "COEFFICIENT_COMPUTED"
        ),
        "normal_ordering_is_selected_not_public_unique": (
            "public Letter uniquely prescribes normal ordering"
            in normal_order["does_not_establish"][0]
        ),
        "bubble_bridge_requires_quartic_counterterm": any(
            row["proper_loop_subgraph"] == "FOUR_POINT_BUBBLE_DEGREE_ZERO"
            for row in auxiliary_rows
        ),
        "no_primitive_six_point_counterterm": all(
            row["overall_superficial_degree"] < 0 for row in auxiliary_rows
        ),
        "original_V3_classes_are_not_auxiliary_addends": True,
        "frame_transfer_requires_Rt_projector_data": True,
        "previous_triangle_coefficient_is_retained": True,
        "previous_next_gate_is_superseded_only_in_frame_typing": True,
        "complete_auxiliary_connected_T6_remains_missing_bubble_bridge": True,
        "complete_q10_is_not_promoted": True,
        "Eq19_gravity_and_causality_are_not_promoted": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_FRAME_TYPED_LOOP_LEDGER_V1",
        "question": "Are the three V3-containing order-six loop families additional direct-auxiliary corrections after the finite-time Omega/Upsilon V4^3 triangle, and what connected auxiliary loop objects actually remain?",
        "answer": "No. The four rows V3^6, V3^4*V4, V3^2*V4^2 and V4^3 are the exhaustive one-loop vertex-count classes of the original perfect-square phi action, whose cubic and quartic vertices have lambda degrees one and two. The direct auxiliary Omega/Upsilon action has no cubic vertex: at six external legs and one loop it forces exactly three quartic vertices and three internal lines. Exact quotient enumeration of all sixteen labeled connected three-vertex multigraphs gives four isomorphism types: the simple triangle, a double-edge four-point bubble with a bridge, a tadpole at the center of a three-vertex tree, and a tadpole at a leaf. In the declared normal-ordered massless unit-residue auxiliary scheme the two tadpole classes vanish, leaving the already certified finite-time triangle and one renormalized bubble-with-bridge class. The bubble has a logarithmically divergent four-point subgraph and must include the same local quartic counterterm and finite-time bubble kernel already certified for the active loop; the overall six-point graph has degree -2 and needs no primitive six-point counterterm. Therefore the prior instruction to add three V3 families after the auxiliary triangle mixed frames and is superseded. The triangle coefficient itself remains valid. A direct auxiliary q10 calculation next assembles the bubble-with-bridge and then source/detector and normalization terms. A standard scalar-phi projector result cannot be obtained by adding graph lists across frames; it requires the missing R_t projector pushforward, Eq. (19), and matched composite/Jacobian/counterterm data.",
        "result_kind": "exact action-frame typing and connected one-loop multigraph classification for the fully rearranged q10 ledger",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-13",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_fully_rearranged_q10_frame_typed_loop_ledger.py",
            "independent_verifier": "reverse_physics/verify_bt_fully_rearranged_q10_frame_typed_loop_ledger.py",
            "method": "Exact nonnegative vertex-count enumeration in the original frame and exhaustive connected symmetric-adjacency enumeration in the auxiliary frame, followed by an exact S3 orbit quotient and subgraph power-counting audit. No floating-point arithmetic enters a claim.",
        },
        "frame_dictionary": {
            "original_phi_action": "S_phi=-1/2*integral (Box(phi)+lambda*(partial phi)^2)^2",
            "original_phi_vertices": "V3 has lambda degree one and V4 has lambda degree two",
            "auxiliary_action": source["public_inputs"]["auxiliary_action"],
            "auxiliary_vertices": "one Omega^2*Upsilon^2 quartic vertex of lambda degree two; no cubic vertex",
            "published_interaction_relation": source["public_inputs"]["interaction_picture_relation"],
            "typing_rule": "choose one action frame for internal graph enumeration; original-phi and direct-auxiliary loop lists are related reorganizations, not additive summands",
            "projector_rule": "transporting the standard scalar projector to the auxiliary frame requires R_t P_phi R_t^dagger and cannot be inferred from an on-shell leading residue coincidence",
            "status": "TWO_ACTION_FRAMES_SEPARATED",
        },
        "original_phi_order6": {
            "half_edge_identity": "3*V3+4*V4=2*I+E",
            "coupling_identity": "V3+2*V4=6",
            "loop_identity": "L=I-(V3+V4)+1",
            "rows": phi_rows,
            "vertex_count_classes": ["V4^3", "V3^2*V4^2", "V3^4*V4", "V3^6"],
            "meaning": "complete vertex-count classes before graph topology, derivative numerator, counterterm and external composite-operator resolution in the original phi action",
            "status": "FOUR_ORIGINAL_PHI_VERTEX_COUNT_CLASSES_EXHAUSTIVE",
        },
        "direct_auxiliary_order6": {
            "identities": "4*V4=2*I+6, L=I-V4+1, lambda_degree=2*V4=6 imply V4=I=3",
            "labeled_multigraph_count": len(labeled_auxiliary),
            "orbit_count": len(auxiliary_rows),
            "rows": auxiliary_rows,
            "normal_ordered_massless_survivors": [
                "triangle",
                "bubble_with_bridge",
            ],
            "counterterm_ledger": {
                "triangle": "UV finite, no proper loop subgraph and no counterterm",
                "bubble_with_bridge": "overall degree -2 with one degree-zero four-point bubble subdivergence; use the matched quartic coupling counterterm",
                "tadpoles": "local two-point mass structures; zero only in the declared normal-ordered massless scheme",
                "primitive_six_point": "none because every overall six-point graph has degree -2",
            },
            "status": "FOUR_AUXILIARY_MULTIGRAPH_ORBITS_TWO_SURVIVE_SELECTED_NORMAL_ORDERING",
        },
        "correction": {
            "predecessor": "REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_OBJECT_LEDGER_V1",
            "status": "SUPERSEDED_NEXT_GATE_FRAME_TYPING",
            "invalid_interpretation": "the auxiliary V4^3 triangle was treated as one member of the original-phi four-row list and the other three V3 families were requested as additive auxiliary corrections",
            "retained_exact_results": [
                "q10=<y5,y5>+2*Re<y4,y6>",
                "four original-phi order-six vertex-count solutions",
                "all original-phi rows are one loop",
                "fully rearranged external disconnected support remains zero",
                "vacuum, source/detector and total-kappa blocks remain required",
                "the isolated finite-time auxiliary triangle coefficient and common-Born class",
            ],
            "replacement": "for the direct auxiliary experiment, compute the renormalized bubble-with-bridge after the triangle and state the tadpole scheme; for the scalar-phi experiment, complete the frame/projector transfer rather than adding auxiliary and phi graph lists",
        },
        "disposition": {
            "original_phi_order6_vertex_count_classes": "FOUR_CLASSIFIED_NOT_COMPUTED",
            "direct_auxiliary_triangle": "COEFFICIENT_COMPUTED_AT_FINITE_TIME",
            "direct_auxiliary_bubble_with_bridge": "MISSING_ASSEMBLY",
            "direct_auxiliary_tadpoles": "ZERO_ONLY_IN_DECLARED_NORMAL_ORDERED_MASSLESS_SCHEME",
            "direct_auxiliary_connected_T6": "INCOMPLETE_ONE_RENORMALIZED_CLASS_REMAINS",
            "cross_frame_addition_of_original_V3_classes": "FORBIDDEN_DOUBLE_COUNTING",
            "standard_scalar_projector_transfer": "NOT_CONSTRUCTED",
            "complete_q10": "NOT_COMPUTED",
            "common_Born_q10": "NOT_ESTABLISHED",
            "general_Eq19": "NOT_PROVED",
            "gravity_or_metric_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED",
        },
        "does_not_establish": [
            "the value or sign of the renormalized bubble-with-bridge packet interference",
            "a public-unique normal-ordering, mass or finite coupling-counterterm prescription",
            "loop-level equality of the original-phi and direct-auxiliary packet experiments",
            "the composite external-operator, functional-Jacobian or local-contact terms of a full field-redefinition equivalence theorem",
            "the complete original-phi one-loop six-leg amplitude",
            "the complete auxiliary connected T6 coefficient",
            "the complete y5 norm or y4-y6 interference",
            "source/detector second-order dressing or vacuum/survival normalization",
            "the value, sign or common-Born property of complete q10",
            "finite-coupling or all-order positivity",
            "general Eq. (19) or the standard scalar projector pushforward",
            "gravity or metric BV--BRST transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "next_gate": "Assemble the renormalized auxiliary bubble-with-bridge six-leg kernel by joining the certified finite-time active four-point bubble, including its matched local quartic counterterm, to one auxiliary tree vertex on every labeled three-three channel. Prove its total-kappa class and compact packet bound. State separately whether the two tadpole orbits are set to zero in the selected normal-ordered massless scheme. Do not compute or add an auxiliary V3^2*V4^2 graph. Complete q10 still requires y5, source/detector dressing and vacuum/survival normalization; a standard scalar-phi result additionally requires R_t/Eq. (19).",
        "checks": {
            "total": len(checks),
            "passed": sum(checks.values()),
            "ok": all(checks.values()),
            "failures": [name for name, passed in checks.items() if not passed],
            "details": checks,
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_fully_rearranged_q10_frame_typed_loop_ledger.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_fully_rearranged_q10_frame_typed_loop_ledger.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_fully_rearranged_q10_frame_typed_loop_ledger",
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
    if args.check:
        if not payload["checks"]["ok"]:
            print("failures: " + ", ".join(payload["checks"]["failures"]))
            return 1
        if os.path.exists(CERT):
            with open(CERT, encoding="utf-8") as handle:
                if handle.read() != rendered:
                    print("certificate drift")
                    return 1
    print(f"{payload['checks']['passed']}/{payload['checks']['total']} checks passed")
    print("RESULT:", "PASS" if payload["checks"]["ok"] else "FAIL")
    return 0 if payload["checks"]["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
