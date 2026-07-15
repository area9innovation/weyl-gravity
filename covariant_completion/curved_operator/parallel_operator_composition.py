"""Component-aware composition of parallel operators on the 24-field bundle.

The derivative normal-form engine acts on abstract covariant tensor slots.
This adapter converts the ``h[10]+f[10]+v[4]`` component convention to those
slots, composes sparse parallel coefficient tables, and converts curvature-
changed slots back to component columns.  It is the required backend for the
quadratic lower-order factor solve; ordinary Fourier-polynomial matrix
multiplication is insufficient at orders two and zero.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import permutations, product
from typing import Mapping

import sympy as sp

from .conventions import SYMMETRIC_COORDINATES, _ordinary_system
from .derivative_normal_form import ParallelCylinderNormalForm


OperatorTable = Mapping[tuple[int, ...], sp.Matrix]


def _column_slots(column: int) -> tuple[int, tuple[int, ...]]:
    if column < 10:
        return 0, SYMMETRIC_COORDINATES[column]
    if column < 20:
        return 10, SYMMETRIC_COORDINATES[column - 10]
    if column < 24:
        return 20, (column - 20,)
    raise IndexError(column)


def _slots_column(block: int, slots: tuple[int, ...]) -> int:
    if block in (0, 10):
        return block + SYMMETRIC_COORDINATES.index(tuple(sorted(slots)))
    if block == 20:
        return 20 + slots[0]
    raise ValueError(block)


def _canonicalize_table(
    table: OperatorTable,
    normal_form: ParallelCylinderNormalForm,
) -> dict[tuple[int, ...], sp.Matrix]:
    """Canonicalize derivative words, including field-slot curvature."""

    output: dict[tuple[int, ...], sp.Matrix] = defaultdict(lambda: sp.zeros(24))
    for word, matrix in table.items():
        for (row, column), value in matrix.todok().items():
            block, slots = _column_slots(column)
            canonical = normal_form.canonicalize({(word, slots): value})
            for (new_word, changed_slots), coefficient in canonical.items():
                changed_column = _slots_column(block, changed_slots)
                output[new_word][row, changed_column] += coefficient
    return {
        word: matrix.applyfunc(sp.expand)
        for word, matrix in output.items()
        if matrix != sp.zeros(24)
    }


def _table_defect(
    left: OperatorTable,
    right: OperatorTable,
) -> dict[tuple[int, ...], sp.Matrix]:
    keys = set(left) | set(right)
    return {
        word: defect
        for word in keys
        if (
            defect := sp.Matrix(
                left.get(word, sp.zeros(24)) - right.get(word, sp.zeros(24))
            ).applyfunc(sp.expand)
        )
        != sp.zeros(24)
    }


def _defect_nonzero_entries(defect: OperatorTable) -> int:
    return sum(value != 0 for matrix in defect.values() for value in matrix)


def polynomial_table(
    matrix: sp.Matrix,
    covector: tuple[sp.Symbol, ...],
    maximum_order: int,
    *,
    normal_form: ParallelCylinderNormalForm | None = None,
) -> dict[tuple[int, ...], sp.Matrix]:
    """Convert a symmetrized covariant-jet polynomial to ordered words.

    The emitted Hessian polynomial uses symmetrized covariant derivatives.
    Replacing a monomial by one sorted derivative word would miss the
    curvature terms produced when the distinct permutations are averaged.
    """

    if normal_form is None:
        normal_form = ParallelCylinderNormalForm.build()
    raw: dict[tuple[int, ...], sp.Matrix] = defaultdict(lambda: sp.zeros(24))
    for degree in range(maximum_order + 1):
        for multiindex in product(range(degree + 1), repeat=4):
            if sum(multiindex) != degree:
                continue
            sorted_word = tuple(
                axis for axis, count in enumerate(multiindex) for _ in range(count)
            )
            coefficient = matrix.applyfunc(
                lambda entry: sp.Poly(entry, *covector).coeff_monomial(
                    sp.prod(covector[a] ** multiindex[a] for a in range(4))
                )
            )
            if coefficient != sp.zeros(24):
                words = tuple(sorted(set(permutations(sorted_word))))
                weight = sp.Rational(1, len(words))
                for word in words:
                    raw[word] += weight * coefficient
    return _canonicalize_table(raw, normal_form)


@dataclass(frozen=True)
class ParallelFieldOperatorComposer:
    normal_form: ParallelCylinderNormalForm

    @staticmethod
    def build() -> "ParallelFieldOperatorComposer":
        result = ParallelFieldOperatorComposer(ParallelCylinderNormalForm.build())
        result.verify()
        return result

    def compose(
        self, outer: OperatorTable, inner: OperatorTable
    ) -> dict[tuple[int, ...], sp.Matrix]:
        result: dict[tuple[int, ...], sp.Matrix] = defaultdict(lambda: sp.zeros(24))
        for outer_word, outer_matrix in outer.items():
            outer_nonzero = [
                (row, middle, outer_matrix[row, middle])
                for row in range(24)
                for middle in range(24)
                if outer_matrix[row, middle] != 0
            ]
            for inner_word, inner_matrix in inner.items():
                inner_by_row = {
                    middle: [
                        (column, inner_matrix[middle, column])
                        for column in range(24)
                        if inner_matrix[middle, column] != 0
                    ]
                    for middle in range(24)
                }
                for row, middle, left in outer_nonzero:
                    for column, right in inner_by_row[middle]:
                        block, slots = _column_slots(column)
                        canonical = self.normal_form.canonicalize(
                            {(outer_word + inner_word, slots): left * right}
                        )
                        for (word, changed_slots), coefficient in canonical.items():
                            changed_column = _slots_column(block, changed_slots)
                            result[word][row, changed_column] += coefficient
        return {
            word: matrix.applyfunc(sp.expand)
            for word, matrix in result.items()
            if matrix != sp.zeros(24)
        }

    def naive_sorted_table_adjoint(
        self,
        table: OperatorTable,
        pairing: sp.Matrix | None = None,
    ) -> dict[tuple[int, ...], sp.Matrix]:
        """Diagnostic transpose/reversal of an ordered component table.

        This is deliberately *not* exposed as the formal-adjoint backend.
        Once a parallel invariant coefficient tensor has been reduced to
        sorted component words, its word coefficients are not individually
        parallel bundle endomorphisms.  The 48-entry Box-square regression
        below demonstrates that componentwise transpose/reversal is invalid;
        adjoints must be formed before this reduction or in a symmetrized-jet
        or PBW representation retaining the coefficient-index slots.
        """

        if pairing is None:
            pairing = _ordinary_system().field_fibre_pairing
        if pairing.shape != (24, 24) or pairing.det() == 0:
            raise ValueError("formal adjoint requires a nondegenerate 24-field pairing")
        inverse = pairing.inv()
        raw = {
            tuple(reversed(word)): sp.simplify(
                (-1) ** len(word) * inverse * matrix.T * pairing
            )
            for word, matrix in table.items()
        }
        return _canonicalize_table(raw, self.normal_form)

    def verify(self) -> None:
        identity = {(): sp.eye(24)}
        if self.compose(identity, identity) != identity:
            raise AssertionError("parallel operator identity composition failed")
        metric = _ordinary_system().metric
        box = {
            (axis, axis): metric[axis, axis] * sp.eye(24)
            for axis in range(4)
        }
        box_square = self.compose(box, box)
        if sorted({len(word) for word in box_square}) != [0, 2, 4]:
            raise AssertionError("box-square curved order ledger drifted")

        # The symmetrized covariant-jet polynomial zeta_1 zeta_2 v_1 is
        # nabla_(1 nabla_2) v_1.  Its ordered form contains the signed
        # half-commutator -v_2/2.
        covector = tuple(sp.symbols("parallel_composer_zeta_0:4"))
        symmetrized = sp.zeros(24)
        symmetrized[21, 21] = covector[1] * covector[2]
        converted = polynomial_table(
            symmetrized, covector, 2, normal_form=self.normal_form
        )
        if converted.get((1, 2), sp.zeros(24))[21, 21] != 1:
            raise AssertionError("symmetrized second derivative principal term drifted")
        if converted.get((), sp.zeros(24))[21, 22] != -sp.Rational(1, 2):
            raise AssertionError("symmetrized derivative curvature sign drifted")

        # Independent Weitzenboeck regression:
        # div(symgrad v)=Box v+grad(div v)+Ric(v).  It detects mixed
        # time--space curvature accidentally introduced by a four-dimensional
        # delta in the cylinder commutator.
        symgrad: dict[tuple[int, ...], sp.Matrix] = defaultdict(
            lambda: sp.zeros(24)
        )
        divergence: dict[tuple[int, ...], sp.Matrix] = defaultdict(
            lambda: sp.zeros(24)
        )
        for row, (a, b) in enumerate(SYMMETRIC_COORDINATES):
            symgrad[(a,)][row, 20 + b] += 1
            symgrad[(b,)][row, 20 + a] += 1
        for output_index in range(4):
            for axis in range(4):
                tensor_column = SYMMETRIC_COORDINATES.index(
                    tuple(sorted((axis, output_index)))
                )
                divergence[(axis,)][20 + output_index, tensor_column] += metric[
                    axis, axis
                ]
        div_symgrad = self.compose(divergence, symgrad)
        expected_raw: dict[tuple[int, ...], sp.Matrix] = defaultdict(
            lambda: sp.zeros(24)
        )
        for output_index in range(4):
            for axis in range(4):
                expected_raw[(axis, axis)][
                    20 + output_index, 20 + output_index
                ] += metric[axis, axis]
                expected_raw[(output_index, axis)][
                    20 + output_index, 20 + axis
                ] += metric[axis, axis]
        for spatial_index in range(1, 4):
            expected_raw[()][20 + spatial_index, 20 + spatial_index] += 2
        expected = _canonicalize_table(expected_raw, self.normal_form)
        if _table_defect(div_symgrad, expected):
            raise AssertionError("div-symgrad curvature-sign regression failed")

        # Fail-closed formal-adjoint audit.  Box^2 is self-adjoint, but the
        # naive operation which transposes/reverses each *already sorted*
        # component table entry has this exact defect.  This proves that such
        # entries cannot be treated as individually parallel coefficients;
        # it does not by itself disprove the primal composition table.
        adjoint_defect = _table_defect(
            self.naive_sorted_table_adjoint(box_square), box_square
        )
        if _defect_nonzero_entries(adjoint_defect) != 48:
            raise AssertionError("naive sorted-table adjoint limitation drifted")

        # Independent coordinate-jet comparison of the primal Box-square
        # composition.  These samples include scalar-like, vector and tensor
        # curvature channels and do not use the sorted-word commutator engine
        # to compute the reference result.
        from .covariant_jets import CovariantJetBasis

        jet_basis = CovariantJetBasis.build(verify=False)

        def table_value(section, rank: int) -> sp.Matrix:
            tensor = (
                {(a,): section[a] for a in range(4)}
                if rank == 1
                else {
                    (a, b): section[a][b]
                    for a in range(4)
                    for b in range(4)
                }
            )
            derivatives = {
                order: (
                    tensor
                    if order == 0
                    else jet_basis._covariant_derivatives(tensor, order)
                )
                for order in {len(word) for word in box_square}
            }
            output = sp.zeros(24, 1)
            for word, matrix in box_square.items():
                value = sp.zeros(24, 1)
                if rank == 1:
                    for component in range(4):
                        value[20 + component] = derivatives[len(word)][
                            word + (component,)
                        ].value
                else:
                    for component, indices in enumerate(SYMMETRIC_COORDINATES):
                        value[component] = derivatives[len(word)][
                            word + indices
                        ].value
                output += matrix * value
            return output.applyfunc(sp.expand)

        vector_section = jet_basis.covariant_monomial_covector(
            1, (1, 1, 0, 0), 4
        )
        exact_vector = jet_basis.geometry.rough_wave_covector(
            jet_basis.geometry.rough_wave_covector(vector_section)
        )
        if table_value(vector_section, 1)[20:24, :] != sp.Matrix(
            [entry.value for entry in exact_vector]
        ):
            raise AssertionError("Box-square vector coordinate-jet defect")

        tensor_section = jet_basis.covariant_monomial_symmetric(
            5, (0, 1, 1, 1), 4
        )
        exact_tensor = jet_basis.geometry.rough_wave_symmetric(
            jet_basis.geometry.rough_wave_symmetric(tensor_section)
        )
        exact_tensor_coordinates = sp.Matrix(
            [exact_tensor[a][b].value for a, b in SYMMETRIC_COORDINATES]
        )
        if table_value(tensor_section, 2)[:10, :] != exact_tensor_coordinates:
            raise AssertionError("Box-square tensor coordinate-jet defect")

    def certificate(self) -> dict[str, object]:
        self.verify()
        metric = _ordinary_system().metric
        box = {
            (axis, axis): metric[axis, axis] * sp.eye(24)
            for axis in range(4)
        }
        square = self.compose(box, box)
        adjoint_defect = _table_defect(
            self.naive_sorted_table_adjoint(square), square
        )
        return {
            "schema": "pure-weyl-parallel-24-field-operator-composer-v2",
            "bundle_order": "h[10]+f[10]+v[4]",
            "canonical_derivative_order": "nondecreasing indices",
            "curvature_action_slots": "inner derivatives plus every input tensor slot",
            "parallel_coefficient_assumption": True,
            "identity_composition": True,
            "box_square_orders": sorted({len(word) for word in square}),
            "box_square_order_two_curvature_present": True,
            "mixed_time_space_curvature_zero": True,
            "symmetrized_order_two_conversion_exact": True,
            "div_symgrad_Weitzenboeck_defect": 0,
            "box_square_coordinate_jet_regressions": 2,
            "box_square_coordinate_jet_defects": 0,
            "naive_sorted_table_adjoint_defect_entries": (
                _defect_nonzero_entries(adjoint_defect)
            ),
            "naive_sorted_table_adjoint_valid": False,
            "primal_composition_counterexample_found": False,
            "standalone_sorted_word_PBW_confluence_proved": False,
            "project_symmetrized_PBW_certificate": "symmetrized_pbw_composition.json",
            "project_quadratic_factor_composition_backend_ready": True,
            "full_factor_certificate_backend_ready": False,
            "quadratic_factor_rank_solve_completed": False,
            "scope": (
                "the mixed curvature sign, symmetrized order-two conversion and "
                "focused primal coordinate-jet compositions are exact.  The "
                "48-entry defect belongs to the invalid naive adjoint of an already "
                "sorted table, not an independent primal-composition counterexample. "
                "The separate exact symmetrized-jet PBW certificate supplies the "
                "project-wide composition proof. A pairing-aware general formal-"
                "adjoint backend and the nonlinear coefficient solve are still "
                "required before a full factor certificate is trusted"
            ),
        }
