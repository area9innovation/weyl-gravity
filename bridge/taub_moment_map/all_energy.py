"""All-energy action-normalized conformal Taub moment maps.

The local second-order Noether identity identifies the Taub functional of a
conformal reducibility with the quadratic Hamiltonian of its action on the
linearized solution space.  In the Hamada--Horata oscillator normalization
the quadratic form is ``J=+E-A-L``.  The action used by the direct curvature
calculation is

    S_red = integral (Ricci^2-R^2/3) = -S_HH/2  (mod Euler),

so the canonical quadratic charge kernel is

    M_X = -1/2 J K_X.

The proper-conformal Killing vector and spherical harmonic used by the raw
curvature scripts differ from the canonical generator basis.  After the
mixed-polarization factor is included, their reduced kernels are

    M_raw(K^-) = sqrt(2)/(2*pi) M_canonical(K^-)
                = -sqrt(2)/(4*pi) J K^-.

Two independent direct ``B^(2)`` curvature integrations fix this one scale.
Conformal equivariance then determines every proper-conformal block at every
energy; the seven compact kernels are fixed directly by the same quadratic
action.  The finite buffers below are verification devices, not finite
representations.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from symbolic import verify_conformal_generator_all_levels as generators
from symbolic.verify_conformal_taub_multiplets import MAGNETIC_COMPONENTS


CANONICAL_ACTION_SCALE = -sp.Rational(1, 2)
RAW_CK_TO_CANONICAL_SCALE = sp.sqrt(2) / (2 * sp.pi)
RAW_TAUB_SCALE = sp.simplify(
    CANONICAL_ACTION_SCALE * RAW_CK_TO_CANONICAL_SCALE
)


def _symbolic_generator_coefficient(family: str, n: sp.Expr) -> sp.Expr:
    n = sp.sympify(n)
    squares = {
        "EE": 2 * (n - 1) * (n + 1) * (n + 3) / (n + 2),
        "AE": 8 * (n - 1) / ((n - 2) * (n + 2)),
        "AA": 2 * (n - 3) * (n - 1) * (n + 2) / (n - 2),
        "LE": 2 * (n - 3) / (n - 2),
        "LA": 8 / (n - 2),
        "LL": 2 * (n - 2) * (n + 1),
    }
    if family not in squares:
        raise ValueError(f"unknown lowering family {family}")
    phase = -1 if family == "LE" else 1
    return sp.simplify(phase * sp.sqrt(squares[family]))


def raw_taub_reduced_coefficient(family: str, energy: sp.Expr) -> sp.Expr:
    """Raw curvature-script coefficient for any proper-CK lowering family."""

    target = family[1]
    target_sign = generators.FORM_SIGN[target]
    return sp.simplify(
        RAW_TAUB_SCALE
        * target_sign
        * _symbolic_generator_coefficient(family, energy)
    )


def _direct_sum(first: sp.MatrixBase, second: sp.MatrixBase) -> sp.Matrix:
    return sp.diag(first, second, cls=sp.SparseMatrix)


@dataclass(frozen=True)
class AllEnergyTaubMomentMap:
    """Parity-complete finite buffer of the all-energy Taub map."""

    maximum_energy: int
    plus: generators.CutoffRepresentation
    minus: generators.CutoffRepresentation
    form: sp.Matrix
    compact_generators: dict[str, sp.Matrix]
    lowering_generators: dict[tuple[sp.Rational, sp.Rational], sp.Matrix]
    raising_generators: dict[tuple[sp.Rational, sp.Rational], sp.Matrix]
    compact_kernels: dict[str, sp.Matrix]
    lowering_kernels: dict[tuple[sp.Rational, sp.Rational], sp.Matrix]
    raising_kernels: dict[tuple[sp.Rational, sp.Rational], sp.Matrix]

    @classmethod
    def build(cls, maximum_energy: int = 5) -> "AllEnergyTaubMomentMap":
        plus = generators.representation_space(maximum_energy, 1)
        minus = generators.representation_space(maximum_energy, -1)
        form = _direct_sum(plus.form, minus.form)
        compact = {
            "D": _direct_sum(plus.energy, minus.energy),
            **{
                f"L{axis}": _direct_sum(plus.left[axis], minus.left[axis])
                for axis in ("x", "y", "z")
            },
            **{
                f"R{axis}": _direct_sum(plus.right[axis], minus.right[axis])
                for axis in ("x", "y", "z")
            },
        }
        lowering = {
            component: _direct_sum(
                plus.lowering[component], minus.lowering[component]
            )
            for component in MAGNETIC_COMPONENTS
        }
        raising = {
            component: _direct_sum(
                plus.raising[component], minus.raising[component]
            )
            for component in MAGNETIC_COMPONENTS
        }

        def kernel(matrix: sp.MatrixBase) -> sp.Matrix:
            return sp.Matrix(CANONICAL_ACTION_SCALE * form * matrix)

        result = cls(
            maximum_energy,
            plus,
            minus,
            sp.Matrix(form),
            compact,
            lowering,
            raising,
            {label: kernel(matrix) for label, matrix in compact.items()},
            {component: kernel(matrix) for component, matrix in lowering.items()},
            {component: kernel(matrix) for component, matrix in raising.items()},
        )
        result.verify()
        return result

    @property
    def dimension(self) -> int:
        return self.form.rows

    def indices_through(self, energy: int) -> tuple[int, ...]:
        plus = self.plus.indices_through(energy)
        return plus + tuple(
            self.plus.dimension + index
            for index in self.minus.indices_through(energy)
        )

    def verify(self) -> None:
        if self.form * self.form != sp.eye(self.dimension):
            raise AssertionError("canonical E/A/L form is not involutive")
        for generator, kernel in (
            *zip(self.compact_generators.values(), self.compact_kernels.values()),
            *zip(self.lowering_generators.values(), self.lowering_kernels.values()),
            *zip(self.raising_generators.values(), self.raising_kernels.values()),
        ):
            if kernel != CANONICAL_ACTION_SCALE * self.form * generator:
                raise AssertionError("moment-map kernel normalization failed")

        for space in (self.plus, self.minus):
            if any(
                defect != sp.zeros(defect.rows, defect.cols)
                for defect in generators.interior_bracket_defects(space)
            ):
                raise AssertionError("all-level conformal algebra failed")
            generators.verify_compact_covariance(space)

        # Canonical real compact generators are J-self-adjoint.  The
        # spherical K+ family is the J-adjoint of K-.
        for matrix in self.compact_generators.values():
            if matrix.conjugate().T * self.form != self.form * matrix:
                raise AssertionError("compact generator is not J-self-adjoint")
        for component in MAGNETIC_COMPONENTS:
            if (
                self.raising_generators[component]
                != self.form
                * self.lowering_generators[component].conjugate().T
                * self.form
            ):
                raise AssertionError("proper-conformal J-adjoint failed")

    def raw_lowering_kernels(self) -> dict[tuple[sp.Rational, sp.Rational], sp.Matrix]:
        """Kernels in the direct-curvature CK normalization."""

        return {
            component: sp.simplify(RAW_CK_TO_CANONICAL_SCALE * kernel)
            for component, kernel in self.lowering_kernels.items()
        }
