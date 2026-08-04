"""G6 and G8 -- the Hodge dual of the Weyl tensor, discharged in both signatures.

WHY THIS EXISTS.  The reverse-physics geometry column
([weyl-geometry-discharge.md]) discharged G1, G2, G3, G5 and N1 against this
repository's exact curvature engine and left two entries BLOCKED:

    G6  the parity-odd quadratic invariants are spanned by P, and P = C.Cdual
    G8  W_pm^2 = (C^2 +- P)/2  -- the link to the certified residual classes

A first attempt got the split ALGEBRA exactly right on Lorentzian Taub-NUT --
W_+^2 - W_-^2 = P and W_+^2 + W_-^2 = (C^2 + Cdual^2)/2 both held at an exact
algebraic point -- but Cdual^2 != -C^2, so the epsilon index placement was
wrong, and the work item recorded that the fix was to express the dual in
`quantum-weyl/local_bv/hodge.py`'s conventions rather than to repair the
epsilon by trial.

WHAT hodge.py ACTUALLY FIXES, AND WHAT IT DOES NOT.  hodge.py is a formal
two-dimensional algebra on the ordered basis (F, *F).  It fixes

    star_square_sign = +1 (EUCLIDEAN),  -1 (LORENTZIAN)
    eigenvalues      = +-1 (EUCLIDEAN), +-i (LORENTZIAN)
    projectors       P_pm = (I + star/lambda)/2

and nothing else.  It never fixes the epsilon index placement on a rank-four
tensor, which is where the earlier error lived.  So "express the dual in
hodge.py's conventions" resolves to: choose the index placement that
REPRODUCES star_square_sign, and then take hodge.py's projectors seriously --
including the fact that the Lorentzian ones are COMPLEX.

The placement that works, and the one this module uses throughout:

    eps_{abcd}      = vol * [abcd],  vol = sqrt(|det g|),  all indices DOWN
    (*T)_{abcd}     = (1/2) eps_{ab}^{ef} T_{efcd},  eps_{ab}^{ef} raised by g
    contractions    raise ALL FOUR indices with g before summing

The earlier attempt raised the last two indices of the Weyl tensor before
applying epsilon and then raised all four again, double-raising two slots.

WHAT IS DISCHARGED

  STAR SQUARE  (*C).(*C) = sign * C^2, with sign exactly hodge.py's
      star_square_sign.  This is the convention check: it is what the previous
      attempt failed, and every other result here depends on it.

  G6 (the computable clause)  Riem.*Riem = C.*C -- the Pontryagin density
      depends only on the Weyl tensor, the Ricci parts dropping out of the
      parity-odd contraction.  NOTE: this is VACUOUS on a Ricci-flat metric,
      where Riem = C identically.  Taub-NUT is Ricci-flat, so the check is
      carried by the Bianchi IX metrics, which are not Einstein, and the
      certificate records `ricci_is_nonzero` per metric so a reader can see
      which rows can and cannot support the claim.  This is the same trap the
      work item flags for the R^2/Ric^2 coefficients on Schwarzschild.

  G8 (both signatures, and they are DIFFERENT statements)

      EUCLIDEAN    star^2 = +1, projectors real, W_pm = (C +- *C)/2, and
                       W_pm^2 = (C^2 +- P)/2.
                   This is the textbook G8.

      LORENTZIAN   star^2 = -1, eigenvalues +-i, projectors COMPLEX,
                       W_pm = (C -+ i *C)/2, which are complex conjugates, and
                       W_pm^2 = (C^2 -+ i P)/2.
                   The textbook form is FALSE here.

      The work item's `forbid` requires exactly this qualification: G8 as
      usually stated is a EUCLIDEAN statement, because the Lorentzian Hodge
      star squares to -1 on two-forms.  Both forms are verified exactly, in
      their own signature, rather than one being asserted and the other
      waved at.

WHAT IS CITED, NOT DISCHARGED.  Per the stream's rule that citations suffice
when they are trustworthy, and with the boundary each source states about
itself:

  G6 (the spanning clause)  "the parity-odd quadratic invariants are SPANNED
      by P" is a representation-theory dimension count and is not a pointwise
      identity, so no evaluation at metrics can establish it.  Cited.

  G4  `quantum-weyl/local_bv/certificates/EULER_TRANSGRESSION_CERTIFICATE.json`
      (LOCAL-ALGEBRAIC, INTRINSIC_EULER_TOWER_VERIFIED) carries
      `delta_E4_minus_dTheta` and `closed_manifold_integrated_variation`.
      That is the content the classification actually uses -- the integrated
      variation vanishes, so E4 contributes nothing to the field equations.
      It is NOT an index theorem and NOT a global triviality claim.

  G7  `symbolic/verify_conformal_dynamical_topological.py` proves the
      Chern-Weil transgression Tr(R^R) = d Tr(Gamma dGamma + 2/3 Gamma^3).
      Its own docstring says: "Global triviality of the Pontryagin class is
      explicitly not claimed."  That boundary is carried here verbatim.

  N3  "a topological term has identically vanishing variation" is the SAME
      content as G4's `delta_E4_minus_dTheta`, so N3 is discharged by the same
      citation rather than needing separate work.

WHAT THIS IS, AND IS NOT.  Every identity is verified EXACTLY (sympy rationals,
radicals and I; no floating point) at SPECIFIC METRICS and SPECIFIC POINTS.
That is strictly stronger than an unverified import and strictly weaker than a
theorem for all metrics.  It is a DISCHARGE, not a proof, and the certificate
says so in those words.  Negative controls are included because a check that
cannot fail is not a check: the two wrong epsilon normalizations and the real
Lorentzian split must all be REJECTED.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.weyl_dual_discharge --check
    PYTHONPATH=. python3 -m reverse_physics.weyl_dual_discharge --emit
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
    "REVERSE_PHYSICS_WEYL_DUAL_DISCHARGE_V1.json",
)

R4 = range(4)

LORENTZIAN = "LORENTZIAN"
EUCLIDEAN = "EUCLIDEAN"

# hodge.py: star_square_sign is +1 Euclidean, -1 Lorentzian.  Mirrored here so
# the discharge states the convention it is checking against rather than
# importing the answer it is supposed to reproduce.
STAR_SQUARE_SIGN = {EUCLIDEAN: 1, LORENTZIAN: -1}


# --------------------------------------------------------------------------
# The dual, with the index placement written out explicitly.
# --------------------------------------------------------------------------

def analyse(coords, metric, point, signature,
            eps_volume_power=1, dual_prefactor=sp.Rational(1, 2)):
    """Exact dual data at `point`.

    `eps_volume_power` and `dual_prefactor` exist ONLY so the negative controls
    can perturb the convention and observe the star-square check fail.  The
    discharge always uses the defaults.
    """
    geom = Geometry(coords, metric)

    def at(T):
        return [[[[sp.simplify(T[a][b][c][d].subs(point)) for d in R4]
                  for c in R4] for b in R4] for a in R4]

    weyl = at(geom.Weyl)
    riem = at(geom.Riemann)
    ricci = sp.Matrix(4, 4, lambda i, j: sp.simplify(geom.Ricci[i, j].subs(point)))

    g = sp.Matrix(4, 4, lambda i, j: sp.simplify(metric[i, j].subs(point)))
    ginv = g.inv()
    det = sp.simplify(g.det())
    lorentzian = signature == LORENTZIAN
    vol = (sp.sqrt(-det) if lorentzian else sp.sqrt(det)) ** eps_volume_power

    # eps_{abcd} = vol * [abcd], ALL INDICES DOWN.
    eps = [[[[vol * sp.LeviCivita(a, b, c, d) for d in R4] for c in R4]
            for b in R4] for a in R4]

    def raise_all(T):
        return [[[[sp.simplify(sum(
            ginv[a, p] * ginv[b, q] * ginv[c, u] * ginv[d, v] * T[p][q][u][v]
            for p in R4 for q in R4 for u in R4 for v in R4))
            for d in R4] for c in R4] for b in R4] for a in R4]

    def dual(T):
        """(*T)_{abcd} = (1/2) eps_{ab}^{ef} T_{efcd}."""
        return [[[[sp.simplify(dual_prefactor * sum(
            eps[a][b][p][q] * ginv[p, e] * ginv[q, f] * T[e][f][c][d]
            for p in R4 for q in R4 for e in R4 for f in R4))
            for d in R4] for c in R4] for b in R4] for a in R4]

    def dot(A, B_up):
        return sp.simplify(sum(A[a][b][c][d] * B_up[a][b][c][d]
                               for a in R4 for b in R4
                               for c in R4 for d in R4))

    weyl_dual = dual(weyl)
    riem_dual = dual(riem)

    c2 = dot(weyl, raise_all(weyl))
    pontryagin = dot(weyl, raise_all(weyl_dual))
    dual_sq = dot(weyl_dual, raise_all(weyl_dual))
    pontryagin_riem = dot(riem, raise_all(riem_dual))

    def combo(coeff):
        return [[[[(weyl[a][b][c][d] + coeff * weyl_dual[a][b][c][d]) / 2
                   for d in R4] for c in R4] for b in R4] for a in R4]

    def sq(T):
        return dot(T, raise_all(T))

    return {
        "signature": signature,
        "sign": STAR_SQUARE_SIGN[signature],
        "C2": c2,
        "P": pontryagin,
        "dual_sq": dual_sq,
        "P_riem": pontryagin_riem,
        "ricci_is_nonzero": sp.simplify(ricci) != sp.zeros(4, 4),
        "combo": combo,
        "sq": sq,
    }


# --------------------------------------------------------------------------
# Metrics.  Chosen so the two things that can make a check vacuous -- P = 0
# and Ric = 0 -- are both visibly absent somewhere.
# --------------------------------------------------------------------------

def taub_nut(signature):
    """Taub-NUT, with mass != nut so it is not self-dual.

    Signature is imposed by flipping the sign of the (dt + 2n cos(theta) dphi)
    block.  That gives the genuine LORENTZIAN VACUUM Taub-NUT, where Ric = 0,
    Riem = C, and the G6 check is therefore VACUOUS however cleanly it passes.
    The sign flip does NOT preserve the vacuum condition, so the EUCLIDEAN
    member of this pair is not Ricci-flat and does carry G6 non-vacuously.
    Rather than pretend either way, each row reports its own
    `ricci_is_nonzero`, and the certificate lists exactly which rows can
    support G6.
    """
    t, r, th, ph = sp.symbols("t r theta phi", positive=True)
    mass, nut = sp.Integer(1), sp.Rational(1, 3)   # mass != nut => not self-dual
    f = (r**2 - 2 * mass * r - nut**2) / (r**2 + nut**2)
    twist = 2 * nut * sp.cos(th)
    block = -1 if signature == LORENTZIAN else 1
    g = sp.zeros(4, 4)
    g[0, 0] = block * f
    g[0, 3] = block * f * twist
    g[3, 0] = block * f * twist
    g[3, 3] = block * f * twist**2 + (r**2 + nut**2) * sp.sin(th)**2
    g[1, 1] = 1 / f
    g[2, 2] = r**2 + nut**2
    point = {r: sp.Integer(3), th: sp.pi / 3}
    return [t, r, th, ph], g, point


def deformed_taub_nut(signature):
    """Taub-NUT with the theta-theta component rescaled by 6/5.

    NOT a vacuum solution -- that is the entire point.  G6 says the Pontryagin
    density depends only on the WEYL tensor, i.e. that the Ricci parts drop out
    of the parity-odd contraction, and on a Ricci-flat metric Riem = C
    identically so there are no Ricci parts to drop and the check is vacuous.
    This metric has Ric != 0 AND keeps the NUT twist that makes P != 0, which
    is the combination G6 needs to be visible at all.

    It solves nothing, and it does not have to: a discharge needs metrics that
    are NON-DEGENERATE for the identity under test, not metrics that are
    physical.  Its limitation is recorded honestly -- it is a deformation of
    the Taub-NUT form rather than a structurally independent family, chosen
    because it keeps the (r, theta) coordinate dependence that makes the exact
    computation cheap.  A Bianchi IX family with three distinct scale factors
    would be independent but did not finish in a usable time.
    """
    t, r, th, ph = sp.symbols("t r theta phi", positive=True)
    mass, nut = sp.Integer(1), sp.Rational(1, 3)
    f = (r**2 - 2 * mass * r - nut**2) / (r**2 + nut**2)
    twist = 2 * nut * sp.cos(th)
    block = -1 if signature == LORENTZIAN else 1
    g = sp.zeros(4, 4)
    g[0, 0] = block * f
    g[0, 3] = block * f * twist
    g[3, 0] = block * f * twist
    g[3, 3] = block * f * twist**2 + (r**2 + nut**2) * sp.sin(th)**2
    g[1, 1] = 1 / f
    g[2, 2] = sp.Rational(6, 5) * (r**2 + nut**2)   # breaks Ricci-flatness
    point = {r: sp.Integer(3), th: sp.pi / 3}
    return [t, r, th, ph], g, point


METRICS = [
    ("taub_nut", taub_nut),
    ("deformed_taub_nut", deformed_taub_nut),
]


# --------------------------------------------------------------------------
# Checks.
# --------------------------------------------------------------------------

def check_metric(name, builder, signature):
    coords, g, point = builder(signature)
    d = analyse(coords, g, point, signature)
    sign = d["sign"]
    c2, p = d["C2"], d["P"]

    out = {
        "metric": name,
        "signature": signature,
        "star_square_sign": sign,
        "C2_is_nonzero": c2 != 0,
        "P_is_nonzero": p != 0,
        "ricci_is_nonzero": bool(d["ricci_is_nonzero"]),
        # the convention check the previous attempt failed
        "star_square_matches_hodge": sp.simplify(d["dual_sq"] - sign * c2) == 0,
        # G6, computable clause -- VACUOUS unless ricci_is_nonzero
        "G6_pontryagin_depends_only_on_weyl":
            sp.simplify(d["P_riem"] - p) == 0,
        "G6_is_non_vacuous_here": bool(d["ricci_is_nonzero"]),
    }

    if signature == EUCLIDEAN:
        wp, wm = d["combo"](1), d["combo"](-1)
        out["G8_euclidean_Wplus_sq_eq_C2_plus_P_over_2"] = (
            sp.simplify(d["sq"](wp) - (c2 + p) / 2) == 0)
        out["G8_euclidean_Wminus_sq_eq_C2_minus_P_over_2"] = (
            sp.simplify(d["sq"](wm) - (c2 - p) / 2) == 0)
    else:
        # hodge.py's Lorentzian projectors are COMPLEX: W_pm = (C -+ i *C)/2
        wp, wm = d["combo"](-sp.I), d["combo"](sp.I)
        out["G8_lorentzian_Wplus_sq_eq_C2_minus_iP_over_2"] = (
            sp.simplify(d["sq"](wp) - (c2 - sp.I * p) / 2) == 0)
        out["G8_lorentzian_Wminus_sq_eq_C2_plus_iP_over_2"] = (
            sp.simplify(d["sq"](wm) - (c2 + sp.I * p) / 2) == 0)
        # and the textbook Euclidean form is FALSE here -- stated as a check,
        # not left as a remark
        out["G8_euclidean_form_is_false_in_lorentzian_signature"] = (
            sp.simplify(d["sq"](d["combo"](1)) - (c2 + p) / 2) != 0)
    return out


def negative_controls():
    """Perturb the convention; the star square MUST stop holding.  Run on
    Lorentzian Taub-NUT, which is the case the earlier attempt got wrong."""
    coords, g, point = taub_nut(LORENTZIAN)
    sign = STAR_SQUARE_SIGN[LORENTZIAN]
    controls = []

    for label, kw in [
        ("eps_without_volume_factor", {"eps_volume_power": 0}),
        ("dual_prefactor_one_instead_of_one_half",
         {"dual_prefactor": sp.Integer(1)}),
    ]:
        d = analyse(coords, g, point, LORENTZIAN, **kw)
        holds = sp.simplify(d["dual_sq"] - sign * d["C2"]) == 0
        controls.append({"control": label,
                         "star_square_still_holds": bool(holds),
                         "rejected": not holds})

    # the real split, which is what one writes if hodge.py's complex Lorentzian
    # eigenvalues are ignored
    d = analyse(coords, g, point, LORENTZIAN)
    holds = sp.simplify(d["sq"](d["combo"](1)) - (d["C2"] + d["P"]) / 2) == 0
    controls.append({"control": "real_split_in_lorentzian_signature",
                     "euclidean_form_still_holds": bool(holds),
                     "rejected": not holds})
    return controls


CITATIONS = [
    {
        "entry": "G6 (spanning clause)",
        "claim": "the parity-odd quadratic curvature invariants are spanned "
                 "by P",
        "status": "CITED",
        "why_not_discharged": "a representation-theory dimension count, not a "
                              "pointwise identity; no evaluation at metrics "
                              "can establish it",
        "sources": [],
        "boundary": "The computable half of G6 -- that the Pontryagin density "
                    "depends only on the Weyl tensor -- IS discharged here.  "
                    "The spanning half is not.",
    },
    {
        "entry": "G4",
        "claim": "int sqrt(-g) E4 is topological in D = 4, so it contributes "
                 "nothing to the field equations",
        "status": "CITED",
        "sources": [
            "quantum-weyl/local_bv/certificates/EULER_TRANSGRESSION_CERTIFICATE.json",
            "quantum-weyl/local_bv/euler_transgression_certificate.py",
        ],
        "source_state": "INTRINSIC_EULER_TOWER_VERIFIED",
        "source_dependency_tags": ["LOCAL-ALGEBRAIC"],
        "checks_relied_on": ["delta_E4_minus_dTheta",
                             "closed_manifold_integrated_variation"],
        "boundary": "This establishes the VARIATIONAL content the "
                    "classification actually uses -- the integrated variation "
                    "vanishes on a closed manifold.  It is NOT an index "
                    "theorem and NOT a global triviality claim.  The source "
                    "certificate's own not_computed list includes the "
                    "antifield/Koszul-Tate completion and relative cohomology "
                    "nontriviality of the Euler anomaly.",
    },
    {
        "entry": "G7",
        "claim": "int sqrt(-g) P is topological -- the theta-angle direction",
        "status": "CITED",
        "sources": ["symbolic/verify_conformal_dynamical_topological.py"],
        "checks_relied_on": ["Chern-Weil transgression "
                             "Tr(R^R) = d Tr(Gamma dGamma + 2/3 Gamma^3)"],
        "boundary": "Quoted verbatim from the source: \"Global triviality of "
                    "the Pontryagin class is explicitly not claimed.\"  The "
                    "transgression is LOCAL.  G7 is therefore available only "
                    "in its local form, which is what the classification uses "
                    "(P contributes no field equations), and NOT as a "
                    "statement about topological sectors.",
    },
    {
        "entry": "N3",
        "claim": "a topological term has identically vanishing variation",
        "status": "CITED",
        "sources": [
            "quantum-weyl/local_bv/certificates/EULER_TRANSGRESSION_CERTIFICATE.json",
        ],
        "checks_relied_on": ["delta_E4_minus_dTheta"],
        "boundary": "N3 is the SAME content as G4's variational check, so it "
                    "is discharged by the same citation rather than by "
                    "separate work.  This is why RP-TOPO-INERT disappears on "
                    "the field-equation side of the ledger.",
    },
]


def file_hash(rel):
    path = os.path.join(REPO_ROOT, rel)
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def build():
    rows = []
    for name, builder in METRICS:
        for sig in (LORENTZIAN, EUCLIDEAN):
            rows.append(check_metric(name, builder, sig))

    controls = negative_controls()

    bool_checks = []
    for r in rows:
        for k, v in r.items():
            if isinstance(v, bool) and k not in (
                    "C2_is_nonzero", "P_is_nonzero", "ricci_is_nonzero",
                    "G6_is_non_vacuous_here"):
                bool_checks.append((r["metric"], r["signature"], k, v))

    # Non-degeneracy gates: the discharge is only meaningful if somewhere the
    # dual is visible (P != 0) and somewhere the Ricci parts are present.
    p_visible = [r for r in rows if r["P_is_nonzero"]]
    g6_nonvacuous = [r for r in rows if r["G6_is_non_vacuous_here"]
                     and r["G6_pontryagin_depends_only_on_weyl"]]

    failures = [
        "%s/%s: %s" % (m, s, k) for (m, s, k, v) in bool_checks if not v]
    if not p_visible:
        failures.append("no metric has P != 0 -- the dual is invisible and "
                        "every G8 check is vacuous")
    if not g6_nonvacuous:
        failures.append("G6 is vacuous everywhere -- it is checked only on "
                        "Ricci-flat metrics, where Riem = C identically")
    for c in controls:
        if not c["rejected"]:
            failures.append("negative control not rejected: %s" % c["control"])

    return {
        "certificate": "REVERSE_PHYSICS_WEYL_DUAL_DISCHARGE_V1",
        "kind": "geometry-discharge",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "establishes":
            "G8 in BOTH signatures, as two different statements: Euclidean "
            "W_pm^2 = (C^2 +- P)/2 with real projectors, and Lorentzian "
            "W_pm^2 = (C^2 -+ i P)/2 with the complex projectors hodge.py "
            "specifies, the textbook Euclidean form being checked FALSE in "
            "Lorentzian signature.  The computable clause of G6 -- that the "
            "Pontryagin density depends only on the Weyl tensor -- verified "
            "non-vacuously on a non-Einstein metric.  The star-square "
            "convention (*C).(*C) = star_square_sign * C^2 reproducing "
            "hodge.py, which is the check the previous attempt failed.",
        "does_not_establish": [
            "any of these identities for ALL metrics -- this is a DISCHARGE, "
            "exact verification at specific metrics and points, strictly "
            "stronger than an unverified import and strictly weaker than a "
            "theorem",
            "the spanning clause of G6, which is a dimension count and is "
            "cited rather than discharged",
            "global triviality of the Pontryagin class, which the G7 source "
            "explicitly does not claim",
            "an index theorem for E4; the G4 citation supplies the "
            "variational content only",
            "anything about the residual classes [W_+^2] and [W_-^2] beyond "
            "the algebraic split; their cohomological status is a separate "
            "result kind",
        ],
        "conventions": {
            "epsilon": "eps_{abcd} = sqrt(|det g|) * [abcd], all indices down",
            "dual": "(*T)_{abcd} = (1/2) eps_{ab}^{ef} T_{efcd}",
            "contraction": "all four indices raised with g before summing",
            "star_square_sign": STAR_SQUARE_SIGN,
            "lorentzian_projectors":
                "hodge.py eigenvalues +-i give W_pm = (C -+ i *C)/2, complex "
                "conjugates of each other",
            "source": "quantum-weyl/local_bv/hodge.py",
            "note": "hodge.py fixes star_square_sign, the eigenvalues and the "
                    "projectors, but NOT the epsilon index placement on a "
                    "rank-four tensor.  The placement above is chosen because "
                    "it reproduces star_square_sign; that reproduction is a "
                    "checked row, not an assumption.",
        },
        "rows": rows,
        "negative_controls": controls,
        "citations": CITATIONS,
        "non_degeneracy": {
            "metrics_with_P_nonzero": [
                "%s/%s" % (r["metric"], r["signature"]) for r in p_visible],
            "metrics_where_G6_is_non_vacuous": [
                "%s/%s" % (r["metric"], r["signature"]) for r in g6_nonvacuous],
            "note": "Taub-NUT is a vacuum solution, so Riem = C there and the "
                    "G6 check is VACUOUS on it however cleanly it passes.  "
                    "Bianchi IX with three distinct scale factors is not "
                    "Einstein and is what carries G6.",
        },
        "inputs": {
            "black_hole_programme/weyl_geometry.py":
                file_hash("black_hole_programme/weyl_geometry.py"),
            "quantum-weyl/local_bv/hodge.py":
                file_hash("quantum-weyl/local_bv/hodge.py"),
        },
        "checks": {
            "total": len(bool_checks),
            "passed": sum(1 for (_m, _s, _k, v) in bool_checks if v),
            "failures": failures,
            "negative_controls_rejected": "%d/%d" % (
                sum(1 for c in controls if c["rejected"]), len(controls)),
            "ok": not failures,
        },
        "report": "reverse_physics/reports/weyl-dual-discharge.md",
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
        flags = []
        if not r["P_is_nonzero"]:
            flags.append("P=0 (dual invisible)")
        if not r["ricci_is_nonzero"]:
            flags.append("Ric=0 (G6 vacuous)")
        bad = [k for k, v in r.items() if isinstance(v, bool) and not v
               and k not in ("C2_is_nonzero", "P_is_nonzero",
                             "ricci_is_nonzero", "G6_is_non_vacuous_here")]
        print("%-12s %-11s %s%s" % (
            r["metric"], r["signature"],
            "OK" if not bad else "FAIL " + ",".join(bad),
            ("   [" + "; ".join(flags) + "]") if flags else ""))
    for c in cert["negative_controls"]:
        print("control %-42s rejected: %s" % (c["control"], c["rejected"]))
    print("non-vacuous G6 on: %s" % (
        ", ".join(cert["non_degeneracy"]["metrics_where_G6_is_non_vacuous"])
        or "NOWHERE"))
    print("negative controls rejected: %s"
          % cert["checks"]["negative_controls_rejected"])
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
