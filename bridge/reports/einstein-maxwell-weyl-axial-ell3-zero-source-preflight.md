# Axial ell=3 zero-frequency source preflight

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The direct four-dimensional source generator has been lifted from the
certified `ell=2` fixture to the axial `ell=3,m=0,k=0` plus, minus, and two
extra-primary representatives.  No coefficient certificate is promoted yet.

The first `extra_e1` replay was stopped after approximately 30 minutes at
full CPU when the uncheckpointed symbolic expansion reached approximately
6.5 GB resident memory.  During that run, an invalid proposed assertion was
also identified: the `Omega!=0` homogeneous left-null relation had been
mistakenly applied to the zero-frequency source.  That assertion has been
removed.  The certified `ell=2` source already demonstrates why the two
relations must remain distinct.

This is a computational preflight failure, not a resonance or extension
counterexample.  The fail-closed status is:

```text
ell=3 direct source coefficient: NOT COMPUTED
all-ell zero-frequency source rank: OPEN
complete all-ell second-order cone: OPEN
```

The next implementation should compute the homogeneous source as the
variation of the arbitrary-`lambda` reduced quadratic action with respect to
the homogeneous background parameters, then use the direct four-dimensional
fixture only as a single optimized audit.  The raw tensor route should be
split into cached curvature, equation-row, and harmonic-projection stages
before it is rerun.

## Verification receipt

Date: 2026-07-17.

* Tier 0: the corrected scaffold compiles.
* Exhaustive direct replay: `STOPPED`, approximately 30 minutes, approximately
  6.5 GB resident memory, no coefficient emitted.
* This stopped rail is not a pass and promotes no source or cone claim.
