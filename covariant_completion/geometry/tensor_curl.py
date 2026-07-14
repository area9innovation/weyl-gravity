"""Convention certificate for tensor curl on TT tensors on the unit S^3."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

import sympy as sp

from .algebra import (
    DIMENSION,
    epsilon,
    rowspace_contains,
    sphere_curvature,
    symmetric_symbols,
)


@dataclass(frozen=True)
class TensorCurlCertificate:
    """Prove TT preservation, formal adjointness, and the curl square."""

    sphere_radius: sp.Integer = sp.Integer(1)

    @staticmethod
    def _first_derivatives():
        values: dict[tuple[int, int, int], sp.Symbol] = {}
        independent: list[sp.Symbol] = []
        for derivative in range(DIMENSION):
            for first in range(DIMENSION):
                for second in range(first, DIMENSION):
                    symbol = sp.Symbol(f"d{derivative}{first}{second}")
                    values[derivative, first, second] = symbol
                    values[derivative, second, first] = symbol
                    independent.append(symbol)
        return values, tuple(independent)

    @staticmethod
    def _commutator(
        first: int,
        second: int,
        covector_first: int,
        covector_second: int,
        tensor: dict[tuple[int, int], sp.Symbol],
    ) -> sp.Expr:
        return sp.expand(
            sum(
                sphere_curvature(first, second, covector_first, raised)
                * tensor[raised, covector_second]
                + sphere_curvature(first, second, covector_second, raised)
                * tensor[covector_first, raised]
                for raised in range(DIMENSION)
            )
        )

    def verify(self) -> None:
        if self.sphere_radius != 1:
            raise AssertionError("this certificate is normalized to the unit S^3")

        derivatives, variables = self._first_derivatives()

        def derivative(axis: int, first: int, second: int) -> sp.Symbol:
            return derivatives[axis, first, second]

        divergence_constraints = tuple(
            sum(derivative(index, index, second) for index in range(DIMENSION))
            for second in range(DIMENSION)
        )
        trace_constraints = tuple(
            sum(derivative(axis, index, index) for index in range(DIMENSION))
            for axis in range(DIMENSION)
        )
        constraints = divergence_constraints + trace_constraints

        def curl(first: int, second: int) -> sp.Expr:
            return sp.expand(
                sum(
                    epsilon(first, derivative_axis, tensor_axis)
                    * derivative(derivative_axis, tensor_axis, second)
                    for derivative_axis in range(DIMENSION)
                    for tensor_axis in range(DIMENSION)
                )
            )

        # The unsymmetrized displayed formula becomes symmetric on TT data.
        for first, second in product(range(DIMENSION), repeat=2):
            if not rowspace_contains(
                constraints, curl(first, second) - curl(second, first), variables
            ):
                raise AssertionError("tensor curl is not symmetric modulo TT constraints")
        if sp.expand(sum(curl(index, index) for index in range(DIMENSION))) != 0:
            raise AssertionError("tensor curl does not preserve trace")

        tensor, tensor_variables = symmetric_symbols("h")
        trace = sum(tensor[index, index] for index in range(DIMENSION))

        # Curvature conversion of D^n D_i h_(nj) on divergence-free data.
        for first, second in product(range(DIMENSION), repeat=2):
            commutator = sum(
                self._commutator(index, first, index, second, tensor)
                for index in range(DIMENSION)
            )
            if not rowspace_contains(
                (trace,), commutator - 3 * tensor[first, second], tensor_variables
            ):
                raise AssertionError("tensor curvature commutator is not +3 h")

        # Divergence of curl is one half epsilon contracted with the
        # commutator; it vanishes identically on symmetric tensors.
        for second in range(DIMENSION):
            divergence_curl = sp.Rational(1, 2) * sum(
                epsilon(first, derivative_axis, tensor_axis)
                * self._commutator(
                    first, derivative_axis, tensor_axis, second, tensor
                )
                for first, derivative_axis, tensor_axis in product(
                    range(DIMENSION), repeat=3
                )
            )
            if sp.expand(divergence_curl) != 0:
                raise AssertionError("tensor curl does not preserve divergence")

        # epsilon_i^(kl) epsilon_l^(mn)
        for first, derivative_axis, middle, tensor_axis in product(
            range(DIMENSION), repeat=4
        ):
            contraction = sum(
                epsilon(first, derivative_axis, contracted)
                * epsilon(contracted, middle, tensor_axis)
                for contracted in range(DIMENSION)
            )
            expected = sp.Integer(
                first == middle and derivative_axis == tensor_axis
            ) - sp.Integer(first == tensor_axis and derivative_axis == middle)
            if contraction != expected:
                raise AssertionError("wrong epsilon contraction in tensor curl square")

        # Integration by parts gives -epsilon_(i a b)=epsilon_(b a i).
        for first, derivative_axis, target in product(range(DIMENSION), repeat=3):
            if -epsilon(first, derivative_axis, target) != epsilon(
                target, derivative_axis, first
            ):
                raise AssertionError("tensor curl formal-adjoint sign failed")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-tensor-curl-v1",
            "manifold": "unit S^3",
            "domain": "smooth transverse-traceless symmetric two-tensors",
            "definition": "(C_2 h)_ij=epsilon_i^(kl) D_k h_lj",
            "output_symmetric": True,
            "output_tracefree": True,
            "output_transverse": True,
            "formal_self_adjoint": True,
            "curvature_convention": "[D^n,D_i]h_nj=+3h_ij",
            "square_identity": "C_2^2=-D^2+3",
            "tt_harmonic_spectrum": {
                "label": "r>=0",
                "minus_laplacian": "r^2+6r+6",
                "absolute_curl": "r+3",
            },
            "absolute_curl_lower_bound": 3,
        }
