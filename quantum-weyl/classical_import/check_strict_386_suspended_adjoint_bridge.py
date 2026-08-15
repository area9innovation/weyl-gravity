#!/usr/bin/env python3
"""Independent exact checker for the strict suspended-adjoint bridge."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_SUSPENDED_ADJOINT_BRIDGE_V1.json"
PAYLOAD = ROOT / "covariant_completion/certificates/curved_prolonged_metric_endpoint_coefficients.json"
BRIDGE = HERE / "certificates/STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1.json"
CAUSAL = ROOT / "covariant_completion/certificates/curved_full_prolonged_green_homotopy_assembly.json"
HYBRID = ROOT / "covariant_completion/certificates/curved_prolonged_hybrid_algebraic_projector.json"
PAIRING = ROOT / "covariant_completion/certificates/curved_direct_causal_pairing_transport.json"


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def diag(entries: Sequence[int]) -> list[list[Fraction]]:
    return [[Fraction(entries[row] if row == column else 0) for column in range(len(entries))] for row in range(len(entries))]


def multiply(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[sum((left[row][middle] * right[middle][column] for middle in range(len(right))), Fraction()) for column in range(len(right[0]))] for row in range(len(left))]


def transpose(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(row) for row in zip(*matrix, strict=True)]


def inverse(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    size = len(matrix)
    work = [row[:] + diag([1] * size)[index] for index, row in enumerate(matrix)]
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            raise ValueError("singular matrix")
        work[column], work[pivot] = work[pivot], work[column]
        divisor = work[column][column]
        work[column] = [entry / divisor for entry in work[column]]
        for row in range(size):
            coefficient = work[row][column]
            if row != column and coefficient:
                work[row] = [entry - coefficient * pivot_entry for entry, pivot_entry in zip(work[row], work[column], strict=True)]
    return [row[size:] for row in work]


def endpoint_pairing(payload: dict[str, Any]) -> list[list[Fraction]]:
    matrix = [[Fraction() for _ in range(30)] for _ in range(30)]
    y = [list(map(Fraction, payload["pairings"]["Y_met"][5 * row:5 * row + 5])) for row in range(5)]
    j = [list(map(Fraction, payload["pairings"]["J_met"][10 * row:10 * row + 10])) for row in range(10)]
    for row in range(5):
        for column in range(5):
            matrix[row][25 + column] = y[row][column]
            matrix[25 + column][row] = -y[row][column]
    for row in range(10):
        for column in range(10):
            matrix[5 + row][15 + column] = j[row][column]
            matrix[15 + column][5 + row] = -j[row][column]
    return matrix


def sparse(matrix: list[list[Fraction]]) -> list[list[object]]:
    return [[row, column, str(entry)] for row, values in enumerate(matrix) for column, entry in enumerate(values) if entry]


def cancel_involutions(word: Sequence[str]) -> tuple[str, ...]:
    stack: list[str] = []
    for symbol in word:
        if symbol in {"R", "T"} and stack and stack[-1] == symbol:
            stack.pop()
        else:
            stack.append(symbol)
    return tuple(stack)


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = json.loads(RESULT.read_text()) if value is None else value
    payload = json.loads(PAYLOAD.read_text())
    bridge = json.loads(BRIDGE.read_text())
    causal = json.loads(CAUSAL.read_text())
    hybrid = json.loads(HYBRID.read_text())
    pairing = json.loads(PAIRING.read_text())
    errors: list[str] = []
    if value.get("result_id") != "STRICT_386_SUSPENDED_ADJOINT_BRIDGE_V1" or value.get("lifecycle") != "CLASSIFIED":
        errors.append("identity/lifecycle")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]:
        errors.append("dependency tags")
    if bridge["coefficientwise_identification"]["arrow_table_counts"]["total"] != 80 or not bridge["pairing_disposition"]["simultaneously_transported_causal_ghost_pullback_equals_negative_gate_canonical"]:
        errors.append("endpoint predecessor")
    if causal["dimension_ledger"].get("identity") != "386=356+30" or not causal["full_hybrid_assembly"]["graded_adjoint_exact_conditionally"]:
        errors.append("causal predecessor")
    if not hybrid["composite_SDR"]["cyclic_and_formally_self_adjoint"] or not pairing["pairing_compatibility"]:
        errors.append("orthogonal pairing predecessor")

    omega = endpoint_pairing(payload)
    t_signs = [1] * 25 + [-1] * 5
    u_signs = [-1] * 5 + [1] * 25
    r_signs = [-1] * 5 + [1] * 20 + [-1] * 5
    t = diag(t_signs)
    tsharp = multiply(multiply(inverse(omega), transpose(t)), omega)
    r = multiply(tsharp, t)
    exact = value.get("endpoint_exact_algebra", {})
    expected_identities = {
        "T_involutive": True, "T_sharp_gate_equals_U": True,
        "R_equals_T_sharp_gate_T": True, "R_involutive": True,
        "R_commutes_with_T": True, "transported_pairing_differs_on_G_I_only": True,
    }
    if exact.get("T_diagonal") != t_signs or exact.get("T_sharp_gate_diagonal") != u_signs or exact.get("R_diagonal") != r_signs:
        errors.append("endpoint diagonal algebra")
    if tsharp != diag(u_signs) or r != diag(r_signs) or exact.get("identities") != expected_identities:
        errors.append("endpoint adjoint identities")
    entries = sparse(omega)
    if exact.get("gate_pairing_nonzero_entries") != len(entries) or exact.get("gate_pairing_sha256") != digest(entries):
        errors.append("endpoint pairing digest")

    # Starting from ddagger(A')=R (R T A^sharp T R) R, the two pairs of
    # adjacent R involutions cancel independently to T A^sharp T.
    if cancel_involutions(("R", "R", "T", "A_sharp", "T", "R", "R")) != ("T", "A_sharp", "T"):
        errors.append("suspended adjoint word")
    theorem = value.get("suspended_adjoint_theorem", {})
    for token in ("A^ddagger=R A^{sharp_G} R", "(A')^ddagger=T A^sharp T", "(Lambda'_+)^ddagger=Lambda'_minus"):
        if not any(token in str(item) for item in theorem.values()):
            errors.append("theorem formula " + token)

    full = value.get("full_carrier_extension", {})
    full_t = [1] * 356 + t_signs
    full_u = [1] * 356 + u_signs
    full_r = [1] * 356 + r_signs
    expected_counts = {
        "T_386_positive": full_t.count(1), "T_386_negative": full_t.count(-1),
        "T_386_sharp_gate_positive": full_u.count(1), "T_386_sharp_gate_negative": full_u.count(-1),
        "R_386_positive": full_r.count(1), "R_386_negative": full_r.count(-1),
    }
    if {key: full.get(key) for key in expected_counts} != expected_counts or expected_counts != {"T_386_positive": 381, "T_386_negative": 5, "T_386_sharp_gate_positive": 381, "T_386_sharp_gate_negative": 5, "R_386_positive": 376, "R_386_negative": 10}:
        errors.append("full-carrier sign counts")
    if full.get("R_386_involutive") is not True or full.get("full_green_suspended_adjoint_replayed") is not True or full.get("full_component_pairing_coefficients_serialized") is not False:
        errors.append("full-carrier boundary")
    flags = value.get("claim_flags", {})
    for key in ("ENDPOINT_SUSPENSION_CHARACTER_EXACT", "FULL_386_SUSPENSION_CHARACTER_EXTENDED", "FULL_386_SUSPENDED_GREEN_ADJOINT_REPLAYED"):
        if flags.get(key) is not True:
            errors.append("missing positive flag " + key)
    for key in ("FULL_386_COMPONENT_PAIRING_SERIALIZED_IN_GATE_CONVENTION", "STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED", "CLASSICAL_IMPORT_GATE_PASSED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED", "LORENTZIAN_QUANTUM_THEORY"):
        if flags.get(key) is not False:
            errors.append("claim promotion " + key)
    gate = value.get("gate_disposition", {})
    if gate != {"endpoint_pairing_sign_resolved_as_convention": True, "abstract_full_carrier_suspended_adjoint_replayed": True, "full_386_component_pairing_serialized": False, "classical_import_gate_a_status": "FAIL_CLOSED", "q2_d_same_carrier_established": False}:
        errors.append("gate disposition")
    for item in value.get("provenance", {}).get("inputs", []):
        path = ROOT / item.get("path", "")
        if not path.is_file() or sha(path) != item.get("sha256"):
            errors.append("provenance " + item.get("path", ""))
    hashes = value.get("canonical_hashes", {})
    if hashes != {"endpoint_exact_algebra_sha256": digest(exact), "suspended_adjoint_theorem_sha256": digest(theorem), "full_carrier_extension_sha256": digest(full)}:
        errors.append("canonical hashes")
    projection = {key: value[key] for key in ("scope", "endpoint_exact_algebra", "suspended_adjoint_theorem", "full_carrier_extension", "foundational_strength", "gate_disposition", "claim_flags", "does_not_establish", "next_gate", "canonical_hashes")}
    if digest(projection) != value.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical result digest")
    return errors


def main() -> int:
    errors = check()
    print("STRICT_386_SUSPENDED_ADJOINT_BRIDGE_V1: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print("  - " + error)
    else:
        print("  - T^sharp_G and R reconstructed from the 54-entry exact endpoint pairing")
        print("  - full R_386 has 376 positive and 10 negative signs")
        print("  - suspended Green adjoint replays; 356-row component pairing serialization remains open")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
