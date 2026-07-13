#!/usr/bin/env python3
"""Interaction-deformation program, step 8 (2026-07-13): the doubled /
Krein structure of the perfect-square theory -- machine verification of
the team's step-9 program (mirror-adjoint relation, paired
pseudo-unitarity, Ward identity) plus the ghost-parity decomposition of
the on-shell obstruction.  Runtime ~4 min.

FRAMING (post literature audit): the two-field O(1,1) embedding, the
exchange U <-> V as ghost parity / charge conjugation, and the Krein
Born rule are Bateman-Turok (arXiv:2607.00096).  What is verified here
is (a) that the "doubled pairing" formulas are EXACTLY a two-sector
representation of that Krein structure -- not a new theory -- and
(b) where the paper-5 positive-metric obstruction sits inside it.

Structural checks (classical / finite-dimensional):
DQ1  Hyperbolic-polar form.  U = sqrt(r) e^chi, V = sqrt(r) e^-chi has
     unit-modulus Jacobian (det = -1) and
       L = -dU.dV + (g/2)U^2V^2
         = -(1/4r)(dr)^2 + r (dchi)^2 + (g/2) r^2;
     the field-space metric -2 dU dV = -dr^2/(2r) + 2r dchi^2 has
     det = -1.  (A coordinate presentation of the BT O(1,1) model:
     boost = chi-shift, exchange = chi -> -chi.)
DQ2  Noether current.  j = V dU - U dV = 2r dchi; d.j = 0 exactly on
     the equations of motion of the full theory; the exchange flips j
     (charge conjugation for the internal O(1,1) charge, as in BT).
DQ3  Adjoint-mirror => conserved doubled pairing.  If
     H_B = W H_A^dag W^dag then eta_dbl = offdiag(W^dag, W) satisfies
     H_dbl^dag eta = eta H_dbl.  Jordan model: J_B = P J_A P = J_A^dag,
     so W = I works (the SO2 model is the W = I case).
DQ4  Null structure.  <Psi, Psi>_eta = 2 Re <psi_B, W psi_A>;
     single-sector states are eta-null; an eigenstate with genuinely
     complex E is eta-self-null ((E - E*) <psi, eta psi> = 0).
DQ5  Graph theorem (standard Krein operator theory, instantiated).
     A positive H_dbl-invariant graph subspace {(psi, W G psi)} exists
     iff a positive pointed metric G exists (H_A^dag G = G H_A, G > 0):
     both directions verified on random instances.  Doubling does NOT
     evade the pointed obstruction.
DQ6  Paired pseudo-unitarity is EXACT at finite time.  For any
     H_B = W H_A^dag W^dag with [W, H0] = 0, the interaction-picture
     S_X(t) = e^{iH0 t} e^{-2iH_X t} e^{iH0 t} satisfies
       S_B(t)^dag W S_A(t) = W
     identically (machine precision, random 8-dim models, several t);
     equivalently i(W T_A - T_B^dag W) + T_B^dag W T_A = 0 with
     T = (S-1)/i.  This is a REPRESENTATION of Krein pseudo-unitarity
     (BT), not a new optical theorem.

Field-theory checks (perfect-square sectors, exact rational point
m_L = 4, m_H = 6, K = {-3, 0, 3}, g = 1, conventions of
verify_sector_obstruction.py / verify_hardening.py HX1):
DQ7  Mirror-adjoint relation -- team step 9A.  With the naive kappa
     identification iota: (b,k)_B ~ (b,k)_A of mirror Fock spaces and
     G = (-1)^{N_ghost} (ghost-branch number parity):
       (a) H3_B = H3_A and H4_B = H4_A as operators under iota
           (kappa is an exact symmetry: the mirror sector is the same
           theory in the mirrored frame);
       (b) H3_A^dag = G H3_A G and H4_A^dag = G H4_A G exactly
           (the pointed positive-frame Hamiltonian is pseudo-Hermitian
           w.r.t. ghost parity -- Krein self-adjointness);
       (c) hence H_B = W H_A^dag W^dag holds EXACTLY with
           W = iota o G.  The mirror-adjoint relation is not new
           structure: it is precisely Krein pseudo-Hermiticity, and
           the doubled pairing eta_dbl = offdiag(W^dag, W) is the
           two-sector unfolding of the BT fundamental symmetry kappa.
DQ8  Paired identity on the obstructed shell -- team step 9B -- and
     ghost-parity decomposition of the obstruction (steps 3-5 of the
     reconciliation program, pointed frame).  On the degenerate shell
     {|H(0)L(0)>, |L(3)L(-3)>} at E = 10 (exhaustively verified to be
     the whole reachable shell; H3 has no on-shell first-order
     elements), the full 2x2 second-order on-shell T matrices satisfy,
     EXACTLY in radicals:
       (a) T_B = T_A under iota;
       (b) W T_A = T_B^dag W, i.e. G T_A G = T_A^dag:
           the on-shell T is exactly ghost-parity (Krein)
           pseudo-Hermitian even though it is NOT Hilbert-Hermitian;
       (c) the source element conj(T_A(in,out)) - T_A(out,in)
           = 401 sqrt(6)/39424 (independent recomputation of the HX1
           obstruction from plain T elements: T_A(out,in)
           = -401 sqrt(6)/78848, T_A(in,out) = +401 sqrt(6)/78848);
       (d) the diagonal (ghost-parity-even) block is real (Hermitian);
           the entire obstruction lives in the ghost-parity-ODD
           (parity-changing, G_in G_out = -1) block.
     CONCLUSION: the positive-metric obstruction is carried exactly by
     the kappa-odd component of the on-shell T -- the component that
     BT's weak-ghost-symmetry positivity mechanism does not use.  The
     pointed positive completion fails while Krein pseudo-unitarity
     holds exactly, on the same matrix elements.  (The remaining
     BT-faithful step -- transporting through their R_t and testing
     membership in the null C component -- needs their embedding and
     is queued.)
DQ9  Ward identity -- team step 9C, classical/regulated.  Unregulated
     pointed theory: d.j = 0 exactly on-shell (affine current
     j = v du - (1+u) dv).  Regulated theory (mu^2 uv IR mass +
     (eps/2)u^2 regulator): the breaking is EXACTLY
       d.j = eps u(1+u) - mu^2 v,
     i.e. explicit regulator terms only, vanishing as (eps, mu) -> 0;
     the interaction terms cancel identically at all orders.  The
     transformation is linear in (U,V) with unit Jacobian (DQ1/SO3):
     no measure factor.  A normal-ordered operator check of
     [H, Q] = (breaking) on the Fock truncation is left as a queued
     item (conventions for the charge's linear piece need care).
"""
import numpy as np
import sympy as sp
from itertools import product, combinations_with_replacement
from collections import defaultdict

PASS = True
def check(msg, ok):
    global PASS
    print(("[OK ] " if ok else "[FAIL] ") + msg)
    PASS = PASS and bool(ok)

rng = np.random.default_rng(20260713)

# ------------------------------- DQ1 -----------------------------------------
t_, z_ = sp.symbols("t z")
g_ = sp.Symbol("g", positive=True)
r_ = sp.Function("r", positive=True)(t_, z_)
ch = sp.Function("chi")(t_, z_)
def dsq(f, h):
    return sp.diff(f, t_)*sp.diff(h, t_) - sp.diff(f, z_)*sp.diff(h, z_)
U_ = sp.sqrt(r_)*sp.exp(ch); V_ = sp.sqrt(r_)*sp.exp(-ch)
L_UV = -dsq(U_, V_) + g_/2*U_**2*V_**2
L_rc = -dsq(r_, r_)/(4*r_) + r_*dsq(ch, ch) + g_/2*r_**2
rs, cs = sp.symbols("rs cs", positive=True)
Us = sp.sqrt(rs)*sp.exp(cs); Vs = sp.sqrt(rs)*sp.exp(-cs)
Jac = sp.Matrix([[sp.diff(Us, rs), sp.diff(Us, cs)],
                 [sp.diff(Vs, rs), sp.diff(Vs, cs)]])
dr, dc = sp.symbols("dr dchi")
dU = sp.diff(Us, rs)*dr + sp.diff(Us, cs)*dc
dV = sp.diff(Vs, rs)*dr + sp.diff(Vs, cs)*dc
ds2 = sp.expand(-2*dU*dV)
gmat = sp.Matrix([[ds2.coeff(dr, 2), ds2.coeff(dr).coeff(dc)/2],
                  [ds2.coeff(dr).coeff(dc)/2, ds2.coeff(dc, 2)]])
check("DQ1: U = sqrt(r)e^chi, V = sqrt(r)e^-chi gives L = -(1/4r)(dr)^2 "
      "+ r(dchi)^2 + (g/2)r^2, Jacobian det = -1, field-space metric "
      "-dr^2/(2r) + 2r dchi^2 with det = -1",
      sp.simplify(L_UV - L_rc) == 0
      and sp.simplify(Jac.det() + 1) == 0
      and sp.simplify(gmat - sp.Matrix([[-1/(2*rs), 0], [0, 2*rs]]))
          == sp.zeros(2, 2)
      and sp.simplify(gmat.det() + 1) == 0)

# ------------------------------- DQ2 -----------------------------------------
Uf = sp.Function("U")(t_, z_); Vf = sp.Function("V")(t_, z_)
box = lambda f: sp.diff(f, t_, 2) - sp.diff(f, z_, 2)
# EL of L = -dU.dV + (g/2)U^2V^2:  box V = -g U V^2,  box U = -g U^2 V
jmu = [Vf*sp.diff(Uf, x) - Uf*sp.diff(Vf, x) for x in (t_, z_)]
divj = sp.diff(jmu[0], t_) - sp.diff(jmu[1], z_)          # d.j = V boxU - U boxV
divj_onshell = divj.subs({
    sp.diff(Uf, t_, 2): sp.diff(Uf, z_, 2) - g_*Uf**2*Vf,
    sp.diff(Vf, t_, 2): sp.diff(Vf, z_, 2) - g_*Uf*Vf**2})
# j = 2 r dchi in polar variables
j_pol = [(Vf*sp.diff(Uf, x) - Uf*sp.diff(Vf, x)).subs(
            {Uf: U_, Vf: V_}, simultaneous=True).doit() for x in (t_, z_)]
check("DQ2: d.j = 0 exactly on shell for j = V dU - U dV; j = 2r dchi; "
      "exchange U <-> V flips j (internal charge conjugation)",
      sp.simplify(divj_onshell) == 0
      and all(sp.simplify(jp - 2*r_*sp.diff(ch, x)) == 0
              for jp, x in zip(j_pol, (t_, z_)))
      and sp.simplify(jmu[0].subs({Uf: Vf, Vf: Uf}, simultaneous=True)
                      + jmu[0]) == 0)

# ------------------------------- DQ3 -----------------------------------------
def rand_c(n, m=None):
    m = m or n
    return rng.standard_normal((n, m)) + 1j*rng.standard_normal((n, m))
def rand_unitary(n):
    q, _ = np.linalg.qr(rand_c(n))
    return q
n = 5
HA = rand_c(n); W = rand_unitary(n)
HB = W @ HA.conj().T @ W.conj().T
Hdbl = np.block([[HA, np.zeros((n, n))], [np.zeros((n, n)), HB]])
eta = np.block([[np.zeros((n, n)), W.conj().T], [W, np.zeros((n, n))]])
w_ = sp.Symbol("omega")
JA_ = sp.Matrix([[w_, 1], [0, w_]]); Pm = sp.Matrix([[0, 1], [1, 0]])
check("DQ3: H_B = W H_A^dag W^dag => H_dbl^dag eta_dbl = eta_dbl H_dbl "
      "with eta_dbl = offdiag(W^dag, W); Jordan model J_B = P J_A P "
      "= J_A^dag (W = I case)",
      np.allclose(Hdbl.conj().T @ eta, eta @ Hdbl)
      and sp.simplify(Pm*JA_*Pm - JA_.T) == sp.zeros(2, 2))

# ------------------------------- DQ4 -----------------------------------------
psiA = rand_c(n, 1); psiB = rand_c(n, 1)
Psi = np.vstack([psiA, psiB]); PsiA0 = np.vstack([psiA, np.zeros((n, 1))])
norm_dbl = (Psi.conj().T @ eta @ Psi)[0, 0]
# complex-eigenvalue nullity: eigvec of Hdbl with complex E is eta-null
ev, evec = np.linalg.eig(Hdbl)
icx = int(np.argmax(np.abs(ev.imag)))
vv = evec[:, icx:icx+1]
check("DQ4: <Psi,Psi>_eta = 2 Re<psi_B, W psi_A>; pure-sector states "
      "eta-null; complex-E eigenstates eta-self-null",
      np.isclose(norm_dbl, 2*np.real((psiB.conj().T @ W @ psiA)[0, 0]))
      and np.isclose((PsiA0.conj().T @ eta @ PsiA0)[0, 0], 0)
      and abs(ev[icx].imag) > 1e-8
      and abs((vv.conj().T @ eta @ vv)[0, 0]) < 1e-8)

# ------------------------------- DQ5 -----------------------------------------
# forward: positive pointed metric G => positive invariant graph
h = rand_c(n); h = h + h.conj().T
G0 = rand_c(n); G = G0 @ G0.conj().T + n*np.eye(n)      # G > 0
import scipy.linalg as sla
Gh = sla.sqrtm(G)
HA5 = np.linalg.solve(Gh, h @ Gh)                       # H_A^dag G = G H_A
HB5 = W @ HA5.conj().T @ W.conj().T
graph_inv = np.allclose(HB5 @ (W @ G), (W @ G) @ HA5)   # H_B(WG psi)=WG(H_A psi)
psi = rand_c(n, 1)
Pg = np.vstack([psi, W @ G @ psi])
eta5 = np.block([[np.zeros((n, n)), W.conj().T], [W, np.zeros((n, n))]])
pos = np.real((Pg.conj().T @ eta5 @ Pg)[0, 0])
# converse: invariant eta-positive graph M => Hermitian part of W^dag M is
# a positive pointed metric
th = 0.3
M = W @ G * np.exp(1j*th)                               # H_B M = M H_A
X = W.conj().T @ M
Xh = (X + X.conj().T)/2
conv = (np.allclose(HB5 @ M, M @ HA5)
        and np.allclose(HA5.conj().T @ X, X @ HA5)
        and np.allclose(HA5.conj().T @ Xh, Xh @ HA5)
        and np.min(np.linalg.eigvalsh(Xh)) > 0)
check("DQ5: positive invariant graph {(psi, WG psi)} exists iff the "
      "pointed positive metric G exists (both directions, random "
      "instances): doubling does not evade the pointed obstruction",
      graph_inv and pos > 0
      and np.isclose(pos, 2*np.real((psi.conj().T @ G @ psi)[0, 0]))
      and conv)

# ------------------------------- DQ6 -----------------------------------------
E0 = np.array([1., 1., 2., 3., 3., 3., 5., 7.])
H0 = np.diag(E0)
blocks = [np.where(E0 == e)[0] for e in sorted(set(E0))]
W6 = np.zeros((8, 8), complex)
for b in blocks:
    W6[np.ix_(b, b)] = rand_unitary(len(b))             # [W, H0] = 0
VA = 0.3*rand_c(8)
HA6 = H0 + VA; HB6 = H0 + W6 @ VA.conj().T @ W6.conj().T
def expmat(A):
    d, V = np.linalg.eig(A)
    return V @ np.diag(np.exp(d)) @ np.linalg.inv(V)
ok6 = True
for tt in (0.3, 1.7, 4.9):
    SA = expmat(1j*H0*tt) @ expmat(-2j*HA6*tt) @ expmat(1j*H0*tt)
    SB = expmat(1j*H0*tt) @ expmat(-2j*HB6*tt) @ expmat(1j*H0*tt)
    TA = (SA - np.eye(8))/1j; TB = (SB - np.eye(8))/1j
    ok6 = (ok6 and np.allclose(SB.conj().T @ W6 @ SA, W6)
           and np.allclose(1j*(W6 @ TA - TB.conj().T @ W6)
                           + TB.conj().T @ W6 @ TA, 0))
check("DQ6: S_B(t)^dag W S_A(t) = W exactly at finite time whenever "
      "H_B = W H_A^dag W^dag and [W, H0] = 0 (3 times, machine "
      "precision); T-form i(W T_A - T_B^dag W) + T_B^dag W T_A = 0 -- "
      "a representation of Krein pseudo-unitarity, not a new theorem",
      ok6)

# ============================ field theory ====================================
m2sq, m1sq = sp.Integer(16), sp.Integer(36)
delta = m1sq - m2sq
g1 = sp.Integer(1)
K = [-3, 0, 3]
def wS(b, k): return sp.sqrt(k*k + (m1sq if b == '+' else m2sq))

def couplings(sector):
    """(u-coeff, v-coeff) functions for the positive-frame expansion.
    Sector A: u carries the base pattern, v = rho_b u, rho = -+ delta/2.
    Sector B: the u <-> v mirror (same masses, same delta)."""
    def base(b, k, e):
        c = 1/sp.sqrt(2*wS(b, k)*delta)
        return c if b == '+' else e*c
    def scaled(b, k, e):
        return (-delta/2 if b == '+' else delta/2)*base(b, k, e)
    return (base, scaled) if sector == 'A' else (scaled, base)

def build(fields, sector):
    ulc, vlc = couplings(sector)
    out = []; coup = -g1 if len(fields) == 3 else -g1/2
    for ks in product(K, repeat=len(fields)):
        for bs in product('+-', repeat=len(fields)):
            for es in product((1, -1), repeat=len(fields)):
                if sum(e*k for e, k in zip(es, ks)) != 0: continue
                cf = coup
                for f, b, k, e in zip(fields, bs, ks, es):
                    cf = cf*(ulc(b, k, e) if f == 'u' else vlc(b, k, e))
                out.append((cf, list(zip(bs, ks, es))))
    return out

dg = lambda T: [(sp.conjugate(c), [(b, k, -e) for (b, k, e) in reversed(o)])
                for c, o in T]

def apply_t(terms, vec):
    out = defaultdict(lambda: sp.Integer(0))
    for key, amp in vec.items():
        occ0 = dict(key)
        for cf, ops in terms:
            occ = dict(occ0); fac = sp.Integer(1); ok = True
            for (b, k, e) in reversed(ops):
                mm = (b, k); nn = occ.get(mm, 0)
                if e == 1:
                    if nn == 0: ok = False; break
                    fac *= sp.sqrt(nn); occ[mm] = nn-1
                    if occ[mm] == 0: del occ[mm]
                else:
                    fac *= sp.sqrt(nn+1); occ[mm] = nn+1
            if ok:
                out[frozenset(occ.items())] += amp*cf*fac
    return dict(out)

en = lambda key: sum(nn*wS(b, k) for ((b, k), nn) in key)
gpar = lambda key: (-1)**sum(nn for ((b, k), nn) in key if b == '-')
def bk(A, B):
    return sum(sp.conjugate(A[k])*B[k] for k in A.keys() & B.keys())

H3A = build('uvv', 'A'); H4A = build('uuvv', 'A')
H3B = build('uuv', 'B'); H4B = build('uuvv', 'B')

# ------------------------------- DQ7 -----------------------------------------
modes = [(b, k) for b in '+-' for k in K]
basis = [frozenset()] + [
    frozenset((m, c.count(m)) for m in set(c))
    for tot in (1, 2, 3)
    for c in combinations_with_replacement(modes, tot)]

def act_table(terms, numeric=True):
    tab = {}
    for s in basis:
        res = apply_t(terms, {s: sp.Integer(1)})
        tab[s] = {k: (complex(v) if numeric else v) for k, v in res.items()
                  if (abs(complex(v)) > 1e-14 if numeric else v != 0)}
    return tab

def gconj_table(tab):
    return {s: {k: gpar(s)*gpar(k)*v for k, v in d.items()}
            for s, d in tab.items()}

def tables_equal(t1, t2, tol=1e-10):
    for s in basis:
        d1, d2 = t1.get(s, {}), t2.get(s, {})
        for k in set(d1) | set(d2):
            if abs(d1.get(k, 0) - d2.get(k, 0)) > tol: return False
    return True

tH3A, tH4A = act_table(H3A), act_table(H4A)
tH3B, tH4B = act_table(H3B), act_table(H4B)
tH3Ad, tH4Ad = act_table(dg(H3A)), act_table(dg(H4A))
ok_a = tables_equal(tH3B, tH3A) and tables_equal(tH4B, tH4A)
ok_b = (tables_equal(tH3Ad, gconj_table(tH3A))
        and tables_equal(tH4Ad, gconj_table(tH4A)))
ok_c = (tables_equal(tH3B, gconj_table(tH3Ad))
        and tables_equal(tH4B, gconj_table(tH4Ad)))
check("DQ7: mirror-adjoint relation H_B = W H_A^dag W^dag holds EXACTLY "
      "with W = iota o (-1)^{N_ghost}: (a) H_B = H_A under the naive "
      "kappa identification, (b) H_A^dag = G H_A G (ghost-parity/Krein "
      "pseudo-Hermiticity of the pointed Hamiltonian), (c) combined "
      "(verified on all Fock states with occupation <= 3) -- the "
      "doubled pairing is the two-sector unfolding of the BT kappa",
      ok_a and ok_b and ok_c)

# ------------------------------- DQ8 -----------------------------------------
IN  = {frozenset([(('+', 0), 1), (('-', 0), 1)]): sp.Integer(1)}
OUT = {frozenset([(('-', 3), 1), (('-', -3), 1)]): sp.Integer(1)}
sIN, sOUT = list(IN)[0], list(OUT)[0]
E = en(sIN)

# shell exhaustiveness: no other degenerate state is reachable
reach = set()
for st in (IN, OUT):
    for H in (H3A, dg(H3A), H4A, dg(H4A)):
        reach |= set(apply_t(H, st))
extra_shell = [s for s in reach
               if s not in (sIN, sOUT) and sp.simplify(en(s) - E) == 0]
# H3 has no first-order elements on the shell (odd operator count)
t1_zero = all(bk(x, apply_t(H3A, y)) == 0 and bk(x, apply_t(dg(H3A), y)) == 0
              for x in (IN, OUT) for y in (IN, OUT))
check("DQ8a: the reachable degenerate shell at E = 10 is exactly "
      "{H(0)L(0), L(3)L(-3)}, and H3 has no on-shell first-order "
      "elements (the order-2 identity closes on T^(2) alone)",
      not extra_shell and t1_zero)

def Tmat(H3, H4):
    """exact 2x2 second-order on-shell T in basis [IN, OUT]."""
    states = [IN, OUT]
    T = sp.zeros(2, 2)
    vecs3  = [apply_t(H3, s) for s in states]
    vecs3d = [apply_t(dg(H3), s) for s in states]
    vecs4  = [apply_t(H4, s) for s in states]
    for i_ in range(2):
        for j_ in range(2):
            val = bk(states[i_], vecs4[j_])
            for nkey in set(vecs3d[i_]) | set(vecs3[j_]):
                En = en(nkey)
                if sp.simplify(E - En) == 0: continue
                val += (sp.conjugate(vecs3d[i_].get(nkey, 0))
                        * vecs3[j_].get(nkey, 0))/(E - En)
            T[i_, j_] = sp.radsimp(sp.simplify(sp.nsimplify(sp.expand(val))))
    return T

TA = Tmat(H3A, H4A)
TB = Tmat(H3B, H4B)
Gd = sp.diag(-1, 1)          # gpar(IN) = -1 (one ghost), gpar(OUT) = +1
Mobs = 401*sp.sqrt(6)/39424
src = sp.simplify(sp.conjugate(TA[0, 1]) - TA[1, 0])
check("DQ8b: T_B = T_A under iota, and W T_A = T_B^dag W on the shell, "
      "i.e. G T_A G = T_A^dag EXACTLY: the on-shell T is ghost-parity "
      "(Krein) pseudo-Hermitian while NOT Hilbert-Hermitian",
      sp.simplify(TB - TA) == sp.zeros(2, 2)
      and sp.simplify(Gd*TA*Gd - TA.T.conjugate()) == sp.zeros(2, 2))
check(f"DQ8c: independent recomputation of the obstruction from plain T "
      f"elements: T_A(out,in) = {TA[1,0]} = -401 sqrt(6)/78848, "
      f"T_A(in,out) = +401 sqrt(6)/78848, source = conj(T(in,out)) - "
      f"T(out,in) = 401 sqrt(6)/39424 (HX1 value)",
      sp.simplify(TA[1, 0] + Mobs/2) == 0
      and sp.simplify(TA[0, 1] - Mobs/2) == 0
      and sp.simplify(src - Mobs) == 0)
anti = (TA - TA.T.conjugate())/2
check("DQ8d: the ghost-parity-EVEN (diagonal) block is real/Hermitian; "
      "the ENTIRE obstruction (Hilbert-anti-Hermitian part) lives in "
      "the parity-ODD (G_in G_out = -1) block -- the kappa-odd "
      "component BT's positivity mechanism does not use",
      sp.im(TA[0, 0]) == 0 and sp.im(TA[1, 1]) == 0
      and anti[0, 0] == 0 and anti[1, 1] == 0
      and sp.simplify(anti[1, 0] + Mobs/2) == 0)

# ------------------------------- DQ9 -----------------------------------------
u, v, mu2, epsl = sp.symbols("u v mu2 epsilon")
# regulated pointed sector A (SO conventions), all interaction orders:
#   L = -du dv - mu2 uv + (eps/2)u^2 + (g/2)v^2 + g u v^2 + (g/2)u^2 v^2
# EL: box v = mu2 v - eps u - g v^2 - g u v^2
#     box u = mu2 u - g v - 2g u v - g u^2 v
boxv = mu2*v - epsl*u - g_*v**2 - g_*u*v**2
boxu = mu2*u - g_*v - 2*g_*u*v - g_*u**2*v
breaking = sp.expand(v*boxu - (1 + u)*boxv)   # d.j for j = v du - (1+u) dv
check("DQ9: classical Ward identity: unregulated pointed d.j = 0 "
      "exactly (all interaction orders cancel); regulated breaking is "
      "EXACTLY d.j = eps u(1+u) - mu^2 v (regulator terms only, -> 0 "
      "as regulators are removed); unit Jacobian => no measure factor",
      sp.expand(breaking - (epsl*u*(1 + u) - mu2*v)) == 0
      and sp.expand(breaking.subs({epsl: 0, mu2: 0})) == 0)

print("\nALL PASS" if PASS else "\nSOME CHECKS FAILED")
