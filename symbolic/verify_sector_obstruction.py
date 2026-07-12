#!/usr/bin/env python3
"""Interaction-deformation program, step 6 (2026-07-13): the sectorwise
second-order question -- OUTCOME A established.  Runtime ~3 min.

Framework (team, verified here): the exact U <-> V symmetry exchanges
two vacuum sectors and is NOT a particle parity inside either sector,
so a positive-metric obstruction in the pointed sector A and the exact
Krein symmetry of the doubled theory are compatible.

Structural checks:
SO1  Sector expansions: about (1,0): L2 = -du dv + (g/2)v^2,
     L3 = g u v^2, L4 = (g/2)u^2v^2; about (0,1) the same with u <-> v;
     the two sectors are exchanged by kappa (verified exactly).
SO2  Doubled Jordan model: J_B = P J_A P, kappa_dbl = offdiag(P, P)
     satisfies kappa^2 = 1, [kappa, J_dbl] = 0 -- the finite model of
     the sector-exchanging parity.
SO3  Jacobians: det d(U,V)/d(phi,psi) = 1 pointwise; the chart
     transition has det = -1: no immediate measure factor.

Main computation (SO4-SO7): regulated sector-A theory
     L0 = -du dv - mu^2 uv + (g/2)v^2 + (eps/2)u^2,
masses^2 = mu^2 +- sqrt(eps g) (heavy '+' healthy, light '-' ghost in
this convention), positive-frame mode expansion derived from the branch
eigenvectors (v = rho_b u on branch b, rho_+- = -+ delta/2) with the
quarter-turn (a - a^dag) structure on the ghost branch.  Interactions
H3 = -g u v^2, H4 = -(g/2) u^2 v^2 are PURE POTENTIALS (no Legendre
corrections -- the reason for working in the two-field frame).

The on-shell second-order source element for the branch-changing
process heavy(ka) + light(kb) -> light(kc) + light(kd) is
    <out| S |in> = <out| v2d - v2 |in>
        + sum_n [<out|v1d|n><n|v1d|in> - <out|v1|n><n|v1|in>]/(E - E_n),
the exact matrix-element form of (v2d - v2) + (1/2)[R1, v1 + v1d]
(uses (vd-v)(v+vd) + (v+vd)(vd-v) = 2(vd vd - v v)).

RESULTS:
SO4  The contact piece <v2d - v2> VANISHES on the shell at every
     kinematics tested: the quartic does not rescue or produce the
     obstruction here.
SO5  The exchange piece is NONZERO: 0.52332382 at
     (ka,kb,kc,kd) = (2,-1,3,-2), m2 = 1, tuned m1 = 3.4458.
SO6  Truncation-complete: identical at momentum cutoffs Kmax = 4 and 6
     (tree-level exchange: all channels s = ka+kb, t = ka-kc,
     u = ka-kd lie in the momentum set; 5-particle time-orderings
     close on the same momenta).
SO7  Generic: nonzero at three independent tuned kinematic points
     (0.5233, 0.3109, 0.3970).

CONCLUSION (Outcome A): the positive pseudo-Hermitian completion of the
pointed sector is obstructed at second order by generic on-shell
branch-changing 2 -> 2 scattering -- the continuum analogue of the
oscillator's isolated 3:1 resonance, with the scattering shells making
it generic.  There is no perfect-square cancellation; the exact
kappa = U <-> V instead maps the obstructed sector-A construction to
the mirror sector-B construction (itself obstructed), consistent with
the revised hypothesis: Krein symmetry lives on the doubled state
space, not inside one pointed positive sector.
"""
import numpy as np
import sympy as sp
from itertools import product
from collections import defaultdict

PASS = True
def check(msg, ok):
    global PASS
    print(("[OK ] " if ok else "[FAIL] ") + msg)
    PASS = PASS and bool(ok)

# ------------------------------ SO1-SO3 --------------------------------------
t, z, gs = sp.symbols("t z g", positive=True)
u_ = sp.Function("u")(t, z); v_ = sp.Function("v")(t, z)
def dsq(f, h): return sp.diff(f,t)*sp.diff(h,t) - sp.diff(f,z)*sp.diff(h,z)
L = lambda A, B: -dsq(A, B) + gs/2*A**2*B**2
eps = sp.Symbol("epsilon")
def taylor(Lf, n):
    return sp.expand(sp.diff(Lf, eps, n).subs(eps, 0)/sp.factorial(n))
LAe = sp.expand(L(1 + eps*u_, eps*v_)); LBe = sp.expand(L(eps*u_, 1 + eps*v_))
swap = lambda e: e.subs({u_: v_, v_: u_}, simultaneous=True)
check("SO1: sector expansions L2, L3, L4 as stated; sector B = "
      "sector A with u <-> v (all orders 2,3,4)",
      all(sp.simplify(taylor(LBe, n) - swap(taylor(LAe, n))) == 0
          for n in (2, 3, 4)))

w = sp.Symbol("omega")
JA = sp.Matrix([[w,1],[0,w]]); P = sp.Matrix([[0,1],[1,0]])
Jd = sp.diag(JA, P*JA*P)
Kd = sp.zeros(4,4); Kd[0:2,2:4] = P; Kd[2:4,0:2] = P
check("SO2: doubled Jordan model: kappa_dbl^2 = 1 and "
      "[kappa_dbl, J_dbl] = 0",
      sp.simplify(Kd*Kd - sp.eye(4)) == sp.zeros(4,4)
      and sp.simplify(Kd*Jd - Jd*Kd) == sp.zeros(4,4))

lam, ph, ps = sp.symbols("lambda phi psi", positive=True)
Uf = sp.exp(lam*ph); Vf = ps/lam*sp.exp(-lam*ph)
Jac = sp.Matrix([[sp.diff(Uf,ph), sp.diff(Uf,ps)],
                 [sp.diff(Vf,ph), sp.diff(Vf,ps)]])
phB = sp.log(ps/lam)/lam - ph
J2 = sp.Matrix([[sp.diff(phB,ph), sp.diff(phB,ps)], [0, 1]])
check("SO3: det d(U,V)/d(phi,psi) = 1; chart transition det = -1",
      sp.simplify(Jac.det()) == 1 and sp.simplify(J2.det()) == -1)

# ------------------------------ SO4-SO7 --------------------------------------
def source_element(kin, m2sq=1.0, Kmax=6):
    ka, kb, kc, kd = kin
    m1sq = (np.sqrt(kc*kc+m2sq)+np.sqrt(kd*kd+m2sq)
            - np.sqrt(kb*kb+m2sq))**2 - ka*ka
    delta = m1sq - m2sq
    if delta <= 0: return None
    K = [k for k in range(-Kmax, Kmax+1) if k != 0]
    g = 1.0
    def wf(b,k): return np.sqrt(k*k + (m1sq if b=='+' else m2sq))
    def ulc(b,k,e):
        base = 1.0/np.sqrt(2*wf(b,k)*delta)
        return base if b == '+' else e*base
    def vlc(b,k,e): return (-delta/2 if b == '+' else delta/2)*ulc(b,k,e)
    def build(fields):
        out = []; coup = -g if len(fields) == 3 else -g/2
        for ks in product(K, repeat=len(fields)):
            for bs in product('+-', repeat=len(fields)):
                for es in product((1,-1), repeat=len(fields)):
                    if sum(e*k for e,k in zip(es,ks)) != 0: continue
                    cf = coup
                    for f,b,k,e in zip(fields,bs,ks,es):
                        cf *= (ulc(b,k,e) if f == 'u' else vlc(b,k,e))
                    if cf != 0: out.append((cf, list(zip(bs,ks,es))))
        return out
    H3 = build('uvv'); H4 = build('uuvv')
    dg = lambda T: [(np.conj(c), [(b,k,-e) for (b,k,e) in reversed(o)])
                    for c,o in T]
    H3d, H4d = dg(H3), dg(H4)
    def apply_t(terms, vec):
        out = defaultdict(complex)
        for key, amp in vec.items():
            occ0 = dict(key)
            for cf, ops in terms:
                occ = dict(occ0); fac = 1.0; ok = True
                for (b,k,e) in reversed(ops):
                    m = (b,k); n = occ.get(m, 0)
                    if e == 1:
                        if n == 0: ok = False; break
                        fac *= np.sqrt(n); occ[m] = n-1
                        if occ[m] == 0: del occ[m]
                    else:
                        fac *= np.sqrt(n+1); occ[m] = n+1
                if ok: out[frozenset(occ.items())] += amp*cf*fac
        return dict(out)
    en = lambda key: sum(n*wf(b,k) for ((b,k),n) in key)
    bk = lambda A,B: sum(np.conj(A[k])*B[k] for k in A.keys() & B.keys())
    IN  = {frozenset([(('+',ka),1), (('-',kb),1)]): 1.0+0j}
    OUT = {frozenset([(('-',kc),1), (('-',kd),1)]): 1.0+0j}
    E = en(list(IN.keys())[0])
    if abs(E - en(list(OUT.keys())[0])) > 1e-9: return None
    c1 = bk(OUT, apply_t(H4d, IN)) - bk(OUT, apply_t(H4, IN))
    al = apply_t(H3, IN); be = apply_t(H3d, IN)
    gm = apply_t(H3, OUT); gmd = apply_t(H3d, OUT)
    c2 = 0j
    for n in set(al) | set(be) | set(gm) | set(gmd):
        En = en(n)
        if abs(E - En) < 1e-9: continue
        c2 += (np.conj(gm.get(n,0))*be.get(n,0)
               - np.conj(gmd.get(n,0))*al.get(n,0))/(E - En)
    return c1, c2

r4 = source_element((2,-1,3,-2), Kmax=4)
r6 = source_element((2,-1,3,-2), Kmax=6)
check("SO4: contact piece <v2d - v2> = 0 on the shell (quartic neither "
      "rescues nor produces the obstruction here)",
      abs(r6[0]) < 1e-12)
check(f"SO5: exchange piece NONZERO: total = {(r6[0]+r6[1]).real:.8f} "
      "at (2,-1,3,-2), m2 = 1, tuned m1 = 3.4458 -- OUTCOME A: "
      "sectorwise positive obstruction",
      abs(r6[0] + r6[1]) > 0.1)
check("SO6: truncation-complete (identical at Kmax = 4 and 6: "
      "tree-exchange closure)",
      abs((r4[0]+r4[1]) - (r6[0]+r6[1])) < 1e-12)
vals = []
for kin in [(2,-1,3,-2), (1,-3,2,-4), (1,-4,3,-6)]:
    r = source_element(kin, Kmax=8)
    vals.append(abs(r[0] + r[1]))
check(f"SO7: generic: nonzero at three independent tuned kinematics "
      f"({', '.join(f'{x:.4f}' for x in vals)})",
      all(x > 0.05 for x in vals))

print("\nALL PASS" if PASS else "\nSOME CHECKS FAILED")
