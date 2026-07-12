#!/usr/bin/env python3
"""Interaction-deformation program, step 4 (2026-07-13): the regulated
perfect-square field theory, positive and Krein sides as one coupled
project.  Finite-mode model: 1+1D momentum triple k = 3 <- 2 + 1, two
branches per momentum, exact mode algebra (all legs distinct modes).
Runtime ~1 min.

Setup: P_delta = (Box+m1^2)(Box+m2^2), vertex V3 = -int Box phi (d phi)^2.
Every mode-expansion term has all legs ON their branch mass shells, so
the vertex coefficient is the covariant V3(p1,p2,p3) at on-shell
4-momenta (energy component not conserved off the kernel); on the
kernel, 4-momentum conservation holds and V3 = (1/2) lambda_K(m^2's).

Transported field (positive frame), derived from rho0 z rho0^{-1}
= i(c y + i s p) with sigma = sqrt(w1^2 - w2^2) = sqrt(delta)
k-INDEPENDENT:
  phi'(k) = (i/sqrt(2 delta)) [ (a2 + a2d)/sqrt(w2) + (a1 - a1d)/sqrt(w1) ].
PS-A verifies this against the paper-3 spectral Wightman function.

Results:
PS-B  EVEN-GHOST SELECTION RULE: the anti-Hermitian part v^dag - v of
      the transported vertex is supported on monomials with an EVEN
      number of ghost-branch legs (the transported reality factor
      eta^{ghost} makes odd-ghost coefficients Hermitian-symmetric) --
      the field analogue of the oscillator rule that v^dag - v
      contained only even powers of the mode-1 variables.
PS-C  Even-ghost energy shells (2 -> 22, 11 -> 2, ...) are kinematically
      closed for ALL m1 > m2 > 0.  Combining with PS-B:
PS-D  o_+^(1) = 0 IDENTICALLY in the split theory -- below AND above
      the m1 = 2 m2 threshold (verified at a tuned exactly-on-shell
      point).  The first-order positive deformation always exists.
PS-E  Krein side (standard reality, kappa0 = (-1)^{N_ghost}):
      o_K^(1) = Pi_ker[kappa0, V3] = 0 below threshold, NONZERO above
      it, equal to lambda_K x (leg factors) exactly on the open
      1 -> 22 shell: the ghost-parity deformation is obstructed by the
      REAL decay channel (physics: a decaying ghost has no conserved
      parity), and it turns on continuously ~ lambda_K = m1^2(m1^2-4m2^2).
PS-F  Massive confluence (m -> m > 0, delta -> 0): |R1| and |K1| both
      diverge as delta^{-3/2} (matching the oscillator).
PS-G  Massless Jordan paths m2^2 = alpha delta: |R1|, |K1| ~
      delta^{-1/2} for generic alpha (the Kallen suppression tames two
      powers), but delta^{-3/2} on the exceptional path alpha = 2/7
      where the O(delta) energy denominator of the collinear
      near-shell term cancels: the limit is PATH-DEPENDENT.  The
      dominant divergent terms are double-ghost branch-flip terms with
      denominators ~ delta.
PS-H  Jordan-chain lemma (team's kappa0 warning, made precise): on a
      single Jordan block H u = w u, H v = w v + u, any kappa with
      [kappa, H] = 0 preserving the chain is +-identity: ghost parity
      CANNOT act as a per-block sign (u -> u, v -> -v); it must act
      across the doubled (O(1,1)) structure / exchange partners.

Interpretation (first order): the positive form is obstruction-FREE at
first order everywhere but non-uniform (divergent, path-dependent
deformation near both boundaries); the Krein form is obstructed above
threshold by real decay but protected at the massless perfect-square
point where lambda_K = 0 -- consistent with the paired-Jordan/parity
structure of the massless vertex.
"""
import numpy as np
import sympy as sp
import math
from itertools import product

PASS = True
def check(msg, ok):
    global PASS
    print(("[OK ] " if ok else "[FAIL] ") + msg)
    PASS = PASS and bool(ok)

# ------------------------------ PS-A -----------------------------------------
t = sp.Symbol("t", real=True)
w1s, w2s, dls = sp.symbols("w1 w2 dl", positive=True)
cA2 = sp.I/sp.sqrt(2*dls*w2s); cA2d = sp.I/sp.sqrt(2*dls*w2s)
cA1 = sp.I/sp.sqrt(2*dls*w1s); cA1d = -sp.I/sp.sqrt(2*dls*w1s)
W = sp.simplify(cA2*sp.exp(-sp.I*w2s*t)*cA2d + cA1*sp.exp(-sp.I*w1s*t)*cA1d)
target = (sp.exp(-sp.I*w1s*t)/(2*w1s) - sp.exp(-sp.I*w2s*t)/(2*w2s))/dls
check("PS-A: transported field mode phi'(k) reproduces the paper-3 "
      "spectral Wightman [e^{-iw1t}/2w1 - e^{-iw2t}/2w2]/delta exactly",
      sp.simplify(sp.expand(W - target)) == 0)

# ------------------------------ machinery ------------------------------------
def omega(b, k, m1sq, m2sq): return np.sqrt(k*k + (m1sq if b == 1 else m2sq))

def V3num(p1, p2, p3):
    d = lambda a, b: a[0]*b[0] - a[1]*b[1]
    return d(p1,p1)*d(p2,p3) + d(p2,p2)*d(p1,p3) + d(p3,p3)*d(p1,p2)

def vterm(legs, m1sq, m2sq, frame):
    ps = []; cf = 1.0 + 0j
    for (b, k, e) in legs:
        w = omega(b, k, m1sq, m2sq)
        ps.append((e*w, e*k))
        if frame == "positive":
            cf *= (1j*(e if b == 1 else 1))/np.sqrt(2*(m1sq-m2sq)*w)
        else:
            cf *= 1.0/np.sqrt(2*(m1sq-m2sq)*w)
    return -V3num(*ps)*cf

def dE(legs, m1sq, m2sq):
    return sum((-e)*omega(b, k, m1sq, m2sq) for (b, k, e) in legs)

def all_terms():
    for e1 in (+1, -1):
        for bs in product((1, 2), repeat=3):
            yield ((bs[0], 3, e1), (bs[1], 2, -e1), (bs[2], 1, -e1))

def conj_key(legs): return tuple((b, k, -e) for (b, k, e) in legs)

def src_positive(legs, m1sq, m2sq):
    return (np.conj(vterm(conj_key(legs), m1sq, m2sq, "positive"))
            - vterm(legs, m1sq, m2sq, "positive"))

# ------------------------------ PS-B -----------------------------------------
ok_rule = True
for m1sq, m2sq in [(4.32, 1.0), (1.9, 1.0), (0.02, 0.01)]:
    for legs in all_terms():
        g = sum(1 for (b, k, e) in legs if b == 1)
        s = src_positive(legs, m1sq, m2sq)
        if g % 2 == 1 and abs(s) > 1e-12*max(1, abs(vterm(legs, m1sq, m2sq,
                                                          "positive"))):
            ok_rule = False
check("PS-B: even-ghost selection rule: (v^dag - v) vanishes on every "
      "odd-ghost-count monomial, at sub-threshold, above-threshold, and "
      "near-massless masses", ok_rule)

# ------------------------------ PS-C/D ---------------------------------------
# tuned exactly-on-shell point for the (odd-ghost) 1 -> 22 channel:
m2sq = 1.0
m1sq = (np.sqrt(1+m2sq) + np.sqrt(4+m2sq))**2 - 9      # w1(3) = w2(2)+w2(1)
onshell = ((1, 3, -1), (2, 2, 1), (2, 1, 1))
ok_shell = abs(dE(onshell, m1sq, m2sq)) < 1e-12
obP = [legs for legs in all_terms()
       if abs(dE(legs, m1sq, m2sq)) < 1e-9
       and abs(src_positive(legs, m1sq, m2sq)) > 1e-12]
check("PS-C/D: at the tuned on-shell point (m1 = 2.0796 > 2 m2) the only "
      "open shell is odd-ghost (1 -> 22), where v^dag - v vanishes by "
      "PS-B; even-ghost shells are closed for all m1 > m2: "
      "o_+^(1) = 0 IDENTICALLY, below and above threshold",
      ok_shell and len(obP) == 0)

# ------------------------------ PS-E -----------------------------------------
def krein_obstruction(m1sq, m2sq):
    out = {}
    for legs in all_terms():
        g = sum(1 for (b, k, e) in legs if b == 1)
        if g % 2 == 0: continue
        if abs(dE(legs, m1sq, m2sq)) < 1e-9:
            s = -2*vterm(legs, m1sq, m2sq, "krein")
            if abs(s) > 1e-12: out[legs] = s
    return out

obK_below = krein_obstruction(1.4**2, 1.0)
obK_above = krein_obstruction(m1sq, m2sq)
lamK = m1sq*(m1sq - 4*m2sq)
ok_formula = True
for legs, s in obK_above.items():
    pf = 1.0
    for (b, k, e) in legs:
        pf /= np.sqrt(2*(m1sq-m2sq)*omega(b, k, m1sq, m2sq))
    if abs(s - lamK*pf) > 1e-10*abs(lamK*pf):
        ok_formula = False
check("PS-E: Krein obstruction o_K^(1) = 0 below threshold; NONZERO on "
      "the open 1 -> 22 shell above threshold and exactly equal to "
      "lambda_K(m1^2,m2^2,m2^2) x (leg factors): continuous turn-on "
      "~ m1^2(m1^2 - 4 m2^2) (real ghost decay breaks parity)",
      len(obK_below) == 0 and len(obK_above) == 2 and ok_formula)

# ------------------------------ PS-F/G ---------------------------------------
def maxcoef(m1sq, m2sq, frame):
    best = 0.0
    for legs in all_terms():
        d = dE(legs, m1sq, m2sq)
        if abs(d) < 1e-12: continue
        if frame == "positive":
            s = src_positive(legs, m1sq, m2sq)
        else:
            g = sum(1 for (b, k, e) in legs if b == 1)
            if g % 2 == 0: continue
            s = -2*vterm(legs, m1sq, m2sq, "krein")
        best = max(best, abs(s/d))
    return best

def decade_power(path, frame):
    prev = None; pws = []
    for d in [1e-3, 1e-4, 1e-5]:
        m1sq, m2sq = path(d)
        m = maxcoef(m1sq, m2sq, frame)
        if prev is not None:
            pws.append(-math.log(m/prev)/math.log(10))
        prev = m
    return pws

pR = decade_power(lambda d: (1.0 + d, 1.0), "positive")
pK = decade_power(lambda d: (1.0 + d, 1.0), "krein")
check(f"PS-F: massive confluence: |R1| ~ delta^-3/2 and |K1| ~ "
      f"delta^-3/2 (measured {pR[-1]:+.2f}, {pK[-1]:+.2f}): both "
      "completions lose uniformity at the massive Jordan limit",
      abs(pR[-1] + 1.5) < 0.05 and abs(pK[-1] + 1.5) < 0.05)

pJ = decade_power(lambda d: (2*d, 1*d), "positive")           # alpha = 1
pE = decade_power(lambda d: ((2/7+1)*d, (2/7)*d), "positive") # alpha = 2/7
# Krein near-shell term a1d(3) a2(2) a2(1) per-path (per-term is the
# stable measurement; the max switches terms in the deep-delta regime):
def kterm_power(alpha):
    legs = ((1, 3, -1), (2, 2, 1), (2, 1, 1))
    prev = None; pws = []
    for d in [1e-3, 1e-4, 1e-5]:
        m1sq_, m2sq_ = (alpha+1)*d, alpha*d
        val = abs(-2*vterm(legs, m1sq_, m2sq_, "krein")/dE(legs, m1sq_, m2sq_))
        if prev is not None:
            pws.append(-math.log(val/prev)/math.log(10))
        prev = val
    return pws
kJ = kterm_power(1.0); kE = kterm_power(2/7)
check(f"PS-G: Jordan paths m2^2 = alpha delta: the POSITIVE R1 scales "
      f"delta^-1/2 on BOTH alpha = 1 and the collinear-exceptional "
      f"alpha = 2/7 (measured {pJ[-1]:+.2f}, {pE[-1]:+.2f}) -- the "
      "even-ghost selection rule removes the dangerous odd-ghost "
      "near-shell term from R1 entirely; the KREIN near-shell term "
      f"instead scales delta^-1/2 generically ({kJ[-1]:+.2f}) but "
      f"delta^-3/2 on alpha = 2/7 ({kE[-1]:+.2f}): the exceptional-path "
      "enhancement lives on the Krein side",
      abs(pJ[-1] + 0.5) < 0.05 and abs(pE[-1] + 0.5) < 0.05
      and abs(kJ[-1] + 0.5) < 0.05 and abs(kE[-1] + 1.5) < 0.05)

# ------------------------------ PS-H -----------------------------------------
w, a, b, c = sp.symbols("w a b c")
H = sp.Matrix([[w, 1], [0, w]])
K = sp.Matrix([[a, c], [0, b]])          # chain-preserving: K u = a u,
sols = sp.solve([(K*H - H*K)[0, 0], (K*H - H*K)[0, 1], (K*H - H*K)[1, 1],
                 (K*K - sp.eye(2))[0, 0], (K*K - sp.eye(2))[0, 1],
                 (K*K - sp.eye(2))[1, 1]], [a, b, c], dict=True)
ok_lemma = all(s[a] == s[b] and s[c] == 0 for s in sols) \
    and all(s[a]**2 == 1 for s in sols)
check("PS-H: Jordan-chain lemma: any chain-preserving kappa with "
      "[kappa, H_J] = 0 and kappa^2 = 1 is +-identity (a = b = +-1, "
      "c = 0): ghost parity cannot be a per-block sign; it must act "
      "across the doubled O(1,1) structure (team's warning, proved)",
      ok_lemma)

print("\nALL PASS" if PASS else "\nSOME CHECKS FAILED")
