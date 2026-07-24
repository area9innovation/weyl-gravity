"""Independent exact linear-algebra helpers for the pullback theorem."""

from __future__ import annotations

import sympy as sp


def adjoint(matrix: sp.Matrix) -> sp.Matrix:
    return matrix.conjugate().T


def is_hermitian(matrix: sp.Matrix) -> bool:
    return sp.simplify(matrix - adjoint(matrix)) == sp.zeros(*matrix.shape)


def inertia_from_eigenvalues(matrix: sp.Matrix) -> tuple[int, int, int]:
    """Return exact Hermitian inertia for the small rational fixtures."""
    if not is_hermitian(matrix):
        raise ValueError("matrix is not Hermitian")
    pos = neg = zero = 0
    for value, multiplicity in matrix.eigenvals().items():
        value = sp.simplify(value)
        if value.is_positive:
            pos += multiplicity
        elif value.is_negative:
            neg += multiplicity
        elif value.is_zero:
            zero += multiplicity
        else:
            raise ValueError(f"undecidable exact eigenvalue sign: {value}")
    return pos, neg, zero


def criterion_fixture(kind: str) -> dict[str, object]:
    """Construct exact passing and adversarial three-dimensional fixtures."""
    if kind == "positive":
        G = sp.diag(1, -1, -1)
        L = sp.diag(sp.Rational(1, 4), sp.Rational(1, 2), sp.Rational(3, 4))
        C = G
    elif kind == "negative_eigenvalue":
        G = sp.diag(1, -1, -1)
        L = sp.diag(-sp.Rational(1, 4), sp.Rational(1, 2), sp.Rational(3, 4))
        C = G
    elif kind == "nonreal_pair":
        G = sp.Matrix([[0, 1, 0], [1, 0, 0], [0, 0, -1]])
        L = sp.diag(sp.I, -sp.I, sp.Rational(1, 2))
        C = sp.diag(1, 1, -1)
    elif kind == "jordan":
        G = sp.Matrix([[0, 1, 0], [1, 0, 0], [0, 0, -1]])
        L = sp.Matrix(
            [
                [sp.Rational(1, 2), 1, 0],
                [0, sp.Rational(1, 2), 0],
                [0, 0, sp.Rational(3, 4)],
            ]
        )
        C = sp.diag(1, 1, -1)
    else:
        raise ValueError(kind)

    KH = sp.simplify(G * L)
    Kplus = sp.simplify(G - KH)
    H0 = sp.simplify(G * C)
    return {
        "G": G,
        "L": L,
        "KH": KH,
        "Kplus": Kplus,
        "C": C,
        "G_hermitian": is_hermitian(G),
        "KH_hermitian": is_hermitian(KH),
        "Kplus_hermitian": is_hermitian(Kplus),
        "L_G_self_adjoint": sp.simplify(adjoint(L) * G - G * L)
        == sp.zeros(3),
        "L_diagonalizable": sum(L.eigenvals().values()) == 3
        and sum(len(basis) for _value, _multiplicity, basis in L.eigenvects())
        == 3,
        "spectrum": [sp.sstr(v) for v in L.eigenvals()],
        "H0_inertia": inertia_from_eigenvalues(H0)
        if is_hermitian(H0)
        else None,
        "KH_C_inertia": inertia_from_eigenvalues(sp.simplify(KH * C))
        if is_hermitian(sp.simplify(KH * C))
        else None,
        "Kplus_C_inertia": inertia_from_eigenvalues(sp.simplify(Kplus * C))
        if is_hermitian(sp.simplify(Kplus * C))
        else None,
    }


def determinant_identity() -> str:
    return (
        "det(L_H)=abs(det(A))^2*det(H_H)/det(G); "
        "no endpoint determinant ratio may be dropped"
    )
