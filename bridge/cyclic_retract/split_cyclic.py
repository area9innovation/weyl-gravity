"""Canonical cyclic form on the BGG-split free-BV contraction.

Every nonphysical coordinate belongs to one directed contractible pair
``a --q--> b`` with ``s b=a``.  The Hermitian hyperbolic block

``[[0,i],[-i,0]]``

makes both ``q`` and ``s`` skew-adjoint.  On cohomology the form is the
canonical conformal oscillator form ``+I_E-I_A-I_L`` in each chirality.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from bridge.bv_complex import FreeBVBlock


def sharp(operator: sp.MatrixBase, source_form: sp.MatrixBase, target_form: sp.MatrixBase) -> sp.Matrix:
    """Adjoint for the normalized involutive source and target forms."""

    return sp.simplify(source_form * operator.conjugate().T * target_form)


def _branch_dimensions(energy: int) -> tuple[int, int, int]:
    e = (energy + 3) * (energy - 1)
    a = (energy + 1) * (energy - 1) if energy >= 3 else 0
    l = (energy + 1) * (energy - 3) if energy >= 4 else 0
    return e, a, l


@dataclass(frozen=True)
class CyclicBVRetraction:
    block: FreeBVBlock
    full_form: sp.SparseMatrix
    reduced_form: sp.SparseMatrix
    compact_energy: sp.SparseMatrix

    @classmethod
    def build(cls, energy: int) -> "CyclicBVRetraction":
        block = FreeBVBlock.at_energy(energy)
        e, a, l = _branch_dimensions(energy)
        one_chirality = e + a + l
        if 2 * one_chirality != block.physical_dimension:
            raise AssertionError("E/A/L split does not exhaust cohomology")
        signs = tuple(
            sign
            for _chirality in range(2)
            for sign, size in ((1, e), (-1, a), (-1, l))
            for _ in range(size)
        )
        reduced_form = sp.diag(*signs, cls=sp.SparseMatrix)

        entries: dict[tuple[int, int], sp.Expr] = {}
        # Physical coordinates inherit the reduced form.
        for (row, column), value in (
            block.inclusion * reduced_form * block.inclusion.T
        ).todok().items():
            entries[row, column] = value

        # q is a partial identity on the contractible complement.  Each arrow
        # gets one Hermitian hyperbolic block; no coordinate may occur twice.
        used: set[int] = set()
        for (target, source), value in block.q.todok().items():
            if value != 1:
                raise AssertionError("split differential is not a partial identity")
            if source in used or target in used:
                raise AssertionError("contractible coordinate belongs to two pairs")
            used.update((source, target))
            entries[source, target] = sp.I
            entries[target, source] = -sp.I
        if len(used) + block.physical_dimension != block.dimension:
            raise AssertionError("not every nonphysical coordinate is paired")
        full_form = sp.SparseMatrix(block.dimension, block.dimension, entries)
        compact_energy = energy * sp.SparseMatrix.eye(block.dimension)
        result = cls(block, full_form, reduced_form, compact_energy)
        result.verify()
        return result

    def verify(self) -> None:
        b = self.block
        full_identity = sp.SparseMatrix.eye(b.dimension)
        reduced_identity = sp.SparseMatrix.eye(b.physical_dimension)
        if self.full_form.conjugate().T != self.full_form:
            raise AssertionError("full BV form is not Hermitian")
        if self.full_form * self.full_form != full_identity:
            raise AssertionError("full BV form is not an involution")
        if self.reduced_form.conjugate().T != self.reduced_form:
            raise AssertionError("reduced form is not Hermitian")
        if self.reduced_form * self.reduced_form != reduced_identity:
            raise AssertionError("reduced form is not an involution")
        if sharp(b.q, self.full_form, self.full_form) != -b.q:
            raise AssertionError("q is not skew-adjoint")
        if sharp(b.homotopy, self.full_form, self.full_form) != -b.homotopy:
            raise AssertionError("s is not skew-adjoint")
        if sharp(b.inclusion, self.reduced_form, self.full_form) != b.projection:
            raise AssertionError("j^sharp != p")
        if b.inclusion.conjugate().T * self.full_form * b.inclusion != self.reduced_form:
            raise AssertionError("inclusion is not an isometry")
        if self.compact_energy * b.homotopy != b.homotopy * self.compact_energy:
            raise AssertionError("[D,s] != 0")
        if self.compact_energy * b.inclusion != b.inclusion * (
            b.energy * sp.SparseMatrix.eye(b.physical_dimension)
        ):
            raise AssertionError("D j != j D_H")

    def dressed_maps(self, perturbation: sp.MatrixBase):
        """Return cyclic HPL maps for a supplied skew-adjoint perturbation."""

        b = self.block
        identity = sp.SparseMatrix.eye(b.dimension)
        left = identity + b.homotopy * perturbation
        right = identity + perturbation * b.homotopy
        inclusion = sp.simplify(left.inv() * b.inclusion)
        projection = sp.simplify(b.projection * right.inv())
        transferred = sp.simplify(b.projection * perturbation * inclusion)
        return inclusion, projection, transferred
