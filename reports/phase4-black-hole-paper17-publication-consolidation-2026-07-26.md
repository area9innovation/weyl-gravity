# Paper 17 publication consolidation

Date: 2026-07-26  
Work item: `sf:program/work/phase4-black-hole-paper17-publication-consolidation`  
Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Outcome

Paper 17 is now a theorem-first 15-page manuscript rather than a 54-page
programme document.  Its publication spine contains five results:

1. the exact filtered RW/RW/Maxwell system and non-split spin-two
   self-extension;
2. the mass-direction cocycle normal form and endpoint-compatible
   critical-mass jet;
3. the validated defective QNM and its non-Einstein generalized root;
4. the nonzero rank-one exterior cut-off Green double pole;
5. nonannihilation by exact null-infinity reconstruction and by an explicit
   conserved, traceless compact odd source.

The manuscript now separates exact, validated, and open statements in a
single dependency table.  The abstract, introduction, conclusion, and
certificate table follow the same five-result order.

## Scientific compression

The previous draft contained 4,569 lines, 15,754 words, and 54 PDF pages.
The consolidated manuscript contains 1,160 lines, 4,049 words, and 15 PDF
pages.

The following correct but nonessential programme material was removed from
the publication manuscript:

- the all-multipole static threshold classification;
- QNM acceleration, higher mass jets, and spectral-flow sum rules;
- the generic two-parameter exceptional-point unfolding;
- pseudospectral, positive-metric, and Krein-limit consequences;
- detector templates and coherent-forcing calculations.

These results remain preserved in git history and their source certificates.
They are candidates for a spectral-kinematics or critical-response follow-up,
not proof dependencies of the present paper.

## Claim boundary

The retained strongest result is a compact-source, compact-observation
meromorphic radial Green pole on the Schwarzschild exterior.  The paper does
not promote this to a `LORENTZIAN-CAUSAL` theorem.

The following remain fail-closed:

- a closed global causal exterior resolvent;
- a complete retarded QNM expansion or late-time theorem;
- standard asymptotic-flatness falloff for the time-independent generalized
  component;
- excitation by a specified astrophysical matter trajectory;
- detector sensitivity or parameter-estimation claims;
- all-multipole Bach nonsplitting;
- quantum positivity, unitarity, or no-go claims.

The author line was changed from computational-system names to
`Authors withheld for review`.

## Reproducibility surface

The claim-map producer, verifier, and mutation suite were rewritten to bind
only the retained publication spine.  The verifier:

- pins the manuscript and ten authority certificates by SHA-256;
- independently re-derives the Bach cocycle normal form;
- checks the factor-of-two triangular gauge and the Coulomb cancellation;
- audits the Smith/root and Green-residue formulas;
- checks the exact null-infinity leading ratios;
- re-derives the conserved-source radial identity;
- imports the decisive exact and validated authority flags;
- rejects causal, source-specific, detector, and generalized-falloff
  promotions;
- rejects reintroduction of the removed programme sections.

## Verification

Passed:

- Python parse checks for the claim-map producer, verifier, and tests;
- generated claim map freshness;
- independent Paper 17 verifier;
- 11 Paper 17 mutation/regression tests;
- conserved-source verifier and 5 tests;
- null-infinity reconstruction verifier and 5 tests;
- finite-interval Fredholm promotion verifier and 6 tests;
- critical-mass parent verifier and 5 tests;
- projective-cocycle verifier and 8 tests;
- full Evans winding verifier and 4 tests;
- local selector verifier and 3 tests;
- spin-one local-unit verifier and 5 tests;
- two-pass `pdflatex` build;
- visual inspection of the abstract, claim table, open-problem section, and
  certificate table;
- scoped `git diff --check`.

Two package-relative verifiers were initially invoked as file paths and
correctly refused their relative imports.  They were rerun successfully with
`python3 -m ...`; this invocation correction is not counted as a scientific
failure or pass.

Tier 3 was not run: no source operator, certificate schema, shared algebra, or
scientific lifecycle state changed, and no new theorem was promoted.  The
affected publication and authority chain was replayed directly.

## Artifact hashes

- manuscript:
  `ad24d9ab328102688a07dddeb4296313861072983c840649fd5b689de81f9914`
- PDF:
  `5b7335cdd264f1d7d25b2354d94641bcab20e786babc769aab7a2ed7fbac13c0`
- claim map:
  `756065db4062102fe3c3cc3573451eea7be5db9a3adaacbe191ce523843026c1`
- claim-map producer:
  `8aae450969975b3e5cacab35f54dbce00f9b848c74b5ee672e62d660a084ae84`
- independent verifier:
  `a09c4c87ff060260bc1b04a870c8dbfd7c0fe1f9481535962ccd3288df385fbe`
- mutation suite:
  `660109e275fd18f5d06272c1574c5cb86ba3158ba65467d2e5a463d785ea3af7`

CLOSE-OUT: DONE — Paper 17 is a concise, audited five-result manuscript with
the causal and physical-source boundaries preserved.

EVIDENCE:
`paper/17-pure-weyl-schwarzschild-extension-structure-claim-map.json`
