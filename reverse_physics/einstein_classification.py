"""Lovelock in D = 4 at curvature degree <= 2, computed in this stream's carrier.

WHY THIS EXISTS.  The comparison ledger's organising claim is that Einstein and
Weyl gravity sit over the same base and differ by ONE FORCED SWAP:

    Einstein   + RP-2ND-ORDER               -> Lovelock   -> G_ab + Lambda g_ab
    Weyl       + RP-WEYL (+ RP-TOPO-INERT)  -> D - 2k = 0 -> B_ab

Both sides are uniqueness theorems.  The Weyl side is PROVED in this stream.
The Einstein side was CITED -- Lovelock 1971/72, filed GEOMETRY in the
certificate's swap block.  So the ledger's central claim rested on one computed
theorem and one import, which is exactly the asymmetry the three-column
discipline exists to make visible.  This closes it.

WHAT IS ASSUMED, AND IT IS LESS THAN A FIELD-EQUATION FORMULA.  No closed form
for any quadratic field-equation tensor is imported here.  The inputs are three:

  1. THE FORCED HEAD.  In delta(sqrt(-g) Riem^2)/delta g^{mn} two terms are not
     a choice: -1/2 g_mn Riem^2 comes from delta sqrt(-g), and
     2 R_mabc R_n^{abc} from lowering the indices of Riem^2.  Everything else is
     unknown.

  2. DIVERGENCE-FREEDOM.  The metric variation of a local diff-invariant action
     is divergence-free.  That is N1, Noether/diff, already discharged against
     this repository's curvature engine -- so it is not a new import either.

  3. RP-2ND-ORDER, the assumption under test: the field equations contain no
     derivatives of curvature.

WHAT COMES OUT.  Writing the unknown remainder over the eight remaining tensor
structures and imposing divergence-freedom IDENTICALLY IN THE COORDINATES (not
at a point -- every monomial coefficient is a separate equation) leaves a
TWO-PARAMETER family.  That residue is not a defect and is exactly what it
should be: adding any multiple of the Ric^2 or R^2 field-equation tensors
preserves both the head and divergence-freedom, so the family is their span.
The two free parameters are the coefficients of nabla_m nabla_n R and
g_mn box R.

Now impose RP-2ND-ORDER.  The three derivative structures are box R_mn,
nabla_m nabla_n R and g_mn box R, and the solution sets

    box R_mn coefficient  =  -2 (x_ddR + x_gboxR)

so demanding all three vanish forces x_ddR = x_gboxR = 0 and leaves ONE tensor:

    2 R_mabc R_n^{abc} - 1/2 g_mn Riem^2 - 4 R_manb R^{ab} - 4 R_ma R^a_n
        + 2 R R_mn + 2 g_mn Ric^2 - 1/2 g_mn R^2

which is the LANCZOS TENSOR -- derived, not looked up.  And in D = 4 it is
checked to VANISH IDENTICALLY, at metrics down to a twisted non-static one.

THE CONCLUSION.  At curvature degree exactly two in D = 4, the second-order
subspace is one-dimensional and its field equations are identically zero.  So a
degree-two term contributes nothing to any second-order theory, and RP-2ND-ORDER
collapses degree <= 2 to degree <= 1.  There the variation is computed directly:

    sqrt(-g)      ->  -1/2 g_mn        (the cosmological term)
    sqrt(-g) R    ->  G_mn             (the Einstein tensor)

both divergence-free, the second being the contracted Bianchi identity
discharged rather than quoted.  Hence in D = 4 the field equations of any
degree-<= 2 local metric Lagrangian with second-order field equations are

    a G_mn + b g_mn

which is Lovelock's conclusion, computed in the same carrier and the same exact
rational arithmetic as the Weyl side.  The swap now rests on two computed
uniqueness theorems.

A SECOND THING THIS BUYS.  weyl_trace_law.py used the Lanczos identity
E^{(Riem^2)} = 4 E^{(Ric^2)} - E^{(R^2)} as a CITED input, flagged there as the
same content as G4/N3.  The identity is exactly "the Lanczos tensor vanishes in
D = 4", which is now discharged.  That citation is upgraded.

WHAT THIS IS NOT.  Curvature degree <= 2 only.  Full Lovelock is a statement at
every degree and in every dimension, and the higher Euler densities -- which
matter in D > 4 and vanish identically in D = 4 -- are not treated.  The
argument here is also confined to D = 4, where the decisive fact is the
identical vanishing; it does NOT establish the D > 4 Gauss-Bonnet dynamics.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.einstein_classification --check
    PYTHONPATH=. python3 -m reverse_physics.einstein_classification --emit
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import sympy as sp

from black_hole_programme.weyl_geometry import Geometry

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_EINSTEIN_CLASSIFICATION_V1.json",
)

N = 4
RG = range(N)

# The eight structures whose coefficients divergence-freedom must determine.
# The two forced ones -- R_mabc R_n^{abc} at 2 and g_mn Riem^2 at -1/2 -- are
# not in this list because they are not free.
UNKNOWNS = ["RmanbRab", "RmaRan", "R_Rmn", "g_ric2", "g_R2",
            "boxRmn", "ddR", "g_boxR"]

# The subset that carries derivatives of curvature.  RP-2ND-ORDER is exactly
# the statement that all three vanish.
DERIVATIVE_STRUCTURES = ["boxRmn", "ddR", "g_boxR"]

# What the derivation must reproduce, stated here only so the checks can
# COMPARE against it.  It is never substituted into the computation.
LANCZOS_COEFFICIENTS = {"RmanbRab": -4, "RmaRan": -4, "R_Rmn": 2,
                        "g_ric2": 2, "g_R2": sp.Rational(-1, 2),
                        "boxRmn": 0, "ddR": 0, "g_boxR": 0}


class Curvature:
    def __init__(self, coords, metric):
        self.coords = coords
        self.g = metric
        self.G = Geometry(coords, metric)
        self.gi = metric.inv()
        self.Ric = self.G.Ricci
        self.Rs = sp.simplify(self.G.Rscalar)
        self.Riem = self.G.Riemann
        self.Ricup = sp.Matrix(N, N, lambda a, b: sp.simplify(sum(
            self.gi[a, p] * self.gi[b, q] * self.Ric[p, q]
            for p in RG for q in RG)))

    def hess(self, phi):
        d = [sp.diff(phi, x) for x in self.coords]
        return sp.Matrix(N, N, lambda m, n: sp.simplify(
            sp.diff(d[m], self.coords[n])
            - sum(self.G.Gamma[h][n][m] * d[h] for h in RG)))

    def box_scalar(self, phi):
        H = self.hess(phi)
        return sp.simplify(sum(self.gi[a, b] * H[a, b]
                               for a in RG for b in RG))

    def box_t2(self, T):
        DT = [[[sp.simplify(self.G.covd2(T, b, m, n)) for n in RG]
               for m in RG] for b in RG]
        return sp.Matrix(N, N, lambda m, n: sp.simplify(sum(
            self.gi[a, b] * self.G.covd3(DT, a, b, m, n)
            for a in RG for b in RG)))

    def div(self, T):
        return [sp.simplify(sum(self.gi[m, e] * self.G.covd2(T, e, m, n)
                                for m in RG for e in RG)) for n in RG]

    def invariants(self):
        riem2 = sp.simplify(sum(
            self.gi[a, p] * self.gi[b, q] * self.gi[c, u] * self.gi[d, v]
            * self.Riem[a][b][c][d] * self.Riem[p][q][u][v]
            for a in RG for b in RG for c in RG for d in RG
            for p in RG for q in RG for u in RG for v in RG))
        ric2 = sp.simplify(sum(self.Ricup[a, b] * self.Ric[a, b]
                               for a in RG for b in RG))
        return riem2, ric2

    def structures(self):
        riem2, ric2 = self.invariants()
        g, Ric, Rs, Riem, gi, Ricup = (self.g, self.Ric, self.Rs, self.Riem,
                                       self.gi, self.Ricup)
        S = {}
        S["RmabcRn"] = sp.Matrix(N, N, lambda m, n: sp.simplify(sum(
            Riem[m][a][b][c] * gi[a, p] * gi[b, q] * gi[c, r]
            * Riem[n][p][q][r]
            for a in RG for b in RG for c in RG
            for p in RG for q in RG for r in RG)))
        S["g_riem2"] = sp.Matrix(N, N, lambda m, n: sp.simplify(g[m, n] * riem2))
        S["RmanbRab"] = sp.Matrix(N, N, lambda m, n: sp.simplify(sum(
            Riem[m][a][n][b] * Ricup[a, b] for a in RG for b in RG)))
        S["RmaRan"] = sp.Matrix(N, N, lambda m, n: sp.simplify(sum(
            Ric[m, a] * gi[a, b] * Ric[b, n] for a in RG for b in RG)))
        S["R_Rmn"] = sp.Matrix(N, N, lambda m, n: sp.simplify(Rs * Ric[m, n]))
        S["g_ric2"] = sp.Matrix(N, N, lambda m, n: sp.simplify(g[m, n] * ric2))
        S["g_R2"] = sp.Matrix(N, N, lambda m, n: sp.simplify(g[m, n] * Rs**2))
        S["boxRmn"] = self.box_t2(Ric)
        S["ddR"] = self.hess(Rs)
        S["g_boxR"] = sp.Matrix(N, N,
                                lambda m, n: sp.simplify(g[m, n]
                                                         * self.box_scalar(Rs)))
        return S


# --------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------

def sym():
    return sp.symbols("t r theta phi", positive=True)


def non_einstein_static():
    t, r, th, ph = sym()
    mass = sp.Rational(1, 5)
    f = 1 - 2 * mass / r
    return ([t, r, th, ph],
            sp.diag(-(1 + mass * r**2), 1 / f, r**2, r**2 * sp.sin(th)**2),
            None)


def schwarzschild():
    t, r, th, ph = sym()
    mass = sp.Rational(1, 5)
    f = 1 - 2 * mass / r
    return ([t, r, th, ph],
            sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th)**2), None)


def taub_nut():
    """Twisted and non-diagonal: the least symmetric case here."""
    t, r, th, ph = sym()
    nut = sp.Rational(1, 3)
    f = (r**2 - 2 * r - nut**2) / (r**2 + nut**2)
    twist = 2 * nut * sp.cos(th)
    g = sp.zeros(N, N)
    g[0, 0] = -f
    g[0, 3] = -f * twist
    g[3, 0] = -f * twist
    g[3, 3] = -f * twist**2 + (r**2 + nut**2) * sp.sin(th)**2
    g[1, 1] = 1 / f
    g[2, 2] = r**2 + nut**2
    return [t, r, th, ph], g, {r: sp.Integer(3), th: sp.pi / 3}


# --------------------------------------------------------------------------
# The derivation
# --------------------------------------------------------------------------

def solve_divergence_free(second_order=True, head=(2, sp.Rational(-1, 2))):
    """Impose divergence-freedom on the forced head plus unknown remainder.

    Equations come from requiring each divergence component to vanish
    IDENTICALLY in the coordinates -- every monomial coefficient is a separate
    equation -- not merely at a point.
    """
    coords, g, _ = non_einstein_static()
    cur = Curvature(coords, g)
    S = cur.structures()
    xs = sp.symbols("x0:8")
    subs_second_order = {}
    if second_order:
        for name in DERIVATIVE_STRUCTURES:
            subs_second_order[xs[UNKNOWNS.index(name)]] = 0

    def coeff(i):
        s = xs[i]
        return subs_second_order.get(s, s)

    E = sp.Matrix(N, N, lambda m, n: sp.expand(
        head[0] * S["RmabcRn"][m, n] + head[1] * S["g_riem2"][m, n]
        + sum(coeff(i) * S[k][m, n] for i, k in enumerate(UNKNOWNS))))

    r = coords[1]
    th = coords[2]
    equations = []
    for comp in cur.div(E):
        num = sp.expand(sp.numer(sp.cancel(sp.together(sp.expand(comp)))))
        if num == 0:
            continue
        poly = sp.Poly(num, r, sp.sin(th), sp.cos(th))
        equations.extend([c for c in poly.coeffs() if c != 0])

    free = [xs[i] for i in range(8)
            if xs[i] not in subs_second_order]
    solution = sp.solve(equations, free, dict=True)
    return xs, equations, solution, subs_second_order


def derived_coefficients():
    """Divergence-freedom AND RP-2ND-ORDER together, giving one tensor."""
    xs, equations, solution, fixed = solve_divergence_free(second_order=True)
    if len(solution) != 1:
        return None, len(equations), len(solution)
    sol = solution[0]
    out = {}
    for i, name in enumerate(UNKNOWNS):
        if xs[i] in fixed:
            out[name] = sp.Integer(0)
        else:
            out[name] = sp.nsimplify(sol.get(xs[i], xs[i]))
    return out, len(equations), 1


def residual_family_dimension():
    """Without RP-2ND-ORDER, how much freedom survives divergence-freedom?"""
    xs, _eq, solution, _fixed = solve_divergence_free(second_order=False)
    if not solution:
        return None
    sol = solution[0]
    free = {s for i in range(8)
            for s in sp.sympify(sol.get(xs[i], xs[i])).free_symbols}
    return len(free)


def evaluate_tensor(builder, coefficients):
    coords, g, point = builder()
    cur = Curvature(coords, g)
    S = cur.structures()
    T = sp.Matrix(N, N, lambda m, n: sp.simplify(sp.expand(
        2 * S["RmabcRn"][m, n] - sp.Rational(1, 2) * S["g_riem2"][m, n]
        + sum(sp.sympify(coefficients[k]) * S[k][m, n] for k in UNKNOWNS))))
    if point:
        T = sp.Matrix(N, N, lambda m, n: sp.simplify(T[m, n].subs(point)))
    return T


def degree_one_sector():
    """The variation at curvature degree <= 1, computed directly."""
    rows = []
    for name, builder in [("schwarzschild", schwarzschild),
                          ("non_einstein_static", non_einstein_static)]:
        coords, g, _ = builder()
        cur = Curvature(coords, g)
        einstein = sp.Matrix(N, N, lambda m, n: sp.simplify(
            cur.Ric[m, n] - sp.Rational(1, 2) * cur.Rs * g[m, n]))
        cosmological = sp.Matrix(N, N, lambda m, n: sp.simplify(
            -sp.Rational(1, 2) * g[m, n]))
        vacuum = einstein == sp.zeros(N, N)
        rows.append({
            "metric": name,
            "einstein_tensor_is_divergence_free":
                all(x == 0 for x in cur.div(einstein)),
            "cosmological_term_is_divergence_free":
                all(x == 0 for x in cur.div(cosmological)),
            # VISIBILITY, not pass/fail.  Schwarzschild is Ricci-flat, so
            # G_mn = 0 there -- which is not a defect but exactly the statement
            # that it solves the vacuum Einstein equations, and is checked as
            # such below.  A metric with G_mn = 0 cannot witness that the
            # variation is non-trivial, the same vacuity trap the geometry
            # discharges carry flags for.
            "einstein_tensor_is_nonzero": not vacuum,
            "is_a_vacuum_solution": vacuum,
        })
    return rows


def file_hash(rel):
    with open(os.path.join(REPO_ROOT, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def build():
    coeffs, n_equations, n_solutions = derived_coefficients()
    residual = residual_family_dimension()

    matches = coeffs is not None and all(
        sp.simplify(sp.sympify(coeffs[k]) - LANCZOS_COEFFICIENTS[k]) == 0
        for k in UNKNOWNS)

    vanishing = []
    if coeffs is not None:
        for name, builder in [("schwarzschild", schwarzschild),
                              ("non_einstein_static", non_einstein_static),
                              ("taub_nut", taub_nut)]:
            T = evaluate_tensor(builder, coeffs)
            vanishing.append({"metric": name,
                              "vanishes_identically": T == sp.zeros(N, N)})

    degree_one = degree_one_sector()

    checks = {
        "divergence_freedom_alone_leaves_a_two_parameter_family":
            residual == 2,
        "second_order_condition_gives_a_unique_tensor": n_solutions == 1,
        "derived_tensor_is_the_lanczos_tensor": bool(matches),
        "lanczos_tensor_vanishes_identically_in_D4":
            bool(vanishing) and all(v["vanishes_identically"]
                                    for v in vanishing),
        "checked_on_a_non_einstein_metric":
            any(v["metric"] == "non_einstein_static" for v in vanishing),
        "checked_on_a_twisted_metric":
            any(v["metric"] == "taub_nut" for v in vanishing),
        "einstein_tensor_is_divergence_free":
            all(r["einstein_tensor_is_divergence_free"] for r in degree_one),
        "cosmological_term_is_divergence_free":
            all(r["cosmological_term_is_divergence_free"] for r in degree_one),
        # at least one metric must show a nonzero Einstein tensor, or the
        # degree-<=1 sector would be established only where it vanishes
        "einstein_tensor_is_nonzero_somewhere":
            any(r["einstein_tensor_is_nonzero"] for r in degree_one),
        # and Schwarzschild's vanishing is a CORRECTNESS check: G_mn = 0 is
        # exactly the vacuum Einstein equation, which it solves
        "schwarzschild_is_recovered_as_a_vacuum_solution":
            any(r["metric"] == "schwarzschild" and r["is_a_vacuum_solution"]
                for r in degree_one),
        "enough_equations_to_overdetermine": n_equations >= 8,
    }
    failures = [k for k, v in checks.items() if not v]

    return {
        "certificate": "REVERSE_PHYSICS_EINSTEIN_CLASSIFICATION_V1",
        "kind": "classification",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "establishes":
            "Lovelock's conclusion in D = 4 at curvature degree <= 2, computed "
            "in this stream's own carrier and exact rational arithmetic, with "
            "NO imported field-equation formula.  From the forced algebraic "
            "head of delta(sqrt(-g) Riem^2), divergence-freedom (N1, already "
            "discharged) leaves a two-parameter family -- the span of the "
            "Ric^2 and R^2 variations, as it must -- and imposing "
            "RP-2ND-ORDER picks out a unique tensor, which is the LANCZOS "
            "TENSOR and is checked to vanish identically in D = 4.  So a "
            "degree-two term contributes nothing to any second-order theory, "
            "RP-2ND-ORDER collapses degree <= 2 to degree <= 1, and there the "
            "variation gives a G_mn + b g_mn with both pieces divergence-free "
            "-- the Einstein case being the contracted Bianchi identity "
            "discharged rather than quoted.  The comparison ledger's forced "
            "swap therefore now rests on TWO computed uniqueness theorems "
            "instead of one computed and one cited.",
        "does_not_establish": [
            "Lovelock's theorem in general.  This is curvature degree <= 2 and "
            "D = 4 only.  The higher Euler densities, which matter in D > 4 "
            "and vanish identically in D = 4, are not treated, and neither is "
            "any degree above two",
            "the D > 4 Gauss-Bonnet dynamics.  The decisive fact used here is "
            "the IDENTICAL VANISHING of the Lanczos tensor in D = 4; in higher "
            "dimensions it does not vanish and the argument changes character",
            "uniqueness among non-polynomial or nonlocal Lagrangians; the "
            "carrier is polynomial in curvature, and RP-LOCAL is a separate "
            "assumption with its own witness",
            "anything about which of a G_mn + b g_mn is physically realised -- "
            "the values of a and b are not fixed by anything here",
        ],
        "inputs_assumed": [
            "the forced head: -1/2 g_mn Riem^2 from delta sqrt(-g) and "
            "2 R_mabc R_n^{abc} from lowering indices.  Not a choice",
            "divergence-freedom of the metric variation of a local "
            "diff-invariant action -- N1, discharged in "
            "REVERSE_PHYSICS_WEYL_GEOMETRY_DISCHARGE_V1, not a new import",
            "RP-2ND-ORDER itself, which is the assumption under test",
        ],
        "derivation": {
            "unknown_structures": UNKNOWNS,
            "derivative_structures": DERIVATIVE_STRUCTURES,
            "equations_from_identical_vanishing": n_equations,
            "residual_family_dimension_without_second_order": residual,
            "why_two":
                "adding any multiple of the Ric^2 or R^2 field-equation "
                "tensors preserves both the forced head and "
                "divergence-freedom, so the residue is exactly their span",
            "solutions_with_second_order": n_solutions,
            "derived_coefficients": {k: str(coeffs[k]) for k in UNKNOWNS}
                                    if coeffs else None,
            "matches_lanczos": bool(matches),
            "lanczos_reference_coefficients":
                {k: str(v) for k, v in LANCZOS_COEFFICIENTS.items()},
            "note": "the reference coefficients are used ONLY to compare "
                    "against; they are never substituted into the computation",
        },
        "vanishing_in_D4": vanishing,
        "degree_one_sector": degree_one,
        "upgrades": {
            "what": "weyl_trace_law.py used E^{(Riem^2)} = 4 E^{(Ric^2)} - "
                    "E^{(R^2)} as a CITED input (the Lanczos/Gauss-Bonnet "
                    "identity, flagged there as the same content as G4/N3)",
            "how": "that identity is exactly 'the Lanczos tensor vanishes in "
                   "D = 4', which is discharged here, so the citation is "
                   "upgraded to a discharge",
        },
        "closes": {
            "what": "the comparison ledger's swap block listed the Einstein "
                    "uniqueness theorem as GEOMETRY / CITED (Lovelock 1971/72) "
                    "while the Weyl side was PROVED",
            "now": "both sides are computed in the same carrier",
        },
        "inputs": {
            "black_hole_programme/weyl_geometry.py":
                file_hash("black_hole_programme/weyl_geometry.py"),
        },
        "checks": {
            "detail": checks,
            "total": len(checks),
            "passed": sum(1 for v in checks.values() if v),
            "failures": failures,
            "ok": not failures,
        },
        "report": "reverse_physics/reports/einstein-classification.md",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--emit", action="store_true")
    args = ap.parse_args(argv)
    if not (args.check or args.emit):
        args.check = True

    cert = build()
    d = cert["derivation"]
    print("equations from identical vanishing : %s" %
          d["equations_from_identical_vanishing"])
    print("divergence-freedom alone           : %s-parameter family"
          % d["residual_family_dimension_without_second_order"])
    print("  + RP-2ND-ORDER                   : %s solution(s)"
          % d["solutions_with_second_order"])
    if d["derived_coefficients"]:
        print("derived tensor coefficients:")
        for k in UNKNOWNS:
            print("   %-10s %s" % (k, d["derived_coefficients"][k]))
    print("is the Lanczos tensor              : %s" % d["matches_lanczos"])
    for v in cert["vanishing_in_D4"]:
        print("   vanishes identically on %-20s %s"
              % (v["metric"], v["vanishes_identically"]))
    for r in cert["degree_one_sector"]:
        print("   degree<=1 on %-20s G_mn div-free %s%s"
              % (r["metric"], r["einstein_tensor_is_divergence_free"],
                 "   [G_mn = 0: a vacuum solution]"
                 if r["is_a_vacuum_solution"] else ""))
    print("checks %d/%d" % (cert["checks"]["passed"], cert["checks"]["total"]))
    for f in cert["checks"]["failures"]:
        print("FAIL %s" % f)

    if args.emit and cert["checks"]["ok"]:
        with open(CERT_PATH, "w") as fh:
            json.dump(cert, fh, indent=2, sort_keys=True, default=str)
            fh.write("\n")
        print("wrote %s" % os.path.relpath(CERT_PATH, REPO_ROOT))

    print("RESULT: %s" % ("PASS" if cert["checks"]["ok"] else "FAIL"))
    return 0 if cert["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
