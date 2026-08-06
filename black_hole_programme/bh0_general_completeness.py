"""BH-0b: completeness WITHOUT a Laurent ansatz.

BH0 certifies that within a six-term Laurent class the Bach equations force
c2 = c3 = 0 and w^2 + 3 u gamma = 1, and its own does_not_establish says
completeness beyond that class is "a literature target, not a repository
theorem".  This closes it, in the conformal gauge b = 1/B, for an ARBITRARY
C^4 function B.

THE STRUCTURE, which is what makes it closable.  With B unspecified, the
three independent Bach rows are not independent equations.  Writing

    L  :=  (r B)''''                                    -- LINEAR in B
    N  :=  2r^4(B B'''' + B'B''' ) - r^4 B''^2
           + 4r^3(B B''' + B'B'' ) - 4r^2(B B'' + B'^2)
           + 8r B B' - 4B^2 + 4                         -- nonlinear

they satisfy, as exact identities in B and its derivatives,

    B_thth  =  N / (24 r^2)
    B_tt    =  B  (N + 2 r^3 B L) / (24 r^4)
    B_rr    =  (-N + 2 r^3 B L) / (24 r^4 B)

so all three rows lie in the span of {N, r^3 B L}.  Hence for B nonvanishing

    Bach = 0   <=>   L = 0  AND  N = 0.

L = 0 is the LINEAR equation (rB)'''' = 0.  Substituting u = rB it is
u'''' = 0, whose solution space is exactly the cubics -- by four
integrations, with no ansatz and no assumption of Laurent form.  So

    B = c0/r + c1 + c2 r + c3 r^2

is FORCED, not chosen.  On that family N collapses to the constant
4(1 + 3 c0 c2 - c1^2), so the remaining content is the single algebraic
condition c1^2 - 3 c0 c2 = 1 -- which is BH0's w^2 + 3 u gamma = 1 in the
substitution c1 = w, c0 = -u, c2 = gamma, c3 = -k.

WHY THIS MATTERS BEYOND TIDINESS.  gamma = c2 is the coefficient of the
LINEAR POTENTIAL, and BH0's Einstein/extra split says the family is Einstein
exactly when gamma = 0.  So the linear potential is not a term appended to
fit rotation curves: it is one of the four coefficients of the general
solution of a linear fourth-order equation, and it is precisely the
non-Einstein content.

Run:  python3 bh0_general_completeness.py
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
    B = sp.Function("B")(r)
    d = lambda n: sp.diff(B, r, n)

    print("computing the Bach rows for an unspecified B(r) ...")
    geo = Geometry(coords, static_spherical_metric(B, 1 / B, r, th))
    Bach = geo.bach()
    tt, rr, thth = sp.simplify(Bach[0, 0]), sp.simplify(Bach[1, 1]), sp.simplify(Bach[2, 2])

    L = sp.diff(r * B, r, 4)
    N = (2 * r**4 * (B * d(4) + d(1) * d(3)) - r**4 * d(2) ** 2
         + 4 * r**3 * (B * d(3) + d(1) * d(2))
         - 4 * r**2 * (B * d(2) + d(1) ** 2)
         + 8 * r * B * d(1) - 4 * B**2 + 4)

    print("\n1. the three rows lie in the span of {N, r^3 B L}")
    check(sp.simplify(thth - N / (24 * r**2)) == 0, "B_thth = N / (24 r^2)")
    check(sp.simplify(tt - B * (N + 2 * r**3 * B * L) / (24 * r**4)) == 0,
          "B_tt   = B (N + 2 r^3 B L) / (24 r^4)")
    check(sp.simplify(rr - (-N + 2 * r**3 * B * L) / (24 * r**4 * B)) == 0,
          "B_rr   = (-N + 2 r^3 B L) / (24 r^4 B)")

    print("\n2. the span is two-dimensional, so the system really is {L = 0, N = 0}")
    # tt/B * (24 r^4) + rr * (24 r^4 B) = 4 r^3 B L  recovers L; thth recovers N.
    recover_L = sp.simplify((tt / B * 24 * r**4 + rr * 24 * r**4 * B) - 4 * r**3 * B * L)
    check(recover_L == 0, "L is recovered from the rows (so Bach = 0 forces L = 0)")
    check(sp.simplify(N - 24 * r**2 * thth) == 0,
          "N is recovered from the rows (so Bach = 0 forces N = 0)")
    check(sp.simplify(L) != 0, "L is not identically zero (the recovery is not vacuous)")
    check(sp.simplify(N) != 0, "N is not identically zero")

    print("\n3. L = 0 is LINEAR, so its solution space needs no ansatz")
    u = sp.Function("u")(r)
    Lu = sp.diff(r * (u / r), r, 4)
    check(sp.simplify(Lu - sp.diff(u, r, 4)) == 0,
          "substituting u = r B turns L = 0 into u'''' = 0")
    # linearity, checked rather than asserted
    f, g = sp.Function("f")(r), sp.Function("g")(r)
    lam, mu = sp.symbols("lambda mu")
    lin = sp.diff(r * (lam * f + mu * g), r, 4) - lam * sp.diff(r * f, r, 4) - mu * sp.diff(r * g, r, 4)
    check(sp.simplify(lin) == 0, "L is linear in B")

    print("\n4. the four powers solve it and are independent")
    c0, c1, c2, c3 = sp.symbols("c0 c1 c2 c3")
    basis = [1 / r, sp.Integer(1), r, r**2]
    for bi in basis:
        check(sp.simplify(sp.diff(r * bi, r, 4)) == 0, f"L[{bi}] = 0")
    W = sp.Matrix(4, 4, lambda i, j: sp.diff(basis[j], r, i))
    check(sp.simplify(W.det()) != 0, f"Wronskian nonzero (= {sp.simplify(W.det())})")

    print("\n5. on that family the remaining content is one algebraic condition")
    Bsol = c0 / r + c1 + c2 * r + c3 * r**2
    Nsol = sp.simplify(N.subs({B: Bsol}, simultaneous=True).doit())
    check(sp.simplify(Nsol - 4 * (1 + 3 * c0 * c2 - c1**2)) == 0,
          f"N on the general solution = 4(1 + 3 c0 c2 - c1^2)   [got {Nsol}]")
    for name, row in (("tt", tt), ("rr", rr), ("thth", thth)):
        val = sp.simplify(row.subs({B: Bsol}, simultaneous=True).doit())
        val = sp.simplify(val.subs(c1, sp.sqrt(1 + 3 * c0 * c2)))
        check(val == 0, f"row {name} vanishes on the constrained family")

    print("\n6. CONTROLS -- the conditions must be able to fail")
    # a non-Laurent B must NOT be Bach-flat, or the theorem is empty
    for probe in (sp.log(r), sp.exp(r), 1 / r**2, r**3):
        val = sp.simplify(sp.diff(r * probe, r, 4))
        check(val != 0, f"non-solution probe B = {probe} has L != 0")
    # the algebraic constraint must cut something out
    bad = sp.simplify(Nsol.subs({c0: 0, c1: 0, c2: 0}))
    check(bad != 0, f"the constraint is non-vacuous (c0=c1=c2=0 gives N = {bad})")
    # and it must admit solutions
    good = sp.simplify(Nsol.subs({c0: 1, c1: 2, c2: 1}))
    check(good == 0, "the constraint admits solutions (c0=1, c1=2, c2=1)")

    print()
    if FAILURES:
        print(f"FAILED {len(FAILURES)}: " + "; ".join(FAILURES))
        return 1
    print("ALL PASS -- (rB)'''' = 0 is forced, so B = c0/r + c1 + c2 r + c3 r^2")
    print("            is the GENERAL solution, not an ansatz; gamma = c2 is one of")
    print("            its four coefficients and is the non-Einstein content.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
