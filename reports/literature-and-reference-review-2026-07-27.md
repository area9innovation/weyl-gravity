# Literature and reference review

Date: 27 July 2026

## Scope

A systematic pass over every bibliography in `paper/`: verify that cited works
exist and are cited correctly, and add resolvable links where reasonable. No
scientific claim, lifecycle state, certificate payload, or theorem changes. The
only manuscript edits are bibliography entries.

This is the generalisation of the ABHT spot-check: rather than argue about
whether one suspicious reference was fabricated, check all of them against
independent registries.

## Link coverage

| | Before | After |
| --- | ---: | ---: |
| Bibliography entries | 353 | 353 |
| Carrying a DOI/arXiv/URL | 230 (65%) | **330 (93%)** |
| Unlinked | 123 | 23 |

98 DOI links were inserted across 17 manuscripts, covering 73 unique works
(references repeat across papers). Style follows the convention already used
in Paper 17: `\href{https://doi.org/X}{doi:X}`.

## Method, and why it is trustworthy

DOIs were resolved against the **CrossRef REST API**, never from memory. A
proposal was accepted only when the CrossRef record independently agreed with
the reference on title (≥0.90 similarity), year, and — when the reference
states them — volume and first page. 95 unique unlinked references were
queried; 75 met the bar.

Those 75 were then **type-checked**, because a strict title match is not
sufficient: a book and its published review share a title. Two matches were
rejected on that basis:

| Reference | Bad match | What it actually is |
| --- | --- | --- |
| Azizov & Iokhvidov, *Linear Operators in Spaces with an Indefinite Metric* (Wiley, 1989) | `10.1016/0378-4754(91)90047-7` | a 1991 review in *Mathematics and Computers in Simulation* |
| Weinberg, *The Quantum Theory of Fields, Vol. I* (CUP, 1995) | `10.1063/1.2808256` | a *Physics Today* book review |

Final accepted set: **73 works**. The remaining 22 unresolved are genuinely
unresolvable or out of scope: forthcoming papers (ABHT), historical works
predating DOI assignment (Ostrogradsky 1850, Keldysh 1951, von Neumann 1939),
books with no CrossRef DOI, and entries that state no title to match on.

## Existing arXiv identifiers: 114 of 115 correct

Every arXiv id already present was fetched from the arXiv API and its real
title compared against the citing bibitem. **106 matched outright; 8 more were
confirmed correct by inspection** after the automated comparison mis-read the
journal name as the title in manuscripts using the ``Title'' + `\emph{Journal}`
style.

**One is genuinely wrong, and is fixed here.**

`paper/07-conformal-residual-cohomology-krein.tex`, entry
`AltasTekinLinearization`, cited:

- title "Linearization instability for generic gravity in AdS"
- Phys. Rev. D **97** (2018) **124017**
- arXiv:**1804.05602**

arXiv:1804.05602 is Altaş and Tekin, *Linearization Instability of Chiral
Gravity*, Phys. Rev. D **97**, 124068 — a **different paper by the same
authors**. The work actually named is arXiv:**1705.10234**, Phys. Rev. D
**97**, 024028. Both the identifier and the page number had been taken from
the neighbouring paper.

The same reference is cited correctly in
`07-08-conformal-residual-cohomology-archive.tex` and
`13-compact-weyl-maxwell-second-order-tangent-cone.tex`, so this was a
transcription slip introduced when Paper 07 was split out of the archive, not
a fabricated citation.

## Companion manuscripts given locators

`13-compact-weyl-maxwell-second-order-tangent-cone.tex` still cited `Paper10`
and `Paper91` as bare "companion manuscript, 2026". Both now carry the
programme number, in-repo path, and repository URL, matching the convention
applied to Papers 01–06 earlier today.

## Finding: 11 entries state no title

These give only author, journal, volume, and page, so a reader cannot tell
what is being cited without resolving the volume by hand, and no automated
check can validate them:

`02:BM2008PRL`, `02:BM2008PRD`, `03:BM2008PRL`, `03:Mostafazadeh2010`,
`03:vN1939`, `03:Holdom`, `04:Stelle`, `04:Holdom`, `04:Riegert`,
`17:stucker2024`, `17:gajicwarnick2024`.

Every one of them is cited *with* a full title elsewhere in the series, so the
information exists; these entries are abbreviated. Supplying the titles is an
editorial pass, recorded in `TODO.md` rather than guessed at here.

## Receipt

| Check | Command | Result |
| --- | --- | --- |
| DOI resolution | CrossRef REST API, strict title+year+volume+page agreement | 75/95 matched |
| Book-vs-review type check | CrossRef `type` field against reference kind | 2 rejected |
| arXiv verification | arXiv API, real title vs citing bibitem | 114/115 correct, 1 fixed |
| Manuscript builds | two `pdflatex` passes each, `-halt-on-error` | 19/19 PASS |
| Undefined citations | `grep "Citation.*undefined"` over all build logs | 0 |
| PDF integrity | `pdfinfo` on every rebuilt PDF | 18/18 |
| Claim-map pins | recompute every `path`/`sha256` pin in `paper/*.json` | 0 stale |
| Claim-map verifiers | Papers 10, 11, 12, 14, 15, 16, 17, 18 | 8/8 PASS |
| Conformal guards | `symbolic/verify_conformal_split_publications.py` | PASS |
| Whitespace | `git diff --check` | PASS |

## Regression caused and repaired in this pass

Editing 17 manuscripts invalidated manuscript-hash pins that several claim
maps and one planning overlay bind. Verifiers for Papers 10, 12, 14, 15 and 16
passed at `HEAD` and failed after the edit; all were restored by regenerating
the claim maps through their own generator scripts and updating the
`paper10-polar-extra-publication-boundary-repair-2026-07-22.json` materiality
hashes. Paper 09's manuscript pin was likewise updated.

This is recorded because it is a standing hazard: **a bibliography-only edit
silently breaks five certificate rails**, and the failure surfaces only when
the verifiers are run. Any future manuscript touch-up must re-run the
claim-map generators.

## Pre-existing failure, not repaired

`paper/verify_09_relational_clocks_claim_map.py` still fails, and failed at
`HEAD` before this pass, on

```
import hash drift: planning/events/observer-phase1-relational-observable-
disposition-synthesis-DONE-4623f01f99cc5526.json
```

This is the same supersession family already recorded as `TODO.md` item 3 —
an input changed and the dependents were never revisited. Its manuscript pin
was updated so that this pass does not compound the drift, but the underlying
import drift is a scientific question and is deliberately left open.

## Does not establish

This review does not verify that any cited work supports the claim it is
attached to — only that the work exists and is identified correctly. It does
not resolve the 54 uncited bibitems, does not supply the 11 missing titles,
and does not check the 230 links that were already present for anything beyond
arXiv-id correctness (existing DOIs were not re-resolved).
