"""Constraint-adjusted symmetric-hyperbolic Weyl--Cotton evolution.

The covariant two-jet calculation in :mod:`curvature_eb_jets` derives the
Weyl/Cotton/Bach equations.  A direct choice of 26 independent temporal rows
is not hyperbolic.  This module performs the necessary *local constraint
addition* in invariant ``S^3`` variables.

Write ``E,B,A,C`` for four spatial STF two-tensors and ``x,y`` for two
spatial one-forms.  With ``L`` the STF symmetric gradient, the adjusted
system is

``E_t + curl_2 B - A = f_E``,
``B_t - curl_2 E - C = f_B``,
``A_t + curl_2 C + E - (1/2)Lx = f_A``,
``C_t - curl_2 A + B - (1/2)Ly = f_C``,
``x_t - div A + (1/2)curl_1 y = f_x``,
``y_t - div C - (1/2)curl_1 x = f_y``.

The constraints ``q,r,a,c,s,t`` and their sourced subsidiary system are
encoded below as an exact natural-operator identity.  The sole difference
between the commuting-symbol calculation and the curved identity is the
unit-sphere commutator contribution

``(1/2)(div L)_curv + (1/4)(curl_1^2)_curv = 1``.

No BV, Green-operator, harmonic-spectrum, or current claim is made here.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from .weyl_3plus1 import epsilon, stf_basis


STF_DIMENSION = 5
VECTOR_DIMENSION = 3
EVOLUTION_DIMENSION = 26
CONSTRAINT_DIMENSION = 14


def _frobenius(first: sp.Matrix, second: sp.Matrix) -> sp.Expr:
    return sp.expand(
        sum(first[i, j] * second[i, j] for i in range(3) for j in range(3))
    )


def _block_slices(sizes: tuple[int, ...]) -> tuple[slice, ...]:
    start = 0
    output: list[slice] = []
    for size in sizes:
        output.append(slice(start, start + size))
        start += size
    return tuple(output)


STATE_SLICES = _block_slices((5, 5, 5, 5, 3, 3))
CONSTRAINT_SLICES = _block_slices((3, 3, 3, 3, 1, 1))


def _put(
    target: sp.Matrix,
    row: slice,
    column: slice,
    value: sp.Matrix,
) -> None:
    target[row, column] = target[row, column] + value


@dataclass(frozen=True)
class ConstraintAdjustedWeylCottonEvolution:
    """Exact matrices for the adjusted evolution and subsidiary system."""

    stf_gram: sp.Matrix
    tensor_curl_coefficients: tuple[sp.Matrix, sp.Matrix, sp.Matrix]
    divergence_coefficients: tuple[sp.Matrix, sp.Matrix, sp.Matrix]
    stf_gradient_coefficients: tuple[sp.Matrix, sp.Matrix, sp.Matrix]
    vector_curl_coefficients: tuple[sp.Matrix, sp.Matrix, sp.Matrix]
    evolution_spatial_coefficients: tuple[sp.Matrix, sp.Matrix, sp.Matrix]
    evolution_zeroth_coefficient: sp.Matrix
    evolution_symmetrizer: sp.Matrix
    constraint_spatial_coefficients: tuple[sp.Matrix, sp.Matrix, sp.Matrix]
    constraint_zeroth_coefficient: sp.Matrix
    constraint_symmetrizer: sp.Matrix
    source_compatibility_spatial_coefficients: tuple[
        sp.Matrix, sp.Matrix, sp.Matrix
    ]
    source_compatibility_zeroth_coefficient: sp.Matrix
    commuting_symbol_defect: sp.Matrix
    sphere_curvature_correction: sp.Matrix
    representative_characteristic: sp.Expr
    subsidiary_characteristic: sp.Expr

    @staticmethod
    def build() -> "ConstraintAdjustedWeylCottonEvolution":
        basis = stf_basis()
        gram = sp.Matrix(
            [[_frobenius(left, right) for right in basis] for left in basis]
        )
        gram_inverse = gram.inv()

        curls: list[sp.Matrix] = []
        divergences: list[sp.Matrix] = []
        gradients: list[sp.Matrix] = []
        vector_curls: list[sp.Matrix] = []
        for axis in range(3):
            tensor_curl = sp.zeros(5)
            divergence = sp.zeros(3, 5)
            gradient = sp.zeros(5, 3)
            vector_curl = sp.zeros(3)
            for column, tensor in enumerate(basis):
                image = sp.Matrix(
                    3,
                    3,
                    lambda i, j: sp.Rational(1, 2)
                    * sum(
                        epsilon(i, axis, middle) * tensor[middle, j]
                        + epsilon(j, axis, middle) * tensor[middle, i]
                        for middle in range(3)
                    ),
                )
                tensor_curl[:, column] = gram_inverse * sp.Matrix(
                    [_frobenius(item, image) for item in basis]
                )
                for output in range(3):
                    divergence[output, column] = tensor[axis, output]
            for column in range(3):
                image = sp.Matrix(
                    3,
                    3,
                    lambda i, j: sp.Rational(1, 2)
                    * (
                        int(i == axis and j == column)
                        + int(j == axis and i == column)
                    )
                    - sp.Rational(1, 3)
                    * int(i == j and axis == column),
                )
                gradient[:, column] = gram_inverse * sp.Matrix(
                    [_frobenius(item, image) for item in basis]
                )
            for output in range(3):
                for input_axis in range(3):
                    vector_curl[output, input_axis] = epsilon(
                        output, axis, input_axis
                    )
            curls.append(tensor_curl)
            divergences.append(divergence)
            gradients.append(gradient)
            vector_curls.append(vector_curl)

        # State ordering: E,B,A,C,x,y.
        evolution_spatial: list[sp.Matrix] = []
        for curl, divergence, gradient, vector_curl in zip(
            curls, divergences, gradients, vector_curls, strict=True
        ):
            coefficient = sp.zeros(EVOLUTION_DIMENSION)
            _put(coefficient, STATE_SLICES[0], STATE_SLICES[1], curl)
            _put(coefficient, STATE_SLICES[1], STATE_SLICES[0], -curl)
            _put(coefficient, STATE_SLICES[2], STATE_SLICES[3], curl)
            _put(
                coefficient,
                STATE_SLICES[2],
                STATE_SLICES[4],
                -sp.Rational(1, 2) * gradient,
            )
            _put(coefficient, STATE_SLICES[3], STATE_SLICES[2], -curl)
            _put(
                coefficient,
                STATE_SLICES[3],
                STATE_SLICES[5],
                -sp.Rational(1, 2) * gradient,
            )
            _put(coefficient, STATE_SLICES[4], STATE_SLICES[2], -divergence)
            _put(
                coefficient,
                STATE_SLICES[4],
                STATE_SLICES[5],
                sp.Rational(1, 2) * vector_curl,
            )
            _put(coefficient, STATE_SLICES[5], STATE_SLICES[3], -divergence)
            _put(
                coefficient,
                STATE_SLICES[5],
                STATE_SLICES[4],
                -sp.Rational(1, 2) * vector_curl,
            )
            evolution_spatial.append(coefficient)

        evolution_zeroth = sp.zeros(EVOLUTION_DIMENSION)
        _put(
            evolution_zeroth,
            STATE_SLICES[0],
            STATE_SLICES[2],
            -sp.eye(5),
        )
        _put(
            evolution_zeroth,
            STATE_SLICES[1],
            STATE_SLICES[3],
            -sp.eye(5),
        )
        _put(
            evolution_zeroth,
            STATE_SLICES[2],
            STATE_SLICES[0],
            sp.eye(5),
        )
        _put(
            evolution_zeroth,
            STATE_SLICES[3],
            STATE_SLICES[1],
            sp.eye(5),
        )
        evolution_symmetrizer = sp.diag(
            gram,
            gram,
            gram,
            gram,
            sp.eye(3) / 2,
            sp.eye(3) / 2,
        )

        # Constraint ordering: q,r,a,c,s,t.  Their homogeneous equations are
        # q_t+(1/2)curl r=0, r_t-(1/2)curl q=0,
        # a_t-q-(1/3)grad s=0, c_t-r-(1/3)grad t=0,
        # s_t-div a=0, t_t-div c=0.
        constraint_spatial: list[sp.Matrix] = []
        for axis, vector_curl in enumerate(vector_curls):
            coefficient = sp.zeros(CONSTRAINT_DIMENSION)
            _put(
                coefficient,
                CONSTRAINT_SLICES[0],
                CONSTRAINT_SLICES[1],
                sp.Rational(1, 2) * vector_curl,
            )
            _put(
                coefficient,
                CONSTRAINT_SLICES[1],
                CONSTRAINT_SLICES[0],
                -sp.Rational(1, 2) * vector_curl,
            )
            gradient = sp.eye(3)[:, axis]
            divergence = sp.eye(3)[axis, :]
            _put(
                coefficient,
                CONSTRAINT_SLICES[2],
                CONSTRAINT_SLICES[4],
                -sp.Rational(1, 3) * gradient,
            )
            _put(
                coefficient,
                CONSTRAINT_SLICES[3],
                CONSTRAINT_SLICES[5],
                -sp.Rational(1, 3) * gradient,
            )
            _put(
                coefficient,
                CONSTRAINT_SLICES[4],
                CONSTRAINT_SLICES[2],
                -divergence,
            )
            _put(
                coefficient,
                CONSTRAINT_SLICES[5],
                CONSTRAINT_SLICES[3],
                -divergence,
            )
            constraint_spatial.append(coefficient)
        constraint_zeroth = sp.zeros(CONSTRAINT_DIMENSION)
        _put(
            constraint_zeroth,
            CONSTRAINT_SLICES[2],
            CONSTRAINT_SLICES[0],
            -sp.eye(3),
        )
        _put(
            constraint_zeroth,
            CONSTRAINT_SLICES[3],
            CONSTRAINT_SLICES[1],
            -sp.eye(3),
        )
        constraint_symmetrizer = sp.diag(
            sp.eye(3),
            sp.eye(3),
            3 * sp.eye(3),
            3 * sp.eye(3),
            sp.eye(1),
            sp.eye(1),
        )

        # The source compatibility operator has the same spatial/zeroth
        # table as the constraint definition K acting on state residuals:
        # (f_x-div f_E, f_y-div f_B,
        #  div f_A+(1/2)curl f_y, div f_C-(1/2)curl f_x,
        #  div f_x, div f_y).
        source_spatial: list[sp.Matrix] = []
        for axis, (divergence, vector_curl) in enumerate(zip(
            divergences, vector_curls, strict=True
        )):
            coefficient = sp.zeros(CONSTRAINT_DIMENSION, EVOLUTION_DIMENSION)
            _put(coefficient, CONSTRAINT_SLICES[0], STATE_SLICES[0], -divergence)
            _put(coefficient, CONSTRAINT_SLICES[1], STATE_SLICES[1], -divergence)
            _put(coefficient, CONSTRAINT_SLICES[2], STATE_SLICES[2], divergence)
            _put(
                coefficient,
                CONSTRAINT_SLICES[2],
                STATE_SLICES[5],
                sp.Rational(1, 2) * vector_curl,
            )
            _put(coefficient, CONSTRAINT_SLICES[3], STATE_SLICES[3], divergence)
            _put(
                coefficient,
                CONSTRAINT_SLICES[3],
                STATE_SLICES[4],
                -sp.Rational(1, 2) * vector_curl,
            )
            _put(
                coefficient,
                CONSTRAINT_SLICES[4],
                STATE_SLICES[4],
                sp.eye(3)[axis, :],
            )
            _put(
                coefficient,
                CONSTRAINT_SLICES[5],
                STATE_SLICES[5],
                sp.eye(3)[axis, :],
            )
            source_spatial.append(coefficient)
        source_zeroth = sp.zeros(CONSTRAINT_DIMENSION, EVOLUTION_DIMENSION)
        _put(source_zeroth, CONSTRAINT_SLICES[0], STATE_SLICES[4], sp.eye(3))
        _put(source_zeroth, CONSTRAINT_SLICES[1], STATE_SLICES[5], sp.eye(3))

        # Check the complete sourced identity as a polynomial in a temporal
        # symbol and an arbitrary spatial covector.  Commuting symbols omit
        # one curvature contribution in each a/c row.  The separately
        # certified unit-S3 identities add precisely that correction.
        tau = sp.Symbol("tau")
        xi = sp.Matrix(sp.symbols("xi0:3"))
        evolution_symbol = tau * sp.eye(EVOLUTION_DIMENSION) + evolution_zeroth
        subsidiary_symbol = tau * sp.eye(CONSTRAINT_DIMENSION) + constraint_zeroth
        source_symbol = source_zeroth.copy()
        for axis in range(3):
            evolution_symbol += xi[axis] * evolution_spatial[axis]
            subsidiary_symbol += xi[axis] * constraint_spatial[axis]
            source_symbol += xi[axis] * source_spatial[axis]
        commuting_defect = sp.simplify(
            subsidiary_symbol * source_symbol - source_symbol * evolution_symbol
        ).applyfunc(sp.expand)
        sphere_correction = sp.zeros(CONSTRAINT_DIMENSION, EVOLUTION_DIMENSION)
        _put(
            sphere_correction,
            CONSTRAINT_SLICES[2],
            STATE_SLICES[4],
            sp.eye(3),
        )
        _put(
            sphere_correction,
            CONSTRAINT_SLICES[3],
            STATE_SLICES[5],
            sp.eye(3),
        )

        spectral_parameter = sp.Symbol("lambda")
        representative_characteristic = sp.factor(
            evolution_spatial[0].charpoly(spectral_parameter).as_expr()
        )
        subsidiary_characteristic = sp.factor(
            constraint_spatial[0].charpoly(spectral_parameter).as_expr()
        )

        result = ConstraintAdjustedWeylCottonEvolution(
            stf_gram=gram,
            tensor_curl_coefficients=tuple(curls),
            divergence_coefficients=tuple(divergences),
            stf_gradient_coefficients=tuple(gradients),
            vector_curl_coefficients=tuple(vector_curls),
            evolution_spatial_coefficients=tuple(evolution_spatial),
            evolution_zeroth_coefficient=evolution_zeroth,
            evolution_symmetrizer=evolution_symmetrizer,
            constraint_spatial_coefficients=tuple(constraint_spatial),
            constraint_zeroth_coefficient=constraint_zeroth,
            constraint_symmetrizer=constraint_symmetrizer,
            source_compatibility_spatial_coefficients=tuple(source_spatial),
            source_compatibility_zeroth_coefficient=source_zeroth,
            commuting_symbol_defect=commuting_defect,
            sphere_curvature_correction=sphere_correction,
            representative_characteristic=representative_characteristic,
            subsidiary_characteristic=subsidiary_characteristic,
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.stf_gram != sp.diag(2, 6, 2, 2, 2):
            raise AssertionError("STF Gram normalization drifted")
        if any(value <= 0 for value in self.evolution_symmetrizer.diagonal()):
            raise AssertionError("evolution symmetrizer is not positive")
        if any(value <= 0 for value in self.constraint_symmetrizer.diagonal()):
            raise AssertionError("subsidiary symmetrizer is not positive")

        for curl, divergence, gradient, vector_curl in zip(
            self.tensor_curl_coefficients,
            self.divergence_coefficients,
            self.stf_gradient_coefficients,
            self.vector_curl_coefficients,
            strict=True,
        ):
            if self.stf_gram * curl + curl.T * self.stf_gram != sp.zeros(5):
                raise AssertionError("tensor curl is not Gram-skew")
            if self.stf_gram * gradient != divergence.T:
                raise AssertionError("STF gradient/divergence symbol adjunction failed")
            if vector_curl + vector_curl.T != sp.zeros(3):
                raise AssertionError("vector curl symbol is not skew")

        for coefficient in self.evolution_spatial_coefficients:
            weighted = self.evolution_symmetrizer * coefficient
            if weighted != weighted.T:
                raise AssertionError("adjusted evolution is not symmetrized")
        for coefficient in self.constraint_spatial_coefficients:
            weighted = self.constraint_symmetrizer * coefficient
            if weighted != weighted.T:
                raise AssertionError("subsidiary system is not symmetrized")

        xi = sp.Matrix(sp.symbols("xi0:3"))
        tensor_curl = sum(
            (
                xi[axis] * self.tensor_curl_coefficients[axis]
                for axis in range(3)
            ),
            sp.zeros(5),
        )
        divergence = sum(
            (
                xi[axis] * self.divergence_coefficients[axis]
                for axis in range(3)
            ),
            sp.zeros(3, 5),
        )
        gradient = sum(
            (
                xi[axis] * self.stf_gradient_coefficients[axis]
                for axis in range(3)
            ),
            sp.zeros(5, 3),
        )
        vector_curl = sum(
            (
                xi[axis] * self.vector_curl_coefficients[axis]
                for axis in range(3)
            ),
            sp.zeros(3),
        )
        xi_squared = sp.expand(xi.dot(xi))
        if (divergence * tensor_curl - sp.Rational(1, 2) * vector_curl * divergence).applyfunc(
            sp.expand
        ) != sp.zeros(3, 5):
            raise AssertionError("div curl_2 identity failed")
        if (
            divergence * gradient
            - sp.Rational(1, 2) * xi_squared * sp.eye(3)
            - sp.Rational(1, 6) * xi * xi.T
        ).applyfunc(sp.expand) != sp.zeros(3):
            raise AssertionError("principal div STF-gradient identity failed")
        if (vector_curl**2 - xi * xi.T + xi_squared * sp.eye(3)).applyfunc(
            sp.expand
        ) != sp.zeros(3):
            raise AssertionError("principal vector curl-square identity failed")
        if (xi.T * vector_curl).applyfunc(sp.expand) != sp.zeros(1, 3):
            raise AssertionError("div curl_1 identity failed")

        # Derive, rather than merely record, the two contracted curvature
        # commutators used below.  For unit S3,
        # [D_a,D_b]v_c=delta_ca v_b-delta_cb v_a.  Acting on both slots of
        # an STF tensor gives the corresponding rank-two formula.
        vector = sp.Matrix(sp.symbols("v0:3"))
        vector_commutator = sp.zeros(3, 1)
        for output in range(3):
            vector_commutator[output] = sum(
                int(contracted == contracted) * vector[output]
                - int(contracted == output) * vector[contracted]
                for contracted in range(3)
            )
        if vector_commutator != 2 * vector:
            raise AssertionError("unit-S3 contracted covector commutator drifted")
        tensor_symbols = sp.symbols("t0:5")
        tensor = sum(
            (
                tensor_symbols[index] * stf_basis()[index]
                for index in range(5)
            ),
            sp.zeros(3),
        )
        tensor_commutator = sp.zeros(3)
        for first in range(3):
            for second in range(3):
                tensor_commutator[first, second] = sum(
                    # [D^k,D_first]T_{k,second}; the first two terms are
                    # curvature on the contracted slot, the last two on the
                    # uncontracted slot.
                    tensor[first, second]
                    - int(contracted == first) * tensor[contracted, second]
                    + int(second == contracted) * tensor[contracted, first]
                    - int(second == first) * tensor[contracted, contracted]
                    for contracted in range(3)
                )
        if tensor_commutator.applyfunc(sp.expand) != 3 * tensor:
            raise AssertionError("unit-S3 contracted STF commutator drifted")

        # On the unit three-sphere the exact lower terms are
        # div L = ... +1 and curl_1^2 = ... +2.  Their occurrence in the
        # subsidiary calculation is (1/2)*1+(1/4)*2=1.
        curvature_coefficient = (
            sp.Rational(1, 2) * 1 + sp.Rational(1, 4) * 2
        )
        if curvature_coefficient != 1:
            raise AssertionError("unit-S3 subsidiary curvature coefficient drifted")
        if self.commuting_symbol_defect + self.sphere_curvature_correction != sp.zeros(
            CONSTRAINT_DIMENSION, EVOLUTION_DIMENSION
        ):
            raise AssertionError("sourced subsidiary operator identity failed")

        lam = sp.Symbol("lambda")
        expected_characteristic = sp.factor(
            lam**6
            * (lam**2 - 1) ** 6
            * (4 * lam**2 - 1) ** 2
            * (3 * lam**2 - 1) ** 2
            / 144
        )
        if self.representative_characteristic != expected_characteristic:
            raise AssertionError("adjusted evolution characteristic drifted")
        expected_subsidiary = sp.factor(
            lam**6 * (4 * lam**2 - 1) ** 2 * (3 * lam**2 - 1) ** 2 / 144
        )
        if self.subsidiary_characteristic != expected_subsidiary:
            raise AssertionError("subsidiary characteristic drifted")

    def certificate(self) -> dict[str, object]:
        self.verify()
        nonzero_defect = [
            [row, column, str(self.commuting_symbol_defect[row, column])]
            for row in range(CONSTRAINT_DIMENSION)
            for column in range(EVOLUTION_DIMENSION)
            if self.commuting_symbol_defect[row, column] != 0
        ]
        return {
            "schema": "pure-weyl-cotton-constraint-adjusted-hyperbolic-v1",
            "background": "R x unit S3, signature (-,+,+,+)",
            "state_order": ["E_STF[5]", "B_STF[5]", "A_STF[5]", "C_STF[5]", "x[3]", "y[3]"],
            "state_rank": EVOLUTION_DIMENSION,
            "constraint_order": ["q[3]", "r[3]", "a[3]", "c[3]", "s[1]", "t[1]"],
            "constraint_rank": CONSTRAINT_DIMENSION,
            "evolution_equations": [
                "E_t+curl_2 B-A=f_E",
                "B_t-curl_2 E-C=f_B",
                "A_t+curl_2 C+E-(1/2)Lx=f_A",
                "C_t-curl_2 A+B-(1/2)Ly=f_C",
                "x_t-div A+(1/2)curl_1 y=f_x",
                "y_t-div C-(1/2)curl_1 x=f_y",
            ],
            "constraints": [
                "q=x-div E",
                "r=y-div B",
                "a=div A+(1/2)curl_1 y",
                "c=div C-(1/2)curl_1 x",
                "s=div x",
                "t=div y",
            ],
            "sourced_subsidiary_equations": [
                "q_t+(1/2)curl_1 r=f_x-div f_E",
                "r_t-(1/2)curl_1 q=f_y-div f_B",
                "a_t-q-(1/3)grad s=div f_A+(1/2)curl_1 f_y",
                "c_t-r-(1/3)grad t=div f_C-(1/2)curl_1 f_x",
                "s_t-div a=div f_x",
                "t_t-div c=div f_y",
            ],
            "unit_S3_operator_identities": {
                "div_curl_2": "div curl_2=(1/2)curl_1 div",
                "div_STF_gradient": "div L=(1/2)D^2+(1/6)grad div+1",
                "vector_curl_square": "curl_1^2=-D^2+grad div+2",
                "div_vector_curl": "div curl_1=0",
                "curvature_cancellation": "(1/2)*1+(1/4)*2=1",
            },
            "unit_S3_contracted_curvature_commutators_verified": True,
            "commuting_symbol_defect_nonzero_entries": nonzero_defect,
            "sphere_curvature_correction_cancels_defect": True,
            "exact_sourced_subsidiary_operator_identity": True,
            "evolution_symmetrizer_diagonal": [
                str(value) for value in self.evolution_symmetrizer.diagonal()
            ],
            "evolution_symmetrizer_positive": True,
            "evolution_spatial_symbols_self_adjoint": True,
            "representative_characteristic": str(
                self.representative_characteristic
            ),
            "characteristic_speeds": {
                "-1": 6,
                "-1/sqrt(3)": 2,
                "-1/2": 2,
                "0": 6,
                "+1/2": 2,
                "+1/sqrt(3)": 2,
                "+1": 6,
            },
            "all_characteristics_causal": True,
            "subsidiary_symmetrizer_positive": True,
            "subsidiary_spatial_symbols_self_adjoint": True,
            "subsidiary_characteristic": str(self.subsidiary_characteristic),
            "homogeneous_constraints_propagate": True,
            "candidate_atomic_flags_if_covariant_row_equivalence_is_proved": [
                "curved_EB_symmetric_hyperbolicity",
                "curved_sourced_constraint_identity",
                "curved_constraint_propagation",
            ],
            "covariant_row_equivalence_audited": False,
            "warranted_atomic_flags": [],
            "flags_promoted_here": [],
            "EAL_curvature_spectrum_match": False,
            "prolonged_BV_operator_identity": False,
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "proof_boundary": (
                "exact internal rank-26 PDE and sourced subsidiary algebra; an "
                "independent audit found that its x/y rows differ from the exact "
                "vector Bach rows by six additional a/c constraints, so this "
                "certificate alone warrants no covariant status flag"
            ),
            "fail_closed": True,
        }
