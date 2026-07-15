"""Minimal Diff x Weyl BRST differential in exact coordinate jets."""

from __future__ import annotations

from .algebra import Expression, JetVariable, LocalJetAlgebra


class MinimalBRSTDifferential:
    """The three minimal rows stated in the quantum programme brief.

    The differential commutes with coordinate total derivatives and extends
    as an odd graded derivation.  Imported antifield and nonminimal rows are
    intentionally absent until Gate A supplies a frozen classical snapshot.
    """

    def __init__(self, algebra: LocalJetAlgebra):
        self.algebra = algebra

    def _base_variation(self, variable: JetVariable) -> Expression:
        algebra = self.algebra
        if variable.field == "g":
            mu, nu = variable.components
            result = Expression()
            for rho in range(algebra.dimension):
                result += algebra.var("xi", (rho,)) * algebra.total_derivative(algebra.var("g", (mu, nu)), rho)
                result += algebra.total_derivative(algebra.var("xi", (rho,)), mu) * algebra.var("g", (rho, nu))
                result += algebra.total_derivative(algebra.var("xi", (rho,)), nu) * algebra.var("g", (mu, rho))
            return result + 2 * algebra.var("omega") * algebra.var("g", (mu, nu))
        if variable.field == "xi":
            (mu,) = variable.components
            result = Expression()
            for nu in range(algebra.dimension):
                result += algebra.var("xi", (nu,)) * algebra.total_derivative(algebra.var("xi", (mu,)), nu)
            return result
        if variable.field == "omega":
            result = Expression()
            for nu in range(algebra.dimension):
                result += algebra.var("xi", (nu,)) * algebra.total_derivative(algebra.var("omega"), nu)
            return result
        raise KeyError(f"no imported BRST row for {variable.field}")

    def on_variable(self, variable: JetVariable) -> Expression:
        base = self.algebra.jet(variable.field, variable.components)
        result = self._base_variation(base)
        for direction, count in enumerate(variable.derivatives):
            for _ in range(count):
                result = self.algebra.total_derivative(result, direction)
        return result

    def __call__(self, expression: Expression) -> Expression:
        result = Expression()
        for monomial, coefficient in expression.terms.items():
            prefix_parity = 0
            for index, variable in enumerate(monomial):
                prefix = Expression({monomial[:index]: coefficient})
                suffix = Expression({monomial[index + 1 :]: 1})
                sign = -1 if prefix_parity else 1
                result += sign * prefix * self.on_variable(variable) * suffix
                prefix_parity = (prefix_parity + variable.parity) % 2
        return result

    def nilpotency_residual(self, variable: JetVariable) -> Expression:
        return self(self.on_variable(variable))
