"""Exact all-row contraction once the auxiliary BV differential is split.

This is the universal algebraic half of the curved retract.  It extracts the
actual 36-dimensional cotangent summand from the certified Fourier complex
and proves its contraction.  The matrices contain no Fourier covector after
the canonical auxiliary shift, so they are the pointwise model of the curved
generalized-auxiliary summand.  Identifying the *actual curved* transformed
BV differential with this model is intentionally a separate false flag.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import sympy as sp

from covariant_completion.auxiliary_equivalence import GeneralizedAuxiliaryRetract


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableDenseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class UniversalAuxiliarySplit:
    differential: sp.Matrix
    homotopy: sp.Matrix
    covector_free: bool

    @staticmethod
    def build(
        retract: GeneralizedAuxiliaryRetract | None = None,
    ) -> "UniversalAuxiliarySplit":
        if retract is None:
            retract = GeneralizedAuxiliaryRetract.build()
        differential = retract.auxiliary_differential
        homotopy = retract.auxiliary_homotopy
        covector_free = not any(
            differential.has(component) or homotopy.has(component)
            for component in retract.system.covector
        )
        result = UniversalAuxiliarySplit(
            differential=differential,
            homotopy=homotopy,
            covector_free=covector_free,
        )
        result.verify()
        return result

    def verify(self) -> None:
        if not self.covector_free:
            raise AssertionError("the post-shift auxiliary summand is not pointwise")
        if self.differential * self.differential != sp.zeros(36):
            raise AssertionError("the universal auxiliary differential is not nilpotent")
        if (
            self.differential * self.homotopy
            + self.homotopy * self.differential
            != -sp.eye(36)
        ):
            raise AssertionError("the universal auxiliary cotangent complex did not contract")

    def certificate(self, *, reverify: bool = True) -> dict[str, object]:
        if reverify:
            self.verify()
        return {
            "schema": "pure-weyl-universal-curved-generalized-auxiliary-split-v1",
            "dimension": 36,
            "pointwise_after_shift": self.covector_free,
            "all_rows": [
                {"arrow": "eta -> -v", "rank": 4},
                {"arrow": "phi_hat -> A_g phi_hat^*", "rank": 10},
                {"arrow": "v^* -> +eta^*", "rank": 4},
            ],
            "nilpotency": "q_genaux^2=0",
            "selected_sign_convention": "q_genaux k+k q_genaux=-identity",
            "contractible": True,
            "differential_sha256": _digest(self.differential),
            "homotopy_sha256": _digest(self.homotopy),
            "actual_curved_Q_identified_with_split_model": False,
            "theorem_boundary": (
                "the universal post-shift summand contracts exactly; the explicit "
                "curved Q conjugation is still required before this becomes the "
                "curved deformation retract"
            ),
        }
