#!/usr/bin/env python3
"""Exact cylinder certificate for conformal vector-vector-TT resonances.

The first part of C1b constructs the lowest allowed transverse-vector and
upper-TT tensor harmonics directly from the normalized Wigner-D/Clebsch-
Gordan formulae of Hamada--Horata, arXiv:hep-th/0307008, Appendix A.

The selected highest-weight modes are

    A_3 : J=1, y=+1/2, M=(3/2,1/2),
    L_6 : J=2, x=+1,   M=(3,1).

They realize Sym^2(3/2,1/2) -> (3,1).  Their elementary normalized Gaunt
overlap is nonzero,

    int_{S^3} L^*_{ij} A^i A^j = sqrt(6)/(3 pi).

This proves that the candidate is not killed by harmonic orthogonality.  The
complete Weyl vertex nevertheless cancels after integration.  The second part
of this file builds a two-jet, multilinear curved-background perturbiner and
proves that the nonzero local density is an exact radial boundary term.

The same calculation is parameterized by the two vector spins.  Four
independent highest-weight channels have been checked exactly:

    (J_1,J_2) = (1,1), (1,3/2), (3/2,3/2), (1,2).

All have zero integrated A_J A_K L_(J+K) coefficient.  The script also checks
the resonant E_2 A_3 A_5 channel.  Its cancellation is compatible with the
known nonzero *complex flat-momentum* EAA amplitude: normalizable positive-
energy cylinder modes define a different, real resonant problem.

The finite scan motivates, but does not replace, an all-spin cubic protection
proof.  No coordinate grid or floating-point approximation is used.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import factorial
import sys

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
time, alpha, beta, gamma = sp.symbols(
    "time alpha beta gamma", real=True
)
coordinates = (time, alpha, beta, gamma)


def magnetic_values(spin: sp.Rational) -> list[sp.Rational]:
    return [spin - index for index in range(int(2 * spin) + 1)]


def wigner_d(
    spin: sp.Rational, magnetic: sp.Rational, magnetic_prime: sp.Rational
) -> sp.Expr:
    """Hamada--Horata Euler convention, matching their Eq. (A.15)."""
    values = magnetic_values(spin)
    small = wigner_d_small(spin, -beta)
    return (
        sp.exp(-I * magnetic * alpha)
        * small[values.index(magnetic), values.index(magnetic_prime)]
        * sp.exp(-I * magnetic_prime * gamma)
    )


def scalar_harmonic(
    spin: sp.Rational, magnetic: sp.Rational, magnetic_prime: sp.Rational
) -> sp.Expr:
    return sp.sqrt((2 * spin + 1) / VOL) * wigner_d(
        spin, magnetic, magnetic_prime
    )


half_values = [HALF, -HALF]
one_values = [sp.Integer(1), sp.Integer(0), sp.Integer(-1)]

# Eq. (A.16), with row m and column m'.
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
    """Normalized rank-two tau, equivalently the J=1 Wigner polynomial."""
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


A_ambient = ambient_vector_harmonic(1, R(3, 2), R(1, 2), HALF)
L_ambient = ambient_tensor_harmonic(2, 3, 1, 1)

# Unit S^3 embedded in R^4, Hamada--Horata Eq. (A.9).
embedding = sp.Matrix(
    [
        sp.cos(beta / 2) * sp.cos((alpha + gamma) / 2),
        sp.sin(beta / 2) * sp.sin((alpha - gamma) / 2),
        -sp.sin(beta / 2) * sp.cos((alpha - gamma) / 2),
        -sp.cos(beta / 2) * sp.sin((alpha + gamma) / 2),
    ]
)
spatial_jacobian = embedding.jacobian((alpha, beta, gamma))
A_covariant = spatial_jacobian.T * A_ambient
L_covariant = spatial_jacobian.T * L_ambient * spatial_jacobian


def ambient_norm_vector(vector: sp.Matrix) -> sp.Expr:
    return sp.trigsimp(sum(sp.conjugate(entry) * entry for entry in vector))


def ambient_norm_tensor(tensor: sp.Matrix) -> sp.Expr:
    return sp.trigsimp(
        sum(
            sp.conjugate(tensor[first, second]) * tensor[first, second]
            for first in range(4)
            for second in range(4)
        )
    )


def ambient_tvv(tensor: sp.Matrix, vector: sp.Matrix) -> sp.Expr:
    return sp.trigsimp(
        sum(
            sp.conjugate(tensor[first, second])
            * vector[first]
            * vector[second]
            for first in range(4)
            for second in range(4)
        )
    )


# The scalar contractions are SO(4) highest-weight singlets and hence are
# alpha/gamma independent.  Evaluating at alpha=gamma=0 makes the remaining
# beta integrals elementary and avoids a gratuitous trigonometric expansion.
origin_angles = {alpha: 0, gamma: 0}
A_norm_density = sp.trigsimp(
    ambient_norm_vector(A_ambient).subs(origin_angles)
)
L_norm_density = sp.trigsimp(
    ambient_norm_tensor(L_ambient).subs(origin_angles)
)
AL_overlap_density = sp.trigsimp(
    ambient_tvv(L_ambient, A_ambient).subs(origin_angles)
)

expected_A_density = (
    sp.sin(beta) ** 2 / (4 * sp.pi**2)
    + sp.cos(beta / 2) ** 4 / sp.pi**2
)
expected_L_density = 3 * sp.cos(beta / 2) ** 4 / (2 * sp.pi**2)
expected_overlap_density = (
    sp.sqrt(6) * sp.cos(beta / 2) ** 4 / (2 * sp.pi**3)
)


def half_angle_identity(expression: sp.Expr) -> bool:
    """Prove an even half-angle identity by t=tan(beta/2)."""
    tangent = sp.symbols("half_angle_tangent", positive=True, real=True)
    rationalized = expression.subs(
        {
            sp.sin(beta): 2 * tangent / (1 + tangent**2),
            sp.cos(beta): (1 - tangent**2) / (1 + tangent**2),
            sp.sin(beta / 2): tangent / sp.sqrt(1 + tangent**2),
            sp.cos(beta / 2): 1 / sp.sqrt(1 + tangent**2),
        },
        simultaneous=True,
    )
    return sp.cancel(rationalized) == 0

check(
    "C1b-1: A3 vector harmonic has the exact normalized density",
    half_angle_identity(A_norm_density - expected_A_density),
)
check(
    "C1b-1: L6 upper-TT harmonic has the exact normalized density",
    half_angle_identity(L_norm_density - expected_L_density),
)
check(
    "C1b-1: the highest-weight L6* A3 A3 density is nonzero",
    half_angle_identity(AL_overlap_density - expected_overlap_density),
)

# Integral over alpha and gamma contributes 8 pi^2; dOmega=sin(beta)/8.
angle_factor = sp.pi**2
A_norm = sp.simplify(
    angle_factor
    * sp.integrate(sp.sin(beta) * expected_A_density, (beta, 0, sp.pi))
)
L_norm = sp.simplify(
    angle_factor
    * sp.integrate(sp.sin(beta) * expected_L_density, (beta, 0, sp.pi))
)
AL_overlap = sp.simplify(
    angle_factor
    * sp.integrate(
        sp.sin(beta) * expected_overlap_density, (beta, 0, sp.pi)
    )
)
check("C1b-1: A3 vector harmonic is unit normalized", A_norm == 1)
check("C1b-1: L6 tensor harmonic is unit normalized", L_norm == 1)
check(
    "C1b-1: normalized L6* A3 A3 overlap is sqrt(6)/(3 pi)",
    AL_overlap == sp.sqrt(6) / (3 * sp.pi),
)


# ---------------------------------------------------------------------------
# Two-jet algebra for an exact curved-background multilinear perturbiner
# ---------------------------------------------------------------------------
JET_ORDER = 2
MultiIndex = tuple[int, int, int, int]
ZERO_MULTI: MultiIndex = (0, 0, 0, 0)
radial_tangent = sp.symbols("radial_tangent", positive=True, real=True)
radial_root = sp.symbols("radial_root", positive=True, real=True)
half_angle = sp.symbols("half_angle", real=True)


def cancel_radial_rational(expression: sp.Expr) -> sp.Expr:
    """Cancel an exact rational function after quadratic-root reduction."""
    return sp.cancel(expression)


def canonical_radial(expression: sp.Expr) -> sp.Expr:
    """Reduce the quadratic tan-half-angle extension exactly.

    Every selected mode coefficient belongs to

        Q(i, radicals, pi)(t)[sqrt(1+t^2)].

    Moreover, the parity of the square root is fixed by the number of A
    waves in a multilinear subset.  Reducing ``radial_root**2`` before
    invoking ``cancel`` keeps the latter in a one-variable rational field;
    asking SymPy to cancel the unreduced algebraic expressions at every jet
    multiplication is several orders of magnitude slower.
    """
    expression = sp.sympify(expression)
    if expression == 0:
        return sp.Integer(0)

    # Work in the exact quadratic extension r^2=1+t^2.  A term-by-term
    # power reduction is insufficient once a previous rational operation
    # has put a polynomial in r in a denominator, so rationalize the full
    # quotient algebraically.
    numerator, denominator = sp.fraction(sp.together(expression))
    root_square = 1 + radial_tangent**2

    def split_root_polynomial(polynomial: sp.Expr) -> tuple[sp.Expr, sp.Expr]:
        even = sp.Integer(0)
        odd = sp.Integer(0)
        for (degree,), coefficient in sp.Poly(
            sp.expand(polynomial), radial_root
        ).terms():
            quotient, parity = divmod(degree, 2)
            reduced = coefficient * root_square**quotient
            if parity:
                odd += reduced
            else:
                even += reduced
        return even, odd

    numerator_even, numerator_odd = split_root_polynomial(numerator)
    denominator_even, denominator_odd = split_root_polynomial(denominator)
    rational_denominator = (
        denominator_even**2
        - root_square * denominator_odd**2
    )
    parity_parts = {
        0: cancel_radial_rational(
            (
                numerator_even * denominator_even
                - root_square * numerator_odd * denominator_odd
            )
            / rational_denominator
        ),
        1: cancel_radial_rational(
            (
                numerator_odd * denominator_even
                - numerator_even * denominator_odd
            )
            / rational_denominator
        ),
    }
    active = [
        (parity, value)
        for parity, value in parity_parts.items()
        if value != 0
    ]
    if not active:
        return sp.Integer(0)
    if len(active) != 1:
        raise ValueError(
            "mixed radial-root parity in one jet coefficient: "
            f"{active}"
        )
    parity, rational = active[0]
    return radial_root**parity * rational


def beta_to_tangent(expression: sp.Expr) -> sp.Expr:
    """Put beta dependence in the rational tan(beta/2) chart."""
    # trigsimp may introduce sin(2 beta), cos(2 beta), cot(beta), etc.  Expand
    # these before making the half-angle substitution; otherwise apparently
    # equal metric jets retain inequivalent trigonometric representatives.
    # SymPy expands cos(3*x), but not cos(3*beta/2) when beta is its base
    # symbol.  Temporarily make beta=2*half_angle so every mode harmonic has
    # an integer multiple of the expansion variable.
    expanded = sp.expand_trig(
        sp.sympify(expression)
        .rewrite(sp.sin)
        .rewrite(sp.cos)
        .subs(beta, 2 * half_angle)
    )
    converted = expanded.subs(
        {
            sp.sin(half_angle): radial_tangent / radial_root,
            sp.cos(half_angle): 1 / radial_root,
        },
        simultaneous=True,
    )
    if converted.has(beta, half_angle):
        raise ValueError(f"unconverted beta dependence: {converted}")
    return canonical_radial(converted)


def multi_indices() -> tuple[MultiIndex, ...]:
    values: list[MultiIndex] = []
    for index in product(range(JET_ORDER + 1), repeat=4):
        if sum(index) <= JET_ORDER:
            values.append(index)
    return tuple(values)


MULTI_INDICES = multi_indices()


def canonical_jet_coefficient(value: sp.Expr) -> sp.Expr:
    """Keep the quadratic one-variable jet algebra reduced incrementally."""
    if value == 0:
        return sp.Integer(0)
    return canonical_radial(value)


@dataclass(frozen=True)
class Jet:
    coefficients: dict[MultiIndex, sp.Expr]

    @staticmethod
    def zero() -> "Jet":
        return Jet({})

    @staticmethod
    def constant(value: sp.Expr | int) -> "Jet":
        value = sp.sympify(value)
        return Jet({ZERO_MULTI: value}) if value != 0 else Jet.zero()

    @staticmethod
    def from_expression(expression: sp.Expr) -> "Jet":
        coefficients: dict[MultiIndex, sp.Expr] = {}
        for index in MULTI_INDICES:
            derivative = expression
            denominator = 1
            for coordinate, count in zip(coordinates, index):
                if count:
                    derivative = sp.diff(derivative, coordinate, count)
                    denominator *= factorial(count)
            value = sp.trigsimp(
                derivative.subs({time: 0, alpha: 0, gamma: 0}) / denominator
            )
            value = beta_to_tangent(value)
            if value != 0:
                coefficients[index] = value
        return Jet(coefficients)

    def __add__(self, other: "Jet") -> "Jet":
        output = dict(self.coefficients)
        for index, value in other.coefficients.items():
            output[index] = output.get(index, 0) + value
        return Jet(
            {
                index: value
                for index, value in output.items()
                if value != 0
            }
        )

    def __neg__(self) -> "Jet":
        return Jet({index: -value for index, value in self.coefficients.items()})

    def __sub__(self, other: "Jet") -> "Jet":
        return self + (-other)

    def __mul__(self, other: "Jet") -> "Jet":
        output: dict[MultiIndex, sp.Expr] = {}
        for left_index, left_value in self.coefficients.items():
            for right_index, right_value in other.coefficients.items():
                index = tuple(
                    left + right
                    for left, right in zip(left_index, right_index)
                )
                if sum(index) > JET_ORDER:
                    continue
                output[index] = output.get(index, 0) + left_value * right_value
        return Jet(
            {
                index: value
                for index, value in output.items()
                if value != 0
            }
        )

    def scale(self, scalar: sp.Expr | int) -> "Jet":
        scalar = sp.sympify(scalar)
        return Jet(
            {
                index: scalar * value
                for index, value in self.coefficients.items()
                if scalar * value != 0
            }
        )

    def derivative(self, direction: int) -> "Jet":
        output: dict[MultiIndex, sp.Expr] = {}
        for index in MULTI_INDICES:
            source = list(index)
            source[direction] += 1
            source_index = tuple(source)
            if source_index not in self.coefficients:
                continue
            output[index] = (index[direction] + 1) * self.coefficients[source_index]
        return Jet(output)

    def conjugate(self) -> "Jet":
        return Jet(
            {
                index: sp.conjugate(value)
                for index, value in self.coefficients.items()
            }
        )

    def reduced(self) -> "Jet":
        coefficients: dict[MultiIndex, sp.Expr] = {}
        for index, value in self.coefficients.items():
            reduced = canonical_jet_coefficient(value)
            if reduced != 0:
                coefficients[index] = reduced
        return Jet(coefficients)

    def value(self) -> sp.Expr:
        return self.coefficients.get(ZERO_MULTI, sp.Integer(0))


def jet_equal(left: Jet, right: Jet) -> bool:
    for index in MULTI_INDICES:
        difference = (
            left.coefficients.get(index, 0)
            - right.coefficients.get(index, 0)
        )
        if canonical_jet_coefficient(difference) != 0:
            return False
    return True


def jet_zero(jet: Jet) -> bool:
    return jet_equal(jet, Jet.zero())


def jet_matrix_from_expressions(matrix: sp.Matrix) -> list[list[Jet]]:
    return [
        [Jet.from_expression(matrix[row, column]) for column in range(matrix.cols)]
        for row in range(matrix.rows)
    ]


def jet_matrix_multiply(
    left: list[list[Jet]], right: list[list[Jet]]
) -> list[list[Jet]]:
    return [
        [
            sum(
                (left[row][middle] * right[middle][column]
                 for middle in range(len(right))),
                Jet.zero(),
            ).reduced()
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def jet_matrix_scale(
    matrix: list[list[Jet]], scalar: sp.Expr | int
) -> list[list[Jet]]:
    return [[entry.scale(scalar) for entry in row] for row in matrix]


def jet_matrix_add(
    left: list[list[Jet]], right: list[list[Jet]]
) -> list[list[Jet]]:
    return [
        [
            (left[row][column] + right[row][column]).reduced()
            for column in range(len(left[0]))
        ]
        for row in range(len(left))
    ]


# A small self-test: Taylor multiplication and differentiation must reproduce
# direct differentiation at the base point.
test_left = Jet.from_expression(sp.exp(I * time) * sp.sin(beta))
test_right = Jet.from_expression(sp.exp(-I * time) * sp.cos(beta))
test_product = test_left * test_right
check(
    "C1b-2: two-jet product reproduces the base function",
    canonical_jet_coefficient(
        test_product.value() - beta_to_tangent(sp.sin(beta) * sp.cos(beta))
    )
    == 0,
)
check(
    "C1b-2: two-jet derivative obeys Leibniz exactly",
    canonical_jet_coefficient(
        test_product.derivative(2).value()
        - beta_to_tangent(sp.cos(2 * beta).expand(trig=True))
    )
    == 0,
)


# ---------------------------------------------------------------------------
# Multilinear tensor algebra and cylinder curvature
# ---------------------------------------------------------------------------
WaveKey = frozenset[int]
Index = tuple[int, ...]
WaveTensor = dict[WaveKey, dict[Index, Jet]]


def jet_is_zero(jet: Jet) -> bool:
    return not jet.coefficients


def wt_reduce(tensor: WaveTensor) -> WaveTensor:
    output: WaveTensor = {}
    for key, components in tensor.items():
        reduced_components: dict[Index, Jet] = {}
        for index, value in components.items():
            reduced = value.reduced()
            if not jet_is_zero(reduced):
                reduced_components[index] = reduced
        if reduced_components:
            output[key] = reduced_components
    return output


def wt_add_raw(left: WaveTensor, right: WaveTensor) -> WaveTensor:
    output: WaveTensor = {
        key: dict(components) for key, components in left.items()
    }
    for key, components in right.items():
        target = output.setdefault(key, {})
        for index, value in components.items():
            target[index] = target.get(index, Jet.zero()) + value
    return output


def wt_add(left: WaveTensor, right: WaveTensor) -> WaveTensor:
    return wt_reduce(wt_add_raw(left, right))


def wt_scale(tensor: WaveTensor, scalar: sp.Expr | int) -> WaveTensor:
    return {
        key: {index: value.scale(scalar) for index, value in components.items()}
        for key, components in tensor.items()
    }


def wt_mul(left: WaveTensor, right: WaveTensor) -> WaveTensor:
    output: WaveTensor = {}
    for left_key, left_components in left.items():
        for right_key, right_components in right.items():
            if left_key & right_key:
                continue
            key = left_key | right_key
            target = output.setdefault(key, {})
            for left_index, left_value in left_components.items():
                for right_index, right_value in right_components.items():
                    index = left_index + right_index
                    target[index] = target.get(index, Jet.zero()) + (
                        left_value * right_value
                    )
    return wt_reduce(output)


def wt_trace(tensor: WaveTensor, first: int, second: int) -> WaveTensor:
    output: WaveTensor = {}
    for key, components in tensor.items():
        target = output.setdefault(key, {})
        for index, value in components.items():
            if index[first] != index[second]:
                continue
            reduced = tuple(
                entry
                for position, entry in enumerate(index)
                if position not in (first, second)
            )
            target[reduced] = target.get(reduced, Jet.zero()) + value
    return wt_reduce(output)


def wt_contract(
    left: WaveTensor,
    right: WaveTensor,
    pairs: tuple[tuple[int, int], ...],
) -> WaveTensor:
    """Multiply tensors and contract selected left/right index pairs.

    This avoids materializing the high-rank outer products discarded by a
    subsequent trace.  It is algebraically identical to ``wt_trace(wt_mul)``
    but is decisive for the rank-six Gamma-Gamma contraction.
    """
    output: WaveTensor = {}
    left_contracted = {left_position for left_position, _ in pairs}
    right_contracted = {right_position for _, right_position in pairs}
    for left_key, left_components in left.items():
        for right_key, right_components in right.items():
            if left_key & right_key:
                continue
            key = left_key | right_key
            target = output.setdefault(key, {})
            for left_index, left_value in left_components.items():
                for right_index, right_value in right_components.items():
                    if any(
                        left_index[left_position]
                        != right_index[right_position]
                        for left_position, right_position in pairs
                    ):
                        continue
                    index = tuple(
                        value
                        for position, value in enumerate(left_index)
                        if position not in left_contracted
                    ) + tuple(
                        value
                        for position, value in enumerate(right_index)
                        if position not in right_contracted
                    )
                    target[index] = target.get(index, Jet.zero()) + (
                        left_value * right_value
                    )
    return wt_reduce(output)


def wt_permute(tensor: WaveTensor, order: tuple[int, ...]) -> WaveTensor:
    return {
        key: {
            tuple(index[position] for position in order): value
            for index, value in components.items()
        }
        for key, components in tensor.items()
    }


def wt_derivative(tensor: WaveTensor) -> WaveTensor:
    output: WaveTensor = {}
    for key, components in tensor.items():
        target = output.setdefault(key, {})
        for index, value in components.items():
            for direction in range(4):
                derivative = value.derivative(direction)
                if jet_is_zero(derivative):
                    continue
                target[(direction,) + index] = derivative
    return output


def wt_component(tensor: WaveTensor, key: WaveKey, index: Index) -> Jet:
    return tensor.get(key, {}).get(index, Jet.zero())


def matrix_to_components(matrix: list[list[Jet]]) -> dict[Index, Jet]:
    return {
        (row, column): matrix[row][column]
        for row in range(len(matrix))
        for column in range(len(matrix[0]))
        if not jet_is_zero(matrix[row][column])
    }


def components_to_matrix(components: dict[Index, Jet]) -> list[list[Jet]]:
    return [
        [components.get((row, column), Jet.zero()) for column in range(4)]
        for row in range(4)
    ]


background_metric_expression = sp.zeros(4)
background_metric_expression[0, 0] = -1
background_metric_expression[1, 1] = R(1, 4)
background_metric_expression[2, 2] = R(1, 4)
background_metric_expression[3, 3] = R(1, 4)
background_metric_expression[1, 3] = sp.cos(beta) / 4
background_metric_expression[3, 1] = sp.cos(beta) / 4
background_inverse_expression = sp.simplify(background_metric_expression.inv())
background_metric = jet_matrix_from_expressions(background_metric_expression)
background_inverse = jet_matrix_from_expressions(background_inverse_expression)

identity_jet_matrix = [
    [Jet.constant(1 if row == column else 0) for column in range(4)]
    for row in range(4)
]
background_product = jet_matrix_multiply(background_metric, background_inverse)
check(
    "C1b-3: cylinder background metric inverse is exact through two jets",
    all(
        jet_equal(
            background_product[row][column], identity_jet_matrix[row][column]
        )
        for row in range(4)
        for column in range(4)
    ),
)


def empty_metric_expression() -> sp.Matrix:
    return sp.zeros(4)


# Canonical oscillator normalizations in Hamada--Horata Eqs. (3.26)--(3.27).
# ``aal`` is the new opposite-sign candidate.  ``eaa`` compares it with the
# channel whose complex flat-momentum amplitude is known to be nonzero.  The
# normalizable positive-energy cylinder coefficient also cancels, exposing
# the distinction between those two kinematic problems.
channel = sys.argv[1].lower() if len(sys.argv) > 1 else "aal"
if channel not in {"aal", "eaa"}:
    raise SystemExit(
        "usage: verify_conformal_aal_vertex.py [aal [J1 J2]|eaa]"
    )


def vector_metric_mode(
    harmonic: sp.Matrix, frequency: int, normalization: sp.Expr, bra: bool
) -> sp.Matrix:
    phase = sp.exp((I if bra else -I) * frequency * time)
    spatial_mode = phase * (sp.conjugate(harmonic) if bra else harmonic)
    perturbation = empty_metric_expression()
    for spatial in range(3):
        perturbation[0, spatial + 1] = normalization * spatial_mode[spatial]
        perturbation[spatial + 1, 0] = normalization * spatial_mode[spatial]
    return perturbation


def tensor_metric_mode(
    harmonic: sp.Matrix, frequency: int, normalization: sp.Expr, bra: bool
) -> sp.Matrix:
    phase = sp.exp((I if bra else -I) * frequency * time)
    spatial_mode = phase * (sp.conjugate(harmonic) if bra else harmonic)
    perturbation = empty_metric_expression()
    for first in range(3):
        for second in range(3):
            perturbation[first + 1, second + 1] = (
                normalization * spatial_mode[first, second]
            )
    return perturbation


if channel == "aal":
    first_spin = sp.Rational(sys.argv[2]) if len(sys.argv) > 2 else R(1)
    second_spin = sp.Rational(sys.argv[3]) if len(sys.argv) > 3 else R(1)
    total_spin = first_spin + second_spin
    first_A_ambient = ambient_vector_harmonic(
        first_spin, first_spin + HALF, first_spin - HALF, HALF
    )
    second_A_ambient = ambient_vector_harmonic(
        second_spin, second_spin + HALF, second_spin - HALF, HALF
    )
    outgoing_L_ambient = ambient_tensor_harmonic(
        total_spin, total_spin + 1, total_spin - 1, 1
    )
    first_A_covariant = spatial_jacobian.T * first_A_ambient
    second_A_covariant = spatial_jacobian.T * second_A_ambient
    outgoing_L_covariant = (
        spatial_jacobian.T * outgoing_L_ambient * spatial_jacobian
    )
    first_frequency = int(2 * first_spin + 1)
    second_frequency = int(2 * second_spin + 1)
    outgoing_frequency = int(2 * total_spin + 2)
    first_normalization = 1 / (
        2
        * sp.sqrt(
            (2 * first_spin - 1)
            * (2 * first_spin + 1)
            * (2 * first_spin + 3)
        )
    )
    second_normalization = 1 / (
        2
        * sp.sqrt(
            (2 * second_spin - 1)
            * (2 * second_spin + 1)
            * (2 * second_spin + 3)
        )
    )
    outgoing_normalization = 1 / (
        4 * sp.sqrt((total_spin + 1) * (2 * total_spin + 1))
    )
    wave_expressions = [
        vector_metric_mode(
            first_A_covariant, first_frequency, first_normalization, False
        ),
        vector_metric_mode(
            second_A_covariant,
            second_frequency,
            second_normalization,
            False,
        ),
        tensor_metric_mode(
            outgoing_L_covariant,
            outgoing_frequency,
            outgoing_normalization,
            True,
        ),
    ]
    expected_phases = (
        (
            -first_frequency * I,
            -(first_spin + HALF) * I,
            -(first_spin - HALF) * I,
        ),
        (
            -second_frequency * I,
            -(second_spin + HALF) * I,
            -(second_spin - HALF) * I,
        ),
        (
            outgoing_frequency * I,
            (total_spin + 1) * I,
            (total_spin - 1) * I,
        ),
    )
else:
    # E_2(2,0) + A_3(1/2,3/2) -> A_5(5/2,3/2).
    E_ambient = ambient_tensor_harmonic(1, 2, 0, 1)
    A3_ambient = ambient_vector_harmonic(1, HALF, R(3, 2), -HALF)
    A5_ambient = ambient_vector_harmonic(2, R(5, 2), R(3, 2), HALF)
    E_covariant = spatial_jacobian.T * E_ambient * spatial_jacobian
    A3_covariant = spatial_jacobian.T * A3_ambient
    A5_covariant = spatial_jacobian.T * A5_ambient
    wave_expressions = [
        tensor_metric_mode(E_covariant, 2, 1 / (4 * sp.sqrt(3)), False),
        vector_metric_mode(A3_covariant, 3, 1 / (2 * sp.sqrt(15)), False),
        vector_metric_mode(A5_covariant, 5, 1 / (2 * sp.sqrt(105)), True),
    ]
    expected_phases = (
        (-2 * I, -2 * I, 0),
        (-3 * I, -HALF * I, -R(3, 2) * I),
        (5 * I, R(5, 2) * I, R(3, 2) * I),
    )

wave_matrices = [jet_matrix_from_expressions(wave) for wave in wave_expressions]


def inverse_metric_by_subsets(
    perturbations: list[list[list[Jet]]],
) -> dict[WaveKey, list[list[Jet]]]:
    inverse: dict[WaveKey, list[list[Jet]]] = {
        frozenset(): background_inverse
    }
    wave_count = len(perturbations)
    for size in range(1, wave_count + 1):
        for mask_integer in range(1, 1 << wave_count):
            key = frozenset(
                wave
                for wave in range(wave_count)
                if mask_integer & (1 << wave)
            )
            if len(key) != size:
                continue
            source = [
                [Jet.zero() for _ in range(4)] for _ in range(4)
            ]
            for wave in key:
                term = jet_matrix_multiply(
                    perturbations[wave], inverse[key - {wave}]
                )
                source = jet_matrix_add(source, term)
            inverse[key] = jet_matrix_scale(
                jet_matrix_multiply(background_inverse, source), -1
            )
    return inverse


inverse_by_key = inverse_metric_by_subsets(wave_matrices)
g_covariant: WaveTensor = {
    frozenset(): matrix_to_components(background_metric)
}
for wave, matrix in enumerate(wave_matrices):
    g_covariant[frozenset({wave})] = matrix_to_components(matrix)
g_contravariant: WaveTensor = {
    key: matrix_to_components(matrix) for key, matrix in inverse_by_key.items()
}

# Verify g_{mu rho} g^{rho nu}=delta_mu^nu in every wave subset.
metric_inverse_product = wt_contract(
    g_covariant, g_contravariant, ((1, 0),)
)
full_key = frozenset(range(3))
check(
    "C1b-3: multilinear inverse metric cancels through three waves",
    all(
        jet_equal(
            wt_component(metric_inverse_product, key, (row, column)),
            Jet.constant(1 if (not key and row == column) else 0),
        )
        for key in inverse_by_key
        for row in range(4)
        for column in range(4)
    ),
)


def relative_trace_expansion() -> WaveTensor:
    relative: WaveTensor = {}
    for wave, perturbation in enumerate(wave_matrices):
        mixed = jet_matrix_multiply(background_inverse, perturbation)
        relative[frozenset({wave})] = matrix_to_components(mixed)
    trace_a = wt_trace(relative, 0, 1)
    square = wt_contract(relative, relative, ((1, 0),))
    trace_a2 = wt_trace(square, 0, 1)
    cube = wt_contract(square, relative, ((1, 0),))
    trace_a3 = wt_trace(cube, 0, 1)

    one: WaveTensor = {frozenset(): {(): Jet.constant(1)}}
    result = wt_add(one, wt_scale(trace_a, R(1, 2)))
    result = wt_add(result, wt_scale(wt_mul(trace_a, trace_a), R(1, 8)))
    result = wt_add(result, wt_scale(trace_a2, -R(1, 4)))
    result = wt_add(
        result, wt_scale(wt_mul(wt_mul(trace_a, trace_a), trace_a), R(1, 48))
    )
    result = wt_add(
        result, wt_scale(wt_mul(trace_a, trace_a2), -R(1, 8))
    )
    result = wt_add(result, wt_scale(trace_a3, R(1, 6)))
    return result


sqrt_background = Jet.from_expression(sp.sin(beta) / 8)
sqrtg = wt_mul(
    {frozenset(): {(): sqrt_background}}, relative_trace_expansion()
)


def curvature(g_lower: WaveTensor, g_upper: WaveTensor) -> WaveTensor:
    derivative_g = wt_derivative(g_lower)
    combination: WaveTensor = {}
    for key, components in derivative_g.items():
        target = combination.setdefault(key, {})
        for (derivative, first, second), value in components.items():
            contributions = (
                ((first, derivative, second), 1),
                ((first, second, derivative), 1),
                ((derivative, first, second), -1),
            )
            for index, sign in contributions:
                target[index] = target.get(index, Jet.zero()) + value.scale(sign)
    combination = wt_scale(combination, HALF)
    combination = wt_reduce(combination)
    christoffel = wt_contract(g_upper, combination, ((1, 0),))
    derivative_christoffel = wt_derivative(christoffel)

    ricci: WaveTensor = {}
    for key, components in derivative_christoffel.items():
        target = ricci.setdefault(key, {})
        for (derivative, upper, first, second), value in components.items():
            if derivative == upper:
                index = (first, second)
                target[index] = target.get(index, Jet.zero()) + value
            if second == upper:
                index = (first, derivative)
                target[index] = target.get(index, Jet.zero()) - value

    # R_mn contains Gamma^rho_{rho lambda} Gamma^lambda_{mn}
    # minus Gamma^rho_{n lambda} Gamma^lambda_{m rho}.  Contract while
    # multiplying instead of building a rank-six outer product.
    christoffel_trace = wt_trace(christoffel, 0, 1)
    first_quadratic = wt_contract(
        christoffel_trace, christoffel, ((0, 0),)
    )
    second_quadratic = wt_contract(
        christoffel, christoffel, ((2, 0), (0, 2))
    )
    second_quadratic = wt_permute(second_quadratic, (1, 0))
    ricci = wt_add_raw(ricci, first_quadratic)
    ricci = wt_add_raw(ricci, wt_scale(second_quadratic, -1))
    return wt_reduce(ricci)


ricci = curvature(g_covariant, g_contravariant)
ricci_scalar = wt_contract(
    g_contravariant, ricci, ((0, 0), (1, 1))
)
ricci_one_up = wt_contract(g_contravariant, ricci, ((1, 0),))
ricci_two_up = wt_contract(g_contravariant, ricci_one_up, ((1, 1),))
ricci_squared = wt_contract(
    ricci_two_up, ricci, ((0, 0), (1, 1))
)

background_ricci = sp.Matrix(
    4,
    4,
    lambda row, column: sp.cancel(
        wt_component(ricci, frozenset(), (row, column)).value()
    ),
)
background_scalar = sp.cancel(
    wt_component(ricci_scalar, frozenset(), ()).value()
)
expected_background_ricci = sp.Matrix(
    [
        [0, 0, 0, 0],
        [0, R(1, 2), 0, sp.cos(beta) / 2],
        [0, 0, R(1, 2), 0],
        [0, sp.cos(beta) / 2, 0, R(1, 2)],
    ]
).applyfunc(beta_to_tangent)
check(
    "C1b-3: perturbiner reproduces Ricci(S3)=2 gamma and R=6",
    background_ricci == expected_background_ricci
    and background_scalar == 6,
)

weyl_reduced_density = wt_mul(
    sqrtg,
    wt_add(
        ricci_squared,
        wt_scale(wt_mul(ricci_scalar, ricci_scalar), -R(1, 3)),
    ),
)
cubic_density = canonical_jet_coefficient(
    wt_component(weyl_reduced_density, full_key, ()).value()
)

# The highest-weight scalar is independent of time, alpha, and gamma.  A
# two-jet curvature calculation determines the density value, but not its
# derivative after two derivatives have already been consumed.  Certify the
# phase cancellation on the external modes themselves instead.
phase_generators = (time, alpha, gamma)
check(
    "C1b-3: external frequencies and azimuthal weights cancel exactly",
    all(
        all(
            sp.simplify(
                sp.diff(wave_expressions[wave][row, column], generator)
                - expected_phases[wave][generator_index]
                * wave_expressions[wave][row, column]
            )
            == 0
            for row in range(4)
            for column in range(4)
        )
        for wave in range(3)
        for generator_index, generator in enumerate(phase_generators)
    ),
)


def tangent_rationalize(expression: sp.Expr) -> tuple[sp.Symbol, sp.Expr]:
    # d beta = 2 dt/(1+t^2).
    return radial_tangent, sp.cancel(
        2 * expression / (1 + radial_tangent**2)
    )


tangent, cubic_integrand = tangent_rationalize(cubic_density)
cubic_spatial_coefficient = sp.simplify(
    8 * sp.pi**2 * sp.integrate(cubic_integrand, (tangent, 0, sp.oo))
)

known_aal_prefactors = {
    (R(1), R(1)): 3 * sp.sqrt(10) / (800 * sp.pi**3),
    (R(1), R(3, 2)): 3 * sp.sqrt(35) / (1120 * sp.pi**3),
    (R(3, 2), R(3, 2)): sp.sqrt(70) / (448 * sp.pi**3),
    (R(1), R(2)): sp.sqrt(5) / (112 * sp.pi**3),
}
spin_key = (
    (min(first_spin, second_spin), max(first_spin, second_spin))
    if channel == "aal"
    else None
)
if channel == "aal" and spin_key in known_aal_prefactors:
    density_power = int(2 * total_spin - 1)
    prefactor = known_aal_prefactors[spin_key]
    expected_density = (
        prefactor
        * radial_tangent
        * (
            (density_power - 1) * radial_tangent**2
            - 1
        )
        / (1 + radial_tangent**2) ** density_power
    )
    primitive = (
        -prefactor
        * radial_tangent**2
        / (1 + radial_tangent**2) ** density_power
    )
    check(
        "C1b-3: AAL local density has the exact highest-weight form",
        canonical_jet_coefficient(cubic_density - expected_density) == 0,
    )
    check(
        "C1b-3: the measured AAL density is an exact radial boundary term",
        sp.cancel(cubic_integrand - sp.diff(primitive, radial_tangent)) == 0
        and sp.limit(primitive, radial_tangent, 0) == 0
        and sp.limit(primitive, radial_tangent, sp.oo) == 0,
    )
    check(
        "C1b-3: complete reduced-Weyl A_J A_K L_(J+K) coefficient cancels",
        cubic_spatial_coefficient == 0,
    )
elif channel == "eaa":
    eaa_prefactor = sp.sqrt(21) / (160 * sp.pi**3)
    expected_density = (
        eaa_prefactor
        * radial_tangent
        * (3 * radial_tangent**2 - 1)
        / (1 + radial_tangent**2) ** 4
    )
    primitive = (
        -eaa_prefactor
        * radial_tangent**2
        / (1 + radial_tangent**2) ** 4
    )
    check(
        "C1b-3: E2 A3 A5 local density has the exact resonant form",
        canonical_jet_coefficient(cubic_density - expected_density) == 0,
    )
    check(
        "C1b-3: the measured EAA density is an exact radial boundary term",
        sp.cancel(cubic_integrand - sp.diff(primitive, radial_tangent)) == 0
        and sp.limit(primitive, radial_tangent, 0) == 0
        and sp.limit(primitive, radial_tangent, sp.oo) == 0,
    )
    check(
        "C1b-3: resonant E2 A3 A5 cylinder coefficient also cancels",
        cubic_spatial_coefficient == 0,
    )
else:
    check(
        "C1b-scan: higher A_J A_K L_(J+K) coefficient is exact",
        not cubic_spatial_coefficient.has(sp.Integral),
    )

print("Reduced-Weyl cubic density:", cubic_density)
print("Reduced-Weyl cubic coefficient:", cubic_spatial_coefficient)


if not PASS:
    raise SystemExit("CONFORMAL C1B HARMONIC SEED: FAIL")

print(f"CONFORMAL C1B {channel.upper()} CYLINDER VERTEX: ALL PASS")
print("Normalized harmonic overlap:", AL_overlap)
