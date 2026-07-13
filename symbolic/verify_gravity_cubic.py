#!/usr/bin/env python3
"""Cubic Einstein-Weyl gravity: G13-G14 (2026-07-14).  Runtime ~1 min.

Engine in gravity_perturbiner.py (multi-wave perturbiner, exact
rational-complex kinematics).  Checks G13a/G13b/G13/G14a/G14b/G14c;
see the check messages.  Precision notes (team, adopted): the G14c
number is the POLARIZATION-CONTRACTED REDUCED residue -- the fully
normalized physical residue carries in addition the massive branch's
kinetic/LSZ normalization (nonzero, so the nonvanishing conclusion is
unaffected); and [(-1)^{N_M}, S] != 0 remains formally conditional on
the real-shell value until G15 (real physical component vs complexified
shell).
"""
import sympy as sp
from gravity_perturbiner import (R, I, ETA, wt_add, wt_scale, wt_mul,
    wt_contract, wt_trace, wt_deriv, comp, raise_idx, metric_objects,
    curvature, densities, C1, ALPHA, BETA, amplitude, dot, sym,
    transverse_basis, massive_tt_basis, as_eps)

PASS = True
def check(msg, ok):
    global PASS
    print(("[OK ] " if ok else "[FAIL] ") + msg)
    PASS = PASS and bool(ok)

# ============================== G13a ==========================================
# 2-wave on-shell test: coefficient of lam1 lam2 with p2 = -p1
def two_point(p, eps):
    P = [list(p), [-c for c in p]]
    return amplitude([as_eps(eps), as_eps(eps)], P)

p_h = [R(1), 0, 0, R(1)]                       # null
q_h = [0, 1, sp.I, 0]                          # q.p = 0, q^2 = 0
eps_h = {(m, n): q_h[m]*q_h[n] for m in range(4) for n in range(4)}
p_M = [R(5, 4), 0, 0, R(3, 4)]                 # p^2 = 1 = M^2
Ms, G5M = massive_tt_basis(p_M)
p_off = [R(2), 0, 0, R(1)]                     # p^2 = 3: off shell
Moff, _ = massive_tt_basis(p_off)
check("G13a: engine validation: the on-shell 2-point coefficient "
      "vanishes for TT waves on BOTH branches (p^2 = 0 graviton, "
      "p^2 = M^2 massive) and is NONZERO off shell (p^2 = 3)",
      two_point(p_h, eps_h) == 0
      and all(two_point(p_M, T) == 0 for T in Ms)
      and two_point(p_off, Moff[0]) != 0)

# ============================== kinematic points ===============================
M = 1
# M -> h h physical decay point (rest frame)
pd1 = [R(1), 0, 0, 0]
pd2 = [-R(1, 2), 0, 0, -R(1, 2)]
pd3 = [-R(1, 2), 0, 0, R(1, 2)]
qd2 = [0, 1, sp.I, 0]      # null, qd2.pd2 = 0
qd3 = [0, 1, -sp.I, 0]     # null, qd3.pd3 = 0
assert dot(pd1, pd1) == 1 and dot(pd2, pd2) == 0 and dot(pd3, pd3) == 0
assert all(pd1[m] + pd2[m] + pd3[m] == 0 for m in range(4))

# MMM rational-complex point
pm1 = [R(5, 4), 0, 0, R(3, 4)]
pm2 = [-R(17, 32), 7*sp.I/8, 0, -R(7, 32)]
pm3 = [-R(23, 32), -7*sp.I/8, 0, -R(17, 32)]
assert all(sp.simplify(dot(p, p) - 1) == 0 for p in (pm1, pm2, pm3))
assert all(pm1[m] + pm2[m] + pm3[m] == 0 for m in range(4))

# MMh rational-complex point
ph1 = [R(5, 4), 0, 0, R(3, 4)]
ph2 = [-R(17, 4), -4*sp.I, 0, -R(23, 4)]
ph3 = [3, 4*sp.I, 0, 5]
qh3 = [5, 0, 4, 3]         # null, qh3.ph3 = 0
assert sp.simplify(dot(ph1, ph1) - 1) == 0
assert sp.simplify(dot(ph2, ph2) - 1) == 0
assert dot(ph3, ph3) == 0 and dot(qh3, qh3) == 0 \
    and sp.simplify(dot(qh3, ph3)) == 0
assert all(ph1[m] + ph2[m] + ph3[m] == 0 for m in range(4))

# ============================== G13b: Ward ====================================
xi = [R(1, 3), R(1, 5), R(2, 7), -R(1, 2)]
B1, _ = massive_tt_basis(ph1)
B2, _ = massive_tt_basis(ph2)
gauge3 = sym([sp.nsimplify(c) for c in ph3], xi)
ward1 = amplitude([as_eps(B1[0]), as_eps(B2[0]), as_eps(gauge3)],
                  [ph1, ph2, ph3])
D1, _ = massive_tt_basis(pd1)
gauge_d2 = sym(pd2, xi)
eps_d3 = {(m, n): qd3[m]*qd3[n] for m in range(4) for n in range(4)}
ward2 = amplitude([as_eps(D1[0]), as_eps(gauge_d2), as_eps(eps_d3)],
                  [pd1, pd2, pd3])
check("G13b: Ward identity at 3 points: gauge polarization "
      "p (x) xi + xi (x) p on the massless leg gives ZERO amplitude "
      "(checked on the M M h point and the M h h decay point)",
      sp.simplify(ward1) == 0 and sp.simplify(ward2) == 0)

# ============================== G13: one-M rule ================================
eps_d2p = {(m, n): qd2[m]*qd2[n] for m in range(4) for n in range(4)}
eps_d2m = {(m, n): sp.conjugate(qd2[m])*sp.conjugate(qd2[n])
           for m in range(4) for n in range(4)}
eps_d3p = {(m, n): qd3[m]*qd3[n] for m in range(4) for n in range(4)}
eps_d3m = {(m, n): sp.conjugate(qd3[m])*sp.conjugate(qd3[n])
           for m in range(4) for n in range(4)}
vals = []
for TM in D1:
    for e2 in (eps_d2p, eps_d2m):
        for e3 in (eps_d3p, eps_d3m):
            vals.append(sp.simplify(amplitude(
                [as_eps(TM), as_eps(e2), as_eps(e3)], [pd1, pd2, pd3])))
check("G13: ONE-M RULE at cubic order: A_3(M, h, h) = 0 for all 5 "
      "massive polarizations x 4 graviton helicity combinations at the "
      "physical decay point M(rest) -> hh (20 exact zeros): the "
      "massive eigenfield does not decay into gravitons at tree cubic "
      "order -- the amplitude-level Einstein-truncation statement",
      all(v == 0 for v in vals))

# ============================== G14a: MMM =====================================
A1, _ = massive_tt_basis(pm1)
A2, _ = massive_tt_basis(pm2)
A3b, G5_3 = massive_tt_basis(pm3)
mmm = amplitude([as_eps(A1[0]), as_eps(A2[0]), as_eps(A3b[0])],
                [pm1, pm2, pm3])
mmm_vals = [mmm]
if mmm == 0:  # scan until a nonzero combination is found
    for i in range(5):
        for j in range(5):
            for l in range(5):
                v = amplitude([as_eps(A1[i]), as_eps(A2[j]),
                               as_eps(A3b[l])], [pm1, pm2, pm3])
                mmm_vals.append(v)
                if v != 0:
                    break
            else:
                continue
            break
        else:
            continue
        break
check(f"G14a: A_3(MMM) NONZERO at the exact rational-complex on-shell "
      f"point (first value: {sp.nsimplify(mmm_vals[-1])}): the cubic "
      "self-coupling of the massive eigenfield exists on shell (not "
      "implied by tr M^3 alone)",
      any(v != 0 for v in mmm_vals))

# ============================== G14b: MMh =====================================
eps_h3 = {(m, n): qh3[m]*qh3[n] for m in range(4) for n in range(4)}
mmh = amplitude([as_eps(B1[0]), as_eps(B2[0]), as_eps(eps_h3)],
                [ph1, ph2, ph3])
mmh_vals = [mmh]
if mmh == 0:
    for i in range(5):
        for j in range(5):
            v = amplitude([as_eps(B1[i]), as_eps(B2[j]), as_eps(eps_h3)],
                          [ph1, ph2, ph3])
            mmh_vals.append(v)
            if v != 0:
                break
        else:
            continue
        break
check(f"G14b: A_3(MMh) NONZERO at the exact rational-complex on-shell "
      f"point (first value: {sp.nsimplify(mmh_vals[-1])}): the massive "
      "eigenfield couples gravitationally at cubic order",
      any(v != 0 for v in mmh_vals))

# ============================== G14c: factorization ===========================
# internal momentum P = -(pm1 + pm2) = pm3 with P^2 = M^2 (s-channel
# pole).  Second vertex: legs (-P, q3, q4) with -P + q3 + q4 = 0, i.e.
# q3 = P - q4; choosing q4 null with q4.P = 0 makes q3^2 = M^2 exact.
# Exact rational-complex solution (derived by hand, verified below):
Pint = [pm3[m] for m in range(4)]               # on-shell internal M
mP = [-c for c in Pint]
q4 = [-R(11, 23), sp.I, R(11, 23), 1]           # null, q4.P = 0
q3 = [Pint[m] - q4[m] for m in range(4)]
legs_ok = (sp.simplify(dot(q4, q4)) == 0
           and sp.simplify(dot(q4, Pint)) == 0
           and sp.simplify(dot(q3, q3) - 1) == 0
           and all(sp.simplify(mP[m] + q3[m] + q4[m]) == 0
                   for m in range(4)))
r4 = [0, sp.I, 0, 1]                            # null, r4.q4 = 0
assert dot(r4, r4) == 0 and sp.simplify(dot(r4, q4)) == 0
eps_q4 = {(m, n): r4[m]*r4[n] for m in range(4) for n in range(4)}
CP, G5P = massive_tt_basis(Pint)     # same tensors serve P and -P (even rank)
BQ3, _ = massive_tt_basis(q3)
vvec = sp.Matrix([amplitude([as_eps(A1[0]), as_eps(A2[0]), as_eps(CP[a])],
                            [pm1, pm2, Pint]) for a in range(5)])
uvec = sp.Matrix([amplitude([as_eps(CP[a]), as_eps(BQ3[0]), as_eps(eps_q4)],
                            [mP, q3, q4]) for a in range(5)])
resid = sp.simplify((vvec.T*G5P.inv()*uvec)[0, 0])
check(f"G14c: factorization residue at the s-channel pole P^2 = M^2: "
      f"legs exact ({legs_ok}); r = A_3(M M M^a(P)) G5^-1 "
      f"A_3(M^b(-P) M h) = {sp.nsimplify(resid)} != 0 (the REDUCED, "
      "polarization-contracted residue; the physical residue carries "
      "in addition the nonzero massive kinetic/LSZ normalization): "
      "the MM -> Mh four-point amplitude is NOT identically zero on "
      "the complexified shell; [(-1)^{N_M}, S] != 0 for the naive "
      "massive number parity, conditional on the real-shell value "
      "(supplied by G15)",
      legs_ok and resid != 0)

print("\nALL PASS" if PASS else "\nSOME CHECKS FAILED")
