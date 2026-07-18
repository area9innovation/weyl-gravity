"""BH-2A stage 2: the extra branch reaches the horizon (linear mode level).

Fail-closed builder for
`black_hole_programme/certificates/BH2A_HORIZON_REACH.json`.

Verdict: BH2A_EXTRA_BRANCH_REACHES_HORIZON_LINEAR_MODE_LEVEL.

Setting: ingoing Eddington--Finkelstein chart (v, r, x = cos theta, phi)
on Schwarzschild; axial l=2 extra-branch carrier psi_ab (trace-free,
divergence-free, components psi_vphi = p S, psi_rphi = q S, psi_xphi from
the divergence constraint) satisfying the certified extra-branch equation
(1/2) Box psi + C psi = 0 (BH-2A stage 1).

Exact results:

1. the divergence constraint solves for the third component with a
   POLYNOMIAL solution -- regular at the horizon (the 1/(r-2m) factor of
   the Schwarzschild-chart solution is a chart artifact);
2. on Fourier modes e^{i omega v} the radial system is first-order
   regularizable with a REGULAR singular point at r = 2m: rho^2 A -> 0
   componentwise for rho = r - 2m;
3. the residue matrix has eigenvalues {0 (x2), -4 i m omega,
   -2 - 4 i m omega} and the zero eigenvalue has geometric multiplicity 2:
   at every frequency there is a TWO-parameter family of extra-branch
   solutions analytic (ingoing-regular) at the future horizon, with no
   leading logarithm;
4. benchmark: the Einstein/Regge--Wheeler master equation in the same
   chart also admits an ingoing-regular family (residue spectrum
   {0, -1 - 4 i m omega}; scalar exponents {0, -4 i m omega}), so horizon
   regularity does NOT distinguish the extra branch from the Einstein
   branch.

Consequence (exact, scoped): excluding the extra fourth-order branch can
never be a future-horizon regularity condition; any exclusion must come
from outer-boundary conditions, causal structure, or flux/sign data.

NOT claimed: flux matrix, Lee--Wald signs, outer-boundary domains, causal
well-posedness, growth/stability, general l, polar sector, non-Einstein
backgrounds, or any ringdown statement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import sympy as sp

from weyl_geometry import Geometry

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "certificates" / "BH2A_HORIZON_REACH.json"
SCHEMA_PATH = HERE / "schema" / "bh2a-horizon-reach-v1.schema.json"
BH2A_CERT = HERE / "certificates" / "BH2A_AXIAL_OPERATOR.json"

SCHEMA_NAME = "pure-weyl-bh2a-horizon-reach-v1"
RESULT_ID = "PURE_WEYL_BH2A_HORIZON_REACH"
RESULT_TOKEN = "BH2A_EXTRA_BRANCH_REACHES_HORIZON_LINEAR_MODE_LEVEL"


class BH2AReachError(RuntimeError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise BH2AReachError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_certificate() -> dict:
    t0_all = time.time()
    v, ph = sp.symbols("v phi")
    r = sp.Symbol("r", positive=True)
    x = sp.Symbol("x")
    m = sp.Symbol("m", positive=True)
    w = sp.Symbol("omega")
    rho = sp.Symbol("rho", positive=True)
    coords = [v, r, x, ph]
    receipts = {}

    B0 = 1 - 2 * m / r
    g0 = sp.zeros(4, 4)
    g0[0, 0] = -B0
    g0[0, 1] = g0[1, 0] = 1
    g0[2, 2] = r**2 / (1 - x**2)
    g0[3, 3] = r**2 * (1 - x**2)
    geo0 = Geometry(coords, g0)
    gi = geo0.ginv
    S = -3 * x * (1 - x**2)

    # ---- carrier and polynomial constraint --------------------------------
    t0 = time.time()
    p = sp.Function("p")(v, r)
    q = sp.Function("q")(v, r)
    c = sp.Function("c")(v, r)
    psi = sp.zeros(4, 4)
    psi[0, 3] = psi[3, 0] = p * S
    psi[1, 3] = psi[3, 1] = q * S
    psi[2, 3] = psi[3, 2] = c * 3 * (x**2 - 1)
    sdiv = sum(gi[a, e] * geo0.covd2(psi, e, a, 3)
               for a in range(4) for e in range(4) if gi[a, e] != 0)
    csol = sp.solve(sp.Eq(sp.cancel(sp.together(sdiv)), 0), c)
    _require(len(csol) == 1, "divergence constraint not uniquely solvable")
    c_expr = sp.expand(csol[0])
    _num, cden = sp.fraction(sp.cancel(sp.together(c_expr)))
    _require(not cden.has(r), f"constraint solution not polynomial in r: den {cden}")
    receipts["carrier_constraint"] = round(time.time() - t0, 1)

    # ---- extra-branch operator rows ---------------------------------------
    t0 = time.time()
    psi2 = sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.together(psi.subs(c, c_expr).doit()[i, j])))
    G = geo0.Gamma
    DX = [[[sp.cancel(sp.together(geo0.covd2(psi2, e, a, b))) for b in range(4)]
           for a in range(4)] for e in range(4)]

    def covd2X2(e, f, a, b):
        s = sp.diff(DX[f][a][b], coords[e])
        for hh in range(4):
            s -= (G[hh][e][f] * DX[hh][a][b] + G[hh][e][a] * DX[f][hh][b]
                  + G[hh][e][b] * DX[f][a][hh])
        return s

    def Lrow(a, b):
        box = sum(gi[e, f] * covd2X2(e, f, a, b)
                  for e in range(4) for f in range(4) if gi[e, f] != 0)
        cx = sum(geo0.Weyl[a][cc][b][d]
                 * sum(gi[cc, e] * gi[d, f] * psi2[e, f] for e in range(4) for f in range(4))
                 for cc in range(4) for d in range(4))
        return sp.cancel(sp.together(box / 2 + cx))

    Lt = sp.cancel(Lrow(0, 3) / S)
    Lr = sp.cancel(Lrow(1, 3) / S)
    _require(not Lt.has(x) and not Lr.has(x), "angular stripping failed")
    receipts["operator_rows"] = round(time.time() - t0, 1)

    # ---- Fourier reduction and residue analysis ---------------------------
    t0 = time.time()
    P = sp.Function("P")(r)
    Q = sp.Function("Q")(r)
    four = {p: P * sp.exp(sp.I * w * v), q: Q * sp.exp(sp.I * w * v)}
    E = sp.exp(sp.I * w * v)
    Ltf = sp.expand(sp.cancel(sp.together(Lt.subs(four).doit() / E)))
    Lrf = sp.expand(sp.cancel(sp.together(Lr.subs(four).doit() / E)))
    D2P, D2Q = sp.Derivative(P, (r, 2)), sp.Derivative(Q, (r, 2))
    sol = sp.solve([sp.Eq(Ltf, 0), sp.Eq(Lrf, 0)], [D2P, D2Q], dict=True)
    _require(bool(sol), "cannot solve for second derivatives")
    s0 = sol[0]
    DP, DQ = sp.Derivative(P, r), sp.Derivative(Q, r)
    A = sp.zeros(4, 4)
    A[0, 1] = sp.Integer(1)
    A[2, 3] = sp.Integer(1)
    eP = sp.expand(s0[D2P])
    eQ = sp.expand(s0[D2Q])
    A[1, 0] = eP.coeff(P); A[1, 1] = eP.coeff(DP); A[1, 2] = eP.coeff(Q); A[1, 3] = eP.coeff(DQ)
    A[3, 0] = eQ.coeff(P); A[3, 1] = eQ.coeff(DP); A[3, 2] = eQ.coeff(Q); A[3, 3] = eQ.coeff(DQ)
    Ar = sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.together(A[i, j].subs(r, 2 * m + rho))))
    for i in range(4):
        for j in range(4):
            _require(sp.simplify(sp.limit(rho**2 * Ar[i, j], rho, 0)) == 0,
                     f"irregular singular point: rho^2 A[{i}{j}] != 0")
    Res = sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.limit(rho * Ar[i, j], rho, 0)))
    ev = {sp.nsimplify(sp.simplify(kk)): mult for kk, mult in Res.eigenvals().items()}
    expected = {sp.Integer(0): 2,
                sp.nsimplify(-4 * sp.I * m * w): 1,
                sp.nsimplify(-2 - 4 * sp.I * m * w): 1}
    _require(
        all(any(sp.simplify(kk - ee) == 0 and mult == emult for ee, emult in expected.items())
            for kk, mult in ev.items()) and len(ev) == len(expected),
        f"unexpected indicial exponents {ev}",
    )
    null = Res.nullspace()
    _require(len(null) == 2, "zero exponent not geometric multiplicity 2")
    comp = sp.Matrix([[null[0][0], null[0][2]], [null[1][0], null[1][2]]])
    _require(comp.rank() == 2,
             "kernel vectors do not span independent (P, Q) profiles")
    receipts["residue_analysis"] = round(time.time() - t0, 1)

    # ---- Regge--Wheeler benchmark in the same chart ------------------------
    t0 = time.time()
    psi_rw = sp.Function("psi_rw")(v, r)
    V = B0 * (6 / r**2 - 6 * m / r**3)
    # RW master in EF: psi(t, r*) with t = v - r*: d/dt -> d/dv,
    # d/dr* -> B d/dr + d/dv acting on EF profile; equivalently the operator
    # -(d_t^2 - d_r*^2 + V) becomes on e^{i w v} Fourier profiles F(r):
    F = sp.Function("F")(r)
    # psi = F(r) e^{i w v}, v = t + r_*: the master equation
    # d_t^2 psi - d_{r*}^2 psi + V psi = 0 becomes B (B F')' + 2 i w B F' - V F = 0
    op = B0 * sp.diff(B0 * sp.diff(F, r), r) + 2 * sp.I * w * B0 * sp.diff(F, r) - V * F
    solF = sp.solve(sp.Eq(sp.expand(op), 0), sp.Derivative(F, (r, 2)), dict=True)
    e2 = sp.expand(solF[0][sp.Derivative(F, (r, 2))])
    A2 = sp.zeros(2, 2)
    A2[0, 1] = sp.Integer(1)
    A2[1, 0] = e2.coeff(F)
    A2[1, 1] = e2.coeff(sp.Derivative(F, r))
    A2r = sp.Matrix(2, 2, lambda i, j: sp.cancel(sp.together(A2[i, j].subs(r, 2 * m + rho))))
    for i in range(2):
        for j in range(2):
            _require(sp.simplify(sp.limit(rho**2 * A2r[i, j], rho, 0)) == 0,
                     "RW benchmark irregular")
    Res2 = sp.Matrix(2, 2, lambda i, j: sp.cancel(sp.limit(rho * A2r[i, j], rho, 0)))
    ev2 = {sp.nsimplify(sp.simplify(kk)): mult for kk, mult in Res2.eigenvals().items()}
    expected2 = {sp.Integer(0): 1, sp.nsimplify(-1 - 4 * sp.I * m * w): 1}
    _require(
        len(ev2) == 2 and all(
            any(sp.simplify(kk - ee) == 0 for ee in expected2) for kk in ev2),
        f"unexpected RW benchmark exponents {ev2}",
    )
    receipts["rw_benchmark"] = round(time.time() - t0, 1)
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
            "background_family": "Schwarzschild (symbolic m)",
            "conformal_frame": "working gauge; ingoing EF chart (v, r, x = cos theta, phi)",
            "generator": "not used; mode-level statements only",
            "phase_space": "none; no flux or pairing claim",
            "horizon_condition": "analyticity at r = 2m in the ingoing EF chart (future-horizon regularity)",
            "infinity_condition": "none imposed",
            "lifecycle": "CLASSIFIED",
        },
        "carrier": {
            "definition": "axial l=2 trace-free divergence-free psi_ab with psi_vphi = p S, psi_rphi = q S; third component solved from the divergence constraint",
            "constraint_regularity": "the EF-chart constraint solution is polynomial in r (the 1/(r-2m) of the Schwarzschild chart is a chart artifact)",
            "equation": "(1/2) Box psi + C psi = 0 (certified extra-branch equation, BH-2A stage 1)",
        },
        "horizon_analysis": {
            "singular_point": "r = 2m is a regular singular point of the Fourier-reduced first-order system (rho^2 A -> 0 componentwise)",
            "indicial_exponents": ["0 (multiplicity 2)", "-4*I*m*omega", "-2 - 4*I*m*omega"],
            "zero_eigenspace": "geometric multiplicity 2: two analytic ingoing families, no leading logarithm",
            "conclusion": "the extra fourth-order branch reaches the future horizon: a two-parameter ingoing-regular family exists at every frequency",
        },
        "rw_benchmark": {
            "statement": "the Einstein/Regge-Wheeler first-order system in the same chart has residue spectrum {0, -1 - 4*I*m*omega} (scalar solution exponents {0, -4*I*m*omega}): an ingoing-regular family also exists",
            "consequence": "future-horizon regularity does not distinguish the extra branch from the Einstein branch; exclusion of the extra branch must come from outer-boundary, causal, or flux/sign conditions",
        },
        "claim_flags": {
            "carrier_constraint_regular_certified": True,
            "regular_singular_point_certified": True,
            "indicial_exponents_certified": True,
            "ingoing_family_dimension_certified": True,
            "rw_benchmark_certified": True,
            "flux_or_sign_certified": False,
            "outer_boundary_domain_certified": False,
            "causal_exclusion_decided": False,
            "growth_or_stability_certified": False,
            "general_l_or_polar_certified": False,
            "non_einstein_background_certified": False,
        },
        "missing_objects": [
            "bilinear symplectic flux matrix and Lee-Wald signs on both branches",
            "outer-boundary operator domains and falloff classification",
            "causal disposition of the extra branch (initial-boundary formulation)",
            "growth/stability data; general l; polar sector",
            "extra-branch horizon analysis on non-Einstein backgrounds",
        ],
        "stage_seconds": receipts,
        "provenance": {
            "generator_path": "black_hole_programme/bh2a_horizon_reach.py",
            "engine_path": "black_hole_programme/weyl_geometry.py",
            "engine_sha256": _sha256(HERE / "weyl_geometry.py"),
            "bh2a_certificate": str(BH2A_CERT.relative_to(ROOT)),
            "bh2a_certificate_sha256": _sha256(BH2A_CERT),
        },
        "verification_command": "python3 black_hole_programme/verify_bh2a_horizon_reach.py",
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
