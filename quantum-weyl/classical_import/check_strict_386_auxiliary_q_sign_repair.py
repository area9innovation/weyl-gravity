#!/usr/bin/env python3
"""Independent receiver for the strict auxiliary-q sign repair."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_AUXILIARY_Q_SIGN_REPAIR_V1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def zero() -> list[list[Fraction]]:
    return [[Fraction() for _ in range(36)] for _ in range(36)]


def mul(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[sum((left[row][middle] * right[middle][column] for middle in range(36)), Fraction()) for column in range(36)] for row in range(36)]


def replay() -> tuple[int, int, int, int]:
    pairing = json.loads((HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json").read_text())
    witness = json.loads((HERE / "certificates/STRICT_386_AUXILIARY_Q_SIGN_WITNESS_V1.json").read_text())
    q_plus, omega = zero(), zero()
    for target, source, coefficient in witness["entries"]:
        q_plus[target][source] = Fraction(coefficient)
    q_minus = [row[:] for row in q_plus]
    for index in range(4):
        q_minus[32 + index][28 + index] = Fraction(-1)
    for item in pairing["pairing_serialization"]["entries"]:
        left, right = item["left_index"], item["right_index"]
        if 30 <= left < 66 and 30 <= right < 66:
            omega[left - 30][right - 30] = Fraction(item["coefficient"])
    degrees = [row["degree"] for row in pairing["component_basis"]["rows"][30:66]]

    def cyclicity(q: list[list[Fraction]]) -> int:
        qt = [list(row) for row in zip(*q, strict=True)]
        first, second = mul(qt, omega), mul(omega, q)
        return sum(first[row][column] + (-1 if degrees[row] % 2 else 1) * second[row][column] != 0 for row in range(36) for column in range(36))

    return (
        sum(entry != 0 for row in mul(q_plus, q_plus) for entry in row),
        cyclicity(q_plus),
        sum(entry != 0 for row in mul(q_minus, q_minus) for entry in row),
        cyclicity(q_minus),
    )


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = json.loads(RESULT.read_text()) if value is None else value
    errors: list[str] = []
    if value.get("result_id") != "STRICT_386_AUXILIARY_Q_SIGN_REPAIR_V1" or value.get("lifecycle") != "CLASSIFIED":
        errors.append("identity/lifecycle")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]:
        errors.append("dependency tags")
    predecessor = value.get("predecessor", {})
    predecessor_path = ROOT / predecessor.get("path", "")
    if predecessor.get("result_id") != "STRICT_386_FULL_Q1_SPLIT_SIGN_GATE_V1" or predecessor.get("preserved") is not True or not predecessor_path.is_file() or sha(predecessor_path) != predecessor.get("sha256"):
        errors.append("immutable predecessor")
    repair = value.get("repair", {})
    if repair != {
        "block": "AUX_V_STAR -> AUX_ETA_STAR",
        "old_declared_sign": "-I_4",
        "authoritative_sign": "+I_4",
        "source_and_ledgers_consistent": True,
        "repair_applied": True,
        "affected_chain_regenerated": True,
        "canonical_runner_dependency_order_repaired": True,
    }:
        errors.append("repair projection")
    plus_q2, plus_cyclic, minus_q2, minus_cyclic = replay()
    expected_replay = {
        "repaired_plus_sign": {"q_squared_defects": plus_q2, "odd_pairing_cyclicity_defects": plus_cyclic},
        "rejected_minus_sign_regression": {"q_squared_defects": minus_q2, "odd_pairing_cyclicity_defects": minus_cyclic},
        "discriminator": "Nilpotency accepts both isolated signs; the serialized odd pairing rejects the minus-sign regression with eight exact rational defects.",
    }
    if value.get("exact_replay") != expected_replay or (plus_q2, plus_cyclic, minus_q2, minus_cyclic) != (0, 0, 0, 8):
        errors.append("independent exact replay")
    for group in ("sources", "certificates"):
        for item in value.get("provenance", {}).get(group, {}).values():
            path = ROOT / item.get("path", "")
            if not path.is_file() or sha(path) != item.get("sha256"):
                errors.append("provenance " + item.get("path", ""))
    for group in ("pairing", "executable_witness"):
        item = value.get("provenance", {}).get(group, {})
        path = ROOT / item.get("path", "")
        if not path.is_file() or sha(path) != item.get("sha256"):
            errors.append("provenance " + item.get("path", ""))
    flags = value.get("claim_flags", {})
    for key in ("STRICT_386_AUXILIARY_Q_SIGN_REPAIR_APPLIED", "STRICT_386_AUXILIARY_Q_SOURCE_LEDGER_PAIRING_CONSISTENT", "AFFECTED_CLASSICAL_CERTIFICATE_CHAIN_VERIFIED", "FULL_CLASSICAL_COVARIANT_SUITE_PASSED"):
        if flags.get(key) is not True:
            errors.append("missing positive flag " + key)
    for key in ("STRICT_FULL_386_Q1_PORTABLE_COMPONENT_BYTES", "CLASSICAL_IMPORT_GATE_PASSED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED", "LORENTZIAN_QUANTUM_THEORY"):
        if flags.get(key) is not False:
            errors.append("claim promotion " + key)
    tier3 = value.get("verification", {}).get("tier_3", {})
    if tier3.get("status") != "PASS" or tier3.get("elapsed_seconds") != 1433.50 or "82/82 PASS" not in tier3.get("terminal_guard", ""):
        errors.append("Tier-3 receipt")
    keys = ("repair", "exact_replay", "verification", "claim_flags", "next_gate", "does_not_establish")
    if digest({key: value[key] for key in keys}) != value.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    return errors


def main() -> int:
    errors = check()
    print("STRICT_386_AUXILIARY_Q_SIGN_REPAIR_V1: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    if not errors:
        print("  - repaired +I4 source/ledger/pairing replay: zero defects")
        print("  - rejected -I4 regression replay: eight exact cyclicity defects")
        print("  - full q1, import acceptance, Hadamard and QME remain fail closed")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
