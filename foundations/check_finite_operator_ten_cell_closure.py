#!/usr/bin/env python3
"""Independently rederive the exact witnesses used by the ten-cell closure."""
from __future__ import annotations

from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "foundations/results/FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1.json"
BORN = ROOT / "foundations/results/FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1.json"

G = tuple[Q, Q]
Matrix = list[list[G]]


def g(real: int | Q = 0, imag: int | Q = 0) -> G:
    return Q(real), Q(imag)


ZERO, ONE, I = g(), g(1), g(0, 1)


def add(a: G, b: G) -> G:
    return a[0] + b[0], a[1] + b[1]


def neg(a: G) -> G:
    return -a[0], -a[1]


def mul(a: G, b: G) -> G:
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def conj(a: G) -> G:
    return a[0], -a[1]


def sum_g(values: Iterable[G]) -> G:
    out = ZERO
    for value in values:
        out = add(out, value)
    return out


def matrix(rows: Iterable[Iterable[int | G]]) -> Matrix:
    return [[x if isinstance(x, tuple) else g(x) for x in row] for row in rows]


def eye(n: int) -> Matrix:
    return [[ONE if i == j else ZERO for j in range(n)] for i in range(n)]


def mmul(a: Matrix, b: Matrix) -> Matrix:
    return [[sum_g(mul(a[i][k], b[k][j]) for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]


def madd(a: Matrix, b: Matrix) -> Matrix:
    return [[add(x, y) for x, y in zip(rx, ry)] for rx, ry in zip(a, b)]


def mscale(a: Matrix, z: G) -> Matrix:
    return [[mul(z, x) for x in row] for row in a]


def adjoint(a: Matrix) -> Matrix:
    return [[conj(a[j][i]) for j in range(len(a))] for i in range(len(a[0]))]


def trace(a: Matrix) -> G:
    return sum_g(a[i][i] for i in range(len(a)))


def kron(a: Matrix, b: Matrix) -> Matrix:
    return [[mul(a[i // len(b)][j // len(b[0])], b[i % len(b)][j % len(b[0])])
             for j in range(len(a[0]) * len(b[0]))]
            for i in range(len(a) * len(b))]


def outer(v: list[G]) -> Matrix:
    return [[mul(v[i], conj(v[j])) for j in range(len(v))] for i in range(len(v))]


def partial_trace_second(rho: Matrix) -> Matrix:
    return [[sum_g(rho[2 * a + b][2 * c + b] for b in range(2)) for c in range(2)] for a in range(2)]


def commutator(a: Matrix, b: Matrix) -> Matrix:
    return madd(mmul(a, b), mscale(mmul(b, a), g(-1)))


def j_adjoint(j: Matrix, a: Matrix) -> Matrix:
    return mmul(mmul(j, adjoint(a)), j)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def qtext(value: Q) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def digest_payload(payload: object) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def check() -> tuple[list[str], dict[str, object]]:
    errors: list[str] = []
    i2 = eye(2)
    pauli = {
        "I": i2,
        "X": matrix([[0, 1], [1, 0]]),
        "Y": matrix([[0, g(0, -1)], [g(0, 1), 0]]),
        "Z": matrix([[1, 0], [0, -1]]),
    }
    words = {(a, b): kron(pauli[a], pauli[b]) for a in pauli for b in pauli}

    gram = [[trace(mmul(adjoint(a), b)) for b in words.values()] for a in words.values()]
    if any(gram[r][c] != (g(4) if r == c else ZERO) for r in range(16) for c in range(16)):
        errors.append("Pauli Hilbert--Schmidt basis")

    h, observable = words[("Z", "Z")], words[("X", "I")]
    expected_delta = mscale(words[("Y", "Z")], g(-2))
    if mscale(commutator(h, observable), I) != expected_delta:
        errors.append("nonzero interaction derivation")

    phases = [g(1, -1), g(1, 1), g(1, 1), g(1, -1)]
    rho = [[mscale(outer(phases), g(Q(1, 8)))[r][c] for c in range(4)] for r in range(4)]
    reduced = partial_trace_second(rho)
    if trace(rho) != ONE or mmul(rho, rho) != rho or reduced != matrix([[g(Q(1, 2)), 0], [0, g(Q(1, 2))]]):
        errors.append("exact entangling output")

    j = words[("Z", "I")]
    if mmul(j, j) != eye(4) or j_adjoint(j, h) != h:
        errors.append("Krein realization")

    parity = words[("Z", "Z")]
    even = [f"{a} tensor {b}" for (a, b), word in words.items() if mmul(parity, word) == mmul(word, parity)]
    expected_even = ["I tensor I", "I tensor Z", "X tensor X", "X tensor Y", "Y tensor X", "Y tensor Y", "Z tensor I", "Z tensor Z"]
    if sorted(even) != sorted(expected_even) or len(even) != 8:
        errors.append("parity commutant basis")

    phases_allowed = {g(1), g(-1), g(0, 1), g(0, -1)}
    products = 0
    for left in words.values():
        for right in words.values():
            product = mmul(left, right)
            matches = sum(product == mscale(word, phase) for word in words.values() for phase in phases_allowed)
            if matches != 1:
                errors.append("Pauli product closure")
                break
            products += 1

    # Reconstruct the certified finite Krein-corner fixture over Q.
    j3 = matrix([[1, 0, 0], [0, 1, 0], [0, 0, -1]])
    s = matrix([[g(Q(3, 5)), g(Q(-4, 5)), 0], [g(Q(4, 5)), g(Q(3, 5)), 0], [0, 0, 1]])
    pin = matrix([[1, 0, 0], [0, 0, 0], [0, 0, 0]])
    outputs = [matrix([[1, 0, 0], [0, 0, 0], [0, 0, 0]]), matrix([[0, 0, 0], [0, 1, 0], [0, 0, 0]]), matrix([[0, 0, 0], [0, 0, 0], [0, 0, 1]])]
    if mmul(j3, j3) != eye(3) or j_adjoint(j3, s) != adjoint(s):
        # S commutes with J, hence S^sharp=S*=S^{-1}.
        errors.append("finite-corner Krein fixture")
    evolved = mmul(mmul(s, pin), adjoint(s))
    probabilities = [trace(mmul(p, evolved))[0] for p in outputs]
    if probabilities != [Q(9, 25), Q(16, 25), Q(0)] or sum(probabilities) != 1:
        errors.append("finite-corner probabilities")

    expected_coordinates = [
        ("CLASSICAL_STANDARD", "HILBERT_OPERATOR", "INTERACTION_CONSTRUCTION"),
        ("CONSTRUCTIVE_COMPUTABLE", "HILBERT_OPERATOR", "INTERACTION_CONSTRUCTION"),
        ("FINITE_DISCRETE", "HILBERT_OPERATOR", "INTERACTION_CONSTRUCTION"),
        ("WEAK_CHOICE_ZF", "HILBERT_OPERATOR", "INTERACTION_CONSTRUCTION"),
        ("CLASSICAL_STANDARD", "KREIN_INDEFINITE", "INTERACTION_CONSTRUCTION"),
        ("WEAK_CHOICE_ZF", "KREIN_INDEFINITE", "INTERACTION_CONSTRUCTION"),
        ("CONSTRUCTIVE_COMPUTABLE", "KREIN_INDEFINITE", "STATE_REPRESENTATION"),
        ("CONSTRUCTIVE_COMPUTABLE", "KREIN_INDEFINITE", "PROBABILITY_RULE"),
        ("FINITE_DISCRETE", "HILBERT_OPERATOR", "COUNTERTERM_CLASSIFICATION"),
        ("FINITE_DISCRETE", "HILBERT_OPERATOR", "RENORMALIZED_PRODUCTS"),
    ]
    payload = {
        "source_hashes": {str(CORE.relative_to(ROOT)): sha(CORE), str(BORN.relative_to(ROOT)): sha(BORN)},
        "coordinates": [list(item) for item in expected_coordinates],
        "pauli_basis_dimension": len(words),
        "gram_diagonal": 4,
        "interaction_derivation": "-2 Y tensor Z",
        "reduced_density": "I/2",
        "krein_h_sharp": "H",
        "parity_even_basis": sorted(even),
        "products_checked": products,
        "probabilities": [qtext(x) for x in probabilities],
        "status_split": {"LOCAL_RESULT": 9, "PIECES_ONLY": 1},
    }
    return errors, {**payload, "digest": digest_payload(payload)}


def main() -> int:
    errors, summary = check()
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
