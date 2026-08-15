#!/usr/bin/env python3
"""Independent audit of the common source q3 snapshot and identity partition."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1.json"
Q1 = HERE / "certificates/STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
SHEAR = HERE / "certificates/STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1.json"
Q2 = HERE / "certificates/STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1.json"
MINIMAL_Q3 = HERE / "certificates/STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1.json"
MINIMAL_ARITY3 = HERE / "certificates/STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1.json"
MINIMAL_CYCLIC = HERE / "certificates/STRICT_MINIMAL_BV_Q3_CYCLICITY_V1.json"
AUXILIARY_Q3 = HERE / "certificates/STRICT_386_SHIFTED_MASS_BV_Q3_LIFT_V1.json"
CLASSICAL_QUARTIC = ROOT / "d_quotient_classical/certificates/CLASSICAL_SHIFTED_AUXILIARY_QUARTIC_MASS_V1.json"
MANIFEST = ROOT / "d_quotient_classical/certificates/CLASSICAL_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST_V1.json"
ACTION_SPLIT = ROOT / "covariant_completion/certificates/curved_presymplectic_potentials.json"
D_ACTION = HERE / "certificates/STRICT_386_FULL_D_ACTION_V1.json"
INPUTS = (
    (Q1, "STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1"),
    (PAIRING, "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1"),
    (SHEAR, "STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1"),
    (Q2, "STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1"),
    (MINIMAL_Q3, "STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1"),
    (MINIMAL_ARITY3, "STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1"),
    (MINIMAL_CYCLIC, "STRICT_MINIMAL_BV_Q3_CYCLICITY_V1"),
    (AUXILIARY_Q3, "STRICT_386_SHIFTED_MASS_BV_Q3_LIFT_V1"),
    (CLASSICAL_QUARTIC, "CLASSICAL_SHIFTED_AUXILIARY_QUARTIC_MASS_V1"),
    (MANIFEST, "CLASSICAL_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST_V1"),
    (ACTION_SPLIT, "pure-weyl-curved-presymplectic-potential-status-v1"),
    (D_ACTION, "STRICT_386_FULL_D_ACTION_V1"),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def auxiliary_ledger(auxiliary: dict[str, Any]) -> list[dict[str, Any]]:
    lift = auxiliary["shifted_mass_q3_lift"]
    result = [
        {"family_id": lift["family_id"], "output_kind": kind, **row}
        for kind, key in (("metric_antifield_output", "metric_antifield_output_entries"), ("auxiliary_antifield_output", "auxiliary_antifield_output_entries"))
        for row in lift[key]
    ]
    return sorted(result, key=lambda row: (row["output_index"], row["input_indices"], row["input_jets"], row["output_kind"]))


def graph_envelope(pairing: dict[str, Any], shear: dict[str, Any], ledger: list[dict[str, Any]]) -> dict[str, Any]:
    rows = pairing["component_basis"]["rows"]
    row_block = {row["index"]: row["block"] for row in rows}
    counts = Counter(row_block.values())
    source = {("ENDPOINT_E", "ENDPOINT_M", "ENDPOINT_M", "ENDPOINT_M")}
    source |= {(row_block[row["output_index"]], *(row_block[index] for index in row["input_indices"])) for row in ledger}
    origins, targets = {block: {block} for block in counts}, {block: {block} for block in counts}
    for table in shear["canonical_transform"]["inverse"]["tables"]:
        origins[table["target_block"]].add(table["source_block"])
    for table in shear["canonical_transform"]["forward"]["tables"]:
        targets[table["source_block"]].add(table["target_block"])
    graph = sorted({
        (out2, left2, middle2, right2)
        for output, left, middle, right in source
        for out2 in targets[output]
        for left2 in origins[left]
        for middle2 in origins[middle]
        for right2 in origins[right]
    })
    inputs = sorted({block for _, left, middle, right in graph for block in (left, middle, right)})
    outputs = sorted({output for output, _, _, _ in graph})
    return {
        "source_block_quadruples": len(source),
        "source_block_quadruple_ledger": [{"output_block": output, "input_blocks": [left, middle, right]} for output, left, middle, right in sorted(source)],
        "graph_block_quadruples": len(graph),
        "graph_block_quadruple_ledger": [{"output_block": output, "input_blocks": [left, middle, right]} for output, left, middle, right in graph],
        "active_graph_input_blocks": inputs,
        "active_graph_output_blocks": outputs,
        "active_graph_input_row_envelope": sum(counts[block] for block in inputs),
        "active_graph_output_row_envelope": sum(counts[block] for block in outputs),
        "transport_formula": "q3_graph(x,y,z)=S q3_shifted_split(S^-1 x,S^-1 y,S^-1 z)",
        "flattened_graph_tensor_exported": False,
        "exact_compositional_DAG_exported": True,
    }


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = value or json.loads(RESULT.read_text())
    values = {path: json.loads(path.read_text()) for path, _ in INPUTS}
    q1, pairing, shear, q2, minimal, minimal_identity, minimal_cyclic, auxiliary, quartic, manifest, action_split, d_action = (values[path] for path, _ in INPUTS)
    errors: list[str] = []
    if value.get("result_id") != "STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1" or value.get("lifecycle") != "CLASSIFIED" or value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]:
        errors.append("identity/lifecycle/dependency boundary")
    rows = pairing["component_basis"]["rows"]
    if len(rows) != 386 or [row["index"] for row in rows] != list(range(386)):
        errors.append("fixed carrier")
    ledger = auxiliary_ledger(auxiliary)
    keys = [(row["output_index"], tuple(row["input_indices"]), tuple(tuple(jet) for jet in row["input_jets"])) for row in ledger]
    collisions = len(keys) - len(set(keys))
    if len(ledger) != 5952 or collisions:
        errors.append("auxiliary ledger count/collisions")

    family = {
        "minimal_q3_families": 1, "auxiliary_q3_families": 1, "total_source_q3_families": 2,
        "families": [
            {"family_id": "MINIMAL_BACH_H_H_H_TO_H_STAR", "authority": minimal["result_id"], "input_jet_order": 4, "serialization": "natural-operator AST"},
            {"family_id": "SHIFTED_MASS_H_H_F_HAT_F_HAT", "authority": auxiliary["result_id"], "input_jet_order": 0, "serialization": "exact component ledger"},
        ],
        "additional_quartic_ghost_antifield_families": 0,
        "reason": "In shifted variables the only auxiliary BRST nonlinearity is the bilinear Diff representation; internal Weyl/boost rows are unary or zero. The exact action modulo d is minimal plus the metric-dependent quadratic f_hat mass. Therefore its fourth Taylor coefficient has exactly the two displayed families.",
        "source_q3_family_census_exhaustive": True, "higher_q4_and_above_excluded_from_claim": True,
    }
    if value.get("family_census") != family:
        errors.append("q3 family census")
    snapshot = {
        "coordinate_presentation": "SHIFTED_SPLIT_SOURCE_COORDINATES", "carrier_rows": 386, "source_theory_rows": 66,
        "receiver_added_split_cone_rows_extended_by_zero": 320, "minimal_natural_operator_components": 1,
        "auxiliary_ordered_component_coefficients": len(ledger), "auxiliary_component_collisions": collisions,
        "minimal_q3_import_sha256": minimal["canonical_hashes"]["import_bridge_sha256"],
        "auxiliary_component_ledger_sha256": digest(ledger), "family_census_sha256": digest(family),
        "accepted_q2_snapshot_sha256": q2["source_q2_snapshot"]["sha256"],
        "source_q3_complete_at_arity_three": True,
    }
    snapshot["sha256"] = digest(snapshot)
    if value.get("source_q3_snapshot") != snapshot:
        errors.append("source q3 snapshot")

    ward = quartic["exact_replay"]
    arity = value.get("arity_three_replay", {})
    prerequisites = (
        minimal_identity["claim_flags"].get("MINIMAL_BV_ARITY_THREE_IDENTITY_CERTIFIED") is True,
        minimal_identity["exact_receiver"].get("all_72_channel_defects_zero") is True,
        action_split.get("compatible_curved_BV_potential_convention", {}).get("shifted_action") == "U^*L_aux=L_met+1/2<f_hat,A_g f_hat>+dB_elim",
        manifest["shifted_auxiliary_covariance"]["boost"].get("f_hat_boost_invariant") is True,
        manifest["shifted_auxiliary_covariance"]["Weyl"].get("f_hat_Weyl_invariant") is True,
        manifest["manifest_summary"].get("additional_nonlinear_Weyl_boost_ghost_antifield_families") == 0,
        ward.get("pure_trace_second_variation_defects") == 0,
        ward.get("mixed_conformal_recursion_defects") == 0,
    )
    if not all(prerequisites):
        errors.append("arity-three proof prerequisites")
    if arity.get("minimal_sector", {}).get("typed_channels") != 72 or arity.get("minimal_sector", {}).get("composable_paths") != 212:
        errors.append("minimal arity-three ledger")
    if arity.get("auxiliary_Weyl_sector", {}).get("pure_trace_checks") != 55 or arity.get("auxiliary_Weyl_sector", {}).get("mixed_recursion_checks") != 550:
        errors.append("auxiliary Weyl Ward ledger")
    for sector in ("minimal_sector", "auxiliary_Diff_sector", "auxiliary_Weyl_sector", "auxiliary_boost_sector"):
        if arity.get(sector, {}).get("defects", arity.get(sector, {}).get("exact_receiver_defects")) != 0:
            errors.append("arity-three sector defect: " + sector)
    if arity.get("unclassified_arity_three_families") != 0 or arity.get("split_386_arity_three_defects") != 0 or arity.get("graph_386_arity_three_defects") != 0:
        errors.append("common arity-three boundary")

    cyclic = value.get("q3_cyclicity_replay", {})
    if cyclic.get("minimal_q3_defects_mod_d") != minimal_cyclic["cyclic_four_form"]["cyclicity_defect_mod_d"] or cyclic.get("auxiliary_q3_equalities_checked") != 40000 or cyclic.get("auxiliary_q3_pointwise_defects") != 0 or cyclic.get("split_386_q3_cyclicity_defects_mod_d") != 0 or cyclic.get("graph_386_q3_cyclicity_defects_mod_d") != 0:
        errors.append("q3 cyclicity replay")
    d_replay = value.get("D_q3_replay", {})
    if d_replay.get("split_D_q3_derivation_defects") != 0 or d_replay.get("graph_D_q3_derivation_defects") != 0 or d_replay.get("minimal_natural_q3_families") != 1 or d_replay.get("auxiliary_zero_jet_q3_families") != 1:
        errors.append("D/q3 derivation replay")
    graph = graph_envelope(pairing, shear, ledger)
    if value.get("graph_transport") != graph or graph["graph_block_quadruples"] != 40:
        errors.append("graph q3 transport")

    hashes = value.get("canonical_hashes", {})
    payloads = {
        "family_census_sha256": family, "source_q3_snapshot_sha256": snapshot,
        "arity_three_replay_sha256": arity, "q3_cyclicity_replay_sha256": cyclic,
        "D_q3_replay_sha256": d_replay, "graph_transport_sha256": graph,
        "gate_boundary_sha256": value.get("gate_boundary"), "foundational_strength_sha256": value.get("foundational_strength"),
    }
    if hashes != {name: digest(payload) for name, payload in payloads.items()}:
        errors.append("canonical hashes")
    pins = value.get("provenance", {}).get("inputs", [])
    if len(pins) != len(INPUTS):
        errors.append("provenance count")
    else:
        for row, (path, expected) in zip(pins, INPUTS):
            if row.get("path") != str(path.relative_to(ROOT)) or row.get("result_id") != expected or row.get("sha256") != sha(path):
                errors.append("provenance " + path.name)
    flags = value.get("claim_flags", {})
    for name in ("FULL_SHIFTED_SOURCE_Q3_COMMON_UNION_ASSEMBLED", "FULL_386_GRAPH_Q3_COMPOSITIONAL_DAG_ASSEMBLED", "FULL_386_ARITY_THREE_IDENTITY_REPLAYED", "FULL_386_Q3_CYCLICITY_REPLAYED_MOD_D", "FULL_386_D_Q3_DERIVATION_REPLAYED", "FULL_SOURCE_Q3_ASSEMBLED"):
        if flags.get(name) is not True:
            errors.append("claim flag " + name)
    for name in ("CLASSICAL_IMPORT_GATE_PASSED", "LORENTZIAN_GREEN_Q3_COMPATIBILITY_CERTIFIED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED"):
        if flags.get(name) is not False:
            errors.append("fail-closed flag " + name)
    return errors


def main() -> int:
    errors = check()
    print("STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1_INDEPENDENT_AUDIT: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
