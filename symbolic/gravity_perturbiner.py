#!/usr/bin/env python3
"""Multi-wave perturbiner engine for Einstein-Weyl gravity (shared).

Engine: multi-wave perturbiner.  g = eta + sum_i lam_i eps^(i) e^{i p_i x}
with exact rational(-complex) momenta; every geometric quantity lives in
the 'wave algebra' (dict: subset of waves -> sparse tensor components),
where products automatically implement multilinear truncation and
d_mu -> i P_mu.  The on-shell n-point vertex is the lam_1...lam_n
coefficient of sqrt(-g)(c1 R + alpha Rmn^2 + beta R^2) at total momentum
zero.  Conventions follow gravity_engine.py: signature (+,-,-,-),
R_{mu kap} = d_nu Gam^nu_{mu kap} - d_kap Gam^nu_{mu nu} + GamGam,
alpha = -3 beta, M^2 = c1/alpha; here M = 1, c1 = -1, alpha = -1,
beta = 1/3 (overall c1 normalization is irrelevant for the checks).

G13a  Engine validation: the 2-point coefficient vanishes on shell for
      TT waves at p^2 = 0 AND p^2 = M^2 (both branches solve the
      linearized EW equations), and is nonzero off shell.
G13b  Ward identity at 3 points: gauge polarization
      eps = p (x) xi + xi (x) p on a massless leg gives zero amplitude
      with the other legs on shell (checked on M M h and M h h).
G13   ONE-M RULE at cubic order: A_3(M, h, h) = 0 for ALL 5 massive
      polarizations x all graviton helicity combinations at the
      physical decay point M(rest) -> h h  (p = M/2 (1,0,0,+-1)).
      This is the amplitude-level content of the Einstein-truncation
      lemma (Einstein metrics are Bach-flat: the Ricci-flat Einstein
      sector is an exact subsector, arXiv:1303.5781), the analogue of
      massive-graviton non-decay (arXiv:1607.03497).
G14a  A_3(MMM) at an exact rational-complex on-shell point: NONZERO
      (values reported; existence of the cubic self-coupling on shell,
      not implied by tr M^3 alone).
G14b  A_3(MMh) at an exact rational-complex on-shell point: NONZERO
      (minimal gravitational coupling of the massive eigenfield).
G14c  FACTORIZATION RESIDUE: at the s-channel pole P = p1 + p2,
      P^2 = M^2, the contraction
        r = A_3(M1 M2 M^a(P)) (G5^{-1})_{ab} A_3(M^b(-P) M3 h4)
      is NONZERO: the pole residue of MM -> Mh cannot be canceled by
      quartic contact terms, so the four-point amplitude is not
      identically zero and [(-1)^{N_M}, S] != 0 for the naive massive
      number parity (Krein conclusion kept conditional: other gradings
      or boundary null ideals are not excluded).
"""
import sympy as sp
from sympy.combinatorics import Permutation
from itertools import permutations

R = sp.Rational
I = sp.I
ETA = [1, -1, -1, -1]

# --------------------------- wave algebra ------------------------------------
# object: dict  frozenset(wave ids) -> dict  (idx tuple) -> sympy number
def wt_add(A, B):
    out = {k: dict(v) for k, v in A.items()}
    for k, v in B.items():
        d = out.setdefault(k, {})
        for i, x in v.items():
            d[i] = d.get(i, 0) + x
    return {k: {i: x for i, x in v.items() if x != 0}
            for k, v in out.items() if v}

def wt_scale(A, c):
    return {k: {i: c*x for i, x in v.items()} for k, v in A.items()}

def wt_mul(A, B):
    out = {}
    for ka, va in A.items():
        for kb, vb in B.items():
            if ka & kb:
                continue
            k = ka | kb
            d = out.setdefault(k, {})
            for ia, xa in va.items():
                for ib, xb in vb.items():
                    i = ia + ib
                    d[i] = d.get(i, 0) + xa*xb
    return out

def wt_contract(A, i1, i2):
    """contract two SAME-position indices (both lower or both upper) with
    the diagonal eta."""
    out = {}
    for k, v in A.items():
        d = out.setdefault(k, {})
        for idx, x in v.items():
            if idx[i1] != idx[i2]:
                continue
            nidx = tuple(m for j, m in enumerate(idx) if j not in (i1, i2))
            d[nidx] = d.get(nidx, 0) + ETA[idx[i1]]*x
    return {k: {i: x for i, x in v.items() if x != 0}
            for k, v in out.items() if v}

def wt_trace(A, i1, i2):
    """plain delta contraction of an UPPER index against a LOWER one."""
    out = {}
    for k, v in A.items():
        d = out.setdefault(k, {})
        for idx, x in v.items():
            if idx[i1] != idx[i2]:
                continue
            nidx = tuple(m for j, m in enumerate(idx) if j not in (i1, i2))
            d[nidx] = d.get(nidx, 0) + x
    return {k: {i: x for i, x in v.items() if x != 0}
            for k, v in out.items() if v}

def wt_deriv(A, P):
    """new FIRST index = derivative index: d_mu -> i (sum of wave momenta)."""
    out = {}
    for k, v in A.items():
        Pk = [sum(P[w][m] for w in k) for m in range(4)]
        d = out.setdefault(k, {})
        for idx, x in v.items():
            for m in range(4):
                if Pk[m] == 0:
                    continue
                d[(m,) + idx] = d.get((m,) + idx, 0) + sp.I*Pk[m]*x
    return {k: {i: x for i, x in v.items() if x != 0}
            for k, v in out.items() if v}

def comp(A, k, idx):
    return A.get(k, {}).get(idx, 0)

ID_ETA_LOW = {frozenset(): {(m, m): ETA[m] for m in range(4)}}
ID_ETA_UP = {frozenset(): {(m, m): ETA[m] for m in range(4)}}

def raise_idx(A, pos):
    """raise ONE index with eta (diagonal): multiply entries by sign."""
    return {k: {i: ETA[i[pos]]*x for i, x in v.items()} for k, v in A.items()}

def metric_objects(waves, P):
    """waves: list of eps (dict idx->val).  Returns g (lower), ginv (upper),
    sqrtg (scalar), all in the wave algebra."""
    h = {}
    for w, eps in enumerate(waves):
        h[frozenset({w})] = dict(eps)
    g = wt_add({k: dict(v) for k, v in ID_ETA_LOW.items()}, h)
    # h with both indices up
    hup = raise_idx(raise_idx(h, 0), 1)
    # ginv = eta - h^^ + h^^ o h^^ - ... (o = eta_{ab} contraction of the
    # two adjacent UPPER indices; Neumann series, auto-truncating)
    ginv = wt_add({k: dict(v) for k, v in ID_ETA_UP.items()},
                  wt_scale(hup, -1))
    t2 = wt_contract(wt_mul(hup, hup), 1, 2)
    ginv = wt_add(ginv, t2)
    t3 = wt_contract(wt_mul(t2, hup), 1, 2)
    ginv = wt_add(ginv, wt_scale(t3, -1))
    t4 = wt_contract(wt_mul(t3, hup), 1, 2)
    ginv = wt_add(ginv, t4)
    # det(g): permutation expansion in the algebra
    det = {}
    for perm in permutations(range(4)):
        sgn = Permutation(perm).signature()
        prod = None
        for r_, c_ in enumerate(perm):
            fac = {k: {(): v[(r_, c_)]} for k, v in g.items()
                   if (r_, c_) in v}
            prod = fac if prod is None else wt_mul(prod, fac)
            if not prod:
                break
        if prod:
            for k, v in prod.items():
                d = det.setdefault(k, {})
                d[()] = d.get((), 0) + sgn*v.get((), 0)
    # sqrt(-det): x = -det - 1;  sqrt(1+x) = 1 + x/2 - x^2/8 + x^3/16 - 5x^4/128
    x = wt_scale(det, -1)
    x = wt_add(x, {frozenset(): {(): -1}})
    x2 = wt_mul(x, x); x3 = wt_mul(x2, x); x4 = wt_mul(x3, x)
    sqrtg = wt_add({frozenset(): {(): 1}}, wt_scale(x, R(1, 2)))
    sqrtg = wt_add(sqrtg, wt_scale(x2, -R(1, 8)))
    sqrtg = wt_add(sqrtg, wt_scale(x3, R(1, 16)))
    sqrtg = wt_add(sqrtg, wt_scale(x4, -R(5, 128)))
    return g, ginv, sqrtg

def curvature(g, ginv, P):
    """Christoffels and Ricci in the wave algebra."""
    dg = wt_deriv(g, P)                          # (d, mu, nu)
    # Gam^lam_{mu nu} = 1/2 g^{lam rho}(dg_{mu rho nu} + dg_{nu rho mu}
    #                                    - dg_{rho mu nu})
    combo = {}
    for k, v in dg.items():
        d = combo.setdefault(k, {})
        for (a, b, c), x in v.items():
            # term d_mu g_{rho nu}: contributes to (rho; mu, nu) = (b; a, c)
            d[(b, a, c)] = d.get((b, a, c), 0) + x
            # term d_nu g_{rho mu}: (rho; mu, nu) = (b; c, a)
            d[(b, c, a)] = d.get((b, c, a), 0) + x
            # term -d_rho g_{mu nu}: (rho; mu, nu) = (a; b, c)
            d[(a, b, c)] = d.get((a, b, c), 0) - x
    combo = wt_scale(combo, R(1, 2))
    # contract ginv's second (upper) index with combo's first (lower) slot
    Gam = wt_trace(wt_mul(ginv, combo), 1, 2)      # (lam^, mu, nu)
    dGam = wt_deriv(Gam, P)                        # (d, lam, mu, nu)
    Ric = {}
    # d_nu Gam^nu_{mu kap} - d_kap Gam^nu_{mu nu}
    for k, v in dGam.items():
        d = Ric.setdefault(k, {})
        for (dd, lam, mu, nu), x in v.items():
            if dd == lam:
                d[(mu, nu)] = d.get((mu, nu), 0) + x
            if nu == lam:
                d[(mu, dd)] = d.get((mu, dd), 0) - x
    # + Gam^nu_{nu rho} Gam^rho_{mu kap} - Gam^nu_{kap rho} Gam^rho_{mu nu}
    GG = wt_mul(Gam, Gam)                          # (n1,m1,k1, n2,m2,k2)
    for k, v in GG.items():
        d = Ric.setdefault(k, {})
        for (n1, m1, k1, n2, m2, k2), x in v.items():
            if n1 == m1 and k1 == n2:
                d[(m2, k2)] = d.get((m2, k2), 0) + x
            if k1 == n2 and n1 == k2:              # -Gam^n_{kap rho}Gam^rho_{mu n}
                d[(m2, m1)] = d.get((m2, m1), 0) - x
    return {k: {i: x for i, x in v.items() if x != 0}
            for k, v in Ric.items() if v}

def densities(waves, P):
    """lam_1..lam_n coefficients of sqrt(-g) R, sqrt(-g) Rmn^2, sqrt(-g) R^2."""
    g, ginv, sqrtg = metric_objects(waves, P)
    Ric = curvature(g, ginv, P)
    # R = g^{ab} R_{ab}: plain traces (upper vs lower)
    Rsc = wt_trace(wt_trace(wt_mul(ginv, Ric), 0, 2), 0, 1)
    # R^a{}_n = g^{ad} R_{dn}
    RicUpHalf = wt_trace(wt_mul(ginv, Ric), 1, 2)
    # R^{cn} = g^{cd} R^n{}_d : plain trace of ginv's d (up) against
    # RicUpHalf's second slot (low); mul -> (c,d,n,dd), trace (1,3)
    RicUp = wt_trace(wt_mul(ginv, RicUpHalf), 1, 3)
    # Rmn^2 = R^{mn} R_{mn}: plain double trace
    Ric2 = wt_trace(wt_trace(wt_mul(RicUp, Ric), 0, 2), 0, 1)
    full = frozenset(range(len(waves)))
    def coeff(X):
        return comp(X, full, ())
    dR = coeff(wt_mul(sqrtg, Rsc))
    dR2 = coeff(wt_mul(sqrtg, wt_mul(Rsc, Rsc)))
    dRic2 = coeff(wt_mul(sqrtg, Ric2))
    return dR, dRic2, dR2

C1 = -1
ALPHA = -1          # M^2 = c1/alpha = 1
BETA = R(1, 3)      # alpha = -3 beta

def amplitude(waves, P):
    dR, dRic2, dR2 = densities(waves, P)
    return sp.simplify(C1*dR + ALPHA*dRic2 + BETA*dR2)

# --------------------------- kinematics helpers -------------------------------
def dot(a, b):
    return sum(ETA[m]*a[m]*b[m] for m in range(4))

def sym(a, b):
    return {(m, n): a[m]*b[n] + a[n]*b[m] for m in range(4) for n in range(4)}

def transverse_basis(p):
    """3 independent rational vectors e with e.p = 0 (works for complex p)."""
    row = sp.Matrix([[ETA[m]*p[m] for m in range(4)]])
    return [list(v) for v in row.nullspace()]

def massive_tt_basis(p):
    """5 independent TT tensors for p^2 = M^2 != 0, plus their Gram matrix."""
    es = transverse_basis(p)
    p2 = dot(p, p)
    Pi = {(m, n): (1 if m == n else 0)*ETA[m] - p[m]*p[n]/p2
          for m in range(4) for n in range(4)}
    cands = []
    for a in range(3):
        for b in range(a, 3):
            eab = dot(es[a], es[b])
            T = {}
            for m in range(4):
                for n in range(4):
                    T[(m, n)] = (es[a][m]*es[b][n] + es[b][m]*es[a][n]
                                 - R(2, 3)*eab*Pi[(m, n)])
            cands.append(T)
    def pair(X, Y):
        return sp.simplify(sum(ETA[m]*ETA[n]*X[(m, n)]*Y[(m, n)]
                               for m in range(4) for n in range(4)))
    # pick 5 with invertible Gram
    for drop in range(5, -1, -1):
        sel = [cands[i] for i in range(6) if i != drop]
        G5 = sp.Matrix(5, 5, lambda i, j: pair(sel[i], sel[j]))
        if G5.det() != 0:
            return sel, G5
    raise RuntimeError("no independent TT basis found")

def as_eps(T):
    return {(m, n): v for (m, n), v in T.items() if v != 0}

