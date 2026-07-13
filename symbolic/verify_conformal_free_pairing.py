#!/usr/bin/env python3
"""Exact first rail for the pure-Weyl conformal/Jordan programme.

This script deliberately proves only the transverse-traceless auxiliary
sector statements that can be established before the full diffeomorphism
plus Weyl BRST reduction on the Einstein cylinder.  In particular, it
does *not* pretend that the two helicity-1 conformal modes have already
been incorporated into an SO(4,2)-invariant one-particle form.

Checks
------
C0a-1  Eliminating the symmetric auxiliary tensor gives
       Ricci^2 - R^2/3 exactly in four dimensions.
C0a-2  The TT quadratic Hessian has the 1/(p^2)^2 cross-paired inverse
       and equations Box f = 0, Box h = -f.
C0a-3  Direct evaluation of the covariant symplectic current on an
       Einstein root and its Jordan partner gives a nondegenerate Gram
       form congruent to sigma_x, with the Einstein root null.
C0a-4  The local constant two-field action has no nontrivial continuous
       internal symmetry.  Removing f^2 requires P(Box)=1/(2 Box), so
       the apparent O(1,1) cross-scaling is singular on the massless
       shell and cannot arise from a finite-derivative field shift.
C0a-5  The bosonic two-particle lift of sigma_x is the advertised J2.
       Einstein-sector zeros plus J2-pseudo-Hermiticity conditionally
       force the LLLL and ELLL blocks to vanish.
C0a-6  For S=-alpha_g int C^2, canonical normalization makes the weak
       coupling g_W=alpha_g^(-1/2), not alpha_g.
C0a-7  Translation of the published flat BRST-cohomology algebra into
       the present basis: two TT Jordan blocks plus two ordinary vector
       modes.  The full fixed-momentum form is nondegenerate, and every
       nondegenerate form preserving a rank-two Jordan Hamiltonian is
       necessarily indefinite.

The next theorem-critical step is C0b: construct the complete cylinder
BRST cohomology and solve for an invariant nondegenerate form on the full
TT-plus-vector SO(4,2) module.
"""

from __future__ import annotations

import sympy as sp


PASS = True


def check(label: str, condition: object) -> None:
    global PASS
    ok = bool(condition)
    print(("[OK ] " if ok else "[FAIL] ") + label)
    PASS = PASS and ok


# ---------------------------------------------------------------------------
# C0a-1: exact auxiliary elimination in d=4
# ---------------------------------------------------------------------------
d = sp.Integer(4)
R, ricci_sq = sp.symbols("R ricci_sq", real=True)
a, b = sp.symbols("a b", real=True)

# Use f_mn = a R_mn + b g_mn R.  The auxiliary equation is
# f_mn - g_mn f = 2 R_mn - g_mn R.
aux_coefficients = sp.solve(
    [sp.Eq(a, 2), sp.Eq(b - (a + d * b), -1)],
    [a, b],
    dict=True,
)
check("C0a-1: auxiliary equation has a unique curvature solution",
      aux_coefficients == [{a: 2, b: -sp.Rational(1, 3)}])

a_sol = aux_coefficients[0][a]
b_sol = aux_coefficients[0][b]
f_trace_coeff = sp.simplify(a_sol + d * b_sol)
f_ricci = a_sol * ricci_sq + b_sol * R**2
f_sq = a_sol**2 * ricci_sq + (2 * a_sol * b_sol + d * b_sol**2) * R**2
f_trace_sq = f_trace_coeff**2 * R**2
f_dot_G = sp.expand(f_ricci - sp.Rational(1, 2) * f_trace_coeff * R**2)
lag_eliminated = sp.simplify(
    f_dot_G - sp.Rational(1, 4) * (f_sq - f_trace_sq)
)

check("C0a-1: f = 2R/3", f_trace_coeff == sp.Rational(2, 3))
check("C0a-1: f_mn = 2 R_mn - g_mn R/3", a_sol == 2 and b_sol == -sp.Rational(1, 3))
check("C0a-1: S_aux eliminates to Ricci^2 - R^2/3",
      sp.simplify(lag_eliminated - (ricci_sq - R**2 / 3)) == 0)


# ---------------------------------------------------------------------------
# C0a-2: TT Hessian and propagator
# ---------------------------------------------------------------------------
z = sp.symbols("z", nonzero=True)  # Fourier symbol of Box
K = sp.Matrix([[0, -z], [-z, -1]])
K_inv = sp.simplify(K.inv())
expected_inverse = sp.Matrix([[z**-2, -z**-1], [-z**-1, 0]])

check("C0a-2: TT Hessian inverse is cross-paired",
      sp.simplify(K_inv - expected_inverse) == sp.zeros(2))
check("C0a-2: hh has a double pole", K_inv[0, 0] == z**-2)
check("C0a-2: hf has a simple pole and ff vanishes",
      K_inv[0, 1] == -z**-1 and K_inv[1, 1] == 0)

h, f = sp.symbols("h f")
eom = K * sp.Matrix([h, f])
check("C0a-2: equations are Box f=0 and Box h=-f",
      eom == sp.Matrix([-z * f, -z * h - f]))


# ---------------------------------------------------------------------------
# C0a-3: one-frequency covariant symplectic Gram form
# ---------------------------------------------------------------------------
t = sp.symbols("t", real=True)
w = sp.symbols("w", positive=True, real=True)
I = sp.I
e_minus = sp.exp(-I * w * t)
e_plus = sp.exp(I * w * t)
ell_minus = t * e_minus / (2 * I * w)
ell_plus = sp.conjugate(ell_minus)


def symplectic_current(state1: tuple[sp.Expr, sp.Expr],
                       state2: tuple[sp.Expr, sp.Expr]) -> sp.Expr:
    """Time component for L=-f Box h-f^2/2, first state already barred."""
    h1, f1 = state1
    h2, f2 = state2
    return sp.simplify(
        sp.diff(f1, t) * h2
        + sp.diff(h1, t) * f2
        - sp.diff(f2, t) * h1
        - sp.diff(h2, t) * f1
    )


E_bar = (e_plus, sp.Integer(0))
E = (e_minus, sp.Integer(0))
L_bar = (ell_plus, e_plus)
L = (ell_minus, e_minus)

omega_EE = symplectic_current(E_bar, E)
omega_EL = symplectic_current(E_bar, L)
omega_LE = symplectic_current(L_bar, E)
omega_LL = symplectic_current(L_bar, L)

# Multiplication by -i/(2w) fixes <E,L>=1 for this plane-wave convention.
gram = sp.simplify(
    -I / (2 * w)
    * sp.Matrix([[omega_EE, omega_EL], [omega_LE, omega_LL]])
)
b_self = sp.simplify(gram[1, 1])
shift = sp.Matrix([[1, -b_self / 2], [0, 1]])
gram_canonical = sp.simplify(sp.conjugate(shift.T) * gram * shift)
J1 = sp.Matrix([[0, 1], [1, 0]])

check("C0a-3: the Einstein root is null", gram[0, 0] == 0)
check("C0a-3: Einstein and Jordan modes pair nontrivially",
      gram[0, 1] == 1 and gram[1, 0] == 1)
check("C0a-3: the symplectic current is time independent",
      all(sp.simplify(sp.diff(x, t)) == 0 for x in
          [omega_EE, omega_EL, omega_LE, omega_LL]))
check("C0a-3: the one-particle Gram form is nondegenerate",
      sp.simplify(gram.det()) != 0)
check("C0a-3: L -> L-(<L,L>/2)E gives J1=sigma_x",
      sp.simplify(gram_canonical - J1) == sp.zeros(2))


# ---------------------------------------------------------------------------
# C0a-4: no regular local elementary O(1,1) presentation
# ---------------------------------------------------------------------------
x11, x12, x21, x22 = sp.symbols("x11 x12 x21 x22", real=True)
X = sp.Matrix([[x11, x12], [x21, x22]])
variation = sp.expand(X.T * K + K * X)
symmetry_equations = []
for entry in variation:
    polynomial = sp.Poly(entry, z)
    symmetry_equations.extend(polynomial.all_coeffs())
symmetry_solutions = sp.solve(
    symmetry_equations, [x11, x12, x21, x22], dict=True
)
check("C0a-4: the local constant two-field action has no continuous internal generator",
      symmetry_solutions == [{x11: 0, x12: 0, x21: 0, x22: 0}])

h_tilde = sp.symbols("h_tilde")
P_nonlocal = sp.Rational(1, 2) / z
lag_shifted = sp.expand(-z * f * (h_tilde - P_nonlocal * f) - f**2 / 2)
check("C0a-4: P(Box)=1/(2 Box) removes the algebraic f^2 term",
      sp.simplify(lag_shifted + z * f * h_tilde) == 0)

degree = 5
p_coeffs = sp.symbols(f"p0:{degree + 1}")
P_polynomial = sum(p_coeffs[n] * z**n for n in range(degree + 1))
local_condition = sp.Poly(sp.expand(z * P_polynomial - sp.Rational(1, 2)), z)
local_solutions = sp.solve(local_condition.all_coeffs(), p_coeffs, dict=True)
check("C0a-4: no finite-derivative polynomial shift can remove f^2",
      local_solutions == [])


# ---------------------------------------------------------------------------
# C0a-5: bosonic two-particle lift and conditional zero pattern
# ---------------------------------------------------------------------------
J_full = sp.kronecker_product(J1, J1)
sqrt2 = sp.sqrt(2)
# Full tensor basis: EE, EL, LE, LL.  Columns embed EE, EL_s, LL.
sym_embedding = sp.Matrix([
    [1, 0, 0],
    [0, 1 / sqrt2, 0],
    [0, 1 / sqrt2, 0],
    [0, 0, 1],
])
J2 = sp.simplify(sym_embedding.T * J_full * sym_embedding)
J2_expected = sp.Matrix([[0, 0, 1], [0, 1, 0], [1, 0, 0]])
check("C0a-5: symmetric two-particle lift has the stated J2",
      J2 == J2_expected)

# Solve J2 T^dagger J2=T together with T_EE,EE=T_EL,EE=T_EE,EL=0.
real_parts = sp.symbols("r0:9", real=True)
imag_parts = sp.symbols("s0:9", real=True)
variables = list(real_parts) + list(imag_parts)
T = sp.Matrix(3, 3, lambda row, col:
              real_parts[3 * row + col] + I * imag_parts[3 * row + col])
T_sharp = sp.simplify(J2 * sp.conjugate(T.T) * J2)
equations: list[sp.Expr] = []
for entry in T_sharp - T:
    equations.extend([sp.re(entry), sp.im(entry)])
for row, col in [(0, 0), (1, 0), (0, 1)]:
    equations.extend([sp.re(T[row, col]), sp.im(T[row, col])])
coefficient_matrix, rhs = sp.linear_eq_to_matrix(equations, variables)
nullspace = coefficient_matrix.nullspace()

expected_free_indices = [2, 4, 6]  # real T_02, T_11, T_20
expected_basis = []
for index in expected_free_indices:
    vector = sp.zeros(18, 1)
    vector[index, 0] = 1
    expected_basis.append(vector)

check("C0a-5: conditional solution space has exactly three real parameters",
      rhs == sp.zeros(rhs.rows, 1) and len(nullspace) == 3)
check("C0a-5: allowed blocks are real T_EE,LL, T_EL,EL, T_LL,EE",
      all(coefficient_matrix * vector == sp.zeros(coefficient_matrix.rows, 1)
          for vector in expected_basis)
      and sp.Matrix.hstack(*expected_basis).rank() == 3)
check("C0a-5: pseudo-unitarity plus Einstein zeros predicts LLLL=ELLL=0",
      coefficient_matrix.rank() == 15)


# ---------------------------------------------------------------------------
# C0a-6: canonical coupling normalization
# ---------------------------------------------------------------------------
alpha = sp.symbols("alpha", positive=True)
h_c = sp.symbols("h_c")
h_unscaled = h_c / sp.sqrt(alpha)
quadratic_scale = sp.simplify(alpha * h_unscaled**2 / h_c**2)
cubic_scale = sp.simplify(alpha * h_unscaled**3 / h_c**3)
quartic_scale = sp.simplify(alpha * h_unscaled**4 / h_c**4)
check("C0a-6: canonical quadratic coefficient is one", quadratic_scale == 1)
check("C0a-6: cubic coupling is g_W=alpha_g^(-1/2)",
      cubic_scale == alpha**(-sp.Rational(1, 2)))
check("C0a-6: quartic coupling is g_W^2=alpha_g^(-1)",
      quartic_scale == alpha**-1)


# ---------------------------------------------------------------------------
# C0a-7: flat physical-cohomology bridge (Kubo--Kuntz convention)
# ---------------------------------------------------------------------------
# Ordered basis (L_+, E_+, L_-, E_-, A_+, A_-).  Their commutators are
# [a_L,a_E^dag]=1 for each TT helicity and [a_A,a_A^dag]=s.  The paper's
# displayed convention has s=+1; reversing the overall Weyl-action sign
# gives s=-1, the sign reached from Paper IV's split-phase convention.
energy = sp.symbols("energy", positive=True, real=True)
jordan_step = sp.Rational(1, 4) / energy
H_jordan = sp.Matrix([[energy, 0], [jordan_step, energy]])
H_full = sp.diag(H_jordan, H_jordan, energy, energy)


def full_gram(vector_sign: int) -> sp.Matrix:
    return sp.diag(J1, J1, vector_sign, vector_sign)


J_phys_plus = full_gram(+1)
J_phys_minus = full_gram(-1)
check("C0a-7: full flat cohomology has two TT Jordan pairs and two vector modes",
      J_phys_plus.det() != 0 and J_phys_minus.det() != 0)
check("C0a-7: the published full Hamiltonian preserves the cross-paired form",
      sp.simplify(H_full.T * J_phys_plus - J_phys_plus * H_full) == sp.zeros(6)
      and sp.simplify(H_full.T * J_phys_minus - J_phys_minus * H_full) == sp.zeros(6))

plus_eigenvalues = J_phys_plus.eigenvals()
minus_eigenvalues = J_phys_minus.eigenvals()
check("C0a-7: vector-sign + gives signature (4,2)",
      plus_eigenvalues.get(1) == 4 and plus_eigenvalues.get(-1) == 2)
check("C0a-7: reversing the action sign gives signature (2,4)",
      minus_eigenvalues.get(1) == 2 and minus_eigenvalues.get(-1) == 4)

# Classify all Hermitian forms preserved by one real Jordan block.
j11, j12_re, j12_im, j22 = sp.symbols(
    "j11 j12_re j12_im j22", real=True
)
J_general = sp.Matrix([
    [j11, j12_re + I * j12_im],
    [j12_re - I * j12_im, j22],
])
invariance = sp.expand(H_jordan.T * J_general - J_general * H_jordan)
invariance_equations = []
for entry in invariance:
    invariance_equations.extend([sp.re(entry), sp.im(entry)])
form_solution = sp.solve(
    invariance_equations, [j11, j12_re, j12_im, j22], dict=True
)
check("C0a-7: invariant Jordan forms require real cross-pairing and null eigenmode",
      form_solution == [{j12_im: 0, j22: 0}])
det_invariant_form = sp.factor(J_general.subs(form_solution[0]).det())
check("C0a-7: every nondegenerate invariant Jordan form is indefinite",
      det_invariant_form == -j12_re**2)


if not PASS:
    raise SystemExit("CONFORMAL C0A: FAIL")
print("CONFORMAL C0A: ALL PASS")
