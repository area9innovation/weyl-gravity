#!/usr/bin/env python3
"""Independent exact checker for the strict local q1/q2 identity."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

import cylinder_polarized_bach_evaluator as point
from local_q1_bach_flat import digest
from local_q1_q2_receiver import channel_id, enumerate_channels, fixture_record, mutation_record


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_LOCAL_Q1_Q2_IDENTITY_V1.json"
Q1 = HERE / "certificates/STRICT_PORTABLE_LOCAL_Q1_AST_V1.json"
Q2 = HERE / "certificates/STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1.json"
SOURCE = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json"
TRUE_FLAGS = {
    "Q1_Q2_CHANNEL_INVENTORY_EXHAUSTIVE",
    "Q1_Q2_ARITY_TWO_NILPOTENCY_REPLAYED",
    "Q1_Q2_RECEIVER_MUTATION_SENSITIVE",
}
FALSE_FLAGS = {
    "STRICT_FULL_LOCAL_D_ACTION_CERTIFIED",
    "D_Q1_COMMUTATOR_REPLAYED",
    "D_Q2_DERIVATION_REPLAYED",
    "BV_CYCLICITY_Q2_REPLAYED",
    "STRICT_SUPPORT_LOCAL_Q2_COMPLETE",
    "CLASSICAL_IMPORT_GATE_PASSED",
    "LORENTZIAN_CAUSAL_CERTIFIED",
    "QME_RESTORED",
}


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(value: dict[str, Any], *, replay_exact: bool = True) -> list[str]:
    errors: list[str] = []
    if value.get("result_state") != "Q1_Q2_ARITY_TWO_IDENTITY_CERTIFIED_D_AND_PAIRING_OPEN":
        errors.append("result state drift")
    if value.get("lifecycle") != "CLASSIFIED" or value.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]:
        errors.append("lifecycle or dependency boundary drift")
    if value.get("convention") != "suspended-graded-symmetric-factorial-v1":
        errors.append("suspension convention drift")
    scope = value.get("scope", {})
    if "Bach-flat" not in scope.get("background_class", "") or scope.get("locality") != "SUPPORT_LOCAL_POLYDIFFERENTIAL":
        errors.append("background or locality scope drift")
    if "(-1)^|x|" not in scope.get("identity", "") or scope.get("maximum_metric_fixture_jet_order") != 5:
        errors.append("arity-two sign or jet-order convention drift")

    q1 = json.loads(Q1.read_text())
    q2 = json.loads(Q2.read_text())
    source = json.loads(SOURCE.read_text())
    q1_components = q1["local_q1_ast"]["components"]
    ordered_q2 = q2["ordered_components"]
    primary = q2["primary_components"]
    parities = {item["symbol"]: item["Grassmann_parity"] for item in q2["generator_ledger"]}
    channels = enumerate_channels(q1_components, ordered_q2, parities)
    inventory = value.get("channel_inventory", {})
    if inventory.get("channels") != channels:
        errors.append("independently reconstructed channel inventory drift")
    if inventory.get("channel_count") != 18 or inventory.get("composable_path_count") != 51:
        errors.append("channel or path count drift")
    if inventory.get("q1_component_count") != 5 or inventory.get("ordered_q2_component_count") != 22:
        errors.append("q1/q2 component count drift")
    used_q1 = {path["q1_component_id"] for item in channels for path in item["paths"]}
    used_q2 = {path["q2_component_id"] for item in channels for path in item["paths"]}
    if used_q1 != {item["component_id"] for item in q1_components} or used_q2 != {item["component_id"] for item in ordered_q2}:
        errors.append("not every q1/q2 component participates")

    expected_counts = {"h": 4, "h_star": 4, "c_star": 5, "omega_star": 5}
    families = value.get("natural_identity_families", [])
    if dict(Counter(item["output"] for item in channels)) != expected_counts:
        errors.append("internal output-family count failure")
    if {item.get("output"): item.get("channel_count") for item in families} != expected_counts:
        errors.append("natural identity family ledger drift")
    for family in families:
        expected_ids = [channel_id(item) for item in channels if item["output"] == family.get("output")]
        if family.get("channel_ids") != expected_ids:
            errors.append(f"{family.get('output')}: family channel crosswalk drift")

    source_checks = {item["check_id"]: item["status"] for item in source.get("producer_checks", [])}
    if source_checks.get("Q_squared_zero") != "VERIFIED":
        errors.append("authoritative source Q square-zero proof unavailable")
    proof = value.get("proof_basis", {})
    if proof.get("status") != "CERTIFIED" or proof.get("legacy_matrix_cartan_helper_used") is not False:
        errors.append("proof status or local-receiver boundary drift")
    if len(proof.get("argument", [])) != 4 or "not used" in proof.get("reason", ""):
        errors.append("proof argument or receiver reason drift")

    exact = value.get("exact_receiver", {})
    records = exact.get("fixture_records", [])
    expected_backgrounds = ["conformal_cylinder", "minkowski", "flat_brinkmann"]
    if [item.get("background") for item in records] != expected_backgrounds:
        errors.append("fixture background inventory drift")
    expected_ids = [channel_id(item) for item in channels]
    for record in records:
        if record.get("channel_count") != 18 or record.get("path_count") != 51 or record.get("all_channels_zero") is not True:
            errors.append(f"{record.get('background')}: fixture summary drift")
            continue
        rows = record.get("rows", [])
        if [item.get("channel_id") for item in rows] != expected_ids or any(item.get("defect_zero") is not True for item in rows):
            errors.append(f"{record.get('background')}: fixture rows drift")
    if replay_exact and not errors:
        q1_by_id = {item["component_id"]: item for item in q1_components}
        q2_by_id = {item["component_id"]: item for item in ordered_q2}
        primary_by_id = {item["primary_id"]: item for item in primary}
        replay = fixture_record(
            channels,
            q1_by_id,
            q2_by_id,
            primary_by_id,
            "conformal_cylinder",
            point.cylinder_background(5),
            left_seed=11,
            right_seed=23,
        )
        if not records or records[0] != replay:
            errors.append("routine exact cylinder receiver replay drift")
        by_id = {channel_id(item): item for item in channels}
        targets = (
            "q1q2__h__c__c",
            "q1q2__h_star__c__h",
            "q1q2__c_star__h__h",
            "q1q2__omega_star__h__h",
        )
        mutations = [
            mutation_record(
                by_id[target],
                q1_by_id,
                q2_by_id,
                primary_by_id,
                point.cylinder_background(5),
                path_index=0,
                left_seed=37,
                right_seed=41,
            )
            for target in targets
        ]
        if exact.get("mutation_records") != mutations:
            errors.append("representative mutation sensitivity replay drift")

    checks = {item.get("check_id"): item.get("status") for item in value.get("proof_checks", [])}
    if checks != {
        "q1_q2_channel_exhaustion": "VERIFIED",
        "q1_q2_arity_two_nilpotency": "VERIFIED",
        "receiver_mutation_sensitivity": "VERIFIED",
        "D_q1_commutator_zero": "NOT_REPLAYED",
        "D_q2_derivation": "NOT_REPLAYED",
        "BV_cyclicity_q2": "NOT_REPLAYED",
    }:
        errors.append("proof-check ledger drift or downstream promotion")
    flags = value.get("claim_flags", {})
    if any(flags.get(flag) is not True for flag in TRUE_FLAGS) or any(flags.get(flag) is not False for flag in FALSE_FLAGS):
        errors.append("claim flags drift or premature promotion")
    if len(value.get("does_not_establish", [])) < 6:
        errors.append("does-not-establish ledger shortened")

    expected_hashes = {
        "channel_inventory_sha256": digest(inventory),
        "natural_identity_families_sha256": digest(families),
        "proof_basis_sha256": digest(proof),
        "exact_receiver_sha256": digest(exact),
        "proof_checks_sha256": digest(value.get("proof_checks")),
    }
    if value.get("canonical_hashes") != expected_hashes:
        errors.append("canonical hashes do not reproduce")
    for group in value.get("provenance", {}).values():
        if not isinstance(group, list):
            errors.append("provenance group is not a list")
            continue
        for item in group:
            path = ROOT / item.get("path", "")
            if not path.is_file() or file_sha(path) != item.get("sha256"):
                errors.append(f"provenance drift: {item.get('path')}")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("STRICT_LOCAL_Q1_Q2_IDENTITY_V1: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print(f"  - {error}")
    else:
        print("  - 18 channels / 51 paths reconstructed; exact cylinder and four sign mutations replayed")
        print("  - D, pairing, Gate A, Lorentzian causal, and QME claims remain false")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
