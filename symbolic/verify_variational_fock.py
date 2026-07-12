#!/usr/bin/env python3
"""Symbolic audit: minimum-distortion theorem (A) and field-theory metric (B).

Direction A (variational selection of the Bender-Mannheim metric):
  For S = S_+ C, C in Stab(J, G0') = SO(2,C)^2, with per-block Gram data
  W_j = C_j C_j^dag = exp(tau_j n_j.sigma)  (det W_j = 1, tau_j >= 0),
  a = (tau1+tau2)/2, b = (tau1-tau2)/2:

    F(S) = ||log(S^dag S)||_F^2
         >= 4 [ a^2 + arccosh^2(cosh r cosh b) ]   (equality at worst alignment)
         >= 4 r^2,
  equality in the chain iff tau1 = tau2 = 0 iff C unitary.

Direction B (free fourth-order field, modewise):
  * PT ground state (normalized coords) = real Gaussian with
      A = [[(w1+w2)/(w1 w2), 1], [1, w1+w2]],  normalizable for all w1>w2>0;
  * fidelity  |<phi0|psi0>|^2 = 4 w1 sqrt(w1^2+w1w2+w2^2)/(4w1^2+3w1w2+w2^2)
      -> sqrt(3)/2  as w1 -> w2 (the UV limit);
  * particle content <N> = w2(w1^2+w2^2)/(2 w1 (w1^2+w1w2+w2^2)) -> 1/3;
  * r(k) = log[(w1+w2)^2/(m1^2-m2^2)] exactly;  spec(M_obs) = e^{+-r} ~ k^{+-2}.

Run:  python3 verify_variational_fock.py   (appends nothing; prints PASS/FAIL table)
"""

import sympy as sp
from sympy import I, sqrt, Rational

PASS = True
def check(name, ok):
    global PASS
    print(f"[{'OK ' if ok else 'FAIL'}] {name}")
    PASS = PASS and bool(ok)

w1, w2 = sp.symbols("omega1 omega2", positive=True)

# ---------------------------------------------------------------- A ----------
print("=== A: minimum-distortion theorem ===")
r_, t1, t2 = sp.symbols("r tau1 tau2", positive=True)
c, s = sp.cosh(r_), sp.sinh(r_)
h1, h2 = sp.cosh(t1), sp.cosh(t2)
g1, g2 = sp.sinh(t1), sp.sinh(t2)
a_, b_ = (t1 + t2) / 2, (t1 - t2) / 2

# A1: invariants of P = C^dag e^{rB} C in terms of Gram data (chi = alignment):
#     T  := cosh x1 + cosh x2 = c (h1 + h2)                     [tr P / 2]
#     Pi := cosh x1 cosh x2   = [(2c^2-s^2) h1 h2 + s^2 (1 + g1 g2 chi)]/2
# (matrix forms of these were verified against random C in numeric/distortion_scan.py)
chi = sp.Symbol("chi", real=True)
T = c * (h1 + h2)
Pi = ((2 * c**2 - s**2) * h1 * h2 + s**2 * (1 + g1 * g2 * chi)) / 2

# A2: worst-alignment closed form: at chi = -1,
#     x1,2 = phi +- a with phi = arccosh(c cosh b).
phi = sp.acosh(c * sp.cosh(b_))
x1, x2 = phi + a_, phi - a_
check("A2a: cosh x1 + cosh x2 == T",
      sp.simplify(sp.expand_trig(sp.cosh(x1) + sp.cosh(x2) - T)) == 0)
check("A2b: cosh x1 * cosh x2 == Pi(chi=-1)",
      sp.simplify(sp.expand_trig(sp.cosh(x1) * sp.cosh(x2) - Pi.subs(chi, -1))) == 0)

# A3: Pi is nondecreasing in chi (coefficient s^2 g1 g2 / 2 >= 0): trivial sign check.
check("A3: dPi/dchi = s^2 g1 g2/2 >= 0",
      sp.simplify(sp.diff(Pi, chi) - s**2 * g1 * g2 / 2) == 0)

# A4: monotonicity lemma: at fixed T, x1^2 + x2^2 is nondecreasing in Pi.
#     Parametrize u1 = T/2 + w, u2 = T/2 - w (Pi = T^2/4 - w^2 decreasing in w):
#     d/dw (x1^2 + x2^2) = 2 (x1/sinh x1 - x2/sinh x2) <= 0 since x/sinh x is
#     strictly decreasing and x1 >= x2. Mechanize the decreasingness of x/sinh x:
xx = sp.Symbol("x", positive=True)
deriv = sp.simplify(sp.diff(xx / sp.sinh(xx), xx))
# derivative = (sinh x - x cosh x)/sinh^2 x ; numerator negative iff tanh x < x: check series+limit
numer = sp.simplify(sp.sinh(xx) - xx * sp.cosh(xx))
check("A4: (x/sinh x)' numerator = sinh x - x cosh x, negative for x>0 "
      "(= -x^3/3 + O(x^5), and d/dx[sinh x - x cosh x] = -x sinh x < 0)",
      sp.simplify(sp.series(numer, xx, 0, 5).removeO() + xx**3 / 3) == 0 and
      sp.simplify(sp.diff(numer, xx) + xx * sp.sinh(xx)) == 0)

# A5: the lower-bound function 4(a^2 + phi(b)^2) >= 4 r^2, equality iff a=b=0:
#     phi(b) = arccosh(cosh r cosh b) >= arccosh(cosh r) = r, equality iff b=0.
# phi(b) >= r via monotone cosh: cosh(phi) - cosh(r) = cosh r (cosh b - 1) >= 0,
# equality iff b = 0 (and phi, r >= 0 makes cosh invertible on the range).
check("A5: cosh(phi) - cosh(r) == cosh(r)(cosh b - 1) >= 0, equality iff b=0",
      sp.simplify(c * sp.cosh(b_) - c - c * (sp.cosh(b_) - 1)) == 0)

# A6: equality forces C unitary: tau_j = 0 <=> W_j = I <=> C_j^dag C_j = I.
#     (W_j = I  <=>  C_j C_j^dag = I  <=>  C_j unitary; recorded as logic, no algebra needed.)
check("A6: equality chain (logic: a=b=0 <=> tau1=tau2=0 <=> W_j=I <=> C unitary)", True)

# ---------------------------------------------------------------- B ----------
print("\n=== B: field-theoretic metric and representation ===")

# B1: PT ground state: solve b_j psi = 0 for Gaussian psi, normalized coords.
sg = sp.sqrt(w1**2 - w2**2)
Bm = sp.zeros(4, 4); Bm[0, 3] = I; Bm[1, 2] = I; Bm[2, 1] = -I; Bm[3, 0] = -I
Spm = (w1 * sp.eye(4) - w2 * Bm) / sg          # S_+^{-1}
l1 = sp.Matrix([1 / sp.sqrt(w2), 0, I * sp.sqrt(w2), 0]) / sp.sqrt(2)
l2 = sp.Matrix([0, sp.sqrt(w1), 0, I / sp.sqrt(w1)]) / sp.sqrt(2)
A11s, A22s, A12s = sp.symbols("A11 A22 A12")
def annihilation_eqs(l):
    v = (l.T * Spm).T
    cx, cy, cp, cq = v[0], v[1], v[2], v[3]
    return [sp.simplify(cx + cp * I * A11s + cq * I * A12s),
            sp.simplify(cy + cp * I * A12s + cq * I * A22s)]
sol = sp.solve(annihilation_eqs(l1) + annihilation_eqs(l2), [A11s, A22s, A12s], dict=True)
A11v, A22v, A12v = [sp.simplify(sol[0][k]) for k in (A11s, A22s, A12s)]
check("B1a: psi0 Gaussian matrix A = [[(w1+w2)/(w1 w2), 1],[1, w1+w2]]",
      sp.simplify(A11v - (w1 + w2) / (w1 * w2)) == 0 and
      sp.simplify(A22v - (w1 + w2)) == 0 and sp.simplify(A12v - 1) == 0)
Apt = sp.Matrix([[A11v, A12v], [A12v, A22v]])
check("B1b: psi0 normalizable: A real with det A = (w1^2+w1w2+w2^2)/(w1 w2) > 0",
      sp.simplify(sp.det(Apt) - (w1**2 + w1 * w2 + w2**2) / (w1 * w2)) == 0)

# B1c: psi0 is the ground state: H'_PT psi0 = (w1+w2)/2 psi0, where in normalized
# coordinates H'_PT = 1/2[ (w1^2+w2^2)/(w1w2) x^2 + w1 w2 y^2 - w1 w2 d_x^2 ] - x d_y.
xs, ys = sp.symbols("x y", real=True)
psi = sp.exp(-(A11v * xs**2 + 2 * A12v * xs * ys + A22v * ys**2) / 2)
HPT_psi = (Rational(1, 2) * ((w1**2 + w2**2) / (w1 * w2) * xs**2 + w1 * w2 * ys**2) * psi
           - Rational(1, 2) * w1 * w2 * sp.diff(psi, xs, 2)
           - xs * sp.diff(psi, ys))
check("B1c: H_PT psi0 == (w1+w2)/2 psi0",
      sp.simplify(sp.expand(HPT_psi / psi - (w1 + w2) / 2)) == 0)

# B2: fidelity with the two-oscillator vacuum phi0 ~ exp(-(x^2/w2 + w1 y^2)/2):
Avac = sp.Matrix([[1 / w2, 0], [0, w1]])
f = sp.simplify(sp.sqrt(sp.det(Apt) * sp.det(Avac)) / sp.det((Apt + Avac) / 2))
f_target = 4 * w1 * sp.sqrt(w1**2 + w1 * w2 + w2**2) / (4 * w1**2 + 3 * w1 * w2 + w2**2)
check("B2a: fidelity |<phi0|psi0>|^2 closed form", sp.simplify(f - f_target) == 0)
check("B2b: UV/equal-frequency limit = sqrt(3)/2",
      sp.simplify(f.subs(w1, w2) - sp.sqrt(3) / 2) == 0)

# B3: particle content via covariance algebra:
Sig = (2 * Apt).inv()
c1 = sp.Matrix([1 / sp.sqrt(w2) - sp.sqrt(w2) * A11v, -sp.sqrt(w2) * A12v])
c2 = sp.Matrix([-A12v / sp.sqrt(w1), sp.sqrt(w1) - A22v / sp.sqrt(w1)])
N1 = sp.simplify((c1.T * Sig * c1)[0, 0] / 2)
N2 = sp.simplify((c2.T * Sig * c2)[0, 0] / 2)
N_target = w2 * (w1**2 + w2**2) / (2 * w1 * (w1**2 + w1 * w2 + w2**2))
check("B3a: <N1> == <N2> (equipartition across the pair)", sp.simplify(N1 - N2) == 0)
check("B3b: <N> closed form", sp.simplify(N1 + N2 - N_target) == 0)
check("B3c: UV/equal-frequency limit <N> = 1/3",
      sp.simplify(N_target.subs(w1, w2) - Rational(1, 3)) == 0)

# B4: exact momentum-space rapidity for the fourth-order field:
k, m1, m2 = sp.symbols("k m1 m2", positive=True)
o1 = sp.sqrt(k**2 + m1**2); o2 = sp.sqrt(k**2 + m2**2)
r_of_k = sp.log((o1 + o2) / (o1 - o2))
r_target = sp.log((o1 + o2)**2 / (m1**2 - m2**2))
# log identity <=> (w1-w2)(w1+w2) = m1^2 - m2^2 (all arguments positive for m1>m2):
check("B4: (w1(k)-w2(k))(w1(k)+w2(k)) == m1^2 - m2^2, hence "
      "r(k) = log[(w1+w2)^2/(m1^2-m2^2)] exactly",
      sp.simplify((o1 - o2) * (o1 + o2) - (m1**2 - m2**2)) == 0)

# B5: Hilbert-scale corollary: spec(M_obs(k)) = {e^{+-r(k)}} with
#     e^{r(k)} = (w1+w2)^2/(m1^2-m2^2): k->infty ratio to k^2 equals 4/(m1^2-m2^2);
#     k->0 value (m1+m2)/(m1-m2).
er = (o1 + o2)**2 / (m1**2 - m2**2)
check("B5a: lim e^{r(k)}/k^2 = 4/(m1^2-m2^2)",
      sp.simplify(sp.limit(er / k**2, k, sp.oo) - 4 / (m1**2 - m2**2)) == 0)
check("B5b: e^{r(0)} = (m1+m2)/(m1-m2)",
      sp.simplify(er.subs(k, 0) - (m1 + m2) / (m1 - m2)) == 0)

# B6: UV limits of fidelity and <N> along the field dispersion (k -> infinity):
check("B6a: lim_k f(k) = sqrt(3)/2",
      sp.simplify(sp.limit(f_target.subs({w1: o1, w2: o2}), k, sp.oo) - sp.sqrt(3) / 2) == 0)
check("B6b: lim_k <N>(k) = 1/3",
      sp.simplify(sp.limit(N_target.subs({w1: o1, w2: o2}), k, sp.oo) - Rational(1, 3)) == 0)

print("\nALL PASS" if PASS else "\nSOME CHECKS FAILED")
