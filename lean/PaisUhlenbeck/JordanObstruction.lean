/-
Verification L: the Jordan-block obstruction (spec section 14),
fully formalized for the 2x2 block.

For H_J = [[w, 1], [0, w]] (w real) and eta Hermitian with
H_J^dagger * eta = eta * H_J we prove:
  1. structure: eta = [[0, b], [b, d]] with b, d real;
  2. no positive-definite invariant Hermitian form exists;
  3. every positive-semidefinite invariant form is degenerate (det = 0);
  4. every nondegenerate invariant form is indefinite: explicit vectors
     x, y with re <x, eta x> > 0 > re <y, eta y>.
-/
import Mathlib

namespace PaisUhlenbeck.Jordan

open Matrix
open scoped ComplexOrder

abbrev M2 := Matrix (Fin 2) (Fin 2) ℂ

/-- The 2x2 Jordan block with real eigenvalue w. -/
def HJ (w : ℝ) : M2 := !![(w : ℂ), 1; 0, (w : ℂ)]

/-- eta is an invariant sesquilinear form for H_J. -/
def Invariant (w : ℝ) (η : M2) : Prop := (HJ w)ᴴ * η = η * HJ w

/-- The quadratic form of eta at x. -/
noncomputable def qf (η : M2) (x : Fin 2 → ℂ) : ℂ := star x ⬝ᵥ (η *ᵥ x)

section Structure

variable {w : ℝ} {η : M2}

/-- Invariance forces the (0,0) entry to vanish. -/
theorem eta00_zero (hinv : Invariant w η) : η 0 0 = 0 := by
  have h := congrArg (fun m => m 0 1) hinv
  simp only [HJ, Matrix.mul_apply, Matrix.conjTranspose_apply, Fin.sum_univ_two] at h
  simp at h
  linear_combination -h

/-- Invariance forces eta 0 1 = eta 1 0. -/
theorem eta01_eq_eta10 (hinv : Invariant w η) : η 0 1 = η 1 0 := by
  have h := congrArg (fun m => m 1 1) hinv
  simp only [HJ, Matrix.mul_apply, Matrix.conjTranspose_apply, Fin.sum_univ_two] at h
  simp at h
  linear_combination h

/-- Structure theorem: every Hermitian invariant form is [[0, b], [b, d]]
    with b, d real. -/
theorem invariant_form (hinv : Invariant w η) (hherm : η.IsHermitian) :
    ∃ b d : ℝ, η = !![0, (b : ℂ); (b : ℂ), (d : ℂ)] := by
  have h00 : η 0 0 = 0 := eta00_zero hinv
  have h01 : η 0 1 = η 1 0 := eta01_eq_eta10 hinv
  have h10s : η 1 0 = star (η 0 1) := by
    have := congrArg (fun m => m 1 0) hherm
    simpa [Matrix.conjTranspose_apply] using this.symm
  have hbim : (η 0 1).im = 0 := by
    have : η 0 1 = star (η 0 1) := h01.trans h10s
    have him := congrArg Complex.im this
    simp only [Complex.star_def, Complex.conj_im] at him
    linarith
  have hdim : (η 1 1).im = 0 := by
    have := congrArg (fun m => m 1 1) hherm
    simp only [Matrix.conjTranspose_apply] at this
    have him := congrArg Complex.im this
    simp only [Complex.star_def, Complex.conj_im] at him
    linarith
  obtain ⟨br, hbr⟩ : ∃ br : ℝ, η 0 1 = (br : ℂ) :=
    ⟨(η 0 1).re, Complex.ext rfl (by simpa using hbim)⟩
  obtain ⟨dr, hdr⟩ : ∃ dr : ℝ, η 1 1 = (dr : ℂ) :=
    ⟨(η 1 1).re, Complex.ext rfl (by simpa using hdim)⟩
  refine ⟨br, dr, ?_⟩
  have hexp : η = !![η 0 0, η 0 1; η 1 0, η 1 1] := by
    ext i j
    fin_cases i <;> fin_cases j <;> rfl
  rw [hexp, h00, ← h01, hbr, hdr]

end Structure

section NoGo

variable {w : ℝ} {η : M2}

/-- The quadratic form of [[0,b],[b,d]] at ![1, t] (t real) is 2tb + t^2 d. -/
theorem qf_form (b d t : ℝ) :
    qf !![0, (b : ℂ); (b : ℂ), (d : ℂ)] ![1, (t : ℂ)] =
      ((2 * t * b + t ^ 2 * d : ℝ) : ℂ) := by
  simp [qf, Matrix.mulVec, dotProduct, Fin.sum_univ_two]
  push_cast
  ring

/-- Part 3: no positive-definite invariant Hermitian form exists. -/
theorem no_posdef (hinv : Invariant w η) : ¬ η.PosDef := by
  intro hpd
  obtain ⟨b, d, hform⟩ := invariant_form hinv hpd.1
  have hx : ((![1, 0] : Fin 2 → ℂ)) ≠ 0 := by
    intro h
    have := congrFun h 0
    simp at this
  have hq := hpd.dotProduct_mulVec_pos hx
  have hval : star (![1, 0] : Fin 2 → ℂ) ⬝ᵥ (η *ᵥ ![1, 0]) = 0 := by
    rw [hform]
    simp [Matrix.mulVec, dotProduct, Fin.sum_univ_two]
  rw [hval] at hq
  exact lt_irrefl _ hq

/-- Part 2: every positive-semidefinite invariant form is degenerate. -/
theorem psd_degenerate (hinv : Invariant w η) (hpsd : η.PosSemidef) :
    η.det = 0 := by
  obtain ⟨b, d, hform⟩ := invariant_form hinv hpsd.1
  subst hform
  -- b must vanish: q(![1,t]) = 2tb + t^2 d >= 0 for all real t.
  have hq : ∀ t : ℝ, (0 : ℝ) ≤ 2 * t * b + t ^ 2 * d := by
    intro t
    have h := hpsd.dotProduct_mulVec_nonneg ![1, (t : ℂ)]
    rw [show star ![(1 : ℂ), (t : ℂ)] ⬝ᵥ
        ((!![0, (b : ℂ); (b : ℂ), (d : ℂ)]) *ᵥ ![1, (t : ℂ)]) =
        qf !![0, (b : ℂ); (b : ℂ), (d : ℂ)] ![1, (t : ℂ)] from rfl, qf_form] at h
    exact_mod_cast h
  have hb : b = 0 := by
    by_contra hb0
    set ε : ℝ := 1 / (1 + |d|) with hεdef
    have hεpos : 0 < ε := by positivity
    have hεd : ε * |d| < 1 := by
      rw [hεdef, div_mul_eq_mul_div, div_lt_one (by positivity)]
      linarith [abs_nonneg d]
    have hb2 : 0 < b ^ 2 := by positivity
    have h := hq (-(ε * b))
    have hval : 2 * (-(ε * b)) * b + (-(ε * b)) ^ 2 * d = ε * b ^ 2 * (-2 + ε * d) := by
      ring
    rw [hval] at h
    have hneg : -2 + ε * d < 0 := by
      have : ε * d ≤ ε * |d| := by
        have := le_abs_self d
        nlinarith
      linarith
    have : ε * b ^ 2 * (-2 + ε * d) < 0 :=
      mul_neg_of_pos_of_neg (mul_pos hεpos hb2) hneg
    linarith
  subst hb
  rw [Matrix.det_fin_two]
  simp

/-- Part 1: every nondegenerate invariant Hermitian form is indefinite:
    explicit vectors with positive and negative (real) quadratic form. -/
theorem nondegenerate_indefinite (hinv : Invariant w η) (hherm : η.IsHermitian)
    (hdet : η.det ≠ 0) :
    ∃ x y : Fin 2 → ℂ, 0 < (qf η x).re ∧ (qf η y).re < 0 := by
  obtain ⟨b, d, hform⟩ := invariant_form hinv hherm
  subst hform
  have hb0 : b ≠ 0 := by
    intro hb
    apply hdet
    subst hb
    rw [Matrix.det_fin_two]
    simp
  set ε : ℝ := 1 / (1 + |d|) with hεdef
  have hεpos : 0 < ε := by positivity
  have hεd : ε * |d| < 1 := by
    rw [hεdef, div_mul_eq_mul_div, div_lt_one (by positivity)]
    linarith [abs_nonneg d]
  have hb2 : 0 < b ^ 2 := by positivity
  have hεdle : ε * d ≤ ε * |d| := by
    have := le_abs_self d
    nlinarith
  have hεdge : -(ε * |d|) ≤ ε * d := by
    have := neg_abs_le d
    nlinarith
  refine ⟨![1, ((ε * b : ℝ) : ℂ)], ![1, ((-(ε * b) : ℝ) : ℂ)], ?_, ?_⟩
  · rw [qf_form]
    have hval : 2 * (ε * b) * b + (ε * b) ^ 2 * d = ε * b ^ 2 * (2 + ε * d) := by
      ring
    have hpos2 : 0 < 2 + ε * d := by linarith
    have : 0 < ε * b ^ 2 * (2 + ε * d) := mul_pos (mul_pos hεpos hb2) hpos2
    simp only [Complex.ofReal_re]
    linarith [hval ▸ this]
  · rw [qf_form]
    have hval : 2 * (-(ε * b)) * b + (-(ε * b)) ^ 2 * d = ε * b ^ 2 * (-2 + ε * d) := by
      ring
    have hneg2 : -2 + ε * d < 0 := by linarith
    have : ε * b ^ 2 * (-2 + ε * d) < 0 :=
      mul_neg_of_pos_of_neg (mul_pos hεpos hb2) hneg2
    simp only [Complex.ofReal_re]
    linarith [hval ▸ this]

end NoGo

end PaisUhlenbeck.Jordan
