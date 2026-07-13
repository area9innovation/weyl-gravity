#!/usr/bin/env python3
"""Closed symbolic-spin harmonic rail for the two EAL tensor structures.

Put ``n=2 J_E`` and ``m=2 J_A``.  Resonance fixes

    p = 2 J_L = n + m - 1.

There are two parity-inequivalent positive-output-chirality products:

* same chirality: ``E_+(n) A_+(m) -> L_+(p)`` for ``n,m>=2``;
* mixed chirality: ``E_+(n) A_-(m) -> L_+(p)`` for ``n>=3,m>=2``.

Each fixed chiral product is multiplicity one, but the nonmaximal SU(2)
factor requires two magnetic products.  This file derives their exact
symbolic Clebsch--Gordan coefficients, gives closed stereographic coordinate
forms for every needed highest/once-lowered harmonic, and checks those forms
against the full Wigner-D/Clebsch--Gordan constructor at finite spins.

The final section records the Jacobi form suggested by the two exact Weyl
curvature seeds.  It proves the *consequence* of that form (endpoint zero),
not the missing generic curvature identity.  The remaining recurrence lemma
is stated explicitly in the output and in ``notes/conformal-eal-generic.md``.
BRST representative independence, SO(4,2) descent, and the global conformal-
charge/linearization-stability audit are separate inputs.
"""

from __future__ import annotations

import sympy as sp
from sympy.physics.wigner import clebsch_gordan

from verify_conformal_quartic_contact import (
    PhysicalMode,
    _load_verified_kernel,
    harmonic,
)


PASS = True


def check(label: str, condition: object) -> None:
    global PASS
    ok = bool(condition)
    print(("[OK ] " if ok else "[FAIL] ") + label)
    PASS = PASS and ok


R = sp.Rational
I = sp.I
HALF = R(1, 2)
n, m = sp.symbols("n m", integer=True, positive=True)
u = sp.symbols("u", real=True)
t = sp.symbols("t", positive=True, real=True)
z = 1 + t**2
sine_beta = 2 * t / z


def same_coefficients(n_value: sp.Expr, m_value: sp.Expr) -> tuple[sp.Expr, sp.Expr]:
    n_value, m_value = sp.sympify(n_value), sp.sympify(m_value)
    denominator = n_value + m_value + 3
    return (
        sp.sqrt((n_value + 2) / denominator),
        -sp.sqrt((m_value + 1) / denominator),
    )


def mixed_coefficients(n_value: sp.Expr, m_value: sp.Expr) -> tuple[sp.Expr, sp.Expr]:
    n_value, m_value = sp.sympify(n_value), sp.sympify(m_value)
    denominator = n_value + m_value - 1
    return (
        sp.sqrt((n_value - 2) / denominator),
        -sp.sqrt((m_value + 1) / denominator),
    )


check(
    "EAL-generic-1: same-chirality CG vector has unit norm symbolically",
    sp.simplify(sum(value**2 for value in same_coefficients(n, m)) - 1) == 0,
)
check(
    "EAL-generic-1: mixed-chirality CG vector has unit norm symbolically",
    sp.simplify(sum(value**2 for value in mixed_coefficients(n, m)) - 1) == 0,
)


def zero_tensor() -> sp.Matrix:
    return sp.zeros(3)


def zero_vector() -> sp.Matrix:
    return sp.zeros(3, 1)


def e_high(n_value: sp.Expr, base: sp.Expr = 1) -> sp.Matrix:
    n_value = sp.sympify(n_value)
    radial = base * z ** (-(n_value - 2) / 2)
    result = zero_tensor()
    result[1, 1] = radial
    result[1, 2] = result[2, 1] = I * sine_beta * radial
    result[2, 2] = -(sine_beta**2) * radial
    return result


def e_left_lowered(n_value: sp.Expr, base: sp.Expr = 1) -> sp.Matrix:
    n_value = sp.sympify(n_value)
    radial = base * z ** (-(n_value - 2) / 2)
    root = sp.sqrt(n_value + 2)
    result = zero_tensor()
    result[0, 1] = result[1, 0] = -2 * I * radial / root
    result[0, 2] = result[2, 0] = 4 * t * radial / (root * z)
    result[1, 1] = (n_value - 2) * t * radial / root
    result[1, 2] = result[2, 1] = (
        2 * I * ((n_value - 1) * t**2 - 1) * radial / (root * z)
    )
    result[2, 2] = (
        -4 * t * (n_value * t**2 - 2) * radial / (root * z**2)
    )
    return result


def e_right_lowered(n_value: sp.Expr, base: sp.Expr = 1) -> sp.Matrix:
    n_value = sp.sympify(n_value)
    return -sp.sqrt(n_value - 2) * t * e_high(n_value, base)


def a_plus_high(m_value: sp.Expr, base: sp.Expr = 1) -> sp.Matrix:
    m_value = sp.sympify(m_value)
    radial = base * z ** (-(m_value - 1) / 2)
    result = zero_vector()
    result[1] = radial
    result[2] = I * sine_beta * radial
    return result


def a_plus_left_lowered(m_value: sp.Expr, base: sp.Expr = 1) -> sp.Matrix:
    m_value = sp.sympify(m_value)
    radial = base * z ** (-(m_value - 1) / 2)
    root = sp.sqrt(m_value + 1)
    result = zero_vector()
    result[0] = -2 * I * radial / root
    result[1] = (m_value - 1) * t * radial / root
    result[2] = 2 * I * (m_value * t**2 - 1) * radial / (root * z)
    return result


def a_minus_high(m_value: sp.Expr, base: sp.Expr = 1) -> sp.Matrix:
    m_value = sp.sympify(m_value)
    radial = base * z ** (-(m_value - 1) / 2)
    result = zero_vector()
    result[0] = I * sine_beta * radial
    result[1] = radial
    return result


def a_minus_right_lowered(m_value: sp.Expr, base: sp.Expr = 1) -> sp.Matrix:
    m_value = sp.sympify(m_value)
    radial = base * z ** (-(m_value - 1) / 2)
    root = sp.sqrt(m_value + 1)
    result = zero_vector()
    result[0] = -2 * I * (m_value * t**2 - 1) * radial / (root * z)
    result[1] = -(m_value - 1) * t * radial / root
    result[2] = 2 * I * radial / root
    return result


def l_bra(n_value: sp.Expr, m_value: sp.Expr, base: sp.Expr = 1) -> sp.Matrix:
    n_value, m_value = sp.sympify(n_value), sp.sympify(m_value)
    # The ket has q tensor q.  The outgoing bra is its complex conjugate.
    radial = base * z ** (-(n_value + m_value - 3) / 2)
    result = zero_tensor()
    result[1, 1] = radial
    result[1, 2] = result[2, 1] = -I * sine_beta * radial
    result[2, 2] = -(sine_beta**2) * radial
    return result


kernel = _load_verified_kernel()
radial_tangent = kernel["radial_tangent"]
radial_root = kernel["radial_root"]
spatial_jacobian = kernel["spatial_jacobian"]
origin_angles = kernel["origin_angles"]


def exact_coordinate(mode: PhysicalMode) -> sp.Matrix:
    ambient = harmonic(kernel, mode)
    if mode.family == "A":
        coordinate = spatial_jacobian.T * ambient
    else:
        coordinate = spatial_jacobian.T * ambient * spatial_jacobian
    return coordinate.applyfunc(
        lambda value: kernel["beta_to_tangent"](value.subs(origin_angles))
    )


def in_constructor_chart(expression: sp.Expr) -> sp.Expr:
    converted = sp.sympify(expression).subs(t, radial_tangent)
    # Compare on the defining positive chart radial_root^2=1+t^2.
    return sp.powsimp(
        converted.subs(radial_root, sp.sqrt(1 + radial_tangent**2)),
        force=True,
    )


def matrices_equal(left: sp.Matrix, right: sp.Matrix) -> bool:
    return all(
        sp.simplify(
            sp.powdenest(
                sp.factor(
                    in_constructor_chart(left[row, column])
                    - in_constructor_chart(right[row, column])
                ),
                force=True,
            )
        )
        == 0
        for row in range(left.rows)
        for column in range(left.cols)
    )


def normalized_bases(n_value: int, m_value: int) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    e_base = sp.sqrt(2 * (n_value - 1)) / (16 * sp.pi)
    a_base = sp.sqrt(m_value) / (4 * sp.pi)
    p_value = n_value + m_value - 1
    l_base = sp.sqrt(2 * (p_value - 1)) / (16 * sp.pi)
    return e_base, a_base, l_base


finite_pairs = ((2, 2), (2, 3), (3, 2), (3, 3), (4, 2))
for n_value, m_value in finite_pairs:
    je = R(n_value, 2)
    ja = R(m_value, 2)
    e_base, a_base, l_base = normalized_bases(n_value, m_value)
    exact_e_high = exact_coordinate(
        PhysicalMode("E", je, 1, je + 1, je - 1)
    )
    exact_e_left = exact_coordinate(
        PhysicalMode("E", je, 1, je, je - 1)
    )
    exact_a_plus_high = exact_coordinate(
        PhysicalMode("A", ja, HALF, ja + HALF, ja - HALF)
    )
    exact_a_plus_left = exact_coordinate(
        PhysicalMode("A", ja, HALF, ja - HALF, ja - HALF)
    )
    exact_l_ket = exact_coordinate(
        PhysicalMode(
            "L",
            R(n_value + m_value - 1, 2),
            1,
            R(n_value + m_value + 1, 2),
            R(n_value + m_value - 3, 2),
        )
    )
    same_matches = {
        "E-high": matrices_equal(exact_e_high, e_high(n_value, e_base)),
        "E-left": matrices_equal(
            exact_e_left, e_left_lowered(n_value, e_base)
        ),
        "A-high": matrices_equal(
            exact_a_plus_high, a_plus_high(m_value, -a_base)
        ),
        "A-left": matrices_equal(
            exact_a_plus_left,
            a_plus_left_lowered(m_value, -a_base),
        ),
        "L-high": matrices_equal(
            exact_l_ket,
            sp.conjugate(l_bra(n_value, m_value, l_base)),
        ),
    }
    check(
        f"EAL-generic-2: same closed harmonics match constructor at n={n_value},m={m_value}",
        all(same_matches.values()),
    )
    if not all(same_matches.values()):
        print("      component matches:", same_matches)

    same_exact = (
        sp.simplify(
            clebsch_gordan(
                je + 1,
                ja + HALF,
                je + ja + HALF,
                je + 1,
                ja - HALF,
                je + ja + HALF,
            )
        ),
        sp.simplify(
            clebsch_gordan(
                je + 1,
                ja + HALF,
                je + ja + HALF,
                je,
                ja + HALF,
                je + ja + HALF,
            )
        ),
    )
    check(
        f"EAL-generic-2: same symbolic CG formula matches constructor at n={n_value},m={m_value}",
        all(
            sp.simplify(actual - expected) == 0
            for actual, expected in zip(
                same_exact, same_coefficients(n_value, m_value)
            )
        ),
    )

    if n_value >= 3:
        exact_e_right = exact_coordinate(
            PhysicalMode("E", je, 1, je + 1, je - 2)
        )
        exact_a_minus_high = exact_coordinate(
            PhysicalMode("A", ja, -HALF, ja - HALF, ja + HALF)
        )
        exact_a_minus_right = exact_coordinate(
            PhysicalMode("A", ja, -HALF, ja - HALF, ja - HALF)
        )
        mixed_matches = {
            "E-right": matrices_equal(
                exact_e_right, e_right_lowered(n_value, e_base)
            ),
            "A-high": matrices_equal(
                exact_a_minus_high, a_minus_high(m_value, a_base)
            ),
            "A-right": matrices_equal(
                exact_a_minus_right,
                a_minus_right_lowered(m_value, a_base),
            ),
        }
        check(
            f"EAL-generic-2: mixed closed harmonics match constructor at n={n_value},m={m_value}",
            all(mixed_matches.values()),
        )
        if not all(mixed_matches.values()):
            print("      component matches:", mixed_matches)
        mixed_exact = (
            sp.simplify(
                clebsch_gordan(
                    je - 1,
                    ja + HALF,
                    je + ja - R(3, 2),
                    je - 1,
                    ja - HALF,
                    je + ja - R(3, 2),
                )
            ),
            sp.simplify(
                clebsch_gordan(
                    je - 1,
                    ja + HALF,
                    je + ja - R(3, 2),
                    je - 2,
                    ja + HALF,
                    je + ja - R(3, 2),
                )
            ),
        )
        check(
            f"EAL-generic-2: mixed symbolic CG formula matches constructor at n={n_value},m={m_value}",
            all(
                sp.simplify(actual - expected) == 0
                for actual, expected in zip(
                    mixed_exact, mixed_coefficients(n_value, m_value)
                )
            ),
        )


# Reverse assembly conjugates every spatial harmonic and negates all compact
# energy and azimuthal weights.  Because the CG coefficients are real, it
# conjugates the projected density without introducing a new intrinsic phase.
same_phases = (
    (
        (-I * n, -I * (n + 2) / 2, -I * (n - 2) / 2),
        (-I * (m + 1), -I * (m - 1) / 2, -I * (m - 1) / 2),
    ),
    (
        (-I * n, -I * n / 2, -I * (n - 2) / 2),
        (-I * (m + 1), -I * (m + 1) / 2, -I * (m - 1) / 2),
    ),
)
mixed_phases = (
    (
        (-I * n, -I * (n + 2) / 2, -I * (n - 2) / 2),
        (-I * (m + 1), -I * (m - 1) / 2, -I * (m - 1) / 2),
    ),
    (
        (-I * n, -I * (n + 2) / 2, -I * (n - 4) / 2),
        (-I * (m + 1), -I * (m - 1) / 2, -I * (m + 1) / 2),
    ),
)
outgoing_phase = (
    I * (n + m + 1),
    I * (n + m + 1) / 2,
    I * (n + m - 3) / 2,
)
check(
    "EAL-generic-3: every same-chirality magnetic component conserves all three weights",
    all(
        all(
            sp.simplify(
                first[index] + second[index] + outgoing_phase[index]
            )
            == 0
            for index in range(3)
        )
        for first, second in same_phases
    ),
)
check(
    "EAL-generic-3: every mixed-chirality magnetic component conserves all three weights",
    all(
        all(
            sp.simplify(
                first[index] + second[index] + outgoing_phase[index]
            )
            == 0
            for index in range(3)
        )
        for first, second in mixed_phases
    ),
)


# Candidate universal radial lemma.  The two exact curvature seeds give
# alpha=0 for n=m=2 (same chirality) and alpha=1 for n=3,m=2 (mixed).
# Both are instances of alpha=n+m-4.
alpha_weight = n + m - 4
P1 = sp.expand_func(sp.jacobi(1, alpha_weight, 0, 2 * u - 1))
jacobi_target = (1 - u) ** alpha_weight * P1
primitive = -u * (1 - u) ** (alpha_weight + 1)
check(
    "EAL-generic-4: candidate Jacobi target has the exact endpoint primitive",
    sp.simplify(
        sp.powsimp(
            (sp.diff(primitive, u) - jacobi_target)
            / (1 - u) ** alpha_weight,
            force=True,
        )
    )
    == 0,
)
r_n, r_m = sp.symbols("r_n r_m", integer=True, nonnegative=True)
same_admissible = primitive.subs({n: r_n + 2, m: r_m + 2})
mixed_admissible = primitive.subs({n: r_n + 3, m: r_m + 2})
check(
    "EAL-generic-4: candidate primitive vanishes for every admissible same and mixed spin",
    sp.limit(same_admissible, u, 0, dir="+") == 0
    and sp.limit(same_admissible, u, 1, dir="-") == 0
    and sp.limit(mixed_admissible, u, 0, dir="+") == 0
    and sp.limit(mixed_admissible, u, 1, dir="-") == 0,
)
check(
    "EAL-generic-4: candidate target reproduces both exact seed Jacobi weights",
    sp.expand(jacobi_target.subs({n: 2, m: 2}) - (2 * u - 1)) == 0
    and sp.expand(
        jacobi_target.subs({n: 3, m: 2}) - (1 - u) * (3 * u - 1)
    )
    == 0,
)

print("Same-chirality symbolic CG coefficients:", same_coefficients(n, m))
print("Mixed-chirality symbolic CG coefficients:", mixed_coefficients(n, m))
print("Candidate common measured Jacobi factor:", jacobi_target, "du")
print("Candidate endpoint primitive:", primitive)
print(
    "OPEN RECURRENCE LEMMA: after CG projection, direct Weyl curvature must "
    "equal an orbit-dependent spin coefficient times this Jacobi factor."
)
print(
    "OPEN DESCENT LEMMA: extend the normalizable highest-weight metric-mode "
    "identity through SO(4,2), parity, BRST-representative changes, and the "
    "global conformal-charge constraint."
)

if not PASS:
    raise SystemExit("CONFORMAL GENERIC EAL HARMONICS: FAIL")

print("CONFORMAL GENERIC EAL HARMONICS: ALL PASS")
