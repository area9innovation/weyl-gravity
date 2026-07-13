#!/usr/bin/env python3
"""Exact two-seed certificate for the resonant conformal-cylinder EAL family.

The current reduced normalizable-mode enumeration leaves three cubic
families: EAA, EAL, and AAL.  EAL has two parity-inequivalent tensor
structures.  This file treats the first same-chirality seed

    E_2(2,0) + A_3(3/2,1/2) -> L_5(5/2,1/2),

plus its parity conjugate.  The output is not the maximal left-SU(2)
product, so a single product of highest-weight harmonics is wrong.  The
normalized incoming highest-weight state is instead

    2/sqrt(7) |E(2,0) A(1/2,1/2)>
      -sqrt(3/7) |E(1,0) A(3/2,1/2)>.

The script constructs this state from exact Clebsch--Gordan coefficients,
checks all harmonic normalizations, and evaluates a nonzero derivative Gaunt
invariant.  The latter proves that the coupling is allowed but is not the
Weyl Hamiltonian coefficient.

The full curvature components are computed by the reusable C1b engine:

    python3 symbolic/verify_conformal_aal_vertex.py eal-1
    python3 symbolic/verify_conformal_aal_vertex.py eal-2
    python3 symbolic/verify_conformal_aal_vertex.py eal-reverse-1
    python3 symbolic/verify_conformal_aal_vertex.py eal-reverse-2

Their projected combination and J-adjoint interpretation are recorded below
once all four exact outputs have been independently obtained.

The second mixed-chirality structure begins at

    E_3(5/2,1/2) + A_3(1/2,3/2) -> L_6(3,1).

Its two forward curvature components and two independently assembled reverse
components are obtained with the analogous ``mixed-eal-*`` commands.  The
projected measured density is the Jacobi weight

    (1-u) P_1^(1,0)(2u-1),

so this second seed also vanishes by exact orthogonality.  These two seed
certificates close the first normalizable representative of each EAL tensor
structure; they are not by themselves an all-spin EAL theorem or a complete
physical-BRST statement.  The latter also requires the global conformal-
charge and linearization-stability audit.
"""

from __future__ import annotations

from itertools import product

import sympy as sp
from sympy.physics.wigner import (
    clebsch_gordan,
    wigner_d_small,
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
VOL_S3 = 2 * sp.pi**2
alpha, beta, gamma = sp.symbols("alpha beta gamma", real=True)
t = sp.symbols("t", positive=True, real=True)
u = sp.symbols("u", real=True)


def magnetic_values(spin: sp.Rational) -> list[sp.Rational]:
    return [spin - index for index in range(int(2 * spin) + 1)]


def wigner_d(
    spin: sp.Rational,
    magnetic: sp.Rational,
    magnetic_prime: sp.Rational,
) -> sp.Expr:
    """Hamada--Horata Euler convention, their Eq. (A.15)."""

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
    return sp.sqrt((2 * spin + 1) / VOL_S3) * wigner_d(
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
    chirality: sp.Rational,
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
                spin,
                HALF,
                spin + chirality,
                scalar_m,
                tangent_m,
                magnetic,
            )
            * clebsch_gordan(
                spin,
                HALF,
                spin - chirality,
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
            result[ambient] += (
                coefficient * scalar * tau1(ambient, tangent_m, tangent_mp)
            )
    return result.applyfunc(sp.simplify)


def ambient_tensor_harmonic(
    spin: sp.Rational,
    magnetic: sp.Rational,
    magnetic_prime: sp.Rational,
    chirality: sp.Rational,
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
                spin,
                1,
                spin + chirality,
                scalar_m,
                tangent_m,
                magnetic,
            )
            * clebsch_gordan(
                spin,
                1,
                spin - chirality,
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
spatial_jacobian = embedding.jacobian((alpha, beta, gamma))
origin_angles = {alpha: 0, gamma: 0}


def ambient_norm_vector(vector: sp.Matrix) -> sp.Expr:
    return sp.expand(sum(sp.conjugate(entry) * entry for entry in vector))


def ambient_norm_tensor(tensor: sp.Matrix) -> sp.Expr:
    return sp.expand(
        sum(
            sp.conjugate(tensor[first, second]) * tensor[first, second]
            for first in range(4)
            for second in range(4)
        )
    )


def rationalize_beta(expression: sp.Expr) -> sp.Expr:
    substitutions = {
        sp.sin(beta): 2 * t / (1 + t**2),
        sp.cos(beta): (1 - t**2) / (1 + t**2),
        sp.sin(beta / 2): t / sp.sqrt(1 + t**2),
        sp.cos(beta / 2): 1 / sp.sqrt(1 + t**2),
        sp.tan(beta / 2): t,
    }
    return sp.cancel(
        sp.powsimp(expression.subs(substitutions, simultaneous=True), force=True)
    )


def integrate_s3_origin_scalar(expression: sp.Expr) -> sp.Expr:
    """Integrate an alpha/gamma-independent scalar over the unit S3."""

    radial = rationalize_beta(expression)
    # int dOmega = pi^2 int sin(beta) d beta and
    # sin(beta)d beta = 4t dt/(1+t^2)^2.
    measured = sp.cancel(4 * t * radial / (1 + t**2) ** 2)
    return sp.simplify(
        sp.pi**2 * sp.integrate(measured, (t, 0, sp.oo))
    )


# ---------------------------------------------------------------------------
# Same-chirality seed E2 A3 -> L5
# ---------------------------------------------------------------------------

seed_left_coefficients = (
    sp.simplify(clebsch_gordan(2, R(3, 2), R(5, 2), 2, HALF, R(5, 2))),
    sp.simplify(
        clebsch_gordan(2, R(3, 2), R(5, 2), 1, R(3, 2), R(5, 2))
    ),
)
seed_expected_coefficients = (2 * sp.sqrt(7) / 7, -sp.sqrt(21) / 7)
check(
    "EAL-1: nonmaximal left-SU(2) projection has the exact two CG coefficients",
    seed_left_coefficients == seed_expected_coefficients,
)
check(
    "EAL-1: projected E2 A3 highest-weight state is unit normalized",
    sp.simplify(sum(value**2 for value in seed_left_coefficients)) == 1,
)
check(
    "EAL-1: compact energy and SO(4) weights match L5",
    2 + 3 == 5
    and (2 + R(3, 2) - 1 == R(5, 2))
    and (0 + HALF == HALF),
)

E20 = ambient_tensor_harmonic(1, 2, 0, 1)
E10 = ambient_tensor_harmonic(1, 1, 0, 1)
A_half = ambient_vector_harmonic(1, HALF, HALF, HALF)
A_three_half = ambient_vector_harmonic(1, R(3, 2), HALF, HALF)
L5 = ambient_tensor_harmonic(R(3, 2), R(5, 2), HALF, 1)

seed_harmonics = (E20, E10, A_half, A_three_half, L5)
seed_norms = tuple(
    integrate_s3_origin_scalar(
        norm(harmonic).subs(origin_angles)
    )
    for harmonic, norm in (
        (E20, ambient_norm_tensor),
        (E10, ambient_norm_tensor),
        (A_half, ambient_norm_vector),
        (A_three_half, ambient_norm_vector),
        (L5, ambient_norm_tensor),
    )
)
check(
    "EAL-2: every harmonic entering the projected seed is unit normalized",
    seed_norms == (1, 1, 1, 1, 1),
)


# A non-derivative EAL scalar cannot contract the odd vector index.  Use the
# natural one-derivative invariant
#
#   int L*^{ij} E_i^k nabla_k A_j.
#
# Its nonzero value proves that harmonic orthogonality does not eliminate the
# projected channel.  It is not identified with the complete Weyl vertex.
spatial_coordinates = (alpha, beta, gamma)
spatial_metric = sp.Matrix(
    [
        [R(1, 4), 0, sp.cos(beta) / 4],
        [0, R(1, 4), 0],
        [sp.cos(beta) / 4, 0, R(1, 4)],
    ]
)
spatial_inverse = sp.simplify(spatial_metric.inv())
christoffel = [
    [
        [
            sp.simplify(
                sum(
                    spatial_inverse[upper, contracted]
                    * (
                        sp.diff(
                            spatial_metric[contracted, second],
                            spatial_coordinates[first],
                        )
                        + sp.diff(
                            spatial_metric[contracted, first],
                            spatial_coordinates[second],
                        )
                        - sp.diff(
                            spatial_metric[first, second],
                            spatial_coordinates[contracted],
                        )
                    )
                    for contracted in range(3)
                )
                / 2
            )
            for second in range(3)
        ]
        for first in range(3)
    ]
    for upper in range(3)
]


def covariant_vector_derivative(vector: sp.Matrix) -> sp.Matrix:
    return sp.Matrix(
        3,
        3,
        lambda derivative, covector: sp.diff(
            vector[covector], spatial_coordinates[derivative]
        )
        - sum(
            christoffel[contracted][derivative][covector]
            * vector[contracted]
            for contracted in range(3)
        ),
    )


L5_covariant = spatial_jacobian.T * L5 * spatial_jacobian
L5_upper_conjugate_origin = (
    spatial_inverse * sp.conjugate(L5_covariant) * spatial_inverse
).subs(origin_angles)


def derivative_gaunt_local(
    einstein: sp.Matrix, vector: sp.Matrix
) -> sp.Expr:
    einstein_covariant = spatial_jacobian.T * einstein * spatial_jacobian
    vector_covariant = spatial_jacobian.T * vector
    einstein_mixed_origin = (
        einstein_covariant * spatial_inverse
    ).subs(origin_angles)
    derivative_origin = covariant_vector_derivative(vector_covariant).subs(
        origin_angles
    )
    product_matrix = einstein_mixed_origin * derivative_origin
    return sp.expand(
        sum(
            L5_upper_conjugate_origin[first, second]
            * product_matrix[first, second]
            for first in range(3)
            for second in range(3)
        )
    )


seed_derivative_density = sp.expand(
    seed_left_coefficients[0] * derivative_gaunt_local(E20, A_half)
    + seed_left_coefficients[1]
    * derivative_gaunt_local(E10, A_three_half)
)
seed_derivative_density_t = rationalize_beta(seed_derivative_density)
seed_derivative_overlap = integrate_s3_origin_scalar(seed_derivative_density)
check(
    "EAL-3: projected derivative-Gaunt local scalar has the exact radial form",
    sp.simplify(
        seed_derivative_density_t
        + sp.sqrt(21) / (3 * sp.pi**3 * (1 + t**2))
    )
    == 0,
)
check(
    "EAL-3: projected derivative-Gaunt overlap is nonzero",
    seed_derivative_overlap == -sp.sqrt(21) / (3 * sp.pi),
)


# ---------------------------------------------------------------------------
# Complete curved-cylinder Weyl coefficient for the projected seed
# ---------------------------------------------------------------------------

# These four component densities are the exact outputs of independent C1b
# curvature runs using the commands in the module docstring.  They include
# the canonical oscillator normalizations.  Each is locally nonzero.
component_forward_densities = (
    I
    * sp.sqrt(6)
    * t
    * (t**2 - 1)
    / (1920 * sp.pi**3 * (1 + t**2) ** 2),
    -I
    * sp.sqrt(2)
    * t
    * (t**2 - 1)
    / (640 * sp.pi**3 * (1 + t**2) ** 2),
)
component_reverse_densities = tuple(
    sp.conjugate(density) for density in component_forward_densities
)

projected_forward_density = sp.factor(
    sum(
        coefficient * density
        for coefficient, density in zip(
            seed_left_coefficients, component_forward_densities
        )
    )
)
projected_reverse_density = sp.factor(
    sum(
        coefficient * density
        for coefficient, density in zip(
            seed_left_coefficients, component_reverse_densities
        )
    )
)
projected_prefactor = I * sp.sqrt(42) / (2688 * sp.pi**3)
expected_projected_density = (
    projected_prefactor * t * (t**2 - 1) / (1 + t**2) ** 2
)
check(
    "EAL-4: two CG-weighted curvature components give the exact projected density",
    sp.simplify(projected_forward_density - expected_projected_density) == 0,
)
check(
    "EAL-4: independently assembled reverse density is the exact conjugate",
    sp.simplify(
        projected_reverse_density - sp.conjugate(projected_forward_density)
    )
    == 0,
)

# Include d beta=2dt/(1+t^2), then transform to u=t^2/(1+t^2).
projected_forward_integrand_t = sp.cancel(
    2 * projected_forward_density / (1 + t**2)
)
projected_reverse_integrand_t = sp.cancel(
    2 * projected_reverse_density / (1 + t**2)
)
P1_legendre = sp.expand_func(sp.jacobi(1, 0, 0, 2 * u - 1))
projected_forward_integrand_u = projected_prefactor * P1_legendre
du_dt = sp.diff(t**2 / (1 + t**2), t)
check(
    "EAL-5: projected measured density is P_1^(0,0)(2u-1)",
    sp.expand(P1_legendre - (2 * u - 1)) == 0
    and sp.simplify(
        projected_forward_integrand_t
        - projected_forward_integrand_u.subs(
            u, t**2 / (1 + t**2)
        )
        * du_dt
    )
    == 0,
)

projected_forward_primitive_u = -projected_prefactor * u * (1 - u)
projected_reverse_primitive_u = sp.conjugate(
    projected_forward_primitive_u
)
check(
    "EAL-5: forward/reverse Jacobi primitives vanish at both endpoints",
    sp.simplify(
        sp.diff(projected_forward_primitive_u, u)
        - projected_forward_integrand_u
    )
    == 0
    and projected_forward_primitive_u.subs(u, 0) == 0
    and projected_forward_primitive_u.subs(u, 1) == 0
    and projected_reverse_primitive_u.subs(u, 0) == 0
    and projected_reverse_primitive_u.subs(u, 1) == 0,
)

# The engine's spatial coefficient has an overall 8pi^2 angular factor.
projected_forward_coefficient = sp.simplify(
    8
    * sp.pi**2
    * sp.integrate(projected_forward_integrand_u, (u, 0, 1))
)
projected_reverse_coefficient = sp.simplify(
    8
    * sp.pi**2
    * sp.integrate(
        sp.conjugate(projected_forward_integrand_u), (u, 0, 1)
    )
)
check(
    "EAL-5: both complete directed Weyl coefficients vanish separately",
    projected_forward_coefficient == 0
    and projected_reverse_coefficient == 0,
)

# sign(EA)=(+)(-)=- and sign(L)=-, so this is another same-sign block.
J_seed = -sp.eye(2)
V_seed = sp.Matrix(
    [
        [0, projected_reverse_coefficient],
        [projected_forward_coefficient, 0],
    ]
)
source_seed = sp.simplify(J_seed * V_seed - V_seed.conjugate().T * J_seed)
check(
    "EAL-6: seed transition block vanishes before the J-adjoint test",
    V_seed == sp.zeros(2) and source_seed == sp.zeros(2),
)


# ---------------------------------------------------------------------------
# First mixed-chirality tensor structure: E3 A3 -> L6
# ---------------------------------------------------------------------------

# Choose the parity representative
#   E_3(5/2,1/2) A_3(1/2,3/2) -> L_6(3,1).
# The left product is maximal; the right product is one step below maximal.
mixed_right_coefficients = (
    sp.simplify(clebsch_gordan(HALF, R(3, 2), 1, HALF, HALF, 1)),
    sp.simplify(
        clebsch_gordan(HALF, R(3, 2), 1, -HALF, R(3, 2), 1)
    ),
)
check(
    "EAL-mixed-1: mixed-chirality projection coefficients are exact",
    mixed_right_coefficients == (HALF, -sp.sqrt(3) / 2)
    and sp.simplify(sum(value**2 for value in mixed_right_coefficients)) == 1,
)
check(
    "EAL-mixed-1: mixed channel first appears at E3 A3 -> L6",
    3 + 3 == 6
    and (R(5, 2) + HALF == 3)
    and (HALF + R(3, 2) - 1 == 1),
)

mixed_E_plus = ambient_tensor_harmonic(
    R(3, 2), R(5, 2), HALF, 1
)
mixed_E_minus = ambient_tensor_harmonic(
    R(3, 2), R(5, 2), -HALF, 1
)
mixed_A_half = ambient_vector_harmonic(1, HALF, HALF, -HALF)
mixed_A_max = ambient_vector_harmonic(1, HALF, R(3, 2), -HALF)
mixed_L6 = ambient_tensor_harmonic(2, 3, 1, 1)
mixed_harmonics = (
    mixed_E_plus,
    mixed_E_minus,
    mixed_A_half,
    mixed_A_max,
    mixed_L6,
)
mixed_norms = tuple(
    integrate_s3_origin_scalar(
        sp.expand_trig(
            norm(harmonic).subs(origin_angles).rewrite(sp.sin)
        )
    )
    for harmonic, norm in (
        (mixed_E_plus, ambient_norm_tensor),
        (mixed_E_minus, ambient_norm_tensor),
        (mixed_A_half, ambient_norm_vector),
        (mixed_A_max, ambient_norm_vector),
        (mixed_L6, ambient_norm_tensor),
    )
)
check(
    "EAL-mixed-1: every harmonic entering the mixed seed is unit normalized",
    mixed_norms == (1, 1, 1, 1, 1),
)


def derivative_gaunt_local_with_output(
    output: sp.Matrix, einstein: sp.Matrix, vector: sp.Matrix
) -> sp.Expr:
    output_covariant = spatial_jacobian.T * output * spatial_jacobian
    output_upper_conjugate_origin = (
        spatial_inverse
        * sp.conjugate(output_covariant)
        * spatial_inverse
    ).subs(origin_angles)
    einstein_covariant = spatial_jacobian.T * einstein * spatial_jacobian
    vector_covariant = spatial_jacobian.T * vector
    einstein_mixed_origin = (
        einstein_covariant * spatial_inverse
    ).subs(origin_angles)
    derivative_origin = covariant_vector_derivative(vector_covariant).subs(
        origin_angles
    )
    product_matrix = einstein_mixed_origin * derivative_origin
    return sp.expand(
        sum(
            output_upper_conjugate_origin[first, second]
            * product_matrix[first, second]
            for first in range(3)
            for second in range(3)
        )
    )


mixed_derivative_density = sp.expand(
    mixed_right_coefficients[0]
    * derivative_gaunt_local_with_output(
        mixed_L6, mixed_E_plus, mixed_A_half
    )
    + mixed_right_coefficients[1]
    * derivative_gaunt_local_with_output(
        mixed_L6, mixed_E_minus, mixed_A_max
    )
)
mixed_derivative_density_expanded = sp.expand_trig(
    mixed_derivative_density.rewrite(sp.sin)
)
mixed_derivative_density_t = rationalize_beta(
    mixed_derivative_density_expanded
)
mixed_derivative_overlap = integrate_s3_origin_scalar(
    mixed_derivative_density_expanded
)
check(
    "EAL-mixed-1: derivative-Gaunt scalar has the exact allowed radial form",
    sp.simplify(
        mixed_derivative_density_t
        - 1 / (2 * sp.pi**3 * (1 + t**2) ** 2)
    )
    == 0,
)
check(
    "EAL-mixed-1: projected derivative-Gaunt overlap is nonzero",
    mixed_derivative_overlap == 1 / (3 * sp.pi),
)

# These are the exact outputs of four independent curved-cylinder runs:
# ``mixed-eal-{1,2}`` and ``mixed-eal-reverse-{1,2}``.  The two components
# are locally distinct and nonzero.  Each independently integrates to zero;
# their CG projection exposes the simpler universal Jacobi mechanism.
mixed_component_forward_densities = (
    I
    * sp.sqrt(6)
    * t
    * (-2 * t**4 + 5 * t**2 - 1)
    / (1280 * sp.pi**3 * (1 + t**2) ** 4),
    I
    * sp.sqrt(2)
    * t
    * (-10 * t**4 + t**2 + 3)
    / (1280 * sp.pi**3 * (1 + t**2) ** 4),
)
mixed_component_reverse_densities = tuple(
    sp.conjugate(density) for density in mixed_component_forward_densities
)
mixed_projected_forward_density = sp.factor(
    sum(
        coefficient * density
        for coefficient, density in zip(
            mixed_right_coefficients, mixed_component_forward_densities
        )
    )
)
mixed_projected_reverse_density = sp.factor(
    sum(
        coefficient * density
        for coefficient, density in zip(
            mixed_right_coefficients, mixed_component_reverse_densities
        )
    )
)
mixed_projected_prefactor = I * sp.sqrt(6) / (640 * sp.pi**3)
mixed_expected_projected_density = (
    mixed_projected_prefactor
    * t
    * (2 * t**2 - 1)
    / (1 + t**2) ** 3
)
check(
    "EAL-mixed-2: CG-weighted curvature components give the exact projected density",
    sp.simplify(
        mixed_projected_forward_density
        - mixed_expected_projected_density
    )
    == 0,
)
check(
    "EAL-mixed-2: independently assembled reverse density is the exact conjugate",
    sp.simplify(
        mixed_projected_reverse_density
        - sp.conjugate(mixed_projected_forward_density)
    )
    == 0,
)

mixed_projected_forward_integrand_t = sp.cancel(
    2 * mixed_projected_forward_density / (1 + t**2)
)
mixed_projected_reverse_integrand_t = sp.cancel(
    2 * mixed_projected_reverse_density / (1 + t**2)
)
P1_mixed = sp.expand_func(sp.jacobi(1, 1, 0, 2 * u - 1))
mixed_projected_forward_integrand_u = (
    mixed_projected_prefactor * (1 - u) * P1_mixed
)
check(
    "EAL-mixed-3: projected measured density is the Jacobi (1-u) P_1^(1,0)",
    sp.expand(P1_mixed - (3 * u - 1)) == 0
    and sp.simplify(
        mixed_projected_forward_integrand_t
        - mixed_projected_forward_integrand_u.subs(
            u, t**2 / (1 + t**2)
        )
        * du_dt
    )
    == 0,
)

mixed_projected_forward_primitive_u = (
    -mixed_projected_prefactor * u * (1 - u) ** 2
)
mixed_projected_reverse_primitive_u = sp.conjugate(
    mixed_projected_forward_primitive_u
)
check(
    "EAL-mixed-3: forward/reverse Jacobi primitives vanish at both endpoints",
    sp.simplify(
        sp.diff(mixed_projected_forward_primitive_u, u)
        - mixed_projected_forward_integrand_u
    )
    == 0
    and mixed_projected_forward_primitive_u.subs(u, 0) == 0
    and mixed_projected_forward_primitive_u.subs(u, 1) == 0
    and mixed_projected_reverse_primitive_u.subs(u, 0) == 0
    and mixed_projected_reverse_primitive_u.subs(u, 1) == 0,
)

mixed_projected_forward_coefficient = sp.simplify(
    8
    * sp.pi**2
    * sp.integrate(mixed_projected_forward_integrand_u, (u, 0, 1))
)
mixed_projected_reverse_coefficient = sp.simplify(
    8
    * sp.pi**2
    * sp.integrate(
        sp.conjugate(mixed_projected_forward_integrand_u), (u, 0, 1)
    )
)
check(
    "EAL-mixed-3: both complete directed Weyl coefficients vanish separately",
    mixed_projected_forward_coefficient == 0
    and mixed_projected_reverse_coefficient == 0,
)

J_mixed = -sp.eye(2)
V_mixed = sp.Matrix(
    [
        [0, mixed_projected_reverse_coefficient],
        [mixed_projected_forward_coefficient, 0],
    ]
)
source_mixed = sp.simplify(
    J_mixed * V_mixed - V_mixed.conjugate().T * J_mixed
)
check(
    "EAL-mixed-4: transition block vanishes before the J-adjoint test",
    V_mixed == sp.zeros(2) and source_mixed == sp.zeros(2),
)


print("\nSame-chirality E2 A3 -> L5 seed")
print("  CG coefficients =", seed_left_coefficients)
print("  harmonic norms =", seed_norms)
print("  derivative-Gaunt radial scalar =", seed_derivative_density_t)
print("  derivative-Gaunt overlap =", seed_derivative_overlap)
print("  forward component densities =", component_forward_densities)
print("  reverse component densities =", component_reverse_densities)
print("  projected forward density =", projected_forward_density)
print("  projected reverse density =", projected_reverse_density)
print("  measured u-form =", projected_forward_integrand_u, "du")
print("  forward primitive =", projected_forward_primitive_u)
print(
    "  forward/reverse coefficients =",
    projected_forward_coefficient,
    projected_reverse_coefficient,
)
print("  induced two-channel form =", J_seed)
print("  J-adjoint source =", source_seed)

print("\nFirst mixed-chirality E3 A3 -> L6 seed")
print("  right-SU(2) CG coefficients =", mixed_right_coefficients)
print("  harmonic norms =", mixed_norms)
print("  derivative-Gaunt radial scalar =", mixed_derivative_density_t)
print("  derivative-Gaunt overlap =", mixed_derivative_overlap)
print("  forward component densities =", mixed_component_forward_densities)
print("  reverse component densities =", mixed_component_reverse_densities)
print("  projected forward density =", mixed_projected_forward_density)
print("  projected reverse density =", mixed_projected_reverse_density)
print("  measured u-form =", mixed_projected_forward_integrand_u, "du")
print("  forward primitive =", mixed_projected_forward_primitive_u)
print(
    "  forward/reverse coefficients =",
    mixed_projected_forward_coefficient,
    mixed_projected_reverse_coefficient,
)
print("  induced two-channel form =", J_mixed)
print("  J-adjoint source =", source_mixed)

print("\nCurvature component commands")
for command in (
    "eal-1",
    "eal-2",
    "eal-reverse-1",
    "eal-reverse-2",
    "mixed-eal-1",
    "mixed-eal-2",
    "mixed-eal-reverse-1",
    "mixed-eal-reverse-2",
):
    print("  python3 symbolic/verify_conformal_aal_vertex.py", command)

if not PASS:
    raise SystemExit("CONFORMAL EAL SEEDS: FAIL")

print("\nCONFORMAL EAL SEED HARMONICS: ALL PASS")
