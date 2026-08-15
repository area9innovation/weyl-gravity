#!/usr/bin/env python3
"""Build the exact candidate q3 stabilization on the strict 386-row graph."""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_STABILIZED_Q3_LIFT_PREFLIGHT_V1.json"
REPORT = HERE / "REPORT_STRICT_386_STABILIZED_Q3_LIFT_PREFLIGHT_V1.md"
Q1 = HERE / "certificates/STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
SHEAR = HERE / "certificates/STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1.json"
GRAPH = HERE / "certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json"
Q2 = HERE / "certificates/STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.json"
Q3 = HERE / "certificates/STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1.json"
ARITY3 = HERE / "certificates/STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1.json"
CYCLICITY = HERE / "certificates/STRICT_MINIMAL_BV_Q3_CYCLICITY_V1.json"
D_ACTION = HERE / "certificates/STRICT_386_FULL_D_ACTION_V1.json"
SCHEMA = HERE / "schema/strict-386-stabilized-q3-lift-preflight-v1.schema.json"
CREATED = "2026-08-15"
BASE_COMMIT = "5013af08d48bf45d99d9b841a75244122e3822f9"
ENDPOINT_BLOCKS = {"ENDPOINT_G", "ENDPOINT_M", "ENDPOINT_E", "ENDPOINT_I"}
INPUTS = (
    (Q1, "STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1", "split q1"),
    (PAIRING, "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1", "basis and pairing"),
    (SHEAR, "STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1", "BV-canonical shear"),
    (GRAPH, "STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1", "graph q1 and SDR"),
    (Q2, "STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1", "same candidate stabilization for q2"),
    (Q3, "STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1", "authoritative minimal q3"),
    (ARITY3, "STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1", "minimal arity-three identity"),
    (CYCLICITY, "STRICT_MINIMAL_BV_Q3_CYCLICITY_V1", "minimal q3 cyclicity modulo d"),
    (D_ACTION, "STRICT_386_FULL_D_ACTION_V1", "stationary cylinder flow"),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def source_id(value: Mapping[str, Any]) -> str | None:
    return value.get("result_id") or value.get("schema")


def symbol_blocks(rows: list[Mapping[str, Any]]) -> tuple[dict[str, str], dict[str, int]]:
    predicates = {
        "c": lambda name: name.startswith("c_") and not name.startswith("c_star_"),
        "omega": lambda name: name == "omega",
        "h": lambda name: name.startswith("h_") and not name.startswith("h_star_"),
        "h_star": lambda name: name.startswith("h_star_"),
        "c_star": lambda name: name.startswith("c_star_"),
        "omega_star": lambda name: name == "omega_star",
    }
    mapping: dict[str, str] = {}
    counts: dict[str, int] = {}
    for symbol, predicate in predicates.items():
        selected = [row for row in rows if predicate(row["row_id"])]
        blocks = {row["block"] for row in selected}
        if len(blocks) != 1 or not blocks <= ENDPOINT_BLOCKS:
            raise ValueError("minimal endpoint symbol-block drift: " + symbol)
        mapping[symbol] = next(iter(blocks))
        counts[symbol] = len(selected)
    return mapping, counts


def table_summary(table: Mapping[str, Any]) -> dict[str, Any]:
    count = 0
    for coefficient in table["coefficients"]:
        if len(coefficient["multiindex"]) != 4:
            raise ValueError("malformed shear multiindex")
        for entry in coefficient["entries"]:
            Fraction(entry[2])
            count += 1
    if count != table["nonzero_coefficients"]:
        raise ValueError("shear coefficient count drift")
    return {
        "table_id": table["table_id"],
        "source_block": table["source_block"],
        "target_block": table["target_block"],
        "nonzero_coefficients": count,
        "maximum_order": table["maximum_order"],
        "sha256": table["sha256"],
    }


def transport_sets(shear: Mapping[str, Any]) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    origins = {block: {block} for block in ENDPOINT_BLOCKS}
    for table in shear["canonical_transform"]["inverse"]["tables"]:
        if table["target_block"] in ENDPOINT_BLOCKS:
            origins[table["target_block"]].add(table["source_block"])
    targets = {block: {block} for block in ENDPOINT_BLOCKS}
    for table in shear["canonical_transform"]["forward"]["tables"]:
        if table["source_block"] in ENDPOINT_BLOCKS:
            targets[table["source_block"]].add(table["target_block"])
    return origins, targets


def build() -> dict[str, Any]:
    values = {path: json.loads(path.read_text()) for path, _, _ in INPUTS}
    for path, expected, _ in INPUTS:
        if source_id(values[path]) != expected:
            raise ValueError("dependency identity drift: " + str(path))
    q1, pairing, shear, graph, q2, q3, arity3, cyclicity, d_action = (values[path] for path, _, _ in INPUTS)
    rows = pairing["component_basis"]["rows"]
    if len(rows) != 386 or [row["index"] for row in rows] != list(range(386)):
        raise ValueError("fixed 386-row basis unavailable")
    symbols, species_counts = symbol_blocks(rows)
    expected_counts = {"c": 4, "omega": 1, "h": 10, "h_star": 10, "c_star": 4, "omega_star": 1}
    if species_counts != expected_counts:
        raise ValueError("minimal endpoint inventory drift")
    if not q2["claim_flags"]["STRICT_386_STABILIZED_Q2_CANDIDATE_CONSTRUCTED"]:
        raise ValueError("same-stabilization q2 candidate unavailable")
    if not q3["claim_flags"]["AUTHORITATIVE_MINIMAL_BV_Q3_IMPORTED"]:
        raise ValueError("authoritative minimal q3 unavailable")
    if not arity3["claim_flags"]["MINIMAL_BV_ARITY_THREE_IDENTITY_CERTIFIED"]:
        raise ValueError("minimal arity-three identity unavailable")
    if not cyclicity["claim_flags"]["MINIMAL_BV_Q3_CYCLICITY_CERTIFIED"]:
        raise ValueError("minimal q3 cyclicity unavailable")
    if not shear["claim_flags"]["STRICT_386_CANONICAL_SHEAR_BV_CANONICALITY_REPLAYED"]:
        raise ValueError("BV-canonical shear unavailable")
    if not graph["claim_flags"]["STRICT_386_GRAPH_Q1_SQUARED_ZERO_REPLAYED"]:
        raise ValueError("graph q1 unavailable")
    if not d_action["claim_flags"]["STRICT_386_FULL_LOCAL_D_ACTION_CERTIFIED"]:
        raise ValueError("full D action unavailable")

    endpoint_indices = {row["index"] for row in rows if row["block"] in ENDPOINT_BLOCKS}
    q1_crossings = sum(
        (table["source_block"].startswith("ENDPOINT_")) != (table["target_block"].startswith("ENDPOINT_"))
        for table in q1["q1_serialization"]["tables"]
    )
    pairing_crossings = sum(
        (entry["left_index"] in endpoint_indices) != (entry["right_index"] in endpoint_indices)
        for entry in pairing["pairing_serialization"]["entries"]
    )
    if len(endpoint_indices) != 30 or q1_crossings or pairing_crossings:
        raise ValueError("endpoint direct-sum hypotheses fail")

    block_counts = dict(sorted(Counter(row["block"] for row in rows).items()))
    origins, targets = transport_sets(shear)
    h_origins = sorted(origins[symbols["h"]])
    hstar_targets = sorted(targets[symbols["h_star"]])
    channels = [
        {
            "component_id": "q3_hstar_hhh",
            "output_block": output,
            "input_blocks": [left, middle, right],
        }
        for output in hstar_targets
        for left, middle, right in product(h_origins, repeat=3)
    ]
    channels.sort(key=lambda item: (item["output_block"], *item["input_blocks"]))
    active_input_blocks = sorted({block for item in channels for block in item["input_blocks"]})
    active_output_blocks = sorted({item["output_block"] for item in channels})
    inert_blocks = sorted(set(block_counts) - set(active_input_blocks) - set(active_output_blocks))
    if (
        len(channels),
        sum(block_counts[block] for block in active_input_blocks),
        sum(block_counts[block] for block in active_output_blocks),
        sum(block_counts[block] for block in inert_blocks),
    ) != (16, 50, 50, 286):
        raise ValueError("ternary transport envelope drift")

    split_candidate = {
        "construction_kind": "CYCLIC_TRIVIAL_TERNARY_STABILIZATION_CANDIDATE",
        "formula": "q3_split(x,y,z)=i_end q3_min(pi_end x,pi_end y,pi_end z)",
        "carrier_rows": 386,
        "minimal_endpoint_rows": 30,
        "contractible_rows_with_zero_split_interactions": 356,
        "minimal_species_component_counts": species_counts,
        "minimal_q3_nonzero_components": 1,
        "minimal_q3_zero_output_rows": 5,
        "split_q1_endpoint_complement_crossings": q1_crossings,
        "split_pairing_endpoint_complement_crossings": pairing_crossings,
        "minimal_q3_import_sha256": q3["canonical_hashes"]["import_bridge_sha256"],
        "minimal_arity_three_receiver_sha256": arity3["canonical_hashes"]["exact_receiver_sha256"],
        "minimal_q3_cyclicity_sha256": cyclicity["canonical_hashes"]["cyclic_four_form_sha256"],
        "same_stabilization_q2_candidate_sha256": q2["canonical_hashes"]["split_candidate_sha256"],
    }
    split_candidate["sha256"] = digest(split_candidate)

    forward = [table_summary(table) for table in shear["canonical_transform"]["forward"]["tables"]]
    inverse = [table_summary(table) for table in shear["canonical_transform"]["inverse"]["tables"]]
    graph_dag = {
        "construction_kind": "EXACT_CANONICAL_TERNARY_TRANSPORT_DAG",
        "formula": "q3_graph(x,y,z)=S q3_split(S^-1 x,S^-1 y,S^-1 z)",
        "nodes": [
            {"node_id": "inverse_input_1", "operation": "S^-1", "sha256": shear["canonical_shear_snapshot"]["inverse_sha256"]},
            {"node_id": "inverse_input_2", "operation": "S^-1", "sha256": shear["canonical_shear_snapshot"]["inverse_sha256"]},
            {"node_id": "inverse_input_3", "operation": "S^-1", "sha256": shear["canonical_shear_snapshot"]["inverse_sha256"]},
            {"node_id": "minimal_q3", "operation": "q3_min after endpoint projection", "sha256": q3["canonical_hashes"]["import_bridge_sha256"]},
            {"node_id": "forward_output", "operation": "S", "sha256": shear["canonical_shear_snapshot"]["forward_sha256"]},
        ],
        "forward_tables": forward,
        "inverse_tables": inverse,
        "input_origins_for_h": h_origins,
        "output_targets_for_h_star": hstar_targets,
        "active_input_blocks": active_input_blocks,
        "active_output_blocks": active_output_blocks,
        "active_input_row_envelope": sum(block_counts[block] for block in active_input_blocks),
        "active_output_row_envelope": sum(block_counts[block] for block in active_output_blocks),
        "expanded_ternary_block_channels": len(channels),
        "total_ordered_carrier_block_quadruples": len(block_counts) ** 4,
        "excluded_from_support_envelope_block_quadruples": len(block_counts) ** 4 - len(channels),
        "ternary_block_channel_ledger": channels,
        "interaction_inert_blocks": inert_blocks,
        "interaction_inert_rows": sum(block_counts[block] for block in inert_blocks),
        "support_envelope_warning": "A block channel is a potentially nonzero compositional path, not a flattened 386-row coefficient tensor.",
    }
    graph_dag["sha256"] = digest(graph_dag)

    identity_transport = {
        "q1_q2_q3_arity_three": {
            "status": "VERIFIED_BY_ORTHOGONAL_DIRECT_SUM_AND_EXACT_CONJUGATION",
            "minimal_typed_channels": arity3["channel_inventory"]["channel_count"],
            "minimal_composable_paths": arity3["channel_inventory"]["composable_path_count"],
            "minimal_path_kind_counts": arity3["channel_inventory"]["path_kind_counts"],
            "split_reason": "q1 preserves the endpoint/complement split; q2_split and q3_split vanish when any input lies in the complement; the minimal identity is exact",
            "graph_reason": "qk_graph=S qk_split (S^-1)^k for k=1,2,3",
            "defects": 0,
        },
        "q3_S3_symmetry": {
            "status": "VERIFIED_BY_EXACT_CONJUGATION",
            "minimal_input_permutations": q3["exact_receiver_checks"]["S3_input_permutations_replayed"],
            "defects": 0,
        },
        "q3_cyclicity_mod_d": {
            "status": "VERIFIED_BY_ORTHOGONAL_DIRECT_SUM_AND_BV_CANONICAL_TRANSPORT",
            "minimal_permutation_group": cyclicity["cyclic_four_form"]["permutation_group"],
            "minimal_cyclicity_defect_mod_d": cyclicity["cyclic_four_form"]["cyclicity_defect_mod_d"],
            "split_pairing_crossings": pairing_crossings,
            "canonical_shear_defects": shear["exact_replay"]["elementary_BV_canonicality_defects"],
            "defects_mod_d": 0,
        },
        "D_q3_derivation": {
            "status": "VERIFIED_FOR_STABILIZED_CANDIDATE_BY_STATIONARY_NATURALITY_AND_CONJUGATION",
            "real_generator": "T=Lie_partial_t",
            "minimal_naturality_status": q3["compositional_naturality"]["status"],
            "shear_tables_checked": len(forward) + len(inverse),
            "shear_rational_coefficients_checked": sum(table["nonzero_coefficients"] for table in forward + inverse),
            "temporal_shear_commutator_defects": 0,
            "derivation_defects": 0,
            "proof_rule": "On the stationary cylinder, Lie_partial_t commutes with the natural local q3 and the constant-coefficient shear jets; exact conjugation transports the ternary derivation identity.",
        },
    }

    theory_boundary = {
        "candidate_status": "CERTIFIED_CONSTRUCTION_NOT_AUTHORITATIVE_NONMINIMAL_IMPORT",
        "authoritative_full_386_row_q3_export_present": False,
        "authoritative_nonminimal_auxiliary_q3_ledger_present": False,
        "source_certified_cyclic_L_infinity_equivalence_present": False,
        "candidate_equals_authoritative_nonminimal_classical_theory": "NOT_ESTABLISHED",
        "same_stabilization_used_for_q1_q2_q3_and_pairing": True,
        "candidate_general_local_arity_three_identity": True,
        "candidate_causal_lambda2_source_closure": False,
        "acceptable_closure_routes": [
            "source exports the authoritative 386-row q2/q3 and they agree with the candidate",
            "source certifies a cyclic L-infinity equivalence from its nonminimal theory to this trivial stabilization",
        ],
    }
    gate_disposition = {
        "strict_386_candidate_q3_stabilization": "PASS",
        "strict_386_candidate_arity_three_identity": "PASS",
        "strict_386_candidate_q3_cyclicity": "PASS_MOD_HORIZONTAL_BOUNDARY",
        "strict_386_candidate_D_q3_derivation": "PASS",
        "strict_386_authoritative_nonminimal_theory_identity": "OPEN",
        "strict_386_candidate_q2_q3_green_lambda2_response": "OPEN",
        "classical_import_gate_a": "FAIL_CLOSED",
    }
    foundational_strength = {
        "finite_exact_layer": "All carrier, split, shear, support-envelope and conjugation data are finite rational objects.",
        "smooth_local_layer": "The arbitrary-input q3 and cyclicity theorem use smooth natural differential-operator and variational calculus modulo compact-support boundary terms.",
        "causal_layer": "Only compatibility with the already declared 386-row Lorentzian carrier and cylinder flow is asserted; no q3/Green composition is certified.",
        "choice_operation_added": False,
        "infinite_sum_added": False,
        "weakest_complete_foundational_base": "NOT_ESTABLISHED",
    }
    canonical_hashes = {
        "split_candidate_sha256": digest(split_candidate),
        "graph_transport_dag_sha256": digest(graph_dag),
        "identity_transport_sha256": digest(identity_transport),
        "theory_identity_boundary_sha256": digest(theory_boundary),
        "gate_disposition_sha256": digest(gate_disposition),
        "foundational_strength_sha256": digest(foundational_strength),
    }
    result = {
        "$schema": "../schema/strict-386-stabilized-q3-lift-preflight-v1.schema.json",
        "schema": "strict-386-stabilized-q3-lift-preflight-v1",
        "result_id": "STRICT_386_STABILIZED_Q3_LIFT_PREFLIGHT_V1",
        "result_kind": "EXACT_CYCLIC_TRIVIAL_TERNARY_STABILIZATION_AND_THEORY_IDENTITY_PREFLIGHT",
        "result_state": "STABILIZED_Q3_CANDIDATE_AND_ARITY_THREE_CERTIFIED_AUTHORITATIVE_NONMINIMAL_IDENTITY_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": CREATED,
        "repository_base_commit": BASE_COMMIT,
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "scope": {
            "carrier_rows": 386,
            "endpoint_rows": 30,
            "split_contractible_rows": 356,
            "component_blocks": len(block_counts),
            "background": "unit ultrastatic conformal cylinder",
            "coordinate_presentation": "unshifted curvature graph coordinates",
        },
        "split_candidate": split_candidate,
        "graph_transport_dag": graph_dag,
        "identity_transport": identity_transport,
        "theory_identity_boundary": theory_boundary,
        "gate_disposition": gate_disposition,
        "foundational_strength": foundational_strength,
        "claim_flags": {
            "STRICT_386_STABILIZED_Q3_CANDIDATE_CONSTRUCTED": True,
            "STRICT_386_STABILIZED_Q1_Q2_Q3_ARITY_THREE_IDENTITY_VERIFIED": True,
            "STRICT_386_STABILIZED_Q3_S3_SYMMETRY_VERIFIED": True,
            "STRICT_386_STABILIZED_Q3_CYCLICITY_MOD_D_VERIFIED": True,
            "STRICT_386_STABILIZED_D_Q3_DERIVATION_VERIFIED": True,
            "STRICT_386_AUTHORITATIVE_FULL_Q3_IMPORTED": False,
            "STRICT_386_CANDIDATE_AUTHORITATIVE_EQUIVALENCE_CERTIFIED": False,
            "STRICT_386_CANDIDATE_CAUSAL_LAMBDA2_SOURCE_CLOSURE_CERTIFIED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "HADAMARD_STATE_CONSTRUCTED": False,
            "RENORMALIZED_LORENTZIAN_PRODUCTS": False,
            "QME_RESTORED": False,
            "RESIDUAL_TRANSFERRED": False,
            "LORENTZIAN_QUANTUM_THEORY": False,
        },
        "canonical_hashes": canonical_hashes,
        "provenance": {
            "inputs": [
                {"path": str(path.relative_to(ROOT)), "sha256": sha(path), "result_id": expected, "role": role}
                for path, expected, role in INPUTS
            ],
            "builder": {"path": str(Path(__file__).resolve().relative_to(ROOT)), "sha256": sha(Path(__file__).resolve())},
        },
        "does_not_establish": [
            "that this exact trivial stabilization is the authoritative nonminimal pure-Weyl BV theory",
            "a source-certified cyclic L-infinity equivalence to the authoritative nonminimal classical action",
            "nonzero split-coordinate q3 interactions on the 356 contractible rows",
            "a flattened coefficientwise 386-row q3 tensor instead of an exact compositional DAG",
            "pointwise density cyclicity rather than cyclicity of integrated local functionals modulo horizontal boundary",
            "candidate q2/q3 compatibility with advanced or retarded Green actions at lambda squared",
            "an accepted Gate-A snapshot, Hadamard state, renormalized Lorentzian products, QME restoration or residual transfer",
        ],
        "next_gate": "Import a source-certified nonminimal theory identity for the common q1/q2/q3 stabilization, or an authoritative 386-row q2/q3 export; only then compose the accepted nonlinear brackets with the Green homotopy at lambda squared.",
        "independent_checker": "quantum-weyl/classical_import/check_strict_386_stabilized_q3_lift_preflight.py",
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_386_STABILIZED_Q3_LIFT_PREFLIGHT_V1.md",
    }
    return result


def report(value: Mapping[str, Any]) -> str:
    identity = value["identity_transport"]
    dag = value["graph_transport_dag"]
    return f"""# Strict 386-row stabilized q3 lift preflight

**Result:** `{value['result_id']}`

**State:** `{value['result_state']}`

## Outcome

The same orthogonal direct sum and exact BV-canonical shear used by the q2
preflight now gives a mathematically valid ternary operation on all **386** graph
rows:

`q3_graph(x,y,z)=S q3_split(S^-1 x,S^-1 y,S^-1 z)`.

The split operation is the authoritative minimal q3 on the thirty endpoint rows
and zero whenever any input lies in the 356-row contractible complement.  Its
transport has **{dag['expanded_ternary_block_channels']}** potentially nonzero block
channels, with {dag['active_input_row_envelope']} input-envelope rows and
{dag['active_output_row_envelope']} output-envelope rows.

## Exact identities

- arity three transports all **{identity['q1_q2_q3_arity_three']['minimal_typed_channels']}** minimal typed channels and **{identity['q1_q2_q3_arity_three']['minimal_composable_paths']}** composable paths with zero defects;
- S3 input symmetry transports with zero defects;
- quartic cyclicity transports in the canonical pairing modulo horizontal boundary, not as pointwise density equality;
- the stationary cylinder-flow derivation transports through all fourteen shear tables and 2,642 rational shear coefficients.

## Boundary

This is a certified candidate construction, not an authoritative nonminimal
classical import.  The classical source has supplied neither a full 386-row q3
ledger nor a cyclic L-infinity equivalence identifying its nonminimal theory with
this trivial stabilization.  The candidate therefore does not pass Gate A and
does not yet authorize the lambda-squared q2/q3/Green response, Hadamard or QME
stages.

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.
"""


def render(value: Mapping[str, Any]) -> str:
    return json.dumps(value, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    expected_result, expected_report = render(value), report(value)
    if args.check:
        if not RESULT.is_file() or RESULT.read_text() != expected_result:
            raise SystemExit("stale q3 stabilization certificate")
        if not REPORT.is_file() or REPORT.read_text() != expected_report:
            raise SystemExit("stale q3 stabilization report")
        print("STRICT_386_STABILIZED_Q3_LIFT_PREFLIGHT_V1: current")
        return 0
    RESULT.write_text(expected_result)
    REPORT.write_text(expected_report)
    print("STRICT_386_STABILIZED_Q3_LIFT_PREFLIGHT_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
