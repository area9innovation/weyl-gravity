"""Projector-free curvature presentation of the rank-14 field cokernel.

After the rank-twelve gauge/subsidiary submodule is removed, the unresolved
part of the reciprocal rank-34 component is the rank-fourteen cokernel of the
six vector-gauge columns in ``(h[10],f[10])``.  This module gives that
cokernel a local 3+1 presentation without transverse or helicity projectors.

For either symmetric tensor ``s`` put

``a=partial_t s_00`` and
``Q_ij=partial_t s_ij-D_i s_0j-D_j s_0i``.

The seven-component operator ``P7:s -> (a,Q)`` kills the three spatial
symmetrized-gradient columns.  For the two tensors, ``P14 A=L14 P14`` with

``L14=[[L7,0],[R7,L7]]``.

There is a pointwise, local ``STF2 plus two scalars`` filtration of ``L7``.
The STF submodule is exactly ``Box I5``.  The scalar quotient is

``Lsc=[[Delta-2T,T],[-Delta,-T]],  T=partial_t^2``,

and has determinant ``2 T^2`` and an explicit same-sided inverse built only
from the temporal Green operator.  Finite triangular recursion therefore
gives a same-sided inverse of the *presented principal quotient*.  The
aligned transverse restriction is the physical triangular biwave block.

Compatible source lifting is explicit.  A one-sided inverse of ``partial_t``
sets ``s_0i=0`` and integrates ``a,Q``.  Its failure to be a left inverse is
exactly a spatial symmetrized gradient, hence the certified gauge submodule.
No elliptic, transverse, TT or helicity projector occurs.

The linearized Weyl map is tied to this presentation by an exact local
prolonged identity ``partial_t C1=R_C P7`` (and therefore also for
``div C1``).  The unprolonged factor uses temporal division on compatible
sources; it is not misreported as a differential bundle map.

This remains a principal differential-module theorem.  The complete curved
lower-order rank-34 operator, its insertion into every BV row and the full
Green homotopy are not supplied, so no top-level Green flag is promoted.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Mapping

import sympy as sp

from covariant_completion.minimal_witness.linearized_bach import LinearizedBach

from .conventions import SYMMETRIC_COORDINATES
from .covariant_jets import CovariantJetBasis
from .expanded_relative_witness_rank34_module import ExpandedRelativeRank34Module
from .weyl_3plus1 import WeylCottonBachFirstOrder, stf_basis


SPATIAL_SYMMETRIC_PAIRS = tuple(
    (first, second)
    for first in range(1, 4)
    for second in range(first, 4)
)


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _nonzero_count(matrix: sp.MatrixBase) -> int:
    return sum(int(value != 0) for value in matrix)


def _quotient_map(
    tau: sp.Symbol, spatial: tuple[sp.Symbol, sp.Symbol, sp.Symbol]
) -> sp.Matrix:
    coordinate = {pair: index for index, pair in enumerate(SYMMETRIC_COORDINATES)}
    result = sp.zeros(7, 10)
    result[0, coordinate[(0, 0)]] = tau
    for row, (first, second) in enumerate(SPATIAL_SYMMETRIC_PAIRS, start=1):
        result[row, coordinate[(first, second)]] = tau
        result[row, coordinate[(0, second)]] -= spatial[first - 1]
        result[row, coordinate[(0, first)]] -= spatial[second - 1]
    return result


def _spatial_gauge(
    tau: sp.Symbol, spatial: tuple[sp.Symbol, sp.Symbol, sp.Symbol]
) -> sp.Matrix:
    coordinate = {pair: index for index, pair in enumerate(SYMMETRIC_COORDINATES)}
    covector = (tau, *spatial)
    result = sp.zeros(10, 3)
    for column in range(3):
        vector_index = column + 1
        for (first, second), row in coordinate.items():
            result[row, column] = (
                covector[first] * int(second == vector_index)
                + int(first == vector_index) * covector[second]
            )
    return result


def _coordinate_right_inverse(quotient: sp.Matrix) -> sp.Matrix:
    """Algebraic derivation aid; the emitted intertwiner is polynomial."""

    coordinate = {pair: index for index, pair in enumerate(SYMMETRIC_COORDINATES)}
    selected = [coordinate[(0, 0)]] + [
        coordinate[pair] for pair in SPATIAL_SYMMETRIC_PAIRS
    ]
    square = quotient[:, selected]
    result = sp.zeros(10, 7)
    inverse = square.inv()
    for row, target in enumerate(selected):
        result[target, :] = inverse[row, :]
    return result


def _stf_scalar_decomposition() -> tuple[sp.Matrix, sp.Matrix, sp.Matrix, sp.Matrix]:
    """Return STF inclusion/projection and scalar inclusion/projection."""

    stf_inclusion = sp.zeros(7, 5)
    for column, tensor in enumerate(stf_basis()):
        for row, (first, second) in enumerate(
            SPATIAL_SYMMETRIC_PAIRS, start=1
        ):
            stf_inclusion[row, column] = tensor[first - 1, second - 1]
    stf_projection = (
        stf_inclusion.T * stf_inclusion
    ).inv() * stf_inclusion.T

    scalar_inclusion = sp.zeros(7, 2)
    scalar_inclusion[0, 0] = 1
    for row, (first, second) in enumerate(SPATIAL_SYMMETRIC_PAIRS, start=1):
        if first == second:
            scalar_inclusion[row, 1] = sp.Rational(1, 3)
    scalar_projection = sp.zeros(2, 7)
    scalar_projection[0, 0] = 1
    for row, (first, second) in enumerate(SPATIAL_SYMMETRIC_PAIRS, start=1):
        if first == second:
            scalar_projection[1, row] = 1
    return (
        stf_inclusion,
        stf_projection,
        scalar_inclusion,
        scalar_projection,
    )


def _weyl_eb_symbol(
    covector: tuple[sp.Symbol, sp.Symbol, sp.Symbol, sp.Symbol]
) -> sp.Matrix:
    """Exact principal ``h -> (E,B)`` linearized-Weyl symbol."""

    basis = CovariantJetBasis.build()
    bach = LinearizedBach.build()
    first_order = WeylCottonBachFirstOrder.build()
    extraction = first_order.decomposition.electric_magnetic_extraction
    result = sp.zeros(10, 10)
    degree_two = tuple(
        multiindex
        for multiindex in basis.geometry.exhaustive_multiindices(2)
        if sum(multiindex) == 2
    )
    for component in range(10):
        for multiindex in degree_two:
            weight = sp.prod(
                covector[axis] ** multiindex[axis] for axis in range(4)
            )
            metric = basis.covariant_monomial_symmetric(
                component, multiindex, 2
            )
            image = bach.linearized_weyl(metric)
            flattened = sp.Matrix(
                [
                    image[a][b][c][d].value
                    for a in range(4)
                    for b in range(4)
                    for c in range(4)
                    for d in range(4)
                ]
            )
            result[:, component] += weight * extraction * flattened
    return result.applyfunc(sp.expand)


def _physical_inclusion_projection() -> tuple[sp.Matrix, sp.Matrix]:
    """Aligned transverse STF inclusion in the fourteen quotient rows."""

    # Per tensor quotient order: a,Q11,Q12,Q13,Q22,Q23,Q33.
    inclusion = sp.zeros(14, 4)
    inclusion[4, 0] = 1
    inclusion[6, 0] = -1
    inclusion[5, 1] = 1
    inclusion[11, 2] = 1
    inclusion[13, 2] = -1
    inclusion[12, 3] = 1
    projection = sp.zeros(4, 14)
    projection[0, 4] = sp.Rational(1, 2)
    projection[0, 6] = -sp.Rational(1, 2)
    projection[1, 5] = 1
    projection[2, 11] = sp.Rational(1, 2)
    projection[2, 13] = -sp.Rational(1, 2)
    projection[3, 12] = 1
    return inclusion, projection


def _nested(mapping: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = mapping.get(key)
    if not isinstance(value, Mapping):
        raise AssertionError(f"missing mapping {key}")
    return value


@dataclass(frozen=True)
class ExpandedRelativeRank14CurvaturePresentation:
    base: ExpandedRelativeRank34Module
    quotient7: sp.Matrix
    quotient14: sp.Matrix
    independent_spatial_gauge: sp.Matrix
    gauge_basis_change: sp.Matrix
    induced14: sp.Matrix
    diagonal7: sp.Matrix
    extension7: sp.Matrix
    stf_inclusion: sp.Matrix
    stf_projection: sp.Matrix
    scalar_inclusion: sp.Matrix
    scalar_projection: sp.Matrix
    stf_operator: sp.Matrix
    scalar_operator: sp.Matrix
    scalar_to_stf: sp.Matrix
    rational_green7: sp.Matrix
    rational_green14: sp.Matrix
    weyl_symbol: sp.Matrix
    prolonged_weyl_factor: sp.Matrix
    physical_block: sp.Matrix

    @staticmethod
    def build() -> "ExpandedRelativeRank14CurvaturePresentation":
        base = ExpandedRelativeRank34Module.build()
        tau, spatial = base.tau, base.spatial_covector
        p7 = _quotient_map(tau, spatial)
        p14 = sp.diag(p7, p7)
        k7 = _spatial_gauge(tau, spatial)
        independent_gauge = sp.diag(k7, k7)

        # The certified B columns are another constant basis of the same six
        # spatial symmetrized-gradient directions.
        basis_change_columns: list[sp.Matrix] = []
        for column in range(6):
            solution, _ = base.gauge_incidence.gauss_jordan_solve(
                independent_gauge[:, column]
            )
            solution = solution.subs(
                {symbol: 0 for symbol in solution.free_symbols}
            )
            basis_change_columns.append(solution)
        basis_change = sp.Matrix.hstack(*basis_change_columns)

        derivation_right_inverse = sp.diag(
            _coordinate_right_inverse(p7), _coordinate_right_inverse(p7)
        )
        induced = (
            p14 * base.field_diagonal * derivation_right_inverse
        ).applyfunc(sp.cancel)
        diagonal7 = induced[:7, :7]
        extension7 = induced[7:, :7]

        stf_i, stf_p, scalar_i, scalar_p = _stf_scalar_decomposition()
        stf_operator = (stf_p * diagonal7 * stf_i).applyfunc(sp.expand)
        scalar_operator = (scalar_p * diagonal7 * scalar_i).applyfunc(sp.expand)
        scalar_to_stf = (stf_p * diagonal7 * scalar_i).applyfunc(sp.expand)

        # Rational symbols encode only the algebra of same-sided Green
        # compositions.  They are not used as Fourier multipliers.
        laplacian = sum(value**2 for value in spatial)
        wave = laplacian - tau**2
        scalar_green = sp.Matrix(
            [
                [-sp.Rational(1, 2) / tau**2, -sp.Rational(1, 2) / tau**2],
                [
                    laplacian / (2 * tau**4),
                    laplacian / (2 * tau**4) - 1 / tau**2,
                ],
            ]
        )
        decomposition = stf_i.row_join(scalar_i)
        decomposition_inverse = stf_p.col_join(scalar_p)
        triangular_green = sp.zeros(7)
        triangular_green[:5, :5] = sp.eye(5) / wave
        triangular_green[:5, 5:] = (
            -sp.eye(5) / wave * scalar_to_stf * scalar_green
        )
        triangular_green[5:, 5:] = scalar_green
        green7 = (
            decomposition * triangular_green * decomposition_inverse
        ).applyfunc(sp.cancel)
        green14 = sp.zeros(14)
        green14[:7, :7] = green7
        green14[7:, 7:] = green7
        green14[7:, :7] = (-green7 * extension7 * green7).applyfunc(
            sp.cancel
        )

        weyl = _weyl_eb_symbol((tau, *spatial))
        # The temporal prolongation removes the sole denominator in the
        # factor through the seven quotient coordinates.
        weyl_factor = (
            tau * weyl * _coordinate_right_inverse(p7)
        ).applyfunc(sp.cancel)

        inclusion, projection = _physical_inclusion_projection()
        aligned = induced.subs({spatial[0]: base.rho, spatial[1]: 0, spatial[2]: 0})
        physical = (projection * aligned * inclusion).applyfunc(sp.factor)

        result = ExpandedRelativeRank14CurvaturePresentation(
            base=base,
            quotient7=p7,
            quotient14=p14,
            independent_spatial_gauge=independent_gauge,
            gauge_basis_change=basis_change,
            induced14=induced,
            diagonal7=diagonal7,
            extension7=extension7,
            stf_inclusion=stf_i,
            stf_projection=stf_p,
            scalar_inclusion=scalar_i,
            scalar_projection=scalar_p,
            stf_operator=stf_operator,
            scalar_operator=scalar_operator,
            scalar_to_stf=scalar_to_stf,
            rational_green7=green7,
            rational_green14=green14,
            weyl_symbol=weyl,
            prolonged_weyl_factor=weyl_factor,
            physical_block=physical,
        )
        result.verify()
        return result

    def verify(self) -> None:
        tau, spatial = self.base.tau, self.base.spatial_covector
        laplacian = sum(value**2 for value in spatial)
        wave = laplacian - tau**2
        if self.quotient14.shape != (14, 20) or self.quotient14.rank() != 14:
            raise AssertionError("rank-fourteen quotient presentation drifted")
        if (
            self.quotient14 * self.base.gauge_incidence
        ).applyfunc(sp.expand) != sp.zeros(14, 6):
            raise AssertionError("quotient map does not kill the gauge submodule")
        if self.gauge_basis_change.det() != 1:
            raise AssertionError("independent spatial-gauge basis change drifted")
        if (
            self.base.gauge_incidence * self.gauge_basis_change
            - self.independent_spatial_gauge
        ).applyfunc(sp.expand) != sp.zeros(20, 6):
            raise AssertionError("certified and independent gauge images differ")
        if any(sp.denom(value) != 1 for value in self.induced14):
            raise AssertionError("induced rank-fourteen operator is not polynomial")
        if (
            self.quotient14 * self.base.field_diagonal
            - self.induced14 * self.quotient14
        ).applyfunc(sp.expand) != sp.zeros(14, 20):
            raise AssertionError("P14 A=L14 P14 intertwiner failed")
        if self.induced14[:7, 7:] != sp.zeros(7):
            raise AssertionError("rank-fourteen operator is not triangular")
        if self.induced14[7:, 7:] != self.diagonal7:
            raise AssertionError("two diagonal rank-seven blocks differ")

        if self.stf_projection * self.stf_inclusion != sp.eye(5):
            raise AssertionError("STF inclusion has no pointwise left inverse")
        if self.scalar_projection * self.scalar_inclusion != sp.eye(2):
            raise AssertionError("scalar inclusion has no pointwise left inverse")
        decomposition = self.stf_inclusion.row_join(self.scalar_inclusion)
        inverse = self.stf_projection.col_join(self.scalar_projection)
        if decomposition * inverse != sp.eye(7) or inverse * decomposition != sp.eye(7):
            raise AssertionError("STF/scalar pointwise decomposition failed")
        if self.stf_operator != wave * sp.eye(5):
            raise AssertionError("rank-five associated graded is not Box I5")
        if (
            self.scalar_projection * self.diagonal7 * self.stf_inclusion
        ).applyfunc(sp.expand) != sp.zeros(2, 5):
            raise AssertionError("STF wave submodule is not invariant")
        expected_scalar = sp.Matrix(
            [[laplacian - 2 * tau**2, tau**2], [-laplacian, -tau**2]]
        )
        if self.scalar_operator != expected_scalar:
            raise AssertionError("rank-two temporal quotient drifted")
        if sp.factor(self.scalar_operator.det()) != 2 * tau**4:
            raise AssertionError("rank-two temporal determinant drifted")

        if (
            self.diagonal7 * self.rational_green7 - sp.eye(7)
        ).applyfunc(sp.cancel) != sp.zeros(7):
            raise AssertionError("rank-seven Green right algebra failed")
        if (
            self.rational_green7 * self.diagonal7 - sp.eye(7)
        ).applyfunc(sp.cancel) != sp.zeros(7):
            raise AssertionError("rank-seven Green left algebra failed")
        if (
            self.induced14 * self.rational_green14 - sp.eye(14)
        ).applyfunc(sp.cancel) != sp.zeros(14):
            raise AssertionError("rank-fourteen Green right algebra failed")
        if (
            self.rational_green14 * self.induced14 - sp.eye(14)
        ).applyfunc(sp.cancel) != sp.zeros(14):
            raise AssertionError("rank-fourteen Green left algebra failed")

        if self.weyl_symbol.rank() != 5:
            raise AssertionError("linearized Weyl EB symbol rank drifted")
        if (
            self.weyl_symbol * self.independent_spatial_gauge[:10, :3]
        ).applyfunc(sp.expand) != sp.zeros(10, 3):
            raise AssertionError("C1 does not annihilate the spatial gauge image")
        if any(
            sp.Poly(
                sp.denom(value), tau, *spatial
            ).total_degree() != 0
            for value in self.prolonged_weyl_factor
            if value != 0
        ):
            raise AssertionError("temporally prolonged Weyl factor is not local")
        if (
            tau * self.weyl_symbol
            - self.prolonged_weyl_factor * self.quotient7
        ).applyfunc(sp.expand) != sp.zeros(10, 10):
            raise AssertionError("partial_t C1 factorization failed")

        rho = self.base.rho
        q = rho**2 - tau**2
        expected_physical = sp.diag(q, q, q, q)
        expected_physical[2, 0] = 4 * rho**2
        expected_physical[3, 1] = 4 * rho**2
        if (
            self.physical_block - expected_physical
        ).applyfunc(sp.expand) != sp.zeros(4):
            raise AssertionError("aligned physical biwave block drifted")

    def certificate(
        self,
        *,
        rank34_certificate: Mapping[str, object],
        helicity_certificate: Mapping[str, object],
        state_map_certificate: Mapping[str, object],
        reverify: bool = True,
    ) -> dict[str, object]:
        if reverify:
            self.verify()
        if rank34_certificate.get("schema") != (
            "pure-weyl-expanded-relative-rank34-module-v1"
        ):
            raise AssertionError("wrong rank-34 module input")
        if _nested(rank34_certificate, "local_differential_submodule").get(
            "intertwining_defect"
        ) != 0:
            raise AssertionError("rank-twelve input submodule regressed")
        if helicity_certificate.get("schema") != (
            "pure-weyl-curved-helicity-two-channel-v1"
        ) or not _nested(helicity_certificate, "linearized_Weyl_symbol").get(
            "is_isomorphism"
        ):
            raise AssertionError("physical Weyl quotient input unavailable")
        if state_map_certificate.get("schema") != (
            "pure-weyl-curvature-auxiliary-equation-chain-map-v1"
        ) or not state_map_certificate.get("first_chain_relation_exact"):
            raise AssertionError("exact (C1,div C1) chain map unavailable")

        tau, spatial = self.base.tau, self.base.spatial_covector
        laplacian = sum(value**2 for value in spatial)
        return {
            "schema": "pure-weyl-expanded-relative-rank14-curvature-presentation-v1",
            "scope": (
                "arbitrary-covector principal field-cokernel presentation and "
                "same-sided Green algebra; curved lower-order insertion is open"
            ),
            "cross_certificates": {
                "rank34_module": "curved_expanded_relative_witness_rank34_module.json",
                "Weyl_helicity_quotient": "curved_helicity_two_channel.json",
                "curvature_state_chain_map": "curved_curvature_auxiliary_chain_map.json",
            },
            "projector_free_quotient": {
                "formula_per_tensor": [
                    "a=partial_t s_00",
                    "Q_ij=partial_t s_ij-D_i s_0j-D_j s_0i",
                ],
                "map_shape": [14, 20],
                "generic_rank": self.quotient14.rank(),
                "P14_B_vector_defect": 0,
                "kernel_rank": 6,
                "kernel_equals_certified_vector_gauge_image_over_polynomial_fraction_field": True,
                "gauge_basis_change_determinant": int(self.gauge_basis_change.det()),
                "finite_order": 1,
                "support_local": True,
                "transverse_projector_used": False,
                "helicity_projector_used": False,
                "sha256": _digest(self.quotient14),
            },
            "induced_operator": {
                "identity": "P14 A_field=L14 P14",
                "identity_defect": 0,
                "shape": [14, 14],
                "maximum_order": 2,
                "polynomial_coefficients": True,
                "block_form": "[[L7,0],[R7,L7]]",
                "matrix_sha256": _digest(self.induced14),
                "aligned_determinant": str(self.base.quotient_field_determinant),
            },
            "rank7_local_filtration": {
                "pointwise_decomposition": "STF2[5] plus (a,tr Q)[2]",
                "pointwise_inverse_exact": True,
                "STF_submodule_invariant": True,
                "STF_operator": "(Delta-partial_t^2) I5",
                "scalar_quotient_operator": (
                    "[[Delta-2 partial_t^2,partial_t^2],"
                    "[-Delta,-partial_t^2]]"
                ),
                "scalar_determinant": "2 partial_t^4",
                "zero_speed_algebraic_multiplicity": 4,
                "light_sector_algebraic_multiplicity": 10,
                "local_STF_projector_only": True,
                "covector_dependent_projector_used": False,
            },
            "presented_quotient_green_algebra": {
                "wave_inverse": "G_Box_plus/minus on STF2",
                "temporal_inverse": "G_T_plus/minus for T=partial_t^2",
                "scalar_inverse": (
                    "1/(2T^2)[[-T,-T],[Delta,Delta-2T]]"
                ),
                "rank7_formula": "finite upper-triangular Green recursion",
                "rank14_formula": "[[G7,0],[-G7 R7 G7,G7]]",
                "rank7_left_defect": 0,
                "rank7_right_defect": 0,
                "rank14_left_defect": 0,
                "rank14_right_defect": 0,
                "same_sided_compositions_only": True,
                "same_sided_causal_support": True,
                "principal_presented_quotient_green_inverse": True,
                "full_curved_rank14_green_inverse": False,
            },
            "physical_biwave_restriction": {
                "aligned_covector": [str(-tau), str(self.base.rho), "0", "0"],
                "basis": ["Qh22-Qh33", "Qh23", "Qf22-Qf33", "Qf23"],
                "matrix": "[[q I2,0],[4 rho^2 I2,q I2]]",
                "identity_defect": 0,
                "Weyl_helicity_isomorphism": True,
                "classification": "physical triangular biwave extension",
            },
            "curvature_presentation": {
                "C1_EB_symbol_rank": self.weyl_symbol.rank(),
                "descended_R_ranks_generic_timelike_spacelike_null": [
                    self.weyl_symbol.subs(
                        {tau: 2, spatial[0]: 1, spatial[1]: 1, spatial[2]: 0}
                    ).rank(),
                    self.weyl_symbol.subs(
                        {tau: 1, spatial[0]: 0, spatial[1]: 0, spatial[2]: 0}
                    ).rank(),
                    self.weyl_symbol.subs(
                        {tau: 0, spatial[0]: 1, spatial[1]: 0, spatial[2]: 0}
                    ).rank(),
                    self.weyl_symbol.subs(
                        {tau: 1, spatial[0]: 1, spatial[1]: 0, spatial[2]: 0}
                    ).rank(),
                ],
                "C1_annihilates_vector_gauge": True,
                "local_prolonged_identity": "partial_t C1=R_C P7",
                "local_prolonged_identity_defect": 0,
                "R_C_maximum_order": 2,
                "divergence_consequence": (
                    "partial_t div(C1)=div(R_C P7), since [partial_t,D_i]=0"
                ),
                "unprolonged_C1_factor_requires_compatible_temporal_lifting": True,
                "nonlocal_helicity_reconstruction_used": False,
            },
            "direct_Weyl_Cotton_retraction_obstruction": {
                "F14_rank": 14,
                "descended_R_equals_C1_divC1_principal_rank": 5,
                "reason": (
                    "div C1 is a differential consequence of C1 and the "
                    "certified state map depends on the retained metric h, "
                    "while the independent f quotient is removed only by the "
                    "auxiliary equations"
                ),
                "direct_SR_equals_identity_possible": False,
                "rank_obstruction": "5 < 14",
                "required_repair": (
                    "construct SDR with SR=1+P14 H+H P14 on the sourced-compatible "
                    "equation quotient, using the auxiliary f equation"
                ),
                "SDR_constructed_here": False,
            },
            "compatible_source_lifting": {
                "one_sided_lift": (
                    "R_plus/minus(a,Q)=(s00=G_dt a,s0i=0,sij=G_dt Qij)"
                ),
                "P14_R_plus_minus": "identity",
                "left_defect": (
                    "1-R_plus/minus P14=K_sp G_dt extract(s0i)"
                ),
                "left_defect_lies_in_certified_gauge_submodule": True,
                "source_compatibility_preserved": True,
                "spatial_or_elliptic_inverse_used": False,
                "same_sided_support": True,
                "global_zero_mode_boundary": (
                    "the formula is on the standard retarded/advanced support "
                    "spaces; unrestricted temporal constants require endpoint rows"
                ),
            },
            "precise_boundary": {
                "principal_module_only": True,
                "curved_lower_order_L14_derived": False,
                "rank34_extension_lift_inserted": False,
                "rank4_vector_singleton_inserted": False,
                "all_BV_rows_inserted": False,
                "QLambda_identity_verified": False,
            },
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "status_flags_promoted": {
                "rank14_principal_projector_free_presentation": True,
                "rank14_principal_green_algebra": True,
                "direct_rank14_curvature_retraction_no_go": True,
                "rank14_equation_SDR_required": True,
            },
            "warranted_atomic_flags": {
                "rank14_principal_projector_free_presentation": True,
                "rank14_principal_green_algebra": True,
                "direct_rank14_curvature_retraction_no_go": True,
                "rank14_equation_SDR_required": True,
            },
            "fail_closed": True,
        }
