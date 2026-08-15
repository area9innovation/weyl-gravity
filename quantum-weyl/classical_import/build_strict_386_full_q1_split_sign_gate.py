#!/usr/bin/env python3
"""Build the fail-closed sign gate preceding full split-basis q1 serialization."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_FULL_Q1_SPLIT_SIGN_GATE_V1.json"
REPORT = HERE / "REPORT_STRICT_386_FULL_Q1_SPLIT_SIGN_GATE_V1.md"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
PORTABILITY = HERE / "certificates/STRICT_386_OPERATOR_PORTABILITY_AUDIT_V1.json"
WITNESS = HERE / "certificates/STRICT_386_AUXILIARY_Q_SIGN_WITNESS_V1.json"
GENERALIZED = ROOT / "covariant_completion/certificates/generalized_auxiliary_contraction.json"
CURVED = ROOT / "covariant_completion/certificates/curved_auxiliary_canonical_split.json"
FACTORIZED_SOURCE = ROOT / "covariant_completion/curved_retract/factorized_q_split.py"
GENERALIZED_SOURCE = ROOT / "covariant_completion/auxiliary_equivalence/generalized_retract.py"
UNIVERSAL_SOURCE = ROOT / "covariant_completion/curved_retract/universal_split.py"


Matrix = list[list[Fraction]]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def zero(size: int) -> Matrix:
    return [[Fraction() for _ in range(size)] for _ in range(size)]


def eye(size: int, coefficient: int = 1) -> Matrix:
    return [[Fraction(coefficient if row == column else 0) for column in range(size)] for row in range(size)]


def add(left: Matrix, right: Matrix) -> Matrix:
    return [[a + b for a, b in zip(lrow, rrow, strict=True)] for lrow, rrow in zip(left, right, strict=True)]


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
            raise ValueError("singular block")
        work[column], work[pivot] = work[pivot], work[column]
        divisor = work[column][column]
        work[column] = [entry / divisor for entry in work[column]]
        for row in range(size):
            if row == column or not work[row][column]:
                continue
            coefficient = work[row][column]
            work[row] = [entry - coefficient * source for entry, source in zip(work[row], work[column], strict=True)]
    return [row[size:] for row in work]


def decode_witness(value: dict[str, Any]) -> Matrix:
    matrix = zero(36)
    for target, source, coefficient in value["entries"]:
        matrix[target][source] = Fraction(coefficient)
    return matrix


def pairing_matrix(value: dict[str, Any]) -> Matrix:
    matrix = zero(36)
    for item in value["pairing_serialization"]["entries"]:
        left, right = item["left_index"], item["right_index"]
        if 30 <= left < 66 and 30 <= right < 66:
            matrix[left - 30][right - 30] = Fraction(item["coefficient"])
    return matrix


def cyclic_defect(q: Matrix, omega: Matrix, degrees: list[int]) -> Matrix:
    ordinary = multiply(transpose(q), omega)
    second = multiply(omega, q)
    signed = [[Fraction(-1 if degrees[row] % 2 else 1) * entry for entry in second[row]] for row in range(36)]
    return add(ordinary, signed)


def nonzero_entries(matrix: Matrix, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "left_index": left + 30,
            "right_index": right + 30,
            "left": rows[left + 30]["row_id"],
            "right": rows[right + 30]["row_id"],
            "coefficient": str(matrix[left][right]),
        }
        for left in range(36)
        for right in range(36)
        if matrix[left][right]
    ]


def contraction(q: Matrix) -> Matrix:
    homotopy = zero(36)
    blocks = ((0, 14, 4), (4, 18, 10), (28, 32, 4))
    for source, target, size in blocks:
        arrow = [[q[target + row][source + column] for column in range(size)] for row in range(size)]
        inv = inverse(arrow)
        for row in range(size):
            for column in range(size):
                homotopy[source + row][target + column] = -inv[row][column]
    return add(multiply(q, homotopy), multiply(homotopy, q))


INPUTS = (
    (PAIRING, "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1", "fixed 386-row basis and exact odd pairing"),
    (PORTABILITY, "STRICT_386_OPERATOR_PORTABILITY_AUDIT_V1", "predecessor operator portability classification"),
    (WITNESS, "strict-386-auxiliary-q-sign-witness-v1", "producer-observed 36-row executable q entries"),
    (GENERALIZED, "pure-weyl-support-local-generalized-auxiliary-retract-v1", "matrix digest and textual arrow declaration"),
    (CURVED, "pure-weyl-curved-auxiliary-canonical-split-v1", "factorized actual-curved-Q declaration"),
)


def identity(value: dict[str, Any]) -> str | None:
    return value.get("result_id") or value.get("schema")


def build() -> dict[str, Any]:
    loaded = {path: json.loads(path.read_text()) for path, _, _ in INPUTS}
    for path, expected, _ in INPUTS:
        if identity(loaded[path]) != expected:
            raise ValueError(f"dependency identity drift: {path}")
    pairing = loaded[PAIRING]
    portability = loaded[PORTABILITY]
    witness = loaded[WITNESS]
    generalized = loaded[GENERALIZED]
    curved = loaded[CURVED]
    if witness["matrix_sha256"] != generalized["matrix_sha256"]["auxiliary_differential"]:
        raise ValueError("witness/authority matrix digest mismatch")
    if witness["observed_blocks"]["v_star_to_eta_star"] != "+I_4":
        raise ValueError("executable sign observation drift")
    declared = curved["factorized_curved_Q_split"]["transformed_Q"]["generalized_auxiliary"]
    if declared[-1] != "v^* -> -eta^*":
        raise ValueError("factorized sign declaration drift")
    source_text = FACTORIZED_SOURCE.read_text()
    if 'q[9][8] = OperatorPolynomial.identity(-1)' not in source_text:
        raise ValueError("factorized source sign drift")

    rows = pairing["component_basis"]["rows"]
    degrees = [row["degree"] for row in rows[30:66]]
    omega = pairing_matrix(pairing)
    q_observed = decode_witness(witness)
    q_declared = [row[:] for row in q_observed]
    for index in range(4):
        q_declared[32 + index][28 + index] = Fraction(-1)
    observed_cyclic = cyclic_defect(q_observed, omega, degrees)
    declared_cyclic = cyclic_defect(q_declared, omega, degrees)
    observed_defects = nonzero_entries(observed_cyclic, rows)
    declared_defects = nonzero_entries(declared_cyclic, rows)
    if observed_defects or len(declared_defects) != 8:
        raise ValueError("auxiliary sign-gate defect count drift")
    if multiply(q_observed, q_observed) != zero(36) or multiply(q_declared, q_declared) != zero(36):
        raise ValueError("auxiliary nilpotency drift")
    if contraction(q_observed) != eye(36, -1) or contraction(q_declared) != eye(36, -1):
        raise ValueError("auxiliary contraction drift")

    projection = {
        "carrier": {
            "basis_result": pairing["result_id"],
            "rows": 386,
            "auxiliary_rows": 36,
            "auxiliary_global_range": [30, 65],
            "pairing_entries_on_auxiliary_rows": pairing["pairing_serialization"]["sector_nonzero_ordered_entry_counts"]["auxiliary_complement"],
        },
        "coordinate_diagnosis": {
            "published_basis": pairing["component_basis"]["ordering"],
            "full_q1_target_presentation": "factorized curved auxiliary split plus split curvature mapping cylinder",
            "T_A_B_location": "degree-zero canonical shear, inclusion/projection and unshifted graph presentation; not primitive arrows of q1 in the published split basis",
            "consequence": "The first full-q1 table should serialize the split differential and serialize the canonical shear separately.",
        },
        "sign_conflict": {
            "block": "AUX_V_STAR -> AUX_ETA_STAR",
            "global_source_rows": [58, 59, 60, 61],
            "global_target_rows": [62, 63, 64, 65],
            "executable_matrix_sign": "+I_4",
            "factorized_source_and_certificate_sign": "-I_4",
            "executable_matrix_sha256": witness["matrix_sha256"],
            "generalized_authority_matrix_sha256": generalized["matrix_sha256"]["auxiliary_differential"],
            "text_matrix_consistent": False,
        },
        "exact_replay": {
            "executable_plus_sign": {
                "q_squared_defects": 0,
                "contraction_defects": 0,
                "cyclicity_defects": 0,
            },
            "declared_minus_sign": {
                "q_squared_defects": 0,
                "contraction_defects": 0,
                "cyclicity_defects": len(declared_defects),
                "cyclicity_defect_entries": declared_defects,
            },
            "discriminator": "Nilpotency and contractibility do not distinguish the signs; the serialized exact odd pairing does.",
        },
        "repair_analysis": {
            "preferred_repair": "Change the factorized curved q dual arrow and textual certificate ledgers to v_star -> +eta_star, matching the executable matrix and current odd pairing.",
            "alternative": "Flip an auxiliary pairing orientation and reverify the entire canonical lift.",
            "alternative_cost": "The alternative changes already serialized pairing bytes and has a wider affected chain.",
            "repair_applied": False,
        },
        "foundational_strength": {
            "exact_sign_gate_upper_bound": "PRA",
            "choice_operation_added": False,
            "analytic_or_infinite_argument_used": False,
        },
        "claim_flags": {
            "STRICT_386_AUXILIARY_Q_TEXT_MATRIX_SIGN_CONFLICT_CERTIFIED": True,
            "STRICT_386_EXECUTABLE_AUXILIARY_Q_CYCLIC_WITH_SERIALIZED_PAIRING": True,
            "STRICT_386_DECLARED_MINUS_SIGN_CYCLIC_WITH_SERIALIZED_PAIRING": False,
            "STRICT_386_SPLIT_COORDINATE_LOCATION_CLASSIFIED": True,
            "STRICT_FULL_386_Q1_PORTABLE_COMPONENT_BYTES": False,
            "STRICT_386_ALL_OPERATOR_COMPONENT_ADJOINTS_REPLAYED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
            "LORENTZIAN_QUANTUM_THEORY": False,
        },
        "does_not_establish": [
            "that the preferred sign repair has been applied to the authoritative classical source and affected certificate chain",
            "a receiver-readable full 386-row q1 component jet table or accepted common operator snapshot hash",
            "componentwise nilpotency and cyclicity of the endpoint and curvature-cone blocks in one combined artifact",
            "portable local SDR maps, endpoint/full Green actions, local D or q2 compatibility",
            "a Hadamard state, Ward theorem, QME restoration, residual transfer or Lorentzian quantum theory",
        ],
        "next_gate": "Repair the factorized curved auxiliary dual-arrow sign to +I_4 or explicitly replace the auxiliary pairing convention, then regenerate and verify the affected classical certificate chain. Only after the repaired source and serialized pairing agree should the full split-basis q1 table be emitted.",
    }
    value: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-386-full-q1-split-sign-gate-v1",
        "result_id": "STRICT_386_FULL_Q1_SPLIT_SIGN_GATE_V1",
        "result_kind": "EXACT_CLASSICAL_IMPORT_TEXT_MATRIX_SIGN_CONSISTENCY_GATE",
        "result_state": "FULL_Q1_SERIALIZATION_BLOCKED_BY_AUXILIARY_COTANGENT_SIGN_CONFLICT",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "5d640c50974b09a12b8bc6e0bfcbafc084636f25",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "question": "Do the executable generalized-auxiliary q bytes, the factorized curved-Q declaration and the serialized odd pairing define one cyclic 36-row summand before they are embedded into the full 386-row q1 table?",
        "answer": "No. The executable generalized-auxiliary matrix whose SHA-256 is already certified contains v_star -> +eta_star on four rows. The factorized actual-curved-Q source and both generalized/curved human ledgers instead declare v_star -> -eta_star. Nilpotency and the 36-row contraction hold for either sign, so the existing algebraic checks cannot detect the mismatch. The serialized exact odd pairing does: the executable plus sign has zero component cyclicity defects, while the declared minus sign has eight exact defects, two orientations for each of four components. The published 386-row carrier is the split mapping-cylinder presentation, so T, A and B belong to the separate canonical shear and endpoint inclusion/projection, not to the primitive split q1 arrows. Full q1 serialization must therefore pause at this sign gate. The minimal repair is to change the factorized dual arrow and textual ledgers to plus, matching both the executable matrix and the current pairing, and then rerun the affected classical chain. No causal theorem is revoked and no Hadamard or QME claim is promoted.",
        **projection,
        "provenance": {
            "inputs": [
                {"path": str(path.relative_to(ROOT)), "result_or_schema_id": expected, "sha256": sha(path), "role": role}
                for path, expected, role in INPUTS
            ] + [
                {"path": str(path.relative_to(ROOT)), "result_or_schema_id": "EXECUTABLE_SOURCE", "sha256": sha(path), "role": role}
                for path, role in (
                    (FACTORIZED_SOURCE, "factorized actual-curved-Q sign declaration"),
                    (GENERALIZED_SOURCE, "producer of the hashed executable 36-row matrix"),
                    (UNIVERSAL_SOURCE, "universal split consumer and textual sign declaration"),
                )
            ]
        },
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_386_full_q1_split_sign_gate.py",
            "expected_digest": digest(projection),
        },
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_386_FULL_Q1_SPLIT_SIGN_GATE_V1.md",
    }
    return value


def render(value: dict[str, Any]) -> str:
    replay = value["exact_replay"]
    lines = [
        "# Strict 386-row full-q1 split sign gate v1", "", "## Outcome", "", value["answer"], "",
        "## Exact sign comparison", "", "| candidate | q1 squared | contraction | pairing cyclicity |", "|---|---:|---:|---:|",
        f"| executable `+I_4` | {replay['executable_plus_sign']['q_squared_defects']} defects | {replay['executable_plus_sign']['contraction_defects']} defects | {replay['executable_plus_sign']['cyclicity_defects']} defects |",
        f"| declared `-I_4` | {replay['declared_minus_sign']['q_squared_defects']} defects | {replay['declared_minus_sign']['contraction_defects']} defects | **{replay['declared_minus_sign']['cyclicity_defects']} defects** |", "",
        "The eight failures are not numerical noise: all coefficients are exact rationals. Nilpotency and contractibility are blind to this isolated cotangent sign; the odd pairing is the decisive independent rail.", "",
        "## Coordinate consequence", "", value["coordinate_diagnosis"]["consequence"], "",
        "## Preferred repair", "", value["repair_analysis"]["preferred_repair"], "", "The repair is **not applied by this result**. The classical affected chain must be regenerated before full q1 bytes can be accepted.", "",
        "## Reproduction", "", "```text", "PYTHONPATH=<sympy-site> python3 quantum-weyl/classical_import/produce_strict_386_auxiliary_q_sign_witness.py --check", "python3 quantum-weyl/classical_import/build_strict_386_full_q1_split_sign_gate.py --check", "python3 quantum-weyl/classical_import/check_strict_386_full_q1_split_sign_gate.py", "python3 quantum-weyl/classical_import/verify_strict_386_full_q1_split_sign_gate.py", "python3 -m unittest quantum-weyl/classical_import/tests/test_strict_386_full_q1_split_sign_gate.py", "```", "", "## Boundaries", "",
    ]
    lines.extend(f"- This does not establish {item}." for item in value["does_not_establish"])
    lines += ["", "## Next gate", "", value["next_gate"], ""]
    return "\n".join(lines)


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, report = generated()
    stale = [str(path.relative_to(ROOT)) for path, content in ((RESULT, result), (REPORT, report)) if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("STRICT_386_FULL_Q1_SPLIT_SIGN_GATE_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("STRICT_386_FULL_Q1_SPLIT_SIGN_GATE_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
