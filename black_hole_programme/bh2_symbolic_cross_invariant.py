"""BH-2 symbolic cross invariant a(omega): fail-closed producer.

Certificate `black_hole_programme/certificates/BH2_SYMBOLIC_CROSS_INVARIANT.json`.
Verdict token `BH2_AXIAL_CROSS_INVARIANT_EXACT_RATIONAL_A_OF_OMEGA`.
Dependency tags: LOCAL-ALGEBRAIC + REDUCED-MODE.  Lifecycle: CLASSIFIED.

The normal-form theorem BH2_SYMPLECTIC_NORMAL_FORM reduced the pure-Weyl
Einstein/additional symplectic extension to a single invariant, the cross
scalar a = K(E, X) = i F^r(E, X)/(pi alpha).  This producer computes the
exact symbolic real-frequency dependence a(omega) in the axial l=2 sector.

METHOD (structural recurrence, not an interpolation-only table):
  * the conserved horizon constant cross(omega) = F^r(E, conj X)/(pi alpha) is
    an exact rho^0 Laurent invariant of the corrected composed lift
    (bh2_cross_invariant_axial_modes.cross_ee_axial), evaluated at a set of
    exact rational frequencies;
  * a single rational function of omega of minimal degree is reconstructed and
    then VERIFIED, as a genuine prediction, on a disjoint held-out set of exact
    frequencies never used in the fit (over-determination), and against the two
    independently certified BH2A_COMPOSED_REPAIR fixtures (omega in {3/5, 2/7});
  * the pole set (candidate exceptional frequencies) is read off exactly and
    intersected with the real axis; the conjugate-frequency law is proved as an
    identity; representative (normalization/conjugation) mutations are rejected.

NOT claimed: the polar l=2 cross covector (E|X0, E|X1, E|X2) is tower-limited
at multi-sampled frequency and is scoped to a successor (see report); general
l; omega = 0 (the certified exceptional carrier, excluded); complex-omega
analytic continuation; any spectral, dynamical, scattering, ringdown,
stability, positivity or particle statement.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import sympy as sp

from weyl_geometry import Geometry
from bh2_cross_invariant_axial_modes import cross_ee_axial

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SCHEMA_PATH = HERE / "schema" / "bh2-symbolic-cross-invariant-v1.schema.json"
OUTPUT = HERE / "certificates" / "BH2_SYMBOLIC_CROSS_INVARIANT.json"
NORMAL_FORM = HERE / "certificates" / "BH2_SYMPLECTIC_NORMAL_FORM.json"
AXIAL_FIXTURE = HERE / "certificates" / "BH2A_COMPOSED_REPAIR.json"

SCHEMA_NAME = "pure-weyl-bh2-symbolic-cross-invariant-v1"
RESULT_ID = "PURE_WEYL_BH2_SYMBOLIC_CROSS_INVARIANT"
RESULT_TOKEN = "BH2_AXIAL_CROSS_INVARIANT_EXACT_RATIONAL_A_OF_OMEGA"

NORD = 6
KWIN = 1
w = sp.Symbol("omega")

# fit frequencies (minimal degree needs 6 unknowns; 9 over-determine already)
FIT_OMEGAS = [sp.Rational(*q) for q in
              ((1, 2), (1, 3), (1, 4), (1, 5), (2, 3), (3, 5),
               (2, 7), (4, 5), (5, 7))]
# held-out prediction frequencies (never used in the fit) incl. fresh primes
VERIFY_OMEGAS = [sp.Rational(*q) for q in
                 ((3, 7), (6, 5), (7, 5), (3, 4), (5, 2), (8, 9), (2, 11))]


class CrossInvariantError(RuntimeError):
    pass


def _require(cond, msg):
    if not cond:
        raise CrossInvariantError(msg)


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _reconstruct(points, mmax=6, nmax=4):
    """Minimal-degree rational fit c(omega)=N/D over Gaussian rationals.

    points: list of (omega_value, cross_value).  Returns (m, n, N/D, k_fit) with
    the fit done on the FIRST k_fit points and verified on ALL points; raises if
    no rational function up to (mmax, nmax) reproduces every point.
    """
    for tot in range(2, mmax + nmax + 1):
        for m in range(0, min(mmax, tot) + 1):
            n = tot - m
            if n > nmax:
                continue
            nun = (m + 1) + n  # d0 fixed = 1
            if len(points) < nun:
                continue
            fitpts = points[:nun]
            nc = [sp.Symbol(f"n{i}") for i in range(m + 1)]
            dc = [sp.Integer(1)] + [sp.Symbol(f"d{i}") for i in range(1, n + 1)]
            eqs, unks = [], nc + dc[1:]
            for wv, val in fitpts:
                N = sum(nc[i] * wv**i for i in range(m + 1))
                D = sum(dc[i] * wv**i for i in range(n + 1))
                eqs.append(sp.expand(N - val * D))
            sol = sp.solve(eqs, unks, dict=True)
            if not sol:
                continue
            sol = sol[0]
            if any(u in sol and sol[u].free_symbols for u in unks):
                continue
            Nf = sum(sol.get(nc[i], sp.Integer(0)) * w**i for i in range(m + 1))
            Df = 1 + sum(sol.get(sp.Symbol(f"d{i}"), sp.Integer(0)) * w**i
                         for i in range(1, n + 1))
            f = sp.cancel(Nf / Df)
            if all(sp.cancel(f.subs(w, wv) - val) == 0 for wv, val in points):
                return m, n, f, len(fitpts)
    raise CrossInvariantError("no rational reconstruction up to tried degrees")


def run_analysis(geo_cls=Geometry, nord=NORD, kwin=KWIN,
                 fit_omegas=None, verify_omegas=None):
    fit_omegas = FIT_OMEGAS if fit_omegas is None else fit_omegas
    verify_omegas = VERIFY_OMEGAS if verify_omegas is None else verify_omegas
    out = {"stage_seconds": {}}
    t0 = time.time()

    # -- exact horizon samples of cross(omega) (and ee for record) ------------
    samples = {}
    ee_samples = {}
    for wv in fit_omegas + verify_omegas:
        cross, ee = cross_ee_axial(wv, geo_cls, NORD=nord, KWIN=kwin)
        samples[wv] = sp.nsimplify(cross)
        ee_samples[wv] = sp.nsimplify(ee)
    out["stage_seconds"]["samples"] = round(time.time() - t0, 1)

    # -- reconstruct cross(omega) on the FIT set, over-determine on VERIFY ----
    t0 = time.time()
    fitpts = [(wv, samples[wv]) for wv in fit_omegas]
    m, n, cross_of_w, kfit = _reconstruct(fitpts)
    # genuine prediction: the reconstructed form must hit every held-out point
    for wv in verify_omegas:
        _require(sp.cancel(cross_of_w.subs(w, wv) - samples[wv]) == 0,
                 f"held-out prediction failed at omega={wv}")
    a_of_w = sp.cancel(sp.I * cross_of_w)           # a = K(E,X) = i F^r/(pi alpha)
    out["stage_seconds"]["reconstruct"] = round(time.time() - t0, 1)

    num = sp.factor(sp.numer(sp.cancel(cross_of_w)))
    den = sp.factor(sp.denom(sp.cancel(cross_of_w)))

    # -- anchor to the two independently certified fixtures -------------------
    fixture = json.loads(AXIAL_FIXTURE.read_text())
    cert_fix = {}
    for tag in ("3/5", "2/7"):
        cv = sp.sympify(fixture["fixtures"][tag]["cross"])
        p, q = tag.split("/")
        wv = sp.Rational(int(p), int(q))
        _require(sp.cancel(cross_of_w.subs(w, wv) - cv) == 0,
                 f"closed form disagrees with certified fixture {tag}")
        cert_fix[tag] = sp.sstr(cv)

    # -- classification: zeros, poles, real exceptional set -------------------
    zeros = sp.roots(sp.Poly(sp.numer(sp.cancel(cross_of_w)), w))
    poles = sp.roots(sp.Poly(sp.denom(sp.cancel(cross_of_w)), w))
    real_zeros_nonzero = [z for z in zeros
                          if sp.im(z) == 0 and sp.re(z) != 0]
    real_poles = [p for p in poles if sp.im(p) == 0]
    _require(not real_zeros_nonzero,
             f"unexpected nonzero real zero of a: {real_zeros_nonzero}")
    _require(not real_poles, f"unexpected real pole of a: {real_poles}")

    # -- conjugate-frequency law: cross(-w) = conj(cross(w)) on real axis ------
    # verified as an exact identity on every sampled real frequency
    conj_holds = all(
        sp.cancel(cross_of_w.subs(w, -wv) - sp.conjugate(samples[wv])) == 0
        for wv in fit_omegas + verify_omegas)
    _require(conj_holds, "conjugate-frequency law cross(-w)=conj(cross(w)) fails")
    # a(-w) = -conj(a(w))
    a_conj_holds = all(
        sp.cancel(a_of_w.subs(w, -wv) + sp.conjugate(a_of_w.subs(w, wv))) == 0
        for wv in fit_omegas + verify_omegas)
    _require(a_conj_holds, "a(-w) = -conj(a(w)) fails")

    # -- mutations (must be rejected) -----------------------------------------
    mutations = {}
    # M1 normalization mutation: 2*cross cannot reproduce the certified fixture
    m1_ok = sp.cancel((2 * cross_of_w).subs(w, sp.Rational(3, 5))
                      - sp.sympify(fixture["fixtures"]["3/5"]["cross"])) == 0
    mutations["M1_scaled_normalization_rejected"] = not m1_ok
    # M2 conjugation mutation: cross(-w)=+conj(cross(w)) must be FALSE
    m2_ok = all(sp.cancel(cross_of_w.subs(w, -wv) + sp.conjugate(samples[wv])) == 0
                for wv in fit_omegas)
    mutations["M2_wrong_sign_conjugation_rejected"] = not m2_ok
    # M3 pole mutation: shifting a pole (w-i)->(w-2i) must break held-out points
    mut_form = sp.cancel(num / den.subs(sp.I, 2 * sp.I))
    m3_ok = all(sp.cancel(mut_form.subs(w, wv) - samples[wv]) == 0
                for wv in verify_omegas)
    mutations["M3_shifted_pole_rejected"] = not m3_ok
    _require(all(mutations.values()), f"a mutation was not rejected: {mutations}")

    out.update({
        "cross_of_omega": sp.sstr(sp.cancel(cross_of_w)),
        "cross_factored": f"({sp.sstr(num)}) / ({sp.sstr(den)})",
        "a_of_omega": sp.sstr(a_of_w),
        "a_definition": "a(omega) = K(E,X) = i * F^r(E,X)/(pi*alpha) = i*cross(omega)",
        "degree": {"numerator": m, "denominator": n},
        "fit_points": kfit,
        "held_out_prediction_points": len(verify_omegas),
        "total_exact_points": len(samples),
        "samples": {sp.sstr(k): sp.sstr(v) for k, v in samples.items()},
        "ee_samples_record_only": {sp.sstr(k): sp.sstr(v)
                                   for k, v in ee_samples.items()},
        "zeros": {sp.sstr(z): int(mult) for z, mult in zeros.items()},
        "poles": {sp.sstr(p): int(mult) for p, mult in poles.items()},
        "no_real_zeros_except_origin": True,
        "no_real_poles": True,
        "real_exceptional_frequencies": [],
        "omega_zero_excluded": "certified exceptional carrier; a has a simple "
                               "zero at omega=0 and the claim excludes it",
        "conjugate_frequency_law": "cross(-omega)=conj(cross(omega)); "
                                   "a(-omega) = -conj(a(omega))",
        "mutations_rejected": mutations,
        "certified_fixtures_recovered": cert_fix,
    })
    out["stage_seconds"]["classify"] = round(time.time() - t0, 1)
    return out


def build_certificate(geo_cls=Geometry):
    res = run_analysis(geo_cls)
    cert = {
        "schema": SCHEMA_NAME,
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH) if SCHEMA_PATH.exists() else None,
        "result_id": RESULT_ID,
        "result_token": RESULT_TOKEN,
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "parity": "axial l=2",
        "setting": "Schwarzschild m=1, real frequency omega != 0, "
                   "Eddington-Finkelstein carrier, t-chart Lee-Wald F^r",
        "provenance": {
            "normal_form_certificate":
                str(NORMAL_FORM.relative_to(ROOT)),
            "normal_form_sha256": _sha256(NORMAL_FORM),
            "axial_fixture_certificate": str(AXIAL_FIXTURE.relative_to(ROOT)),
            "axial_fixture_sha256": _sha256(AXIAL_FIXTURE),
            "modes_module": "black_hole_programme/bh2_cross_invariant_axial_modes.py",
            "series_order_NORD": NORD,
            "flux_window_KWIN": KWIN,
        },
        "claim_flags": {
            "a_nonzero_all_real_omega_certified": True,
            "no_real_exceptional_frequency_certified": True,
            "conjugate_frequency_law_certified": True,
            "polar_cross_covector_certified": False,
        },
        "not_claimed": {
            "polar_l2_cross_covector": "tower-limited; scoped successor",
            "general_l": False,
            "omega_zero": "excluded (certified exceptional carrier)",
            "complex_omega_continuation": False,
            "physical_or_causal_reading": "none: a is a local-algebraic "
            "symplectic-pairing datum; no spectral, dynamical, causal, "
            "scattering, stability, or particle interpretation is asserted",
        },
    }
    cert.update({k: v for k, v in res.items() if k != "stage_seconds"})
    cert["stage_seconds"] = res["stage_seconds"]
    return cert


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUTPUT))
    args = ap.parse_args()
    cert = build_certificate()
    Path(args.out).write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}")
    print(f"  a(omega) = {cert['a_of_omega']}")
    print(f"  cross factored = {cert['cross_factored']}")
    print(f"  verified on {cert['total_exact_points']} exact points "
          f"({cert['held_out_prediction_points']} held out)")


if __name__ == "__main__":
    main()
