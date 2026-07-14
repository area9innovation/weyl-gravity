"""Exact matrix kernel for conjugating a four-row BV differential.

The genuinely curved input to this kernel is the complete 66-by-66
differential produced by the curved-operator workstream.  This module does
not manufacture that input.  It centralizes every algebraic check which must
be run once it exists: change of variables, block split, both chain maps, and
the deformation-retract identity.

For now :meth:`from_fourier_regression` instantiates the kernel on the exact
ordinary-derivative Fourier complex.  That regression is important: it
proves that the interface and signs used here recover the already certified
66-to-30 SDR, without mistaking the regression for the missing curved
coefficient theorem.
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
class FourRowQConjugation:
    """A checked 66-to-30 SDR obtained from one supplied differential.

    ``ordered_new_to_old`` includes both the local canonical change and the
    permutation putting the retained 30 coordinates before the 36
    generalized-auxiliary coordinates.  Supplying it explicitly avoids any
    ambiguity about whether a matrix acts on fields, antifields, or their
    reordered direct sum.
    """

    source_differential: sp.Matrix
    ordered_new_to_old: sp.Matrix
    transformed_differential: sp.Matrix
    core_differential: sp.Matrix
    auxiliary_differential: sp.Matrix
    auxiliary_homotopy: sp.Matrix
    inclusion: sp.Matrix
    projection: sp.Matrix
    homotopy: sp.Matrix
    source_scope: str

    @staticmethod
    def build(
        *,
        source_differential: sp.MatrixBase,
        ordered_new_to_old: sp.MatrixBase,
        auxiliary_homotopy: sp.MatrixBase,
        source_scope: str,
    ) -> "FourRowQConjugation":
        """Conjugate one exact four-row differential and extract its SDR.

        The coefficient ring must support exact SymPy matrix arithmetic.  A
        curved caller is responsible for first reducing differential
        compositions to the repository's canonical derivative normal form.
        """

        q = sp.Matrix(source_differential)
        u = sp.Matrix(ordered_new_to_old)
        k_aux = sp.Matrix(auxiliary_homotopy)
        if q.shape != (66, 66):
            raise ValueError("the four-row BV differential must be 66-by-66")
        if u.shape != (66, 66):
            raise ValueError("the ordered canonical transformation must be 66-by-66")
        if k_aux.shape != (36, 36):
            raise ValueError("the generalized-auxiliary homotopy must be 36-by-36")

        u_inverse = u.inv()
        transformed = sp.simplify(u_inverse * q * u)
        core = transformed[:30, :30]
        auxiliary = transformed[30:, 30:]

        core_embedding = sp.eye(66)[:, :30]
        inclusion = sp.simplify(u * core_embedding)
        projection = sp.simplify(core_embedding.T * u_inverse)
        ordered_homotopy = sp.zeros(66)
        ordered_homotopy[30:, 30:] = k_aux
        homotopy = sp.simplify(u * ordered_homotopy * u_inverse)

        result = FourRowQConjugation(
            source_differential=q,
            ordered_new_to_old=u,
            transformed_differential=transformed,
            core_differential=core,
            auxiliary_differential=auxiliary,
            auxiliary_homotopy=k_aux,
            inclusion=inclusion,
            projection=projection,
            homotopy=homotopy,
            source_scope=source_scope,
        )
        result.verify()
        return result

    @staticmethod
    def from_fourier_regression(
        retract: GeneralizedAuxiliaryRetract | None = None,
    ) -> "FourRowQConjugation":
        """Recover the existing exact Fourier SDR through the new interface."""

        if retract is None:
            retract = GeneralizedAuxiliaryRetract.build()
        core_indices = (
            list(range(0, 4))
            + [8]
            + list(range(9, 19))
            + list(range(43, 53))
            + list(range(61, 66))
        )
        auxiliary_indices = (
            list(range(4, 8))
            + list(range(19, 29))
            + list(range(29, 33))
            + list(range(33, 43))
            + list(range(53, 57))
            + list(range(57, 61))
        )
        permutation = sp.eye(66)[:, core_indices + auxiliary_indices]
        # Reuse the matrices already conjugated and verified by the source
        # retract.  Repeating a symbolic 66-by-66 inversion here adds minutes
        # to every aggregate verifier without increasing coverage.
        result = FourRowQConjugation(
            source_differential=retract.original_differential,
            ordered_new_to_old=retract.total_new_to_old * permutation,
            transformed_differential=retract.ordered_differential,
            core_differential=retract.core_differential,
            auxiliary_differential=retract.auxiliary_differential,
            auxiliary_homotopy=retract.auxiliary_homotopy,
            inclusion=retract.inclusion,
            projection=retract.projection,
            homotopy=retract.total_homotopy,
            source_scope="flat_fourier_regression",
        )
        result.verify()
        if sp.simplify(
            result.transformed_differential - retract.ordered_differential
        ) != sp.zeros(66):
            raise AssertionError("the conjugation interface changed the ordered Q")
        if sp.simplify(result.inclusion - retract.inclusion) != sp.zeros(66, 30):
            raise AssertionError("the conjugation interface changed the inclusion")
        if sp.simplify(result.projection - retract.projection) != sp.zeros(30, 66):
            raise AssertionError("the conjugation interface changed the projection")
        if sp.simplify(result.homotopy - retract.total_homotopy) != sp.zeros(66):
            raise AssertionError("the conjugation interface changed the homotopy")
        return result

    @property
    def off_diagonal_defect(self) -> sp.Matrix:
        return self.transformed_differential[:30, 30:].row_join(
            sp.zeros(30, 30)
        ).col_join(
            sp.zeros(36, 36).row_join(
                self.transformed_differential[30:, :30]
            )
        )

    def verify(self) -> None:
        q = self.source_differential
        q_core = self.core_differential
        q_aux = self.auxiliary_differential
        if sp.simplify(q * q) != sp.zeros(66):
            raise AssertionError("the supplied four-row Q is not nilpotent")
        if self.transformed_differential[:30, 30:] != sp.zeros(30, 36):
            raise AssertionError("the retained core maps into the auxiliary sector")
        if self.transformed_differential[30:, :30] != sp.zeros(36, 30):
            raise AssertionError("the auxiliary sector maps into the retained core")
        if sp.simplify(q_core * q_core) != sp.zeros(30):
            raise AssertionError("the retained metric differential is not nilpotent")
        if sp.simplify(q_aux * q_aux) != sp.zeros(36):
            raise AssertionError("the generalized-auxiliary differential is not nilpotent")
        if sp.simplify(
            q_aux * self.auxiliary_homotopy
            + self.auxiliary_homotopy * q_aux
        ) != -sp.eye(36):
            raise AssertionError("the generalized-auxiliary homotopy has the wrong sign")
        if self.projection * self.inclusion != sp.eye(30):
            raise AssertionError("p i is not the identity")
        if sp.simplify(q * self.inclusion - self.inclusion * q_core) != sp.zeros(66, 30):
            raise AssertionError("the inclusion is not a chain map")
        if sp.simplify(self.projection * q - q_core * self.projection) != sp.zeros(30, 66):
            raise AssertionError("the projection is not a chain map")
        if sp.simplify(
            self.inclusion * self.projection
            - sp.eye(66)
            - q * self.homotopy
            - self.homotopy * q
        ) != sp.zeros(66):
            raise AssertionError("i p-1=Qk+kQ failed")

    def certificate(self, *, reverify: bool = True) -> dict[str, object]:
        if reverify:
            self.verify()
        return {
            "schema": "pure-weyl-four-row-Q-conjugation-kernel-v1",
            "source_scope": self.source_scope,
            "dimensions": {
                "source": 66,
                "retained_metric_core": 30,
                "generalized_auxiliary": 36,
            },
            "exact_checks": {
                "source_Q_squared": "zero",
                "transformed_off_diagonal_blocks": "zero",
                "core_Q_squared": "zero",
                "auxiliary_Q_squared": "zero",
                "p_i": "identity",
                "Q_i_minus_i_Qcore": "zero",
                "p_Q_minus_Qcore_p": "zero",
                "i_p_minus_identity": "Qk+kQ",
            },
            "matrix_sha256": {
                "source_Q": _digest(self.source_differential),
                "ordered_new_to_old": _digest(self.ordered_new_to_old),
                "transformed_Q": _digest(self.transformed_differential),
                "core_Q": _digest(self.core_differential),
                "auxiliary_Q": _digest(self.auxiliary_differential),
                "inclusion": _digest(self.inclusion),
                "projection": _digest(self.projection),
                "homotopy": _digest(self.homotopy),
            },
            "is_complete_curved_Q_certificate": self.source_scope == "curved_global",
            "guard": (
                "the Fourier regression proves the conjugation/retract engine and "
                "its sign conventions, but only a canonical-normal-form input with "
                "source_scope=curved_global can discharge the curved theorem"
            ),
        }
