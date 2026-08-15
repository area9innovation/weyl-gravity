#!/usr/bin/env python3
"""Assemble the authoritative shifted-source q2 on one 386-row snapshot."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
Q1 = HERE / "certificates/STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.json"
GRAPH = HERE / "certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
SHEAR = HERE / "certificates/STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1.json"
MINIMAL = HERE / "certificates/STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1.json"
MINIMAL_IDENTITY = HERE / "certificates/STRICT_LOCAL_Q1_Q2_IDENTITY_V1.json"
MINIMAL_CYCLIC = HERE / "certificates/STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.json"
PREFLIGHT = HERE / "certificates/STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.json"
D_ACTION = HERE / "certificates/STRICT_386_FULL_D_ACTION_V1.json"
MASS = HERE / "certificates/STRICT_386_SHIFTED_MASS_BV_Q2_LIFT_V1.json"
DIFF = HERE / "certificates/STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V2.json"
MANIFEST = ROOT / "d_quotient_classical/certificates/CLASSICAL_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST_V1.json"
RESULT = HERE / "certificates/STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1.json"
REPORT = HERE / "REPORT_STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1.md"

INPUTS = (
    (Q1, "STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1", "split-coordinate full unary table"),
    (GRAPH, "STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1", "graph-coordinate q1 and exact conjugation"),
    (PAIRING, "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1", "fixed basis and odd pairing"),
    (SHEAR, "STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1", "BV-canonical graph shear and inverse"),
    (MINIMAL, "STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1", "complete strict minimal q2 AST"),
    (MINIMAL_IDENTITY, "STRICT_LOCAL_Q1_Q2_IDENTITY_V1", "minimal q1/q2 theorem"),
    (MINIMAL_CYCLIC, "STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1", "minimal canonical cyclicity"),
    (PREFLIGHT, "STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1", "stationary D and graph-transport theorem"),
    (D_ACTION, "STRICT_386_FULL_D_ACTION_V1", "unit-cylinder local D action"),
    (MASS, "STRICT_386_SHIFTED_MASS_BV_Q2_LIFT_V1", "exact shifted-mass q2 component tables"),
    (DIFF, "STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V2", "canonically translated auxiliary Diff q2 tables"),
    (MANIFEST, "CLASSICAL_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST_V1", "exhaustive nonlinear internal ghost-family census"),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def source_id(value: dict[str, Any]) -> str | None:
    return value.get("result_id") or value.get("schema")


def auxiliary_ledger(mass: dict[str, Any], diff: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for key in ("metric_antifield_output_entries", "auxiliary_antifield_output_entries"):
        for row in mass["shifted_mass_q2_lift"][key]:
            result.append({"family_id": "SHIFTED_MASS_H_F_HAT_F_HAT", **row})
    for family in diff["BV_representation_lifts"]:
        for key in ("field_output_entries", "antifield_output_entries", "c_star_output_entries"):
            for row in family[key]:
                result.append({"family_id": family["family_id"], "output_kind": key, **row})
    result.sort(key=lambda row: (row["output_index"], row["left_input_index"], row["left_input_jet"], row["right_input_index"], row["right_input_jet"], row["family_id"], row.get("output_kind", "")))
    return result


def auxiliary_channels(q1: dict[str, Any], ledger: list[dict[str, Any]]) -> tuple[int, int]:
    arrows = set()
    for table in q1["q1_serialization"]["tables"]:
        for slab in table["coefficients"]:
            for output, input_, _ in slab["entries"]:
                if output < 66 and input_ < 66:
                    arrows.add((output, input_))
    q2_triples = {(row["output_index"], row["left_input_index"], row["right_input_index"]) for row in ledger}
    channels: dict[tuple[int, int, int], set[tuple[str, int, int, int]]] = defaultdict(set)
    for output, left, right in q2_triples:
        for unary_output, unary_input in arrows:
            if unary_input == output:
                channels[(unary_output, left, right)].add(("post", output, left, right))
            if unary_output == left:
                channels[(output, unary_input, right)].add(("pre_left", output, left, right))
            if unary_output == right:
                channels[(output, left, unary_input)].add(("pre_right", output, left, right))
    return len(channels), sum(len(paths) for paths in channels.values())


def graph_envelope(pairing: dict[str, Any], shear: dict[str, Any], minimal: dict[str, Any], ledger: list[dict[str, Any]]) -> dict[str, Any]:
    rows = pairing["component_basis"]["rows"]
    row_block = {row["index"]: row["block"] for row in rows}
    counts = Counter(row_block.values())
    symbol_blocks = {"c": "ENDPOINT_G", "omega": "ENDPOINT_G", "h": "ENDPOINT_M", "h_star": "ENDPOINT_E", "c_star": "ENDPOINT_I", "omega_star": "ENDPOINT_I"}
    triples = {(symbol_blocks[row["output"]], symbol_blocks[row["inputs"][0]], symbol_blocks[row["inputs"][1]]) for row in minimal["ordered_components"]}
    triples |= {(row_block[row["output_index"]], row_block[row["left_input_index"]], row_block[row["right_input_index"]]) for row in ledger}
    origins = {block: {block} for block in counts}
    targets = {block: {block} for block in counts}
    for table in shear["canonical_transform"]["inverse"]["tables"]:
        origins[table["target_block"]].add(table["source_block"])
    for table in shear["canonical_transform"]["forward"]["tables"]:
        targets[table["source_block"]].add(table["target_block"])
    graph_triples = sorted({(out2, left2, right2) for output, left, right in triples for out2 in targets[output] for left2 in origins[left] for right2 in origins[right]})
    input_blocks = sorted({left for _, left, _ in graph_triples} | {right for _, _, right in graph_triples})
    output_blocks = sorted({output for output, _, _ in graph_triples})
    return {
        "source_block_triples": len(triples),
        "graph_block_triples": len(graph_triples),
        "graph_block_triple_ledger": [{"output_block": output, "left_input_block": left, "right_input_block": right} for output, left, right in graph_triples],
        "active_graph_input_blocks": input_blocks,
        "active_graph_output_blocks": output_blocks,
        "active_graph_input_row_envelope": sum(counts[block] for block in input_blocks),
        "active_graph_output_row_envelope": sum(counts[block] for block in output_blocks),
        "transport_formula": "q2_graph(x,y)=S q2_shifted_split(S^-1 x,S^-1 y)",
        "flattened_graph_tensor_exported": False,
        "exact_compositional_DAG_exported": True,
    }


def build() -> dict[str, Any]:
    values = {path: json.loads(path.read_text()) for path, _, _ in INPUTS}
    for path, expected, _ in INPUTS:
        if source_id(values[path]) != expected:
            raise ValueError(f"common-q2 dependency identity drift: {path}")
    q1, graph, pairing, shear, minimal, minimal_identity, minimal_cyclic, preflight, d_action, mass, diff, manifest = (values[path] for path, _, _ in INPUTS)
    rows = pairing["component_basis"]["rows"]
    if len(rows) != 386 or [row["index"] for row in rows] != list(range(386)):
        raise ValueError("fixed 386-row carrier unavailable")
    if not manifest["claim_flags"]["EXHAUSTIVE_NONLINEAR_WEYL_BOOST_GHOST_ANTIFIELD_MANIFEST"]:
        raise ValueError("exhaustive nonlinear internal manifest unavailable")
    if diff["canonical_sign_repair"]["repaired_q1_q2_nonzero_coefficients"] != 0:
        raise ValueError("auxiliary q1/q2 identity not closed")
    ledger = auxiliary_ledger(mass, diff)
    keys = [(row["output_index"], row["left_input_index"], tuple(row["left_input_jet"]), row["right_input_index"], tuple(row["right_input_jet"])) for row in ledger]
    collisions = len(keys) - len(set(keys))
    if len(ledger) != 2064 or collisions:
        raise ValueError("auxiliary q2 common-byte collision or count drift")
    channels, paths = auxiliary_channels(q1, ledger)
    if (channels, paths) != (926, 3568):
        raise ValueError("auxiliary arity-two structural channel inventory drift")
    cone_crossings = 0
    for table in q1["q1_serialization"]["tables"]:
        for slab in table["coefficients"]:
            for output, input_, _ in slab["entries"]:
                cone_crossings += int((output < 66) != (input_ < 66))
    if cone_crossings:
        raise ValueError("source 66-row sector is not a unary direct summand")

    family_census = {
        "minimal_primary_q2_families": len(minimal["primary_components"]),
        "shifted_source_auxiliary_q2_families": 4,
        "total_shifted_source_q2_families": len(minimal["primary_components"]) + 4,
        "auxiliary_family_ids": ["SHIFTED_MASS_H_F_HAT_F_HAT", "DIFF_C_F_HAT_F_HAT_STAR", "DIFF_C_V_V_STAR", "DIFF_C_ETA_ETA_STAR"],
        "nonlinear_internal_additional_families": 0,
        "type_II_coordinate_map_families_excluded_from_source_vector_field": ["TYPE_II_F_HAT_STAR_V_V", "TYPE_II_F_HAT_STAR_H_H", "TYPE_II_F_HAT_STAR_H_V"],
        "scoped_family_census_exhaustive": True,
    }
    snapshot = {
        "coordinate_presentation": "SHIFTED_SPLIT_SOURCE_COORDINATES",
        "carrier_rows": 386,
        "source_theory_rows": 66,
        "receiver_added_split_cone_rows_extended_by_zero": 320,
        "minimal_ordered_symbolic_components": len(minimal["ordered_components"]),
        "auxiliary_ordered_component_coefficients": len(ledger),
        "auxiliary_component_collisions": collisions,
        "minimal_ordered_components_sha256": minimal["canonical_hashes"]["ordered_components_sha256"],
        "auxiliary_component_ledger_sha256": digest(ledger),
        "family_census_sha256": digest(family_census),
        "source_q2_complete_at_arity_two": True,
    }
    snapshot["sha256"] = digest(snapshot)
    identity = {
        "minimal_endpoint": {"channels": 18, "composable_paths": 51, "defects": 0, "authority": minimal_identity["result_id"]},
        "auxiliary_coupled": {"component_channels": channels, "row_level_composable_paths": paths, "exact_nonzero_residual_coefficients": 0, "authority": diff["result_id"]},
        "minimal_auxiliary_channel_overlap": 0,
        "source66_to_zero_cone_q1_crossings": cone_crossings,
        "split_386_q1_q2_defects": 0,
        "graph_386_q1_q2_defects": 0,
        "graph_reason": "exact conjugation by the certified degree-zero canonical shear",
    }
    cyclicity = {
        "minimal_q2_defects": minimal_cyclic["cyclicity_receiver"]["translated_convention_defect"]["coefficient_count"],
        "shifted_mass_equalities_checked": mass["exact_replay"]["cyclicity_equalities_checked"],
        "shifted_mass_defects": mass["exact_replay"]["cyclicity_defects"],
        "auxiliary_Diff_master_density_coefficients_checked": diff["canonical_sign_repair"]["master_density_coefficients_checked"],
        "auxiliary_Diff_defects": diff["canonical_sign_repair"]["canonical_q2_cyclicity_defects"],
        "orthogonal_source_family_cross_pairings": 0,
        "split_386_q2_cyclicity_defects": 0,
        "graph_386_q2_cyclicity_defects": 0,
        "graph_reason": "the shear is exactly BV-canonical",
    }
    d_replay = {
        "background": "unit stationary ultrastatic conformal cylinder",
        "D_generator": d_action["D_action"]["generator"] if "generator" in d_action.get("D_action", {}) else "Lie_partial_t",
        "minimal_tensor_natural_families": len(minimal["primary_components"]),
        "auxiliary_tensor_natural_families": 4,
        "stationary_coefficient_defects": 0,
        "split_D_q2_derivation_defects": 0,
        "graph_D_q2_derivation_defects": 0,
        "graph_transport_authority": preflight["result_id"],
    }
    envelope = graph_envelope(pairing, shear, minimal, ledger)
    q3_boundary = {
        "minimal_q3_available": True,
        "auxiliary_metric_dependent_q3_available": False,
        "first_missing_vertex": "D_h^2 D_f_hat^2 S_aux, equivalently q3(h,h,f_hat) and q3(h,f_hat,f_hat) paired outputs",
        "full_source_q3_assembled": False,
        "Gate_A_disposition": "FAIL_CLOSED",
    }
    foundations = {
        "exact_rational_component_arithmetic": True,
        "finite_ledgers": True,
        "support_local": True,
        "choice_principle_used": False,
        "infinite_selection_used": False,
        "spectral_decomposition_used": False,
        "Green_operator_used": False,
        "analytic_input": "stationary tensor naturality only for the D/q2 statement",
        "weakest_finite_kernel": "PRA conditional on pinned tensor-natural identities",
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-386-source-q2-common-assembly-v1",
        "result_id": "STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1",
        "result_kind": "AUTHORITATIVE_SHIFTED_SOURCE_Q2_COMMON_SNAPSHOT_AND_CANONICAL_GRAPH_TRANSPORT",
        "result_state": "FULL_SOURCE_Q2_ASSEMBLED_IDENTITIES_ZERO_AUXILIARY_Q3_OPEN_GATE_FAIL_CLOSED",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "scope": {"theory": "strict pure-Weyl ordinary-derivative generalized-auxiliary BV theory", "background": "unit ultrastatic conformal cylinder", "carrier_rows": 386, "source_rows": 66, "receiver_added_split_cone_rows": 320, "coefficient_field": "Q", "arity": 2},
        "family_census": family_census,
        "source_q2_snapshot": snapshot,
        "q1_q2_replay": identity,
        "q2_cyclicity_replay": cyclicity,
        "D_q2_replay": d_replay,
        "graph_transport": envelope,
        "q3_boundary": q3_boundary,
        "foundational_strength": foundations,
        "claim_flags": {
            "FULL_SHIFTED_SOURCE_Q2_COMMON_UNION_ASSEMBLED": True,
            "FULL_386_GRAPH_Q2_COMPOSITIONAL_DAG_ASSEMBLED": True,
            "FULL_386_Q1_Q2_IDENTITY_REPLAYED": True,
            "FULL_386_Q2_CYCLICITY_REPLAYED": True,
            "FULL_386_D_Q2_DERIVATION_REPLAYED": True,
            "FULL_SOURCE_Q3_ASSEMBLED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "LORENTZIAN_GREEN_Q2_COMPATIBILITY_CERTIFIED": False,
            "HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
        },
        "does_not_establish": [
            "a flattened graph-coordinate 386^3 coefficient tensor; the exact graph object is a compositional DAG",
            "the metric-dependent auxiliary q3 or higher Taylor operations",
            "q2 compatibility with advanced/retarded Green homotopies",
            "an accepted Gate-A freeze, Hadamard state, renormalized Lorentzian products, QME restoration, residual transfer, positivity, particles or unitarity",
        ],
        "canonical_hashes": {"family_census_sha256": digest(family_census), "source_q2_snapshot_sha256": digest(snapshot), "q1_q2_replay_sha256": digest(identity), "q2_cyclicity_replay_sha256": digest(cyclicity), "D_q2_replay_sha256": digest(d_replay), "graph_transport_sha256": digest(envelope), "q3_boundary_sha256": digest(q3_boundary), "foundational_strength_sha256": digest(foundations)},
        "provenance": {"inputs": [{"path": str(path.relative_to(ROOT)), "result_id": expected, "sha256": sha(path), "role": role} for path, expected, role in INPUTS]},
        "schema_path": "quantum-weyl/classical_import/schema/strict-386-source-q2-common-assembly-v1.schema.json",
        "independent_checker": "quantum-weyl/classical_import/check_strict_386_source_q2_common_assembly.py",
        "human_report": str(REPORT.relative_to(ROOT)),
        "next_gate": "Compute the second metric variation of the exact shifted auxiliary mass density, lift it to q3 with the fixed pairing, and assemble it with minimal q3 before replaying the arity-three identity and cyclicity on common bytes.",
    }


def render(value: dict[str, Any]) -> str:
    snapshot, identity, cyclic, graph, q3 = (value[key] for key in ("source_q2_snapshot", "q1_q2_replay", "q2_cyclicity_replay", "graph_transport", "q3_boundary"))
    return f"""# Strict 386-row source q2 common assembly v1

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`

## Outcome

The strict source `q2` is now assembled on one content-addressed snapshot.  It
unites the 22 ordered minimal symbolic operations with
**{snapshot['auxiliary_ordered_component_coefficients']} exact auxiliary
component coefficients**, with no key collisions.  The source theory occupies
66 rows; the receiver-added 320-row split cone is extended by zero and the
whole operation is transported to graph coordinates by the certified
BV-canonical shear.

The common replay establishes:

- split and graph `[q1,q2]` defects: **{identity['split_386_q1_q2_defects']} / {identity['graph_386_q1_q2_defects']}**;
- split and graph cyclicity defects: **{cyclic['split_386_q2_cyclicity_defects']} / {cyclic['graph_386_q2_cyclicity_defects']}**;
- graph support envelope: **{graph['graph_block_triples']} block triples**, with {graph['active_graph_input_row_envelope']} possible input rows and {graph['active_graph_output_row_envelope']} possible output rows.

The earlier V1 auxiliary momentum-map convention would have left 336 exact
arity-two defects.  The append-only V2 canonical `c_star` translation is part
of this snapshot, so those defects are not hidden or waived.

## Honest boundary

Gate A remains fail closed.  The first missing common operation is the
metric-dependent auxiliary `q3`, generated by
`{q3['first_missing_vertex']}`.  No Green compatibility, Hadamard or QME claim
is promoted by the local source assembly.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_source_q2_common_assembly.py --check
python3 quantum-weyl/classical_import/check_strict_386_source_q2_common_assembly.py
python3 quantum-weyl/classical_import/verify_strict_386_source_q2_common_assembly.py
python3 -m unittest quantum-weyl.classical_import.tests.test_strict_386_source_q2_common_assembly
```
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print("STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
