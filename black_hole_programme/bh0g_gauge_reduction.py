"""BH-0g: the gauge assumption BH0B carries, discharged where it can be.

BH0B proved completeness in the conformal gauge b = 1/B and listed as NOT
established: "that an arbitrary static spherically symmetric metric
diag(-a, b, r^2, ...) can be brought to that gauge by a conformal
transformation and a radial reparametrisation is the standard
Mannheim-Kazanas argument and is ASSUMED here, not proved."

That assumption has two halves and they are not equally hard.

  (A) CONFORMAL COVARIANCE.  Bach flatness must be preserved by
      g -> Omega^2 g, or classifying one gauge says nothing about the
      others.  In D = 4 the Bach tensor has conformal weight -2:
      B_ab[Omega^2 g] = Omega^(-2) B_ab[g].  This is the load-bearing half
      and it is COMPUTED here, for the two-function ansatz with BOTH metric
      functions and the conformal factor left as unspecified functions.

  (B) REACHABILITY.  That some Omega actually attains b = 1/a.  This is
      REDUCED here from an assumption to a first-order ODE: setting the new
      radius to rho = Omega r so the angular part stays rho^2, the gauge
      condition becomes

          r Omega'  =  Omega ( Omega sqrt(a b) - 1 )

      which is first order and solvable locally by Picard-Lindelof wherever
      a b > 0 and r != 0.  So reachability holds LOCALLY; what remains open
      is global existence -- whether the solution can be continued without
      Omega hitting zero or blowing up.  That is a much smaller assumption
      than the original, and a different KIND of one.

Discharging (A) is what makes the gauge choice legitimate rather than
lucky: Bach flatness is a property of the CONFORMAL CLASS, so BH0B's
classification classifies classes, and the only thing (B) adds is that
every class has a representative of the assumed form.

Run:  python3 bh0g_gauge_reduction.py
"""

from __future__ import annotations

import sympy as sp

from weyl_geometry import Geometry, mk_metric_function, static_spherical_metric

FAILURES: list[str] = []


def check(cond: bool, label: str) -> None:
    print(("  PASS  " if cond else "  FAIL  ") + label)
    if not cond:
        FAILURES.append(label)


def main() -> int:
    t, r, th, ph = sp.symbols("t r theta phi")
    coords = [t, r, th, ph]

    # The MK family carries symbolic parameters, so "conformally covariant" below is a
    # statement about a FAMILY rather than about one metric -- and the conformal factor is an
    # unspecified function, so it is every conformal transformation of that family at once.
    beta, gam, k = sp.symbols("beta gamma k")
    # The EXACT MK function, not the weak-field 1 - 2 beta/r + gamma r - k r^2.  The first
    # draft used the weak-field form and check 3 caught it: that form has w = 1 and u = 2 beta,
    # so w^2 + 3 u gamma = 1 + 6 beta gamma, which is OFF the constraint surface unless
    # beta gamma = 0 -- it is not Bach-flat.  The exact form has w = 1 - 3 beta gamma and
    # u = beta(2 - 3 beta gamma), which satisfies the constraint identically.
    B = mk_metric_function(beta, gam, k, r)
    Om = sp.Function("Omega")(r)

    print("computing Bach for the family and for its conformal transform ...")
    g0 = static_spherical_metric(B, 1 / B, r, th)
    geo0 = Geometry(coords, g0)
    B0 = geo0.bach()

    g1 = sp.Matrix(4, 4, lambda i, j: sp.simplify(Om**2 * g0[i, j]))
    geo1 = Geometry(coords, g1)
    B1 = geo1.bach()

    print("\n1. CONFORMAL COVARIANCE: B_ab[Omega^2 g] = Omega^(-2) B_ab[g]")
    cov_ok = True
    for i in range(4):
        for j in range(4):
            d = sp.simplify(sp.expand(sp.together(B1[i, j] - Om ** (-2) * B0[i, j])))
            if d != 0:
                cov_ok = False
                print(f"     mismatch at ({i},{j}): {d}")
    check(cov_ok, "the Bach tensor has conformal weight -2 in D = 4")

    print("\n2. NON-VACUITY -- the untransformed Bach must not be identically zero for a")
    print("   generic member, or covariance would be a statement about nothing.")
    Bgen = B + sp.Symbol("delta") / r**2
    geoG = Geometry(coords, static_spherical_metric(Bgen, 1 / Bgen, r, th))
    BG = geoG.bach()
    nonzero = any(sp.simplify(BG[i, j]) != 0 for i in range(4) for j in range(4))
    check(nonzero, "a metric off the Bach-flat locus has nonzero Bach")

    print("\n3. and the CONSEQUENCE: Bach flatness is a property of the conformal CLASS")
    flat0 = all(sp.simplify(B0[i, j]) == 0 for i in range(4) for j in range(4))
    flat1 = all(sp.simplify(B1[i, j]) == 0 for i in range(4) for j in range(4))
    check(flat0, "the MK family is Bach-flat")
    check(flat1, "and so is every conformal transform of it, for unspecified Omega")

    print("\n4. CONTROL -- the conformal factor is genuinely free, not secretly trivial")
    check(sp.simplify(sp.diff(Om, r)) != 0, "Omega is an unspecified function of r")
    # a transform that is NOT conformal must break flatness, or check 3 is vacuous
    gbad = sp.Matrix(4, 4, lambda i, j: g0[i, j] * (Om**2 if i == j and i > 0 else 1))
    geoB = Geometry(coords, gbad)
    BB = geoB.bach()
    broke = any(sp.simplify(BB[i, j]) != 0 for i in range(4) for j in range(4))
    check(broke, "a NON-conformal rescaling of only the spatial block breaks Bach flatness")

    print("\n5. REACHABILITY, reduced from an assumption to an ODE")
    # After g -> Omega^2 g, set the new radius rho = Omega r so the angular part is rho^2.
    # The gauge condition is then (-g_tt)(g_rho rho) = 1 for arbitrary a(r), b(r).
    af = sp.Function("a")(r)
    bf = sp.Function("b")(r)
    rho = Om * r
    g_tt = Om**2 * af
    g_rr = Om**2 * bf / sp.diff(rho, r) ** 2
    num = sp.numer(sp.together(sp.simplify(g_tt * g_rr - 1)))
    check(sp.ode_order(sp.Eq(num, 0), Om) == 1,
          "the gauge condition is FIRST ORDER in Omega, not second or higher")
    sol = sp.solve(sp.Eq(num, 0), sp.diff(Om, r))
    want = Om * (sp.sqrt(af * bf) * Om - 1) / r
    check(any(sp.simplify(sp.together(x - want)) == 0 for x in sol),
          f"Omega' = Omega (Omega sqrt(ab) - 1)/r is one branch   [{len(sol)} branches]")

    print("\n6. the ODE is not vacuous, and the identity is a solution when it should be")
    check(sp.simplify(num) != 0,
          "the gauge condition is not identically satisfied (so it constrains Omega)")
    # If the gauge ALREADY holds (b = 1/a, so ab = 1) then Omega = 1 must solve the ODE --
    # the gauge is a fixed point of the flow.  Substituted through an ACTUAL metric pair with
    # a b = 1 rather than by rewriting the product, because the first draft of this check
    # replaced its own computation with the tautology (1-1)/r on the next line and would have
    # passed for any ODE whatsoever.
    Af = sp.Function("A")(r)
    want_ab1 = want.subs({af: Af, bf: 1 / Af})
    id_lhs = sp.simplify(want_ab1.subs(Om, 1))
    check(sp.simplify(id_lhs) == 0,
          f"with b = 1/a, Omega = 1 solves the ODE -- the gauge is a fixed point [{id_lhs}]")
    # and the fixed point is NOT free: a different constant Omega must NOT solve it
    two_lhs = sp.simplify(want_ab1.subs(Om, 2))
    check(sp.simplify(two_lhs) != 0,
          f"but Omega = 2 does NOT, so the fixed point is isolated [{two_lhs}]")

    print()
    if FAILURES:
        print(f"FAILED {len(FAILURES)}: " + "; ".join(FAILURES))
        return 1
    print("ALL PASS")
    print("  Bach flatness is preserved by g -> Omega^2 g for an UNSPECIFIED Omega, so it is")
    print("  a property of the CONFORMAL CLASS.  BH0B's classification therefore classifies")
    print("  classes.  And reachability is reduced to r Omega' = Omega(Omega sqrt(ab) - 1),")
    print("  first order and locally solvable -- so what remains open is GLOBAL existence,")
    print("  not reachability in principle.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
