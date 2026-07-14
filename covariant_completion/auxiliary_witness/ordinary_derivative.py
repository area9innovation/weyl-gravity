"""Exact algebra for the local ordinary-derivative Weyl realization.

The four-dimensional field content is the Metsaev tensor--tensor--vector
system

``(h_ab, f_ab, v_a)``

with gauge parameters ``(xi_-2^a, xi_0^a, sigma)``.  The module checks three
facts needed by the Green-hyperbolic fallback:

* the modified de Donder gauge conditions have a triangular
  Faddeev--Popov symbol with scalar metric principal part;
* the complete flat-symbol Hessian of the ordinary-derivative action has the
  advertised gauge kernel;
* the modified de Donder gauge-fixing quadratic form is solved exactly and
  turns its degree-two part into a scalar wave symbol after a nondegenerate
  tensor/vector fibre pairing is used to identify fields and dual fields;
* the auxiliary tensor has an algebraically invertible equation and its
  support-local elimination returns ``Ric^2-R^2/3`` exactly.

The lower-order cylinder coefficients are defined by linearizing the
covariant ordinary-derivative action.  Their complete global reconstruction
and integration-by-parts adjoint check are intentionally certified in a
separate curved-operator layer.
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


def _digest(matrix: sp.MatrixBase) -> str:
    payload = sp.srepr(sp.ImmutableDenseMatrix(matrix)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class OrdinaryDerivativeWeylSystem:
    metric: sp.Matrix
    covector: sp.Matrix
    covector_up: sp.Matrix
    covector_square: sp.Expr
    tensor_basis: tuple[sp.Matrix, ...]
    tensor_pairing: sp.Matrix
    trace: sp.Matrix
    gauge_map: sp.Matrix
    gauge_condition: sp.Matrix
    ghost_operator: sp.Matrix
    linearized_einstein_operator: sp.Matrix
    maxwell_operator: sp.Matrix
    tensor_vector_mixing: sp.Matrix
    gauge_invariant_flat_hessian: sp.Matrix
    gauge_fixing_pairing: sp.Matrix
    gauge_fixed_flat_hessian: sp.Matrix
    field_fibre_pairing: sp.Matrix
    field_principal_symbol: sp.Matrix
    field_witness_operator: sp.Matrix
    auxiliary_mass_hessian: sp.Matrix

    @staticmethod
    def build() -> "OrdinaryDerivativeWeylSystem":
        metric = sp.diag(-1, 1, 1, 1)
        covector = sp.Matrix(sp.symbols("zeta_0:4", real=True))
        covector_up = metric * covector
        covector_square = sp.expand((covector.T * metric * covector)[0])

        tensor_basis: list[sp.Matrix] = []
        for mu, nu in SYMMETRIC_COORDINATES:
            tensor = sp.zeros(DIMENSION)
            tensor[mu, nu] = 1
            tensor[nu, mu] = 1
            tensor_basis.append(tensor)
        tensor_basis_tuple = tuple(tensor_basis)

        def tensor_coordinates(tensor: sp.Matrix) -> sp.Matrix:
            return sp.Matrix(
                [tensor[mu, nu] for mu, nu in SYMMETRIC_COORDINATES]
            )

        tensor_pairing = sp.Matrix(
            10,
            10,
            lambda row, column: sp.trace(
                metric
                * tensor_basis_tuple[row]
                * metric
                * tensor_basis_tuple[column]
            ),
        )
        trace = sp.Matrix(
            1,
            10,
            lambda _, column: sp.trace(metric * tensor_basis_tuple[column]),
        )

        # Ghost coordinates are (xi_-2[4], xi_0[4], sigma).
        # Field coordinates are (h[10], f[10], v[4]).
        gauge_map = sp.zeros(24, 9)
        for column in range(4):
            xi = sp.zeros(4, 1)
            xi[column] = 1
            h_image = covector * xi.T + xi * covector.T
            gauge_map[:10, column] = tensor_coordinates(h_image)

            eta = sp.zeros(4, 1)
            eta[column] = 1
            f_image = covector * eta.T + eta * covector.T
            gauge_map[10:20, 4 + column] = tensor_coordinates(f_image)
            gauge_map[20:24, 4 + column] = -eta

        gauge_map[:10, 8] = tensor_coordinates(metric)
        gauge_map[20:24, 8] = covector

        # Gauge conditions (C0_a,C2_a,C1), equations (5.50)-(5.51) in
        # four-dimensional component form.
        gauge_condition = sp.zeros(9, 24)
        for column, tensor in enumerate(tensor_basis_tuple):
            divergence = tensor * covector_up
            tensor_trace = sp.trace(metric * tensor)
            gauge_condition[:4, column] = (
                divergence - sp.Rational(1, 2) * covector * tensor_trace
            )
            gauge_condition[4:8, 10 + column] = (
                divergence - sp.Rational(1, 2) * covector * tensor_trace
            )
            gauge_condition[8, 10 + column] = sp.Rational(1, 2) * tensor_trace
        gauge_condition[:4, 20:24] = sp.eye(4)
        gauge_condition[8, 20:24] = covector_up.T

        ghost_operator = sp.simplify(gauge_condition * gauge_map)

        # Exact flat-symbol Hessian of the ordinary-derivative action.  Its
        # coefficients are fixed by gauge invariance in the present Fourier
        # and Lorentz-sign conventions:
        #
        #   1/2 f E_EH h + 1/2 v E_Max v
        #   + v.(delta f-d tr f) - f^2/4+(tr f)^2/4.
        #
        # Curvature completions on the cylinder are lower order and do not
        # change the normally-hyperbolic principal symbol certified here.
        linearized_einstein_operator = sp.zeros(10)
        for column, tensor in enumerate(tensor_basis_tuple):
            divergence = tensor * covector_up
            tensor_trace = sp.trace(metric * tensor)
            double_divergence = (covector_up.T * tensor * covector_up)[0]
            image = (
                covector_square * tensor
                - covector * divergence.T
                - divergence * covector.T
                + covector * covector.T * tensor_trace
                + metric
                * (double_divergence - covector_square * tensor_trace)
            )
            linearized_einstein_operator[:, column] = tensor_coordinates(image)
        einstein_hessian = sp.simplify(
            tensor_pairing * linearized_einstein_operator
        )

        maxwell_operator = sp.simplify(
            covector_square * sp.eye(4) - covector * covector_up.T
        )
        maxwell_hessian = sp.simplify(metric * maxwell_operator)

        tensor_vector_mixing = sp.zeros(4, 10)
        for column, tensor in enumerate(tensor_basis_tuple):
            tensor_vector_mixing[:, column] = (
                tensor * covector_up
                - covector * sp.trace(metric * tensor)
            )

        # Hessian of -f_ab f^ab/4+(tr f)^2/4.
        auxiliary_mass_hessian = (
            -sp.Rational(1, 2) * tensor_pairing
            + sp.Rational(1, 2) * trace.T * trace
        )

        gauge_invariant_flat_hessian = sp.zeros(24)
        gauge_invariant_flat_hessian[:10, 10:20] = (
            sp.Rational(1, 2) * einstein_hessian
        )
        gauge_invariant_flat_hessian[10:20, :10] = (
            sp.Rational(1, 2) * einstein_hessian.T
        )
        gauge_invariant_flat_hessian[20:24, 20:24] = maxwell_hessian
        vector_tensor_hessian = metric * tensor_vector_mixing
        gauge_invariant_flat_hessian[20:24, 10:20] = vector_tensor_hessian
        # The opposite sign is the integration-by-parts sign of the
        # first-order f--v mixing.  Consequently E(-zeta)^T=E(zeta), which
        # is the actual formal-adjoint identity; E(zeta)^T=E(zeta) would be
        # the wrong test for this odd-order block.
        gauge_invariant_flat_hessian[10:20, 20:24] = -vector_tensor_hessian.T
        gauge_invariant_flat_hessian[10:20, 10:20] = auxiliary_mass_hessian

        # The unique invariant pairing built from C0.C2 and C1^2 that removes
        # all non-wave degree-two terms is
        #
        #   -C0^a C2_a - 1/2 C1^2
        #
        # at action level.  Its Hessian therefore has cross C0/C2 blocks -g
        # and scalar block -1.
        gauge_fixing_pairing = sp.zeros(9)
        gauge_fixing_pairing[:4, 4:8] = -metric
        gauge_fixing_pairing[4:8, :4] = -metric
        gauge_fixing_pairing[8, 8] = -1
        negative_covector = {
            component: -component for component in covector
        }
        gauge_fixed_flat_hessian = sp.simplify(
            gauge_invariant_flat_hessian
            + gauge_condition.subs(negative_covector).T
            * gauge_fixing_pairing
            * gauge_condition
        )

        # The tensor kinetic pairing is the trace-reversed (DeWitt) form.
        # The factors 1/2 and +1 are fixed by the action Hessian above; they
        # are not normalization guesses.
        de_witt = tensor_pairing - sp.Rational(1, 2) * trace.T * trace
        field_fibre_pairing = sp.zeros(24)
        field_fibre_pairing[:10, 10:20] = sp.Rational(1, 2) * de_witt
        field_fibre_pairing[10:20, :10] = sp.Rational(1, 2) * de_witt
        field_fibre_pairing[20:24, 20:24] = metric
        field_principal_symbol = covector_square * field_fibre_pairing
        field_witness_operator = sp.simplify(
            field_fibre_pairing.inv() * gauge_fixed_flat_hessian
        )

        result = OrdinaryDerivativeWeylSystem(
            metric=metric,
            covector=covector,
            covector_up=covector_up,
            covector_square=covector_square,
            tensor_basis=tensor_basis_tuple,
            tensor_pairing=tensor_pairing,
            trace=trace,
            gauge_map=gauge_map,
            gauge_condition=gauge_condition,
            ghost_operator=ghost_operator,
            linearized_einstein_operator=linearized_einstein_operator,
            maxwell_operator=maxwell_operator,
            tensor_vector_mixing=tensor_vector_mixing,
            gauge_invariant_flat_hessian=gauge_invariant_flat_hessian,
            gauge_fixing_pairing=gauge_fixing_pairing,
            gauge_fixed_flat_hessian=gauge_fixed_flat_hessian,
            field_fibre_pairing=field_fibre_pairing,
            field_principal_symbol=field_principal_symbol,
            field_witness_operator=field_witness_operator,
            auxiliary_mass_hessian=auxiliary_mass_hessian,
        )
        result.verify()
        return result

    def tensor_coordinates(self, tensor: sp.Matrix) -> sp.Matrix:
        return sp.Matrix(
            [tensor[mu, nu] for mu, nu in SYMMETRIC_COORDINATES]
        )

    def verify(self) -> None:
        q = self.covector_square
        expected_ghost = sp.zeros(9)
        expected_ghost[:4, :4] = q * sp.eye(4)
        expected_ghost[:4, 4:8] = -sp.eye(4)
        expected_ghost[4:8, 4:8] = q * sp.eye(4)
        expected_ghost[8, 8] = q
        if sp.simplify(self.ghost_operator - expected_ghost) != sp.zeros(9):
            raise AssertionError("modified de Donder ghost operator is incorrect")

        negative_covector = {
            component: -component for component in self.covector
        }
        if sp.simplify(
            self.gauge_invariant_flat_hessian.subs(negative_covector).T
            - self.gauge_invariant_flat_hessian
        ) != sp.zeros(24):
            raise AssertionError(
                "ordinary-derivative action Hessian is not formally self-adjoint"
            )
        if sp.simplify(
            self.gauge_invariant_flat_hessian * self.gauge_map
        ) != sp.zeros(24, 9):
            raise AssertionError(
                "ordinary-derivative action Hessian does not annihilate its gauge map"
            )
        if sp.simplify(
            self.gauge_fixing_pairing * self.gauge_condition
            - self.gauge_map.subs(negative_covector).T
            * self.field_fibre_pairing
        ) != sp.zeros(9, 24):
            raise AssertionError(
                "modified de Donder companion is not the formal adjoint of the gauge map"
            )
        if self.gauge_fixing_pairing.rank() != 9:
            raise AssertionError("the auxiliary ghost pairing is degenerate")
        if sp.simplify(
            self.gauge_fixing_pairing * self.ghost_operator
            - self.ghost_operator.subs(negative_covector).T
            * self.gauge_fixing_pairing
        ) != sp.zeros(9):
            raise AssertionError("the ghost witness operator is not formally self-adjoint")
        if sp.simplify(
            self.gauge_fixed_flat_hessian.subs(negative_covector).T
            - self.gauge_fixed_flat_hessian
        ) != sp.zeros(24):
            raise AssertionError("gauge-fixed field Hessian is not formally self-adjoint")
        if sp.simplify(
            self.gauge_fixed_flat_hessian
            - self.gauge_invariant_flat_hessian
            - self.field_fibre_pairing
            * self.gauge_map
            * self.gauge_condition
        ) != sp.zeros(24):
            raise AssertionError("the exact field QW+WQ identity failed")

        # Extract the homogeneous degree-two part without discarding the
        # first- and zero-order couplings in the exact flat symbol.
        scale = sp.symbols("symbol_scale")
        scaled = {
            component: scale * component for component in self.covector
        }
        principal = self.gauge_fixed_flat_hessian.applyfunc(
            lambda entry: sp.expand(entry.subs(scaled)).coeff(scale, 2)
        )
        if sp.simplify(principal - self.field_principal_symbol) != sp.zeros(24):
            raise AssertionError(
                "modified de Donder gauge fixing did not produce the certified wave symbol"
            )

        if self.field_fibre_pairing.rank() != 24:
            raise AssertionError("ordinary-derivative field pairing is degenerate")
        normalized_field = sp.simplify(
            self.field_fibre_pairing.inv() * self.field_principal_symbol
        )
        if normalized_field != q * sp.eye(24):
            raise AssertionError("field system does not have scalar wave principal part")

        if self.auxiliary_mass_hessian.rank() != 10:
            raise AssertionError("the Pauli-Fierz auxiliary Hessian is singular")
        generic = sp.Matrix(sp.symbols("G0:10"))
        solution = sp.simplify(
            self.auxiliary_mass_hessian.inv()
            * self.tensor_pairing
            * generic
        )
        generic_tensor = sum(
            (generic[index] * self.tensor_basis[index] for index in range(10)),
            sp.zeros(4),
        )
        trace_generic = (self.trace * generic)[0]
        expected_tensor = (
            -2 * generic_tensor
            + sp.Rational(2, 3) * self.metric * trace_generic
        )
        if sp.simplify(solution - self.tensor_coordinates(expected_tensor)) != sp.zeros(10, 1):
            raise AssertionError("auxiliary tensor solution is not -2G+2g tr(G)/3")

        eliminated = sp.expand(
            -(solution.T * self.tensor_pairing * generic)[0]
            + sp.Rational(1, 2)
            * (solution.T * self.auxiliary_mass_hessian * solution)[0]
        )
        target = sp.expand(
            (generic.T * self.tensor_pairing * generic)[0]
            - sp.Rational(1, 3) * trace_generic**2
        )
        if sp.simplify(eliminated - target) != 0:
            raise AssertionError("auxiliary elimination did not return G^2-(tr G)^2/3")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-ordinary-derivative-auxiliary-system-v2",
            "background": "Lorentzian conformal cylinder",
            "source_action": (
                "L=-f^{mu nu}G^v_{mu nu}-F(v)^2/4-f^{mu nu}f_{mu nu}/4"
                "+(tr f)^2/4, linearized about its cylinder solution"
            ),
            "field_content": {
                "h_symmetric": 10,
                "f_auxiliary_symmetric": 10,
                "v_stueckelberg_covector": 4,
            },
            "gauge_parameters": {
                "xi_minus_2": 4,
                "xi_0": 4,
                "sigma": 1,
            },
            "modified_de_donder_variations": {
                "delta_C0": "Box xi_minus_2-xi_0",
                "delta_C2": "Box xi_0",
                "delta_C1": "Box sigma",
            },
            "ghost_operator": {
                "principal_symbol": "zeta^2 I_9",
                "lower_triangular_coupling": "C0 contains -xi_0",
                "ghost_pairing_rank": self.gauge_fixing_pairing.rank(),
                "symbol_formally_self_adjoint": True,
                "wave_principal_symbol_verified": True,
                "curved_global_operator_verified": False,
            },
            "field_operator": {
                "action_hessian_formally_self_adjoint": "E(-zeta)^T=E(zeta)",
                "action_hessian_times_gauge_map": "zero",
                "gauge_fixing_density": "-C0^a C2_a-C1^2/2",
                "gauge_fixing_hessian_blocks": {
                    "C0_C2": "-g^{ab}",
                    "C1_C1": "-1",
                },
                "companion_adjoint_identity": (
                    "Y_ghost C(zeta)=K(-zeta)^T J_aux"
                ),
                "principal_symbol_before_fibre_identification": "zeta^2 J_aux",
                "fibre_pairing_rank": self.field_fibre_pairing.rank(),
                "normalized_principal_symbol": "zeta^2 I_24",
                "wave_principal_symbol_verified": True,
                "curved_global_operator_verified": False,
                "exact_witness_operator": "J_aux^{-1}E_aux+K_aux C_aux",
                "lower_order_terms": (
                    "fixed by the covariant ordinary-derivative action and the "
                    "chosen modified de Donder gauge"
                ),
            },
            "generalized_auxiliary_elimination": {
                "mass_hessian_rank": self.auxiliary_mass_hessian.rank(),
                "solution": "f=-2G^v+(2/3)g tr(G^v)",
                "substituted_density": "G^v_ab G_v^ab-(tr G^v)^2/3",
                "in_stueckelberg_gauge_v_zero": "Ric^2-R^2/3",
                "local": True,
                "support_preserving": True,
                "reason": (
                    "the inverse is a pointwise algebraic fibre map; the source "
                    "contains only finitely many local derivatives of h and v"
                ),
            },
            "matrix_sha256": {
                "gauge_map": _digest(self.gauge_map),
                "gauge_condition": _digest(self.gauge_condition),
                "ghost_operator": _digest(self.ghost_operator),
                "linearized_einstein_operator": _digest(
                    self.linearized_einstein_operator
                ),
                "maxwell_operator": _digest(self.maxwell_operator),
                "tensor_vector_mixing": _digest(self.tensor_vector_mixing),
                "gauge_invariant_flat_hessian": _digest(
                    self.gauge_invariant_flat_hessian
                ),
                "gauge_fixing_pairing": _digest(self.gauge_fixing_pairing),
                "gauge_fixed_flat_hessian": _digest(
                    self.gauge_fixed_flat_hessian
                ),
                "field_fibre_pairing": _digest(self.field_fibre_pairing),
                "field_witness_operator": _digest(self.field_witness_operator),
                "auxiliary_mass_hessian": _digest(self.auxiliary_mass_hessian),
            },
            "theorem_boundary": (
                "this certifies the exact auxiliary Fourier-symbol realization and "
                "its scalar metric principal symbols.  The curved lower-order "
                "operator/adjoint table and retarded/advanced BV homotopies are "
                "separate certificates"
            ),
        }
