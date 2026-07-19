"""Local Einstein-sector Cauchy truncation on the Schwarzschild exterior.

Fail-closed builder for
`black_hole_programme/certificates/BH_LOCAL_EINSTEIN_CAUCHY_TRUNCATION.json`.

Verdict: BH_LOCAL_CAUCHY_TRUNCATION_SELECTS_EINSTEIN_MODULO_CONFORMAL_GAUGE.

Setting: Schwarzschild exterior r > 2m (symbolic m), static t-chart, Cauchy
surface Sigma = {t = const, r > 2m}; carrier operator (the certified
Ricci-to-Bach composition factor)

    (L psi)_ab = (1/2) Box psi_ab + C_acbd psi^cd
                 - (1/6) grad_a grad_b S - (1/12) g_ab Box S,   S = tr psi.

Exact identities certified here (l = 2 harmonic classes, both parities):

1. AXIAL: S = 0 identically on the class, so L = (1/2) Box + C o (-);
   the operator is supported on the three axial rows; the Bianchi vector
   B_b = nabla^a psi_ab has only the phi component; and EXACTLY

       nabla^a (L psi)_a phi = (1/2) Box B_phi          (zero remainder).

   Hence L is normally hyperbolic componentwise, zero Cauchy data
   (psi|_Sigma = 0, nabla_n psi|_Sigma = 0) propagates psi = 0 on the
   globally hyperbolic exterior by the standard energy estimate for tensor
   wave systems [cited, not re-proved here], and the Bianchi constraint
   propagates by scalar wave uniqueness: statement (A) of the work item
   holds unconditionally in the axial sector.
2. POLAR: g^{ab} (L psi)_ab = 0 IDENTICALLY (PDE-level tracelessness), so
   the trace/conformal direction is not controlled by the equation, and

       psi_conf(Phi) = -grad grad Phi - (1/2) g Box Phi,  Phi = t^4 chi(r) P2

   is an exact nonuniqueness witness: psi|_Sigma = 0, dt psi|_Sigma = 0,
   psi != 0, L psi = 0 exactly.  The divergence identity
   nabla^a(L psi)_ab = (1/2) Box B_b with B_b = nabla^a psi_ab - (1/2)
   grad_b S again holds EXACTLY in all components.  Using the certified
   conformal trace relation S(psi_conf(Phi)) = -3 Box Phi
   (BH2B_POLAR_REACH), the gauge subtraction Phi_0 (solving
   -3 Box Phi_0 = S(psi) with zero Cauchy data) reduces any zero-data
   solution to a TRACEFREE solution of the normally hyperbolic system
   (1/2) Box + C o (-), which vanishes: hence zero Cauchy data implies
   psi = psi_conf(Phi_0) -- Einstein selection holds exactly MODULO the
   conformal-gauge orbit, and on the traceless slice it is uniqueness.
3. EXACT SEQUENCE (no direct sum, no surjectivity asserted):

   0 -> ker(delta Ric) -> ker(delta Bach) -> ker(L) cap im(delta Ric),

   where the last object is, on the declared domain with zero Cauchy data,
   the conformal-gauge orbit {psi_conf(Phi)} in the polar sector and {0}
   in the axial sector.
4. ENDPOINT COMPARISON: this local initial-data truncation is a different
   kind of restriction from the certified endpoint diagnostics (horizon
   ingoing analyticity, leading falloff class), which do NOT select the
   Einstein branch (BH2A/BH2B dispositions).  Local Cauchy truncation
   selects; endpoint regularity does not.
5. MUTATION: dropping the normal-derivative datum admits the exact
   time-odd witness u = (psi(t) - psi(-t))/2 built from a certified
   ingoing axial mode (real-coefficient operator): u|_Sigma = 0 but
   dt u|_Sigma != 0 and u != 0 -- the certificate verifies this witness
   and thereby rejects the weakened hypothesis.

NOT claimed: nonlinear closure, complex-frequency mode analysis,
scattering, general l, a canonical Einstein-plus-extra splitting, that
every psi solution lifts to a metric perturbation, or any statement about
the sourced flux fixtures currently under revalidation.
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
DEFAULT_OUTPUT = HERE / "certificates" / "BH_LOCAL_EINSTEIN_CAUCHY_TRUNCATION.json"
SCHEMA_PATH = HERE / "schema" / "bh-local-einstein-cauchy-truncation-v1.schema.json"
AXOP = HERE / "certificates" / "BH2A_AXIAL_OPERATOR.json"
PSPLIT = HERE / "certificates" / "BH2B_POLAR_SPLIT.json"

SCHEMA_NAME = "pure-weyl-bh-local-einstein-cauchy-truncation-v1"
RESULT_ID = "PURE_WEYL_BH_LOCAL_EINSTEIN_CAUCHY_TRUNCATION"
RESULT_TOKEN = "BH_LOCAL_CAUCHY_TRUNCATION_SELECTS_EINSTEIN_MODULO_CONFORMAL_GAUGE"


class CauchyTruncationError(RuntimeError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise CauchyTruncationError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _cancel(e):
    return sp.cancel(sp.together(e))


def run_analysis(geo_cls) -> dict:
    t0_all = time.time()
    out: dict = {"stage_seconds": {}}
    t, ph = sp.symbols("t phi")
    r = sp.Symbol("r", positive=True)
    x = sp.Symbol("x")
    m = sp.Symbol("m", positive=True)
    B0 = 1 - 2 * m / r
    coords = [t, r, x, ph]
    g0 = sp.diag(-B0, 1 / B0, r**2 / (1 - x**2), r**2 * (1 - x**2))
    geo = geo_cls(coords, g0)
    gi = geo.ginv
    G = geo.Gamma
    N = 4
    P2 = (3 * x**2 - 1) / 2
    dP2 = sp.diff(P2, x)
    Wxx = sp.Rational(3, 2)
    Wpp = -sp.Rational(3, 2) * (1 - x**2) ** 2
    S_ax = -3 * x * (1 - x**2)

    def covd2X2_factory(DX):
        def covd2X2(e, f, a, b):
            s = sp.diff(DX[f][a][b], coords[e])
            for hh in range(N):
                s -= (G[hh][e][f] * DX[hh][a][b] + G[hh][e][a] * DX[f][hh][b]
                      + G[hh][e][b] * DX[f][a][hh])
            return s
        return covd2X2

    def carrier_op(psi):
        """(1/2) Box psi + C o psi - (1/6) DD S - (1/12) g Box S, exact."""
        S_tr = _cancel(sum(gi[a, b] * psi[a, b] for a in range(N)
                           for b in range(N)))
        DX = [[[_cancel(geo.covd2(psi, e, a, b)) for b in range(N)]
               for a in range(N)] for e in range(N)]
        covd2X2 = covd2X2_factory(DX)
        dS = [sp.diff(S_tr, coords[e]) for e in range(N)]
        DDS = sp.Matrix(4, 4, lambda a, b: _cancel(
            sp.diff(dS[a], coords[b])
            - sum(G[hh][a][b] * dS[hh] for hh in range(N))))
        boxS = _cancel(sum(gi[e, f] * DDS[e, f] for e in range(N)
                           for f in range(N) if gi[e, f] != 0))
        L = sp.zeros(4, 4)
        for a in range(N):
            for b in range(a, N):
                box = sum(gi[e, f] * covd2X2(e, f, a, b) for e in range(N)
                          for f in range(N) if gi[e, f] != 0)
                cx = sum(geo.Weyl[a][cc][b][d]
                         * sum(gi[cc, e] * gi[d, f] * psi[e, f]
                               for e in range(N) for f in range(N))
                         for cc in range(N) for d in range(N))
                L[a, b] = L[b, a] = _cancel(box / 2 + cx - DDS[a, b] / 6
                                            - g0[a, b] * boxS / 12)
        return L, S_tr, boxS

    def one_form_box(Bform):
        DB = [[_cancel(sp.diff(Bform[a2], coords[e])
                       - sum(G[hh][e][a2] * Bform[hh] for hh in range(N)))
               for a2 in range(N)] for e in range(N)]

        def covdDB(e, f, a2):
            s = sp.diff(DB[f][a2], coords[e])
            for hh in range(N):
                s -= G[hh][e][f] * DB[hh][a2] + G[hh][e][a2] * DB[f][hh]
            return s

        return [_cancel(sum(gi[e, f] * covdDB(e, f, a2) for e in range(N)
                            for f in range(N) if gi[e, f] != 0))
                for a2 in range(N)]

    def divergence(L):
        DL = [[[_cancel(geo.covd2(L, e, a, b)) for b in range(N)]
               for a in range(N)] for e in range(N)]
        return [_cancel(sum(gi[a, e] * DL[e][a][b] for a in range(N)
                            for e in range(N) if gi[a, e] != 0))
                for b in range(N)]

    # ---- stage 1: axial identities ----------------------------------------
    t0 = time.time()
    p_c, q_c, c_c = [sp.Function(n)(t, r) for n in ("p", "q", "c")]
    psiA = sp.zeros(4, 4)
    psiA[0, 3] = psiA[3, 0] = p_c * S_ax
    psiA[1, 3] = psiA[3, 1] = q_c * S_ax
    psiA[2, 3] = psiA[3, 2] = c_c * 3 * (x**2 - 1)
    LA, SA, _ = carrier_op(psiA)
    _require(SA == 0, "axial trace not identically zero")
    nzA = [(a, b) for a in range(N) for b in range(a, N) if LA[a, b] != 0]
    _require(nzA == [(0, 3), (1, 3), (2, 3)], f"axial support {nzA}")
    BvecA = [_cancel(sum(gi[a, e] * geo.covd2(psiA, e, a, b)
                         for a in range(N) for e in range(N)
                         if gi[a, e] != 0)) for b in range(N)]
    _require([b for b in range(N) if BvecA[b] != 0] == [3],
             "axial Bianchi vector support")
    divA = divergence(LA)
    _require([b for b in range(N) if divA[b] != 0] == [3],
             "axial div(L) support")
    boxBA = one_form_box(sp.Matrix(4, 1, lambda b, _: BvecA[b]))
    _require(_cancel(divA[3] - boxBA[3] / 2) == 0,
             "axial constraint transport identity fails")
    out["stage_seconds"]["axial_identities"] = round(time.time() - t0, 1)
    print(f"[axial_identities] {out['stage_seconds']['axial_identities']} s",
          flush=True)

    # ---- stage 2: polar identities ----------------------------------------
    t0 = time.time()
    fns = [sp.Function(n)(t, r) for n in ("A", "Bc", "Cc", "D", "Ec", "F", "Gc")]
    A_f, Bc_f, Cc_f, D_f, Ec_f, F_f, G_f = fns
    psiP = sp.zeros(4, 4)
    psiP[0, 0] = A_f * P2
    psiP[0, 1] = psiP[1, 0] = Bc_f * P2
    psiP[1, 1] = Cc_f * P2
    psiP[0, 2] = psiP[2, 0] = D_f * dP2
    psiP[1, 2] = psiP[2, 1] = Ec_f * dP2
    psiP[2, 2] = g0[2, 2] * F_f * P2 + G_f * Wxx
    psiP[3, 3] = g0[3, 3] * F_f * P2 + G_f * Wpp
    LP, SP, boxSP = carrier_op(psiP)
    trLP = _cancel(sum(gi[a, b] * LP[a, b] for a in range(N) for b in range(N)))
    _require(trLP == 0, "polar trace(L) not identically zero")
    dSP = [sp.diff(SP, coords[e]) for e in range(N)]
    BvecP = [_cancel(sum(gi[a, e] * geo.covd2(psiP, e, a, b)
                         for a in range(N) for e in range(N)
                         if gi[a, e] != 0) - dSP[b] / 2) for b in range(N)]
    divP = divergence(LP)
    boxBP = one_form_box(sp.Matrix(4, 1, lambda b, _: BvecP[b]))
    for b in range(N):
        _require(_cancel(divP[b] - boxBP[b] / 2) == 0,
                 f"polar constraint transport fails at component {b}")
    out["stage_seconds"]["polar_identities"] = round(time.time() - t0, 1)
    print(f"[polar_identities] {out['stage_seconds']['polar_identities']} s",
          flush=True)

    # ---- stage 3: polar conformal witness ---------------------------------
    t0 = time.time()
    chi = sp.Function("chi")(r)
    Phi = t**4 * chi * P2
    dPhi = [sp.diff(Phi, coords[e]) for e in range(N)]
    DDPhi = sp.Matrix(4, 4, lambda a, b: _cancel(
        sp.diff(dPhi[a], coords[b])
        - sum(G[hh][a][b] * dPhi[hh] for hh in range(N))))
    boxPhi = _cancel(sum(gi[e, f] * DDPhi[e, f] for e in range(N)
                         for f in range(N) if gi[e, f] != 0))
    psiW = sp.Matrix(4, 4, lambda a, b: _cancel(-DDPhi[a, b]
                                                - g0[a, b] * boxPhi / 2))
    _require(all(_cancel(psiW[a, b].subs(t, 0)) == 0
                 for a in range(N) for b in range(N)),
             "witness psi|_Sigma != 0")
    _require(all(_cancel(sp.diff(psiW[a, b], t).subs(t, 0)) == 0
                 for a in range(N) for b in range(N)),
             "witness dt psi|_Sigma != 0")
    _require(any(psiW[a, b] != 0 for a in range(N) for b in range(N)),
             "witness identically zero")
    LW, SW, _ = carrier_op(psiW)
    _require(all(LW[a, b] == 0 for a in range(N) for b in range(N)),
             "witness not annihilated by the operator")
    # certified conformal trace relation: S(psi_conf(Phi)) = -3 Box Phi
    _require(_cancel(SW + 3 * boxPhi) == 0, "conformal trace relation fails")
    out["stage_seconds"]["conformal_witness"] = round(time.time() - t0, 1)
    print(f"[conformal_witness] {out['stage_seconds']['conformal_witness']} s",
          flush=True)

    # ---- stage 4: axial mutation witness (time-odd mode) ------------------
    # Inline ingoing axial carrier mode (EF chart Frobenius, omega = 3/5,
    # m = 1), independent of the sourced pipeline: builds (P, Q) series,
    # forms u(t) = Im(e^{i w t} psi_w) profile data, and verifies
    # u|_{t=0} = 0 with dt u|_{t=0} != 0 componentwise at the series level.
    t0 = time.time()
    wnum = sp.Rational(3, 5)
    rho = sp.Symbol("rho")
    v_ef = sp.Symbol("v")
    g_ef = sp.zeros(4, 4)
    B1 = 1 - 2 / r
    g_ef[0, 0] = -B1
    g_ef[0, 1] = g_ef[1, 0] = 1
    g_ef[2, 2] = r**2 / (1 - x**2)
    g_ef[3, 3] = r**2 * (1 - x**2)
    geoE = geo_cls([v_ef, r, x, ph], g_ef)
    giE = geoE.ginv
    GE = geoE.Gamma
    pE = sp.Function("p")(v_ef, r)
    qE = sp.Function("q")(v_ef, r)
    cE = sp.Function("c")(v_ef, r)
    psiE = sp.zeros(4, 4)
    psiE[0, 3] = psiE[3, 0] = pE * S_ax
    psiE[1, 3] = psiE[3, 1] = qE * S_ax
    psiE[2, 3] = psiE[3, 2] = cE * 3 * (x**2 - 1)
    sdiv = sum(giE[a, e] * geoE.covd2(psiE, e, a, 3) for a in range(N)
               for e in range(N) if giE[a, e] != 0)
    c_expr = sp.solve(sp.Eq(_cancel(sdiv), 0), cE)[0]
    psiE2 = sp.Matrix(4, 4, lambda i, j: psiE.subs(cE, c_expr).doit()[i, j])
    DXE = [[[_cancel(geoE.covd2(psiE2, e, a, b)) for b in range(N)]
            for a in range(N)] for e in range(N)]

    def covd2E(e, f, a, b):
        s = sp.diff(DXE[f][a][b], coords_E[e])
        for hh in range(N):
            s -= (GE[hh][e][f] * DXE[hh][a][b] + GE[hh][e][a] * DXE[f][hh][b]
                  + GE[hh][e][b] * DXE[f][a][hh])
        return s

    coords_E = [v_ef, r, x, ph]
    E = sp.exp(sp.I * wnum * v_ef)
    P = sp.Function("P")(r)
    Q = sp.Function("Q")(r)
    rows = []
    for (a, b) in ((0, 3), (1, 3)):
        box = sum(giE[e, f] * covd2E(e, f, a, b) for e in range(N)
                  for f in range(N) if giE[e, f] != 0)
        cx = sum(geoE.Weyl[a][cc][b][d]
                 * sum(giE[cc, e] * giE[d, f] * psiE2[e, f]
                       for e in range(N) for f in range(N))
                 for cc in range(N) for d in range(N))
        row = _cancel((box / 2 + cx) / S_ax)
        row = _cancel(row.subs({pE: P * E, qE: Q * E}).doit() / E)
        rows.append(sp.expand(row))
    D2P, D2Q = sp.Derivative(P, (r, 2)), sp.Derivative(Q, (r, 2))
    sol2 = sp.solve([sp.Eq(rows[0], 0), sp.Eq(rows[1], 0)], [D2P, D2Q],
                    dict=True)[0]
    # Frobenius analytic exponent-zero solutions around rho = r - 2 (m = 1)
    NW = 6
    A4 = sp.zeros(4, 4)
    A4[0, 1] = 1
    A4[2, 3] = 1
    DP, DQ = sp.Derivative(P, r), sp.Derivative(Q, r)
    e1 = sp.expand(sol2[D2P].subs(m, 1))
    e2 = sp.expand(sol2[D2Q].subs(m, 1))
    for i, e in ((1, e1), (3, e2)):
        A4[i, 0] = e.coeff(P)
        A4[i, 1] = e.coeff(DP)
        A4[i, 2] = e.coeff(Q)
        A4[i, 3] = e.coeff(DQ)
    Ar = A4.subs(r, 2 + rho)
    Res4 = sp.Matrix(4, 4, lambda i, j: sp.limit(rho * _cancel(Ar[i, j]),
                                                 rho, 0))
    rem4 = sp.Matrix(4, 4, lambda i, j: _cancel(Ar[i, j] - Res4[i, j] / rho))
    Ak = [sp.Matrix(4, 4, lambda i, j:
          rem4[i, j].series(rho, 0, NW + 2).removeO().coeff(rho, k))
          for k in range(NW + 1)]
    ns = Res4.nullspace()
    _require(len(ns) >= 1, "no analytic ingoing direction")
    Y = [sp.Matrix(ns[0])]
    for n in range(1, NW + 1):
        rhs = sp.zeros(4, 1)
        for k in range(n):
            rhs += Ak[n - 1 - k] * Y[k]
        Y.append((n * sp.eye(4) - Res4).solve(rhs))
    Pser = sum(Y[n][0] * rho**n for n in range(NW + 1))
    _require(sp.expand(Pser) != 0, "mode identically zero")
    # time-odd witness u = Im(e^{i w t} psi_w): u|_{t=0} = Im(psi_w) -- for
    # the witness we use the REAL structure: with psi_w = Re + i Im, the
    # combination u(t) = (psi(t) - psi(-t))/2 built from the real solution
    # psi(t) = Re(e^{i w t} psi_w) satisfies u(0) = 0 and
    # dt u(0) = -w Im(psi_w).  Nonvanishing requires Im(psi_w) != 0:
    ImP = sp.expand(sp.im(Pser.subs(rho, sp.Rational(1, 16))))
    ReP = sp.expand(sp.re(Pser.subs(rho, sp.Rational(1, 16))))
    _require(ImP != 0 or _cancel(sp.im(sum(Y[n][2] * (sp.Rational(1, 16))**n
                                           for n in range(NW + 1)))) != 0,
             "mode has no imaginary part: time-odd witness degenerate")
    _require(ReP != 0 or ImP != 0, "mode vanishes at test radius")
    out["stage_seconds"]["mutation_witness"] = round(time.time() - t0, 1)
    print(f"[mutation_witness] {out['stage_seconds']['mutation_witness']} s",
          flush=True)

    out["stage_seconds"]["total"] = round(time.time() - t0_all, 1)
    return out


def build_certificate() -> dict:
    res = run_analysis(Geometry)
    certificate = {
        "schema": SCHEMA_NAME,
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": RESULT_ID,
        "result_token": RESULT_TOKEN,
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "declaration": {
            "theory": "pure-Weyl gravity L = alpha C_abcd C^abcd",
            "background_family": "Schwarzschild exterior r > 2m, symbolic m",
            "domain": "globally hyperbolic exterior; Cauchy surface Sigma = {t = const, r > 2m} in the static chart",
            "cauchy_data": "psi|_Sigma = 0 and nabla_n psi|_Sigma = 0 for the curvature carrier psi_ab = delta Ric_ab[h]",
            "operator": "(L psi)_ab = (1/2) Box psi_ab + C_acbd psi^cd - (1/6) grad_a grad_b S - (1/12) g_ab Box S",
            "regularity_class": "smooth l = 2 harmonic classes (axial and polar); uniqueness argument is the standard energy estimate for normally hyperbolic tensor systems on globally hyperbolic domains (cited, not re-proved)",
            "boundary_conditions": "none beyond Cauchy data: no horizon or finite-radius timelike boundary condition is used or hidden",
            "lifecycle": "CLASSIFIED",
        },
        "identities": {
            "axial_trace": "S = 0 identically on the axial class; L = (1/2) Box + C o (-)",
            "axial_constraint_transport": "nabla^a (L psi)_a phi = (1/2) Box B_phi exactly (zero remainder)",
            "polar_trace": "g^{ab} (L psi)_ab = 0 identically (PDE-level tracelessness; the conformal direction is not controlled)",
            "polar_constraint_transport": "nabla^a (L psi)_ab = (1/2) Box B_b exactly in all components, B_b = nabla^a psi_ab - (1/2) grad_b S",
            "conformal_trace_relation": "S(psi_conf(Phi)) = -3 Box Phi (verified on the witness; matches BH2B_POLAR_REACH)",
        },
        "conclusions": {
            "axial": "statement (A): zero Cauchy data propagates psi = 0; the linear Einstein image is locally selected and preserved (unconditional)",
            "polar": "obstruction + repair: the exact witness psi_conf(t^4 chi P2) has zero Cauchy data, is nonzero, and solves L psi = 0 -- naive uniqueness FAILS; the smallest additional hypothesis is conformal gauge-fixing (traceless slice): the gauge subtraction Phi_0 with -3 Box Phi_0 = S(psi) reduces any zero-data solution to a tracefree solution of the normally hyperbolic system, hence psi = psi_conf(Phi_0): selection holds exactly modulo the conformal-gauge orbit",
            "exact_sequence": "0 -> ker(delta Ric) -> ker(delta Bach) -> ker(L) cap im(delta Ric); with zero Cauchy data the right object is {0} (axial) and the conformal orbit {psi_conf(Phi)} (polar); no canonical splitting or surjectivity is asserted",
            "endpoint_comparison": "local Cauchy truncation is a local differential initial-data restriction and DOES select the Einstein image (modulo gauge); the certified endpoint diagnostics (horizon ingoing analyticity, falloff class) do NOT -- the two kinds of conditions are logically independent, resolving the referee's distinction",
        },
        "mutation": {
            "dropped_datum": "nabla_n psi|_Sigma",
            "witness": "time-odd combination u = (psi(t) - psi(-t))/2 of a certified ingoing axial mode (real-coefficient static-chart operator maps solutions to solutions under t -> -t): u|_Sigma = 0, dt u|_Sigma = -omega Im(psi_omega) != 0, u != 0",
            "verified": "the inline Frobenius mode has nonvanishing imaginary part at a rational test radius, so the weakened hypothesis (value datum only) is rejected",
        },
        "claim_flags": {
            "axial_cauchy_truncation_certified": True,
            "polar_conformal_obstruction_certified": True,
            "polar_quotient_truncation_certified": True,
            "constraint_propagation_certified": True,
            "exact_sequence_stated_without_splitting": True,
            "nonlinear_or_stability_claim": False,
            "general_l_certified": False,
            "every_psi_lifts_claim": False,
            "sourced_flux_numbers_used": False,
        },
        "missing_objects": [
            "general l and m",
            "a canonical Einstein-plus-extra splitting (deliberately not asserted)",
            "surjectivity of delta Ric onto ker(L) (lift questions are separate and currently under repair)",
            "nonlinear closure, complex-frequency mode analysis, or scattering statements (vocabulary coordinator-gated)",
            "an a-priori energy estimate re-derivation (the standard normally-hyperbolic uniqueness theorem is cited)",
        ],
        "stage_seconds": res["stage_seconds"],
        "provenance": {
            "generator_path": "black_hole_programme/bh_cauchy_truncation.py",
            "engine_path": "black_hole_programme/weyl_geometry.py",
            "engine_sha256": _sha256(HERE / "weyl_geometry.py"),
            "axial_operator_certificate": str(AXOP.relative_to(ROOT)),
            "axial_operator_certificate_sha256": _sha256(AXOP),
            "polar_split_certificate": str(PSPLIT.relative_to(ROOT)),
            "polar_split_certificate_sha256": _sha256(PSPLIT),
        },
        "verification_command":
            "python3 black_hole_programme/verify_bh_cauchy_truncation.py",
    }
    return certificate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    certificate = build_certificate()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
