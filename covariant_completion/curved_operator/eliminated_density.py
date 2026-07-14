"""Exact boundary identity for the eliminated Stueckelberg vector.

After the auxiliary square is completed, the remaining density contains

``G_b^{ab}G^b_ab-(tr G_b)^2/3-F(b)^2/4``.

This module proves algebraically that its difference from
``Ric^2-R^2/3`` is a divergence.  This is the missing step needed to justify
the zero vector block in the factorized curved Hessian; algebraic auxiliary
elimination alone would not suffice.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp


@dataclass(frozen=True)
class EliminatedVectorDensityIdentity:
    raw_defect: sp.Expr
    divergence_expansion: sp.Expr

    @staticmethod
    def build() -> "EliminatedVectorDensityIdentity":
        # Independent invariant contractions.  A2=A_ab A^ab and
        # Across=A_ab A^ba for A_ab=nabla_a b_b.
        R, d, u = sp.symbols("R d u")
        ric2, ric_a, ric_bb = sp.symbols("Ric2 RicA Ricbb")
        a2, across, s_bb = sp.symbols("A2 Across Sbb")

        # G_b=H+g q with H=Ric+S+b b/2 and
        # q=-R/2-d+u/4.  The formula retains every contraction before using
        # integration by parts.
        tr_h = R + d + sp.Rational(1, 2) * u
        h_squared = (
            ric2
            + 2 * ric_a
            + ric_bb
            + sp.Rational(1, 2) * (a2 + across)
            + s_bb
            + sp.Rational(1, 4) * u**2
        )
        q = -sp.Rational(1, 2) * R - d + sp.Rational(1, 4) * u
        gb_trace_adjusted = sp.expand(
            h_squared
            - sp.Rational(1, 3) * tr_h**2
            - sp.Rational(2, 3) * q * tr_h
            - sp.Rational(4, 3) * q**2
        )
        f_squared_over_four = sp.Rational(1, 2) * (a2 - across)
        raw_defect = sp.expand(
            gb_trace_adjusted
            - f_squared_over_four
            - (ric2 - sp.Rational(1, 3) * R**2)
        )

        # Expand the divergence current
        # 2 Ric^{ab}b_b-Rb^a+b^b nabla_b b^a-b^a d+(u/2)b^a.
        # Contracted Bianchi cancels the two dR terms; the vector commutator
        # gives +Ric(b,b); and b^a nabla_a u=2 S(b,b).
        curvature_current = 2 * ric_a - R * d
        acceleration_current = across - d**2 + ric_bb
        cubic_current = s_bb + sp.Rational(1, 2) * d * u
        divergence_expansion = sp.expand(
            curvature_current + acceleration_current + cubic_current
        )

        result = EliminatedVectorDensityIdentity(
            raw_defect=raw_defect,
            divergence_expansion=divergence_expansion,
        )
        result.verify()
        return result

    def verify(self) -> None:
        if sp.expand(self.raw_defect - self.divergence_expansion) != 0:
            raise AssertionError("the eliminated b-density is not the claimed divergence")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-eliminated-vector-density-boundary-v1",
            "G_b": (
                "Ric+sym(nabla b)/2+b tensor b/2"
                "-g(R+2 div b-b^2/2)/2"
            ),
            "identity": (
                "G_b^2-(tr G_b)^2/3-F(b)^2/4 "
                "=Ric^2-R^2/3+nabla_a B^a"
            ),
            "boundary_current": (
                "B^a=2 Ric^{ab}b_b-R b^a+b^b nabla_b b^a"
                "-b^a div(b)+(b^2/2)b^a"
            ),
            "reduction_identities": {
                "contracted_Bianchi": "2 nabla_a Ric^{ab}=nabla^b R",
                "vector_commutator": (
                    "nabla_a nabla_b b^a-nabla_b nabla_a b^a=Ric_bc b^c"
                ),
                "cubic": "b^a nabla_a(b^2)=2 b^a b^b nabla_a b_b",
                "S_squared_minus_F_squared_over_4": (
                    "(nabla_a b_b)(nabla^b b^a)"
                ),
            },
            "symbolic_defect": str(self.raw_defect),
            "symbolic_divergence_expansion": str(self.divergence_expansion),
            "defect_minus_divergence": 0,
            "consequence": (
                "the eliminated action is Ric^2-R^2/3 modulo a local boundary; "
                "its b Hessian is zero modulo the corresponding current improvement"
            ),
        }
