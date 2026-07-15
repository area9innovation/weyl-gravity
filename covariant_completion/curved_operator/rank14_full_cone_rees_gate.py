"""Common-Douglis/Rees associated-graded gate for the rank-14 cone.

The fibre-identified 66-row BV differential uses
``Caux=Y^{-1}K^sharp J``, namely ``OrdinaryDerivativeWeylSystem.gauge_condition``.
It does *not* use the raw action-dual row ``K(-zeta)^T J``.  This distinction
is decisive: the former has a nonzero Rees-degree-zero component, while the
latter begins two layers lower in the present coordinate weights.

This module reconstructs all eight maps from their authoritative coordinate
sources, keeps every emitted Rees layer separate, and performs the square
gate before any cohomology calculation.  No Green or deformation-retract
claim follows from the associated-graded calculation alone.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import sympy as sp

from covariant_completion.minimal_witness.linearized_bach import LinearizedBach
from covariant_completion.curved_retract.curvature_auxiliary_chain_map import (
    _symmetric_coordinate_inclusion,
    _target_extraction,
)
from covariant_completion.curved_retract.tangent_shift import (
    CurvedAuxiliaryTangentShift,
)

from .conventions import CurvedBVConventions, SYMMETRIC_COORDINATES, _ordinary_system
from .covariant_jets import CovariantJetBasis
from .expanded_hessian import load_coefficient_cache
from .null_symbol_rank_obstruction import DEFAULT_CACHE
from .rank14_full_cone_symbol_gate import MAP_DEGREES, OBJECT_WEIGHTS
from .rank14_weyl_cotton_incoming_map_ledger import (
    Rank14WeylCottonIncomingMapLedger,
    _auxiliary_identity_map,
    _bach_to_curvature,
)
from .rank14_weyl_cotton_symbol_audit import Rank14WeylCottonSymbolAudit


REES_LEADING_DEGREES = {**MAP_DEGREES, "C": 0}


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _nonzero_count(matrix: sp.MatrixBase) -> int:
    return sum(int(value != 0) for value in matrix)


def _weighted_components(
    matrix: sp.MatrixBase,
    covector: tuple[sp.Symbol, ...],
    source_weights: tuple[int, ...],
    target_weights: tuple[int, ...],
) -> dict[int, sp.Matrix]:
    """Split a polynomial operator by componentwise Douglis degree."""

    if matrix.cols != len(source_weights) or matrix.rows != len(target_weights):
        raise ValueError("weight ledger does not match operator shape")
    output: dict[int, sp.Matrix] = {}
    for row in range(matrix.rows):
        for column in range(matrix.cols):
            value = sp.expand(matrix[row, column])
            if value == 0:
                continue
            for monomial, coefficient in sp.Poly(value, *covector).terms():
                if coefficient == 0:
                    continue
                degree = (
                    sum(monomial)
                    + source_weights[column]
                    - target_weights[row]
                )
                if degree not in output:
                    output[degree] = sp.zeros(matrix.rows, matrix.cols)
                output[degree][row, column] += coefficient * sp.prod(
                    covector[axis] ** monomial[axis] for axis in range(4)
                )
    return {
        degree: component.applyfunc(sp.expand)
        for degree, component in sorted(output.items(), reverse=True)
    }


def _symbol_from_tables(
    tables: tuple[sp.Matrix, ...], covector: tuple[sp.Symbol, ...]
) -> sp.Matrix:
    """Table order is temporal, three spatial, then zeroth."""

    return (
        covector[0] * tables[0]
        + sum(
            (covector[axis + 1] * tables[axis + 1] for axis in range(3)),
            sp.zeros(tables[0].rows, tables[0].cols),
        )
        + tables[4]
    ).applyfunc(sp.expand)


def _provisional_shift(basis: CovariantJetBasis) -> CurvedAuxiliaryTangentShift:
    """Exact shift evaluator without rerunning its exhaustive gauge audit."""

    linearized = LinearizedBach.build()
    return CurvedAuxiliaryTangentShift(
        geometry=basis.geometry,
        linearized_geometry=linearized,
        metric_principal_symbol=sp.zeros(10),
        vector_principal_symbol=sp.zeros(10, 4),
        metric_flat_principal_defect=sp.zeros(10),
        vector_flat_principal_defect=sp.zeros(10, 4),
        diffeomorphism_gauge_defect=sp.zeros(10, 4),
        conformal_boost_gauge_defect=sp.zeros(10, 4),
        weyl_gauge_defect=sp.zeros(10, 1),
    )


def _full_equation_attachment(
    covector: tuple[sp.Symbol, ...],
) -> tuple[sp.Matrix, int]:
    """Reconstruct the complete order-two ``A:Ebar_aux -> Q`` table.

    This is the coefficient formula certified in
    :mod:`curvature_auxiliary_chain_map`, but it avoids rebuilding the 700
    four-jets used there to determine the already-persisted constant
    Bach-to-curvature map.
    """

    source = _ordinary_system()
    basis = CovariantJetBasis.build()
    shift = _provisional_shift(basis)
    projection = _target_extraction() * _symmetric_coordinate_inclusion()
    through_two = tuple(basis.geometry.exhaustive_multiindices(2))
    coefficients = {multiindex: sp.zeros(40, 24) for multiindex in through_two}
    zero = (0, 0, 0, 0)
    coefficients[zero][:, :10] = (
        _bach_to_curvature() * projection * source.tensor_pairing.inv()
    )
    for multiindex in through_two:
        shift_coefficient = sp.zeros(10)
        for column in range(10):
            metric = basis.covariant_monomial_symmetric(column, multiindex, 2)
            image = shift.apply(metric, basis.geometry.zero_covector())
            shift_coefficient[:, column] = sp.Matrix(
                [image[a][b].value for a, b in SYMMETRIC_COORDINATES]
            )
        order = sum(multiindex)
        coefficients[multiindex][:, 10:20] += (
            _bach_to_curvature()
            * projection
            * source.tensor_pairing.inv()
            * ((-1) ** order * shift_coefficient.T)
        )
    polynomial = sp.zeros(40, 24)
    occurrence_count = 0
    for multiindex, raw in coefficients.items():
        paired = raw * source.field_fibre_pairing
        occurrence_count += _nonzero_count(paired)
        polynomial += sp.prod(
            covector[axis] ** multiindex[axis] for axis in range(4)
        ) * paired
    return polynomial.applyfunc(sp.expand), occurrence_count


@dataclass(frozen=True)
class Rank14FullConeReesGate:
    covector: tuple[sp.Symbol, ...]
    map_components: dict[str, dict[int, sp.Matrix]]
    leading_differentials: tuple[sp.Matrix, ...]
    full_attachment_occurrences: int

    @staticmethod
    def build() -> "Rank14FullConeReesGate":
        zeta = tuple(sp.symbols("rank14_rees_z0:4", real=True))
        source = _ordinary_system()
        conventions = CurvedBVConventions.build()
        source_substitution = dict(zip(source.covector, zeta, strict=True))

        # Authoritative fibre-identified blocks are exactly those in
        # GeneralizedAuxiliaryRetract.original_differential.  In particular
        # Caux is the gauge condition/companion, not the raw action-dual row.
        gauge = source.gauge_map.subs(source_substitution).applyfunc(sp.expand)
        identity = source.gauge_condition.subs(source_substitution).applyfunc(
            sp.expand
        )

        cache_covector, hessian, _ = load_coefficient_cache(DEFAULT_CACHE)
        hessian = hessian.subs(
            dict(zip(cache_covector, zeta, strict=True))
        ).applyfunc(sp.expand)
        auxiliary_equation = (
            conventions.field_pairing.inv() * hessian
        ).applyfunc(sp.expand)

        state_audit = Rank14WeylCottonSymbolAudit.build()
        state_substitution = {
            state_audit.tau: zeta[0],
            **dict(zip(state_audit.spatial_covector, zeta[1:], strict=True)),
        }
        state_map = state_audit.state_symbol_fields.subs(
            state_substitution
        ).row_join(sp.zeros(26, 4)).applyfunc(sp.expand)

        attachment, attachment_occurrences = _full_equation_attachment(zeta)
        ledger = Rank14WeylCottonIncomingMapLedger.build()
        curvature_equation = _symbol_from_tables(
            ledger.equation_complex_tables, zeta
        )
        curvature_identity = _symbol_from_tables(
            ledger.identity_complex_tables, zeta
        )
        identity_attachment = _auxiliary_identity_map()

        full_maps = {
            "K": ("G", "M", gauge),
            "E": ("M", "E", auxiliary_equation),
            "C": ("E", "I", identity),
            "T": ("M", "U", state_map),
            "A": ("E", "Q", attachment),
            "B": ("I", "J", identity_attachment),
            "Ewc": ("U", "Q", curvature_equation),
            "N": ("Q", "J", curvature_identity),
        }
        components = {
            name: _weighted_components(
                matrix,
                zeta,
                OBJECT_WEIGHTS[source_name],
                OBJECT_WEIGHTS[target_name],
            )
            for name, (source_name, target_name, matrix) in full_maps.items()
        }

        leading = {
            name: component[REES_LEADING_DEGREES[name]]
            for name, component in components.items()
        }
        # Candidate degree-zero associated graded in the fibre-identified
        # coordinates of the actual 66-row differential.
        d_minus_two = leading["K"]
        d_minus_one = leading["T"].col_join(-leading["E"])
        d_zero = leading["Ewc"].row_join(leading["A"]).col_join(
            sp.zeros(9, 26).row_join(-leading["C"])
        )
        d_one = leading["N"].row_join(leading["B"])
        result = Rank14FullConeReesGate(
            covector=zeta,
            map_components=components,
            leading_differentials=(d_minus_two, d_minus_one, d_zero, d_one),
            full_attachment_occurrences=attachment_occurrences,
        )
        result.verify()
        return result

    def _sample(self, value: tuple[int, int, int, int]) -> dict[str, object]:
        substitution = dict(zip(self.covector, value, strict=True))
        matrices = tuple(
            matrix.subs(substitution) for matrix in self.leading_differentials
        )
        square_ranks = [
            (matrices[index + 1] * matrices[index]).rank()
            for index in range(3)
        ]
        if square_ranks != [0, 0, 0]:
            return {
                "differential_ranks": [matrix.rank() for matrix in matrices],
                "square_ranks": square_ranks,
                "cohomology_defined": False,
            }
        ranks = [matrix.rank() for matrix in matrices]
        dimensions = [9, 24, 50, 49, 14]
        cohomology = [
            dimensions[0] - ranks[0],
            dimensions[1] - ranks[0] - ranks[1],
            dimensions[2] - ranks[1] - ranks[2],
            dimensions[3] - ranks[2] - ranks[3],
            dimensions[4] - ranks[3],
        ]
        return {
            "differential_ranks": ranks,
            "square_ranks": square_ranks,
            "cohomology_defined": True,
            "cohomology_ranks": cohomology,
        }

    def verify(self) -> None:
        if [matrix.shape for matrix in self.leading_differentials] != [
            (24, 9),
            (50, 24),
            (49, 50),
            (14, 49),
        ]:
            raise AssertionError("leading cone degree ledger drifted")
        if self.full_attachment_occurrences != 149:
            raise AssertionError("authoritative full A occurrence count drifted")
        if tuple(self.map_components["C"]) != (0, -2, -4):
            raise AssertionError("fibre-identified Caux Rees ledger drifted")
        for name in ("K", "E", "C", "T", "A", "B", "Ewc", "N"):
            if max(self.map_components[name]) != 0:
                raise AssertionError(f"leading Rees degree drifted for {name}")
        d_m2, d_m1, d_0, d_1 = self.leading_differentials
        squares = tuple(
            square.applyfunc(sp.expand)
            for square in (d_m1 * d_m2, d_0 * d_m1, d_1 * d_0)
        )
        if squares[0] != sp.zeros(50, 9):
            raise AssertionError("incoming degree-zero cone square failed")
        if squares[1] != sp.zeros(49, 24):
            raise AssertionError("middle degree-zero cone square failed")
        final = squares[2]
        nonzero_rows = tuple(
            row
            for row in range(final.rows)
            if any(final[row, column] != 0 for column in range(final.cols))
        )
        if _nonzero_count(final) != 68 or nonzero_rows != (6, 7, 8, 12):
            raise AssertionError("rank-four degree-zero A/N obstruction drifted")
        for sample in (
            (2, 1, 3, 5),
            (2, 1, 0, 0),
            (0, 1, 0, 0),
            (1, 0, 0, 0),
            (1, 1, 0, 0),
        ):
            values = self._sample(sample)
            if values["square_ranks"] != [0, 0, 4]:
                raise AssertionError(f"degree-zero square ranks drifted at {sample}")
            if values["cohomology_defined"]:
                raise AssertionError(f"cohomology bypassed d^2 gate at {sample}")

    def certificate(self) -> dict[str, object]:
        self.verify()
        samples = {
            name: self._sample(value)
            for name, value in {
                "generic_(2,1,3,5)": (2, 1, 3, 5),
                "timelike_(2,1,0,0)": (2, 1, 0, 0),
                "spacelike_(0,1,0,0)": (0, 1, 0, 0),
                "temporal_(1,0,0,0)": (1, 0, 0, 0),
                "null_(1,1,0,0)": (1, 1, 0, 0),
            }.items()
        }
        component_ledger = {}
        for name, components in self.map_components.items():
            component_ledger[name] = {
                "certified_leading_degree": REES_LEADING_DEGREES[name],
                "emitted_degrees": list(components),
                "components": {
                    str(degree): {
                        "shape": list(matrix.shape),
                        "nonzero_entries": _nonzero_count(matrix),
                        "sha256": _digest(matrix),
                    }
                    for degree, matrix in components.items()
                },
            }
        c_zero = self.map_components["C"][0]
        b_zero = self.map_components["B"][0]
        n_a = (
            self.map_components["N"][0] * self.map_components["A"][0]
        ).applyfunc(sp.expand)
        b_c = (b_zero * c_zero).applyfunc(sp.expand)
        final_defect = (n_a - b_c).applyfunc(sp.expand)
        return {
            "schema": "pure-weyl-rank14-full-cone-rees-gate-v1",
            "scope": (
                "common componentwise Douglis/Rees associated graded at a "
                "cylinder base point; lower PBW pages remain separate"
            ),
            "degree_ledger": {
                "cochain_degrees": [-2, -1, 0, 1, 2],
                "ranks": [9, 24, 50, 49, 14],
                "incoming_gauge_row_included": True,
            },
            "object_weights": {
                key: list(value) for key, value in OBJECT_WEIGHTS.items()
            },
            "map_components": component_ledger,
            "authoritative_full_A": {
                "coefficient_occurrences": self.full_attachment_occurrences,
                "leading_degree_zero_nonzero_entries": _nonzero_count(
                    self.map_components["A"][0]
                ),
                "direct_equal_weight_A0_included": True,
                "lower_shift_terms_kept_on_their_own_Rees_pages": True,
            },
            "degree_zero_cone": {
                "Caux_block": (
                    "system.gauge_condition[0]=Y^-1 K^sharp J in the "
                    "fibre-identified 66-row differential"
                ),
                "differential_shapes": [
                    list(matrix.shape) for matrix in self.leading_differentials
                ],
                "square_nonzero_entries": [
                    _nonzero_count((right * left).applyfunc(sp.expand))
                    for left, right in zip(
                        self.leading_differentials[:-1],
                        self.leading_differentials[1:],
                        strict=True,
                    )
                ],
                "is_complex": False,
                "cohomology_computed": False,
                "cohomology_refusal": "last square has exact rank 4",
                "last_square": {
                    "operator": "N[0] A[0]-B[0] Caux[0]",
                    "N0_A0_nonzero_entries": _nonzero_count(n_a),
                    "B0_C0_nonzero_entries": _nonzero_count(b_c),
                    "defect_nonzero_entries": _nonzero_count(final_defect),
                    "nonzero_identity_rows": [6, 7, 8, 12],
                    "row_types": "a[3],s[1]",
                    "rank_on_all_tested_strata": 4,
                },
            },
            "causal_strata": samples,
            "coordinate_correction": {
                "actual_Q_identity_block": "system.gauge_condition",
                "actual_Caux_emitted_degrees": [0, -2, -4],
                "raw_action_dual_row": "K(-zeta)^T J",
                "raw_action_dual_is_the_fibre_identified_Q_block": False,
                "previous_Caux_degree_minus_two_demotion_corrected": True,
            },
            "final_square_obstruction": {
                "generic_rank": final_defect.subs(
                    dict(zip(self.covector, (2, 1, 3, 5), strict=True))
                ).rank(),
                "interpretation": (
                    "the current constant B attachment does not establish the "
                    "inferred typed relation N A=B C in the leading Rees page; "
                    "the discrepancy is scoped to A/B/N attachment data or "
                    "their filtration"
                ),
            },
            "decision": {
                "leading_associated_graded_cone_is_a_complex": False,
                "leading_associated_graded_cohomology_computed": False,
                "complete_Rees_PBW_cone_constructed": False,
                "support_local_contraction_constructed": False,
                "prolonged_green_witness": False,
                "causal_green_homotopy": False,
                "rank14_SDR_constructed": False,
            },
            "refined_boundary": (
                "the authoritative fibre-identified auxiliary Q block is now "
                "used and the first two cone squares close; the remaining "
                "rank-four last square is an attachment-consistency obstruction, "
                "not a no-go theorem for Green hyperbolicity"
            ),
            "status_flags_promoted": [],
            "fail_closed": True,
        }
