# Public front-door refresh — 26 July 2026

## Scope

This receipt covers the release-facing revision of Papers 00, 98, and 99.
The change is editorial and organizational. It does not add or promote a
scientific theorem, lifecycle state, or certificate.

The revision:

- replaces the former twelve-paper chronology in Paper 00 with a concise map
  of the current eighteen-paper technical programme;
- updates Papers 98 and 99 to the Phase-1 synthesis and the Paper 16–17
  Schwarzschild endpoint and resonance results;
- distinguishes the cut-off radial Green pole and isolated local contour
  term from a global retarded waveform theorem;
- marks Paper 18 as a companion scaffold rather than a completed theorem
  paper;
- foregrounds the AI-orchestrated research experiment and its accountability
  boundary;
- reduces the three source documents from approximately 28,500 words to
  6,459 words.

## Tier 0 receipt

| Check | Command | Elapsed | Result |
| --- | --- | ---: | --- |
| Paper 00 build | `pdflatex -interaction=nonstopmode -halt-on-error 00-ghosts-geometry-reality.tex` twice from `paper/` | 0.75 s | PASS |
| Paper 98 build | `pandoc 98-physicist-executive-summary.md --from=gfm --pdf-engine=xelatex -V geometry:margin=0.9in -V fontsize=10pt -V colorlinks=true -V title-meta='Pure-Weyl gravity programme: executive summary for physicists' -V author-meta='GPT-5.6.sol; Asger Alstrup Palm' -o 98-physicist-executive-summary.pdf` | 2.12 s | PASS |
| Paper 99 build | `pandoc 99-how-to-build-a-universe.md --from=gfm --pdf-engine=xelatex -V geometry:margin=0.75in -V fontsize=10pt -V colorlinks=true -V title-meta="Are Weyl Gravity's Ghosts Real?" -V author-meta='GPT-5.6.sol; Asger Alstrup Palm' -o 99-how-to-build-a-universe.pdf` | 2.13 s | PASS |
| Local links | Parse relative Markdown links and require every target to exist | \(11/11\) and \(5/5\) | PASS |
| PDF structure | `pdfinfo` and `pdftotext` on all three PDFs | 9, 5, and 4 pages | PASS |
| Whitespace | `git diff --check` | \(<1\) s | PASS |

The first and last pages were also rendered to PNG and inspected for clipping,
duplicate titles, and over-wide tables. The first Paper 98 draft exposed an
over-wide table; the table was replaced by audience-readable lists before the
final build.

## Final hashes

| Artifact | SHA-256 |
| --- | --- |
| `paper/00-ghosts-geometry-reality.tex` | `1c17a62ab92d377dafb4d197ad7a006a6610670d6d1d508cc407906d3542920e` |
| `paper/00-ghosts-geometry-reality.pdf` | `5674aa1bd1ac8da22627d02b53f97d59fa67d90d8c403f76656742caa4fb199c` |
| `paper/98-physicist-executive-summary.md` | `d8b64ee26bf0a0d0f98466f559d0f9a0c67bba6e16a7b83b947c45b7045e8e6e` |
| `paper/98-physicist-executive-summary.pdf` | `a70cae76e26eb9fe2129561eed809c3a11a8e1693d91126f0d30e1c25fbdb2ff` |
| `paper/99-how-to-build-a-universe.md` | `7c61e134e4366f3e1e6bec4762a7d9dc22a775977d2d5fefd0403585c3c37ed7` |
| `paper/99-how-to-build-a-universe.pdf` | `49c48ee1dd8bb40efed2b8fa6edbe3c91d006aa5073ebeffc06c705f01c4829c` |

## Higher tiers

Tier 1 scientific verifiers and Tier 2–3 certificate chains were not run.
No mathematical input, operator, machine-readable scientific certificate, or
paper theorem was changed. Running the full scientific suite would therefore
not be a relevant falsification test for this editorial release pass.

## Does not establish

This refresh does not independently verify the scientific claims summarized
in the three papers, make the repository peer reviewed, complete Paper 18,
or promote the local Schwarzschild resonance contour to a global causal
ringdown theorem.
