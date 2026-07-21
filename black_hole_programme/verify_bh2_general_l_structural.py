"""Independent verifier for BH2_GENERAL_L_STRUCTURAL.

Independent rails:
  1. DIFFERENT HARMONIC recomputation.  The producer derives the axial reduction
     with a SYMBOLIC Lambda.  Here we recompute at CONCRETE l=3 (Lambda=12) with
     the explicit Legendre polynomial P_3 = (5x^3-3x)/2 -- no symbolic Lambda --
     and confirm: the RW master potential is B(12/r^2 - 6m/r^3); the extra-branch
     horizon residue spectrum is {0(x2), -4imw, -2-4imw}.  Because l=3 != l=2 and
     the spectrum is identical, the Lambda-independence is not an l=2 artifact.
  2. l=2 POSITIVE CONTROL against the certified BH2A operator / horizon reach:
     the symbolic potential at Lambda=6 equals B(6/r^2-6m/r^3); the residue
     spectrum equals the certified BH2A stage-2 spectrum.
  3. exceptional harmonics vanish exactly at l=0,1 and are nonzero for l>=2..4.
  4. stop-condition gate: the imported polar repair is fixture-only (its
     no_real_exceptional_frequency flag is False); provenance hashes; schema.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import sympy as sp

from weyl_geometry import Geometry
from linearized_bach import LinearizedBach

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERT = HERE / "certificates" / "BH2_GENERAL_L_STRUCTURAL.json"
POLAR_REPAIR = HERE / "certificates" / "BH2_POLAR_QUANTIFIER_REPAIR.json"
SCHEMA = HERE / "schema" / "bh2-general-l-structural-v1.schema.json"

t, v, ph = sp.symbols("t v phi")
r = sp.Symbol("r", positive=True)
x = sp.Symbol("x")
m = sp.Symbol("m", positive=True)
w = sp.Symbol("omega")
rho = sp.Symbol("rho", positive=True)


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _rw_potential_concrete(P):
    """Recompute the axial RW master potential for a CONCRETE Legendre P (no
    symbolic Lambda); return V such that B(BF')' + (w^2 - V)F = 0."""
    coords = [t, r, x, ph]
    B0 = 1 - 2 * m / r
    g0 = sp.diag(-B0, 1 / B0, r**2 / (1 - x**2), r**2 * (1 - x**2))
    geo0 = Geometry(coords, g0)
    lb = LinearizedBach(geo0)
    S = -(1 - x**2) * sp.diff(P, x)
    h0, h1 = sp.Function("h0")(t, r), sp.Function("h1")(t, r)
    h = sp.zeros(4, 4)
    h[0, 3] = h[3, 0] = h0 * S
    h[1, 3] = h[3, 1] = h1 * S
    lb.build(h)
    dRic = lb.dRic
    R1 = sp.cancel(sp.together(dRic[1, 3]) / S)
    # xphi row: divide by the concrete second harmonic (Lambda P - 2x P')
    Lam = sp.Integer(P.as_poly(x).degree() * (P.as_poly(x).degree() + 1)) \
        if P != 1 else sp.Integer(0)
    H2 = sp.expand(Lam * P - 2 * x * sp.diff(P, x))
    R2 = sp.cancel(sp.together(dRic[2, 3]) / H2)
    assert not R1.has(x) and not R2.has(x), "angular stripping failed"
    H0, H1 = sp.Function("H0")(r), sp.Function("H1")(r)
    E = sp.exp(sp.I * w * t)
    sub4 = {h0: H0 * E, h1: H1 * E}
    R1f = sp.cancel(sp.together(sp.expand(R1.subs(sub4).doit() / E)))
    R2f = sp.cancel(sp.together(sp.expand(R2.subs(sub4).doit() / E)))
    H0sol = sp.solve(sp.Eq(R2f, 0), H0)[0]
    resid = sp.cancel(sp.together(
        R1f.subs({sp.Derivative(H0, r): sp.diff(H0sol, r), H0: H0sol}).doit()))
    num, _ = sp.fraction(resid)
    psi = sp.Function("psi")(r)
    n2, _ = sp.fraction(sp.cancel(sp.together(
        sp.expand(num).subs(H1, r * psi / B0).doit())))
    V = B0 * (Lam / r**2 - 6 * m / r**3)
    master = sp.expand(B0 * sp.diff(B0 * sp.diff(psi, r), r) + (w**2 - V) * psi)
    ratio = sp.cancel(sp.together(sp.expand(n2) / master))
    ok = (not ratio.has(psi)) and sp.simplify(ratio + r**6) == 0
    return V, ok


def _extra_residue_concrete(P):
    """Recompute the axial extra-branch horizon residue spectrum for a concrete P."""
    coords = [v, r, x, ph]
    B0 = 1 - 2 * m / r
    g0 = sp.zeros(4, 4)
    g0[0, 0] = -B0
    g0[0, 1] = g0[1, 0] = 1
    g0[2, 2] = r**2 / (1 - x**2)
    g0[3, 3] = r**2 * (1 - x**2)
    geo0 = Geometry(coords, g0)
    gi = geo0.ginv
    deg = P.as_poly(x).degree()
    Lam = sp.Integer(deg * (deg + 1))
    S = -(1 - x**2) * sp.diff(P, x)
    H2 = sp.expand(Lam * P - 2 * x * sp.diff(P, x))
    p, q, c = (sp.Function("p")(v, r), sp.Function("q")(v, r),
               sp.Function("c")(v, r))
    psi = sp.zeros(4, 4)
    psi[0, 3] = psi[3, 0] = p * S
    psi[1, 3] = psi[3, 1] = q * S
    psi[2, 3] = psi[3, 2] = c * H2
    sdiv = sum(gi[a, e] * geo0.covd2(psi, e, a, 3)
               for a in range(4) for e in range(4) if gi[a, e] != 0)
    c_expr = sp.expand(sp.solve(sp.Eq(sp.cancel(sp.together(sdiv)), 0), c)[0])
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

    Lt = sp.cancel(sp.together(Lrow(0, 3) / S))
    Lr = sp.cancel(sp.together(Lrow(1, 3) / S))
    assert not Lt.has(x) and not Lr.has(x), "extra angular stripping failed"
    Pr, Qr = sp.Function("P")(r), sp.Function("Q")(r)
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
    return {sp.simplify(k): int(mult) for k, mult in Res.eigenvals().items()}


def main():
    cert = json.loads(CERT.read_text())
    checks = []

    def check(name, cond):
        checks.append((name, bool(cond)))
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}", flush=True)

    P3 = (5 * x**3 - 3 * x) / 2          # l = 3, Lambda = 12
    P2 = (3 * x**2 - 1) / 2              # l = 2, Lambda = 6

    # Rail 1: different-harmonic (l=3) RW potential
    V3, ok3 = _rw_potential_concrete(P3)
    check("l=3 RW potential = B(12/r^2 - 6m/r^3), factor -r^6",
          ok3 and sp.simplify(V3 - (1 - 2 * m / r) * (12 / r**2 - 6 * m / r**3))
          == 0)
    # l=2 positive control
    V2, ok2 = _rw_potential_concrete(P2)
    check("l=2 RW potential = B(6/r^2 - 6m/r^3) (certified control)",
          ok2 and sp.simplify(V2 - (1 - 2 * m / r) * (6 / r**2 - 6 * m / r**3))
          == 0)

    # Rail 1: extra-branch residue at l=3 vs l=2 (must be identical)
    exp_spec = {sp.Integer(0): 2, sp.simplify(-4 * sp.I * m * w): 1,
                sp.simplify(-2 - 4 * sp.I * m * w): 1}
    res3 = _extra_residue_concrete(P3)
    res2 = _extra_residue_concrete(P2)

    def spec_eq(a, b):
        if len(a) != len(b):
            return False
        return all(any(sp.simplify(ka - kb) == 0 and va == vb
                       for kb, vb in b.items()) for ka, va in a.items())
    check("l=3 extra-branch residue = {0(x2), -4imw, -2-4imw}",
          spec_eq(res3, exp_spec))
    check("l=2 extra-branch residue = certified spectrum", spec_eq(res2, exp_spec))
    check("residue spectra at l=3 and l=2 are IDENTICAL (l-independence)",
          spec_eq(res3, res2))

    # Rail 3: exceptional harmonics
    legP = {0: sp.Integer(1), 1: x, 2: P2, 3: P3,
            4: (35 * x**4 - 30 * x**2 + 3) / 8}
    exc_ok = True
    for l, P in legP.items():
        S = sp.expand(-(1 - x**2) * sp.diff(P, x))
        H2 = sp.expand(l * (l + 1) * P - 2 * x * sp.diff(P, x))
        if l == 0:
            exc_ok &= (S == 0 and H2 == 0)
        elif l == 1:
            exc_ok &= (S != 0 and H2 == 0)
        else:
            exc_ok &= (S != 0 and H2 != 0)
    check("exceptional set {0,1} by harmonic degeneration; l>=2 nonsingular",
          exc_ok and cert["proven_axial_generic_l"]["exceptional_set"]
          ["exceptional_l"] == [0, 1])

    # Rail 4: stop-condition gate + provenance + schema
    repair = json.loads(POLAR_REPAIR.read_text())
    check("polar repair is fixture-only (stop-condition gate)",
          repair["claim_flags"]["no_real_exceptional_frequency_certified"]
          is False)
    check("cert records pairing NOT_ACTIVATED, no extrapolation",
          cert["pairing_not_activated"]["no_extrapolation_from_samples"] is True
          and cert["claim_flags"]["generic_l_cross_pairing_certified"] is False)
    check("polar repair provenance hash matches",
          cert["provenance"]["polar_repair_sha256"] == _sha256(POLAR_REPAIR))
    try:
        import jsonschema
        jsonschema.validate(cert, json.loads(SCHEMA.read_text()))
        check("schema validation", True)
    except ImportError:
        print("  [SKIP] schema validation (jsonschema not installed)")
    except Exception as exc:  # noqa: BLE001
        check(f"schema validation ({exc})", False)

    ok = all(c for _, c in checks)
    print(f"\n{'ALL CHECKS PASSED' if ok else 'VERIFICATION FAILED'} "
          f"({sum(c for _, c in checks)}/{len(checks)})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
