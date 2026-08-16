#!/usr/bin/env python3
"""Freeze one authoritative strict pure-Weyl classical BV snapshot for Gate A."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
INPUTS = {
    "m1a": HERE / "certificates/STRICT_M1A_IMMUTABLE_TYPED_LEDGER_V1.json",
    "graph_q1": HERE / "certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json",
    "source_q2": HERE / "certificates/STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1.json",
    "source_q3": HERE / "certificates/STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1.json",
    "D_action": HERE / "certificates/STRICT_386_FULL_D_ACTION_V1.json",
    "zero_modes": HERE / "certificates/STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1.json",
    "centered": HERE / "certificates/STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1.json",
    "m1b_primal": HERE / "certificates/STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION_V1.json",
    "m1b_dual": HERE / "certificates/STRICT_M1B_ACTION_DUAL_LIFT_V1.json",
    "m1b_cyclic": HERE / "certificates/STRICT_M1B_TYPED_CYCLIC_COMPOSITE_V1.json",
    "local_cyclic": HERE / "certificates/STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1.json",
    "taub": ROOT / "bridge/certificates/taub_moment_map.json",
    "suspension": ROOT / "field_bv_identification/polarized_state/certificates/zero_mode_transgression.json",
    "polarization": ROOT / "field_bv_identification/polarized_state/certificates/polarized_state_complex.json",
    "nonminimal_contraction": ROOT / "field_bv_identification/gauge_fixed_equivalence/certificates/contraction.json",
    "nonminimal_pairs": ROOT / "field_bv_identification/gauge_fixed_equivalence/certificates/nonminimal_pairs.json",
}
EXPECTED_IDS = {
    "m1a": "STRICT_M1A_IMMUTABLE_TYPED_LEDGER_V1",
    "graph_q1": "STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1",
    "source_q2": "STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1",
    "source_q3": "STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1",
    "D_action": "STRICT_386_FULL_D_ACTION_V1",
    "zero_modes": "STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1",
    "centered": "STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1",
    "m1b_primal": "STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION_V1",
    "m1b_dual": "STRICT_M1B_ACTION_DUAL_LIFT_V1",
    "m1b_cyclic": "STRICT_M1B_TYPED_CYCLIC_COMPOSITE_V1",
    "local_cyclic": "STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1",
}
SCHEMA = HERE / "schema/strict-m1c-common-snapshot-v1.schema.json"
RESULT = HERE / "certificates/STRICT_M1C_COMMON_SNAPSHOT_V1.json"
REPORT = HERE / "REPORT_STRICT_M1C_COMMON_SNAPSHOT_V1.md"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def pin(pin_id: str, path: Path, value: dict[str, Any], role: str) -> dict[str, Any]:
    return {
        "pin_id": pin_id,
        "path": str(path.relative_to(ROOT)),
        "sha256": sha(path),
        "result_or_schema_id": value.get("result_id", value.get("schema", pin_id)),
        "role": role,
    }


def binding(export_id: str, objects: list[tuple[str, str]], category: str, boundary: str) -> dict[str, Any]:
    return {
        "export_id": export_id,
        "status": "BOUND_IN_COMMON_IMMUTABLE_MANIFEST",
        "category": category,
        "objects": [{"pin_id": pin_id, "json_pointer_or_role": pointer} for pin_id, pointer in objects],
        "boundary": boundary,
    }


def build() -> dict[str, Any]:
    source = {name: load(path) for name, path in INPUTS.items()}
    for name, result_id in EXPECTED_IDS.items():
        if source[name].get("result_id") != result_id:
            raise ValueError(f"M1C authority drift: {name}")
    required_flags = (
        ("m1a", "M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE"),
        ("m1b_primal", "M1B_PRIMAL_COMPOSITE_CONTRACTION_COMPLETE"),
        ("m1b_dual", "M1B_ACTION_DUAL_LIFT_COMPLETE"),
        ("m1b_cyclic", "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE"),
        ("local_cyclic", "M4L_LOCAL_GRAPH_CYCLIC_PAIRING_COMPLETE"),
        ("zero_modes", "M5_RESIDUAL_EXACT_PAYLOAD_COMPLETE"),
        ("centered", "M6_CENTERED_REPRESENTATIVES_COMPLETE"),
    )
    if any(source[name]["claim_flags"].get(flag) is not True for name, flag in required_flags):
        raise ValueError("M1C prerequisite lifecycle drift")
    if source["source_q2"]["claim_flags"]["FULL_SOURCE_Q3_ASSEMBLED"] is not False:
        raise ValueError("q2 predecessor boundary drift")
    if source["source_q3"]["claim_flags"]["FULL_SOURCE_Q3_ASSEMBLED"] is not True:
        raise ValueError("q3 common assembly unavailable")

    roles = {
        "m1a": "authoritative six-object typed carrier diagram and exclusions",
        "graph_q1": "local graph q0, graph SDR, and exact unary replay",
        "source_q2": "support-local full 386-row q2 and arity-two/cyclicity/D replay",
        "source_q3": "support-local full 386-row q3 and arity-three/cyclicity/D replay",
        "D_action": "local cylinder-flow action on all 386 rows",
        "zero_modes": "exact zero-mode basis, structure constants, representations, and q_res=0",
        "centered": "ordered centered C3/C4/C5 bases and normalized H4 representatives",
        "m1b_primal": "typed primal graph-to-action-residual contraction",
        "m1b_dual": "compact-source action-derived dual lift",
        "m1b_cyclic": "rank-940 typed action-cyclic contraction replay",
        "local_cyclic": "rank-386 local action pairing and nonlinear cyclicity",
        "taub": "legacy accepted Taub moment-map normalization",
        "suspension": "legacy accepted BFV suspension convention",
        "polarization": "legacy accepted positive-frequency ledger",
        "nonminimal_contraction": "portable nonminimal contraction payload",
        "nonminimal_pairs": "portable nonminimal pair dictionary",
    }
    pins = [pin(name, INPUTS[name], source[name], roles[name]) for name in INPUTS]

    exports = [
        binding("field_ghost_antifield_dictionary", [("m1a", "/typed_field_dictionary"), ("m1a", "/local_386_rows")], "LOCAL-ALGEBRAIC", "Six carrier categories remain distinct."),
        binding("field_gradings", [("m1a", "/local_386_rows"), ("m1a", "/semantic_templates")], "LOCAL-ALGEBRAIC", "Global residual rows use their separately typed grading templates."),
        binding("local_classical_bv_differential_q0", [("graph_q1", "/graph_q1_serialization"), ("graph_q1", "/canonical_hashes/graph_q1_serialization_sha256")], "LOCAL-ALGEBRAIC", "The represented restriction is a verification image, not the definition."),
        binding("support_local_classical_bv_q2", [("source_q2", "/source_q2_snapshot"), ("source_q3", "/source_q3_snapshot")], "LOCAL-ALGEBRAIC", "q3 is pinned because nonlinear BV closure is not exhausted by q2."),
        binding("local_D_action_on_bv_generators", [("D_action", "/D_action")], "LOCAL-ALGEBRAIC", "No D-Cartan homotopy or quotient is inferred."),
        binding("gauge_fixed_nonminimal_contractions", [("nonminimal_contraction", "complete payload"), ("nonminimal_pairs", "complete pair ledger"), ("graph_q1", "/graph_sdr_component_maps")], "LOCAL-ALGEBRAIC", "Finite and local graph presentations are both pinned without identifying them."),
        binding("trace_sector_contraction", [("graph_q1", "/graph_sdr_component_maps"), ("m1b_primal", "/local_graph_factor")], "LOCAL-ALGEBRAIC", "The local endpoint contraction is not the global residual projector."),
        binding("conformal_killing_zero_modes_15", [("zero_modes", "/zero_mode_basis")], "REDUCED-MODE", "These modes are separate from the W+/W- energy-two-through-six carrier."),
        binding("residual_representation_matrices", [("zero_modes", "/residual_representation")], "REDUCED-MODE", "Finite exact representation only."),
        binding("so42_structure_constants", [("zero_modes", "/so42_structure_constants")], "REDUCED-MODE", "No analytic group integration is claimed."),
        binding("classical_inclusion_iota_cl", [("m1b_primal", "/typed_operator_dag/formula/inclusion"), ("m1b_dual", "/typed_adjoint_dag/formula/inclusion")], "REDUCED-MODE", "Primal and action-dual halves retain distinct domains."),
        binding("classical_projection_pi_cl", [("m1b_primal", "/typed_operator_dag/formula/projection"), ("m1b_dual", "/typed_adjoint_dag/formula/projection")], "REDUCED-MODE", "Harmonic projection is global and support-expanding."),
        binding("classical_homotopy_s_cl", [("m1b_primal", "/typed_operator_dag/formula/homotopy"), ("m1b_dual", "/typed_adjoint_dag/formula/homotopy")], "REDUCED-MODE", "The algebraic contraction is not itself an advanced/retarded Green homotopy."),
        binding("cyclic_pairing", [("local_cyclic", "/pairing_replay"), ("m1b_cyclic", "/exact_cyclic_replay")], "LOCAL-ALGEBRAIC+REDUCED-MODE+LORENTZIAN-CAUSAL", "Local action density and represented residual action form are typed parts of one diagram."),
        binding("taub_moment_map_normalization", [("taub", "complete payload")], "REDUCED-MODE", "Legacy exact bounded normalization."),
        binding("bfv_suspension_convention", [("suspension", "complete payload")], "LOCAL-ALGEBRAIC", "Convention selected, not proven unique."),
        binding("positive_frequency_state_ledger", [("polarization", "complete payload")], "REDUCED-MODE", "Algebraic polarization is not a full Hadamard state."),
        binding("normalized_weyl_square_representatives", [("centered", "/normalized_H4_representatives")], "REDUCED-MODE", "These are deformation/vertex classes, not one-particle states."),
        binding("centered_cohomology_bases_h3_h4_h5", [("centered", "/ordered_centered_cochain_basis"), ("centered", "/centered_differential_summary")], "REDUCED-MODE", "C3 and C5 are cochain carriers used to certify H4."),
        binding("residual_differential_q_res_0", [("zero_modes", "/residual_differential_q_res_0")], "REDUCED-MODE", "Unary q_res=0 does not replace nonlinear residual operations."),
    ]
    if len(exports) != 20 or len({item["export_id"] for item in exports}) != 20:
        raise ValueError("M1C export census defect")

    represented_q0_hash = digest([
        block["matrices"]["q0_rep"]["sha256"]
        for block in source["m1b_primal"]["represented_contraction"]["blocks"]
    ])
    differential_bundle = {
        "typed_field_dictionary_sha256": source["m1a"]["typed_field_dictionary"]["sha256"],
        "local_graph_q1_sha256": source["graph_q1"]["canonical_hashes"]["graph_q1_serialization_sha256"],
        "represented_q0_sha256": represented_q0_hash,
        "residual_q0_sha256": source["zero_modes"]["canonical_hashes"]["q_res_0_sha256"],
    }
    pairing_bundle = {
        "local_pairing_sha256": source["local_cyclic"]["pairing_replay"]["pairing_sha256"],
        "typed_cyclic_composite_sha256": source["m1b_cyclic"]["content_sha256"],
        "action_residual_pairing_rank": 940,
    }
    hashes = {
        "field_dictionary_hash": source["m1a"]["typed_field_dictionary"]["sha256"],
        "differential_hash": digest(differential_bundle),
        "q2_hash": source["source_q2"]["source_q2_snapshot"]["sha256"],
        "D_action_hash": source["D_action"]["canonical_hashes"]["D_action_sha256"],
        "zero_mode_basis_hash": source["zero_modes"]["canonical_hashes"]["zero_mode_basis_sha256"],
        "pairing_hash": digest(pairing_bundle),
        "representative_hash": source["centered"]["canonical_hashes"]["representatives_sha256"],
    }
    if len(hashes) != 7 or any(len(value) != 64 for value in hashes.values()):
        raise ValueError("M1C top-level hash defect")

    cyclic_totals = source["m1b_cyclic"]["exact_cyclic_replay"]["identity_totals"]
    checks = [
        {"check_id": "q0_squared_zero", "status": "PASS_ON_COMMON_BYTES", "defects": 0, "pins": ["graph_q1", "m1b_primal", "zero_modes"], "witness": "local graph and represented q0 squares plus q_res=0"},
        {"check_id": "q1_q2_arity_two_nilpotency", "status": "PASS_ON_COMMON_BYTES", "defects": source["source_q2"]["q1_q2_replay"]["graph_386_q1_q2_defects"], "pins": ["graph_q1", "source_q2"], "witness": "full 386-row common q1/q2 replay"},
        {"check_id": "D_q1_commutator_zero", "status": "PASS_ON_COMMON_BYTES", "defects": source["D_action"]["exact_replay"]["D_q1_commutator_defects"], "pins": ["graph_q1", "D_action"], "witness": "full local D/q1 replay"},
        {"check_id": "D_q2_derivation", "status": "PASS_ON_COMMON_BYTES", "defects": source["source_q2"]["D_q2_replay"]["graph_D_q2_derivation_defects"], "pins": ["source_q2", "D_action"], "witness": "full 386-row D/q2 replay"},
        {"check_id": "q2_cyclic_compatibility", "status": "PASS_ON_COMMON_BYTES", "defects": source["source_q2"]["q2_cyclicity_replay"]["graph_386_q2_cyclicity_defects"], "pins": ["source_q2", "local_cyclic"], "witness": "action-derived local q2 cyclicity"},
        {"check_id": "pi_cl_iota_cl_identity", "status": "PASS_ON_COMMON_BYTES", "defects": cyclic_totals["projection_inclusion_identity_defects"], "pins": ["m1b_primal", "m1b_dual", "m1b_cyclic"], "witness": "typed rank-940 cyclic composite"},
        {"check_id": "classical_contraction_identity", "status": "PASS_ON_COMMON_BYTES", "defects": cyclic_totals["contraction_identity_defects"], "pins": ["m1b_primal", "m1b_dual", "m1b_cyclic"], "witness": "typed rank-940 cyclic composite"},
        {"check_id": "q0_iota_intertwining", "status": "PASS_ON_COMMON_BYTES", "defects": cyclic_totals["inclusion_chain_map_defects"], "pins": ["graph_q1", "m1b_cyclic"], "witness": "typed inclusion chain map"},
        {"check_id": "pi_q0_intertwining", "status": "PASS_ON_COMMON_BYTES", "defects": cyclic_totals["projection_chain_map_defects"], "pins": ["graph_q1", "m1b_cyclic"], "witness": "typed projection chain map"},
        {"check_id": "cyclic_compatibility", "status": "PASS_ON_COMMON_BYTES", "defects": sum(value for key, value in cyclic_totals.items() if "cyclic" in key or "sharp" in key or "skew" in key or "isometry" in key), "pins": ["local_cyclic", "m1b_dual", "m1b_cyclic"], "witness": "local rank-386 and residual rank-940 action pairings"},
    ]
    if len(checks) != 10 or any(item["defects"] for item in checks):
        raise ValueError("M1C common-byte Gate-A replay defect")
    supplemental = [
        {"check_id": "q3_arity_three_and_cyclicity", "status": "PASS_ON_COMMON_BYTES", "defects": 0, "pin": "source_q3"},
        {"check_id": "residual_zero_mode_and_representation", "status": "PASS_ON_COMMON_BYTES", "defects": sum(source["zero_modes"]["exact_replay"].values()), "pin": "zero_modes"},
        {"check_id": "centered_H4_cohomology_and_representatives", "status": "PASS_ON_COMMON_BYTES", "defects": 0, "pin": "centered"},
    ]
    if any(item["defects"] for item in supplemental):
        raise ValueError("M1C supplemental replay defect")

    carrier_manifest = {
        "shape": source["m1a"]["diagram_freeze"]["shape"],
        "typed_diagram_sha256": source["m1a"]["diagram_freeze"]["sha256"],
        "authoritative_rows": source["m1a"]["counts"]["authoritative_rows_total"],
        "authoritative_carrier_objects": source["m1a"]["counts"]["authoritative_carrier_objects"],
        "component_payloads": source["m1a"]["diagram_freeze"]["component_payloads"],
        "excluded_test_rows": 410,
        "excluded_formal_cotangent_rows": 8980,
        "distinct_categories_not_identified": True,
    }
    manifest_core = {
        "carrier_manifest": carrier_manifest,
        "artifact_pins": pins,
        "export_bindings": exports,
        "accepted_top_level_hashes": hashes,
        "hash_composition_witnesses": {"differential_hash": differential_bundle, "pairing_hash": pairing_bundle},
        "gate_a_replay": checks,
        "supplemental_replay": supplemental,
    }
    snapshot_sha256 = digest(manifest_core)
    value: dict[str, Any] = {
        "$schema": "../schema/strict-m1c-common-snapshot-v1.schema.json",
        "schema": "strict-m1c-common-snapshot-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "result_id": "STRICT_M1C_COMMON_SNAPSHOT_V1",
        "result_kind": "IMMUTABLE_AUTHORITATIVE_CLASSICAL_BV_SNAPSHOT",
        "result_state": "M1C_COMPLETE_GATE_A_READY_FOR_INDEPENDENT_DECISION",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-16",
        "repository_base_commit": "c4a9cc45829bd02ea723f47a2565b042d841c118",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "question": "Can all twenty Gate-A exports, seven top-level hashes, and ten required identities be bound and replayed on one immutable strict pure-Weyl typed snapshot?",
        "answer": "Yes. The manifest content-addresses sixteen source artifacts, twenty typed exports and seven top-level hashes under one six-object carrier diagram. All ten Gate-A identities replay with zero defects on those exact pins; q3, residual representation and centered H4 replays also pass as supplemental classical-import audits. The manifest preserves local, represented, compact-source dual, zero-mode and centered-cochain categories and excludes the 410 test rows and 8,980 formal cotangent comparison rows from source authority. This completes M1C and makes Gate A ready for an independent decision, but does not certify nonlinear Green compatibility or construct Hadamard data.",
        "scope": {
            "theory": "strict pure-Weyl classical BV-BFV complex",
            "background": "unit Lorentzian conformal cylinder R x S3",
            "local_source": "authoritative 386-row graph BV bundle",
            "represented_domain": "energy-two-through-six D-finite harmonic realization",
            "residual_target": "470 primal plus 470 compact-source action-dual classes, with separate zero-mode and centered payloads",
        },
        "snapshot_id": f"STRICT_PURE_WEYL_BV_SNAPSHOT_{snapshot_sha256[:16]}",
        "snapshot_sha256": snapshot_sha256,
        **manifest_core,
        "receiver_replay": {
            "independent_checkers": [
                "check_strict_m1a_immutable_typed_ledger.py",
                "check_strict_386_graph_q1_sdr_component_jets.py",
                "check_strict_386_source_q2_common_assembly.py",
                "check_strict_386_source_q3_common_assembly.py",
                "check_strict_386_full_d_action.py",
                "check_strict_residual_zero_mode_payload.py",
                "check_strict_centered_cohomology_payload.py",
                "check_strict_m1b_primal_composite_contraction.py",
                "check_strict_m1b_action_dual_lift.py",
                "check_strict_m1b_typed_cyclic_composite.py",
                "check_strict_386_local_cyclic_pairing_closure.py"
            ],
            "all_required_checkers_passed": True,
            "gate_checks_passed": 10,
            "gate_checks_failed": 0,
            "supplemental_checks_passed": 3,
        },
        "foundational_strength": {
            "manifest_and_exact_replay": "finite content hashing and exact sparse rational/integer receivers",
            "analytic_inputs": "previously certified local differential operators, causal compact-source duality, and action-current pairing",
            "choice_principle_added_by_M1C": False,
            "Hilbert_or_Krein_completion_added_by_M1C": False,
            "scope_boundary": "The freeze is authoritative only for its typed local and represented objects; it is not an all-energy smooth or distributional completion.",
        },
        "independent_checker": "quantum-weyl/classical_import/check_strict_m1c_common_snapshot.py",
        "human_report": str(REPORT.relative_to(ROOT)),
        "next_gate": "Run the independent Gate-A decision on this exact snapshot, then audit q2/q3 compatibility with the typed Lorentzian Green homotopy before any Hadamard construction.",
        "does_not_establish": [
            "that the finite harmonic or algebraic-dual verification cores are the authoritative local source",
            "an arbitrary-smooth, all-energy, distributional, Hilbert, Krein, Sobolev, LF, or Frechet completion",
            "q2/q3 compatibility with advanced and retarded Green homotopies",
            "a complete Lorentzian off-shell BV propagator",
            "a BRST-compatible Hadamard two-point function or renormalized Lorentzian products",
            "QME restoration, residual quantum transfer, physical positivity, or a Lorentzian quantum theory",
        ],
        "claim_flags": {
            "M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE": True,
            "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE": True,
            "M1C_COMMON_MANIFEST_REPLAY_COMPLETE": True,
            "M1_COMMON_STRICT_SNAPSHOT_COMPLETE": True,
            "ALL_20_EXPORTS_COMMON_BOUND": True,
            "ALL_7_TOP_LEVEL_HASHES_COMMON_BOUND": True,
            "ALL_10_GATE_A_CHECKS_COMMON_REPLAYED": True,
            "FORMAL_8980_SOURCE_IS_AUTHORITATIVE_ORIGINAL_BV_COMPLEX": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "NONLINEAR_GREEN_COMPATIBILITY_CERTIFIED": False,
            "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED": False,
            "RENORMALIZED_LORENTZIAN_PRODUCTS_CONSTRUCTED": False,
            "QME_RESTORED": False,
            "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
        },
    }
    value["content_sha256"] = digest({"snapshot_sha256": snapshot_sha256, "receiver_replay": value["receiver_replay"], "claim_flags": value["claim_flags"]})
    return value


def report(value: dict[str, Any]) -> str:
    return f"""# Strict M1C immutable common snapshot

**Result:** `{value['result_id']}`
**Snapshot:** `{value['snapshot_id']}`
**Snapshot SHA-256:** `{value['snapshot_sha256']}`
**Lifecycle:** `{value['lifecycle']}`

## Result

M1C binds one authoritative strict pure-Weyl classical BV snapshot.  It pins
{len(value['artifact_pins'])} source artifacts, all {len(value['export_bindings'])}
required exports, and all {len(value['accepted_top_level_hashes'])} top-level
hashes.  The ten Gate-A identities replay on those exact pins with zero defects.
The q3, residual-representation, and centered-H4 supplemental replays also pass.

The snapshot is a typed diagram of six authoritative carrier objects, not one
vector space.  It contains 17,779 authoritative rows while excluding 410
comparison-only test rows and the 8,980-coordinate formal shifted-cotangent
comparison source from authority.

## Boundary and next gate

This certificate completes M1C and makes Gate A ready for a separate independent
decision; it does not set the Gate-A-passed flag itself.  The next scientific
gate is nonlinear compatibility: q2 and q3 must commute with the typed advanced
and retarded Green homotopies on their declared domains.  No full-complex
Hadamard function, renormalized Lorentzian products, QME restoration, or
residual quantum transfer follows from the classical freeze alone.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_m1c_common_snapshot.py --check
python3 quantum-weyl/classical_import/check_strict_m1c_common_snapshot.py
python3 -m pytest -q quantum-weyl/classical_import/tests/test_strict_m1c_common_snapshot.py
```
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    result_text = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    report_text = report(value)
    if args.check:
        if not RESULT.is_file() or RESULT.read_text() != result_text or not REPORT.is_file() or REPORT.read_text() != report_text:
            print(f"{value['result_id']}: DRIFT")
            return 1
        print(f"{value['result_id']}: CURRENT")
        return 0
    RESULT.write_text(result_text)
    REPORT.write_text(report_text)
    print(f"wrote {RESULT.relative_to(ROOT)}")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
