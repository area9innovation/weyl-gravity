"""Exact action-level current comparison for the auxiliary realization.

This module deliberately separates two statements which are easy to conflate.

* The ordinary-derivative auxiliary action and its differential auxiliary
  elimination determine exact constant-coefficient (Fourier-polynomial)
  Green currents.  Their difference is an explicitly constructed spatial
  improvement on a Cauchy slice.
* The same statement for the complete curved cylinder actions requires the
  first- and zeroth-order connection/curvature terms in both presymplectic
  potentials.  Those data are not reconstructed here, so the curved-current
  theorem flag remains false.

The polynomial construction is useful rather than cosmetic: it fixes the
current convention, verifies that the cotangent lift is BV canonical, and
provides the exact comparison algorithm to which the curved coefficients must
be supplied.  No mode fit or final Gram matrix is used as a substitute for an
off-shell current identity.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import sympy as sp

from covariant_completion.auxiliary_equivalence import GeneralizedAuxiliaryRetract
from covariant_completion.curved_retract import CurvedAuxiliaryEOMShift
from covariant_completion.symplectic import BranchResidues


DIMENSION = 4


def _digest_matrices(matrices: tuple[sp.Matrix, ...]) -> str:
    payload = sp.srepr(
        tuple(sp.ImmutableDenseMatrix(matrix) for matrix in matrices)
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _matrix_polynomial_degree(
    matrices: tuple[sp.Matrix, ...], variables: tuple[sp.Symbol, ...]
) -> int:
    degree = 0
    for matrix in matrices:
        for entry in matrix:
            if entry != 0:
                degree = max(degree, sp.Poly(sp.expand(entry), *variables).total_degree())
    return degree


def _substitute_matrix(
    matrix: sp.MatrixBase,
    source: tuple[sp.Symbol, ...],
    target: tuple[sp.Expr, ...],
) -> sp.Matrix:
    return sp.Matrix(matrix).subs(dict(zip(source, target)), simultaneous=True)


def _integrate_polynomial_in_t(expression: sp.Expr, t: sp.Symbol) -> sp.Expr:
    polynomial = sp.Poly(sp.expand(expression), t)
    result = sp.Integer(0)
    for (power,), coefficient in polynomial.terms():
        result += coefficient / sp.Integer(power + 1)
    return sp.expand(result)


def canonical_green_current(
    operator: sp.MatrixBase,
    covector: tuple[sp.Symbol, ...],
    left_covector: tuple[sp.Symbol, ...],
    right_covector: tuple[sp.Symbol, ...],
) -> tuple[sp.Matrix, ...]:
    """Return the canonical polynomial Green current of ``operator``.

    For a (possibly rectangular) polynomial differential symbol ``A(z)``,
    the returned matrices satisfy

    ``sum_mu (x_mu+y_mu) J^mu(x,y) = A(y)-A(-x)``.

    This is the integrated straight-line divided difference from ``-x`` to
    ``y``.  It is coordinate covariant at symbol level and works at arbitrary
    finite differential order.
    """

    if not (
        len(covector) == len(left_covector) == len(right_covector) == DIMENSION
    ):
        raise ValueError("the current implementation expects four covector components")
    t = sp.symbols("current_homotopy_t", real=True)
    path = tuple(
        -left_covector[index]
        + t * (left_covector[index] + right_covector[index])
        for index in range(DIMENSION)
    )
    result: list[sp.Matrix] = []
    for mu in range(DIMENSION):
        derivative = sp.Matrix(operator).diff(covector[mu])
        along_path = _substitute_matrix(derivative, covector, path)
        current = along_path.applyfunc(
            lambda entry: _integrate_polynomial_in_t(entry, t)
        )
        result.append(sp.Matrix(current))
    return tuple(result)


def _current_divergence(
    current: tuple[sp.Matrix, ...],
    left_covector: tuple[sp.Symbol, ...],
    right_covector: tuple[sp.Symbol, ...],
) -> sp.Matrix:
    return sp.Matrix(
        sum(
            (
                (left_covector[mu] + right_covector[mu]) * current[mu]
                for mu in range(DIMENSION)
            ),
            sp.zeros(*current[0].shape),
        )
    ).applyfunc(sp.expand)


def _composition_current(
    operator: sp.Matrix,
    inclusion: sp.Matrix,
    covector: tuple[sp.Symbol, ...],
    left_covector: tuple[sp.Symbol, ...],
    right_covector: tuple[sp.Symbol, ...],
) -> tuple[sp.Matrix, ...]:
    """Green current obtained before eliminating a differential auxiliary.

    The metric Hessian is ``A^sharp E A``.  Applying Green's identity first
    to ``A^sharp``, then to ``E``, then to ``A`` gives this three-term
    current.  This is the precise current pulled through a derivative field
    redefinition; merely substituting ``A h`` into the middle current would
    omit the two chain-rule boundary terms.
    """

    negative = tuple(-component for component in covector)
    inclusion_sharp = _substitute_matrix(
        inclusion, covector, negative
    ).T
    current_left = canonical_green_current(
        inclusion_sharp, covector, left_covector, right_covector
    )
    current_operator = canonical_green_current(
        operator, covector, left_covector, right_covector
    )
    current_right = canonical_green_current(
        inclusion, covector, left_covector, right_covector
    )

    a_x = _substitute_matrix(inclusion, covector, left_covector)
    a_y = _substitute_matrix(inclusion, covector, right_covector)
    e_minus_x = _substitute_matrix(
        operator, covector, tuple(-component for component in left_covector)
    )
    e_y = _substitute_matrix(operator, covector, right_covector)
    return tuple(
        sp.Matrix(
            current_left[mu] * e_y * a_y
            + a_x.T * current_operator[mu] * a_y
            + a_x.T * e_minus_x * current_right[mu]
        ).applyfunc(sp.expand)
        for mu in range(DIMENSION)
    )


def _koszul_improvement(
    closed_current: tuple[sp.Matrix, ...],
    left_covector: tuple[sp.Symbol, ...],
    right_covector: tuple[sp.Symbol, ...],
) -> tuple[tuple[sp.Matrix, ...], ...]:
    """Construct ``B^{nu mu}=-B^{mu nu}`` with ``J^mu=s_nu B^{nu mu}``.

    Here ``s=x+y`` is the divergence covector.  The formula is the polynomial
    Koszul homotopy, applied separately to each homogeneous degree in ``s``.
    """

    s = tuple(sp.symbols("current_sum_0:4", real=True))
    to_sum = {
        right_covector[index]: s[index] - left_covector[index]
        for index in range(DIMENSION)
    }
    current_s = tuple(
        matrix.subs(to_sum, simultaneous=True).applyfunc(sp.expand)
        for matrix in closed_current
    )
    scale = sp.symbols("current_sum_scale", real=True)

    homogeneous: list[list[sp.Matrix]] = [
        [sp.zeros(*closed_current[0].shape) for _ in range(4)] for _ in range(5)
    ]
    maximum_degree = 0
    for mu in range(DIMENSION):
        scaled = current_s[mu].subs(
            {s[index]: scale * s[index] for index in range(DIMENSION)},
            simultaneous=True,
        )
        for row in range(scaled.rows):
            for column in range(scaled.cols):
                polynomial = sp.Poly(sp.expand(scaled[row, column]), scale)
                for (degree,), coefficient in polynomial.terms():
                    maximum_degree = max(maximum_degree, degree)
                    while degree >= len(homogeneous):
                        homogeneous.append(
                            [sp.zeros(*closed_current[0].shape) for _ in range(4)]
                        )
                    homogeneous[degree][mu][row, column] = coefficient

    improvement: list[list[sp.Matrix]] = [
        [sp.zeros(*closed_current[0].shape) for _ in range(4)]
        for _ in range(4)
    ]
    for degree in range(maximum_degree + 1):
        for nu in range(DIMENSION):
            for mu in range(DIMENSION):
                improvement[nu][mu] += (
                    homogeneous[degree][mu].diff(s[nu])
                    - homogeneous[degree][nu].diff(s[mu])
                ) / sp.Integer(degree + 1)

    # Return in the original (x,y) variables.
    from_sum = {
        s[index]: left_covector[index] + right_covector[index]
        for index in range(DIMENSION)
    }
    return tuple(
        tuple(
            matrix.subs(from_sum, simultaneous=True).applyfunc(sp.expand)
            for matrix in row
        )
        for row in improvement
    )


@dataclass(frozen=True)
class ActionCurrentComparison:
    """Exact Fourier-action comparison plus fail-closed curved status."""

    retract: GeneralizedAuxiliaryRetract
    left_covector: tuple[sp.Symbol, ...]
    right_covector: tuple[sp.Symbol, ...]
    metric_inclusion: sp.Matrix
    metric_hessian: sp.Matrix
    auxiliary_current: tuple[sp.Matrix, ...]
    metric_current: tuple[sp.Matrix, ...]
    composite_current: tuple[sp.Matrix, ...]
    current_difference: tuple[sp.Matrix, ...]
    improvement: tuple[tuple[sp.Matrix, ...], ...]
    bv_pairing: sp.Matrix

    @staticmethod
    def build() -> "ActionCurrentComparison":
        retract = GeneralizedAuxiliaryRetract.build()
        system = retract.system
        zeta = tuple(system.covector)
        left = tuple(sp.symbols("current_left_0:4", real=True))
        right = tuple(sp.symbols("current_right_0:4", real=True))

        # Restrict the exact shifted auxiliary inclusion to the ten metric
        # coordinates: (h,f_hat=0,v=0) -> (h,f(h),0).
        metric_inclusion = sp.Matrix(retract.field_new_to_old[:, :10])
        negative = tuple(-component for component in zeta)
        inclusion_sharp = _substitute_matrix(
            metric_inclusion, zeta, negative
        ).T
        metric_hessian = sp.Matrix(
            inclusion_sharp
            * system.gauge_invariant_flat_hessian
            * metric_inclusion
        ).applyfunc(sp.expand)

        auxiliary_current = canonical_green_current(
            system.gauge_invariant_flat_hessian, zeta, left, right
        )
        metric_current = canonical_green_current(
            metric_hessian, zeta, left, right
        )
        composite_current = _composition_current(
            system.gauge_invariant_flat_hessian,
            metric_inclusion,
            zeta,
            left,
            right,
        )
        current_difference = tuple(
            sp.Matrix(composite_current[mu] - metric_current[mu]).applyfunc(
                sp.expand
            )
            for mu in range(DIMENSION)
        )
        improvement = _koszul_improvement(current_difference, left, right)

        # Symmetric presentation of the odd cotangent pairing.  Graded signs
        # live in the degree convention; this matrix tests the exact inverse
        # formal-transpose lift used by the four-row transformation.
        j = system.field_fibre_pairing
        y = system.gauge_fixing_pairing
        bv_pairing = sp.zeros(66)
        bv_pairing[0:9, 57:66] = y
        bv_pairing[57:66, 0:9] = y
        bv_pairing[9:33, 33:57] = j
        bv_pairing[33:57, 9:33] = j

        result = ActionCurrentComparison(
            retract=retract,
            left_covector=left,
            right_covector=right,
            metric_inclusion=metric_inclusion,
            metric_hessian=metric_hessian,
            auxiliary_current=auxiliary_current,
            metric_current=metric_current,
            composite_current=composite_current,
            current_difference=current_difference,
            improvement=improvement,
            bv_pairing=bv_pairing,
        )
        result.verify()
        return result

    def verify(self) -> None:
        system = self.retract.system
        zeta = tuple(system.covector)
        left = self.left_covector
        right = self.right_covector
        negative_left = tuple(-component for component in left)

        e_y = _substitute_matrix(
            system.gauge_invariant_flat_hessian, zeta, right
        )
        e_minus_x = _substitute_matrix(
            system.gauge_invariant_flat_hessian, zeta, negative_left
        )
        if _current_divergence(self.auxiliary_current, left, right) != (
            e_y - e_minus_x
        ).applyfunc(sp.expand):
            raise AssertionError("the auxiliary action Green identity failed")

        metric_y = _substitute_matrix(self.metric_hessian, zeta, right)
        metric_minus_x = _substitute_matrix(
            self.metric_hessian, zeta, negative_left
        )
        expected_metric_divergence = (metric_y - metric_minus_x).applyfunc(
            sp.expand
        )
        if _current_divergence(
            self.metric_current, left, right
        ) != expected_metric_divergence:
            raise AssertionError("the metric action Green identity failed")
        if _current_divergence(
            self.composite_current, left, right
        ) != expected_metric_divergence:
            raise AssertionError("the differential pullback Green identity failed")
        if sp.simplify(
            _substitute_matrix(
                self.metric_hessian, zeta, tuple(-component for component in zeta)
            ).T
            - self.metric_hessian
        ) != sp.zeros(10):
            raise AssertionError("the eliminated metric Hessian is not formally self-adjoint")
        if _current_divergence(
            self.current_difference, left, right
        ) != sp.zeros(10):
            raise AssertionError("the current difference is not identically conserved")

        for nu in range(DIMENSION):
            if self.improvement[nu][nu] != sp.zeros(10):
                raise AssertionError("the current improvement is not antisymmetric")
            for mu in range(DIMENSION):
                if self.improvement[nu][mu] != -self.improvement[mu][nu]:
                    raise AssertionError("the current improvement is not antisymmetric")
        for mu in range(DIMENSION):
            reconstructed = sum(
                (
                    (left[nu] + right[nu]) * self.improvement[nu][mu]
                    for nu in range(DIMENSION)
                ),
                sp.zeros(10),
            ).applyfunc(sp.expand)
            if reconstructed != self.current_difference[mu]:
                raise AssertionError("the explicit current improvement is incomplete")

        # For mu=0 the antisymmetric B^{00} vanishes, so the Cauchy-current
        # difference is a spatial divergence exactly.
        cauchy_difference = sum(
            (
                (left[index] + right[index]) * self.improvement[index][0]
                for index in range(1, DIMENSION)
            ),
            sp.zeros(10),
        ).applyfunc(sp.expand)
        if cauchy_difference != self.current_difference[0]:
            raise AssertionError("the Cauchy-current difference is not spatially exact")

        # Exact formal BV-canonicality of the all-row cotangent lift.
        old_to_new = self.retract.total_new_to_old
        negative_covector = {
            component: -component for component in system.covector
        }
        canonical_defect = sp.simplify(
            old_to_new.subs(negative_covector).T
            * self.bv_pairing
            * old_to_new
            - self.bv_pairing
        )
        if canonical_defect != sp.zeros(66):
            raise AssertionError("the auxiliary shift is not BV canonical")

        BranchResidues().verify()
        CurvedAuxiliaryEOMShift.build().verify()

        if _matrix_polynomial_degree(
            (system.gauge_invariant_flat_hessian,), zeta
        ) != 2:
            raise AssertionError("the auxiliary action is not second order")
        if _matrix_polynomial_degree((self.metric_inclusion,), zeta) != 2:
            raise AssertionError("the differential auxiliary inclusion is not order two")
        if _matrix_polynomial_degree((self.metric_hessian,), zeta) != 4:
            raise AssertionError("the eliminated metric action is not fourth order")
        if _matrix_polynomial_degree(
            tuple(
                self.improvement[nu][mu]
                for nu in range(DIMENSION)
                for mu in range(DIMENSION)
            ),
            left + right,
        ) > 2:
            raise AssertionError("the current improvement exceeded differential order two")

    def certificate(self, *, reverify: bool = True) -> dict[str, object]:
        if reverify:
            self.verify()
        return {
            "schema": "pure-weyl-action-current-comparison-v1",
            "exact_action_level": {
                "auxiliary_green_identity": True,
                "metric_green_identity": True,
                "differential_pullback_green_identity": True,
                "current_difference_is_closed": True,
                "explicit_antisymmetric_improvement": True,
                "cauchy_difference_is_spatial_divergence": True,
                "auxiliary_shift_is_BV_canonical": True,
                "comparison_uses_minimal_action_before_gauge_fixing": True,
                "operator_orders": {
                    "auxiliary": 2,
                    "metric_after_elimination": 4,
                    "metric_inclusion": 2,
                    "current_improvement_at_most": 2,
                },
            },
            "exact_curved_algebraic_input": {
                "nonlinear_auxiliary_square_completed": True,
                "shift": "phi_hat=phi-A_g^{-1}G^b(g,b)",
                "pointwise_inverse": "A_g^{-1}(s)=-2s+(2/3)g tr_g(s)",
                "source_module": (
                    "covariant_completion.curved_retract.auxiliary_eom_shift"
                ),
                "scope": (
                    "exact curved zero-derivative auxiliary block; the curved "
                    "derivative current coefficients remain open"
                ),
            },
            "current_convention": (
                "straight-line polynomial Green current; differential pullback "
                "includes both chain-rule boundary terms"
            ),
            "cauchy_statement": (
                "the time-current difference is an exact spatial divergence; "
                "its integral vanishes on closed S^3 once the curved identity is supplied"
            ),
            "EAL_regression": {
                "derived_from_reduced_action": True,
                "families": ["E", "A", "L"],
                "chiralities": ["+", "-"],
                "krein_signs": {"E": 1, "A": -1, "L": -1},
                "all_energy_normalization": True,
                "role": "regression, not proof of the curved current identity",
            },
            "matrix_sha256": {
                "metric_inclusion": _digest_matrices((self.metric_inclusion,)),
                "metric_hessian": _digest_matrices((self.metric_hessian,)),
                "auxiliary_current": _digest_matrices(self.auxiliary_current),
                "metric_current": _digest_matrices(self.metric_current),
                "composite_current": _digest_matrices(self.composite_current),
                "current_difference": _digest_matrices(self.current_difference),
                "improvement": _digest_matrices(
                    tuple(
                        self.improvement[nu][mu]
                        for nu in range(DIMENSION)
                        for mu in range(DIMENSION)
                    )
                ),
                "bv_pairing": _digest_matrices((self.bv_pairing,)),
            },
            "curved_promotion_criteria": {
                "auxiliary_presymplectic_potential_derived": False,
                "metric_presymplectic_potential_derived": False,
                "pullback_difference_is_d_plus_Q": False,
                "cauchy_current_zero_on_cohomology": False,
                "Green_pairing_equals_current_pairing": False,
                "EAL_normalization_regression": True,
            },
            "curved_current_comparison": False,
            "theorem_boundary": (
                "the exact action/Fourier Green currents, BV-canonical cotangent "
                "lift, and explicit improvement are proved.  Promotion still "
                "requires both complete curved presymplectic potentials, their "
                "off-shell d+Q comparison, equality with the curved Green pairing, "
                "and the separately contractible gauge-fixing/nonminimal currents"
            ),
        }
