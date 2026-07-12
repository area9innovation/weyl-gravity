# TODO — symplectic-reconstruction

Working list. Move items to DONE with commit hash when closed.

## Paper 4 referee round 2 — APPLIED (see DONE); residual items

- [ ] Repo/companion identifiability (referee pt 11, remainder): repo is
  PRIVATE. Decide with Asger: make companions + verification public, or
  reproduce needed lemmas in a paper-4 appendix. Paper currently cites
  the directory + scripts + versions + tag paper4-v1.0 (tag not yet
  created — create at freeze).
- [ ] Referee suggested full section reordering (reduced complex theory →
  real forms → Cartan → intrinsic kernel → degeneration). Applied as
  insertion (new Cartan §5 + definitions at §3 head) without global
  reorder; revisit only if next round asks again.

## Paper 4 referee round 2 (major revision, 2026-07-12)

1. [x] **FATAL: kernel normalization** — eq. (exactkernel) has one factor
   1/M² too many. Full covariant coefficient is C = 4/c₁ (equivalently
   𝒩/M² with 𝒩 = 4/α, NOT 4/c₁). Note 1/(γM²) = 2/(αM²) = 2/c₁ exactly
   since αM² = c₁. Propagate: reassembly theorem, Weyl-correlator
   normalization, conformal-limit section, abstract "𝒩 = 4/c₁" wording,
   verification script claim text.
2. [x] **Missing 1/γ in TT Jordan kernel** — conformal limit is
   −(1+ikt)e^{−ikt}/(4γk³), not /(4k³) (unless explicitly announced as
   unit-normalized divided difference).
3. [x] **Formal classification category** — define (V_ℂ, σ, U); real form
   = antilinear involution κ compatible with σ, dynamics, Poincaré;
   completion = Hilbert/Krein topology on fixed points + GNS; equivalence
   modulo U-equivariant complex-symplectic automorphisms. Fix "same
   state" language: same complex bilinear covariance, different
   involutions/positivity.
4. [x] **Integrate Cartan-projection theorem** (paper 2): F = 2|μ(S)|²,
   μ(S₊) = (r,r) on the C₂ Weyl wall; stabilizer H = SO(2,ℂ)² NOT
   θ-compatible (H∩K = ℤ₂×ℤ₂) — resolution via compatible supergroup
   SL(2,ℂ)²; do NOT present as plain Kempf–Ness. Three jobs: canonical
   representative selection; equal-frequency divergence = |μ|→∞ escape
   to infinity toward Jordan stratum; unify companion imports in
   intro/discussion.
5. [x] **Covariance proof gap** — add induced-representation (Wigner)
   lemma: shells don't mix under translations; covariant Hermitian
   structures ↔ little-group invariant fiber forms; classify equivariant
   antilinear involutions on the real-type spin-2 irrep; D_tot assembles
   into equivariant bundle map (rest-frame SO(3) invariance alone ≠
   boost covariance).
6. [x] **Conformal boundary comparison maps** — 𝔄_{c₁≠0} and 𝔄₀ are
   different algebras; convergence needs comparison maps. Use Option B
   (curvature/Weyl-generated algebra as the common regular subalgebra)
   with Option A (ι_{c₁}: 𝒪_reg → 𝔄_{c₁}) language. Master theorem must
   claim convergence only on the specified regular subalgebra.
7. [x] **Positive class at boundary: nuance** — distinguish (i) no
   continuation as nondegenerate positive-definite invariant metric,
   (ii) singular/semidefinite boundary forms, (iii) distinct
   non-diagonalizable PT-Jordan realization (Bender–Mannheim
   arXiv:0804.4190 — ADD citation), (iv) Krein continuation. Replace
   "only the Krein class crosses it".
8. [x] **Microlocal argument too compressed** — explain why
   massive−massless divided difference lowers singular order but removes
   no WF directions; nonzero log-coefficient via explicit Hadamard
   expansion (companion 3, 1/(8π²)); mention polarization-set (Dencker)
   framing.
9. [x] **Zero-momentum qualification** — "for every fixed k > 0"; zero
   mode excluded by test-function framework on ℝ³ (state it); compact
   sections caveat. Specify cond(N) norm = Euclidean operator 2-norm in
   canonical basis.
10. [x] **Abstract scope** — open with "We classify translation-invariant,
    quasifree, mode-local real-form completions of free scalar-free
    Einstein–Weyl gravity linearized about Minkowski space...".
11. [x] **Companion citations + artifact identifiability** — add repo
    URL, tags (paper1-v1.0, paper2-v1.1, paper3-v1.1), commit hash,
    exact commands, software versions, appendix table mapping G1–G12 to
    theorems. Blocked partially: repo is private → either make
    companions public or reproduce needed lemmas in appendix (decide
    with Asger).
12. [x] **Smaller fixes** — μ_S vs 3c₁/4: say "coefficient of ṗ²";
    "positive-frequency" → "spectral-support-positive" (support in
    p⁰>0, not distributional positivity); interaction outlook "decide" →
    "provide the first necessary tests"; keep "Bateman–Turok-type
    gravitational extension" phrasing.

Script side:
- [x] Update verify_gravity_spectral.py claim text for the corrected
  coefficient (C = 4/c₁ full, no extra 1/M²) + explicit three-sector
  coefficient check; TT Jordan limit with 1/γ.
- [x] Add massless-shell Weyl-symbol nonvanishing check (linearized Weyl
  tensor of a TT massless wave ≠ 0) — supports the WF-equality proof.

## Receipts / verification backlog (from 2026-07-12 audit)

1. [ ] Lean: Schur no-hybrid (commutant of so(3) spin-2 5-dim irrep =
   ℝ·I) — paper 4's central obstruction, finite-dim matrix algebra.
2. [ ] Lean: orbit-constancy eigenvector lemma (ℓᵀX = −iℓᵀ ⇒
   metric-independence) — load-bearing for papers 3 AND 4.
3. [ ] Lean: trilemma coset {T: TA₊T⁻¹ = −A₊} = T₀·SO(2,ℂ) +
   quarter-turn congruence (4×4, reuses NormalForm.lean patterns).
4. [ ] mpmath regression rail for papers 3–4 kernels (bridge Wightman,
   sector kernels, conformal limits) — second independent rail; the
   Wolfram rail has never run (no Mathematica).
5. [ ] Lean (cheap): paper-2 discrete counterexample {Aⁿ}; fidelity
   √3/2 and occupation 1/3 identities.
6. [ ] Lean (expensive, optional): paper-2 minimum-distortion scalar
   inequality with arccosh closed form.

## Housekeeping

- [ ] paper4 freeze + tag paper4-v1.0 after referee rounds conclude.
- [ ] Before submission (all papers): author metadata, "to appear"
  references, companion arXiv IDs once public.

## DONE

- [x] Paper 4 drafted (c449326b), referee pass 1 six repairs (bbe7a6d0).
- [x] Rename main.tex → symplectic-diagonalization.tex (c5b12d45).
- [x] G12d′ exact divergence law cond(N)/e^r → 1 (bbe7a6d0).
