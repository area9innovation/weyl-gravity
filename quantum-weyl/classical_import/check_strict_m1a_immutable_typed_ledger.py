#!/usr/bin/env python3
"""Independent receiver for the M1A4 immutable typed ledger."""

from __future__ import annotations

import copy
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
INPUTS = (GRADING, LOCAL_EXTENSION, REPRESENTED, ZERO_MODES, CENTERED, FORMAL, PREFLIGHT)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def is_na(value: Any) -> bool:
    return isinstance(value, dict) and value.get("status") == "NOT_APPLICABLE" and bool(value.get("reason"))


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    grading, extension, represented, zero, centered, formal, preflight = [load(path) for path in INPUTS]
    if value.get("result_id") != "STRICT_M1A_IMMUTABLE_TYPED_LEDGER_V1" or value.get("lifecycle") != "CLASSIFIED":
        errors.append("identity/lifecycle")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"]:
        errors.append("dependency tags")
    provenance = {row.get("path"): row for row in value.get("provenance", {}).get("inputs", [])}
    for path in INPUTS:
        relative = str(path.relative_to(ROOT))
        if provenance.get(relative, {}).get("sha256") != file_hash(path):
            errors.append(f"input hash {relative}")
    if preflight["authoritative_source_decision"]["snapshot_shape"] != "CONTENT_ADDRESSED_TYPED_DIAGRAM_NOT_ONE_VECTOR_SPACE":
        errors.append("typed diagram prerequisite")

    local_rows = value.get("local_386_rows", [])
    if len(local_rows) != 386 or [row.get("index") for row in local_rows] != list(range(386)):
        errors.append("local row order/count")
    else:
        endpoints = grading["local_endpoint_typed_rows"]
        for source, row in zip(endpoints, local_rows[:30], strict=True):
            for field in ("index", "row_id", "block", "role", "bv_ghost_number", "chain_degree", "antifield_number", "form_degree", "Grassmann_parity", "mass_dimension", "Weyl_weight", "intrinsic_jet_order_bound"):
                if row.get(field) != source.get(field):
                    errors.append(f"endpoint row semantics {source['row_id']}:{field}")
            if not is_na(row.get("conformal_compact_weight")) or not is_na(row.get("ce_ghost_number")) or row.get("semantic_state") != "FULLY_NAMESPACED":
                errors.append(f"endpoint namespaces {source['row_id']}")
        if local_rows[30:] != extension["local_extension_rows"]:
            errors.append("local extension payload")
        required = (
            "role", "tensor_type", "bv_ghost_number", "chain_degree", "antifield_number", "form_degree",
            "Grassmann_parity", "mass_dimension", "Weyl_weight", "conformal_compact_weight",
            "ce_ghost_number", "intrinsic_jet_order_bound", "semantic_state", "authority",
        )
        if any(any(field not in row for field in required) for row in local_rows):
            errors.append("local required namespace fields")

    zero_rows = value.get("zero_mode_rows", [])
    basis = zero["zero_mode_basis"]
    expected_labels = basis["canonical_generator_order"] + basis["canonical_dual_order"]
    expected_weights = basis["compact_degrees"] + basis["dual_compact_degrees"]
    if len(zero_rows) != 30:
        errors.append("zero-mode row count")
    else:
        for index, (row, label, weight) in enumerate(zip(zero_rows, expected_labels, expected_weights, strict=True)):
            expected_role = "CONFORMAL_ZERO_MODE_GENERATOR" if index < 15 else "CONFORMAL_ZERO_MODE_ACTION_DUAL"
            if (row.get("index"), row.get("label"), row.get("carrier_role"), row.get("conformal_compact_weight")) != (index, label, expected_role, weight):
                errors.append(f"zero-mode row {index}")
            for field in ("chain_degree", "bv_ghost_number", "antifield_number", "form_degree", "Grassmann_parity", "mass_dimension", "Weyl_weight", "ce_ghost_number", "intrinsic_jet_order_bound"):
                if not is_na(row.get(field)):
                    errors.append(f"zero-mode namespace {index}:{field}")

    centered_rows = value.get("centered_cochain_row_index", [])
    cursor = 0
    for degree_text in ("3", "4", "5"):
        block = centered["ordered_centered_cochain_basis"]["degrees"][degree_text]
        for local_index, entry in enumerate(block["entries"]):
            if cursor >= len(centered_rows):
                errors.append("centered row truncation")
                break
            row = centered_rows[cursor]
            sector, ghost_monomial, state_index = entry
            expected = {
                "index": cursor, "cochain_degree": int(degree_text), "degree_local_index": local_index,
                "sector": sector, "ghost_monomial_indices": ghost_monomial,
                "transferred_state_index": state_index, "ce_ghost_number": block["ghost_number"],
                "conformal_compact_weight": block["total_compact_degree"],
                "semantic_template": "CENTERED_RESIDUAL_CE_COCHAIN_NOT_LOCAL_BV_ROW",
            }
            if any(row.get(key) != expected_value for key, expected_value in expected.items()):
                errors.append(f"centered row {cursor}")
            cursor += 1
    if cursor != 12343 or len(centered_rows) != 12343:
        errors.append("centered row count")
    template = value.get("semantic_templates", {}).get("CENTERED_RESIDUAL_CE_COCHAIN_NOT_LOCAL_BV_ROW", {})
    for field in ("chain_degree", "bv_ghost_number", "antifield_number", "form_degree", "Grassmann_parity", "mass_dimension", "Weyl_weight", "intrinsic_jet_order_bound"):
        if not is_na(template.get(field)):
            errors.append(f"centered template {field}")

    rep_hashes = represented["row_payload_hashes"]
    expected_components = [
        ("LOCAL_GRAPH_BV_386", "LOCAL_COMPONENT_JET", 386, canonical_digest(local_rows), "AUTHORITATIVE_TYPED_SOURCE"),
        ("REPRESENTED_ENDPOINT_DFINITE_4080", "REDUCED_MODE_GLOBAL_HARMONIC", 4080, rep_hashes["represented_endpoint_rows_sha256"], "AUTHORITATIVE_TYPED_REPRESENTED_DOMAIN"),
        ("ACTION_RESIDUAL_PRIMAL_470", "REDUCED_MODE_CAUSAL_COHOMOLOGY", 470, rep_hashes["action_residual_primal_rows_sha256"], "AUTHORITATIVE_TYPED_REPRESENTED_TARGET"),
        ("ACTION_RESIDUAL_DUAL_470", "COMPACT_SOURCE_ACTION_DUAL", 470, rep_hashes["action_residual_dual_rows_sha256"], "AUTHORITATIVE_TYPED_REPRESENTED_ACTION_DUAL"),
        ("ZERO_MODE_15_PLUS_15", "RESIDUAL_ZERO_MODE", 30, canonical_digest(zero_rows), "AUTHORITATIVE_TYPED_SCOPED_PAYLOAD"),
        ("CENTERED_C3_C4_C5", "RESIDUAL_COCHAIN", 12343, canonical_digest([centered_rows, value.get("semantic_templates", {})]), "AUTHORITATIVE_TYPED_SCOPED_PAYLOAD"),
    ]
    components = value.get("component_payloads", [])
    if len(components) != 6:
        errors.append("component count")
    else:
        for row, expected in zip(components, expected_components, strict=True):
            if (row.get("carrier_id"), row.get("category"), row.get("row_count"), row.get("row_payload_sha256"), row.get("status")) != expected:
                errors.append(f"component payload {expected[0]}")

    exclusions = value.get("exclusion_ledger", [])
    if len(exclusions) != 2:
        errors.append("exclusion count")
    else:
        test, formal_row = exclusions
        if (test.get("carrier_id"), test.get("row_count"), test.get("row_payload_sha256"), test.get("disposition")) != (
            "TEST_NONMINIMAL_COMPARISON_410", 410, rep_hashes["test_nonminimal_rows_sha256"], "EXCLUDED_FROM_AUTHORITATIVE_LOCAL_SOURCE"
        ):
            errors.append("test exclusion")
        if (formal_row.get("carrier_id"), formal_row.get("row_count"), formal_row.get("row_payload_sha256"), formal_row.get("disposition")) != (
            "FORMAL_COTANGENT_COMPARISON_8980", formal["formal_cotangent_completion"]["full_dimension"], file_hash(FORMAL), "COMPARISON_ONLY_NOT_AUTHORITATIVE_ORIGINAL_BV_SOURCE"
        ):
            errors.append("formal exclusion")

    dictionary = value.get("typed_field_dictionary", {})
    expected_dictionary = {
        "namespace_contract_sha256": canonical_digest(grading["namespace_contract"]),
        "ordered_authoritative_carriers": [row[0] for row in expected_components],
        "component_row_hashes": {row[0]: row[3] for row in expected_components},
        "semantic_templates_sha256": canonical_digest(value.get("semantic_templates", {})),
        "exclusion_ledger_sha256": canonical_digest(exclusions),
    }
    expected_dictionary["sha256"] = canonical_digest(expected_dictionary)
    if dictionary != expected_dictionary:
        errors.append("typed field dictionary hash")
    diagram = value.get("diagram_freeze", {})
    expected_diagram = {
        "shape": "CONTENT_ADDRESSED_TYPED_DIAGRAM_NOT_ONE_VECTOR_SPACE",
        "authoritative_row_count": 17779,
        "comparison_excluded_row_count": 9390,
        "component_payloads": components,
        "typed_field_dictionary_sha256": expected_dictionary["sha256"],
        "all_component_hashes_nonempty": True,
        "all_authoritative_rows_have_a_materialization_rule": True,
        "distinct_categories_not_identified": True,
    }
    expected_diagram["sha256"] = canonical_digest(expected_diagram)
    if diagram != expected_diagram:
        errors.append("diagram freeze hash")

    expected_counts = {
        "local_rows": 386, "represented_endpoint_rows": 4080,
        "action_residual_primal_rows": 470, "action_residual_dual_rows": 470,
        "zero_mode_rows": 30, "centered_cochain_rows": 12343,
        "authoritative_rows_total": 17779, "excluded_test_rows": 410,
        "excluded_formal_comparison_rows": 8980, "authoritative_carrier_objects": 6,
        "exclusion_objects": 2, "untyped_authoritative_rows": 0,
        "category_identification_defects": 0,
    }
    if value.get("counts") != expected_counts:
        errors.append("counts")

    flags = value.get("claim_flags", {})
    for flag in (
        "M1A1_NAMESPACE_CONTRACT_ADOPTED", "M1A2_LOCAL_386_FULLY_TYPED",
        "M1A3_REPRESENTED_CROSSWALK_COMPLETE", "M1A4_IMMUTABLE_LEDGER_FREEZE_COMPLETE",
        "M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE", "ALL_AUTHORITATIVE_ROWS_CONTENT_ADDRESSED",
    ):
        if flags.get(flag) is not True:
            errors.append(f"positive flag {flag}")
    for flag in (
        "TEST_NONMINIMAL_410_IS_AUTHORITATIVE_LOCAL_SOURCE", "FORMAL_8980_SOURCE_IS_AUTHORITATIVE_ORIGINAL_BV_COMPLEX",
        "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE", "M1C_COMMON_MANIFEST_REPLAY_COMPLETE",
        "CLASSICAL_IMPORT_GATE_PASSED", "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED",
        "RENORMALIZED_LORENTZIAN_PRODUCTS_CONSTRUCTED", "QME_RESTORED", "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
    ):
        if flags.get(flag) is not False:
            errors.append(f"fail-closed flag {flag}")

    replay = copy.deepcopy(value)
    expected_digest = replay.get("independent_checker", {}).get("expected_digest")
    replay.setdefault("independent_checker", {})["expected_digest"] = ""
    if expected_digest != canonical_digest(replay):
        errors.append("certificate digest")
    if not REPORT.exists():
        errors.append("human report absent")
    else:
        report = REPORT.read_text(encoding="utf-8")
        for token in ("17,779", "4,080", "12,343", "410 scalar test", "8,980-dimensional", "M1B", "Gate A", "Hadamard", "QME"):
            if token not in report:
                errors.append(f"report token {token}")
    return errors


def main() -> int:
    errors = check(load(RESULT))
    if errors:
        print("STRICT_M1A_IMMUTABLE_TYPED_LEDGER_V1: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("STRICT_M1A_IMMUTABLE_TYPED_LEDGER_V1: PASS")
    print("  - 17,779 authoritative rows content-addressed across six typed carrier objects")
    print("  - 410 test and 8,980 formal comparison rows remain explicit exclusions")
    print("  - M1A complete; M1B, M1C, Gate A, Hadamard and QME remain fail closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
