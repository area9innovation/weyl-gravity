#!/usr/bin/env python3
"""Independent exact receiver for the strict full-q1 split sign gate."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_FULL_Q1_SPLIT_SIGN_GATE_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
PORTABILITY = HERE / "certificates/STRICT_386_OPERATOR_PORTABILITY_AUDIT_V1.json"
WITNESS = HERE / "certificates/STRICT_386_AUXILIARY_Q_SIGN_WITNESS_V1.json"
GENERALIZED = ROOT / "covariant_completion/certificates/generalized_auxiliary_contraction.json"
CURVED = ROOT / "covariant_completion/certificates/curved_auxiliary_canonical_split.json"
FACTORIZED_SOURCE = ROOT / "covariant_completion/curved_retract/factorized_q_split.py"
REPAIR = HERE / "certificates/STRICT_386_AUXILIARY_Q_SIGN_REPAIR_V1.json"
SUPERSEDED_PATHS = {
    "covariant_completion/certificates/generalized_auxiliary_contraction.json",
    "covariant_completion/certificates/curved_auxiliary_canonical_split.json",
    "covariant_completion/curved_retract/factorized_q_split.py",
    "covariant_completion/auxiliary_equivalence/generalized_retract.py",
    "covariant_completion/curved_retract/universal_split.py",
}


Matrix = list[list[Fraction]]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def zero(size: int) -> Matrix:
    return [[Fraction() for _ in range(size)] for _ in range(size)]


def eye(size: int, coefficient: int = 1) -> Matrix:
    return [[Fraction(coefficient if row == column else 0) for column in range(size)] for row in range(size)]


def multiply(left: Matrix, right: Matrix) -> Matrix:
    size = len(left)
    return [[sum((left[row][middle] * right[middle][column] for middle in range(size)), Fraction()) for column in range(size)] for row in range(size)]


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix, strict=True)]


def inverse(matrix: Matrix) -> Matrix:
    size = len(matrix)
    work = [row[:] + eye(size)[index] for index, row in enumerate(matrix)]
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            raise ValueError("singular")
        work[column], work[pivot] = work[pivot], work[column]
        divisor = work[column][column]
        work[column] = [entry / divisor for entry in work[column]]
        for row in range(size):
            coefficient = work[row][column]
            if row != column and coefficient:
                work[row] = [entry - coefficient * source for entry, source in zip(work[row], work[column], strict=True)]
    return [row[size:] for row in work]


def add(left: Matrix, right: Matrix) -> Matrix:
    return [[a + b for a, b in zip(lrow, rrow, strict=True)] for lrow, rrow in zip(left, right, strict=True)]


def decode_q(witness: dict[str, Any]) -> Matrix:
    result = zero(36)
    for target, source, coefficient in witness.get("entries", []):
        if not (0 <= target < 36 and 0 <= source < 36) or result[target][source]:
            raise ValueError("witness entry identity")
        result[target][source] = Fraction(coefficient)
    return result


def decode_pairing(pairing: dict[str, Any]) -> Matrix:
    result = zero(36)
    for item in pairing["pairing_serialization"]["entries"]:
        left, right = item["left_index"], item["right_index"]
        if 30 <= left < 66 and 30 <= right < 66:
            result[left - 30][right - 30] = Fraction(item["coefficient"])
    return result


def cyclic(q: Matrix, omega: Matrix, degrees: list[int]) -> Matrix:
    first = multiply(transpose(q), omega)
    second = multiply(omega, q)
    return [[first[row][column] + Fraction(-1 if degrees[row] % 2 else 1) * second[row][column] for column in range(36)] for row in range(36)]


def entries(matrix: Matrix, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"left_index": left + 30, "right_index": right + 30, "left": rows[left + 30]["row_id"], "right": rows[right + 30]["row_id"], "coefficient": str(matrix[left][right])} for left in range(36) for right in range(36) if matrix[left][right]]


def contraction(q: Matrix) -> Matrix:
    h = zero(36)
    for source, target, size in ((0, 14, 4), (4, 18, 10), (28, 32, 4)):
        block = [[q[target + row][source + column] for column in range(size)] for row in range(size)]
        inv = inverse(block)
        for row in range(size):
            for column in range(size):
                h[source + row][target + column] = -inv[row][column]
    return add(multiply(q, h), multiply(h, q))


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = json.loads(RESULT.read_text()) if value is None else value
    repair = json.loads(REPAIR.read_text()) if REPAIR.is_file() else {}
    superseded = (
        repair.get("result_id") == "STRICT_386_AUXILIARY_Q_SIGN_REPAIR_V1"
        and repair.get("predecessor", {}).get("sha256") == sha(RESULT)
        and repair.get("repair", {}).get("repair_applied") is True
    )
    pairing = json.loads(PAIRING.read_text())
    witness = json.loads(WITNESS.read_text())
    generalized = json.loads(GENERALIZED.read_text())
    curved = json.loads(CURVED.read_text())
    errors: list[str] = []
    if value.get("result_id") != "STRICT_386_FULL_Q1_SPLIT_SIGN_GATE_V1" or value.get("lifecycle") != "CLASSIFIED":
        errors.append("identity/lifecycle")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]:
        errors.append("dependency tags")
    if witness.get("matrix_sha256") != generalized.get("matrix_sha256", {}).get("auxiliary_differential") or witness.get("authority_matrix_sha256") != witness.get("matrix_sha256"):
        errors.append("executable matrix digest")
    if witness.get("nonzero_entries") != 30 or witness.get("observed_blocks", {}).get("v_star_to_eta_star") != "+I_4":
        errors.append("witness sign/count")
    if not superseded:
        if curved.get("factorized_curved_Q_split", {}).get("transformed_Q", {}).get("generalized_auxiliary", [])[-1:] != ["v^* -> -eta^*"]:
            errors.append("curved declaration")
        if 'q[9][8] = OperatorPolynomial.identity(-1)' not in FACTORIZED_SOURCE.read_text():
            errors.append("factorized source declaration")
    elif repair.get("claim_flags", {}).get("AFFECTED_CLASSICAL_CERTIFICATE_CHAIN_VERIFIED") is not True:
        errors.append("superseding repair chain")

    try:
        q_plus = decode_q(witness)
    except (ValueError, KeyError, ZeroDivisionError):
        errors.append("witness decoding")
        q_plus = zero(36)
    q_minus = [row[:] for row in q_plus]
    for index in range(4):
        q_minus[32 + index][28 + index] = Fraction(-1)
    omega = decode_pairing(pairing)
    rows = pairing["component_basis"]["rows"]
    degrees = [row["degree"] for row in rows[30:66]]
    plus_defects = entries(cyclic(q_plus, omega, degrees), rows)
    minus_defects = entries(cyclic(q_minus, omega, degrees), rows)
    expected_replay = {
        "executable_plus_sign": {
            "q_squared_defects": sum(bool(item) for row in multiply(q_plus, q_plus) for item in row),
            "contraction_defects": sum(left != right for lrow, rrow in zip(contraction(q_plus), eye(36, -1), strict=True) for left, right in zip(lrow, rrow, strict=True)),
            "cyclicity_defects": len(plus_defects),
        },
        "declared_minus_sign": {
            "q_squared_defects": sum(bool(item) for row in multiply(q_minus, q_minus) for item in row),
            "contraction_defects": sum(left != right for lrow, rrow in zip(contraction(q_minus), eye(36, -1), strict=True) for left, right in zip(lrow, rrow, strict=True)),
            "cyclicity_defects": len(minus_defects),
            "cyclicity_defect_entries": minus_defects,
        },
        "discriminator": "Nilpotency and contractibility do not distinguish the signs; the serialized exact odd pairing does.",
    }
    if value.get("exact_replay") != expected_replay or len(minus_defects) != 8 or plus_defects:
        errors.append("exact sign replay")
    conflict = value.get("sign_conflict", {})
    if conflict.get("executable_matrix_sign") != "+I_4" or conflict.get("factorized_source_and_certificate_sign") != "-I_4" or conflict.get("text_matrix_consistent") is not False:
        errors.append("sign-conflict projection")
    if value.get("coordinate_diagnosis", {}).get("T_A_B_location", "").startswith("degree-zero canonical shear") is not True:
        errors.append("split-coordinate classification")
    if value.get("repair_analysis", {}).get("repair_applied") is not False or "+eta_star" not in value.get("repair_analysis", {}).get("preferred_repair", ""):
        errors.append("repair boundary")
    flags = value.get("claim_flags", {})
    for key in ("STRICT_386_AUXILIARY_Q_TEXT_MATRIX_SIGN_CONFLICT_CERTIFIED", "STRICT_386_EXECUTABLE_AUXILIARY_Q_CYCLIC_WITH_SERIALIZED_PAIRING", "STRICT_386_SPLIT_COORDINATE_LOCATION_CLASSIFIED"):
        if flags.get(key) is not True:
            errors.append("missing positive flag " + key)
    for key in ("STRICT_386_DECLARED_MINUS_SIGN_CYCLIC_WITH_SERIALIZED_PAIRING", "STRICT_FULL_386_Q1_PORTABLE_COMPONENT_BYTES", "STRICT_386_ALL_OPERATOR_COMPONENT_ADJOINTS_REPLAYED", "CLASSICAL_IMPORT_GATE_PASSED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED", "LORENTZIAN_QUANTUM_THEORY"):
        if flags.get(key) is not False:
            errors.append("claim promotion " + key)
    projection_keys = ("carrier", "coordinate_diagnosis", "sign_conflict", "exact_replay", "repair_analysis", "foundational_strength", "claim_flags", "does_not_establish", "next_gate")
    if digest({key: value[key] for key in projection_keys}) != value.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    for item in value.get("provenance", {}).get("inputs", []):
        path = ROOT / item.get("path", "")
        historical = superseded and item.get("path") in SUPERSEDED_PATHS
        recorded = item.get("sha256", "")
        if historical:
            if len(recorded) != 64 or any(character not in "0123456789abcdef" for character in recorded):
                errors.append("historical provenance " + item.get("path", ""))
        elif not path.is_file() or sha(path) != recorded:
            errors.append("provenance " + item.get("path", ""))
    return errors


def main() -> int:
    errors = check()
    print("STRICT_386_FULL_Q1_SPLIT_SIGN_GATE_V1: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print("  - " + error)
    else:
        print("  - executable +I dual arrow: zero exact cyclicity defects")
        print("  - declared -I dual arrow: eight exact cyclicity defects")
        repair = json.loads(REPAIR.read_text()) if REPAIR.is_file() else {}
        if repair.get("repair", {}).get("repair_applied") is True:
            print("  - historical diagnosis preserved; superseding repair is certified")
        else:
            print("  - full q1 serialization remains fail closed pending classical sign repair")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
