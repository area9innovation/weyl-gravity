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
