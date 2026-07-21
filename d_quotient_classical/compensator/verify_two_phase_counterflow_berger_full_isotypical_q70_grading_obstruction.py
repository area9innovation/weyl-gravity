#!/usr/bin/env python3
"""Independent replay of the full-isotypical q70 grading obstruction."""

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
CERTIFICATE = HERE / "TWO_PHASE_COUNTERFLOW_BERGER_FULL_ISOTYPICAL_Q70_GRADING_OBSTRUCTION_V1.json"
PAYLOAD = HERE / "TWO_PHASE_COUNTERFLOW_BERGER_FULL_ISOTYPICAL_Q70_GRADING_OBSTRUCTION_PAYLOAD_V1.json"
CERTIFICATE_SCHEMA = HERE / "schema/two-phase-counterflow-berger-full-isotypical-q70-grading-obstruction-v1.schema.json"
PAYLOAD_SCHEMA = HERE / "schema/two-phase-counterflow-berger-full-isotypical-q70-grading-obstruction-payload-v1.schema.json"
Q54 = ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json"
PARENT = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _finite_q54(record: dict[str, object], two_j: int, z: sp.Symbol) -> sp.MutableSparseMatrix:
    n = two_j + 1
    spatial = generators(two_j)
    u = 3 * sp.sqrt(10) / 20
    v = 2 * sp.sqrt(10) / 3
    result = sp.MutableSparseMatrix(54 * n, 54 * n, {})
    for row, column, terms in record["entries"]:
        block = sp.zeros(n)
        for exponents, raw in terms:
            operator = sp.eye(n) * z ** exponents[0]
            for axis in range(3):
                operator *= spatial[axis] ** exponents[axis + 1]
            coefficient = sp.sympify(
                raw, locals={"u": u, "v": v, "alpha_B": sp.Integer(1)}
            )
            block += coefficient * operator
        for i in range(n):
            for j in range(n):
                if block[i, j] != 0:
                    result[row * n + i, column * n + j] = sp.expand(block[i, j])
    return result


def _cross_m_pairing(q54: dict[str, object], two_j: int) -> sp.MutableSparseMatrix:
    n = two_j + 1
    j = sp.Rational(two_j, 2)
    weights = [-j + index for index in range(n)]
    conjugation = sp.zeros(n)
    m = j
    for column, k in enumerate(weights):
        conjugation[n - 1 - column, column] = (-1) ** int(m - k)
    result = sp.MutableSparseMatrix(54 * n, 54 * n, {})
    for row, column, terms in q54["contraction"]["cyclic_pairing"]["entries"]:
        coefficient = sp.sympify(terms[0][1])
        for i in range(n):
            for j_index in range(n):
                if conjugation[i, j_index] != 0:
                    result[row * n + i, column * n + j_index] = (
                        coefficient * conjugation[i, j_index]
                    )
    return result


def _check_finite_wigner(q54: dict[str, object]) -> None:
    z = sp.Symbol("z", real=True)
    q = _finite_q54(q54["classical_unary_q1"]["matrix"], 1, z)
    square = q * q
    if any(sp.simplify(value) != 0 for value in square.todok().values()):
        raise AssertionError("finite two_j=1 q54 square failed")
    pairing = _cross_m_pairing(q54, 1)
    cyclic = q.subs(z, -z).T * pairing + pairing * q
    if any(sp.simplify(value) != 0 for value in cyclic.todok().values()):
        raise AssertionError("finite cross-m cyclicity failed")


def _check_ladder_connectivity() -> None:
    for two_j in range(1, 7):
        n = two_j + 1
        e1, e2, _ = generators(two_j)
        adjacency = {index: set() for index in range(n)}
        for operator in (e1, e2):
            for row in range(n):
                for column in range(n):
                    if operator[row, column] != 0:
                        adjacency[row].add(column)
                        adjacency[column].add(row)
        reached = {0}
        frontier = [0]
        while frontier:
            node = frontier.pop()
            for target in adjacency[node] - reached:
                reached.add(target)
                frontier.append(target)
        if reached != set(range(n)):
            raise AssertionError(f"k-weight graph disconnected at two_j={two_j}")
        # Connectedness is the truncation-boundary mutation: every proper
        # nonempty subset has an e1/e2 edge to its complement.
        for mask in range(1, (1 << n) - 1):
            subset = {index for index in range(n) if mask & (1 << index)}
            if not any(adjacency[node] - subset for node in subset):
                raise AssertionError(f"proper k truncation closed at two_j={two_j}")


def _check_u1(parent: dict[str, object]) -> None:
    extension = parent["u1_minimal_nonminimal_extension"]
    names = extension["changed_basis_order"]
    ranks = extension["changed_basis_component_ranks"]
    ghost = [0, 1, -1, 0, -2, -1, -1, 0, -1, 0]
    degrees = [-value for value in ghost]
    q = sp.zeros(16)
    s = sp.zeros(16)
    offsets = []
    offset = 0
    for rank in ranks:
        offsets.append(offset)
        offset += rank
    for entry in extension["Q_changed_basis"]["entries"]:
        row, column = entry["row"], entry["column"]
        coefficient = sp.Rational(entry["coefficient"])
        if degrees[row] - degrees[column] != -1:
            raise AssertionError("serialized U1 arrow is not uniformly degree -1")
        for component in range(ranks[row]):
            q[offsets[row] + component, offsets[column] + component] = coefficient
    for entry in extension["S_changed_basis"]["entries"]:
        row, column = entry["row"], entry["column"]
        coefficient = sp.Rational(entry["coefficient"])
        for component in range(ranks[row]):
            s[offsets[row] + component, offsets[column] + component] = coefficient
    if q * q != sp.zeros(16) or q * s + s * q != sp.eye(16):
        raise AssertionError("serialized U1 algebraic contraction failed")
    repaired_q = q.T
    repaired_s = s.T
    if repaired_q * repaired_q != sp.zeros(16):
        raise AssertionError("transpose repair lost nilpotency")
    if repaired_q * repaired_s + repaired_s * repaired_q != sp.eye(16):
        raise AssertionError("transpose repair lost contraction")
    for row, column in repaired_q.todok():
        row_multiplet = max(index for index, start in enumerate(offsets) if start <= row)
        column_multiplet = max(index for index, start in enumerate(offsets) if start <= column)
        if degrees[row_multiplet] - degrees[column_multiplet] != 1:
            raise AssertionError("transpose repair is not degree +1")

    # Reconstruct the canonical changed-basis odd pairing.  The relative
    # signs of chi--H and c--c* are fixed by cyclicity; the vector and
    # nonminimal canonical pairs use their row-name duals.
    omega = sp.zeros(16)
    pairs = [
        (offsets[0], offsets[5], 1),
        (offsets[1], offsets[4], -1),
        *[(offsets[3] + i, offsets[2] + i, 1) for i in range(4)],
        (offsets[6], offsets[9], 1),
        (offsets[7], offsets[8], 1),
    ]
    for left, right, sign in pairs:
        omega[left, right] = sign
        omega[right, left] = -sign
    if omega.rank() != 16:
        raise AssertionError("reconstructed U1 pairing is degenerate")
    if repaired_q.T * omega + omega * repaired_q != sp.zeros(16):
        raise AssertionError("transpose repair is not cyclic")
    if "bar_c-b_star" not in extension["cyclic_pairing"]:
        raise AssertionError("parent pairing text mutation was not detected")
    if names[8] != "b_star" or names[9] != "bar_c_star":
        raise AssertionError("nonminimal row names drifted")


def main() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    q54 = json.loads(Q54.read_text())
    parent = json.loads(PARENT.read_text())
    Draft202012Validator(json.loads(CERTIFICATE_SCHEMA.read_text())).validate(certificate)
    Draft202012Validator(json.loads(PAYLOAD_SCHEMA.read_text())).validate(payload)
    if certificate["payload_ref"]["sha256"] != _sha(PAYLOAD):
        raise AssertionError("payload hash mismatch")
    if payload["content_sha256"] != _digest(
        {key: value for key, value in payload.items() if key != "content_sha256"}
    ):
        raise AssertionError("payload content digest mismatch")
    row_degrees = {
        row["index"]: row["degree"] for row in q54["row_layout"]["component_rows"]
    }
    shifts = [
        row_degrees[row] - row_degrees[column]
        for row, column, _ in q54["classical_unary_q1"]["matrix"]["entries"]
    ]
    if len(shifts) != 309 or set(shifts) != {1}:
        raise AssertionError("independent q54 grading replay failed")
    _check_u1(parent)
    _check_ladder_connectivity()
    _check_finite_wigner(q54)
    if certificate["terminal_verdict"]["graded_q70_import"] != "OBSTRUCTED":
        raise AssertionError("obstruction verdict dropped")
    print("independent full-isotypical q70 grading obstruction: PASS")


if __name__ == "__main__":
    main()
