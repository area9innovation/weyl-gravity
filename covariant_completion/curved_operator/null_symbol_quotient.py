"""Exact quotient and helicity analysis of the obstructing null symbol.

The scalar-wave no-go is stronger when its two excess directions are kept as
positive data.  This module computes the quotient

``im(N_2(zeta))/im(K_1(zeta))``,  ``N_2=J_act^{-1}E_2``,

at ``zeta=(1,1,0,0)`` and identifies its transverse real helicity-two
representation.  It also evaluates the exact principal linearized Weyl
symbol and proves that the induced map between the corresponding two
dimensional quotients is an isomorphism.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path

import sympy as sp

from covariant_completion.minimal_witness.linearized_bach import LinearizedBach

from .conventions import CurvedBVConventions, SYMMETRIC_COORDINATES, _ordinary_system
from .covariant_jets import CovariantJetBasis
from .expanded_hessian import load_coefficient_cache
from .invariant_pairings import _rotation_generators, _tensor_representation
from .null_symbol_rank_obstruction import DEFAULT_CACHE


def _sparse_column(vector: sp.Matrix) -> list[list[object]]:
    return [
        [index, str(vector[index])]
        for index in range(vector.rows)
        if vector[index] != 0
    ]


def _digest(matrix: sp.Matrix) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableDenseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _field_label(index: int) -> str:
    if index < 10:
        a, b = SYMMETRIC_COORDINATES[index]
        return f"h_({a},{b})"
    if index < 20:
        a, b = SYMMETRIC_COORDINATES[index - 10]
        return f"f_({a},{b})"
    return f"v_{index - 20}"


@dataclass(frozen=True)
class CurvedNullSymbolQuotient:
    hessian_kernel_dimension: int
    hessian_cokernel_dimension: int
    field_operator_rank: int
    gauge_image_dimension: int
    combined_image_dimension: int
    image_intersection_dimension: int
    quotient_dimension: int
    gauge_image_basis: tuple[dict[str, object], ...]
    quotient_basis: tuple[dict[str, object], ...]
    hessian_quotient_matrix: sp.Matrix
    little_group_generator: sp.Matrix
    weyl_symbol_rank: int
    weyl_descent_stack_rank: int
    weyl_image_of_gauge_preimages_rank: int
    weyl_target_quotient_dimension: int
    induced_weyl_matrix: sp.Matrix
    electric_weyl_matrix: sp.Matrix
    weyl_image_nonzero_counts: tuple[int, int]
    weyl_image_squared_coordinate_norms: tuple[sp.Expr, sp.Expr]
    weyl_symbol_sha256: str

    @staticmethod
    def build(cache_path: Path = DEFAULT_CACHE) -> "CurvedNullSymbolQuotient":
        zeta, hessian, _ = load_coefficient_cache(cache_path)
        scale = sp.Symbol("null_quotient_scale")
        principal = hessian.applyfunc(
            lambda value: sp.expand(
                value.subs({entry: scale * entry for entry in zeta})
            ).coeff(scale, 2)
        )
        null_covector = (1, 1, 0, 0)
        hessian_at_null = principal.subs(dict(zip(zeta, null_covector, strict=True)))
        source = _ordinary_system()
        field_operator = source.field_fibre_pairing.inv() * hessian_at_null
        conventions = CurvedBVConventions.build()
        gauge = sum(
            (
                null_covector[axis]
                * conventions.gauge_generator.derivative_coefficients[axis]
                for axis in range(4)
            ),
            sp.zeros(24, 9),
        )

        gauge_basis = tuple(
            {
                "ghost_column": column,
                "ghost_label": (
                    f"xi_{column}"
                    if column < 4
                    else f"kappa_{column - 4}"
                    if column < 8
                    else "sigma"
                ),
                "nonzero_components": _sparse_column(gauge[:, column]),
                "component_labels": [
                    _field_label(index)
                    for index in range(24)
                    if gauge[index, column] != 0
                ],
            }
            for column in range(9)
        )

        first = sp.zeros(24, 1)
        first[17] = 1
        first[19] = -1
        second = sp.zeros(24, 1)
        second[18] = 1
        gauge_subtraction = sp.Matrix(
            [sp.Rational(1, 2), sp.Rational(1, 2), 0, 0, -2, 2, 0, 0, 0]
        )
        if field_operator[:, 7] - gauge * gauge_subtraction != 2 * first:
            raise AssertionError("first normalized quotient representative drifted")
        if field_operator[:, 8] != 4 * second:
            raise AssertionError("second normalized quotient representative drifted")
        quotient_basis = (
            {
                "name": "f_22_minus_f_33",
                "normalized_representative": _sparse_column(first),
                "relation": "u1=(N e7-K a)/2",
                "gauge_coefficients_a": [str(value) for value in gauge_subtraction],
            },
            {
                "name": "f_23",
                "normalized_representative": _sparse_column(second),
                "relation": "u2=N e8/4",
                "gauge_coefficients_a": ["0"] * 9,
            },
        )
        physical_domain = sp.zeros(24, 2)
        physical_domain[7, 0] = 1
        physical_domain[9, 0] = -1
        physical_domain[8, 1] = 1
        physical_codomain = sp.Matrix.hstack(first, second)
        if field_operator * physical_domain != 4 * physical_codomain:
            raise AssertionError("physical normalized Hessian quotient block drifted")
        hessian_quotient = 4 * sp.eye(2)

        # The second cylinder rotation generator fixes zeta and rotates the
        # transverse (2,3)-plane.  Derive, rather than assume, its action on
        # the normalized quotient representatives.
        field_rotation = sp.zeros(24)
        field_rotation[10:20, 10:20] = _tensor_representation(
            _rotation_generators()[1]
        )
        if field_rotation * first != -2 * second:
            raise AssertionError("transverse rotation of f22-f33 drifted")
        if field_rotation * second != 2 * first:
            raise AssertionError("transverse rotation of f23 drifted")
        little_group = sp.Matrix([[0, 2], [-2, 0]])

        # Exact principal linearized Weyl symbol.  Flattening all 4^4 tensor
        # slots avoids choosing Weyl symmetries while computing ranks.
        basis = CovariantJetBasis.build()
        linearized_bach = LinearizedBach.build()
        weyl = sp.zeros(4**4, 24)
        degree_two = tuple(
            multiindex
            for multiindex in basis.geometry.exhaustive_multiindices(2)
            if sum(multiindex) == 2
        )
        for component in range(10):
            for multiindex in degree_two:
                weight = sp.prod(
                    null_covector[axis] ** multiindex[axis]
                    for axis in range(4)
                )
                if weight == 0:
                    continue
                tensor = basis.covariant_monomial_symmetric(
                    component, multiindex, 2
                )
                image = linearized_bach.linearized_weyl(tensor)
                row = 0
                for a in range(4):
                    for b in range(4):
                        for c in range(4):
                            for d in range(4):
                                weyl[row, component] += (
                                    weight * image[a][b][c][d].value
                                )
                                row += 1

        # ker(N) subset ker(W), hence W descends from im(N).  Pick exact
        # preimages X of im(K); W X is the three-dimensional subspace divided
        # out on the Weyl side.
        preimages = sp.zeros(24, 9)
        for column in range(9):
            solution, _ = field_operator.gauss_jordan_solve(gauge[:, column])
            solution = solution.subs(
                {symbol: 0 for symbol in solution.free_symbols}
            )
            preimages[:, column] = solution
        if field_operator * preimages != gauge:
            raise AssertionError("exact gauge-image preimages drifted")
        weyl_gauge = weyl * preimages

        # In the normalized domain quotient basis u1,u2, choose the natural
        # target basis W(h22-h33),W(h23).  The first relation uses
        # N(e7+e9)=K(1,1,0,0,-4,4,0,0,0), so it is exact modulo W X.
        relation = sp.Matrix([1, 1, 0, 0, -4, 4, 0, 0, 0])
        if field_operator[:, 7] + field_operator[:, 9] != gauge * relation:
            raise AssertionError("Weyl quotient first-basis relation drifted")
        physical_weyl_basis = sp.Matrix.hstack(
            weyl[:, 7] - weyl[:, 9], weyl[:, 8]
        )
        if weyl_gauge.row_join(physical_weyl_basis).rank() != 5:
            raise AssertionError("physical Weyl quotient basis is not exhaustive")
        induced_weyl = sp.Rational(1, 4) * sp.eye(2)

        def flat_index(a: int, b: int, c: int, d: int) -> int:
            return ((a * 4 + b) * 4 + c) * 4 + d

        electric_rows = (flat_index(0, 2, 0, 2), flat_index(0, 2, 0, 3))
        physical_weyl = weyl * physical_domain
        electric_weyl = physical_weyl.extract(electric_rows, (0, 1))

        combined_rank = field_operator.row_join(gauge).rank()
        intersection = field_operator.rank() + gauge.rank() - combined_rank
        result = CurvedNullSymbolQuotient(
            hessian_kernel_dimension=24 - hessian_at_null.rank(),
            hessian_cokernel_dimension=24 - hessian_at_null.rank(),
            field_operator_rank=field_operator.rank(),
            gauge_image_dimension=gauge.rank(),
            combined_image_dimension=combined_rank,
            image_intersection_dimension=intersection,
            quotient_dimension=field_operator.rank() - intersection,
            gauge_image_basis=gauge_basis,
            quotient_basis=quotient_basis,
            hessian_quotient_matrix=hessian_quotient,
            little_group_generator=little_group,
            weyl_symbol_rank=weyl.rank(),
            weyl_descent_stack_rank=sp.Matrix.vstack(field_operator, weyl).rank(),
            weyl_image_of_gauge_preimages_rank=weyl_gauge.rank(),
            weyl_target_quotient_dimension=(
                weyl.rank() - weyl_gauge.rank()
            ),
            induced_weyl_matrix=induced_weyl,
            electric_weyl_matrix=electric_weyl,
            weyl_image_nonzero_counts=tuple(
                sum(1 for value in physical_weyl[:, column] if value != 0)
                for column in range(2)
            ),
            weyl_image_squared_coordinate_norms=tuple(
                sp.simplify(
                    (physical_weyl[:, column].T * physical_weyl[:, column])[0]
                )
                for column in range(2)
            ),
            weyl_symbol_sha256=_digest(weyl),
        )
        result.verify()
        return result

    def verify(self) -> None:
        if (self.hessian_kernel_dimension, self.hessian_cokernel_dimension) != (
            13,
            13,
        ):
            raise AssertionError("null Hessian kernel/cokernel dimensions drifted")
        if (
            self.field_operator_rank,
            self.gauge_image_dimension,
            self.combined_image_dimension,
            self.image_intersection_dimension,
            self.quotient_dimension,
        ) != (11, 9, 11, 9, 2):
            raise AssertionError("null field/gauge quotient dimensions drifted")
        if len(self.gauge_image_basis) != 9:
            raise AssertionError("gauge-image basis is incomplete")
        if self.little_group_generator**2 != -4 * sp.eye(2):
            raise AssertionError("helicity-two little-group action drifted")
        if self.hessian_quotient_matrix != 4 * sp.eye(2):
            raise AssertionError("normalized Hessian quotient block drifted")
        if (
            self.weyl_symbol_rank,
            self.weyl_descent_stack_rank,
            self.weyl_image_of_gauge_preimages_rank,
            self.weyl_target_quotient_dimension,
        ) != (5, 11, 3, 2):
            raise AssertionError("linearized Weyl quotient dimensions drifted")
        if self.induced_weyl_matrix != sp.Rational(1, 4) * sp.eye(2):
            raise AssertionError("induced Weyl quotient map drifted")
        if self.induced_weyl_matrix.det() == 0:
            raise AssertionError("induced Weyl quotient map lost invertibility")
        if self.electric_weyl_matrix != -sp.Rational(1, 2) * sp.eye(2):
            raise AssertionError("electric helicity-two Weyl symbol drifted")
        if self.weyl_image_nonzero_counts != (32, 32):
            raise AssertionError("Weyl image support count drifted")
        if self.weyl_image_squared_coordinate_norms != (8, 8):
            raise AssertionError("Weyl image coordinate norm drifted")

    def quotient_certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-curved-null-symbol-quotient-v1",
            "atomic_flag": "curved_null_symbol_quotient_exact",
            "curved_null_symbol_quotient_exact": True,
            "covector": [1, 1, 0, 0],
            "E_2_kernel_dimension": self.hessian_kernel_dimension,
            "E_2_cokernel_dimension": self.hessian_cokernel_dimension,
            "rank_N": self.field_operator_rank,
            "rank_K": self.gauge_image_dimension,
            "rank_concatenated_N_K": self.combined_image_dimension,
            "image_intersection_dimension": self.image_intersection_dimension,
            "image_N_mod_image_K_dimension": self.quotient_dimension,
            "im_K_basis": list(self.gauge_image_basis),
            "normalized_quotient_basis": list(self.quotient_basis),
            "physical_normalized_block": {
                "domain_basis": ["h_22-h_33", "h_23"],
                "codomain_basis": ["f_22-f_33", "f_23"],
                "matrix": [
                    [str(value) for value in row]
                    for row in self.hessian_quotient_matrix.tolist()
                ],
                "rank": self.hessian_quotient_matrix.rank(),
                "is_semisimple": True,
                "Jordan_blocks": [
                    {"eigenvalue": "4", "size": 1},
                    {"eigenvalue": "4", "size": 1},
                ],
                "characteristic_polynomial": "(lambda-4)^2",
                "minimal_polynomial": "lambda-4",
                "rational_invariant_factors": ["lambda-4", "lambda-4"],
            },
            "exact": True,
        }

    def helicity_certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-curved-helicity-two-channel-v1",
            "atomic_flag": "curved_helicity_two_channel",
            "curved_helicity_two_channel": True,
            "little_group": "SO(2) stabilizing zeta=(1,1,0,0)",
            "real_basis": ["f_22-f_33", "f_23"],
            "infinitesimal_generator": [
                [int(value) for value in row]
                for row in self.little_group_generator.tolist()
            ],
            "generator_square": "-4 I_2",
            "complex_weights": ["+2i", "-2i"],
            "characteristic_polynomial": "lambda^2+4",
            "minimal_polynomial": "lambda^2+4",
            "rational_invariant_factors": ["lambda^2+4"],
            "linearized_Weyl_symbol": {
                "full_symbol_rank": self.weyl_symbol_rank,
                "ker_N_subset_ker_W": self.weyl_descent_stack_rank == 11,
                "rank_W_on_gauge_preimages": (
                    self.weyl_image_of_gauge_preimages_rank
                ),
                "target_quotient_dimension": self.weyl_target_quotient_dimension,
                "induced_quotient_matrix": [
                    [str(value) for value in row]
                    for row in self.induced_weyl_matrix.tolist()
                ],
                "is_isomorphism": self.induced_weyl_matrix.det() != 0,
                "determinant": str(self.induced_weyl_matrix.det()),
                "characteristic_polynomial": "(lambda-1/4)^2",
                "minimal_polynomial": "lambda-1/4",
                "Jordan_blocks": [
                    {"eigenvalue": "1/4", "size": 1},
                    {"eigenvalue": "1/4", "size": 1},
                ],
                "rational_invariant_factors": [
                    "lambda-1/4",
                    "lambda-1/4",
                ],
                "electric_TT_matrix_on_h22-h33_h23": [
                    [str(value) for value in row]
                    for row in self.electric_weyl_matrix.tolist()
                ],
                "electric_TT_determinant": str(self.electric_weyl_matrix.det()),
                "physical_image_nonzero_component_counts": list(
                    self.weyl_image_nonzero_counts
                ),
                "physical_image_squared_coordinate_norms": [
                    str(value)
                    for value in self.weyl_image_squared_coordinate_norms
                ],
                "sha256": self.weyl_symbol_sha256,
            },
            "exact": True,
        }

    def symbol_extension_certificate(self) -> dict[str, object]:
        return {
            "kernel_cokernel": {
                "E_2_kernel_dimension": self.hessian_kernel_dimension,
                "E_2_cokernel_dimension": self.hessian_cokernel_dimension,
            },
            "gauge_image": {
                "dimension": self.gauge_image_dimension,
                "basis": list(self.gauge_image_basis),
            },
            "quotient": self.quotient_certificate(),
            "helicity_two": self.helicity_certificate(),
        }
