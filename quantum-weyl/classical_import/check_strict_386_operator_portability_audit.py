#!/usr/bin/env python3
"""Independent boundary checker for the strict 386 operator portability audit."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_OPERATOR_PORTABILITY_AUDIT_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
ENDPOINT = HERE / "certificates/STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1.json"
GENERALIZED = ROOT / "covariant_completion/certificates/generalized_auxiliary_contraction.json"
MAPPING_KERNEL = ROOT / "covariant_completion/certificates/curved_curvature_mapping_cylinder_kernel.json"
MAPPING = ROOT / "covariant_completion/certificates/curved_curvature_mapping_cylinder_substitution.json"
HYBRID = ROOT / "covariant_completion/certificates/curved_prolonged_hybrid_algebraic_projector.json"
TRANSFER = ROOT / "covariant_completion/certificates/adjoint_tractor_green_transfer.json"
PBW = ROOT / "covariant_completion/certificates/adjoint_tractor_bgg_curved_pbw.json"
FULL_GREEN = ROOT / "covariant_completion/certificates/curved_full_prolonged_green_homotopy_assembly.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = json.loads(RESULT.read_text()) if value is None else value
    source = {path: json.loads(path.read_text()) for path in (PAIRING, ENDPOINT, GENERALIZED, MAPPING_KERNEL, MAPPING, HYBRID, TRANSFER, PBW, FULL_GREEN)}
    errors: list[str] = []
    if value.get("result_id") != "STRICT_386_OPERATOR_PORTABILITY_AUDIT_V1" or value.get("lifecycle") != "CLASSIFIED":
        errors.append("identity/lifecycle")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]:
        errors.append("dependency tags")

    contracts = value.get("portability_contracts", [])
    contract_ids = [item.get("id") for item in contracts]
    if contract_ids != ["FINITE_COMPONENT_JET_TABLE", "FINITE_SPARSE_COMPONENT_MAP", "ANALYTIC_GREEN_ACTION"]:
        errors.append("typed portability contracts")
    if any(len(item.get("required_fields", [])) < 4 or not item.get("independent_replay") for item in contracts):
        errors.append("portability contract completeness")
    green_contract = contracts[2] if len(contracts) == 3 else {}
    if "finite jet table cannot encode" not in green_contract.get("independent_replay", ""):
        errors.append("local/nonlocal type firewall")

    inventory = value.get("operator_inventory", [])
    expected_ids = ["ENDPOINT_Q1_30", "FULL_Q1_386", "H_ALG_AND_PROJECTORS_386", "ENDPOINT_INCLUSION_PROJECTION_386_30", "ENDPOINT_GREEN_PLUS_MINUS_30", "FULL_GREEN_PLUS_MINUS_386"]
    if [item.get("id") for item in inventory] != expected_ids:
        errors.append("operator inventory order")
    by_id = {item.get("id"): item for item in inventory}
    expected_status = {
        "ENDPOINT_Q1_30": "PORTABLE_COMPONENT_BYTES",
        "FULL_Q1_386": "PRODUCER_COEFFICIENTWISE_COMPLETE_RECEIVER_TABLE_ABSENT",
        "H_ALG_AND_PROJECTORS_386": "EXACT_EXECUTABLE_AND_HASHED_RECEIVER_TABLE_ABSENT",
        "ENDPOINT_INCLUSION_PROJECTION_386_30": "EXACT_EXECUTABLE_AND_HASHED_RECEIVER_TABLE_ABSENT",
        "ENDPOINT_GREEN_PLUS_MINUS_30": "THEOREM_CHARACTERIZED_PORTABLE_ACTION_ABSENT",
        "FULL_GREEN_PLUS_MINUS_386": "THEOREM_CHARACTERIZED_PORTABLE_ACTION_ABSENT",
    }
    if {key: by_id.get(key, {}).get("status") for key in expected_ids} != expected_status:
        errors.append("operator status classification")
    counts = Counter(expected_status.values())
    if value.get("status_counts") != dict(sorted(counts.items())):
        errors.append("status counts")

    pairing, endpoint, generalized, kernel, mapping, hybrid, transfer, pbw, full_green = (source[path] for path in (PAIRING, ENDPOINT, GENERALIZED, MAPPING_KERNEL, MAPPING, HYBRID, TRANSFER, PBW, FULL_GREEN))
    carrier = value.get("carrier", {})
    if carrier.get("rows") != 386 or carrier.get("split") != "386=30+36+320" or carrier.get("basis_digest") != pairing["canonical_hashes"]["component_basis_sha256"]:
        errors.append("carrier projection")
    endpoint_present = by_id.get("ENDPOINT_Q1_30", {}).get("present", {})
    if endpoint_present != {"arrow_tables": 80, "common_nonzero_coefficients": 619, "Bach_columns_checked": 700}:
        errors.append("endpoint q1 projection")
    full_q = by_id.get("FULL_Q1_386", {}).get("present", {})
    table_counts = {key: item["coefficient_multiindices"] for key, item in mapping["coefficient_tables"].items()}
    if full_q.get("attachment_table_multiindices") != table_counts or table_counts != {"T_state": 35, "A_equation": 15, "B_identity": 1}:
        errors.append("full q1 producer projection")
    if full_q.get("prolonged_Q_digest") != kernel["matrix_sha256"]["prolonged_Q"] or full_q.get("auxiliary_original_differential_digest") != generalized["matrix_sha256"]["original_differential"]:
        errors.append("full q1 hash projection")
    local_sdr = by_id.get("H_ALG_AND_PROJECTORS_386", {}).get("present", {})
    if local_sdr.get("auxiliary_H_alg_digest") != hybrid["component_projectors"]["auxiliary"]["sha256"]["H_alg"] or local_sdr.get("mapping_homotopy_digest") != kernel["matrix_sha256"]["homotopy"]:
        errors.append("local SDR projection")
    maps = by_id.get("ENDPOINT_INCLUSION_PROJECTION_386_30", {}).get("present", {})
    for name in ("inclusion", "projection"):
        if maps.get(f"auxiliary_{name}_digest") != generalized["matrix_sha256"][name] or maps.get(f"mapping_{name}_digest") != kernel["matrix_sha256"][name]:
            errors.append("endpoint map projection " + name)
    endpoint_green = by_id.get("ENDPOINT_GREEN_PLUS_MINUS_30", {}).get("present", {})
    if endpoint_green.get("tracefree_causal_green_homotopy") is not transfer["tracefree_causal_green_homotopy"] or endpoint_green.get("parent_green_homotopy_transferred_in_PBW_file") is not pbw["theorem_boundary"]["parent_green_homotopy_transferred"]:
        errors.append("endpoint Green theorem boundary")
    full = by_id.get("FULL_GREEN_PLUS_MINUS_386", {}).get("present", {})
    if full.get("causal_green_homotopy_theorem") is not full_green["causal_green_homotopy"] or full.get("assembly_formula") != full_green["full_hybrid_assembly"]["formula"]:
        errors.append("full Green theorem projection")

    routes = value.get("route_split", [])
    if [item.get("rank") for item in routes] != [1, 2, 3, 4] or [item.get("kind") for item in routes] != ["FINITE_COMPONENT_JET_TABLE", "FINITE_SPARSE_COMPONENT_MAP", "ANALYTIC_GREEN_ACTION", "ANALYTIC_GREEN_ACTION"]:
        errors.append("route split")
    strength = value.get("foundational_strength", {})
    if strength.get("finite_local_serialization_upper_bound") != "PRA" or strength.get("weakest_base_for_analytic_green_action") != "NOT_ESTABLISHED" or strength.get("physics_implies_choice_principle") is not False:
        errors.append("foundational boundary")
    flags = value.get("claim_flags", {})
    for key in ("STRICT_386_OPERATOR_PORTABILITY_TYPES_CLASSIFIED", "STRICT_ENDPOINT_Q1_PORTABLE_COMPONENT_BYTES", "STRICT_CAUSAL_GREEN_HOMOTOPY_THEOREM_PRESERVED"):
        if flags.get(key) is not True:
            errors.append("missing positive flag " + key)
    for key in ("STRICT_FULL_386_Q1_PORTABLE_COMPONENT_BYTES", "STRICT_FULL_386_LOCAL_SDR_PORTABLE_COMPONENT_BYTES", "STRICT_ENDPOINT_GREEN_PORTABLE_ACTION_SERIALIZED", "STRICT_FULL_GREEN_PORTABLE_ACTION_SERIALIZED", "STRICT_386_ALL_OPERATOR_COMPONENT_ADJOINTS_REPLAYED", "STRICT_386_LOCAL_D_CERTIFIED", "STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED", "CLASSICAL_IMPORT_GATE_PASSED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED", "LORENTZIAN_QUANTUM_THEORY"):
        if flags.get(key) is not False:
            errors.append("claim promotion " + key)

    projection_keys = ("carrier", "portability_contracts", "operator_inventory", "status_counts", "route_split", "foundational_strength", "claim_flags", "does_not_establish", "next_gate")
    if digest({key: value[key] for key in projection_keys}) != value.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    for item in value.get("provenance", {}).get("inputs", []):
        path = ROOT / item.get("path", "")
        if not path.is_file() or sha(path) != item.get("sha256"):
            errors.append("provenance " + item.get("path", ""))
    return errors


def main() -> int:
    errors = check()
    print("STRICT_386_OPERATOR_PORTABILITY_AUDIT_V1: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print("  - " + error)
    else:
        print("  - six operator families classified under three nonconflated contracts")
        print("  - endpoint q1 portable; full local operators executable but not serialized")
        print("  - causal theorem preserved; endpoint/full Green action portability open")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
