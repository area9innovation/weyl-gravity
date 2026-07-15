"""Exact low-arity transfer in the suspended graded-symmetric convention.

Let ``q = q1 + q2 + q3 + ...`` be a degree-one coderivation and let
``(iota_cl, pi_cl, s_cl)`` be a strong deformation retract with convention

    q1 s_cl + s_cl q1 = 1 - iota_cl pi_cl.

Taylor tensors use the factorial convention
``q(x) = q1(x) + q2(x,x)/2! + q3(x,x,x)/3! + ...``.  Through arity three,
the transferred tensors are

    ell_2 = pi_cl q2(iota_cl, iota_cl),
    I_2   = -s_cl q2(iota_cl, iota_cl),
    ell_3 = pi_cl(q3(iota_cl^3) + sum_(2,1)-unshuffles q2(I_2, iota_cl)).

All entries are SymPy exact expressions.  Floating-point atoms are rejected.
The implementation verifies the linear SDR and Koszul symmetry/parity of the
provided Taylor tensors.  It does not infer absent classical BV tensors.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
from typing import Sequence

import sympy as sp
from sympy.tensor.array import ImmutableDenseNDimArray, MutableDenseNDimArray


Tensor = ImmutableDenseNDimArray


def _require_exact(name: str, value: object) -> None:
    expressions: list[sp.Expr] = []
    if isinstance(value, sp.MatrixBase):
        expressions = list(value)
    elif isinstance(value, (ImmutableDenseNDimArray, MutableDenseNDimArray)):
        expressions = list(value)
    else:
        expressions = [sp.sympify(value)]
    if any(expression.has(sp.Float) for expression in expressions):
        raise ValueError(f"{name} contains floating-point data")


def _as_tensor(name: str, value: object, shape: tuple[int, ...]) -> Tensor:
    tensor = ImmutableDenseNDimArray(value)
    if tensor.shape != shape:
        raise ValueError(f"{name} has shape {tensor.shape}, expected {shape}")
    _require_exact(name, tensor)
    return tensor


def _zero_tensor(shape: tuple[int, ...]) -> MutableDenseNDimArray:
    return MutableDenseNDimArray.zeros(*shape)


def _koszul_swap(left_parity: int, right_parity: int) -> int:
    return -1 if left_parity and right_parity else 1


def _check_parities(name: str, parities: Sequence[int]) -> tuple[int, ...]:
    result = tuple(parities)
    if not result or any(parity not in (0, 1) for parity in result):
        raise ValueError(f"{name} must be a nonempty sequence of zero/one parities")
    return result


def _check_map_parity(
    name: str,
    matrix: sp.MatrixBase,
    output_parities: Sequence[int],
    input_parities: Sequence[int],
    degree: int,
) -> None:
    for output, input_ in product(range(matrix.rows), range(matrix.cols)):
        if matrix[output, input_] and (
            output_parities[output] - input_parities[input_] - degree
        ) % 2:
            raise ValueError(f"{name}[{output},{input_}] violates parity degree {degree}")


@dataclass(frozen=True)
class Contraction:
    """An exact strong deformation retract of the linear BV differential."""

    q1: sp.ImmutableMatrix
    inclusion: sp.ImmutableMatrix
    projection: sp.ImmutableMatrix
    homotopy: sp.ImmutableMatrix
    full_parities: tuple[int, ...]
    residual_parities: tuple[int, ...]

    @classmethod
    def build(
        cls,
        q1: sp.MatrixBase,
        inclusion: sp.MatrixBase,
        projection: sp.MatrixBase,
        homotopy: sp.MatrixBase,
        *,
        full_parities: Sequence[int],
        residual_parities: Sequence[int],
    ) -> "Contraction":
        result = cls(
            sp.ImmutableMatrix(q1),
            sp.ImmutableMatrix(inclusion),
            sp.ImmutableMatrix(projection),
            sp.ImmutableMatrix(homotopy),
            _check_parities("full_parities", full_parities),
            _check_parities("residual_parities", residual_parities),
        )
        result.verify()
        return result

    @property
    def full_dimension(self) -> int:
        return self.q1.rows

    @property
    def residual_dimension(self) -> int:
        return self.inclusion.cols

    @property
    def residual_differential(self) -> sp.ImmutableMatrix:
        return sp.ImmutableMatrix(self.projection * self.q1 * self.inclusion)

    def verify(self) -> None:
        n = self.q1.rows
        r = self.inclusion.cols
        expected_shapes = {
            "q1": (n, n),
            "inclusion": (n, r),
            "projection": (r, n),
            "homotopy": (n, n),
        }
        for name, matrix in (
            ("q1", self.q1),
            ("inclusion", self.inclusion),
            ("projection", self.projection),
            ("homotopy", self.homotopy),
        ):
            if matrix.shape != expected_shapes[name]:
                raise ValueError(
                    f"{name} has shape {matrix.shape}, expected {expected_shapes[name]}"
                )
            _require_exact(name, matrix)
        if len(self.full_parities) != n or len(self.residual_parities) != r:
            raise ValueError("parity ledgers do not match contraction dimensions")

        _check_map_parity("q1", self.q1, self.full_parities, self.full_parities, 1)
        _check_map_parity(
            "inclusion", self.inclusion, self.full_parities, self.residual_parities, 0
        )
        _check_map_parity(
            "projection", self.projection, self.residual_parities, self.full_parities, 0
        )
        _check_map_parity(
            "homotopy", self.homotopy, self.full_parities, self.full_parities, 1
        )

        ell1 = self.projection * self.q1 * self.inclusion
        identities = {
            "q1_squared": self.q1 * self.q1 == sp.zeros(n),
            "projection_inclusion": self.projection * self.inclusion == sp.eye(r),
            "contraction": self.q1 * self.homotopy + self.homotopy * self.q1
            == sp.eye(n) - self.inclusion * self.projection,
            "inclusion_chain_map": self.q1 * self.inclusion == self.inclusion * ell1,
            "projection_chain_map": self.projection * self.q1 == ell1 * self.projection,
            "homotopy_squared": self.homotopy * self.homotopy == sp.zeros(n),
            "homotopy_inclusion": self.homotopy * self.inclusion == sp.zeros(n, r),
            "projection_homotopy": self.projection * self.homotopy == sp.zeros(r, n),
        }
        failed = [name for name, passed in identities.items() if not passed]
        if failed:
            raise ValueError(f"invalid strong deformation retract: {', '.join(failed)}")


def _verify_taylor_tensor(
    name: str,
    tensor: Tensor,
    parities: Sequence[int],
    arity: int,
) -> None:
    dimension = len(parities)
    for index in product(range(dimension), repeat=arity + 1):
        coefficient = tensor[index]
        if not coefficient:
            continue
        output, inputs = index[0], index[1:]
        if (parities[output] - sum(parities[item] for item in inputs) - 1) % 2:
            raise ValueError(f"{name}{index} violates degree-one parity")
        for position in range(arity - 1):
            swapped = list(index)
            swapped[position + 1], swapped[position + 2] = (
                swapped[position + 2],
                swapped[position + 1],
            )
            sign = _koszul_swap(
                parities[inputs[position]], parities[inputs[position + 1]]
            )
            if coefficient != sign * tensor[tuple(swapped)]:
                raise ValueError(f"{name} is not Koszul symmetric at {index}")


def _unshuffle_sign(
    selected: tuple[int, ...],
    inputs: tuple[int, ...],
    parities: Sequence[int],
) -> int:
    selected_set = set(selected)
    exponent = sum(
        parities[inputs[earlier]] * parities[inputs[later]]
        for later in selected
        for earlier in range(later)
        if earlier not in selected_set
    )
    return (-1) ** exponent


def _taylor_entry(
    arity: int,
    tensor: sp.MatrixBase | Tensor,
    output: int,
    inputs: tuple[int, ...],
) -> sp.Expr:
    if arity == 1:
        assert isinstance(tensor, sp.MatrixBase)
        return tensor[output, inputs[0]]
    assert isinstance(tensor, ImmutableDenseNDimArray)
    return tensor[(output, *inputs)]


def _verify_coderivation_square(
    name: str,
    q1: sp.MatrixBase,
    q2: Tensor,
    q3: Tensor,
    parities: Sequence[int],
) -> None:
    """Verify ``Q^2=0`` coefficientwise through arity three."""

    tensors: dict[int, sp.MatrixBase | Tensor] = {1: q1, 2: q2, 3: q3}
    dimension = len(parities)
    for arity in range(1, 4):
        for output in range(dimension):
            for inputs in product(range(dimension), repeat=arity):
                total = 0
                for inner_arity in range(1, arity + 1):
                    outer_arity = arity - inner_arity + 1
                    for selected in combinations(range(arity), inner_arity):
                        selected_set = set(selected)
                        inner_inputs = tuple(inputs[position] for position in selected)
                        direct_inputs = tuple(
                            inputs[position]
                            for position in range(arity)
                            if position not in selected_set
                        )
                        sign = _unshuffle_sign(selected, inputs, parities)
                        for middle in range(dimension):
                            total += sign * _taylor_entry(
                                outer_arity,
                                tensors[outer_arity],
                                output,
                                (middle, *direct_inputs),
                            ) * _taylor_entry(
                                inner_arity,
                                tensors[inner_arity],
                                middle,
                                inner_inputs,
                            )
                if sp.simplify(total) != 0:
                    raise ValueError(
                        f"{name} coderivation square is nonzero at arity {arity}, "
                        f"output {output}, inputs {inputs}: {total}"
                    )


@dataclass(frozen=True)
class TransferThroughArityThree:
    """Transferred Taylor tensors and the quadratic inclusion correction."""

    ell1: sp.ImmutableMatrix
    ell2: Tensor
    ell3: Tensor
    ell3_contact: Tensor
    ell3_exchange: Tensor
    inclusion2: Tensor


def transfer_through_arity_three(
    contraction: Contraction,
    q2: object,
    q3: object,
) -> TransferThroughArityThree:
    """Transfer ``q2`` and ``q3`` exactly through a verified contraction."""

    n = contraction.full_dimension
    r = contraction.residual_dimension
    q2_tensor = _as_tensor("q2", q2, (n, n, n))
    q3_tensor = _as_tensor("q3", q3, (n, n, n, n))
    _verify_taylor_tensor("q2", q2_tensor, contraction.full_parities, 2)
    _verify_taylor_tensor("q3", q3_tensor, contraction.full_parities, 3)
    _verify_coderivation_square(
        "full", contraction.q1, q2_tensor, q3_tensor, contraction.full_parities
    )

    inclusion2 = _zero_tensor((n, r, r))
    ell2 = _zero_tensor((r, r, r))
    ell3 = _zero_tensor((r, r, r, r))
    ell3_contact = _zero_tensor((r, r, r, r))
    ell3_exchange = _zero_tensor((r, r, r, r))

    for output, left, right in product(range(n), range(r), range(r)):
        inclusion2[output, left, right] = -sum(
            contraction.homotopy[output, target]
            * q2_tensor[target, first, second]
            * contraction.inclusion[first, left]
            * contraction.inclusion[second, right]
            for target, first, second in product(range(n), repeat=3)
        )

    for output, left, right in product(range(r), repeat=3):
        ell2[output, left, right] = sum(
            contraction.projection[output, target]
            * q2_tensor[target, first, second]
            * contraction.inclusion[first, left]
            * contraction.inclusion[second, right]
            for target, first, second in product(range(n), repeat=3)
        )

    for output, first_input, second_input, third_input in product(
        range(r), repeat=4
    ):
        contact = sum(
            contraction.projection[output, target]
            * q3_tensor[target, first, second, third]
            * contraction.inclusion[first, first_input]
            * contraction.inclusion[second, second_input]
            * contraction.inclusion[third, third_input]
            for target, first, second, third in product(range(n), repeat=4)
        )
        parity_first = contraction.residual_parities[first_input]
        parity_second = contraction.residual_parities[second_input]
        parity_third = contraction.residual_parities[third_input]
        unshuffles = (
            (first_input, second_input, third_input, 1),
            (
                first_input,
                third_input,
                second_input,
                _koszul_swap(parity_second, parity_third),
            ),
            (
                second_input,
                third_input,
                first_input,
                (-1) ** (parity_first * (parity_second + parity_third)),
            ),
        )
        exchange = 0
        for paired_left, paired_right, singleton, sign in unshuffles:
            exchange += sign * sum(
                contraction.projection[output, target]
                * q2_tensor[target, inner, direct]
                * inclusion2[inner, paired_left, paired_right]
                * contraction.inclusion[direct, singleton]
                for target, inner, direct in product(range(n), repeat=3)
            )
        index = (output, first_input, second_input, third_input)
        ell3_contact[index] = contact
        ell3_exchange[index] = exchange
        ell3[index] = contact + exchange

    result = TransferThroughArityThree(
        contraction.residual_differential,
        ImmutableDenseNDimArray(ell2),
        ImmutableDenseNDimArray(ell3),
        ImmutableDenseNDimArray(ell3_contact),
        ImmutableDenseNDimArray(ell3_exchange),
        ImmutableDenseNDimArray(inclusion2),
    )
    _verify_taylor_tensor("ell2", result.ell2, contraction.residual_parities, 2)
    _verify_taylor_tensor("ell3", result.ell3, contraction.residual_parities, 3)
    _verify_coderivation_square(
        "transferred",
        result.ell1,
        result.ell2,
        result.ell3,
        contraction.residual_parities,
    )
    return result
