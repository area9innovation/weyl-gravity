# Paper 7 major-revision response ledger

This ledger records the response to the first external-style mathematical
review of `paper/07-08-conformal-residual-cohomology-archive.tex`.  It distinguishes edits
already made in the archival manuscript from work still required before an
external submission.  A passing verification rail does not close an item
that requires independent expert judgment.

## Mathematical assessment accepted

The revision adopts the review's narrow statement of the result.  In the
selected closed-cylinder BV--BFV problem, all fifteen residual conformal
transformations are gauged.  The completed free/linearized BRST complex in
the selected Fock representation has no one-particle residual class and has
two ghost-dressed Weyl-square vertex/deformation classes in degree four.
Their induced complementary-degree form is positive definite and becomes
`I2` only after the declared orientation, normalization, and chiral basis
are fixed.  The result is not a positive graviton Hilbert-space theorem, an
interacting quantum theory, a Hadamard construction, or a universal choice
of cylinder boundary problem.

## Implemented in the archival manuscript

- The abstract is reduced from roughly 1,050 words to approximately 330 and
  places the full-residual-gauging and quantum/Hadamard boundaries in the
  abstract itself.
- The introduction's “seven statements” error is corrected to eight.
- The two literal `quad` typesetting defects and the ambiguous `pi=1`
  notation are corrected.
- A standalone derived residual-reduction theorem now states separately how
  the BFV differential imposes the Taub/moment-map zero locus and takes the
  derived stabilizer quotient.
- A companion remark contrasts the selected closed-universe problem with a
  fixed-cylinder, boundary-charge, or deparametrized problem.  Deleting the
  `D` ghost is explicitly rejected as a substitute for constructing the
  appropriate relative complex.
- The positivity language is made invariant: the cohomological form has
  signature `(2,0)` and is normalized to `I2` in the stated basis.
- The classical BV complex is distinguished from its polarized completed
  free/linearized Fock representation.
- Authorship now follows the programme convention: GPT-5.6.sol is the sole
  technical/model author; Asger Alstrup Palm commissioned and directed the
  work and is identified as non-technical orchestrator and corresponding
  human contact.
- The unrelated quantum local-invariant research log is reduced to a short
  outlook paragraph.
- The conclusion is shortened to the theorem, its interpretation, and its
  remaining boundary.
- The only active generated TeX input is identified and confirmed tracked:
  `paper/generated/endpoint_factorization_nullstellensatz.tex`.
- A Python-standard-library checker independently reconstructs the central
  two-particle representation and proves rank `53` with a two-dimensional
  chiral kernel without importing the authoritative conformal/BRST code.

## Publication restructuring

The section-level split into a residual-cohomology article, a covariant
causal-completion article, and a versioned computational supplement is
implemented as `paper/07-conformal-residual-cohomology-krein.tex`,
`paper/08-conformal-covariant-causal-transport.tex`, and the computational
supplement.  Both articles compile standalone and carry focused claim
ledgers.  The current monolith remains an archival theorem/label source.
Split-publication editorial guards and the isolated tracked-snapshot release
audit prevent a cosmetic split that silently breaks cross-references or
certificate scope.

## Completed artifact gate

The clean `git archive` publication audit now passes for all four publication
entrypoints.  Its machine-readable receipt is archived as
`conformal-publication-release-audit.json`; the receipt records the exact
audited commit, focused checks, recursively active TeX inputs, and
reference-stable PDF builds.  Papers 7--8 are therefore `ARTIFACT_READY` in
the programme lifecycle, but not yet `SUBMISSION_READY`.

## Still required before submission

1. Freeze a public repository release and archival identifier containing all
   generated inputs, manifests, certificates, and minimal checkers.
2. Obtain independent reviews from conformal/BGG geometry, BV--BFV,
   Lorentzian PDE, and BRST representation theory.  Repository hashes and
   internal mutation tests are not substitutes for those reviews.
3. Independently rederive the large one-particle absolute ranks and the
   central covariant all-row identities.  The new rank-53 checker addresses
   only the smallest two-particle calculation.
4. Decide and state the target journal's policy for computer-assisted proofs,
   artifact review, anonymous code, and supplementary data.

## Evidence commands

```bash
python3 symbolic/verify_conformal_residual_rank53_independent.py
python3 symbolic/verify_conformal_manuscript_claim_discipline.py
python3 symbolic/verify_conformal_split_publications.py
python3 symbolic/verify_conformal_paper_free.py --required --timeout 180
python3 symbolic/verify_conformal_covariant_H4_proof_ledger.py --check --guards
python3 symbolic/update_conformal_paper_snapshot.py --check
python3 symbolic/audit_conformal_publication_release.py --tree-ish HEAD
```

The exhaustive publication rail remains:

```bash
python3 symbolic/verify_conformal_paper_free.py --reproduce --timeout 1800
```
