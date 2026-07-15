"""Exact structural screen for degree-one Macaulay multipliers.

For the 179 sharp order-two quadrics ``f_i`` this module assembles the
degree-one multiplier space

``span_Q{f_i, x_a f_i}``, ``i=1..179``, ``a=1..114``.

The resulting Macaulay matrix is too large for an uncontrolled rational
RREF in the standard verifier.  We therefore persist exact combinatorial
upper bounds and one rigorous modular-minor lower bound for its homogeneous
degree-three block.  A nonzero minor modulo a prime not meeting any input
denominator is a nonzero rational minor, so that lower bound is exact over
``Q``.  It does not decide whether the constant lies in the ideal.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import scipy.sparse as sparse
from scipy.sparse.csgraph import maximum_bipartite_matching, structural_rank
import sympy as sp
from sympy import GF
from sympy.polys.matrices.sdm import SDM

from .general_nonlinear_factor_sharp_order2 import (
    GeneralNonlinearFactorSharpOrderTwo,
)


PRIME = 1_000_003


def _modular(value: sp.Expr, domain):
    rational = sp.Rational(value)
    denominator = int(rational.q) % PRIME
    if denominator == 0:
        raise AssertionError("Macaulay prime meets an input denominator")
    return domain(int(rational.p) % PRIME) * domain(pow(denominator, -1, PRIME))


@dataclass(frozen=True)
class GeneralNonlinearFactorSharpMacaulayScreen:
    multiplier_columns: int
    rows_by_degree: tuple[int, ...]
    nonzero_entries: int
    content_sha256: str
    high_block_shapes: tuple[tuple[int, int], ...]
    high_block_nonzero_entries: tuple[int, ...]
    high_block_structural_ranks: tuple[int, ...]
    degree_three_effective_columns: int
    degree_three_matched_minor_nonzero_entries: int
    degree_three_matching_sha256: str
    degree_three_modular_rank: int
    degree_three_rational_upper_bound: int

    @staticmethod
    def build() -> "GeneralNonlinearFactorSharpMacaulayScreen":
        constraints = GeneralNonlinearFactorSharpOrderTwo.build().projected_constraints
        variables = 114
        columns = len(constraints) * (variables + 1)

        monomials = {
            monomial for polynomial in constraints for monomial in polynomial
        }
        monomials.update(
            tuple(sorted(monomial + (variable,)))
            for polynomial in constraints
            for monomial in polynomial
            for variable in range(variables)
        )
        ordered_monomials = tuple(sorted(monomials, key=lambda item: (len(item), item)))
        row_index = {monomial: row for row, monomial in enumerate(ordered_monomials)}

        rows: list[int] = []
        cols: list[int] = []
        values: list[sp.Expr] = []
        digest = hashlib.sha256()
        for constraint_index, polynomial in enumerate(constraints):
            for monomial, coefficient in sorted(polynomial.items()):
                row = row_index[monomial]
                column = constraint_index * 115
                rows.append(row)
                cols.append(column)
                values.append(coefficient)
                digest.update(
                    f"{row}|{column}|{sp.srepr(coefficient)}\n".encode()
                )
            for variable in range(variables):
                column = constraint_index * 115 + 1 + variable
                for monomial, coefficient in sorted(polynomial.items()):
                    changed = tuple(sorted(monomial + (variable,)))
                    row = row_index[changed]
                    rows.append(row)
                    cols.append(column)
                    values.append(coefficient)
                    digest.update(
                        f"{row}|{column}|{sp.srepr(coefficient)}\n".encode()
                    )

        pattern = sparse.coo_matrix(
            ([1] * len(rows), (rows, cols)),
            shape=(len(ordered_monomials), columns),
        ).tocsr()
        degrees = tuple(len(monomial) for monomial in ordered_monomials)
        rows_by_degree = tuple(degrees.count(degree) for degree in range(4))

        block_shapes = []
        block_nonzeros = []
        block_structural_ranks = []
        blocks = {}
        for minimum_degree in range(4):
            selected_rows = [
                row for row, degree in enumerate(degrees) if degree >= minimum_degree
            ]
            block = pattern[selected_rows, :]
            blocks[minimum_degree] = (selected_rows, block)
            block_shapes.append(block.shape)
            block_nonzeros.append(block.nnz)
            block_structural_ranks.append(int(structural_rank(block)))

        # The constant-multiplier columns vanish in degree three.  Match the
        # remaining 179*114 columns into the degree-three rows, then compute
        # the exact rank modulo PRIME of that deterministic square minor.
        effective_columns = tuple(
            constraint * 115 + 1 + variable
            for constraint in range(179)
            for variable in range(114)
        )
        degree_three_rows, degree_three = blocks[3]
        effective = degree_three[:, list(effective_columns)]
        matching = maximum_bipartite_matching(effective, perm_type="row")
        if any(item < 0 for item in matching):
            raise AssertionError("degree-three structural matching ceased to be full")
        matched_original_rows = {
            degree_three_rows[int(local_row)]: square_row
            for square_row, local_row in enumerate(matching)
        }
        effective_column_index = {
            column: index for index, column in enumerate(effective_columns)
        }
        domain = GF(PRIME)
        modular_rows: dict[int, dict[int, object]] = {}
        matched_nnz = 0
        for row, column, value in zip(rows, cols, values, strict=True):
            square_row = matched_original_rows.get(row)
            square_column = effective_column_index.get(column)
            if square_row is None or square_column is None:
                continue
            modular_value = _modular(value, domain)
            if modular_value:
                modular_rows.setdefault(square_row, {})[
                    square_column
                ] = modular_value
                matched_nnz += 1
        modular = SDM(
            modular_rows,
            (len(effective_columns), len(effective_columns)),
            domain,
        )
        _, pivots = modular.rref()

        result = GeneralNonlinearFactorSharpMacaulayScreen(
            multiplier_columns=columns,
            rows_by_degree=rows_by_degree,
            nonzero_entries=pattern.nnz,
            content_sha256=digest.hexdigest(),
            high_block_shapes=tuple(block_shapes),
            high_block_nonzero_entries=tuple(block_nonzeros),
            high_block_structural_ranks=tuple(block_structural_ranks),
            degree_three_effective_columns=len(effective_columns),
            degree_three_matched_minor_nonzero_entries=matched_nnz,
            degree_three_matching_sha256=hashlib.sha256(
                repr(tuple(int(item) for item in matching)).encode()
            ).hexdigest(),
            degree_three_modular_rank=len(pivots),
            # The quadratic coefficient space has exact dimension 124, so
            # multiplication by the 114 variables has image dimension at most
            # 124*114 over every characteristic-zero field.
            degree_three_rational_upper_bound=124 * 114,
        )
        result.verify()
        return result

    def verify(self) -> None:
        if (
            self.multiplier_columns,
            self.rows_by_degree,
            self.nonzero_entries,
            self.content_sha256,
        ) != (
            20585,
            (1, 114, 2693, 133777),
            536360,
            "3c8573fa64a6cbbd5cb09a717fbde0fa2999e9dadfc8778e18748f8d9ca4da56",
        ):
            raise AssertionError("Macaulay sparse matrix ledger drifted")
        if self.high_block_shapes != (
            (136585, 20585),
            (136584, 20585),
            (136470, 20585),
            (133777, 20585),
        ):
            raise AssertionError("Macaulay block-shape ledger drifted")
        if self.high_block_nonzero_entries != (
            536360,
            536319,
            531552,
            516420,
        ):
            raise AssertionError("Macaulay block-sparsity ledger drifted")
        if self.high_block_structural_ranks != (
            20585,
            20585,
            20585,
            20406,
        ):
            raise AssertionError("Macaulay structural-rank ledger drifted")
        if (
            self.degree_three_effective_columns,
            self.degree_three_matched_minor_nonzero_entries,
            self.degree_three_matching_sha256,
            self.degree_three_modular_rank,
            self.degree_three_rational_upper_bound,
        ) != (
            20406,
            145857,
            "5249e94cdb1fc7e8f2a8700f064d2e4a25c5fe6472d1943bc21617b68a3a86db",
            12861,
            14136,
        ):
            raise AssertionError("Macaulay degree-three exact bounds drifted")

    def certificate(self) -> dict[str, object]:
        self.verify()
        labels = ("all", "degree>=1", "degree>=2", "degree=3")
        return {
            "schema": "pure-weyl-general-nonlinear-factor-sharp-macaulay-screen-v1",
            "input": {
                "quadrics": 179,
                "variables": 114,
                "multipliers": "constants plus all degree-one monomials",
                "multiplier_columns": self.multiplier_columns,
            },
            "exact_sparse_matrix": {
                "rows_by_degree_0_to_3": list(self.rows_by_degree),
                "total_rows": sum(self.rows_by_degree),
                "nonzero_entries": self.nonzero_entries,
                "content_sha256": self.content_sha256,
                "blocks": {
                    label: {
                        "shape": list(shape),
                        "nonzero_entries": nonzero,
                        "structural_rank_upper_bound": rank,
                    }
                    for label, shape, nonzero, rank in zip(
                        labels,
                        self.high_block_shapes,
                        self.high_block_nonzero_entries,
                        self.high_block_structural_ranks,
                        strict=True,
                    )
                },
            },
            "degree_three_exact_bounds": {
                "effective_nonconstant_multiplier_columns": (
                    self.degree_three_effective_columns
                ),
                "deterministic_matched_minor_nonzero_entries": (
                    self.degree_three_matched_minor_nonzero_entries
                ),
                "matching_sha256": self.degree_three_matching_sha256,
                "prime": PRIME,
                "prime_avoids_all_input_denominators": True,
                "modular_minor_rank": self.degree_three_modular_rank,
                "rational_rank_lower_bound": self.degree_three_modular_rank,
                "rational_rank_upper_bound": (
                    self.degree_three_rational_upper_bound
                ),
                "upper_bound_derivation": "rank(Q_2)*114=124*114",
            },
            "outcome": {
                "degree_one_Macaulay_matrix_assembled": True,
                "constant_contradiction_decided": False,
                "constant_contradiction_found": False,
                "low_degree_ideal_dimensions_decided": False,
                "full_rational_rank_computation_completed": False,
                "general_factorization_disproved": False,
                "green_realization_proved": False,
                "flag_promoted": False,
            },
            "theorem_boundary": (
                "the exact degree-one Macaulay matrix and all structural rank "
                "bounds are assembled.  A deterministic modular minor gives a "
                "rigorous characteristic-zero lower bound for the degree-three "
                "block, but the rational ranks of the full and truncated blocks "
                "remain undetermined.  Therefore neither a constant ideal "
                "contradiction nor a low-degree elimination theorem is claimed"
            ),
        }
