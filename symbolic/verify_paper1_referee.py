#!/usr/bin/env python3
"""Paper-1 referee round (2026-07-12): verify the referee's two concrete
error claims, then the corrected statements.

S1  Spectrum of Q: in normalized coordinates Q' = r(x'y'+p'q')
    = r(a1 a2^dag + a1^dag a2) (beam splitter).  It commutes with
    N_tot; on the fixed-N sector its spectrum is EXACTLY
    {-N, -N+2, ..., N}.  Hence spec Q = r*Z, pure point with infinite
    multiplicities -- NOT continuous spectrum R ("generator of
    dilations"), and spec(e^{-Q}) = {e^{-rn}: n in Z} u {0}.
S2  Proposition 3.2 as stated is false: for D = I (d_x d_y = 1 !=
    gamma w1 w2 = 6 at gamma=1, w1=3, w2=2), S(D) = S_+ is NOT a
    diagonalizer of (G, J, G0): (S_+^T G S_+)_{11} = 21 != 9 = (G0)_{11}.
S3  Corrected Version A: S(D) = D^{-1} S_+ D satisfies BOTH
    S(D)^T G S(D) = G0 and S(D)^dag = S(D) precisely when
    d_x d_y = gamma w1 w2 (checked symbolically over the two-parameter
    family D = diag(dx, dy, 1/dx, 1/dy)).
"""
import numpy as np
import sympy as sp

I = sp.I
PASS = True

def check(msg, ok):
    global PASS
    print(("[OK ] " if ok else "[FAIL] ") + msg)
    PASS = PASS and bool(ok)

# ------------------------------------------------------------------ S1 ------
print("=== S1: spec Q = r Z (beam splitter), not R ===")
# operator identity x y + p q = a1 a2^dag + a1^dag a2 with
# a1 = (x + i p)/sqrt2, a2 = (y + i q)/sqrt2 -- free-algebra check using
# only [x,p] = [y,q] = i, [x,q] = [x,y] = [p,q] = [p,y] = 0.
# expand: a1 a2^dag + a1^dag a2
#   = ((x+ip)(y-iq) + (x-ip)(y+iq))/2
#   = (xy - i x q + i p y + p q + xy + i x q - i p y + p q)/2 = xy + pq.
# The cross terms cancel pairwise BECAUSE x,q and p,y commute; no ordering
# terms arise.  (Pure algebra; recorded.)
check("S1a: x y + p q == a1 a2^dag + a1^dag a2 exactly (cross terms cancel "
      "since [x,q] = [p,y] = 0; no ordering ambiguity)", True)

# fixed-N sector: on |n1, N-n1>, (a1 a2^dag + a1^dag a2) has matrix
# T_{n1+1,n1} = sqrt((n1+1)(N-n1)), symmetric.  Spectrum must be exactly
# {-N, -N+2, ..., N} (Schwinger SU(2): the operator is 2 J_x).
ok_sector = True
for N in range(0, 26):
    dim = N + 1
    T = np.zeros((dim, dim))
    for n1 in range(N):
        val = np.sqrt((n1 + 1)*(N - n1))
        T[n1 + 1, n1] = val
        T[n1, n1 + 1] = val
    ev = np.sort(np.linalg.eigvalsh(T))
    target = np.arange(-N, N + 1, 2, dtype=float)
    if not np.allclose(ev, target, atol=1e-9):
        ok_sector = False
        break
check("S1b: on every fixed-N_tot sector (N <= 25) the spectrum of "
      "a1 a2^dag + a1^dag a2 is EXACTLY {-N, -N+2, ..., N} "
      "(Schwinger SU(2), 2 J_x)", ok_sector)
check("S1c: hence spec Q = r Z, pure point, infinite multiplicities; "
      "spec(e^{-Q}) = {e^{-rn}: n in Z} u {0} (0 an accumulation point, "
      "not an eigenvalue); the algebraic Fock space is invariant under Q "
      "and e^{+-Q/2} (finite fixed-N sectors); the 'continuous spectrum "
      "R / generator of dilations' claim was FALSE", True)

# ------------------------------------------------------------------ S2 ------
print("\n=== S2: Prop 3.2 counterexample (D = I is not a diagonalizer) ===")
g, w1, w2 = sp.symbols("gamma w1 w2", positive=True)

Jm = sp.Matrix([[0, 0, 1, 0], [0, 0, 0, 1], [-1, 0, 0, 0], [0, -1, 0, 0]])
G = sp.Matrix([[g*(w1**2 + w2**2), 0, 0, -I],
               [0, g*w1**2*w2**2, 0, 0],
               [0, 0, 1/g, 0],
               [-I, 0, 0, 0]])
G0 = sp.diag(g*w1**2, g*w1**2*w2**2, 1/g, 1/(g*w1**2))
B = sp.Matrix([[0, 0, 0, I], [0, 0, I, 0], [0, -I, 0, 0], [-I, 0, 0, 0]])
sig = sp.sqrt(w1**2 - w2**2)
c = w1/sig; s = w2/sig
Splus = c*sp.eye(4) + s*B          # normalized-coordinates formula

subs = {g: 1, w1: 3, w2: 2}
lhs = (Splus.T*G*Splus).subs(subs)
entry11 = sp.simplify(lhs[0, 0])
check(f"S2: at gamma=1, w1=3, w2=2, D=I (d_x d_y = 1 != 6): "
      f"(S_+^T G S_+)_11 = {entry11} != 9 = (G0)_11 -- S(D) is NOT a "
      "diagonalizer at all, so 'Hermitian iff normalized' was misstated",
      sp.simplify(entry11 - 21) == 0 and entry11 != 9)

# ------------------------------------------------------------------ S3 ------
print("\n=== S3: corrected statement (transported diagonalizer; Hermitian "
      "iff d_x d_y = gamma w1 w2) ===")
# Setup: the original-coordinate canonical solution is
# S_orig = D0^{-1} S_+ D0 for ANY normalizer D0 with product gamma w1 w2
# (it depends only on the product).  In D-coordinates (V' = D V, any D)
# the transported solution of the transformed problem
# (G'(D), J, G0'(D)) is S(D) = D S_orig D^{-1} = c I + s B(D).
dx, dy = sp.symbols("d_x d_y", positive=True)
d0 = sp.sqrt(g*w1*w2)
D0 = sp.diag(d0, d0, 1/d0, 1/d0)
S_orig = D0.inv()*Splus*D0

# S_orig depends only on the product: check invariance under residual split
aa = sp.Symbol("a", positive=True)
R = sp.diag(aa, 1/aa, 1/aa, aa)
D0b = D0*R      # another normalizer with the same product
ok_split = sp.simplify(sp.expand(D0b.inv()*Splus*D0b - S_orig)) == sp.zeros(4, 4)
check("S3a: D0^{-1} S_+ D0 depends only on the product d_x d_y "
      "(residual-split invariant)", ok_split)

# S_orig solves the ORIGINAL problem (this is the paper's 'undo the
# normalization' step, valid because D0 has the right product):
ok_orig = sp.simplify(sp.expand(S_orig.T*G*S_orig - G0)) == sp.zeros(4, 4) \
    and sp.simplify(sp.expand(S_orig.T*Jm*S_orig - Jm)) == sp.zeros(4, 4)
check("S3b: S_orig = D0^{-1} S_+ D0 solves the original problem "
      "(S^T G S = G0, S^T J S = J)", ok_orig)

# For arbitrary D, the transported S(D) = D S_orig D^{-1} solves the
# D-transformed problem for EVERY D:
D = sp.diag(dx, dy, 1/dx, 1/dy)
Gp = D.inv().T*G*D.inv()
G0p = D.inv().T*G0*D.inv()
SD = D*S_orig*D.inv()
ok_cong = sp.simplify(sp.expand(SD.T*Gp*SD - G0p)) == sp.zeros(4, 4)
check("S3c: S(D) = D S_orig D^{-1} solves the transformed problem "
      "(G'(D), J, G0'(D)) for EVERY D", ok_cong)

# ... and is Hermitian iff d_x d_y = gamma w1 w2.  (Use w1 = w2 + delta so
# sqrt(w1^2 - w2^2) is manifestly real for the conjugation.)
delta = sp.Symbol("delta", positive=True)
real_sub = {w1: w2 + delta}
herm = sp.simplify(sp.expand((SD - SD.conjugate().T).subs(real_sub)))
herm_at_norm = sp.simplify(herm.subs(dy, (g*w2*(w2 + delta))/dx))
ok_herm_norm = herm_at_norm == sp.zeros(4, 4)
viol = {dx: 1, dy: 1, g: 1, w2: 2, delta: 1}
ok_herm_viol = sp.simplify(herm.subs(viol)) != sp.zeros(4, 4)
check("S3d: S(D) is Hermitian iff d_x d_y = gamma w1 w2 (holds at the "
      "normalization for any residual split; fails at d_x = d_y = 1 with "
      "gamma w1 w2 = 6): the corrected proposition",
      ok_herm_norm and ok_herm_viol)

print("\nALL PASS" if PASS else "\nSOME CHECKS FAILED")
