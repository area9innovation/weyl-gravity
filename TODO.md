# TODO — symplectic-reconstruction

Working list. Completed work is recorded in
`reports/variational-and-field-theory.md` and git history; this file
holds only open items.

## Release / freeze

1. [x] Freeze tags created and pushed 2026-07-13. Current set (after
   the series-wide framing pass, same day): `paper1-v1.2`,
   `paper2-v1.3`, `paper3-v1.3`, `paper4-v1.1`, `paper5-v1.1` (each
   referenced in its paper's Verification paragraph; earlier tags
   remain for history).
1b. [ ] Mint a DOI for the archived commit (team asked for "immutable
   commit + DOI"): needs Asger's Zenodo (or similar) account; natural
   to do together with the repo extraction (item 2).
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
   corresponding human — all six technical papers.)

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
    - DONE (step 7): hardening — EXACT obstruction 401√6/39424 at the
      rational CM point (open-subset genericity); CONFLUENT PARITY
      THEOREM (P_δ unbounded in one sector; δ-independent sector
      exchange on the oppositely-oriented doubling). **PAPER 5 DRAFTED**
      (interaction-obstructions.tex, 12 pp.).
    - DONE (step 8): paper-5 referee pass applied (matrix convention,
      ρ±=∓δ/(2g), ω₂^{−13/2} scale, PT proposition, exact Sturm
      certificate, narrowed genericity, truncation lemma, chart
      distinction, six derivation appendices, new title); paper 0
      revised per team spec (new interaction section and diagram; this
      was later superseded by the six-paper Paper-VI synthesis).
    - DONE (step 9, 2026-07-13): doubled/Krein verification suite
      (verify_doubled_theory.py DQ1–DQ9 ALL PASS): mirror-adjoint
      relation H_B = WH_A†W† EXACT with W = ι∘(−1)^{N_ghost} — i.e.
      it IS Krein pseudo-Hermiticity, the "doubled pairing" is the
      two-sector unfolding of BT's κ; on-shell T exactly
      Krein-pseudo-Hermitian (GTG = T†) while Hilbert-Hermiticity
      fails; **obstruction lives entirely in the κ-odd block**
      (T(out,in) = −401√6/78848); finite-time S_B†WS_A = W exact;
      graph theorem both directions; O(1,1) polar form r,χ; classical
      Ward with exact regulator breaking εu(1+u) − μ²v. Literature
      repositioning applied to papers 5+0 (BT attribution for O(1,1)/
      exchange/quantum embedding; new refs Mostafazadeh-nd, Feinberg–
      Znojil, Mannheim CPT, Liu–Modesto–Calcagni, Azizov–Iokhvidov;
      new Prop. cprop:krein + separation-of-completions discussion).
    - DONE (step 10, 2026-07-13): **5:1 CONFIRMED at order 4**
      (verify_51_order4.py FO1–FO9 ALL PASS): 𝔬₊^(4) =
      −(203125√5/2341011456)(a₁a₂†⁵−a₁†a₂⁵) exactly, orders 2–3
      vanish at 5:1, gauge-independent, ω₂^{−9} scaling (series
      𝔬₊^(n) ∝ ω₂^{−(5n−2)/2}), R₄ = O(ε⁻⁶) (4th point of ε^{−3n/2}).
      Hierarchy conjecture p+q−2 (odd p) now verified at 3 points.
    - DONE (step 11, 2026-07-14): obstruction-to-null STAGE 1
      (verify_obstruction_null.py ON1–ON4 ALL PASS + paper-5 Lemma
      lem:chargenull + Comp. Prop. cprop:embedding, tag paper5-v1.1):
      charge-null lemma self-contained (graded Krein trace, kinematic);
      canonical Bogoliubov map to the BT charge basis; **EXACT law
      S_UU/S_VV = (δ/2g)² = ε/g** for the mapped vacuum's charged
      squeezing — one-sided iff ε = 0 (the O(1,1)-symmetric confluent
      line; BT's massless point also requires μ² = 0); confluent
      S_VV → −g/(4w²), or −1/(4w²) at g = 1, matching BT (C5)–(C6)
      at μ² = 0. Reference-dispersion no-go is exact; the broader
      charge-preserving-frame search runs away numerically to a
      degenerate frame. BT null-relocation is exact at the massless
      boundary; ε/g contamination at split is the charge-frame image
      of PS-D broken parity and is not assumed small away from the
      boundary.
    - DONE (step 12, 2026-07-14): **GRAVITY G13–G14 ALL PASS**
      (verify_gravity_cubic.py, multi-wave perturbiner engine, exact
      ℚ(i) kinematics): one-M rule A₃(Mhh) = 0 at the physical decay
      point (20 exact zeros; Einstein-truncation/Bach-flat, supports
      gravitational 𝔬₊^(1) = 0); Ward identities exact; A₃(MMM) ≠ 0,
      A₃(MMh) ≠ 0 exact; **factorization residue at P² = M² nonzero
      ⇒ MM→Mh not identically zero ⇒ [(-1)^{N_M},S] ≠ 0** (naive
      massive parity; other gradings open).
      Independent Einstein-frame rail verify_gravity_factorization.py
      closes the factorization sum exactly: the traceless potential's
      cubic `tr Phi^3` terms cancel; the nonlinear kinetic term gives
      A₃(MMM)=−sqrt(6)/8, while A₃(MMh)=−sqrt(2)/8; the arbitrary-xi
      Ward identity and massive-leg exchange symmetry vanish exactly.
      The complete five-polarization residue numerator is sqrt(3)/32.
      The internal TT inverse kernel is (P²+M²)/4 in the script's L_M
      normalization, so the pole-normalized residue is sqrt(3)/8
      (overall action normalization conventional): NONZERO.  By
      real-analyticity/Zariski density of the physical 2→2 component,
      MM→Mh is nonzero on a nonempty open real-shell subset.  This
      supplies the existence input for the second-order obstruction;
      the explicit real point is now a hardening certificate.
    - DONE (step 13, 2026-07-14): **GRAVITY G15 ALL PASS** at the
      interior rational point.  The exact contact plus all three
      gauge-fixed exchanges gives
      A_K(MM→Mh) = 7881241032/5584765625 ≠ 0 at
      s = 25/4 M², cosθ = 3/5 with real polarizations.  The total Ward
      identity, initial-M Bose symmetry, gauge-representative and
      internal-gauge independence are exact; the threshold value is
      −509784/390625.  The shifted massive-pole residue reproduces the
      G14 factorization contraction with the ghost kinetic sign.
    - DONE (step 14, 2026-07-14): **GRAVITY G17 ALL PASS**
      (`verify_gravity_obstruction.py`).  The quartic contact and every
      exchange channel were exposed separately; the physical-adjoint
      reverse process agrees term by term.  Under M = −i Mhat, the
      contact, internal-massless exchange, and internal-massive exchange
      all acquire +i (the last includes the compensating −1 of the
      quarter-turned massive inverse kernel).  Therefore
      Π_shell(B₂†−B₂) = −2i A_K σ_x, with exact off-diagonal element
      −15762482064 i/5584765625 ≠ 0.  External EOM, total Ward, and
      axial/de Donder checks pass.  The result is independent of the
      first-order metric commutant: the complete connected cubic
      physical-shell block vanishes, hence
      Π_E[G,v₁+v₁†]Π_E = 0 for every [G,h₀]=0.
      G17g now verifies the exact finite-shell identity
      P_E[(v₂†−v₂)+1/2[R₁,v₁+v₁†]]P_E = B₂†−B₂, closing the
      amplitude-to-deformation-cocycle bridge raised in Paper-6 review.
    - DONE (step 15, 2026-07-14): **GRAVITY G18 ALL PASS**
      (`verify_gravity_krein.py`) on physical BRST cohomology under the
      conventional natural-lift class: nondegenerate one-particle
      fundamental symmetry, agreement with the free Krein real form,
      and particle-number-diagonal cluster-multiplicative Fock lift.  The
      proper-orthochronous commutant is
      diag(ε₊,ε₋,ε_M I₅); parity/real-field compatibility equates ε₊ and
      ε₋, while the free signature fixes (+,+,−) even without that extra
      condition.  Tensor multiplicativity uniquely gives
      J_F=(−1)^{N_M}.  For t=iA_K,
      Tr(X^sharp X)=−A_K²≠0, and for the full G17 obstruction
      Tr(O^sharp O)=−8A_K²≠0: Z₂-odd is neutral after squaring, not null.
      The verified MMM/MMh vertices force 3q_M=2q_M=0 and hence q_M=0
      for any uniform abelian charge; the physical block also survives
      BRST cohomology and cannot be BRST-exact.
    - DONE (step 16, 2026-07-14): **PAPER 6 DRAFT + MAJOR-REVIEW
      REVISION.**  The source is correctly ordered and compiles; the
      manuscript now proves the Born--deformation identity, states the
      regulated full cubic-shell lemma including spectators and soft-mode
      prescription, maps covariant graphs to the stationary Born series
      with LSZ/Bose conventions, narrows the metric/Fock/BRST scope, and
      includes a one-command archived reproduction suite.  README and
      Paper 0 now synthesize Paper 6.  The G16 250-polarization scan
      remains optional regression hardening and is not on the theorem
      path.
    - NEXT (ON5, precise spec): boundary Born-trace evaluation —
      build the mapped process operator A_s = Σ(T_s)_xy|x_s⟩⟨y_s|
      on a truncated charge-Fock space with the squeezed vacuum;
      charge-decompose; verify the obstruction coefficient never
      enters the boundary NEUTRAL component B_0; compute τ(B_s†B_s)
      vs τ_φ(A_s†A_s), including the first ε/g correction. Use an
      on-shell path to the BT point, naturally m_L = 4s, m_H = 6s,
      |k_out| = 3s, μ² = 26s², εg = 100s⁴, and prove the s → 0 limit
      rather than varying only the embedding while holding the split
      DQ8 matrix fixed. This yields the obstruction-to-null theorem
      (paper-5 capstone). Machinery: cross-paired Gram + graded trace
      from ON1, map from ON2, squeezing from ON3.
    - GRAVITY RAIL STATUS: the originally proposed M→h+h test is now
      closed (zero by Einstein truncation), cubic order is protected,
      and G17 proves the second-order MM→Mh positive-metric obstruction.
      G18 rules out nullity for the canonical natural,
      particle-number-diagonal cluster-multiplicative lift induced on
      physical BRST cohomology.  Paper 6 is drafted and post-review
      revised; do not broaden its no-go beyond those explicit classes.
    - DEFERRED, not in the active queue: vacuum-overlap / superselection
      at r = 0; normal-ordered internal-charge Ward identity;
      confluent-state R₁ matrix elements; field-theory complex-spectrum
      question; 5:3 at order 6 and the even-mode-2-transfer exclusion
      mechanism. Do not extend the doubled-scalar reconstruction before
      the Einstein–Weyl calculation.
15. [ ] Paper 2 outlook (i): classify quadratic PT Hamiltonians whose
    positive diagonalizer direction is inter-mode for some splitting.
16. [ ] Λ ≠ 0 phase diagram (critical gravity / partial masslessness
    loci) — flagged out of scope in paper 4.
