"""BH-2B stage 4: polar flux matrix stage 1 -- the Einstein branch is
symplectically null in the even-parity sector.

Fail-closed builder for
`black_hole_programme/certificates/BH2B_POLAR_FLUX.json`.

Verdict: BH2B_POLAR_FLUX_STAGE1_EINSTEIN_BRANCH_SYMPLECTICALLY_NULL.

Exact results (Schwarzschild, symbolic m, polar l=2, RW gauge, rational
chart x = cos theta):

1. machinery controls: the action-derived symplectic current reproduces
   the certified BH-1B values (conformal x parameter degeneracy and the
   static pair current 48 alpha/(19 r^2));
2. the general polar bilinear: sphere-integrated symplectic density F^t
   and radial flux F^r between two arbitrary RW-gauge polar perturbations
   (H0, H1, H2, K)_{a,b}(t, r), stored exactly in the certificate;
3. the exact OFF-SHELL identity
       d_t F^t + d_r F^r = 4 alpha Int_S2 sqrt(g) [h_B . dB(h_A) - h_A . dB(h_B)]
   (on-shell conservation + action normalization pinned);
4. Einstein-branch block: substituting two on-shell polar Einstein modes
   (K_i, H1_i) e^{i w_i t} (H2 = H0, H0 algebraic; reduction modulo the
   certified 2-dim system of BH-2B stage 3), the radial flux becomes an
   exact bilinear whose four coefficients ALL carry the factor
   (omega_1 + omega_2); the diagonal (K,K) and (H1,H1) coefficients carry
   (omega_1^2 - omega_2^2).  For conjugate pairs omega_2 = -omega_1 the
   flux VANISHES IDENTICALLY: the polar Einstein branch is SYMPLECTICALLY
   NULL -- the even-parity twin of the certified axial RW-null theorem;
5. conformal-gauge control: the sphere-integrated symplectic pairing of
   the linearized conformal direction h = Phi g (Phi = phi(t, r) P2,
   arbitrary phi) with an arbitrary RW-gauge polar perturbation is
   computed exactly; its value (zero or not) is recorded fail-closed and
   asserted, pinning how the conformal direction pairs under the polar
   presymplectic form.

Consequence: in BOTH parity sectors of l = 2, Einstein gravitational
waves carry zero Lee--Wald flux in pure Weyl gravity; all polar symplectic
pairing must live in blocks involving the extra (Ricci-carrier) branch.

NOT claimed: polar extra x extra and Einstein x extra block values or
signs (requires the polar delta Ric[h] = psi composition), operator
domains, causal disposition, general l, omega = 0, non-Einstein
backgrounds, growth/stability, or any ringdown statement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import sympy as sp

from linearized_bach import LinearizedBach
from linearized_theta import LinearizedTheta
from weyl_geometry import Geometry, mk_metric_function, static_spherical_metric

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "certificates" / "BH2B_POLAR_FLUX.json"
SCHEMA_PATH = HERE / "schema" / "bh2b-polar-flux-v1.schema.json"
BH1B_CERT = HERE / "certificates" / "BH1B_DYNAMICAL_EXTENSION.json"
BH2BE_CERT = HERE / "certificates" / "BH2B_POLAR_EINSTEIN.json"

SCHEMA_NAME = "pure-weyl-bh2b-polar-flux-v1"
RESULT_ID = "PURE_WEYL_BH2B_POLAR_FLUX"
RESULT_TOKEN = "BH2B_POLAR_FLUX_STAGE1_EINSTEIN_BRANCH_SYMPLECTICALLY_NULL"


class PolarFluxError(RuntimeError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise PolarFluxError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _cancel(e):
    return sp.cancel(sp.together(e))


def run_flux_analysis(geo_cls) -> dict:
    t0_all = time.time()
    out: dict = {"stage_seconds": {}}
    t, ph = sp.symbols("t phi")
    r, th = sp.symbols("r theta", positive=True)
    x = sp.Symbol("x")
    m = sp.Symbol("m", positive=True)
    alpha = sp.Symbol("alpha")
    w = sp.Symbol("omega")
    w1, w2 = sp.symbols("omega1 omega2")

    def stage(name, t0):
        out["stage_seconds"][name] = round(time.time() - t0, 1)
        print(f"[{name}] {out['stage_seconds'][name]} s", flush=True)

    # ---- 1. machinery controls (certified BH-1B values) -------------------
    t0 = time.time()
    tc = [t, r, th, ph]
    B_s = 1 - 2 * m / r
    g_s = static_spherical_metric(B_s, 1 / B_s, r, th)
    lt_s = LinearizedTheta(geo_cls(tc, g_s), alpha)
    om_c = sp.Function("omega_c")(t, r)
    h_par = sp.Matrix(4, 4, lambda i, j: sp.diff(
        static_spherical_metric(1 - 2 * m / r, 1 / (1 - 2 * m / r), r, th)[i, j], m))
    w_cp = lt_s.omega(2 * om_c * g_s, h_par)
    _require(all(v == 0 for v in w_cp), "control: omega(conf, param) != 0")
    beta, gam, kk = sp.symbols("beta gamma k")
    fx = {beta: sp.Rational(3, 2), gam: sp.Rational(12, 19), kk: sp.Rational(1, 19)}
    Bfam = mk_metric_function(beta, gam, kk, r)
    gfam = static_spherical_metric(Bfam, 1 / Bfam, r, th)
    lt_f = LinearizedTheta(geo_cls(tc, gfam.subs(fx)), alpha)
    w_bg = lt_f.omega(
        sp.Matrix(4, 4, lambda i, j: sp.diff(gfam[i, j], beta)).subs(fx),
        sp.Matrix(4, 4, lambda i, j: sp.diff(gfam[i, j], gam)).subs(fx))
    _require(
        w_bg[0] == 0 and w_bg[2] == 0 and w_bg[3] == 0
        and sp.simplify(w_bg[1] - 48 * alpha / (19 * r**2)) == 0,
        "control: static pair current mismatch",
    )
    stage("machinery_controls", t0)

    # ---- 2. general polar bilinear ----------------------------------------
    t0 = time.time()
    coords = [t, r, x, ph]
    g0 = sp.diag(-B_s, 1 / B_s, r**2 / (1 - x**2), r**2 * (1 - x**2))
    geo0 = geo_cls(coords, g0)
    lt = LinearizedTheta(geo0, alpha)
    P2 = (3 * x**2 - 1) / 2

    def polar_h(tag):
        H0, H1, H2, K = [sp.Function(n + tag)(t, r) for n in ("H0", "H1", "H2", "K")]
        h = sp.zeros(4, 4)
        h[0, 0] = B_s * H0 * P2
        h[0, 1] = h[1, 0] = H1 * P2
        h[1, 1] = H2 / B_s * P2
        h[2, 2] = g0[2, 2] * K * P2
        h[3, 3] = g0[3, 3] * K * P2
        return h, (H0, H1, H2, K)

    hA, fA = polar_h("a")
    hB, fB = polar_h("b")
    wab = lt.omega(hA, hB)
    _require(wab[3] == 0, "phi component of omega nonzero")
    Ft = _cancel(sp.integrate(sp.integrate(wab[0] * r**2, (x, -1, 1)), (ph, 0, 2 * sp.pi)))
    Fr = _cancel(sp.integrate(sp.integrate(wab[1] * r**2, (x, -1, 1)), (ph, 0, 2 * sp.pi)))
    _require(Ft != 0 and Fr != 0, "bilinear unexpectedly zero")
    out["Ft"] = Ft
    out["Fr"] = Fr
    stage("polar_bilinear", t0)

    # ---- 3. off-shell 4 alpha identity ------------------------------------
    t0 = time.time()
    D = sp.expand(sp.diff(Ft, t) + sp.diff(Fr, r))
    dBA = LinearizedBach(geo0).build(hA)
    dBB = LinearizedBach(geo0).build(hB)
    gi = geo0.ginv

    def contract(h, dB):
        s = sp.Integer(0)
        for b in range(4):
            for c in range(4):
                if h[b, c] == 0:
                    continue
                up = sum(gi[b, p] * gi[c, q] * dB[p, q] for p in range(4) for q in range(4))
                s += h[b, c] * up
        return s

    integrand = _cancel(contract(hB, dBA) - contract(hA, dBB)) * r**2
    Xi = sp.expand(sp.simplify(_cancel(
        sp.integrate(sp.integrate(integrand, (x, -1, 1)), (ph, 0, 2 * sp.pi)))))
    _require(sp.simplify(sp.expand(D - 4 * alpha * Xi)) == 0, "off-shell identity fails")
    stage("offshell_identity", t0)

    # ---- 4. Einstein-branch block -----------------------------------------
    t0 = time.time()
    cert = json.loads(BH2BE_CERT.read_text(encoding="utf-8"))
    locs = {"r": r, "omega": w, "m": m, "I": sp.I,
            "K": sp.Function("K"), "H1": sp.Function("H1")}
    Msys = sp.Matrix(2, 2, lambda i, j: sp.sympify(cert["reduction"]["M"][i][j], locals=locs))
    H0alg = sp.sympify(cert["reduction"]["H0_algebraic"], locals=locs)
    Kf, H1f = locs["K"](r), locs["H1"](r)
    h0K = _cancel(sp.expand(H0alg).coeff(Kf))
    h0H = _cancel(sp.expand(H0alg).coeff(H1f))
    _require(_cancel(H0alg - h0K * Kf - h0H * H1f) == 0, "H0 not linear in (K, H1)")

    KS = {tag: sp.Symbol("K" + tag) for tag in ("a", "b")}
    HS = {tag: sp.Symbol("H1" + tag) for tag in ("a", "b")}
    KEY = {("Ka", "Kb"): "KK", ("Ka", "H1b"): "KH", ("H1a", "Kb"): "HK",
           ("H1a", "H1b"): "HH"}

    def linforms(wv):
        Ms = sp.Matrix(2, 2, lambda i, j: _cancel(Msys[i, j].subs(w, wv)))
        base = {"K": (sp.Integer(1), sp.Integer(0)),
                "H1": (sp.Integer(0), sp.Integer(1)),
                "H0": (_cancel(h0K.subs(w, wv)), _cancel(h0H.subs(w, wv)))}
        res = {}
        for nm, v0 in base.items():
            v = [v0[0], v0[1]]
            for k in range(0, 4):
                res[(nm, k)] = (v[0], v[1])
                v = [_cancel(sp.diff(v[0], r) + Ms[0, 0] * v[0] + Ms[1, 0] * v[1]),
                     _cancel(sp.diff(v[1], r) + Ms[0, 1] * v[0] + Ms[1, 1] * v[1])]
        return res

    LF = {"a": linforms(w1), "b": linforms(w2)}
    funcs = {}
    for tag, tup in (("a", fA), ("b", fB)):
        for nm, f in zip(("H0", "H1", "H2", "K"), tup):
            funcs[nm + tag] = f
    submap = {}
    atoms = Fr.atoms(sp.Derivative) | {f for f in funcs.values() if Fr.has(f)}
    for at in atoms:
        if isinstance(at, sp.Derivative):
            f = at.args[0]
            jt = sum(int(p[1]) for p in at.args[1:] if p[0] == t)
            kr = sum(int(p[1]) for p in at.args[1:] if p[0] == r)
        else:
            f, jt, kr = at, 0, 0
        name = f.func.__name__
        tag = name[-1]
        nm = name[:-1]
        if nm == "H2":
            nm = "H0"
        wv = w1 if tag == "a" else w2
        cK, cH = LF[tag][(nm, kr)]
        submap[at] = (sp.I * wv) ** jt * (cK * KS[tag] + cH * HS[tag])
    Fr1 = Fr.subs(submap)
    C = {}
    for ua in (KS["a"], HS["a"]):
        for ub in (KS["b"], HS["b"]):
            C[KEY[(str(ua), str(ub))]] = _cancel(sp.diff(Fr1, ua, ub))
    # bilinearity residual check
    resid = Fr1 - sum(C[KEY[(str(ua), str(ub))]] * ua * ub
                      for ua in (KS["a"], HS["a"]) for ub in (KS["b"], HS["b"]))
    for v_ in (KS["a"], HS["a"], KS["b"], HS["b"]):
        resid = resid.subs(v_, 0)
    _require(_cancel(resid) == 0, "Einstein block not bilinear")
    # null theorem asserts
    for key, cc in C.items():
        _require(_cancel(cc.subs(w2, -w1)) == 0,
                 f"conjugate-pair flux nonzero in coefficient {key}")
    for key in ("KK", "HH"):
        _require(_cancel(C[key].subs(w2, w1)) == 0,
                 f"diagonal coefficient {key} nonzero at equal frequencies")
    # swap antisymmetry: C_{K H1}(w1, w2) = -C_{H1 K}(w2, w1)
    _require(_cancel(C["KH"]
                     + C["HK"].subs([(w1, w2), (w2, w1)], simultaneous=True)) == 0,
             "swap antisymmetry fails")
    out["einstein_block"] = {k: sp.sstr(sp.factor(v_)) for k, v_ in C.items()}
    stage("einstein_block", t0)

    # ---- 5. conformal-gauge control ---------------------------------------
    t0 = time.time()
    phi_f = sp.Function("phic")(t, r)
    h_conf = sp.Matrix(4, 4, lambda i, j: phi_f * P2 * g0[i, j])
    w_c = lt.omega(h_conf, hB)
    conf = {}
    for i, nm in [(0, "Ft"), (1, "Fr")]:
        val = _cancel(sp.integrate(sp.integrate(w_c[i] * r**2, (x, -1, 1)),
                                   (ph, 0, 2 * sp.pi)))
        conf[nm] = val
    _require(conf["Ft"] == 0 and conf["Fr"] == 0,
             "conformal direction pairs nontrivially off-shell: "
             f"Ft={sp.sstr(conf['Ft'])[:80]} Fr={sp.sstr(conf['Fr'])[:80]}")
    out["conformal_control"] = "EXACT_ZERO_OFF_SHELL"
    stage("conformal_control", t0)
    out["stage_seconds"]["total"] = round(time.time() - t0_all, 1)
    return out


def build_certificate() -> dict:
    res = run_flux_analysis(Geometry)
    certificate = {
        "schema": SCHEMA_NAME,
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": RESULT_ID,
        "result_token": RESULT_TOKEN,
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "declaration": {
            "theory": "pure-Weyl gravity L = alpha C_abcd C^abcd",
            "background_family": "Schwarzschild (symbolic m)",
            "conformal_frame": "working gauge; t-chart RW polar gauge, x = cos theta",
            "generator": "not used; bilinear flux statements only",
            "phase_space": "sphere-integrated Lee-Wald bilinear (F^t, F^r) between polar l=2 perturbations",
            "horizon_condition": "none imposed; algebraic flux identities",
            "infinity_condition": "none imposed",
            "frequency_domain": "symbolic omega_1, omega_2; conjugate pairs omega_2 = -omega_1",
            "lifecycle": "CLASSIFIED",
        },
        "bilinear": {
            "Ft": sp.sstr(res["Ft"]),
            "Fr": sp.sstr(res["Fr"]),
            "offshell_identity": "d_t F^t + d_r F^r = 4 alpha Int_S2 sqrt(g) [h_B . dB(h_A) - h_A . dB(h_B)] (verified exactly)",
        },
        "einstein_block": {
            "coefficients": res["einstein_block"],
            "structure": "F^r = C_KK Ka Kb + C_KH Ka H1b + C_HK H1a Kb + C_HH H1a H1b on shell of the certified 2-dim polar Einstein system; every coefficient carries (omega1 + omega2); diagonals carry (omega1^2 - omega2^2)",
            "null_theorem": "for conjugate pairs omega2 = -omega1 the polar Einstein-branch radial flux VANISHES IDENTICALLY: the polar Einstein branch is symplectically null (even-parity twin of the axial RW-null theorem)",
        },
        "conformal_control": {
            "statement": "the sphere-integrated symplectic pairing of the linearized conformal direction h = Phi g (Phi = phi(t,r) P2, arbitrary phi) with an ARBITRARY RW-gauge polar perturbation vanishes identically OFF-SHELL (F^t = F^r = 0 exactly)",
            "consequence": "the conformal gauge direction is an exact degeneracy of the sphere-integrated polar presymplectic form; polar flux statements need no conformal quotient at the bilinear level",
            "result": res["conformal_control"],
        },
        "claim_flags": {
            "machinery_controls_certified": True,
            "polar_bilinear_certified": True,
            "offshell_identity_certified": True,
            "einstein_block_null_certified": True,
            "conformal_degeneracy_certified": True,
            "extra_block_certified": False,
            "cross_block_certified": False,
            "flux_signs_certified": False,
            "outer_boundary_domain_certified": False,
            "causal_exclusion_decided": False,
            "growth_or_stability_certified": False,
            "general_l_certified": False,
        },
        "missing_objects": [
            "polar extra x extra and Einstein x extra flux blocks (needs the polar delta Ric[h] = psi composition)",
            "horizon flux signs on the polar extra family",
            "outer-boundary operator domains and falloff classification (polar)",
            "causal disposition of the polar sector",
            "general l; omega = 0; growth/stability data",
        ],
        "stage_seconds": res["stage_seconds"],
        "provenance": {
            "generator_path": "black_hole_programme/bh2b_polar_flux.py",
            "engine_path": "black_hole_programme/weyl_geometry.py",
            "engine_sha256": _sha256(HERE / "weyl_geometry.py"),
            "theta_path": "black_hole_programme/linearized_theta.py",
            "theta_sha256": _sha256(HERE / "linearized_theta.py"),
            "bach_path": "black_hole_programme/linearized_bach.py",
            "bach_sha256": _sha256(HERE / "linearized_bach.py"),
            "bh1b_certificate": str(BH1B_CERT.relative_to(ROOT)),
            "bh1b_certificate_sha256": _sha256(BH1B_CERT),
            "bh2b_einstein_certificate": str(BH2BE_CERT.relative_to(ROOT)),
            "bh2b_einstein_certificate_sha256": _sha256(BH2BE_CERT),
        },
        "verification_command": "python3 black_hole_programme/verify_bh2b_polar_flux.py",
    }
    return certificate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    certificate = build_certificate()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
