# Verification report: Symplectic reconstruction of the Pais–Uhlenbeck PT metric

**Status of the audit** (spec: `physics/Symplectic Reconstruction.md`).
Symbolic engine: SymPy 1.14 (`symbolic/verify_sympy.py`, 51 machine-checked claims,
`reports/verification.json`). Numerics: mpmath at 50–80 significant digits
(`numeric/regression.py`, `reports/regression.json`), four parameter triples
including the near-degenerate `(1, 1.0001, 1)`. Lean 4 formalization: see
`lean/` and §5 below.

Conventions used throughout (spec §2): `V = (x,y,p,q)ᵀ`, `[x,p] = [y,q] = i`,
`J = [[0,I₂],[−I₂,0]]`, `H = ½VᵀGV`, `A = JG`, `γ > 0`, `ω₁ > ω₂ > 0`,
`r = log((ω₁+ω₂)/(ω₁−ω₂)) > 0`, `s := √(ω₁²−ω₂²)`.

---

## 1. Confirmed results

| # | Result | Where proved |
|---|--------|--------------|
| A | `½VᵀGV = H_PT` with the spec's G; `det(λI−A) = (λ²+ω₁²)(λ²+ω₂²)` computed from the determinant directly (not from the PU equation) | A1, A2 |
| B | `αβ = r²` with `r = log((ω₁+ω₂)/(ω₁−ω₂))`; positivity `α, β > 0` (from `ω₁ > ω₂ > 0`, `γ > 0`) removes the square-root ambiguity; `Q = ½VᵀMV` exact | B1–B3 |
| C | `K = JM` satisfies `K² = −αβ I = −r² I` | C1 |
| C | **Derived** (not assumed) commutator: `[Q, V] = −iKV` (V column vector, componentwise). The variant `[Q,V] = +iKV` is wrong under `[x,p] = +i` | C2 |
| C | `e^{−Q/2} V e^{Q/2} = e^{+iK/2} V` and `e^{Q/2} V e^{−Q/2} = e^{−iK/2} V` | C3 |
| D | `S(t) = cosh(rt)I + i sinh(rt)K/r` satisfies `S(0)=I`, `S′ = iKS`, hence equals `e^{iKt}` (power-series/ODE argument); the candidate `S = cosh(r/2)I + i(K/r)sinh(r/2)` **is** correct with sign convention `e^{−Q/2}Ve^{Q/2} = SV` | D1 |
| D | Hyperbolic-values lemma: `cosh(r/2) = ω₁/s`, `sinh(r/2) = ω₂/s`, `cosh r = (ω₁²+ω₂²)/(ω₁²−ω₂²)`, `sinh r = 2ω₁ω₂/(ω₁²−ω₂²)`, `tanh r = 2ω₁ω₂/(ω₁²+ω₂²)` | D1b |
| D | `SᵀJS = J`, `det S = 1` | D2, D3 |
| E | `SᵀGS = G₀` exactly, with the spec's `G₀ = diag(γω₁², γω₁²ω₂², γ⁻¹, (γω₁²)⁻¹)`; all six mixed coefficients (xq, yp, xp, yq, xy, pq) vanish identically | E1, E3 |
| E | Flow relation: `S⁻¹AS = A₀` (mutually consistent with E1 via `JSᵀ = S⁻¹J`) | E2 |
| F | Reconstruction **without assuming Q**: full solution family of `{SᵀJS = J, SᵀG′S = G₀′}` is the coset `S′₊ · Stab(J, G₀′)`; the Hermitian-positive member is **unique** and equals `S′₊ = e^{iK′/2}`; `log S′₊ = (r/2)B` reconstructs exactly the Bender–Mannheim `Q = αpq + βxy` | F1–F8 |
| F | The candidate `S = (tI + B)/√(t²−1)`, `t = ω₁/ω₂`, is **correct in the rescaled coordinates** (see §2, correction 2) | F9 |
| G | `Q† = Q` at the formal algebraic level (α, β real; `[p,q] = [x,y] = 0`) | G2 |
| G | Matrix-level pseudo-Hermiticity: `S^{2T} G S² = Ḡ`, the exact matrix form of `e^{−Q} H_PT e^{Q} = H_PT†`, i.e. `η H_PT = H_PT† η` with `η = e^{−Q}` | G1 |
| G | Formal implication mechanized in the free algebra: `ρ(h†−h)ρ = H†η − ηH` for `ρ† = ρ`, `η = ρ²`, `h = ρHρ⁻¹` | G3 |
| H | Classification: `η′ ↦ W = ρ^{−†}η′ρ⁻¹` is a bijection between positive invertible intertwiners (`H†η′ = η′H`) and `{W > 0 invertible, [W,h] = 0}`; both directions proved; `W = I` gives the canonical `η = e^{−Q}` | H1, H2 |
| I | `C = S₁⁻¹S₂ ∈ Stab(J, G₀)` for any two admissible diagonalizers | I1 |
| J | `M_obs = S′†S′ = S′²` has spectrum `{e^r, e^r, e^{−r}, e^{−r}}` — **in the rescaled coordinates** (see correction 4) | J1, J2 |
| J | `d(I, M_obs) = ‖log M_obs‖_F = 2r = 2·log((ω₁+ω₂)/(ω₁−ω₂))`, with the trace metric normalized as `⟨U,V⟩_G = tr(G⁻¹UG⁻¹V)` and **no** extra factor | J3 |
| K | `r = log(ω/ε)` **exactly** (not just asymptotically) for `ω₁ = ω+ε`, `ω₂ = ω−ε` | K1 |
| K | `S′ ~ ½√(ω/ε)(I+B)` diverges like `ε^{−1/2}`, collapsing onto the rank-2 spectral projector of B (exceptional-point degeneration); `d = 2 log(ω/ε) → ∞`; **no scalar normalization** gives a finite positive nondegenerate limit (proved: top/bottom eigenvalue ratio `(ω/ε)² → ∞`) | K2–K4 |
| L | Jordan block (2×2): invariant Hermitian forms are exactly `η = [[0,b],[b,d]]`, b real; nondegenerate ⇒ indefinite (`det = −b² < 0`); PSD ⇒ degenerate; positive-definite impossible. General n: invariant forms are anti-triangular Hankel with `η₁₁ = 0` (mechanized at n = 5; general proof below) | L1–L3 |

**General-n Jordan proof** (L3). Write `H_J = ωI + N`, ω real, N the nilpotent
shift. Invariance `H_J†η = ηH_J` reduces to `Nᵀη = ηN`, i.e.
`η_{j−1,k} = η_{j,k−1}` (constant anti-diagonals: Hankel) with boundary
`η_{1,k} = 0` for `k ≤ n−1` (anti-triangular). In particular `η₁₁ = 0 = ⟨e₁, ηe₁⟩`
with `e₁ ≠ 0`, so no invariant positive-definite form exists for any `n ≥ 2`;
a PSD form with a zero diagonal entry has zero row 1, hence is degenerate;
a nondegenerate one needs the full anti-diagonal nonzero and is indefinite
(the quadratic form on `span{e₁, eₙ}` is a hyperbolic plane up to sign).

---

## 2. Corrected formulas / claims

1. **S is NOT Hermitian in the original variables** (D4a; spec §6.4 asked).
   `S₁₄ = i·sinh(r/2)/(γω₁ω₂ s)·…` vs `S₄₁ = −i·γω₁ω₂·sinh(r/2)/s`: Hermiticity
   requires `α = β`, i.e. `γω₁ω₂ = 1`. Numerically `‖S − S†‖ = 1.73, 13.0, 867`
   at the three generic triples.

2. **Exact canonical rescaling** (D4b). `D = diag(d_x, d_y, 1/d_x, 1/d_y)` is
   symplectic for all `d_x, d_y > 0`; the rescaled `S′ = DSD⁻¹` is Hermitian
   positive **iff `d_x·d_y = γω₁ω₂`** (only the product enters
   `K′ = DKD⁻¹`). Symmetric choice `d_x = d_y = √(γω₁ω₂)`. Then
   `B = iK′/r = [[0,0,0,i],[0,0,i,0],[0,−i,0,0],[−i,0,0,0]]` is a parameter-free
   Hermitian involution and `S′ = cosh(r/2)I + sinh(r/2)B > 0` with spectrum
   `{e^{±r/2}}`, each twice.

3. **The stabilizer is NOT exactly U(1)×U(1)** (I2; spec §11 asked to check).
   Over ℂ, `Stab(J, G₀′) = SO(2,ℂ) × SO(2,ℂ)` (one complex rotation angle per
   normal mode; F1 commutant is exactly 4-dimensional for `ω₁ ≠ ω₂`).
   `U(1)×U(1)` is precisely its **unitary subgroup** (real angles); imaginary
   angles give non-unitary hyperbolic elements.

4. **The polar-factor uniqueness claim is FALSE as stated** (I3; spec §11).
   Explicit counterexample: `C(θ₁ = i/3, θ₂ = 0)` is admissible
   (residuals < 1e−25) but `‖(S′₊C)†(S′₊C) − S′₊²‖ ≈ 3.6 ≠ 0`.
   **Strongest correct uniqueness theorem:**
   *There is exactly one Hermitian positive-definite admissible diagonalizer,
   namely `S′₊ = e^{iK′/2}`. The positive polar factor of a general admissible
   diagonalizer `S′₊C` equals `S′₊` iff `C` is unitary; hence the polar factor
   is constant exactly on the coset `S′₊·U(1)²`, and the set of polar factors
   is a 2-real-parameter family parametrized by the hyperbolic directions of
   the stabilizer* — the finite-dimensional shadow of the `W`-freedom in the
   metric classification (Verification H).

5. **The candidate spectrum `{e^r, e^r, e^{−r}, e^{−r}}` of `M_obs = S†S` holds
   only after the canonical rescaling** (J2). In the original coordinates
   `S†S` has a different, γ-dependent spectrum. The spec's phrase "after a
   verified symplectic normalization" is thereby made precise: the
   normalization is correction 2, and it is unique up to the `d_x/d_y` split,
   which `M_obs`'s spectrum does not see.

6. **Commutator convention resolved** (C2): with `[x,p] = +i` and V a column
   vector, the correct identity is `[Q, V] = −iKV`, and the exponent
   convention is `e^{−Q/2}Ve^{Q/2} = e^{+iK/2}V = SV`. The congruence that
   holds is `SᵀGS = G₀` (E1) with flow `S⁻¹AS = A₀` (E2); the inverse-position
   variants are false (checked: `S^{−T}GS⁻¹` is not even diagonal).

---

## 3. Unproved assumptions (declared, not claimed)

* **Operator domains.** All operator statements (`Q† = Q`, `η = e^{−Q}`
  bounded/invertible, closability of `H_PT`) are made at the formal algebraic
  level on the dense invariant domain of finite linear combinations of
  oscillator (Schwartz) states. `e^{−Q}` is unbounded; the finite-dimensional
  results proved here are exact statements about the metaplectic/symplectic
  data and do **not** by themselves constitute an operator-theoretic
  similarity theorem. This is exactly the split the spec's §9 demands
  (formal part mechanized in G3; analytic part not claimed).
* **W-classification at operator level** (H). The bijection is proved
  algebraically (free algebra, G3-style). The statement that `[W, h] = 0` for
  the PU h forces `W = f(N₁, N₂)` uses the spectral theorem for the two
  commuting number operators — standard, but analytic, hence listed here.
* Genericity: all uniqueness statements assume `ω₁ ≠ ω₂` (and `γω₁ω₂ ≠ 1`
  only where explicitly flagged in F5's linear solve; the conclusion `C = ±I`
  was cross-checked numerically at `γω₁ω₂ = 2, 15, 210, ≈1` with no extra
  solutions found).

---

## 4. Failed claims

* **"The positive polar factor of every admissible diagonalizer is the same"**
  — disproved with an explicit counterexample; replacement theorem in §2.4.
* **"Stab(J, G₀) = U(1)×U(1)"** — false over ℂ; it is `SO(2,ℂ)²`, with
  `U(1)²` as its unitary subgroup (§2.3).
* **"S is Hermitian positive"** in the original variables — false unless
  `γω₁ω₂ = 1`; true after the canonical rescaling (§2.1–2.2).
* No other candidate formula failed: G, the characteristic polynomial, α, β,
  r, M, K, the exponential formula, G₀, the congruence, `Q† = Q`, the
  spectrum-after-rescaling, the distance `2r`, and the equal-frequency
  divergence all verified.

---

## 5. Lean 4 formalization status

`lean/PaisUhlenbeck/` (Mathlib v4.29.0):

* `Definitions.lean` — J, G, G₀, M, K, N = iK/r, S as explicit
  `Matrix (Fin 4) (Fin 4) ℂ` with abstract real parameters and product-form
  hypotheses (no division in statements).
* `Symplectic.lean` — `K² = −(αβ)I`; `N² = I`; `SᵀJS = J`; `det S = 1`.
* `NormalForm.lean` — `SᵀGS = G₀` under the declared hypotheses.
* `JordanObstruction.lean` — the 2×2 no-go theorem, self-contained
  (invariant Hermitian forms have `η₁₁ = 0`, `η₀₁` real; no positive-definite
  invariant form; PSD ⇒ degenerate; nondegenerate ⇒ indefinite via explicit
  witness vectors).

Files listed as completed contain no `sorry`. Phases 2–4 of the spec's Lean
plan (transcendental identities, matrix exponential, abstract polar
uniqueness) are **not** attempted; the corresponding facts rest on the SymPy
proofs plus the 50–80-digit numerics.

**Independent-CAS caveat (spec §17):** only one CAS (SymPy) is installed on
this machine; Wolfram/Mathematica and Sage are not available. The second
independent rail is (i) the numeric mpmath implementation, which rebuilds all
matrices from the parameter triples independently of the symbolic code and
computes `S` by Padé `expm` rather than the closed formula, and (ii) the Lean
formalization of the algebraic core. Running `verify_wolfram.wl` on a machine
with Mathematica remains open.

---

## 6. Answers to the twelve research questions (spec §20)

1. **Is the proposed G correct?** Yes: `½VᵀGV = H_PT` exactly, and
   `det(λI−JG) = (λ²+ω₁²)(λ²+ω₂²)` (A1, A2).
2. **Exact convention relating S, Q, conjugation of V?** `[Q,V] = −iKV`
   componentwise on the column vector V; `e^{−Q/2}Ve^{Q/2} = SV` with
   `S = e^{iK/2} = cosh(r/2)I + i(K/r)sinh(r/2)`; `e^{Q/2}Ve^{−Q/2} = S⁻¹V` (C2, C3, D1).
3. **Does the explicit S diagonalize G?** Yes: `SᵀGS = G₀` with the spec's
   G₀, all mixed terms vanishing identically; flow form `S⁻¹AS = A₀` (E1–E3).
4. **Is S Hermitian positive in the original coordinates?** **No.** Only
   when `γω₁ω₂ = 1`. After the canonical symplectic rescaling
   `d_xd_y = γω₁ω₂` it is Hermitian positive with spectrum `{e^{±r/2}}` (D4).
5. **Can S be reconstructed without assuming Q?** Yes. Solving
   `{SᵀJS = J, SᵀG′S = G₀′, S = S† > 0}` from scratch yields a unique
   solution `S′₊`, and `log S′₊` reproduces `Q = αpq + βxy` exactly (F).
6. **Which input beyond H_PT is required to select S?** Three choices:
   (i) the target normal form G₀ (which fixes the mode frequencies' pairing
   and the `q`-scale `1/(γω₁²)`); (ii) the positivity/Hermiticity condition,
   which is coordinate-dependent and requires declaring the canonical
   rescaling class `d_xd_y = γω₁ω₂`; (iii) positivity itself (else `±S′₊C`,
   any stabilizer C). Nothing else.
7. **Is the positive polar factor unique?** As a property of *all* admissible
   diagonalizers — **no** (counterexample). The Hermitian-positive admissible
   diagonalizer itself is unique, and the polar factor is constant exactly on
   its `U(1)²` coset (I3).
8. **Exact stabilizer of the positive normal form?** `SO(2,ℂ) × SO(2,ℂ)`
   (complex rotation per mode) for `ω₁ ≠ ω₂`; unitary subgroup `U(1)×U(1)` (F3, I2).
9. **Is the observable-space distance exactly 2r?** Yes, in the canonical
   (rescaled) coordinates, with `⟨U,V⟩ = tr(G⁻¹UG⁻¹V)` unnormalized:
   `d(I, M_obs) = 2r = 2 log((ω₁+ω₂)/(ω₁−ω₂))` (J3), diverging as
   `2 log(ω/ε)` in the equal-frequency limit (K).
10. **Which claims extend to the Hilbert-space metric?** The identities that
    are purely quadratic/metaplectic extend formally: `η = e^{−Q}` intertwines
    (G1/G3), the W-classification (H). Statements about `M_obs = S†S`
    (spectrum, distance) are finite-dimensional observable-space facts and are
    **not** operator statements about η — the spec's §12 warning is confirmed
    and respected: the two live on different spaces.
11. **What fails at ω₁ = ω₂?** `r → ∞` (`α, β` diverge), S diverges like
    `ε^{−1/2}` onto a rank-2 projector, A acquires Jordan blocks, and the
    Jordan no-go theorem (L) shows no positive invariant metric exists at the
    exceptional point; the distance `2 log(ω/ε) → ∞` measures the approach.
    No scalar renormalization cures it (K4).
12. **Which statements are paper-ready theorems?** (i) the derived-convention
    theorem (Q2 above); (ii) diagonalization `SᵀGS = G₀` with the hyperbolic-
    values lemma; (iii) existence/uniqueness of the Hermitian-positive
    admissible diagonalizer + reconstruction of Q from its logarithm (the
    paper's main theorem); (iv) the stabilizer `SO(2,ℂ)²` and the corrected
    polar-factor theorem; (v) the metric classification `η′ = ρ†Wρ`;
    (vi) distance `= 2r` and its exact equal-frequency divergence; (vii) the
    Jordan no-go theorem (Lean-formalized). Items marked "formal level" in §3
    should be stated as such.
