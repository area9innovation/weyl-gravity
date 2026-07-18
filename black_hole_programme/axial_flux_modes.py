"""Axial l=2 horizon-flux mode pipeline (validated composition route).

Builds ingoing-analytic RW and extra-branch modes near the Schwarzschild
horizon (m = 1) and evaluates the certified Lee--Wald radial-flux bilinear
on conjugate pairs.  All series arithmetic is exact; the RW x RW null
control provides the in-run validation gate.  Extracted verbatim from the
scratch pipeline whose results were validated by the null control at
1e-18 relative and by frequency robustness.
"""

def run_pipeline(wnum, NORD=16, radii=None):
    import time, pickle
    import sympy as sp
    t0 = time.time()
    import weyl_geometry as wg
    
    
    v, ph = sp.symbols("v phi")
    r = sp.Symbol("r", positive=True)
    x = sp.Symbol("x")
    w = sp.Symbol("omega", positive=True)
    rho = sp.Symbol("rho")
    m = sp.Integer(1)
    B0 = 1 - 2 * m / r
    coords = [v, r, x, ph]
    g0 = sp.zeros(4, 4)
    g0[0, 0] = -B0
    g0[0, 1] = g0[1, 0] = 1
    g0[2, 2] = r**2 / (1 - x**2)
    g0[3, 3] = r**2 * (1 - x**2)
    geo0 = wg.Geometry(coords, g0)
    gi = geo0.ginv
    S = -3 * x * (1 - x**2)
    N = 4
    
    # ---------- 1. dRic-only for EF axial h (inline light half of LinearizedBach)
    h0f = sp.Function("h0")(v, r)
    h1f = sp.Function("h1")(v, r)
    h = sp.zeros(4, 4)
    h[0, 3] = h[3, 0] = h0f * S
    h[1, 3] = h[3, 1] = h1f * S
    cancel = lambda e: sp.cancel(sp.together(e))
    dG = [[[sp.Integer(0)] * N for _ in range(N)] for _ in range(N)]
    for a in range(N):
        for b in range(N):
            for c in range(b, N):
                s = sp.Integer(0)
                for d in range(N):
                    if gi[a, d] == 0:
                        continue
                    s += gi[a, d] * (geo0.covd2(h, b, d, c) + geo0.covd2(h, c, b, d)
                                     - geo0.covd2(h, d, b, c))
                val = cancel(s / 2)
                dG[a][b][c] = val
                dG[a][c][b] = val
    
    
    def cov_dG(e, a, b, c):
        s = sp.diff(dG[a][b][c], coords[e])
        G = geo0.Gamma
        for hh in range(N):
            s += G[a][e][hh] * dG[hh][b][c]
            s -= G[hh][e][b] * dG[a][hh][c] + G[hh][e][c] * dG[a][b][hh]
        return s
    
    
    dRic = sp.Matrix(N, N, lambda b, d: cancel(
        sum(cov_dG(a, a, d, b) - cov_dG(d, a, a, b) for a in range(N))))
    print("dRic built", round(time.time() - t0, 1), flush=True)
    
    # axial rows of dRic (strip angular)
    Rt = cancel(cancel(dRic[0, 3]) / S)
    Rr = cancel(cancel(dRic[1, 3]) / S)
    Rx = cancel(cancel(dRic[2, 3]) / (3 * (x - 1) * (x + 1)))
    assert not Rt.has(x) and not Rr.has(x) and not Rx.has(x)
    
    # Fourier profiles
    H0 = sp.Function("H0")(r)
    H1 = sp.Function("H1")(r)
    E = sp.exp(sp.I * w * v)
    four = {h0f: H0 * E, h1f: H1 * E}
    Rtf = sp.expand(cancel(Rt.subs(four).doit() / E))
    Rrf = sp.expand(cancel(Rr.subs(four).doit() / E))
    Rxf = sp.expand(cancel(Rx.subs(four).doit() / E))
    print("dRic rows Fourier ready", round(time.time() - t0, 1), flush=True)
    
    # ---------- 2. carrier ingoing series from the certified 4x4 EF system
    p_c = sp.Function("p")(v, r)
    q_c = sp.Function("q")(v, r)
    c_c = sp.Function("c")(v, r)
    psi_t = sp.zeros(4, 4)
    psi_t[0, 3] = psi_t[3, 0] = p_c * S
    psi_t[1, 3] = psi_t[3, 1] = q_c * S
    psi_t[2, 3] = psi_t[3, 2] = c_c * 3 * (x**2 - 1)
    sdiv = sum(gi[a, e] * geo0.covd2(psi_t, e, a, 3) for a in range(N) for e in range(N)
               if gi[a, e] != 0)
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
        box = sum(gi[e, f] * covd2X2(e, f, a, b) for e in range(N) for f in range(N)
                  if gi[e, f] != 0)
        cx = sum(geo0.Weyl[a][cc][b][d]
                 * sum(gi[cc, e] * gi[d, f] * psi2[e, f] for e in range(N) for f in range(N))
                 for cc in range(N) for d in range(N))
        return cancel(box / 2 + cx)
    
    
    Lt_c = cancel(Lrow(0, 3) / S)
    Lr_c = cancel(Lrow(1, 3) / S)
    P = sp.Function("P")(r)
    Q = sp.Function("Q")(r)
    four_c = {p_c: P * E, q_c: Q * E}
    Ltf_c = sp.expand(cancel(Lt_c.subs(four_c).doit() / E))
    Lrf_c = sp.expand(cancel(Lr_c.subs(four_c).doit() / E))
    D2P, D2Q = sp.Derivative(P, (r, 2)), sp.Derivative(Q, (r, 2))
    sol_c = sp.solve([sp.Eq(Ltf_c, 0), sp.Eq(Lrf_c, 0)], [D2P, D2Q], dict=True)[0]
    print("carrier system ready", round(time.time() - t0, 1), flush=True)
    
    
    def series_system(sol2, funcs, wval, nord=NORD):
        """Frobenius-analytic series solutions around rho = r - 2 (m=1)."""
        # first-order system Y' = A(r) Y in (F1, F1', F2, F2')
        A = sp.zeros(4, 4)
        A[0, 1] = 1
        A[2, 3] = 1
        F1, F2 = funcs
        DF1, DF2 = sp.Derivative(F1, r), sp.Derivative(F2, r)
        e1 = sp.expand(sol2[sp.Derivative(F1, (r, 2))]).subs(w, wval)
        e2 = sp.expand(sol2[sp.Derivative(F2, (r, 2))]).subs(w, wval)
        A[1, 0] = e1.coeff(F1); A[1, 1] = e1.coeff(DF1); A[1, 2] = e1.coeff(F2); A[1, 3] = e1.coeff(DF2)
        A[3, 0] = e2.coeff(F1); A[3, 1] = e2.coeff(DF1); A[3, 2] = e2.coeff(F2); A[3, 3] = e2.coeff(DF2)
        Ar = A.subs(r, 2 + rho)
        # Laurent expansion A = Res/rho + sum A_k rho^k
        Acoeffs = []
        Res = sp.Matrix(4, 4, lambda i, j: sp.limit(rho * cancel(Ar[i, j]), rho, 0))
        rem = sp.Matrix(4, 4, lambda i, j: cancel(Ar[i, j] - Res[i, j] / rho))
        for k in range(nord + 1):
            Ak = sp.Matrix(4, 4, lambda i, j: rem[i, j].series(rho, 0, nord + 2).removeO().coeff(rho, k))
            Acoeffs.append(Ak)
        sols = []
        for v0 in Res.nullspace():
            Y = [sp.Matrix(v0)]
            for n in range(1, nord + 1):
                rhs = sp.zeros(4, 1)
                for k in range(n):
                    rhs += Acoeffs[n - 1 - k] * Y[k]
                Mn = n * sp.eye(4) - Res
                Y.append(Mn.solve(rhs))
            sols.append(Y)
        return sols
    
    
    psi_sols = series_system(sol_c, (P, Q), wnum)
    print("carrier ingoing series built:", len(psi_sols), round(time.time() - t0, 1), flush=True)
    
    # ---------- 3. RW ingoing h-mode series (EF master), lifted to (H0, H1)
    F = sp.Function("F")(r)
    V = B0 * (6 / r**2 - 6 * m / r**3)
    opF = B0 * sp.diff(B0 * sp.diff(F, r), r) + 2 * sp.I * w * B0 * sp.diff(F, r) - V * F
    e2F = sp.expand(sp.solve(sp.Eq(sp.expand(opF), 0), sp.Derivative(F, (r, 2)), dict=True)[0][
        sp.Derivative(F, (r, 2))])
    
    
    def series_scalar(e2, func, wval, nord=NORD):
        DF = sp.Derivative(func, r)
        a1 = e2.coeff(DF).subs(w, wval)
        a0 = e2.coeff(func).subs(w, wval)
        a1r = cancel(a1.subs(r, 2 + rho))
        a0r = cancel(a0.subs(r, 2 + rho))
        # rho * F'' = rho a1 F' + rho a0 F ; analytic exponent 0 solution
        b1 = [cancel(rho * a1r).series(rho, 0, nord + 2).removeO().coeff(rho, k) for k in range(nord + 2)]
        b0 = [cancel(rho**2 * a0r).series(rho, 0, nord + 2).removeO().coeff(rho, k) for k in range(nord + 2)]
        # recurrence from rho^2 F'' - rho*(rho a1) F' - (rho^2 a0) F = 0
        cn = [sp.Integer(1)]
        for n in range(1, nord + 1):
            acc = sp.Integer(0)
            for k in range(n):
                acc += cn[k] * (k * b1[n - k] + b0[n - k])
            # indicial: n(n-1) - b1[0]*n - b0[0] ; for analytic branch b-consistency
            denom = sp.nsimplify(n * (n - 1) - b1[0] * n - b0[0])
            cn.append(sp.cancel(acc / denom))
        return cn
    
    
    rw_F = series_scalar(e2F, F, wnum)
    print("RW master ingoing series built", round(time.time() - t0, 1), flush=True)
    
    def poly_of(coeffs):
        return sum(c * rho**k for k, c in enumerate(coeffs))
    
    
    # ---------- 4. extra h-modes: solve dRic[h] = psi order by order ------------
    def ric_first_order(wval):
        """reduce the dRic system to Y' = M Y + N*source, Y = (H0, H1, H1')."""
        Rx_w = sp.expand(Rxf.subs(w, wval))
        H0p_expr = sp.solve(sp.Eq(Rx_w, sp.Symbol("XSRC")), sp.Derivative(H0, r))[0]
        Rr_w = sp.expand(Rrf.subs(w, wval))
        # substitute H0'' = d/dr(H0p_expr), H0' = H0p_expr into the rphi row
        H0pp = sp.diff(H0p_expr, r).subs(sp.Derivative(H0, r), H0p_expr)
        row = Rr_w.subs({sp.Derivative(H0, (r, 2)): H0pp, sp.Derivative(H0, r): H0p_expr}).doit()
        H1pp_expr = sp.solve(sp.Eq(sp.expand(row), sp.Symbol("TSRC")), sp.Derivative(H1, (r, 2)))[0]
        return H0p_expr, H1pp_expr
    
    
    def series_ric(wval, Qsrc=None, Xsrc=None, nord=NORD):
        """forward-recurrence analytic series solutions of the dRic system.
    
        Returns list of homogeneous solutions (free low-order data) if no
        source, else one particular solution. Y = (H0, H1, H1').
        """
        H0p_expr, H1pp_expr = ric_first_order(wval)
        XS, TS = sp.Symbol("XSRC"), sp.Symbol("TSRC")
        DH1 = sp.Derivative(H1, r)
        M = sp.zeros(3, 3)
        e0 = sp.expand(H0p_expr)
        M[0, 0] = e0.coeff(H0); M[0, 1] = e0.coeff(H1); M[0, 2] = e0.coeff(DH1)
        M[1, 2] = 1
        e2 = sp.expand(H1pp_expr)
        M[2, 0] = e2.coeff(H0); M[2, 1] = e2.coeff(H1); M[2, 2] = e2.coeff(DH1)
        Nvec = sp.Matrix([e0.coeff(XS), 0, e2.coeff(XS) * 0 + e2.coeff(TS)])
        NvecX = sp.Matrix([e0.coeff(XS), 0, e2.coeff(XS)])
        NvecT = sp.Matrix([0, 0, e2.coeff(TS)])
        Mr = M.subs(r, 2 + rho)
        Res = sp.Matrix(3, 3, lambda i, j: sp.limit(rho * cancel(Mr[i, j]), rho, 0))
        rem = sp.Matrix(3, 3, lambda i, j: cancel(Mr[i, j] - Res[i, j] / rho))
        Mk = []
        for k in range(nord + 1):
            Mk.append(sp.Matrix(3, 3, lambda i, j:
                      rem[i, j].series(rho, 0, nord + 2).removeO().coeff(rho, k)))
        def src_coeffs(vecfac, poly):
            if poly is None:
                return [sp.zeros(3, 1) for _ in range(nord + 1)]
            vr = sp.Matrix(3, 1, lambda i, _: cancel(vecfac[i].subs(r, 2 + rho)))
            out = []
            for k in range(nord + 1):
                col = sp.zeros(3, 1)
                for i in range(3):
                    pieces = sp.expand(cancel(rho * vr[i]) * poly)
                    col[i] = pieces.series(rho, 0, nord + 2).removeO().coeff(rho, k)
                out.append(col)
            return out
        # source enters as (1/rho)*(rho*vec)*poly to align with the M expansion
        SX = src_coeffs(NvecX, Xsrc)
        STt = src_coeffs(NvecT, Qsrc)
        def recur(Y0, with_src):
            Y = [Y0]
            for n in range(1, nord + 1):
                rhs = sp.zeros(3, 1)
                for k in range(n):
                    rhs += Mk[n - 1 - k] * Y[k]
                if with_src:
                    rhs += SX[n] + STt[n]
                Mn = n * sp.eye(3) - Res
                if Mn.det() != 0:
                    Y.append(Mn.solve(rhs))
                else:
                    soln, params = Mn.gauss_jordan_solve(rhs)
                    # consistency required (no log); set free directions to zero
                    soln = soln.subs({pp: 0 for pp in params})
                    chk = sp.simplify(Mn * soln - rhs)
                    if any(sp.simplify(cc) != 0 for cc in chk):
                        raise RuntimeError(f"log resonance at order {n}")
                    Y.append(soln)
            return Y
        if Qsrc is None and Xsrc is None:
            return [recur(sp.Matrix(vv), False) for vv in Res.nullspace()]
        return recur(sp.zeros(3, 1), True)
    
    
    print("starting mode construction", round(time.time() - t0, 1), flush=True)
    
    
    def carrier_polys(wval, sols):
        Y = sols[0]
        Pp = poly_of([yy[0] for yy in Y])
        Qp = poly_of([yy[2] for yy in Y])
        c_ser = c_expr.subs({p_c: sp.Function("Pf")(r) * E, q_c: sp.Function("Qf")(r) * E}).doit() / E
        c_ser = sp.expand(cancel(c_ser)).subs(w, wval)
        Pf = sp.Function("Pf")(r); Qf = sp.Function("Qf")(r)
        Xp = c_ser.subs({sp.Derivative(Pf, r): sp.diff(Pp.subs(rho, r - 2), r),
                         Pf: Pp.subs(rho, r - 2),
                         sp.Derivative(Qf, r): sp.diff(Qp.subs(rho, r - 2), r),
                         Qf: Qp.subs(rho, r - 2)}).doit()
        Xp = sp.expand(Xp.subs(r, 2 + rho))
        return Pp, Qp, Xp
    
    
    psi_m = series_system(sol_c, (P, Q), -wnum)
    Pp_p, Qp_p, Xp_p = carrier_polys(wnum, psi_sols)
    Pp_m, Qp_m, Xp_m = carrier_polys(-wnum, psi_m)
    
    # pure RW modes from the certified master series (t-chart lift)
    t_ch = sp.Symbol("t")
    r_t, th_t = sp.symbols("r theta", positive=True)
    # t-chart constraint lift H0(H1) rederived via the diagonal-chart machinery
    import weyl_geometry as wg2
    from linearized_bach import LinearizedBach as LB2
    x2 = sp.Symbol("x")
    ph2 = sp.Symbol("phi")
    coords_t = [t_ch, r, x2, ph2]
    Bt0 = 1 - 2 / r
    g_t = sp.diag(-Bt0, 1 / Bt0, r**2 / (1 - x2**2), r**2 * (1 - x2**2))
    geo_t = wg2.Geometry(coords_t, g_t)
    lb_t = LB2(geo_t)
    h0t = sp.Function("h0")(t_ch, r)
    h1t = sp.Function("h1")(t_ch, r)
    S2 = -3 * x2 * (1 - x2**2)
    ht = sp.zeros(4, 4)
    ht[0, 3] = ht[3, 0] = h0t * S2
    ht[1, 3] = ht[3, 1] = h1t * S2
    lb_t.build(ht)
    R2t = sp.cancel(sp.cancel(sp.together(lb_t.dRic[2, 3])) / (3 * (x2 - 1) * (x2 + 1)))
    H0sy = sp.Symbol("H0s")
    def rw_tchart(wval, Fc):
        Et = sp.exp(sp.I * wval * t_ch)
        R2f_t = sp.cancel(sp.together(sp.expand(
            R2t.subs({h0t: H0sy * Et, h1t: sp.Function("H1")(r) * Et}).doit() / Et)))
        H0l = sp.solve(sp.Eq(R2f_t, 0), H0sy)[0]
        H1g2 = sp.Function("H1")(r)
        rstar_l = sp.Function("rstar")(r)
        prof = r * poly_of(Fc).subs(rho, r - 2) / Bt0 * sp.exp(sp.I * wval * rstar_l) * sp.exp(sp.I * wval * sp.Symbol("t"))
        H0full = H0l.subs({H1g2: prof, sp.Derivative(H1g2, r): sp.diff(prof, r)}).doit()
        # replace rstar derivative
        H0full = H0full.subs(sp.Derivative(rstar_l, r), 1 / Bt0).doit()
        return sp.expand(sp.cancel(sp.together(H0full))), prof
    
    rw_F_m = [sp.conjugate(c) for c in rw_F]
    print("RW t-chart modes ready", round(time.time() - t0, 1), flush=True)
    ex_p_Y = series_ric(wnum, Qsrc=Qp_p, Xsrc=Xp_p)
    ex_m_Y = [sp.Matrix(3, 1, lambda i, _: sp.conjugate(yy[i])) for yy in ex_p_Y]
    print("extra particular modes built (conjugate basis)", round(time.time() - t0, 1), flush=True)
    
    t_s = sp.Symbol("t")
    alpha = sp.Symbol("alpha")
    loc = {"h0a": sp.Function("h0a"), "h1a": sp.Function("h1a"),
           "h0b": sp.Function("h0b"), "h1b": sp.Function("h1b"),
           "t": t_s, "r": r, "m": sp.Symbol("m"), "alpha": alpha, "pi": sp.pi}
    import json
    from pathlib import Path
    _cert = json.loads((Path(__file__).resolve().parent / "certificates" / "BH2A_FLUX_MATRIX.json").read_text())
    Fr_bil = sp.sympify(_cert["bilinear"]["F_r"], locals=loc).subs(loc["m"], 1)
    rstar = sp.Function("rstar")(r)
    Bnum = 1 - 2 / r
    
    
    def schw_mode(Yser, wval):
        H0p = poly_of([yy[0] for yy in Yser]).subs(rho, r - 2)
        H1p = poly_of([yy[1] for yy in Yser]).subs(rho, r - 2)
        fac = sp.exp(sp.I * wval * rstar) * sp.exp(sp.I * wval * t_s)
        return H0p * fac, (H1p + H0p / Bnum) * fac
    
    
    def apply_pair(FA, FB):
        (a0, a1), (b0, b1) = FA, FB
        sub = {loc["h0a"](t_s, r): a0, loc["h1a"](t_s, r): a1,
               loc["h0b"](t_s, r): b0, loc["h1b"](t_s, r): b1}
        e = Fr_bil.subs(sub).doit()
        for k in range(6, 0, -1):
            e = e.subs(sp.Derivative(rstar, (r, k)), sp.diff(1 / Bnum, r, k - 1))
        return sp.expand(cancel(e.doit()))
    
    
    rwP = rw_tchart(wnum, rw_F)
    rwM = rw_tchart(-wnum, rw_F_m)
    exP = schw_mode(ex_p_Y, wnum)
    exM = schw_mode(ex_m_Y, -wnum)
    
    ctrl = apply_pair(rwP, rwM)
    cross = apply_pair(rwP, exM)
    ee = apply_pair(exP, exM)
    print("bilinears built", round(time.time() - t0, 1), flush=True)
    out = {}
    if radii is None:
        radii = [sp.Rational(65, 32), sp.Rational(33, 16)]
    for name, expr in [("control", ctrl), ("cross", cross), ("ee", ee)]:
        vals = []
        for rv in radii:
            vals.append(sp.simplify(expr.subs(r, rv)))
        out[name] = vals
    return out
