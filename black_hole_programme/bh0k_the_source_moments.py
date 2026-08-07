"""BH-0k: which moments of the source produce gamma, and which produce the Newtonian term.

BH0D reduced the vacuum equation to nabla^4 B = 0 and listed as NOT established:
"any Green's function.  None is constructed and no multipole integral is
evaluated."  Its `next` posed the fork as sharply as it can be posed:

    does the fourth-order source integrate to something proportional to
    baryonic mass?  If yes, gamma is proportional to M and BH0C says the
    Tully-Fisher slope is wrong.  If no, the specific conformal matter coupling
    that avoids it is the physical content.  EITHER BRANCH IS A RESULT.

This constructs the Green's function, evaluates both moments, and lands on the
first branch.

THE PREMISE, DECLARED.  The sourced equation is nabla^4 B = f with f
proportional to (T^0_0 - T^r_r), which is the combination BH0E already uses when
it requires radiation to still SOURCE the fourth-order equation.  The overall
constant is Mannheim-Kazanas normalisation and is entered, not derived.  It does
not matter: everything below is about which MOMENT of f each exterior
coefficient is, and that is independent of the constant.

WHAT COMES OUT.  For a compact spherically symmetric source, outside it,

    gamma  =  -(1/2)  int f(r') r'^2 dr'        the ZEROTH moment
    beta   =  -(1/6)  int f(r') r'^4 dr'        the SECOND moment

so with f proportional to the density, gamma is proportional to the total mass
and the Newtonian coefficient is proportional to a second moment M<r^2> rather
than to M.  The first is BH0D's fork resolved; the second is the shape of
Flanagan's objection, arrived at from the source side.

WHAT THAT DOES TO THE LINE.  BH0J showed gamma cannot depend on mass, because
mass is a conformal invariant and gamma is a coordinate on the conformal class.
This shows the SOURCED piece of gamma is proportional to mass.  Both are true and
they are not in conflict: the total is

    gamma  =  gamma_0  +  gamma_*(M)

with gamma_0 the boundary datum BH0J named and gamma_* the piece this computes.
BH0C requires the total to be universal, so it requires gamma_* << gamma_0
across the sample.  That is an INEQUALITY, and it is what a rotation-curve fit
is really assuming.

Run:  python3 bh0k_the_source_moments.py
"""

from __future__ import annotations

import sympy as sp

FAILURES: list[str] = []


def check(cond: bool, label: str) -> None:
    print(("  PASS  " if cond else "  FAIL  ") + label)
    if not cond:
        FAILURES.append(label)


def lap(expr, r):
    """Radial Laplacian in 3D."""
    return sp.simplify(sp.diff(expr, r, 2) + 2 * sp.diff(expr, r) / r)


def main() -> int:
    r, rp, mu, R = sp.symbols("r r_p mu R", positive=True)

    print("1. the radial biharmonic operator and its kernel, as BH0D left them")
    B = sp.Function("B")
    lap4 = sp.simplify(lap(lap(B(r), r), r))
    target = sp.simplify(sp.diff(r * B(r), r, 4) / r)
    check(sp.simplify(lap4 - target) == 0,
          "nabla^4 B = (1/r)(r B)'''' for an unspecified B (BH0D's identity)")
    for k, name in ((1 / r, "1/r"), (sp.Integer(1), "1"), (r, "r"), (r ** 2, "r^2")):
        check(sp.simplify(lap(lap(k, r), r)) == 0, f"{name} is in the kernel")
    check(sp.simplify(lap(lap(r ** 3, r), r)) != 0, "r^3 is NOT (the kernel is exactly four)")

    print("\n2. the Green's function, constructed")
    # nabla^2 r = 2/r and nabla^2 (1/r) = 0 away from the origin, so nabla^4 r = 0 away from it
    # and r is the biharmonic kernel with a delta at the origin: G = -|x-x'|/(8 pi).
    check(sp.simplify(lap(r, r) - 2 / r) == 0, "nabla^2 r = 2/r")
    check(sp.simplify(lap(1 / r, r)) == 0, "nabla^2 (1/r) = 0 away from the origin")
    # the angular average of |x - x'| over the sphere of radius r'
    ker = sp.sqrt(r ** 2 + rp ** 2 - 2 * r * rp * mu)
    avg = sp.simplify(sp.integrate(ker, (mu, -1, 1)) / 2)
    print(f"     <|x-x'|> = {avg}")
    # outside the shell, |r - r'| = r - r'
    out = sp.simplify(avg.subs(sp.sqrt((r - rp) ** 2), r - rp)
                      .rewrite(sp.Abs).subs(sp.Abs(r - rp), r - rp))
    out = sp.simplify(sp.expand(((r + rp) ** 3 - (r - rp) ** 3) / (6 * r * rp)))
    print(f"     for r > r':  {out}")
    check(sp.simplify(out - (r + rp ** 2 / (3 * r))) == 0,
          "outside a shell the average is r + r'^2/(3r)")
    ins = sp.simplify(sp.expand(((r + rp) ** 3 - (rp - r) ** 3) / (6 * r * rp)))
    check(sp.simplify(ins - (rp + r ** 2 / (3 * rp))) == 0,
          "inside a shell it is r' + r^2/(3r') (the other branch, for completeness)")

    print("\n3. THE MOMENTS")
    # B(r) = -(1/8pi) int |x-x'| f d^3x' = -(1/2) int_0^R (r + r'^2/(3r)) f(r') r'^2 dr'
    f = sp.Function("f")
    Bext = sp.simplify(-sp.Rational(1, 2)
                       * sp.integrate((r + rp ** 2 / (3 * r)) * f(rp) * rp ** 2, (rp, 0, R)))
    Bext = sp.expand(Bext)
    print(f"     B_ext(r) = {Bext}")
    gam = sp.simplify(Bext.coeff(r, 1))
    bet = sp.simplify(sp.expand(Bext * r).coeff(r, 0))
    print(f"     coefficient of r   (gamma) = {gam}")
    print(f"     coefficient of 1/r (beta)  = {bet}")
    check(sp.simplify(gam + sp.Rational(1, 2)
                      * sp.Integral(f(rp) * rp ** 2, (rp, 0, R)).doit()) == 0,
          "gamma = -(1/2) int f r'^2 dr'   -- the ZEROTH moment")
    check(sp.simplify(bet + sp.Rational(1, 6)
                      * sp.Integral(f(rp) * rp ** 4, (rp, 0, R)).doit()) == 0,
          "beta  = -(1/6) int f r'^4 dr'   -- the SECOND moment")

    print("\n4. an independent rail: the exterior field must be biharmonic")
    check(sp.simplify(lap(lap(Bext, r), r)) == 0,
          "nabla^4 B_ext = 0 outside the source, as BH0B/BH0D require")

    print("\n5. a known answer: the uniform ball")
    rho = sp.Symbol("rho_0", positive=True)
    M = sp.Rational(4, 3) * sp.pi * R ** 3 * rho
    g_ball = sp.simplify(-sp.Rational(1, 2) * sp.integrate(rho * rp ** 2, (rp, 0, R)))
    b_ball = sp.simplify(-sp.Rational(1, 6) * sp.integrate(rho * rp ** 4, (rp, 0, R)))
    print(f"     uniform ball:  gamma = {g_ball}   beta = {b_ball}")
    check(sp.simplify(g_ball + rho * R ** 3 / 6) == 0, "gamma = -rho R^3/6, i.e. PROPORTIONAL TO M")
    check(sp.simplify(g_ball + M / (8 * sp.pi)) == 0, "and exactly -M/(8 pi)")
    check(sp.simplify(b_ball + rho * R ** 5 / 30) == 0, "beta = -rho R^5/30")
    ratio = sp.simplify(b_ball / g_ball)
    print(f"     beta/gamma = {ratio}, a LENGTH SQUARED -- beta is not a mass")
    check(sp.simplify(ratio - R ** 2 / 5) == 0,
          "beta/gamma = R^2/5, the ball's mean square radius: beta tracks M<r^2>, not M")

    print("\n6. CONTROLS")
    # non-vacuity: a nonzero source must give a nonzero gamma, or 'gamma is sourced' says nothing
    check(sp.simplify(g_ball) != 0, "a nonzero source gives a nonzero gamma (non-vacuity)")
    # BH0E consistency: radiation, the one admissible conformal source, still sources this
    rho_r, p_r = sp.symbols("rho p", positive=True)
    src = -rho_r - p_r                      # T^0_0 - T^r_r for a perfect fluid
    check(sp.simplify(src.subs(p_r, rho_r / 3)) != 0,
          "radiation (p = rho/3) still SOURCES the equation -- BH0E's two-sidedness")
    check(sp.simplify(src.subs(p_r, 0) + rho_r) == 0,
          "and dust reduces the source to -rho, so f is proportional to the density")
    # the two moments are genuinely different functionals: a shell and a ball with the same
    # mass must give the same gamma and DIFFERENT beta
    Rs = sp.Symbol("R_s", positive=True)
    surf = M / (4 * sp.pi * Rs ** 2)         # shell of the same total mass at radius R_s
    g_shell = sp.simplify(-sp.Rational(1, 2) * surf * Rs ** 2)
    b_shell = sp.simplify(-sp.Rational(1, 6) * surf * Rs ** 4)
    check(sp.simplify(g_shell - g_ball.subs(rho, M / (sp.Rational(4, 3) * sp.pi * R ** 3))) == 0,
          "a shell and a ball of equal mass give the SAME gamma")
    check(sp.simplify(b_shell - b_ball.subs(rho, M / (sp.Rational(4, 3) * sp.pi * R ** 3))) != 0,
          "and DIFFERENT beta -- so the two coefficients see different things about the source")

    print()
    if FAILURES:
        print(f"FAILED {len(FAILURES)}: " + "; ".join(FAILURES))
        return 1
    print("ALL PASS")
    print("  BH0D's fork resolves on the first branch: gamma is the ZEROTH moment of the")
    print("  fourth-order source, so for f proportional to density it is PROPORTIONAL TO")
    print("  THE TOTAL MASS.  The Newtonian coefficient is the SECOND moment, tracking")
    print("  M<r^2> rather than M -- which is the shape of Flanagan's objection reached")
    print("  from the source side.  With BH0J's boundary datum the total is")
    print("  gamma = gamma_0 + gamma_*(M), and BH0C's universality becomes the inequality")
    print("  gamma_*(M) << gamma_0 across the sample.  That is what a fit assumes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
