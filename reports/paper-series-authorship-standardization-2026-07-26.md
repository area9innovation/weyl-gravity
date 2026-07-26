# Paper-series authorship standardization — 26 July 2026

## Outcome

All 24 authored LaTeX documents in `paper/` now use a common programme
authorship presentation.

- Paper 00 names GPT-5.6.sol, Claude Fable 5, and Asger Alstrup Palm.
- The other 23 papers, supplements, and archives name GPT-5.6.sol and Asger
  Alstrup Palm.
- Asger Alstrup Palm is identified as programme orchestrator, corresponding
  human contact, and Honorary Professor at DTU Compute, Technical University
  of Denmark.
- Claude Fable 5 is retained only on Paper 00, where Claude participated.
- The stale Paper 10 bibliography attribution in Paper 13 was corrected to
  match the current Paper 10 authorship.

This is a documentation-only `LOCAL-ALGEBRAIC` change. It changes no theorem,
equation, certificate conclusion, dependency tag, or lifecycle state.

## Verification

The complete source audit found exactly 24 `\author` blocks: 23 common
GPT-5.6.sol/Asger blocks and one Paper 00 GPT-5.6.sol/Claude/Asger block.
First-page PDF extraction confirmed the same names in all 24 compiled
artifacts. Title-page raster inspection was also performed for Papers 00 and
17.

All 24 documents compiled successfully with three `pdflatex` passes. Papers
11 and 12's computational supplement were compiled from the repository root
because their declared `\input{paper/...}` paths require that working
directory. The initial `latexmk` attempt was rejected because `latexmk` is
not installed; it is recorded as an unsuccessful tool-discovery attempt, not
as a test pass.

Manuscript-bound hashes were refreshed for Papers 09, 10, 11, 12, 14, 15,
16, and 17. The Paper 09, 10, 11, 12, 13/14, 14, 16, and 17 verification
rails pass. The Paper 14, 16, and 17 mutation suites also pass; Paper 17
passes all 15 consolidated tests.

Paper 15's generated claim map is current and its standardized author block
passes the exact series audit. Its full legacy verifier proceeds past the
author check and then rejects because it requires the exact phrase
`does not establish a globally populated negative scattering`, which is
absent from both the pre-edit `HEAD` manuscript and the current manuscript.
That pre-existing scientific-scope drift was not repaired under this
authorship-only work item.

## Claim boundary

This work establishes consistent public attribution and buildable publication
artifacts. It does not establish publication-policy compliance, human
technical authorship, journal eligibility, or any new scientific claim.

CLOSE-OUT: DONE — The 24 authored papers now carry the declared consistent programme attribution, all publication PDFs compile, and affected manuscript provenance is refreshed.

EVIDENCE: `reports/PAPER_SERIES_AUTHORSHIP_STANDARDIZATION_TIER_RECEIPT.json`
