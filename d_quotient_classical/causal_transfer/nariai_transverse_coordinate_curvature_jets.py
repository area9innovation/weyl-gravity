"""Exact coordinate derivation of transverse Nariai curvature jets.

The jet-aware PBW calculation needs covariant derivatives of the variation
of the Levi-Civita curvature, not merely derivatives of its scalar sectional
coefficients.  This module differentiates the full mixed tensor

    C_i{}^j{}_{ab} = -R^j{}_{iab}

for the Kantowski--Sachs family and then converts it to the background
orthonormal frame at ``sinh(t)=1, theta=pi/2``.  The recurrence is linearized
before evaluation, so every connection action on every tensor slot is kept.
"""

from __future__ import annotations

from functools import lru_cache
from itertools import product

import sympy as sp


Index = tuple[int, ...]
SparseTensor = dict[Index, sp.Expr]
Poly2 = dict[tuple[int, int], sp.Expr]
PolyTensor = dict[Index, Poly2]


t, chi, theta, phi, epsilon = sp.symbols(
    "t chi theta phi epsilon", real=True
)
COORDINATES = (t, chi, theta, phi)
X, Y = sp.symbols("X Y")
MAX_JET_ORDER = 3


def _coefficient(value: sp.Expr, order: int) -> sp.Expr:
    return sp.expand(value).coeff(epsilon, order)


@lru_cache(maxsize=1)
def connections() -> tuple[tuple[tuple[sp.Expr, ...], ...], tuple[tuple[sp.Expr, ...], ...]]:
    """Return ``(Gamma_0, dot Gamma)`` for the exact perturbed metric."""

    alpha = -sp.sinh(2 * t) / 3
    beta = sp.sinh(t)
    a = sp.cosh(t) + epsilon * alpha
    b = 1 + epsilon * beta
    metric = sp.diag(-1, a**2, b**2, b**2 * sp.sin(theta) ** 2)
    inverse = metric.inv()
    gamma = [[[sp.Integer(0) for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for output, derivative, source in product(range(4), repeat=3):
        gamma[output][derivative][source] = sp.simplify(
            sum(
                inverse[output, contracted]
                * (
                    sp.diff(metric[contracted, source], COORDINATES[derivative])
                    + sp.diff(metric[contracted, derivative], COORDINATES[source])
                    - sp.diff(metric[derivative, source], COORDINATES[contracted])
                )
                for contracted in range(4)
            )
            / 2
        )
    base = tuple(
        tuple(
            tuple(sp.simplify(gamma[o][a][b].subs(epsilon, 0)) for b in range(4))
            for a in range(4)
        )
        for o in range(4)
    )
    delta = tuple(
        tuple(
            tuple(
                sp.simplify(sp.diff(gamma[o][a][b], epsilon).subs(epsilon, 0))
                for b in range(4)
            )
            for a in range(4)
        )
        for o in range(4)
    )
    return base, delta


def _riemann(
    gamma: tuple[tuple[tuple[sp.Expr, ...], ...], ...]
) -> SparseTensor:
    """Return ``R^rho{}_{sigma mu nu}`` as a sparse tensor."""

    result: SparseTensor = {}
    for rho, sigma, mu, nu in product(range(4), repeat=4):
        value = (
            sp.diff(gamma[rho][nu][sigma], COORDINATES[mu])
            - sp.diff(gamma[rho][mu][sigma], COORDINATES[nu])
            + sum(
                gamma[rho][mu][lam] * gamma[lam][nu][sigma]
                - gamma[rho][nu][lam] * gamma[lam][mu][sigma]
                for lam in range(4)
            )
        )
        value = sp.simplify(sp.expand_trig(value))
        if value != 0:
            result[(rho, sigma, mu, nu)] = value
    return result


@lru_cache(maxsize=1)
def covector_curvature() -> tuple[SparseTensor, SparseTensor]:
    """Return base and first variation of ``C_i{}^j{}_{ab}``."""

    gamma0, gamma1 = connections()
    r0 = _riemann(gamma0)
    # Linearized Riemann is obtained by a dual-number connection.  This keeps
    # the quadratic Gamma_0 Gamma_1 terms without expanding the full metric a
    # second time.
    dual = tuple(
        tuple(
            tuple(gamma0[o][a][b] + epsilon * gamma1[o][a][b] for b in range(4))
            for a in range(4)
        )
        for o in range(4)
    )
    rdual = _riemann(dual)
    base: SparseTensor = {}
    delta: SparseTensor = {}
    for output, source, left, right in product(range(4), repeat=4):
        # Covector convention: C_output{}^source = -R^source{}_{output}.
        value0 = -r0.get((source, output, left, right), sp.Integer(0))
        value1 = -_coefficient(
            rdual.get((source, output, left, right), sp.Integer(0)), 1
        )
        if value0 != 0:
            base[(output, left, right, source)] = value0
        if value1 != 0:
            delta[(output, left, right, source)] = sp.simplify(value1)
    return base, delta


def covariant_derivative(
    tensor: SparseTensor,
    lower_count: int,
    upper_count: int,
    gamma: tuple[tuple[tuple[sp.Expr, ...], ...], ...],
) -> SparseTensor:
    """Apply the base covariant derivative, adding its lower slot first."""

    if upper_count != 1:
        raise NotImplementedError("the curvature-jet audit has one upper slot")
    accumulated: dict[Index, sp.Expr] = {}

    def add(key: Index, value: sp.Expr) -> None:
        if value != 0:
            accumulated[key] = accumulated.get(key, sp.Integer(0)) + value

    for index, tensor_value in tensor.items():
        for derivative, coordinate in enumerate(COORDINATES):
            add((derivative,) + index, sp.diff(tensor_value, coordinate))
            # Rewrite the output index directly from each nonzero source
            # component.  This is equivalent to the dense formula but avoids
            # simplifying 4^(rank+1) zeros at every jet order.
            for position in range(lower_count):
                source_value = index[position]
                for output_value in range(4):
                    changed = list(index)
                    changed[position] = output_value
                    add(
                        (derivative,) + tuple(changed),
                        -gamma[source_value][derivative][output_value] * tensor_value,
                    )
            upper_position = lower_count
            source_value = index[upper_position]
            for output_value in range(4):
                changed = list(index)
                changed[upper_position] = output_value
                add(
                    (derivative,) + tuple(changed),
                    gamma[output_value][derivative][source_value] * tensor_value,
                )
    result: SparseTensor = {}
    for key, value in accumulated.items():
        value = sp.simplify(sp.expand_trig(value))
        if value != 0:
            result[key] = value
    return result


def connection_variation_action(
    tensor: SparseTensor,
    lower_count: int,
    upper_count: int,
    gamma_delta: tuple[tuple[tuple[sp.Expr, ...], ...], ...],
) -> SparseTensor:
    """Apply ``dot Gamma`` to every old slot while adding a derivative slot."""

    if upper_count != 1:
        raise NotImplementedError("the curvature-jet audit has one upper slot")
    accumulated: dict[Index, sp.Expr] = {}

    def add(key: Index, value: sp.Expr) -> None:
        if value != 0:
            accumulated[key] = accumulated.get(key, sp.Integer(0)) + value

    for index, tensor_value in tensor.items():
        for derivative in range(4):
            for position in range(lower_count):
                source_value = index[position]
                for output_value in range(4):
                    changed = list(index)
                    changed[position] = output_value
                    add(
                        (derivative,) + tuple(changed),
                        -gamma_delta[source_value][derivative][output_value]
                        * tensor_value,
                    )
            upper_position = lower_count
            source_value = index[upper_position]
            for output_value in range(4):
                changed = list(index)
                changed[upper_position] = output_value
                add(
                    (derivative,) + tuple(changed),
                    gamma_delta[output_value][derivative][source_value]
                    * tensor_value,
                )
    result: SparseTensor = {}
    for key, value in accumulated.items():
        value = sp.simplify(sp.expand_trig(value))
        if value != 0:
            result[key] = value
    return result


def _add(left: SparseTensor, right: SparseTensor) -> SparseTensor:
    keys = set(left) | set(right)
    return {
        key: value
        for key in keys
        if (value := sp.simplify(left.get(key, 0) + right.get(key, 0))) != 0
    }


def _poly_add(left: Poly2, right: Poly2) -> Poly2:
    output: Poly2 = dict(left)
    for powers, value in right.items():
        coefficient = sp.expand(output.get(powers, 0) + value)
        if coefficient == 0:
            output.pop(powers, None)
        else:
            output[powers] = coefficient
    return output


def _poly_scale(value: Poly2, scalar: sp.Expr) -> Poly2:
    if scalar == 0:
        return {}
    return {
        powers: coefficient
        for powers, coefficient0 in value.items()
        if (coefficient := sp.expand(scalar * coefficient0)) != 0
    }


def _poly_mul(left: Poly2, right: Poly2, degree: int) -> Poly2:
    output: Poly2 = {}
    for (li, lj), lvalue in left.items():
        for (ri, rj), rvalue in right.items():
            powers = (li + ri, lj + rj)
            if sum(powers) <= degree:
                output = _poly_add(output, {powers: lvalue * rvalue})
    return output


def _poly_derivative(value: Poly2, axis: int) -> Poly2:
    output: Poly2 = {}
    position = 0 if axis == 0 else 1
    for powers, coefficient in value.items():
        exponent = powers[position]
        if exponent:
            changed = list(powers)
            changed[position] -= 1
            output[tuple(changed)] = sp.expand(exponent * coefficient)
    return output


def _taylor_at_star(value: sp.Expr, degree: int = MAX_JET_ORDER) -> Poly2:
    result: Poly2 = {}
    for t_order in range(degree + 1):
        for theta_order in range(degree + 1 - t_order):
            derivative = sp.diff(value, t, t_order, theta, theta_order)
            coefficient = _at_star(derivative) / (
                sp.factorial(t_order) * sp.factorial(theta_order)
            )
            coefficient = sp.expand(coefficient)
            if coefficient != 0:
                result[(t_order, theta_order)] = coefficient
    return result


@lru_cache(maxsize=1)
def polynomial_connections():
    gamma0, gamma1 = connections()
    convert = lambda gamma: tuple(
        tuple(
            tuple(_taylor_at_star(gamma[o][a][b]) for b in range(4))
            for a in range(4)
        )
        for o in range(4)
    )
    return convert(gamma0), convert(gamma1)


@lru_cache(maxsize=1)
def polynomial_covector_curvature() -> tuple[SparseTensor, SparseTensor]:
    base, delta = covector_curvature()
    return (
        {key: _taylor_at_star(value) for key, value in base.items()},
        {key: _taylor_at_star(value) for key, value in delta.items()},
    )


def polynomial_covariant_derivative(
    tensor: PolyTensor,
    lower_count: int,
    gamma,
    degree: int,
) -> PolyTensor:
    accumulated: PolyTensor = {}

    def add(key: Index, value: Poly2) -> None:
        if value:
            accumulated[key] = _poly_add(accumulated.get(key, {}), value)

    for index, tensor_value in tensor.items():
        for derivative in range(4):
            partial = (
                _poly_derivative(tensor_value, 0)
                if derivative == 0
                else _poly_derivative(tensor_value, 2)
                if derivative == 2
                else {}
            )
            add((derivative,) + index, partial)
            for position in range(lower_count):
                source_value = index[position]
                for output_value in range(4):
                    changed = list(index)
                    changed[position] = output_value
                    add(
                        (derivative,) + tuple(changed),
                        _poly_scale(
                            _poly_mul(
                                gamma[source_value][derivative][output_value],
                                tensor_value,
                                degree,
                            ),
                            -1,
                        ),
                    )
            source_value = index[lower_count]
            for output_value in range(4):
                changed = list(index)
                changed[lower_count] = output_value
                add(
                    (derivative,) + tuple(changed),
                    _poly_mul(
                        gamma[output_value][derivative][source_value],
                        tensor_value,
                        degree,
                    ),
                )
    return {key: value for key, value in accumulated.items() if value}


def polynomial_connection_variation_action(
    tensor: PolyTensor,
    lower_count: int,
    gamma_delta,
    degree: int,
) -> PolyTensor:
    accumulated: PolyTensor = {}

    def add(key: Index, value: Poly2) -> None:
        if value:
            accumulated[key] = _poly_add(accumulated.get(key, {}), value)

    for index, tensor_value in tensor.items():
        for derivative in range(4):
            for position in range(lower_count):
                source_value = index[position]
                for output_value in range(4):
                    changed = list(index)
                    changed[position] = output_value
                    add(
                        (derivative,) + tuple(changed),
                        _poly_scale(
                            _poly_mul(
                                gamma_delta[source_value][derivative][output_value],
                                tensor_value,
                                degree,
                            ),
                            -1,
                        ),
                    )
            source_value = index[lower_count]
            for output_value in range(4):
                changed = list(index)
                changed[lower_count] = output_value
                add(
                    (derivative,) + tuple(changed),
                    _poly_mul(
                        gamma_delta[output_value][derivative][source_value],
                        tensor_value,
                        degree,
                    ),
                )
    return {key: value for key, value in accumulated.items() if value}


def _poly_tensor_add(left: PolyTensor, right: PolyTensor) -> PolyTensor:
    output: PolyTensor = dict(left)
    for key, value in right.items():
        combined = _poly_add(output.get(key, {}), value)
        if combined:
            output[key] = combined
        else:
            output.pop(key, None)
    return output


@lru_cache(maxsize=None)
def coordinate_delta_jet(order: int) -> PolyTensor:
    """Return ``dot(nabla^order C)`` in the coordinate frame."""

    if order < 0:
        raise ValueError(order)
    gamma0, gamma1 = polynomial_connections()
    base, delta = polynomial_covector_curvature()
    if order == 0:
        return delta
    first = _poly_tensor_add(
        polynomial_covariant_derivative(delta, 3, gamma0, MAX_JET_ORDER - 1),
        polynomial_connection_variation_action(base, 3, gamma1, MAX_JET_ORDER - 1),
    )
    value = first
    # The Nariai base curvature is parallel, so every positive-order base jet
    # vanishes.  Higher variations are therefore ordinary base covariant
    # derivatives of the preceding varied jet.
    for current_order in range(1, order):
        value = polynomial_covariant_derivative(
            value,
            3 + current_order,
            gamma0,
            MAX_JET_ORDER - current_order - 1,
        )
    return value


def _at_star(value: sp.Expr) -> sp.Expr:
    evaluated = sp.expand_trig(value).subs(
        {
            sp.sinh(t): sp.Integer(1),
            sp.cosh(t): sp.sqrt(2),
            sp.tanh(t): 1 / sp.sqrt(2),
        }
    )
    if theta in evaluated.free_symbols:
        evaluated = sp.limit(evaluated, theta, sp.pi / 2)
    else:
        evaluated = evaluated.subs(
            {
                sp.sin(theta): sp.Integer(1),
                sp.cos(theta): sp.Integer(0),
                sp.cot(theta): sp.Integer(0),
            }
        )
    return sp.simplify(evaluated)


def orthonormal_covector_jet(
    word: tuple[int, ...], left: int, right: int
) -> sp.Matrix:
    """Evaluate one varied curvature jet as a 4x4 covector endomorphism."""

    order = len(word)
    tensor = coordinate_delta_jet(order)
    # At the evaluation point the background orthonormal frame is diagonal.
    frame = (sp.Integer(1), 1 / sp.sqrt(2), sp.Integer(1), sp.Integer(1))
    coframe = tuple(1 / value for value in frame)
    matrix = sp.zeros(4)
    for output, source in product(range(4), repeat=2):
        coordinate_index = word + (output, left, right, source)
        # Tensor order is: derivative slots, output-lower, left-lower,
        # right-lower, source-upper.
        value = tensor.get(coordinate_index, {}).get((0, 0), sp.Integer(0))
        factor = (
            sp.prod(frame[axis] for axis in word)
            * frame[output]
            * frame[left]
            * frame[right]
            * coframe[source]
        )
        matrix[output, source] = _at_star(factor * value)
    return matrix


if __name__ == "__main__":
    for order in range(4):
        tensor = coordinate_delta_jet(order)
        print(order, len(tensor))
