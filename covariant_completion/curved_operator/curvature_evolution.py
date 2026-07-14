"""Candidate principal symmetric-hyperbolic Weyl-curvature evolution.

This module certifies the algebra of the analytic principal block suggested
by the exact null-symbol quotient.  The electric and magnetic parts of a Weyl tensor are
spatial symmetric trace-free tensors.  Their Maxwell-type evolution uses the
symmetrized tensor curl,

    d_t E - curl_2 B = lower order,
    d_t B + curl_2 E = lower order.

The block is not yet derived from the curved Bianchi/Bach equations.  That
derivation, their lower terms, full constraint propagation, and the local
prolongation retract are separate fail-closed obligations.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from .weyl_3plus1 import epsilon as _epsilon
from .weyl_3plus1 import stf_basis as _stf_basis


def _frobenius(first: sp.Matrix, second: sp.Matrix) -> sp.Expr:
    return sp.expand(sum(first[i, j] * second[i, j] for i in range(3) for j in range(3)))


def _tensor_curl_coefficient(axis: int, tensor: sp.Matrix) -> sp.Matrix:
    """Coefficient of ``partial_axis`` in the symmetrized tensor curl."""

    result = sp.zeros(3)
    for i in range(3):
        for j in range(3):
            result[i, j] = sp.Rational(1, 2) * sum(
                _epsilon(i, axis, a) * tensor[a, j]
                + _epsilon(j, axis, a) * tensor[a, i]
                for a in range(3)
            )
    return result


@dataclass(frozen=True)
class CurvatureEvolutionPrincipalSymbol:
    """Exact 10-component electric/magnetic principal evolution block."""

    stf_gram: sp.Matrix
    curl_coefficients: tuple[sp.Matrix, sp.Matrix, sp.Matrix]
    symmetrizer: sp.Matrix
    evolution_coefficients: tuple[sp.Matrix, sp.Matrix, sp.Matrix]
    transverse_basis: sp.Matrix
    transverse_curl: sp.Matrix
    transverse_characteristic: sp.Matrix
    constraint_curl_factor: sp.Rational

    @staticmethod
    def build() -> "CurvatureEvolutionPrincipalSymbol":
        basis = _stf_basis()
        gram = sp.Matrix(
            [[_frobenius(left, right) for right in basis] for left in basis]
        )

        curls: list[sp.Matrix] = []
        for axis in range(3):
            coefficient = sp.zeros(5)
            for column, tensor in enumerate(basis):
                image = _tensor_curl_coefficient(axis, tensor)
                pairings = sp.Matrix([_frobenius(item, image) for item in basis])
                coefficient[:, column] = gram.inv() * pairings
            curls.append(coefficient)

        zero = sp.zeros(5)
        symmetrizer = sp.diag(gram, gram)
        evolution: list[sp.Matrix] = []
        for curl in curls:
            evolution.append(zero.row_join(-curl).col_join(curl.row_join(zero)))

        # For a spatial covector along x^1, transverse STF tensors are
        # h_22=-h_33 and h_23.  In the rational STF basis these are columns
        # (b1-b2)/2 and b5.
        transverse = sp.zeros(5, 2)
        transverse[:, 0] = sp.Matrix([sp.Rational(1, 2), -sp.Rational(1, 2), 0, 0, 0])
        transverse[:, 1] = sp.Matrix([0, 0, 0, 0, 1])
        transverse_gram = transverse.T * gram * transverse
        transverse_curl = transverse_gram.inv() * transverse.T * gram * curls[0] * transverse
        transverse_characteristic = (
            sp.zeros(2).row_join(-transverse_curl).col_join(
                transverse_curl.row_join(sp.zeros(2))
            )
        )

        result = CurvatureEvolutionPrincipalSymbol(
            stf_gram=gram,
            curl_coefficients=(curls[0], curls[1], curls[2]),
            symmetrizer=symmetrizer,
            evolution_coefficients=(evolution[0], evolution[1], evolution[2]),
            transverse_basis=transverse,
            transverse_curl=transverse_curl,
            transverse_characteristic=transverse_characteristic,
            constraint_curl_factor=sp.Rational(1, 2),
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.stf_gram != sp.diag(2, 6, 2, 2, 2):
            raise AssertionError("STF Frobenius Gram matrix drifted")
        if any(value <= 0 for value in self.stf_gram.diagonal()):
            raise AssertionError("STF symmetrizer is not positive definite")
        for curl, evolution in zip(
            self.curl_coefficients, self.evolution_coefficients, strict=True
        ):
            if self.stf_gram * curl + curl.T * self.stf_gram != sp.zeros(5):
                raise AssertionError("tensor-curl coefficient is not Gram-skew")
            weighted = self.symmetrizer * evolution
            if weighted != weighted.T:
                raise AssertionError("electric/magnetic evolution is not symmetrized")
        if self.transverse_curl**2 != -sp.eye(2):
            raise AssertionError("transverse tensor curl does not carry helicity two")
        spectral_parameter = sp.Symbol("lambda")
        expected_characteristic = (
            (spectral_parameter - 1) ** 2
            * (spectral_parameter + 1) ** 2
        )
        if sp.expand(self.transverse_characteristic.charpoly().as_expr()) != sp.expand(
            expected_characteristic
        ):
            raise AssertionError("physical curvature characteristic speeds drifted")
        expected_full_characteristic = (
            spectral_parameter**2
            * (spectral_parameter**2 - sp.Rational(1, 4)) ** 2
            * (spectral_parameter**2 - 1) ** 2
        )
        if sp.expand(
            self.evolution_coefficients[0].charpoly().as_expr()
        ) != sp.expand(expected_full_characteristic):
            raise AssertionError("full candidate curvature spectrum drifted")

        # The principal divergence constraints form their own homogeneous
        # Maxwell-type subsystem.  For arbitrary spatial covector xi,
        # div(curl_2 h)=(1/2) curl_1(div h).
        xi = sp.symbols("xi0:3")
        basis = _stf_basis()
        divergence = sp.zeros(3, 5)
        vector_curl = sp.zeros(3)
        for output in range(3):
            for column, tensor in enumerate(basis):
                divergence[output, column] = sum(
                    xi[index] * tensor[index, output] for index in range(3)
                )
            for input_axis in range(3):
                vector_curl[output, input_axis] = sum(
                    _epsilon(output, derivative, input_axis) * xi[derivative]
                    for derivative in range(3)
                )
        tensor_curl = sum(
            (xi[axis] * self.curl_coefficients[axis] for axis in range(3)),
            sp.zeros(5),
        )
        constraint_defect = divergence * tensor_curl - (
            self.constraint_curl_factor * vector_curl * divergence
        )
        if constraint_defect.applyfunc(sp.expand) != sp.zeros(3, 5):
            raise AssertionError("principal Weyl divergence constraints do not close")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-curvature-evolution-principal-symbol-v2",
            "bundle": "STF_2(S^3) electric + STF_2(S^3) magnetic",
            "rank": 10,
            "principal_equations": [
                "partial_t E-curl_2 B=lower order",
                "partial_t B+curl_2 E=lower order",
            ],
            "A0": "I_10",
            "symmetrizer": [
                [str(value) for value in row]
                for row in self.symmetrizer.tolist()
            ],
            "symmetrizer_positive_definite": True,
            "spatial_symbol_symmetric_after_symmetrization": True,
            "transverse_curl_matrix": [
                [str(value) for value in row]
                for row in self.transverse_curl.tolist()
            ],
            "transverse_curl_square": "-I_2",
            "representative_unit_spatial_covector": [1, 0, 0],
            "direction_globalization": (
                "the delta/epsilon construction is SO(3)-equivariant, so the "
                "representative-direction physical spectrum holds for every "
                "unit spatial covector"
            ),
            "physical_characteristic_speeds": [-1, -1, 1, 1],
            "candidate_curvature_principal_symmetric_hyperbolicity": True,
            "principal_constraint_identity": (
                "div(curl_2 h)=(1/2) curl_1(div h)"
            ),
            "candidate_curvature_principal_constraints_propagate": True,
            "full_candidate_characteristic_speeds": {
                "-1": 2,
                "-1/2": 2,
                "0": 2,
                "1/2": 2,
                "1": 2,
            },
            "principal_system_derived_from_curved_Bianchi_Bach": False,
            "curved_Bianchi_Bach_lower_terms_derived": False,
            "curved_EB_equations": False,
            "curved_EB_first_order_closure": False,
            "curved_EB_symmetric_hyperbolicity": False,
            "curved_sourced_constraint_identity": False,
            "curvature_constraints_propagate": False,
            "curved_constraint_propagation": False,
            "EAL_curvature_spectrum_match": False,
            "local_prolongation_retract_verified": False,
            "support_local_prolongation_retract": False,
            "prolonged_BV_operator_identity": False,
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "complete_curvature_green_realization": False,
            "proof_boundary": (
                "the exact certificate is only the SO(3)-equivariant candidate "
                "principal block and principal divergence identity; it does not "
                "derive the curved Bianchi--Bach system, sourced constraints, "
                "all-level E/A/L spectrum, or a BV Green homotopy"
            ),
            "fail_closed": True,
        }
