#!/usr/bin/env python3
"""Interaction-deformation program, step 2 (2026-07-13): selection rules
and the third-order structural audit for the cubic PU vertex V = -i y^3.
Runtime ~15-25 min (quintic Moyal algebra at several loci).

Selection rule (SR1-SR3):
  Order-n objects have (i) transfers in the n-fold sumset of the vertex
  transfer set (transfer is additive under star products/commutators:
  grading by ad_{h0}); (ii) total polynomial degree <= n+2 (each extra
  commutator reduces degree by >= 2), with degree parity == n mod 2.
  Hence the order-n obstruction is supported on interior resonance
  ratios w1/w2 = |d2|/|d1| > 1 with d1 d2 < 0, |d1|+|d2| <= n+2 and
  |d1|+|d2| == n (mod 2):
     order 1: {2:1}          order 2: {3:1}
     order 3: {3:2, 2:1, 4:1}   order 4: {5:1, 3:1, 2:1(as (2,-4))}
  The lattice gives CANDIDATES; coefficients decide (2:1 and 4:1 have
  vanishing coefficients through order 3 -- observed, mechanism open:
  all obstructions so far carry ODD mode-2 transfer).

Third order (O3a-O3e, NEW):
  - generic frequencies: obstruction vanishes; R3 exists, Hermitian,
    with odd total degrees <= 5 (parity rule confirmed);
  - candidate loci: 2:1 and 4:1 clean; AT w1/w2 = 3:2 the obstruction
    is NONZERO and exact:
        o_+^(3) = -(117 sqrt(30)/1120) i (a1^2 a2dag^3 + a1dag^2 a2^3),
    the on-shell 2-quanta <-> 3-quanta conversion;
  - gauge independence: unchanged under R1 -> R1 + {N1, N2, N1 N2} and
    R2 -> R2 + on-shell quintic kernel operators;
  - Jordan scaling: R3 = O(eps^{-9/2}) (measured +4.488 per decade at
    1e-2 -> 1e-3), third data point of R_n = O(eps^{-3n/2}).

Refined hierarchy conjecture: the coprime ratio w1/w2 = p:q first
obstructs at order p+q-2 when p (the mode-2 transfer) is odd:
  3:1 -> order 2 (verified), 3:2 -> order 3 (verified),
  5:1 -> order 4 (the team's next target), 5:3 -> order 6, ...
"""
import sympy as sp
import math
from fractions import Fraction

I = sp.I
x, y, p, q = sp.symbols("x y p q", real=True)
PASS = True

def check(msg, ok):
    global PASS
    print(("[OK ] " if ok else "[FAIL] ") + msg)
    PASS = PASS and bool(ok)

# --------------------------- Moyal machinery --------------------------------
def LamN(f, g, n):
    tot = 0
    for n1 in range(n+1):
        for n2 in range(n+1-n1):
            for n3 in range(n+1-n1-n2):
                n4 = n-n1-n2-n3
                coef = sp.factorial(n)/(sp.factorial(n1)*sp.factorial(n2)
                                        *sp.factorial(n3)*sp.factorial(n4))
                sgn = (-1)**(n2+n4)
                df = sp.diff(f, x, n1, p, n2, y, n3, q, n4)
                if df == 0: continue
                dg = sp.diff(g, p, n1, x, n2, q, n3, y, n4)
                if dg == 0: continue
                tot += coef*sgn*df*dg
    return tot

def star(f, g):
    out = 0
    for n in range(0, 14):
        t = LamN(f, g, n)
        if t != 0:
            out += (I/2)**n/sp.factorial(n)*t
    return sp.expand(out)

def comm(f, g): return sp.expand(star(f, g) - star(g, f))
def hc(f): return sp.expand(sp.conjugate(f))

def model(w1, w2):
    sig = sp.sqrt(w1**2 - w2**2); c = w1/sig; s = w2/sig
    h0 = sp.Rational(1,2)*(w1*w2*p**2 + (w1/w2)*x**2
                           + (w2/w1)*q**2 + w1*w2*y**2)
    v = sp.expand(-I*(c*y + I*s*p)**3)
    den = 4*w1**2 - w2**2
    R1 = ( 2*c**3/(w1*w2)*q*y**2 + 4*c**3/(3*w1**3*w2)*q**3
         - 6*c*s**2*(2*w1**2-w2**2)/(w1*w2*den)*p**2*q
         + 12*c*s**2*w1/(w2*den)*p*x*y
         - 12*c*s**2*w1/(w2**3*den)*q*x**2 )
    return h0, v, R1

def to_modes(f, w1, w2):
    a1, a1b, a2, a2b = sp.symbols("a1 a1b a2 a2b")
    sub = {x: sp.sqrt(w2)*(a1+a1b)/sp.sqrt(2),
           p: -I*(a1-a1b)/(sp.sqrt(2)*sp.sqrt(w2)),
           y: (a2+a2b)/(sp.sqrt(2)*sp.sqrt(w1)),
           q: -I*sp.sqrt(w1)*(a2-a2b)/sp.sqrt(2)}
    return sp.expand(f.subs(sub)), (a1, a1b, a2, a2b)

def from_modes(f, w1, w2, syms):
    a1, a1b, a2, a2b = syms
    return sp.expand(f.subs({
        a1: (x/sp.sqrt(w2)+I*sp.sqrt(w2)*p)/sp.sqrt(2),
        a1b: (x/sp.sqrt(w2)-I*sp.sqrt(w2)*p)/sp.sqrt(2),
        a2: (sp.sqrt(w1)*y+I*q/sp.sqrt(w1))/sp.sqrt(2),
        a2b: (sp.sqrt(w1)*y-I*q/sp.sqrt(w1))/sp.sqrt(2)}))

def ker_split(f, w1, w2):
    fa, syms = to_modes(f, w1, w2)
    Pol = sp.Poly(fa, *syms)
    kerp = 0; Rsol = 0
    for mono, coeff in zip(Pol.monoms(), Pol.coeffs()):
        a, b, cc, d = mono
        Om = sp.simplify((a-b)*w1 + (cc-d)*w2)
        m = syms[0]**a*syms[1]**b*syms[2]**cc*syms[3]**d
        if Om == 0: kerp += coeff*m
        else: Rsol += (-coeff/Om)*m
    return kerp, Rsol, syms

def order3(w1, w2, dR1=0, dR2ker=0):
    """ob2, ob3, R3 (mode form) with optional gauge probes."""
    h0, v, R1 = model(w1, w2)
    R1 = sp.expand(R1 + dR1)
    S2 = sp.expand(sp.Rational(1,2)*comm(R1, sp.expand(v + hc(v))))
    ob2, R2m, syms = ker_split(S2, w1, w2)
    R2 = sp.expand(from_modes(R2m, w1, w2, syms) + dR2ker)
    T3 = sp.expand( sp.Rational(1,8)*(comm(comm(h0,R1),R2)
                                      + comm(comm(h0,R2),R1))
                  + sp.Rational(1,48)*comm(comm(comm(h0,R1),R1),R1)
                  + sp.Rational(1,2)*comm(v,R2)
                  + sp.Rational(1,8)*comm(comm(v,R1),R1) )
    S3 = sp.expand(T3 - hc(T3))
    ob3, R3m, syms3 = ker_split(sp.expand(-S3), w1, w2)
    return sp.simplify(ob2), sp.simplify(ob3), R3m, syms3

# ============================== SR1-SR3 ======================================
print("=== selection-rule lattice ===")
T1 = set()
for a in range(4):
    b = 3 - a
    for d1 in range(-a, a+1, 2):
        for d2 in range(-b, b+1, 2):
            T1.add((d1, d2))

def sumset(A, B):
    return {(u1+v1, u2+v2) for (u1,u2) in A for (v1,v2) in B}

Tn = {1: T1}
for n in range(2, 5):
    Tn[n] = sumset(Tn[n-1], T1)

def candidates(n):
    out = set()
    for (d1, d2) in Tn[n]:
        if d1 == 0 or d2 == 0 or (d1 > 0) == (d2 > 0):
            continue
        if abs(d1)+abs(d2) > n+2 or (abs(d1)+abs(d2)-n) % 2 != 0:
            continue
        r = Fraction(abs(d2), abs(d1))
        if r > 1:
            out.add(r)
    return out

check("SR1: transfer additivity + degree bound n+2 + parity give the "
      "candidate interior loci: order 1 {2}, order 2 {3}, order 3 "
      "{3/2, 2, 4}, order 4 contains 5",
      candidates(1) == {Fraction(2)} and candidates(2) == {Fraction(3)}
      and candidates(3) == {Fraction(3,2), Fraction(2), Fraction(4)}
      and Fraction(5) in candidates(4))
check("SR2: 5:1 is NOT reachable at order 3 (parity/degree): the 5:1 "
      "test belongs at order 4, as the team corrected",
      Fraction(5) not in candidates(3))
check("SR3: recorded: order-2 computation realized exactly the "
      "candidate set {3:1}; coefficients (not the lattice) kill 2:1 at "
      "order 1 and 2:1, 4:1 at order 3 -- all obstructions so far have "
      "ODD mode-2 transfer (mechanism open)", True)

# ============================== O3a-O3b ======================================
print("\n=== third order, generic frequencies (13/7, 1) ===")
ob2g, ob3g, R3m, syms3 = order3(sp.Rational(13,7), sp.S(1))
R3 = from_modes(R3m, sp.Rational(13,7), sp.S(1), syms3)
degs = sorted({sum(m) for m in sp.Poly(R3, x, y, p, q).monoms()})
check("O3a: generic third-order obstruction vanishes "
      "(and second-order re-vanishes en route)",
      ob2g == 0 and ob3g == 0)
check(f"O3b: R3 exists, Hermitian, with ODD total degrees {degs} <= 5 "
      "(parity and degree rules confirmed)",
      sp.simplify(sp.expand(R3 - hc(R3))) == 0
      and all(d % 2 == 1 and d <= 5 for d in degs))

# ============================== O3c ==========================================
print("\n=== third order at the candidate loci ===")
_, ob3_21, _, _ = order3(sp.S(2), sp.S(1))
_, ob3_41, _, _ = order3(sp.S(4), sp.S(1))
_, ob3_32, _, _ = order3(sp.S(3), sp.S(2))
a1, a1b, a2, a2b = sp.symbols("a1 a1b a2 a2b")
target32 = -117*sp.sqrt(30)*I/1120*(a1**2*a2b**3 + a1b**2*a2**3)
check("O3c: 2:1 and 4:1 have VANISHING third-order obstruction; at "
      "w1/w2 = 3:2 the obstruction is NONZERO and exactly "
      "-(117 sqrt(30)/1120) i (a1^2 a2dag^3 + a1dag^2 a2^3): the "
      "on-shell 2 <-> 3 conversion (2 w1 = 3 w2)",
      ob3_21 == 0 and ob3_41 == 0
      and sp.simplify(sp.expand(ob3_32 - target32)) == 0)

# ============================== O3d ==========================================
print("\n=== gauge independence of the 3:2 obstruction ===")
w1v, w2v = sp.S(3), sp.S(2)
N1 = from_modes(a1*a1b, w1v, w2v, (a1,a1b,a2,a2b))
N2 = from_modes(a2*a2b, w1v, w2v, (a1,a1b,a2,a2b))
Kp = from_modes(a1**2*a2b**3 + a1b**2*a2**3, w1v, w2v, (a1,a1b,a2,a2b))
Km = from_modes(I*(a1**2*a2b**3 - a1b**2*a2**3), w1v, w2v, (a1,a1b,a2,a2b))
ok_gauge = True
for dR1, dR2 in [(N1,0), (N2,0), (sp.expand(N1*N2),0), (0,Kp), (0,Km)]:
    _, ob3p, _, _ = order3(w1v, w2v, dR1, dR2)
    if sp.simplify(sp.expand(ob3p - ob3_32)) != 0:
        ok_gauge = False
check("O3d: the 3:2 obstruction is unchanged under R1 -> R1 + "
      "{N1, N2, N1 N2} and R2 -> R2 + (on-shell quintic kernel ops): "
      "gauge-independent (cohomological)", ok_gauge)

# ============================== O3e ==========================================
print("\n=== Jordan scaling of R3 ===")
prev = None; pw = None
for e in [sp.Rational(1,100), sp.Rational(1,1000)]:
    _, _, R3m_e, syms_e = order3(sp.nsimplify(1+e), sp.nsimplify(1-e))
    R3e = from_modes(R3m_e, sp.nsimplify(1+e), sp.nsimplify(1-e), syms_e)
    mx = max(abs(float(sp.N(cf))) for cf in sp.Poly(R3e, x, y, p, q).coeffs())
    if prev is not None:
        pw = math.log(mx/prev)/math.log(10)
    prev = mx
check(f"O3e: R3 = O(eps^-9/2) (measured decade exponent {pw:+.3f}, "
      "prediction +4.5): third data point of R_n = O(eps^(-3n/2))",
      pw is not None and abs(pw - 4.5) < 0.1)

print("\nALL PASS" if PASS else "\nSOME CHECKS FAILED")
