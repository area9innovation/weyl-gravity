/-
Verification E in Lean (Phase 1): the congruence S^T G S = G0.

Division-free formulation.  With sg^2 = w1^2 - w2^2 we scale T := sg * S,
whose entries are polynomial:
  T = w1 * 1 + w2 * N u (gm*w1*w2),   u * (gm*w1*w2) = 1,   m * w1 = 1.
The congruence becomes the polynomial identity
  T^T * G * T = sg^2 * G0
with G, G0 written division-free via u and m:
  G  = G (gm(w1^2+w2^2)) (gm w1^2 w2^2) (u w1 w2)          [1/gm = u w1 w2]
  G0 = diag(gm w1^2, gm w1^2 w2^2, u w1 w2, u w2 m)        [1/(gm w1^2) = u w2 m]
Every entry closes by `linear_combination` with certificates computed by
polynomial reduction (see symbolic/verify_sympy.py pipeline).
The division form S = sg^{-1} T then gives S^T G S = G0 (S_congruence).
-/
import PaisUhlenbeck.Definitions
import PaisUhlenbeck.Symplectic
import Mathlib

namespace PaisUhlenbeck

open Matrix

/-- The scaled congruence: T^T G T = sg^2 * G0, entirely polynomial. -/
theorem T_congruence (gm w1 w2 sg u m : ℂ)
    (hI : Complex.I ^ 2 = -1)
    (hs2 : sg ^ 2 - w1 ^ 2 + w2 ^ 2 = 0)
    (hu : u * gm * w1 * w2 - 1 = 0)
    (hm : m * w1 - 1 = 0)
    (hum : gm * u * w2 - m = 0) :
    (w1 • (1 : M4) + w2 • N u (gm * w1 * w2))ᵀ
        * G (gm * (w1 ^ 2 + w2 ^ 2)) (gm * w1 ^ 2 * w2 ^ 2) (u * w1 * w2)
        * (w1 • (1 : M4) + w2 • N u (gm * w1 * w2))
      = (sg ^ 2) • G0 (gm * w1 ^ 2) (gm * w1 ^ 2 * w2 ^ 2) (u * w1 * w2) (u * w2 * m) := by
  ext i j
  simp only [N, G, G0, Matrix.mul_apply, Matrix.transpose_apply, Fin.sum_univ_four,
    Matrix.add_apply, Matrix.smul_apply, Matrix.one_apply]
  fin_cases i <;> fin_cases j <;> (try simp) <;>
    first
    | ring1
    | linear_combination (norm := ring1) ((2*gm*w1^2*w2^2) * hI + (-gm*w1^2) * hs2)
    | linear_combination (norm := ring1) ((Complex.I*gm*u*w1*w2^3) * hI + (-Complex.I*gm*u*w1*w2 + Complex.I) * hs2 + (Complex.I*sg^2 + Complex.I*w2^2) * hu)
    | linear_combination (norm := ring1) ((gm^2*u*w1^3*w2^5) * hI + (gm^2*u*w1*w2^5 - gm*w1^2*w2^2 - gm*w2^4) * hs2 + (-gm*sg^2*w2^4 - gm*w2^6) * hu)
    | linear_combination (norm := ring1) ((gm*u^2*w1^2*w2^4) * hI + (-(u*w1*w2)) * hs2 + (-(u*w1*w2^3)) * hu)
    | linear_combination (norm := ring1) ((gm*u^2*w1^2*w2^2 + gm*u^2*w2^4 - 2*u*w1*w2) * hI + (-(m*u*w2)) * hs2 + (-(u*w1*w2)) * hm + (-(u*w1*w2)) * hu + (-(u*w2^3)) * hum)

/-- Verification E1: S^T G S = G0 in the division form, derived from the
    scaled polynomial congruence. -/
theorem S_congruence (gm w1 w2 sg : ℂ)
    (hgm : gm ≠ 0) (hw1 : w1 ≠ 0) (hw2 : w2 ≠ 0) (hsg : sg ≠ 0)
    (hs2 : sg ^ 2 = w1 ^ 2 - w2 ^ 2) :
    (S (w1 / sg) (w2 / sg) (1 / (gm * w1 * w2)) (gm * w1 * w2))ᵀ
        * G (gm * (w1 ^ 2 + w2 ^ 2)) (gm * w1 ^ 2 * w2 ^ 2) (1 / (gm * w1 * w2) * w1 * w2)
        * S (w1 / sg) (w2 / sg) (1 / (gm * w1 * w2)) (gm * w1 * w2)
      = G0 (gm * w1 ^ 2) (gm * w1 ^ 2 * w2 ^ 2) (1 / (gm * w1 * w2) * w1 * w2)
          (1 / (gm * w1 * w2) * w2 * (1 / w1)) := by
  have hI : Complex.I ^ 2 = -1 := Complex.I_sq
  set u : ℂ := 1 / (gm * w1 * w2) with hudef
  set m : ℂ := 1 / w1 with hmdef
  have hu : u * gm * w1 * w2 - 1 = 0 := by
    rw [hudef]; field_simp
    all_goals norm_num
  have hm : m * w1 - 1 = 0 := by
    rw [hmdef]; field_simp
    all_goals norm_num
  have hum : gm * u * w2 - m = 0 := by
    rw [hudef, hmdef]; field_simp
    all_goals norm_num
  have hs2' : sg ^ 2 - w1 ^ 2 + w2 ^ 2 = 0 := by rw [hs2]; ring
  have hT := T_congruence gm w1 w2 sg u m hI hs2' hu hm hum
  -- S = sg⁻¹ • T
  have hS : S (w1 / sg) (w2 / sg) u (gm * w1 * w2)
      = sg⁻¹ • (w1 • (1 : M4) + w2 • N u (gm * w1 * w2)) := by
    ext i j
    simp only [S, Matrix.add_apply, Matrix.smul_apply, Matrix.one_apply, smul_add, smul_smul,
      smul_eq_mul]
    fin_cases i <;> fin_cases j <;> simp [N, div_eq_inv_mul] <;> ring
  rw [hS, Matrix.transpose_smul, smul_mul_assoc, smul_mul_assoc, mul_smul_comm,
    smul_smul, hT, smul_smul]
  have hone : sg⁻¹ * sg⁻¹ * sg ^ 2 = 1 := by
    field_simp
  rw [hone, one_smul]

end PaisUhlenbeck
