"""Exact Jordan-obstruction screen for the alternative relative incidences.

The complete incidence audit leaves three minimal reciprocal saddles

``(R1,R6)``, ``(R1,R7)`` and ``(R2,R7)``.

The first branch has now been ruled out after fixing its temporal
normalization and cyclic scalar completion: all 46 spatial ``R6sharp``
parameters annihilate the intrinsic polynomial Jordan chain.  This module
applies the cheaper *sensitivity-first* test to the other two incidences.

Both alternatives contain the same first-order map

``R7sharp : M_aux[24] -> Y_Eq_sharp[40]``.

The coefficient of ``R7sharp`` occurs directly in the degree-zero operator
row ``X_Eq_sharp <- M_aux``.  It also occurs in
``Y_U_sharp <- M_aux`` after composition with ``-EcurvSharp``.  Consequently
the direct row is sufficient to decide whether the complete equivariant
coefficient family can act on the known aligned polynomial chain

``a0=2 f_23,  a1=h_23``.

The exact rotation-generator equations give a 36-dimensional temporal
intertwiner family and an 86-dimensional spatial-vector intertwiner family.
At the aligned root, their restricted chain-sensitivity ranks are eight and
eight, and the joint rank is sixteen.  Hence neither alternative incidence
is rejected by the parameter-rigidity theorem that killed ``(R1,R6)``.

This is deliberately a screen, not a construction.  It does not select
temporal coefficients, assemble either full Douglis polynomial, prove
semisimplicity, or promote a Green-theoretic flag.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import sympy as sp
from sympy.polys.matrices import DomainMatrix

from covariant_completion.curved_retract.curvature_mapping_cylinder_kernel import (
    CurvatureMappingCylinderKernel,
    _add,
    _multiply,
)
from covariant_completion.minimal_witness.formal_operators import OperatorPolynomial

from .expanded_relative_witness import ExpandedRelativeWitnessAudit
from .expanded_relative_witness_commutant import (
    _block_generators,
    _commutant_matrix,
)
from .invariant_pairings import _rotation_generators
from .relative_saddle_witness import _relative_pair_matrix


TARGET_BLOCK = 14
SOURCE_BLOCK = 1
TARGET_RANK = 40
SOURCE_RANK = 24
SPATIAL_DIMENSION = 3
TEMPORAL_PARAMETER_COUNT = 36
SPATIAL_PARAMETER_COUNT = 86
ALIGNED_EIGENVECTOR_COLUMN = 18  # a0=2 f_23
ALIGNED_GENERALIZED_COLUMN = 8   # a1=h_23


def _digest(matrix: sp.MatrixBase) -> str:
    sparse = sp.SparseMatrix(matrix)
    payload = [f"{sparse.rows}x{sparse.cols}"]
    payload.extend(
        f"{row},{column}:{sp.srepr(value)}"
        for (row, column), value in sorted(sparse.todok().items())
    )
    return hashlib.sha256("\n".join(payload).encode("utf-8")).hexdigest()


def _spatial_variable(axis: int, output: int, input_: int) -> int:
    return (axis * TARGET_RANK + output) * SOURCE_RANK + input_


def _spatial_covariance_matrix() -> sp.SparseMatrix:
    """Complete vector-intertwiner equations for ``R7sharp``."""

    target = _block_generators()[TARGET_BLOCK]
    source = _block_generators()[SOURCE_BLOCK]
    rotations = tuple(
        generator[1:, 1:] for generator in _rotation_generators()
    )
    entries: dict[tuple[int, int], sp.Expr] = {}
    equation = 0
    for target_generator, source_generator, rotation in zip(
        target, source, rotations, strict=True
    ):
        for axis in range(SPATIAL_DIMENSION):
            for output in range(TARGET_RANK):
                target_nonzero = [
                    (middle, target_generator[output, middle])
                    for middle in range(TARGET_RANK)
                    if target_generator[output, middle]
                ]
                for input_ in range(SOURCE_RANK):
                    for middle, value in target_nonzero:
                        key = (
                            equation,
                            _spatial_variable(axis, middle, input_),
                        )
                        entries[key] = entries.get(key, 0) + value
                    for middle in range(SOURCE_RANK):
                        value = -source_generator[middle, input_]
                        if value:
                            key = (
                                equation,
                                _spatial_variable(axis, output, middle),
                            )
                            entries[key] = entries.get(key, 0) + value
                    for image_axis in range(SPATIAL_DIMENSION):
                        value = -rotation[image_axis, axis]
                        if value:
                            key = (
                                equation,
                                _spatial_variable(image_axis, output, input_),
                            )
                            entries[key] = entries.get(key, 0) + value
                    equation += 1
    return sp.SparseMatrix(
        equation,
        SPATIAL_DIMENSION * TARGET_RANK * SOURCE_RANK,
        {key: sp.expand(value) for key, value in entries.items() if value},
    )


def _temporal_chain_column(vector: sp.MatrixBase) -> sp.Matrix:
    """Sensitivity of the two chain equations to one temporal table."""

    result = sp.zeros(2 * TARGET_RANK, 1)
    for output in range(TARGET_RANK):
        f23 = vector[ALIGNED_EIGENVECTOR_COLUMN * TARGET_RANK + output]
        h23 = vector[ALIGNED_GENERALIZED_COLUMN * TARGET_RANK + output]
        # R(-z,e1)=-z T0+T1 and R'=-T0.
        result[output] = -2 * f23
        result[TARGET_RANK + output] = -h23 - 2 * f23
    return result


def _spatial_chain_column(vector: sp.MatrixBase) -> sp.Matrix:
    """Sensitivity of the chain equations to one spatial coefficient triple."""

    result = sp.zeros(2 * TARGET_RANK, 1)
    for output in range(TARGET_RANK):
        f23 = vector[
            _spatial_variable(0, output, ALIGNED_EIGENVECTOR_COLUMN)
        ]
        h23 = vector[
            _spatial_variable(0, output, ALIGNED_GENERALIZED_COLUMN)
        ]
        result[output] = 2 * f23
        result[TARGET_RANK + output] = h23
    return result


def _selected_pair_operator(pair: tuple[int, int]) -> list[list[OperatorPolynomial]]:
    kernel = CurvatureMappingCylinderKernel.build()
    witness = [[OperatorPolynomial.zero() for _ in range(16)] for _ in range(16)]
    for pair_index in pair:
        witness = _add(witness, _relative_pair_matrix(pair_index, kernel.pairing)[0])
    return _add(
        _multiply(kernel.split_differential, witness),
        _multiply(witness, kernel.split_differential),
    )


@dataclass(frozen=True)
class ExpandedRelativeIncidenceScreen:
    temporal_equations: sp.SparseMatrix
    spatial_equations: sp.SparseMatrix
    temporal_rank: int
    spatial_rank: int
    temporal_basis: tuple[sp.Matrix, ...]
    spatial_basis: tuple[sp.Matrix, ...]
    temporal_sensitivity: sp.Matrix
    spatial_sensitivity: sp.Matrix
    joint_sensitivity: sp.Matrix
    pair17_operator: list[list[OperatorPolynomial]]
    pair27_operator: list[list[OperatorPolynomial]]

    @staticmethod
    def build() -> "ExpandedRelativeIncidenceScreen":
        generators = _block_generators()
        temporal = _commutant_matrix(
            generators[TARGET_BLOCK], generators[SOURCE_BLOCK]
        )
        spatial = _spatial_covariance_matrix()
        temporal_rank = DomainMatrix.from_Matrix(temporal).rank()
        spatial_rank = DomainMatrix.from_Matrix(spatial).rank()
        temporal_basis = tuple(sp.Matrix(vector) for vector in temporal.nullspace())
        spatial_basis = tuple(sp.Matrix(vector) for vector in spatial.nullspace())
        temporal_sensitivity = sp.Matrix.hstack(
            *(_temporal_chain_column(vector) for vector in temporal_basis)
        )
        spatial_sensitivity = sp.Matrix.hstack(
            *(_spatial_chain_column(vector) for vector in spatial_basis)
        )
        joint = temporal_sensitivity.row_join(spatial_sensitivity)
        result = ExpandedRelativeIncidenceScreen(
            temporal_equations=temporal,
            spatial_equations=spatial,
            temporal_rank=temporal_rank,
            spatial_rank=spatial_rank,
            temporal_basis=temporal_basis,
            spatial_basis=spatial_basis,
            temporal_sensitivity=temporal_sensitivity,
            spatial_sensitivity=spatial_sensitivity,
            joint_sensitivity=joint,
            pair17_operator=_selected_pair_operator((1, 7)),
            pair27_operator=_selected_pair_operator((2, 7)),
        )
        result.verify()
        return result

    def verify(self) -> None:
        incidence = ExpandedRelativeWitnessAudit.build()
        if incidence.minimal_global_saddles != ((1, 6), (1, 7), (2, 7)):
            raise AssertionError("minimal reciprocal-incidence list drifted")
        if self.temporal_equations.shape != (2880, 960):
            raise AssertionError("R7sharp temporal equation shape drifted")
        if self.spatial_equations.shape != (8640, 2880):
            raise AssertionError("R7sharp spatial equation shape drifted")
        if self.temporal_rank != 924 or self.spatial_rank != 2794:
            raise AssertionError("R7sharp equivariance rank drifted")
        if len(self.temporal_basis) != TEMPORAL_PARAMETER_COUNT:
            raise AssertionError("R7sharp temporal nullity drifted")
        if len(self.spatial_basis) != SPATIAL_PARAMETER_COUNT:
            raise AssertionError("R7sharp spatial nullity drifted")
        if self.temporal_sensitivity.shape != (80, 36):
            raise AssertionError("temporal sensitivity shape drifted")
        if self.spatial_sensitivity.shape != (80, 86):
            raise AssertionError("spatial sensitivity shape drifted")
        if self.joint_sensitivity.shape != (80, 122):
            raise AssertionError("joint sensitivity shape drifted")
        if self.temporal_sensitivity.rank() != 8:
            raise AssertionError("temporal sensitivity rank drifted")
        if self.spatial_sensitivity.rank() != 8:
            raise AssertionError("spatial sensitivity rank drifted")
        if self.joint_sensitivity.rank() != 16:
            raise AssertionError("joint sensitivity rank drifted")

        atom = OperatorPolynomial.atom
        zero = OperatorPolynomial.zero()
        for operator in (self.pair17_operator, self.pair27_operator):
            if operator[11][1] != atom("R7sharp"):
                raise AssertionError("R7sharp direct Jordan-sensitive row drifted")
            if operator[15][1] != atom("EcurvSharp") * atom("R7sharp", -1):
                raise AssertionError("R7sharp adjoint-evolution row drifted")
        if self.pair17_operator[1][11] != atom("K") * atom("R1"):
            raise AssertionError("pair-(1,7) reciprocal row drifted")
        if self.pair17_operator[1][15] != zero:
            raise AssertionError("pair-(1,7) gained a spurious R2 row")
        if self.pair27_operator[1][15] != atom("K") * atom("R2"):
            raise AssertionError("pair-(2,7) reciprocal row drifted")
        if self.pair27_operator[1][11] != zero:
            raise AssertionError("pair-(2,7) gained a spurious R1 row")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-expanded-relative-incidence-screen-v1",
            "complete_minimal_incidence_list": {
                "pair_sets": ["1+6", "1+7", "2+7"],
                "complete": True,
                "pair_1_plus_6_status": (
                    "fixed-temporal cyclic -2Pi family ruled out by the separate "
                    "parameter-uniform R6sharp Jordan certificate"
                ),
                "pair_1_plus_6_certificate": (
                    "curved_expanded_relative_witness_r6_chain_obstruction.json"
                ),
            },
            "alternative_common_map": {
                "map": "R7sharp: M_aux[24] -> Y_Eq_sharp[40]",
                "actual_blocks": {"source": SOURCE_BLOCK, "target": TARGET_BLOCK},
                "pair_1_plus_7_direct_rows": [
                    "X_Eq_sharp <- M_aux: R7sharp",
                    "Y_U_sharp <- M_aux: -EcurvSharp R7sharp",
                    "M_aux <- X_Eq_sharp: K R1",
                ],
                "pair_2_plus_7_direct_rows": [
                    "X_Eq_sharp <- M_aux: R7sharp",
                    "Y_U_sharp <- M_aux: -EcurvSharp R7sharp",
                    "M_aux <- Y_U_sharp: K R2",
                ],
                "formal_incidence_checked_coefficientwise": True,
            },
            "complete_first_order_R7sharp_family": {
                "temporal_equations_shape": list(self.temporal_equations.shape),
                "temporal_equations_nonzero_entries": len(
                    self.temporal_equations.todok()
                ),
                "temporal_equations_sha256": _digest(self.temporal_equations),
                "temporal_rank": self.temporal_rank,
                "temporal_nullity": len(self.temporal_basis),
                "spatial_equations_shape": list(self.spatial_equations.shape),
                "spatial_equations_nonzero_entries": len(
                    self.spatial_equations.todok()
                ),
                "spatial_equations_sha256": _digest(self.spatial_equations),
                "spatial_rank": self.spatial_rank,
                "spatial_nullity": len(self.spatial_basis),
                "complete_under_SO3_equivariance": True,
            },
            "intrinsic_Jordan_obstruction_sensitivity": {
                "aligned_covector": "(-z,+1,0,0)",
                "root": "+1",
                "chain": "a0=2 f_23, a1=h_23",
                "conditions": (
                    "R7sharp(1)a0 and "
                    "R7sharp(1)a1+R7sharp'(1)a0"
                ),
                "temporal_matrix_shape": list(self.temporal_sensitivity.shape),
                "temporal_rank": self.temporal_sensitivity.rank(),
                "temporal_sha256": _digest(self.temporal_sensitivity),
                "spatial_matrix_shape": list(self.spatial_sensitivity.shape),
                "spatial_rank": self.spatial_sensitivity.rank(),
                "spatial_sha256": _digest(self.spatial_sensitivity),
                "joint_matrix_shape": list(self.joint_sensitivity.shape),
                "joint_rank": self.joint_sensitivity.rank(),
                "joint_nonzero_entries": sum(
                    int(value != 0) for value in self.joint_sensitivity
                ),
                "joint_sha256": _digest(self.joint_sensitivity),
                "secondary_row_adds_no_independent_conditions": (
                    "for S=-Esharp R, the two chain defects are "
                    "S1=-Esharp C1 and S2=-Esharp C2-(Esharp)' C1"
                ),
            },
            "screening_result": {
                "pair_1_plus_7_rejected_by_zero_sensitivity": False,
                "pair_2_plus_7_rejected_by_zero_sensitivity": False,
                "both_alternatives_act_on_obstruction_quotient": True,
                "next_required_order": [
                    "choose actual temporal R1/R2/R7sharp coefficients",
                    "assemble the exact arbitrary-covector polynomial",
                    "test temporal regularity and polynomial semisimplicity",
                    "only then solve a symmetrizer",
                ],
            },
            "scope": (
                "exact sensitivity-first screen for the complete first-order "
                "SO(3)-equivariant R7sharp coefficient family shared by pairs "
                "(1,7) and (2,7); it proves only that these incidences are not "
                "parameter-rigid in the manner of the fixed (1,6) branch"
            ),
            "strong_hyperbolicity_pair_1_plus_7": False,
            "strong_hyperbolicity_pair_2_plus_7": False,
            "prolonged_green_witness": False,
            "warranted_atomic_flags": [],
            "status_flags_promoted": [],
            "fail_closed": True,
        }
