# TODO — symplectic-reconstruction

Working list. Move items to DONE with commit hash when closed.

## Paper 2 referee round (final; major revision of field section) — APPLIED

Decisive claim verified in symbolic/verify_paper2_referee.py (T1–T3, ALL
PASS): ψ₀ = ρ⁻¹φ₀ EXACTLY at the Gaussian level (transported annihilators
of the normal-form vacuum reproduce the paper's PT Gaussian) ⇒ ρ_k is a
POINTED η-unitary (per-mode overlap ≡ 1, physical occupation ≡ 0) ⇒
pointed infinite tensor product exists ⇒ physical PT completion GLOBALLY
unitarily equivalent to normal-form Fock completion. The √3/2 / 1/3 /
disjointness are AUXILIARY identity-embedding quantities (same L², same
standard involution, identity map on canonical variables). Also: worst-
alignment pair needs |φ(b)−a| (fails for a > φ(b)); exact overlap
asymptotic coefficient log(2/√3)·vol(B_d)/(2π)^d.

Applied: abstract + intro reframed (pointed equivalence vs auxiliary
obstruction; obstruction = identity embedding vs Dyson-transported
involution); lem:closedform absolute value; cor:secondproof stratified
hull; thm:nmode ends at finite-dim statement + new Corollary
(*-compatibility hypothesis; PU case safe — real minimizers); cor:scale
normalized-bundle qualification (invariant Sobolev claim withdrawn);
thm:groundstate gains ψ₀ = ρ⁻¹φ₀ + renamed "identity-embedding Gaussian
fidelity" / "auxiliary standard-Fock occupation"; NEW Prop (pointed
unitary equivalence of physical completions); thm:disjoint renamed
"Auxiliary identity-embedding obstruction" with respecified conclusions +
exact overlap asymptotics + (k,−k) convention; rem:meaning rewritten
(contradiction resolved; three-level alignment); discussion "three
levels" + boxed revised central conclusion; verification identifiers
(tag paper2-v1.2 at freeze). CASCADE: paper 4 rem:field qualified
("under the identity embedding...; Dyson-transported completions
pointed-unitarily equivalent"). Paper 3's obstruction was already
auxiliary-scoped in its own referee pass — consistent.

## Paper 1 referee round (major revision, 2026-07-12) — APPLIED

Referee's two concrete errors verified in
symbolic/verify_paper1_referee.py (S1–S3, ALL PASS), then all 16 points
applied:
- spec Q = rℤ pure point (beam splitter, Schwinger SU(2) sectors), NOT
  continuous ℝ/"dilation generator"; spec(e^{−Q}) = {e^{−rn}}∪{0}. New
  Prop (Spectrum of Q); rem:twospaces fixed; algebraic Fock domain
  F_alg declared invariant and used as the common core.
- Prop 3.2 was misstated (D=I: (S₊ᵀGS₊)₁₁ = 21 ≠ 9 — not a diagonalizer
  at all). NOTE: referee's own Version A also fails (D⁻¹S₊D with the
  product condition is a diagonalizer of the ORIGINAL problem but NOT
  Hermitian); correct object is the TRANSPORTED solution
  S(D) = D S_orig D⁻¹ = cI + sB(D), which solves the D-transformed
  problem for every D and is Hermitian iff d_xd_y = γω₁ω₂ (S3a–d).
- Uniqueness stated relative to fixed data + Remark (intrinsic vs
  canonical); proof displays in λ₁, λ₂ only.
- Unitary part: generic ℤ₂², exceptional λ_j=1 U(1), never full U(1)²
  (invariant: λ₁/λ₂ ≠ 1; H∩K not maximal compact in H).
- New §6 subsection: Cartan-coset theorem (Gram convention μ = log
  spec(S†S) = 2μ_std declared; F = 2‖μ‖²; C₂ wall; non-θ-compatible;
  SL(2,ℂ)² hull; escape to infinity).
- Metric classification narrowed to algebraic positive metric forms on
  F_alg; Gaussian stabilizer freedom ⊊ full commutant (Gaussian shadow);
  rational-ratio degeneracy caveat.
- "Complexified metaplectic" terminology fixed; flow→Jordan lemma
  (H = iA) + one-line η^{1/2}Hη^{−1/2} proof; "empty cone" →
  nondegenerate positive-definite cone; equal-frequency PT realizations
  (BM 0804.4190) excluded from scope, not refuted; γ<0 transport remark
  (gravity companion); verification artifact identifiers (tag
  paper1-v1.1 at freeze).

## Paper 3 referee round (major revision, 2026-07-12) — APPLIED; residuals

Referee claims verified in symbolic/verify_paper3_referee.py (R1–R5, ALL
PASS): sign chain (confluent = +∂_{m²}W = −δ′; §5 def was −∂ —
inconsistent; BT = action-sign reversal); Hadamard remainder has
+Σρ²logρ/(64π²) term (NOT smooth); fidelity formula reproduces UV
(Σ−Σ̄)²/12k⁴; IR: N_rel ~ (m₁+m₂)m₁m₂/(6k³) vs massless anchor →
∫k^{d−1}N_rel diverges d≤3 (referee constant exact); Cartan μ=(r,r) is
the GRAM convention (=2μ_std), the only one consistent with F=2‖μ‖².

1. [x] Bridge: three-level statement (split / massive resonance / doubly
   massless); BT identification only at m=0 up to action-sign reversal.
2. [x] Fix §5 W_mm = +∂_{m²}W_m; carry explicit ε through; explicit
   action in Conventions.
3. [x] Hadamard: V₁₂ log σ₊ + H₁₂, smooth V₁₂, diagonal 1/(16π²);
   flat display log + O(ρ²logρ²) + C^∞.
4. [x] Parametrix: full log coefficient; "provides the local microlocal
   input", not "perturbation theory available".
5. [x] Sector theorem → UV hierarchy; □² anchor needs separate IR theorem
   ((1−f) is UV-only; N_rel IR-divergent d≤3).
6. [x] Resonance regularity: separate m>0 resonance / m=0 corner / UV
   local / global.
7. [x] Cartan convention: declare Gram μ = log spec(S†S) = 2μ_std;
   Lemma noframe: symplectic frame.
8. [x] Decoupling thm (v): drop "or ≤ f(‖μ‖)"; only no-coercive-lower-
   bound claimed.
9. [x] "Pure beam splitter" → complexified beam-splitter generator (Levi
   of vacuum-line parabolic).
10. [x] "No map G/K→G/P_Ω" → q_Ω does not factor through q_K; P_Ω =
    Siegel parabolic.
11. [x] Cartan-projection theorem incorporated accurately (non-θ-
    compatible stabilizer, SL(2,ℂ)² hull, C₂ wall, escape within one
    vacuum-ray fiber).
12. [x] Metric-independence: display ω_{ρ′}(A) = w₀^{1/2}w₀^{−1/2}ω_ρ(A)
    cancellation; specify domain/admissible/unbounded W.
13. [x] GNS disjointness: explicit common auxiliary real CCR algebra.
14. [x] "Krein completion is the only one" → canonical nondegenerate
    spectral completion; PT-Jordan realizations not classified.
15. [x] Define "universal" (universal selected complex covariance).
16. [x] Sector expansion wording (matched Σ; mass pair up to interchange).
17. [x] Quadratic-gravity ¶ → helicity-stratified version citing paper 4.
18. [x] Action + algebra before EOM; complex covariance / involution /
    completion triple.
19. [x] WF proof sharpened; "fourth-order microlocal spectrum condition".
20. [x] Artifact identifiers (same pattern as paper 4).

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

- [ ] Freeze + tags after referee rounds conclude: paper1-v1.1, paper2-v1.2, paper3-v1.2, paper4-v1.0 (all referenced in the papers' Verification paragraphs).
- [ ] Before submission (all papers): author metadata, "to appear"
  references, companion arXiv IDs once public.

## DONE

- [x] Paper 4 drafted (c449326b), referee pass 1 six repairs (bbe7a6d0).
- [x] Rename main.tex → symplectic-diagonalization.tex (c5b12d45).
- [x] G12d′ exact divergence law cond(N)/e^r → 1 (bbe7a6d0).
