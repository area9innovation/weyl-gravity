# TODO — weyl-gravity

Open items only. Completed work lives in `reports/` and git history.

Scope note: this file tracks **release gates and the legacy Paper 01–06
backlog**. Open scientific work for Papers 07–18 and the black-hole,
conformal, quantum, and observer streams is tracked in
`planning/work-items/` (the operational face of
`notes/universe-building-roadmap.md`), not here. Do not add new stream work
to this file.

## Release / freeze

**Publication model (decided 2026-07-27): GitHub only.** The programme
publishes as an open repository. There is no arXiv submission, no journal
submission, no release tag, and no DOI.

The reason is authorship, and it is deliberate rather than a gap to close.
The manuscripts name GPT-5.6.sol as principal author and Asger Alstrup Palm
as non-technical orchestrator and corresponding human contact, which is an
accurate description of how the work was produced. arXiv and every major
journal require that a human author take authorship and accountability, and
prohibit listing an AI as an author. Rather than restate the authorship to
fit those venues, the programme publishes where the honest attribution can
stand. Reconsider only if the attribution itself is reconsidered.

A DOI was also declined (2026-07-27): the tree is still too fluid for an
archival snapshot to be worth minting. Tags were declined for the same
reason — a tag asserts a snapshot worth pointing at.

Consequences that are now closed rather than open:

- The monorepo-era per-paper tags (`paper1-v1.2`, `paper2-v1.3`,
  `paper3-v1.3`, `paper4-v1.1`, `paper5-v1.1`) are obsolete and will not be
  recreated. All five in-manuscript references to them are removed;
  manuscripts now tell readers to cite the repository commit hash.
- The 22 dead `companion paper, 2026` bibliography entries in Papers 01–06,
  plus the unlocated companion entries in Papers 08 and 11, now carry
  authors, exact titles, programme paper numbers, in-repo paths, and the
  repository URL.

1. [x] **Supply titles for 11 abbreviated bibliography entries.** Found
   2026-07-27 during the reference review. They give only author, journal,
   volume and page, so a reader cannot tell what is cited and no automated
   check can validate them: `02:BM2008PRL`, `02:BM2008PRD`, `03:BM2008PRL`,
   `03:Mostafazadeh2010`, `03:vN1939`, `03:Holdom`, `04:Stelle`,
   `04:Holdom`, `04:Riegert`, `17:stucker2024`, `17:gajicwarnick2024`.
   Each is cited *with* its full title elsewhere in the series, so this is
   transcription, not research.

   Completed 2026-07-27. Papers 02--04 now carry the missing titles; the two
   Holdom volume/article pairs were also corrected. The Paper 17 entries
   already contained plain-text titles and required no edit.

2. [ ] **Disposition 54 uncited bibliography entries across 17 manuscripts.**
   Found 2026-07-27. Every `\cite` in the series resolves — there are zero
   cited-but-undefined keys — but 54 `\bibitem`s are never cited and render
   in reference lists with nothing pointing at them. Worst offenders:
   `07-08-archive` (6), `06` (6), `13` (6), `14` (6), `11` (5), `00` (4),
   `03` (4).

   Many are foundational works the paper plainly rests on but never
   explicitly cites (Bach, Regge–Wheeler, Lee–Wald, Stelle, BV). Those want
   a citation in the text, not deletion. Deciding which need citing and
   where is an editorial judgement per paper. Once dispositioned, add a
   bibliography-hygiene rail; one is not added now because the tree would
   fail it immediately, and a rail that is expected to fail is not a rail.

3. [x] **Repair the 22 verifiers broken by the subtree extraction.** Found
   and quantified 2026-07-27 while building the crosswalk; see
   `reports/standalone-history-crosswalk-2026-07-27.md`.

   Of 30 verifier/test scripts that reference a dangling commit or the old
   `physics/symplectic-reconstruction/` path prefix, 22 fail: 17 on
   git-attached lookups, 2 on content supersession, 3 on an import path that
   masks the same git-attached failure. They are live scientific rails in
   `quantum-weyl/`, `closed_universe_observers/`, `d_quotient_classical/`,
   `bridge/`, `paper/`, and `residual_atlas/`.

   The repair was mechanically determined — `reports/standalone-history-
   crosswalk.json` supplies every missing commit id and the path fix is
   prefix stripping. Rewriting the
   pinned ids in place would edit historical provenance records, which the
   append-only law forbids, and some pins sit inside certificates whose own
   hashes are pinned downstream, so no pin was rewritten.

   Completed 2026-07-27 with the fail-closed runtime resolver
   `ci/standalone_provenance.py`, two append-only successor rails for
   self-hashing V1 verifiers, and explicit retirement of four obsolete
   monorepo-materialization process rails. See
   `reports/standalone-provenance-runtime-repair-2026-07-27.md`.

4. [x] **Decide whether five superseded input pins invalidate their results.**
   Separate from the extraction, and not a provenance repair.
   `closed_universe_observers/certificates/CHARGED_TIME_RECEIVER_ADMISSIBILITY_CROSSWALK_V1.json`
   now hashes to `78cdd185…`, but five older certificates still pin the
   superseded `e2c9aad2…` (listed in the crosswalk report). The old content
   is genuinely in history, so this is the fail-closed machinery working:
   an input changed and the dependents were never revisited. Whether those
   five results survive the change is a scientific question.

   Completed 2026-07-27 without repinning V1 records. Two are intentionally
   historical-base replays. Rebuilding the other three against the current
   input gives identical scientific projections and changed provenance only.
   See
   `closed_universe_observers/receipts/OBSERVER_SUPERSEDED_INPUT_REVALIDATION_2026_07_27_V1.json`.

## Known weak spots in Papers 01–06 (not yet raised by referees)

5. [ ] `04-fourth-order-gravity`: referee 2 suggested a full section reorder
   (reduced complex theory → real forms → Cartan → kernel → degeneration);
   applied as insertions only. Revisit if raised again.

6. [ ] `03-fourth-order-vacuum`: the □²-anchor infrared question is
   explicitly open (Remark "anchor is an infrared question"). A proper IR
   Shale/Araki–Yamagami analysis would close it — a new result, not a repair.

7. [ ] `02-variational-fock`: invariant Sobolev classification of the
   original field variables (pullback D(k)†M_obs(k)D(k) in a fixed
   trivialization) — withdrawn claim, recoverable with one computation.

## Receipts / verification backlog (2026-07-12 audit)

8. [ ] Lean: Schur no-hybrid (commutant of so(3) spin-2 5-dim irrep = ℝ·I) —
   Paper 04's central obstruction, finite-dim matrix algebra.

9. [ ] Lean: orbit-constancy eigenvector lemma (ℓᵀX = −iℓᵀ ⇒
   metric-independence) — load-bearing for Papers 03 AND 04.

10. [ ] Lean: trilemma coset {T: TA₊T⁻¹ = −A₊} = T₀·SO(2,ℂ) + quarter-turn
   congruence (4×4, reuses `NormalForm.lean` patterns).

11. [ ] Lean: pointed-unitary Gaussian identity ψ₀ = ρ⁻¹φ₀ at the covector
    level (finite-dim, cheap) — formalizes the corrected central claim of
    Paper 02.

12. [ ] mpmath regression rail for Papers 03–04 kernels (bridge Wightman,
    sector kernels, conformal limits) — second independent rail; the Wolfram
    rail has never run (no Mathematica available).

13. [ ] Lean (cheap): Paper 02 discrete counterexample {Aⁿ}; fidelity √3/2
    and occupation 1/3 identities.

14. [ ] Lean (expensive, optional): Paper 02 minimum-distortion scalar
    inequality with arccosh closed form.

## Research continuations (from the papers' own outlooks)

15. [ ] **ON5 — boundary Born-trace evaluation** (Paper 05 capstone, the
    obstruction-to-null theorem). Build the mapped process operator
    A_s = Σ(T_s)_xy|x_s⟩⟨y_s| on a truncated charge-Fock space with the
    squeezed vacuum; charge-decompose; verify the obstruction coefficient
    never enters the boundary NEUTRAL component B_0; compute τ(B_s†B_s) vs
    τ_φ(A_s†A_s), including the first ε/g correction. Use an on-shell path
    to the BT point — naturally m_L = 4s, m_H = 6s, |k_out| = 3s, μ² = 26s²,
    εg = 100s⁴ — and prove the s → 0 limit rather than varying only the
    embedding while holding the split DQ8 matrix fixed. Machinery:
    cross-paired Gram + graded trace from ON1, map from ON2, squeezing
    from ON3.

16. [ ] Paper 02 outlook (i): classify quadratic PT Hamiltonians whose
    positive diagonalizer direction is inter-mode for some splitting.

17. [ ] Λ ≠ 0 phase diagram (critical gravity / partial masslessness loci) —
    flagged out of scope in Paper 04.

## Deferred (explicitly not in the active queue)

Vacuum-overlap / superselection at r = 0; normal-ordered internal-charge Ward
identity; confluent-state R₁ matrix elements; the field-theory
complex-spectrum question; 5:3 at order 6 and the even-mode-2-transfer
exclusion mechanism. Do not extend the doubled-scalar reconstruction before
the Einstein–Weyl calculation.

## Closed

- Repository license (CC BY 4.0 for manuscripts, data, and documentation;
  MIT for code) — assigned 2026-07-27, see `LICENSE`.
- Dead companion-paper citations and dangling release-tag references —
  repaired 2026-07-27, see
  `reports/publication-model-and-citation-repair-2026-07-27.md`.
- Papers 07 and the 07–08 computational supplement lost their authorship
  disclosure in the 2026-07-14 standardization commit `181125aa`, which had
  been failing `symbolic/verify_conformal_split_publications.py` on `master`
  ever since. Restored 2026-07-27 in the same pass.
- ABHT reference checked 2026-07-27 and found **genuine, not fabricated**.
  `ABHT` is Anderson, Bateman, Herzog and Turok; both titles are cited as
  "to appear" in refs. [25] and [27] of Bateman–Turok, *Escape from
  Ostrogradsky via hidden ghost parity*, arXiv:2607.00096 — which this
  programme already cites as `BT2026`. Still unpublished as of July 2026,
  so the entry now says so and names the corroborating source instead of
  the bare "to appear".
- Literature and reference review — completed 2026-07-27, see
  `reports/literature-and-reference-review-2026-07-27.md`. Bibliography link
  coverage 65% → 93% (98 DOI links over 73 works, each verified against
  CrossRef on title+year+volume+page, with two book-*review* false matches
  rejected on a type check). All 115 existing arXiv ids checked against the
  arXiv API: 114 correct, one wrong and fixed (Paper 07 cited Altaş–Tekin
  arXiv:1804.05602 "Chiral Gravity" for the "generic gravity in AdS" paper,
  which is arXiv:1705.10234, PRD 97 024028 — a split-out transcription slip;
  the archive and Paper 13 were already correct).
  **Hazard recorded there: a bibliography-only edit silently breaks five
  claim-map rails. Re-run the claim-map generators after any manuscript
  touch-up.**
- Subtree extraction into the standalone repository — completed 2026-07-26.
- Standalone-history replay crosswalk — completed 2026-07-27. 858 provenance
  pins swept; 244 of 245 dangling commits resolved to their standalone image
  by content, the one remainder correctly classified as the external
  tango/forge substrate. Artifact
  `reports/standalone-history-crosswalk.json`, rail
  `ci/standalone_history_crosswalk.py --check`, receipt
  `reports/standalone-history-crosswalk-2026-07-27.md`. The extraction damage
  the sweep exposed is item 2 above.
- The interaction-deformation, gravity-rail, and conformal residual logs that
  formerly filled item 14 are archived verbatim in
  `reports/todo-interaction-conformal-log-archive-2026-07-27.md`. The
  GRAVITY RAIL STATUS boundary recorded there still governs: Paper 06's
  no-go is scoped to the canonical natural, particle-number-diagonal
  cluster-multiplicative lift and must not be broadened.
