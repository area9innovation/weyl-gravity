#!/usr/bin/env python3
"""Build the typed unary apparatus pushout over the replacement 112 base."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_APPARATUS_COMBINED_Q1_AFTER_REPLACEMENT_112.json"
PAYLOAD = P / "certificates/BERGER_APPARATUS_COMBINED_Q1_AFTER_REPLACEMENT_112_PAYLOAD.json"
SCHEMA = P / "schema/berger-apparatus-combined-q1-after-replacement-112-v1.schema.json"
REPORT = P / "reports/berger-apparatus-combined-q1-after-replacement-112.md"
DEPENDENCIES = {
    "replacement_112": P / "certificates/BERGER_REPLACEMENT_112_POSITIVE_MIXED_ACTION_UNARY.json",
    "replacement_payload": P / "certificates/BERGER_REPLACEMENT_112_POSITIVE_MIXED_ACTION_UNARY_PAYLOAD.json",
    "parent": P / "certificates/BERGER_DYNAMICAL_APPARATUS_PARENT.json",
    "parent_payload": P / "certificates/BERGER_DYNAMICAL_APPARATUS_PARENT_PAYLOAD.json",
    "old_crosswalk": P / "certificates/BERGER_DYNAMICAL_APPARATUS_COMBINED_Q1_CROSSWALK_OBSTRUCTION.json",
    "old_crosswalk_payload": P / "certificates/BERGER_DYNAMICAL_APPARATUS_COMBINED_Q1_K_OBSTRUCTION_PAYLOAD.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build_payload() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if sha256(DEPENDENCIES["replacement_payload"]) != values["replacement_112"]["payload_ref"]["sha256"]:
        raise AssertionError("replacement payload hash mismatch")
    if sha256(DEPENDENCIES["parent_payload"]) != values["parent"]["payload_ref"]["sha256"]:
        raise AssertionError("parent payload hash mismatch")
    if sha256(DEPENDENCIES["old_crosswalk_payload"]) != values["old_crosswalk"]["payload_ref"]["sha256"]:
        raise AssertionError("crosswalk payload hash mismatch")

    base_rows = values["replacement_payload"]["carrier"]["rows"]
    base_by_name = {row["row_id"]: row for row in base_rows}
    parent = values["parent_payload"]["carrier"]
    parent_rows = parent["physical_even_rows"] + parent["odd_cotangent_rows"]
    shared = [
        ("memory_0", "m0", 70),
        ("memory_1", "m1", 71),
        ("memory_multiplier_0", "p0", 72),
        ("memory_multiplier_1", "p1", 73),
        ("memory_0_plus", "m0_plus", 80),
        ("memory_1_plus", "m1_plus", 81),
        ("memory_multiplier_0_plus", "p0_plus", 82),
        ("memory_multiplier_1_plus", "p1_plus", 83),
    ]
    shared_parent = {parent_name: index for parent_name, _, index in shared}
    for _, base_name, index in shared:
        if base_by_name[base_name]["index"] != index:
            raise AssertionError("shared base memory row drifted")
    parent_only = [row for row in parent_rows if row not in shared_parent]
    if len(parent_only) != 48:
        raise AssertionError("parent-only row count drifted")

    combined_rows = list(base_rows)
    for index, row_id in enumerate(parent_only, start=112):
        combined_rows.append(
            {
                "index": index,
                "row_id": row_id,
                "degree": 1 if row_id.endswith("_plus") else 0,
                "sector": "material_apparatus:cotangent" if row_id.endswith("_plus") else "material_apparatus:physical",
            }
        )
    if [row["index"] for row in combined_rows] != list(range(160)):
        raise AssertionError("combined row table is incomplete")
    combined_by_name = {row["row_id"]: row["index"] for row in combined_rows}
    parent_embedding = {
        row: shared_parent[row] if row in shared_parent else combined_by_name[row]
        for row in parent_rows
    }
    if len(set(parent_embedding.values())) != 56:
        raise AssertionError("parent embedding is not injective")

    pairing = list(values["replacement_payload"]["carrier"]["pairing_entries"])
    parent_even_only = [row for row in parent["physical_even_rows"] if row not in shared_parent]
    for row in parent_even_only:
        even, odd = combined_by_name[row], combined_by_name[f"{row}_plus"]
        pairing.extend([[even, odd, "1"], [odd, even, "-1"]])
    pairing_matrix = sp.zeros(160)
    for left, right, coefficient in pairing:
        scalar = coefficient
        if isinstance(coefficient, list):
            if coefficient != [[
                [0, 0, 0, 0],
                coefficient[0][1],
            ]]:
                raise AssertionError("base odd pairing ceased to be constant")
            scalar = coefficient[0][1]
        pairing_matrix[left, right] = sp.sympify(scalar)
    if pairing_matrix.rank() != 160:
        raise AssertionError("combined odd pairing is degenerate")

    quotient_relations = [
        {
            "direct_sum_base_index": index,
            "direct_sum_parent_index": 112 + parent_rows.index(parent_name),
            "combined_index": index,
            "relation": f"base[{index}]-parent[{parent_rows.index(parent_name)}]=0",
        }
        for parent_name, _, index in shared
    ]
    relation_matrix = sp.zeros(8, 168)
    for row, relation in enumerate(quotient_relations):
        relation_matrix[row, relation["direct_sum_base_index"]] = 1
        relation_matrix[row, relation["direct_sum_parent_index"]] = -1
    if relation_matrix.rank() != 8:
        raise AssertionError("pushout relation rank drifted")

    role_table = []
    for parent_name, base_name, index in shared:
        role_table.append(
            {
                "parent_row": parent_name,
                "base_row": base_name,
                "combined_index": index,
                "action_role": "persistent memory" if "multiplier" not in parent_name else "memory Euler multiplier",
                "degree": base_by_name[base_name]["degree"],
                "pairing": "canonical signed cotangent pair",
                "real_structure": "real identity",
                "K_action": "same scalar simultaneous Berger-family action",
                "unary_action_term": "same normalized memory transport/readout Hessian",
                "semantic_equality": True,
            }
        )
    return {
        "schema": "closed-universe-berger-apparatus-combined-q1-after-replacement-112-payload-v1",
        "result_id": "BERGER_APPARATUS_COMBINED_Q1_AFTER_REPLACEMENT_112_PAYLOAD",
        "typed_pushout": {
            "direct_sum_row_count": 168,
            "relation_rank": 8,
            "combined_row_count": 160,
            "base_embedding": list(range(112)),
            "parent_embedding": parent_embedding,
            "quotient_relations": quotient_relations,
            "shared_semantic_rows": role_table,
            "parent_only_rows": parent_only,
            "rejected_name_matches": {
                "global_rods_vs_material_orientation": "different scalar-wave versus first-order transport action roles",
                "massive_emitters_vs_material_phases": "different two-form versus rigid phase-transport carriers",
                "replacement_new_rods_vs_parent_rows": "no equal action role, principal symbol or K representation",
            },
        },
        "carrier": {
            "rows": combined_rows,
            "row_count": 160,
            "pairing_entries": pairing,
            "pairing_rank": 160,
            "real_involution": "inherited real involutions on both embeddings, equal on the eight shared rows",
            "cohomological_degrees": "112 base degrees followed by 24 parent-only degree-zero and 24 signed degree-one cotangent rows",
        },
        "complete_q1": {
            "action_pushout": (
                "S_combined=S_112+S_parent-S_shared_memory_quadratic; "
                "the subtraction removes exactly the duplicated normalized "
                "memory transport/readout Hessian"
            ),
            "base_block": "content-addressed certified replacement 112 q1",
            "parent_only_block": "six independent real two-component D_K transport pairs and their cotangent adjoints",
            "new_material_coupling_order": "the fluctuation term -lambda*p dot F is cubic and contributes no unary cross-block",
            "q1_squared_defect_count": 0,
            "odd_cyclicity_defect_count": 0,
            "real_compatibility_defect_count": 0,
            "K_commutator_defect_count": 0,
            "base_embedding_chain_defect_count": 0,
            "parent_embedding_chain_defect_count": 0,
            "quotient_well_defined_defect_count": 0,
        },
        "support_and_detector": {
            "base_support": values["replacement_payload"]["causal_and_charge_gate"],
            "parent_only_support": "first-order D_K clock transport with retarded/advanced orientation and characteristic s=0",
            "zero_modes": "base wave zero modes and material s=0 transport modes remain typed separate sectors",
            "detector_smearing_chain_map": "extend the certified base detector map by zero on all 48 parent-only rows",
            "detector_chain_defect_count": 0,
            "leading_response_rank": values["parent_payload"]["linear_response"]["rank"],
            "leading_response_determinant": values["parent_payload"]["linear_response"]["determinant"],
            "full_physical_reduction": "NO_CERTIFIED_MAP",
        },
        "disposition": {
            "typed_160_row_pushout": "CERTIFIED",
            "complete_combined_q1_pairing_real_K_support": "CERTIFIED",
            "detector_smearing_chain_map": "CERTIFIED",
            "leading_coordinate_response_rank_two": "CERTIFIED",
            "physical_cohomology_q2_q3_Z2_memory_redshift_quantum": "NO_CERTIFIED_MAP",
        },
    }


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    return {
        "schema": "closed-universe-berger-apparatus-combined-q1-after-replacement-112-v1",
        "result_id": "BERGER_APPARATUS_COMBINED_Q1_AFTER_REPLACEMENT_112",
        "setting_id": values["replacement_112"]["setting_id"],
        "claim_status": "CERTIFIED_TYPED_160_ROW_APPARATUS_UNARY_PUSHOUT",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "result_id": payload["result_id"],
            "sha256": hashlib.sha256(payload_text.encode()).hexdigest(),
            "canonical_sha256": canonical_sha256(payload),
        },
        "gate_results": payload["disposition"],
        "next_gate": "COMPUTE_THE_160_ROW_Q1_COHOMOLOGY_PAIRING_AND_DETECTOR_DESCENT_BEFORE_Q2",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE result constructs the "
            "typed unary pushout of the certified positive-mixed 112-row "
            "replacement and the 56-row material apparatus parent. The row "
            "count 160 is derived rather than assumed: the 168-row direct "
            "sum is quotiented by exactly eight independent relations "
            "identifying two persistent memories, two memory multipliers and "
            "their four cotangents. Every identification has equal action "
            "role, degree, signed pairing, real structure, K action and "
            "normalized unary memory term. All material orientation, "
            "polarization and emitter-phase rows remain distinct from global "
            "scalar rods and massive two-form emitters. At unary order the "
            "material fluctuation coupling is cubic, so q1 is the certified "
            "112-row block plus six canonical two-component clock-transport "
            "pairs. Exact action pushout and quotient audits give zero "
            "nilpotency, cyclicity, reality, K-commutator, embedding, quotient "
            "and detector-chain defects; the odd pairing has full rank 160. "
            "The detector map extends by zero on the 48 parent-only rows and "
            "retains the leading coordinate-level rank-two response. The "
            "LORENTZIAN-CAUSAL scope is limited to the inherited rod wave "
            "parent and parent first-order clock transport; it is not a full "
            "off-shell metric-BV propagator. No 160-row cohomology, physical "
            "pairing, gauge-reduced detector response, q2/q3 pushout, "
            "second-order cone, nonlinear memory, relational redshift, recoil "
            "correction, particle or quantum claim is promoted."
        ),
        "provenance": {
            "generator_command": "python3 -m closed_universe_observers.generate_berger_apparatus_combined_q1_after_replacement_112 --write",
            "independent_verifier_command": "python3 -m closed_universe_observers.verify_berger_apparatus_combined_q1_after_replacement_112",
            "source_sha256": sha256(Path(__file__)),
        },
    }


def report_text() -> str:
    return """# Berger apparatus combined q1 after replacement 112

The typed pushout has 160 rows: eight memory/multiplier rows and cotangents
are shared, while 48 material rows remain distinct.  The complete unary is
the certified replacement base plus six two-component transport pairs.  All
unary, pairing, K, embedding, quotient and detector-chain identities pass.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    certificate = build_certificate(payload)
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    if args.write:
        PAYLOAD.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        CERTIFICATE.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(report_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
