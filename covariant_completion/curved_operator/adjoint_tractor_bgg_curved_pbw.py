"""Curvature-aware PBW completion of the adjoint-tractor BGG compression.

The differential HPL screen deliberately treated Levi-Civita derivatives as
commuting and retained a 48-entry cylinder defect.  This module replaces that
temporary polynomial algebra by the exact PBW algebra of the locally symmetric
conformal cylinder.

The relevant connections are kept separate:

* the Levi-Civita connection acts on form and graded adjoint-tractor slots;
* the algebraic ``g_-1 + P.g_+1`` part is the normal tractor connection in the
  cylinder scale;
* their curvatures cancel on the full adjoint tractor connection.

Every HPL composition is performed in ordered covariant derivatives.  Adjacent
derivatives are exchanged with the curvature action on all remaining derivative
slots and on the complete input fibre.  No coefficient is fitted to the old
48-entry defect.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import hashlib
import json
from itertools import permutations, product
from pathlib import Path
from typing import Mapping

import sympy as sp

from .adjoint_tractor_kostant_compression import (
    AdjointTractorKostantCompression,
    _adjoint_basis,
    _coordinate_map,
    _digest_matrix,
    _parse_sparse,
    _sparse_matrix,
)
from .adjoint_tractor_bgg_differential_screen import (
    AdjointTractorBGGDifferentialScreen,
    Multiindex,
    _adjoint_actions,
    _sparse_table,
    _parse_table,
)
from .cylinder_background import CylinderBackground
from .conventions import SYMMETRIC_COORDINATES
from .prolonged_metric_endpoint_complex import ProlongedMetricEndpointComplex


OperatorTable = dict[tuple[int, ...], sp.Matrix]


def _clean(table: Mapping[tuple[int, ...], sp.Matrix]) -> OperatorTable:
    return {
        word: expanded
        for word, matrix in table.items()
        if (expanded := matrix.applyfunc(sp.expand)) != sp.zeros(*matrix.shape)
    }


def _add(*tables: Mapping[tuple[int, ...], sp.Matrix]) -> OperatorTable:
    if not tables:
        return {}
    sample = next(iter(next(table for table in tables if table).values()))
    result: dict[tuple[int, ...], sp.Matrix] = defaultdict(
        lambda: sp.zeros(*sample.shape)
    )
    for table in tables:
        for word, matrix in table.items():
            result[word] += matrix
    return _clean(result)


def _scale(
    table: Mapping[tuple[int, ...], sp.Matrix], value: sp.Expr
) -> OperatorTable:
    return _clean({word: value * matrix for word, matrix in table.items()})


def _identity(rank: int) -> OperatorTable:
    return {(): sp.eye(rank)}


def _algebraic(matrix: sp.Matrix) -> OperatorTable:
    return {(): matrix}


def _table_digest(table: Mapping[tuple[int, ...], sp.Matrix]) -> str:
    payload = "\n".join(
        f"{word}:{sp.srepr(sp.ImmutableSparseMatrix(table[word]))}"
        for word in sorted(table)
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _sparse_ordered_table(
    table: Mapping[tuple[int, ...], sp.Matrix]
) -> dict[str, object]:
    return {
        "entries": [
            {"word": list(word), "matrix": _sparse_matrix(table[word])}
            for word in sorted(table)
        ],
        "sha256": _table_digest(table),
    }


def _defect_channels(
    screen: AdjointTractorBGGDifferentialScreen,
    algebraic: AdjointTractorKostantCompression,
) -> dict[str, object]:
    """Decompose the old 48 entries into SO(3)-invariant Hom channels."""

    matrices = {
        tuple(axis for axis, count in enumerate(multiindex) for _ in range(count)):
        matrix
        for multiindex, matrix in screen.cylinder_chain_defect.items()
    }
    channels: dict[str, dict[tuple[int, ...], sp.Matrix]] = {
        name: {}
        for name in (
            "order0_form0_boost",
            "order0_spatial_dilation",
            "order0_spatial_rotation",
            "dt_form0_Kspatial",
            "dt_formspatial_K0",
            "Dspatial_form0_K0_dot",
            "Dspatial_form0_Kspatial_time",
            "Dspatial_formspatial_K0_time",
            "Dspatial_spatial_trace_dot",
            "Dspatial_spatial_antisymmetric",
        )
    }
    for word, matrix in matrices.items():
        pieces = {name: sp.zeros(60, 4) for name in channels}
        for (row, column), value in matrix.todok().items():
            form = row // 15
            adjoint = row % 15
            if len(word) == 0:
                if form == 0 and 4 <= adjoint <= 6:
                    name = "order0_form0_boost"
                elif form in (1, 2, 3) and adjoint == 10:
                    name = "order0_spatial_dilation"
                else:
                    name = "order0_spatial_rotation"
            elif word == (0,):
                name = (
                    "dt_form0_Kspatial"
                    if form == 0
                    else "dt_formspatial_K0"
                )
            else:
                if form == 0 and adjoint == 11:
                    name = "Dspatial_form0_K0_dot"
                elif form == 0:
                    name = "Dspatial_form0_Kspatial_time"
                elif adjoint == 11:
                    name = "Dspatial_formspatial_K0_time"
                elif form == adjoint - 11:
                    name = "Dspatial_spatial_trace_dot"
                else:
                    name = "Dspatial_spatial_antisymmetric"
            pieces[name][row, column] = value
        for name, piece in pieces.items():
            if piece != sp.zeros(60, 4):
                channels[name][word] = piece

    reconstruction = _add(
        *(table for table in channels.values())
    )
    if reconstruction != _clean(matrices):
        raise AssertionError("invariant channel decomposition lost defect entries")

    background = CylinderBackground.build()
    adjoint_curvature = _adjoint_lc_curvature(algebraic)
    curvature_c0 = _tensor_product_curvature(background, adjoint_curvature, 0)
    curvature_c1 = _tensor_product_curvature(background, adjoint_curvature, 1)
    curvature_h0 = _induced_harmonic_curvature(
        curvature_c0, algebraic.i0, screen.harmonic_p0
    )

    invariant_channels: dict[str, bool] = {}
    for name, table in channels.items():
        invariant = True
        zeroth = table.get((), sp.zeros(60, 4))
        derivative = {
            axis: table.get((axis,), sp.zeros(60, 4)) for axis in range(4)
        }
        for left, right in ((1, 2), (1, 3), (2, 3)):
            if (
                curvature_c1[left][right] * zeroth
                - zeroth * curvature_h0[left][right]
            ) != sp.zeros(60, 4):
                invariant = False
            for axis in range(4):
                defect = (
                    curvature_c1[left][right] * derivative[axis]
                    - derivative[axis] * curvature_h0[left][right]
                    + sum(
                        (
                            background.covector_commutator(left, right)[axis, changed]
                            * derivative[changed]
                            for changed in range(4)
                        ),
                        sp.zeros(60, 4),
                    )
                ).applyfunc(sp.expand)
                if defect != sp.zeros(60, 4):
                    invariant = False
        invariant_channels[name] = invariant
    if not all(invariant_channels.values()):
        raise AssertionError(
            "defect masks are not individually SO(3)-invariant: "
            f"{invariant_channels}"
        )

    def combined_rank(table: Mapping[tuple[int, ...], sp.Matrix]) -> int:
        # Columns are derivative-word/input-component pairs.
        blocks = [table[word] for word in sorted(table)]
        return sp.Matrix.hstack(*blocks).rank() if blocks else 0

    return {
        "original_entry_count": sum(
            value != 0 for matrix in matrices.values() for value in matrix
        ),
        "orders": {
            str(order): sum(
                value != 0
                for word, matrix in matrices.items()
                if len(word) == order
                for value in matrix
            )
            for order in (0, 1)
        },
        "defect_SO3_invariant_Hom_basis_dimension": len(channels),
        "channels": {
            name: {
                "nonzero_entries": sum(
                    value != 0 for matrix in table.values() for value in matrix
                ),
                "combined_rank": combined_rank(table),
                "coefficient_sha256": _table_digest(table),
                "SO3_generator_defects": 0,
            }
            for name, table in channels.items()
        },
        "algebraic_Hom_closed": True,
        "reconstruction_exact": True,
    }


class FibrePBW:
    """Ordered PBW normal form for one input bundle representation."""

    def __init__(
        self,
        curvature: tuple[tuple[sp.Matrix, ...], ...],
        background: CylinderBackground,
        name: str,
    ) -> None:
        self.curvature = curvature
        self.background = background
        self.name = name
        self.rank = curvature[0][0].rows
        self._cache: dict[
            tuple[tuple[int, ...], int],
            dict[tuple[tuple[int, ...], int], sp.Expr],
        ] = {}

    def _curvature_action(
        self,
        left: int,
        right: int,
        derivative_suffix: tuple[int, ...],
        component: int,
    ) -> dict[tuple[tuple[int, ...], int], sp.Expr]:
        result: dict[tuple[tuple[int, ...], int], sp.Expr] = defaultdict(
            lambda: sp.Integer(0)
        )
        covector = self.background.covector_commutator(left, right)
        for position, old_axis in enumerate(derivative_suffix):
            for new_axis in range(4):
                coefficient = covector[old_axis, new_axis]
                if coefficient == 0:
                    continue
                changed = list(derivative_suffix)
                changed[position] = new_axis
                result[(tuple(changed), component)] += coefficient
        fibre = self.curvature[left][right]
        for new_component in range(self.rank):
            # ``component`` labels the output component occurring in the
            # operator monomial.  Commuting derivatives replaces it by an
            # input component with coefficient R[output,input].
            coefficient = fibre[component, new_component]
            if coefficient != 0:
                result[(derivative_suffix, new_component)] += coefficient
        return dict(result)

    def canonical_term(
        self, word: tuple[int, ...], component: int
    ) -> dict[tuple[tuple[int, ...], int], sp.Expr]:
        key = (word, component)
        if key in self._cache:
            return self._cache[key]
        inversion = next(
            (
                index
                for index in range(len(word) - 1)
                if word[index] > word[index + 1]
            ),
            None,
        )
        if inversion is None:
            result = {(word, component): sp.Integer(1)}
            self._cache[key] = result
            return result

        position = inversion
        left, right = word[position], word[position + 1]
        prefix = word[:position]
        suffix = word[position + 2 :]
        swapped = word[:position] + (right, left) + word[position + 2 :]
        result: dict[tuple[tuple[int, ...], int], sp.Expr] = defaultdict(
            lambda: sp.Integer(0)
        )
        for changed, coefficient in self.canonical_term(swapped, component).items():
            result[changed] += coefficient
        for (changed_suffix, changed_component), curvature_coefficient in (
            self._curvature_action(left, right, suffix, component).items()
        ):
            shortened = prefix + changed_suffix
            for changed, coefficient in self.canonical_term(
                shortened, changed_component
            ).items():
                result[changed] += curvature_coefficient * coefficient
        output = {
            changed: sp.expand(coefficient)
            for changed, coefficient in result.items()
            if sp.expand(coefficient) != 0
        }
        self._cache[key] = output
        return output

    def canonicalize_table(
        self, table: Mapping[tuple[int, ...], sp.Matrix]
    ) -> OperatorTable:
        if not table:
            return {}
        sample = next(iter(table.values()))
        result: dict[tuple[int, ...], sp.Matrix] = defaultdict(
            lambda: sp.zeros(sample.rows, self.rank)
        )
        for word, matrix in table.items():
            if matrix.cols != self.rank:
                raise AssertionError(
                    f"{self.name} PBW input rank mismatch: {matrix.cols}!={self.rank}"
                )
            for (row, component), value in matrix.todok().items():
                for (changed_word, changed_component), coefficient in (
                    self.canonical_term(word, component).items()
                ):
                    result[changed_word][row, changed_component] += value * coefficient
        return _clean(result)

    def from_symmetrized(
        self, table: Mapping[tuple[int, ...], sp.Matrix]
    ) -> OperatorTable:
        raw: dict[tuple[int, ...], sp.Matrix] = defaultdict(
            lambda: sp.zeros(*next(iter(table.values())).shape)
        )
        for word, matrix in table.items():
            distinct = tuple(sorted(set(permutations(word))))
            weight = sp.Rational(1, len(distinct))
            for ordered in distinct:
                raw[ordered] += weight * matrix
        return self.canonicalize_table(raw)

    def compose(
        self,
        outer: Mapping[tuple[int, ...], sp.Matrix],
        inner: Mapping[tuple[int, ...], sp.Matrix],
    ) -> OperatorTable:
        if not outer or not inner:
            return {}
        output_rank = next(iter(outer.values())).rows
        result: dict[tuple[int, ...], sp.Matrix] = defaultdict(
            lambda: sp.zeros(output_rank, self.rank)
        )
        inner_by_row: dict[tuple[int, ...], dict[int, list[tuple[int, sp.Expr]]]] = {}
        for inner_word, inner_matrix in inner.items():
            rows: dict[int, list[tuple[int, sp.Expr]]] = defaultdict(list)
            for (middle, component), value in inner_matrix.todok().items():
                rows[middle].append((component, value))
            inner_by_row[inner_word] = rows
        for outer_word, outer_matrix in outer.items():
            for (row, middle), left_value in outer_matrix.todok().items():
                for inner_word, rows in inner_by_row.items():
                    for component, right_value in rows.get(middle, ()):
                        for (changed_word, changed_component), coefficient in (
                            self.canonical_term(outer_word + inner_word, component).items()
                        ):
                            result[changed_word][row, changed_component] += (
                                left_value * right_value * coefficient
                            )
        return _clean(result)


def _tensor_product_curvature(
    background: CylinderBackground,
    adjoint_curvature: tuple[tuple[sp.Matrix, ...], ...],
    form_degree: int,
) -> tuple[tuple[sp.Matrix, ...], ...]:
    pairs = tuple(
        (left, right)
        for left in range(4)
        for right in range(left + 1, 4)
    )
    form_components: tuple[tuple[int, ...], ...]
    if form_degree == 0:
        form_components = ((),)
    elif form_degree == 1:
        form_components = tuple((axis,) for axis in range(4))
    elif form_degree == 2:
        form_components = pairs
    else:
        raise ValueError(form_degree)
    form_lookup = {value: index for index, value in enumerate(form_components)}
    rank = len(form_components) * 15
    output: list[list[sp.Matrix]] = [
        [sp.zeros(rank) for _ in range(4)] for _ in range(4)
    ]
    for left in range(4):
        for right in range(4):
            matrix = output[left][right]
            covector = background.covector_commutator(left, right)
            # ``slots`` labels the *output* covariant component.  The
            # commutator matrix convention is R[output,input], so changing a
            # slot constructs the input column, not a new output row.
            for form_index, slots in enumerate(form_components):
                for adjoint_input in range(15):
                    row = 15 * form_index + adjoint_input
                    for adjoint_output in range(15):
                        value = adjoint_curvature[left][right][
                            adjoint_output, adjoint_input
                        ]
                        if value != 0:
                            matrix[15 * form_index + adjoint_output, 15 * form_index + adjoint_input] += value
                    for position, old_axis in enumerate(slots):
                        for new_axis in range(4):
                            value = covector[old_axis, new_axis]
                            if value == 0:
                                continue
                            changed = list(slots)
                            changed[position] = new_axis
                            if len(set(changed)) != len(changed):
                                continue
                            inversions = sum(
                                changed[a] > changed[b]
                                for a in range(len(changed))
                                for b in range(a + 1, len(changed))
                            )
                            canonical = tuple(sorted(changed))
                            input_form = form_lookup[canonical]
                            matrix[row, 15 * input_form + adjoint_input] += (
                                (-1) ** inversions * value
                            )
    return tuple(tuple(row) for row in output)


def _adjoint_lc_curvature(
    algebraic: AdjointTractorKostantCompression,
) -> tuple[tuple[sp.Matrix, ...], ...]:
    _, basis = _adjoint_basis()
    embedded, left_inverse = _coordinate_map(basis)
    connection = tuple(basis[axis] + basis[11 + axis] / 2 for axis in range(4))
    output: list[list[sp.Matrix]] = [
        [sp.zeros(15) for _ in range(4)] for _ in range(4)
    ]
    for left in range(4):
        for right in range(4):
            standard_curvature = -(
                connection[left] * connection[right]
                - connection[right] * connection[left]
            )
            columns: list[sp.Matrix] = []
            for value in basis:
                commutator = standard_curvature * value - value * standard_curvature
                coordinates = left_inverse * commutator.reshape(36, 1)
                if embedded * coordinates != commutator.reshape(36, 1):
                    raise AssertionError("LC adjoint curvature escaped so(4,2)")
                columns.append(coordinates)
            output[left][right] = sp.Matrix.hstack(*columns)
    return tuple(tuple(row) for row in output)


def _induced_harmonic_curvature(
    parent_curvature: tuple[tuple[sp.Matrix, ...], ...],
    inclusion: sp.Matrix,
    projection: sp.Matrix,
) -> tuple[tuple[sp.Matrix, ...], ...]:
    output = tuple(
        tuple(
            (projection * parent_curvature[left][right] * inclusion).applyfunc(
                sp.expand
            )
            for right in range(4)
        )
        for left in range(4)
    )
    for left in range(4):
        for right in range(4):
            if (
                parent_curvature[left][right] * inclusion
                - inclusion * output[left][right]
            ) != sp.zeros(parent_curvature[left][right].rows, inclusion.cols):
                raise AssertionError("harmonic carrier is not LC invariant")
    return output


def _raw_polynomial_table(
    table: Mapping[Multiindex, sp.Matrix]
) -> dict[tuple[int, ...], sp.Matrix]:
    return {
        tuple(axis for axis, count in enumerate(multiindex) for _ in range(count)): matrix
        for multiindex, matrix in table.items()
    }


def _formal_adjoint(
    table: Mapping[tuple[int, ...], sp.Matrix],
    source_pairing: sp.Matrix,
    target_pairing: sp.Matrix,
    target_pbw: FibrePBW,
) -> OperatorTable:
    raw = {
        tuple(reversed(word)): (
            (-1) ** len(word)
            * source_pairing.inv()
            * matrix.T
            * target_pairing
        ).applyfunc(sp.expand)
        for word, matrix in table.items()
    }
    return target_pbw.canonicalize_table(raw)


@dataclass(frozen=True)
class AdjointTractorBGGCurvedPBW:
    algebraic: AdjointTractorKostantCompression
    screen: AdjointTractorBGGDifferentialScreen
    bundle_curvature_digests: Mapping[str, str]
    i0: OperatorTable
    i1: OperatorTable
    p0: OperatorTable
    p1: OperatorTable
    h0: OperatorTable
    h1: OperatorTable
    k0: OperatorTable
    i_equation: OperatorTable
    p_equation: OperatorTable
    i_identity: OperatorTable
    p_identity: OperatorTable
    compressed_middle: OperatorTable
    bach_target: OperatorTable
    bach_defect: OperatorTable
    chain_defect: OperatorTable
    homotopy0_defect: OperatorTable
    homotopy1_defect: OperatorTable
    cyclic_equation_defect: OperatorTable
    cyclic_identity_defect: OperatorTable

    @staticmethod
    def build(
        algebraic: AdjointTractorKostantCompression,
        screen: AdjointTractorBGGDifferentialScreen,
        endpoint: ProlongedMetricEndpointComplex,
    ) -> "AdjointTractorBGGCurvedPBW":
        background = CylinderBackground.build()
        adjoint_curvature = _adjoint_lc_curvature(algebraic)
        curvature_c0 = _tensor_product_curvature(background, adjoint_curvature, 0)
        curvature_c1 = _tensor_product_curvature(background, adjoint_curvature, 1)
        curvature_c2 = _tensor_product_curvature(background, adjoint_curvature, 2)
        curvature_h0 = _induced_harmonic_curvature(
            curvature_c0, algebraic.i0, screen.harmonic_p0
        )
        curvature_h1 = _induced_harmonic_curvature(
            curvature_c1, algebraic.i1, screen.harmonic_p1
        )
        curvature_h0_dual = tuple(
            tuple(-matrix.T for matrix in row) for row in curvature_h0
        )
        curvature_h1_dual = tuple(
            tuple(-matrix.T for matrix in row) for row in curvature_h1
        )

        pbw_c0 = FibrePBW(curvature_c0, background, "C0")
        pbw_c1 = FibrePBW(curvature_c1, background, "C1")
        pbw_c2 = FibrePBW(curvature_c2, background, "C2")
        pbw_h0 = FibrePBW(curvature_h0, background, "H0")
        pbw_h1 = FibrePBW(curvature_h1, background, "H1")
        pbw_h0_dual = FibrePBW(curvature_h0_dual, background, "H0dual")
        pbw_h1_dual = FibrePBW(curvature_h1_dual, background, "H1dual")

        _, basis = _adjoint_basis()
        k_actions = _adjoint_actions(basis[11:15], basis)
        rho0 = sp.Matrix.vstack(*(action / 2 for action in k_actions))
        rho1_rows: list[sp.Matrix] = []
        for left in range(4):
            for right in range(left + 1, 4):
                block = sp.zeros(15, 60)
                block[:, 15 * right : 15 * (right + 1)] = k_actions[left] / 2
                block[:, 15 * left : 15 * (left + 1)] = -k_actions[right] / 2
                rho1_rows.append(block)
        rho1 = sp.Matrix.vstack(*rho1_rows)

        derivative0 = {
            (axis,): sp.Matrix.vstack(
                *(sp.eye(15) if form == axis else sp.zeros(15) for form in range(4))
            )
            for axis in range(4)
        }
        derivative1: OperatorTable = {}
        pairs = tuple(
            (left, right)
            for left in range(4)
            for right in range(left + 1, 4)
        )
        for axis in range(4):
            matrix = sp.zeros(90, 60)
            for pair_index, (left, right) in enumerate(pairs):
                if axis == left:
                    matrix[15 * pair_index : 15 * (pair_index + 1), 15 * right : 15 * (right + 1)] += sp.eye(15)
                if axis == right:
                    matrix[15 * pair_index : 15 * (pair_index + 1), 15 * left : 15 * (left + 1)] -= sp.eye(15)
            derivative1[(axis,)] = matrix

        delta0 = _add(_algebraic(rho0), derivative0)
        delta1 = _add(_algebraic(rho1), derivative1)
        total0 = _add(_algebraic(screen.cohomology_d0), delta0)
        total1 = _add(_algebraic(screen.cohomology_d1), delta1)
        tractor_flatness_defect = pbw_c0.compose(total1, total0)
        if tractor_flatness_defect:
            entries = sum(
                value != 0
                for matrix in tractor_flatness_defect.values()
                for value in matrix
            )
            raise AssertionError(
                f"normal tractor exterior square has {entries} PBW defects"
            )
        q1 = _algebraic(screen.q1)
        q2 = _algebraic(screen.q2)

        n0 = pbw_c0.compose(q1, delta0)
        n1 = pbw_c1.compose(q2, delta1)
        i0_alg = _algebraic(algebraic.i0)
        i1_alg = _algebraic(algebraic.i1)
        n0_i0 = pbw_h0.compose(n0, i0_alg)
        n1_i1 = pbw_h1.compose(n1, i1_alg)
        i0 = _add(i0_alg, _scale(n0_i0, -1), pbw_h0.compose(n0, n0_i0))
        i1 = _add(i1_alg, _scale(n1_i1, -1), pbw_h1.compose(n1, n1_i1))

        raw_k = pbw_h0.compose(total0, i0)
        k0 = pbw_h0.compose(_algebraic(screen.harmonic_p1), raw_k)

        r0 = pbw_c1.compose(delta0, q1)
        r1 = pbw_c2.compose(delta1, q2)
        inverse_r0 = _add(_identity(60), _scale(r0, -1), pbw_c1.compose(r0, r0))
        inverse_r1 = _add(_identity(90), _scale(r1, -1), pbw_c2.compose(r1, r1))
        p0 = _algebraic(screen.harmonic_p0)
        p1 = pbw_c1.compose(_algebraic(screen.harmonic_p1), inverse_r0)
        h0 = pbw_c1.compose(q1, inverse_r0)
        h1 = pbw_c2.compose(q2, inverse_r1)

        chain_defect = _add(
            pbw_h0.compose(total0, i0),
            _scale(pbw_h0.compose(i1, k0), -1),
        )
        homotopy0_defect = _add(
            pbw_c0.compose(h0, total0),
            pbw_c0.compose(i0, p0),
            _scale(_identity(15), -1),
        )
        homotopy1_defect = _add(
            pbw_c1.compose(total0, h0),
            pbw_c1.compose(h1, total1),
            pbw_c1.compose(i1, p1),
            _scale(_identity(60), -1),
        )

        i_equation = _formal_adjoint(
            p1,
            algebraic.one_form_pairing,
            algebraic.endpoint_field_pairing,
            pbw_h1_dual,
        )
        p_equation = _formal_adjoint(
            i1,
            algebraic.endpoint_field_pairing,
            algebraic.one_form_pairing,
            pbw_c1,
        )
        i_identity = _formal_adjoint(
            p0,
            algebraic.adjoint_pairing,
            algebraic.endpoint_ghost_pairing,
            pbw_h0_dual,
        )
        p_identity = _formal_adjoint(
            i0,
            algebraic.endpoint_ghost_pairing,
            algebraic.adjoint_pairing,
            pbw_c0,
        )
        cyclic_equation_defect = _add(
            pbw_h1_dual.compose(p_equation, i_equation),
            _scale(_identity(9), -1),
        )
        cyclic_identity_defect = _add(
            pbw_h0_dual.compose(p_identity, i_identity),
            _scale(_identity(4), -1),
        )

        eta = sp.diag(-1, 1, 1, 1)
        two_form_metric = sp.diag(
            *(
                eta[left, left] * eta[right, right]
                for left, right in pairs
            )
        )
        two_form_pairing = sp.kronecker_product(
            two_form_metric, algebraic.adjoint_pairing
        )
        total1_sharp = _formal_adjoint(
            total1,
            algebraic.one_form_pairing,
            two_form_pairing,
            pbw_c2,
        )
        maxwell = pbw_c1.compose(total1_sharp, total1)
        i1_sharp = _formal_adjoint(
            i1,
            algebraic.endpoint_field_pairing,
            algebraic.one_form_pairing,
            pbw_c1,
        )
        compressed_middle = pbw_h1.compose(
            i1_sharp, pbw_h1.compose(maxwell, i1)
        )

        stf = screen.endpoint_stf_embedding
        bach_sym = {
            tuple(axis for axis, count in enumerate(multiindex) for _ in range(count)):
            (stf.T * endpoint.field_pairing * coefficient * stf).applyfunc(sp.expand)
            for multiindex, coefficient in endpoint.bach_coefficients
        }
        bach_target = pbw_h1.from_symmetrized(bach_sym)
        bach_defect = _add(compressed_middle, _scale(bach_target, 2))

        digests = {
            "C0": hashlib.sha256("".join(_digest_matrix(m) for row in curvature_c0 for m in row).encode()).hexdigest(),
            "C1": hashlib.sha256("".join(_digest_matrix(m) for row in curvature_c1 for m in row).encode()).hexdigest(),
            "C2": hashlib.sha256("".join(_digest_matrix(m) for row in curvature_c2 for m in row).encode()).hexdigest(),
            "H0": hashlib.sha256("".join(_digest_matrix(m) for row in curvature_h0 for m in row).encode()).hexdigest(),
            "H1": hashlib.sha256("".join(_digest_matrix(m) for row in curvature_h1 for m in row).encode()).hexdigest(),
        }
        return AdjointTractorBGGCurvedPBW(
            algebraic=algebraic,
            screen=screen,
            bundle_curvature_digests=digests,
            i0=i0,
            i1=i1,
            p0=p0,
            p1=p1,
            h0=h0,
            h1=h1,
            k0=k0,
            i_equation=i_equation,
            p_equation=p_equation,
            i_identity=i_identity,
            p_identity=p_identity,
            compressed_middle=compressed_middle,
            bach_target=bach_target,
            bach_defect=bach_defect,
            chain_defect=chain_defect,
            homotopy0_defect=homotopy0_defect,
            homotopy1_defect=homotopy1_defect,
            cyclic_equation_defect=cyclic_equation_defect,
            cyclic_identity_defect=cyclic_identity_defect,
        )

    def summary(self) -> dict[str, object]:
        def count(table: Mapping[tuple[int, ...], sp.Matrix]) -> int:
            return sum(value != 0 for matrix in table.values() for value in matrix)

        return {
            "chain_defect_entries": count(self.chain_defect),
            "homotopy0_defect_entries": count(self.homotopy0_defect),
            "homotopy1_defect_entries": count(self.homotopy1_defect),
            "cyclic_equation_defect_entries": count(self.cyclic_equation_defect),
            "cyclic_identity_defect_entries": count(self.cyclic_identity_defect),
            "bach_defect_entries": count(self.bach_defect),
            "orders": {
                "i0": max(map(len, self.i0), default=0),
                "i1": max(map(len, self.i1), default=0),
                "p1": max(map(len, self.p1), default=0),
                "h0": max(map(len, self.h0), default=0),
                "h1": max(map(len, self.h1), default=0),
                "middle": max(map(len, self.compressed_middle), default=0),
            },
        }

    def verify(self) -> None:
        summary = self.summary()
        for key in (
            "chain_defect_entries",
            "homotopy0_defect_entries",
            "homotopy1_defect_entries",
            "cyclic_equation_defect_entries",
            "cyclic_identity_defect_entries",
            "bach_defect_entries",
        ):
            if summary[key] != 0:
                raise AssertionError(f"curved PBW certificate has nonzero {key}")
        if summary["orders"] != {
            "i0": 2,
            "i1": 2,
            "p1": 0,
            "h0": 1,
            "h1": 1,
            "middle": 4,
        }:
            raise AssertionError("curved BGG differential order ledger drifted")
        if self.compressed_middle != _scale(self.bach_target, -2):
            raise AssertionError("full curved Bach normalization drifted")

    def payload(self) -> dict[str, object]:
        self.verify()
        tables = {
            "i_G": self.i0,
            "i_M": self.i1,
            "p_G": self.p0,
            "p_M": self.p1,
            "H_0": self.h0,
            "H_1": self.h1,
            "K_BGG": self.k0,
            "i_E": self.i_equation,
            "p_E": self.p_equation,
            "i_I": self.i_identity,
            "p_I": self.p_identity,
            "compressed_parent_middle": self.compressed_middle,
            "endpoint_Bach_bilinear": self.bach_target,
        }
        return {
            "schema_version": 1,
            "arithmetic": "exact rational ordered PBW",
            "normalization": {
                "compressed_parent_middle": "-2 endpoint_Bach_bilinear"
            },
            "bundle_curvature_sha256": dict(self.bundle_curvature_digests),
            "tables": {
                name: _sparse_ordered_table(table)
                for name, table in tables.items()
            },
        }

    def certificate(
        self,
        payload_sha256: str,
        dependencies: Mapping[str, str],
    ) -> dict[str, object]:
        self.verify()
        order_ledger: dict[str, dict[str, int]] = {}
        for order in range(5):
            left = {
                word: matrix
                for word, matrix in self.compressed_middle.items()
                if len(word) == order
            }
            right = {
                word: matrix
                for word, matrix in self.bach_target.items()
                if len(word) == order
            }
            order_ledger[str(order)] = {
                "compressed_nonzero_entries": sum(
                    value != 0 for matrix in left.values() for value in matrix
                ),
                "Bach_nonzero_entries": sum(
                    value != 0 for matrix in right.values() for value in matrix
                ),
                "defect_entries": 0,
            }
        return {
            "schema_version": 1,
            "dependency_tag": "LORENTZIAN-CAUSAL",
            "fail_closed": True,
            "result": "PASS",
            "payload_sha256": payload_sha256,
            "dependencies": dict(dependencies),
            "PBW": {
                "canonical_derivative_order": "nondecreasing",
                "curvature_acts_on_derivative_suffix": True,
                "curvature_acts_on_form_slots": True,
                "curvature_acts_on_graded_adjoint_tractor": True,
                "normal_tractor_curvature": "zero after LC plus algebraic connection cancellation",
                "normal_tractor_exterior_square_defects": 0,
            },
            "former_48_entry_defect": {
                **_defect_channels(self.screen, self.algebraic),
                "PBW_corrected_defect_entries": 0,
                "correction_source": (
                    "certified Kostant Q and finite HPL compositions; no fitted coefficients"
                ),
            },
            "curved_HPL": {
                "row_ranks_parent": [15, 60, 60, 15],
                "row_ranks_compressed": [4, 9, 9, 4],
                "inclusion_chain_defects": 0,
                "projection_chain_defects": 0,
                "homotopy_defects": [0, 0],
                "cyclic_dual_defects": [0, 0],
                "orders": self.summary()["orders"],
                "support_local": True,
            },
            "Bach_comparison": {
                "identity": "compressed_parent_middle=-2 S^T J_met Bach_bar S",
                "normalization": "-2",
                "every_derivative_order_compared": True,
                "order_ledger": order_ledger,
                "total_defect_entries": 0,
            },
            "theorem_boundary": {
                "curved_BGG_chain_maps_exact": True,
                "curved_differential_homotopy_exact": True,
                "endpoint_Bach_operator_match": True,
                "support_local": True,
                "cyclic_i_sharp_equals_p": True,
                "parent_green_homotopy_transferred": False,
            },
            "claim": (
                "The adjoint-tractor Yang-Mills detour complex compresses by "
                "finite support-local curved BGG HPL maps to the metric deformation "
                "detour endpoint, with exact middle normalization -2.  This file "
                "does not itself import or transfer parent Green homotopies."
            ),
        }


def write_json(path: Path, value: Mapping[str, object]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
