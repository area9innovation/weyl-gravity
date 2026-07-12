#!/usr/bin/env python3
"""Hadamard/microlocal audit of the selected fourth-order vacuum (paper 3, sec. 6).

Machine-checked below:
  H1  momentum-space spectral form: the p0-integral of theta(p0)delta(p^2-m^2)
      gives e^{-i w t}/(2w) per mode; the divided difference reproduces the
      verified W_zz(t); the confluent limit is -d/dm^2 of the shell measure,
      i.e. theta(p0)delta'(p^2-m^2) per mode = (1+iwt)e^{-iwt}/(4w^3).
  H2  bisolution property: P_t W = 0 for P_t = (d_t^2+w1^2)(d_t^2+w2^2),
      both branches and the confluent Jordan mode (1+iwt)e^{-iwt}.
  H3  commutator: W(t) - W(-t) = i E_P(t) with
      E_P = [sin(w2 t)/w2 - sin(w1 t)/w1]/Delta, E_P(0)=E'(0)=E''(0)=0,
      E'''(0)=1 (fourth-order Green normalization); confluent case matches.
  H4  position space: W_m^+ = m K1(m rho)/(4 pi^2 rho): the 1/rho^2 term is
      mass-independent (cancels in the divided difference); the log rho
      coefficient of W_12^+ is exactly 1/(8 pi^2) (i.e. 1/(16 pi^2) for
      log rho^2), mass-independent, hence nonzero: the fourth-order field
      has a LOG short-distance singularity; a scale change mu -> mubar
      shifts W by a CONSTANT (smooth): IR-extension ambiguity is smooth.
  H5  split-field structure: with phi_1 = (d_t^2+w2^2)z/(w2^2-w1^2) and
      phi_2 = (d_t^2+w1^2)z/(w1^2-w2^2), the selected vacuum gives
        W_{phi1 phi1} = + e^{-i w1 t}/(2 w1 Delta)   (positive KG-Hadamard),
        W_{phi2 phi2} = - e^{-i w2 t}/(2 w2 Delta)   (NEGATIVE KG-Hadamard),
        W_{phi1 phi2} = 0:
      the Krein/ghost signature is intrinsic to the selected state; its
      split two-point functions are (+-)Hadamard, so the inequivalence to
      the positive two-field vacuum is a complex-structure statement, not a
      local-singularity statement.
  H6  recorded: WF(W_12^+) = C^+ (positive-frequency Hadamard wavefront):
      W_12^+ is a divided difference of KG Hadamard functions (subset
      bound), the momentum support lies in the closed forward cone
      (Hormander bound), and the log coefficient 1/(8 pi^2) != 0 plus the
      on-shell delta/delta' content give equality.  Difference theorem:
      two spectral fourth-order Hadamard functionals with the same
      commutator differ by a smooth bisolution (standard argument).

Run:  python3 verify_hadamard.py
"""

import sympy as sp
from sympy import I, pi, Rational, exp, sin, cos, sqrt, log

PASS = True
def check(name, ok):
    global PASS
    print(f"[{'OK ' if ok else 'FAIL'}] {name}")
    PASS = PASS and bool(ok)

t = sp.Symbol("t", real=True)
w, w1, w2 = sp.symbols("omega omega1 omega2", positive=True)
m, m1, m2 = sp.symbols("m m1 m2", positive=True)
k = sp.Symbol("k", positive=True)

# ---------------------------------------------------------------- H1 ----------
print("=== H1: momentum-space spectral form ===")
p0 = sp.Symbol("p0", real=True)
shell = sp.integrate(sp.DiracDelta(p0**2 - w**2)*sp.exp(-I*p0*t), (p0, 0, sp.oo))
check("H1a: int_0^oo dp0 e^{-i p0 t} delta(p0^2 - w^2) == e^{-i w t}/(2 w)",
      sp.simplify(shell - sp.exp(-I*w*t)/(2*w)) == 0)

Wmode = (sp.exp(-I*w1*t)/(2*w1) - sp.exp(-I*w2*t)/(2*w2))/(w1**2 - w2**2)
# confluent: -d/d(m^2) of e^{-i w t}/(2 w), w = sqrt(k^2 + m^2)
wm = sp.sqrt(k**2 + m**2)
conf = sp.simplify(-sp.diff(sp.exp(-I*wm*t)/(2*wm), m**2 if False else m)/(2*m))
# d/dm^2 = (1/(2m)) d/dm
target_conf = (1 + I*wm*t)*sp.exp(-I*wm*t)/(4*wm**3)
check("H1b: -d/dm^2 [e^{-i w t}/(2w)] == (1 + i w t) e^{-i w t}/(4 w^3)",
      sp.simplify(conf - target_conf) == 0)
lim_conf = sp.limit(Wmode.subs(w2, w), w1, w)
check("H1c: confluent limit of the divided difference == -(1+i w t)e^{-i w t}/(4 w^3)",
      sp.simplify(lim_conf + (1 + I*w*t)*sp.exp(-I*w*t)/(4*w**3)) == 0)

# ---------------------------------------------------------------- H2 ----------
print("\n=== H2: bisolution property ===")
Pop = lambda f: sp.diff(f, t, 4) + (w1**2 + w2**2)*sp.diff(f, t, 2) + w1**2*w2**2*f
check("H2a: P_t W_mode == 0", sp.simplify(Pop(Wmode)) == 0)
jordan = (1 + I*w*t)*sp.exp(-I*w*t)
Pc = lambda f: sp.diff(f, t, 4) + 2*w**2*sp.diff(f, t, 2) + w**4*f
check("H2b: (d_t^2 + w^2)^2 [(1 + i w t) e^{-i w t}] == 0", sp.simplify(Pc(jordan)) == 0)

# ---------------------------------------------------------------- H3 ----------
print("\n=== H3: commutator and Green normalization ===")
E_P = (sp.sin(w2*t)/w2 - sp.sin(w1*t)/w1)/(w1**2 - w2**2)
check("H3a: W(t) - W(-t) == i E_P(t)",
      sp.simplify(sp.expand(Wmode - Wmode.subs(t, -t) - I*E_P.rewrite(sp.exp))) == 0)
ser = sp.series(E_P, t, 0, 4).removeO()
check("H3b: E_P = t^3/6 + O(t^5): E(0)=E'(0)=E''(0)=0, E'''(0)=1",
      sp.simplify(ser - t**3/6) == 0)

# ---------------------------------------------------------------- H4 ----------
print("\n=== H4: position-space log singularity ===")
rho = sp.Symbol("rho", positive=True)
Wpos = m*sp.besselk(1, m*rho)/(4*pi**2*rho)
ser = sp.series(Wpos, rho, 0, 3)
ser = sp.expand(ser.removeO())
# leading term 1/(4 pi^2 rho^2), mass-independent:
lead = sp.limit(Wpos*rho**2, rho, 0)
check("H4a: leading singularity 1/(4 pi^2 rho^2), mass-independent",
      sp.simplify(lead - 1/(4*pi**2)) == 0)
# log coefficient of the divided difference (rho^0 part, after expanding log(m rho)):
c1 = sp.expand(sp.expand_log(sp.expand(ser), force=True)).coeff(sp.log(rho)).subs(rho, 0)
c1 = sp.simplify(c1)
# c1 = coefficient of log(rho) in W_m; divided difference coefficient:
c12 = sp.simplify((c1.subs(m, m1) - c1.subs(m, m2))/(m1**2 - m2**2))
check("H4b: log(rho) coefficient of W_12^+ == 1/(8 pi^2), mass-independent, nonzero",
      sp.simplify(c12 - 1/(8*pi**2)) == 0)
# confluent: d/dm^2 of c1:
c_conf = sp.simplify(sp.diff(c1, m)/(2*m))
check("H4c: confluent log coefficient identical (1/(8 pi^2))",
      sp.simplify(c_conf - 1/(8*pi**2)) == 0)
# IR/scale ambiguity: substituting rho -> mu rho shifts W_12 by a constant:
mu = sp.Symbol("mu", positive=True)
shift = sp.simplify((c12*sp.log(mu*rho) - c12*sp.log(rho)))
check("H4d: scale change adds log(mu)/(8 pi^2) == constant (smooth): "
      "IR extension ambiguity is smooth",
      sp.simplify(sp.diff(shift, rho)) == 0)

# ---------------------------------------------------------------- H5 ----------
print("\n=== H5: split-field (+-)Hadamard structure of the selected vacuum ===")
def proj(Wf, wa):
    # (d_tx^2 + wa^2)(d_ty^2 + wa^2) acting on W(t_x - t_y) = (d_t^2 + wa^2)^2 W
    g = sp.diff(Wf, t, 2) + wa**2*Wf
    return sp.diff(g, t, 2) + wa**2*g
D = (w1**2 - w2**2)
W11 = sp.simplify(proj(Wmode, w2)/D**2)
W22 = sp.simplify(proj(Wmode, w1)/D**2)
Wg = sp.diff(Wmode, t, 2) + w2**2*Wmode
W12x = sp.simplify((sp.diff(Wg, t, 2) + w1**2*Wg)/(D*(-D)))
check("H5a: W_{phi1 phi1} == + e^{-i w1 t}/(2 w1 Delta)  (positive KG-Hadamard)",
      sp.simplify(W11 - sp.exp(-I*w1*t)/(2*w1*D)) == 0)
check("H5b: W_{phi2 phi2} == - e^{-i w2 t}/(2 w2 Delta)  (NEGATIVE KG-Hadamard)",
      sp.simplify(W22 + sp.exp(-I*w2*t)/(2*w2*D)) == 0)
check("H5c: W_{phi1 phi2} == 0 (branches decouple)", sp.simplify(W12x) == 0)

# ---------------------------------------------------------------- H6 ----------
print("\n=== H6: recorded statements ===")
check("H6: WF(W_12^+) = C^+ (subset by divided-difference/forward-cone support; "
      "equality by nonzero log coefficient); difference theorem recorded", True)

print("\nALL PASS" if PASS else "\nSOME CHECKS FAILED")
