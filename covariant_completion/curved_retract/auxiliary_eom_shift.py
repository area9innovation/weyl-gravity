"""Exact covariant completion of the auxiliary tensor square.

The ordinary-derivative Weyl action contains the auxiliary part

``1/2 <phi,A_g phi>-<phi,G^b(g,b)>``

with ``A_g phi=-1/2(phi-g tr_g(phi))``.  The inverse of ``A_g`` is a
pointwise natural bundle map in four dimensions.  Consequently the nonlinear
change ``phi_hat=phi-A_g^{-1}G^b`` is exact on every curved background; no
Fourier transform, Green operator, or cylinder harmonic projector is used.

This module proves the fibre algebra and the completion-of-square identity.
It deliberately does *not* claim that the repository's not-yet-emitted curved
four-row BV matrix has been conjugated by the tangent of this shift.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import sympy as sp


DIMENSION = 4
SYMMETRIC_COORDINATES = (
    (0, 0),
    (0, 1),
    (0, 2),
    (0, 3),
    (1, 1),
    (1, 2),
    (1, 3),
    (2, 2),
    (2, 3),
    (3, 3),
)


def _symmetric_tensor(prefix: str) -> sp.Matrix:
    entries = sp.symbols(f"{prefix}0:{len(SYMMETRIC_COORDINATES)}")
    tensor = sp.zeros(DIMENSION)
    for entry, (mu, nu) in zip(entries, SYMMETRIC_COORDINATES, strict=True):
        tensor[mu, nu] = entry
        tensor[nu, mu] = entry
    return tensor


def _digest(expr: sp.Expr | sp.MatrixBase) -> str:
    return hashlib.sha256(sp.srepr(expr).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CurvedAuxiliaryEOMShift:
    """Coordinate-free fibre certificate for the curved auxiliary shift."""

    metric: sp.Matrix
    inverse_metric: sp.Matrix
    auxiliary_tensor: sp.Matrix
    source_tensor: sp.Matrix
    mass_image: sp.Matrix
    inverse_mass_image: sp.Matrix
    shifted_tensor: sp.Matrix
    original_density: sp.Expr
    split_density: sp.Expr
    eliminated_density: sp.Expr

    @staticmethod
    def build() -> "CurvedAuxiliaryEOMShift":
        # A normal orthonormal frame is sufficient for this natural pointwise
        # bundle identity.  Its formula below is tensorial and therefore valid
        # for every Lorentzian metric, not just at the selected frame.
        metric = sp.diag(-1, 1, 1, 1)
        inverse_metric = metric.inv()
        auxiliary = _symmetric_tensor("f")
        source = _symmetric_tensor("G")

        def trace(tensor: sp.Matrix) -> sp.Expr:
            return sp.expand(sp.trace(inverse_metric * tensor))

        def inner(left: sp.Matrix, right: sp.Matrix) -> sp.Expr:
            return sp.expand(
                sp.trace(inverse_metric * left * inverse_metric * right)
            )

        def mass(tensor: sp.Matrix) -> sp.Matrix:
            return sp.simplify(
                -sp.Rational(1, 2)
                * (tensor - metric * trace(tensor))
            )

        def inverse_mass(tensor: sp.Matrix) -> sp.Matrix:
            return sp.simplify(
                -2 * tensor
                + sp.Rational(2, 3) * metric * trace(tensor)
            )

        mass_image = mass(auxiliary)
        inverse_mass_image = inverse_mass(source)
        shifted = sp.simplify(auxiliary - inverse_mass_image)

        original_density = sp.expand(
            sp.Rational(1, 2) * inner(auxiliary, mass_image)
            - inner(auxiliary, source)
        )
        split_density = sp.expand(
            sp.Rational(1, 2) * inner(shifted, mass(shifted))
            - sp.Rational(1, 2) * inner(source, inverse_mass_image)
        )
        eliminated_density = sp.expand(
            inner(source, source)
            - sp.Rational(1, 3) * trace(source) ** 2
        )

        result = CurvedAuxiliaryEOMShift(
            metric=metric,
            inverse_metric=inverse_metric,
            auxiliary_tensor=auxiliary,
            source_tensor=source,
            mass_image=mass_image,
            inverse_mass_image=inverse_mass_image,
            shifted_tensor=shifted,
            original_density=original_density,
            split_density=split_density,
            eliminated_density=eliminated_density,
        )
        result.verify()
        return result

    def _trace(self, tensor: sp.Matrix) -> sp.Expr:
        return sp.expand(sp.trace(self.inverse_metric * tensor))

    def _mass(self, tensor: sp.Matrix) -> sp.Matrix:
        return sp.simplify(
            -sp.Rational(1, 2)
            * (tensor - self.metric * self._trace(tensor))
        )

    def _inverse_mass(self, tensor: sp.Matrix) -> sp.Matrix:
        return sp.simplify(
            -2 * tensor
            + sp.Rational(2, 3) * self.metric * self._trace(tensor)
        )

    def verify(self) -> None:
        if self._mass(self.inverse_mass_image) != self.source_tensor:
            raise AssertionError("A_g A_g^{-1} is not the identity")
        if self._inverse_mass(self.mass_image) != self.auxiliary_tensor:
            raise AssertionError("A_g^{-1} A_g is not the identity")
        if sp.expand(self.original_density - self.split_density) != 0:
            raise AssertionError("the curved auxiliary square did not complete")
        on_shell = sp.expand(
            self.original_density.subs(
                {
                    self.auxiliary_tensor[mu, nu]: self.inverse_mass_image[mu, nu]
                    for mu, nu in SYMMETRIC_COORDINATES
                },
                simultaneous=True,
            )
        )
        if sp.expand(on_shell - self.eliminated_density) != 0:
            raise AssertionError("the pointwise auxiliary elimination is wrong")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-curved-auxiliary-eom-shift-v1",
            "dimension": DIMENSION,
            "source_action_auxiliary_density": (
                "1/2 <phi,A_g phi>-<phi,G^b(g,b)>"
            ),
            "mass_bundle_map": "A_g(phi)=-1/2(phi-g tr_g(phi))",
            "pointwise_inverse": "A_g^{-1}(s)=-2s+(2/3)g tr_g(s)",
            "nonlinear_shift": "phi_hat=phi-A_g^{-1}G^b(g,b)",
            "exact_completion_of_square": True,
            "eliminated_density": "<G^b,G^b>-(tr_g G^b)^2/3",
            "tangent_shift": (
                "f_hat=f-D[A_g^{-1}G^b]_(gbar,bbar)(h,v)"
            ),
            "tangent_differential_orders": {
                "h": 2,
                "v": 1,
                "auxiliary_mass_inverse": 0,
            },
            "pointwise_mass_inverse_exact": True,
            "uses_green_operator": False,
            "uses_nonlocal_projector": False,
            "sha256": {
                "mass_image": _digest(self.mass_image),
                "inverse_mass_image": _digest(self.inverse_mass_image),
                "original_density": _digest(self.original_density),
                "split_density": _digest(self.split_density),
            },
            "theorem_boundary": (
                "the natural nonlinear auxiliary shift and its tangent are exact; "
                "the explicit curved four-row Q conjugation remains a separate check"
            ),
        }
