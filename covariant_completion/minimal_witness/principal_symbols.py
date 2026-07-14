"""Exact Lorentzian principal symbols for the minimal detour witness.

This module works on a four-dimensional trace-free symmetric tensor fibre.
It derives the Bach symbol from the quadratic repository action

``Ric_1(h)^2 - R_1(h)^2/3``

rather than inserting a gauge-fixed Bach symbol.  The calculation therefore
fixes the coefficient of the third-order companion in the same convention as
``notes/conformal-local-detour.md``.

Principal-symbol exactness is only the first stage of a Green's-witness
proof.  No Green-hyperbolicity claim is made here: curvature completion and
an exact local factorization remain separate obligations.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import sympy as sp


DIMENSION = 4
TRACEFREE_COORDINATES = (
    (0, 0),
    (0, 1),
    (0, 2),
    (0, 3),
    (1, 1),
    (1, 2),
    (1, 3),
    (2, 2),
    (2, 3),
)


def _digest(matrix: sp.MatrixBase) -> str:
    payload = sp.srepr(sp.ImmutableDenseMatrix(matrix)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class MinimalWitnessPrincipalSymbols:
    """Action-derived symbol matrices for ``K``, ``T`` and ``B``."""

    metric: sp.Matrix
    covector: sp.Matrix
    covector_up: sp.Matrix
    covector_square: sp.Expr
    tensor_basis: tuple[sp.Matrix, ...]
    tensor_pairing: sp.Matrix
    conformal_killing: sp.Matrix
    companion: sp.Matrix
    bach: sp.Matrix

    @staticmethod
    def build() -> "MinimalWitnessPrincipalSymbols":
        metric = sp.diag(-1, 1, 1, 1)
        covector = sp.Matrix(sp.symbols("zeta_0:4", real=True))
        covector_up = metric * covector
        covector_square = sp.expand((covector.T * metric * covector)[0])

        def tensor_from_coordinates(values: list[sp.Expr]) -> sp.Matrix:
            tensor = sp.zeros(DIMENSION)
            for value, (mu, nu) in zip(values, TRACEFREE_COORDINATES):
                tensor[mu, nu] = value
                tensor[nu, mu] = value
            # -h_00+h_11+h_22+h_33=0 in the selected Lorentz convention.
            tensor[3, 3] = values[0] - values[4] - values[7]
            return tensor

        tensor_basis = tuple(
            tensor_from_coordinates(
                [sp.Integer(index == basis_index) for index in range(9)]
            )
            for basis_index in range(9)
        )

        def tensor_coordinates(tensor: sp.Matrix) -> sp.Matrix:
            return sp.Matrix(
                [tensor[mu, nu] for mu, nu in TRACEFREE_COORDINATES]
            )

        tensor_pairing = sp.Matrix(
            9,
            9,
            lambda row, column: sp.trace(
                metric
                * tensor_basis[row]
                * metric
                * tensor_basis[column]
            ),
        )

        conformal_killing = sp.zeros(9, DIMENSION)
        for column in range(DIMENSION):
            vector = sp.zeros(DIMENSION, 1)
            vector[column] = 1
            contraction = (covector_up.T * vector)[0]
            image = (
                covector * vector.T
                + vector * covector.T
                - sp.Rational(1, 2) * metric * contraction
            )
            conformal_killing[:, column] = tensor_coordinates(image)

        companion = sp.zeros(DIMENSION, 9)
        for column, tensor in enumerate(tensor_basis):
            divergence = tensor * covector_up
            double_divergence = (covector_up.T * tensor * covector_up)[0]
            companion[:, column] = (
                covector_square * divergence
                - sp.Rational(1, 3) * covector * double_divergence
            )

        # Linearized Ricci tensors and scalar curvatures on trace-free input.
        ricci: list[sp.Matrix] = []
        scalar: list[sp.Expr] = []
        for tensor in tensor_basis:
            divergence = tensor * covector_up
            ricci_tensor = sp.zeros(DIMENSION)
            for mu in range(DIMENSION):
                for nu in range(DIMENSION):
                    ricci_tensor[mu, nu] = sp.Rational(1, 2) * (
                        covector[mu] * divergence[nu]
                        + covector[nu] * divergence[mu]
                        - covector_square * tensor[mu, nu]
                    )
            ricci.append(ricci_tensor)
            scalar.append((covector_up.T * tensor * covector_up)[0])

        # This is the mixed Hessian of Ric_1^2-R_1^2/3.  The factor two is
        # essential: the action is quadratic at a conformally flat background.
        action_hessian = sp.Matrix(
            9,
            9,
            lambda row, column: sp.expand(
                2
                * sp.trace(
                    metric * ricci[row] * metric * ricci[column]
                )
                - sp.Rational(2, 3) * scalar[row] * scalar[column]
            ),
        )
        bach = sp.simplify(tensor_pairing.inv() * action_hessian)

        return MinimalWitnessPrincipalSymbols(
            metric=metric,
            covector=covector,
            covector_up=covector_up,
            covector_square=covector_square,
            tensor_basis=tensor_basis,
            tensor_pairing=tensor_pairing,
            conformal_killing=conformal_killing,
            companion=companion,
            bach=bach,
        )

    def verify(self) -> None:
        q4 = sp.expand(self.covector_square**2)
        identity_g = sp.eye(DIMENSION)
        identity_m = sp.eye(9)

        if sp.simplify(
            self.companion * self.conformal_killing - q4 * identity_g
        ) != sp.zeros(DIMENSION):
            raise AssertionError("sigma(T_pr K) is not (zeta^2)^2 I_G")

        gauge_fixed = sp.simplify(
            self.bach
            + sp.Rational(1, 2)
            * self.conformal_killing
            * self.companion
        )
        if sp.simplify(
            gauge_fixed - sp.Rational(1, 2) * q4 * identity_m
        ) != sp.zeros(9):
            raise AssertionError(
                "sigma(B+K T_pr/2) is not (zeta^2)^2 I_M/2"
            )
        if sp.simplify(self.bach * self.conformal_killing) != sp.zeros(9, 4):
            raise AssertionError("the action-derived Bach symbol does not kill K")
        if sp.simplify(
            self.tensor_pairing * self.bach
            - self.bach.T * self.tensor_pairing
        ) != sp.zeros(9):
            raise AssertionError("the Bach symbol is not formally self-adjoint")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-minimal-witness-principal-symbol-v1",
            "category": "four-dimensional Lorentzian trace-free fibres",
            "metric_signature": "(-,+,+,+)",
            "tracefree_metric_dimension": 9,
            "ghost_fibre_dimension": 4,
            "conformal_killing_convention": (
                "K(xi)_mn=zeta_m xi_n+zeta_n xi_m-eta_mn(zeta.xi)/2"
            ),
            "companion_principal_part": "T_pr=Box delta-(1/3)d delta^2",
            "bach_source": (
                "mixed Hessian of Ric_1^2-(1/3)R_1^2 in the repository "
                "action normalization"
            ),
            "ghost_identity": "sigma(T_pr K)=(zeta^2)^2 I_G",
            "field_identity": (
                "sigma(B+(1/2)K T_pr)=(1/2)(zeta^2)^2 I_M"
            ),
            "solved_coefficients": {"alpha": "1/2", "beta": "1/2"},
            "ward_identity": "sigma(B) sigma(K)=0",
            "formal_self_adjointness": True,
            "matrix_digests": {
                "K": _digest(self.conformal_killing),
                "T_pr": _digest(self.companion),
                "B": _digest(self.bach),
                "J_M": _digest(self.tensor_pairing),
            },
            "scope_guard": (
                "principal-symbol scalar biwave form is necessary but does not "
                "prove Green hyperbolicity; an exact curvature completion and "
                "local hyperbolic factorization or equivalent system remain required"
            ),
        }
