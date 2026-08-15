#!/usr/bin/env python3
"""Independent checker for the exhaustive minimal-BV arity-three identity."""

from __future__ import annotations

from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import cylinder_polarized_bach_evaluator as point
import local_q1_q2_q3_receiver as receiver


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1.json"
Q1 = HERE / "certificates/STRICT_PORTABLE_LOCAL_Q1_AST_V1.json"
Q2 = HERE / "certificates/STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1.json"
CLASSICAL_Q3 = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_Q3_EXPORT_V1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any], *, replay: bool = True) -> list[str]:
    errors: list[str] = []
    q1_value = json.loads(Q1.read_text())
    q2_value = json.loads(Q2.read_text())
    classical_q3 = json.loads(CLASSICAL_Q3.read_text())
    q1_components = q1_value["local_q1_ast"]["components"]
    q2_components = q2_value["ordered_components"]
    primary_components = q2_value["primary_components"]
    parities = {item["symbol"]: item["Grassmann_parity"] for item in q2_value["generator_ledger"]}
    q3_ast = classical_q3["natural_operator_ast"]

    if value.get("result_id") != "STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1" or value.get("result_kind") != "EXHAUSTIVE_NATURAL_AND_EXACT_LOCAL_MINIMAL_BV_ARITY_THREE_IDENTITY":
        errors.append("result identity or kind drift")
    if value.get("result_state") != "MINIMAL_ARITY_THREE_IDENTITY_CERTIFIED_Q3_CYCLICITY_AND_386_STABILIZATION_OPEN" or value.get("lifecycle") != "CLASSIFIED":
        errors.append("result state or lifecycle drift")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]:
        errors.append("dependency tag promotion")
    scope = value.get("scope", {})
    if "q1 q3" not in scope.get("identity", "") or scope.get("locality") != "SUPPORT_LOCAL_POLYDIFFERENTIAL" or scope.get("maximum_metric_fixture_jet_order") != 5:
        errors.append("identity, locality or jet-order scope drift")

    expected_channels = receiver.enumerate_channels(q1_components, q2_components, parities)
    inventory = value.get("channel_inventory", {})
    counts = Counter(path["kind"] for channel in expected_channels for path in channel["paths"])
    if inventory.get("channels") != expected_channels:
        errors.append("typed arity-three channel serialization drift")
    if inventory.get("channel_count") != 72 or inventory.get("composable_path_count") != 212 or inventory.get("path_kind_counts") != dict(sorted(counts.items())):
        errors.append("72-channel/212-path census drift")
    if inventory.get("output_channel_counts") != {"c": 1, "c_star": 22, "h": 12, "h_star": 18, "omega": 3, "omega_star": 16}:
        errors.append("output-channel partition drift")
    if inventory.get("type_compatible_q1_component_count") != 4 or inventory.get("all_type_compatible_q1_components_used") is not True or inventory.get("all_ordered_q2_components_used_as_inner_or_outer") is not True or inventory.get("q3_used_in_all_type_compatible_positions") is not True:
        errors.append("operator coverage drift")

    families = value.get("natural_identity_families", [])
    if [item.get("channels") for item in families] != [64, 3, 3, 1, 1] or sum(item.get("channels", 0) for item in families) != 72:
        errors.append("natural identity family partition drift")
    proof = value.get("proof_basis", {})
    argument = proof.get("argument", [])
    if proof.get("status") != "CERTIFIED" or len(argument) != 6 or "third derivative" not in argument[2] or "not substituted" not in proof.get("independent_receiver_role", ""):
        errors.append("arbitrary-input proof basis or receiver boundary drift")

    exact = value.get("exact_receiver", {})
    if exact.get("background") != "minkowski" or exact.get("seeds") != [1, 2, 3] or exact.get("all_72_channel_defects_zero") is not True:
        errors.append("exact receiver fixture declaration drift")
    mutations = exact.get("mutation_checks", [])
    if [(item.get("channel_id"), item.get("mutated_path_kind"), item.get("detected")) for item in mutations] != [
        ("q1q2q3__omega_star__h__h__h", "q1_q3", True),
        ("q1q2q3__h_star__c__h__h", "q3_q1", True),
        ("q1q2q3__c__c__c__c", "q2_q2", True),
    ] or exact.get("all_mutations_detected") is not True:
        errors.append("mutation-sensitivity ledger drift")

    if replay and not errors:
        q1_by_id = {item["component_id"]: item for item in q1_components}
        q2_by_id = {item["component_id"]: item for item in q2_components}
        primary_by_id = {item["primary_id"]: item for item in primary_components}
        background = point.flat_background(5)
        fixture = receiver.fixture_record(
            expected_channels, q1_by_id, q2_by_id, primary_by_id, q3_ast,
            "minkowski", background, seeds=(1, 2, 3),
        )
        if not fixture["all_channel_defects_zero"] or fixture["channels"] != exact.get("channel_results") or digest(fixture) != exact.get("fixture_sha256"):
            errors.append("independent exact 72-channel replay drift")
        else:
            specs = (
                ("omega_star", ["h", "h", "h"], "q1_q3"),
                ("h_star", ["c", "h", "h"], "q3_q1"),
                ("c", ["c", "c", "c"], "q2_q2"),
            )
            for stored, (output, inputs, kind) in zip(mutations, specs):
                channel = copy.deepcopy(next(item for item in expected_channels if item["output"] == output and item["inputs"] == inputs))
                next(item for item in channel["paths"] if item["kind"] == kind)["multiplier"] += 1
                defect = receiver.evaluate_channel(channel, q1_by_id, q2_by_id, primary_by_id, q3_ast, background, seeds=(1, 2, 3))
                serialized = receiver.lower.serialize_field(output, defect)
                if serialized != stored.get("nonzero_defect") or all(item == "0" for item in serialized):
                    errors.append(f"{kind} mutation replay drift")

    gates = {item.get("gate"): item.get("status") for item in value.get("gate_advancement", [])}
    if gates != {
        "AUTHORITATIVE_MINIMAL_Q3_IMPORT": "PASS",
        "MINIMAL_ARITY_THREE_Q_SQUARED": "PASS",
        "MINIMAL_Q3_CYCLICITY": "OPEN",
        "STRICT_386_CYCLIC_STABILIZATION": "OPEN",
        "GENERAL_LAMBDA2_SOURCE_CLOSURE_ON_386": "OPEN",
    }:
        errors.append("gate advancement drift or premature promotion")
    flags = value.get("claim_flags", {})
    true_flags = ("AUTHORITATIVE_MINIMAL_BV_Q3_IMPORTED", "MINIMAL_BV_ARITY_THREE_IDENTITY_CERTIFIED", "ALL_72_TYPED_CHANNELS_EXHAUSTED", "ALL_212_COMPOSABLE_PATHS_REPLAYED", "Q3_SIGN_MUTATIONS_DETECTED")
    false_flags = ("MINIMAL_BV_Q3_CYCLICITY_CERTIFIED", "STRICT_386_Q3_STABILIZED", "STRICT_386_GENERAL_LAMBDA2_SOURCE_CLOSURE_CERTIFIED", "CLASSICAL_IMPORT_GATE_PASSED", "LORENTZIAN_CAUSAL_CERTIFIED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED")
    if any(flags.get(name) is not True for name in true_flags) or any(flags.get(name) is not False for name in false_flags):
        errors.append("claim flags drift or premature promotion")
    foundations = value.get("foundational_strength", {})
    if foundations.get("dependency_boundary") != "LOCAL-ALGEBRAIC" or foundations.get("choice_operation_added") is not False or foundations.get("Hilbert_completion_used") is not False or foundations.get("Green_operator_used") is not False:
        errors.append("foundational-strength boundary drift")
    expected_hashes = {
        "channel_inventory_sha256": digest(inventory),
        "natural_identity_families_sha256": digest(families),
        "proof_basis_sha256": digest(proof),
        "exact_receiver_sha256": digest(exact),
        "gate_advancement_sha256": digest(value.get("gate_advancement")),
        "foundational_strength_sha256": digest(foundations),
    }
    if value.get("canonical_hashes") != expected_hashes:
        errors.append("canonical hashes do not reproduce")
    provenance = value.get("provenance", {})
    for item in provenance.get("inputs", []):
        path = ROOT / item.get("path", "")
        if not path.is_file() or item.get("sha256") != sha(path):
            errors.append(f"input provenance drift: {item.get('path')}")
    implementation = provenance.get("implementation", {})
    path = ROOT / implementation.get("path", "")
    if not path.is_file() or implementation.get("sha256") != sha(path):
        errors.append("receiver implementation provenance drift")
    if len(value.get("does_not_establish", [])) < 6:
        errors.append("does-not-establish ledger shortened")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1_CHECK: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print(f"  - {error}")
    else:
        print("  - all 72 typed channels and 212 paths independently replayed")
        print("  - cyclicity and 386-row stabilization remain fail closed")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
