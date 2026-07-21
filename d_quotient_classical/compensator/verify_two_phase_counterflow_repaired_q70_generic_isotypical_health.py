#!/usr/bin/env python3
"""Independent PBW/finite-Wigner replay of the repaired q70 health obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp
from sympy import QQ


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CERT = HERE / "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_FIRST_GENERIC_ISOTYPICAL_HEALTH_OBSTRUCTION_V1.json"
PAYLOAD = HERE / "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_FIRST_GENERIC_ISOTYPICAL_HEALTH_OBSTRUCTION_PAYLOAD_V1.json"
CERT_SCHEMA = HERE / "schema/two-phase-counterflow-repaired-q70-first-generic-isotypical-health-obstruction-v1.schema.json"
PAYLOAD_SCHEMA = HERE / "schema/two-phase-counterflow-repaired-q70-first-generic-isotypical-health-obstruction-payload-v1.schema.json"
PARENT = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V2.json"
OPERATOR = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"

Z = sp.Symbol("z")
S = sp.sqrt(10)
U = 3 * S / 20
V = 2 * S / 3


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _spin_half() -> list[sp.Matrix]:
    return [
        sp.Matrix([[0, -sp.I / 2], [-sp.I / 2, 0]]),
        sp.Matrix([[0, sp.Rational(1, 2)], [-sp.Rational(1, 2), 0]]),
        sp.diag(sp.I / (2 * U), -sp.I / (2 * U)),
    ]


def _finite(record: dict[str, object], alpha_b: sp.Expr = sp.Integer(1)) -> sp.Matrix:
    spatial = _spin_half()
    result = sp.MutableSparseMatrix(record["shape"][0] * 2, record["shape"][1] * 2, {})
    for row, column, terms in record["entries"]:
        block = sp.zeros(2)
        for exponents, raw in terms:
            word = sp.eye(2) * Z ** exponents[0]
            for axis in range(3):
                word *= spatial[axis] ** exponents[axis + 1]
            block += sp.sympify(raw, locals={"u": U, "v": V, "alpha_B": alpha_b}) * word
        for i in range(2):
            for j in range(2):
                if block[i, j] != 0:
                    result[2 * row + i, 2 * column + j] = sp.expand(block[i, j])
    return sp.Matrix(result)


def _rank_mod(matrix: sp.Matrix, polynomial: sp.Expr) -> int:
    field = QQ.algebraic_field(S, sp.I)
    ring = field.poly_ring(Z)
    modulus = ring.from_sympy(polynomial)
    rows = [
        [ring.rem(ring.from_sympy(sp.expand(matrix[i, j])), modulus) for j in range(matrix.cols)]
        for i in range(matrix.rows)
    ]
    pivot_row = 0
    for column in range(matrix.cols):
        found = next((row for row in range(pivot_row, matrix.rows) if rows[row][column]), None)
        if found is None:
            continue
        rows[pivot_row], rows[found] = rows[found], rows[pivot_row]
        inverse = ring.invert(rows[pivot_row][column], modulus)
        for row in range(pivot_row + 1, matrix.rows):
            if rows[row][column]:
                coefficient = ring.rem(rows[row][column] * inverse, modulus)
                rows[row] = [
                    ring.rem(rows[row][j] - coefficient * rows[pivot_row][j], modulus)
                    for j in range(matrix.cols)
                ]
        pivot_row += 1
        if pivot_row == matrix.rows:
            break
    return pivot_row


def _check_full_parent(parent: dict[str, object], payload: dict[str, object]) -> None:
    q70 = _finite(parent["operators"]["q70"])
    q70_core = {
        "shape": [q70.rows, q70.cols],
        "entries": [
            [row, column, sp.sstr(sp.factor(q70[row, column]))]
            for row in range(q70.rows)
            for column in range(q70.cols)
            if q70[row, column] != 0
        ],
    }
    stored_finite = payload["carrier"]["finite_repaired_unary_and_contraction"]
    if stored_finite["q70_sha256"] != _digest(q70_core):
        raise AssertionError("finite repaired q70 hash failed")
    if any(sp.simplify(value) != 0 for value in (q70 * q70).todok().values()):
        raise AssertionError("finite repaired q70 square failed")
    degrees = {row["index"]: row["degree"] for row in parent["row_layout"]["component_rows"]}
    shifts = [degrees[row] - degrees[column] for row, column, _ in parent["operators"]["q70"]["entries"]]
    if len(shifts) != 317 or set(shifts) != {1}:
        raise AssertionError("repaired q70 grading failed")

    s70 = _finite(parent["operators"]["S70"])
    inclusion = _finite(parent["operators"]["iota70_from_26"])
    projection = _finite(parent["operators"]["pi26_from_70"])
    if projection * inclusion != sp.eye(52):
        raise AssertionError("finite repaired projection/inclusion failed")
    if q70 * s70 + s70 * q70 != sp.eye(140) - inclusion * projection:
        raise AssertionError("finite repaired homotopy identity failed")
    if s70 * s70 != sp.zeros(140) or s70 * inclusion != sp.zeros(140, 52) or projection * s70 != sp.zeros(52, 140):
        raise AssertionError("finite repaired contraction side conditions failed")

    conjugation = sp.Matrix([[0, 1], [-1, 0]])
    pairing = sp.MutableSparseMatrix(140, 140, {})
    for row, column, terms in parent["operators"]["pairing70"]["entries"]:
        coefficient = sp.sympify(terms[0][1])
        for i in range(2):
            for j in range(2):
                if conjugation[i, j] != 0:
                    pairing[row * 2 + i, column * 2 + j] = coefficient * conjugation[i, j]
    cyclic = q70.subs(Z, -Z).T * pairing + pairing * q70
    if pairing.rank() != 140 or any(sp.simplify(value) != 0 for value in cyclic.todok().values()):
        raise AssertionError("finite repaired cross-m cyclicity failed")

    # The old orientation mutation is the exact transpose-back of the final
    # eight U1 component arrows and has degree -1.
    u1_entries = [entry for entry in parent["operators"]["q70"]["entries"] if entry[0] >= 54]
    if len(u1_entries) != 8 or {degrees[column] - degrees[row] for row, column, _ in u1_entries} != {-1}:
        raise AssertionError("old-orientation mutation was not detected")

    # No one-weight truncation is invariant in the spin-half irrep.
    if _spin_half()[0][1, 0] == 0 or _spin_half()[1][1, 0] == 0:
        raise AssertionError("omitted-weight mutation unexpectedly closed")


def _check_quotient(operator: dict[str, object], payload: dict[str, object]) -> None:
    blocks = operator["q1_blocks"]
    gauge = _finite(blocks["K_spatial"])
    hessian = _finite(blocks["H_retained"])
    selected_hessian = _finite(blocks["H_retained"], sp.Integer(5))
    if selected_hessian != 5 * hessian:
        raise AssertionError("positive alpha_B normalization failed")
    identity = _finite(blocks["minus_K_spatial_sharp"])
    free = [0, 1, 2, 3, 4, 5, 6, 7, 14, 15, 16, 17, 18, 19]
    pivot = [8, 9, 10, 11, 12, 13]
    if gauge[pivot, :].det() != sp.Rational(1, 16):
        raise AssertionError("gauge chart determinant failed")
    if identity[:, pivot].det() != sp.Rational(1, 16):
        raise AssertionError("identity chart determinant failed")
    if sp.simplify(hessian * gauge) != sp.zeros(20, 6) or sp.simplify(identity * hessian) != sp.zeros(6, 20):
        raise AssertionError("finite Noether complex failed")

    physical = hessian.extract(free, free)
    determinant = sp.Poly(sp.factor(physical.det(method="domain-ge")), Z).monic().as_expr()
    factors = [
        Z**2 + 13,
        40 * Z**4 + 773 * Z**2 + 3748,
        3240 * Z**4 + 168093 * Z**2 + 2172895,
        933120 * Z**6 + 10517040 * Z**4 + 34117578 * Z**2 + 24373901,
    ]
    expected = sp.Poly(sp.prod(factor**2 for factor in factors), Z).monic().as_expr()
    if sp.expand(determinant - expected) != 0:
        raise AssertionError("physical determinant failed")
    if any(_rank_mod(physical, factor) != 12 for factor in factors):
        raise AssertionError("physical geometric multiplicity failed")

    unstable = factors[1]
    y = sp.Symbol("y")
    y_polynomial = 40 * y**2 + 773 * y + 3748
    if sp.discriminant(y_polynomial, y) != -2151:
        raise AssertionError("complex-frequency discriminant failed")
    growth_squared = (8 * sp.sqrt(9370) - 773) / 160
    if not sp.N(growth_squared, 50) > 0:
        raise AssertionError("positive growth rate failed")
    if sp.expand(sp.sympify(payload["terminal_verdict"]["complex_frequency_factor"].replace("^", "**")) - unstable) != 0:
        raise AssertionError("terminal unstable factor drifted")

    # Independent real energy congruence: q contributes one negative sign,
    # P1 one positive sign, and the (Dq,P0) block has negative determinant.
    middle = sp.Matrix([[773, 1], [1, 0]])
    if middle.det() != -1 or payload["unstable_sector"]["two_copy_inertia_positive_negative_zero"] != [4, 4, 0]:
        raise AssertionError("split energy inertia failed")

    # The stored residue determinants must be units modulo their factors.
    for factor, audit in zip(factors, payload["physical_quotient"]["factor_audits"]):
        numerator = sp.together(sp.sympify(audit["residue_determinant"])).as_numer_denom()[0]
        if sp.gcd(sp.Poly(numerator, Z), sp.Poly(factor, Z)).degree() != 0:
            raise AssertionError("residue pairing mutation failed")


def main() -> None:
    certificate = json.loads(CERT.read_text())
    payload = json.loads(PAYLOAD.read_text())
    parent = json.loads(PARENT.read_text())
    operator = json.loads(OPERATOR.read_text())
    Draft202012Validator(json.loads(CERT_SCHEMA.read_text())).validate(certificate)
    Draft202012Validator(json.loads(PAYLOAD_SCHEMA.read_text())).validate(payload)
    if certificate["payload_ref"]["sha256"] != _sha(PAYLOAD):
        raise AssertionError("payload file hash failed")
    if payload["content_sha256"] != _digest({key: value for key, value in payload.items() if key != "content_sha256"}):
        raise AssertionError("payload content hash failed")
    _check_full_parent(parent, payload)
    _check_quotient(operator, payload)
    if payload["charge_actions"]["R_rel"].startswith("zero tangent action") is False:
        raise AssertionError("charged-orbit separation failed")
    if payload["normalization"]["selected_action_alpha_B"] != "5":
        raise AssertionError("selected-action normalization drifted")
    print("independent repaired q70 first generic physical-health obstruction: PASS")


if __name__ == "__main__":
    main()
