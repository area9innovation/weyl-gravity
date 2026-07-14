"""Coefficient chain map from auxiliary equations to curvature equations.

This module derives the first mapping-cylinder component

``E_curv T_state = A_equation E_aux``

at a cylinder base point and globalizes it by homogeneity.  The state map is
``T_state h=(C1 h, div C1 h)`` in the natural 26 curvature coordinates.  The
auxiliary Hessian construction gives the exact local recovery

``B_action h = E_h + S_h^sharp E_f``.

Consequently ``A_equation`` is the composition of this order-two recovery
with a constant map from the nine Bach components to the forty adjusted
curvature rows.  That constant map is solved and verified on the exhaustive
``10*binomial(8,4)=700`` metric four-jet fibre.  No status flag is changed.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from fractions import Fraction
import hashlib
from itertools import product

import sympy as sp

from covariant_completion.curved_operator.conventions import (
    SYMMETRIC_COORDINATES,
    _ordinary_system,
)
from covariant_completion.curved_operator.covariant_jets import CovariantJetBasis
from covariant_completion.curved_operator.expanded_hessian import (
    ExpandedCurvedAuxiliaryHessian,
)
from covariant_completion.curved_operator.weyl_3plus1 import (
    WeylCottonBachFirstOrder,
    tracefree_symmetric_spacetime_basis,
)
from covariant_completion.curved_operator.weyl_cotton_hyperbolic import (
    ConstraintAdjustedWeylCottonEvolution,
)
from covariant_completion.curved_operator.weyl_cotton_row_audit import (
    _old_from_natural_state,
)
from covariant_completion.minimal_witness.cylinder_jets import Jet, _sum
from covariant_completion.minimal_witness.linearized_bach import LinearizedBach, _rank


def _digest_tables(tables: tuple[tuple[tuple[int, ...], sp.Matrix], ...]) -> str:
    payload = "\n".join(
        f"{multiindex}:" + sp.srepr(sp.ImmutableDenseMatrix(matrix))
        for multiindex, matrix in tables
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _digest_matrix(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableDenseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _matrix_times_jets(matrix: sp.Matrix, values: list[Jet]) -> list[Jet]:
    return [
        _sum(matrix[row, column] * values[column] for column in range(matrix.cols))
        for row in range(matrix.rows)
    ]


def _target_extraction() -> sp.Matrix:
    basis = tracefree_symmetric_spacetime_basis()
    inclusion = sp.zeros(16, 9)
    for column, tensor in enumerate(basis):
        for a, b in product(range(4), repeat=2):
            inclusion[4 * a + b, column] = tensor[a, b]
    return (inclusion.T * inclusion).inv() * inclusion.T


def _symmetric_coordinate_inclusion() -> sp.Matrix:
    """Embed the ten symmetric coordinates into all sixteen tensor entries."""

    inclusion = sp.zeros(16, len(SYMMETRIC_COORDINATES))
    for column, (first, second) in enumerate(SYMMETRIC_COORDINATES):
        inclusion[4 * first + second, column] = 1
        inclusion[4 * second + first, column] = 1
    return inclusion


def _state_from_metric(
    metric: list[list[Jet]],
    bach: LinearizedBach,
    first_order: WeylCottonBachFirstOrder,
    natural_from_old: sp.Matrix,
) -> list[Jet]:
    """Return natural ``(E,B,A,C,x,y)`` jets from ``C1 h`` and its divergence."""

    weyl = bach.linearized_weyl(metric)
    flattened_weyl = [
        weyl[a][b][c][d] for a, b, c, d in product(range(4), repeat=4)
    ]
    eb = _matrix_times_jets(
        first_order.decomposition.electric_magnetic_extraction,
        flattened_weyl,
    )

    derivative = bach.covariant_derivative_rank4(weyl)
    cotton = _rank((4, 4, 4))
    geometry = bach.geometry
    for mu, nu, sigma in product(range(4), repeat=3):
        cotton[mu][nu][sigma] = _sum(
            geometry.inverse_metric[rho][axis]
            * derivative[axis][mu][rho][nu][sigma]
            for rho, axis in product(range(4), repeat=2)
        )
    flattened_cotton = [
        cotton[a][b][c] for a, b, c in product(range(4), repeat=3)
    ]
    cotton_coordinates = _matrix_times_jets(
        first_order.decomposition.cotton_coordinate_extraction
        * first_order.decomposition.cotton_xy_extraction,
        flattened_cotton,
    )
    return _matrix_times_jets(natural_from_old, eb + cotton_coordinates)


def _curvature_equations(
    state: list[Jet],
    evolution: ConstraintAdjustedWeylCottonEvolution,
) -> sp.Matrix:
    values = sp.Matrix([entry.value for entry in state])
    derivatives = tuple(
        sp.Matrix([entry.derivative(axis).value for entry in state])
        for axis in range(4)
    )
    evolution_value = derivatives[0] + evolution.evolution_zeroth_coefficient * values
    for axis in range(3):
        evolution_value += evolution.evolution_spatial_coefficients[axis] * derivatives[
            axis + 1
        ]
    constraint_value = evolution.source_compatibility_zeroth_coefficient * values
    for axis in range(3):
        constraint_value += evolution.source_compatibility_spatial_coefficients[
            axis
        ] * derivatives[axis + 1]
    return sp.Matrix.vstack(evolution_value, constraint_value).applyfunc(sp.expand)


def _action_bach_coordinates(
    metric: list[list[Jet]], bach: LinearizedBach, extraction: sp.Matrix
) -> sp.Matrix:
    tensor = bach.action_normalized_bach(metric)
    return (
        extraction
        * sp.Matrix([tensor[a][b].value for a, b in product(range(4), repeat=2)])
    ).applyfunc(sp.expand)


def _partition[T](values: tuple[T, ...], workers: int) -> tuple[tuple[T, ...], ...]:
    """Deterministically distribute exact jet labels over worker processes."""

    return tuple(tuple(values[index::workers]) for index in range(workers))


def _state_coefficient_chunk(
    multiindices: tuple[tuple[int, ...], ...],
) -> tuple[tuple[tuple[int, ...], sp.Matrix], ...]:
    basis = CovariantJetBasis.build()
    bach = LinearizedBach.build()
    first_order = WeylCottonBachFirstOrder.build()
    natural_from_old = _old_from_natural_state().inv()
    output: list[tuple[tuple[int, ...], sp.Matrix]] = []
    for multiindex in multiindices:
        coefficient = sp.zeros(26, 24)
        for component in range(10):
            metric = basis.covariant_monomial_symmetric(component, multiindex, 3)
            state = _state_from_metric(metric, bach, first_order, natural_from_old)
            coefficient[:, component] = sp.Matrix([entry.value for entry in state])
        output.append((multiindex, coefficient))
    return tuple(output)


def _four_jet_sample_chunk(
    multiindices: tuple[tuple[int, ...], ...],
) -> tuple[tuple[sp.Matrix, ...], tuple[sp.Matrix, ...]]:
    basis = CovariantJetBasis.build()
    bach = LinearizedBach.build()
    first_order = WeylCottonBachFirstOrder.build()
    evolution = ConstraintAdjustedWeylCottonEvolution.build()
    natural_from_old = _old_from_natural_state().inv()
    extraction = _target_extraction()
    bach_columns: list[sp.Matrix] = []
    curvature_columns: list[sp.Matrix] = []
    for multiindex in multiindices:
        for component in range(10):
            metric = basis.covariant_monomial_symmetric(component, multiindex, 4)
            state = _state_from_metric(metric, bach, first_order, natural_from_old)
            bach_columns.append(_action_bach_coordinates(metric, bach, extraction))
            curvature_columns.append(_curvature_equations(state, evolution))
    return tuple(bach_columns), tuple(curvature_columns)


@dataclass(frozen=True)
class CurvatureAuxiliaryEquationChainMap:
    """Exact state and equation maps through the adjusted curvature rows."""

    state_coefficients: tuple[tuple[tuple[int, ...], sp.Matrix], ...]
    bach_to_curvature: sp.Matrix
    equation_coefficients: tuple[tuple[tuple[int, ...], sp.Matrix], ...]
    tested_metric_four_jets: int
    bach_sample_rank: int
    curvature_factorization_defect: int
    differential_ac_rows_nonzero: int

    @staticmethod
    def build(*, workers: int = 1) -> "CurvatureAuxiliaryEquationChainMap":
        if workers < 1:
            raise ValueError("workers must be positive")
        basis = CovariantJetBasis.build()
        extraction = _target_extraction()

        # Emit T_state coefficientwise through its exact order three.
        state_multiindices = tuple(basis.geometry.exhaustive_multiindices(3))
        if workers == 1:
            state_coefficients = list(_state_coefficient_chunk(state_multiindices))
        else:
            with ProcessPoolExecutor(max_workers=workers) as executor:
                chunks = executor.map(
                    _state_coefficient_chunk,
                    _partition(state_multiindices, workers),
                )
                state_coefficients = sorted(
                    (entry for chunk in chunks for entry in chunk),
                    key=lambda entry: entry[0],
                )

        # Determine and exhaustively verify the constant H with
        # E_curv T_state=H B_action on all metric four-jets.
        sample_multiindices = tuple(basis.geometry.exhaustive_multiindices(4))
        if workers == 1:
            sample_chunks = (_four_jet_sample_chunk(sample_multiindices),)
        else:
            with ProcessPoolExecutor(max_workers=workers) as executor:
                sample_chunks = tuple(
                    executor.map(
                        _four_jet_sample_chunk,
                        _partition(sample_multiindices, workers),
                    )
                )
        # Worker chunks are round-robin partitions.  Column order is irrelevant
        # to the factorization/rank proof as long as Bach and curvature columns
        # remain paired, which this flattening preserves.
        bach_columns = [
            column for bach_chunk, _ in sample_chunks for column in bach_chunk
        ]
        curvature_columns = [
            column for _, curvature_chunk in sample_chunks for column in curvature_chunk
        ]
        bach_samples = sp.Matrix.hstack(*bach_columns)
        curvature_samples = sp.Matrix.hstack(*curvature_columns)
        right_inverse = bach_samples.T * (bach_samples * bach_samples.T).inv()
        bach_to_curvature = (curvature_samples * right_inverse).applyfunc(sp.expand)
        factorization_defect = (
            curvature_samples - bach_to_curvature * bach_samples
        ).applyfunc(sp.expand)

        # B_action=E_h+S_h^sharp E_f.  Convert the action-dual equation
        # coordinates using the exact tensor pairing and the emitted S_h
        # table.  No v-equation component is needed.
        expanded = ExpandedCurvedAuxiliaryHessian.build(
            basis=basis,
            exhaustive_high_order=False,
            workers=workers,
        )
        tensor_pairing_inverse = _ordinary_system().tensor_pairing.inv()
        bach_coordinate_projection = extraction * _symmetric_coordinate_inclusion()
        through_two = basis.geometry.exhaustive_multiindices(2)
        equation_by_multiindex = {
            multiindex: sp.zeros(40, 24) for multiindex in through_two
        }
        zero = (0, 0, 0, 0)
        equation_by_multiindex[zero][:, :10] = (
            bach_to_curvature
            * bach_coordinate_projection
            * tensor_pairing_inverse
        )
        for multiindex, coefficient in expanded.shift_metric_coefficients:
            order = sum(multiindex)
            equation_by_multiindex[multiindex][:, 10:20] += (
                bach_to_curvature
                * bach_coordinate_projection
                * tensor_pairing_inverse
                * ((-1) ** order * coefficient.T)
            )
        # The four-row differential acts on the paired field-equation row
        # Ebar=J_aux^{-1}E_raw.  Therefore A_paired=A_raw J_aux.
        field_pairing = _ordinary_system().field_fibre_pairing
        equation_coefficients = tuple(
            sorted(
                (
                    multiindex,
                    coefficient * field_pairing,
                )
                for multiindex, coefficient in equation_by_multiindex.items()
            )
        )

        # In the adjusted presentation the six a,c rows are the last six
        # components of the fourteen constraint rows.  Their nonzero image
        # records the differential generation absent from pointwise row
        # selection of the original 34 covariant equations.
        ac_block = bach_to_curvature[34:40, :]
        result = CurvatureAuxiliaryEquationChainMap(
            state_coefficients=tuple(state_coefficients),
            bach_to_curvature=bach_to_curvature,
            equation_coefficients=equation_coefficients,
            tested_metric_four_jets=len(bach_columns),
            bach_sample_rank=bach_samples.rank(),
            curvature_factorization_defect=sum(
                int(value != 0) for value in factorization_defect
            ),
            differential_ac_rows_nonzero=sum(
                int(value != 0) for value in ac_block
            ),
        )
        result.verify()
        return result

    def verify(self) -> None:
        if len(self.state_coefficients) != 35:
            raise AssertionError("T_state order-three coefficient coverage drifted")
        if any(matrix.shape != (26, 24) for _, matrix in self.state_coefficients):
            raise AssertionError("wrong T_state coefficient shape")
        if self.bach_to_curvature.shape != (40, 9):
            raise AssertionError("wrong Bach-to-curvature map shape")
        if self.tested_metric_four_jets != 700:
            raise AssertionError("metric four-jet coverage is not exhaustive")
        if self.bach_sample_rank != 9:
            raise AssertionError("Bach target was not exhausted")
        if self.curvature_factorization_defect:
            raise AssertionError("E_curv T_state does not factor through Bach")
        if len(self.equation_coefficients) != 15:
            raise AssertionError("A_equation order-two coefficient coverage drifted")
        if any(matrix.shape != (40, 24) for _, matrix in self.equation_coefficients):
            raise AssertionError("wrong A_equation coefficient shape")
        if self.differential_ac_rows_nonzero == 0:
            raise AssertionError("the differential a,c generators were dropped")

    def certificate(self) -> dict[str, object]:
        self.verify()
        nonzero_state = sum(
            int(value != 0) for _, matrix in self.state_coefficients for value in matrix
        )
        nonzero_equation = sum(
            int(value != 0)
            for _, matrix in self.equation_coefficients
            for value in matrix
        )
        return {
            "schema": "pure-weyl-curvature-auxiliary-equation-chain-map-v1",
            "T_state": {
                "operator": "(C1,div C1)",
                "shape": [26, 24],
                "maximum_order": 3,
                "coefficient_multiindices": len(self.state_coefficients),
                "nonzero_coefficients": nonzero_state,
                "sha256": _digest_tables(self.state_coefficients),
            },
            "A_equation": {
                "shape": [40, 24],
                "maximum_order": 2,
                "factorization": (
                    "A_raw=H_Bach(E_h+S_h^sharp E_f), "
                    "A_equation=A_raw J_aux on Ebar=J_aux^-1 E_raw"
                ),
                "input_row": "paired Ebar=J_aux^-1 E_raw",
                "raw_to_paired_conversion": "A_equation=A_raw J_aux",
                "Bach_to_curvature_shape": list(self.bach_to_curvature.shape),
                "Bach_to_curvature_rank": self.bach_to_curvature.rank(),
                "Bach_to_curvature_sha256": _digest_matrix(
                    self.bach_to_curvature
                ),
                "coefficient_multiindices": len(self.equation_coefficients),
                "nonzero_coefficients": nonzero_equation,
                "sha256": _digest_tables(self.equation_coefficients),
            },
            "exhaustive_jet_certificate": {
                "base_point": "cylinder stereographic origin",
                "metric_components": 10,
                "covariant_multiindices_through_order_4": 70,
                "tested_metric_four_jets": self.tested_metric_four_jets,
                "Bach_sample_rank": self.bach_sample_rank,
                "E_curv_T_minus_H_Bach_defect": self.curvature_factorization_defect,
                "globalization": "R x SO(4) homogeneity",
            },
            "differential_ac_generation": {
                "included": True,
                "nonzero_H_entries_in_a_c_rows": self.differential_ac_rows_nonzero,
                "rows": "adjusted constraint rows a[3],c[3]",
            },
            "first_chain_relation": "E_curv T_state=A_equation E_aux",
            "first_chain_relation_exact": True,
            "B_identity_emitted": False,
            "mapping_cylinder_cotangent_kernel_assembled": False,
            "warranted_atomic_flags": [],
            "status_flags_promoted": [],
            "proof_boundary": (
                "the state/equation chain square is coefficientwise exact; "
                "the identity-row factorization N_curv A_equation=B_identity "
                "C_aux remains to be solved before cotangent assembly"
            ),
            "fail_closed": True,
        }
