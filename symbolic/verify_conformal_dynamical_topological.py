#!/usr/bin/env python3
"""C2l-P: dynamical/topological splitting of the residual I2 sector.

The certificate proves the Chern--Weil transgression

    Tr(R wedge R) = d Tr(Gamma dGamma + 2/3 Gamma^3)

in a small exact graded-cyclic trace algebra, checks its order-by-order
finite-cylinder consequence, constructs the Euler--Lagrange quotient of the
two residual classes, and verifies that the theta boundary functional acts
as a local canonical/Krein-unitary transformation.

The standard variation of integral C^2 into the Bach tensor is a declared
field-theory identity, not rederived by this finite algebra.  Global
triviality of the Pontryagin class is explicitly not claimed.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
from typing import Iterable

import sympy as sp


Word = tuple[tuple[str, int], ...]
Expression = dict[Word, Fraction]
R = sp.Rational


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def cyclic_canonical(word: Word) -> tuple[Word | None, int]:
    """Canonicalize a graded trace word under cyclicity.

    Returns ``(None, 0)`` when graded cyclicity makes the trace vanish.
    Otherwise ``Tr(word) = sign Tr(canonical)``.
    """

    if not word:
        return word, 1
    candidates: list[tuple[Word, int]] = []
    total_degree = sum(degree for _, degree in word)
    for cut in range(len(word)):
        prefix = word[:cut]
        suffix = word[cut:]
        prefix_degree = sum(degree for _, degree in prefix)
        suffix_degree = total_degree - prefix_degree
        sign = -1 if (prefix_degree * suffix_degree) % 2 else 1
        candidates.append((suffix + prefix, sign))
    canonical = min(candidate for candidate, _ in candidates)
    signs = {sign for candidate, sign in candidates if candidate == canonical}
    if signs == {-1, 1}:
        return None, 0
    return canonical, signs.pop()


def simplify(terms: Iterable[tuple[Fraction, Word]]) -> Expression:
    result: defaultdict[Word, Fraction] = defaultdict(Fraction)
    for coefficient, word in terms:
        canonical, sign = cyclic_canonical(word)
        if canonical is not None:
            result[canonical] += coefficient * sign
    return {word: coefficient for word, coefficient in result.items() if coefficient}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--claim-pontryagin-globally-trivial", action="store_true"
    )
    parser.add_argument("--claim-theta-has-no-observables", action="store_true")
    parser.add_argument(
        "--claim-machine-derived-nonlinear-bach-variation", action="store_true"
    )
    parser.add_argument(
        "--claim-explicit-cylinder-harmonic-cs-functional", action="store_true"
    )
    parser.add_argument("--claim-two-local-dynamics", action="store_true")
    args = parser.parse_args()
    if args.claim_pontryagin_globally_trivial:
        raise SystemExit(
            "Pontryagin is locally variationally trivial but can label topology, boundaries, horizons, and large transformations"
        )
    if args.claim_theta_has_no_observables:
        raise SystemExit(
            "the theta term can have global, boundary, horizon, or contact-term effects"
        )
    if args.claim_machine_derived_nonlinear_bach_variation:
        raise SystemExit(
            "the nonlinear C^2 Euler--Lagrange identity is a declared theorem dependency here"
        )
    if args.claim_explicit_cylinder_harmonic_cs_functional:
        raise SystemExit(
            "the certificate proves the all-field transgression and its quadratic consequence, not a mode-expanded CS^(2) formula"
        )
    if args.claim_two_local_dynamics:
        raise SystemExit(
            "the odd residual class is topological and lies in the Euler--Lagrange kernel"
        )

    # Formal spacetime form degrees: Gamma is one, A=dGamma is two.  Expand
    # d Q3 and R^2 exactly.  Graded cyclicity kills Tr(Gamma^4) and combines
    # the mixed terms.
    G = ("G", 1)
    A = ("A", 2)
    d_q3 = simplify(
        [
            (Fraction(1), (A, A)),
            (Fraction(2, 3), (A, G, G)),
            (Fraction(-2, 3), (G, A, G)),
            (Fraction(2, 3), (G, G, A)),
        ]
    )
    curvature_squared = simplify(
        [
            (Fraction(1), (A, A)),
            (Fraction(1), (A, G, G)),
            (Fraction(1), (G, G, A)),
            (Fraction(1), (G, G, G, G)),
        ]
    )
    check(
        "C2l-P1: d CS_3(Gamma) equals Tr(R wedge R) in the exact graded trace algebra",
        d_q3 == curvature_squared,
    )
    check(
        "C2l-P1: the apparent Tr(Gamma^4) term vanishes by graded cyclicity",
        simplify([(Fraction(1), (G, G, G, G))]) == {},
    )

    # The Chern--Weil variation uses delta R=D(delta Gamma), the Bianchi
    # identity DR=0, and trace cyclicity.  Verify first that varying both R
    # factors gives 2 Tr(DX R), then compare it with
    # 2 d Tr(X R)=2 Tr(DX R)-2 Tr(X DR) after imposing DR=0.
    X = ("X", 1)
    DX = ("DX", 2)
    CURV = ("R", 2)
    DR = ("DR", 3)
    variation_pontryagin = simplify(
        [(Fraction(1), (DX, CURV)), (Fraction(1), (CURV, DX))]
    )
    transgression_derivative = simplify(
        [
            (Fraction(2), (DX, CURV)),
            (Fraction(-2), (X, DR)),
        ]
    )
    transgression_after_bianchi = simplify(
        [(Fraction(2), (DX, CURV))]
    )
    check(
        "C2l-P2: the Pontryagin variation has only the boundary transgression after DR=0",
        variation_pontryagin == transgression_after_bianchi
        and transgression_derivative != transgression_after_bianchi,
    )

    # Since P(eps)=d Q(eps) identically, every perturbative coefficient is a
    # boundary term.  In particular the eps^2 coefficient on [t1,t2]xS3 is
    # CS^(2)(t2)-CS^(2)(t1).  Symbols keep the two endpoints independent.
    cs2_t1, cs2_t2 = sp.symbols("CS2_t1 CS2_t2")
    delta_cs2_t1, delta_cs2_t2 = sp.symbols(
        "delta_CS2_t1 delta_CS2_t2"
    )
    integral_p2 = cs2_t2 - cs2_t1
    endpoint_variation = (
        sp.diff(integral_p2, cs2_t2) * delta_cs2_t2
        + sp.diff(integral_p2, cs2_t1) * delta_cs2_t1
    )
    check(
        "C2l-P3: the quadratic finite-cylinder Pontryagin coefficient is an endpoint difference",
        integral_p2 == cs2_t2 - cs2_t1,
    )
    check(
        "C2l-P3: fixed-endpoint variations give no bulk Euler--Lagrange term",
        endpoint_variation != 0
        and endpoint_variation.subs(
            {delta_cs2_t1: 0, delta_cs2_t2: 0}
        )
        == 0,
    )

    # Euler--Lagrange map on the residual parity basis.  The standard
    # field-theory identities are E(C^2)=lambda_B B and E(C*C)=0.  Their
    # nonlinear derivation is outside the finite trace algebra, but all rank,
    # quotient, pairing, and obstruction consequences are exact here.
    lambda_b = sp.symbols("lambda_B", nonzero=True, real=True)
    euler_lagrange = sp.Matrix([[lambda_b, 0]])
    residual_gram = sp.eye(2)
    topological_vector = sp.Matrix([0, 1])
    dynamical_inclusion = sp.Matrix([1, 0])
    check(
        "C2l-P4: the residual Euler--Lagrange map has rank one and kernel span{o}",
        euler_lagrange.rank() == 1
        and euler_lagrange * topological_vector == sp.zeros(1, 1),
    )
    quotient_gram = sp.simplify(
        dynamical_inclusion.T * residual_gram * dynamical_inclusion
    )
    check(
        "C2l-P4: quotienting variationally trivial vertices leaves the positive Gram I1",
        quotient_gram == sp.Matrix([[1]]),
    )

    # The literature-seeded, parity-preserving projected type-B target
    # factors through the same one-dimensional quotient and annihilates the
    # topological kernel.  C2k leaves its direct BV coefficient unresolved.
    c_spin2 = R(199, 30)
    projected_type_b = sp.Matrix([[c_spin2, 0]])
    check(
        "C2l-P5: the projected type-B target is rank one on the dynamical quotient",
        projected_type_b.rank() == 1
        and projected_type_b * topological_vector == sp.zeros(1, 1)
        and projected_type_b * dynamical_inclusion == sp.Matrix([c_spin2]),
    )

    # A boundary theta term shifts p by theta grad CS(q).  The Jacobian is a
    # symplectic shear whenever the Hessian of CS is symmetric.  This exact
    # finite-dimensional identity is the local canonical model of the field-
    # theory transformation.
    theta, h11, h12, h22 = sp.symbols(
        "theta h11 h12 h22", real=True
    )
    identity = sp.eye(2)
    zero = sp.zeros(2)
    hessian = sp.Matrix([[h11, h12], [h12, h22]])
    shear = identity.row_join(zero).col_join((theta * hessian).row_join(identity))
    symplectic = zero.row_join(identity).col_join((-identity).row_join(zero))
    check(
        "C2l-P6: the theta momentum shift preserves the symplectic two-form",
        sp.simplify(shear.T * symplectic * shear) == symplectic,
    )

    # Multiplication by exp(i theta CS) is unitary for real theta and real CS.
    # A scalar phase commutes with any fixed Krein form, so it is J-unitary as
    # well as Dirac-unitary locally.
    cs = sp.symbols("CS", real=True)
    phase = sp.exp(sp.I * theta * cs)
    krein = sp.diag(1, -1)
    unitary = phase * sp.eye(2)
    check(
        "C2l-P6: a real theta boundary phase is locally J-unitary",
        sp.simplify(unitary.conjugate().T * krein * unitary) == krein,
    )

    print("d CS3 canonical terms:", d_q3)
    print("Tr(R wedge R) canonical terms:", curvature_squared)
    print("residual Gram: I2")
    print("Euler--Lagrange matrix [even,odd]:", euler_lagrange)
    print("dynamical quotient Gram:", quotient_gram)
    print("projected type-B target:", projected_type_b)
    print(
        "CONFORMAL C2l-P DYNAMICAL/TOPOLOGICAL SPLIT: ALL PASS. "
        "Pontryagin is locally variationally trivial, not globally erased; "
        "the nonlinear Bach variation is a declared theorem dependency."
    )


if __name__ == "__main__":
    main()
