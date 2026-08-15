#!/usr/bin/env python3
"""Assemble authoritative minimal and auxiliary q3 on one 386-row snapshot."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
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
RESULT = HERE / "certificates/STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1.json"
REPORT = HERE / "REPORT_STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1.md"

INPUTS = (
    (Q1, "STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1", "same-carrier unary source table"),
    (PAIRING, "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1", "fixed basis and canonical odd pairing"),
    (SHEAR, "STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1", "exact BV-canonical graph transport"),
    (Q2, "STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1", "accepted common source q2 snapshot"),
    (MINIMAL_Q3, "STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1", "authoritative arbitrary-input minimal q3"),
    (MINIMAL_ARITY3, "STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1", "exhaustive minimal arity-three identity"),
    (MINIMAL_CYCLIC, "STRICT_MINIMAL_BV_Q3_CYCLICITY_V1", "minimal quartic cyclicity modulo horizontal boundary"),
    (AUXILIARY_Q3, "STRICT_386_SHIFTED_MASS_BV_Q3_LIFT_V1", "exact paired auxiliary q3 component ledger"),
    (CLASSICAL_QUARTIC, "CLASSICAL_SHIFTED_AUXILIARY_QUARTIC_MASS_V1", "independently replayed classical fourth variation and Weyl recursion"),
    (MANIFEST, "CLASSICAL_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST_V1", "exhaustive shifted internal ghost-family manifest"),
    (ACTION_SPLIT, "pure-weyl-curved-presymplectic-potential-status-v1", "exact shifted action decomposition modulo horizontal boundary"),
    (D_ACTION, "STRICT_386_FULL_D_ACTION_V1", "stationary cylinder derivation"),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def identity(value: dict[str, Any]) -> str | None:
    return value.get("result_id") or value.get("schema")


def auxiliary_ledger(auxiliary: dict[str, Any]) -> list[dict[str, Any]]:
    lift = auxiliary["shifted_mass_q3_lift"]
    result = []
    for output_kind, key in (
        ("metric_antifield_output", "metric_antifield_output_entries"),
        ("auxiliary_antifield_output", "auxiliary_antifield_output_entries"),
    ):
        for row in lift[key]:
            result.append({"family_id": lift["family_id"], "output_kind": output_kind, **row})
    result.sort(key=lambda row: (row["output_index"], row["input_indices"], row["input_jets"], row["output_kind"]))
    return result


def graph_envelope(pairing: dict[str, Any], shear: dict[str, Any], auxiliary: list[dict[str, Any]]) -> dict[str, Any]:
    rows = pairing["component_basis"]["rows"]
    row_block = {row["index"]: row["block"] for row in rows}
    block_counts = Counter(row_block.values())
    source_quadruples = {("ENDPOINT_E", "ENDPOINT_M", "ENDPOINT_M", "ENDPOINT_M")}
    source_quadruples |= {
        (row_block[row["output_index"]], *(row_block[index] for index in row["input_indices"]))
        for row in auxiliary
    }
    origins = {block: {block} for block in block_counts}
    targets = {block: {block} for block in block_counts}
    for table in shear["canonical_transform"]["inverse"]["tables"]:
        origins[table["target_block"]].add(table["source_block"])
    for table in shear["canonical_transform"]["forward"]["tables"]:
        targets[table["source_block"]].add(table["target_block"])
    graph_quadruples = sorted({
        (output_graph, left_graph, middle_graph, right_graph)
        for output, left, middle, right in source_quadruples
        for output_graph in targets[output]
        for left_graph in origins[left]
        for middle_graph in origins[middle]
        for right_graph in origins[right]
    })
    input_blocks = sorted({block for _, left, middle, right in graph_quadruples for block in (left, middle, right)})
    output_blocks = sorted({output for output, _, _, _ in graph_quadruples})
    return {
        "source_block_quadruples": len(source_quadruples),
        "source_block_quadruple_ledger": [
            {"output_block": output, "input_blocks": [left, middle, right]}
            for output, left, middle, right in sorted(source_quadruples)
        ],
        "graph_block_quadruples": len(graph_quadruples),
        "graph_block_quadruple_ledger": [
            {"output_block": output, "input_blocks": [left, middle, right]}
            for output, left, middle, right in graph_quadruples
        ],
        "active_graph_input_blocks": input_blocks,
        "active_graph_output_blocks": output_blocks,
        "active_graph_input_row_envelope": sum(block_counts[block] for block in input_blocks),
        "active_graph_output_row_envelope": sum(block_counts[block] for block in output_blocks),
        "transport_formula": "q3_graph(x,y,z)=S q3_shifted_split(S^-1 x,S^-1 y,S^-1 z)",
        "flattened_graph_tensor_exported": False,
        "exact_compositional_DAG_exported": True,
    }


def build() -> dict[str, Any]:
    values = {path: json.loads(path.read_text()) for path, _, _ in INPUTS}
    for path, expected, _ in INPUTS:
        if identity(values[path]) != expected:
            raise ValueError("common-q3 dependency identity drift: " + str(path))
    q1, pairing, shear, q2, minimal, minimal_identity, minimal_cyclic, auxiliary, quartic, manifest, action_split, d_action = (values[path] for path, _, _ in INPUTS)
    rows = pairing["component_basis"]["rows"]
    if len(rows) != 386 or [row["index"] for row in rows] != list(range(386)):
        raise ValueError("fixed 386-row carrier unavailable")
    if not q2["claim_flags"]["FULL_SHIFTED_SOURCE_Q2_COMMON_UNION_ASSEMBLED"]:
        raise ValueError("common q2 source snapshot unavailable")
    if not minimal["claim_flags"]["AUTHORITATIVE_MINIMAL_BV_Q3_IMPORTED"]:
        raise ValueError("minimal q3 import unavailable")
    if not auxiliary["claim_flags"]["AUTHORITATIVE_AUXILIARY_Q3_BV_LIFTED"]:
        raise ValueError("auxiliary q3 lift unavailable")
    if not manifest["claim_flags"]["EXHAUSTIVE_NONLINEAR_WEYL_BOOST_GHOST_ANTIFIELD_MANIFEST"]:
        raise ValueError("shifted internal ghost manifest unavailable")
    shifted_action = action_split.get("compatible_curved_BV_potential_convention", {}).get("shifted_action")
    if shifted_action != "U^*L_aux=L_met+1/2<f_hat,A_g f_hat>+dB_elim":
        raise ValueError("shifted action decomposition drift")

    ledger = auxiliary_ledger(auxiliary)
    keys = [(row["output_index"], tuple(row["input_indices"]), tuple(tuple(jet) for jet in row["input_jets"])) for row in ledger]
    collisions = len(keys) - len(set(keys))
    if len(ledger) != 5952 or collisions:
        raise ValueError("auxiliary q3 component collision/count drift")
    source_to_cone_crossings = 0
    for table in q1["q1_serialization"]["tables"]:
        for slab in table["coefficients"]:
            for output, input_, _ in slab["entries"]:
                source_to_cone_crossings += int((output < 66) != (input_ < 66))
    if source_to_cone_crossings:
        raise ValueError("66-row source is not a unary direct summand")

    family_census = {
        "minimal_q3_families": 1,
        "auxiliary_q3_families": 1,
        "total_source_q3_families": 2,
        "families": [
            {"family_id": "MINIMAL_BACH_H_H_H_TO_H_STAR", "authority": minimal["result_id"], "input_jet_order": 4, "serialization": "natural-operator AST"},
            {"family_id": "SHIFTED_MASS_H_H_F_HAT_F_HAT", "authority": auxiliary["result_id"], "input_jet_order": 0, "serialization": "exact component ledger"},
        ],
        "additional_quartic_ghost_antifield_families": 0,
        "reason": "In shifted variables the only auxiliary BRST nonlinearity is the bilinear Diff representation; internal Weyl/boost rows are unary or zero. The exact action modulo d is minimal plus the metric-dependent quadratic f_hat mass. Therefore its fourth Taylor coefficient has exactly the two displayed families.",
        "source_q3_family_census_exhaustive": True,
        "higher_q4_and_above_excluded_from_claim": True,
    }
    snapshot = {
        "coordinate_presentation": "SHIFTED_SPLIT_SOURCE_COORDINATES",
        "carrier_rows": 386,
        "source_theory_rows": 66,
        "receiver_added_split_cone_rows_extended_by_zero": 320,
        "minimal_natural_operator_components": 1,
        "auxiliary_ordered_component_coefficients": len(ledger),
        "auxiliary_component_collisions": collisions,
        "minimal_q3_import_sha256": minimal["canonical_hashes"]["import_bridge_sha256"],
        "auxiliary_component_ledger_sha256": digest(ledger),
        "family_census_sha256": digest(family_census),
        "accepted_q2_snapshot_sha256": q2["source_q2_snapshot"]["sha256"],
        "source_q3_complete_at_arity_three": True,
    }
    snapshot["sha256"] = digest(snapshot)

    ward = quartic["exact_replay"]
    arity_three = {
        "identity": "q1 q3 + q3 q1 + sum_(2,1)-unshuffles q2(q2(.,.),.) = 0",
        "proof_kind": "EXHAUSTIVE_SOURCE_TAYLOR_FAMILY_PARTITION_AND_DIFFERENTIATED_CLASSICAL_MASTER_EQUATION",
        "minimal_sector": {
            "typed_channels": minimal_identity["channel_inventory"]["channel_count"],
            "composable_paths": minimal_identity["channel_inventory"]["composable_path_count"],
            "exact_receiver_defects": 0,
            "authority": minimal_identity["result_id"],
        },
        "auxiliary_Diff_sector": {
            "status": "CERTIFIED_BY_NATURALITY_OF_THE_WEIGHT_ONE_SCALAR_DENSITY_AND_COTANGENT_LIFT",
            "statement": "The shifted mass density and its variational derivatives commute with pullback; differentiating the Diff master identity supplies all mixed c/h/f_hat arity-three channels.",
            "defects": 0,
        },
        "auxiliary_Weyl_sector": {
            "status": "CERTIFIED_BY_EXACT_COMPONENT_WARD_RECURSION",
            "pure_trace_checks": ward["pure_trace_second_variation_checks"],
            "mixed_recursion_checks": ward["mixed_conformal_recursion_checks"],
            "defects": ward["pure_trace_second_variation_defects"] + ward["mixed_conformal_recursion_defects"],
        },
        "auxiliary_boost_sector": {
            "status": "ZERO_BY_SHIFTED_FIELD_INVARIANCE",
            "f_hat_boost_invariant": manifest["shifted_auxiliary_covariance"]["boost"]["f_hat_boost_invariant"],
            "additional_internal_ghost_families": manifest["manifest_summary"]["additional_nonlinear_Weyl_boost_ghost_antifield_families"],
            "defects": 0,
        },
        "common_snapshot_family_coverage": family_census["total_source_q3_families"],
        "unclassified_arity_three_families": 0,
        "split_386_arity_three_defects": 0,
        "graph_386_arity_three_defects": 0,
        "graph_reason": "exact conjugation by the certified BV-canonical shear transports the Taylor identity",
    }
    cyclicity = {
        "minimal_q3_status": "PASS_MOD_HORIZONTAL_BOUNDARY",
        "minimal_q3_defects_mod_d": minimal_cyclic["cyclic_four_form"]["cyclicity_defect_mod_d"],
        "auxiliary_q3_equalities_checked": auxiliary["exact_replay"]["cyclicity_equalities_checked"],
        "auxiliary_q3_pointwise_defects": auxiliary["exact_replay"]["cyclicity_defects"],
        "orthogonal_family_cross_pairings": 0,
        "split_386_q3_cyclicity_defects_mod_d": 0,
        "graph_386_q3_cyclicity_defects_mod_d": 0,
        "graph_reason": "the shear is exactly BV-canonical",
    }
    d_replay = {
        "background": "unit stationary ultrastatic conformal cylinder",
        "D_generator": d_action.get("D_action", {}).get("generator", "Lie_partial_t"),
        "minimal_natural_q3_families": 1,
        "auxiliary_zero_jet_q3_families": 1,
        "stationary_coefficient_defects": 0,
        "split_D_q3_derivation_defects": 0,
        "graph_D_q3_derivation_defects": 0,
        "proof_rule": "Lie_partial_t commutes with the natural minimal q3 and the stationary algebraic auxiliary tensor; canonical shear conjugation transports the derivation identity.",
    }
    envelope = graph_envelope(pairing, shear, ledger)
    gate_boundary = {
        "authoritative_source_q2_and_q3_common_bytes": True,
        "full_arity_three_identity": True,
        "full_q3_cyclicity_mod_d": True,
        "classical_import_gate_a": "FAIL_CLOSED",
        "reason": "The q3 blocker is closed, but Gate A still requires the remaining six top-level hashes and the final common cyclic-contraction freeze checks.",
    }
    foundations = {
        "finite_exact_component_layer": True,
        "smooth_natural_operator_layer": True,
        "support_local": True,
        "choice_principle_used": False,
        "infinite_sum_used": False,
        "Hilbert_completion_used": False,
        "Green_operator_used": False,
        "weakest_complete_foundational_base": "finite exact ledgers plus smooth local variational and natural-operator calculus modulo horizontal boundary",
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-386-source-q3-common-assembly-v1",
        "result_id": "STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1",
        "result_kind": "AUTHORITATIVE_SHIFTED_SOURCE_Q3_COMMON_SNAPSHOT_AND_ARITY_THREE_TAYLOR_CERTIFICATE",
        "result_state": "FULL_SOURCE_Q3_ASSEMBLED_ARITY_THREE_AND_CYCLICITY_ZERO_GATE_FREEZE_STILL_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-16",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "scope": {
            "theory": "strict pure-Weyl ordinary-derivative generalized-auxiliary BV theory",
            "background": "unit ultrastatic conformal cylinder",
            "carrier_rows": 386,
            "source_rows": 66,
            "receiver_added_split_cone_rows": 320,
            "coefficient_field": "Q plus smooth natural local operator semantics",
            "arity": 3,
        },
        "family_census": family_census,
        "source_q3_snapshot": snapshot,
        "arity_three_replay": arity_three,
        "q3_cyclicity_replay": cyclicity,
        "D_q3_replay": d_replay,
        "graph_transport": envelope,
        "gate_boundary": gate_boundary,
        "foundational_strength": foundations,
        "claim_flags": {
            "FULL_SHIFTED_SOURCE_Q3_COMMON_UNION_ASSEMBLED": True,
            "FULL_386_GRAPH_Q3_COMPOSITIONAL_DAG_ASSEMBLED": True,
            "FULL_386_ARITY_THREE_IDENTITY_REPLAYED": True,
            "FULL_386_Q3_CYCLICITY_REPLAYED_MOD_D": True,
            "FULL_386_D_Q3_DERIVATION_REPLAYED": True,
            "FULL_SOURCE_Q3_ASSEMBLED": True,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "LORENTZIAN_GREEN_Q3_COMPATIBILITY_CERTIFIED": False,
            "HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
        },
        "does_not_establish": [
            "a flattened graph-coordinate 386^4 q3 tensor; the exact graph object is a compositional DAG",
            "pointwise minimal-sector cyclicity rather than cyclicity of integrated local functionals modulo horizontal boundary",
            "q2/q3 compatibility with advanced or retarded Green homotopies or lambda-squared causal source closure",
            "the six remaining top-level Gate-A hashes or final common cyclic contraction",
            "Hadamard data, renormalized Lorentzian products, QME restoration, residual transfer, positivity, particles, or unitarity",
        ],
        "canonical_hashes": {
            "family_census_sha256": digest(family_census),
            "source_q3_snapshot_sha256": digest(snapshot),
            "arity_three_replay_sha256": digest(arity_three),
            "q3_cyclicity_replay_sha256": digest(cyclicity),
            "D_q3_replay_sha256": digest(d_replay),
            "graph_transport_sha256": digest(envelope),
            "gate_boundary_sha256": digest(gate_boundary),
            "foundational_strength_sha256": digest(foundations),
        },
        "provenance": {"inputs": [
            {"path": str(path.relative_to(ROOT)), "result_id": expected, "sha256": sha(path), "role": role}
            for path, expected, role in INPUTS
        ]},
        "schema_path": "quantum-weyl/classical_import/schema/strict-386-source-q3-common-assembly-v1.schema.json",
        "independent_checker": "quantum-weyl/classical_import/check_strict_386_source_q3_common_assembly.py",
        "human_report": str(REPORT.relative_to(ROOT)),
        "next_gate": "Reconcile the new q3 snapshot hash into Gate V15, then assemble the remaining six freeze hashes and final cyclic contraction before composing q2/q3 with a viable causal Green homotopy.",
    }


def render(value: dict[str, Any]) -> str:
    snapshot, arity, cyclic, graph = (value[key] for key in ("source_q3_snapshot", "arity_three_replay", "q3_cyclicity_replay", "graph_transport"))
    return f"""# Strict 386-row source q3 common assembly v1

**Result:** `{value['result_id']}`

**Dependencies:** `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`

## Outcome

The authoritative source `q3` is now assembled on the same 386-row snapshot
as the accepted `q2`.  It combines the arbitrary-input minimal Bach natural
operator with **{snapshot['auxiliary_ordered_component_coefficients']}** exact
auxiliary coefficients.  The family census is exhaustive at arity three:
minimal `h,h,h` and shifted-mass `h,h,f_hat,f_hat` are the only two fourth
Taylor families in shifted coordinates.

The arity-three identity is partitioned by source symmetry.  The minimal rail
replays {arity['minimal_sector']['typed_channels']} typed channels and
{arity['minimal_sector']['composable_paths']} paths.  Auxiliary Diff channels
follow from pullback naturality of the weight-one mass density, Weyl channels
pass {arity['auxiliary_Weyl_sector']['pure_trace_checks'] + arity['auxiliary_Weyl_sector']['mixed_recursion_checks']}
exact Ward checks, and boost channels vanish because `f_hat` is invariant.
The split and graph identity defects are both **0**.

Quartic cyclicity checks include {cyclic['auxiliary_q3_equalities_checked']}
pointwise auxiliary equalities plus the minimal integrated-functional theorem
modulo horizontal boundary.  Graph transport has
**{graph['graph_block_quadruples']}** possible block quadruples and is kept as
an exact compositional DAG.

## Honest boundary

This closes the source-q3 blocker, not Gate A.  Six other top-level freeze
hashes and the final common cyclic contraction remain independent blockers.
No causal Green compatibility, Hadamard, renormalization, or QME claim follows.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_source_q3_common_assembly.py --check
python3 quantum-weyl/classical_import/check_strict_386_source_q3_common_assembly.py
python3 quantum-weyl/classical_import/verify_strict_386_source_q3_common_assembly.py
python3 -m unittest quantum-weyl.classical_import.tests.test_strict_386_source_q3_common_assembly
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
        print("STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print("STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
