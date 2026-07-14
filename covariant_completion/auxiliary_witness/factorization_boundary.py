"""Fail-closed boundary for a direct same-bundle metric factorization."""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp


@dataclass(frozen=True)
class FullMetricFactorizationBoundary:
    """Prove the narrow no-go and state the remaining direct obligation.

    The TT polynomial already excludes two scalar curvature-shifted wave
    factors.  It does not exclude factors containing tensor curl or
    off-diagonal longitudinal couplings, so this module deliberately does
    not claim a general non-factorization theorem for the gauge-completed
    operator.
    """

    def verify(self) -> None:
        x, y, a, b = sp.symbols("x y a b")
        target = sp.expand(x**2 + 2 * x * (y - 4) + (y - 2) ** 2)
        candidate = sp.expand((x + y + a) * (x + y + b))
        polynomial = sp.Poly(candidate - target, x, y)
        equations = {
            monomial: coefficient
            for monomial, coefficient in polynomial.terms()
        }
        # x coefficient requires a+b=-8; y coefficient requires a+b=-4.
        if sp.simplify(equations[(1, 0)] - (a + b + 8)) != 0:
            raise AssertionError("unexpected time-polynomial condition")
        if sp.simplify(equations[(0, 1)] - (a + b + 4)) != 0:
            raise AssertionError("unexpected spatial-polynomial condition")
        if sp.solve(
            [equations[(1, 0)], equations[(0, 1)]], [a, b], dict=True
        ):
            raise AssertionError("scalar shifted-wave factors unexpectedly exist")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-full-metric-factorization-boundary-v1",
            "exact_full_operator": "H=B_lin+(1/2)K T on S^2_0 T*",
            "proved_restrictions": [
                "HK=(1/2)K Box(Box+2)",
                "TT restriction has the two local tensor-curl factors",
                "the action-normalized arbitrary-component operator is reconstructed from C_1^sharp C_1",
            ],
            "narrow_no_go": (
                "the TT polynomial cannot be written as two scalar "
                "curvature-shifted wave factors (x+y+a)(x+y+b): the x and y "
                "coefficients require a+b=-8 and a+b=-4 simultaneously"
            ),
            "not_ruled_out": (
                "a full-bundle product with first-order tensor curl and "
                "off-diagonal longitudinal couplings"
            ),
            "direct_same_bundle_status": "not certified",
            "selected_fallback": (
                "local ordinary-derivative tensor--tensor--vector realization "
                "with support-preserving generalized auxiliary elimination"
            ),
            "guard": (
                "the Einstein-background factorization obstruction for the "
                "gauge-invariant conformal wave operator is supporting context, "
                "not by itself a no-go theorem for the gauge-completed H"
            ),
        }
