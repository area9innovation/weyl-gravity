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

## Paper 4 referee pass 2 (2026-07-12) — major revision applied

**Referee caught a genuine normalization error** (their pt 1): the exact
kernel display had (𝒩/M²) with 𝒩 = 4/c₁ — one factor 1/M² too many,
which would have destroyed the conformal limit (~M⁻² δ′(p²)). Since
αM² = c₁, the TT prefactor 1/(γM²) = 2/c₁ is M-independent; the FULL
covariant coefficient is C = 4/c₁ (equivalently (4/α)/M²). New check
G10c6 pins the absolute coefficient sector-by-sector. Also their pt 2:
the physical TT Jordan kernel is −(1+ikt)e^{−ikt}/(4γk³) — the 1/γ was
missing; new check G12a′ verifies both the physical and covariant routes.
New check G11e: Weyl principal symbol nonzero on massless TT while
killing null pure gauge. All three scripts ALL PASS.

All twelve referee points applied:
1. Kernel coefficient corrected everywhere (abstract, intro, reassembly
   theorem with absolute-normalization display, conformal section).
2. 1/γ in TT Jordan kernel (theorem now displays W⁺_TT,0 with 1/(4γk³)).
3. Formal category: Definition (complex dynamical algebra (V_ℂ,σ,U);
   real form κ; completion; equivalence via U-equivariant symplectic
   automorphisms) + Remark (states vs covariances: same complex bilinear
   covariance, NOT same positive state on one *-algebra).
4. Cartan-projection theorem integrated: new §5 (F = 2‖μ‖², μ(S₊)=(r,r)
   on C₂ wall; NOT plain Kempf–Ness — H∩K = ℤ₂×ℤ₂, proof via
   θ-compatible hull SL(2,ℂ)²); intro item; discussion paragraph
   ("geometric picture"); termination = escape to infinity ‖μ(S₊)‖→∞.
5. Induced-representation lemma (Wigner): shell superselection,
   fiber-form correspondence, two equivariant involution classes on the
   real-type spin-2 irrep, D_tot as equivariant bundle map; wired into
   no-hybrid + two-real-forms theorems.
6. Comparison maps at the boundary: Definition (curvature-generated
   𝒪_reg, ι_{c₁}, ω_{c₁}∘ι_{c₁} → ω₀∘ι₀); master theorem claims
   convergence ONLY on the regular subalgebra.
7. Boundary nuance: "no continuation as nondegenerate positive-definite
   invariant metric"; PT-Jordan realization (BM arXiv:0804.4190, new ref;
   also fixed BM2008PRD → PRL 100 110402, the PRD 78 025022 WAS
   0804.4190) is a distinct singular completion, not a continuation.
8. Microlocal proof expanded: divided difference lowers singular order
   (log ρ, coefficient 1/(8π²) ≠ 0 per companion 3) but removes no
   directions; Dencker polarization-set framing; σ_C injective on
   physical polarizations (G11c/G11e).
9. "For every fixed k > 0"; zero-mode remark (ℝ³ test functions /
   compact-section caveat); cond norm = Euclidean operator 2-norm.
10. Abstract rescoped: "We classify translation-invariant, quasifree,
    mode-local real-form completions ... subject to ...".
11. Verification paragraph: directory, script names, exact runner,
    SymPy 1.14.0 / NumPy 2.4.4 / Python 3.14, tag paper4-v1.0 (to be
    created at freeze); new Appendix A mapping G1–G12d′ to theorems.
    RESIDUAL: repo privacy — decide public release vs lemma appendix.
12. "spectral-support-positive" for the kernel; scalar "coefficient of
    ṗ² = μ_S/2 = 3c₁/4"; interaction outlook "provide the first
    necessary tests" + explicit non-claims.

Now 14 pp., compiles clean. TODO.md tracks residual items.

## Paper 3 referee pass (2026-07-12) — major revision applied

Referee claims first machine-verified in symbolic/verify_paper3_referee.py
(R1–R5, ALL PASS):
- R1 sign chain: confluent limit of the divided difference is
  +∂_{m²}W_m = −(1+iωt)e^{−iωt}/(4ω³) = −δ′(p²−m²); the paper's §6
  definition W_mm = −∂_{m²}W_m was internally inconsistent with its own
  eq. (Wspectral)/(Wmode). BT's +δ′₁(p²) is the action-sign REVERSAL of
  our confluent covariance at m=0.
- R2 Hadamard remainder: divided difference = (1/8π²)logρ +
  (Σ/64π²)ρ²logρ + ... — the remainder is NOT smooth ("log + smooth" was
  false for nonzero masses). Exact coefficient +Σ/(64π²) pinned.
- R3 the 2×2 Gaussian overlap formula reproduces the verified UV
  expansion (Σ−Σ̄)²/12k⁴ (self-check).
- R4 IR obstruction of the □² anchor: N_rel(k) ~ (m₁+m₂)m₁m₂/(6k³) as
  k→0 (referee's constant EXACT), so ∫k^{d−1}N_rel diverges precisely
  for d≤3; 1−f ≤ 1 always IR-converges, exposing the (1−f) criterion as
  UV-only, not global Shale.
- R5 Cartan convention: singular values of S₊ are e^{±r/2} → μ_std =
  (r/2,r/2); the papers' μ(S₊)=(r,r) is the Gram convention
  μ = log spec(S†S) = 2μ_std — the only one consistent with F = 2‖μ‖².

All 20 points applied to fourth-order-vacuum.tex (now 13 pp., clean):
bridge restructured as three statements (split / massive BT-type
resonance / doubly-massless with action-sign reversal, explicit ε);
explicit action S = (ε/2)∫φ(□+m₁²)(□+m₂²)φ with ε=+1 and the complex
covariance / involution / completion hierarchy in Conventions; W_mm
sign fixed; Hadamard theorem in V₁₂logσ₊+H₁₂ form with universal
DIAGONAL value 1/(16π²) and machine-verified Σρ²logρ/(64π²) remainder;
parametrix = "local microlocal input", HW/BF adaptation flagged as
genuine further step; sector theorem → UV hierarchy with common IR
regular class + new Remark (□² anchor is an open IR question, exact
N_rel asymptotic displayed); four resonance boundaries separated (m>0
resonance vs m=0 corner vs UV local vs global); decoupling (v) reduced
to no-coercive-lower-bound (upper envelopes exist); "pure beam
splitter" → complexified beam-splitter generator (e^{−Q′/2} nonunitary);
q_Ω does not factor through q_K (Siegel parabolic named); Gram–Cartan
convention declared (synchronized with F = 2‖μ‖²), noframe lemma on
symplectic frames with the 2log s ≥ log ρ(M²) chain; Cartan-projection
theorem incorporated (non-θ-compatible stabilizer, SL(2,ℂ)² hull, C₂
wall) + new wall-escape remark (escape along the wall within one
vacuum-ray fibre); metric-independence proof displays the
w₀^{1/2}w₀^{−1/2} cancellation with admissibility/domain spec;
disjointness on the explicit common auxiliary CCR algebra (standard
involution; PT rotation is the genuinely complex step); "Krein is the
only one" → canonical nondegenerate spectral completion, PT-Jordan
realizations (BM 0804.4190, title+arXiv added) not classified;
"universal" defined (universal selected complex covariance);
matched-Σ wording + pair-up-to-interchange; quadratic-gravity ¶ replaced
with the helicity-stratified statement citing companion4 (added to bib);
WF proof sharpened (boundary-value form, V₁₂(x,x)≠0, no directions
removed; "fourth-order microlocal spectrum condition" naming);
verification artifact identifiers (scripts, versions, tag paper3-v1.2
to be created at freeze).

## Paper 1 referee pass (2026-07-12) — major revision applied

Referee's two concrete errors machine-verified first
(symbolic/verify_paper1_referee.py, S1–S3, ALL PASS):
- S1: spec Q = rℤ, pure point, infinite multiplicities (Q′ =
  r(a₁a₂†+a₁†a₂) commutes with N_tot; every fixed-N sector is Schwinger
  SU(2) 2J_x with spectrum exactly {−N,...,N step 2}, checked N ≤ 25);
  spec(e^{−Q}) = {e^{−rn}}∪{0}. The paper's "purely continuous spectrum
  (0,∞), Q unitarily equivalent to a dilation generator" was FALSE.
- S2: Prop 3.2 counterexample confirmed: γ=1, ω₁=3, ω₂=2, D=I gives
  (S₊ᵀGS₊)₁₁ = 21 ≠ 9 — S₊ is not a diagonalizer of the original
  problem at all.
- S3: the referee's own Version-A repair is ALSO wrong (D⁻¹S₊D with
  d_xd_y = γω₁ω₂ satisfies the original congruence but is NOT
  Hermitian — Hermiticity of that matrix needs d_xd_y = 1). The correct
  proposition, machine-verified: S_orig = D₀⁻¹S₊D₀ depends only on the
  product and solves the original problem (S3a/b); the TRANSPORTED
  canonical solution S(D) = D S_orig D⁻¹ = cI + sB(D) solves the
  D-transformed problem for EVERY D (S3c) and is Hermitian iff
  d_xd_y = γω₁ω₂ (S3d).

All 16 points applied to symplectic-diagonalization.tex (now 17 pp.,
clean): new Prop (Spectrum of Q) + corrected rem:twospaces + invariant
algebraic Fock domain F_alg as common core; corrected Prop
(Hermiticity requires the normalization) with the transported
formulation and the three-conditions caveat (solution / Hermitian /
normalized are distinct); uniqueness relative to fixed data + Remark
(intrinsic uniqueness vs coordinate-free equivalence class); eq:herm
and polar proof in λ₁, λ₂; unitary-part remark (generic ℤ₂²,
exceptional U(1), never U(1)²; H∩K not maximal compact — the invariant
statement); new §6.2 Cartan-coset theorem with declared Gram convention
(μ(S₊) = (r,r) = 2μ_std, singular values e^{±r/2}), F = 2‖μ‖², C₂
wall, non-Kempf–Ness caveat, SL(2,ℂ)² hull, wall-escape reading of the
equal-frequency limit; metric theorem narrowed to algebraic positive
metric forms on F_alg with rational/irrational commutant care;
Gaussian-shadow paragraph (stabilizer ⊊ commutant); complexified-
metaplectic terminology; flow→Jordan lemma (H = iA on the +iω
generalized eigenspace) + one-line η^{1/2}Hη^{−1/2} diagonalizability
proof; "empty cone" qualified to nondegenerate positive-definite;
Jordan-PT-realization scope remark (BM 0804.4190 arXiv id added); γ<0
transport paragraph citing the gravity companion (new bibitem);
verification artifact identifiers incl. Lean declaration names and tag
paper1-v1.1 (to create at freeze).

## Paper 2 referee pass (final round, 2026-07-12) — field section corrected

**The referee's decisive objection is CORRECT and machine-verified**
(symbolic/verify_paper2_referee.py, T1–T3 ALL PASS): the PT ground state
is exactly the Dyson pullback, ψ₀ = ρ⁻¹φ₀ (T1: transporting the
normal-form vacuum's annihilation covectors by ρ⁻¹Vρ = S₊⁻¹V reproduces
the paper's PT Gaussian [[(ω₁+ω₂)/(ω₁ω₂),1],[1,ω₁+ω₂]] exactly). Hence
U_k = ρ_k is a POINTED η-unitary (Uψ = φ, per-mode pointed overlap ≡ 1,
physical occupation ⟨ρ⁻¹Nρ⟩_η = ⟨N⟩_φ = 0), the pointed infinite tensor
product exists with no von Neumann obstruction, and the physical PT
completion is GLOBALLY unitarily equivalent to the positive normal-form
Fock completion. The paper's "physical (PT) and naive Fock
representations are disjoint" was FALSE as a physical statement: the
√3/2 fidelity, 1/3 occupation, and product disjointness are quantities
of the AUXILIARY identity embedding (both Gaussians as vectors of one
standard L², standard involution, canonical variables identified by the
identity map). The obstruction is identity-embedding vs
Dyson-transported involution — an involution-level mismatch, exactly the
three-level structure (covariance ≠ involution ≠ completion) of the
later companions. Also verified: T2 worst-alignment log-eigenvalue pair
is {φ(b)+a, |φ(b)−a|} (displayed φ−a goes negative for a > φ(b); F
unaffected); T3 exact overlap coefficient log(2/√3)·vol(B_d)/(2π)^d
replaces the loose e^{−cVΛ^d}.

All revisions applied (now 14 pp., clean): abstract/intro reframed; new
Proposition (pointed unitary equivalence of the physical completions);
theorem renamed "Auxiliary identity-embedding obstruction" with
conclusions respecified (auxiliary algebra, identity map, not the
physical completion) + exact asymptotics + (k,−k) real-field convention;
"identity-embedding Gaussian fidelity" / "auxiliary standard-Fock
occupation" terminology; ψ₀ = ρ⁻¹φ₀ added to the ground-state theorem;
rem:meaning rewritten (the old "naturally identified with Fock space"
vs "globally disjoint" contradiction resolved); |φ−a| in lem:closedform;
cor:secondproof on the stratified hull; thm:nmode split into finite-dim
theorem + *-compatibility corollary (matrix unitarity ≠ quantum
unitarity; PU minimizers real, hence safe); cor:scale restricted to the
normalized mode bundle (invariant Sobolev claim withdrawn pending fixed
trivialization); discussion "three levels" + boxed revised central
conclusion; verification identifiers (tag paper2-v1.2 at freeze).
Cascade: paper-4 field-level remark qualified accordingly; paper 3
already auxiliary-scoped from its own pass.

## Paper 0 drafted (2026-07-12): expository introduction

`paper/ghosts-geometry-reality.tex` — **Ghosts, Geometry, and Reality in
Fourth-Order Quantum Theories: A guided introduction to the
Pais–Uhlenbeck oscillator, Krein quantization, and higher-derivative
gravity** (17 pp., compiles clean, zero overfull). Audience: knows some
math/physics, not expert. Based on Asger's draft, rendered to the series
house style with: full bibliography (Ostrogradsky/Woodard, PU, BM,
BT, SGH/Mostafazadeh, Stelle, Radzikowski/BF/HW, Maldacena, Lü–Pope,
DJW, Kubo–Kuntz, + Papers I–IV as companions); TikZ Figure 1 =
one-page visual summary of complex covariance → two real forms → two
completions (with "same complex correlators" bridge and Jordan-boundary
annotations); TikZ Figure 2 = four-paper dependency diagram; TOC.
All formulas cross-checked against the POST-referee-round papers: spec
Q = rℤ, Gram–Cartan μ(S₊) = (r,r) with F = 2‖μ‖², H∩K = ℤ₂², hull
generically SL(2,ℂ)², ε action sign in the covariance and its confluent
−εθδ′ limit, BT = action-sign reversal, V log σ + H with σ log σ
remainder and V(x,x) = ε/16π², pointed Dyson transport (ψ = ρ⁻¹φ,
per-mode overlap 1) vs auxiliary identity embedding (√3/2, 1/3),
helicity stratification 2Γ_PU ⊕ 2Γ₋ ⊕ Γ₋, Schur no-hybrid, conformal
count 4+2+0 = 6, PU metric-constancy safe (real minimizers). README
gains the paper-0 row.

## Interaction-deformation program, step 1 (2026-07-13)

New direction from the other team: deform the two real forms under
interaction; obstruction classes 𝔬₊(V) = Π_ker ad_{h₀}(v†−v) (positive
form) and 𝔬_K(V) = Π_ker ad_{H₀}[κ₀,V] (Krein form). They supplied the
first-order theory for the cubic PU vertex V = −iy³.

**Their first-order claims: ALL VERIFIED** (verify_interaction_
deformation.py, ID1–ID5, exact Weyl/Moyal calculus): transported vertex
v = −i(cy+isp)³ with v†−v = 2ic(c²y³−3s²yp²); their explicit Weyl-ordered
R₁ (eq 5.1) solves [h₀,R₁] = v†−v exactly for all ω₁>ω₂>0 (denominator
4ω₁²−ω₂² safe); equivalent Hermitian interaction s(3c²y²p−s²p³); scalings
c~s~√ω/(2√ε), R₁ = O(ε^{−3/2}) vs Q₀ = O(log ε⁻¹).

**Second order COMPUTED (new, ID6–ID10):**
1. Generic (incommensurate) frequencies: 𝔬₊^(2) = Π_ker(½[R₁,v+v†]) = 0.
   R₂ exists, Hermitian; END-TO-END check: h_λ = e^{−X/2}⋆(h₀+λv)⋆e^{X/2}
   with X = λR₁+λ²R₂ is Hermitian through O(λ²) (validates their eq 8.1,
   including the ⅛[[h₀,R₁],R₁] term and the Λ³ Moyal constant).
2. R₂ carries resonance denominators (ω₁−ω₂) AND (ω₁−3ω₂): an INTERIOR
   3:1 resonance locus, invisible at first order.
3. **AT ω₁ = 3ω₂ the positive form is OBSTRUCTED at second order**:
   𝔬₊^(2) = 27√3/(320ω₂⁴)·(a₁a₂†³ − a₁†a₂³) exactly — the on-shell
   1-quantum ↔ 3-quanta conversion vertex. UNREMOVABLE by any first-order
   freedom (checked: Π_ker([G, v+v†]) = Π_ker([v−v†, G]) = 0 for the
   on-shell quartet K± and all quadratic invariants N₁,N₂,N²-type).
   Physics: perturbative PT-breaking (complex eigenvalue pairs) at the
   internal resonance — the ghost branch acquires a decay-like channel
   that no metric can hide.
4. ε-scaling: R₂ = O(ε^{−3}) (measured −2.94, −3.00 per decade) — the
   naive (ε^{−3/2})² with NO small-denominator enhancement from ω₁−ω₂
   (those source components are suppressed). Geometric hierarchy
   R_n ~ ε^{−3n/2} ⇒ conjectured deformation radius of convergence
   λ_c ~ ε^{3/2} → 0 at the Jordan boundary. Refines the team's
   hypothesis: the positive form deforms generically but (a) fails on a
   dense-in-frequency-ratio set of interior resonance loci as order
   grows (ω₁ = 3ω₂ at n=2; expect ω₁ = 5ω₂, 5ω₂→? at higher orders),
   and (b) has vanishing convergence radius at resonance.

Next per the team's program: first-order obstruction for the
perfect-square vertex □φ(∂φ)² (mass-regulated split, transport, 𝔬₊ and
𝔬_K, remove splitting); then the Einstein–Weyl cubic vertices. The Krein
side needs the κ₀ conventions fixed first.

## Interaction-deformation, step 2 (2026-07-13): selection rules + order 3

Per the team's revised order of attack (their parity correction accepted:
5:1 tests at order 4, not 3). verify_interaction_order3.py, ALL PASS:

**Selection-rule theorem (SR1–SR3).** Order-n objects have transfers in
the n-fold sumset of the vertex transfer set (ad_{h₀}-grading is additive
under star products), total degree ≤ n+2 (each commutator reduces degree
by ≥ 2), degree parity ≡ n mod 2. Candidate interior loci: order 1 {2:1},
order 2 {3:1}, order 3 {3:2, 2:1, 4:1}, order 4 ∋ 5:1. The lattice gives
candidates; coefficients decide.

**Third-order audit (O3a–O3e).**
- Generic: obstruction vanishes; R₃ exists, Hermitian, odd degrees {1,5}
  ≤ 5 (parity rule confirmed).
- **NEW OBSTRUCTION at ω₁/ω₂ = 3:2** (order 3):
  𝔬₊^(3) = −(117√30/1120)·i·(a₁²a₂†³ + a₁†²a₂³) — the on-shell
  2-quanta ↔ 3-quanta conversion (2ω₁ = 3ω₂). Gauge-independent
  (unchanged under R₁ + {N₁,N₂,N₁N₂} and R₂ + on-shell quintic kernel
  operators).
- 2:1 (order 1 AND 3) and 4:1 (order 3) escape with vanishing
  coefficients — every obstruction found so far carries ODD mode-2
  transfer; mechanism open (flagged for paper 5 §8).
- R₃ = O(ε^{−9/2}) (measured +4.488/decade at 10⁻²→10⁻³): third data
  point of R_n = O(ε^{−3n/2}).

**Refined hierarchy conjecture** (replaces "(2k+1):1 at order 2k"):
the coprime ratio ω₁/ω₂ = p:q first obstructs at order p+q−2 when the
mode-2 transfer p is odd. Verified: 3:1 → order 2, 3:2 → order 3.
Predicts: 5:1 → order 4 (the targeted kernel-projection test), 5:3 →
order 6.

**Next (per team priority): the perfect-square benchmark.** Opening
kinematic observation, to be developed: with the split-mass regulator
(m₁² − m₂² = δ small, so m₁ < 2m₂), the 1→2 decay channels
ω₁(k₁) = ω₂(k₂) + ω₂(k₃) are kinematically CLOSED and 0→3 is closed for
any positive masses — the first-order obstruction 𝔬₊^(1) vanishes
identically for the regulated theory by kinematics alone. The content
is therefore in (a) the δ→0 divergence rate of the off-shell R₁
coefficients (the collinear massless limit, where 1→2 becomes on-shell
on the measure-zero collinear set) and (b) whether the □φ factor of the
vertex — which vanishes on the massless branch shell — kills the
collinear obstruction distributionally. Then the parallel Krein 𝔬_K with
κ₀ fixed. Paper 5 drafting (their title: "Interaction Obstructions and
Resonant Breakdown of the Positive Pais–Uhlenbeck Metric") once the
perfect-square first-order results are in.

## Interaction-deformation, step 3 (2026-07-13): spectral PT-breaking + PS vertex

Team's degenerate-PT results ALL VERIFIED + independently cross-checked
(verify_pt_breaking.py, ALL PASS):

**Spectral PT-breaking at 3:1 (PT1–PT4).**
- E = 27ω₂ shell (10 states |j,27−3j⟩): second-order effective matrix is
  real tridiagonal; their closed forms for the antisymmetric off-diagonal
  K_{j,j+1} = −(27√3/640)√((j+1)n(n−1)(n−2)) and the diagonal
  D(n₁,n₂) = (633n₁²−1836n₁n₂−285n₁+3969n₂²+3051n₂+818)/26880 confirmed
  entrywise to 1e−8.
- Spectrum: 8 real + one complex pair κ± = 2.448807382199 ±
  0.224586593808i — matches the team to 13 digits. Lowest doublet
  {|1,0⟩,|0,3⟩} stays REAL (diagonal shifts dominate): metric obstruction
  ≠ automatic breaking of the lowest pair.
- **Beyond formal PT**: exact diagonalization of the truncated h₀+λv at
  λ = 0.02 (two cutoffs) exhibits the complex pair IN the spectrum:
  Im = ±0.2246λ² to 0.5%, Re−27 = 2.4488λ² to 5 digits. ⇒ genuine
  perturbative PT-breaking: wherever the pair persists, NO
  positive-definite invariant metric exists (analytic or otherwise) —
  the strong spectral conclusion, modulo the stated operator-theoretic
  qualifications (formal PT, unbounded cubic).
- **Tongue law**: detuned shell pencil diag(jδ) + λ²K goes complex for
  |δ| < δ_c = 38.4151·λ² — exactly linear in λ² (multiplet constant).
  (Fixed a bracket-initialization bug in my first search that saturated
  at the initial guess.) Order-n resonance ⇒ O(λⁿ) tongue.

**Perfect-square vertex (PS1–PS2).**
- Symmetrized cubic vertex of □φ(∂φ)² == ½λ_K(p₁²,p₂²,p₃²) identically
  (Källén polynomial), verified with explicit 4-vectors.
- Selection rules: λ_K(0,0,0) = 0 (no on-shell massless 3-amplitude);
  ∇λ_K|₀ = 0 (one generalized Jordan leg → zero); Hessian = (2,−2) ≠ 0
  (Jordan legs couple in PAIRS — the ghost-parity-compatible structure);
  threshold factorization λ_K(m₁²,m₂²,m₂²) = m₁²(m₁−2m₂)(m₁+2m₂):
  the regulated 1→2 channel closes below m₁ = 2m₂ and the vertex
  vanishes AT threshold.

Wording correction adopted (team §5): the resonance set is an EXPANDING
HIERARCHY, not (yet) dense — density would require general p:q loci,
a separate selection-rule question.

Three-mechanism picture now machine-verified end to end: (i) Jordan
scaling R_n ~ ε^{−3n/2} (λ_c ~ ε^{3/2} conjecture), (ii) cohomological
obstructions at interior resonances (3:1 order 2; 3:2 order 3), (iii)
genuine spectral breaking in excited resonant multiplets. Opposite
tendency for the perfect-square interaction (massless & one-Jordan-leg
amplitudes vanish; pairs couple) — the clearest indication yet of why
Krein/ghost-parity survives where the positive completion fails.

## Interaction-deformation, step 4 (2026-07-13): regulated perfect square

Coupled positive+Krein computation in the finite-mode model (1+1D triple
k = 3 ← 2+1, both branches, exact mode algebra; the transported field
mode φ'(k) = (i/√(2δ))[(a₂+a₂†)/√ω₂ + (a₁−a₁†)/√ω₁] derived from
ρ₀zρ₀⁻¹ and verified against the paper-3 spectral Wightman; σ = √δ is
k-independent). verify_perfect_square.py PS-A..H ALL PASS.

**Headline: the first-order answers INVERT the naive expectations.**
1. **Even-ghost selection rule (PS-B)**: v†−v is supported on even-
   ghost-count monomials only (the transported reality factor η^{ghost}
   makes odd-ghost coefficients Hermitian-symmetric) — the exact field
   analogue of the oscillator's v†−v ⊃ {y³, yp²} rule.
2. **𝔬₊^(1) = 0 IDENTICALLY (PS-C/D)** — below AND above the m₁ = 2m₂
   threshold: the only openable shells (1→22) are odd-ghost, where
   v†−v vanishes; even-ghost shells (2→22, 11→2) are kinematically
   closed for all m₁ > m₂. The team's "possibly nonzero above
   threshold" resolves to NO at first order.
3. **𝔬_K^(1) (PS-E)**: zero below threshold; NONZERO on the open 1→22
   shell above it, exactly λ_K(m₁²,m₂²,m₂²)×(leg factors) — continuous
   turn-on ∝ m₁²(m₁²−4m₂²). Physics: a really-decaying ghost has no
   conserved parity; the Krein/parity structure is protected only where
   λ_K = 0 (threshold and the massless perfect-square point).
4. **Scaling table (PS-F/G)**:
   - massive confluence (m > 0, δ→0): |R₁| ~ |K₁| ~ δ^{−3/2} — both
     completions lose uniformity (matches the oscillator).
   - massless Jordan paths m₂² = αδ: positive R₁ ~ δ^{−1/2} with
     PATH-INDEPENDENT power (α = 1 and the collinear-exceptional
     α = 2/7 both −0.50) — the selection rule removes the dangerous
     odd-ghost near-shell term from R₁; the Krein near-shell term is
     δ^{−1/2} generic but δ^{−3/2} on α = 2/7 (path-dependent).
   - λ_K suppression is what tames the massless limit relative to the
     massive one (δ^{−1/2} vs δ^{−3/2}).
   - CAVEAT for the paper: the 1/√δ-per-leg normalization is intrinsic
     to the split (partial-fraction) mode basis, which itself
     degenerates at δ = 0; a basis-independent uniformity statement
     (matrix elements between fixed limit states) is the required
     sharpening — flagged, not yet done.
5. **Jordan-chain lemma (PS-H)**: any chain-preserving κ with
   [κ,H_J] = 0, κ² = 1 is ±identity — ghost parity cannot be a
   per-block sign (u→u, v→−v fails, as the team warned); it must act
   across the doubled O(1,1) structure. The constructive κ₀ derivation
   from the regulated Krein algebra (δ→0 limit of (−1)^{N_ghost})
   remains next.

Refined comparison table (first order, split perfect square):
              | positive           | Krein
  sub-thresh  | 𝔬 = 0, R₁ finite   | 𝔬 = 0, K₁ finite
  above thresh| 𝔬 = 0 (selection!) | 𝔬 ∝ λ_K ≠ 0 (real decay)
  massive conf| R₁ ~ δ^{−3/2}      | K₁ ~ δ^{−3/2}
  massless    | R₁ ~ δ^{−1/2} unif | K₁ ~ δ^{−1/2}, exc. path δ^{−3/2}
The distinction the series predicts must therefore sit at SECOND order
(where oscillator experience says the positive form hits on-shell
obstructions from even-ghost composites — the analogue of 3:1) and in
the exact massless parity structure (λ_K = 0 kills the Krein
obstruction there while the paired-Jordan vertex preserves parity).
Next: second-order field obstructions; constructive κ₀; paper 5.

## Interaction-deformation, step 5 (2026-07-13): two-field rewriting + κ₀

The team's story pivot adopted ("Krein symmetry is not generic in the
split theory; it emerges at the special massless perfect-square
boundary" — symmetry enhancement at a singular boundary, mirroring the
Weyl enhancement at the gravity conformal locus). Their exact two-field
rewriting verified and extended (verify_two_field.py TF1–TF7 ALL PASS):

1. Auxiliary elimination + exact nonlinear map U = e^{λφ},
   V = (ψ/λ)e^{−λφ} give ℒ = −∂U·∂V + (λ²/2)U²V² EXACTLY; X,Y form
   has the O(1,1)-invariant interaction (λ²/8)(X²−Y²)².
2. **Constructive ghost parity (queue item 1 DONE at the exact level)**:
   κ₀ = U↔V is an exact symmetry of the full interacting action; in the
   original variables κ₀: (φ,ψ) → ((1/λ)log(ψ/λ) − φ, ψ) — exact,
   NONLINEAR, invisible at any finite perturbative order in (φ,ψ).
3. κ₀ swaps the null backgrounds (1,0) ↔ (0,1): ghost parity acts
   BETWEEN the two pointed sectors — exactly what the Jordan-chain
   no-go lemma (PS-H) requires. The regulated (−1)^{N_ghost} and the
   exact U↔V are different objects; their relation (confluent limit) is
   the remaining derivation.
4. **The Jordan structure is generated by the interaction**:
   linearizing about the null background gives ℒ₂ = −∂u·∂v + (λ²/2)v²,
   EOM □v = 0, □u = λ²v — the exact □² Jordan pair with the coupling λ²
   as the off-diagonal. The free □² theory and the interacting
   perfect-square vacuum structure are one object.
5. **Legendre warning recorded (TF7)**: in (U,V) the interaction has no
   time derivatives ⇒ H_int = −L_int exactly; in (φ,ψ) the quartic
   −½(∂φ)⁴ has time derivatives ⇒ the canonical second-order source
   (team eq. 3–4) needs Legendre corrections. The Outcome A/B on-shell
   computation (1+2 → 2+2, quartic contact term included) should be
   built in the two-field frame to avoid a false obstruction.

Queue: (2) on-shell second-order positive source at 1+2→2+2 in the
two-field frame; (3) second-order Krein identity (κ₀ now exact — the
question becomes whether the PERTURBATIVE sector-preserving remnant of
U↔V survives order by order); (4) confluent-state matrix elements of R₁
(basis-independent uniformity); (5) 5:1 projection; (6) paper 5.

## Interaction-deformation, step 6 (2026-07-13): OUTCOME A — sectorwise obstruction

Team's reframing adopted and verified (verify_sector_obstruction.py
SO1–SO7 ALL PASS): κ = U↔V exchanges vacuum sectors, is not a particle
parity inside either sector, so a pointed-sector positive obstruction
and exact doubled-theory Krein symmetry are COMPATIBLE.

Structural: sector-B expansion = sector-A with u↔v (orders 2,3,4);
doubled Jordan model κ_dbl = offdiag(P,P) with κ² = 1, [κ,J_dbl] = 0;
Jacobians: det ∂(U,V)/∂(φ,ψ) = 1 pointwise, chart transition det = −1.

**Main result (Outcome A).** Regulated sector-A theory ℒ₀ = −∂u∂v −
μ²uv + (g/2)v² + (ε/2)u² (masses² = μ²±√(εg); regulator necessarily
breaks κ — consistent with boundary-emergent parity), positive-frame
quantization via branch eigenvectors (v = ρ_b u, ρ± = ∓δ/2) with the
quarter-turn structure on the ghost branch; interactions H₃ = −g uv²,
H₄ = −(g/2)u²v² are PURE POTENTIALS (Legendre trap avoided by
construction). The exact matrix-element form of the second-order source
⟨out|S|in⟩ = ⟨v₂†−v₂⟩ + Σ_n[⟨out|v₁†|n⟩⟨n|v₁†|in⟩ −
⟨out|v₁|n⟩⟨n|v₁|in⟩]/(E−E_n) (uses (v†−v)(v+v†)+(v+v†)(v†−v) =
2(v†v†−vv)) evaluated on tuned branch-changing shells
heavy+light → light+light:
- contact piece ⟨v₂†−v₂⟩ = 0 on every shell tested (the quartic neither
  rescues nor produces the obstruction);
- exchange piece NONZERO: 0.5233 at (2,−1,3,−2); 0.3109 at (1,−3,2,−4);
  0.3970 at (1,−4,3,−6) — three independent tuned kinematics;
- truncation-complete (identical at K_max = 4 and 6: all tree channels
  s,t,u inside the momentum set; OFPT 1-, 3-, 5-particle intermediates
  close on the same momenta).

**Conclusion**: the positive pseudo-Hermitian completion of the pointed
sector is obstructed at second order by generic on-shell branch-
changing 2→2 scattering — the continuum analogue of the oscillator's
isolated 3:1 resonance, made generic by the scattering shells. No
perfect-square cancellation (Outcome B refuted); the exact κ maps the
obstructed sector-A construction to the mirror sector-B construction,
consistent with: **Krein symmetry lives on the doubled state space,
not inside one pointed positive sector.** (A quick regulator-swapped
"sector-B" run is also obstructed, −0.0177 — any pointed positive
completion fails.)

Paper-5 arc now complete at the free+second-order level:
oscillator (generic deformation → isolated resonant obstructions →
spectral PT-breaking → R_n ~ ε^{−3n/2}) ⇒ field theory (first-order
protection by the even-ghost rule ⇒ generic second-order scattering
obstruction in every pointed sector ⇒ exact nonlinear sector-exchange
κ on the doubled theory ⇒ Jordan structure generated by the interaction
at the massless boundary). Remaining before drafting: (i) regulated
parity on H_A⊕H_B (confluent limit of (−1)^{N_ghost} as off-diagonal
map — team's prediction), (ii) confluent-state R₁ matrix elements,
(iii) 5:1 fourth-order projection, (iv) superselection question
(cat states |0_A⟩±|0_B⟩).

## Interaction-deformation, step 7 (2026-07-13): hardening + PAPER 5 DRAFT

Theorem hardening (verify_hardening.py HX1–HX3 ALL PASS):
- HX1 **exact obstruction value**: at the rational CM point m_L = 4,
  m_H = 6 = (3/2)m_L, H(0)+L(0) → L(3)+L(−3) (E = 10 exactly on shell):
  𝓜_obs = 401√6/39424 exactly, contact = 0 exactly ⇒ by analyticity the
  obstruction is nonzero on an OPEN SUBSET of the branch-changing shell
  (theorem-strength genericity).
- HX2 confluent parity, single sector: P_δ = [[0, δ/2],[2/δ, 0]] in the
  (c,d) basis — P² = 1 but NO bounded δ→0 limit (algebraic version of
  the PS-H no-go, exactly the team's matrix).
- HX3 doubled space: with OPPOSITELY oriented confluent identification
  in sector B, the cross parity b±^A ↔ ±b±^B equals the δ-INDEPENDENT
  sector exchange (c_A,d_A)↔(c_B,d_B) exactly ⇒ the regulated branch
  parity converges on the doubled space to the exact U↔V involution.
  CONFLUENT PARITY THEOREM proved.

**PAPER 5 DRAFTED**: paper/interaction-obstructions.tex (12 pp., clean)
— "Interaction Obstructions and Resonant Breakdown of the Positive
Pais–Uhlenbeck Metric". Structure: deformation complex (with ζ vs λ
bookkeeping fixed) → oscillator first/second order → exact 3:1
obstruction → spectral PT-breaking (with the right-strength corollary:
complex pair excludes ALL positive metrics where it persists;
perturbative qualifications stated) → third order + transfer-lattice
selection rules + hierarchy conjecture (p+q−2 for odd p; expanding
hierarchy, not dense) → Jordan divergence hierarchy (theorem at fixed
order + conjecture for λ_c) → Källén vertex → first-order field
protection + Krein decay obstruction → exact two-field rewriting +
nonlinear κ₀ + interaction-generated Jordan sectors → sectorwise
second-order obstruction with the EXACT value 401√6/39424 and the
oscillator-vs-continuum table → confluent parity theorem → discussion
(boundary symmetry enhancement mirroring gravity's Weyl; superselection
open and stated conditionally; 5:1 and EW-vertex predictions).
Appendix maps all check IDs to theorems. Authors block as the series.
Tag paper5-v1.0 at freeze.

## Paper 5 referee pass + paper 0 revision (2026-07-13)

**Paper 5 referee round (major revision applied).** Concrete errors
verified first:
- I.1 CONFIRMED: confluent matrix was the row-convention transpose;
  column convention P_δ = [[0, 2/δ],[δ/2, 0]] (P c = (δ/2)d,
  P d = (2/δ)c) — HX2/HX3 fixed, unboundedness/doubling conclusions
  unchanged.
- I.2 CONFIRMED: branch ratio is ρ± = ∓δ/(2g) (nullspace check); my
  computations used g = 1 so numerics stand; convention now explicit.
- I.3 CONFIRMED: 3:2 obstruction scales exactly as ω₂^{−13/2}
  (ratio 2^{−13/2} between (6,4) and (3,2), exact) — dimensional
  factor now stated.
New certificates: **PT proposition** (𝒜 = Π∘K antiunitary, [𝒜,h_ζ] = 0,
machine-verified — "PT breaking" now formally defined); **exact Sturm
certificate** for the complex pair (tridiagonal ⇒ rational char poly;
exact count: 8 real roots ⇒ exactly one complex pair; 30-digit
enclosure); **exact R₁ Jordan asymptotics** (leading Laurent
coefficients extracted: theorem for R₁; R₂/R₃ demoted to Computational
Proposition per referee).
All major revisions applied: new title "Interaction Obstructions,
Resonant PT Breaking, and Doubled Jordan Symmetry in Fourth-Order
Theories"; abstract → 4 results with inherited qualifications;
chart-vs-global distinction for U↔V (exact symmetry of the EXTENDED
theory; transition map singular at ψ = 0); "constant zero-action
stationary backgrounds" wording; confluent theorem → "linearization of
the exchange"; sector genericity narrowed to nonempty-open-subset with
the exact point (no per-mass-pair claim); full normalization
conventions for 401√6/39424; truncation completeness now a LEMMA with
the surviving-spectator proof; finite-volume formulation of the kernel
projection stated (Remark); gauge independence at 3:1 restated with
the resonant quartic R₁-additions (already verified in ID9b) and the
R₂-additions clarified as third-order; tongue = effective-multiplet
statement + o(ζ²); O(ζⁿ) tongue = expectation, not proposition;
Källén Jordan-leg claim → "second-order zero of the polynomial vertex
factor"; six appendices with actual derivations (Moyal recursion,
3:1 projection + gauge independence, shell matrix + charpoly, transfer
lattice, field conventions + source formula + truncation proof,
doubled parity); check-classification table (exact-symbolic /
exact-rational / numeric). Authorship kept per Asger (non-traditional
publication). 13 pp. clean.

**Paper 0 revised per the team's specification**: abstract gains the
paper-V paragraph (their wording); intro reframed as Stage 1 (free) /
Stage 2 (interaction stability) with the machine-balance sentence; §3
gains the three-level distinction + "solved locally / paper V
determines where it survives" box; NEW §14 "When interactions are
switched on" with five subsections (deformation equation with lay
explanation, oscillator resonances + spectral breaking with the
two-level caution, continuum mechanism, second-order timing via
Källén/even-ghost, mirror Jordan sectors + confluent parity) +
mechanism diagram (Figure 2) + terminology paragraph; gravity section
gains "What Paper V predicts" (no failure claim — machinery +
predictions only); §17 gains Paper V row + the program paragraph +
Paper-V node in the dependency figure; open questions updated (field
complex energies, superselection, EW vertices); conclusion → five-level
hierarchy + "which completion survives the allowed interactions?".
22 pp. (grew ~29%, within the spec's 25–35%), clean.

## Paper 5: ACCEPT after final audit — audit applied (2026-07-13)

Referee verdict: "Accept after a final consistency and presentation
audit" (from major revision — first paper in the series to reach accept
on the first revision). All six audit points applied:
1. Spectral claim localized: explicit 3-level hierarchy in the
   corollary (exact effective-matrix pair / cutoff-stable truncations /
   full unbounded operator OPEN); abstract carries the qualification
   inline ("effective resonant-shell characteristic polynomial...; the
   statement for the full unbounded operator remains open").
2. Notation: complex conjugation renamed K → Θ with an explicit
   disambiguation sentence (vs Krein K_n, K^(2), K_max).
3. g-convention before the exact number + g-restored display:
   𝓜_obs = 401√6/(39424 g²) → g=1 — the 1/g² dependence VERIFIED
   exactly (each vertex ∝ gρ² = δ²/(4g); numerical check at
   g ∈ {1/2, 1, 2} exact).
4. "Generic" disambiguated: three senses defined in the Strength
   paragraph (oscillator frequencies / open shell subset /
   kinematically open ≠ dynamically nonzero).
5. Status ledger added (R₁ thm; R₂,R₃ comp props; R_n conjecture;
   5:1 prediction; field spectrum open; classical involution thm;
   quantum implementation open) — single authoritative list in the
   intro.
6. Confluent wording checked: "linearization of the exchange" only,
   nowhere upgraded.
Referee's three-level failure taxonomy adopted as the paper's
contribution summary: geometric (Jordan R_n divergence) /
cohomological (on-shell conversion) / spectral (nonreal energies).

Paper 0: the four permitted upgrades applied — "formally defined
perturbative PT breaking" (antilinear symmetry constructed + commutes),
"exactly certified in the effective resonant multiplet", field
obstruction as "open scattering-shell subset (not every kinematic
point)", confluent result as the "linear bridge" to the independently
exact nonlinear exchange with the no-stronger-identification note.
Both papers compile clean (13 pp. / 22 pp.).

## 2026-07-13 — Doubled/Krein verification, literature repositioning, 5:1 confirmed, freeze tags

Team direction (two messages): (1) verify the "doubled theory" program
— mirror-adjoint relation, paired optical theorem, Ward identity —
plus the O(1,1)/rapidity structure; (2) mid-flight literature audit:
the O(1,1) embedding, exchange-as-ghost-parity/charge-conjugation,
quantum embedding R, Krein Born rule are all Bateman–Turok
(arXiv:2607.00096) — reposition papers 5/0 accordingly; the genuinely
new items are the obstruction complex, the exact 3:1/3:2/(5:1)
classes, the certified spectral pair, the shell obstruction, the
confluent bridge, and the SEPARATION of the two completions.

### verify_doubled_theory.py (DQ1–DQ9, ALL PASS, ~3 min)

- DQ1–DQ2: hyperbolic-polar form U=√r e^χ, V=√r e^−χ:
  ℒ = −(1/4r)(∂r)² + r(∂χ)² + (g/2)r², Jacobian det −1, field-space
  metric det −1; Noether current j = V∂U − U∂V = 2r∂χ conserved
  on-shell exactly; exchange flips j.
- DQ3–DQ6 (structural): H_B = WH_A†W† ⇒ conserved off-diagonal
  pairing; pure-sector and complex-E states η-null; graph theorem
  BOTH directions (positive invariant half of the doubled space ⇔
  pointed positive metric — doubling cannot evade the obstruction);
  finite-time interaction-picture S_B(t)†WS_A(t) = W EXACT whenever
  [W,H0] = 0 (so the "paired optical theorem" is a representation of
  Krein pseudo-unitarity, as the team's audit suspected).
- DQ7 (team step 9A, the sharp finding): the mirror-adjoint relation
  holds EXACTLY with W = ι∘(−1)^{N_ghost}: (a) H_B = H_A under the
  naive κ identification (mirror sector = same theory in mirrored
  frame); (b) H_A† = G H_A G term by term. So the mirror-adjoint
  relation IS Krein pseudo-Hermiticity w.r.t. ghost parity, and the
  doubled pairing is the two-sector unfolding of BT's κ — this
  DEMONSTRATES the equivalence the audit asked to be demonstrated.
- DQ8 (team step 9B + steps 3–5 of the reconciliation program,
  pointed frame): on the exhaustively-verified degenerate shell
  {H(0)L(0), L(3)L(−3)} at E = 10, the full 2×2 second-order on-shell
  T satisfies GTG = T† EXACTLY in radicals while Hilbert Hermiticity
  fails; T_B = T_A; diagonal (κ-even) block real; the ENTIRE
  obstruction is the κ-odd block: T(out,in) = −401√6/78848 =
  −𝓜_obs/2 (independent recomputation of HX1 from plain T elements).
  ⇒ The obstruction is carried exactly by the κ-odd component — the
  component BT's weak-ghost-symmetry positivity mechanism does not
  use. Krein pseudo-unitarity and positive-metric failure coexist on
  the SAME matrix elements.
- DQ9 (team step 9C, classical/regulated): unregulated pointed Ward
  ∂·j = 0 exactly (all interaction orders cancel); regulated breaking
  EXACTLY εu(1+u) − μ²v (regulator terms only). Unit Jacobian ⇒ no
  measure factor. Normal-ordered operator check [H,Q̂] queued.

### verify_51_order4.py (FO1–FO9, ALL PASS, ~90 s, agent-built, independently re-run)

Order-n sources generated programmatically from the adjoint series
e^{−X/2}⋆(h0+ζv)⋆e^{X/2} (word generator; T4 = 11 words), validated
by re-deriving the order-2 (27√3/320 at 3:1) and order-3
(−117√30/1120 i at 3:2) classes exactly. At (5,1): orders 2–3 kernel
projections VANISH, R₂,R₃ Hermitian; order 4 NONZERO exactly:
  𝔬₊^(4) = −(203125√5/2341011456)(a₁a₂†⁵ − a₁†a₂⁵)
         = −(13·5^{13/2}/(2¹⁶3⁶7²))(…) ≈ ∓1.94·10⁻⁴,
the predicted 1↔5 monomial. HIERARCHY CONJECTURE (p+q−2, odd p)
CONFIRMED at its first prediction. Scaling 𝔬₊^(4) ∝ ω₂⁻⁹ exact
(2⁻⁹ ratio (10,2)/(5,1)), extending 𝔬₊^(n) ∝ ω₂^{−(5n−2)/2};
gauge-independent; R₄ = O(ε⁻⁶) (measured +5.993/decade), 4th point
of R_n = O(ε^{−3n/2}).

### Paper edits

Paper 5 (now 16 pp., compiles clean): abstract (iv) reattributed to
BT + separation claim; new "Relation to prior work" intro paragraph
(BT / standard pseudo-Hermitian–Krein–Lee-Wick lineage / what's new);
thm:twofield marked "[adapted] BT" with attribution preamble + their
nonperturbative U>0 caveat adopted; NEW Comp. Prop. cprop:krein
(mirror-adjoint = Krein pseudo-Hermiticity; κ-odd localization;
finite-time pseudo-unitarity; graph iff); NEW Comp. Prop.
cprop:fiveone (5:1 confirmed); status ledger updated; discussion:
"Separation of the two completions" paragraph + BT R_t/null-C
transport as the concrete next calculation; open questions: r=0
boundary problem in (r,χ), operator Ward; 5 new bib entries
(Mostafazadeh math-ph/0207009, Feinberg–Znojil 2111.04216, Mannheim
1611.02100, Liu–Modesto–Calcagni 2208.13536, Azizov–Iokhvidov).
Paper 0 (22 pp.): rewriting attributed to BT; separation paragraph
added to §14.

### BT digest

notes/bateman-turok-embedding.md — full LaTeX-source digest of
arXiv:2607.00096 (agent; equations verbatim from the authors' TeX).
Load-bearing caveats for the next calculation: proof of their Eq.(19)
and the "no positively charged operators" lemma deferred to a
companion paper ("to appear"); R defined only by adjoint action
(R_tR_t† = 1 only); R_±∞ convergence unaddressed (secular terms);
Krein † and tr never explicitly defined; dagger placements differ
across (17)/(19)/(21); the O(1,1) charge is a boost-weight grading,
not a particle/antiparticle U(1). The null-C test must be
self-contained.

### Housekeeping

Freeze tags created + pushed: paper1-v1.1, paper2-v1.2, paper3-v1.2,
paper4-v1.0, paper5-v1.0 (as referenced in each paper's Verification
paragraph). DOI minting deferred to repo extraction (needs Asger's
account). README/TODO updated.

## 2026-07-13 — Series-wide framing pass (papers I–IV) after the literature audit

Team verdict: no theorem withdrawals anywhere; framing/scope changes
only. Applied (all four papers recompiled clean; tags bumped to
paper1-v1.2 / paper2-v1.3 / paper3-v1.3 / paper4-v1.1, Verification
paragraphs updated accordingly):

- Paper I (17 pp.): explicit "classify and canonically reconstruct the
  KNOWN positive free quantization" framing in the intro; new
  "Kinematic status" discussion paragraph (free canonical status ≠
  interacting deformability; obstruction can't be blamed on a bad
  metric since the deformed metric is the canonical/least-distorting
  one, cites Paper V); abstract Jordan no-go narrowed to "no
  NONDEGENERATE positive-definite invariant Hermitian form (indefinite/
  degenerate forms and intrinsically Jordan PT realizations remain)".
  The rem:jordanpt narrow scoping and the prominent BM equal-frequency
  realization were already in place.
- Paper II (14 pp.): "free geometric optimality ≠ interacting dynamical
  stability" distinction added to the variational-principle discussion;
  strengthening reading made explicit (the obstruction strikes the
  OPTIMAL free metric).
- Paper III (13 pp.): "division of labor" paragraph — Krein
  quantization, ghost parity, O(1,1) embedding, indefinite-space
  positivity are BT's constructions, none claimed; novelty restated as
  "identify the common free complex covariance + determine which data
  (involution/algebra/completion) distinguish"; explicit caution:
  common free covariance ⇏ identical interacting theory (completions
  SEPARATE under interaction, Paper V); "Krein boundary" qualified as a
  free-covariance statement (confluent covariance admits a Krein
  completion; BT's interacting structure is additional data).
- Paper IV (15 pp.): NEW "Relation to Mannheim's CPT program" paragraph
  (Mannheim 1611.02100 + Mostafazadeh math-ph/0207009 added to bib):
  (i) away from the conformal locus every massive spin-2 polarization
  admits a positive completion but only JOINTLY with uniformly rotated
  reality — a CPT-based positive product lies INSIDE the classified
  class with that qualification; (ii) at the boundary cond(N) = e^r
  diverges; (iii) the Jordan theorem excludes exactly nondegenerate
  time-independent positive-definite invariant forms — BM's
  equal-frequency treatment (nonstationary Jordan states, degenerate
  pairing) is OUTSIDE the excluded class, so no contradiction, only
  delimitation; (iv) the trilemma is the choice a CPT-based ghost-free
  quadratic gravity must make. Also: interchangeability caveat added
  to "Relation to the two programs" (free agreement ≠ interacting
  interchangeability; scalar separation proven in Paper V,
  gravitational case not computed); interaction outlook cites Paper V's
  mechanism with the team's suggested wording.
- All four papers now cite Paper V (companionV/companion5 bib entries).

Series hierarchy now uniform: known constructions (BM positive, BT
Krein) → I–II derive/classify/characterize the free positive metric →
III identifies the common covariance and separates real form/completion
→ IV classifies gauge/Lorentz effects in gravity → V proves
positive-metric deformability fails on interacting on-shell channels
while the Krein structure survives (the separation statement).
