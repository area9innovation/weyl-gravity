#!/usr/bin/env python3
"""Interaction-deformation program, step 3 (2026-07-13): the order-4
kernel projection of the cubic PU vertex V = -i y^3 at the 5:1 locus
(w1, w2) = (5, 1).  Runtime ~2-4 min (sextic Moyal algebra; the star
product is degree-capped, which makes the order-4 recursion cheap).

Derivation (FO1): the order-n sources are generated GENERICALLY from
the adjoint series
    h_zeta = e^{-X/2} star (h0 + zeta v) star e^{X/2},
    X = sum_j zeta^j R_j,
    e^{-X/2} A e^{X/2} = sum_k 1/(2^k k!) ad_X^k(A),
collected order by order in zeta by a word generator (no hand-derived
formulas): [h0, R_n] = -(T_n - T_n^dag), obstruction
o_+^(n) = Pi_ker(-(T_n - T_n^dag)).  The generated word lists at
orders 2 and 3 coincide exactly with the paper's T_2, T_3
(Appendix "The Weyl-Moyal recursion"); order 4 has 11 words:
  1/2 [v,R3];
  1/8 { [[h0,R1],R3], [[h0,R3],R1], [[h0,R2],R2], [[v,R1],R2],
        [[v,R2],R1] };
  1/48 { [[[h0,R1],R1],R2], [[[h0,R1],R2],R1], [[[h0,R2],R1],R1],
         [[[v,R1],R1],R1] };
  1/384 [[[[h0,R1],R1],R1],R1].

Validation (FO2-FO4): the SAME code path reproduces the two known
obstructions EXACTLY --
  order 2 at (3,1):  o_+^(2) = 27 sqrt(3)/320 (a1 a2dag^3 - a1dag a2^3),
  order 3 at (3,2):  o_+^(3) = -(117 sqrt(30)/1120) i
                                  (a1^2 a2dag^3 + a1dag^2 a2^3),
and at generic frequencies (13/7, 1) orders 2-4 are unobstructed with
Hermitian R2, R3, R4 and end-to-end Hermitian h4.

RESULTS at (w1, w2) = (5, 1) (FO5-FO9, NEW):
  - orders 2 and 3: kernel projections VANISH (selection rule); R2, R3
    exist and are Hermitian -- the deformation is unobstructed through
    order 3 at 5:1;
  - order 4: the obstruction is NONZERO and exact:
        o_+^(4) = -(203125 sqrt(5)/2341011456) (a1 a2dag^5 - a1dag a2^5)
                = -(13 * 5^(13/2)/(2^16 3^6 7^2))
                                       (a1 a2dag^5 - a1dag a2^5),
    the on-shell 1-quantum <-> 5-quanta conversion (w1 = 5 w2).  This
    CONFIRMS the hierarchy conjecture: the coprime ratio p:q with p odd
    first obstructs at order p+q-2 (5:1 -> order 4), with the predicted
    kernel monomial a1 a2dag^5 - a1dag a2^5;
  - w2-scaling: at (10,2) the obstruction is exactly 1/2^9 of the (5,1)
    value, i.e. o_+^(4) ~ w2^(-9), extending the pattern
    o_+^(n) ~ w2^(-(5n-2)/2)  (n=2: -4, n=3: -13/2, n=4: -9);
  - gauge independence: unchanged under R1 -> R1 + {N1, N2, N1 N2},
    R2 -> R2 + N1^2, R3 -> R3 + (a1 a2dag^5 + a1dag a2^5)
    (cohomological);
  - Jordan scaling: R4 = O(eps^-6) (measured +5.99 per decade at
    1e-2 -> 1e-3), fourth data point of R_n = O(eps^(-3n/2)).

All computations use exact Weyl-symbol Moyal calculus (finite for
polynomials; cubic-cubic commutators include the Lambda^3 term); the
Moyal/mode machinery is copied verbatim from
verify_interaction_deformation.py / verify_interaction_order3.py, with
one safe optimization: star(f,g) truncates at
n <= min(deg f, deg g) since Lambda^n needs n derivatives on each side.
"""
import sympy as sp
from sympy import Rational, factorial
import math

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

def _deg(f):
    f = sp.expand(f)
    if f == 0:
        return -1
    try:
        return sp.Poly(f, x, y, p, q).total_degree()
    except sp.PolynomialError:
        return 13

def star(f, g):
    """Star product, truncated at n <= min(deg f, deg g): Lambda^n takes
    n derivatives of each factor, so higher terms vanish identically."""
    if f == 0 or g == 0:
        return sp.S(0)
    nmax = min(_deg(f), _deg(g), 13)
    out = 0
    for n in range(0, nmax+1):
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

# ----------------- generic adjoint-series word generation --------------------
def gen_words(N):
    """All (coeff, zeta_power, word) of e^{-X/2}(h0 + zeta v)e^{X/2}
    through zeta^N; word is 'h0' | 'v' | ('c', word, j) = [word, R_j]."""
    out = []
    for base, p0 in (('h0', 0), ('v', 1)):
        out.append((sp.S(1), p0, base))
        current = [(p0, base)]
        for k in range(1, N+1):
            nxt = []
            for pw, w in current:
                for j in range(1, N-pw+1):
                    nxt.append((pw+j, ('c', w, j)))
            current = nxt
            if not current:
                break
            ck = Rational(1, 2**k)/factorial(k)
            for pw, w in current:
                out.append((ck, pw, w))
    return out

def order_terms(n):
    """(coeff, word) at zeta^n, excluding the LHS word (1/2)[h0, R_n]."""
    lhs = ('c', 'h0', n)
    return [(c, w) for (c, pw, w) in gen_words(n) if pw == n and w != lhs]

def eval_word(w, ctx, memo):
    if isinstance(w, str):
        return ctx[w]
    if w in memo:
        return memo[w]
    _, inner, j = w
    r = comm(eval_word(inner, ctx, memo), ctx['R%d' % j])
    memo[w] = r
    return r

def run_orders(w1, w2, max_order, dR=None):
    """{n: (obstruction, Rn_mode_form, syms)} for n = 2..max_order via
    [h0,R_n] = -(T_n - T_n^dag); stops early if an obstruction is
    nonzero.  dR: optional {n: phase-space expr} gauge probes (Hermitian
    kernel elements added to R_n; dR[1] modifies R1 before order 2)."""
    dR = dR or {}
    h0, v, R1 = model(w1, w2)
    ctx = {'h0': h0, 'v': v, 'R1': sp.expand(R1 + dR.get(1, 0))}
    memo = {}
    results = {}
    for n in range(2, max_order+1):
        T = sp.S(0)
        for c, w in order_terms(n):
            T += c*eval_word(w, ctx, memo)
        T = sp.expand(T)
        S = sp.expand(-(T - hc(T)))          # source: [h0, R_n] = S
        ob, Rm, syms = ker_split(S, w1, w2)
        ob = sp.simplify(ob)
        results[n] = (ob, Rm, syms)
        if n < max_order:
            if ob != 0:
                return results               # obstructed: no R_n
            ctx['R%d' % n] = sp.expand(from_modes(Rm, w1, w2, syms)
                                       + dR.get(n, 0))
    return results

a1, a1b, a2, a2b = sp.symbols("a1 a1b a2 a2b")
SY = (a1, a1b, a2, a2b)

# ================================ FO1 ========================================
print("=== FO1: generic adjoint-series derivation of the sources ===")
paperT2 = {(Rational(1,2), ('c', 'v', 1)),
           (Rational(1,8), ('c', ('c', 'h0', 1), 1))}
paperT3 = {(Rational(1,2), ('c', 'v', 2)),
           (Rational(1,8), ('c', ('c', 'h0', 1), 2)),
           (Rational(1,8), ('c', ('c', 'h0', 2), 1)),
           (Rational(1,8), ('c', ('c', 'v', 1), 1)),
           (Rational(1,48), ('c', ('c', ('c', 'h0', 1), 1), 1))}
w4 = order_terms(4)
check("FO1: the word generator reproduces the paper's T2 and T3 term "
      "lists exactly, and T4 has 11 words with coefficients "
      "{1/2, 1/8 x5, 1/48 x4, 1/384}",
      set(order_terms(2)) == paperT2 and set(order_terms(3)) == paperT3
      and len(w4) == 11
      and sorted(c for c, _ in w4) ==
          sorted([Rational(1,2)] + [Rational(1,8)]*5
                 + [Rational(1,48)]*4 + [Rational(1,384)]))

# ================================ FO2-FO3 ====================================
print("\n=== FO2-FO3: reproduce the known order-2 and order-3 obstructions ===")
res31 = run_orders(sp.S(3), sp.S(1), 2)
target2 = 27*sp.sqrt(3)/320*(a1*a2b**3 - a1b*a2**3)
ob2_31 = res31[2][0].subs(dict(zip(res31[2][2], SY)))
check("FO2: order-2 at (3,1) from the generic path equals EXACTLY "
      "27 sqrt(3)/320 (a1 a2dag^3 - a1dag a2^3)  [= ID9a of "
      "verify_interaction_deformation.py]",
      sp.simplify(sp.expand(ob2_31 - target2)) == 0)

res32 = run_orders(sp.S(3), sp.S(2), 3)
target3 = -117*sp.sqrt(30)*I/1120*(a1**2*a2b**3 + a1b**2*a2**3)
ob3_32 = res32[3][0].subs(dict(zip(res32[3][2], SY)))
check("FO3: order-3 at (3,2) from the generic path: order-2 vanishes en "
      "route and o_+^(3) equals EXACTLY -(117 sqrt(30)/1120) i "
      "(a1^2 a2dag^3 + a1dag^2 a2^3)  [= O3c of "
      "verify_interaction_order3.py]",
      res32[2][0] == 0
      and sp.simplify(sp.expand(ob3_32 - target3)) == 0)

# ================================ FO4 ========================================
print("\n=== FO4: order 4 at generic frequencies (13/7, 1) ===")
w1g, w2g = sp.Rational(13,7), sp.S(1)
resg = run_orders(w1g, w2g, 4)
ok_zero = all(resg[n][0] == 0 for n in (2, 3, 4))
Rg = {n: from_modes(resg[n][1], w1g, w2g, resg[n][2]) for n in (2, 3, 4)}
ok_herm = all(sp.simplify(sp.expand(Rg[n] - hc(Rg[n]))) == 0
              for n in (2, 3, 4))
h0g, vg, R1g = model(w1g, w2g)
ctxg = {'h0': h0g, 'v': vg, 'R1': R1g,
        'R2': Rg[2], 'R3': Rg[3], 'R4': Rg[4]}
memog = {}
h4g = sp.Rational(1,2)*comm(h0g, Rg[4])
for c, w in order_terms(4):
    h4g += c*eval_word(w, ctxg, memog)
h4g = sp.expand(h4g)
check("FO4: at (13/7, 1) orders 2-4 are UNOBSTRUCTED; R2, R3, R4 exist "
      "and are Hermitian; and the assembled h4 = (1/2)[h0,R4] + T4 is "
      "Hermitian end-to-end (validates the order-4 equation)",
      ok_zero and ok_herm
      and sp.simplify(sp.expand(h4g - hc(h4g))) == 0)

# ================================ FO5-FO6 ====================================
print("\n=== FO5-FO6: the 5:1 locus (w1, w2) = (5, 1) ===")
w1r, w2r = sp.S(5), sp.S(1)
res51 = run_orders(w1r, w2r, 4)
R2_51 = from_modes(res51[2][1], w1r, w2r, res51[2][2])
R3_51 = from_modes(res51[3][1], w1r, w2r, res51[3][2])
check("FO5: at (5,1) the order-2 AND order-3 kernel projections VANISH "
      "(selection rule: 5:1 unreachable below order 4) and R2, R3 exist "
      "and are Hermitian",
      res51[2][0] == 0 and res51[3][0] == 0
      and sp.simplify(sp.expand(R2_51 - hc(R2_51))) == 0
      and sp.simplify(sp.expand(R3_51 - hc(R3_51))) == 0)

ob4 = res51[4][0].subs(dict(zip(res51[4][2], SY)))
coef4 = Rational(203125, 2341011456)*sp.sqrt(5)
target4 = -coef4*(a1*a2b**5 - a1b*a2**5)
check("FO6: the order-4 obstruction at (5,1) is NONZERO and equals "
      "EXACTLY -(203125 sqrt(5)/2341011456)(a1 a2dag^5 - a1dag a2^5) "
      "= -(13 * 5^(13/2)/(2^16 3^6 7^2))(a1 a2dag^5 - a1dag a2^5): the "
      "on-shell 1 <-> 5 conversion -- the hierarchy conjecture's "
      "prediction (p+q-2 = 4) CONFIRMED with the predicted monomial",
      sp.simplify(sp.expand(ob4 - target4)) == 0
      and sp.simplify(coef4 - 13*5**Rational(13,2)
                      /(2**16*3**6*7**2)) == 0)

# ================================ FO7 ========================================
print("\n=== FO7: w2-scaling of the order-4 obstruction ===")
res102 = run_orders(sp.S(10), sp.S(2), 4)
ob4_102 = res102[4][0].subs(dict(zip(res102[4][2], SY)))
check("FO7: at (10,2) the obstruction is EXACTLY 2^-9 times the (5,1) "
      "value: o_+^(4) ~ w2^(-9), extending o_+^(n) ~ w2^(-(5n-2)/2) "
      "(n=2: -4, n=3: -13/2, n=4: -9)",
      sp.simplify(sp.expand(ob4_102 - target4/2**9)) == 0)

# ================================ FO8 ========================================
print("\n=== FO8: gauge independence of the 5:1 obstruction ===")
N1 = from_modes(a1*a1b, w1r, w2r, SY)
N2 = from_modes(a2*a2b, w1r, w2r, SY)
Kp = from_modes(a1*a2b**5 + a1b*a2**5, w1r, w2r, SY)
ok_gauge = True
for dR in [{1: N1}, {1: N2}, {1: sp.expand(N1*N2)},
           {2: sp.expand(N1*N1)}, {3: Kp}]:
    rp = run_orders(w1r, w2r, 4, dR=dR)
    obp = rp[4][0].subs(dict(zip(rp[4][2], SY)))
    if sp.simplify(sp.expand(obp - target4)) != 0:
        ok_gauge = False
check("FO8: the 5:1 obstruction is unchanged under R1 -> R1 + "
      "{N1, N2, N1 N2}, R2 -> R2 + N1^2, and R3 -> R3 + "
      "(a1 a2dag^5 + a1dag a2^5): gauge-independent (cohomological)",
      ok_gauge)

# ================================ FO9 ========================================
print("\n=== FO9: Jordan scaling of R4 ===")
prev = None; pw = None
for e in [sp.Rational(1,100), sp.Rational(1,1000)]:
    rese = run_orders(1+e, 1-e, 4)
    R4e = from_modes(rese[4][1], 1+e, 1-e, rese[4][2])
    mx = max(abs(float(sp.N(cf))) for cf in sp.Poly(R4e, x, y, p, q).coeffs())
    if prev is not None:
        pw = math.log(mx/prev)/math.log(10)
    prev = mx
check(f"FO9: R4 = O(eps^-6) (measured decade exponent {pw:+.3f}, "
      "prediction +6.0): fourth data point of R_n = O(eps^(-3n/2))",
      pw is not None and abs(pw - 6) < 0.1)

print("\nALL PASS" if PASS else "\nSOME CHECKS FAILED")
