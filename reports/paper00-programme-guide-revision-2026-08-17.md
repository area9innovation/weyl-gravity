# Paper 00 programme-guide revision — 2026-08-17

## Result

Paper 00 now serves as the thematic guide to the manuscript programme rather
than as a third public synthesis. It routes readers by scientific question,
explains the four claim levels and exact quantum dependency tags, and gives
each headline paper both an intended use and an explicit inference boundary.

The guide covers:

- all 22 headline papers (01–22);
- the two public entrances (98 and 99);
- four computational supplements;
- the combined 07–08 archival manuscript;
- bridge notes 90–92; and
- the interactive Reverse Physics Atlas.

The repository README now identifies Paper 00 as the programme guide, includes
the previously omitted Papers 19–22 in the manuscript table, and states the
current Hadamard boundary precisely: the certified full-complex object is an
indefinite pseudo-state pair, not a positive BRST-compatible state.

## Machine receipt

The content-addressed receipt is
`paper/00-ghosts-geometry-reality-receipt.json`, schema
`paper-00-programme-guide-receipt-v2`, result
`PAPER_00_THEMATIC_PROGRAMME_GUIDE_V2`.

It records 33 resolved local destinations, hashes the source and PDF, and
pins 11 scientific authorities used to police the guide's claim boundaries.
All promotion flags are false. In particular, this navigation revision does
not establish a new theorem, a positive Hadamard state, a Lorentzian QME, a
global black-hole waveform, population-level model selection, or a complete
theory.

Dependency tags carried by the receipt:

```text
LOCAL-ALGEBRAIC
EUCLIDEAN-SPECTRAL
REDUCED-MODE
LORENTZIAN-CAUSAL
```

## Verification

| Tier | Command or inspection | Elapsed | Result |
| --- | --- | ---: | --- |
| 0 | `cd paper && pdflatex -interaction=nonstopmode -halt-on-error 00-ghosts-geometry-reality.tex` (twice) | 2.6 s | PASS; 8-page PDF, no LaTeX, overfull, or underfull warnings |
| 0 | `git diff --check -- README.md paper/00-ghosts-geometry-reality.tex paper/00-ghosts-geometry-reality.pdf paper/00-ghosts-geometry-reality-receipt.json paper/generate_00_timeless_introduction_receipt.py paper/verify_00_timeless_introduction.py` plus PDF stale-language and 22-link checks | 0.2 s | PASS |
| 1 | `python3 paper/generate_00_timeless_introduction_receipt.py --check` | included below | PASS |
| 1 | `python3 paper/verify_00_timeless_introduction.py` | 0.6 s combined with receipt, syntax, and JSON checks | PASS |
| 1 | `python3 -m py_compile paper/generate_00_timeless_introduction_receipt.py paper/verify_00_timeless_introduction.py` and `python3 -m json.tool paper/00-ghosts-geometry-reality-receipt.json` | included above | PASS |
| visual | Rendered all 8 pages; inspected title/contents, thread pages, reading-routes table, evidence path, and final claim boundary | manual | PASS |

Tier 2 was not run because no mathematical input, operator, schema consumed by
a scientific certificate chain, generated scientific artifact, or promoted
claim changed. Tier 3 was not run because this was not a freeze, theorem
promotion, shared-core change, release, or explicit full-suite request.

## Human-readable boundary

Paper 99 explains why the programme matters. Paper 98 gives the compact
physicist-facing synthesis. Paper 00 now answers a different question: where
should a reader go next, and where must each reading route stop?
