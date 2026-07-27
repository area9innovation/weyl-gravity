# Release gate: repository license and TODO restructure

Date: 27 July 2026

## Scope

This pass is editorial and administrative. It closes one publication release
gate and repairs the working list. It adds, removes, promotes, and demotes no
scientific claim, lifecycle state, certificate, or theorem.

The pass:

- assigns the repository license (CC BY 4.0 for manuscripts, certificates,
  data, and documentation; MIT for code) and installs the full legal texts;
- updates the `README.md` release-status bullet, which previously named the
  missing license as an open gate;
- restructures `TODO.md` back into an open-items list, archiving the
  554-line completed-work log verbatim.

## What was actually open

`TODO.md` had drifted badly. It was last meaningfully revised on 2026-07-14
and described a six-paper programme; the repository now carries Papers 00–18
plus bridges 90–92 and front-door documents 98–99, across 26 authored LaTeX
sources. Item 14 had become a 554-line log of *finished* work inside a file
whose own header declared it held only open items.

Nothing in the repository referenced `TODO.md` except one stale line in
`reports/variational-and-field-theory.md`. Live work coordination is
`planning/work-items/` (445 items). `TODO.md` now says so explicitly and is
scoped to release gates plus the legacy Paper 01–06 backlog.

Three findings changed the release picture:

1. The repository carried **no tags at all**. The tag item as written named
   monorepo-era tags (`paper1-v1.2` … `paper5-v1.1`) for a five-paper series
   that no longer matches the renumbered 00–18 programme. That item is
   recorded as obsolete and replaced by a single repository-wide archive tag
   serving as the DOI anchor.
2. The **missing license was a release gate that `TODO.md` did not track**,
   although `README.md` named it. It is now assigned.
3. The arXiv-citation item is unchanged in substance but was quantified: 31
   `companion paper` citations across nine manuscripts, plus one `to appear`
   reference (ABHT, `paper/03-fourth-order-vacuum.tex:951`).

## Licensing decision

The split is by kind of file, not by directory, because nearly every
directory here mixes executable verifiers with the certificates and prose
they produce. `LICENSE` records the mapping; `LICENSE-MIT.txt` and
`LICENSE-CC-BY-4.0.txt` carry the full texts.

`LICENSE-CC-BY-4.0.txt` is the canonical Creative Commons legal code
retrieved from `https://creativecommons.org/licenses/by/4.0/legalcode.txt`.
Its content was verified word-identical to the retrieved source after a
trailing-blank-line strip.

| Artifact | SHA-256 |
| --- | --- |
| Retrieved CC BY 4.0 legal code (upstream bytes) | `9ba9550ad48438d0836ddab3da480b3b69ffa0aac7b7878b5a0039e7ab429411` |

`LICENSE` also states two boundaries the programme's own discipline requires:
a permissive license is not an endorsement of any claim the licensed file
makes, and it is independent of the claim-lifecycle and dependency-tag scopes
recorded in the manuscripts.

## Tier 0 receipt

| Check | Command | Result |
| --- | --- | --- |
| Whitespace | `git diff --check` on the six scoped paths | PASS |
| License files present | `test -f` on `LICENSE`, `LICENSE-MIT.txt`, `LICENSE-CC-BY-4.0.txt` | 3/3 PASS |
| CC BY text fidelity | `diff` of whitespace-normalized local file against retrieved canonical text | IDENTICAL |
| README local links | Parse relative Markdown links, require each target to exist | 29/29 PASS, 0 missing |
| Archive completeness | `sed -n '63,616p'` of `TODO.md` at `df710e96` transcribed verbatim; `DONE` marker count preserved | 22/22 PASS |

## Higher tiers

Tier 1, 2, and 3 were not run, and their omission is not a skipped pass. No
mathematical input, shared operator, schema, generated artifact, certificate
payload, or paper theorem changed in this pass. No `.tex`, `.py`, `.lean`, or
`.json` file was modified. Running the certificate chains would therefore not
be a falsification test for any changed claim.

## Does not establish

This pass does not make the repository peer reviewed, mint the archival DOI,
create any release tag, post any manuscript to arXiv, resolve the
`companion paper` citations, or complete the standalone-history replay
crosswalk. Those remain open in `TODO.md` items 1–3.

## Concurrent shared-tree activity

This pass started at `df710e96`. The other team committed `85c1ad94`
("Complete global ECS Fredholm realization") to the shared tree while it was
in progress, which landed
`black_hole_programme/phase4/axial_qnm_ecs_fredholm_v1/` and touched
`README.md`.

`README.md` was the only overlapping path. Their edit is the Schwarzschild
row of the current-position table; this pass edits the release-status bullet
list. The two hunks are disjoint. Rather than commit a `README.md` based on
the superseded parent, this pass restored the file from `85c1ad94` and
reapplied its own edit on top, so their Fredholm row is preserved intact. No
other scoped path overlapped.

## Working tree not included

One untracked path was present and was deliberately left untouched, per
shared-master discipline:

- `,` in the repository root — a stray shell script that activates `mise` and
  hard-codes a path to a sibling private `seed-studio` repository and a
  `bp2transformer` tool. **It must not be published**; it is unrelated to this
  programme and leaks a private-repo path. It is not covered by `.gitignore`,
  so it will keep surfacing as untracked until it is deleted or ignored.
