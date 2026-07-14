"""Exhaustive cylinder-jet comparison for the Weyl/Cotton 3+1 system.

This module is the coordinate check complementary to :mod:`weyl_3plus1`.
It reconstructs an arbitrary algebraic Weyl field from ten electric/magnetic
STF components in stereographic cylinder coordinates, computes its covariant
first divergence and Bach image, and compares those results with the exact
normal-frame coefficient tables on every Weyl two-jet at the base point.

There are ``10 * binomial(6,4) = 150`` independent input jets.  The test is
therefore exhaustive for the second-order curvature equations; it is not a
finite harmonic sample.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product

import sympy as sp

from covariant_completion.minimal_witness.cylinder_jets import (
    CylinderJetGeometry,
    Jet,
    _sum,
    _zero,
)
from covariant_completion.minimal_witness.linearized_bach import (
    LinearizedBach,
    _rank,
)

from .weyl_3plus1 import (
    WEYL_DIMENSION,
    WeylCottonBachFirstOrder,
    epsilon,
    stf_basis,
    tracefree_symmetric_spacetime_basis,
)


def _jet_is_zero(value: Jet) -> bool:
    return not value.coefficients


def _jet_equal(left: Jet, right: Jet) -> bool:
    return _jet_is_zero(left - right)


def _canonical_pair(first: int, second: int) -> tuple[tuple[int, int] | None, int]:
    if first == second:
        return None, 0
    if first < second:
        return (first, second), 1
    return (second, first), -1


def _conformal_factor() -> Jet:
    coordinates = tuple(
        Jet.monomial(tuple(1 if axis == index else 0 for axis in range(4)))
        for index in range(4)
    )
    radius_squared = _sum(
        coordinates[index] * coordinates[index] for index in range(1, 4)
    )
    u = Fraction(1, 4) * radius_squared
    # Omega=(1+u)^-1.  Terms u^3 and above have degree at least six and are
    # outside the order-five cylinder jet algebra.
    return Jet.constant(1) - u + u * u


def _stf_tensor(components: tuple[Jet, ...]) -> list[list[Jet]]:
    if len(components) != 5:
        raise ValueError("an STF tensor needs five components")
    basis = stf_basis()
    return [
        [
            _sum(basis[column][first, second] * components[column] for column in range(5))
            for second in range(3)
        ]
        for first in range(3)
    ]


def reconstruct_weyl_jets(
    electric_components: tuple[Jet, ...],
    magnetic_components: tuple[Jet, ...],
) -> list:
    """Reconstruct all-lowered coordinate Weyl jets from spatial STF jets."""

    electric = _stf_tensor(electric_components)
    magnetic = _stf_tensor(magnetic_components)
    omega = _conformal_factor()
    omega_squared = omega * omega
    output = _rank((4, 4, 4, 4))
    for first, second, third, fourth in product(range(4), repeat=4):
        left_pair, left_sign = _canonical_pair(first, second)
        right_pair, right_sign = _canonical_pair(third, fourth)
        if left_pair is None or right_pair is None:
            continue
        left, right = left_pair, right_pair
        if left > right:
            left, right = right, left
        a, b = left
        c, d = right
        if a == 0 and c == 0:
            value = electric[b - 1][d - 1]
        elif a == 0:
            value = omega * _sum(
                epsilon(middle, c - 1, d - 1) * magnetic[middle][b - 1]
                for middle in range(3)
            )
        else:
            value = -omega_squared * _sum(
                epsilon(a - 1, b - 1, middle)
                * epsilon(c - 1, d - 1, other)
                * electric[middle][other]
                for middle in range(3)
                for other in range(3)
            )
        output[first][second][third][fourth] = left_sign * right_sign * value
    return output


def _flatten_rank3(tensor) -> list[Jet]:
    return [tensor[a][b][c] for a, b, c in product(range(4), repeat=3)]


def _flatten_rank2_values(tensor) -> sp.Matrix:
    return sp.Matrix([tensor[a][b].value for a, b in product(range(4), repeat=2)])


def _matrix_times_jets(matrix: sp.Matrix, values: list[Jet]) -> list[Jet]:
    return [
        _sum(matrix[row, column] * values[column] for column in range(matrix.cols))
        for row in range(matrix.rows)
    ]


@dataclass(frozen=True)
class CurvedWeylCottonJetComparison:
    tested_weyl_components: int
    tested_multiindices: int
    tested_two_jets: int
    cotton_coordinate_defects: int
    cotton_reconstruction_defects: int
    bach_coordinate_defects: int
    algebraic_weyl_defects: int

    @staticmethod
    def build() -> "CurvedWeylCottonJetComparison":
        bach_operator = LinearizedBach.build()
        geometry = bach_operator.geometry
        first_order = WeylCottonBachFirstOrder.build()
        decomposition = first_order.decomposition
        multiindices = geometry.exhaustive_multiindices(2)
        cotton_extraction = (
            decomposition.cotton_coordinate_extraction
            * decomposition.cotton_xy_extraction
        )

        target_basis = tracefree_symmetric_spacetime_basis()
        target_inclusion = sp.zeros(16, 9)
        for column, tensor in enumerate(target_basis):
            for a, b in product(range(4), repeat=2):
                target_inclusion[4 * a + b, column] = tensor[a, b]
        target_extraction = (
            (target_inclusion.T * target_inclusion).inv() * target_inclusion.T
        )

        cotton_defects = 0
        cotton_reconstruction_defects = 0
        bach_defects = 0
        algebraic_defects = 0

        for component in range(WEYL_DIMENSION):
            symbols = {
                multiindex: sp.Symbol(
                    "u_" + str(component) + "_" + "".join(map(str, multiindex))
                )
                for multiindex in multiindices
            }
            field = Jet(symbols)
            components = tuple(
                field if index == component else _zero()
                for index in range(WEYL_DIMENSION)
            )
            weyl = reconstruct_weyl_jets(components[:5], components[5:])

            # Algebraic Weyl identities are checked as complete jets, not just
            # at the base point.
            for a, b, c, d in product(range(4), repeat=4):
                if not _jet_equal(weyl[a][b][c][d], -weyl[b][a][c][d]):
                    algebraic_defects += 1
                if not _jet_equal(weyl[a][b][c][d], -weyl[a][b][d][c]):
                    algebraic_defects += 1
                if not _jet_equal(weyl[a][b][c][d], weyl[c][d][a][b]):
                    algebraic_defects += 1
                cyclic = (
                    weyl[a][b][c][d]
                    + weyl[a][c][d][b]
                    + weyl[a][d][b][c]
                )
                if not _jet_is_zero(cyclic):
                    algebraic_defects += 1
            for b, d in product(range(4), repeat=2):
                trace = _sum(
                    geometry.inverse_metric[a][c] * weyl[a][b][c][d]
                    for a, c in product(range(4), repeat=2)
                )
                if not _jet_is_zero(trace):
                    algebraic_defects += 1

            derivative = bach_operator.covariant_derivative_rank4(weyl)
            cotton = _rank((4, 4, 4))
            # V_{mu,nu,sigma}=nabla^rho Psi_{mu,rho,nu,sigma}.
            # This is the divergence convention used by the normal-frame
            # coefficient table.  The equivalent fourth-slot divergence in
            # LinearizedBach is related by the Weyl pair/Bianchi symmetries.
            for mu, nu, sigma in product(range(4), repeat=3):
                cotton[mu][nu][sigma] = _sum(
                    geometry.inverse_metric[rho][axis]
                    * derivative[axis][mu][rho][nu][sigma]
                    for rho, axis in product(range(4), repeat=2)
                )
            cotton_flat = _flatten_rank3(cotton)
            cotton_jets = _matrix_times_jets(cotton_extraction, cotton_flat)
            actual_cotton = sp.Matrix([value.value for value in cotton_jets])
            expected_cotton = sum(
                (
                    first_order.decomposition.cotton_divergence_coefficients[axis]
                    * sp.Matrix(
                        [
                            components[index].derivative(axis).value
                            for index in range(WEYL_DIMENSION)
                        ]
                    )
                    for axis in range(4)
                ),
                sp.zeros(16, 1),
            )
            cotton_defects += sum(
                int(sp.expand(value) != 0)
                for value in actual_cotton - expected_cotton
            )
            reconstructed_cotton = _matrix_times_jets(
                decomposition.cotton_reconstruction, cotton_jets
            )
            cotton_reconstruction_defects += sum(
                int(sp.expand(left.value - right.value) != 0)
                for left, right in zip(
                    reconstructed_cotton, cotton_flat, strict=True
                )
            )

            actual_bach_tensor = bach_operator.standard_bach_from_weyl(weyl)
            actual_bach = target_extraction * _flatten_rank2_values(
                actual_bach_tensor
            )
            cotton_derivatives = tuple(
                sp.Matrix([value.derivative(axis).value for value in cotton_jets])
                for axis in range(4)
            )
            field_value = sp.Matrix([value.value for value in components])
            expected_bach = sum(
                (
                    first_order.bach_derivative_coefficients[axis]
                    * cotton_derivatives[axis]
                    for axis in range(4)
                ),
                first_order.bach_zeroth_coefficient * field_value,
            )
            bach_defects += sum(
                int(sp.expand(value) != 0) for value in actual_bach - expected_bach
            )

        result = CurvedWeylCottonJetComparison(
            tested_weyl_components=WEYL_DIMENSION,
            tested_multiindices=len(multiindices),
            tested_two_jets=WEYL_DIMENSION * len(multiindices),
            cotton_coordinate_defects=cotton_defects,
            cotton_reconstruction_defects=cotton_reconstruction_defects,
            bach_coordinate_defects=bach_defects,
            algebraic_weyl_defects=algebraic_defects,
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.tested_weyl_components != 10:
            raise AssertionError("Weyl component coverage is not exhaustive")
        if self.tested_multiindices != 15 or self.tested_two_jets != 150:
            raise AssertionError("Weyl two-jet coverage is not exhaustive")
        defects = (
            self.cotton_coordinate_defects,
            self.cotton_reconstruction_defects,
            self.bach_coordinate_defects,
            self.algebraic_weyl_defects,
        )
        if any(defects):
            raise AssertionError(f"curved Weyl/Cotton jet defects: {defects}")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-cotton-curved-jet-comparison-v1",
            "background": "R x unit S3 in stereographic spatial coordinates",
            "input_bundle": "Weyl = E_STF[5] + B_STF[5]",
            "input_differential_order": 2,
            "tested_weyl_components": self.tested_weyl_components,
            "tested_multiindices_per_component": self.tested_multiindices,
            "tested_two_jets": self.tested_two_jets,
            "expected_two_jets": 150,
            "coverage_complete": self.tested_two_jets == 150,
            "algebraic_weyl_defects": self.algebraic_weyl_defects,
            "cotton_coordinate_defects": self.cotton_coordinate_defects,
            "cotton_reconstruction_defects": self.cotton_reconstruction_defects,
            "bach_coordinate_defects": self.bach_coordinate_defects,
            "covariant_first_divergence_matches_3plus1_table": (
                self.cotton_coordinate_defects == 0
            ),
            "covariant_Bach_matches_first_order_table": (
                self.bach_coordinate_defects == 0
            ),
            "dual_Bach_covered_by_Hodge_and_exhaustive_input": True,
            "globalization": (
                "the operator comparison is natural and R x SO(4)-equivariant; "
                "complete two-jet vanishing at one point globalizes"
            ),
            "curved_EB_equations": True,
            "curved_EB_first_order_closure": True,
            "symmetric_hyperbolicity_proved": False,
            "sourced_constraint_identity_proved": False,
            "EAL_curvature_spectrum_match": False,
            "fail_closed": True,
        }
