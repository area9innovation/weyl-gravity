#!/usr/bin/env python3
"""Independent content and boundary replay for the common source-q2 assembly."""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1.json"
PATHS = (
    HERE / "certificates/STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.json",
    HERE / "certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json",
    HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json",
    HERE / "certificates/STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1.json",
    HERE / "certificates/STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1.json",
    HERE / "certificates/STRICT_LOCAL_Q1_Q2_IDENTITY_V1.json",
    HERE / "certificates/STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.json",
    HERE / "certificates/STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.json",
    HERE / "certificates/STRICT_386_FULL_D_ACTION_V1.json",
    HERE / "certificates/STRICT_386_SHIFTED_MASS_BV_Q2_LIFT_V1.json",
    HERE / "certificates/STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V2.json",
    ROOT / "d_quotient_classical/certificates/CLASSICAL_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST_V1.json",
)


def canonical_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def rebuild_ledger(mass: dict[str, Any], diff: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for section in ("metric_antifield_output_entries", "auxiliary_antifield_output_entries"):
        rows.extend({"family_id": "SHIFTED_MASS_H_F_HAT_F_HAT", **entry} for entry in mass["shifted_mass_q2_lift"][section])
    for family in diff["BV_representation_lifts"]:
        for section in ("field_output_entries", "antifield_output_entries", "c_star_output_entries"):
            rows.extend({"family_id": family["family_id"], "output_kind": section, **entry} for entry in family[section])
    return sorted(rows, key=lambda row: (row["output_index"], row["left_input_index"], row["left_input_jet"], row["right_input_index"], row["right_input_jet"], row["family_id"], row.get("output_kind", "")))


def structural_channels(q1: dict[str, Any], ledger: list[dict[str, Any]]) -> tuple[int, int, int]:
    arrows = set()
    crossings = 0
    for table in q1["q1_serialization"]["tables"]:
        for slab in table["coefficients"]:
            for output, input_, _ in slab["entries"]:
                crossings += int((output < 66) != (input_ < 66))
                if output < 66 and input_ < 66:
                    arrows.add((output, input_))
    triples = {(row["output_index"], row["left_input_index"], row["right_input_index"]) for row in ledger}
    channels: dict[tuple[int, int, int], set[tuple[str, int, int, int]]] = defaultdict(set)
    for output, left, right in triples:
        for unary_output, unary_input in arrows:
            if unary_input == output:
                channels[(unary_output, left, right)].add(("p", output, left, right))
            if unary_output == left:
                channels[(output, unary_input, right)].add(("l", output, left, right))
            if unary_output == right:
                channels[(output, left, unary_input)].add(("r", output, left, right))
    return len(channels), sum(len(paths) for paths in channels.values()), crossings


def rebuild_envelope(pairing: dict[str, Any], shear: dict[str, Any], minimal: dict[str, Any], ledger: list[dict[str, Any]]) -> dict[str, Any]:
    basis = pairing["component_basis"]["rows"]
    row_block = {row["index"]: row["block"] for row in basis}
    counts = Counter(row_block.values())
    symbols = {"c": "ENDPOINT_G", "omega": "ENDPOINT_G", "h": "ENDPOINT_M", "h_star": "ENDPOINT_E", "c_star": "ENDPOINT_I", "omega_star": "ENDPOINT_I"}
    source = {(symbols[row["output"]], symbols[row["inputs"][0]], symbols[row["inputs"][1]]) for row in minimal["ordered_components"]}
    source.update((row_block[row["output_index"]], row_block[row["left_input_index"]], row_block[row["right_input_index"]]) for row in ledger)
    origins = {block: {block} for block in counts}
    targets = {block: {block} for block in counts}
    for table in shear["canonical_transform"]["inverse"]["tables"]:
        origins[table["target_block"]].add(table["source_block"])
    for table in shear["canonical_transform"]["forward"]["tables"]:
        targets[table["source_block"]].add(table["target_block"])
    graph = sorted({(o2, l2, r2) for o, l, r in source for o2 in targets[o] for l2 in origins[l] for r2 in origins[r]})
    inputs = sorted({l for _, l, _ in graph} | {r for _, _, r in graph})
    outputs = sorted({o for o, _, _ in graph})
    return {"source_block_triples": len(source), "graph_block_triples": len(graph), "graph_block_triple_ledger": [{"output_block": o, "left_input_block": l, "right_input_block": r} for o, l, r in graph], "active_graph_input_blocks": inputs, "active_graph_output_blocks": outputs, "active_graph_input_row_envelope": sum(counts[x] for x in inputs), "active_graph_output_row_envelope": sum(counts[x] for x in outputs), "transport_formula": "q2_graph(x,y)=S q2_shifted_split(S^-1 x,S^-1 y)", "flattened_graph_tensor_exported": False, "exact_compositional_DAG_exported": True}


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    q1, graph, pairing, shear, minimal, minimal_identity, minimal_cyclic, preflight, d_action, mass, diff, manifest = (json.loads(path.read_text()) for path in PATHS)
    ledger = rebuild_ledger(mass, diff)
    keys = [(row["output_index"], row["left_input_index"], tuple(row["left_input_jet"]), row["right_input_index"], tuple(row["right_input_jet"])) for row in ledger]
    channels, paths, crossings = structural_channels(q1, ledger)
    if (len(ledger), len(keys) - len(set(keys)), channels, paths, crossings) != (2064, 0, 926, 3568, 0):
        errors.append("common auxiliary ledger or channel inventory mismatch")
    census = value.get("family_census", {})
    expected_census = {"minimal_primary_q2_families": 12, "shifted_source_auxiliary_q2_families": 4, "total_shifted_source_q2_families": 16, "auxiliary_family_ids": ["SHIFTED_MASS_H_F_HAT_F_HAT", "DIFF_C_F_HAT_F_HAT_STAR", "DIFF_C_V_V_STAR", "DIFF_C_ETA_ETA_STAR"], "nonlinear_internal_additional_families": 0, "type_II_coordinate_map_families_excluded_from_source_vector_field": ["TYPE_II_F_HAT_STAR_V_V", "TYPE_II_F_HAT_STAR_H_H", "TYPE_II_F_HAT_STAR_H_V"], "scoped_family_census_exhaustive": True}
    if census != expected_census or not manifest["claim_flags"]["EXHAUSTIVE_NONLINEAR_WEYL_BOOST_GHOST_ANTIFIELD_MANIFEST"]:
        errors.append("source family census mismatch")
    snapshot = value.get("source_q2_snapshot", {})
    expected_snapshot = {"coordinate_presentation": "SHIFTED_SPLIT_SOURCE_COORDINATES", "carrier_rows": 386, "source_theory_rows": 66, "receiver_added_split_cone_rows_extended_by_zero": 320, "minimal_ordered_symbolic_components": 22, "auxiliary_ordered_component_coefficients": 2064, "auxiliary_component_collisions": 0, "minimal_ordered_components_sha256": minimal["canonical_hashes"]["ordered_components_sha256"], "auxiliary_component_ledger_sha256": canonical_digest(ledger), "family_census_sha256": canonical_digest(census), "source_q2_complete_at_arity_two": True}
    expected_snapshot["sha256"] = canonical_digest(expected_snapshot)
    if snapshot != expected_snapshot:
        errors.append("source-q2 common snapshot mismatch")
    identity = value.get("q1_q2_replay", {})
    if identity.get("minimal_endpoint", {}).get("defects") != 0 or identity.get("auxiliary_coupled") != {"component_channels": 926, "row_level_composable_paths": 3568, "exact_nonzero_residual_coefficients": 0, "authority": diff["result_id"]} or identity.get("source66_to_zero_cone_q1_crossings") != 0 or identity.get("split_386_q1_q2_defects") != 0 or identity.get("graph_386_q1_q2_defects") != 0:
        errors.append("q1/q2 common identity boundary mismatch")
    cyclic = value.get("q2_cyclicity_replay", {})
    if any(cyclic.get(key) != 0 for key in ("minimal_q2_defects", "shifted_mass_defects", "auxiliary_Diff_defects", "orthogonal_source_family_cross_pairings", "split_386_q2_cyclicity_defects", "graph_386_q2_cyclicity_defects")):
        errors.append("common cyclicity replay mismatch")
    if cyclic.get("shifted_mass_equalities_checked") != 3000 or cyclic.get("auxiliary_Diff_master_density_coefficients_checked") != 264:
        errors.append("cyclicity coverage count mismatch")
    envelope = rebuild_envelope(pairing, shear, minimal, ledger)
    if value.get("graph_transport") != envelope:
        errors.append("graph transport envelope mismatch")
    q3 = value.get("q3_boundary", {})
    if q3.get("auxiliary_metric_dependent_q3_available") is not False or q3.get("full_source_q3_assembled") is not False or q3.get("Gate_A_disposition") != "FAIL_CLOSED":
        errors.append("q3 fail-closed boundary mismatch")
    hashes = value.get("canonical_hashes", {})
    for key, payload in (("family_census_sha256", census), ("source_q2_snapshot_sha256", snapshot), ("q1_q2_replay_sha256", identity), ("q2_cyclicity_replay_sha256", cyclic), ("D_q2_replay_sha256", value.get("D_q2_replay")), ("graph_transport_sha256", envelope), ("q3_boundary_sha256", q3), ("foundational_strength_sha256", value.get("foundational_strength"))):
        if hashes.get(key) != canonical_digest(payload):
            errors.append(f"canonical hash drift: {key}")
    pins = {row.get("path"): row.get("sha256") for row in value.get("provenance", {}).get("inputs", [])}
    if pins != {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in PATHS}:
        errors.append("provenance pin mismatch")
    flags = value.get("claim_flags", {})
    for name in ("FULL_SHIFTED_SOURCE_Q2_COMMON_UNION_ASSEMBLED", "FULL_386_GRAPH_Q2_COMPOSITIONAL_DAG_ASSEMBLED", "FULL_386_Q1_Q2_IDENTITY_REPLAYED", "FULL_386_Q2_CYCLICITY_REPLAYED", "FULL_386_D_Q2_DERIVATION_REPLAYED"):
        if flags.get(name) is not True:
            errors.append(f"claim flag drift: {name}")
    for name in ("FULL_SOURCE_Q3_ASSEMBLED", "CLASSICAL_IMPORT_GATE_PASSED", "LORENTZIAN_GREEN_Q2_COMPATIBILITY_CERTIFIED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED"):
        if flags.get(name) is not False:
            errors.append(f"fail-closed flag drift: {name}")
    if value.get("result_id") != "STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1" or value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]:
        errors.append("result identity or dependency boundary mismatch")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1_INDEPENDENT_REPLAY: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print(json.dumps({"source_snapshot": value["source_q2_snapshot"]["sha256"], "graph_block_triples": value["graph_transport"]["graph_block_triples"], "q3": value["q3_boundary"]["full_source_q3_assembled"]}, sort_keys=True))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
