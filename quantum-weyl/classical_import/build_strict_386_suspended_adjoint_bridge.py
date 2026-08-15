#!/usr/bin/env python3
"""Build the exact suspension-twisted adjoint bridge on the strict carrier."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_SUSPENDED_ADJOINT_BRIDGE_V1.json"
REPORT = HERE / "REPORT_STRICT_386_SUSPENDED_ADJOINT_BRIDGE_V1.md"
ENDPOINT_BRIDGE = HERE / "certificates/STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1.json"
CYCLIC = HERE / "certificates/STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.json"
PAYLOAD = ROOT / "covariant_completion/certificates/curved_prolonged_metric_endpoint_coefficients.json"
CAUSAL = ROOT / "covariant_completion/certificates/curved_full_prolonged_green_homotopy_assembly.json"
HYBRID = ROOT / "covariant_completion/certificates/curved_prolonged_hybrid_algebraic_projector.json"
PAIRING = ROOT / "covariant_completion/certificates/curved_direct_causal_pairing_transport.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def zero(size: int) -> list[list[Fraction]]:
    return [[Fraction() for _ in range(size)] for _ in range(size)]


def diag(entries: Sequence[int]) -> list[list[Fraction]]:
    return [[Fraction(entries[row] if row == column else 0) for column in range(len(entries))] for row in range(len(entries))]


def transpose(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(row) for row in zip(*matrix, strict=True)]


def multiply(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[sum((left[row][middle] * right[middle][column] for middle in range(len(right))), Fraction()) for column in range(len(right[0]))] for row in range(len(left))]


def inverse(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    size = len(matrix)
    identity = diag([1] * size)
    work = [row[:] + identity[index] for index, row in enumerate(matrix)]
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            raise ValueError("singular endpoint pairing")
        work[column], work[pivot] = work[pivot], work[column]
        divisor = work[column][column]
        work[column] = [entry / divisor for entry in work[column]]
        for row in range(size):
            coefficient = work[row][column]
            if row != column and coefficient:
                work[row] = [entry - coefficient * pivot_entry for entry, pivot_entry in zip(work[row], work[column], strict=True)]
    return [row[size:] for row in work]


def pairing_matrix(payload: dict[str, Any]) -> list[list[Fraction]]:
    matrix = zero(30)
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


INPUTS = (
    (ENDPOINT_BRIDGE, "STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1", "common minimal q1 content and pairing-sign boundary"),
    (CYCLIC, "STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1", "Gate-canonical suspended BV convention"),
    (PAYLOAD, "pure-weyl-prolonged-metric-endpoint-coefficients-v1", "exact endpoint pairings"),
    (CAUSAL, "pure-weyl-full-prolonged-green-homotopy-assembly-v1", "full causal Green homotopy and adjoint relation"),
    (HYBRID, "pure-weyl-prolonged-hybrid-algebraic-projector-v1", "cyclic orthogonal 356+30 decomposition"),
    (PAIRING, "pure-weyl-direct-causal-pairing-transport-v1", "causal Green/current pairing theorem"),
)


def source_id(value: dict[str, Any]) -> str | None:
    return value.get("result_id") or value.get("schema")


def build() -> dict[str, Any]:
    values = {path: json.loads(path.read_text()) for path, _, _ in INPUTS}
    for path, expected, _ in INPUTS:
        if source_id(values[path]) != expected:
            raise ValueError("dependency identity drift: " + str(path))
    bridge, cyclic, payload, causal, hybrid, pairing = (values[path] for path, _, _ in INPUTS)
    if bridge["coefficientwise_identification"]["arrow_table_counts"]["total"] != 80:
        raise ValueError("common endpoint q1 unavailable")
    if not cyclic["claim_flags"]["BV_CYCLICITY_Q1_REPLAYED"]:
        raise ValueError("Gate suspension cyclicity unavailable")
    if causal["dimension_ledger"].get("identity") != "386=356+30" or not causal["full_hybrid_assembly"]["graded_adjoint_exact_conditionally"]:
        raise ValueError("full causal adjoint theorem unavailable")
    if not hybrid["composite_SDR"]["cyclic_and_formally_self_adjoint"]:
        raise ValueError("orthogonal hybrid decomposition unavailable")
    if not pairing["pairing_compatibility"]:
        raise ValueError("causal pairing theorem unavailable")

    omega = pairing_matrix(payload)
    t_signs = [1] * 25 + [-1] * 5
    t = diag(t_signs)
    t_sharp = multiply(multiply(inverse(omega), transpose(t)), omega)
    r = multiply(t_sharp, t)
    u_signs = [-1] * 5 + [1] * 25
    r_signs = [-1] * 5 + [1] * 20 + [-1] * 5
    if t_sharp != diag(u_signs) or r != diag(r_signs):
        raise ValueError("endpoint adjoint/suspension character drift")
    if multiply(r, r) != diag([1] * 30) or multiply(r, t) != multiply(t, r):
        raise ValueError("suspension involution/commutation failed")

    full_t = [1] * 356 + t_signs
    full_t_sharp = [1] * 356 + u_signs
    full_r = [1] * 356 + r_signs
    value: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-386-suspended-adjoint-bridge-v1",
        "result_id": "STRICT_386_SUSPENDED_ADJOINT_BRIDGE_V1",
        "result_kind": "SAME_THEORY_FULL_CARRIER_SUSPENSION_CONVENTION_BRIDGE",
        "result_state": "PAIRING_SIGN_IDENTIFIED_AS_SUSPENDED_ADJOINT_TWIST_FULL_COMPONENT_PAIRING_SERIALIZATION_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "f2d898b68309a437d66b3efeec6307580a4fd269",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "question": "Is the five-row pairing sign found by the endpoint q1 bridge a causal obstruction, or the explicit difference between the causal and Gate BV suspension adjoints?",
        "answer": "It is an exact suspension-adjoint twist, not a new obstruction to the unary causal architecture. On the thirty-row endpoint, let T=diag(I_5,I_10,I_10,-I_5) be the q1 sign transport and let sharp_G use the untransported endpoint pairing, which the content bridge pulls back to the Gate-canonical pairing. Exact rational matrix algebra gives T^{sharp_G}=U=diag(-I_5,I_10,I_10,I_5) and R=T^{sharp_G}T=diag(-I_5,I_10,I_10,-I_5). Therefore, for every transported operator A'=TAT, (A')^{sharp_G}=R T A^sharp T R. Defining the Gate suspended adjoint A^ddagger=R A^{sharp_G} R recovers the source adjoint exactly. In particular q' is odd cyclic in the certified Gate convention and (Lambda'_+)^ddagger=Lambda'_- while the two-sided causal homotopy and support identities stay unchanged. The cyclic self-adjoint 356+30 projector extends R by I_356, giving a full-carrier order-zero involution with 376 positive and ten negative signs. This resolves the endpoint sign conceptually and algebraically, but it does not serialize the 356-row pairing coefficients or produce a Gate-A common full-carrier hash. q2, D, Hadamard and QME remain open.",
        "scope": {
            "theory": "strict pure-Weyl unary BV complex",
            "background": "unit conformal cylinder",
            "endpoint_dimension": 30,
            "algebraic_complement_dimension": 356,
            "full_dimension": 386,
            "arithmetic": "exact rational endpoint matrices plus finite involution algebra",
        },
        "endpoint_exact_algebra": {
            "ordered_blocks": ["G[5] degree -1", "M[10] degree 0", "E[10] degree 1", "I[5] degree 2"],
            "gate_pairing_nonzero_entries": len(sparse(omega)),
            "gate_pairing_sha256": digest(sparse(omega)),
            "T_diagonal": t_signs,
            "T_sharp_gate_diagonal": u_signs,
            "R_diagonal": r_signs,
            "identities": {
                "T_involutive": multiply(t, t) == diag([1] * 30),
                "T_sharp_gate_equals_U": t_sharp == diag(u_signs),
                "R_equals_T_sharp_gate_T": r == multiply(t_sharp, t),
                "R_involutive": multiply(r, r) == diag([1] * 30),
                "R_commutes_with_T": multiply(r, t) == multiply(t, r),
                "transported_pairing_differs_on_G_I_only": True,
            },
        },
        "suspended_adjoint_theorem": {
            "gate_ordinary_adjoint": "sharp_G is defined by the untransported endpoint pairing pulled back to the Gate-canonical pairing",
            "suspension_character": "R=diag(-I_G,+I_M,+I_E,-I_I)",
            "gate_suspended_adjoint": "A^ddagger=R A^{sharp_G} R",
            "universal_transport_formula": "for A'=T A T, (A')^{sharp_G}=R T A^sharp T R",
            "recovered_formula": "(A')^ddagger=T A^sharp T",
            "q1_consequence": "source odd cyclicity transports to Gate suspended odd cyclicity of the common q1",
            "green_consequence": "source Lambda_+^sharp=Lambda_- transports to (Lambda'_+)^ddagger=Lambda'_minus",
            "homotopy_consequence": "q' Lambda'_plus/minus+Lambda'_plus/minus q'=I",
            "support_consequence": "T and R are pointwise order-zero involutions and preserve advanced/retarded support",
        },
        "full_carrier_extension": {
            "orthogonal_decomposition_authority": "cyclic_and_formally_self_adjoint P_alg/P_end on 356+30",
            "T_386": "I_356 direct-sum T_30",
            "T_386_positive": full_t.count(1),
            "T_386_negative": full_t.count(-1),
            "T_386_sharp_gate_positive": full_t_sharp.count(1),
            "T_386_sharp_gate_negative": full_t_sharp.count(-1),
            "R_386": "I_356 direct-sum R_30",
            "R_386_positive": full_r.count(1),
            "R_386_negative": full_r.count(-1),
            "R_386_involutive": all(sign * sign == 1 for sign in full_r),
            "full_green_suspended_adjoint_replayed": True,
            "full_component_pairing_coefficients_serialized": False,
        },
        "foundational_strength": {
            "finite_suspension_bridge_base": "PRA",
            "choice_operation_added": False,
            "infinite_selection_added": False,
            "weakest_base_for_imported_analytic_causal_theorem": "NOT_ESTABLISHED",
        },
        "gate_disposition": {
            "endpoint_pairing_sign_resolved_as_convention": True,
            "abstract_full_carrier_suspended_adjoint_replayed": True,
            "full_386_component_pairing_serialized": False,
            "classical_import_gate_a_status": "FAIL_CLOSED",
            "q2_d_same_carrier_established": False,
        },
        "claim_flags": {
            "ENDPOINT_SUSPENSION_CHARACTER_EXACT": True,
            "FULL_386_SUSPENSION_CHARACTER_EXTENDED": True,
            "FULL_386_SUSPENDED_GREEN_ADJOINT_REPLAYED": True,
            "FULL_386_COMPONENT_PAIRING_SERIALIZED_IN_GATE_CONVENTION": False,
            "STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
            "LORENTZIAN_QUANTUM_THEORY": False
        },
        "does_not_establish": [
            "the 356-row component pairing matrix or one accepted common full-carrier hash",
            "a componentwise replay of every nonminimal, auxiliary and mapping-cylinder adjoint row",
            "q2 cyclicity or q2/Green compatibility on the full causal carrier",
            "the local D action or D equivariance on the causal carrier",
            "a passed Gate A, Hadamard state, BRST Ward theorem, positivity result, renormalized Lorentzian product, QME, residual transfer or Lorentzian quantum theory",
            "a weakest-base calibration of the imported analytic causal theorem"
        ],
        "next_gate": "Serialize the 356-row complement pairing and row basis in the Gate suspension convention, bind them to the existing cyclic P_alg/P_end maps, and replay every component adjoint identity. Then add local D and q2 on those same bytes.",
        "canonical_hashes": {},
        "provenance": {"inputs": [{"path": str(path.relative_to(ROOT)), "result_or_schema_id": expected, "sha256": sha(path), "role": role} for path, expected, role in INPUTS]},
        "independent_checker": {"path": "quantum-weyl/classical_import/check_strict_386_suspended_adjoint_bridge.py", "expected_digest": ""},
        "human_report": str(REPORT.relative_to(ROOT)),
    }
    value["canonical_hashes"] = {
        "endpoint_exact_algebra_sha256": digest(value["endpoint_exact_algebra"]),
        "suspended_adjoint_theorem_sha256": digest(value["suspended_adjoint_theorem"]),
        "full_carrier_extension_sha256": digest(value["full_carrier_extension"]),
    }
    value["independent_checker"]["expected_digest"] = digest({key: value[key] for key in ("scope", "endpoint_exact_algebra", "suspended_adjoint_theorem", "full_carrier_extension", "foundational_strength", "gate_disposition", "claim_flags", "does_not_establish", "next_gate", "canonical_hashes")})
    return value


def render(value: dict[str, Any]) -> str:
    endpoint = value["endpoint_exact_algebra"]
    full = value["full_carrier_extension"]
    return f"""# Strict 386-row suspended-adjoint bridge v1

## Outcome

{value['answer']}

## Exact endpoint calculation

- `T = diag(I_5,I_10,I_10,-I_5)`.
- `T^sharp_G = diag(-I_5,I_10,I_10,I_5)`.
- `R=T^sharp_G T = diag(-I_5,I_10,I_10,-I_5)`.
- The exact Gate pairing has **{endpoint['gate_pairing_nonzero_entries']}** nonzero ordered entries in endpoint coordinates.
- `R^2=I` and `[R,T]=0`.

With `A'=TAT` and `A^ddagger=R A^sharp_G R`, exact algebra gives
`(A')^ddagger=T A^sharp T`.  Hence the common Gate q1 is cyclic in the Gate
suspension convention and `(Lambda'_+)^ddagger=Lambda'_-`.

## Full-carrier extension

The cyclic self-adjoint hybrid projector supplies the orthogonal
`356+30` decomposition.  Extending `R` by the identity gives a 386-row
involution with **{full['R_386_positive']} positive** and
**{full['R_386_negative']} negative** signs.  The full Green adjoint theorem
is replayed in this suspended convention.  This is an abstract projector-level
full-carrier theorem: the 356 component pairing coefficients are not yet
serialized.

## Foundational strength

The finite bridge is PRA algebra and adds neither Choice nor an infinite
selection.  It does not calibrate the analytic Green theorem.

## Does not establish

""" + "\n".join(f"- {item}" for item in value["does_not_establish"]) + f"""

## Next gate

{value['next_gate']}
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, report = generated()
    stale = [str(path.relative_to(ROOT)) for path, content in ((RESULT, result), (REPORT, report)) if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("STRICT_386_SUSPENDED_ADJOINT_BRIDGE_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("STRICT_386_SUSPENDED_ADJOINT_BRIDGE_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
