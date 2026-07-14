"""Exact graded block assembly for the trace-free minimal witness."""

from __future__ import annotations

from dataclasses import dataclass

from .formal_operators import (
    OperatorPolynomial,
    matrix_add,
    matrix_multiply,
    zero_matrix,
)


@dataclass(frozen=True)
class MinimalWitnessMatrix:
    """The formal four-row matrix on ``G -> M -> E -> I``.

    This certificate separates two questions:

    * the block identity ``P=QW+WQ``, proved exactly here;
    * Green hyperbolicity of each displayed diagonal block, which requires
      the differential-operator factorization certificates.
    """

    q: tuple[tuple[OperatorPolynomial, ...], ...]
    w: tuple[tuple[OperatorPolynomial, ...], ...]
    p: tuple[tuple[OperatorPolynomial, ...], ...]

    @staticmethod
    def build() -> "MinimalWitnessMatrix":
        q = zero_matrix(4)
        q[1][0] = OperatorPolynomial.atom("K")
        q[2][1] = OperatorPolynomial.atom("B")
        q[3][2] = OperatorPolynomial.atom("Ksharp")

        w = zero_matrix(4)
        w[0][1] = OperatorPolynomial.atom("T")
        # This coefficient is forced by H=B+KT/2 in the action convention.
        w[1][2] = OperatorPolynomial.identity(2)
        w[2][3] = OperatorPolynomial.atom("Tsharp")

        p = matrix_add(matrix_multiply(q, w), matrix_multiply(w, q))
        result = MinimalWitnessMatrix(
            q=tuple(tuple(row) for row in q),
            w=tuple(tuple(row) for row in w),
            p=tuple(tuple(row) for row in p),
        )
        result.verify()
        return result

    def verify(self) -> None:
        expected = (
            OperatorPolynomial._from_dict({("T", "K"): 1}),
            OperatorPolynomial._from_dict({("B",): 2, ("K", "T"): 1}),
            OperatorPolynomial._from_dict(
                {("B",): 2, ("Tsharp", "Ksharp"): 1}
            ),
            OperatorPolynomial._from_dict({("Ksharp", "Tsharp"): 1}),
        )
        for row in range(4):
            for column in range(4):
                target = expected[row] if row == column else OperatorPolynomial.zero()
                if self.p[row][column] != target:
                    raise AssertionError(
                        f"incorrect witness block {row,column}: "
                        f"{self.p[row][column].display()} != {target.display()}"
                    )

        # The BV pairing reverses the four rows: G<->I and M<->E.  Under
        # this reversal, T and T^sharp exchange and the middle 2I is fixed.
        dual = (3, 2, 1, 0)
        for row in range(4):
            for column in range(4):
                paired_adjoint = self.w[dual[column]][dual[row]].adjoint()
                if self.w[row][column] != paired_adjoint:
                    raise AssertionError(
                        f"W is not graded self-dual at {row,column}"
                    )

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-minimal-witness-block-matrix-v1",
            "complex": "G --K--> M --B--> E --Ksharp--> I",
            "backward_blocks": {
                "M_to_G": "T",
                "E_to_M": "2 sharp^{-1}",
                "I_to_E": "Tsharp",
            },
            "identity": "P=QW+WQ",
            "degreewise_blocks": {
                "G": self.p[0][0].display(),
                "M": self.p[1][1].display(),
                "E": self.p[2][2].display(),
                "I": self.p[3][3].display(),
            },
            "normalization": (
                "with H=B+(1/2)KT, the actual metric witness block is 2H; "
                "the ghost block is R=TK"
            ),
            "graded_formal_self_adjointness": True,
            "analytic_scope": (
                "this exact block calculation does not by itself prove that "
                "the full metric block 2H is Green hyperbolic"
            ),
        }
