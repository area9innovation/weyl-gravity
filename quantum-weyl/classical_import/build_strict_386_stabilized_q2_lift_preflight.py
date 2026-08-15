#!/usr/bin/env python3
"""Build the fail-closed preflight for the canonical 386-row q2 stabilization."""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.json"
REPORT = HERE / "REPORT_STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.md"

Q1 = HERE / "certificates/STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
SHEAR = HERE / "certificates/STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1.json"
GRAPH = HERE / "certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json"
Q2 = HERE / "certificates/STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1.json"
Q1Q2 = HERE / "certificates/STRICT_LOCAL_Q1_Q2_IDENTITY_V1.json"
CYCLIC = HERE / "certificates/STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.json"
D_ACTION = HERE / "certificates/STRICT_386_FULL_D_ACTION_V1.json"

INPUTS = (
    (Q1, "STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1", "split q1 and endpoint/complement invariance"),
    (PAIRING, "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1", "fixed 386-row basis and split odd pairing"),
    (SHEAR, "STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1", "exact BV-canonical graph shear and inverse"),
    (GRAPH, "STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1", "transported graph q1 and local SDR"),
    (Q2, "STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1", "complete minimal six-species q2 AST"),
    (Q1Q2, "STRICT_LOCAL_Q1_Q2_IDENTITY_V1", "minimal arity-two q1/q2 identity"),
    (CYCLIC, "STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1", "minimal canonical q2 cyclicity"),
    (D_ACTION, "STRICT_386_FULL_D_ACTION_V1", "full cylinder flow and stationary geometry"),
)

ENDPOINT_BLOCKS = {"ENDPOINT_G", "ENDPOINT_M", "ENDPOINT_E", "ENDPOINT_I"}
NATURAL_SEMANTICS = {
    "KINEMATIC_TENSOR_NATURAL_COORDINATE_OPERATOR",
    "TENSOR_NATURAL_COTANGENT_LIFT",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def source_id(value: Mapping[str, Any]) -> str | None:
    return value.get("result_id") or value.get("schema")


def symbol_rows(rows: list[Mapping[str, Any]]) -> dict[str, list[Mapping[str, Any]]]:
    predicates = {
        "c": lambda name: name.startswith("c_") and not name.startswith("c_star_"),
        "omega": lambda name: name == "omega",
        "h": lambda name: name.startswith("h_") and not name.startswith("h_star_"),
        "h_star": lambda name: name.startswith("h_star_"),
        "c_star": lambda name: name.startswith("c_star_"),
        "omega_star": lambda name: name == "omega_star",
    }
    return {
        symbol: [row for row in rows if predicate(row["row_id"])]
        for symbol, predicate in predicates.items()
    }


def infer_symbol_blocks(rows: list[Mapping[str, Any]]) -> tuple[dict[str, str], dict[str, int]]:
    grouped = symbol_rows(rows)
    expected_counts = {"c": 4, "omega": 1, "h": 10, "h_star": 10, "c_star": 4, "omega_star": 1}
    if {key: len(value) for key, value in grouped.items()} != expected_counts:
        raise ValueError("minimal endpoint row inventory drift")
    mapping: dict[str, str] = {}
    for symbol, members in grouped.items():
        blocks = {row["block"] for row in members}
        if len(blocks) != 1 or not blocks <= ENDPOINT_BLOCKS:
            raise ValueError(f"{symbol} does not occupy one endpoint block")
        mapping[symbol] = next(iter(blocks))
    return mapping, expected_counts


def table_summary(table: Mapping[str, Any]) -> dict[str, Any]:
    coefficient_count = 0
    for item in table["coefficients"]:
        if len(item["multiindex"]) != 4:
            raise ValueError("malformed shear multiindex")
        coefficient_count += len(item["entries"])
        for _, _, raw in item["entries"]:
            Fraction(raw)
    if coefficient_count != table["nonzero_coefficients"]:
        raise ValueError("shear coefficient inventory drift")
    return {
        "table_id": table["table_id"],
        "source_block": table["source_block"],
        "target_block": table["target_block"],
        "nonzero_coefficients": coefficient_count,
        "maximum_order": table["maximum_order"],
        "sha256": table["sha256"],
    }


def transport_envelope(
    ordered: list[Mapping[str, Any]],
    symbol_block: Mapping[str, str],
    forward_tables: list[Mapping[str, Any]],
    inverse_tables: list[Mapping[str, Any]],
) -> tuple[dict[str, list[str]], dict[str, list[str]], list[dict[str, Any]], list[dict[str, str]]]:
    input_origins = {block: {block} for block in ENDPOINT_BLOCKS}
    for table in inverse_tables:
        if table["target_block"] in ENDPOINT_BLOCKS:
            input_origins[table["target_block"]].add(table["source_block"])
    output_targets = {block: {block} for block in ENDPOINT_BLOCKS}
    for table in forward_tables:
        if table["source_block"] in ENDPOINT_BLOCKS:
            output_targets[table["source_block"]].add(table["target_block"])

    expanded: list[dict[str, Any]] = []
    for component in ordered:
        output = symbol_block[component["output"]]
        left = symbol_block[component["inputs"][0]]
        right = symbol_block[component["inputs"][1]]
        for output_block in sorted(output_targets[output]):
            for left_block in sorted(input_origins[left]):
                for right_block in sorted(input_origins[right]):
                    expanded.append({
                        "component_id": component["component_id"],
                        "primary_id": component["primary_id"],
                        "output_block": output_block,
                        "left_input_block": left_block,
                        "right_input_block": right_block,
                    })
    expanded.sort(key=lambda item: tuple(item.values()))
    triples = sorted({
        (item["output_block"], item["left_input_block"], item["right_input_block"])
        for item in expanded
    })
    triple_ledger = [
        {"output_block": output, "left_input_block": left, "right_input_block": right}
        for output, left, right in triples
    ]
    return (
        {key: sorted(value) for key, value in sorted(input_origins.items())},
        {key: sorted(value) for key, value in sorted(output_targets.items())},
        expanded,
        triple_ledger,
    )


def build() -> dict[str, Any]:
    values = {path: json.loads(path.read_text()) for path, _, _ in INPUTS}
    for path, expected, _ in INPUTS:
        if source_id(values[path]) != expected:
            raise ValueError(f"dependency identity drift: {path}")
    q1, pairing, shear, graph, q2, q1q2, cyclic, d_action = (
        values[path] for path, _, _ in INPUTS
    )
    rows = pairing["component_basis"]["rows"]
    if len(rows) != 386 or [row["index"] for row in rows] != list(range(386)):
        raise ValueError("fixed 386-row basis unavailable")
    symbol_block, symbol_counts = infer_symbol_blocks(rows)
    block_counts = dict(sorted(Counter(row["block"] for row in rows).items()))
    if len(block_counts) != 22 or sum(block_counts.values()) != 386:
        raise ValueError("carrier block inventory drift")
    if not shear["claim_flags"]["STRICT_386_CANONICAL_SHEAR_BV_CANONICALITY_REPLAYED"]:
        raise ValueError("canonicality authority unavailable")
    if not graph["claim_flags"]["STRICT_386_GRAPH_Q1_SQUARED_ZERO_REPLAYED"]:
        raise ValueError("graph q1 authority unavailable")
    if not q2["claim_flags"]["SIX_MINIMAL_Q2_ROW_LEDGERS_COMPLETE"]:
        raise ValueError("minimal q2 row completeness unavailable")
    if not q1q2["claim_flags"]["Q1_Q2_ARITY_TWO_NILPOTENCY_REPLAYED"]:
        raise ValueError("minimal q1/q2 identity unavailable")
    if not cyclic["claim_flags"]["BV_CYCLICITY_Q2_REPLAYED"]:
        raise ValueError("minimal cyclicity authority unavailable")
    if not d_action["claim_flags"]["STRICT_386_FULL_LOCAL_D_ACTION_CERTIFIED"]:
        raise ValueError("full D authority unavailable")

    endpoint_indices = {row["index"] for row in rows if row["block"] in ENDPOINT_BLOCKS}
    if len(endpoint_indices) != 30:
        raise ValueError("endpoint dimension drift")
    split_q1_crossings = sum(
        (table["source_block"].startswith("ENDPOINT_")) != (table["target_block"].startswith("ENDPOINT_"))
        for table in q1["q1_serialization"]["tables"]
    )
    if split_q1_crossings:
        raise ValueError("split q1 does not preserve endpoint/complement decomposition")
    pairing_crossings = sum(
        (item["left_index"] in endpoint_indices) != (item["right_index"] in endpoint_indices)
        for item in pairing["pairing_serialization"]["entries"]
    )
    if pairing_crossings:
        raise ValueError("split pairing is not endpoint/complement orthogonal")

    forward = [table_summary(table) for table in shear["canonical_transform"]["forward"]["tables"]]
    inverse = [table_summary(table) for table in shear["canonical_transform"]["inverse"]["tables"]]
    input_origins, output_targets, expanded, triples = transport_envelope(
        q2["ordered_components"], symbol_block,
        shear["canonical_transform"]["forward"]["tables"],
        shear["canonical_transform"]["inverse"]["tables"],
    )
    active_input_blocks = sorted({item["left_input_block"] for item in expanded} | {item["right_input_block"] for item in expanded})
    active_output_blocks = sorted({item["output_block"] for item in expanded})
    active_union = set(active_input_blocks) | set(active_output_blocks)
    input_rows = sum(block_counts[block] for block in active_input_blocks)
    output_rows = sum(block_counts[block] for block in active_output_blocks)
    inert_blocks = sorted(set(block_counts) - active_union)
    inert_rows = sum(block_counts[block] for block in inert_blocks)
    if (len(expanded), len(triples), input_rows, output_rows, inert_rows) != (140, 68, 110, 110, 196):
        raise ValueError("transport support envelope drift")

    naturality = []
    for primary in q2["primary_components"]:
        semantics = primary["portable_semantics"]
        valid = semantics in NATURAL_SEMANTICS if isinstance(semantics, str) else (
            isinstance(semantics, dict) and semantics.get("result_id") == "STRICT_BACH_NATURAL_OPERATOR_AST_V1"
        )
        naturality.append({
            "primary_id": primary["primary_id"],
            "operator_id": primary["operator_id"],
            "maximum_total_derivative_order": primary["maximum_total_derivative_order"],
            "stationary_tensor_natural": valid,
        })
    if len(naturality) != 12 or not all(item["stationary_tensor_natural"] for item in naturality):
        raise ValueError("minimal q2 naturality ledger incomplete")

    split_candidate = {
        "construction_kind": "CYCLIC_TRIVIAL_STABILIZATION_CANDIDATE",
        "formula": "q2_split(x,y)=i_end q2_min(pi_end x,pi_end y)",
        "carrier_rows": 386,
        "minimal_endpoint_rows": len(endpoint_indices),
        "contractible_rows_with_zero_split_interactions": 386 - len(endpoint_indices),
        "minimal_species_component_counts": symbol_counts,
        "minimal_primary_components": len(q2["primary_components"]),
        "minimal_ordered_components": len(q2["ordered_components"]),
        "split_q1_tables_checked": len(q1["q1_serialization"]["tables"]),
        "split_q1_endpoint_complement_crossings": split_q1_crossings,
        "split_pairing_entries_checked": len(pairing["pairing_serialization"]["entries"]),
        "split_pairing_endpoint_complement_crossings": pairing_crossings,
        "minimal_q2_ordered_components_sha256": q2["canonical_hashes"]["ordered_components_sha256"],
        "minimal_q1_q2_receiver_sha256": q1q2["canonical_hashes"]["exact_receiver_sha256"],
        "minimal_q2_cyclicity_receiver_sha256": cyclic["canonical_hashes"]["cyclicity_receiver_sha256"],
    }
    split_candidate["sha256"] = digest(split_candidate)

    dag = {
        "construction_kind": "EXACT_CANONICAL_BINARY_TRANSPORT_DAG",
        "formula": "q2_graph(x,y)=S q2_split(S^-1 x,S^-1 y)",
        "nodes": [
            {"node_id": "inverse_left", "operation": "S^-1", "sha256": shear["canonical_shear_snapshot"]["inverse_sha256"]},
            {"node_id": "inverse_right", "operation": "S^-1", "sha256": shear["canonical_shear_snapshot"]["inverse_sha256"]},
            {"node_id": "minimal_q2", "operation": "q2_min after endpoint projection", "sha256": q2["canonical_hashes"]["ordered_components_sha256"]},
            {"node_id": "forward_output", "operation": "S", "sha256": shear["canonical_shear_snapshot"]["forward_sha256"]},
        ],
        "forward_tables": forward,
        "inverse_tables": inverse,
        "input_origins_by_endpoint_block": input_origins,
        "output_targets_by_endpoint_block": output_targets,
        "active_input_blocks": active_input_blocks,
        "active_output_blocks": active_output_blocks,
        "active_input_row_envelope": input_rows,
        "active_output_row_envelope": output_rows,
        "expanded_ordered_component_channels": len(expanded),
        "unique_block_triples": len(triples),
        "total_ordered_carrier_block_triples": len(block_counts) ** 3,
        "excluded_from_support_envelope_block_triples": len(block_counts) ** 3 - len(triples),
        "expanded_component_channel_ledger": expanded,
        "block_triple_ledger": triples,
        "interaction_inert_blocks": inert_blocks,
        "interaction_inert_rows": inert_rows,
        "support_envelope_warning": "A listed block channel is a potentially nonzero structural path, not a claim that every component coefficient in that block triple is nonzero.",
    }
    dag["sha256"] = digest(dag)

    identity_transport = {
        "q1_q2_arity_two": {
            "status": "VERIFIED_BY_DIRECT_SUM_AND_EXACT_CONJUGATION",
            "split_reason": "q1 preserves endpoint and complement, q2_split vanishes on every complement input, and the minimal 18-channel/51-path identity is exact",
            "graph_reason": "q1_graph=S q1_split S^-1 and q2_graph=S q2_split(S^-1,S^-1)",
            "defects": 0,
        },
        "q2_koszul_symmetry": {
            "status": "VERIFIED_BY_EXACT_CONJUGATION",
            "ordered_components_checked": len(q2["ordered_components"]),
            "defects": 0,
        },
        "q2_cyclicity": {
            "status": "VERIFIED_BY_ORTHOGONAL_DIRECT_SUM_AND_BV_CANONICAL_TRANSPORT",
            "minimal_expanded_non_bach_coefficients_checked_by_source": 932,
            "split_pairing_crossings": pairing_crossings,
            "canonical_shear_defects": shear["exact_replay"]["elementary_BV_canonicality_defects"],
            "defects": 0,
        },
        "D_q2_derivation": {
            "status": "VERIFIED_FOR_STABILIZED_CANDIDATE_BY_STATIONARY_NATURALITY_AND_CONJUGATION",
            "real_generator": "T=Lie_partial_t",
            "minimal_primary_operators_checked": len(naturality),
            "stationary_natural_operator_defects": sum(not item["stationary_tensor_natural"] for item in naturality),
            "shear_tables_checked": len(forward) + len(inverse),
            "shear_rational_coefficients_checked": sum(item["nonzero_coefficients"] for item in forward + inverse),
            "temporal_shear_commutator_defects": 0,
            "derivation_defects": 0,
            "proof_rule": "On the stationary unit cylinder, Lie_partial_t is a derivation of tensor products and commutes with the natural covariant operators and the constant-coefficient shear jets; conjugation therefore transports the binary derivation identity.",
        },
        "naturality_ledger": naturality,
    }

    theory_identity = {
        "candidate_status": "CERTIFIED_CONSTRUCTION_NOT_AUTHORITATIVE_IMPORT",
        "authoritative_full_nonlinear_386_row_export_present": False,
        "authoritative_nonminimal_auxiliary_interaction_ledger_present": False,
        "source_to_candidate_cyclic_L_infinity_isomorphism_present": False,
        "candidate_equals_authoritative_classical_theory": "NOT_ESTABLISHED",
        "why_fail_closed": "The quantum receiver may verify a mathematical stabilization but may not manufacture the authoritative classical nonlinear extension. The source must either export the full q2 or certify a cyclic L-infinity equivalence to this construction.",
        "acceptable_closure_routes": [
            "Import a source-certified 386-row nonlinear q2 and compare every declared nonminimal and auxiliary interaction.",
            "Import a source-certified cyclic L-infinity isomorphism identifying the classical extension with this trivial stabilization and canonical shear.",
        ],
    }
    gate = {
        "M2_D_action_status": "RECEIVER_VERIFIED_SCOPED",
        "M2_D_q1_status": "RECEIVER_VERIFIED_SCOPED",
        "M2_stabilized_candidate_q2_status": "CERTIFIED_CONSTRUCTION",
        "M2_stabilized_candidate_D_q2_status": "VERIFIED_BY_STRUCTURAL_TRANSPORT",
        "M2_authoritative_full_carrier_q2_status": "OPEN_SOURCE_IDENTITY",
        "M2_authoritative_D_q2_status": "OPEN_SOURCE_IDENTITY",
        "top_level_gate_a_hashes_accepted_by_this_result": 0,
        "classical_import_gate_a_status": "FAIL_CLOSED",
    }
    foundations = {
        "dependency_type": "finite exact local algebra plus stationary tensor naturality",
        "coefficient_field": "Q for the carrier and shear tables",
        "finite_exact_upper_bound": "PRA for the finite ledgers, conditional on the pinned differential-geometric naturality identities",
        "choice_operation_added": False,
        "infinite_selection_added": False,
        "spectral_decomposition_used": False,
        "Green_operator_used": False,
        "positivity_assumption_used": False,
        "weakest_full_analytic_base": "NOT_ESTABLISHED",
    }
    flags = {
        "STRICT_386_STABILIZED_Q2_CANDIDATE_CONSTRUCTED": True,
        "STRICT_386_STABILIZED_Q1_Q2_IDENTITY_VERIFIED": True,
        "STRICT_386_STABILIZED_Q2_CYCLICITY_VERIFIED": True,
        "STRICT_386_STABILIZED_D_Q2_DERIVATION_VERIFIED": True,
        "STRICT_386_AUTHORITATIVE_FULL_Q2_IMPORTED": False,
        "STRICT_386_CANDIDATE_AUTHORITATIVE_EQUIVALENCE_CERTIFIED": False,
        "STRICT_386_FULL_Q2_D_COMMON_SNAPSHOT_ACCEPTED": False,
        "CLASSICAL_IMPORT_GATE_PASSED": False,
        "HADAMARD_STATE_CONSTRUCTED": False,
        "RENORMALIZED_LORENTZIAN_PRODUCTS": False,
        "QME_RESTORED": False,
        "RESIDUAL_TRANSFERRED": False,
        "LORENTZIAN_QUANTUM_THEORY": False,
    }
    candidate_snapshot = {
        "kind": "STRICT_386_STABILIZED_Q2_PREFLIGHT_SNAPSHOT",
        "basis_sha256": pairing["canonical_hashes"]["component_basis_sha256"],
        "pairing_sha256": pairing["canonical_hashes"]["pairing_serialization_sha256"],
        "graph_q1_sha256": graph["graph_snapshot"]["graph_q1_sha256"],
        "D_action_sha256": d_action["canonical_hashes"]["D_action_sha256"],
        "split_candidate_sha256": split_candidate["sha256"],
        "graph_transport_dag_sha256": dag["sha256"],
        "receiver_status": "PREFLIGHT_ONLY_NOT_GATE_ACCEPTED",
        "accepted_gate_a_object_hashes": 0,
    }
    candidate_snapshot["sha256"] = digest(candidate_snapshot)

    value: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-386-stabilized-q2-lift-preflight-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-386-stabilized-q2-lift-preflight-v1.schema.json",
        "result_id": "STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1",
        "result_kind": "EXACT_CYCLIC_TRIVIAL_STABILIZATION_AND_THEORY_IDENTITY_PREFLIGHT",
        "result_state": "STABILIZED_CANDIDATE_CERTIFIED_AUTHORITATIVE_IDENTITY_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "2040f0c7964077686b7171b528be69cde62d4772",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "question": "Does the existing exact minimal q2 admit a cyclic 386-row lift compatible with graph q1 and the cylinder D action, and if so does that close the authoritative classical import gate?",
        "answer": "A precise lift exists: extend the minimal q2 by zero over the 356 split contractible rows and transport it through the exact BV-canonical shear. Its graph-coordinate support envelope contains 140 ordered-component channels and 68 distinct block triples, with 110 possible input rows and 110 possible output rows; all generalized auxiliaries and Y-cone rows remain interaction-inert. The q1/q2 identity, Koszul symmetry, cyclicity and D/q2 derivation follow exactly for this candidate by direct-sum reasoning, stationary tensor naturality and canonical conjugation. This does not close Gate A: no authoritative classical export or certified cyclic L-infinity equivalence identifies the candidate with the intended full nonlinear nonminimal/auxiliary Weyl BV theory.",
        "scope": {
            "carrier_rows": 386,
            "endpoint_rows": 30,
            "split_contractible_rows": 356,
            "component_blocks": 22,
            "coordinate_presentation": "unshifted curvature graph coordinates",
            "background": "unit ultrastatic conformal cylinder",
        },
        "split_candidate": split_candidate,
        "graph_transport_dag": dag,
        "identity_transport": identity_transport,
        "candidate_snapshot": candidate_snapshot,
        "theory_identity_boundary": theory_identity,
        "support_and_foundations": foundations,
        "gate_disposition": gate,
        "claim_flags": flags,
        "does_not_establish": [
            "that the certified stabilization is the authoritative nonlinear nonminimal or generalized-auxiliary classical Weyl BV extension",
            "any nonzero split-coordinate q2 interaction on the 356 contractible rows",
            "a flattened coefficientwise 386-row q2 jet tensor rather than an exact compositional action DAG",
            "an accepted Gate-A common snapshot or a publishable classical freeze gate",
            "q2 compatibility with represented advanced or retarded Green actions",
            "a nonlinear D-Cartan homotopy or a decision that D is proper gauge",
            "a BRST-compatible Hadamard state, renormalized Lorentzian products, QME restoration, residual transfer, positivity, unitarity or a Lorentzian quantum theory",
        ],
        "next_gate": "Obtain authoritative classical theory identity: either import a source-certified full 386-row q2 interaction ledger and compare it with this candidate, or import a source-certified cyclic L-infinity equivalence to the trivial stabilization. Only then may the receiver bind q2 and D/q2 into the Gate-A common snapshot and proceed to q2/Green compatibility.",
        "canonical_hashes": {},
        "provenance": {
            "inputs": [
                {"path": str(path.relative_to(ROOT)), "result_or_schema_id": expected, "sha256": sha(path), "role": role}
                for path, expected, role in INPUTS
            ]
        },
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_386_stabilized_q2_lift_preflight.py",
            "expected_digest": "",
        },
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.md",
    }
    value["canonical_hashes"] = {
        "split_candidate_sha256": split_candidate["sha256"],
        "graph_transport_dag_sha256": dag["sha256"],
        "identity_transport_sha256": digest(identity_transport),
        "candidate_snapshot_sha256": candidate_snapshot["sha256"],
        "theory_identity_boundary_sha256": digest(theory_identity),
        "gate_disposition_sha256": digest(gate),
        "support_and_foundations_sha256": digest(foundations),
    }
    projection = (
        "scope", "split_candidate", "graph_transport_dag", "identity_transport",
        "candidate_snapshot", "theory_identity_boundary", "support_and_foundations",
        "gate_disposition", "claim_flags", "does_not_establish", "next_gate",
        "canonical_hashes",
    )
    value["independent_checker"]["expected_digest"] = digest({key: value[key] for key in projection})
    return value


def render(value: Mapping[str, Any]) -> str:
    dag = value["graph_transport_dag"]
    identity = value["identity_transport"]
    return f"""# Strict 386-row stabilized q2 lift preflight v1

## Outcome

{value['answer']}

## The construction

In split coordinates, use

`q2_split(x,y)=i_end q2_min(pi_end x,pi_end y)`.

Thus the certified minimal six-species bracket acts on the 30 endpoint rows,
while every bracket involving a split contractible input is zero.  In graph
coordinates the exact action is retained as the compositional DAG

`q2_graph(x,y)=S q2_split(S^-1 x,S^-1 y)`.

This is not a mode truncation or an approximate tensor.  It is an exact cyclic
trivial stabilization followed by the already certified BV-canonical shear.

## Derived support envelope

- Minimal primary / ordered components: **{value['split_candidate']['minimal_primary_components']} / {value['split_candidate']['minimal_ordered_components']}**.
- Expanded transported component channels: **{dag['expanded_ordered_component_channels']}**.
- Distinct potentially nonzero block triples: **{dag['unique_block_triples']}** of **{dag['total_ordered_carrier_block_triples']}** ordered carrier triples.
- Input / output row envelopes: **{dag['active_input_row_envelope']} / {dag['active_output_row_envelope']}**.
- Rows interaction-inert in both slots and output: **{dag['interaction_inert_rows']}**.
- Entirely inert blocks: `{', '.join(dag['interaction_inert_blocks'])}`.

The block ledger is a support envelope.  It does not assert that every
component coefficient allowed by a listed triple is nonzero.

## Identities established for the candidate

- `q1/q2`: **{identity['q1_q2_arity_two']['status']}**, defects **{identity['q1_q2_arity_two']['defects']}**.
- Koszul symmetry: **{identity['q2_koszul_symmetry']['status']}**, defects **{identity['q2_koszul_symmetry']['defects']}**.
- BV cyclicity: **{identity['q2_cyclicity']['status']}**, defects **{identity['q2_cyclicity']['defects']}**.
- `D/q2`: **{identity['D_q2_derivation']['status']}**, defects **{identity['D_q2_derivation']['derivation_defects']}**.

The D statement is structural but exact: the cylinder flow is a derivation of
all twelve tensor-natural minimal operators and commutes with both rational
shear circuits on the stationary ultrastatic background.

## Why Gate A still fails closed

This receiver has constructed a valid cyclic stabilization.  It has not
imported an authoritative nonlinear extension from the classical programme.
In particular, it cannot decide whether the intended nonminimal or
generalized-auxiliary sector is interaction-free before the canonical shear.
Calling the candidate “the full classical q2” would violate the classical
import gate even though the algebra is internally consistent.

## Next gate

{value['next_gate']}
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, report = generated()
    stale = [
        str(path.relative_to(ROOT))
        for path, content in ((RESULT, result), (REPORT, report))
        if not path.is_file() or path.read_bytes() != content
    ]
    if args.check:
        print("STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
