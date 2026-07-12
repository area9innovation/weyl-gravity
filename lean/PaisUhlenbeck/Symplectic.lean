/-
Core matrix identities (spec sections 5-6, Lean plan Phase 1):
  * K^2 = -(a b) I                                  (Verification C)
  * N^2 = I  when u v = 1
  * N^T J = - (J N)   (N is J-Hamiltonian)
  * S^T J S = J  when u v = 1 and c^2 - s^2 = 1     (Verification D2)
  * det S = 1    under the same hypotheses          (Verification D3)
-/
import PaisUhlenbeck.Definitions
import Mathlib

namespace PaisUhlenbeck

open Matrix

/-- Verification C: K^2 = -(a b) I.  Identity in a, b: no hypotheses. -/
theorem K_sq (a b : ℂ) : K a b * K a b = (-(a * b)) • (1 : M4) := by
  ext i j
  simp only [K, Matrix.mul_apply, Fin.sum_univ_four, Matrix.smul_apply, Matrix.one_apply]
  fin_cases i <;> fin_cases j <;> simp <;> ring

/-- N squares to the identity when u v = 1. -/
theorem N_sq (u v : ℂ) (huv : u * v = 1) : N u v * N u v = 1 := by
  have hI : Complex.I ^ 2 = -1 := Complex.I_sq
  ext i j
  simp only [N, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply]
  fin_cases i <;> fin_cases j <;> simp <;>
    linear_combination (-(u * v)) * hI + huv

/-- N is Hamiltonian for J: N^T J = -(J N).  Identity in u, v. -/
theorem NT_J_anti (u v : ℂ) : (N u v)ᵀ * J = -(J * N u v) := by
  ext i j
  simp only [N, J, Matrix.mul_apply, Matrix.transpose_apply, Fin.sum_univ_four,
    Matrix.neg_apply]
  fin_cases i <;> fin_cases j <;> simp

/-- Verification D2: S^T J S = J under u v = 1 and c^2 - s^2 = 1.
    Algebraic proof: the cross terms cancel by `NT_J_anti`, and
    N^T J N = -(J N) N = -J N^2 = -J. -/
theorem S_symplectic (c s u v : ℂ) (huv : u * v = 1) (hcs : c ^ 2 - s ^ 2 = 1) :
    (S c s u v)ᵀ * J * S c s u v = J := by
  have hN2 := N_sq u v huv
  have hNJ := NT_J_anti u v
  have hST : (S c s u v)ᵀ = c • (1 : M4) + s • (N u v)ᵀ := by
    simp [S, Matrix.transpose_add, Matrix.transpose_smul, Matrix.transpose_one]
  have hNJN : (N u v)ᵀ * (J * N u v) = -J := by
    rw [← Matrix.mul_assoc, hNJ, neg_mul, Matrix.mul_assoc, hN2, Matrix.mul_one]
  have expand :
      (S c s u v)ᵀ * J * S c s u v =
        (c * c) • J + (c * s) • (J * N u v) + (s * c) • ((N u v)ᵀ * J)
          + (s * s) • ((N u v)ᵀ * (J * N u v)) := by
    rw [hST]
    show (c • (1 : M4) + s • (N u v)ᵀ) * J * (c • (1 : M4) + s • N u v) = _
    simp only [Matrix.add_mul, Matrix.mul_add, Matrix.smul_mul, Matrix.mul_smul,
      Matrix.one_mul, Matrix.mul_one, Matrix.mul_assoc]
    module
  rw [expand, hNJ, hNJN]
  have hfinal : (c * c) • J + (c * s) • (J * N u v) + (s * c) • -(J * N u v)
      + (s * s) • -J = (c ^ 2 - s ^ 2) • J := by
    module
  rw [hfinal, hcs, one_smul]

/-- Cofactor helper: the block-sparse determinant shape of S. -/
theorem det_block_sparse (c A B : ℂ) :
    (!![c, 0, 0, A;
        0, c, A, 0;
        0, B, c, 0;
        B, 0, 0, c] : M4).det = (c ^ 2 - A * B) ^ 2 := by
  set_option maxHeartbeats 1000000 in
  rw [Matrix.det_succ_row_zero]
  simp [Fin.sum_univ_succ, Matrix.det_fin_three,
    show Fin.succAbove 3 2 = (2 : Fin 4) from rfl]
  ring

/-- Verification D3: det S = 1 under u v = 1 and c^2 - s^2 = 1.
    det S = (c^2 + I^2 s^2 u v)^2 by cofactor expansion. -/
theorem S_det (c s u v : ℂ) (huv : u * v = 1) (hcs : c ^ 2 - s ^ 2 = 1) :
    (S c s u v).det = 1 := by
  have hI : Complex.I ^ 2 = -1 := Complex.I_sq
  have hS : S c s u v =
      !![c, 0, 0, Complex.I * (s * u);
         0, c, Complex.I * (s * u), 0;
         0, -(Complex.I * (s * v)), c, 0;
         -(Complex.I * (s * v)), 0, 0, c] := by
    ext i j
    simp only [S, N, Matrix.add_apply, Matrix.smul_apply, Matrix.one_apply]
    fin_cases i <;> fin_cases j <;> simp <;> ring
  rw [hS, det_block_sparse]
  linear_combination (norm := ring)
    (s ^ 2 * u * v * (2 * c ^ 2 + (Complex.I ^ 2 - 1) * s ^ 2 * u * v)) * hI
    + (c ^ 2 - s ^ 2 * u * v + 1) * hcs
    - (s ^ 2 * (c ^ 2 - s ^ 2 * u * v + 1)) * huv

end PaisUhlenbeck
