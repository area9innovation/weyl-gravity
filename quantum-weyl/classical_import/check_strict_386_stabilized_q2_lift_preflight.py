#!/usr/bin/env python3
"""Independently replay the 386-row stabilized-q2 lift preflight."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.json"
Q1 = HERE / "certificates/STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
SHEAR = HERE / "certificates/STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1.json"
GRAPH = HERE / "certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json"
Q2 = HERE / "certificates/STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1.json"
Q1Q2 = HERE / "certificates/STRICT_LOCAL_Q1_Q2_IDENTITY_V1.json"
CYCLIC = HERE / "certificates/STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.json"
D_ACTION = HERE / "certificates/STRICT_386_FULL_D_ACTION_V1.json"

INPUTS = (
    (Q1, "STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1"),
    (PAIRING, "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1"),
    (SHEAR, "STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1"),
    (GRAPH, "STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1"),
    (Q2, "STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1"),
    (Q1Q2, "STRICT_LOCAL_Q1_Q2_IDENTITY_V1"),
    (CYCLIC, "STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1"),
    (D_ACTION, "STRICT_386_FULL_D_ACTION_V1"),
)
ENDPOINTS = {"ENDPOINT_G", "ENDPOINT_M", "ENDPOINT_E", "ENDPOINT_I"}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def source_id(value: Mapping[str, Any]) -> str | None:
    return value.get("result_id") or value.get("schema")


def infer_symbols(rows: list[Mapping[str, Any]]) -> tuple[dict[str, str], dict[str, int]]:
    tests = {
        "c": lambda name: name.startswith("c_") and not name.startswith("c_star_"),
        "omega": lambda name: name == "omega",
        "h": lambda name: name.startswith("h_") and not name.startswith("h_star_"),
        "h_star": lambda name: name.startswith("h_star_"),
        "c_star": lambda name: name.startswith("c_star_"),
        "omega_star": lambda name: name == "omega_star",
    }
    counts: dict[str, int] = {}
    mapping: dict[str, str] = {}
    for symbol, predicate in tests.items():
        selected = [row for row in rows if predicate(row.get("row_id", ""))]
        counts[symbol] = len(selected)
        blocks = {row.get("block") for row in selected}
        if len(blocks) != 1:
            raise ValueError("ambiguous symbol block " + symbol)
        mapping[symbol] = next(iter(blocks))
    return mapping, counts


def summarize(table: Mapping[str, Any]) -> dict[str, Any]:
    count = 0
    for item in table.get("coefficients", []):
        if len(item.get("multiindex", [])) != 4:
            raise ValueError("bad shear multiindex")
        for entry in item.get("entries", []):
            if len(entry) != 3:
                raise ValueError("bad shear entry")
            Fraction(entry[2])
            count += 1
    return {
        "table_id": table.get("table_id"),
        "source_block": table.get("source_block"),
        "target_block": table.get("target_block"),
        "nonzero_coefficients": count,
        "maximum_order": table.get("maximum_order"),
        "sha256": table.get("sha256"),
    }


def derive_channels(
    components: list[Mapping[str, Any]],
    symbols: Mapping[str, str],
    forward: list[Mapping[str, Any]],
    inverse: list[Mapping[str, Any]],
) -> tuple[dict[str, list[str]], dict[str, list[str]], list[dict[str, Any]], list[dict[str, str]]]:
    origins = {block: {block} for block in ENDPOINTS}
    for table in inverse:
        target = table.get("target_block")
        if target in ENDPOINTS:
            origins[target].add(table.get("source_block"))
    targets = {block: {block} for block in ENDPOINTS}
    for table in forward:
        source = table.get("source_block")
        if source in ENDPOINTS:
            targets[source].add(table.get("target_block"))
    channels: list[dict[str, Any]] = []
    for component in components:
        output = symbols[component["output"]]
        left = symbols[component["inputs"][0]]
        right = symbols[component["inputs"][1]]
        for oblock in sorted(targets[output]):
            for lblock in sorted(origins[left]):
                for rblock in sorted(origins[right]):
                    channels.append({
                        "component_id": component["component_id"],
                        "primary_id": component["primary_id"],
                        "output_block": oblock,
                        "left_input_block": lblock,
                        "right_input_block": rblock,
                    })
    channels.sort(key=lambda item: tuple(item.values()))
    triples = sorted({
        (item["output_block"], item["left_input_block"], item["right_input_block"])
        for item in channels
    })
    ledger = [
        {"output_block": output, "left_input_block": left, "right_input_block": right}
        for output, left, right in triples
    ]
    return (
        {key: sorted(value) for key, value in sorted(origins.items())},
        {key: sorted(value) for key, value in sorted(targets.items())},
        channels,
        ledger,
    )


def check(value: Mapping[str, Any] | None = None) -> list[str]:
    value = load(RESULT) if value is None else value
    q1, pairing, shear, graph, q2, q1q2, cyclic, d_action = (load(path) for path, _ in INPUTS)
    errors: list[str] = []
    if (
        value.get("result_id") != "STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1"
        or value.get("result_kind") != "EXACT_CYCLIC_TRIVIAL_STABILIZATION_AND_THEORY_IDENTITY_PREFLIGHT"
        or value.get("result_state") != "STABILIZED_CANDIDATE_CERTIFIED_AUTHORITATIVE_IDENTITY_OPEN"
        or value.get("lifecycle") != "CLASSIFIED"
    ):
        errors.append("identity/lifecycle")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]:
        errors.append("dependency tags")

    rows = pairing.get("component_basis", {}).get("rows", [])
    if len(rows) != 386 or [row.get("index") for row in rows] != list(range(386)):
        errors.append("source basis")
        return errors
    try:
        symbols, symbol_counts = infer_symbols(rows)
    except (KeyError, TypeError, ValueError) as error:
        errors.append("symbol inference: " + str(error))
        return errors
    expected_symbol_counts = {"c": 4, "omega": 1, "h": 10, "h_star": 10, "c_star": 4, "omega_star": 1}
    if symbol_counts != expected_symbol_counts or set(symbols.values()) != ENDPOINTS:
        errors.append("minimal endpoint partition")
    block_counts = dict(sorted(Counter(row["block"] for row in rows).items()))
    endpoint_indices = {row["index"] for row in rows if row["block"] in ENDPOINTS}
    q1_crossings = sum(
        (table.get("source_block", "").startswith("ENDPOINT_")) != (table.get("target_block", "").startswith("ENDPOINT_"))
        for table in q1.get("q1_serialization", {}).get("tables", [])
    )
    pairing_crossings = sum(
        (entry.get("left_index") in endpoint_indices) != (entry.get("right_index") in endpoint_indices)
        for entry in pairing.get("pairing_serialization", {}).get("entries", [])
    )
    candidate = value.get("split_candidate", {})
    expected_candidate = {
        "construction_kind": "CYCLIC_TRIVIAL_STABILIZATION_CANDIDATE",
        "formula": "q2_split(x,y)=i_end q2_min(pi_end x,pi_end y)",
        "carrier_rows": 386,
        "minimal_endpoint_rows": len(endpoint_indices),
        "contractible_rows_with_zero_split_interactions": 386 - len(endpoint_indices),
        "minimal_species_component_counts": symbol_counts,
        "minimal_primary_components": len(q2.get("primary_components", [])),
        "minimal_ordered_components": len(q2.get("ordered_components", [])),
        "split_q1_tables_checked": len(q1.get("q1_serialization", {}).get("tables", [])),
        "split_q1_endpoint_complement_crossings": q1_crossings,
        "split_pairing_entries_checked": len(pairing.get("pairing_serialization", {}).get("entries", [])),
        "split_pairing_endpoint_complement_crossings": pairing_crossings,
        "minimal_q2_ordered_components_sha256": q2["canonical_hashes"]["ordered_components_sha256"],
        "minimal_q1_q2_receiver_sha256": q1q2["canonical_hashes"]["exact_receiver_sha256"],
        "minimal_q2_cyclicity_receiver_sha256": cyclic["canonical_hashes"]["cyclicity_receiver_sha256"],
    }
    expected_candidate["sha256"] = digest(expected_candidate)
    if candidate != expected_candidate or q1_crossings or pairing_crossings:
        errors.append("split candidate/direct-sum replay")

    forward_raw = shear.get("canonical_transform", {}).get("forward", {}).get("tables", [])
    inverse_raw = shear.get("canonical_transform", {}).get("inverse", {}).get("tables", [])
    try:
        forward = [summarize(table) for table in forward_raw]
        inverse = [summarize(table) for table in inverse_raw]
        origins, targets, channels, triples = derive_channels(q2.get("ordered_components", []), symbols, forward_raw, inverse_raw)
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
        errors.append("transport replay: " + str(error))
        return errors
    active_inputs = sorted({item["left_input_block"] for item in channels} | {item["right_input_block"] for item in channels})
    active_outputs = sorted({item["output_block"] for item in channels})
    inert_blocks = sorted(set(block_counts) - set(active_inputs) - set(active_outputs))
    expected_dag = {
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
        "input_origins_by_endpoint_block": origins,
        "output_targets_by_endpoint_block": targets,
        "active_input_blocks": active_inputs,
        "active_output_blocks": active_outputs,
        "active_input_row_envelope": sum(block_counts[block] for block in active_inputs),
        "active_output_row_envelope": sum(block_counts[block] for block in active_outputs),
        "expanded_ordered_component_channels": len(channels),
        "unique_block_triples": len(triples),
        "total_ordered_carrier_block_triples": len(block_counts) ** 3,
        "excluded_from_support_envelope_block_triples": len(block_counts) ** 3 - len(triples),
        "expanded_component_channel_ledger": channels,
        "block_triple_ledger": triples,
        "interaction_inert_blocks": inert_blocks,
        "interaction_inert_rows": sum(block_counts[block] for block in inert_blocks),
        "support_envelope_warning": "A listed block channel is a potentially nonzero structural path, not a claim that every component coefficient in that block triple is nonzero.",
    }
    expected_dag["sha256"] = digest(expected_dag)
    if value.get("graph_transport_dag") != expected_dag:
        errors.append("graph transport DAG/support envelope")
    if (len(channels), len(triples), expected_dag["active_input_row_envelope"], expected_dag["active_output_row_envelope"], expected_dag["interaction_inert_rows"]) != (140, 68, 110, 110, 196):
        errors.append("transport inventory")

    naturality = []
    for primary in q2.get("primary_components", []):
        semantics = primary.get("portable_semantics")
        natural = semantics in {
            "KINEMATIC_TENSOR_NATURAL_COORDINATE_OPERATOR", "TENSOR_NATURAL_COTANGENT_LIFT"
        } if isinstance(semantics, str) else (
            isinstance(semantics, dict) and semantics.get("result_id") == "STRICT_BACH_NATURAL_OPERATOR_AST_V1"
        )
        naturality.append({
            "primary_id": primary.get("primary_id"),
            "operator_id": primary.get("operator_id"),
            "maximum_total_derivative_order": primary.get("maximum_total_derivative_order"),
            "stationary_tensor_natural": natural,
        })
    identity = value.get("identity_transport", {})
    required_status = {
        "q1_q2_arity_two": "VERIFIED_BY_DIRECT_SUM_AND_EXACT_CONJUGATION",
        "q2_koszul_symmetry": "VERIFIED_BY_EXACT_CONJUGATION",
        "q2_cyclicity": "VERIFIED_BY_ORTHOGONAL_DIRECT_SUM_AND_BV_CANONICAL_TRANSPORT",
        "D_q2_derivation": "VERIFIED_FOR_STABILIZED_CANDIDATE_BY_STATIONARY_NATURALITY_AND_CONJUGATION",
    }
    for key, status in required_status.items():
        if identity.get(key, {}).get("status") != status:
            errors.append("identity status " + key)
    if (
        identity.get("q1_q2_arity_two", {}).get("defects") != 0
        or identity.get("q2_koszul_symmetry", {}).get("defects") != 0
        or identity.get("q2_cyclicity", {}).get("defects") != 0
        or identity.get("D_q2_derivation", {}).get("derivation_defects") != 0
        or identity.get("D_q2_derivation", {}).get("temporal_shear_commutator_defects") != 0
        or identity.get("D_q2_derivation", {}).get("shear_rational_coefficients_checked") != 2642
        or identity.get("naturality_ledger") != naturality
        or len(naturality) != 12
        or not all(item["stationary_tensor_natural"] for item in naturality)
        or not q1q2.get("claim_flags", {}).get("Q1_Q2_ARITY_TWO_NILPOTENCY_REPLAYED")
        or not cyclic.get("claim_flags", {}).get("BV_CYCLICITY_Q2_REPLAYED")
        or not shear.get("claim_flags", {}).get("STRICT_386_CANONICAL_SHEAR_BV_CANONICALITY_REPLAYED")
        or not d_action.get("claim_flags", {}).get("STRICT_386_FULL_LOCAL_D_ACTION_CERTIFIED")
    ):
        errors.append("identity dependency/replay boundary")

    theory = value.get("theory_identity_boundary", {})
    if not (
        theory.get("candidate_status") == "CERTIFIED_CONSTRUCTION_NOT_AUTHORITATIVE_IMPORT"
        and theory.get("authoritative_full_nonlinear_386_row_export_present") is False
        and theory.get("authoritative_nonminimal_auxiliary_interaction_ledger_present") is False
        and theory.get("source_to_candidate_cyclic_L_infinity_isomorphism_present") is False
        and theory.get("candidate_equals_authoritative_classical_theory") == "NOT_ESTABLISHED"
        and len(theory.get("acceptable_closure_routes", [])) == 2
    ):
        errors.append("theory identity fail-closed boundary")
    gate = value.get("gate_disposition", {})
    if not (
        gate.get("M2_stabilized_candidate_q2_status") == "CERTIFIED_CONSTRUCTION"
        and gate.get("M2_stabilized_candidate_D_q2_status") == "VERIFIED_BY_STRUCTURAL_TRANSPORT"
        and gate.get("M2_authoritative_full_carrier_q2_status") == "OPEN_SOURCE_IDENTITY"
        and gate.get("M2_authoritative_D_q2_status") == "OPEN_SOURCE_IDENTITY"
        and gate.get("top_level_gate_a_hashes_accepted_by_this_result") == 0
        and gate.get("classical_import_gate_a_status") == "FAIL_CLOSED"
    ):
        errors.append("Gate-A boundary")
    snapshot = value.get("candidate_snapshot", {})
    expected_snapshot = {
        "kind": "STRICT_386_STABILIZED_Q2_PREFLIGHT_SNAPSHOT",
        "basis_sha256": pairing["canonical_hashes"]["component_basis_sha256"],
        "pairing_sha256": pairing["canonical_hashes"]["pairing_serialization_sha256"],
        "graph_q1_sha256": graph["graph_snapshot"]["graph_q1_sha256"],
        "D_action_sha256": d_action["canonical_hashes"]["D_action_sha256"],
        "split_candidate_sha256": expected_candidate["sha256"],
        "graph_transport_dag_sha256": expected_dag["sha256"],
        "receiver_status": "PREFLIGHT_ONLY_NOT_GATE_ACCEPTED",
        "accepted_gate_a_object_hashes": 0,
    }
    expected_snapshot["sha256"] = digest(expected_snapshot)
    if snapshot != expected_snapshot:
        errors.append("candidate snapshot")

    flags = value.get("claim_flags", {})
    true_flags = (
        "STRICT_386_STABILIZED_Q2_CANDIDATE_CONSTRUCTED",
        "STRICT_386_STABILIZED_Q1_Q2_IDENTITY_VERIFIED",
        "STRICT_386_STABILIZED_Q2_CYCLICITY_VERIFIED",
        "STRICT_386_STABILIZED_D_Q2_DERIVATION_VERIFIED",
    )
    false_flags = (
        "STRICT_386_AUTHORITATIVE_FULL_Q2_IMPORTED",
        "STRICT_386_CANDIDATE_AUTHORITATIVE_EQUIVALENCE_CERTIFIED",
        "STRICT_386_FULL_Q2_D_COMMON_SNAPSHOT_ACCEPTED",
        "CLASSICAL_IMPORT_GATE_PASSED", "HADAMARD_STATE_CONSTRUCTED",
        "RENORMALIZED_LORENTZIAN_PRODUCTS", "QME_RESTORED", "RESIDUAL_TRANSFERRED",
        "LORENTZIAN_QUANTUM_THEORY",
    )
    if any(flags.get(key) is not True for key in true_flags) or any(flags.get(key) is not False for key in false_flags):
        errors.append("claim promotion boundary")
    foundations = value.get("support_and_foundations", {})
    for key in ("choice_operation_added", "infinite_selection_added", "spectral_decomposition_used", "Green_operator_used", "positivity_assumption_used"):
        if foundations.get(key) is not False:
            errors.append("foundational boundary " + key)

    provenance = value.get("provenance", {}).get("inputs", [])
    if len(provenance) != len(INPUTS):
        errors.append("provenance count")
    else:
        for item, (path, expected) in zip(provenance, INPUTS, strict=True):
            if item.get("path") != str(path.relative_to(ROOT)) or item.get("sha256") != sha(path):
                errors.append("provenance path/hash " + str(path))
            if item.get("result_or_schema_id") != expected or source_id(load(path)) != expected:
                errors.append("provenance identity " + str(path))

    hashes = value.get("canonical_hashes", {})
    expected_hashes = {
        "split_candidate_sha256": expected_candidate["sha256"],
        "graph_transport_dag_sha256": expected_dag["sha256"],
        "identity_transport_sha256": digest(identity),
        "candidate_snapshot_sha256": expected_snapshot["sha256"],
        "theory_identity_boundary_sha256": digest(theory),
        "gate_disposition_sha256": digest(gate),
        "support_and_foundations_sha256": digest(foundations),
    }
    if hashes != expected_hashes:
        errors.append("canonical hashes")
    projection = (
        "scope", "split_candidate", "graph_transport_dag", "identity_transport",
        "candidate_snapshot", "theory_identity_boundary", "support_and_foundations",
        "gate_disposition", "claim_flags", "does_not_establish", "next_gate",
        "canonical_hashes",
    )
    if value.get("independent_checker", {}).get("expected_digest") != digest({key: value.get(key) for key in projection}):
        errors.append("canonical digest")
    return errors


def main() -> int:
    errors = check()
    print("STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print("  - exact trivial stabilization and canonical graph transport DAG certified")
        print("  - 140 component channels, 68 block triples and 110/110 row envelopes replayed")
        print("  - candidate identities close; authoritative theory identity and Gate A remain fail closed")
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
