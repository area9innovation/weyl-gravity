"""Exact aligned Jordan-chain obstruction for the complete spatial R6# family.

The time-only pair-(1,6) candidate has an intrinsic polynomial Jordan chain
at the aligned characteristic root ``z=+1``.  The complete equivariant
first-order family leaves 46 spatial coefficients of

``R6sharp: M_aux[24] -> X_Id_sharp[14]``

free after its temporal coefficient is fixed.  This module asks whether
those coefficients can break that chain.

For propagation in the first spatial direction, write

``R6sharp(-z,1,0,0) = -z R6sharp_0 + T_1(p)``.

The chain vectors live in the two aligned helicity-two coordinates
``a0=2 f_23`` and ``a1=h_23``.  Every one of the 46 exact spatial-vector
intertwiners has zero first-direction column on both coordinates.  Hence
the complete affine sensitivity of

``Q(1,p)a0`` and ``Q(1,p)a1 + Q'(1,p)a0``

is the zero matrix.  There are therefore no linear parameter conditions
inside this family that break the known chain: it persists for every
choice of the 46 parameters.

An exact sparse rational screen verifies regularity away from the root for
the origin, every signed coordinate vector, and adjacent two-coordinate
sums.  Those samples are regular matrix polynomials but retain the same
length-two chain, so none is semisimple at all nonzero roots.  The universal
zero-sensitivity calculation, not the finite screen, is the obstruction.

This is scoped to the fixed pair-(1,6) incidence and scalar branch.  It is
not a no-go for other relative pairs, a larger witness, or Green
hyperbolicity.  No project flag is promoted.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import sympy as sp

from .expanded_relative_witness_full_symbol import (
    COMPLETE_RANK,
    CURVATURE_RANK,
    FIELD_RANK,
    ExpandedRelativeFullSymbol,
)
from .expanded_relative_witness_r6_family import (
    SPATIAL_PARAMETER_COUNT,
    ExpandedRelativeR6Family,
)


ALIGNED_ROOT = sp.Integer(1)
REGULARITY_TEST_POINTS = tuple(map(sp.Integer, (2, 3, 5, 7)))


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _aligned_symbol(
    full: ExpandedRelativeFullSymbol,
    spatial_first: sp.MatrixBase,
    z: sp.Expr,
) -> sp.Matrix:
    """Return ``P_weighted((-z,1,0,0))`` with the selected spatial R6#.

    ``ExpandedRelativeFullSymbol.symbol`` already contains the fixed
    temporal term ``-z R6sharp_0``.  Only the exact lower-left correction
    ``-N(-z,1)^T T_1`` must be added.
    """

    result = full.symbol((-z, 1, 0, 0), separated=True)
    identity = (
        -z * full.identity_coefficients[0]
        + full.identity_coefficients[1]
    )
    correction = sp.zeros(CURVATURE_RANK, FIELD_RANK)
    correction[26:66, :] = -identity.T * spatial_first
    result[FIELD_RANK:, :FIELD_RANK] += correction
    return result


def _parameter_samples() -> tuple[tuple[str, tuple[int, ...]], ...]:
    """Deterministic exact screen with support at most two."""

    zero = (0,) * SPATIAL_PARAMETER_COUNT
    result: list[tuple[str, tuple[int, ...]]] = [("zero", zero)]
    for index in range(SPATIAL_PARAMETER_COUNT):
        positive = list(zero)
        positive[index] = 1
        result.append((f"+e{index}", tuple(positive)))
        negative = list(zero)
        negative[index] = -1
        result.append((f"-e{index}", tuple(negative)))
    for index in range(SPATIAL_PARAMETER_COUNT):
        adjacent = list(zero)
        adjacent[index] = 1
        adjacent[(index + 1) % SPATIAL_PARAMETER_COUNT] = 1
        result.append((f"e{index}+e{(index + 1) % SPATIAL_PARAMETER_COUNT}", tuple(adjacent)))
    return tuple(result)


@dataclass(frozen=True)
class ExpandedRelativeR6ChainObstruction:
    family: ExpandedRelativeR6Family
    full_symbol: ExpandedRelativeFullSymbol
    polynomial_eigenvector: sp.Matrix
    polynomial_generalized_vector: sp.Matrix
    aligned_first_column_eigenvector: sp.Matrix
    aligned_first_column_generalized: sp.Matrix
    chain_sensitivity: sp.Matrix
    sparse_sample_count: int
    sparse_maximum_support: int
    sparse_regularity_ranks: tuple[int, ...]
    sparse_chain_defects: tuple[int, ...]

    @staticmethod
    def build() -> "ExpandedRelativeR6ChainObstruction":
        family = ExpandedRelativeR6Family.build()
        full = ExpandedRelativeFullSymbol.build()
        # Reconstruct the intrinsic 116-row polynomial vectors directly;
        # do not infer their persistence from the 212-row reduction.
        a0 = sp.zeros(COMPLETE_RANK, 1)
        a0[18] = 2
        a1 = sp.zeros(COMPLETE_RANK, 1)
        a1[8] = 1

        # For aligned propagation, T_1 is the first member of every spatial
        # coefficient triple.  Persist the direct column calculation as
        # well as the complete polynomial-chain sensitivity.
        direct_a0 = sp.Matrix.hstack(
            *(triple[0] * a0[:FIELD_RANK, :] for triple in family.spatial_basis)
        )
        direct_a1 = sp.Matrix.hstack(
            *(triple[0] * a1[:FIELD_RANK, :] for triple in family.spatial_basis)
        )

        sensitivity_columns: list[sp.Matrix] = []
        for triple in family.spatial_basis:
            spatial_first = triple[0]
            identity_at_root = (
                -full.identity_coefficients[0]
                + full.identity_coefficients[1]
            )
            value_correction = sp.zeros(CURVATURE_RANK, FIELD_RANK)
            value_correction[26:66, :] = -identity_at_root.T * spatial_first
            derivative_correction = sp.zeros(CURVATURE_RANK, FIELD_RANK)
            derivative_correction[26:66, :] = (
                full.identity_coefficients[0].T * spatial_first
            )
            value = sp.zeros(COMPLETE_RANK)
            derivative = sp.zeros(COMPLETE_RANK)
            value[FIELD_RANK:, :FIELD_RANK] = value_correction
            derivative[FIELD_RANK:, :FIELD_RANK] = derivative_correction
            sensitivity_columns.append(
                (value * a0).col_join(value * a1 + derivative * a0)
            )
        sensitivity = sp.Matrix.hstack(*sensitivity_columns)

        samples = _parameter_samples()
        regularity_ranks: list[int] = []
        chain_defects: list[int] = []
        for _, parameters in samples:
            coefficients = family.spatial_coefficients(tuple(map(sp.Integer, parameters)))
            polynomial = _aligned_symbol(full, coefficients[0], sp.Symbol("z"))
            root = polynomial.subs("z", ALIGNED_ROOT)
            derivative = polynomial.diff("z").subs("z", ALIGNED_ROOT)
            chain_defects.append(
                sum(int(value != 0) for value in root * a0)
                + sum(int(value != 0) for value in root * a1 + derivative * a0)
            )
            maximum_rank = 0
            for test_point in REGULARITY_TEST_POINTS:
                maximum_rank = max(
                    maximum_rank,
                    _aligned_symbol(full, coefficients[0], test_point).rank(),
                )
                if maximum_rank == COMPLETE_RANK:
                    break
            regularity_ranks.append(maximum_rank)

        result = ExpandedRelativeR6ChainObstruction(
            family=family,
            full_symbol=full,
            polynomial_eigenvector=a0,
            polynomial_generalized_vector=a1,
            aligned_first_column_eigenvector=direct_a0,
            aligned_first_column_generalized=direct_a1,
            chain_sensitivity=sensitivity,
            sparse_sample_count=len(samples),
            sparse_maximum_support=max(
                sum(int(value != 0) for value in parameters)
                for _, parameters in samples
            ),
            sparse_regularity_ranks=tuple(regularity_ranks),
            sparse_chain_defects=tuple(chain_defects),
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.chain_sensitivity.shape != (
            2 * COMPLETE_RANK,
            SPATIAL_PARAMETER_COUNT,
        ):
            raise AssertionError("chain-sensitivity shape drifted")
        if self.chain_sensitivity != sp.zeros(
            2 * COMPLETE_RANK, SPATIAL_PARAMETER_COUNT
        ):
            raise AssertionError("a spatial R6# parameter changes the known chain")
        if self.aligned_first_column_eigenvector != sp.zeros(
            14, SPATIAL_PARAMETER_COUNT
        ):
            raise AssertionError("the spatial family acts on aligned f_23")
        if self.aligned_first_column_generalized != sp.zeros(
            14, SPATIAL_PARAMETER_COUNT
        ):
            raise AssertionError("the spatial family acts on aligned h_23")

        z = sp.Symbol("z")
        base = _aligned_symbol(self.full_symbol, sp.zeros(14, 24), z)
        root = base.subs(z, ALIGNED_ROOT)
        derivative = base.diff(z).subs(z, ALIGNED_ROOT)
        if root * self.polynomial_eigenvector != sp.zeros(COMPLETE_RANK, 1):
            raise AssertionError("base polynomial eigenvector drifted")
        if (
            root * self.polynomial_generalized_vector
            + derivative * self.polynomial_eigenvector
            != sp.zeros(COMPLETE_RANK, 1)
        ):
            raise AssertionError("base polynomial generalized vector drifted")
        if self.polynomial_eigenvector == sp.zeros(COMPLETE_RANK, 1):
            raise AssertionError("polynomial eigenvector vanished")
        if self.sparse_sample_count != 139 or self.sparse_maximum_support != 2:
            raise AssertionError("sparse rational screen coverage drifted")
        if any(rank != COMPLETE_RANK for rank in self.sparse_regularity_ranks):
            raise AssertionError("a screened polynomial is not regular at z=2")
        if any(self.sparse_chain_defects):
            raise AssertionError("a screened parameter choice broke the chain")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-expanded-relative-r6-chain-obstruction-v1",
            "scope": {
                "relative_branch": "pair-(1,6)",
                "scalar_branch": "D_alt=-2 Pi_(h00,f00,v0)",
                "temporal_R6sharp_fixed": True,
                "spatial_R6sharp_family_dimension": SPATIAL_PARAMETER_COUNT,
                "aligned_covector": "(-z,+1,0,0)",
            },
            "known_polynomial_chain": {
                "root": "+1",
                "eigenvector": "a0=2 f_23",
                "generalized_vector": "a1=h_23",
                "identity": "Q(1,p)a0=0; Q(1,p)a1+Q'(1,p)a0=0",
                "base_defect": 0,
            },
            "complete_parameter_dependence": {
                "condition_map_shape": list(self.chain_sensitivity.shape),
                "condition_map_rank": self.chain_sensitivity.rank(),
                "condition_map_nonzero_entries": sum(
                    int(value != 0) for value in self.chain_sensitivity
                ),
                "condition_map_sha256": _digest(self.chain_sensitivity),
                "T1_on_f23_rank": self.aligned_first_column_eigenvector.rank(),
                "T1_on_h23_rank": self.aligned_first_column_generalized.rank(),
                "linear_conditions_that_break_chain": [],
                "chain_persists_for_all_46_parameters": True,
                "representation_explanation": (
                    "the aligned helicity-two h_23/f_23 columns are annihilated "
                    "by every first-direction vector intertwiner in the exact family"
                ),
            },
            "sparse_rational_screen": {
                "parameter_values": [-1, 0, 1],
                "sample_family": (
                    "origin, every signed coordinate vector, and every adjacent "
                    "two-coordinate sum"
                ),
                "sample_count": self.sparse_sample_count,
                "maximum_support": self.sparse_maximum_support,
                "regularity_test_points": [
                    f"z={value}" for value in REGULARITY_TEST_POINTS
                ],
                "minimum_rank_at_test_point": min(self.sparse_regularity_ranks),
                "maximum_rank_at_test_point": max(self.sparse_regularity_ranks),
                "chain_defects": sum(self.sparse_chain_defects),
                "semisimple_at_all_nonzero_roots_count": 0,
                "screen_is_not_universal_proof": True,
            },
            "scoped_obstruction": (
                "for every regular member of the complete 46-parameter spatial "
                "R6sharp family, the aligned nonzero root +1 retains a length-two "
                "polynomial Jordan chain; changing these parameters alone cannot "
                "produce a semisimple first-order reduction"
            ),
            "remaining_routes": [
                "other relative-pair incidence",
                "change the temporal R6sharp normalization",
                "enlarge the witness or field content",
                "use a Green-hyperbolic realization not requiring this strong reduction",
            ],
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "warranted_atomic_flags": [],
            "status_flags_promoted": [],
            "fail_closed": True,
        }
