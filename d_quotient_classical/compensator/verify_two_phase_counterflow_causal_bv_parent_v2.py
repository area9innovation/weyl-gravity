#!/usr/bin/env python3
"""Independent action/cotangent replay of the repaired q70 V2 parent."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from closed_universe_observers.generate_berger_peter_weyl_form_laplacian import generators


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V2.json"
PAYLOAD = HERE / "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V2.json"
RECEIVER = HERE / "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_RECEIVER_CONTRACT_V2.json"
SCHEMAS = (
    HERE / "schema/two-phase-counterflow-causal-bv-parent-v2.schema.json",
    HERE / "schema/two-phase-counterflow-causal-bv-parent-payload-v2.schema.json",
    HERE / "schema/two-phase-counterflow-causal-bv-receiver-contract-v2.schema.json",
)
Q54 = ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json"
PARENT_V1_PAYLOAD = HERE / "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _record_hash(record: dict[str, object]) -> str:
    return _digest({"shape": record["shape"], "entries": record["entries"]})


def _constant_matrix(record: dict[str, object], row_start: int, row_stop: int, column_start: int, column_stop: int) -> sp.Matrix:
    result = sp.zeros(row_stop - row_start, column_stop - column_start)
    for row, column, terms in record["entries"]:
        if row_start <= row < row_stop and column_start <= column < column_stop:
            if len(terms) != 1 or terms[0][0] != [0, 0, 0, 0]:
                raise AssertionError("expected algebraic matrix entry")
            result[row - row_start, column - column_start] = sp.Rational(terms[0][1])
    return result


def _derive_u1_from_action(parent_v1: dict[str, object]) -> tuple[sp.Matrix, sp.Matrix, sp.Matrix, list[int]]:
    rows = {row["id"]: row for row in parent_v1["u1_minimal_nonminimal_extension"]["original_rows"]}
    expected = {
        "chi": (0, "c_U1"),
        "c_U1": (1, "0"),
        "A": (0, "d c_U1"),
        "A_star": (-1, "-4(A-dchi)"),
        "chi_star": (-1, "4 delta(A-dchi)"),
        "c_U1_star": (-2, "chi_star+delta A_star"),
        "bar_c": (-1, "b"),
        "b": (0, "0"),
        "b_star": (-1, "-bar_c_star"),
        "bar_c_star": (0, "0"),
    }
    for name, (ghost, image) in expected.items():
        if rows[name]["ghost_number"] != ghost or rows[name]["Q_image"] != image:
            raise AssertionError(f"action row drifted: {name}")

    # Changed component order: chi,c,A*0..3,B0..3,c*,H,barc,b,b*,barc*.
    q = sp.zeros(16)
    s = sp.zeros(16)
    omega = sp.zeros(16)
    for row, column, coefficient in ((0, 1, 1), (2, 6, -4), (3, 7, -4), (4, 8, -4), (5, 9, -4), (10, 11, 1), (12, 13, 1), (14, 15, -1)):
        q[row, column] = coefficient
    for row, column, coefficient in ((1, 0, 1), (6, 2, -sp.Rational(1, 4)), (7, 3, -sp.Rational(1, 4)), (8, 4, -sp.Rational(1, 4)), (9, 5, -sp.Rational(1, 4)), (11, 10, 1), (13, 12, 1), (15, 14, -1)):
        s[row, column] = coefficient
    for left, right, coefficient in ((0, 11, 1), (1, 10, -1), (6, 2, 1), (7, 3, 1), (8, 4, 1), (9, 5, 1), (12, 15, 1), (13, 14, 1)):
        omega[left, right] = coefficient
        omega[right, left] = -coefficient
    degrees = [0, -1, 1, 1, 1, 1, 0, 0, 0, 0, 2, 1, 1, 0, 1, 0]
    return q, s, omega, degrees


def _finite_q54(q54: dict[str, object], two_j: int, z: sp.Symbol) -> sp.MutableSparseMatrix:
    n = two_j + 1
    spatial = generators(two_j)
    u = 3 * sp.sqrt(10) / 20
    v = 2 * sp.sqrt(10) / 3
    result = sp.MutableSparseMatrix(54 * n, 54 * n, {})
    for row, column, terms in q54["classical_unary_q1"]["matrix"]["entries"]:
        block = sp.zeros(n)
        for exponents, raw in terms:
            operator = sp.eye(n) * z ** exponents[0]
            for axis in range(3):
                operator *= spatial[axis] ** exponents[axis + 1]
            block += sp.sympify(raw, locals={"u": u, "v": v, "alpha_B": 1}) * operator
        for i in range(n):
            for j in range(n):
                if block[i, j] != 0:
                    result[row * n + i, column * n + j] = sp.expand(block[i, j])
    return result


def _check_mutations(q: sp.Matrix, s: sp.Matrix, omega: sp.Matrix, degrees: list[int]) -> None:
    old = q.T
    old_shifts = {degrees[row] - degrees[column] for row, column in old.todok()}
    if old_shifts != {-1}:
        raise AssertionError("old orientation mutation was not rejected")
    missing = q.copy()
    missing[0, 1] = 0
    if missing * s + s * missing == sp.eye(16):
        raise AssertionError("one-arrow mutation passed contraction")
    pairing_sign = omega.copy()
    pairing_sign[1, 10] *= -1
    pairing_sign[10, 1] *= -1
    if q.T * pairing_sign + pairing_sign * q == sp.zeros(16):
        raise AssertionError("pairing-sign mutation passed cyclicity")
    degree_mutation = list(degrees)
    degree_mutation[0] = -1
    if all(degree_mutation[row] - degree_mutation[column] == 1 for row, column in q.todok()):
        raise AssertionError("degree mutation passed")
    contraction_mutation = s.copy()
    contraction_mutation[6, 2] = -sp.Rational(1, 5)
    if q * contraction_mutation + contraction_mutation * q == sp.eye(16):
        raise AssertionError("contraction mutation passed")


def main() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    receiver = json.loads(RECEIVER.read_text())
    q54 = json.loads(Q54.read_text())
    parent_v1 = json.loads(PARENT_V1_PAYLOAD.read_text())
    for schema_path, value in zip(SCHEMAS, (certificate, payload, receiver), strict=True):
        schema = json.loads(schema_path.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(value)
    if certificate["payload_ref"]["sha256"] != _sha(PAYLOAD) or certificate["receiver_ref"]["sha256"] != _sha(RECEIVER):
        raise AssertionError("V2 child hash mismatch")
    if payload["content_sha256"] != _digest({key: value for key, value in payload.items() if key != "content_sha256"}):
        raise AssertionError("V2 payload content hash mismatch")
    if receiver["content_sha256"] != _digest({key: value for key, value in receiver.items() if key != "content_sha256"}):
        raise AssertionError("V2 receiver content hash mismatch")
    for record in payload["operators"].values():
        if record["sha256"] != _record_hash(record):
            raise AssertionError("operator record hash mismatch")

    q, s, omega, degrees = _derive_u1_from_action(parent_v1)
    if q * q != sp.zeros(16) or q * s + s * q != sp.eye(16):
        raise AssertionError("independent repaired contraction failed")
    if omega.rank() != 16 or q.T * omega + omega * q != sp.zeros(16):
        raise AssertionError("independent repaired cyclicity failed")
    if s.T * omega + omega * s != sp.zeros(16):
        raise AssertionError("independent repaired homotopy cyclicity failed")
    if _constant_matrix(payload["operators"]["q70"], 54, 70, 54, 70) != q:
        raise AssertionError("serialized q16 differs from action derivation")
    if _constant_matrix(payload["operators"]["S70"], 54, 70, 54, 70) != s:
        raise AssertionError("serialized S16 differs from action derivation")
    if _constant_matrix(payload["operators"]["pairing70"], 54, 70, 54, 70) != omega:
        raise AssertionError("serialized pairing16 differs from canonical derivation")
    _check_mutations(q, s, omega, degrees)

    row_degrees = {row["index"]: row["degree"] for row in payload["row_layout"]["component_rows"]}
    shifts = [row_degrees[row] - row_degrees[column] for row, column, _ in payload["operators"]["q70"]["entries"]]
    if len(shifts) != 317 or set(shifts) != {1}:
        raise AssertionError("full q70 degree replay failed")
    if payload["operators"]["q70"]["entries"][:309] != q54["classical_unary_q1"]["matrix"]["entries"]:
        raise AssertionError("q54 block was changed during repair")
    if any(row >= 54 for row, _, _ in payload["operators"]["iota70_from_26"]["entries"]):
        raise AssertionError("contractible U1 row entered retained inclusion")
    if any(column >= 54 for _, column, _ in payload["operators"]["pi26_from_70"]["entries"]):
        raise AssertionError("contractible U1 row survived retained projection")

    # Method-distinct finite representation: exact q54 Wigner block plus the
    # algebraic q16 tensor identity.  Cross terms vanish by direct sum.
    z = sp.Symbol("z", real=True)
    q54_mode = _finite_q54(q54, 1, z)
    if any(sp.simplify(value) != 0 for value in (q54_mode * q54_mode).todok().values()):
        raise AssertionError("finite q54 mode square failed")
    q16_mode = sp.kronecker_product(q, sp.eye(2))
    if q16_mode * q16_mode != sp.zeros(32):
        raise AssertionError("finite repaired U1 mode square failed")

    if receiver["stale_hash_policy"]["V1_q2_or_receiver_hashes"] != "REJECT_FOR_V2_CLAIMS":
        raise AssertionError("stale receiver/q2 policy dropped")
    if certificate["terminal_verdict"]["physical_quotient_status"] != "OPEN":
        raise AssertionError("physical quotient was silently promoted")
    print("independent repaired graded-cyclic q70 parent: PASS")


if __name__ == "__main__":
    main()
