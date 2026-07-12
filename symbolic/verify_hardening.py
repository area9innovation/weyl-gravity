#!/usr/bin/env python3
"""Interaction-deformation program, step 7 (2026-07-13): theorem
hardening for paper 5.  Runtime ~3 min.

HX1  EXACT obstruction value.  At the clean center-of-mass point
     m_L = 4, m_H = 6 = (3/2) m_L (delta = 20), in-state H(0) + L(0)
     both at rest, out-state L(3) + L(-3) with E = 5 = (5/4) m_L per
     particle: the shell is exactly satisfied (10 = 10) and the
     second-order source element is EXACTLY
         M_obs = 401 sqrt(6) / 39424   (~ 0.0249149...),
     with the contact piece exactly zero.  Since the source is analytic
     on the nonsingular part of the branch-changing shell, one exact
     nonzero value implies the obstruction is nonzero on an open subset
     of the shell: the theorem-strength genericity statement.
HX2  Confluent parity, single sector.  With P_delta b_pm = +- b_pm and
     the confluent Jordan basis c = (b+ + b-)/2, d = (b+ - b-)/delta:
     P c = (delta/2) d and P d = (2/delta) c, i.e. in the standard
     COLUMN-vector convention on the ordered basis (c, d)
         P_delta = [[0, 2/delta], [delta/2, 0]];
     P^2 = 1 but NO bounded limit as delta -> 0: the regulated ghost
     parity cannot converge as a chain-preserving parity inside one
     Jordan sector (algebraic version of the PS-H no-go).
     (Referee correction adopted: the earlier display was the row-
     convention transpose.)
HX3  Confluent parity, doubled space.  With the OPPOSITELY oriented
     confluent identification in sector B (c_B = (b+ - b-)/2,
     d_B = (b+ + b-)/delta), the cross parity b_pm^A <-> +- b_pm^B is
     EXACTLY the delta-independent sector exchange
     (c_A, d_A) <-> (c_B, d_B): bounded, involutive, and equal to
     kappa_dbl for every delta.  The regulated branch parity has no
     bounded confluent limit on either pointed sector separately, but
     converges on the doubled oppositely oriented sectors to the exact
     sector-exchange involution U <-> V.
"""
import sympy as sp
from itertools import product
from collections import defaultdict

PASS = True
def check(msg, ok):
    global PASS
    print(("[OK ] " if ok else "[FAIL] ") + msg)
    PASS = PASS and bool(ok)

# ------------------------------- HX1 -----------------------------------------
m2sq, m1sq = sp.Integer(16), sp.Integer(36)
delta = m1sq - m2sq
g = sp.Integer(1)
K = [-3, 0, 3]

def w(b, k): return sp.sqrt(k*k + (m1sq if b == '+' else m2sq))
def ulc(b, k, e):
    base = 1/sp.sqrt(2*w(b, k)*delta)
    return base if b == '+' else e*base
def vlc(b, k, e): return (-delta/2 if b == '+' else delta/2)*ulc(b, k, e)

def build(fields):
    out = []; coup = -g if len(fields) == 3 else -g/2
    for ks in product(K, repeat=len(fields)):
        for bs in product('+-', repeat=len(fields)):
            for es in product((1, -1), repeat=len(fields)):
                if sum(e*k for e, k in zip(es, ks)) != 0: continue
                cf = coup
                for f, b, k, e in zip(fields, bs, ks, es):
                    cf = cf*(ulc(b, k, e) if f == 'u' else vlc(b, k, e))
                out.append((cf, list(zip(bs, ks, es))))
    return out

H3 = build('uvv'); H4 = build('uuvv')
dg = lambda T: [(sp.conjugate(c), [(b, k, -e) for (b, k, e) in reversed(o)])
                for c, o in T]
H3d, H4d = dg(H3), dg(H4)

def apply_t(terms, vec):
    out = defaultdict(lambda: sp.Integer(0))
    for key, amp in vec.items():
        occ0 = dict(key)
        for cf, ops in terms:
            occ = dict(occ0); fac = sp.Integer(1); ok = True
            for (b, k, e) in reversed(ops):
                mm = (b, k); n = occ.get(mm, 0)
                if e == 1:
                    if n == 0: ok = False; break
                    fac *= sp.sqrt(n); occ[mm] = n-1
                    if occ[mm] == 0: del occ[mm]
                else:
                    fac *= sp.sqrt(n+1); occ[mm] = n+1
            if ok:
                out[frozenset(occ.items())] += amp*cf*fac
    return dict(out)

en = lambda key: sum(n*w(b, k) for ((b, k), n) in key)
def bk(A, B):
    return sum(sp.conjugate(A[k])*B[k] for k in A.keys() & B.keys())

IN  = {frozenset([(('+', 0), 1), (('-', 0), 1)]): sp.Integer(1)}
OUT = {frozenset([(('-', 3), 1), (('-', -3), 1)]): sp.Integer(1)}
E = en(list(IN.keys())[0])
c1 = sp.simplify(bk(OUT, apply_t(H4d, IN)) - bk(OUT, apply_t(H4, IN)))
al = apply_t(H3, IN); be = apply_t(H3d, IN)
gm = apply_t(H3, OUT); gmd = apply_t(H3d, OUT)
c2 = sp.Integer(0)
for n in set(al) | set(be) | set(gm) | set(gmd):
    En = sp.simplify(en(n))
    if sp.simplify(E - En) == 0: continue
    c2 += (sp.conjugate(gm.get(n, 0))*be.get(n, 0)
           - sp.conjugate(gmd.get(n, 0))*al.get(n, 0))/(E - En)
c2 = sp.radsimp(sp.simplify(sp.nsimplify(sp.expand(c2))))
check("HX1: exact rational kinematic point (m_L, m_H) = (4, 6), "
      "H(0)+L(0) -> L(3)+L(-3): contact = 0 and the exact obstruction "
      f"value is {c2} = 401 sqrt(6)/39424 != 0 "
      "(open-subset genericity by analyticity)",
      c1 == 0 and sp.simplify(c2 - 401*sp.sqrt(6)/39424) == 0)

# ------------------------------- HX2 -----------------------------------------
d = sp.Symbol("delta", positive=True)
# change-of-basis matrix: COLUMNS are the new basis vectors (c, d) in
# branch coordinates; operator matrix in the new basis is C^{-1} P C
C = sp.Matrix([[sp.Rational(1, 2), 1/d], [sp.Rational(1, 2), -1/d]])
P = sp.diag(1, -1)
P_conf = sp.simplify(C.inv()*P*C)
check("HX2: P_delta in the confluent (c, d) basis, COLUMN convention, "
      "is [[0, 2/delta], [delta/2, 0]] (P c = (delta/2) d, "
      "P d = (2/delta) c) with P^2 = 1 and no bounded delta -> 0 limit",
      P_conf == sp.Matrix([[0, 2/d], [d/2, 0]])
      and sp.simplify(P_conf*P_conf - sp.eye(2)) == sp.zeros(2, 2))

# ------------------------------- HX3 -----------------------------------------
CA = C
CB = sp.Matrix([[sp.Rational(1, 2), 1/d], [-sp.Rational(1, 2), 1/d]])
kb = sp.zeros(4, 4)
kb[0:2, 2:4] = sp.diag(1, -1)
kb[2:4, 0:2] = sp.diag(1, -1)
T = sp.diag(CA, CB)
kc = sp.simplify(T.inv()*kb*T)
X = sp.zeros(4, 4); X[0, 2] = X[1, 3] = X[2, 0] = X[3, 1] = 1
check("HX3: with oppositely oriented confluent identification in sector "
      "B, the cross parity equals the delta-INDEPENDENT sector exchange "
      "(c_A,d_A) <-> (c_B,d_B) exactly (kappa^2 = 1): the regulated "
      "branch parity converges on the doubled space to the exact "
      "U <-> V involution",
      (not kc.has(d)) and sp.simplify(kc - X) == sp.zeros(4, 4)
      and sp.simplify(kc*kc - sp.eye(4)) == sp.zeros(4, 4))

print("\nALL PASS" if PASS else "\nSOME CHECKS FAILED")
