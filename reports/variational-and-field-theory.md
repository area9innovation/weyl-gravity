# Report: minimum-distortion theorem (A) and field-theory representation (B)

Continuation of `verification.md` (2026-07-12, second session). Machine
verification: `symbolic/verify_variational_fock.py` (20 checks, ALL PASS),
`numeric/distortion_scan.py` (global optimization + invariant cross-checks).
Paper draft: `paper/variational-fock.tex`.

## A. Minimum-distortion theorem — PROVED (conjecture confirmed)

**Theorem.** For every admissible diagonalizer `S = S₊C`,
`C ∈ Stab(J,G₀′) = SO(2,ℂ)²`, with Gram rapidities `cosh τⱼ = ½tr(CⱼCⱼ†)`,
`a = (τ₁+τ₂)/2`, `b = (τ₁−τ₂)/2`:

```
F(S) = ‖log(S†S)‖²_F  ≥  4[a² + arccosh²(cosh r · cosh b)]  ≥  4r² = F(S₊),
```

equality overall iff C is unitary. All minimizers share polar factor S₊ and
hence the same Hilbert-space metric η = e^{−Q}: the Bender–Mannheim metric is
selected by minimum distortion.

Proof structure (elementary, no NPC/Kempf–Ness machinery needed):
1. `P = S†S` is Hermitian-positive AND symplectic ⇒ log-eigenvalues ±x₁, ±x₂.
2. Invariants: `cosh x₁ + cosh x₂ = cosh r (cosh τ₁ + cosh τ₂)` (tr(BW) = 0,
   B off-diagonal in the mode split); `cosh x₁ cosh x₂` from tr P² via the
   2×2 identity `σ₂Mσ₂ = det(M)·M^{-T}`, with alignment parameter χ ∈ [−1,1].
3. Alignment monotonicity: x₁²+x₂² nondecreasing in the product invariant at
   fixed sum (x/sinh x decreasing); worst case χ = −1.
4. **Closed form at χ = −1: x₁,₂ = arccosh(cosh r cosh b) ± a** (hyperbolic
   addition; the key discovery).
5. φ(b) ≥ r via cosh φ − cosh r = cosh r(cosh b − 1) ≥ 0.

Notes:
- The stronger per-eigenvalue claim `xᵢ ≥ r` is FALSE (numerically refuted);
  only the joint bound holds — this is why one invariant (trace) is not
  enough (lopsided spectra beat 2r² under the trace constraint alone).
- The suggested reduction "aⱼ is unitary gauge, set aⱼ = 0" is invalid in
  the canonical coordinates (real angles are non-unitary there — the ℤ₂²
  phenomenon from verification.md §2.3/2.4); the Gram-rapidity variables
  avoid the issue entirely.
- Numerics: global Nelder–Mead from many starts at 4 parameter sets bottoms
  out at exactly 4r² (gaps ≤ 1e−11); equality points found are exactly the
  unitary stabilizer elements (incl. the enhanced-U(1) cases when ωⱼ = 1).

## B. Free fourth-order field — exact modewise data, disjoint representations

Setting: `(□+m₁²)(□+m₂²)φ = 0`, per-k PU pair with ωᵢ(k) = √(k²+mᵢ²).

**Exact rapidity:** `r(k) = log[(ω₁+ω₂)²/(m₁²−m₂²)]` (since
(ω₁−ω₂)(ω₁+ω₂) = m₁²−m₂² identically) = 2log|k| + O(1).

**Phase-space Hilbert scale (corollary):** spec M_obs(k) = e^{±r(k)} with
e^{r(k)} = (ω₁+ω₂)²/Δm² ≍ 1+k²: the observable-space metric is an
H¹⊕H⁻¹-type Sobolev pair — NOT uniformly equivalent to the standard norm.
(This confirms the "Hilbert-scale theorem" as the correct statement at the
phase-space layer.)

**PT ground state (exact, new):** in normalized coordinates
```
ψ₀ ∝ exp{−½[ (ω₁+ω₂)/(ω₁ω₂) x² + 2xy + (ω₁+ω₂) y² ]}
```
— a REAL Gaussian, normalizable for ALL ω₁ > ω₂ > 0 (det of the form =
(ω₁²+ω₁ω₂+ω₂²)/(ω₁ω₂) > 0), eigenvalue (ω₁+ω₂)/2 verified against the PDE.
Smooth across the exceptional point: the EP pathology lives in S₊ and the
excited spectrum, not the ground state.

**Exact fidelity and occupation vs the two-field Fock vacuum:**
```
f  = 4ω₁√(ω₁²+ω₁ω₂+ω₂²) / (4ω₁²+3ω₁ω₂+ω₂²)      → √3/2  ≈ 0.866  (k→∞)
⟨N⟩ = ω₂(ω₁²+ω₂²) / [2ω₁(ω₁²+ω₁ω₂+ω₂²)]          → 1/3            (k→∞)
```
⟨N₁⟩ = ⟨N₂⟩ (equipartition). UNIVERSAL constants (mass-independent), because
the UV limit is ω₁/ω₂ → 1. Fidelity confirmed by 25-digit quadrature.

**Consequences (Theorem):**
1. vacuum overlap ∏ f(k) ≤ e^{−cVΛ^d} — orthogonality catastrophe;
2. relative particle density (1/V)⟨N_tot⟩ ~ (1/3)∫^Λ d^dk/(2π)^d = ∞ in
   EVERY spatial dimension d ≥ 1;
3. von Neumann ITP classes differ ⇒ the PT/physical and naive Fock
   representations are DISJOINT — while each mode is unitarily equivalent.

**Correction to prior expectations (both directions):**
- The naive Shale–Stinespring estimate |β(k)|² ~ sinh²(r/2) ~ k² is wrong —
  as suspected, ρ = e^{−Q/2} is not *-preserving, and the pseudo-Bogoliubov
  coefficients violate αα† − ββ† = 1 (they give cosh r). But the exact
  state-level answer is not a Sobolev-type k-growing mismatch either: it
  SATURATES at O(1) per mode (1/3 quantum). The k^{±2} behavior is real but
  lives at the phase-space/observable layer only.
- Divergence is NOT dimension-marginal: Σ⟨N(k)⟩ ~ Λ^d/3 diverges for all
  d ≥ 1 (not just d ≥ 2 as a β ~ 1/k² estimate would give).

**Physics framing (kept modest in the paper):** PT unitarization of the free
fourth-order field is exact modewise and changes the field-theoretic
representation; the physical completion is the (m₁, m₂) two-field Fock space,
mutually singular with the naive covariant representation. Interacting
constructions must pick a representation first; η = e^{−Q} is not a bounded
operator on the covariant Fock space (Hilbert scale + disjointness).

## Status table

| claim | status |
|---|---|
| A: invariant formulas (tr P, tr P²) | VERIFIED (symbolic + random-matrix numeric) |
| A: closed form x₁,₂ = φ(b) ± a at χ=−1 | PROVED_SYMBOLICALLY |
| A: monotonicity lemma | PROVED_SYMBOLICALLY (calculus mechanized) |
| A: F ≥ 4r², equality iff C unitary | PROVED (chain of above) + numeric global search |
| A: xᵢ ≥ r individually | REFUTED (numeric counterexamples) |
| B: r(k) identity | PROVED_SYMBOLICALLY |
| B: ψ₀ Gaussian + eigenvalue + normalizability | PROVED_SYMBOLICALLY |
| B: fidelity, ⟨N⟩ closed forms, √3/2 and 1/3 limits | PROVED_SYMBOLICALLY + 25-digit quadrature |
| B: disjointness in all d ≥ 1 | PROVED (given standard von Neumann ITP criterion) |
| B: Hilbert-scale corollary (H¹⊕H⁻¹) | PROVED (from r(k) identity) |

## A′. Geometric recognition: the theorem IS a Cartan projection theorem

(Added after session-2 commit; numerics in this section's claims run 2026-07-12.)

Identifications, all verified:
- `F(S) = 2‖μ(S)‖²` where μ = Cartan projection of Sp(4,ℂ) (log-singular-value
  vector in the closed C₂ Weyl chamber); `μ(S₊) = (r, r)` sits ON the chamber
  wall x₁ = x₂.
- The stabilizer H = SO(2,ℂ)² is NOT θ-compatible in the canonical
  coordinates (H∩K = ℤ₂², not maximal compact) — so the theorem is NOT bare
  Mostow/Kempf–Ness for H. The fix: H embeds in the θ-compatible supergroup
  C = SL(2,ℂ)×SL(2,ℂ) (block-diagonal symplectics), whose orbit through the
  basepoint is the totally geodesic H³×H³ ⊂ X = Sp(4,ℂ)/Sp(2) (dim 10, rank 2).
  The Gram data (τⱼ, nⱼ) are exactly polar coordinates on the two H³ factors.
- The Bender–Mannheim direction B is trace-orthogonal to ALL block-diagonal
  Hermitian Hamiltonians (tr(B·m) = 0) ⇒ the S₊-geodesic leaves the orbit
  H³×H³ orthogonally at the basepoint ⇒ by the NPC projection theorem
  (unique nearest point on a convex totally geodesic subset), the basepoint
  is the unique foot ⇒ minimality over C ⊃ H AND the equality set
  {C : CC† = I} in one stroke.
- The closed form is the Pythagorean law of the symmetric space: at worst
  alignment the configuration sweeps a totally geodesic H²×ℝ, and
  x₁,₂ = arccosh(cosh r cosh b) ± a is the HYPERBOLIC Pythagoras
  (hypotenuse law of H²) in b combined with the flat Pythagoras in a.

Generalization (numerically confirmed, proof = the NPC argument above):
for ANY ξ ∈ p with ξ ⊥ p∩c (c = block-diagonal subalgebra), and all C in the
stabilizer coset: ‖μ(e^ξ C)‖ ≥ ‖μ(e^ξ)‖, equality iff C unitary. Random
off-diagonal ξ: 4/4 hold to 1e-8; random ξ with block-diagonal components:
4/4 FAIL — orthogonality is exactly the right hypothesis. So the PU
minimum-distortion theorem is the instance ξ = (r/2)B of:

  **Orthogonal-projection principle for Cartan projections.** G reductive,
  C ⊂ G a θ-compatible reductive subgroup, ξ ∈ p orthogonal to p ∩ Lie(C).
  Then for every c ∈ C: ‖μ(e^ξ c)‖ ≥ ‖μ(e^ξ)‖, equality iff c ∈ K.

The PU-specific content reduces to: (i) Stab(J,G₀′) ⊂ C; (ii) tr(B·m) = 0;
(iii) the exact H²×ℝ value formula. Elevates the variational theorem from a
PU statement to an instance of NPC/Cartan geometry; candidate standalone
math-phys note.

## A″. Referee-pass strengthenings (integrated into paper 2 §2.3)

1. **Iff theorem.** The projection principle is now bidirectional
   (Thm. 2.9 in paper 2): e minimizes c ↦ ‖μ(e^ξc)‖ on C ⟺ ξ ⊥ 𝔠∩𝔭, via
   the exact first-variation identity d/dt F(e^ξe^{tη})|₀ = 8⟨η,ξ⟩
   (verified numerically to 1e-7 rel., mixed ξ; numeric/cartan_checks.py).
   argmin stated as C∩K. The 4/4+4/4 numerical test is thereby replaced by
   a proof and demoted to a regression check.
2. **Canonical hull (new Prop.).** C_θ(H) := smallest closed group ⊇ H ∪ θ(H)
   EQUALS SL(2,ℂ)×SL(2,ℂ) for ω₁,ω₂ ≠ 1: proof via
   [X_j, X_j†] = (ω_j²−ω_j⁻²)diag(1,−1) ≠ 0 and a 6-dim real-span count;
   machine-checked Lie-closure dims: 6 (generic), 2 at ω_j = 1
   (where θ(H_j) = H_j). So the compatible supergroup is not a choice but
   the minimal θ-stable subgroup forced by the physical stabilizer.
3. **Naming/claims discipline.** Renamed to "orthogonal Cartan-norm
   projection principle" — it controls ‖μ‖, not the vector-valued Cartan
   projection; the scalar inequality is flagged as classical
   (Mostow self-adjoint groups, Ann. Math. 62 (1955); Kempf–Ness). The
   novel content: twisted stabilizer + canonical hull + exact H²×ℝ formula
   + n-mode theorem.
4. **Normalization fixed.** μ(S) := chamber-ordered log-spectrum of S†S
   (2× log-singular values), ⟨ξ,η⟩ = tr(ξη); then F = 2‖μ‖², μ(S₊) = (r,r).
5. **Sp(2n,ℂ) theorem (new).** C_n = ∏ⁿSL(2,ℂ) mode-preserving, positive
   part (ℍ³)ⁿ; (𝔠_n∩𝔭)^⊥ = inter-mode Hermitian symplectic couplings; for
   every inter-mode ξ: min = ‖2ξ‖_F, argmin = C_n∩K. Portability to general
   quadratic PT systems is now a theorem, with the inter-mode condition
   both sufficient AND necessary (by the iff).
6. **Compactness phrasing.** H∩K ≅ ℤ₂² refers to the ambient maximal
   compact fixed by the physical inner product; abstractly ℂ^× has maximal
   compact U(1) — the obstruction belongs to the embedding, not the group.

## A‴. Final referee-proof pass (paper 2 v4)

- **Normalization dictionary boxed** (eq. dictionary): F(g) = 2‖μ(g)‖²,
  F(e^ξ) = 4d_X(o,e^ξo)² = ‖2ξ‖²_F; explicit relations min√F = ‖2ξ‖_F,
  min‖μ‖ = ‖2ξ‖_F/√2; first-variation coefficient 8 consistency noted.
  Theorem statements were already in √F form (correct); dictionary added
  as regression check (numeric/cartan_checks.py, passes).
- **Hull stratified**: C_θ(H) = C₁×C₂ with C_j = SL(2,ℂ) (ω_j≠1) /
  SO(2,ℂ) (ω_j=1); new remark on discontinuous symmetry enhancement at
  alignment: hull ∩ K jumps SU(2)→U(1), physical H_j∩K jumps ℤ₂→U(1) —
  property of the embedding, not the abstract group.
- **n-mode normal-space proof made structural**: blockwise trace pairing
  shows 𝔠_n∩𝔭 = {ξ_ij = 0, i≠j} and orthocomplement = {ξ_ii = 0};
  dimension identity n(2n+1) = 3n + 2n(n−1) demoted to a check.
- **Kempf–Ness repositioned**: Mostow/Cartan geometry supplies the theorem
  (totally geodesic convex orbit + normal geodesics); KN described as a
  related variational perspective, not the source.
- **Architecture**: abstract and intro now lead with the hierarchy
  normal-coset principle ⟹ Sp(2n,ℂ) inter-mode theorem (principal general
  result) ⟹ exact ℍ²×ℝ formula (integrable n=2 content); PU = the fully
  integrable model. Still integrated as paper 2.

## B′. Paper-3 proposal audit (2026-07-12, third session)

All checks in `symbolic/verify_paper3_audit.py` (P1–P7, ALL PASS). The
proposed obstruction-and-reconstruction arc survives in shape but its
central quantitative claims are corrected:

**Refuted / corrected:**
1. `tr β†β ≥ 2ω₂²/Δ` with equality at S₊ — REFUTED in both natural frames:
   - canonical frame: Q′ = r(x′y′+p′q′) = r(a₁a₂† + a₁†a₂) is a PURE BEAM
     SPLITTER: [Q′, N] = 0, Q′|0_can⟩ = 0, cost exactly 0 (P1);
   - physical two-field frame: exact cost is paper 2's ⟨N⟩ → 1/3 (P2).
   The identification "tr β†β = Σ sinh²(μ/2)" is frame-invalid; moreover NO
   frame tames the singular values (μ_phys ≈ (r,r) numerically, P7): the
   occupation is a vacuum-ray functional, not a Cartan-norm functional.
   Obstruction rate: Θ(VΛ^d), not Θ(VΛ^{d+2}).
2. Δ-superselection — REFUTED: in common physical PT variables,
   1 − f(k) = (Σ−Σ̄)²/(12k⁴) + O(k⁻⁶), Σ = m₁²+m₂² (P3). The leading label
   is Σ, sums converge for d < 4: ONE universal dressed sector in d ≤ 3.
3. "Dressed sector runs to infinite distance as Δ→0" — REFUTED: the
   selected vacuum is analytic across Δ = 0 (1−f ~ ε⁴, P5) and the
   occupation limits commute (⟨N⟩ ≡ 1/3 at Δ = 0 for every k). The
   resonant singularity is purely dynamical (metric operator, similarity,
   Jordan excited spectrum), not representational.

**New results (stronger than the proposal):**
4. ORBIT CONSTANCY (P6): ℓ_jᵀX_j = −iℓ_jᵀ — the physical annihilator
   covectors are eigenvectors of the stabilizer generators, so
   ℓᵀC(θ)⁻¹ = e^{iθ}ℓᵀ for complex θ: the selected physical state is
   IDENTICAL for every metric in the Gaussian orbit; and since any
   W = f(N₁,N₂) > 0 also fixes the vacuum ray, the PT vacuum is
   metric-independent over the ENTIRE positive-metric family.
   ⇒ Universal Fock no-go for free: every admissible metric gives the same
   modewise cost ⟨N⟩(k) → 1/3, Σ_k = ∞ in every d ≥ 1. No minimization
   needed — computation (b)'s answer is "constant", stronger than
   "minimized at S₊".
5. UNIVERSAL ANCHOR (P4): the selected vacuum of □²φ = 0 (m₁ = m₂ = 0) is
   regular and every massive selected representation is quasi-equivalent
   to it in d ≤ 3 (1−f = Σ²/(12k⁴)). Candidate synthesis with
   Bateman–Turok: their Krein quantization vs the Δ→0 selected vacuum —
   same sector? (open, computable).

**Corrected paper-3 arc:** frame-decoupling theorem (beam splitter /
1/3 / no-frame-tames) → universal no-go via orbit constancy (Θ(VΛ^d)) →
one universal UV-dressed sector anchored at the □² vacuum (d < 4
criticality) → resonant boundary: vacuum-sector analytic, dynamics
Jordan-singular → quadratic-gravity application.

## B″. Bridge theorem and sector hierarchy (paper-3 core, 2026-07-12)

**Bridge theorem (P8, outcome 1 — same quasifree state).** The physical
Wightman function of the selected (Bender–Mannheim) vacuum, computed as
W(t) = S₊e^{tA₀'}ΓS₊ᵀ pulled back to the physical field variable z = iy, is
EXACTLY the spectral Wightman function of the fourth-order field:
```
Δ > 0:   W_zz(t) = [e^{−iω₁t}/(2ω₁) − e^{−iω₂t}/(2ω₂)] / Δ
Δ = 0:   W_zz(t) = −(1 + iωt) e^{−iωt} / (4ω³)
```
— pure positive frequencies with ghost partial-fraction weights; the Δ = 0
limit equals Bateman–Turok's per-mode W̃(p) = θ(p⁰)δ′₁(p²)
(arXiv:2607.00096, eq. 5, mode expansion C3 with null pairing
[a₁,a₂†] = [a₂,a₁†] ≠ 0) up to the overall action-sign convention
(S_BT = −½∫(□φ+λ(∂φ)²)²; the theory-independent commutator parts differ by
the same sign — our commutator is the classical +½-normalized confluent PU
Green-difference i(sin ωt − ωt cos ωt)/(2ω³), verified).

Consequently: **Bender–Mannheim metric selection and the Bateman–Turok
spectral condition pick the SAME quasifree state, for every Δ ≥ 0.** The
two quantizations differ only in the completion: positive η-inner product
(available for Δ > 0) versus Krein space with ghost parity (necessary at
Δ = 0, where the state remains analytic but the metric and the
diagonalizability of the dynamics fail — paper 1's Jordan theorem).
The user's conjectured refinement is thus PROVED at the free level:
"the selected and Krein quantizations share the resonant vacuum
covariance, differing in inner-product completion and treatment of Jordan
excitations."

**Complete UV sector hierarchy (P9).** With Σ = m₁²+m₂², Π = m₁²m₂²:
```
1 − f = (Σ−Σ̄)²/(12k⁴) + O(k⁻⁶)          generic
1 − f|_{Σ=Σ̄} = (29/576)(δ²−δ̄²)²/k⁸ + …   δ = Δ/2;  (δ²−δ̄²) ∝ (Π̄−Π)
```
No k⁻⁶ term. Sector labels: none (d ≤ 3), Σ (4 ≤ d < 8), full mass pair
(Σ,Π) (d ≥ 8). The classification TERMINATES (two invariants determine the
pair) — the provisional d ≥ 8 threshold is now a theorem with coefficient
29/576.

**Remaining before paper-3 draft:** the microlocal/Hadamard audit (§6 of
the proposal): fourth-order short-distance wavefront structure of W_zz and
local composites. The Δ>0 closed form above is the natural starting point.

## B‴. Hadamard audit + paper 3 draft (2026-07-12)

Hadamard/microlocal audit (`symbolic/verify_hadamard.py`, 14 checks, ALL
PASS), outcome favorable exactly as conjectured:
- H1: spectral momentum form + confluent −∂_{m²} identity;
- H2: bisolution (both branches + Jordan mode);
- H3: commutator = fourth-order E_P, normalization E‴(0) = 1;
- H4: 1/ρ² mass-independent (cancels); log ρ coefficient of W₁₂⁺ EXACTLY
  1/(8π²) (1/(16π²) for log ρ²), mass-independent hence nonzero;
  confluent identical; IR scale change = smooth constant;
- H5 (new): split-field structure W_{φ₁φ₁} = +W⁺_{m₁}/Δ,
  W_{φ₂φ₂} = −W⁺_{m₂}/Δ, cross = 0 — the selected vacuum restricted to
  the local partial-fraction fields is (±)KG-Hadamard: Krein signature
  intrinsic, local singularity standard;
- H6: WF(W₁₂⁺) = 𝒞⁺ (recorded argument: forward-cone support ⊆; nonzero
  log coefficient ⇒ equality); difference theorem recorded.

Paper 3 drafted: `paper/fourth-order-vacuum.tex` (9 pp., compiles clean):
"The Universal Vacuum of the Fourth-Order Scalar Field: Metric Orbits,
Fock Sectors, and the Krein Boundary". Arc: three-geometries separation /
parabolic decoupling → orbit constancy + universal Fock obstruction →
universal dressed sector + terminating hierarchy → spectral bridge to
Bateman–Turok → fourth-order Hadamard theorem (+ ±Hadamard split) →
discussion with quadratic gravity as outlook only.

## Paper 3 freeze pass (2026-07-12)

- G/K → G/P_Ω "projection" replaced by the correspondence
  G/K ← G → G/P_Ω (no such map exists: K ≅ Sp(n) ⊄ P_Ω,
  K∩P_Ω ≅ U(n)); theorem renamed "Cartan–parabolic decoupling", restated
  via the two quotient maps q_K, q_Ω with the fibre statement and the PU
  collapse q_Ω(S₊H) = {[Ω_PT]}.
- "Same quasifree state" → "same quasifree two-point functional" (bridge
  theorem restated with matched action sign + IR extension, completions
  named; no positivity asserted w.r.t. a common involution); ghost branch
  reworded to "KG-Hadamard distribution with negative Krein signature".
- Resonant limit split into three regularities (distributional /
  representation / dynamical-metric) with the boxed conclusion:
  resonance is not a vacuum singularity; it is a metric and dynamical
  singularity.
- "No frame tames μ" upgraded from numerics to an analytic lemma:
  σ_max(T⁻¹S₊T) ≥ ρ(S₊) = e^{r/2} ⇒ ‖μ‖_∞ ≥ r in every invertible frame
  (P10 in verify_paper3_audit.py, numeric corroboration).
- Sector table endpoints: logarithmic obstruction at d = 4 and d = 8
  stated explicitly.

## Trilogy repair pass (2026-07-12, post-freeze; tags v1.1)

**Paper 2 — theorem-level repair (real error, caught by reviewer pass):**
the totally-geodesic lemma's hypothesis "closed + †-stable" was
insufficient — counterexample: the discrete group {Aⁿ}, A = diag(2, ½) ∈
Sp(2,ℝ), is closed and self-adjoint with all elements positive but
A^{1/2} ∉ 𝒞, 𝔠_𝔭 = 0, and ξ = −(3/4)log A violates the projection theorem
(c = A beats c = e). Repair: new Definition (compatible subgroup) requiring
the global Cartan decomposition 𝒞 = K_𝒞 exp 𝔠_𝔭, with the counterexample
recorded in-text; lemma restated (ℙ_𝒞 = exp 𝔠_𝔭) and proof rewritten
(polar uniqueness + Ad_{K_𝒞}-invariance for the Gram set). Theorem
hypothesis updated; unused "for every c ∈ 𝒞" removed from part (a).
All applications unaffected: SL(2,ℂ)², ∏SL(2,ℂ), SO(2,ℂ) are connected
†-stable reductive, hence compatible (noted in-text).

**Paper 1 — dimensionless aspect parameters:** λ₁, λ₂ > 0 defined as the
mode-aspect parameters of the canonical coordinates (λ₁ = ω₂, λ₂ = ω₁ in
normalized units for the symmetric split; ratio λ₁/λ₂ = ω₂/ω₁ < 1 is
split-invariant). All exceptional conditions rewritten as alignments
λ_j = 1 — no dimensionful quantity is compared with 1. Same in paper 2's
stratified hull and enhancement remark.

**Paper 3 — vocabulary propagation:** "vacuum state" → "vacuum
functional/ray" wherever the involution/completion is in play; discussion
"not a state in" → "not normal to the naive Fock representation"; both
log-coefficient normalizations (1/(8π²) log ρ = 1/(16π²) log ρ²) displayed
together once in the Hadamard theorem.

Re-frozen: paper1-v1.0, paper2-v1.1, paper3-v1.1.

## Paper 4, first calculation: gravitational reduction (2026-07-12)

`symbolic/gravity_engine.py` (O(ε²) perturbation engine, flat background,
mostly-minus, mode k along z) + `symbolic/verify_gravity_reduction.py`
(G1–G7, ALL PASS). Model: L = √−g[c₁R + αR_μν² + βR²], α = −3β
(scalar-free Einstein–Weyl); healthy-graviton convention c₁ = −1;
M² = c₁/α > 0 for α < 0.

**Results:**
1. TT (helicity ±2): L_TT = (α/4)(Ä+k²A)² − (c₁/4)(Ȧ²−k²A²) — perfect
   square + Einstein; EOM (∂²+k²)(∂²+k²+M²)A = 0: EXACT PU block per
   polarization, γ_k = α/2 < 0 (= BT perfect-square sign; massless branch
   healthy, massive ghost), mass pair (m₁, m₂) = (M, 0). Trilogy applies
   verbatim per polarization.
2. Vector (helicity ±1): gauge-invariant w = k·h_tx + ∂_t h_xz;
   L_V = (α/4)(ẇ²−k²w²) − (c₁/4)w²: SINGLE second-order massive mode,
   ghost-signed. The massless PU partner is pure diffeomorphism gauge —
   REMOVED by the quotient. **PU pairing is broken by gauge reduction
   outside helicity ±2.**
3. Scalar (helicity 0): h_tt auxiliary; at α = −3β single massive ghost
   mode (effective kinetic 3c₁/4 < 0, β-independent); generic (α, β):
   fourth order, scalaron m₀² = −c₁/(2(α+3β)) — decouples iff α = −3β ✓.
4. Mode count: 4 (TT pairs) + 2 + 1 = 7 = 2 + 5 ✓.
5. Polarization-enhanced stabilizer: normal-form stabilizer Lie-algebra
   dim jumps 4 → 16 for one vs two identical PU blocks (numeric
   null-space computation); SO(2)-helicity covariance + Schur ⇒ covariant
   metric S₊ ⊗ I_pol.

**Structural consequence for the paper-4 master theorem:** the conjecture
"PT diagonalization commutes with gravitational symplectic reduction"
FAILS in its naive form — it holds exactly on the helicity-±2 blocks. The
massive helicity ±1, 0 polarizations survive reduction as UNPAIRED
ghost-signed second-order oscillators with no BM mixing partner: their
completion is the bare dichotomy (positive norm + unbounded-below energy,
or Krein norm + positive energy). Imposing the spectral condition forces
Krein signature on helicities ±1, 0 EVEN IN THE SPLIT PHASE. Hence, unlike
the scalar theory, split Einstein–Weyl gravity is necessarily Krein on the
lower helicities for all Δ > 0; the positive pseudo-Hermitian phase is a
property of the TT sector only. Master-theorem item 2 must be restated
accordingly ("TT-positive phase"), and the critical surface remains the
locus where the TT sector too becomes Jordan (flat space: c₁ → 0, pure
Weyl; then conformal gauge enhancement in the lower helicities — to be
analyzed).

## Paper 4, G8/G9: completion classification and covariance (2026-07-12)

`symbolic/verify_gravity_completion.py` — ALL PASS.

**G8 (unpaired-ghost completion theorem):**
- Quarter-turn dictionary verified in the trilogy formalism: D = (qp+pq)/2
  has K_D = diag(1,−1); ρ = e^{−πD/2} implements q → iq, p → −ip;
  ρH₋ρ⁻¹ = H₊ (matrix congruence + symplecticity checked);
  η = e^{−πD} > 0 formally.
- Physical adjoint: q‡ = −q, p‡ = −p — standard reality broken; iq is the
  observable. Three-way incompatibility recorded: for an unpaired ghost,
  {positivity, spectral condition, standard reality} — pick two.
- Classification: {T ∈ Sp(2,ℂ): TA₊T⁻¹ = −A₊} = T₀·SO(2,ℂ),
  T₀ = diag(i,−i): all real-form changes H₋ → H₊ form one quarter-turn
  coset of the mode stabilizer.

**G9 (massive spin-2 covariance) — decides the headline:**
- (a) Schur: invariant symmetric forms on the 5-dim spin-2 irrep of SO(3)
  are exactly ℝ·I (machine-solved commutant): any covariant Hermitian form
  has UNIFORM signature. The hybrid (+,+,−,−,−) explicitly violates
  invariance. ⇒ **the sectorwise TT-positive/lower-Krein completion is NOT
  Lorentz covariant.**
- (b) The total quarter-turn generator D_tot = Σ_pol(qp+pq)/2 is
  SO(3)-invariant ([J_i, K_Dtot] = 0): a covariant uniform-positive
  pseudo-Hermitian completion of the massive multiplet EXISTS, with
  uniformly rotated reality (the massive field is ‡-anti-Hermitian; i×field
  observable).
- (c) Assembly: the quarter-turn on the ghost NORMAL MODE of the TT PU
  pair is itself an admissible positive diagonalizer (T′ᵀJT′ = J and
  T′ᵀG_PU T′ real positive-definite, verified numerically with the gravity
  sign γ = −1) ⇒ it lies in the paper-1 family S₊·Stab ⇒ by paper-3 orbit
  constancy it defines the SAME vacuum functional as the Bender–Mannheim
  metric. TT-BM and lower-helicity quarter-turns assemble consistently.

**Headline classification theorem (paper 4):**
1. Gauge reduction stratifies: PU pairs survive at helicity ±2 only;
   massive ±1, 0 are unpaired ghosts.
2. Unpaired ghosts: positivity + spectral + standard reality — choose two.
3. Covariance forbids mixed signature on the massive multiplet: the hybrid
   completion dies.
4. Exactly two covariant completions remain: uniform-positive
   pseudo-Hermitian with rotated massive reality (Mannheim-extended via
   quarter-turns), and uniform Krein with standard reality (Bateman–Turok).
5. Both are completions of the same complex spectral vacuum functional
   (orbit constancy + paper 3): they are different real forms of one
   reduced complex spectral theory.

Queued: G10 (helicity-resolved spectral kernel), G11 (linearized-Weyl
gauge-invariant correlator), G12 (conformal limit c₁ → 0, sectorwise).

## Paper 4, G10–G12: spectral kernel, Weyl correlator, conformal limit (2026-07-12)

`symbolic/verify_gravity_spectral.py` — ALL PASS.

**G10 (full reduced spectral kernel):**
- TT: W_A = (1/(γM²))[e^{−iω₁t}/2ω₁ − e^{−iω₂t}/2ω₂], γ = α/2: bisolution
  + commutator with E‴(0) = +1/γ (verified from Ostrogradsky brackets).
- Vector/scalar single-shell kernels with residues fixed by the reduced
  symplectic forms (μ_V = α/2, μ_S = 3c₁/2); commutator E′(0) = −1/μ.
- **Covariant reassembly**: with Π^{(2,M)} built from P = η − pp/M²:
  Π_{xy,xy} = ½;  (cΠc̄)_w = (E²−k²)²/2M² = M²/2  (the complex-basis
  gauge invariant is w̃ = −ik h_tx − iE h_xz);  O_S-contraction = 1/6.
  These match the reduced residue ratios 1 : M² : 1/3 EXACTLY with a single
  overall normalization 𝒩 = 4/c₁ — uniform ghost sign: the five massive
  helicities assemble into one SO(3)-invariant projector at correlator
  level (the correlator-side counterpart of G9a). Massless shell couples
  only to TT.
- Real-form independence: the quarter-turn completion's physical Wightman
  for an unpaired ghost equals the Krein spectral value (i² flip): the
  complex W⁺ is completion-independent. With G9c this closes the bridge:
  the full gravitational vacuum functionals of the two covariant real
  forms coincide.

**G11 (linearized Weyl correlator):**
- Linearized Riemann annihilates pure gauge (momentum space, symbolic p);
  linearized Weyl traceless (coefficient validation).
- **Projector-singularity cancellation**: the full Weyl–Weyl contraction of
  Π^{(2,M)} equals that of Π₀ (all P → η): every 1/M², 1/M⁴ term of the
  massive projector is annihilated by the Weyl map — the curvature kernel
  is M-regular and covariant. Recorded: WF directions Hadamard 𝒞⁺;
  W_h ~ log ρ while W_CC ~ ∂⁴log ρ.

**G12 (conformal limit, α fixed, c₁ → 0):**
- TT: divided difference → −(1+ikt)e^{−ikt}/(4k³) = −∂_{m²} shell: □²
  Jordan per polarization (4 TT configuration modes).
- Vector: smooth massless limit e^{−ikt}/(αk) with FIXED normalization
  μ_V = α/2: ordinary massless ghost, not Jordan.
- Scalar: kinetic ∝ c₁ → 0 (null), and δh = 2ση is machine-verified to be
  a gauge symmetry of the α = −3β action exactly at c₁ = 0 (and NOT at
  c₁ ≠ 0): the scalar sector is Weyl-gauge on the conformal locus.
  Count: 4 + 2 + 0 = 6 = flat conformal gravity ✓.
- Completion limit: cond(N) of the split normal-mode decomposition grows
  7.6 → 47.5 → 403 → 4447 as M = 1 → 0.03: the uniform positive
  quarter-turn completion (which requires the split) terminates at the
  conformal locus, explicitly, not just by citing the Jordan no-go; the
  spectral functional and the Krein form continue distributionally.

**The paper-4 master theorem is now fully supported** (scope: translation-
invariant quasifree mode-local completions compatible with the reduced
symplectic form, the spectral condition, and massive-spin-2 covariance):
one reduced complex spectral quasifree functional; two covariant real
forms in the split phase (positive pseudo-Hermitian with rotated massive
reality / Krein with standard gravitational reality); no covariant hybrid;
identical complex gauge-invariant correlators; regular distributional
conformal limit at which the positive form terminates and the Krein form
continues (TT Jordan + massless vectors + Weyl-null scalar).

## Paper 4 drafted (2026-07-12)

`paper/fourth-order-gravity.tex` — **Gauge Reduction and the Completion
Problem in Fourth-Order Gravity: PU Pairing, Covariant Real Forms, and the
Conformal Jordan Boundary** (8 pp., compiles clean).

Logical order as directed: reduction (§2, G1–G7) → completion trilemma
(§3, G8) → covariance classification (§4, G9) → spectral bridge (§5, G10)
→ gauge-invariant correlator (§6, G11) → conformal boundary (§7, G12) →
master theorem (§8) → discussion. Abstract leads with: one complex
spectral theory, exactly two covariant real-form completions in the split
phase, no covariant helicity hybrid, only the Krein completion continuing
through the conformal Jordan boundary.

Framing discipline maintained: classification + covariance obstruction,
NOT "gravity is solved"; Maldacena boundary truncation placed as a third,
distinct construction (removes a branch of the solution algebra vs
changes the inner-product structure); interaction question (rotated
reality vs cubic Weyl vertices; gravitational ghost parity
[P_ghost, S_int] = 0) stated as sharp outlook, explicitly not computed;
Λ ≠ 0 (critical gravity, partial masslessness) flagged as outside scope.
Gauge/BRST ghosts vs higher-derivative ghost branch distinguished in the
introduction. Every theorem carries its G-check provenance via the
Verification paragraph.

## Paper 4 referee pass 1 (2026-07-12) — six repairs applied

1. **Gauge-invariant quotient**: Definition (Invariant observable algebra)
   𝔄_inv added in §2; all uniqueness/continuation claims restated on
   𝔄_inv; potential kernels W⁺_h explicitly "modulo pure-gauge
   bi-distributions, used as computational representatives". Abstract and
   master theorem tightened accordingly.
2. **Schur/Krein wording contradiction resolved**: the Krein form's
   indefiniteness lives BETWEEN irreps, never inside the massive
   multiplet: ℋ_1p = ℋ_{0,+2} ⊕ ℋ_{M,−5}, signature (+,+;−,−,−,−,−);
   "invariant indefinite form on each irrep" removed.
3. **Schematic kernel replaced by exact formulation**: reassembly theorem
   now states the equivalence class [W̃⁺_h] ∈ 𝒟′(Sym²⊗Sym²)/{pure-gauge}
   with the exact representative (𝒩/M²)θ(p⁰)[Π^{(2,M)}δ(p²−M²) −
   Π^{(2,0)}(p;n)δ(p²)], frame-independence of the class noted, plus the
   frame-free curvature-kernel formulation.
4. **Scalar conformal limit regular only after quotienting**: new Remark —
   raw W⁺_S ~ 1/c₁ diverges; the convergent object is the presymplectic
   family (Γ_{c₁},Ω_{c₁}) → (Γ₀/ker Ω₀, Ω̄₀) with the induced functional
   on 𝔄_inv; observable algebra changes rank at the boundary (treated as
   a feature).
5. **Verification claim restricted**: "all statements machine-verified" →
   finite-dimensional/variational/symplectic/tensor-algebraic/modewise-
   distributional identities machine-verified; representation-theoretic
   and microlocal conclusions from analytic arguments. WF equality (not
   just ⊆) proved: Weyl principal symbol nonvanishing on physical spin-2
   polarizations over the characteristic set.
6. **Exact asymptotic replaces numerical conditioning**: termination
   theorem now rests on r(k,M) = log((√(k²+M²)+k)²/M²) ~ log(4k²/M²) → ∞
   + Jordan no-positive-form obstruction; cond(N) = e^r(1+o(1)) ~ 4k²/M²;
   numerics demoted to regression check. New script check G12d′:
   cond(N)/e^r → 1 (ratios 1.31, 1.023, 1.0025, 1.0002) — ALL PASS.

Also: field-level hierarchy remark (modewise real-form change → positive
one-particle Hermitian structure → quasifree GNS representation;
η = e^{−πD_tot} is formal shorthand on a common algebraic domain, NOT a
global operator on naïve Fock space — consistent with paper-2/3
disjointness); master theorem replaced by the corrected referee text
verbatim; discussion terminology: "Bateman–Turok-type Krein real form /
gravitational extension", since BT quantize the scalar perfect-square
theory, not this field. Now 10 pp., compiles clean.
