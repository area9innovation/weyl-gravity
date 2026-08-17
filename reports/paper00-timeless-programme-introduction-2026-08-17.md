# Paper 00 timeless programme introduction — 2026-08-17

## Outcome

Paper 00 was rewritten as a durable conceptual introduction rather than a
programme update. The former pre-release label, “newest results” framing,
first-six-papers chronology, paper map, open-work roadmap, and current-verdict
box were removed.

The paper's organizing claim is that “ghost” denotes at least four different
objects: a local solution, a gauge-reduced classical direction, a nonlinearly
continuable direction, and a state or particle in a positive quantum theory.
Those objects are placed on an obligation ladder whose conclusions depend on
physical postulates, mathematical carriers, logic and existence assumptions,
operational bridges, and empirical tests.

The examples are thematic rather than chronological:

- Pais–Uhlenbeck completion and interaction obstructions;
- pure-Weyl residual cohomology and compact classical tests;
- the immutable classical import gate, local anomaly, and full-complex
  BRST–Hadamard pseudo-state boundary;
- Schwarzschild endpoint non-selection and defective response;
- the Mannheim solution/interpretation/data distinction;
- the Bateman–Turok deterministic counterfamily;
- the reverse-foundations atlas, assemblies, passports, and proof surfaces.

The repository navigation description for Paper 00 was updated accordingly.

## Scientific boundary

This is an expository synthesis, not a scientific promotion. It does not
establish a positive full-BV state, Lorentzian QME, global black-hole waveform,
population-level galactic verdict, continuum Bateman–Turok reconstruction,
matrix-cell promotion, or complete theory.

The residual classes `[W_+^2]` and `[W_-^2]` remain deformation/vertex classes,
not one-particle gravitons. The 386-row Lorentzian object remains an indefinite
pseudo-state pair rather than a positive state. Euclidean, reduced-mode, and
Lorentzian-causal claims remain on separate dependency rails.

## Machine-readable receipt

`paper/00-ghosts-geometry-reality-receipt.json` records:

- SHA-256 hashes of the LaTeX source and PDF;
- eleven content-addressed scientific authorities;
- all sixteen resolved bibliography keys and six resolved local links;
- exact atlas, passport, empirical, anomaly, Hadamard, BT, and black-hole
  assertions used by the introduction;
- ten rejected changelog fragments;
- seven false scientific-promotion flags and explicit nonclaims.

The independent audit is `paper/verify_00_timeless_introduction.py`.

## Verification

### Tier 0 — PASS

Build command, run twice from `paper/`:

```text
pdflatex -interaction=nonstopmode -halt-on-error 00-ghosts-geometry-reality.tex
```

- The second build contains no LaTeX warnings, undefined citations, overfull
  boxes, or underfull boxes.
- PDF metadata contains the intended title, subject, and three authors.
- The PDF has 10 pages.
- The first page, contents page, representative black-hole/data page, and
  final page were visually inspected without clipping or overlap.
- All local PDF/site links and bibliography keys resolve.
- Both Python audit sources compile and the receipt parses as JSON.
- `git diff --check` passes on the scoped change.

### Tier 1 — PASS

```text
python3 paper/generate_00_timeless_introduction_receipt.py --check
Paper 00 timeless-introduction receipt: PASS

python3 paper/verify_00_timeless_introduction.py
Paper 00 independent timeless-introduction audit: PASS
```

### Tier 2 — not triggered

No mathematical input, shared operator, certificate schema, or generated
scientific result changed. Existing authorities were checked by content hash
and exact field assertions rather than rebuilt.

### Tier 3 — not triggered

This is an editorial synthesis and navigation change, not a freeze, theorem
or lifecycle promotion, shared-core change, release, or explicit full-suite
request.

## Files in scope

- `README.md`
- `paper/00-ghosts-geometry-reality.tex`
- `paper/00-ghosts-geometry-reality.pdf`
- `paper/00-ghosts-geometry-reality-receipt.json`
- `paper/generate_00_timeless_introduction_receipt.py`
- `paper/verify_00_timeless_introduction.py`
- this report
