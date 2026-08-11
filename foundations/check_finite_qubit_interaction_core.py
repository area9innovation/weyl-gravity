#!/usr/bin/env python3
"""Independent exact checker for the finite qubit interaction core.

All scalar arithmetic is Gaussian rational arithmetic.  The one time value used
for the entanglement witness is represented by the unnormalised phase vector
and an exact rational density matrix, so no trigonometric or floating-point
library enters the certificate.
"""
from __future__ import annotations

from fractions import Fraction as Q
import hashlib
import json
from typing import Iterable

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


def scale(a: G, q: Q) -> G:
    return a[0] * q, a[1] * q


def matrix(rows: Iterable[Iterable[int | G]]) -> Matrix:
    return [[x if isinstance(x, tuple) else g(x) for x in row] for row in rows]


def eye(n: int) -> Matrix:
    return [[ONE if i == j else ZERO for j in range(n)] for i in range(n)]


def madd(a: Matrix, b: Matrix) -> Matrix:
    return [[add(x, y) for x, y in zip(rx, ry)] for rx, ry in zip(a, b)]


def mneg(a: Matrix) -> Matrix:
    return [[neg(x) for x in row] for row in a]


def mscale(a: Matrix, z: G) -> Matrix:
    return [[mul(z, x) for x in row] for row in a]


def mmul(a: Matrix, b: Matrix) -> Matrix:
    return [[sum_g(mul(a[i][k], b[k][j]) for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]


def adjoint(a: Matrix) -> Matrix:
    return [[conj(a[j][i]) for j in range(len(a))] for i in range(len(a[0]))]


def trace(a: Matrix) -> G:
    return sum_g(a[i][i] for i in range(len(a)))


def sum_g(values: Iterable[G]) -> G:
    out = ZERO
    for value in values:
        out = add(out, value)
    return out


def kron(a: Matrix, b: Matrix) -> Matrix:
    return [[mul(a[i // len(b)][j // len(b[0])], b[i % len(b)][j % len(b[0])])
             for j in range(len(a[0]) * len(b[0]))]
            for i in range(len(a) * len(b))]


def outer(v: list[G]) -> Matrix:
    return [[mul(v[i], conj(v[j])) for j in range(len(v))] for i in range(len(v))]


def partial_trace_second(rho: Matrix) -> Matrix:
    return [[sum_g(rho[2 * a + b][2 * c + b] for b in range(2)) for c in range(2)] for a in range(2)]


def commutator(a: Matrix, b: Matrix) -> Matrix:
    return madd(mmul(a, b), mneg(mmul(b, a)))


def delta(h: Matrix, a: Matrix) -> Matrix:
    return mscale(commutator(h, a), I)


def j_adjoint(j: Matrix, a: Matrix) -> Matrix:
    return mmul(mmul(j, adjoint(a)), j)


def scalar_text(z: G) -> str:
    def q(x: Q) -> str:
        return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    return f"{q(z[0])}{'+' if z[1] >= 0 else ''}{q(z[1])}i"


def digest_payload(payload: object) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def check() -> tuple[list[str], dict[str, object]]:
    errors: list[str] = []
    i2 = eye(2)
    x = matrix([[0, 1], [1, 0]])
    z = matrix([[1, 0], [0, -1]])
    h = kron(z, z)
    a, b = kron(x, i2), kron(i2, x)
    i4 = eye(4)

    if mmul(h, h) != i4 or adjoint(h) != h:
        errors.append("interaction Hamiltonian")
    if commutator(a, b) != matrix([[0] * 4 for _ in range(4)]):
        errors.append("separate-subsystem commutation")
    if delta(h, mmul(a, b)) != madd(mmul(delta(h, a), b), mmul(a, delta(h, b))):
        errors.append("Leibniz rule")
    if delta(h, adjoint(a)) != adjoint(delta(h, a)):
        errors.append("star derivation")

    bell = [[scale(x, Q(1, 2)) for x in row] for row in outer([ONE, ZERO, ZERO, ONE])]
    p00 = matrix([[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
    parity_even = matrix([[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 1]])
    if trace(bell) != ONE or mmul(bell, bell) != bell or trace(mmul(bell, p00)) != g(Q(1, 2)):
        errors.append("Bell state/Born probability")
    if trace(mmul(bell, parity_even)) != ONE:
        errors.append("parity probability")

    # At t=pi/4, exp(-it Z tensor Z)|++><++|exp(it Z tensor Z).
    # The common sqrt(2) denominator is absorbed into the density factor 1/8.
    phases = [g(1, -1), g(1, 1), g(1, 1), g(1, -1)]
    evolved = [[scale(x, Q(1, 8)) for x in row] for row in outer(phases)]
    reduced = partial_trace_second(evolved)
    if trace(evolved) != ONE or mmul(evolved, evolved) != evolved:
        errors.append("exact evolved pure state")
    if reduced != matrix([[(g(Q(1, 2))), 0], [0, g(Q(1, 2))]]):
        errors.append("entanglement reduced state")

    j = matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, -1, 0], [0, 0, 0, -1]])
    if mmul(j, j) != i4 or adjoint(j) != j or j_adjoint(j, h) != h:
        errors.append("Krein fundamental symmetry")
    # The diagonal phase vector defines U(pi/4) up to the common sqrt(2).
    u_scaled = matrix([[phases[i] if i == k else ZERO for k in range(4)] for i in range(4)])
    if mmul(j_adjoint(j, u_scaled), u_scaled) != mscale(i4, g(2)):
        errors.append("scaled J-unitarity")

    payload = {
        "field": "Q(i)",
        "dimension": 4,
        "hamiltonian_diagonal": [scalar_text(h[i][i]) for i in range(4)],
        "born_p00": scalar_text(trace(mmul(bell, p00))),
        "born_even": scalar_text(trace(mmul(bell, parity_even))),
        "reduced_state": [[scalar_text(x) for x in row] for row in reduced],
        "delta_a": [[scalar_text(x) for x in row] for row in delta(h, a)],
        "j_signature": [2, 2],
        "checks": [
            "H*=H and H^2=1",
            "commuting subsystem observables",
            "exact star derivation and Leibniz rule",
            "positive normalized pure density matrices",
            "exact Born probabilities",
            "interaction produces a maximally mixed one-qubit reduction",
            "J*=J, J^2=1, H^sharp=H, and scaled J-unitarity",
        ],
    }
    return errors, {**payload, "digest": digest_payload(payload)}


def main() -> int:
    errors, summary = check()
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
