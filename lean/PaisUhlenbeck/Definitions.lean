/-
Definitions for the Pais-Uhlenbeck symplectic reconstruction audit.

Conventions (spec section 2):
  V = (x, y, p, q)^T,  J = [[0,I2],[-I2,0]],  H = 1/2 V^T G V,  A = J G.

To keep every statement division-free we parametrize by real numbers subject
to product-form hypotheses:
  * a, b   : the Bender-Mannheim coefficients alpha, beta  (a*b = r^2)
  * u, v   : u = alpha/r = 1/(gamma w1 w2), v = beta/r = gamma w1 w2  (u*v = 1)
  * c, s   : cosh(r/2), sinh(r/2)                          (c^2 - s^2 = 1)
and relate them to gamma, w1, w2 only where needed (NormalForm.lean).
-/
import Mathlib

namespace PaisUhlenbeck

open Matrix

abbrev M4 := Matrix (Fin 4) (Fin 4) ℂ

/-- The symplectic form matrix J (spec section 2). -/
def J : M4 :=
  !![0, 0, 1, 0;
     0, 0, 0, 1;
     -1, 0, 0, 0;
     0, -1, 0, 0]

/-- The PU quadratic-form matrix G (spec section 3), parameters as complex
    scalars g1 = gamma (w1^2 + w2^2), g2 = gamma w1^2 w2^2, g3 = 1/gamma. -/
def G (g1 g2 g3 : ℂ) : M4 :=
  !![g1, 0, 0, -Complex.I;
     0, g2, 0, 0;
     0, 0, g3, 0;
     -Complex.I, 0, 0, 0]

/-- The positive normal form G0 (spec section 7), diagonal entries abstract. -/
def G0 (d1 d2 d3 d4 : ℂ) : M4 :=
  !![d1, 0, 0, 0;
     0, d2, 0, 0;
     0, 0, d3, 0;
     0, 0, 0, d4]

/-- The Bender-Mannheim quadratic matrix M with Q = 1/2 V^T M V = a pq + b xy. -/
def Mq (a b : ℂ) : M4 :=
  !![0, b, 0, 0;
     b, 0, 0, 0;
     0, 0, 0, a;
     0, 0, a, 0]

/-- K = J M (spec section 5). -/
def K (a b : ℂ) : M4 :=
  !![0, 0, 0, a;
     0, 0, a, 0;
     0, -b, 0, 0;
     -b, 0, 0, 0]

/-- N = iK/r written division-free: u = a/r, v = b/r with u v = 1. -/
def N (u v : ℂ) : M4 :=
  !![0, 0, 0, Complex.I * u;
     0, 0, Complex.I * u, 0;
     0, -Complex.I * v, 0, 0;
     -Complex.I * v, 0, 0, 0]

/-- S = cosh(r/2) I + sinh(r/2) N  (the candidate exponential, spec section 6). -/
def S (c s u v : ℂ) : M4 := c • (1 : M4) + s • N u v

/-- K = J * Mq: the defining relation, proved by entrywise computation. -/
theorem K_eq_J_mul_M (a b : ℂ) : K a b = J * Mq a b := by
  simp only [K, J, Mq]
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [Matrix.mul_apply, Fin.sum_univ_four]

end PaisUhlenbeck
