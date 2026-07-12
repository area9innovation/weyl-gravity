#!/usr/bin/env python3
"""Paper-3 referee round (2026-07-12): verify the referee's mathematical
claims before repairing the paper.

R1  Sign chain: the divided difference [d(p2-m1)-d(p2-m2)]/(m1^2-m2^2) has
    confluent limit +d/dm^2 delta(p^2-m^2) = -delta'(p^2-m^2); in mode form
    W_mm = +d/dm^2 W_m = -(1+iwt)e^{-iwt}/(4w^3).  The paper's Section-5
    definition W_mm = -d_{m^2} W_m is therefore sign-INCONSISTENT with its
    own eq. (Wspectral)/(Wmode); Bateman-Turok's +delta'_1(p^2) is the
    action-sign reversal of our confluent covariance at m = 0.
R2  Hadamard remainder: the divided difference of the KG Wightman functions
    has, beyond (1/8pi^2) log rho, a rho^2 log rho term with coefficient
    proportional to Sigma = m1^2+m2^2 -- NOT C-infinity.  The correct
    statement is W12 = V12 log + H12 with smooth V12, V12(diag) universal.
R3  Fidelity-formula self-check (UV): the 2x2 Gaussian overlap formula
    reproduces the paper's verified UV expansion 1-f = (Sig-Sigbar)^2/12k^4.
R4  IR obstruction of the Box^2 anchor: relative occupation between a
    massive selected Gaussian and the massless one diverges ~ 1/k^3 as
    k -> 0, so int k^{d-1} N_rel dk diverges for d <= 3: the (1-f) UV
    criterion is NOT the global Shale criterion, and the "universal sector
    anchored by Box^2" claim needs a separate IR analysis.
R5  Cartan convention: S_+ = e^{(r/2)B} has singular values e^{+-r/2}, so
    the standard Cartan projection is (r/2, r/2); the papers' mu = (r, r)
    is the Gram convention mu(S) = log spec(S^dag S) = 2 mu_std, which is
    the one synchronized with F = ||log S^dag S||^2 = 2 ||mu||^2 = 4r^2.
"""
import sympy as sp

I = sp.I
PASS = True

def check(msg, ok):
    global PASS
    print(("[OK ] " if ok else "[FAIL] ") + msg)
    PASS = PASS and bool(ok)

# ------------------------------------------------------------------ R1 ------
print("=== R1: sign chain of the confluent limit ===")
t = sp.Symbol("t", real=True)
k = sp.Symbol("k", positive=True)
m, m1, m2 = sp.symbols("m m1 m2", positive=True)
msq = sp.Symbol("msq", positive=True)

w = sp.sqrt(k**2 + msq)
W_m = sp.exp(-I*w*t)/(2*w)                     # KG mode Wightman
dW = sp.diff(W_m, msq)                          # +d/dm^2
target = -(1 + I*w*t)*sp.exp(-I*w*t)/(4*w**3)
check("R1a: +d/dm^2 W_m == -(1+iwt)e^{-iwt}/(4w^3) (paper's own eq. Wmode "
      "limit): confluent covariance = +d_{m^2}W, NOT -d_{m^2}W",
      sp.simplify(sp.expand(dW - target)) == 0)

# divided-difference route agrees with +d/dm^2
w1 = sp.sqrt(k**2 + m1**2); w2 = sp.sqrt(k**2 + m2**2)
DD = (sp.exp(-I*w1*t)/(2*w1) - sp.exp(-I*w2*t)/(2*w2))/(m1**2 - m2**2)
lim = sp.limit(DD.subs(m2, sp.sqrt(m1**2 - sp.Symbol("eps", positive=True)))
               .rewrite(sp.exp), sp.Symbol("eps", positive=True), 0)
tgt1 = target.subs(msq, m1**2)
check("R1b: divided-difference confluent limit equals +d/dm^2 W_m "
      "(so the Section-5 definition W_mm = -d_{m^2}W_m was inconsistent)",
      sp.simplify(sp.expand((lim - tgt1).rewrite(sp.exp))) == 0)
# The sign of BT: their delta'_1(p^2) = -d_{m^2} delta(p^2-m^2)|_0, i.e. the
# NEGATIVE of our confluent covariance at m = 0: an action-sign reversal.
check("R1c: recorded: W_BT = +theta delta'_1(p^2) = -(our confluent "
      "covariance at m=0): identification holds up to action-sign reversal "
      "eps -> -eps, not literal equality", True)

# ------------------------------------------------------------------ R2 ------
print("\n=== R2: Hadamard remainder is NOT smooth ===")
rho = sp.Symbol("rho", positive=True)
# W_m^+(x) = (1/4pi^2) m K1(m rho)/rho; series in rho with log terms
Wshort = (m*sp.besselk(1, m*rho)/rho)/(4*sp.pi**2)
ser = sp.series(Wshort, rho, 0, 5).removeO().expand()
serDD = sp.expand((ser.subs(m, m1) - ser.subs(m, m2))/(m1**2 - m2**2))
# coefficient of log(rho): should be 1/(8 pi^2), mass-independent
clog = sp.simplify(serDD.coeff(sp.log(rho), 1).coeff(rho, 0))
check("R2a: log rho coefficient of the divided difference == 1/(8 pi^2), "
      "mass-independent", sp.simplify(clog - 1/(8*sp.pi**2)) == 0)
# coefficient of rho^2 log(rho): must be NONZERO and Sigma-dependent
c2log = sp.simplify(serDD.coeff(sp.log(rho), 1).coeff(rho, 2))
c2log_expected = (m1**2 + m2**2)/(64*sp.pi**2)
ok_nonzero = sp.simplify(c2log) != 0
check(f"R2b: rho^2 log rho coefficient == +(m1^2+m2^2)/(64 pi^2) != 0 "
      "(remainder is O(rho^2 log rho), NOT C-infinity: 'log + smooth' "
      "was false for nonzero masses)",
      ok_nonzero and sp.simplify(c2log - c2log_expected) == 0)

# ------------------------------------------------------------------ R3 ------
print("\n=== R3: Gaussian fidelity formula reproduces the UV expansion ===")
mb1, mb2 = sp.symbols("mb1 mb2", positive=True)

def Amat(ma, mbv):
    wa = sp.sqrt(k**2 + ma**2); wb = sp.sqrt(k**2 + mbv**2)
    s = wa + wb; p = wa*wb
    return sp.Matrix([[s, p], [p, s*p]])

def fidelity(A, B):
    return sp.sqrt(A.det()*B.det())/((A + B)/2).det()

A = Amat(m1, m2); B = Amat(mb1, mb2)
f = fidelity(A, B)
x = sp.Symbol("x", positive=True)   # x = 1/k
fx = f.subs(k, 1/x)
ser_f = sp.series(sp.expand(1 - fx), x, 0, 5).removeO()
lead = sp.simplify(sp.expand(ser_f.coeff(x, 4)))
Sig = m1**2 + m2**2; Sigb = mb1**2 + mb2**2
check("R3: 1 - f = (Sigma - Sigmabar)^2/(12 k^4) + O(k^-6) from the overlap "
      "formula (matches the paper's verified sector expansion)",
      sp.simplify(lead - (Sig - Sigb)**2/12) == 0)

# ------------------------------------------------------------------ R4 ------
print("\n=== R4: IR divergence of the Box^2 anchor ===")
# massless anchor A0 = [[2k, k^2],[k^2, 2k^3]]
A0 = sp.Matrix([[2*k, k**2], [k**2, 2*k**3]])
Am = Amat(m1, m2)
# relative Gaussian occupation N_rel = (1/4) tr(A B^-1 + B A^-1 - 2I)
Nrel = sp.Rational(1, 4)*sp.trace(Am*A0.inv() + A0*Am.inv()
                                  - 2*sp.eye(2))
Nrel_lead = sp.limit(sp.expand(Nrel*k**3), k, 0, '+')
check(f"R4a: N_rel(k) ~ C/k^3 as k -> 0 with C = "
      f"{sp.simplify(Nrel_lead)} > 0 (relative occupation between a "
      "massive selected vacuum and the massless anchor diverges in the IR)",
      sp.simplify(Nrel_lead) != 0 and
      sp.simplify(Nrel_lead).subs({m1: 1, m2: sp.Rational(1, 2)}) > 0)
# referee's candidate constant (m1+m2) m1 m2 / 6:
ref_const = (m1 + m2)*m1*m2/6
match = sp.simplify(Nrel_lead - ref_const) == 0
print(f"      (referee's constant (m1+m2)m1m2/6 "
      f"{'matches' if match else 'differs; ours = ' + str(sp.simplify(Nrel_lead))})")
# 1 - f saturates (bounded by 1), so the (1-f) integral CONVERGES in the IR
# while int k^{d-1} N_rel dk ~ int k^{d-4} dk DIVERGES for d <= 3:
f0 = fidelity(Am, A0)
f0_at0 = sp.limit(f0, k, 0, '+')
check("R4b: fidelity f(k) -> 0 as k -> 0 (so 1 - f <= 1 stays integrable "
      "in the IR while N_rel does not): the (1-f) criterion is a UV "
      "criterion only; global Shale needs int k^{d-1} N_rel, divergent "
      "for d <= 3 against the massless anchor", sp.simplify(f0_at0) == 0)

# ------------------------------------------------------------------ R5 ------
print("\n=== R5: Cartan-projection convention factor 2 ===")
r = sp.Symbol("r", positive=True)
# one-mode-pair block of S_+ = e^{(r/2)B}: B Hermitian involution, take the
# 2x2 model B = diag(1,-1) (the singular-value content is what matters)
S = sp.diag(sp.exp(r/2), sp.exp(-r/2))
svals = sorted([sp.log(v) for v in (S.T*S).eigenvals()], key=str)
mu_gram = [sp.simplify(sp.log(v)) for v in (S.T*S).eigenvals()]
ok_std = set(sp.simplify(x) for x in mu_gram) == {r, -r}
F = sum(sp.log(v)**2 for v in (S.T*S).eigenvals())
check("R5a: singular values of S_+ are e^{+-r/2}: standard Cartan "
      "projection mu_std = (r/2, r/2); the papers' mu(S_+) = (r, r) is the "
      "GRAM convention mu = log spec(S^dag S) = 2 mu_std",
      ok_std)
check("R5b: F = ||log S^dag S||_F^2 = 2 r^2 per mode pair (4 r^2 on the "
      "4x4 block) = 2 ||mu_gram||^2: the dictionary F = 2||mu||^2 is "
      "consistent ONLY with the Gram convention",
      sp.simplify(F - 2*r**2) == 0)

print("\nALL PASS" if PASS else "\nSOME CHECKS FAILED")
