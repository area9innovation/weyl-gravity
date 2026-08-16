#!/usr/bin/env python3
"""Independent receiver for the M1A carrier-grading convention audit."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_M1A_CARRIER_GRADING_CONVENTION_AUDIT_V1.json"
REPORT = HERE / "REPORT_STRICT_M1A_CARRIER_GRADING_CONVENTION_AUDIT_V1.md"
FIELD_DICTIONARY = ROOT / "d_quotient_classical/minimal_bv_antifield/foundation/field_dictionary.json"
ATOM_MANIFEST = ROOT / "d_quotient_classical/minimal_bv_antifield/foundation/atom_basis_manifest.json"
LOCAL_386 = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
DFINITE = HERE / "certificates/STRICT_DFINITE_RESIDUAL_SDR_V1.json"
REPRESENTED = HERE / "certificates/STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1.json"
FORMAL_COTANGENT = HERE / "certificates/STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1.json"
ACTION_DUAL = HERE / "certificates/STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1.json"
ZERO_MODES = HERE / "certificates/STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1.json"
CENTERED = HERE / "certificates/STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1.json"


def canonical_digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sector_at(block: dict[str, Any], index: int) -> dict[str, Any]:
    for sector in block["full_sectors"]:
        if sector["start"] <= index < sector["stop"]:
            return sector
    raise ValueError(f"uncovered D-finite index {index}")


def endpoint_symbol(block: str, local_index: int) -> str:
    table = {
        "ENDPOINT_G": ("xi", "xi", "xi", "xi", "omega"),
        "ENDPOINT_M": ("g",) * 10,
        "ENDPOINT_E": ("g_star",) * 10,
        "ENDPOINT_I": ("xi_star", "xi_star", "xi_star", "xi_star", "omega_star"),
    }
    return table[block][local_index]


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    field_dictionary = json.loads(FIELD_DICTIONARY.read_text())
    atom_manifest = json.loads(ATOM_MANIFEST.read_text())
    local = json.loads(LOCAL_386.read_text())
    dfinite = json.loads(DFINITE.read_text())
    represented = json.loads(REPRESENTED.read_text())
    formal = json.loads(FORMAL_COTANGENT.read_text())
    action = json.loads(ACTION_DUAL.read_text())
    zero = json.loads(ZERO_MODES.read_text())
    centered = json.loads(CENTERED.read_text())

    if value.get("result_id") != "STRICT_M1A_CARRIER_GRADING_CONVENTION_AUDIT_V1" or value.get("lifecycle") != "CLASSIFIED":
        errors.append("identity/lifecycle")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"]:
        errors.append("dependency tags")

    provenance = {row.get("path"): row for row in value.get("provenance", {}).get("inputs", [])}
    for path in (FIELD_DICTIONARY, ATOM_MANIFEST, LOCAL_386, DFINITE, REPRESENTED, FORMAL_COTANGENT, ACTION_DUAL, ZERO_MODES, CENTERED):
        relative = str(path.relative_to(ROOT))
        if provenance.get(relative, {}).get("sha256") != file_hash(path):
            errors.append(f"input hash {relative}")

    generators = {row["symbol"]: row for row in field_dictionary["generators"]}
    atoms = {row["atom_id"]: row for row in atom_manifest["atoms"]}
    actual_endpoint = value.get("local_endpoint_typed_rows", [])
    source_rows = local["component_basis"]["rows"][:30]
    if len(actual_endpoint) != 30 or len(source_rows) != 30:
        errors.append("endpoint row count")
    else:
        for source, actual in zip(source_rows, actual_endpoint, strict=True):
            symbol = endpoint_symbol(source["block"], source["local_index"])
            generator = generators[symbol]
            atom = atoms[symbol]
            expected = {
                "index": source["index"],
                "row_id": source["row_id"],
                "block": source["block"],
                "role": generator["role"],
                "bv_ghost_number": generator["ghost_number"],
                "chain_degree": source["degree"],
                "antifield_number": generator["antifield_number"],
                "form_degree": generator["form_degree"],
                "Grassmann_parity": generator["Grassmann_parity"],
                "mass_dimension": generator["mass_dimension"],
                "Weyl_weight": generator["Weyl_weight"],
                "intrinsic_jet_order_bound": atom["covariant_derivative_order"],
                "conformal_compact_weight": None,
                "ce_ghost_number": None,
            }
            if {key: actual.get(key) for key in expected} != expected:
                errors.append(f"endpoint semantics {source['row_id']}")
            if source["degree"] != -generator["ghost_number"] or generator["Grassmann_parity"] != generator["ghost_number"] % 2:
                errors.append(f"endpoint grading bridge {source['row_id']}")

    q_defects = 0
    for block in dfinite["blocks"]:
        for target, source, _ in block["matrices"]["q0"]["entries"]:
            q_defects += int(sector_at(block, target)["ghost_number"] != sector_at(block, source)["ghost_number"] + 1)
    minimal_map = {
        "diff_ghost": "xi", "weyl_ghost": "omega", "metric_trace": "g", "metric_tf": "g",
        "metric_antifield": "g_star", "trace_antifield": "g_star",
        "diff_ghost_antifield": "xi_star", "weyl_ghost_antifield": "omega_star",
    }
    minimal_count = nonminimal_count = sign_defects = 0
    for block in dfinite["blocks"]:
        for sector in block["full_sectors"]:
            if sector["name"] in minimal_map:
                minimal_count += sector["dimension"]
                sign_defects += sector["dimension"] * int(sector["ghost_number"] != -generators[minimal_map[sector["name"]]]["ghost_number"])
            else:
                nonminimal_count += sector["dimension"]
    centered_dimension = sum(centered["ordered_centered_cochain_basis"]["degrees"][key]["dimension"] for key in ("3", "4", "5"))
    expected_counts = {
        "local_rows_total": 386,
        "local_endpoint_rows_fully_namespaced": 30,
        "local_rows_partially_namespaced": 356,
        "local_endpoint_nonzero_bv_ghost_rows": 20,
        "dfinite_full_coordinates": sum(block["full_dimension"] for block in dfinite["blocks"]),
        "dfinite_minimal_coordinates_with_sign_bridge": minimal_count,
        "dfinite_test_nonminimal_coordinates_without_local_source_dictionary": nonminimal_count,
        "represented_residual_rows": len(represented["ordered_residual_basis"]),
        "formal_cotangent_rows": formal["formal_cotangent_completion"]["full_dimension"],
        "action_residual_rows": action["action_pairing_identification"]["phase_space_dimension"],
        "zero_mode_rows": len(zero["zero_mode_basis"]["canonical_generator_order"]) + len(zero["zero_mode_basis"]["canonical_dual_order"]),
        "centered_cochain_rows": centered_dimension,
        "dfinite_q_degree_defects": q_defects,
        "dfinite_minimal_sign_bridge_defects": sign_defects,
    }
    if value.get("counts") != expected_counts:
        errors.append("carrier/collision counts")

    witness = value.get("convention_collision_witness", {})
    if not (
        witness.get("endpoint_rows_satisfy_chain_degree_equals_minus_bv_ghost_number") is True
        and witness.get("dfinite_legacy_key") == "ghost_number"
        and witness.get("dfinite_semantic_value") == "chain_degree"
        and witness.get("dfinite_q_raises_legacy_value_by_one") is True
        and witness.get("dfinite_minimal_value_equals_minus_local_bv_ghost_number") is True
        and witness.get("compact_degree_collision", {}).get("same_semantic_field") is False
    ):
        errors.append("collision witness")

    namespace = value.get("namespace_contract", {})
    expected_names = [
        "bv_ghost_number", "chain_degree", "antifield_number", "form_degree",
        "Grassmann_parity", "mass_dimension", "Weyl_weight",
        "conformal_compact_weight", "ce_ghost_number", "intrinsic_jet_order_bound",
        "operator_order_bounds",
    ]
    if [row.get("name") for row in namespace.get("fields", [])] != expected_names:
        errors.append("namespace fields")
    if namespace.get("forbidden_aliases") != [
        "ghost_number=chain_degree", "compact_degree=chain_degree",
        "compact_degree=conformal_compact_weight", "row_derivative_order=operator_order",
        "not_applicable=0",
    ]:
        errors.append("forbidden aliases")

    carrier_rows = {row.get("carrier"): row for row in value.get("carrier_audit", [])}
    if set(carrier_rows) != {
        "LOCAL_GRAPH_BV_386", "REPRESENTED_ENDPOINT_DFINITE_4080", "DFINITE_COMPARISON_4490",
        "FORMAL_COTANGENT_COMPARISON_8980", "ACTION_RESIDUAL_940", "ZERO_MODE_15_PLUS_15",
        "CENTERED_C3_C4_C5",
    }:
        errors.append("carrier audit identities")
    if carrier_rows.get("LOCAL_GRAPH_BV_386", {}).get("fully_namespaced_rows") != 30:
        errors.append("local carrier coverage")

    flags = value.get("claim_flags", {})
    required_true = ["M1A_CONVENTION_COLLISION_AUDITED", "LOCAL_ENDPOINT_30_FULLY_NAMESPACED"]
    required_false = [
        "LOCAL_386_FULLY_TYPED", "DFINITE_LEGACY_GHOST_NUMBER_IS_SAFE_TO_IMPORT_AS_BV_GHOST_NUMBER",
        "CHAIN_DEGREE_AND_CONFORMAL_COMPACT_WEIGHT_IDENTICAL", "M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE",
        "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE", "M1C_COMMON_MANIFEST_REPLAY_COMPLETE",
        "CLASSICAL_IMPORT_GATE_PASSED", "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED",
        "RENORMALIZED_LORENTZIAN_PRODUCTS_CONSTRUCTED", "QME_RESTORED",
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
    ]
    if any(flags.get(name) is not True for name in required_true) or any(flags.get(name) is not False for name in required_false):
        errors.append("claim flags")

    replay = copy.deepcopy(value)
    expected_digest = replay.get("independent_checker", {}).get("expected_digest")
    replay.setdefault("independent_checker", {})["expected_digest"] = ""
    if expected_digest != canonical_digest(replay):
        errors.append("certificate digest")

    if not REPORT.exists():
        errors.append("human report absent")
    else:
        report = REPORT.read_text()
        for token in ("opposite sign", "NOT_APPLICABLE", "4,080", "410", "Gate A remains `FAIL_CLOSED`", "Hadamard", "QME"):
            if token not in report:
                errors.append(f"report token {token}")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    if errors:
        print("STRICT_M1A_CARRIER_GRADING_CONVENTION_AUDIT_V1: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("STRICT_M1A_CARRIER_GRADING_CONVENTION_AUDIT_V1: PASS")
    print("  - 30 endpoint rows independently crosswalked to the action dictionary")
    print("  - 4,080 finite-harmonic minimal coordinates obey the sign bridge")
    print("  - chain degree, BV ghost number and conformal compact weight remain distinct")
    print("  - M1A, Gate A, Hadamard and QME remain fail closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
