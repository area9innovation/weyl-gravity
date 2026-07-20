"""Polar metric-side indicial structure and the mu = 0 shearing obstruction.

Verdict token: BH2C_POLAR_METRIC_INDICIAL_MU0_REQUIRES_SHEARING
Tags: LOCAL-ALGEBRAIC + REDUCED-MODE.  Lifecycle: CLASSIFIED.

Second split of the asymptotic-Jordan work item, and the metric-side
counterpart of BH2C_SYMBOLIC_INDICIAL (which covered the carrier).  It
records one established result, one exact obstruction, and the evidence
that separates them.

ESTABLISHED
-----------
The 4-dim polar h-system at infinity has leading matrix characteristic
polynomial  lam^3 (lam + 2 I omega)  at SYMBOLIC omega, which reduces to
the certified fixture value lam^3 (5 lam + 6 I)/5 at omega = 3/5.

Sector mu = -2 I omega is semisimple (algebraic = geometric = 1) and its
Frobenius exponent is sigma0 = -4 I omega + 1, EXACTLY the value the
certified BH2C_POLAR_FLUX_CLASS producer feeds to column_jets for the
homogeneous h-jets in that sector.

OBSTRUCTION
-----------
Sector mu = 0 has algebraic multiplicity 3 but geometric multiplicity 1:
the kernel staircase dim ker(A0)^k = [1, 2, 3] gives a SINGLE JORDAN
CHAIN OF LENGTH 3.  When the leading matrix is non-semisimple at an
eigenvalue, the Frobenius exponents are NOT the eigenvalues of A1
projected onto the generalized eigenspace -- that reduction presupposes
diagonalizability.  The singularity is irregular in that sector and a
Moser/Turrittin shearing transformation is required, with ramified
exponents admissible a priori.

The obstruction is self-diagnosing, and this is the decisive evidence:

  sector mu = -2 I omega (semisimple): naive extraction gives
      -4 I omega + 1  ==  certified producer sigma0     -> POSITIVE CONTROL
  sector mu = 0 (Jordan chain 3):      naive extraction gives
      {-3, 0, 0}      !=  certified producer sigma0 = 1 -> NEGATIVE CONTROL

The same procedure reproduces certified data exactly where it is valid
and fails to reproduce it exactly where the Jordan block makes it
invalid.  The mu = 0 metric exponents are therefore NOT established here
and the values {-3, 0, 0} are recorded as a REFUTED artifact of the
inapplicable method, never as a result.

EXPLICITLY NOT CLAIMED
----------------------
The Jordan chain does NOT explain the composed-metric log tails reported
by BH2C_FLUX_CLASS.  The exponent matrix on the generalized eigenspace is
itself semisimple (log-factor count 0 for every exponent), consistent
with BH2C_ASYMPTOTIC_JORDAN's log-free verdict for the homogeneous formal
systems; the log tails arise in the SOURCED composition, not in this
homogeneous indicial data.  Any narrative linking the two is unsupported.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import sympy as sp

import bh2b_polar_reach as reach
from weyl_geometry import Geometry

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SCHEMA_NAME = "pure-weyl-bh2c-polar-metric-indicial-v1"
SCHEMA_PATH = HERE / "schema" / "bh2c-polar-metric-indicial-v1.schema.json"
CERT_PATH = HERE / "certificates" / "BH2C_POLAR_METRIC_INDICIAL.json"
RESULT_ID = "PURE_WEYL_BH2C_POLAR_METRIC_INDICIAL"
RESULT_TOKEN = "BH2C_POLAR_METRIC_INDICIAL_MU0_REQUIRES_SHEARING"
FLUXCLASS_CERT = HERE / "certificates" / "BH2C_POLAR_FLUX_CLASS.json"
INDICIAL_CERT = HERE / "certificates" / "BH2C_SYMBOLIC_INDICIAL.json"

N = 4
_cancel = lambda e: sp.cancel(sp.together(e))
lam = sp.Symbol("lam")

# sigma0 values the certified polar producer feeds to column_jets
CERTIFIED_SIGMA0 = {"mu0": sp.Integer(1), "mu2w_offset": sp.Integer(1)}


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_h_system(geo_cls):
    """4-dim polar h-system leading/subleading matrices at symbolic omega."""
    R = reach.run_analysis(geo_cls, light=True)
    v = R["syms"]["v"]
    r = R["syms"]["r"]
    w = R["syms"]["omega"]
    x = R["syms"]["x"]
    coords = [v, r, x, sp.Symbol("phi")]
    B0 = 1 - 2 / r
    g0 = sp.zeros(4, 4)
    g0[0, 0] = -B0
    g0[0, 1] = g0[1, 0] = 1
    g0[2, 2] = r**2 / (1 - x**2)
    g0[3, 3] = r**2 * (1 - x**2)
    geo0 = geo_cls(coords, g0)
    gi, G = geo0.ginv, geo0.Gamma
    P2 = (3 * x**2 - 1) / 2
    dP2 = sp.diff(P2, x)
    Wxx = sp.Rational(3, 2)
    E = sp.exp(sp.I * w * v)
    Ah, Bh, Ch, Kh = [sp.Function(n)(r) for n in ("Ah", "Bh", "Ch", "Kh")]
    hp = sp.zeros(4, 4)
    hp[0, 0] = Ah * P2 * E
    hp[0, 1] = hp[1, 0] = Bh * P2 * E
    hp[1, 1] = Ch * P2 * E
    hp[2, 2] = g0[2, 2] * Kh * P2 * E
    hp[3, 3] = g0[3, 3] * Kh * P2 * E

    dG = [[[sp.Integer(0)] * N for _ in range(N)] for _ in range(N)]
    for a in range(N):
        for b in range(N):
            for c in range(b, N):
                s = sum(gi[a, d] * (geo0.covd2(hp, b, d, c)
                                    + geo0.covd2(hp, c, b, d)
                                    - geo0.covd2(hp, d, b, c))
                        for d in range(N) if gi[a, d] != 0)
                val = _cancel(s / 2)
                dG[a][b][c] = val
                dG[a][c][b] = val

    def cov_dG(e, a, b, c):
        s = sp.diff(dG[a][b][c], coords[e])
        for hh in range(N):
            s += G[a][e][hh] * dG[hh][b][c]
            s -= G[hh][e][b] * dG[a][hh][c] + G[hh][e][c] * dG[a][b][hh]
        return s

    dRic = {}
    for (b, d) in ((0, 2), (1, 2), (1, 1), (2, 2)):
        dRic[(b, d)] = _cancel(sum(cov_dG(a, a, b, d) - cov_dG(d, a, b, a)
                                   for a in range(N)))
    x0, x1 = sp.Integer(0), sp.Rational(1, 2)

    def strip(raw, ang, xa, xb):
        e0_ = _cancel(raw.subs(x, xa).doit() / E) / ang.subs(x, xa)
        chk = _cancel(raw.subs(x, xb).doit() / E - e0_ * ang.subs(x, xb))
        _require(chk == 0, "strip inconsistent")
        return _cancel(e0_)

    hrow = {"vx": strip(dRic[(0, 2)], dP2, x1, sp.Rational(1, 3)),
            "rx": strip(dRic[(1, 2)], dP2, x1, sp.Rational(1, 3)),
            "rr": strip(dRic[(1, 1)], P2, x0, x1)}
    raw = dRic[(2, 2)] / E
    Msv = sp.Matrix([[g0[2, 2].subs(x, x0) * P2.subs(x, x0), Wxx],
                     [g0[2, 2].subs(x, x1) * P2.subs(x, x1), Wxx]])
    solv = Msv.solve(sp.Matrix([_cancel(raw.subs(x, x0).doit()),
                                _cancel(raw.subs(x, x1).doit())]))
    hrow["angW"] = _cancel(solv[1])

    d1 = lambda fn: sp.Derivative(fn, r)
    Bc_sol = sp.solve(sp.Eq(hrow["angW"], 0), Bh)
    _require(len(Bc_sol) == 1, "Bc not solvable")
    Bc_e = _cancel(Bc_sol[0])
    subB = {sp.Derivative(Bh, (r, 2)): sp.diff(Bc_e, r, 2).doit(),
            sp.Derivative(Bh, r): sp.diff(Bc_e, r).doit(), Bh: Bc_e}
    R2 = {nm: _cancel(hrow[nm].subs(subB).doit())
          for nm in ("vx", "rx", "rr")}
    Ap = _cancel(sp.solve(sp.Eq(R2["vx"], 0), d1(Ah))[0])
    Kp = _cancel(sp.solve(sp.Eq(R2["rx"], 0), d1(Kh))[0])
    rr1 = R2["rr"].subs({sp.Derivative(Kh, (r, 2)): sp.diff(Kp, r).doit(),
                         d1(Kh): Kp}).doit()
    rr1 = _cancel(rr1.subs(d1(Ah), Ap).doit())
    C2 = _cancel(sp.solve(sp.Eq(rr1, 0), sp.Derivative(Ch, (r, 2)))[0])
    state = [Ah, Ch, d1(Ch), Kh]
    Mh = sp.zeros(4, 4)
    Mh[1, 2] = 1
    for i, expr in ((0, Ap), (2, C2), (3, Kp)):
        e = sp.expand(expr)
        for j, st in enumerate(state):
            Mh[i, j] = _cancel(e.coeff(st))

    u = sp.Symbol("u", positive=True)

    def ser(e, kmax=1):
        if e == 0:
            return {}
        num, den = sp.fraction(_cancel(e))
        ratio = sp.cancel(sp.expand(num.subs(r, 1 / u))
                          / sp.expand(den.subs(r, 1 / u)))
        s = sp.series(ratio, u, 0, kmax + 1).removeO()
        pol = sp.Poly(sp.expand(s), u)
        return {mo[0]: pol.coeff_monomial(u**mo[0]) for mo in pol.monoms()
                if mo[0] <= kmax}

    A0 = sp.zeros(4, 4)
    A1 = sp.zeros(4, 4)
    for i in range(4):
        for j in range(4):
            s = ser(Mh[i, j], 1)
            A0[i, j] = _cancel(s.get(0, sp.Integer(0)))
            A1[i, j] = _cancel(s.get(1, sp.Integer(0)))
    return A0, A1, w


def run_analysis(geo_cls) -> dict:
    t0 = time.time()
    A0, A1, w = build_h_system(geo_cls)
    cp0 = sp.factor(sp.expand(A0.charpoly(lam).as_expr()))
    _require(sp.simplify(cp0 - lam**3 * (lam + 2 * sp.I * w)) == 0,
             f"polar h-system charpoly unexpected: {cp0}")
    # fixture cross-check against the certified producer's recorded value
    fix = sp.factor(sp.expand(cp0.subs(w, sp.Rational(3, 5))))
    _require(sp.simplify(fix - lam**3 * (5 * lam + 6 * sp.I) / 5) == 0,
             f"fixture charpoly {fix} != certified lam^3(5 lam + 6 I)/5")

    rts = sp.roots(sp.Poly(A0.charpoly(lam).as_expr(), lam))
    sectors = {}
    for mu, alg in rts.items():
        Amu = (A0 - mu * sp.eye(4)).applyfunc(sp.cancel)
        stair, P = [], sp.eye(4)
        for _ in range(alg):
            P = (P * Amu).applyfunc(sp.cancel)
            stair.append(len(P.nullspace()))
        incr = [stair[0]] + [stair[k] - stair[k - 1]
                             for k in range(1, len(stair))]
        chains = []
        for k in range(len(incr), 0, -1):
            n_k = incr[k - 1] - (incr[k] if k < len(incr) else 0)
            chains += [k] * n_k
        chains.sort(reverse=True)
        gen = P.nullspace()
        _require(len(gen) == alg, "generalized eigenspace dimension mismatch")
        rest = []
        for mu2, alg2 in rts.items():
            if mu2 == mu:
                continue
            Q = sp.eye(4)
            for _ in range(alg2):
                Q = (Q * (A0 - mu2 * sp.eye(4))).applyfunc(sp.cancel)
            rest += Q.nullspace()
        M = sp.Matrix.hstack(*(gen + rest))
        _require(sp.cancel(M.det()) != 0, "generalized basis degenerate")
        Ared = (M.inv() * A1 * M)[:alg, :alg].applyfunc(sp.cancel)
        rr = sp.roots(sp.Poly(Ared.charpoly(lam).as_expr(), lam))
        exps = {sp.sstr(sp.cancel(k)): int(v) for k, v in rr.items()}
        logf = {}
        for k, v in rr.items():
            gm = len((Ared - k * sp.eye(alg)).nullspace())
            logf[sp.sstr(sp.cancel(k))] = int(v) - gm
        sectors[sp.sstr(mu)] = {
            "algebraic": alg,
            "geometric": stair[0],
            "kernel_staircase": stair,
            "chain_lengths": chains,
            "semisimple": max(chains) == 1,
            "naive_exponents": exps,
            "exponent_log_factors": logf,
        }

    semis = sectors[sp.sstr(-2 * sp.I * w)]
    jord = sectors["0"]
    _require(semis["semisimple"], "mu = -2I omega unexpectedly non-semisimple")
    _require(not jord["semisimple"], "mu = 0 unexpectedly semisimple")
    _require(jord["kernel_staircase"] == [1, 2, 3],
             f"unexpected staircase {jord['kernel_staircase']}")
    _require(jord["chain_lengths"] == [3],
             f"unexpected chain lengths {jord['chain_lengths']}")

    # POSITIVE CONTROL: the semisimple sector reproduces certified sigma0
    got = [sp.sympify(k, locals={"omega": w, "I": sp.I})
           for k in semis["naive_exponents"]]
    _require(len(got) == 1, "semisimple sector exponent count")
    expected = -4 * sp.I * w + CERTIFIED_SIGMA0["mu2w_offset"]
    _require(sp.simplify(got[0] - expected) == 0,
             f"positive control FAILED: {got[0]} != {expected}")

    # NEGATIVE CONTROL: the Jordan sector does NOT reproduce certified sigma0
    got0 = {sp.sympify(k) for k in jord["naive_exponents"]}
    _require(not any(sp.simplify(g - CERTIFIED_SIGMA0["mu0"]) == 0
                     for g in got0),
             "negative control FAILED: naive extraction unexpectedly "
             "reproduced the certified sigma0 in the Jordan sector")

    # log-factor count is zero everywhere: consistent with the certified
    # log-free verdict; the Jordan chain does NOT produce log(r) here
    for sec in sectors.values():
        _require(all(v == 0 for v in sec["exponent_log_factors"].values()),
                 "unexpected nonzero log-factor count")

    return {
        "charpoly": sp.sstr(cp0),
        "fixture_charpoly_omega_3_5": sp.sstr(fix),
        "sectors": sectors,
        "positive_control": {
            "sector": sp.sstr(-2 * sp.I * w),
            "extracted": sp.sstr(got[0]),
            "certified_sigma0": sp.sstr(expected),
            "match": True,
        },
        "negative_control": {
            "sector": "0",
            "extracted": sorted(jord["naive_exponents"]),
            "certified_sigma0": sp.sstr(CERTIFIED_SIGMA0["mu0"]),
            "match": False,
            "reading": "the naive projection is INVALID in a Jordan sector; "
                       "the extracted values are a REFUTED artifact, not a "
                       "result",
        },
        "stage_seconds": {"total": round(time.time() - t0, 1)},
    }


def build_certificate() -> dict:
    res = run_analysis(Geometry)
    return {
        "schema": SCHEMA_NAME,
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": RESULT_ID,
        "result_token": RESULT_TOKEN,
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "declaration": {
            "theory": "S = alpha * integral sqrt(-g) C_{abcd} C^{abcd}",
            "background_family": "Schwarzschild exterior, m = 1",
            "conformal_frame": "fixed representative g (certified atlas)",
            "generator": "polar l = 2 metric (h-system) at infinity",
            "phase_space": "not constructed here (indicial layer only)",
            "horizon_condition": "not used (infinity endpoint)",
            "infinity_condition": "leading matrix analysis after the "
                                  "oscillatory split",
            "lifecycle": "CLASSIFIED",
        },
        "companion": {
            "certificate": str(INDICIAL_CERT.relative_to(ROOT)),
            "certificate_sha256": _sha256(INDICIAL_CERT),
            "relation": "metric-side counterpart of the carrier-side "
                        "symbolic indicial certificate; supersedes nothing",
        },
        "established": {
            "charpoly": res["charpoly"],
            "fixture_charpoly_omega_3_5": res["fixture_charpoly_omega_3_5"],
            "semisimple_sector": res["positive_control"],
        },
        "obstruction": {
            "sector": "0",
            "algebraic_multiplicity": res["sectors"]["0"]["algebraic"],
            "geometric_multiplicity": res["sectors"]["0"]["geometric"],
            "kernel_staircase": res["sectors"]["0"]["kernel_staircase"],
            "jordan_chain_lengths": res["sectors"]["0"]["chain_lengths"],
            "statement": "the leading matrix is non-semisimple at mu = 0, so "
                         "Frobenius exponents are NOT the eigenvalues of A1 "
                         "projected onto the generalized eigenspace; a "
                         "Moser/Turrittin shearing is required and ramified "
                         "exponents are admissible a priori",
            "evidence": res["negative_control"],
            "required_technique": "Moser/Turrittin shearing transformation",
        },
        "sectors": res["sectors"],
        "not_claimed": {
            "jordan_chain_explains_log_tails": False,
            "detail": "the exponent matrix is semisimple in every sector "
                      "(log-factor count 0), consistent with "
                      "BH2C_ASYMPTOTIC_JORDAN's log-free verdict; the "
                      "composed-metric log tails of BH2C_FLUX_CLASS arise in "
                      "the SOURCED composition, not in this homogeneous "
                      "indicial data",
            "mu0_metric_exponents_established": False,
        },
        "verification_discipline": [
            "Jordan structure from the kernel dimension staircase "
            "dim ker(A0 - mu)^k, never inferred from the characteristic "
            "polynomial (the work item forbids that inference)",
            "the extraction method is validated by a POSITIVE control (it "
            "reproduces certified sigma0 in the semisimple sector) and "
            "falsified by a NEGATIVE control (it fails to in the Jordan "
            "sector)",
            "refuted values are recorded as refuted, never as results",
            "no floating point; no nsimplify",
        ],
        "claim_flags": {
            "leading_charpoly_symbolic_certified": True,
            "semisimple_sector_exponent_certified": True,
            "jordan_structure_certified": True,
            "mu0_exponents_certified": False,
            "shearing_analysis_performed": False,
            "log_tail_mechanism_certified": False,
            "general_l_certified": False,
        },
        "missing_objects": [
            "Moser/Turrittin shearing analysis of the mu = 0 metric sector",
            "mu = 0 metric Frobenius exponents (possibly ramified)",
            "all-orders metric reconstruction maps",
            "symbolic-frequency finite-flux power table",
            "the assembled endpoint-nonselection theorem",
        ],
        "stage_seconds": res["stage_seconds"],
        "provenance": {
            "generator_path":
                "black_hole_programme/bh2c_polar_metric_indicial.py",
            "reach_path": "black_hole_programme/bh2b_polar_reach.py",
            "reach_sha256": _sha256(HERE / "bh2b_polar_reach.py"),
            "certified_sigma0_source": str(FLUXCLASS_CERT.relative_to(ROOT)),
            "certified_sigma0_source_sha256": _sha256(FLUXCLASS_CERT),
        },
        "verification_command":
            "python3 black_hole_programme/verify_bh2c_polar_metric_indicial.py",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(CERT_PATH))
    args = parser.parse_args()
    Path(args.out).write_text(
        json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
