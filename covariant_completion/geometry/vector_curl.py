"""Convention certificate for ordinary curl on transverse one-forms."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

import sympy as sp

from .algebra import DIMENSION, epsilon, sphere_curvature


@dataclass(frozen=True)
class VectorCurlCertificate:
    sphere_radius: sp.Integer = sp.Integer(1)

    @staticmethod
    def _commutator(
        first: int,
        second: int,
        covector: int,
        vector: tuple[sp.Symbol, ...],
    ) -> sp.Expr:
        return sp.expand(
            sum(
                sphere_curvature(first, second, covector, raised) * vector[raised]
                for raised in range(DIMENSION)
            )
        )

    def verify(self) -> None:
        if self.sphere_radius != 1:
            raise AssertionError("this certificate is normalized to the unit S^3")
        vector = sp.symbols("v0:3")

        for first in range(DIMENSION):
            commutator = sum(
                self._commutator(index, first, index, vector)
                for index in range(DIMENSION)
            )
            if sp.expand(commutator - 2 * vector[first]) != 0:
                raise AssertionError("vector curvature commutator is not +2 v")

        # div(curl v)=epsilon^(ikl) D_i D_k v_l/2 and only sees curvature.
        divergence_curl = sp.Rational(1, 2) * sum(
            epsilon(first, second, covector)
            * self._commutator(first, second, covector, vector)
            for first, second, covector in product(range(DIMENSION), repeat=3)
        )
        if sp.expand(divergence_curl) != 0:
            raise AssertionError("vector curl does not preserve transversality")

        for first, derivative_axis, target in product(range(DIMENSION), repeat=3):
            if -epsilon(first, derivative_axis, target) != epsilon(
                target, derivative_axis, first
            ):
                raise AssertionError("vector curl formal-adjoint sign failed")

        for first, derivative_axis, middle, target in product(
            range(DIMENSION), repeat=4
        ):
            contraction = sum(
                epsilon(first, derivative_axis, contracted)
                * epsilon(contracted, middle, target)
                for contracted in range(DIMENSION)
            )
            expected = sp.Integer(first == middle and derivative_axis == target) - sp.Integer(
                first == target and derivative_axis == middle
            )
            if contraction != expected:
                raise AssertionError("wrong epsilon contraction in vector curl square")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-vector-curl-v1",
            "manifold": "unit S^3",
            "domain": "smooth transverse one-forms",
            "definition": "(C_1 v)_i=epsilon_i^(jk) D_j v_k",
            "output_transverse": True,
            "formal_self_adjoint": True,
            "curvature_convention": "[D^n,D_i]v_n=+2v_i",
            "square_identity": "C_1^2=-D^2+2",
            "transverse_harmonic_spectrum": {
                "label": "r>=0",
                "minus_laplacian": "r^2+4r+2",
                "absolute_curl": "r+2",
            },
            "killing_band": {
                "label": "r=0",
                "absolute_curl": 2,
                "excluded_from_metric_A_branch": True,
            },
        }
