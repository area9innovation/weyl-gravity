"""Exact electric/magnetic coordinates on the four-dimensional Weyl bundle.

The conventions are those of the unit Lorentzian cylinder in a positively
oriented normal orthonormal frame:

``g = diag(-1,1,1,1)`` and ``epsilon_0123 = +1``.

For an all-lowered algebraic Weyl tensor ``Psi`` we use

``E_ij = Psi_0i0j`` and
``B_ij = (1/2) epsilon_i{}^{kl} Psi_0jkl``.

Both ``E`` and ``B`` are spatial symmetric trace-free tensors.  This module
constructs the inverse map, verifies every algebraic Weyl identity, and fixes
the Lorentzian Hodge action.  It contains no field equation and deliberately
does not promote any curvature-evolution flag.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp


DIMENSION = 4
SPATIAL = range(1, 4)
SIGNATURE = (-1, 1, 1, 1)


def _stf_matrix(prefix: str) -> sp.Matrix:
    diagonal_11, diagonal_22, off_12, off_13, off_23 = sp.symbols(
        f"{prefix}11 {prefix}22 {prefix}12 {prefix}13 {prefix}23"
    )
    return sp.Matrix(
        [
            [diagonal_11, off_12, off_13],
            [off_12, diagonal_22, off_23],
            [off_13, off_23, -diagonal_11 - diagonal_22],
        ]
    )


def _canonical_pair(first: int, second: int) -> tuple[tuple[int, int], int]:
    if first < second:
        return (first, second), 1
    if second < first:
        return (second, first), -1
    return (first, second), 0


def _spatial_epsilon(first: int, second: int, third: int) -> sp.Integer:
    """Spatial epsilon with indices labelled by spacetime values 1,2,3."""

    return sp.Integer(sp.LeviCivita(first, second, third))


@dataclass(frozen=True)
class WeylElectricMagneticBundle:
    """The exact ten-dimensional algebraic Weyl/STF+STF isomorphism."""

    electric: sp.Matrix
    magnetic: sp.Matrix
    weyl: sp.MutableDenseNDimArray
    hodge_weyl: sp.MutableDenseNDimArray

    @staticmethod
    def reconstruct(
        electric: sp.Matrix, magnetic: sp.Matrix
    ) -> sp.MutableDenseNDimArray:
        if electric.shape != (3, 3) or magnetic.shape != (3, 3):
            raise ValueError("electric and magnetic tensors must be 3 by 3")
        if electric != electric.T or magnetic != magnetic.T:
            raise ValueError("electric and magnetic tensors must be symmetric")
        if sp.simplify(sp.trace(electric)) != 0:
            raise ValueError("electric tensor must be trace free")
        if sp.simplify(sp.trace(magnetic)) != 0:
            raise ValueError("magnetic tensor must be trace free")

        output = sp.MutableDenseNDimArray.zeros(4, 4, 4, 4)
        for first in range(4):
            for second in range(4):
                left_pair, left_sign = _canonical_pair(first, second)
                for third in range(4):
                    for fourth in range(4):
                        right_pair, right_sign = _canonical_pair(third, fourth)
                        if left_sign == 0 or right_sign == 0:
                            continue
                        left, right = left_pair, right_pair
                        if left > right:
                            left, right = right, left
                        a, b = left
                        c, d = right
                        if a == 0 and c == 0:
                            value = electric[b - 1, d - 1]
                        elif a == 0:
                            value = sum(
                                _spatial_epsilon(middle, c, d)
                                * magnetic[middle - 1, b - 1]
                                for middle in SPATIAL
                            )
                        else:
                            value = -sum(
                                _spatial_epsilon(a, b, middle)
                                * _spatial_epsilon(c, d, other)
                                * electric[middle - 1, other - 1]
                                for middle in SPATIAL
                                for other in SPATIAL
                            )
                        output[first, second, third, fourth] = sp.expand(
                            left_sign * right_sign * value
                        )
        return output

    @staticmethod
    def electric_part(tensor: sp.MutableDenseNDimArray) -> sp.Matrix:
        return sp.Matrix(
            3,
            3,
            lambda first, second: tensor[0, first + 1, 0, second + 1],
        )

    @staticmethod
    def magnetic_part(tensor: sp.MutableDenseNDimArray) -> sp.Matrix:
        return sp.Matrix(
            3,
            3,
            lambda first, second: sp.Rational(1, 2)
            * sum(
                _spatial_epsilon(first + 1, left, right)
                * tensor[0, second + 1, left, right]
                for left in SPATIAL
                for right in SPATIAL
            ),
        )

    @staticmethod
    def hodge_first_pair(
        tensor: sp.MutableDenseNDimArray,
    ) -> sp.MutableDenseNDimArray:
        output = sp.MutableDenseNDimArray.zeros(4, 4, 4, 4)
        for first in range(4):
            for second in range(4):
                for third in range(4):
                    for fourth in range(4):
                        output[first, second, third, fourth] = sp.simplify(
                            sp.Rational(1, 2)
                            * sum(
                                sp.LeviCivita(first, second, left, right)
                                * SIGNATURE[left]
                                * SIGNATURE[right]
                                * tensor[left, right, third, fourth]
                                for left in range(4)
                                for right in range(4)
                            )
                        )
        return output

    @staticmethod
    def build() -> "WeylElectricMagneticBundle":
        electric = _stf_matrix("E")
        magnetic = _stf_matrix("B")
        weyl = WeylElectricMagneticBundle.reconstruct(electric, magnetic)
        hodge = WeylElectricMagneticBundle.hodge_first_pair(weyl)
        result = WeylElectricMagneticBundle(
            electric=electric,
            magnetic=magnetic,
            weyl=weyl,
            hodge_weyl=hodge,
        )
        result.verify()
        return result

    def verify(self) -> None:
        tensor = self.weyl
        for a in range(4):
            for b in range(4):
                for c in range(4):
                    for d in range(4):
                        if sp.simplify(tensor[a, b, c, d] + tensor[b, a, c, d]):
                            raise AssertionError("Weyl first-pair antisymmetry failed")
                        if sp.simplify(tensor[a, b, c, d] + tensor[a, b, d, c]):
                            raise AssertionError("Weyl second-pair antisymmetry failed")
                        if sp.simplify(tensor[a, b, c, d] - tensor[c, d, a, b]):
                            raise AssertionError("Weyl pair symmetry failed")
                        bianchi = (
                            tensor[a, b, c, d]
                            + tensor[a, c, d, b]
                            + tensor[a, d, b, c]
                        )
                        if sp.simplify(bianchi):
                            raise AssertionError("Weyl algebraic Bianchi identity failed")

        for b in range(4):
            for d in range(4):
                trace = sum(
                    SIGNATURE[a] * tensor[a, b, a, d] for a in range(4)
                )
                if sp.simplify(trace):
                    raise AssertionError("Weyl trace-free identity failed")

        if self.electric_part(tensor) != self.electric:
            raise AssertionError("electric extraction is not inverse to reconstruction")
        if self.magnetic_part(tensor) != self.magnetic:
            raise AssertionError("magnetic extraction is not inverse to reconstruction")

        hodge_electric = self.electric_part(self.hodge_weyl)
        hodge_magnetic = self.magnetic_part(self.hodge_weyl)
        if hodge_electric != self.magnetic or hodge_magnetic != -self.electric:
            raise AssertionError("Lorentzian Hodge action is not (E,B)->(B,-E)")
        hodge_squared = self.hodge_first_pair(self.hodge_weyl)
        for indices in sp.utilities.iterables.cartes(range(4), repeat=4):
            if sp.simplify(hodge_squared[indices] + tensor[indices]):
                raise AssertionError("Lorentzian Hodge square is not -1")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-curvature-electric-magnetic-bundle-v1",
            "background_frame": "oriented normal orthonormal cylinder frame",
            "signature": "(-,+,+,+)",
            "orientation": "epsilon_0123=+1 and epsilon_123=+1",
            "definitions": {
                "electric": "E_ij=Psi_0i0j",
                "magnetic": "B_ij=(1/2) epsilon_i^{kl} Psi_0jkl",
            },
            "inverse_formulas": {
                "Psi_0i0j": "E_ij",
                "Psi_0ijk": "epsilon_mjk B_mi",
                "Psi_ijkl": "-epsilon_ijm epsilon_kln E_mn",
            },
            "domain": "STF_2(Sigma) direct-sum STF_2(Sigma)",
            "domain_dimension": 10,
            "target": "algebraic Weyl tensors",
            "target_dimension": 10,
            "reconstruction_and_extraction_are_inverse": True,
            "weyl_symmetries_verified": True,
            "algebraic_Bianchi_verified": True,
            "trace_free_verified": True,
            "hodge_action": "star(E,B)=(B,-E)",
            "hodge_square": "-identity",
            "positive_chirality_relation": "star W_+=-i W_+ implies B=-i E",
            "negative_chirality_relation": "star W_-=+i W_- implies B=+i E",
            "field_equations_claimed": False,
            "curved_EB_equations": False,
            "fail_closed": True,
        }
