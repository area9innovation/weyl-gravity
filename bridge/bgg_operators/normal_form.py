"""Exact all-energy normal form of the four-dimensional cylinder BGG block.

The raw tensor-harmonic matrices depend on basis and phase conventions.  The
cohomological information does not.  Smooth BGG exactness, the chiral Weyl
resolution, and the explicit coordinate E/A/L curvature preimages put every
finite ``D x SO(4)`` block into the normal form constructed here.

For compact energy ``n >= 2`` the trace-free deformation block splits as

``metric = gauge + W_+ + W_- + equation``

and the algebraic Weyl block as

``curvature = W_+ + W_- + equation + compatibility``.

The equation and compatibility summands have equal dimension.  Lorentzian
Hodge star exchanges them and has eigenvalues ``-i,+i`` on the two physical
chiral summands.  In this basis the complete finite matrices are sparse
partial identities.  They are exact representatives of the operator block,
not a claim that the original coordinate harmonic basis has this form before
the certified changes of basis are made.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb

import sympy as sp


def _choose(value: int, degree: int) -> int:
    return comb(value, degree) if value >= degree >= 0 else 0


@dataclass(frozen=True)
class SymbolicBlockDimensions:
    """Polynomial dimensions of one parity-complete energy block."""

    gauge: sp.Expr
    metric: sp.Expr
    chirality: sp.Expr
    physical: sp.Expr
    equation: sp.Expr
    curvature: sp.Expr
    bach_target: sp.Expr
    noether_identity: sp.Expr


def symbolic_dimensions(n: sp.Expr | None = None) -> SymbolicBlockDimensions:
    """Return closed dimensions valid for integer ``n >= 2``.

    ``gauge`` is the trace-free conformal-Killing image (the Weyl scalar has
    already removed the metric trace).  ``equation`` is both the rank of the
    Bach block and the dimension of the off-shell Weyl pair exchanged by
    Hodge star.
    """

    n = sp.symbols("n", integer=True, positive=True) if n is None else sp.sympify(n)
    gauge = 4 * sp.binomial(n + 4, 3)
    metric = 9 * sp.binomial(n + 3, 3)
    chirality = 3 * n**2 - 7
    physical = 2 * chirality
    equation = (n - 2) * (n - 3) * (5 * n + 7) / 6
    curvature = 10 * sp.binomial(n + 1, 3)
    bach_target = 9 * sp.binomial(n - 1, 3)
    noether_identity = 4 * sp.binomial(n - 2, 3)
    return SymbolicBlockDimensions(
        *(sp.factor(sp.expand_func(value)) for value in (
            gauge,
            metric,
            chirality,
            physical,
            equation,
            curvature,
            bach_target,
            noether_identity,
        ))
    )


@dataclass(frozen=True)
class BlockDimensions:
    energy: int
    gauge: int
    metric: int
    chirality: int
    physical: int
    equation: int
    curvature: int
    bach_target: int
    noether_identity: int


def block_dimensions(energy: int) -> BlockDimensions:
    """Evaluate the all-energy formulas with the correct low-level zeros."""

    if energy < 2:
        raise ValueError("physical cylinder BGG blocks start at energy two")
    n = energy
    gauge = 4 * _choose(n + 4, 3)
    metric = 9 * _choose(n + 3, 3)
    chirality = 3 * n * n - 7
    physical = 2 * chirality
    equation = (n - 2) * (n - 3) * (5 * n + 7) // 6
    curvature = 10 * _choose(n + 1, 3)
    bach_target = 9 * _choose(n - 1, 3)
    noether_identity = 4 * _choose(n - 2, 3)
    return BlockDimensions(
        n,
        gauge,
        metric,
        chirality,
        physical,
        equation,
        curvature,
        bach_target,
        noether_identity,
    )


def _identity_entries(row_start: int, column_start: int, size: int) -> dict[tuple[int, int], sp.Expr]:
    return {
        (row_start + offset, column_start + offset): sp.Integer(1)
        for offset in range(size)
    }


def _partial_permutation_rank(matrix: sp.SparseMatrix) -> int:
    """Rank of a sparse partial signed-permutation matrix, checked exactly."""

    entries = matrix.todok()
    rows = [row for row, _ in entries]
    columns = [column for _, column in entries]
    if len(rows) != len(set(rows)) or len(columns) != len(set(columns)):
        raise AssertionError("matrix is not a partial permutation")
    if any(value == 0 for value in entries.values()):
        raise AssertionError("sparse matrix stores an explicit zero")
    return len(entries)


@dataclass(frozen=True)
class CylinderBGGBlock:
    """One exact finite BGG block in a certified split harmonic basis."""

    dimensions: BlockDimensions
    gauge_map: sp.SparseMatrix
    curvature_map: sp.SparseMatrix
    hodge: sp.SparseMatrix
    curvature_adjoint: sp.SparseMatrix
    compatibility: sp.SparseMatrix
    bach: sp.SparseMatrix
    noether: sp.SparseMatrix

    @classmethod
    def at_energy(cls, energy: int) -> "CylinderBGGBlock":
        d = block_dimensions(energy)
        g, ch, eq = d.gauge, d.chirality, d.equation

        # H = gauge | W+ | W- | equation.
        h_plus = g
        h_minus = g + ch
        h_equation = g + 2 * ch

        # C = W+ | W- | equation | compatibility.
        c_plus = 0
        c_minus = ch
        c_equation = 2 * ch
        c_compatibility = 2 * ch + eq

        gauge_entries = _identity_entries(0, 0, g)
        gauge_map = sp.SparseMatrix(d.metric, g, gauge_entries)

        curvature_entries: dict[tuple[int, int], sp.Expr] = {}
        curvature_entries.update(_identity_entries(c_plus, h_plus, ch))
        curvature_entries.update(_identity_entries(c_minus, h_minus, ch))
        curvature_entries.update(_identity_entries(c_equation, h_equation, eq))
        curvature_map = sp.SparseMatrix(d.curvature, d.metric, curvature_entries)

        # star=-i on W+, +i on W-.  On the off-shell pair use
        # star(equation)=-compatibility, star(compatibility)=equation.
        hodge_entries: dict[tuple[int, int], sp.Expr] = {}
        for offset in range(ch):
            hodge_entries[c_plus + offset, c_plus + offset] = -sp.I
            hodge_entries[c_minus + offset, c_minus + offset] = sp.I
        for offset in range(eq):
            hodge_entries[c_compatibility + offset, c_equation + offset] = -1
            hodge_entries[c_equation + offset, c_compatibility + offset] = 1
        hodge = sp.SparseMatrix(d.curvature, d.curvature, hodge_entries)

        # C^sharp kills the on-shell chiral curvatures and compatibility
        # block; it maps the equation curvature block into im(B).
        adjoint_entries = _identity_entries(0, c_equation, eq)
        curvature_adjoint = sp.SparseMatrix(
            d.bach_target, d.curvature, adjoint_entries
        )
        compatibility = curvature_adjoint * hodge
        bach = curvature_adjoint * curvature_map

        # K^sharp has kernel im(B).  The remaining equation coordinates map
        # isomorphically to the Noether-identity target.
        noether_entries = _identity_entries(0, eq, d.noether_identity)
        noether = sp.SparseMatrix(
            d.noether_identity, d.bach_target, noether_entries
        )

        return cls(
            d,
            gauge_map,
            curvature_map,
            hodge,
            curvature_adjoint,
            compatibility,
            bach,
            noether,
        )

    @property
    def physical_dimension(self) -> int:
        return self.dimensions.physical

    def verify(self) -> None:
        """Raise if any complex, factorization, rank, or exactness rail fails."""

        d = self.dimensions
        zero_cg = sp.SparseMatrix(d.curvature, d.gauge, {})
        zero_ec = sp.SparseMatrix(d.bach_target, d.metric, {})
        zero_ng = sp.SparseMatrix(d.noether_identity, d.metric, {})
        if self.curvature_map * self.gauge_map != zero_cg:
            raise AssertionError("C K != 0")
        if self.compatibility * self.curvature_map != zero_ec:
            raise AssertionError("D2 C != 0")
        if self.bach != self.curvature_adjoint * self.curvature_map:
            raise AssertionError("B != C^sharp C")
        if self.noether * self.bach != zero_ng:
            raise AssertionError("K^sharp B != 0")
        if self.hodge * self.hodge != -sp.SparseMatrix.eye(d.curvature):
            raise AssertionError("Lorentzian star^2 != -1")

        rank_gauge = _partial_permutation_rank(self.gauge_map)
        rank_curvature = _partial_permutation_rank(self.curvature_map)
        rank_bach = _partial_permutation_rank(self.bach)
        rank_compatibility = _partial_permutation_rank(self.compatibility)
        rank_noether = _partial_permutation_rank(self.noether)
        if rank_gauge != d.gauge:
            raise AssertionError("K is not injective after CKV separation")
        if rank_curvature != d.physical + d.equation:
            raise AssertionError("unexpected rank C")
        if rank_bach != d.equation:
            raise AssertionError("unexpected rank B")
        if rank_compatibility != d.equation:
            raise AssertionError("unexpected rank D2")
        if rank_noether != d.noether_identity:
            raise AssertionError("unexpected rank K^sharp")

        if d.metric - rank_bach - rank_gauge != d.physical:
            raise AssertionError("ker B / im K has the wrong dimension")
        if d.metric - rank_curvature != rank_gauge:
            raise AssertionError("ker C != im K by dimension")
        if d.curvature - rank_compatibility != rank_curvature:
            raise AssertionError("ker D2 != im C by dimension")
        if d.bach_target - rank_noether != rank_bach:
            raise AssertionError("ker K^sharp != im B by dimension")
