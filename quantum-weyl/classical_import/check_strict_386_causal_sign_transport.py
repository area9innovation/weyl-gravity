#!/usr/bin/env python3
"""Independent structural checker for strict 386-row causal sign transport."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_CAUSAL_SIGN_TRANSPORT_V1.json"
GATE = HERE / "certificates/CLASSICAL_IMPORT_GATE_V5_RECONCILIATION.json"
CYCLIC = HERE / "certificates/STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.json"
CAUSAL = ROOT / "covariant_completion/certificates/curved_full_prolonged_green_homotopy_assembly.json"
RETRACT = ROOT / "covariant_completion/certificates/curved_deformation_retract_status.json"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def reduce_conjugated_word(word: tuple[str, ...]) -> tuple[str, ...]:
    """Cancel adjacent involutions in a free word; independent of the builder."""

    stack: list[str] = []
    for symbol in word:
        if symbol == "T" and stack and stack[-1] == "T":
            stack.pop()
        else:
            stack.append(symbol)
    return tuple(stack)


def expected_blocks() -> list[dict[str, Any]]:
    return [
        {"cochain_block": "G", "role": "Diff plus Weyl ghosts", "gate_generators": ["c", "omega"], "dimension": 5, "transport_sign": 1},
        {"cochain_block": "M", "role": "metric field", "gate_generators": ["h"], "dimension": 10, "transport_sign": 1},
        {"cochain_block": "E", "role": "metric antifield", "gate_generators": ["h_star"], "dimension": 10, "transport_sign": 1},
        {"cochain_block": "I", "role": "Diff plus Weyl ghost antifields", "gate_generators": ["c_star", "omega_star"], "dimension": 5, "transport_sign": -1},
    ]


def check(value: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    gate = json.loads(GATE.read_text())
    cyclic = json.loads(CYCLIC.read_text())
    causal = json.loads(CAUSAL.read_text())
    retract = json.loads(RETRACT.read_text())

    if value.get("result_state") != "STRICT_386_CAUSAL_ARCHITECTURE_STABLE_UNDER_MINIMAL_SIGN_TRANSPORT_COMMON_HASH_OPEN":
        errors.append("result state drift")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]:
        errors.append("dependency boundary drift")

    bridge = value.get("carrier_bridge", {})
    blocks = expected_blocks()
    if bridge.get("endpoint_blocks") != blocks:
        errors.append("endpoint block bridge drift")
    if [row["dimension"] for row in blocks] != causal["endpoint_channel_assembly"]["full_endpoint_ranks"]:
        errors.append("endpoint ranks do not match causal authority")
    # The entry ledger is ordered in both directions. Count unique left basis
    # labels instead of trusting the producer's dimension statement.
    labels = {row["left"] for row in cyclic["canonical_pairing"]["entries"]}
    gate_group_dimensions = {
        "G": len({label for label in labels if (label.startswith("c_") and not label.startswith("c_star_")) or label == "omega"}),
        "M": len({label for label in labels if label.startswith("h_") and not label.startswith("h_star_")}),
        "E": len({label for label in labels if label.startswith("h_star_")}),
        "I": len({label for label in labels if label.startswith("c_star_") or label == "omega_star"}),
    }
    if gate_group_dimensions != {"G": 5, "M": 10, "E": 10, "I": 5}:
        errors.append("Gate minimal basis does not reconstruct 5/10/10/5")

    signs = [1] * 356 + [
        row["transport_sign"] for row in blocks for _ in range(row["dimension"])
    ]
    transport = value.get("transport", {})
    if (
        len(signs) != 386
        or any(sign * sign != 1 for sign in signs)
        or transport.get("positive_eigenvalue_multiplicity") != 381
        or transport.get("negative_eigenvalue_multiplicity") != 5
        or transport.get("rank") != 386
        or transport.get("determinant") != -1
        or transport.get("involutive") is not True
    ):
        errors.append("full signed involution arithmetic drift")
    if transport.get("q1_rows_changed") != ["q1_cstar_hstar", "q1_omegastar_hstar"]:
        errors.append("q1 sign support drift")
    if transport.get("q2_rows_changed_but_not_causally_transferred") != [
        "q2_cstar_hhstar__forward",
        "q2_cstar_hhstar__reverse",
        "q2_omegastar_hhstar__forward",
        "q2_omegastar_hhstar__reverse",
    ]:
        errors.append("q2 sign support drift")

    # Free-word rail for the two conjugation identities. This reconstructs the
    # cancellations rather than importing prose or the producer's proof rows.
    q_squared = reduce_conjugated_word(("T", "Q", "T", "T", "Q", "T"))
    q_lambda = reduce_conjugated_word(("T", "Q", "T", "T", "L", "T"))
    lambda_q = reduce_conjugated_word(("T", "L", "T", "T", "Q", "T"))
    if q_squared != ("T", "Q", "Q", "T"):
        errors.append("nilpotency conjugation word failed")
    if q_lambda != ("T", "Q", "L", "T") or lambda_q != ("T", "L", "Q", "T"):
        errors.append("Green identity conjugation words failed")
    if reduce_conjugated_word(("T", "T")):
        errors.append("involution word did not reduce to identity")

    if causal.get("causal_green_homotopy") is not True:
        errors.append("causal source authority drift")
    if causal.get("dimension_ledger", {}).get("identity") != "386=356+30":
        errors.append("causal source dimension drift")
    if retract.get("factorized_actual_curved_Q", {}).get("exact_inputs", {}).get("cotangent_lift_full_66_row_pairing_defect") != 0:
        errors.append("curved pairing control drift")
    if gate.get("gate_disposition", {}).get("accepted_common_snapshot_hashes") != 0:
        errors.append("common hash boundary promoted")

    checks = {row.get("check_id"): row.get("status") for row in value.get("proof_ledger", [])}
    if checks != {
        "endpoint_type_dimension_bridge": "VERIFIED",
        "full_transport_involution": "VERIFIED",
        "transported_unary_nilpotency": "VERIFIED_BY_EXACT_CONJUGATION",
        "transported_green_homotopy": "VERIFIED_BY_EXACT_CONJUGATION",
        "causal_support_and_orientation": "VERIFIED",
        "transported_adjoint_relation": "VERIFIED_ON_TRANSPORTED_PAIRING",
        "common_byte_identification": "NOT_ESTABLISHED",
        "nonlinear_causal_compatibility": "NOT_ESTABLISHED",
    }:
        errors.append("proof ledger drift")

    strength = value.get("foundational_strength", {})
    if (
        strength.get("fixed_carrier_transport_base") != "PRA"
        or strength.get("choice_operation_added_by_transport") is not False
        or strength.get("infinite_selection_added_by_transport") is not False
        or strength.get("weakest_base_for_imported_causal_theorem") != "NOT_ESTABLISHED"
    ):
        errors.append("foundational-strength boundary drift")

    flags = value.get("claim_flags", {})
    true_flags = {
        "STRICT_386_SIGN_TRANSPORT_INVOLUTIVE",
        "STRICT_386_UNARY_NILPOTENCY_PRESERVED",
        "STRICT_386_CAUSAL_GREEN_HOMOTOPY_PRESERVED",
        "STRICT_386_CAUSAL_SUPPORT_PRESERVED",
        "STRICT_386_GRADED_ADJOINT_PRESERVED_ON_TRANSPORTED_PAIRING",
    }
    false_flags = {
        "STRICT_386_ARCHITECTURE_INVALIDATED_BY_GATE_V5",
        "GATE_V5_TO_386_COMMON_BYTES_IDENTIFIED",
        "FULL_386_CANONICAL_PAIRING_SERIALIZED",
        "STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED",
        "CLASSICAL_IMPORT_GATE_PASSED",
        "BRST_HADAMARD_STATE_CONSTRUCTED",
        "LORENTZIAN_QME_RESTORED",
    }
    if any(flags.get(flag) is not True for flag in true_flags) or any(flags.get(flag) is not False for flag in false_flags):
        errors.append("claim flags drift or downstream promotion")

    hashes = value.get("canonical_hashes", {})
    expected_hashes = {
        "carrier_bridge_sha256": digest(bridge),
        "transport_sha256": digest(transport),
        "proof_ledger_sha256": digest(value.get("proof_ledger")),
        "foundational_strength_sha256": digest(strength),
        "architecture_disposition_sha256": digest(value.get("architecture_disposition")),
    }
    if hashes != expected_hashes:
        errors.append("canonical hashes do not reproduce")
    for item in value.get("provenance", {}).get("inputs", []):
        path = ROOT / item.get("path", "")
        if not path.is_file() or file_hash(path) != item.get("sha256"):
            errors.append(f"provenance drift: {item.get('path')}")
    if len(value.get("does_not_establish", [])) != 7:
        errors.append("claim boundary ledger drift")
    report = (HERE / "REPORT_STRICT_386_CAUSAL_SIGN_TRANSPORT_V1.md")
    if not report.is_file() or "not yet the missing import bridge" not in report.read_text():
        errors.append("human report firewall missing")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("STRICT_386_CAUSAL_SIGN_TRANSPORT_V1: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print(f"  - {error}")
    else:
        print("  - endpoint type bridge: 30=5+10+10+5")
        print("  - T_386: 381 positive, 5 negative; unary causal identities transported")
        print("  - common bytes, full pairing, q2/D, Gate A, Hadamard and QME remain open")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
