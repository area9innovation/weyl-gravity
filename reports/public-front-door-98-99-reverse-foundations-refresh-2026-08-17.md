# Papers 98–99 public-front-door refresh — 2026-08-17

## Outcome

Papers 98 and 99 were rebuilt as the programme's current public front doors.
Paper 98 now gives physicists a compact map from the certified classical
BV–BFV base through the quantum dependency boundary, empirical comparison,
Bateman–Turok counterfamily, and reverse-foundations atlas. Paper 99 now
introduces the same programme to a general audience through the idea that a
physical theory is a stack of physical, mathematical, and logical choices.

The refresh also updates the repository `README.md` labels and generates new
PDFs. The papers point readers to the interactive foundations atlas and to
Papers 19–22 rather than stopping at the older resonance-centred narrative.

This is a navigation and exposition result. It does **not** promote a matrix
cell, select a complete theory, establish a positive Hadamard state, restore a
Lorentzian QME, or create a new scientific theorem.

## Claims and boundaries checked

- The completion atlas is described as 6 foundations × 6 carriers × 16
  obligations = 576 coordinates, not 576 complete theories.
- The atlas contains nine programme prototypes; their coverage envelopes are
  not presented as rankings or proofs that their cells compose.
- The end-to-end view contains eight passports across six stages.
- The two Lean 4.32/Physlib demonstrations are described as proof passports,
  not as sources of missing physical premises.
- The strict 386-row Lorentzian construction is called a BRST-compatible
  Hadamard two-point **pseudo-state pair**, not a positive state.
- `[W_+^2]` and `[W_-^2]` remain deformation/vertex classes, not one-particle
  graviton states.
- The Mannheim, Newtonian-baryon, and GR+NFW NGC 3198 outcomes retain the
  bounded common-protocol scope and do not become population-level verdicts.
- The Bateman–Turok result remains a deterministic finite-volume Euclidean
  counterfamily and is not transferred to a Lorentzian or continuum claim.

The machine-readable receipt pins every imported authority and every rendered
artifact by SHA-256:

- `paper/98-99-public-front-door-receipt.json`

Independent audit entry point:

- `python3 paper/verify_98_99_public_front_doors.py`

## Build and verification receipt

The PDFs were built with:

```text
pandoc paper/98-physicist-executive-summary.md --from=gfm --pdf-engine=xelatex -V geometry:margin=0.9in -V fontsize=10pt -V colorlinks=true -V title-meta='Reverse Physics and Pure-Weyl Gravity: Executive Summary for Physicists' -V author-meta='GPT-5.6.sol; Asger Alstrup Palm' -o paper/98-physicist-executive-summary.pdf
pandoc paper/99-how-to-build-a-universe.md --from=gfm --pdf-engine=xelatex -V geometry:margin=0.75in -V fontsize=10pt -V colorlinks=true -V title-meta='How to Build a Universe: Physics, Mathematics, Logic—and Research in the Age of AI' -V author-meta='GPT-5.6.sol; Asger Alstrup Palm' -o paper/99-how-to-build-a-universe.pdf
```

Observed render results:

- Paper 98: 5 pages; title and author metadata present.
- Paper 99: 4 pages; title and author metadata present.
- First and final pages of both PDFs were visually inspected; no clipping or
  overlapping text was observed.
- All nine local Markdown links resolve: five in Paper 98 and four in Paper 99.

### Tier 0 — PASS

- Python sources compile.
- The JSON receipt parses.
- `git diff --check` passes on the scoped change.
- PDF metadata, page counts, extracted text, and local links were inspected.

### Tier 1 — PASS

```text
python3 paper/generate_98_99_public_front_door_receipt.py --check
Papers 98–99 public-front-door receipt: PASS

python3 paper/verify_98_99_public_front_doors.py
Papers 98–99 independent public-front-door audit: PASS
```

The independent verifier re-hashes the papers, PDFs, and scientific
authorities; checks the atlas/passport counts and selected exact empirical
values; rejects stale or boundary-crossing prose; and requires every
scientific-promotion flag to remain false.

### Tier 2 — not triggered

No mathematical input, shared operator, certificate schema, or generated
scientific artifact changed. Existing scientific authorities were therefore
checked by content hash and exact field assertions rather than rebuilt.

### Tier 3 — not triggered

This change is an editorial navigation refresh, not a freeze, theorem
promotion, shared-core change, release, or explicit full-suite request.

## Files in scope

- `README.md`
- `paper/98-physicist-executive-summary.md`
- `paper/98-physicist-executive-summary.pdf`
- `paper/99-how-to-build-a-universe.md`
- `paper/99-how-to-build-a-universe.pdf`
- `paper/98-99-public-front-door-receipt.json`
- `paper/generate_98_99_public_front_door_receipt.py`
- `paper/verify_98_99_public_front_doors.py`
- this report
