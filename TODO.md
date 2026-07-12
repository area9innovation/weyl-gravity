# TODO — symplectic-reconstruction

Working list. Completed work is recorded in
`reports/variational-and-field-theory.md` and git history; this file
holds only open items.

## Release / freeze

1. [ ] Freeze all four papers + create tags (each is already referenced
   in its own Verification paragraph): `paper1-v1.1`, `paper2-v1.2`,
   `paper3-v1.2`, `paper4-v1.0`.
2. [ ] Extract `physics/symplectic-reconstruction/` into a standalone
   shareable repo (deferred by Asger, 2026-07-12: "we will move it
   later"). Plan: intended for sharing directly with Mannheim, Bateman,
   et al. DO NOT share the monorepo link — `area9innovation/
   bp2transformer` is private, contains all unrelated company work,
   and (per project memory) a Hetzner token elsewhere in the tree.
   The symplectic-reconstruction directory itself scanned clean of
   secrets (2026-07-12). Extraction also resolves the referees'
   citable-artifact requirement (papers 1, 3, 4); create the paper
   tags in the new repo.
3. [ ] Before submission (all papers): replace "companion paper, 2026"
   citations with arXiv IDs once public, check "to appear" references
   (ABHT in paper 3). (Author metadata DONE: GPT-5.6.sol + Claude
   Fable 5 as authors with role footnotes; Asger as commissioning /
   corresponding human — all five papers.)

## Known weak spots (not yet raised by referees)

4. [ ] Paper 4: referee 2 suggested a full section reorder (reduced
   complex theory → real forms → Cartan → kernel → degeneration);
   applied as insertions only. Revisit if raised again.
5. [ ] Paper 3: the □²-anchor infrared question is now explicitly open
   (Remark "anchor is an infrared question"). A proper IR
   Shale/Araki–Yamagami analysis would close it — new result, not just
   a repair.
6. [ ] Paper 2: invariant Sobolev classification of the original field
   variables (pullback D(k)†M_obs(k)D(k) in a fixed trivialization) —
   withdrawn claim, recoverable with one computation.

## Receipts / verification backlog (2026-07-12 audit)

7. [ ] Lean: Schur no-hybrid (commutant of so(3) spin-2 5-dim irrep =
   ℝ·I) — paper 4's central obstruction, finite-dim matrix algebra.
8. [ ] Lean: orbit-constancy eigenvector lemma (ℓᵀX = −iℓᵀ ⇒
   metric-independence) — load-bearing for papers 3 AND 4.
9. [ ] Lean: trilemma coset {T: TA₊T⁻¹ = −A₊} = T₀·SO(2,ℂ) +
   quarter-turn congruence (4×4, reuses NormalForm.lean patterns).
10. [ ] Lean (new, from paper-2 pass): pointed-unitary Gaussian identity
    ψ₀ = ρ⁻¹φ₀ at the covector level (finite-dim, cheap) — formalizes
    the corrected central claim of paper 2.
11. [ ] mpmath regression rail for papers 3–4 kernels (bridge Wightman,
    sector kernels, conformal limits) — second independent rail; the
    Wolfram rail has never run (no Mathematica).
12. [ ] Lean (cheap): paper-2 discrete counterexample {Aⁿ}; fidelity
    √3/2 and occupation 1/3 identities.
13. [ ] Lean (expensive, optional): paper-2 minimum-distortion scalar
    inequality with arccosh closed form.

## Research continuations (from the papers' own outlooks)

14. [~] Interaction-deformation program (other team's direction,
    2026-07-13, ACTIVE — see reports entry + verify_interaction_
    deformation.py ID1–ID10 ALL PASS):
    - DONE: cubic PU first order verified (their R₁ exact); second
      order computed: generic unobstructed w/ end-to-end O(λ²)
      Hermiticity; **obstruction 27√3/(320ω₂⁴)(a₁a₂†³−a₁†a₂³) at
      ω₁ = 3ω₂, unremovable**; R₂ = O(ε⁻³) ⇒ R_n ~ ε^{−3n/2},
      λ_c ~ ε^{3/2} conjecture.
    - DONE (step 2): selection-rule lattice theorem (candidates =
      transfers with |d₁|+|d₂| ≤ n+2, parity n mod 2); third-order
      audit: generic clean, R₃ odd/Hermitian, **NEW obstruction at
      3:2, order 3: −(117√30/1120)i(a₁²a₂†³+a₁†²a₂³), gauge-indep**;
      2:1, 4:1 escape (odd-mode-2-transfer rule, mechanism open);
      R₃ = O(ε⁻⁹ᐟ²). Refined conjecture: p:q first obstructs at order
      p+q−2 for odd p.
    - DONE (step 3): spectral PT-breaking VERIFIED at 3:1 (E=27ω₂
      shell: κ± = 2.4488 ± 0.2246i, 13 digits; exact diagonalization
      confirms pair in truncated spectrum ⇒ no positive metric exists
      there at all); lowest doublet real; tongue δ_c = 38.4151λ²;
      perfect-square vertex = ½λ_K(p₁²,p₂²,p₃²) with massless &
      one-Jordan-leg vanishing, Jordan-PAIR coupling, threshold
      factorization m₁²(m₁−2m₂)(m₁+2m₂). "Expanding hierarchy" (not
      dense) wording adopted.
    - DONE (step 4, perfect square first order, both completions):
      even-ghost selection rule ⇒ 𝔬₊^(1) = 0 IDENTICALLY (even above
      threshold); 𝔬_K^(1) ∝ λ_K ≠ 0 above threshold (real ghost decay);
      scaling: massive confluence both δ^{−3/2}; massless Jordan paths:
      positive δ^{−1/2} path-independent, Krein exceptional path
      α = 2/7 δ^{−3/2}; Jordan-chain lemma: κ ≠ per-block sign
      (verify_perfect_square.py PS-A..H).
    - DONE (step 5): exact two-field rewriting verified (ℒ = −∂U∂V +
      (λ²/2)U²V², O(1,1) form); **constructive κ₀ = U↔V exact symmetry,
      nonlinear in (φ,ψ): (φ,ψ) → ((1/λ)log(ψ/λ) − φ, ψ)**; sector
      swap (1,0)↔(0,1) consistent with PS-H; linearization about null
      background = exact □² Jordan pair (□v = 0, □u = λ²v); Legendre
      warning: do second-order source in two-field frame
      (verify_two_field.py TF1–TF7).
    - DONE (step 6): **OUTCOME A — the pointed-sector positive
      completion is obstructed at second order by generic
      branch-changing 2→2 scattering** (contact piece vanishes;
      exchange piece nonzero at three tuned kinematics; truncation-
      complete). Compatible with exact κ (sector exchange, not
      in-sector parity). verify_sector_obstruction.py SO1–SO7.
    - NEXT: (a) regulated parity on H_A⊕H_B: confluent limit of
      (−1)^{N_ghost} as an off-diagonal sector map (team prediction);
      superselection / cat-state question; (b) confluent-state R₁
      matrix elements (basis-independent δ→0); (c) order-4 kernel
      projection AT ω₁ = 5ω₂; (d) PAPER 5 DRAFT — the arc is complete:
      oscillator hierarchy → spectral breaking → field first-order
      protection → generic second-order sector obstruction → exact
      doubled-space κ → interaction-generated Jordan boundary;
      (e) EW cubic vertices.
15. [ ] Paper 2 outlook (i): classify quadratic PT Hamiltonians whose
    positive diagonalizer direction is inter-mode for some splitting.
16. [ ] Λ ≠ 0 phase diagram (critical gravity / partial masslessness
    loci) — flagged out of scope in paper 4.
