# Publication model decision and citation repair

Date: 27 July 2026

## Scope

Editorial and administrative. No scientific claim, lifecycle state,
certificate payload, or theorem is added, removed, promoted, or demoted. No
mathematical operator or shared algebra changed.

## The publication-model decision

The programme publishes as an open GitHub repository. There is no arXiv
submission, no journal submission, no release tag, and no DOI.

The reason is authorship. The manuscripts name GPT-5.6.sol as principal
author and Asger Alstrup Palm as non-technical orchestrator and corresponding
human contact. That is an accurate description of how the work was produced:
the orchestrator states that he wrote none of the mathematics and does not
follow most of it. arXiv and the major journals require a human author who
takes authorship and accountability, and prohibit listing an AI as an author.
The decision is to publish where the honest attribution can stand rather than
restate the attribution to fit a venue.

A DOI was separately declined on the ground that the tree is still too fluid
for an archival snapshot to be worth minting. Release tags were declined for
the same reason: a tag asserts a snapshot worth pointing at. Versions are
fixed by commit hash.

This closes the former release gates as decisions rather than as completed
work. It is recorded so that a future reader does not mistake the absence of
an arXiv ID or a DOI for an oversight.

## Citation repair

The former gate "replace companion-paper citations with arXiv IDs once
public" cannot be satisfied, but the underlying defect was real and is now
fixed: the affected entries were dead references that gave a reader no way to
find the cited manuscript.

| Repair | Count | Where |
| --- | ---: | --- |
| `companion paper, 2026` bibitems given authors, exact titles, paper numbers, in-repo paths, and the repository URL | 22 | Papers 01–06 |
| Unlocated companion bibitem repaired, and its title corrected to Paper VII's actual title | 1 | Paper 08 |
| Unlocated companion bibitem given a path and repository URL | 1 | Paper 11 |
| Abstract reference to "the companion paper" resolved to Paper VII | 1 | Paper 08 |
| Editorial note describing the causal companion as "planned" updated to name it as the published Paper VIII | 1 | 07–08 archive |
| Dangling `paperN-vX.Y` release-tag references replaced by "cite the repository commit hash" | 5 | Papers 01–05 |

Prose uses of the phrase "the companion paper \cite{key}" were left alone:
those keys now resolve.

The dangling tag references in `reports/variational-and-field-theory.md` were
deliberately **not** edited. That is historical record, and history is
repaired by new records rather than rewritten.

## Pre-existing regression found and fixed

`symbolic/verify_conformal_split_publications.py` was **already failing on
`master`** before this pass, and would have failed the conformal publication
release audit.

The authorship-standardization commit `181125aa` (2026-07-14) replaced a long
`\thanks` block with a shorter one. Papers 08 and the 07–08 archive carry a
separate `\section*{Authorship and generated inputs}` and were unaffected, but
Paper 07 and the 07–08 computational supplement carried the disclosure only
inside the replaced `\thanks`, so both silently lost it. The guard requires
the phrase "non-technical"; it had been failing on Paper 07 ever since, which
also masked the identical failure on the supplement.

Both documents now carry the same standardized authorship-disclosure section
as the rest of the series. This was verified to be pre-existing by stashing
this pass's manuscript edits and re-running the guard against `HEAD`, where it
failed identically.

## Receipt

| Check | Command | Result |
| --- | --- | --- |
| Companion-bibitem rewrite | scripted, fail-closed on author/path/URL presence; idempotent on rerun | 22/22 PASS |
| Manuscript builds | two `pdflatex` passes each, `-halt-on-error` | 11/11 PASS |
| Undefined citations | `grep "Citation.*undefined"` over all 11 build logs | 0 |
| PDF integrity | `pdfinfo` page count on all 11 rebuilt PDFs | 11/11 non-zero |
| Paper 11 claim map | `paper/verify_11_gravity_light_claim_map.py` | PASS |
| Conformal editorial guards | `symbolic/verify_conformal_split_publications.py` | ALL PASS (was FAILING at HEAD) |
| Certificate provenance | `symbolic/verify_conformal_certificate_provenance.py` | 11/11 PASS |
| Dangling tag sweep | `grep -rn "paper[0-9]-v[0-9]" paper/*.tex` | NONE remain |
| JSON parse | claim map reparsed after edit | PASS |
| Whitespace | `git diff --check` on scoped paths | PASS |

Paper 11 `\input`s a path relative to the repository root and must be built
from there, not from `paper/`. Building it from `paper/` fails and **deletes
the tracked PDF**; that happened once during this pass and the PDF was
restored from `HEAD` before the correct rebuild. Worth knowing before the next
paper-series build pass.

Verifiers requiring `sympy` must run under the mise Python
(`~/.local/share/mise/installs/python/latest/bin/python3`); the default
`python3` lacks it and fails at import, which is not a pass.

The Paper 11 claim map's `manuscript_sha256` was updated from
`e4ed0a80…5d00cee` to `06c73488…ea91626c` by exact single-occurrence string
replacement, so the diff is one line. No other field changed.

## Higher tiers

Tiers 2 and 3 were not run, and their omission is not a skipped pass. No
mathematical input, shared operator, schema, generated artifact, or
certificate payload changed. The changes are bibliography entries, one
abstract sentence, one editorial note, two restored authorship sections, and
one manuscript hash tracking those edits. The directly affected verifiers —
the Paper 11 claim map and both conformal guards — were run and pass.

## Does not establish

This pass does not make the repository peer reviewed, verify any scientific
claim, resolve the ABHT third-party reference, or complete the
standalone-history replay crosswalk. Those remain open in `TODO.md`.
