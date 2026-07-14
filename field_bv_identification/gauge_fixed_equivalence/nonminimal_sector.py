"""Full Diff x Weyl nonminimal sector in suspended tangent convention.

The coordinate BRST rules are

``s bar_c = b`` and ``s bar_omega = b_omega``.

The raw detour complex, however, is the tangent complex of the BRST vector
field and uses tangent degree ``-gh_BV``.  Its linearized arrows therefore
run in the transpose direction

``b -> bar_c`` and ``bar_c_star -> b_star``.

Recording both conventions prevents the common but consequential mistake of
adding only an antighost/multiplier ket pair to a tangent BV chain while
omitting its antifield dual.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from bridge.bv_complex.conformal_polynomials import homogeneous_monomials


@dataclass(frozen=True)
class NonminimalSlice:
    name: str
    start: int
    stop: int
    tensor_type: str
    conventional_ghost_number: int
    antifield_number: int
    tangent_degree: int
    primary_weight: int
    role: str

    @property
    def dimension(self) -> int:
        return self.stop - self.start


def _vector_dimension(level: int) -> int:
    return 4 * len(homogeneous_monomials(level))


def _scalar_dimension(level: int) -> int:
    return len(homogeneous_monomials(level))


def _identity_entries(row: int, column: int, size: int):
    return {(row + offset, column + offset): sp.Integer(1) for offset in range(size)}


@dataclass(frozen=True)
class NonminimalBlock:
    """Two nonminimal doublets and both antifield-dual doublets."""

    energy: int
    slices: tuple[NonminimalSlice, ...]
    tangent_q: sp.SparseMatrix
    tangent_homotopy: sp.SparseMatrix

    @classmethod
    def at_energy(cls, energy: int) -> "NonminimalBlock":
        # The conformal weights are fixed by the Landau gauge fermion
        # bar_c.div(h_0)+bar_omega.tau, a weight-four density.
        specifications = (
            (
                "vector_antighost",
                _vector_dimension(energy - 3),
                "vector",
                -1,
                0,
                1,
                3,
                "Diff nonminimal antighost",
            ),
            (
                "vector_multiplier",
                _vector_dimension(energy - 3),
                "vector",
                0,
                0,
                0,
                3,
                "Diff Nakanishi--Lautrup multiplier",
            ),
            (
                "scalar_antighost",
                _scalar_dimension(energy - 4),
                "scalar",
                -1,
                0,
                1,
                4,
                "Weyl nonminimal antighost",
            ),
            (
                "scalar_multiplier",
                _scalar_dimension(energy - 4),
                "scalar",
                0,
                0,
                0,
                4,
                "Weyl Nakanishi--Lautrup multiplier",
            ),
            (
                "vector_antighost_antifield",
                _vector_dimension(energy - 1),
                "covector density",
                0,
                1,
                0,
                1,
                "antifield of the Diff antighost",
            ),
            (
                "vector_multiplier_antifield",
                _vector_dimension(energy - 1),
                "covector density",
                -1,
                1,
                1,
                1,
                "antifield of the Diff multiplier",
            ),
            (
                "scalar_antighost_antifield",
                _scalar_dimension(energy),
                "scalar density",
                0,
                1,
                0,
                0,
                "antifield of the Weyl antighost",
            ),
            (
                "scalar_multiplier_antifield",
                _scalar_dimension(energy),
                "scalar density",
                -1,
                1,
                1,
                0,
                "antifield of the Weyl multiplier",
            ),
        )
        slices: list[NonminimalSlice] = []
        cursor = 0
        for specification in specifications:
            name, dimension, tensor, ghost, antifield, degree, weight, role = specification
            slices.append(
                NonminimalSlice(
                    name,
                    cursor,
                    cursor + dimension,
                    tensor,
                    ghost,
                    antifield,
                    degree,
                    weight,
                    role,
                )
            )
            cursor += dimension
        by_name = {value.name: value for value in slices}
        q_entries: dict[tuple[int, int], sp.Expr] = {}
        s_entries: dict[tuple[int, int], sp.Expr] = {}

        def tangent_pair(source: str, target: str) -> None:
            left = by_name[source]
            right = by_name[target]
            if left.dimension != right.dimension:
                raise AssertionError(f"nonminimal dimension mismatch: {source}->{target}")
            q_entries.update(_identity_entries(right.start, left.start, left.dimension))
            s_entries.update(_identity_entries(left.start, right.start, left.dimension))

        # Tangent arrows are opposite to the displayed coordinate BRST rule.
        tangent_pair("vector_multiplier", "vector_antighost")
        tangent_pair("scalar_multiplier", "scalar_antighost")
        tangent_pair("vector_antighost_antifield", "vector_multiplier_antifield")
        tangent_pair("scalar_antighost_antifield", "scalar_multiplier_antifield")
        result = cls(
            energy,
            tuple(slices),
            sp.SparseMatrix(cursor, cursor, q_entries),
            sp.SparseMatrix(cursor, cursor, s_entries),
        )
        result.verify()
        return result

    @property
    def dimension(self) -> int:
        return self.tangent_q.rows

    def field(self, name: str) -> NonminimalSlice:
        return next(value for value in self.slices if value.name == name)

    def verify(self) -> None:
        zero = sp.SparseMatrix(self.dimension, self.dimension, {})
        identity = sp.SparseMatrix.eye(self.dimension)
        if self.tangent_q * self.tangent_q != zero:
            raise AssertionError("nonminimal tangent differential is not nilpotent")
        if (
            self.tangent_q * self.tangent_homotopy
            + self.tangent_homotopy * self.tangent_q
            != identity
        ):
            raise AssertionError("nonminimal sector is not explicitly contractible")
        if self.tangent_homotopy * self.tangent_homotopy != zero:
            raise AssertionError("nonminimal homotopy is not square-zero")

    def coordinate_brst_rules(self) -> tuple[dict[str, str], ...]:
        return (
            {"source": "vector_antighost", "image": "vector_multiplier"},
            {"source": "vector_multiplier", "image": "0"},
            {"source": "scalar_antighost", "image": "scalar_multiplier"},
            {"source": "scalar_multiplier", "image": "0"},
            {
                "source": "vector_multiplier_antifield",
                "image": "vector_antighost_antifield",
            },
            {"source": "vector_antighost_antifield", "image": "0"},
            {
                "source": "scalar_multiplier_antifield",
                "image": "scalar_antighost_antifield",
            },
            {"source": "scalar_antighost_antifield", "image": "0"},
        )

