# Paper 7 major-revision response ledger

This ledger records the response to the first external-style mathematical
review of `paper/conformal-residual-cohomology.tex`.  It distinguishes edits
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
specified in `notes/conformal-paper-split-roadmap.md`.  The current monolith
remains the archival theorem source until both article extractions compile,
have independent manifests, and pass their own claim ledgers.  This avoids a
cosmetic split that silently breaks cross-references or certificate scope.

## Still required before submission

1. Extract and independently build Papers A and B and the supplement; the
   roadmap alone is not the requested final split.
2. Replace anonymous-review authorship with final author names,
   affiliations, contribution statements, and responsibility for the
   computer-assisted proofs.
3. Freeze a public repository release and archival identifier containing all
   generated inputs, manifests, certificates, and minimal checkers.
4. Obtain independent reviews from conformal/BGG geometry, BV--BFV,
   Lorentzian PDE, and BRST representation theory.  Repository hashes and
   internal mutation tests are not substitutes for those reviews.
5. Independently rederive the large one-particle absolute ranks and the
   central covariant all-row identities.  The new rank-53 checker addresses
   only the smallest two-particle calculation.
6. Decide and state the target journal's policy for computer-assisted proofs,
   artifact review, anonymous code, and supplementary data.

## Evidence commands

```bash
python3 symbolic/verify_conformal_residual_rank53_independent.py
python3 symbolic/verify_conformal_manuscript_claim_discipline.py
python3 symbolic/verify_conformal_paper_free.py --required --timeout 180
python3 symbolic/verify_conformal_covariant_H4_proof_ledger.py --check --guards
python3 symbolic/update_conformal_paper_snapshot.py --check
```

The exhaustive publication rail remains:

```bash
python3 symbolic/verify_conformal_paper_free.py --reproduce --timeout 1800
```
