# Papers 98–99 timeless-synthesis revision — 2026-08-17

## Purpose

The public-facing papers had accurate scientific content but retained the
shape of a programme update. Paper 98 used an established/partial/open
inventory, a chronological paper map, and a list of next questions. Paper 99
ended with a public scorecard and included temporal phrases such as “more
recently” and “latest.”

This revision separates two genres:

- Papers 98 and 99 present durable arguments, examples, and conclusions.
- Reports and machine-readable receipts retain chronology, artifact history,
  and verification status.

No scientific certificate, matrix grade, dependency boundary, or quantum
lifecycle state changed.

## Editorial result

Paper 98 is organized around:

1. a typed judgement separating logic, existence assumptions, mathematical
   carriers, physical premises, and obligations;
2. an obligation ladder covering algebraic/classical, nonlinear/quantum,
   propagation/empirical, and foundation/composition questions;
3. five thematic case studies;
4. the scientific consequences for positivity, interface composition,
   empirical robustness, and changes of foundation.

The status inventory became an argument about why evidence does not climb
automatically between obligations. The chronological paper map became a
thematic guide to supporting arguments. The roadmap became a synthesis of
three recurring forks in theory construction.

Paper 99 retains its central general-audience thesis—“a theory is a stack, not
an equation”—but replaces its scorecard with an explanation of what the
examples collectively establish. Temporal release language was removed.

## Machine-readable receipt

`paper/98-99-public-front-door-receipt.json` was regenerated as
`PUBLIC_FRONT_DOOR_98_99_TIMELESS_SYNTHESIS_V3`. It content-addresses the two
Markdown sources, both PDFs, and nine scientific authorities. Twelve stale or
changelog-style fragments are rejected explicitly, including the former paper
map, next-questions, scorecard, pre-release, and recent/latest language.

All scientific-promotion flags remain false. In particular, the receipt does
not establish a new theorem, matrix-cell promotion, complete theory, positive
Hadamard state, population-level empirical result, or Lorentzian QME.

## Verification

### Tier 0 — PASS

- Both Python audit sources compile.
- The JSON receipt parses.
- All local Markdown links resolve.
- `git diff --check` passes on the scoped paths.
- PDF title, author, and page metadata were inspected.
- The first and final page of each PDF were visually inspected without
  finding clipping, overlap, or malformed headings.

Render results:

- Paper 98: 5 pages.
- Paper 99: 4 pages.

### Tier 1 — PASS

```text
python3 paper/generate_98_99_public_front_door_receipt.py --check
Papers 98–99 public-front-door receipt: PASS

python3 paper/verify_98_99_public_front_doors.py
Papers 98–99 independent public-front-door audit: PASS
```

The independent rail checks artifact and authority hashes, exact atlas and
passport counts, selected empirical values, the strict Lorentzian frontier,
the BT scope boundary, required synthesis sections, and the absence of the
former changelog-style headings.

### Tier 2 — not triggered

No mathematical input, shared operator, certificate schema, or generated
scientific result changed. The authorities were checked by content hash and
exact field assertions.

### Tier 3 — not triggered

This is an editorial restructuring of public papers, not a freeze, scientific
promotion, shared-core change, release, or explicit full-suite request.

## Files in scope

- `paper/98-physicist-executive-summary.md`
- `paper/98-physicist-executive-summary.pdf`
- `paper/99-how-to-build-a-universe.md`
- `paper/99-how-to-build-a-universe.pdf`
- `paper/98-99-public-front-door-receipt.json`
- `paper/generate_98_99_public_front_door_receipt.py`
- `paper/verify_98_99_public_front_doors.py`
- this report
