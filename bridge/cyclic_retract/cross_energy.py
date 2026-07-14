"""Contravariant form on the raw transferred cylinder cohomology.

The raw polynomial retract supplies rational matrices for the four lowering
and four raising conformal generators, but its cohomology basis is not the
``E/A/L`` oscillator basis.  This module reconstructs the invariant form in
that raw basis without fitting a change of basis.

Write ``P_a(n): H_n -> H_(n-1)`` for ``K^-`` and
``K_a(n-1): H_(n-1) -> H_n`` for ``K^+``.  In the conventions of
``RawResidualModule`` the contravariant identity is

    J_n K_a(n-1) = -P_a(n)^T J_(n-1).

The four raising blocks have joint full row rank.  Consequently ``J_n`` is
fixed uniquely by ``J_(n-1)``.  Starting with the curvature-normalized
positive form at energy two gives the complete cross-energy form on every
finite buffer.  All arithmetic is exact rational arithmetic.

This is the physical cohomology form.  It does not by itself identify the
canonical BV antibracket on every contractible field/antifield row.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from bridge.residual_bfv import ConformalCE
from bridge.transfer.raw_residual import RawResidualModule


def exact_symmetric_inertia(matrix: sp.MatrixBase) -> tuple[int, int, int]:
    """Return the inertia of an exact real symmetric matrix by congruence.

    A nonzero diagonal pivot contributes its rational sign and is removed by
    a Schur complement.  If every diagonal entry vanishes, a nonzero
    off-diagonal entry supplies a hyperbolic two-plane with inertia ``(1,1)``.
    This is an exact Sylvester-law calculation; no floating eigenvalues enter.
    """

    work = sp.MutableDenseMatrix(matrix)
    positive = negative = zero = 0
    while work.rows:
        size = work.rows
        pivot = next((i for i in range(size) if work[i, i] != 0), None)
        if pivot is not None:
            if pivot:
                work.row_swap(0, pivot)
                work.col_swap(0, pivot)
            value = work[0, 0]
            if bool(value > 0):
                positive += 1
            elif bool(value < 0):
                negative += 1
            else:  # pragma: no cover - guarded by exact rational inputs
                raise AssertionError(f"undecidable exact pivot sign: {value}")
            if size == 1:
                work = sp.MutableDenseMatrix(0, 0, [])
                continue
            column = work[1:, 0]
            work = sp.MutableDenseMatrix(
                work[1:, 1:] - column * column.T / value
            )
            continue

        pair = next(
            (
                (first, second)
                for first in range(size)
                for second in range(first + 1, size)
                if work[first, second] != 0
            ),
            None,
        )
        if pair is None:
            zero += size
            break
        remainder = [index for index in range(size) if index not in pair]
        permutation = [*pair, *remainder]
        work = sp.MutableDenseMatrix(work.extract(permutation, permutation))
        hyperbolic = work[:2, :2]
        coupling = work[2:, :2]
        positive += 1
        negative += 1
        work = sp.MutableDenseMatrix(
            work[2:, 2:] - coupling * hyperbolic.inv() * coupling.T
        )
    return positive, negative, zero


def expected_signature(energy: int) -> tuple[int, int, int]:
    """The parity-complete ``+E,-A,-L`` signature at one energy."""

    e = (energy + 3) * (energy - 1)
    a = (energy + 1) * (energy - 1) if energy >= 3 else 0
    l = (energy + 1) * (energy - 3) if energy >= 4 else 0
    return 2 * e, 2 * (a + l), 0


def _solve_next_form(
    raw: RawResidualModule,
    previous_form: sp.MatrixBase,
    energy: int,
) -> tuple[sp.Matrix, int]:
    ce = ConformalCE.build()
    previous = raw.indices_at(energy - 1)
    current = raw.indices_at(energy)
    raising_blocks: list[sp.Matrix] = []
    targets: list[sp.Matrix] = []
    for axis in range(4):
        lowering = sp.Matrix(raw.matrices[ce.index[f"K-_{axis}"]]).extract(
            previous, current
        )
        raising = sp.Matrix(raw.matrices[ce.index[f"K+_{axis}"]]).extract(
            current, previous
        )
        raising_blocks.append(raising)
        targets.append(-lowering.T * previous_form)

    joint_raising = sp.Matrix.hstack(*raising_blocks)
    target = sp.Matrix.hstack(*targets)
    pivots = tuple(
        joint_raising.rref(simplify=False, normalize_last=True)[1]
    )
    if len(pivots) != len(current):
        raise AssertionError(
            f"four raising blocks do not span H_{energy}: "
            f"rank {len(pivots)} != {len(current)}"
        )
    square = joint_raising[:, list(pivots)]
    result = sp.Matrix(target[:, list(pivots)] * square.inv())
    if any(
        result * raising != expected
        for raising, expected in zip(raising_blocks, targets)
    ):
        raise AssertionError("contravariant recursion is inconsistent")
    return result, len(pivots)


@dataclass(frozen=True)
class CrossEnergyCohomologyForm:
    """Exact invariant forms in the raw polynomial cohomology bases."""

    raw: RawResidualModule
    forms: dict[int, sp.Matrix]
    joint_raising_ranks: dict[int, int]
    signatures: dict[int, tuple[int, int, int]]

    @classmethod
    def build(cls, maximum_energy: int = 5) -> "CrossEnergyCohomologyForm":
        if maximum_energy < 3:
            raise ValueError("need at least energies two and three")
        raw = RawResidualModule.build(maximum_energy)

        # Lazy import avoids a package cycle: integration imports the raw
        # residual module, while this module is an optional stronger layer.
        from bridge.transfer.integration import energy_two_metric_form

        forms = {2: sp.Matrix(energy_two_metric_form(raw))}
        ranks: dict[int, int] = {}
        for energy in range(3, maximum_energy + 1):
            forms[energy], ranks[energy] = _solve_next_form(
                raw, forms[energy - 1], energy
            )
        signatures = {
            energy: exact_symmetric_inertia(form)
            for energy, form in forms.items()
        }
        result = cls(raw, forms, ranks, signatures)
        result.verify()
        return result

    def verify(self) -> None:
        ce = ConformalCE.build()
        for energy, form in self.forms.items():
            dimension = self.raw.dimensions[energy]
            if form.shape != (dimension, dimension):
                raise AssertionError("cross-energy form has the wrong shape")
            if form != form.T or form.rank() != dimension:
                raise AssertionError("cross-energy form is not nondegenerate symmetric")
            if self.signatures[energy] != expected_signature(energy):
                raise AssertionError(
                    f"energy {energy} signature {self.signatures[energy]} "
                    f"!= {expected_signature(energy)}"
                )
            retract = self.raw.retracts[energy]
            for first in range(4):
                for second in range(first + 1, 4):
                    rotation = retract.induced(
                        retract.block.rotation(first, second), retract
                    )
                    if rotation.T * form + form * rotation != sp.zeros(dimension):
                        raise AssertionError("SO(4) invariance failed")

        for energy in range(3, self.raw.maximum_energy + 1):
            previous = self.raw.indices_at(energy - 1)
            current = self.raw.indices_at(energy)
            for axis in range(4):
                lowering = sp.Matrix(
                    self.raw.matrices[ce.index[f"K-_{axis}"]]
                ).extract(previous, current)
                raising = sp.Matrix(
                    self.raw.matrices[ce.index[f"K+_{axis}"]]
                ).extract(current, previous)
                if (
                    self.forms[energy] * raising
                    != -lowering.T * self.forms[energy - 1]
                ):
                    raise AssertionError("K+/K- contravariant identity failed")

    def block_diagonal_form(self) -> sp.Matrix:
        return sp.diag(
            *(self.forms[energy] for energy in sorted(self.forms))
        )


def sharp(
    operator: sp.MatrixBase,
    source_form: sp.MatrixBase,
    target_form: sp.MatrixBase,
) -> sp.Matrix:
    """Adjoint between arbitrary nondegenerate Hermitian forms."""

    return sp.simplify(
        sp.Matrix(source_form).inv()
        * sp.Matrix(operator).conjugate().T
        * sp.Matrix(target_form)
    )


@dataclass(frozen=True)
class RawCyclicRetraction:
    """Cyclic form transported to the actual raw polynomial BV basis.

    The physical block is the cross-energy form reconstructed above.  Every
    partial-identity arrow in the adapted contractible complement receives
    the canonical Hermitian hyperbolic form.  Transport by the exact adapted
    basis gives a nondegenerate form on the raw ghost/metric/equation/identity
    rows and makes ``q``, ``s``, ``j``, and ``p`` cyclic exactly.
    """

    retraction: object
    reduced_form: sp.Matrix
    full_form: sp.Matrix

    @classmethod
    def build(
        cls,
        retraction: object,
        reduced_form: sp.MatrixBase,
    ) -> "RawCyclicRetraction":
        # ``object`` avoids a runtime import cycle in type checking; the
        # required interface is RawPolynomialRetraction.
        r = retraction
        t_inverse = sp.Matrix(r.adapted_inverse)
        q_adapted = t_inverse * sp.Matrix(r.block.q) * sp.Matrix(r.adapted_basis)
        inclusion_adapted = t_inverse * sp.Matrix(r.inclusion)
        full_adapted = sp.zeros(r.block.dimension)

        physical_rows = []
        for column in range(inclusion_adapted.cols):
            rows = [
                row
                for row in range(inclusion_adapted.rows)
                if inclusion_adapted[row, column] != 0
            ]
            if len(rows) != 1 or inclusion_adapted[rows[0], column] != 1:
                raise AssertionError("adapted cohomology inclusion is not coordinate")
            physical_rows.append(rows[0])
        for row, physical_row in enumerate(physical_rows):
            for column, physical_column in enumerate(physical_rows):
                full_adapted[physical_row, physical_column] = reduced_form[row, column]

        used = set(physical_rows)
        for (target, source), value in q_adapted.todok().items():
            if value != 1:
                raise AssertionError("adapted q is not a partial identity")
            if source in used or target in used:
                raise AssertionError("adapted cyclic coordinate used twice")
            used.update((source, target))
            full_adapted[source, target] = sp.I
            full_adapted[target, source] = -sp.I
        if len(used) != r.block.dimension:
            raise AssertionError("raw cyclic form did not exhaust the BV block")

        full_raw = sp.simplify(t_inverse.conjugate().T * full_adapted * t_inverse)
        result = cls(r, sp.Matrix(reduced_form), sp.Matrix(full_raw))
        result.verify()
        return result

    def verify(self) -> None:
        r = self.retraction
        if self.full_form != self.full_form.conjugate().T:
            raise AssertionError("raw full cyclic form is not Hermitian")
        # Nondegeneracy follows constructively: the adapted physical block is
        # nondegenerate, every other block is a 2x2 hyperbolic plane, and the
        # transported basis is invertible.  Avoid re-inverting the large raw
        # matrix merely to restate that fact.
        if (
            sp.Matrix(r.block.q).conjugate().T * self.full_form
            != -self.full_form * sp.Matrix(r.block.q)
        ):
            raise AssertionError("raw q is not cyclic")
        if (
            sp.Matrix(r.homotopy).conjugate().T * self.full_form
            != -self.full_form * sp.Matrix(r.homotopy)
        ):
            raise AssertionError("raw s is not cyclic")
        if (
            sp.Matrix(r.inclusion).conjugate().T * self.full_form
            != self.reduced_form * sp.Matrix(r.projection)
        ):
            raise AssertionError("raw j^sharp != p")
        if (
            r.inclusion.conjugate().T * self.full_form * r.inclusion
            != self.reduced_form
        ):
            raise AssertionError("raw inclusion is not an exact isometry")
