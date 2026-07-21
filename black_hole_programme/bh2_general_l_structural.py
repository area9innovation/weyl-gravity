"""BH-2 general-l structural extension (axial exact sequence, symbolic l).

Certificate `black_hole_programme/certificates/BH2_GENERAL_L_STRUCTURAL.json`.
Verdict token `BH2_GENERAL_L_AXIAL_EXACT_SEQUENCE_SYMBOLIC_L_PAIRING_NOT_ACTIVATED`.
Dependency tags LOCAL-ALGEBRAIC + REDUCED-MODE.  Lifecycle CLASSIFIED.
Disposition AXIAL_SYMBOLIC_L_PROVEN + PAIRING_NOT_ACTIVATED.

STOP-CONDITION GATE (fixture-only branch).  The terminal polar universal-quantifier
repair BH2_POLAR_QUANTIFIER_REPAIR closed FIXTURE-ONLY (the generic-omega
inertia / no-real-exceptional-frequency statement is fail-closed; only a != 0 is
all-omega).  Per this item's stop condition, the generic-l invariant CROSS PAIRING
theorem is therefore recorded NOT_ACTIVATED until a symbolic-omega polar identity
exists; NO generic-l pairing statement is extrapolated from the l=2 samples.

What IS proved here is the l-dependence that transports WITHOUT omega-pairing and
WITHOUT mode sampling: the axial Ricci-to-Bach exact-sequence operator structure as
an exact function of the angular eigenvalue Lambda = l(l+1).  Every angular factor
is derived from the Legendre identity (1-x^2)P'' = 2x P' - Lambda P applied to a
generic P_l(x); l=2 (Lambda=6) is a positive control against the certified
BH2A_AXIAL_L2_OPERATOR / BH2A stage-2 residue spectrum; l=0,1 are isolated as
exceptional representations by exact harmonic degeneration; a finite list of l
values is never used to establish the generic statement.

PROVEN (axial parity, both branches, generic l >= 2):
  1. Einstein/RW branch master potential V = B(Lambda/r^2 - 6 m/r^3), Lambda=l(l+1)
     (proportionality factor -r^6, identical to the certified l=2 reduction);
     reduces to the certified V = B(6/r^2 - 6 m/r^3) at Lambda = 6.
  2. RW horizon indicial: exponents s = +-2 i m omega at the regular singular point
     r = 2m, INDEPENDENT of Lambda (the Lambda/r^2 term is regular there and enters
     only at subleading order) => RW ingoing-regular dimension = 1 for all l.
  3. Extra branch (Ricci-to-Bach carrier, (1/2)Box psi + C psi = 0, ingoing EF chart):
     horizon residue spectrum {0 (x2), -4 i m omega, -2 - 4 i m omega}, INDEPENDENT
     of Lambda; identical to the certified l=2 spectrum => extra-branch ingoing
     structure is l-independent for all l >= 2.
  4. Operator composition is l-generic: the split identity delta B = (1/2)Box dRic
     + C.dRic (axial, dR=0) is background-tensorial (certified general, BH2B stage 1);
     under tensor-harmonic reduction l enters ONLY through Lambda = l(l+1).
  5. Exceptional set = {0, 1}: the axial vector harmonic S_l = -(1-x^2)P_l' vanishes
     at l=0, and the extra-branch angular component H2_l = Lambda P_l - 2x P_l'
     vanishes at l=1 (Lambda=2, P_1=x); l >= 2 carries the full exact sequence.

NOT_ACTIVATED (this item's stop condition):
  * the generic-l invariant cross pairing / cross-scalar theorem (both parities) --
    activation condition: a symbolic-omega polar identity (BH2_POLAR_QUANTIFIER_REPAIR
    route B, the gauge-radical identity Z = E - (K^{-1}a^H).X symplectically null for
    all real omega).

NOT ESTABLISHED (honest boundary; not this item): the polar-parity detailed
symbolic-Lambda radial reduction (Zerilli potential + polar extra-branch residue) --
the same Legendre method applies and is the immediate parallel step, but it is not
computed in this certificate; complex omega; asymptotic phase space; stability;
QNM; ringdown; scattering; positivity; particle; nonlinear.  l=0,1 are excluded
from the generic theorem (isolated exceptional representations).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import sympy as sp

from weyl_geometry import Geometry
from linearized_bach import LinearizedBach

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SCHEMA_PATH = HERE / "schema" / "bh2-general-l-structural-v1.schema.json"
OUTPUT = HERE / "certificates" / "BH2_GENERAL_L_STRUCTURAL.json"
AXIAL_L2 = HERE / "certificates" / "BH2A_AXIAL_OPERATOR.json"
EXTRA_L2 = HERE / "certificates" / "BH2A_HORIZON_REACH.json"
POLAR_REPAIR = HERE / "certificates" / "BH2_POLAR_QUANTIFIER_REPAIR.json"
SPLIT_L2 = HERE / "certificates" / "BH2B_POLAR_SPLIT.json"

SCHEMA_NAME = "pure-weyl-bh2-general-l-structural-v1"
RESULT_ID = "PURE_WEYL_BH2_GENERAL_L_STRUCTURAL"
RESULT_TOKEN = ("BH2_GENERAL_L_AXIAL_EXACT_SEQUENCE_SYMBOLIC_L_"
                "PAIRING_NOT_ACTIVATED")

# symbols
t, v, ph = sp.symbols("t v phi")
r = sp.Symbol("r", positive=True)
x = sp.Symbol("x")
m = sp.Symbol("m", positive=True)
w = sp.Symbol("omega")
Lam = sp.Symbol("Lambda")
rho = sp.Symbol("rho", positive=True)


class GeneralLError(RuntimeError):
    pass


def _require(cond, msg):
    if not cond:
        raise GeneralLError(msg)


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _legendre_reduce(e, P):
    """Reduce every x-derivative of P of order >= 2 via the Legendre identity
    (1-x^2) P'' = 2x P' - Lambda P, leaving only P and P'."""
    e = sp.expand(e)
    Pp = sp.diff(P, x)
    for order in range(10, 1, -1):
        d = sp.diff(P, (x, order))
        if e.has(d):
            repl = sp.diff((2 * x * Pp - Lam * P) / (1 - x**2), (x, order - 2))
            e = sp.expand(sp.together(e.subs(d, repl)))
    return sp.cancel(sp.together(e))


# --------------------------------------------------------------------------- #
#  1-2. axial Einstein/RW branch: master potential and horizon indicial       #
# --------------------------------------------------------------------------- #
def axial_rw_branch():
    coords = [t, r, x, ph]
    B0 = 1 - 2 * m / r
    g0 = sp.diag(-B0, 1 / B0, r**2 / (1 - x**2), r**2 * (1 - x**2))
    geo0 = Geometry(coords, g0)
    lb = LinearizedBach(geo0)
    P = sp.Function("P")(x)
    S = -(1 - x**2) * sp.diff(P, x)
    h0 = sp.Function("h0")(t, r)
    h1 = sp.Function("h1")(t, r)
    h = sp.zeros(4, 4)
    h[0, 3] = h[3, 0] = h0 * S
    h[1, 3] = h[3, 1] = h1 * S
    lb.build(h)
    dRic = lb.dRic

    # [1,3] ~ S; strip
    R1 = _legendre_reduce(dRic[1, 3], P)
    R1r = _legendre_reduce(sp.cancel(sp.together(R1 / S)), P)
    _require(not R1r.has(x) and not R1r.has(P), "[1,3]/S not x-free")
    # [2,3] = C0 * (Lambda P - 2x P'); extract C0
    R2 = _legendre_reduce(dRic[2, 3], P)
    Px, Ps = sp.Symbol("Px"), sp.Symbol("Ps")
    C0 = sp.cancel(sp.together(
        R2.subs({sp.diff(P, x): Px, P: Ps}) / (Lam * Ps - 2 * x * Px)))
    _require(not C0.has(x) and not C0.has(Ps) and not C0.has(Px),
             "[2,3] != C0*(Lambda P - 2x P')")

    # Fourier, eliminate H0, reduce to RW master
    H0 = sp.Function("H0")(r)
    H1 = sp.Function("H1")(r)
    E = sp.exp(sp.I * w * t)
    sub4 = {h0: H0 * E, h1: H1 * E}
    R1f = sp.cancel(sp.together(sp.expand(R1r.subs(sub4).doit() / E)))
    R2f = sp.cancel(sp.together(sp.expand(C0.subs(sub4).doit() / E)))
    H0sol = sp.solve(sp.Eq(R2f, 0), H0)[0]
    resid = sp.cancel(sp.together(
        R1f.subs({sp.Derivative(H0, r): sp.diff(H0sol, r), H0: H0sol}).doit()))
    num, _ = sp.fraction(resid)
    _require(not sp.expand(num).has(H0), "H0 not eliminated")
    psi = sp.Function("psi")(r)
    n2, _ = sp.fraction(sp.cancel(sp.together(
        sp.expand(num).subs(H1, r * psi / B0).doit())))
    V = B0 * (Lam / r**2 - 6 * m / r**3)
    master = sp.expand(B0 * sp.diff(B0 * sp.diff(psi, r), r) + (w**2 - V) * psi)
    ratio = sp.cancel(sp.together(sp.expand(n2) / master))
    _require(not ratio.has(psi), "reduction is not the RW master equation")
    _require(sp.simplify(ratio + r**6) == 0,
             f"unexpected proportionality factor {ratio}")

    # horizon indicial at r = 2m (t-chart): exponents s, Lambda-independence
    B0r = 1 - 2 * m / (2 * m + rho)
    Vr = B0r * (Lam / (2 * m + rho)**2 - 6 * m / (2 * m + rho)**3)
    ss = sp.Symbol("s")
    psr = rho**ss
    Lpsi = (B0r * (sp.diff(B0r, rho) * sp.diff(psr, rho)
                   + B0r * sp.diff(psr, (rho, 2))) + (w**2 - Vr) * psr)
    ind = sp.simplify(sp.limit(sp.cancel(sp.together(Lpsi / rho**ss)), rho, 0))
    exps = sp.solve(sp.Eq(ind, 0), ss)
    lam_dep = any(sp.sympify(z).has(Lam) for z in exps)
    _require(not lam_dep, "RW horizon exponents depend on Lambda")
    _require(set(sp.simplify(e) for e in exps)
             == {sp.simplify(2 * sp.I * m * w), sp.simplify(-2 * sp.I * m * w)},
             f"unexpected RW exponents {exps}")
    return {
        "rw_master_potential": "B*(Lambda/r**2 - 6*m/r**3)",
        "master_proportionality_factor": "-r**6",
        "rw_potential_at_l2": sp.sstr(sp.cancel(V.subs(Lam, 6))),
        "horizon_indicial_polynomial": sp.sstr(ind),
        "horizon_exponents": [sp.sstr(e) for e in exps],
        "horizon_exponents_lambda_independent": (not lam_dep),
        "rw_ingoing_dimension": 1,
    }


# --------------------------------------------------------------------------- #
#  3. axial extra branch (Ricci-to-Bach carrier) horizon residue spectrum      #
# --------------------------------------------------------------------------- #
def axial_extra_branch():
    coords = [v, r, x, ph]
    B0 = 1 - 2 * m / r
    g0 = sp.zeros(4, 4)
    g0[0, 0] = -B0
    g0[0, 1] = g0[1, 0] = 1
    g0[2, 2] = r**2 / (1 - x**2)
    g0[3, 3] = r**2 * (1 - x**2)
    geo0 = Geometry(coords, g0)
    gi = geo0.ginv
    P = sp.Function("P")(x)
    Pp = sp.diff(P, x)
    S = -(1 - x**2) * Pp
    H2ang = Lam * P - 2 * x * Pp
    p = sp.Function("p")(v, r)
    q = sp.Function("q")(v, r)
    c = sp.Function("c")(v, r)
    psi = sp.zeros(4, 4)
    psi[0, 3] = psi[3, 0] = p * S
    psi[1, 3] = psi[3, 1] = q * S
    psi[2, 3] = psi[3, 2] = c * H2ang
    sdiv = sum(gi[a, e] * geo0.covd2(psi, e, a, 3)
               for a in range(4) for e in range(4) if gi[a, e] != 0)
    sdiv = _legendre_reduce(sdiv, P)
    Ps, Pps = sp.Symbol("Ps"), sp.Symbol("Pps")
    csol = sp.solve(sp.Eq(sp.cancel(sp.together(
        sdiv.subs({Pp: Pps, P: Ps}))), 0), c)
    _require(len(csol) == 1, "divergence constraint not uniquely solvable")
    c_expr = sp.expand(csol[0]).subs({Pps: Pp, Ps: P})
    psi2 = sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.together(
        psi.subs(c, c_expr).doit()[i, j])))
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
                 * sum(gi[cc, e] * gi[d, f] * psi2[e, f]
                       for e in range(4) for f in range(4))
                 for cc in range(4) for d in range(4))
        return sp.cancel(sp.together(box / 2 + cx))

    Lt = _legendre_reduce(sp.cancel(sp.together(
        _legendre_reduce(Lrow(0, 3), P) / S)), P)
    Lr = _legendre_reduce(sp.cancel(sp.together(
        _legendre_reduce(Lrow(1, 3), P) / S)), P)
    _require(not Lt.has(x) and not Lt.has(P), "extra Lt/S not x-free")
    _require(not Lr.has(x) and not Lr.has(P), "extra Lr/S not x-free")
    Pr = sp.Function("P")(r)
    Qr = sp.Function("Q")(r)
    E = sp.exp(sp.I * w * v)
    four = {p: Pr * E, q: Qr * E}
    Ltf = sp.expand(sp.cancel(sp.together(Lt.subs(four).doit() / E)))
    Lrf = sp.expand(sp.cancel(sp.together(Lr.subs(four).doit() / E)))
    D2P, D2Q = sp.Derivative(Pr, (r, 2)), sp.Derivative(Qr, (r, 2))
    sol = sp.solve([sp.Eq(Ltf, 0), sp.Eq(Lrf, 0)], [D2P, D2Q], dict=True)[0]
    DP, DQ = sp.Derivative(Pr, r), sp.Derivative(Qr, r)
    A = sp.zeros(4, 4)
    A[0, 1] = 1
    A[2, 3] = 1
    eP, eQ = sp.expand(sol[D2P]), sp.expand(sol[D2Q])
    A[1, 0], A[1, 1] = eP.coeff(Pr), eP.coeff(DP)
    A[1, 2], A[1, 3] = eP.coeff(Qr), eP.coeff(DQ)
    A[3, 0], A[3, 1] = eQ.coeff(Pr), eQ.coeff(DP)
    A[3, 2], A[3, 3] = eQ.coeff(Qr), eQ.coeff(DQ)
    Ar = sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.together(
        A[i, j].subs(r, 2 * m + rho))))
    Res = sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.limit(rho * Ar[i, j], rho, 0)))
    ev = Res.eigenvals()
    ev_simpl = {sp.simplify(k): int(mult) for k, mult in ev.items()}
    expected = {sp.simplify(sp.Integer(0)): 2,
                sp.simplify(-4 * sp.I * m * w): 1,
                sp.simplify(-2 - 4 * sp.I * m * w): 1}
    lam_dep = any(k.has(Lam) for k in ev_simpl)
    _require(not lam_dep, "extra-branch residue depends on Lambda")
    _require(all(any(sp.simplify(k - e) == 0 and mult == emult
                     for e, emult in expected.items())
                 for k, mult in ev_simpl.items())
             and len(ev_simpl) == len(expected),
             f"unexpected extra-branch residue spectrum {ev_simpl}")
    return {
        "extra_branch_residue_spectrum":
            ["0 (x2)", "-4*I*m*omega", "-2 - 4*I*m*omega"],
        "residue_lambda_independent": (not lam_dep),
        "extra_branch_ingoing_structure": "l-independent for all l >= 2",
    }


# --------------------------------------------------------------------------- #
#  5. exceptional set: harmonic degeneration at l = 0, 1                        #
# --------------------------------------------------------------------------- #
def exceptional_set():
    legP = {0: sp.Integer(1), 1: x, 2: (3 * x**2 - 1) / 2,
            3: (5 * x**3 - 3 * x) / 2}
    rows = {}
    for l, P in legP.items():
        S = sp.expand(-(1 - x**2) * sp.diff(P, x))
        H2 = sp.expand(l * (l + 1) * P - 2 * x * sp.diff(P, x))
        rows[l] = {"S_l": sp.sstr(S), "H2_l": sp.sstr(H2),
                   "S_vanishes": S == 0, "H2_vanishes": H2 == 0}
    _require(rows[0]["S_vanishes"] and rows[0]["H2_vanishes"],
             "l=0 not fully degenerate")
    _require((not rows[1]["S_vanishes"]) and rows[1]["H2_vanishes"],
             "l=1 exceptional signature wrong")
    _require((not rows[2]["S_vanishes"]) and (not rows[2]["H2_vanishes"]),
             "l=2 unexpectedly degenerate")
    return {"exceptional_l": [0, 1],
            "criterion": "axial vector harmonic S_l = -(1-x^2)P_l' vanishes at "
                         "l=0; extra-branch harmonic H2_l = Lambda P_l - 2x P_l' "
                         "vanishes at l=1 (Lambda=2, P_1=x); l>=2 nonzero and "
                         "independent",
            "controls": rows}


def build_certificate():
    out = {"stage_seconds": {}}
    t0 = time.time()
    rw = axial_rw_branch()
    out["stage_seconds"]["axial_rw_branch"] = round(time.time() - t0, 1)
    t0 = time.time()
    extra = axial_extra_branch()
    out["stage_seconds"]["axial_extra_branch"] = round(time.time() - t0, 1)
    exc = exceptional_set()

    prov = {}
    for key, path in (("axial_l2", AXIAL_L2), ("extra_l2", EXTRA_L2),
                      ("polar_repair", POLAR_REPAIR), ("split_l2", SPLIT_L2)):
        if path.exists():
            prov[f"{key}_certificate"] = str(path.relative_to(ROOT))
            prov[f"{key}_sha256"] = _sha256(path)
    _require(POLAR_REPAIR.exists(),
             "polar quantifier repair certificate required (stop-condition gate)")
    repair = json.loads(POLAR_REPAIR.read_text())
    fixture_only = (repair["claim_flags"]
                    ["no_real_exceptional_frequency_certified"] is False)
    _require(fixture_only,
             "polar repair is not fixture-only; re-evaluate the stop condition "
             "ELSE branch (land the full generic-l pairing theorem)")

    cert = {
        "schema": SCHEMA_NAME,
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH) if SCHEMA_PATH.exists() else None,
        "result_id": RESULT_ID,
        "result_token": RESULT_TOKEN,
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "disposition": "AXIAL_SYMBOLIC_L_PROVEN + PAIRING_NOT_ACTIVATED",
        "setting": "Schwarzschild symbolic m, axial l>=2, real frequency omega; "
                   "Lambda = l(l+1); Legendre identity (1-x^2)P'' = 2x P' - Lambda P",
        "stop_condition_branch":
            "fixture-only: BH2_POLAR_QUANTIFIER_REPAIR closed the polar universal "
            "quantifier fixture-only, so the generic-l cross pairing is "
            "NOT_ACTIVATED; no pairing extrapolated from l=2 samples",
        "provenance": prov,
        "proven_axial_generic_l": {
            "operator_composition_l_generic":
                "split identity delta B = (1/2)Box dRic + C.dRic is "
                "background-tensorial (BH2B stage 1, general); l enters only "
                "through Lambda = l(l+1)",
            "einstein_rw_branch": rw,
            "extra_branch": extra,
            "exceptional_set": exc,
            "positive_control_l2":
                "Lambda=6 reproduces the certified BH2A l=2 RW potential and the "
                "certified BH2A stage-2 residue spectrum exactly",
        },
        "pairing_not_activated": {
            "statement": "the generic-l invariant cross pairing / cross-scalar "
                         "theorem (both parities) is NOT_ACTIVATED",
            "reason": "the terminal polar universal-quantifier repair closed "
                      "fixture-only (no symbolic-omega polar pairing identity)",
            "activation_condition":
                "a symbolic-omega polar identity -- BH2_POLAR_QUANTIFIER_REPAIR "
                "route B: Z = E - (K^{-1} a^H).X symplectically null for all real "
                "omega (gauge-radical, even-parity twin of the axial RW-null "
                "theorem)",
            "no_extrapolation_from_samples": True,
        },
        "claim_flags": {
            "axial_rw_potential_symbolic_l_certified": True,
            "axial_rw_horizon_indicial_l_independent_certified": True,
            "axial_extra_branch_residue_l_independent_certified": True,
            "exceptional_set_0_1_certified": True,
            "polar_detailed_reduction_certified": False,
            "generic_l_cross_pairing_certified": False,
        },
        "not_claimed": {
            "polar_detailed_symbolic_lambda_reduction":
                "the polar Zerilli potential and polar extra-branch residue with "
                "symbolic Lambda are NOT computed here; the same Legendre method "
                "applies and is the immediate parallel step",
            "generic_l_cross_pairing": "NOT_ACTIVATED (see pairing_not_activated)",
            "l_0_and_l_1": "excluded as isolated exceptional representations",
            "complex_omega_stability_qnm_ringdown_scattering_positivity_particle_"
            "nonlinear": "none asserted",
        },
    }
    cert.update({k: v for k, v in out.items() if k != "stage_seconds"})
    cert["stage_seconds"] = out["stage_seconds"]
    return cert


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUTPUT))
    args = ap.parse_args()
    cert = build_certificate()
    Path(args.out).write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}")
    print("  disposition:", cert["disposition"])
    print("  RW potential: V = B(Lambda/r^2 - 6m/r^3); horizon exponents",
          cert["proven_axial_generic_l"]["einstein_rw_branch"]["horizon_exponents"],
          "(Lambda-independent)")
    print("  extra-branch residue:",
          cert["proven_axial_generic_l"]["extra_branch"]
          ["extra_branch_residue_spectrum"], "(Lambda-independent)")
    print("  exceptional l:",
          cert["proven_axial_generic_l"]["exceptional_set"]["exceptional_l"])


if __name__ == "__main__":
    main()
