"""Four imported geometric facts, discharged against this repository's own exact
curvature engine.

WHY THIS EXISTS.  [PHYSICS-VS-MATH.md] separates the Weyl-gravity ledger into
PHYSICS (assumptions under test), GEOMETRY (imported, isolated) and MATHEMATICS
(proved).  Its own honest-limits section says the quiet part:

    "Geometry is imported wholesale.  G1-G8 are standard, but they are THE BULK
     OF THE INTELLECTUAL CONTENT and none of them is machine-checked here."

and its how-to-attack-this section ranks the sharpest objection first:

    "Reject G5. ... What remains open is that the witness metric -- matter-
     dominated FRW, a(t) = t^(2/3), R = 4/3t^2 -- is NAMED, NOT FORMALISED.
     Formalising it needs a Riemann tensor, which this development does not
     have.  This is the sharpest attack available."

That last sentence was true of the reverse-physics stream and false of the
repository.  `black_hole_programme/weyl_geometry.py` is an exact Christoffel /
Riemann / Ricci / Weyl / Bach engine with frozen BH-0 conventions, already
consumed by a dozen black-hole modules.  The gap was never that the Riemann
tensor did not exist here -- it was that the reverse-physics ledger had not been
wired to it.  (The overview records exactly this lesson from a previous stream:
"search the corpus before deriving".)

WHAT IS DISCHARGED

  G5  the non-degeneracy witness.  Matter-dominated FRW a(t) = t^(2/3) gives
      R = 4/(3 t^2) -- the value the report NAMED -- and box R = -8/(3 t^4),
      which is nonzero.  Without some metric having box R != 0 the whole action
      classification is vacuous, and the module already proves that
      (`without_non_degeneracy_the_classification_is_vacuous`).  The input is now
      computed rather than asserted.

  G1  C^2 = Riem^2 - 2 Ric^2 + R^2/3 in D = 4, equivalently
      C^2 = E4 + 2 Ric^2 - (2/3) R^2 with E4 = Riem^2 - 4 Ric^2 + R^2.  These are
      the coordinate vectors of the whole classification.

  G2  the conformal law R[e^{2s} g] = e^{-2s}(R - 6 box s - 6 (grad s)^2) in D = 4.
      This is what makes the R^2 component carry the anomaly.

  G3  C_abcd[e^{2s} g] = e^{2s} C_abcd -- the Weyl tensor's conformal weight.
      This is the one that matters most: the DERIVED derivative order k = D/2,
      the best result the stream has on Weyl gravity itself, rests on it.

WHAT THIS IS, AND IS NOT.  Each fact is verified EXACTLY (sympy rationals and
symbols, no floating point) at SPECIFIC METRICS chosen to be non-vacuous -- a
non-Einstein, non-conformally-flat one is included so the identities are not
satisfied by zeros.  That is strictly stronger than an unverified import and
strictly weaker than a theorem for all metrics.  It is a discharge, not a proof,
and the certificate says so in those words.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.weyl_geometry_discharge --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from black_hole_programme.weyl_geometry import Geometry

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_WEYL_GEOMETRY_DISCHARGE_V1.json"

RESULT_ID = "REVERSE_PHYSICS_WEYL_GEOMETRY_DISCHARGE_V1"
SCHEMA_NAME = "reverse-physics-weyl-geometry-discharge-v1"

PINNED = {
    "curvature_engine": ROOT / "black_hole_programme/weyl_geometry.py",
    "weyl_action_witnesses": ROOT / "rocq/WeylActionClassification.v",
    # The VARIATIONAL link itself is not re-derived here.  It is checked elsewhere
    # in this repository on the Nariai product family, and cited rather than
    # repeated -- see `variational_link_is_imported` below.
    "nariai_action_derived_bach": ROOT / (
        "d_quotient_classical/reports/nariai-action-derived-bach-endpoint.md"
    ),
}

T, R_, TH, PH, MM = sp.symbols("t r theta phi M", positive=True)
TT = sp.symbols("t", positive=True)


def metrics():
    """Test metrics, ordered by how much they can hide.

    Schwarzschild is Ricci-flat, so any identity with a Ric^2 term is only half
    tested by it.  Schwarzschild-de Sitter switches R on.  The last one is
    neither Einstein nor conformally flat, which is what makes the identities
    non-vacuous -- its C^2 is a genuinely messy rational function.
    """
    f = 1 - 2 * MM / R_
    sph = R_**2 * sp.sin(TH) ** 2
    yield ("schwarzschild", [T, R_, TH, PH], sp.diag(-f, 1 / f, R_**2, sph))
    k = sp.Rational(1, 7)
    fk = f - k * R_**2
    yield ("schwarzschild_de_sitter", [T, R_, TH, PH], sp.diag(-fk, 1 / fk, R_**2, sph))
    yield ("non_einstein_static", [T, R_, TH, PH],
           sp.diag(-(1 + MM * R_**2), 1 / f, R_**2, sph))


def box_scalar(coords, g, phi):
    """box phi = (1/sqrt(-g)) d_a( sqrt(-g) g^{ab} d_b phi ), exact."""
    ginv = g.inv()
    sr = sp.sqrt(-sp.simplify(g.det()))
    total = sp.Integer(0)
    for i, xi in enumerate(coords):
        for j, xj in enumerate(coords):
            if ginv[i, j] != 0:
                total += sp.diff(sr * ginv[i, j] * sp.diff(phi, xj), xi)
    return sp.simplify(total / sr)


def grad_sq(coords, g, phi):
    ginv = g.inv()
    return sp.simplify(sum(ginv[i, j] * sp.diff(phi, coords[i]) * sp.diff(phi, coords[j])
                           for i in range(len(coords)) for j in range(len(coords))
                           if ginv[i, j] != 0))


def check_g5():
    """The non-degeneracy witness, computed rather than named."""
    a = TT ** sp.Rational(2, 3)
    coords = [TT] + list(sp.symbols("x y z", positive=True))
    g = sp.diag(-1, a**2, a**2, a**2)
    R = sp.simplify(Geometry(coords, g).Rscalar)
    box = box_scalar(coords, g, R)
    return {
        "witness": "matter-dominated FRW, a(t) = t^(2/3)",
        "R": sp.srepr(R),
        "R_matches_the_named_value_4_over_3tsq": sp.simplify(R - sp.Rational(4, 3) / TT**2) == 0,
        "box_R": sp.srepr(box),
        "box_R_is_nonzero": sp.simplify(box) != 0,
    }


def check_g1_g3(name, coords, g):
    """G1 (the coordinate vectors) and G3 (the Weyl weight) on one metric."""
    G = Geometry(coords, g)
    inv = G.invariants()
    c2, kre, ric2, rs = inv["WeylSq"], inv["Kretschmann"], inv["RicciSq"], inv["R"]
    e4 = kre - 4 * ric2 + rs**2

    out = {
        "metric": name,
        "C2": sp.srepr(sp.simplify(c2)),
        "C2_is_nonzero": sp.simplify(c2) != 0,          # non-vacuity
        "G1_C2_eq_Riem2_minus_2Ric2_plus_R2_over_3":
            sp.simplify(c2 - (kre - 2 * ric2 + rs**2 / 3)) == 0,
        "G1_C2_eq_E4_plus_2Ric2_minus_2R2_over_3":
            sp.simplify(c2 - (e4 + 2 * ric2 - sp.Rational(2, 3) * rs**2)) == 0,
        # WHICH COEFFICIENT CAN THIS METRIC SEE?  A Ricci-flat metric has R = 0
        # and Ric^2 = 0, so BOTH the R^2/3 and the -2 Ric^2 coefficients are
        # invisible to it -- the identity reduces to C^2 = Riem^2 and would hold
        # for any coefficients whatsoever.  Recording this per metric is the
        # honest form: a control aggregated over all of them would be vacuous,
        # and silently so.
        "R_is_nonzero": sp.simplify(rs) != 0,
        "Ric2_is_nonzero": sp.simplify(ric2) != 0,
        # NEGATIVE CONTROLS, meaningful only on a metric that can see the term.
        "control_wrong_R2_coefficient_fails":
            (sp.simplify(rs) != 0) and sp.simplify(c2 - (kre - 2 * ric2 + rs**2 / 4)) != 0,
        "control_wrong_Ric2_coefficient_fails":
            (sp.simplify(ric2) != 0) and sp.simplify(c2 - (kre - 3 * ric2 + rs**2 / 3)) != 0,
    }
    return out


def check_g2_g3_conformal(name, coords, g, sigma, sigma_name):
    """G2 (the conformal law for R) and G3 (the Weyl weight) under e^{2 sigma}."""
    gt = sp.exp(2 * sigma) * g
    G, Gt = Geometry(coords, g), Geometry(coords, gt)
    rs, rst = G.Rscalar, sp.simplify(Gt.Rscalar)
    pred = sp.exp(-2 * sigma) * (rs - 6 * box_scalar(coords, g, sigma)
                                 - 6 * grad_sq(coords, g, sigma))
    c, ct = G.Weyl, Gt.Weyl
    n = len(coords)
    idx = [(a, b, cc, d) for a in range(n) for b in range(n)
           for cc in range(n) for d in range(n)]
    weight_ok = all(sp.simplify(ct[a][b][cc][d] - sp.exp(2 * sigma) * c[a][b][cc][d]) == 0
                    for (a, b, cc, d) in idx)
    # NEGATIVE CONTROL: the WRONG weight must fail, on a component that is nonzero
    nonzero = [(a, b, cc, d) for (a, b, cc, d) in idx if sp.simplify(c[a][b][cc][d]) != 0]
    wrong_weight_fails = bool(nonzero) and any(
        sp.simplify(ct[a][b][cc][d] - sp.exp(4 * sigma) * c[a][b][cc][d]) != 0
        for (a, b, cc, d) in nonzero)
    return {
        "metric": name,
        "sigma": sigma_name,
        "G2_conformal_law_for_R": sp.simplify(rst - pred) == 0,
        "G2_control_wrong_coefficient_fails":
            sp.simplify(rst - sp.exp(-2 * sigma) * (rs - 5 * box_scalar(coords, g, sigma)
                                                    - 6 * grad_sq(coords, g, sigma))) != 0,
        "G3_weyl_has_conformal_weight_two": weight_ok,
        "G3_weyl_is_not_identically_zero": bool(nonzero),
        "G3_control_wrong_weight_fails": wrong_weight_fails,
    }


def check_field_equations():
    """The FIELD-EQUATION layer, which the ledger records as never computed.

    It is computed -- `weyl_geometry.py` has had a Bach tensor all along.  What can
    be checked pointwise, and is:

      N1   nabla^a B_ab = 0.  This IS the Noether/diff content: the metric
           variation of a local diff-invariant action is divergence-free.  Stated
           in the ledger as an imported fact; here it is computed for the actual
           tensor.
      -    g^ab B_ab = 0, the trace-free property that makes the field equations
           conformally invariant, and B_ab[e^{2s}g] = e^{-2s} B_ab, which is that
           invariance directly.
      -    B_ab = 0 on an Einstein metric.  Not decoration: it is why Schwarzschild
           solves Weyl gravity at all, which the entire black-hole programme rests
           on, and it is checked here rather than assumed.
      -    B_ab != 0 on a non-Einstein metric, so none of the above is vacuous.
    """
    f = 1 - 2 * MM / R_
    sph = R_**2 * sp.sin(TH) ** 2
    coords = [T, R_, TH, PH]
    einstein = sp.diag(-f, 1 / f, R_**2, sph)
    generic = sp.diag(-(1 + MM * R_**2), 1 / f, R_**2, sph)

    Ge = Geometry(coords, einstein)
    Be = Ge.bach()
    einstein_flat = all(sp.simplify(Be[a, b]) == 0 for a in range(4) for b in range(4))

    G = Geometry(coords, generic)
    B = G.bach()
    ginv = generic.inv()
    nonzero = any(sp.simplify(B[a, b]) != 0 for a in range(4) for b in range(4))
    trace = sp.simplify(sum(ginv[a, b] * B[a, b] for a in range(4) for b in range(4)))
    symmetric = all(sp.simplify(B[a, b] - B[b, a]) == 0 for a in range(4) for b in range(4))
    div = [sp.simplify(sum(ginv[a, e] * G.covd2(B, e, a, b)
                           for a in range(4) for e in range(4) if ginv[a, e] != 0))
           for b in range(4)]
    sigma = R_**2 / 8
    Bt = Geometry(coords, sp.exp(2 * sigma) * generic).bach()
    weight = all(sp.simplify(Bt[a, b] - sp.exp(-2 * sigma) * B[a, b]) == 0
                 for a in range(4) for b in range(4))

    return {
        "N1_bach_is_divergence_free": all(d == 0 for d in div),
        "bach_is_trace_free": trace == 0,
        "bach_is_symmetric": symmetric,
        "bach_has_conformal_weight_minus_two": weight,
        "bach_vanishes_on_an_einstein_metric": einstein_flat,
        "bach_is_nonzero_on_a_non_einstein_metric": nonzero,
    }


def check_g5_witness_is_a_real_choice():
    """Schwarzschild is Ricci-flat, so R = 0 and box R = 0: it does NOT witness G5.

    Without this, "some metric has box R != 0" would look like a formality
    satisfied by whatever metric came to hand.  It is not -- the vacuum solutions
    the rest of this repository spends its time on all fail it.
    """
    f = 1 - 2 * MM / R_
    coords = [T, R_, TH, PH]
    g = sp.diag(-f, 1 / f, R_**2, R_**2 * sp.sin(TH) ** 2)
    R = sp.simplify(Geometry(coords, g).Rscalar)
    return {
        "metric": "schwarzschild",
        "R_is_identically_zero": sp.simplify(R) == 0,
        "therefore_box_R_is_zero_and_it_cannot_witness_G5":
            sp.simplify(box_scalar(coords, g, R)) == 0,
    }


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    g5 = check_g5()
    g1 = [check_g1_g3(n, c, g) for (n, c, g) in metrics()]
    f = 1 - 2 * MM / R_
    sph = R_**2 * sp.sin(TH) ** 2
    base = ("schwarzschild", [T, R_, TH, PH], sp.diag(-f, 1 / f, R_**2, sph))
    g23 = [check_g2_g3_conformal(base[0], base[1], base[2], s, nm)
           for (nm, s) in [("r^2/8", R_**2 / 8), ("log(r)/3", sp.log(R_) / 3)]]
    control = check_g5_witness_is_a_real_choice()
    fe = check_field_equations()

    checks = {
        **fe,
        "G5_R_matches_named_value": g5["R_matches_the_named_value_4_over_3tsq"],
        "G5_box_R_nonzero": g5["box_R_is_nonzero"],
        "G5_witness_is_a_real_choice": (control["R_is_identically_zero"]
                                        and control["therefore_box_R_is_zero_and_it_cannot_witness_G5"]),
        "G1_holds_on_every_metric": all(m["G1_C2_eq_Riem2_minus_2Ric2_plus_R2_over_3"] for m in g1),
        "G1_E4_form_holds_on_every_metric": all(m["G1_C2_eq_E4_plus_2Ric2_minus_2R2_over_3"] for m in g1),
        "G1_is_non_vacuous": all(m["C2_is_nonzero"] for m in g1),
        # The discriminating controls, applied only where they can discriminate --
        # and asserted to be applicable SOMEWHERE, which is the part that stops the
        # whole check from being satisfied by Ricci-flat metrics alone.
        "G1_some_metric_can_see_the_R2_term": any(m["R_is_nonzero"] for m in g1),
        "G1_some_metric_can_see_the_Ric2_term": any(m["Ric2_is_nonzero"] for m in g1),
        "G1_wrong_R2_coefficient_is_rejected_wherever_visible":
            all(m["control_wrong_R2_coefficient_fails"] for m in g1 if m["R_is_nonzero"]),
        "G1_wrong_Ric2_coefficient_is_rejected_wherever_visible":
            all(m["control_wrong_Ric2_coefficient_fails"] for m in g1 if m["Ric2_is_nonzero"]),
        "G2_holds_for_every_sigma": all(m["G2_conformal_law_for_R"] for m in g23),
        "G2_wrong_coefficient_is_rejected": all(m["G2_control_wrong_coefficient_fails"] for m in g23),
        "G3_weyl_weight_two_for_every_sigma": all(m["G3_weyl_has_conformal_weight_two"] for m in g23),
        "G3_is_non_vacuous": all(m["G3_weyl_is_not_identically_zero"] for m in g23),
        "G3_wrong_weight_is_rejected": all(m["G3_control_wrong_weight_fails"] for m in g23),
    }

    return {
        "schema": SCHEMA_NAME,
        "result_id": RESULT_ID,
        "result_state": "IMPORTED_GEOMETRY_PARTIALLY_DISCHARGED",
        "lifecycle_ladder": "reverse-physics-v0",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "record_kind": (
            "DISCHARGE — moves four facts from the GEOMETRY column (imported, "
            "unverified) toward the MATHEMATICS column, by computing them in this "
            "repository's own exact curvature engine"
        ),
        "what_this_is": (
            "each fact verified EXACTLY at specific metrics chosen to be non-vacuous. "
            "STRICTLY STRONGER than an unverified import and STRICTLY WEAKER than a "
            "theorem for all metrics. A discharge, not a proof."
        ),
        "discharged": {
            "N1": "the Noether/diff fact, computed as nabla^a B_ab = 0 for the actual Bach tensor rather than imported",
            "G5": "the non-degeneracy witness, previously NAMED and not formalised — the report's own sharpest self-identified attack",
            "G1": "C^2 = Riem^2 - 2Ric^2 + R^2/3, the coordinate vectors of the classification",
            "G2": "the conformal law for R, which makes the R^2 component carry the anomaly",
            "G3": "the Weyl tensor's conformal weight, which the DERIVED derivative order k = D/2 rests on",
        },
        "still_imported": {
            "G4": "int sqrt(-g) E4 is topological in D = 4 — a global statement, not reachable pointwise",
            "G6": "the parity-odd quadratic invariants are spanned by P; P = C.Cdual in D = 4 — the engine has no dual yet",
            "G7": "int sqrt(-g) P is topological — global, as G4",
            "G8": "W±^2 = (C^2 ± P)/2 — follows from G6 once the dual exists",
            "N2_N3": "the remaining Noether facts. N2 (the trace of the variation is a nonzero multiple of the anomaly) is a quantum statement; N3 (a topological term has vanishing variation) needs the variation of E4, not curvature at a point",
        },
        "variational_link_is_imported": {
            "identity": "delta int sqrt(-g) C^2 = 4 int sqrt(-g) B_mn delta g^mn",
            "status": "NOT re-derived here — cited",
            "where_it_is_checked_in_this_repository": (
                "d_quotient_classical/reports/nariai-action-derived-bach-endpoint.md: an "
                "independent product-family calculation for g(x,y) = x g_dS2 + y g_S2 gives "
                "the standard variation diag(2/3, -2/3, 2/3, 2/3) along d_x - d_y, and the "
                "normal-frame operator reproduces its action-normalized value exactly, with "
                "B_action = -2 B_standard"
            ),
            "also": (
                "black_hole_programme/bh1b_dynamical.py records the Lee-Wald form "
                "delta(sqrt(-g) alpha C^2) = div(sqrt(-g) theta) exactly on shell; "
                "symbolic/verify_conformal_dynamical_topological.py states the same "
                "variation as a DECLARED field-theory identity and does not re-derive it"
            ),
            "what_is_computed_here_instead": (
                "the consequences of that link that are visible pointwise -- N1, "
                "trace-freeness, conformal weight, and Einstein => Bach-flat"
            ),
        },
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "G5_detail": g5,
        "G1_detail": g1,
        "G2_G3_detail": g23,
        "G5_negative_control_detail": control,
        "field_equation_detail": fe,
        "does_not_establish": [
            "any of these identities FOR ALL METRICS — they are verified at three static metrics and one FRW metric",
            "the R^2 or Ric^2 coefficients of G1 from a Ricci-flat metric alone: both terms VANISH there, so Schwarzschild cannot discriminate them and the certificate records which metric sees which term",
            "G4, G6, G7, G8 or the Noether facts N1-N3, which remain imported",
            "that the curvature engine's BH-0 conventions are the right ones; they are pinned by hash and adopted, not re-derived",
            "anything about the quantum theory, the BV-BFV complex, or the residual classes",
        ],
        "source_manifest": {str(p.relative_to(ROOT)): sha(p) for p in PINNED.values()},
        "verification_commands": [
            "PYTHONPATH=. python3 -m reverse_physics.weyl_geometry_discharge --check",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    fresh = build()
    if fresh["status"] != "PASS":
        bad = [k for k, v in fresh["checks"].items() if not v]
        print("FAIL: " + ", ".join(bad))
        return 1

    if args.check:
        if not OUTPUT.exists():
            print(f"FAIL: {OUTPUT.relative_to(ROOT)} is missing")
            return 1
        stored = json.loads(OUTPUT.read_text())
        for field in ("checks", "source_manifest", "discharged", "still_imported"):
            if stored.get(field) != fresh[field]:
                print(f"FAIL: {field} drifted from the stored certificate")
                return 1
        print(f"{RESULT_ID}: PASS — {len(fresh['checks'])} exact checks, engine pinned")
        return 0

    OUTPUT.write_text(json.dumps(fresh, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
