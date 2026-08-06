"""BH-0f: costing the symmetry-breaking branch of the BH0E dilemma.

BH0E left two branches.  Branch two is the standard construction: conformal
symmetry is broken in the matter sector by a conformally coupled scalar
acquiring a vacuum expectation value, which generates a mass scale and lets
ordinary matter source the theory after all.

This costs that branch, and the cost is severe.

THE ARGUMENT, in three computed steps.

1.  For the conformally coupled scalar in D = 4,

        S_m = int sqrt(-g) [ (1/2)(dS)^2 - (1/12) R S^2 - lambda S^4 ]

    the scalar's own field equation is  box S + (1/6) R S + 4 lambda S^3 = 0.
    For a CONSTANT vacuum expectation value S = S0 != 0 that reduces to an
    algebraic condition forcing R to be CONSTANT:

        R = -24 lambda S0^2      (and R = 0 when lambda = 0).

    So a constant VEV does not merely add a scale -- it PINS THE RICCI
    SCALAR.

2.  For the forced Mannheim-Kazanas family the Ricci scalar is computed here
    (not asserted) and comes out

        R = 12 k - 6 gamma / r + 2 (1 - w) / r^2 .

3.  That is constant in r if and only if gamma = 0 AND w = 1.

Hence: A CONSTANT SCALAR VEV FORCES gamma = 0.  The linear potential --
the entire reason conformal gravity is of interest for rotation curves --
is incompatible with the simplest form of the symmetry breaking that was
supposed to rescue the matter coupling.

WHAT THAT DOES AND DOES NOT SHOW.  It does not refute the programme: a
working construction can take the scalar NON-CONSTANT.  What it shows is
that it MUST, and that moves the universality question.  With a
position-dependent scalar the profile is a property of each configuration,
so "is gamma universal?" becomes "is the scalar profile universal across
galaxies?" -- a question about the symmetry-breaking sector, and one with no
obvious reason to answer yes.

Run:  python3 bh0f_vev_forces_gamma_zero.py
"""

from __future__ import annotations

import sympy as sp

from weyl_geometry import Geometry, static_spherical_metric

FAILURES: list[str] = []


def check(cond: bool, label: str) -> None:
    print(("  PASS  " if cond else "  FAIL  ") + label)
    if not cond:
        FAILURES.append(label)


def main() -> int:
    t, r, th, ph = sp.symbols("t r theta phi")
    coords = [t, r, th, ph]
    w, u, gam, k = sp.symbols("w u gamma k")
    S0, lam = sp.symbols("S_0 lambda", positive=True)

    B = w - u / r + gam * r - k * r**2

    print("1. the Ricci scalar of the forced family, COMPUTED from the metric")
    geo = Geometry(coords, static_spherical_metric(B, 1 / B, r, th))
    R = sp.simplify(sp.expand(geo.Rscalar))
    print(f"     R = {R}")
    target = 12 * k - 6 * gam / r + 2 * (1 - w) / r**2
    check(sp.simplify(R - target) == 0, "R = 12k - 6 gamma/r + 2(1-w)/r^2")

    print("\n2. the 1/r^3 terms cancel -- u drops out entirely")
    check(sp.simplify(sp.diff(R, u)) == 0,
          "R does not depend on u (the Newtonian coefficient)")

    print("\n3. R is CONSTANT in r iff gamma = 0 and w = 1")
    dR = sp.simplify(sp.diff(R, r))
    check(sp.simplify(dR) != 0, "R is not automatically constant (non-vacuity)")
    # dR/dr = 0 for ALL r  <=>  every coefficient of the cleared polynomial vanishes.
    # Solving the polynomial rather than the rational expression is what makes this a
    # statement about all r instead of about the points where sympy happens to simplify.
    poly = sp.Poly(sp.simplify(dR * r**3), r)
    coeffs = poly.all_coeffs()
    conds = [sp.simplify(c) for c in coeffs if sp.simplify(c) != 0]
    print(f"     dR/dr = 0 for all r  <=>  {conds} all vanish")
    sol = sp.solve(conds, [gam, w], dict=True)
    check(len(sol) == 1 and sp.simplify(sol[0].get(gam, None) - 0) == 0,
          f"the unique solution has gamma = 0   [{sol}]")
    check(len(sol) == 1 and sp.simplify(sol[0].get(w, None) - 1) == 0,
          f"and w = 1   [{sol}]")

    print("\n4. the scalar field equation pins R for a CONSTANT vev")
    Sf = sp.Function("S")(r)
    Rs = sp.Symbol("R")
    # box S + (1/6) R S + 4 lambda S^3 = 0 ; for S = S0 constant the box term drops
    eq_const = sp.Rational(1, 6) * Rs * S0 + 4 * lam * S0**3
    Rsol = sp.solve(sp.Eq(eq_const, 0), Rs)
    check(len(Rsol) == 1 and sp.simplify(Rsol[0] - (-24 * lam * S0**2)) == 0,
          f"constant vev forces R = -24 lambda S0^2   [{Rsol}]")
    # lambda = 0 degenerates to R = 0, still constant
    check(sp.simplify(Rsol[0].subs(lam, 0)) == 0,
          "with lambda = 0 it degenerates to R = 0 -- still constant")

    print("\n5. THE CONCLUSION: constant vev => R constant => gamma = 0")
    R_at_gamma0_w1 = sp.simplify(R.subs({gam: 0, w: 1}))
    check(sp.simplify(sp.diff(R_at_gamma0_w1, r)) == 0,
          f"at gamma = 0, w = 1 the Ricci scalar is constant ( = {R_at_gamma0_w1} )")
    R_at_gamma_nonzero = sp.simplify(sp.diff(R.subs({w: 1}), r))
    check(sp.simplify(R_at_gamma_nonzero) != 0,
          "and with gamma != 0 it is NOT constant, so the implication is not vacuous")

    print("\n6. CONTROLS")
    # the Einstein locus of BH0 agrees: Einstein <=> gamma = 0 on the MK sheet
    check(sp.simplify(R.subs({gam: 0, w: 1}) - 12 * k) == 0,
          "the constant value is 12k, i.e. the (A)dS curvature -- consistent with BH0")
    # gamma genuinely controls the 1/r term and nothing else does
    check(sp.simplify(sp.diff(R, gam) + 6 / r) == 0,
          "gamma controls exactly the 1/r term of R")
    check(sp.simplify(sp.diff(R, k) - 12) == 0, "k controls exactly the constant term")

    print()
    if FAILURES:
        print(f"FAILED {len(FAILURES)}: " + "; ".join(FAILURES))
        return 1
    print("ALL PASS")
    print("  A CONSTANT scalar vev forces R constant, and R is constant on the forced")
    print("  family only when gamma = 0.  So the symmetry-breaking branch of the BH0E")
    print("  dilemma KILLS the linear potential unless the scalar is non-constant --")
    print("  and then 'is gamma universal?' becomes 'is the scalar PROFILE universal?'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
