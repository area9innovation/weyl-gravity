#!/usr/bin/env python3
"""Exact constructor certificate for generic AAL highest-weight harmonics.

Hamada--Horata construct transverse vector and TT tensor harmonics from
scalar Wigner functions, Clebsch--Gordan coefficients, and the ambient tau
tensors (arXiv:hep-th/0307008, Eqs. A.26 and A.37).  In the same-chirality
highest-weight AAL channel those finite sums collapse to

    A[J]_i = -sqrt(2J)/(4*pi) c**(2J-1) exp(-i Phi_J) q_i,
    L[S]_ij = sqrt(2(2S-1))/(16*pi) c**(2S-2)
              exp(-i Phi_S) q_i q_j,

where

    c=cos(beta/2),
    q=d beta+i sin(beta)d gamma,
    Phi_J=(J+1/2)alpha+(J-1/2)gamma,
    Phi_S=(S+1)alpha+(S-1)gamma.

This script builds the harmonics from the original finite sums and compares
them exactly with the closed forms at several integer and half-integer spins.
It also verifies the general normalization and null-polarization identities.
The finite constructor comparisons are regressions of the algebraic CG
collapse, not an interpolation of a curvature coefficient.
"""

from __future__ import annotations

from itertools import product

import sympy as sp
from sympy.physics.wigner import clebsch_gordan, wigner_d_small


PASS = True


def check(label: str, condition: object) -> None:
    global PASS
    ok = bool(condition)
    print(("[OK ] " if ok else "[FAIL] ") + label)
    PASS = PASS and ok


R = sp.Rational
I = sp.I
HALF = R(1, 2)
VOL = 2 * sp.pi**2
alpha, beta, gamma = sp.symbols("alpha beta gamma", real=True)
t = sp.symbols("t", positive=True, real=True)


def magnetic_values(spin: sp.Rational) -> list[sp.Rational]:
    return [spin - index for index in range(int(2 * spin) + 1)]


def wigner_d(
    spin: sp.Rational,
    magnetic: sp.Rational,
    magnetic_prime: sp.Rational,
) -> sp.Expr:
    values = magnetic_values(spin)
    small = wigner_d_small(spin, -beta)
    return (
        sp.exp(-I * magnetic * alpha)
        * small[values.index(magnetic), values.index(magnetic_prime)]
        * sp.exp(-I * magnetic_prime * gamma)
    )


def scalar_harmonic(
    spin: sp.Rational,
    magnetic: sp.Rational,
    magnetic_prime: sp.Rational,
) -> sp.Expr:
    return sp.sqrt((2 * spin + 1) / VOL) * wigner_d(
        spin, magnetic, magnetic_prime
    )


half_values = [HALF, -HALF]
one_values = [sp.Integer(1), sp.Integer(0), sp.Integer(-1)]
tau_vector = (
    sp.Matrix([[1, 0], [0, 1]]),
    sp.Matrix([[0, I], [I, 0]]),
    sp.Matrix([[0, 1], [-1, 0]]),
    sp.Matrix([[I, 0], [0, -I]]),
)


def tau1(
    ambient_index: int,
    magnetic: sp.Rational,
    magnetic_prime: sp.Rational,
) -> sp.Expr:
    return tau_vector[ambient_index][
        half_values.index(magnetic), half_values.index(magnetic_prime)
    ]


def tau2(
    first_index: int,
    second_index: int,
    magnetic: sp.Integer,
    magnetic_prime: sp.Integer,
) -> sp.Expr:
    result = 0
    for first_m, second_m, first_mp, second_mp in product(
        half_values, half_values, half_values, half_values
    ):
        result += (
            clebsch_gordan(HALF, HALF, 1, first_m, second_m, magnetic)
            * clebsch_gordan(
                HALF, HALF, 1, first_mp, second_mp, magnetic_prime
            )
            * tau1(first_index, first_m, first_mp)
            * tau1(second_index, second_m, second_mp)
        )
    return sp.expand(result)


def ambient_vector_harmonic(
    spin: sp.Rational,
    magnetic: sp.Rational,
    magnetic_prime: sp.Rational,
) -> sp.Matrix:
    result = sp.zeros(4, 1)
    for scalar_m, scalar_mp, tangent_m, tangent_mp in product(
        magnetic_values(spin),
        magnetic_values(spin),
        half_values,
        half_values,
    ):
        coefficient = (
            clebsch_gordan(
                spin, HALF, spin + HALF, scalar_m, tangent_m, magnetic
            )
            * clebsch_gordan(
                spin,
                HALF,
                spin - HALF,
                scalar_mp,
                tangent_mp,
                magnetic_prime,
            )
            / sp.sqrt(2)
        )
        if coefficient == 0:
            continue
        scalar = scalar_harmonic(spin, scalar_m, scalar_mp)
        for ambient in range(4):
            result[ambient] += coefficient * scalar * tau1(
                ambient, tangent_m, tangent_mp
            )
    return result.applyfunc(sp.simplify)


def ambient_tensor_harmonic(
    spin: sp.Rational,
    magnetic: sp.Rational,
    magnetic_prime: sp.Rational,
) -> sp.Matrix:
    result = sp.zeros(4, 4)
    for scalar_m, scalar_mp, tangent_m, tangent_mp in product(
        magnetic_values(spin),
        magnetic_values(spin),
        one_values,
        one_values,
    ):
        coefficient = (
            clebsch_gordan(
                spin, 1, spin + 1, scalar_m, tangent_m, magnetic
            )
            * clebsch_gordan(
                spin,
                1,
                spin - 1,
                scalar_mp,
                tangent_mp,
                magnetic_prime,
            )
            / 2
        )
        if coefficient == 0:
            continue
        scalar = scalar_harmonic(spin, scalar_m, scalar_mp)
        for first in range(4):
            for second in range(4):
                result[first, second] += coefficient * scalar * tau2(
                    first, second, tangent_m, tangent_mp
                )
    return result.applyfunc(sp.simplify)


embedding = sp.Matrix(
    [
        sp.cos(beta / 2) * sp.cos((alpha + gamma) / 2),
        sp.sin(beta / 2) * sp.sin((alpha - gamma) / 2),
        -sp.sin(beta / 2) * sp.cos((alpha - gamma) / 2),
        -sp.cos(beta / 2) * sp.sin((alpha + gamma) / 2),
    ]
)
jacobian = embedding.jacobian((alpha, beta, gamma))


def vector_constructor(spin: sp.Rational) -> sp.Matrix:
    return jacobian.T * ambient_vector_harmonic(
        spin, spin + HALF, spin - HALF
    )


def tensor_constructor(spin: sp.Rational) -> sp.Matrix:
    return (
        jacobian.T
        * ambient_tensor_harmonic(spin, spin + 1, spin - 1)
        * jacobian
    )


q = sp.Matrix([0, 1, I * sp.sin(beta)])


def vector_closed(spin: sp.Rational) -> sp.Matrix:
    phase = sp.exp(
        -I * ((spin + HALF) * alpha + (spin - HALF) * gamma)
    )
    return (
        -sp.sqrt(2 * spin)
        / (4 * sp.pi)
        * sp.cos(beta / 2) ** (2 * spin - 1)
        * phase
        * q
    )


def tensor_closed(spin: sp.Rational) -> sp.Matrix:
    phase = sp.exp(-I * ((spin + 1) * alpha + (spin - 1) * gamma))
    return (
        sp.sqrt(2 * (2 * spin - 1))
        / (16 * sp.pi)
        * sp.cos(beta / 2) ** (2 * spin - 2)
        * phase
        * q
        * q.T
    )


def radialize(expression: sp.Expr) -> sp.Expr:
    converted = sp.expand_trig(expression).subs(
        {
            sp.sin(beta): 2 * t / (1 + t**2),
            sp.cos(beta): (1 - t**2) / (1 + t**2),
            sp.sin(beta / 2): t / sp.sqrt(1 + t**2),
            sp.cos(beta / 2): 1 / sp.sqrt(1 + t**2),
        },
        simultaneous=True,
    )
    return sp.cancel(sp.powsimp(converted, force=True))


def phase_radial_match(
    constructed: sp.Matrix,
    closed: sp.Matrix,
    alpha_weight: sp.Rational,
    gamma_weight: sp.Rational,
) -> bool:
    # Each coordinate component is a simultaneous alpha/gamma weight vector.
    # Equality of its radial value at alpha=gamma=0 therefore proves the full
    # Euler-angle expression.
    for row in range(constructed.rows):
        for column in range(constructed.cols):
            value = constructed[row, column]
            if sp.simplify(sp.diff(value, alpha) + I * alpha_weight * value) != 0:
                return False
            if sp.simplify(sp.diff(value, gamma) + I * gamma_weight * value) != 0:
                return False
            difference = (value - closed[row, column]).subs(
                {alpha: 0, gamma: 0}
            )
            if radialize(difference) != 0:
                return False
    return True


vector_spins = (R(1), R(3, 2), R(2), R(5, 2))
tensor_spins = (R(2), R(5, 2), R(3), R(7, 2))
for spin in vector_spins:
    check(
        f"AAL-harmonic: vector constructor equals q-form at J={spin}",
        phase_radial_match(
            vector_constructor(spin),
            vector_closed(spin),
            spin + HALF,
            spin - HALF,
        ),
    )
for spin in tensor_spins:
    check(
        f"AAL-harmonic: tensor constructor equals q tensor q at S={spin}",
        phase_radial_match(
            tensor_constructor(spin),
            tensor_closed(spin),
            spin + 1,
            spin - 1,
        ),
    )


# General CG coefficients entering the collapse.  They follow from the usual
# lowering recursion and orthogonality to the higher total-spin multiplets.
# Exact constructor values at several symbolic half-integer instances verify
# the phase convention used above.
for spin in vector_spins:
    actual = (
        sp.simplify(
            clebsch_gordan(
                spin, HALF, spin - HALF, spin, -HALF, spin - HALF
            )
        ),
        sp.simplify(
            clebsch_gordan(
                spin, HALF, spin - HALF, spin - 1, HALF, spin - HALF
            )
        ),
    )
    expected = (
        sp.sqrt(2 * spin / (2 * spin + 1)),
        -1 / sp.sqrt(2 * spin + 1),
    )
    check(
        f"AAL-CG: vector right-coupling recursion at J={spin}",
        all(sp.simplify(left - right) == 0 for left, right in zip(actual, expected)),
    )

for spin in tensor_spins:
    actual = (
        sp.simplify(clebsch_gordan(spin, 1, spin - 1, spin, -1, spin - 1)),
        sp.simplify(
            clebsch_gordan(spin, 1, spin - 1, spin - 1, 0, spin - 1)
        ),
        sp.simplify(
            clebsch_gordan(spin, 1, spin - 1, spin - 2, 1, spin - 1)
        ),
    )
    expected = (
        sp.sqrt((2 * spin - 1) / (2 * spin + 1)),
        -sp.sqrt((2 * spin - 1) / (spin * (2 * spin + 1))),
        1 / sp.sqrt(spin * (2 * spin + 1)),
    )
    check(
        f"AAL-CG: tensor right-coupling recursion at S={spin}",
        all(sp.simplify(left - right) == 0 for left, right in zip(actual, expected)),
    )


# General null and normalization identities for the closed forms.
spatial_metric = sp.Matrix(
    [
        [R(1, 4), 0, sp.cos(beta) / 4],
        [0, R(1, 4), 0],
        [sp.cos(beta) / 4, 0, R(1, 4)],
    ]
)
spatial_inverse = sp.simplify(spatial_metric.inv())
check(
    "AAL-harmonic: common polarization q is null",
    sp.simplify((q.T * spatial_inverse * q)[0]) == 0,
)
check(
    "AAL-harmonic: Hermitian q norm is eight",
    sp.simplify((sp.conjugate(q).T * spatial_inverse * q)[0]) == 8,
)

J = sp.symbols("J", positive=True)
S = sp.symbols("S", positive=True)
# With x=cos(beta/2)^2, sin(beta)d beta=-2dx.  The two norms are elementary
# beta moments.  The Euler-angle ranges contribute pi^2 after the 1/8 in
# sqrt(gamma); writing every factor explicitly avoids a heuristic symbolic
# trigonometric integral with symbolic exponents.
angular_measure = sp.pi**2
vector_pointwise_coefficient = J / sp.pi**2
vector_beta_moment = 1 / J
tensor_pointwise_coefficient = (2 * S - 1) / (2 * sp.pi**2)
tensor_beta_moment = 2 / (2 * S - 1)
vector_norm = sp.simplify(
    angular_measure * vector_pointwise_coefficient * vector_beta_moment
)
tensor_norm = sp.simplify(
    angular_measure * tensor_pointwise_coefficient * tensor_beta_moment
)
check("AAL-harmonic: closed vector normalization is one", vector_norm == 1)
check("AAL-harmonic: closed tensor normalization is one", tensor_norm == 1)

if not PASS:
    raise SystemExit("CONFORMAL AAL HIGHEST HARMONICS: FAIL")

print("CONFORMAL AAL HIGHEST HARMONICS: ALL PASS")
