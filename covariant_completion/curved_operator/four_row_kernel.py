"""Exact formal four-row assembly of the curved auxiliary witness.

Once ``K``, ``C`` and the action-normalized field equation
``Ebar=J_aux^{-1}E`` are fixed, the identity ``QW+WQ=P`` is block algebra;
it is not another curvature-coefficient calculation.  This module performs
that multiplication in an exact noncommutative polynomial algebra.  The two
non-formal inputs, ``Ebar K=0`` and its adjoint, are supplied by the
action-derived completion-square kernel.
"""

from __future__ import annotations

from dataclasses import dataclass

from covariant_completion.minimal_witness.formal_operators import (
    OperatorPolynomial,
    matrix_add,
    matrix_multiply,
    zero_matrix,
)


@dataclass(frozen=True)
class CurvedFourRowKernel:
    q: list[list[OperatorPolynomial]]
    witness: list[list[OperatorPolynomial]]
    wave: list[list[OperatorPolynomial]]
    defect: list[list[OperatorPolynomial]]

    @staticmethod
    def build() -> "CurvedFourRowKernel":
        # Row order is (G[9],M[24],E[24],I[9]).
        k = OperatorPolynomial.atom("Kcyl")
        c = OperatorPolynomial.atom("Ccyl")
        equation = OperatorPolynomial.atom("JinvEcyl")
        identity = OperatorPolynomial.identity()

        q = zero_matrix(4)
        q[1][0] = k
        q[2][1] = equation
        q[3][2] = c

        witness = zero_matrix(4)
        witness[0][1] = c
        witness[1][2] = identity
        witness[2][3] = k

        wave = zero_matrix(4)
        wave[0][0] = c * k
        wave[1][1] = equation + k * c
        wave[2][2] = equation + k * c
        wave[3][3] = c * k

        defect = matrix_add(
            matrix_add(matrix_multiply(q, witness), matrix_multiply(witness, q)),
            [[entry.scale(-1) for entry in row] for row in wave],
        )
        result = CurvedFourRowKernel(q, witness, wave, defect)
        result.verify()
        return result

    def verify(self) -> None:
        zero = OperatorPolynomial.zero()
        if any(entry != zero for row in self.defect for entry in row):
            raise AssertionError("formal curved QW+WQ-P block defect")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-curved-four-row-operator-kernel-v1",
            "row_order": ["G[9]", "M[24]", "E[24]", "I[9]"],
            "Q_blocks": {
                "G_to_M": "K_cyl",
                "M_to_E": "J_aux^{-1}E_aux,cyl",
                "E_to_I": "C_cyl",
            },
            "W_blocks": {
                "M_to_G": "C_cyl",
                "E_to_M": "identity_24",
                "I_to_E": "K_cyl",
            },
            "P_blocks": {
                "G": "C_cyl K_cyl",
                "M": "J_aux^{-1}E_aux,cyl+K_cyl C_cyl",
                "E": "J_aux^{-1}E_aux,cyl+K_cyl C_cyl",
                "I": "C_cyl K_cyl",
            },
            "QW_plus_WQ_minus_P": "zero",
            "noncommutative_block_multiplication_exact": True,
            "Q_squared_inputs": [
                "E_aux,cyl K_cyl=0 from action-derived tangent split",
                "K_cyl^sharp E_aux,cyl=0 by formal adjointness",
            ],
            "formal_adjoint_inputs": [
                "E_aux,cyl^sharp=E_aux,cyl from action Hessian",
                "Y_gh C_cyl=K_cyl^sharp J_aux coefficientwise",
            ],
        }
