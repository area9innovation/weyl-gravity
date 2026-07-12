# TODO — symplectic-reconstruction

Working list. Completed work is recorded in
`reports/variational-and-field-theory.md` and git history; this file
holds only open items.

## Release / freeze

1. [ ] Freeze all four papers + create tags (each is already referenced
   in its own Verification paragraph): `paper1-v1.1`, `paper2-v1.2`,
   `paper3-v1.2`, `paper4-v1.0`.
2. [ ] Repo/companion identifiability (raised by referees of papers 1,
   3, 4): the repository is PRIVATE. Decide: (a) make the companions +
   verification code public and cite immutable versions, or (b)
   reproduce the load-bearing lemmas in appendices. Needs Asger.
3. [ ] Before submission (all papers): author metadata (title pages are
   blank), replace "companion paper, 2026" citations with arXiv IDs
   once public, check "to appear" references (ABHT in paper 3).

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

14. [ ] Paper 4 interaction diagnostic: [P_ghost, S_int] = 0 at cubic
    order for the gravitational Krein form; rotated-reality
    compatibility with cubic Weyl vertices for the positive form.
15. [ ] Paper 2 outlook (i): classify quadratic PT Hamiltonians whose
    positive diagonalizer direction is inter-mode for some splitting.
16. [ ] Λ ≠ 0 phase diagram (critical gravity / partial masslessness
    loci) — flagged out of scope in paper 4.
