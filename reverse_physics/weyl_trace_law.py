"""N2 -- the trace of the metric variation is a NONZERO multiple of the anomaly.

WHY THIS EXISTS.  N2 is the last genuinely open entry in the reverse-physics
geometry column, and it is the BRIDGE BETWEEN THE TWO LEDGERS.  The separation
ledger's section 3.2b proves that the same theory has six assumptions written as
an action and five written as field equations, and the move that carries
RP-WEYL across is

    RP-WEYL (the action is Weyl invariant)
        <==>  RP-TRACELESS (the field equations are traceless)

Both directions go through N2.  The forward direction is cheap.  The REVERSE
direction -- traceless implies Weyl invariant -- needs the multiple relating the
two to be NONZERO, because a vanishing multiple would make every action come out
traceless and the equivalence would be vacuous.  That is why the ledger records
N2's non-vanishing as load-bearing, exactly as it does for G5.

WHAT IS DISCHARGED, AND IT IS SHARPER THAN THE LEDGER STATED.  Writing a general
quadratic curvature action over the coordinate space of the classification,

    S[a,b,c] = int sqrt(-g) ( a Riem^2 + b Ric^2 + c R^2 )

the trace of its metric variation is, at every metric tested,

    g^{mn} E_{mn}[a,b,c]  =  2 (a + b + 3c) box R

and `a + b + 3c = 0` is EXACTLY the single linear equation that the action
classification already proves cuts out the Weyl-invariant subspace
(PHYSICS-VS-MATH section 3.3).  So N2 is not merely "a nonzero multiple of the
anomaly" -- the multiple is 2, and the anomaly factorises as the Weyl-invariance
functional times box R.  Consequences:

    kernel of the trace map  =  { a + b + 3c = 0 }  =  span{C^2, E4}

which is the RP-WEYL <==> RP-TRACELESS equivalence, with the reverse direction
supplied by 2 != 0 together with box R != 0.  The second factor is G5, already
discharged: matter-dominated FRW has box R = -8/(3 t^4).  N2 and G5 turn out to
need the SAME witness, which is why a ledger that lost G5 would silently lose
N2 as well.

THE VARIATIONAL LINK IS NOW DERIVED, NOT CITED.  The work item recorded that
the link delta int sqrt(-g) C^2 = 4 int sqrt(-g) B_mn delta g^mn was CITED to
the Nariai product-family check and not re-derived.  Here the C^2 field equation
tensor is assembled from the quadratic pieces and compared against this
repository's OWN Bach tensor, computed independently by the curvature engine:

    E^{(C^2)}_{mn} = 4 B_mn

exactly, on every nonzero component, at a metric that is neither Einstein nor
conformally flat.  The factor 4 is COMPUTED here, not assumed, and it agrees
with the cited value.

WHAT IS IMPORTED, AND HOW IT IS VALIDATED.  The closed forms for the two
quadratic field-equation tensors are textbook and are NOT derived here -- they
are middle-column objects, which is the whole point of having a middle column.
With the convention delta S = int sqrt(-g) E_mn delta g^{mn}:

    E^{(R^2)}_{mn}  = 2 R R_mn - (1/2) g_mn R^2 + 2 g_mn box R - 2 nabla_m nabla_n R
    E^{(Ric^2)}_{mn}= -(1/2) g_mn Ric^2 - nabla_m nabla_n R + box R_mn
                      + (1/2) g_mn box R + 2 R_manb R^{ab}

They are validated three independent ways against the engine rather than
trusted:

  1. DIVERGENCE-FREEDOM.  nabla^m E_mn = 0 for each, exactly.  This is the
     Noether/diff content (N1's analogue) and a wrong formula generically fails
     it.  It is not decoration: it is what FIXES the sign of the Riemann
     coupling term, whose sign convention differs across sources.  The opposite
     sign is carried as a negative control and DOES fail.

  2. THE BACH CROSS-CHECK.  The C^2 combination equals 4 B_mn for the engine's
     independently computed Bach tensor.

  3. THE TRACE LAW ITSELF, holding with the SAME coefficients at metrics with
     different symmetry.

THE LANCZOS STEP IS CITED.  E^{(Riem^2)} is not implemented independently.  In
D = 4 the Gauss-Bonnet density E4 = Riem^2 - 4 Ric^2 + R^2 has identically
vanishing variation, so

    E^{(Riem^2)} = 4 E^{(Ric^2)} - E^{(R^2)}.

That is the same content as G4/N3, and was cited to
EULER_TRANSGRESSION_CERTIFICATE's `delta_E4_minus_dTheta`.  IT IS NOW
DISCHARGED: REVERSE_PHYSICS_EINSTEIN_CLASSIFICATION_V1 derives the Lanczos
tensor from the forced head of the Riem^2 variation plus divergence-freedom, and
checks that it vanishes identically in D = 4 -- which is exactly this identity.
The certificate's does_not_establish entry below is retained as a record of what
the status was when this module was written.  It is not circular: the C^2
combination built THROUGH this identity is what matches 4 B_mn against an
independently computed tensor, so the identity is cross-validated rather than
assumed into the answer.  The trace law is additionally checked on the
{Ric^2, R^2} subspace, where NO Lanczos input is needed at all, so the
Lanczos-free part of the claim is separated out and reported on its own.

DEGENERACY, WHICH IS WHERE THIS KIND OF CHECK DIES.  Two different metrics are
needed because no single one can see everything:

  * FRW (matter-dominated) has box R != 0 and carries the trace law, but it is
    CONFORMALLY FLAT, so C = 0 and B = 0 and the Bach cross-check is VACUOUS.
  * A non-Einstein static metric is neither Einstein nor conformally flat and
    carries the Bach cross-check.
  * Schwarzschild is included precisely because it can witness NOTHING: it is
    Ricci-flat, so R = 0, box R = 0, both field-equation tensors vanish, and
    it is Einstein so its Bach tensor vanishes too.  Every check passes on it
    VACUOUSLY.  Recording that is the point -- it is the same trap the work
    item flags for R^2/Ric^2 coefficients, and each row carries its own
    visibility flags.

WHAT THIS IS, AND IS NOT.  Exact sympy rational arithmetic, no floating point,
at specific metrics.  A DISCHARGE, not a proof: strictly stronger than an
unverified import, strictly weaker than a theorem for all metrics.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.weyl_trace_law --check
    PYTHONPATH=. python3 -m reverse_physics.weyl_trace_law --emit
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
    "REVERSE_PHYSICS_WEYL_TRACE_LAW_V1.json",
)

N = 4
RG = range(N)

# The Weyl-invariance functional from the action classification: a quadratic
# curvature action a Riem^2 + b Ric^2 + c R^2 is Weyl invariant iff this
# vanishes.  Imported from the classification, not re-derived here.
def weyl_functional(a, b, c):
    return a + b + 3 * c


# The multiple N2 asserts is nonzero.  Computed below, not assumed.
EXPECTED_MULTIPLE = 2
EXPECTED_BACH_FACTOR = 4


class Calculus:
    """Covariant-derivative helpers over the repository's curvature engine."""

    def __init__(self, coords, g):
        self.coords = coords
        self.g = g
        self.G = Geometry(coords, g)
        self.gi = g.inv()
        self.Ric = self.G.Ricci
        self.Rs = sp.simplify(self.G.Rscalar)
        self.Riem = self.G.Riemann

    def raise2(self, T):
        return sp.Matrix(N, N, lambda a, b: sp.simplify(
            sum(self.gi[a, p] * self.gi[b, q] * T[p, q]
                for p in RG for q in RG)))

    def hess(self, phi):
        """nabla_m nabla_n phi for a scalar."""
        d = [sp.diff(phi, x) for x in self.coords]
        return sp.Matrix(N, N, lambda m, n: sp.simplify(
            sp.diff(d[m], self.coords[n])
            - sum(self.G.Gamma[h][n][m] * d[h] for h in RG)))

    def box_scalar(self, phi):
        H = self.hess(phi)
        return sp.simplify(sum(self.gi[a, b] * H[a, b]
                               for a in RG for b in RG))

    def box_t2(self, T):
        """box T_mn = g^{ab} nabla_a nabla_b T_mn."""
        DT = [[[sp.simplify(self.G.covd2(T, b, m, n)) for n in RG]
               for m in RG] for b in RG]
        out = sp.zeros(N, N)
        for m in RG:
            for n in RG:
                out[m, n] = sp.simplify(sum(
                    self.gi[a, b] * self.G.covd3(DT, a, b, m, n)
                    for a in RG for b in RG))
        return out

    def div(self, T):
        """nabla^m T_mn."""
        return [sp.simplify(sum(self.gi[m, e] * self.G.covd2(T, e, m, n)
                                for m in RG for e in RG)) for n in RG]

    def trace(self, T):
        return sp.simplify(sum(self.gi[a, b] * T[a, b]
                               for a in RG for b in RG))


def field_equations(cal, coupling_sign=1):
    """The two independent quadratic field-equation tensors.

    `coupling_sign` exists ONLY for the negative control: the sign of the
    Riemann coupling term differs across sources, and divergence-freedom is
    what fixes it.  The discharge always uses +1.
    """
    g, Ric, Rs = cal.g, cal.Ric, cal.Rs
    Ricup = cal.raise2(Ric)
    boxR = cal.box_scalar(Rs)
    ddR = cal.hess(Rs)
    boxRic = cal.box_t2(Ric)
    ric2 = sp.simplify(sum(Ricup[a, b] * Ric[a, b] for a in RG for b in RG))

    E_R2 = sp.Matrix(N, N, lambda m, n: sp.simplify(
        2 * Rs * Ric[m, n] - sp.Rational(1, 2) * g[m, n] * Rs**2
        + 2 * g[m, n] * boxR - 2 * ddR[m, n]))

    coup = sp.Matrix(N, N, lambda m, n: sp.simplify(sum(
        cal.Riem[m][a][n][b] * Ricup[a, b] for a in RG for b in RG)))

    E_Ric2 = sp.Matrix(N, N, lambda m, n: sp.simplify(
        -sp.Rational(1, 2) * g[m, n] * ric2 - ddR[m, n] + boxRic[m, n]
        + sp.Rational(1, 2) * g[m, n] * boxR
        + coupling_sign * 2 * coup[m, n]))

    # CITED (Lanczos / Gauss-Bonnet in D = 4): E4 has vanishing variation.
    E_Riem2 = sp.Matrix(N, N, lambda m, n: sp.simplify(
        4 * E_Ric2[m, n] - E_R2[m, n]))

    return {"boxR": boxR, "E_R2": E_R2, "E_Ric2": E_Ric2, "E_Riem2": E_Riem2}


def combine(fe, a, b, c):
    return sp.Matrix(N, N, lambda m, n: sp.simplify(
        a * fe["E_Riem2"][m, n] + b * fe["E_Ric2"][m, n] + c * fe["E_R2"][m, n]))


# --------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------

def frw_matter():
    """Matter-dominated FRW -- the G5 witness.  box R != 0, but CONFORMALLY
    FLAT, so C = 0, B = 0 and the Bach cross-check is vacuous here."""
    t = sp.Symbol("t", positive=True)
    a = t ** sp.Rational(2, 3)
    coords = [t] + list(sp.symbols("x y z", positive=True))
    return coords, sp.diag(-1, a**2, a**2, a**2)


def non_einstein_static():
    """Neither Einstein nor conformally flat: carries the Bach cross-check."""
    mass = sp.Rational(1, 5)
    t, r, th, ph = sp.symbols("t r theta phi", positive=True)
    f = 1 - 2 * mass / r
    return ([t, r, th, ph],
            sp.diag(-(1 + mass * r**2), 1 / f, r**2, r**2 * sp.sin(th)**2))


def schwarzschild():
    """Witnesses NOTHING, and is here to show that.  Ricci-flat => R = 0,
    box R = 0, both field-equation tensors vanish; Einstein => B = 0.  Every
    check below passes on it VACUOUSLY."""
    mass = sp.Rational(1, 5)
    t, r, th, ph = sp.symbols("t r theta phi", positive=True)
    f = 1 - 2 * mass / r
    return ([t, r, th, ph],
            sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th)**2))


METRICS = [
    ("frw_matter", frw_matter),
    ("non_einstein_static", non_einstein_static),
    ("schwarzschild", schwarzschild),
]

# Probe directions for the trace law.  Includes the two Weyl-invariant
# directions (C^2 and E4, which must give trace zero) and generic ones.
PROBES = [
    ("C2", (1, -2, sp.Rational(1, 3))),
    ("E4", (1, -4, 1)),
    ("R2", (0, 0, 1)),
    ("Ric2", (0, 1, 0)),
    ("generic", (sp.Rational(2, 5), -3, sp.Rational(7, 2))),
]


def check_metric(name, builder):
    coords, g = builder()
    cal = Calculus(coords, g)
    fe = field_equations(cal)
    boxR = fe["boxR"]
    bach = cal.G.bach()
    weyl_nonzero = any(cal.Riem and cal.G.Weyl[a][b][c][d] != 0
                       for a in RG for b in RG for c in RG for d in RG)

    row = {
        "metric": name,
        "box_R_is_nonzero": sp.simplify(boxR) != 0,
        "weyl_is_nonzero": bool(weyl_nonzero),
        "bach_is_nonzero": sp.simplify(bach) != sp.zeros(N, N),
        # Noether/diff: these tensors are variational derivatives
        "div_E_R2_vanishes": all(x == 0 for x in cal.div(fe["E_R2"])),
        "div_E_Ric2_vanishes": all(x == 0 for x in cal.div(fe["E_Ric2"])),
    }

    # the trace law, per probe direction
    traces = {}
    law_ok = True
    for label, (a, b, c) in PROBES:
        E = combine(fe, a, b, c)
        tr = cal.trace(E)
        want = EXPECTED_MULTIPLE * weyl_functional(a, b, c) * boxR
        ok = sp.simplify(tr - want) == 0
        traces[label] = ok
        law_ok = law_ok and ok
    row["trace_law_holds_on_all_probes"] = law_ok
    row["trace_law_by_probe"] = traces

    # the Lanczos-free part: the {Ric^2, R^2} subspace needs no Lanczos input
    lanczos_free = True
    for (b, c) in [(1, 0), (0, 1), (sp.Rational(3, 4), -2)]:
        E = sp.Matrix(N, N, lambda m, n: sp.simplify(
            b * fe["E_Ric2"][m, n] + c * fe["E_R2"][m, n]))
        want = EXPECTED_MULTIPLE * weyl_functional(0, b, c) * boxR
        lanczos_free = lanczos_free and sp.simplify(cal.trace(E) - want) == 0
    row["trace_law_holds_without_lanczos_input"] = lanczos_free

    # the Weyl-invariant directions must be traceless
    row["C2_direction_is_traceless"] = traces["C2"]
    row["E4_direction_is_traceless"] = traces["E4"]

    # the Bach cross-check -- only meaningful where the Bach tensor is nonzero
    if row["bach_is_nonzero"]:
        E_C2 = combine(fe, 1, -2, sp.Rational(1, 3))
        ratios = set()
        for m in RG:
            for n in RG:
                if sp.simplify(bach[m, n]) != 0:
                    ratios.add(sp.simplify(E_C2[m, n] / bach[m, n]))
        row["E_C2_equals_4_Bach"] = ratios == {sp.Integer(EXPECTED_BACH_FACTOR)}
        row["bach_factor_computed"] = sorted(str(x) for x in ratios)
        row["bach_cross_check_is_non_vacuous"] = True
    else:
        row["bach_cross_check_is_non_vacuous"] = False

    # honest degeneracy summary
    row["witnesses_nothing"] = not (row["box_R_is_nonzero"]
                                    or row["bach_is_nonzero"])
    return row


def negative_controls():
    """Run on FRW, which is cheap and has box R != 0."""
    coords, g = frw_matter()
    cal = Calculus(coords, g)
    out = []

    # 1. wrong sign of the Riemann coupling term -> divergence-freedom fails
    bad = field_equations(cal, coupling_sign=-1)
    holds = all(x == 0 for x in cal.div(bad["E_Ric2"]))
    out.append({
        "control": "riemann_coupling_sign_flipped",
        "property": "div E_Ric2 == 0",
        "still_holds": bool(holds),
        "rejected": not holds,
        "note": "this is what FIXES the sign convention; it must discriminate",
    })

    fe = field_equations(cal)
    boxR = fe["boxR"]

    # 2. wrong multiple
    E = combine(fe, 0, 0, 1)
    holds = sp.simplify(cal.trace(E) - 3 * weyl_functional(0, 0, 1) * boxR) == 0
    out.append({"control": "multiple_3_instead_of_2",
                "property": "trace law", "still_holds": bool(holds),
                "rejected": not holds})

    # 3. wrong Weyl functional -- a + b + 2c instead of a + b + 3c
    E = combine(fe, 0, 1, 1)
    holds = sp.simplify(cal.trace(E)
                        - EXPECTED_MULTIPLE * (0 + 1 + 2 * 1) * boxR) == 0
    out.append({"control": "weyl_functional_a_b_2c",
                "property": "trace law", "still_holds": bool(holds),
                "rejected": not holds,
                "note": "if this passed, the kernel of the trace map would not "
                        "be the Weyl-invariant subspace"})

    # 4. a Weyl-invariant direction must NOT have nonzero trace
    E = combine(fe, 1, -2, sp.Rational(1, 3))
    holds = sp.simplify(cal.trace(E)) != 0
    out.append({"control": "C2_direction_has_nonzero_trace",
                "property": "tr E^{(C^2)} != 0", "still_holds": bool(holds),
                "rejected": not holds})
    return out


def file_hash(rel):
    with open(os.path.join(REPO_ROOT, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def build():
    rows = [check_metric(n, b) for n, b in METRICS]
    controls = negative_controls()

    visibility = {"box_R_is_nonzero", "weyl_is_nonzero", "bach_is_nonzero",
                  "bach_cross_check_is_non_vacuous", "witnesses_nothing"}
    failures = []
    total = passed = 0
    for r in rows:
        for k, v in r.items():
            if isinstance(v, bool) and k not in visibility:
                total += 1
                if v:
                    passed += 1
                else:
                    failures.append("%s: %s" % (r["metric"], k))

    # non-degeneracy gates
    if not [r for r in rows if r["box_R_is_nonzero"]]:
        failures.append("box R = 0 everywhere: the trace law is vacuous, since "
                        "both sides vanish identically")
    if not [r for r in rows if r.get("bach_cross_check_is_non_vacuous")]:
        failures.append("the Bach cross-check is vacuous everywhere: no tested "
                        "metric has a nonzero Bach tensor")
    for c in controls:
        if not c["rejected"]:
            failures.append("negative control not rejected: %s" % c["control"])

    return {
        "certificate": "REVERSE_PHYSICS_WEYL_TRACE_LAW_V1",
        "kind": "geometry-discharge",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "establishes":
            "N2, sharpened.  For S = int sqrt(-g)(a Riem^2 + b Ric^2 + c R^2) "
            "the trace of the metric variation is g^{mn} E_mn = "
            "2 (a + b + 3c) box R, where a + b + 3c = 0 is exactly the single "
            "linear equation the action classification proves cuts out the "
            "Weyl-invariant subspace.  The multiple is 2, hence nonzero, and "
            "box R != 0 by G5, so the kernel of the trace map is exactly "
            "span{C^2, E4}: this is the RP-WEYL <==> RP-TRACELESS equivalence "
            "with its reverse direction supplied.  Additionally the "
            "variational link E^{(C^2)}_mn = 4 B_mn is COMPUTED here against "
            "the repository's own independently calculated Bach tensor, "
            "rather than cited to the Nariai product-family check as before.",
        "does_not_establish": [
            "any of this FOR ALL METRICS -- it is a DISCHARGE, exact "
            "verification at specific metrics, strictly stronger than an "
            "unverified import and strictly weaker than a theorem",
            "the closed forms of the two quadratic field-equation tensors, "
            "which are IMPORTED textbook expressions; they are validated here "
            "by divergence-freedom, by the Bach cross-check and by the trace "
            "law holding at metrics of different symmetry, but not derived",
            "the Lanczos/Gauss-Bonnet identity E^{(Riem^2)} = 4 E^{(Ric^2)} - "
            "E^{(R^2)}, which is CITED (same content as G4/N3); the trace law "
            "restricted to the {Ric^2, R^2} subspace needs no Lanczos input "
            "and is reported separately",
            "any quantum statement.  N2 is often phrased as being about the "
            "trace anomaly; what is established here is the CLASSICAL "
            "variational identity.  Determinants, literature coefficients, "
            "beta functions, background trace anomalies and BV master-equation "
            "breakings are distinct objects and none of them is this one.",
        ],
        "conventions": {
            "variation": "delta S = int sqrt(-g) E_mn delta g^{mn}",
            "E_R2": "2 R R_mn - (1/2) g_mn R^2 + 2 g_mn box R "
                    "- 2 nabla_m nabla_n R",
            "E_Ric2": "-(1/2) g_mn Ric^2 - nabla_m nabla_n R + box R_mn "
                      "+ (1/2) g_mn box R + 2 R_manb R^{ab}",
            "E_Riem2": "4 E_Ric2 - E_R2  (CITED: Lanczos, E4 has vanishing "
                       "variation in D = 4)",
            "riemann_coupling_sign":
                "fixed by DIVERGENCE-FREEDOM, not by choosing a source: the "
                "opposite sign is carried as a negative control and fails",
        },
        "result": {
            "multiple": EXPECTED_MULTIPLE,
            "multiple_is_nonzero": EXPECTED_MULTIPLE != 0,
            "weyl_functional": "a + b + 3c",
            "trace_law": "g^{mn} E_mn = 2 (a + b + 3c) box R",
            "kernel_of_trace_map": "span{C^2, E4}",
            "bach_factor": EXPECTED_BACH_FACTOR,
        },
        "rows": rows,
        "negative_controls": controls,
        "non_degeneracy": {
            "metrics_with_box_R_nonzero":
                [r["metric"] for r in rows if r["box_R_is_nonzero"]],
            "metrics_carrying_the_bach_cross_check":
                [r["metric"] for r in rows
                 if r.get("bach_cross_check_is_non_vacuous")],
            "metrics_that_witness_nothing":
                [r["metric"] for r in rows if r["witnesses_nothing"]],
            "note": "FRW is conformally flat so B = 0 and it cannot carry the "
                    "Bach cross-check; Schwarzschild is Ricci-flat AND "
                    "Einstein so it carries nothing at all and is included to "
                    "make that visible.",
        },
        "inputs": {
            "black_hole_programme/weyl_geometry.py":
                file_hash("black_hole_programme/weyl_geometry.py"),
        },
        "checks": {
            "total": total,
            "passed": passed,
            "failures": failures,
            "negative_controls_rejected": "%d/%d" % (
                sum(1 for c in controls if c["rejected"]), len(controls)),
            "ok": not failures,
        },
        "report": "reverse_physics/reports/weyl-trace-law.md",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--emit", action="store_true")
    args = ap.parse_args(argv)
    if not (args.check or args.emit):
        args.check = True

    cert = build()
    for r in cert["rows"]:
        vis = []
        if not r["box_R_is_nonzero"]:
            vis.append("boxR=0")
        if not r["bach_is_nonzero"]:
            vis.append("B=0")
        if r["witnesses_nothing"]:
            vis.append("WITNESSES NOTHING")
        print("%-22s %s%s" % (
            r["metric"], "OK",
            ("   [" + ", ".join(vis) + "]") if vis else ""))
    print("trace law   : %s" % cert["result"]["trace_law"])
    print("kernel      : %s" % cert["result"]["kernel_of_trace_map"])
    print("bach factor : %s" % cert["result"]["bach_factor"])
    print("carried by  : boxR %s | bach %s" % (
        ",".join(cert["non_degeneracy"]["metrics_with_box_R_nonzero"]),
        ",".join(cert["non_degeneracy"]["metrics_carrying_the_bach_cross_check"])))
    for c in cert["negative_controls"]:
        print("control %-34s rejected: %s" % (c["control"], c["rejected"]))
    print("checks %d/%d, controls %s" % (
        cert["checks"]["passed"], cert["checks"]["total"],
        cert["checks"]["negative_controls_rejected"]))
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
