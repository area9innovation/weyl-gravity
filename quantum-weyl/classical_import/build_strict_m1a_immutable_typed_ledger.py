#!/usr/bin/env python3
"""Freeze M1A4 as one content-addressed typed carrier diagram."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_M1A_IMMUTABLE_TYPED_LEDGER_V1.json"
REPORT = HERE / "REPORT_STRICT_M1A_IMMUTABLE_TYPED_LEDGER_V1.md"
GRADING = HERE / "certificates/STRICT_M1A_CARRIER_GRADING_CONVENTION_AUDIT_V1.json"
LOCAL_EXTENSION = HERE / "certificates/STRICT_M1A_LOCAL_SEMANTIC_EXTENSION_V1.json"
REPRESENTED = HERE / "certificates/STRICT_M1A_REPRESENTED_CARRIER_CROSSWALK_V1.json"
ZERO_MODES = HERE / "certificates/STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1.json"
CENTERED = HERE / "certificates/STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1.json"
FORMAL = HERE / "certificates/STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1.json"
PREFLIGHT = HERE / "certificates/STRICT_M1_COMMON_SNAPSHOT_PREFLIGHT_V1.json"

INPUTS = (
    (GRADING, "STRICT_M1A_CARRIER_GRADING_CONVENTION_AUDIT_V1", "namespaced grading contract and thirty local endpoint rows"),
    (LOCAL_EXTENSION, "STRICT_M1A_LOCAL_SEMANTIC_EXTENSION_V1", "356-row local semantic extension"),
    (REPRESENTED, "STRICT_M1A_REPRESENTED_CARRIER_CROSSWALK_V1", "4,080 represented rows, 410-row exclusion ledger and 940 action-residual rows"),
    (ZERO_MODES, "STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1", "fifteen plus fifteen zero-mode cotangent rows"),
    (CENTERED, "STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1", "ordered centered C3/C4/C5 cochain dictionaries"),
    (FORMAL, "STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1", "excluded formal-cotangent comparison category"),
    (PREFLIGHT, "STRICT_M1_COMMON_SNAPSHOT_PREFLIGHT_V1", "M1A/M1B/M1C typed-diagram contract"),
)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def na(reason: str) -> dict[str, str]:
    return {"status": "NOT_APPLICABLE", "reason": reason}


def normalized_local_rows(grading: dict[str, Any], extension: dict[str, Any]) -> list[dict[str, Any]]:
    endpoint: list[dict[str, Any]] = []
    component_tensor = {
        "xi": "contravariant vector ghost", "omega": "scalar ghost", "g": "symmetric covariant two-tensor",
        "g_star": "symmetric contravariant two-tensor density", "xi_star": "covector density",
        "omega_star": "scalar density",
    }
    for source in grading["local_endpoint_typed_rows"]:
        row = dict(source)
        species = source["authority"]["generator"].rsplit("/", 1)[-1]
        row["tensor_type"] = component_tensor[species]
        row["conformal_compact_weight"] = na("local component row, not a compact conformal eigenspace")
        row["ce_ghost_number"] = na("local BV coordinate, not a residual CE cochain")
        row["semantic_state"] = "FULLY_NAMESPACED"
        endpoint.append(row)
    rows = endpoint + extension["local_extension_rows"]
    rows.sort(key=lambda row: row["index"])
    if len(rows) != 386 or [row["index"] for row in rows] != list(range(386)):
        raise ValueError("local row union drift")
    required = (
        "role", "tensor_type", "bv_ghost_number", "chain_degree", "antifield_number", "form_degree",
        "Grassmann_parity", "mass_dimension", "Weyl_weight", "conformal_compact_weight",
        "ce_ghost_number", "intrinsic_jet_order_bound", "semantic_state", "authority",
    )
    if any(any(field not in row for field in required) for row in rows):
        raise ValueError("local row namespace incomplete")
    return rows


def zero_mode_rows(zero: dict[str, Any]) -> list[dict[str, Any]]:
    basis = zero["zero_mode_basis"]
    rows: list[dict[str, Any]] = []
    local_na = {
        "chain_degree": na("zero-mode symmetry/cotangent coordinate, not a local q1 row"),
        "bv_ghost_number": na("zero-mode residual role is kept distinct from local BV generator grading"),
        "antifield_number": na("zero-mode residual role is kept distinct from local Koszul-Tate filtration"),
        "form_degree": na("global residual coordinate, not a local differential form"),
        "Grassmann_parity": na("no local BV parity is assigned to this global residual basis row"),
        "mass_dimension": na("global conformal generator coordinate, not an action-normalized local field"),
        "Weyl_weight": na("global conformal generator coordinate, not a local Weyl eigenfield"),
        "ce_ghost_number": na("generator/cotangent carrier underlying the CE complex, not itself a centered cochain row"),
        "intrinsic_jet_order_bound": na("global polynomial zero mode, not a local jet coordinate"),
    }
    for index, (label, weight) in enumerate(zip(basis["canonical_generator_order"], basis["compact_degrees"], strict=True)):
        rows.append({
            "index": index, "label": label, "carrier_role": "CONFORMAL_ZERO_MODE_GENERATOR",
            "conformal_compact_weight": weight, **local_na,
            "semantic_state": "FULLY_NAMESPACED_RESIDUAL_ZERO_MODE_GENERATOR",
            "authority": f"{ZERO_MODES.relative_to(ROOT)}#/zero_mode_basis/canonical_generator_order/{index}",
        })
    for index, (label, weight) in enumerate(zip(basis["canonical_dual_order"], basis["dual_compact_degrees"], strict=True)):
        rows.append({
            "index": 15 + index, "label": label, "carrier_role": "CONFORMAL_ZERO_MODE_ACTION_DUAL",
            "conformal_compact_weight": weight, **local_na,
            "semantic_state": "FULLY_NAMESPACED_RESIDUAL_ZERO_MODE_ACTION_DUAL",
            "authority": f"{ZERO_MODES.relative_to(ROOT)}#/zero_mode_basis/canonical_dual_order/{index}",
        })
    return rows


def centered_rows(centered: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for degree_text in ("3", "4", "5"):
        degree = int(degree_text)
        block = centered["ordered_centered_cochain_basis"]["degrees"][degree_text]
        for local_index, entry in enumerate(block["entries"]):
            sector, ghost_monomial, state_index = entry
            rows.append({
                "index": len(rows),
                "cochain_degree": degree,
                "degree_local_index": local_index,
                "sector": sector,
                "ghost_monomial_indices": ghost_monomial,
                "transferred_state_index": state_index,
                "ce_ghost_number": block["ghost_number"],
                "conformal_compact_weight": block["total_compact_degree"],
                "semantic_template": "CENTERED_RESIDUAL_CE_COCHAIN_NOT_LOCAL_BV_ROW",
                "authority": f"{CENTERED.relative_to(ROOT)}#/ordered_centered_cochain_basis/degrees/{degree_text}/entries/{local_index}",
            })
    if len(rows) != 727 + 3084 + 8532:
        raise ValueError("centered cochain row count drift")
    return rows


def build() -> dict[str, Any]:
    source = {path: load(path) for path, _, _ in INPUTS}
    for path, expected, _ in INPUTS:
        if source[path].get("result_id") != expected:
            raise ValueError(f"dependency identity drift: {path}")
    grading = source[GRADING]
    extension = source[LOCAL_EXTENSION]
    represented = source[REPRESENTED]
    zero = source[ZERO_MODES]
    centered = source[CENTERED]
    formal = source[FORMAL]
    preflight = source[PREFLIGHT]
    if preflight["authoritative_source_decision"]["snapshot_shape"] != "CONTENT_ADDRESSED_TYPED_DIAGRAM_NOT_ONE_VECTOR_SPACE":
        raise ValueError("M1 typed-diagram contract drift")
    if represented["claim_flags"]["M1A3_REPRESENTED_CROSSWALK_COMPLETE"] is not True:
        raise ValueError("M1A3 prerequisite drift")

    local_rows = normalized_local_rows(grading, extension)
    zero_rows = zero_mode_rows(zero)
    centered_index = centered_rows(centered)
    represented_hashes = represented["row_payload_hashes"]
    semantic_templates = {
        "CENTERED_RESIDUAL_CE_COCHAIN_NOT_LOCAL_BV_ROW": {
            "role": "centered residual Chevalley-Eilenberg cochain basis monomial",
            "chain_degree": na("CE differential degree is namespaced separately from local q1 chain degree"),
            "bv_ghost_number": na("residual CE cochain degree is not local BV ghost number"),
            "antifield_number": na("residual CE cochain, not a local Koszul-Tate row"),
            "form_degree": na("residual CE cochain, not a local spacetime form"),
            "Grassmann_parity": na("the serialized CE degree is authoritative; no local field parity is assigned"),
            "mass_dimension": na("residual cochain basis, not an action-normalized local field"),
            "Weyl_weight": na("total compact degree is namespaced separately from local Weyl weight"),
            "intrinsic_jet_order_bound": na("residual cochain basis, not a local jet coordinate"),
        }
    }

    component_payloads = [
        {
            "carrier_id": "LOCAL_GRAPH_BV_386", "category": "LOCAL_COMPONENT_JET", "row_count": 386,
            "authority": "embedded:local_386_rows", "row_payload_sha256": digest(local_rows),
            "status": "AUTHORITATIVE_TYPED_SOURCE",
        },
        {
            "carrier_id": "REPRESENTED_ENDPOINT_DFINITE_4080", "category": "REDUCED_MODE_GLOBAL_HARMONIC", "row_count": 4080,
            "authority": f"{REPRESENTED.relative_to(ROOT)}#/represented_endpoint_rows",
            "row_payload_sha256": represented_hashes["represented_endpoint_rows_sha256"],
            "status": "AUTHORITATIVE_TYPED_REPRESENTED_DOMAIN",
        },
        {
            "carrier_id": "ACTION_RESIDUAL_PRIMAL_470", "category": "REDUCED_MODE_CAUSAL_COHOMOLOGY", "row_count": 470,
            "authority": f"{REPRESENTED.relative_to(ROOT)}#/action_residual_primal_rows",
            "row_payload_sha256": represented_hashes["action_residual_primal_rows_sha256"],
            "status": "AUTHORITATIVE_TYPED_REPRESENTED_TARGET",
        },
        {
            "carrier_id": "ACTION_RESIDUAL_DUAL_470", "category": "COMPACT_SOURCE_ACTION_DUAL", "row_count": 470,
            "authority": f"{REPRESENTED.relative_to(ROOT)}#/action_residual_dual_rows",
            "row_payload_sha256": represented_hashes["action_residual_dual_rows_sha256"],
            "status": "AUTHORITATIVE_TYPED_REPRESENTED_ACTION_DUAL",
        },
        {
            "carrier_id": "ZERO_MODE_15_PLUS_15", "category": "RESIDUAL_ZERO_MODE", "row_count": 30,
            "authority": "embedded:zero_mode_rows", "row_payload_sha256": digest(zero_rows),
            "status": "AUTHORITATIVE_TYPED_SCOPED_PAYLOAD",
        },
        {
            "carrier_id": "CENTERED_C3_C4_C5", "category": "RESIDUAL_COCHAIN", "row_count": len(centered_index),
            "authority": "embedded:centered_cochain_row_index+semantic_templates",
            "row_payload_sha256": digest([centered_index, semantic_templates]),
            "status": "AUTHORITATIVE_TYPED_SCOPED_PAYLOAD",
        },
    ]
    authoritative_rows = sum(row["row_count"] for row in component_payloads)
    if authoritative_rows != 17779:
        raise ValueError("authoritative typed row census drift")

    exclusion_ledger = [
        {
            "carrier_id": "TEST_NONMINIMAL_COMPARISON_410",
            "category": "REDUCED_MODE_COMPARISON_FIXTURE",
            "row_count": 410,
            "authority": f"{REPRESENTED.relative_to(ROOT)}#/test_nonminimal_rows",
            "row_payload_sha256": represented_hashes["test_nonminimal_rows_sha256"],
            "disposition": "EXCLUDED_FROM_AUTHORITATIVE_LOCAL_SOURCE",
            "reason": "no corresponding local endpoint species or action-derived local BV dictionary",
        },
        {
            "carrier_id": "FORMAL_COTANGENT_COMPARISON_8980",
            "category": "FORMAL_SHIFTED_COTANGENT",
            "row_count": formal["formal_cotangent_completion"]["full_dimension"],
            "authority": str(FORMAL.relative_to(ROOT)),
            "row_payload_sha256": file_hash(FORMAL),
            "disposition": "COMPARISON_ONLY_NOT_AUTHORITATIVE_ORIGINAL_BV_SOURCE",
            "reason": "formal dualization supplies an exact finite control but is not the action-derived local graph carrier",
        },
    ]
    typed_field_dictionary = {
        "namespace_contract_sha256": digest(grading["namespace_contract"]),
        "ordered_authoritative_carriers": [row["carrier_id"] for row in component_payloads],
        "component_row_hashes": {row["carrier_id"]: row["row_payload_sha256"] for row in component_payloads},
        "semantic_templates_sha256": digest(semantic_templates),
        "exclusion_ledger_sha256": digest(exclusion_ledger),
    }
    typed_field_dictionary["sha256"] = digest(typed_field_dictionary)
    diagram_freeze = {
        "shape": "CONTENT_ADDRESSED_TYPED_DIAGRAM_NOT_ONE_VECTOR_SPACE",
        "authoritative_row_count": authoritative_rows,
        "comparison_excluded_row_count": 410 + 8980,
        "component_payloads": component_payloads,
        "typed_field_dictionary_sha256": typed_field_dictionary["sha256"],
        "all_component_hashes_nonempty": all(row["row_payload_sha256"] for row in component_payloads),
        "all_authoritative_rows_have_a_materialization_rule": True,
        "distinct_categories_not_identified": True,
    }
    diagram_freeze["sha256"] = digest(diagram_freeze)

    value: dict[str, Any] = {
        "$schema": "../schema/strict-m1a-immutable-typed-ledger-v1.schema.json",
        "schema": "strict-m1a-immutable-typed-ledger-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-m1a-immutable-typed-ledger-v1.schema.json",
        "result_id": "STRICT_M1A_IMMUTABLE_TYPED_LEDGER_V1",
        "result_kind": "M1A4_CONTENT_ADDRESSED_TYPED_CARRIER_DIAGRAM_FREEZE",
        "result_state": "M1A_TYPED_LEDGER_COMPLETE_M1B_M1C_AND_GATE_A_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-16",
        "repository_base_commit": "a03539c2d82920e945cb776186531b95e993a105",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "question": "Can the completed local and represented semantics be frozen as one authoritative typed diagram while preserving the zero-mode, centered, comparison-only and formal-dual category boundaries?",
        "answer": "Yes. The freeze binds 17,779 authoritative rows across six distinct carrier objects: 386 local graph rows, 4,080 represented endpoint coordinates, 470 primal plus 470 action-dual residual coordinates, 30 zero-mode cotangent coordinates and 12,343 centered CE cochains. The 410 test-doublet rows and formal 8,980-coordinate cotangent comparison remain explicit exclusions. Every row is either embedded here or materializable from a content-addressed row payload and semantic template. This completes M1A, but M1B must still construct the represented composite contraction and M1C must bind all Gate-A exports and replay them on one snapshot.",
        "scope": {
            "theory": "strict pure-Weyl classical BV import",
            "background": "unit conformal cylinder",
            "freeze_shape": "typed diagram with distinct local, harmonic, action-dual, zero-mode and CE objects",
            "arithmetic": "finite exact row materialization and SHA-256 content addressing",
        },
        "namespace_contract": grading["namespace_contract"],
        "semantic_templates": semantic_templates,
        "local_386_rows": local_rows,
        "zero_mode_rows": zero_rows,
        "centered_cochain_row_index": centered_index,
        "component_payloads": component_payloads,
        "exclusion_ledger": exclusion_ledger,
        "typed_field_dictionary": typed_field_dictionary,
        "diagram_freeze": diagram_freeze,
        "counts": {
            "local_rows": 386,
            "represented_endpoint_rows": 4080,
            "action_residual_primal_rows": 470,
            "action_residual_dual_rows": 470,
            "zero_mode_rows": 30,
            "centered_cochain_rows": 12343,
            "authoritative_rows_total": authoritative_rows,
            "excluded_test_rows": 410,
            "excluded_formal_comparison_rows": 8980,
            "authoritative_carrier_objects": len(component_payloads),
            "exclusion_objects": len(exclusion_ledger),
            "untyped_authoritative_rows": 0,
            "category_identification_defects": 0,
        },
        "foundational_strength": {
            "freeze_base": "primitive-recursive finite enumeration, tagged unions and decidable hash equality",
            "choice_used": False,
            "completion_used_by_freeze": False,
            "analytic_content": "No new analytic theorem; represented action-dual meaning remains imported under its LORENTZIAN-CAUSAL certificate.",
        },
        "gate_a_effect": {
            "M1A_status": "COMPLETE",
            "field_dictionary_candidate_sha256": typed_field_dictionary["sha256"],
            "typed_diagram_candidate_sha256": diagram_freeze["sha256"],
            "accepted_common_snapshot_hash": False,
            "reason_not_accepted": "M1B composite maps and pairing are not yet serialized on this diagram, and M1C has not replayed all Gate-A checks on one immutable manifest",
        },
        "claim_flags": {
            "M1A1_NAMESPACE_CONTRACT_ADOPTED": True,
            "M1A2_LOCAL_386_FULLY_TYPED": True,
            "M1A3_REPRESENTED_CROSSWALK_COMPLETE": True,
            "M1A4_IMMUTABLE_LEDGER_FREEZE_COMPLETE": True,
            "M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE": True,
            "ALL_AUTHORITATIVE_ROWS_CONTENT_ADDRESSED": True,
            "TEST_NONMINIMAL_410_IS_AUTHORITATIVE_LOCAL_SOURCE": False,
            "FORMAL_8980_SOURCE_IS_AUTHORITATIVE_ORIGINAL_BV_COMPLEX": False,
            "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE": False,
            "M1C_COMMON_MANIFEST_REPLAY_COMPLETE": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED": False,
            "RENORMALIZED_LORENTZIAN_PRODUCTS_CONSTRUCTED": False,
            "QME_RESTORED": False,
            "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
        },
        "does_not_establish": [
            "that the typed diagram is one vector space or that its carrier categories are interchangeable",
            "a support-local identification of global harmonic coefficients with fixed local component rows",
            "that the 410 test rows or formal 8,980 cotangent rows belong to the authoritative original BV source",
            "the M1B composite inclusion, projection, homotopy or action pairing on these exact bytes",
            "the M1C twenty-export, seven-hash and ten-check common replay",
            "a passed classical import gate",
            "a full-complex Hadamard state, renormalized Lorentzian products, QME restoration or residual quantum transfer",
        ],
        "next_gate": "Construct M1B by materializing pi_cl, iota_cl, s_cl and the action pairing across this exact typed diagram, with the local 386-to-30 support-local SDR and the represented 30-to-940 analysis/action-dual stages kept as distinct composed arrows.",
        "human_report": str(REPORT.relative_to(ROOT)),
        "provenance": {
            "inputs": [
                {"path": str(path.relative_to(ROOT)), "result_id": result_id, "sha256": file_hash(path), "role": role}
                for path, result_id, role in INPUTS
            ],
            "producer": str(Path(__file__).resolve().relative_to(ROOT)),
        },
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_m1a_immutable_typed_ledger.py",
            "method": "re-materialize local, zero-mode and centered rows; replay every external row hash, exclusion and diagram hash from pinned source certificates",
            "expected_digest": "",
        },
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def report(value: dict[str, Any]) -> str:
    components = "\n".join(
        f"| `{row['carrier_id']}` | `{row['category']}` | {row['row_count']:,} | `{row['status']}` |"
        for row in value["component_payloads"]
    )
    exclusions = "\n".join(
        f"| `{row['carrier_id']}` | {row['row_count']:,} | `{row['disposition']}` |"
        for row in value["exclusion_ledger"]
    )
    return f"""# Strict M1A4 immutable typed ledger v1

**Result:** `{value['result_id']}`
**Lifecycle:** `{value['lifecycle']}`
**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

## Outcome

M1A is complete.  One content-addressed typed diagram now binds **17,779
authoritative rows** without pretending that they form one vector space.
Every row is either embedded in this certificate or reconstructed from an
exact pinned row payload plus an explicit semantic template.

| Carrier object | Category | Rows | Status |
|---|---|---:|---|
{components}

The typed field-dictionary candidate is
`{value['typed_field_dictionary']['sha256']}` and the complete diagram freeze
is `{value['diagram_freeze']['sha256']}`.

## Explicit exclusions

| Object | Rows | Disposition |
|---|---:|---|
{exclusions}

The 410 scalar test rows remain a useful finite SDR control, and the formal
8,980-dimensional shifted cotangent remains an exact comparison.  Neither is
the action-derived local graph BV source.

## What the freeze means

The 386 local rows carry local BV semantics.  The 4,080 harmonic rows carry a
species-level realization plus compact energy.  The residual primal/action
dual rows carry represented cohomology and compact-source meaning.  The zero
modes carry conformal generator/cotangent weights, while the 12,343 centered
rows carry CE degree.  Nonapplicable gradings are tagged, never replaced by
zero or silently aliased.

The freeze itself uses only finite enumeration, tagged unions and content
hashes; it uses neither Choice nor an analytic completion.  Its compact-source
meaning remains imported from the separately certified Lorentzian causal
result.

## Remaining gate

This is not yet Gate A.  M1B must construct the composite `iota_cl`, `pi_cl`,
`s_cl` and action pairing on these exact carriers.  M1C must then bind all
twenty exports and seven hashes and replay all ten identities on one immutable
manifest.  No full-complex Hadamard state, renormalized Lorentzian products,
QME restoration or residual transfer is promoted.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    rendered = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    report_text = report(value)
    if args.check:
        ok = RESULT.exists() and REPORT.exists() and RESULT.read_text() == rendered and REPORT.read_text() == report_text
        print("STRICT_M1A_IMMUTABLE_TYPED_LEDGER_V1: CURRENT" if ok else "STRICT_M1A_IMMUTABLE_TYPED_LEDGER_V1: DRIFT")
        return 0 if ok else 1
    RESULT.write_text(rendered, encoding="utf-8")
    REPORT.write_text(report_text, encoding="utf-8")
    print(f"wrote {RESULT.relative_to(ROOT)}")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
