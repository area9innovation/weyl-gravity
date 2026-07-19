"""BH-2A stage 5: causal disposition — the extra branch is unavoidable.

Fail-closed builder for
`black_hole_programme/certificates/BH2A_CAUSAL_DISPOSITION.json`.

Verdict: BH2A_AXIAL_CAUSAL_DISPOSITION_EXTRA_BRANCH_UNAVOIDABLE.

Exact computation (Schwarzschild m = 1, axial l = 2, carrier system of the
certified extra branch, symbolic real omega): the asymptotic analysis at
r -> infinity with ansatz (P, Q) ~ e^{i lam r} r^sigma (v0 + ...):

1. leading dispersion (lam^2 - omega^2)^2 = 0: the extra branch propagates
   on exactly the Einstein characteristics (massless/luminal), with
   two-dimensional amplitude spaces at lam = +/- omega;
2. degenerate next-order solvability: sigma in {+-2 i m omega,
   +-2 i m omega - 1}: pure Coulomb log-phases (r^{2 i omega} combines
   with e^{i omega r} into e^{i omega r_*}) with amplitude growths r^0 and
   r^{-1}: NO growing asymptotic solutions at real frequencies;
3. RW-master control: the same analysis on the Einstein master equation
   gives the same characteristic structure (simple roots), confirming the
   branches are asymptotically indistinguishable by falloff.

Disposition (combining certified facts): the extra branch (i) reaches the
future horizon with a two-parameter ingoing-regular family
(BH2A_HORIZON_REACH), (ii) carries nonzero horizon flux
(BH2A_CROSS_FLUX), and (iii) has bounded oscillatory asymptotics on the
Einstein characteristics at infinity (this certificate).  Therefore, at
the axial l = 2 linear mode level, no causal decay or regularity
prescription at the horizon or at infinity excludes the extra branch;
exclusion could only be imposed as a branch projection on scattering
data, which constrains both temporal ends and is not a causal
initial-boundary condition.  This realizes the decision-tree alternative
"removing the extra branch requires a future boundary condition" at the
mode level: pure-Weyl black-hole exteriors cannot be causally truncated
to the Einstein sector, and their radiation lives in the mixed/extra
sectors.

NOT claimed: complex-frequency (quasinormal/instability) structure,
general l or m, polar sector, nonlinear or all-orders statements, a full
initial-boundary well-posedness theorem, stability, or ringdown.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import sympy as sp

import weyl_geometry as wg

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "certificates" / "BH2A_CAUSAL_DISPOSITION.json"
SCHEMA_PATH = HERE / "schema" / "bh2a-causal-disposition-v1.schema.json"
REACH_CERT = HERE / "certificates" / "BH2A_HORIZON_REACH.json"
CROSS_CERT = HERE / "certificates" / "BH2A_CROSS_FLUX.json"

SCHEMA_NAME = "pure-weyl-bh2a-causal-disposition-v1"
RESULT_ID = "PURE_WEYL_BH2A_CAUSAL_DISPOSITION"
RESULT_TOKEN = "BH2A_AXIAL_CAUSAL_DISPOSITION_EXTRA_BRANCH_UNAVOIDABLE"


class DispositionError(RuntimeError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise DispositionError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_certificate() -> dict:
    t0_all = time.time()
    t_ch, ph = sp.symbols("t phi")
    r = sp.Symbol("r", positive=True)
    x = sp.Symbol("x")
    w = sp.Symbol("omega", positive=True)
    m = sp.Integer(1)
    B0 = 1 - 2 * m / r
    coords = [t_ch, r, x, ph]
    g0 = sp.diag(-B0, 1 / B0, r**2 / (1 - x**2), r**2 * (1 - x**2))
    geo0 = wg.Geometry(coords, g0)
    gi = geo0.ginv
    S = -3 * x * (1 - x**2)
    N = 4
    cancel = lambda e: sp.cancel(sp.together(e))  # noqa: E731
    receipts = {}

    # carrier rows (t-chart)
    t0 = time.time()
    p_c = sp.Function("p")(t_ch, r)
    q_c = sp.Function("q")(t_ch, r)
    c_c = sp.Function("c")(t_ch, r)
    psi_t = sp.zeros(4, 4)
    psi_t[0, 3] = psi_t[3, 0] = p_c * S
    psi_t[1, 3] = psi_t[3, 1] = q_c * S
    psi_t[2, 3] = psi_t[3, 2] = c_c * 3 * (x**2 - 1)
    sdiv = sum(gi[a, e] * geo0.covd2(psi_t, e, a, 3)
               for a in range(N) for e in range(N) if gi[a, e] != 0)
    c_expr = sp.solve(sp.Eq(cancel(sdiv), 0), c_c)[0]
    psi2 = sp.Matrix(N, N, lambda i, j: cancel(psi_t.subs(c_c, c_expr).doit()[i, j]))
    G = geo0.Gamma
    DX = [[[cancel(geo0.covd2(psi2, e, a, b)) for b in range(N)] for a in range(N)]
          for e in range(N)]

    def covd2X2(e, f, a, b):
        s = sp.diff(DX[f][a][b], coords[e])
        for hh in range(N):
            s -= (G[hh][e][f] * DX[hh][a][b] + G[hh][e][a] * DX[f][hh][b]
                  + G[hh][e][b] * DX[f][a][hh])
        return s

    def Lrow(a, b):
        box = sum(gi[e, f] * covd2X2(e, f, a, b)
                  for e in range(N) for f in range(N) if gi[e, f] != 0)
        cx = sum(geo0.Weyl[a][cc][b][d]
                 * sum(gi[cc, e] * gi[d, f] * psi2[e, f] for e in range(N) for f in range(N))
                 for cc in range(N) for d in range(N))
        return cancel(box / 2 + cx)

    Lt = cancel(Lrow(0, 3) / S)
    Lr = cancel(Lrow(1, 3) / S)
    P = sp.Function("P")(r)
    Q = sp.Function("Q")(r)
    E = sp.exp(sp.I * w * t_ch)
    four = {p_c: P * E, q_c: Q * E}
    Ltf = sp.expand(cancel(Lt.subs(four).doit() / E))
    Lrf = sp.expand(cancel(Lr.subs(four).doit() / E))
    receipts["carrier_rows"] = round(time.time() - t0, 1)

    # asymptotic analysis
    t0 = time.time()
    lam, sig = sp.symbols("lambda_ sigma")
    a0, b0 = sp.symbols("a0 b0")
    ans = {P: a0 * sp.exp(sp.I * lam * r) * r**sig,
           Q: b0 * sp.exp(sp.I * lam * r) * r**sig}

    def leading(row):
        e = row
        for func, val in ans.items():
            e = e.subs({sp.Derivative(func, (r, 2)): sp.diff(val, r, 2),
                        sp.Derivative(func, r): sp.diff(val, r),
                        func: val})
        e = sp.expand(e.doit() / (sp.exp(sp.I * lam * r) * r**sig))
        num, _den = sp.fraction(sp.together(sp.expand(cancel(sp.together(e)))))
        return sp.Poly(sp.expand(num), r)

    pol1 = leading(Ltf)
    pol2 = leading(Lrf)
    d1 = max(mon[0] for mon in pol1.monoms())
    d2 = max(mon[0] for mon in pol2.monoms())
    top1 = sp.expand(pol1.coeff_monomial(r**d1))
    top2 = sp.expand(pol2.coeff_monomial(r**d2))
    M0 = sp.Matrix([[top1.coeff(a0), top1.coeff(b0)],
                    [top2.coeff(a0), top2.coeff(b0)]])
    disp = sp.factor(M0.det())
    _require(sp.simplify(disp / ((lam - w) ** 2 * (lam + w) ** 2)).is_constant(),
             f"dispersion not (lam^2-omega^2)^2: {disp}")
    sig_results = {}
    for lv, expect in [(w, {2 * sp.I * w, 2 * sp.I * w - 1}),
                       (-w, {-2 * sp.I * w, -2 * sp.I * w - 1})]:
        M0l = M0.subs(lam, lv)
        ns = M0l.nullspace()
        _require(len(ns) == 2, "leading nullspace not 2-dimensional")
        nxt1 = sp.expand(pol1.coeff_monomial(r**(d1 - 1))).subs(lam, lv)
        nxt2 = sp.expand(pol2.coeff_monomial(r**(d2 - 1))).subs(lam, lv)
        N1 = sp.Matrix([[nxt1.coeff(a0), nxt1.coeff(b0)],
                        [nxt2.coeff(a0), nxt2.coeff(b0)]])
        lnsl = M0l.T.nullspace()
        proj = sp.Matrix(2, 2, lambda i, j: sp.expand((lnsl[i].T * N1 * ns[j])[0, 0]))
        sigs = set(sp.solve(sp.Eq(sp.factor(sp.expand(proj.det())), 0), sig))
        _require(
            all(any(sp.simplify(sv - ev) == 0 for ev in expect) for sv in sigs)
            and len(sigs) == 2,
            f"unexpected sigma set at lam={lv}: {sigs}",
        )
        sig_results[str(lv)] = [sp.sstr(sv) for sv in sorted(sigs, key=sp.default_sort_key)]
    receipts["asymptotics"] = round(time.time() - t0, 1)

    # RW-master control: same characteristics, no growing behaviour
    t0 = time.time()
    F = sp.Function("F")(r)
    V = B0 * (6 / r**2 - 6 * m / r**3)
    opF = sp.expand(B0 * sp.diff(B0 * sp.diff(F, r), r) + (w**2 - V) * F)
    e = opF.subs({sp.Derivative(F, (r, 2)): sp.diff(a0 * sp.exp(sp.I * lam * r) * r**sig, r, 2),
                  sp.Derivative(F, r): sp.diff(a0 * sp.exp(sp.I * lam * r) * r**sig, r),
                  F: a0 * sp.exp(sp.I * lam * r) * r**sig}).doit()
    e = sp.expand(e / (sp.exp(sp.I * lam * r) * r**sig))
    num, _ = sp.fraction(sp.together(sp.expand(cancel(sp.together(e)))))
    polF = sp.Poly(sp.expand(num), r)
    dF_ = max(mon[0] for mon in polF.monoms())
    dispF = sp.factor(sp.expand(polF.coeff_monomial(r**dF_)).coeff(a0))
    _require(sp.simplify(dispF / (lam**2 - w**2)).is_constant(),
             f"RW dispersion unexpected: {dispF}")
    for lv, expect in [(w, 2 * sp.I * w), (-w, -2 * sp.I * w)]:
        nx = sp.expand(polF.coeff_monomial(r**(dF_ - 1))).coeff(a0).subs(lam, lv)
        sv = sp.solve(sp.Eq(nx, 0), sig)
        _require(len(sv) == 1 and sp.simplify(sv[0] - expect) == 0,
                 f"RW sigma unexpected at lam={lv}: {sv}")
    receipts["rw_control"] = round(time.time() - t0, 1)
    receipts["total"] = round(time.time() - t0_all, 1)

    certificate = {
        "schema": SCHEMA_NAME,
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": RESULT_ID,
        "result_token": RESULT_TOKEN,
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "declaration": {
            "theory": "pure-Weyl gravity L = alpha C_abcd C^abcd",
            "background_family": "Schwarzschild, m = 1 fixture; omega symbolic real",
            "conformal_frame": "working gauge; t-chart",
            "generator": "none; asymptotic mode classification",
            "phase_space": "axial l = 2 linear modes",
            "horizon_condition": "imported: certified two-parameter ingoing-regular extra family",
            "infinity_condition": "formal asymptotic classification at r -> infinity (leading two orders)",
            "lifecycle": "CLASSIFIED",
        },
        "asymptotics": {
            "dispersion": "(lambda^2 - omega^2)^2: extra branch propagates on the Einstein characteristics (massless/luminal), amplitude spaces 2-dimensional at each sign",
            "sigma": sig_results,
            "interpretation": "sigma = +-2 i m omega are Coulomb log-phases (r^{2 i omega} e^{i omega r} = e^{i omega r_*}); amplitude growths r^0 and r^{-1}: no growing asymptotic solutions at real frequencies",
            "rw_control": "the Einstein master equation has the same characteristics and log-phases (simple roots): the branches are asymptotically indistinguishable by falloff",
        },
        "disposition": {
            "statement": "at the axial l = 2 linear mode level, the extra branch reaches the horizon (ingoing-regular), carries nonzero flux, and is bounded oscillatory radiation on the Einstein characteristics at infinity; none of the TESTED endpoint diagnostics (future-horizon analyticity, leading outer symbol and falloff class) excludes it. This is an endpoint-admissibility statement, not a classification of all local differential boundary operators: zero Cauchy data for the carrier is a local linear Einstein-sector restriction whose naturalness remains open",
            "consequence": "within the tested endpoint prescriptions, exclusion could only be a branch projection on scattering data, constraining both temporal ends: not a causal initial-boundary condition. Pure-Weyl exteriors cannot be truncated to the Einstein sector by the TESTED endpoint conditions, and at the mode level their radiation lives in the mixed/extra sectors",
            "decision_tree": "realizes 'removing the extra branch requires a future boundary condition' at the mode level",
        },
        "claim_flags": {
            "dispersion_certified": True,
            "no_growing_asymptotics_certified": True,
            "rw_control_certified": True,
            "extra_branch_unavoidable_mode_level_certified": True,
            "complex_frequency_structure_certified": False,
            "general_l_or_m_certified": False,
            "polar_sector_certified": False,
            "initial_boundary_wellposedness_certified": False,
            "nonlinear_or_all_orders_certified": False,
            "stability_or_ringdown_certified": False,
        },
        "missing_objects": [
            "complex-frequency (quasinormal/instability) mode structure",
            "general l, general m, polar sector",
            "a full initial-boundary well-posedness theorem for the fourth-order exterior problem",
            "nonlinear and all-orders statements",
            "stability and ringdown (BH-3 vocabulary stays locked)",
        ],
        "stage_seconds": receipts,
        "provenance": {
            "generator_path": "black_hole_programme/bh2a_causal_disposition.py",
            "engine_path": "black_hole_programme/weyl_geometry.py",
            "engine_sha256": _sha256(HERE / "weyl_geometry.py"),
            "reach_certificate": str(REACH_CERT.relative_to(ROOT)),
            "reach_certificate_sha256": _sha256(REACH_CERT),
            "cross_certificate": str(CROSS_CERT.relative_to(ROOT)),
            "cross_certificate_sha256": _sha256(CROSS_CERT),
        },
        "verification_command": "python3 black_hole_programme/verify_bh2a_causal_disposition.py",
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
