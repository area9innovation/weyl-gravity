"""Exact all-energy right inverse on the E/A/L curvature blocks.

For a normalized highest-weight metric oscillator ``h_{F,n,M}``, define the
geometric curvature basis by

    U_{F,n,M} := C_1 h_{F,n,M}.

The coordinate calculation in :mod:`bridge.cylinder_harmonics` proves that
the highest-weight image is nonzero for symbolic ``n`` in every allowed
tower and that it solves the chiral geometric Weyl equation.  Since ``C_1``
is ``SO(4)``-equivariant and each listed irrep occurs with multiplicity one,
the same holds for every magnetic component.  The map below is consequently
an explicit same-energy, same-irrep right inverse on the whole block:

    R_n(U_{F,n,M}) = h_{F,n,M}.

This normalization is intentional: the Weyl basis inherits the unit
oscillator normalization and invariant form from the metric representative.
``pivot`` additionally records a nonzero coordinate component so the map is
not certified only by a dimension count.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from bridge.cylinder_harmonics.linearized_geometry import (
    CylinderMode,
    LinearizedCylinderGeometry,
    Tensor,
    canonical,
    highest_weight_mode,
    n_symbol,
    tensor_get,
)


BRANCH_MINIMUM = {"E": 2, "A": 3, "L": 4}
PIVOT = {
    (1, "E"): (0, 2, 0, 2),
    (1, "A"): (0, 1, 0, 2),
    (1, "L"): (0, 2, 0, 2),
    (-1, "E"): (0, 1, 0, 1),
    (-1, "A"): (0, 1, 0, 1),
    (-1, "L"): (0, 1, 0, 1),
}


@dataclass(frozen=True)
class CurvatureBasisVector:
    family: str
    energy: sp.Expr
    chirality: int
    metric_preimage: CylinderMode
    tensor: Tensor
    pivot_index: tuple[int, int, int, int]
    pivot: sp.Expr

    @property
    def spin_left(self) -> sp.Expr:
        return self.metric_preimage.spin_left

    @property
    def spin_right(self) -> sp.Expr:
        return self.metric_preimage.spin_right

    @property
    def dimension(self) -> sp.Expr:
        return sp.simplify((2 * self.spin_left + 1) * (2 * self.spin_right + 1))


def curvature_basis(
    family: str,
    energy: sp.Expr = n_symbol,
    chirality: int = 1,
    *,
    geometry: LinearizedCylinderGeometry | None = None,
) -> CurvatureBasisVector:
    if family not in BRANCH_MINIMUM:
        raise ValueError(f"unknown family {family!r}")
    mode = highest_weight_mode(family, energy, chirality)
    geometry = geometry or LinearizedCylinderGeometry()
    tensor = geometry.linearized_weyl(mode)
    pivot_index = PIVOT[chirality, family]
    pivot = canonical(tensor_get(tensor, *pivot_index))
    if pivot == 0:
        raise AssertionError(f"zero Weyl pivot for {family}_{energy}^{chirality:+d}")
    return CurvatureBasisVector(
        family,
        sp.sympify(energy),
        chirality,
        mode,
        tensor,
        pivot_index,
        pivot,
    )


def right_inverse(vector: CurvatureBasisVector) -> CylinderMode:
    """Apply the exact blockwise right inverse to one normalized basis vector."""

    return vector.metric_preimage


def block_dimension(family: str, energy: sp.Expr) -> sp.Expr:
    energy = sp.sympify(energy)
    formulas = {
        "E": (energy + 3) * (energy - 1),
        "A": (energy + 1) * (energy - 1),
        "L": (energy + 1) * (energy - 3),
    }
    if family not in formulas:
        raise ValueError(family)
    return sp.expand(formulas[family])


def level_dimension(energy: int) -> int:
    return int(
        2
        * sum(
            block_dimension(family, energy)
            for family, minimum in BRANCH_MINIMUM.items()
            if energy >= minimum
        )
    )
