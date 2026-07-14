"""Tangent complex of the quadratic minimal pure-Weyl BV master action.

We use the conventional minimal coordinates

``h, c, omega, h_star, c_star, omega_star``

with conventional BV ghost numbers ``0,1,1,-1,-2,-2``.  The raw detour
complex acts on tangent vectors at the background.  Its cochain degree is
therefore the *negative* of conventional BV ghost number:

``(c,omega) -> h -> h_star -> (c_star,omega_star)``.

At quadratic order around a conformally flat background the nonlinear
terms ``c_star[c,c]``, ``omega_star L_c omega``, and the field-dependent
part of ``h_star L_c h`` do not enter this tangent differential.  In the
flat conformal chart used by the polynomial realization it is

``Q h = 2 d_(mu c_nu) + 2 omega eta_(mu nu)``,
``Q h_star = B_lin h``,
``Q c_star = -2 d^mu h_star_(mu nu)``,
``Q omega_star = 2 tr(h_star)``.

The signs fix one explicit antibracket convention.  Changing the global BV
sign only conjugates the displayed chain by row signs and does not alter its
cohomology.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from bridge.bv_complex.conformal_polynomials import (
    DIMENSION,
    SYMMETRIC_PAIRS,
    homogeneous_monomials,
)
from symbolic.verify_conformal_detour_polynomial import bach_matrix, gauge_matrix


@dataclass(frozen=True)
class MinimalBVVariable:
    """Field-theoretic metadata before the trace/ghost redefinition."""

    name: str
    symbol: str
    tensor_type: str
    conventional_ghost_number: int
    antifield_number: int
    grassmann_parity: str
    tangent_degree: int
    primary_compact_weight: int
    role: str


MINIMAL_VARIABLES = (
    MinimalBVVariable(
        "diffeomorphism_ghost",
        "c_mu",
        "vector",
        1,
        0,
        "odd",
        -1,
        -1,
        "minimal Diff ghost",
    ),
    MinimalBVVariable(
        "weyl_ghost",
        "omega",
        "scalar",
        1,
        0,
        "odd",
        -1,
        0,
        "minimal Weyl ghost",
    ),
    MinimalBVVariable(
        "metric_fluctuation",
        "h_mn",
        "symmetric",
        0,
        0,
        "even",
        0,
        0,
        "metric fluctuation",
    ),
    MinimalBVVariable(
        "metric_antifield",
        "hstar_mn",
        "symmetric",
        -1,
        1,
        "odd",
        1,
        4,
        "equation/Koszul--Tate row",
    ),
    MinimalBVVariable(
        "diffeomorphism_ghost_antifield",
        "cstar_mu",
        "vector",
        -2,
        2,
        "even",
        2,
        5,
        "Diff Noether-identity row",
    ),
    MinimalBVVariable(
        "weyl_ghost_antifield",
        "omegastar",
        "scalar",
        -2,
        2,
        "even",
        2,
        4,
        "Weyl Noether-identity row",
    ),
)


@dataclass(frozen=True)
class TangentSlice:
    name: str
    start: int
    stop: int
    tangent_degree: int

    @property
    def dimension(self) -> int:
        return self.stop - self.start


def _differentiate(exponent: tuple[int, ...], axis: int):
    if exponent[axis] == 0:
        return None
    output = list(exponent)
    coefficient = sp.Integer(output[axis])
    output[axis] -= 1
    return coefficient, tuple(output)


def vector_divergence_matrix(degree: int) -> sp.SparseMatrix:
    """``partial.c`` from vector polynomials of degree ``degree``."""

    source = homogeneous_monomials(degree)
    target = homogeneous_monomials(degree - 1)
    target_index = {exponent: row for row, exponent in enumerate(target)}
    entries: dict[tuple[int, int], sp.Expr] = {}
    for component in range(DIMENSION):
        for monomial, exponent in enumerate(source):
            result = _differentiate(exponent, component)
            if result is None:
                continue
            coefficient, output = result
            entries[
                target_index[output], component * len(source) + monomial
            ] = coefficient
    return sp.SparseMatrix(len(target), DIMENSION * len(source), entries)


def scalar_gradient_matrix(degree: int) -> sp.SparseMatrix:
    """``partial_mu`` from scalar degree ``degree`` to vector degree ``degree-1``."""

    source = homogeneous_monomials(degree)
    target = homogeneous_monomials(degree - 1)
    target_index = {exponent: row for row, exponent in enumerate(target)}
    entries: dict[tuple[int, int], sp.Expr] = {}
    for monomial, exponent in enumerate(source):
        for component in range(DIMENSION):
            result = _differentiate(exponent, component)
            if result is None:
                continue
            coefficient, output = result
            entries[
                component * len(target) + target_index[output], monomial
            ] = coefficient
    return sp.SparseMatrix(DIMENSION * len(target), len(source), entries)


def symmetric_divergence_matrix(degree: int) -> sp.SparseMatrix:
    """``partial^mu t_(mu nu)`` for a symmetric tensor polynomial."""

    source = homogeneous_monomials(degree)
    target = homogeneous_monomials(degree - 1)
    target_index = {exponent: row for row, exponent in enumerate(target)}
    entries: dict[tuple[int, int], sp.Expr] = {}
    for pair_index, (first, second) in enumerate(SYMMETRIC_PAIRS):
        for monomial, exponent in enumerate(source):
            if first == second:
                actions = ((first, first),)
            else:
                actions = ((first, second), (second, first))
            for derivative, target_component in actions:
                result = _differentiate(exponent, derivative)
                if result is None:
                    continue
                coefficient, output = result
                key = (
                    target_component * len(target) + target_index[output],
                    pair_index * len(source) + monomial,
                )
                entries[key] = entries.get(key, 0) + coefficient
    return sp.SparseMatrix(
        DIMENSION * len(target), len(SYMMETRIC_PAIRS) * len(source), entries
    )


def symmetric_trace_matrix(degree: int) -> sp.SparseMatrix:
    """Algebraic trace of a symmetric tensor, monomial by monomial."""

    monomials = homogeneous_monomials(degree)
    entries: dict[tuple[int, int], sp.Expr] = {}
    for pair_index, (first, second) in enumerate(SYMMETRIC_PAIRS):
        if first != second:
            continue
        for monomial in range(len(monomials)):
            entries[monomial, pair_index * len(monomials) + monomial] = 1
    return sp.SparseMatrix(
        len(monomials), len(SYMMETRIC_PAIRS) * len(monomials), entries
    )


@dataclass(frozen=True)
class MinimalBVBlock:
    """One fixed-total-energy block of the minimal tangent BV complex."""

    energy: int
    slices: tuple[TangentSlice, ...]
    q: sp.SparseMatrix

    @classmethod
    def at_energy(cls, energy: int) -> "MinimalBVBlock":
        if energy < 0:
            raise ValueError("the polynomial BV realization uses energy >= 0")

        vector_ghost = DIMENSION * len(homogeneous_monomials(energy + 1))
        scalar_ghost = len(homogeneous_monomials(energy))
        metric = len(SYMMETRIC_PAIRS) * len(homogeneous_monomials(energy))
        metric_antifield = len(SYMMETRIC_PAIRS) * len(
            homogeneous_monomials(energy - 4)
        )
        vector_antifield = DIMENSION * len(homogeneous_monomials(energy - 5))
        scalar_antifield = len(homogeneous_monomials(energy - 4))

        specifications = (
            ("gauge", vector_ghost + scalar_ghost, -1),
            ("metric", metric, 0),
            ("equation", metric_antifield, 1),
            ("identity", vector_antifield + scalar_antifield, 2),
        )
        slices: list[TangentSlice] = []
        cursor = 0
        for name, dimension, degree in specifications:
            slices.append(TangentSlice(name, cursor, cursor + dimension, degree))
            cursor += dimension
        by_name = {chain_slice.name: chain_slice for chain_slice in slices}
        entries: dict[tuple[int, int], sp.Expr] = {}

        def insert(target: str, source: str, matrix: sp.MatrixBase) -> None:
            target_slice = by_name[target]
            source_slice = by_name[source]
            if matrix.shape != (target_slice.dimension, source_slice.dimension):
                raise AssertionError(
                    f"{source}->{target} shape {matrix.shape} != "
                    f"{(target_slice.dimension, source_slice.dimension)}"
                )
            for (row, column), value in matrix.todok().items():
                entries[target_slice.start + row, source_slice.start + column] = value

        insert("metric", "gauge", gauge_matrix(energy))
        insert("equation", "metric", bach_matrix(energy))
        if metric_antifield:
            noether = sp.SparseMatrix.vstack(
                -2 * symmetric_divergence_matrix(energy - 4),
                2 * symmetric_trace_matrix(energy - 4),
            )
            insert("identity", "equation", noether)

        result = cls(energy, tuple(slices), sp.SparseMatrix(cursor, cursor, entries))
        result.verify()
        return result

    @property
    def dimension(self) -> int:
        return self.q.rows

    def slice(self, name: str) -> TangentSlice:
        return next(value for value in self.slices if value.name == name)

    def arrow(self, target: str, source: str) -> sp.SparseMatrix:
        target_slice = self.slice(target)
        source_slice = self.slice(source)
        return sp.SparseMatrix(
            self.q[
                target_slice.start : target_slice.stop,
                source_slice.start : source_slice.stop,
            ]
        )

    def verify(self) -> None:
        zero = sp.SparseMatrix(self.dimension, self.dimension, {})
        if self.q * self.q != zero:
            raise AssertionError(f"quadratic minimal BV tangent differential is not nilpotent at E={self.energy}")


def master_action_summary() -> dict[str, object]:
    """Machine-readable separation of quadratic and nonlinear master terms."""

    return {
        "minimal_master_action": [
            "S_W[g]",
            "integral gstar^(mu nu) (L_c g_(mu nu) + 2 omega g_(mu nu))",
            "integral cstar_mu [c,c]^mu/2",
            "integral omegastar L_c omega",
        ],
        "quadratic_tangent_terms": [
            "S_W^(2)[h]/2",
            "integral hstar^(mu nu) (2 nabla_(mu c_(nu)) + 2 omega gbar_(mu nu))",
        ],
        "free_tangent_differential": {
            "c_mu": "0",
            "omega": "0",
            "h_mu_nu": "2 nabla_(mu c_nu) + 2 omega gbar_mu_nu",
            "hstar_mu_nu": "B_lin[h]_mu_nu",
            "cstar_nu": "-2 nabla^mu hstar_mu_nu",
            "omegastar": "2 gbar^mu_nu hstar_mu_nu",
        },
        "nonlinear_terms_excluded_from_q": [
            "hstar L_c h",
            "2 hstar omega h",
            "cstar [c,c]/2",
            "omegastar L_c omega",
            "cubic and higher terms in S_W",
        ],
        "grading_convention": (
            "raw local tangent degree equals minus conventional BV ghost number"
        ),
    }
