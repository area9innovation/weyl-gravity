"""BH-0c: what the forced metric says about the Tully-Fisher scaling.

BH0B established that the linear potential coefficient gamma is one of four
coefficients of the GENERAL static spherically symmetric Bach-vacuum
solution -- forced, not chosen.  This asks the next question, which is the
cheap falsifier: given that form, what rotation-curve scaling follows, and
is it the observed one?

THE POINT IS A CONDITIONAL, NOT A FIT.  Nothing here is fitted to any
galaxy.  What is computed is the algebraic consequence of the forced metric,
and the conclusion has the shape of a reverse-physics statement:

    the baryonic Tully-Fisher relation v^4 proportional to M FORCES gamma to
    be a UNIVERSAL CONSTANT, and identifies it with MOND's acceleration
    scale as gamma = a0 / (2 c^2).

Turned around, that is a falsifier: if fitting galaxies requires gamma to
carry a mass-dependent piece, the predicted Tully-Fisher slope moves off the
observed one.  gamma proportional to M gives v^4 proportional to M^2.

WHAT IS ALGEBRA AND WHAT IS NOT.  Everything below the line "exact algebra"
is exact and certified.  The identification with a0, and any numerical
comparison with fitted values in the literature, are NOT computed here and
are NOT certified -- they are stated as the consequence of the algebra plus
an observational input, and the observational input is not this
repository's.

Run:  python3 bh0c_tully_fisher_scaling.py
"""

from __future__ import annotations

import sympy as sp

FAILURES: list[str] = []


def check(cond: bool, label: str) -> None:
    print(("  PASS  " if cond else "  FAIL  ") + label)
    if not cond:
        FAILURES.append(label)


def main() -> int:
    r, beta, gam, k, c = sp.symbols("r beta gamma k c", positive=True)
    M, G, a0 = sp.symbols("M G a_0", positive=True)

    # the forced solution, in Mannheim-Kazanas normalisation:
    # c0 = -2 beta, c1 = 1, c2 = gamma, c3 = -k, with beta = G M / c^2
    B = 1 - 2 * beta / r + gam * r - k * r**2

    print("1. circular orbits: the exact condition reduces to the weak-field one")
    v2_exact = r * sp.diff(B, r) / (2 * B)          # locally measured v^2/c^2
    v2_weak = sp.expand(r * sp.diff(B, r) / 2)
    check(sp.simplify(v2_weak - (beta / r + gam * r / 2 - k * r**2)) == 0,
          "v^2/c^2 = beta/r + gamma r/2 - k r^2  (weak field)")
    # The weak field is B -> 1, i.e. SMALL DEVIATION, not small beta alone: scale all three
    # parameters by eps and compare the O(eps) terms.  The first draft of this check compared
    # at beta -> 0 with gamma and k left finite, which is not a weak field at all -- it fails,
    # and rightly, because r gamma /(2(1 + gamma r)) is not r gamma / 2.
    eps = sp.Symbol("epsilon", positive=True)
    scale = {beta: eps * beta, gam: eps * gam, k: eps * k}
    ex = sp.series(v2_exact.subs(scale), eps, 0, 2).removeO()
    wk = sp.series(v2_weak.subs(scale), eps, 0, 2).removeO()
    check(sp.simplify(sp.expand(ex - wk)) == 0,
          "exact and weak-field agree to first order in the field strength")

    print("\n2. the rotation curve has a STATIONARY POINT, and it is a minimum")
    v2 = beta / r + gam * r / 2                     # k = 0: the galactic regime
    dv2 = sp.simplify(sp.diff(v2, r))
    rstar = sp.simplify(sp.solve(sp.Eq(dv2, 0), r)[0])
    check(sp.simplify(rstar - sp.sqrt(2 * beta / gam)) == 0,
          f"stationary radius r* = sqrt(2 beta / gamma)   [got {rstar}]")
    d2 = sp.simplify(sp.diff(v2, r, 2).subs(r, rstar))
    check(sp.simplify(d2) > 0,
          f"it is a MINIMUM (second derivative {sp.simplify(d2)} > 0)")

    print("\n3. the value there -- this is the scaling law")
    v2star = sp.simplify(v2.subs(r, rstar))
    check(sp.simplify(v2star - sp.sqrt(2 * beta * gam)) == 0,
          f"v^2/c^2 at the minimum = sqrt(2 beta gamma)   [got {v2star}]")
    v4 = sp.simplify(v2star**2)
    check(sp.simplify(v4 - 2 * beta * gam) == 0, f"so v^4/c^4 = 2 beta gamma   [got {v4}]")
    # restore beta = G M / c^2 :  v^4 = 2 G M gamma c^2
    v4_phys = sp.simplify((v4 * c**4).subs(beta, G * M / c**2))
    check(sp.simplify(v4_phys - 2 * G * M * gam * c**2) == 0,
          f"v^4 = 2 G M gamma c^2   [got {v4_phys}]")

    print("\n4. THE CONDITIONAL.  v^4 proportional to M  <=>  gamma independent of M")
    # universal gamma -> Tully-Fisher slope exactly 4
    slope_universal = sp.simplify(sp.diff(v4_phys, M) * M / v4_phys)
    check(sp.simplify(slope_universal - 1) == 0,
          "with gamma universal, v^4 is exactly LINEAR in M (BTFR slope 4 in v)")
    # gamma carrying a mass-proportional piece -> wrong slope
    gstar = sp.Symbol("gamma_star", positive=True)
    v4_massdep = sp.simplify(v4_phys.subs(gam, gstar * M))
    slope_massdep = sp.simplify(sp.diff(v4_massdep, M) * M / v4_massdep)
    check(sp.simplify(slope_massdep - 2) == 0,
          f"with gamma proportional to M, v^4 goes as M^2 -- the WRONG slope [{slope_massdep}]")

    print("\n5. the identification with MOND's scale, given BTFR as input")
    sol = sp.solve(sp.Eq(2 * G * M * gam * c**2, G * M * a0), gam)
    check(len(sol) == 1 and sp.simplify(sol[0] - a0 / (2 * c**2)) == 0,
          f"matching v^4 = G M a_0 forces gamma = a_0/(2 c^2)   [got {sol}]")

    print("\n6. CONTROLS")
    # gamma -> 0 must destroy the stationary point: pure Newtonian has none
    newt = sp.simplify(sp.diff(beta / r, r))
    check(sp.solve(sp.Eq(newt, 0), r) == [],
          "with gamma = 0 there is NO stationary radius (pure Newtonian, no flat part)")
    # the curve RISES beyond r*, which is a qualitative departure from MOND
    rise = sp.simplify(sp.diff(v2, r).subs(r, 2 * rstar))
    check(sp.simplify(rise) > 0,
          f"beyond r* the curve RISES (dv^2/dr at 2r* = {sp.simplify(rise)} > 0)")
    # and the k term is what must bend it back
    v2k = beta / r + gam * r / 2 - k * r**2
    check(sp.simplify(sp.diff(v2k, r) - (sp.diff(v2, r) - 2 * k * r)) == 0,
          "the -k r^2 term is the only thing available to bend the rise back down")
    # non-vacuity: the scaling law is not trivially zero or independent of M
    check(sp.simplify(v4_phys.subs(M, 0)) == 0 and sp.diff(v4_phys, M) != 0,
          "the scaling law genuinely depends on M")

    print()
    if FAILURES:
        print(f"FAILED {len(FAILURES)}: " + "; ".join(FAILURES))
        return 1
    print("ALL PASS")
    print("  v^4 = 2 G M gamma c^2 at the flattest point of the rotation curve.")
    print("  BTFR (v^4 proportional to M) therefore FORCES gamma universal, and")
    print("  identifies it with MOND's scale as gamma = a_0/(2 c^2).")
    print("  A mass-dependent gamma gives v^4 proportional to M^2 -- falsifiable.")
    print("  NOT certified here: any numerical value of a_0 or of fitted gamma.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
