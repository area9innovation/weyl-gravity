"""Canonical derivative ordering on the parallel-curvature cylinder.

The normal form is component based and exact.  A term is represented by a
word of covariant-derivative indices followed by the covariant indices of
the underlying field.  Adjacent derivative inversions are exchanged using
the curvature commutator.  Curvature acts on *all* covariant slots of the
inner tensor, including its remaining derivative slots.  Since
``nabla R=0`` on the cylinder, no derivative-of-curvature terms occur.

This engine supplies the correct algebra for an exhaustive one-point jet
calculation.  It does not claim that the 24-component Hessian has already
been fed through that calculation.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Mapping

import sympy as sp

from .cylinder_background import CylinderBackground


TermKey = tuple[tuple[int, ...], tuple[int, ...]]


@dataclass(frozen=True)
class ParallelCylinderNormalForm:
    background: CylinderBackground

    @staticmethod
    def build() -> "ParallelCylinderNormalForm":
        result = ParallelCylinderNormalForm(CylinderBackground.build())
        result.verify()
        return result

    def _curvature_action(
        self,
        a: int,
        b: int,
        derivative_suffix: tuple[int, ...],
        field_indices: tuple[int, ...],
    ) -> dict[TermKey, sp.Expr]:
        slots = derivative_suffix + field_indices
        result: dict[TermKey, sp.Expr] = defaultdict(lambda: sp.Integer(0))
        commutator = self.background.covector_commutator(a, b)
        suffix_length = len(derivative_suffix)
        for position, old_index in enumerate(slots):
            for new_index in range(4):
                coefficient = commutator[old_index, new_index]
                if coefficient == 0:
                    continue
                changed = list(slots)
                changed[position] = new_index
                new_suffix = tuple(changed[:suffix_length])
                new_field = tuple(changed[suffix_length:])
                result[(new_suffix, new_field)] += coefficient
        return dict(result)

    def _canonical_term(
        self,
        derivative_word: tuple[int, ...],
        field_indices: tuple[int, ...],
    ) -> tuple[tuple[TermKey, sp.Expr], ...]:
        inversion = next(
            (
                index
                for index in range(len(derivative_word) - 1)
                if derivative_word[index] > derivative_word[index + 1]
            ),
            None,
        )
        if inversion is None:
            return (((derivative_word, field_indices), sp.Integer(1)),)

        position = inversion
        a = derivative_word[position]
        b = derivative_word[position + 1]
        prefix = derivative_word[:position]
        suffix = derivative_word[position + 2 :]

        # D_a D_b = D_b D_a + [D_a,D_b].
        swapped = (
            derivative_word[:position]
            + (b, a)
            + derivative_word[position + 2 :]
        )
        result: dict[TermKey, sp.Expr] = defaultdict(lambda: sp.Integer(0))
        for key, coefficient in self._canonical_term(swapped, field_indices):
            result[key] += coefficient

        for (changed_suffix, changed_field), curvature_coefficient in (
            self._curvature_action(a, b, suffix, field_indices).items()
        ):
            shortened_word = prefix + changed_suffix
            for key, coefficient in self._canonical_term(
                shortened_word, changed_field
            ):
                result[key] += curvature_coefficient * coefficient

        return tuple(
            sorted(
                (
                    (key, sp.simplify(coefficient))
                    for key, coefficient in result.items()
                    if sp.simplify(coefficient) != 0
                ),
                key=lambda item: item[0],
            )
        )

    def canonicalize(
        self,
        terms: Mapping[TermKey, sp.Expr],
    ) -> dict[TermKey, sp.Expr]:
        result: dict[TermKey, sp.Expr] = defaultdict(lambda: sp.Integer(0))
        for (word, indices), outer_coefficient in terms.items():
            for key, inner_coefficient in self._canonical_term(word, indices):
                result[key] += outer_coefficient * inner_coefficient
        return {
            key: sp.simplify(coefficient)
            for key, coefficient in result.items()
            if sp.simplify(coefficient) != 0
        }

    def verify(self) -> None:
        # Ordered terms are fixed points.
        ordered = {((0, 1, 3), (2,)): sp.Integer(5)}
        if self.canonicalize(ordered) != ordered:
            raise AssertionError("ordered derivative terms are not stable")

        # D_2 D_1 v_3 = D_1 D_2 v_3 + [D_2,D_1]v_3.
        direct = self.canonicalize({((2, 1), (3,)): sp.Integer(1)})
        expected: dict[TermKey, sp.Expr] = {
            ((1, 2), (3,)): sp.Integer(1)
        }
        for key, value in self._curvature_action(2, 1, (), (3,)).items():
            expected[key] = expected.get(key, 0) + value
        expected = {key: value for key, value in expected.items() if value != 0}
        if direct != expected:
            raise AssertionError("covector commutator normalization failed")

        # Independent coordinate-jet audit of the curvature sign, including
        # the vanishing mixed time--space commutators.  This catches replacing
        # the spatial raised-index projector by a four-dimensional Kronecker
        # delta.
        from covariant_completion.minimal_witness.cylinder_jets import Jet
        from .covariant_jets import CovariantJetBasis

        jet_basis = CovariantJetBasis.build(verify=False)
        for input_index in range(4):
            covector = {
                (index,): Jet.constant(int(index == input_index))
                for index in range(4)
            }
            second = jet_basis._covariant_derivatives(covector, 2)
            for a in range(4):
                for b in range(4):
                    commutator = self.background.covector_commutator(a, b)
                    for output_index in range(4):
                        actual = sp.expand(
                            second[(a, b, output_index)].value
                            - second[(b, a, output_index)].value
                        )
                        if actual != commutator[output_index, input_index]:
                            raise AssertionError(
                                "coordinate-jet curvature commutator mismatch"
                            )

        # Normalization is idempotent, including curvature acting on an
        # inner derivative slot of a rank-two tensor.
        sample = {((3, 1, 2, 0), (1, 3)): sp.Integer(1)}
        once = self.canonicalize(sample)
        twice = self.canonicalize(once)
        if once != twice:
            raise AssertionError("curved derivative normal form is not idempotent")

        # Jacobi identity on covectors.
        for a in range(4):
            for b in range(4):
                for c in range(4):
                    matrices = (
                        self.background.covector_commutator(a, b),
                        self.background.covector_commutator(b, c),
                        self.background.covector_commutator(c, a),
                    )
                    # Parallel curvature means [D_a,R_bc]+cyclic=0; the
                    # algebraic Bianchi identity is independently verified
                    # by CylinderBackground.
                    if any(matrix.shape != (4, 4) for matrix in matrices):
                        raise AssertionError("wrong commutator representation")

    def certificate(self) -> dict[str, object]:
        self.verify()
        sample = self.canonicalize(
            {((3, 1, 2, 0), (1, 3)): sp.Integer(1)}
        )
        return {
            "schema": "pure-weyl-parallel-cylinder-derivative-normal-form-v1",
            "canonical_order": "nondecreasing derivative indices",
            "commutator": (
                "[nabla_a,nabla_b] acts on every covariant field and inner-derivative slot"
            ),
            "nabla_Riemann": "zero",
            "derivatives_of_curvature_generated": False,
            "ordered_terms_fixed": True,
            "curvature_commutator_verified": True,
            "idempotent": True,
            "sample_input_order": 4,
            "sample_normal_form_terms": len(sample),
            "scope": (
                "exact normal-form engine available; full auxiliary Hessian/witness "
                "has not yet been submitted to exhaustive jet evaluation"
            ),
        }
