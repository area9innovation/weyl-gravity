"""BH-0j: the pair solves the coupled system, and the assumption has a name.

BH0H listed one thing as not established: that the profile realising its frame
change actually SOLVES the coupled scalar-plus-Bach system, rather than merely
realising a conformal map.  BH0I then computed which frame matter follows.
This closes the first, and the closure turns the whole line into a single named
assumption.

STEP 1 -- THE PAIR IS A SOLUTION.  In the frame where the scalar is constant
the conformally coupled action collapses to Einstein-Hilbert plus a
cosmological term, so its stress tensor is a multiple of the Einstein tensor
plus a multiple of the metric.  The gravitational equation is alpha W_ab =
(1/2) T_ab and the hatted metric is a Bach vacuum, W_ab = 0, so consistency
demands T_ab = 0 -- which for a constant scalar is exactly the demand that the
metric be an EINSTEIN SPACE.  The hatted metric is Schwarzschild-de Sitter,
which is Einstein, and the cosmological constant it carries is tied to lambda
S_0^2 by precisely BH0F's relation R = -24 lambda S_0^2.  So the pair is an
exact solution of the coupled system in the exterior, with nothing left over.

STEP 2 -- WHAT IS CONFORMALLY INVARIANT AND WHAT IS NOT.  BH0H's action reads
u -> u and gamma -> gamma - 2 w C - 3 u C^2.  The Newtonian coefficient is a
conformal INVARIANT of the solution; the linear coefficient is not.  A quantity
that is not invariant cannot be a function of one that is, so

    GAMMA IS NOT A FUNCTION OF THE MASS.

It needs a second datum, and BH0H identifies that datum exactly: C, the
scalar's fractional gradient, which is a boundary condition on the
symmetry-breaking sector and not a property of the galaxy.

STEP 3 -- SO THE ASSUMPTION IS NAMED, AND IT IS NOT A CONTRADICTION.  BH0C
requires gamma to be one constant across galaxies whose masses differ by orders
of magnitude.  Step 2 says gamma cannot depend on mass anyway, so that
requirement is not in tension with the structure -- it is the statement that
ONE BOUNDARY DATUM IS COMMON TO ALL GALAXIES while the mass varies freely.
That is consistent, it is not delivered by the gravitational theory, and it is
the whole of what a conformal-gravity rotation-curve fit assumes.

WHAT IS STILL NOT DONE.  The interior, and the matching that would fix C from a
given configuration, need a matter model this repository does not have.  What
is closed is the vacuum side: the exterior pair is a solution, the invariance
structure is computed, and the assumption is located on one number.

Run:  python3 bh0j_the_assumption_named.py
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
    u, kh, C = sp.symbols("u hat_k C")
    S0, lam = sp.symbols("S_0 lambda", positive=True)

    print("1. a constant scalar forces the metric to be an EINSTEIN space")
    # With S = S_0 constant the conformally coupled action is -(1/12) R S_0^2 - lambda S_0^4,
    # i.e. Einstein-Hilbert plus a cosmological term, so T_ab is a combination of G_ab and
    # g_ab.  The hatted metric is a Bach VACUUM, so alpha W_ab = (1/2) T_ab with W_ab = 0
    # forces T_ab = 0, which for constant S is the Einstein condition.
    Bhat = 1 - u / r - kh * r ** 2
    geo = Geometry(coords, static_spherical_metric(Bhat, 1 / Bhat, r, th))
    E = geo.einstein_defect()
    worst = [sp.simplify(E[a, b]) for a in range(4) for b in range(4)]
    check(all(e == 0 for e in worst),
          "the S-constant frame metric is Einstein (trace-free Ricci vanishes)")
    Rhat = sp.simplify(geo.Rscalar)
    print(f"     its Ricci scalar is R = {Rhat}")
    check(sp.simplify(Rhat - 12 * kh) == 0, "R = 12 hat_k, constant as BH0F requires")
    check(sp.simplify(sp.diff(Rhat, u)) == 0,
          "and independent of the mass coefficient u (consistency with BH0F)")

    print("\n2. the cosmological constant it carries is the scalar's own")
    # BH0F: a constant vev forces R = -24 lambda S_0^2.  Equating fixes hat_k.
    khat_sol = sp.solve(sp.Eq(Rhat, -24 * lam * S0 ** 2), kh)
    print(f"     R = -24 lambda S_0^2   =>   hat_k = {khat_sol[0]}")
    check(len(khat_sol) == 1 and sp.simplify(khat_sol[0] + 2 * lam * S0 ** 2) == 0,
          "hat_k = -2 lambda S_0^2 -- the de Sitter term IS the scalar potential")
    # non-vacuity: with lambda = 0 the space is Ricci-flat, not merely 'some Einstein space'
    check(sp.simplify(Rhat.subs(kh, khat_sol[0]).subs(lam, 0)) == 0,
          "lambda = 0 degenerates to R = 0, i.e. Schwarzschild (control)")

    print("\n3. so the exterior pair is an exact solution, with nothing left over")
    # Both halves hold simultaneously: Bach-flat (the gravity equation with T = 0) and
    # Einstein (the scalar's own requirement).  Checked together on the same metric.
    Bfix = Bhat.subs(kh, khat_sol[0])
    geo2 = Geometry(coords, static_spherical_metric(Bfix, 1 / Bfix, r, th))
    bach_zero = all(sp.simplify(geo2.bach()[a, b]) == 0 for a in range(4) for b in range(4))
    einstein_zero = all(sp.simplify(geo2.einstein_defect()[a, b]) == 0
                        for a in range(4) for b in range(4))
    check(bach_zero, "Bach-flat, so the gravitational equation holds with T_ab = 0")
    check(einstein_zero, "and Einstein, so the constant scalar's own equation holds")

    print("\n4. u is a conformal invariant and gamma is not")
    # BH0H's action, re-derived here from the map rather than imported, so this file does not
    # depend on the other one having been run.
    w, gam, k = sp.symbols("w gamma k")
    rhat = r / (1 - C * r)
    B = sp.expand(sp.simplify((r / rhat) ** 2
                              * (w - u / rhat + gam * rhat - k * rhat ** 2)))
    c = sp.Poly(sp.expand(B * r), r).all_coeffs()
    u_img, gam_img = sp.expand(-c[3]), sp.expand(c[1])
    check(sp.simplify(u_img - u) == 0, "u -> u under every member of the group")
    check(sp.simplify(sp.diff(gam_img, C)) != 0, "gamma moves with C")
    # the sharp consequence: gamma is not determined by u
    g_a = gam_img.subs({w: 1, gam: 0, C: sp.Rational(1, 2)})
    g_b = gam_img.subs({w: 1, gam: 0, C: sp.Rational(1, 3)})
    check(sp.simplify(g_a - g_b) != 0,
          "two frames with the SAME u carry different gamma, so gamma is not a function of u")

    print("\n5. THE ASSUMPTION, NAMED")
    print("     gamma is fixed by C, the scalar's fractional gradient, and u is fixed by the")
    print("     mass.  They are independent coordinates on the solution, so requiring gamma")
    print("     universal while u varies is CONSISTENT -- and is exactly one boundary datum")
    print("     assumed common to every galaxy.")
    # the two are genuinely independent: solve for (C, u) given any (gamma, u) pair
    tgt = sp.Symbol("gamma_target")
    sols = sp.solve(sp.Eq(gam_img.subs({w: 1, gam: 0}), tgt), C)
    check(len(sols) >= 1,
          f"for any target gamma and any u there is a C attaining it   [{len(sols)} branch(es)]")
    # and it is not vacuous: the C that does it depends on gamma, i.e. gamma really is free
    check(sp.simplify(sp.diff(sols[0], tgt)) != 0,
          "the required C varies with the target, so gamma is a free datum and not derived")

    print()
    if FAILURES:
        print(f"FAILED {len(FAILURES)}: " + "; ".join(FAILURES))
        return 1
    print("ALL PASS")
    print("  The exterior pair (metric, constant scalar) is an exact solution of the")
    print("  coupled system: Bach-flat AND Einstein, with the de Sitter term equal to the")
    print("  scalar potential.  So BH0H's profile is admissible, not merely a conformal")
    print("  relabelling.  And u is a conformal invariant while gamma is not, so gamma is")
    print("  not a function of the mass: it is set by one boundary datum on the")
    print("  symmetry-breaking sector.  Requiring it universal across galaxies is")
    print("  therefore consistent, un-delivered by gravity, and the whole of what a")
    print("  conformal-gravity rotation-curve fit assumes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
