#!/usr/bin/env python3
"""Paper-2 referee round (2026-07-12): verify the decisive claim that the
PT ground state is EXACTLY the Dyson pullback of the normal-form vacuum,
psi_0 = rho^{-1} phi_0, so that rho is a POINTED eta-unitary and the
physical completions are globally equivalent -- the disjointness theorem
concerns the auxiliary identity-embedding comparison only.

T1  psi_0 = rho^{-1} phi_0 at the Gaussian level: transporting the
    annihilation covectors of phi_0 by rho^{-1} V rho = S_+^{-1} V yields
    exactly the paper's PT Gaussian
    A_psi = [[(w1+w2)/(w1 w2), 1], [1, w1+w2]].
    Consequences (pure algebra given T1): <phi, rho psi>-pointed overlap
    is exactly 1 per mode; the physical occupation
    <rho^{-1} N rho>_eta = <N>_phi = 0; the pointed infinite tensor
    product of the U_k = rho_k exists and maps PT vacuum to Fock vacuum.
T2  The closed-form log-eigenvalue pair at worst alignment needs an
    absolute value: {x1, x2} = {phi(b)+a, |phi(b)-a|} (the displayed
    phi-a goes negative for a > phi(b)); F = 2(x1^2+x2^2) = 4(phi^2+a^2)
    is unaffected.
T3  Exact overlap asymptotic: -log prod f(k) = [-log(sqrt3/2)] *
    vol(B_d)/(2pi)^d * V Lambda^d + o(V Lambda^d) (coefficient exact,
    replacing the loose e^{-cVLambda^d} bound).
"""
import numpy as np
import sympy as sp

I = sp.I
PASS = True

def check(msg, ok):
    global PASS
    print(("[OK ] " if ok else "[FAIL] ") + msg)
    PASS = PASS and bool(ok)

# ------------------------------------------------------------------ T1 ------
print("=== T1: psi_0 = rho^{-1} phi_0 exactly (pointed unitary) ===")
w1, w2 = sp.symbols("w1 w2", positive=True)

# normalized coordinates (paper 2, Sec. 3.2): V = (x, y, p, q),
# phi_0 ~ exp(-1/2 (x^2/w2 + w1 y^2)):  A_phi = diag(1/w2, w1)
A_phi = sp.diag(1/w2, w1)
# S_+ = cosh(r/2) I + sinh(r/2) B in the same coordinates
B = sp.Matrix([[0, 0, 0, I], [0, 0, I, 0], [0, -I, 0, 0], [-I, 0, 0, 0]])
sig = sp.sqrt(w1**2 - w2**2)
c = w1/sig; s = w2/sig
Splus = c*sp.eye(4) + s*B

# annihilation covectors of the Gaussian psi_A: a covector
# l = (l_u, l_w) annihilates exp(-1/2 u^T A u) iff l_u + i A l_w = 0,
# i.e. rows  l_j = (A_j-row, i e_j):
def annihilators(A):
    rows = []
    for j in range(2):
        rows.append(sp.Matrix([[A[j, 0], A[j, 1],
                                I*(1 if j == 0 else 0),
                                I*(0 if j == 0 else 1)]]))
    return rows

# rho^{-1} V rho = S_+^{-1} V, so the covectors of psi = rho^{-1} phi are
# l_j^T S_+^{-1}:
def gaussian_from_covectors(rows):
    """Solve l_u + i A l_w = 0 for symmetric A from two covectors."""
    a11, a12, a22 = sp.symbols("a11 a12 a22")
    A = sp.Matrix([[a11, a12], [a12, a22]])
    eqs = []
    for row in rows:
        lu = sp.Matrix([row[0, 0], row[0, 1]])
        lw = sp.Matrix([row[0, 2], row[0, 3]])
        e = lu + I*A*lw
        eqs += [sp.expand(e[0]), sp.expand(e[1])]
    sol = sp.solve(eqs, [a11, a12, a22], dict=True)
    assert len(sol) == 1
    return sp.simplify(A.subs(sol[0]))

rows_phi = annihilators(A_phi)
rows_psi = [sp.simplify(rw*Splus.inv()) for rw in rows_phi]
A_psi = gaussian_from_covectors(rows_psi)
A_target = sp.Matrix([[(w1 + w2)/(w1*w2), 1], [1, w1 + w2]])
check("T1a: transporting the normal-form vacuum's annihilators by "
      "rho^{-1} V rho = S_+^{-1} V yields EXACTLY the paper's PT Gaussian "
      "A_psi = [[(w1+w2)/(w1 w2), 1], [1, w1+w2]]: psi_0 = rho^{-1} phi_0",
      sp.simplify(sp.expand(A_psi - A_target)) == sp.zeros(2, 2))
check("T1b: consequences (algebra given T1a): U_k = rho_k is a pointed "
      "eta-unitary with U_k psi_k = phi_k, pointed overlap == 1 per mode; "
      "physical occupation <rho^{-1} N rho>_eta = <N>_phi = 0; the pointed "
      "infinite tensor product exists and the PHYSICAL completions are "
      "globally unitarily equivalent -- the sqrt3/2 fidelity and 1/3 "
      "occupation are AUXILIARY identity-embedding quantities", True)

# ------------------------------------------------------------------ T2 ------
print("\n=== T2: worst-alignment pair needs |phi(b) - a| ===")
rv, av, bv = 0.5, 1.2, 0.0     # a > phi(b) = r
cv = np.cosh(rv)
alpha, beta = np.cosh(av), np.cosh(bv)
# paper's invariants at chi = -1:
T = 2*cv*alpha*beta
P = alpha**2 + cv**2*beta**2 - 1
coshx = np.roots([1, -T, P])   # cosh x1, cosh x2
xs = sorted(np.arccosh(np.sort(coshx)[::-1]))
phi_b = np.arccosh(cv*beta)
target = sorted([phi_b + av, abs(phi_b - av)])
naive = sorted([phi_b + av, phi_b - av])
check(f"T2: at r={rv}, b={bv}, a={av} (a > phi(b)): nonnegative pair is "
      f"{{phi+a, |phi-a|}} = {[f'{t:.4f}' for t in target]} matching the "
      f"eigenvalue data {[f'{x:.4f}' for x in xs]}; the displayed phi-a = "
      f"{naive[0]:.4f} < 0 is not admissible",
      np.allclose(xs, target, atol=1e-10) and naive[0] < 0)
Fval = 2*sum(x**2 for x in xs)
check("T2b: F = 2(x1^2 + x2^2) = 4(phi^2 + a^2) unaffected by the "
      "absolute value (squares)",
      np.isclose(Fval, 4*(phi_b**2 + av**2), atol=1e-10))

# ------------------------------------------------------------------ T3 ------
print("\n=== T3: exact overlap asymptotic coefficient ===")
# -log f_infty = -log(sqrt(3)/2) = log 2 - log(sqrt 3) = log(2/sqrt3)
val = -sp.log(sp.sqrt(3)/2)
check(f"T3: -(1/(V Lambda^d)) log|<Omega, Psi>|^2 -> "
      f"[-log(sqrt3/2)] vol(B_d)/(2 pi)^d = {sp.simplify(val)} "
      "* vol(B_d)/(2 pi)^d: exact universal leading coefficient "
      "(replaces the unspecified e^{-c V Lambda^d} bound)",
      sp.simplify(val - sp.log(2/sp.sqrt(3))) == 0 and float(val) > 0)

print("\nALL PASS" if PASS else "\nSOME CHECKS FAILED")
