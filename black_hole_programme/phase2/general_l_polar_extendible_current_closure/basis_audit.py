"""Congruence audit for admissible Einstein lifts of the extra complement."""
from __future__ import annotations

import json
from pathlib import Path

import sympy as sp

PKG = Path(__file__).resolve().parent
ART = PKG / "current_artifacts"
OUT = ART / "basis-lift-congruence.json"
NAMES = ("E", "X0", "X1", "X2")
L, W = sp.symbols("Lambda omega", real=True)


def numerator(left: str, right: str, power: int = 0) -> sp.Expr:
    data = json.loads((ART / f"oscillatory-{left}-{right}.json").read_text())
    layer = data["result"]["layers"].get(str(power))
    if layer is None:
        return sp.Integer(0)
    return sum(
        sp.sympify(coefficient, locals={"I": sp.I}) * L**monomial[0] * W**monomial[1]
        for monomial, coefficient in layer["sparse_terms"]
    )


def denominator(name: str) -> sp.Expr:
    data = json.loads((ART / f"oscillatory-{name}-{name}.json").read_text())
    return sp.sympify(data["profile_common_denominators"][name], locals={"Lambda": L, "omega": W, "I": sp.I})


def main() -> None:
    # Verify the abstract block formula without using any current artifact.
    a = sp.Matrix(1, 3, sp.symbols("a0:3"))
    b = sp.Matrix(3, 1, sp.symbols("b0:3"))
    k = sp.Matrix(3, 3, sp.symbols("k0:9"))
    c = sp.Matrix(1, 3, sp.symbols("c0:3"))
    s = sp.eye(4)
    for j in range(3):
        s[0, j + 1] = c[j]
    g = sp.zeros(4)
    g[0, 1:] = a
    g[1:, 0] = b
    g[1:, 1:] = k
    transformed = sp.expand(s.conjugate().T * g * s)
    expected_k = k + c.conjugate().T*a + b*c
    if transformed[0, 1:] != a or transformed[1:, 1:] != expected_k:
        raise RuntimeError("abstract lift-congruence formula failed")

    # Exact rational fixture: this shows that complement data change although
    # the full rank, radical dimension, and Einstein cross covector do not.
    probe = {L: sp.Integer(6), W: sp.Rational(3, 5)}
    ds = [denominator(name).subs(probe) for name in NAMES]
    matrix = sp.Matrix(
        4,
        4,
        lambda i, j: sp.cancel(
            numerator(NAMES[i], NAMES[j]).subs(probe)
            / (ds[i] * sp.conjugate(ds[j]))
        ),
    )
    shear = sp.eye(4)
    for j, value in enumerate((1, 2, -1), start=1):
        shear[0, j] = value
    changed = sp.simplify(shear.conjugate().T * matrix * shear)
    if matrix.rank() != changed.rank() or len(matrix.nullspace()) != len(changed.nullspace()):
        raise RuntimeError("full congruence invariants changed")
    if matrix[0, 1:] != changed[0, 1:]:
        raise RuntimeError("Einstein cross covector changed under Einstein lift")
    if matrix[1:, 1:] == changed[1:, 1:]:
        raise RuntimeError("negative-control lift failed to change the raw XX block")
    if matrix[1:, 1:].det() == changed[1:, 1:].det():
        raise RuntimeError("negative-control lift failed to change detK")

    output = {
        "schema_version": "polar-basis-lift-congruence-v1",
        "abstract_identity": {
            "basis_change": "X' = X + E*c",
            "shear": "S=[[1,c],[0,I3]]",
            "current": "G'=S^dagger*G*S",
            "extra_block": "K'=K+c^dagger*a+b*c when G_EE=0",
            "einstein_cross_covector": "a'=a",
            "verified": True,
        },
        "exact_probe": {
            "Lambda": 6,
            "omega": "3/5",
            "shear_c": [1, 2, -1],
            "rank_before": matrix.rank(),
            "rank_after": changed.rank(),
            "radical_dimension_before": len(matrix.nullspace()),
            "radical_dimension_after": len(changed.nullspace()),
            "raw_extra_block_changed": matrix[1:, 1:] != changed[1:, 1:],
            "raw_detK_changed": matrix[1:, 1:].det() != changed[1:, 1:].det(),
            "einstein_cross_covector_unchanged": matrix[0, 1:] == changed[0, 1:],
        },
        "invariant_ledger": {
            "invariant": [
                "full current rank",
                "full radical dimension",
                "filtered finite-line dimension",
                "nonvanishing of the Einstein cross covector",
            ],
            "lift_sensitive": [
                "raw XX entries",
                "chosen-complement detK and its factorization",
                "coordinates of the mixed radical",
                "a sign assigned to one chosen extra lift",
            ],
        },
    }
    OUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(OUT)


if __name__ == "__main__":
    main()
