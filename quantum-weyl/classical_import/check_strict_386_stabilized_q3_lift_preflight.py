#!/usr/bin/env python3
"""Independent structural replay of the strict 386-row q3 stabilization."""

from __future__ import annotations

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
FILES = {
    "q1": (HERE / "certificates/STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.json", "STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1"),
    "pairing": (HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json", "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1"),
    "shear": (HERE / "certificates/STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1.json", "STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1"),
    "graph": (HERE / "certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json", "STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1"),
    "q2": (HERE / "certificates/STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.json", "STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1"),
    "q3": (HERE / "certificates/STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1.json", "STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1"),
    "arity3": (HERE / "certificates/STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1.json", "STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1"),
    "cyclicity": (HERE / "certificates/STRICT_MINIMAL_BV_Q3_CYCLICITY_V1.json", "STRICT_MINIMAL_BV_Q3_CYCLICITY_V1"),
    "d_action": (HERE / "certificates/STRICT_386_FULL_D_ACTION_V1.json", "STRICT_386_FULL_D_ACTION_V1"),
}
ENDPOINTS = {"ENDPOINT_G", "ENDPOINT_M", "ENDPOINT_E", "ENDPOINT_I"}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def table_summary(table: Mapping[str, Any]) -> dict[str, Any]:
    count = 0
    for coefficient in table.get("coefficients", []):
        if len(coefficient.get("multiindex", [])) != 4:
            raise ValueError("bad multiindex")
        for entry in coefficient.get("entries", []):
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


def infer(rows: list[Mapping[str, Any]]) -> tuple[dict[str, str], dict[str, int]]:
    tests = {
        "c": lambda name: name.startswith("c_") and not name.startswith("c_star_"),
        "omega": lambda name: name == "omega",
        "h": lambda name: name.startswith("h_") and not name.startswith("h_star_"),
        "h_star": lambda name: name.startswith("h_star_"),
        "c_star": lambda name: name.startswith("c_star_"),
        "omega_star": lambda name: name == "omega_star",
    }
    mapping, counts = {}, {}
    for symbol, predicate in tests.items():
        selected = [row for row in rows if predicate(row.get("row_id", ""))]
        blocks = {row.get("block") for row in selected}
        if len(blocks) != 1:
            raise ValueError("ambiguous endpoint symbol")
        mapping[symbol], counts[symbol] = next(iter(blocks)), len(selected)
    return mapping, counts


def check(value: Mapping[str, Any] | None = None) -> list[str]:
    value = load(RESULT) if value is None else value
    sources = {name: load(path) for name, (path, _) in FILES.items()}
    errors: list[str] = []
    if (
        value.get("result_id") != "STRICT_386_STABILIZED_Q3_LIFT_PREFLIGHT_V1"
        or value.get("result_kind") != "EXACT_CYCLIC_TRIVIAL_TERNARY_STABILIZATION_AND_THEORY_IDENTITY_PREFLIGHT"
        or value.get("result_state") != "STABILIZED_Q3_CANDIDATE_AND_ARITY_THREE_CERTIFIED_AUTHORITATIVE_NONMINIMAL_IDENTITY_OPEN"
        or value.get("lifecycle") != "CLASSIFIED"
    ):
        errors.append("identity/lifecycle drift")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]:
        errors.append("dependency-tag drift")
    for name, (path, expected) in FILES.items():
        source = sources[name]
        if (source.get("result_id") or source.get("schema")) != expected:
            errors.append("source identity " + name)

    rows = sources["pairing"].get("component_basis", {}).get("rows", [])
    if len(rows) != 386 or [row.get("index") for row in rows] != list(range(386)):
        return errors + ["386-row basis drift"]
    try:
        symbols, counts = infer(rows)
    except (KeyError, TypeError, ValueError) as error:
        return errors + ["symbol inference: " + str(error)]
    if counts != {"c": 4, "omega": 1, "h": 10, "h_star": 10, "c_star": 4, "omega_star": 1}:
        errors.append("minimal endpoint census")
    endpoint_indices = {row["index"] for row in rows if row["block"] in ENDPOINTS}
    q1_crossings = sum(
        table.get("source_block", "").startswith("ENDPOINT_") != table.get("target_block", "").startswith("ENDPOINT_")
        for table in sources["q1"].get("q1_serialization", {}).get("tables", [])
    )
    pairing_crossings = sum(
        (entry.get("left_index") in endpoint_indices) != (entry.get("right_index") in endpoint_indices)
        for entry in sources["pairing"].get("pairing_serialization", {}).get("entries", [])
    )
    if len(endpoint_indices) != 30 or q1_crossings or pairing_crossings:
        errors.append("direct-sum hypotheses")

    shear = sources["shear"]
    origins = {block: {block} for block in ENDPOINTS}
    for table in shear.get("canonical_transform", {}).get("inverse", {}).get("tables", []):
        if table.get("target_block") in ENDPOINTS:
            origins[table["target_block"]].add(table.get("source_block"))
    targets = {block: {block} for block in ENDPOINTS}
    for table in shear.get("canonical_transform", {}).get("forward", {}).get("tables", []):
        if table.get("source_block") in ENDPOINTS:
            targets[table["source_block"]].add(table.get("target_block"))
    h_origins = sorted(origins[symbols["h"]])
    hstar_targets = sorted(targets[symbols["h_star"]])
    channels = sorted(
        [
            {"component_id": "q3_hstar_hhh", "output_block": output, "input_blocks": [a, b, c]}
            for output in hstar_targets for a, b, c in product(h_origins, repeat=3)
        ],
        key=lambda item: (item["output_block"], *item["input_blocks"]),
    )
    block_counts = Counter(row["block"] for row in rows)
    active_inputs = sorted({block for item in channels for block in item["input_blocks"]})
    active_outputs = sorted({item["output_block"] for item in channels})
    inert_blocks = sorted(set(block_counts) - set(active_inputs) - set(active_outputs))

    q2, q3, arity3, cyclicity = sources["q2"], sources["q3"], sources["arity3"], sources["cyclicity"]
    expected_split = {
        "construction_kind": "CYCLIC_TRIVIAL_TERNARY_STABILIZATION_CANDIDATE",
        "formula": "q3_split(x,y,z)=i_end q3_min(pi_end x,pi_end y,pi_end z)",
        "carrier_rows": 386,
        "minimal_endpoint_rows": 30,
        "contractible_rows_with_zero_split_interactions": 356,
        "minimal_species_component_counts": counts,
        "minimal_q3_nonzero_components": 1,
        "minimal_q3_zero_output_rows": 5,
        "split_q1_endpoint_complement_crossings": q1_crossings,
        "split_pairing_endpoint_complement_crossings": pairing_crossings,
        "minimal_q3_import_sha256": q3["canonical_hashes"]["import_bridge_sha256"],
        "minimal_arity_three_receiver_sha256": arity3["canonical_hashes"]["exact_receiver_sha256"],
        "minimal_q3_cyclicity_sha256": cyclicity["canonical_hashes"]["cyclic_four_form_sha256"],
        "same_stabilization_q2_candidate_sha256": q2["canonical_hashes"]["split_candidate_sha256"],
    }
    expected_split["sha256"] = digest(expected_split)
    if value.get("split_candidate") != expected_split:
        errors.append("split candidate replay")

    dag = value.get("graph_transport_dag", {})
    try:
        forward = [table_summary(table) for table in shear["canonical_transform"]["forward"]["tables"]]
        inverse = [table_summary(table) for table in shear["canonical_transform"]["inverse"]["tables"]]
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
        return errors + ["shear replay: " + str(error)]
    expected_nodes = [
        {"node_id": "inverse_input_1", "operation": "S^-1", "sha256": shear["canonical_shear_snapshot"]["inverse_sha256"]},
        {"node_id": "inverse_input_2", "operation": "S^-1", "sha256": shear["canonical_shear_snapshot"]["inverse_sha256"]},
        {"node_id": "inverse_input_3", "operation": "S^-1", "sha256": shear["canonical_shear_snapshot"]["inverse_sha256"]},
        {"node_id": "minimal_q3", "operation": "q3_min after endpoint projection", "sha256": q3["canonical_hashes"]["import_bridge_sha256"]},
        {"node_id": "forward_output", "operation": "S", "sha256": shear["canonical_shear_snapshot"]["forward_sha256"]},
    ]
    dag_projection = {
        "construction_kind": dag.get("construction_kind"),
        "formula": dag.get("formula"),
        "nodes": dag.get("nodes"),
        "forward_tables": dag.get("forward_tables"),
        "inverse_tables": dag.get("inverse_tables"),
        "input_origins_for_h": dag.get("input_origins_for_h"),
        "output_targets_for_h_star": dag.get("output_targets_for_h_star"),
        "active_input_blocks": dag.get("active_input_blocks"),
        "active_output_blocks": dag.get("active_output_blocks"),
        "active_input_row_envelope": dag.get("active_input_row_envelope"),
        "active_output_row_envelope": dag.get("active_output_row_envelope"),
        "expanded_ternary_block_channels": dag.get("expanded_ternary_block_channels"),
        "total_ordered_carrier_block_quadruples": dag.get("total_ordered_carrier_block_quadruples"),
        "excluded_from_support_envelope_block_quadruples": dag.get("excluded_from_support_envelope_block_quadruples"),
        "ternary_block_channel_ledger": dag.get("ternary_block_channel_ledger"),
        "interaction_inert_blocks": dag.get("interaction_inert_blocks"),
        "interaction_inert_rows": dag.get("interaction_inert_rows"),
        "support_envelope_warning": dag.get("support_envelope_warning"),
    }
    expected_dag = {
        "construction_kind": "EXACT_CANONICAL_TERNARY_TRANSPORT_DAG",
        "formula": "q3_graph(x,y,z)=S q3_split(S^-1 x,S^-1 y,S^-1 z)",
        "nodes": expected_nodes,
        "forward_tables": forward,
        "inverse_tables": inverse,
        "input_origins_for_h": h_origins,
        "output_targets_for_h_star": hstar_targets,
        "active_input_blocks": active_inputs,
        "active_output_blocks": active_outputs,
        "active_input_row_envelope": sum(block_counts[block] for block in active_inputs),
        "active_output_row_envelope": sum(block_counts[block] for block in active_outputs),
        "expanded_ternary_block_channels": len(channels),
        "total_ordered_carrier_block_quadruples": len(block_counts) ** 4,
        "excluded_from_support_envelope_block_quadruples": len(block_counts) ** 4 - len(channels),
        "ternary_block_channel_ledger": channels,
        "interaction_inert_blocks": inert_blocks,
        "interaction_inert_rows": sum(block_counts[block] for block in inert_blocks),
        "support_envelope_warning": "A block channel is a potentially nonzero compositional path, not a flattened 386-row coefficient tensor.",
    }
    if dag_projection != expected_dag or dag.get("sha256") != digest(expected_dag):
        errors.append("graph transport DAG replay")
    if (len(channels), expected_dag["active_input_row_envelope"], expected_dag["active_output_row_envelope"], expected_dag["interaction_inert_rows"]) != (16, 50, 50, 286):
        errors.append("ternary envelope census")

    identity = value.get("identity_transport", {})
    arity = identity.get("q1_q2_q3_arity_three", {})
    cyclic = identity.get("q3_cyclicity_mod_d", {})
    d_q3 = identity.get("D_q3_derivation", {})
    if arity.get("status") != "VERIFIED_BY_ORTHOGONAL_DIRECT_SUM_AND_EXACT_CONJUGATION" or arity.get("minimal_typed_channels") != 72 or arity.get("minimal_composable_paths") != 212 or arity.get("defects") != 0:
        errors.append("arity-three transport")
    if identity.get("q3_S3_symmetry", {}).get("minimal_input_permutations") != 6 or identity.get("q3_S3_symmetry", {}).get("defects") != 0:
        errors.append("S3 transport")
    if cyclic.get("status") != "VERIFIED_BY_ORTHOGONAL_DIRECT_SUM_AND_BV_CANONICAL_TRANSPORT" or cyclic.get("minimal_permutation_group") != "S4" or cyclic.get("minimal_cyclicity_defect_mod_d") != "0" or cyclic.get("defects_mod_d") != 0:
        errors.append("cyclicity transport")
    if d_q3.get("status") != "VERIFIED_FOR_STABILIZED_CANDIDATE_BY_STATIONARY_NATURALITY_AND_CONJUGATION" or d_q3.get("shear_tables_checked") != 14 or d_q3.get("shear_rational_coefficients_checked") != 2642 or d_q3.get("derivation_defects") != 0:
        errors.append("D/q3 transport")

    theory = value.get("theory_identity_boundary", {})
    if not (
        theory.get("candidate_status") == "CERTIFIED_CONSTRUCTION_NOT_AUTHORITATIVE_NONMINIMAL_IMPORT"
        and theory.get("authoritative_full_386_row_q3_export_present") is False
        and theory.get("source_certified_cyclic_L_infinity_equivalence_present") is False
        and theory.get("candidate_equals_authoritative_nonminimal_classical_theory") == "NOT_ESTABLISHED"
        and theory.get("candidate_general_local_arity_three_identity") is True
        and theory.get("candidate_causal_lambda2_source_closure") is False
    ):
        errors.append("authoritative theory firewall")
    flags = value.get("claim_flags", {})
    true_flags = (
        "STRICT_386_STABILIZED_Q3_CANDIDATE_CONSTRUCTED",
        "STRICT_386_STABILIZED_Q1_Q2_Q3_ARITY_THREE_IDENTITY_VERIFIED",
        "STRICT_386_STABILIZED_Q3_S3_SYMMETRY_VERIFIED",
        "STRICT_386_STABILIZED_Q3_CYCLICITY_MOD_D_VERIFIED",
        "STRICT_386_STABILIZED_D_Q3_DERIVATION_VERIFIED",
    )
    false_flags = (
        "STRICT_386_AUTHORITATIVE_FULL_Q3_IMPORTED",
        "STRICT_386_CANDIDATE_AUTHORITATIVE_EQUIVALENCE_CERTIFIED",
        "STRICT_386_CANDIDATE_CAUSAL_LAMBDA2_SOURCE_CLOSURE_CERTIFIED",
        "CLASSICAL_IMPORT_GATE_PASSED",
        "HADAMARD_STATE_CONSTRUCTED",
        "RENORMALIZED_LORENTZIAN_PRODUCTS",
        "QME_RESTORED",
        "RESIDUAL_TRANSFERRED",
        "LORENTZIAN_QUANTUM_THEORY",
    )
    if any(flags.get(key) is not True for key in true_flags) or any(flags.get(key) is not False for key in false_flags):
        errors.append("claim flag promotion")
    expected_hashes = {
        "split_candidate_sha256": digest(value.get("split_candidate")),
        "graph_transport_dag_sha256": digest(value.get("graph_transport_dag")),
        "identity_transport_sha256": digest(identity),
        "theory_identity_boundary_sha256": digest(theory),
        "gate_disposition_sha256": digest(value.get("gate_disposition")),
        "foundational_strength_sha256": digest(value.get("foundational_strength")),
    }
    if value.get("canonical_hashes") != expected_hashes:
        errors.append("canonical hashes")
    provenance = value.get("provenance", {}).get("inputs", [])
    expected_provenance = {(str(path.relative_to(ROOT)), expected, sha(path)) for path, expected in FILES.values()}
    actual_provenance = {(item.get("path"), item.get("result_id"), item.get("sha256")) for item in provenance}
    if actual_provenance != expected_provenance:
        errors.append("input provenance")
    if len(value.get("does_not_establish", [])) < 7:
        errors.append("does-not-establish ledger")
    return errors


def main() -> int:
    errors = check()
    print("STRICT_386_STABILIZED_Q3_LIFT_PREFLIGHT_V1_CHECK: " + ("PASS" if not errors else "FAIL"))
    for item in errors:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
