# Intersection-cube literature expansion

`FOUNDATIONAL_INTERSECTION_CUBE_EXPANSION_V1` adds 103 new coordinates to the
previous 59-cell assessed set.  The resulting cube deliberately classifies
162 of 216 coordinates, exactly 75.0% of the Cartesian product.

The additions are 19 bounded local results, 42 literature results, and 42 pieces-only
assessments.  No new priority-gap row was needed to reach the
threshold: the selection rule preferred stronger evidence first.  Across the
whole cube there are now 43 local results, 55 literature results, 47
pieces-only cells, 17 explicit priority gaps, and 54 not-mapped cells.

## Method

The generator declares, for each mathematical-regime/carrier pair, which of
the six physical obligations the reviewed sources address directly.  A direct
primary theorem or construction is a literature result.  A bounded repository
certificate is a local result.  Sources that live on the right axes but do not
compose at the requested intersection are pieces only.  A reviewed meaningful
miss is a priority gap.  “Not mapped” remains an unreviewed coordinate.

The 103 additions are chosen deterministically: evidence strength first, then
interaction/gauge/dynamics leverage, then the previously underexposed
mathematical regime.  Every cell stores source identifiers, a finding, and two
transfer boundaries.  The expansion can be reproduced with:

```text
python3 foundations/expand_intersection_cube.py --rebuild --write
python3 foundations/verify_intersection_cube_expansion.py
python3 -m unittest foundations.tests.test_intersection_cube_expansion
```

## What changed in the overview

Classical-standard and finite/discrete work are now nearly saturated as a map:
35 and 34 of their 36 coordinates have been assessed.  This does not mean the
programmes are solved.  It means a reader can now see whether a coordinate has
a bounded local witness, a direct source, only separate ingredients, or a
specified gap.

The topos and constructive slices changed most qualitatively.  Internal state
measures and contextual entropy fill state/reconstruction cells; internal
one-parameter groups fill a genuine dynamics cell but not spacetime causal
propagation; constructive/effective spectral results fill Hilbert cells while
the Pour-El-Richards example records a serious computability obstruction for
wave evolution.

Weak arithmetic remains the thinnest slice: only 15 of 36 cells are assessed,
and most non-finite entries are pieces or gaps.  This is not accidental noise.
The literature often proves a theorem in standard, constructive, choice-free,
or topos mathematics without reversing the coded theorem over a common weak
base.  That interface is now the clearest underexposed area.

## Surprises and boundaries

The strongest positive surprise is that “non-Hilbert” is not one alternative.
Algebraic C*-systems, Krein carriers, categorical semantics, and localic/topos
objects solve different obligations.  State representation is relatively
well-developed in algebraic and topos settings, while physical state selection
remains open.  Internal group dynamics is much better developed than internal
causal PDE or BV renormalization.

The finite exact witness also shows that interactions need not wait for a
continuum theory: an entangling interaction and its probabilities can be
certified over Gaussian rationals.  But the combined cube heading still does
not establish counterterms, renormalization, or QME restoration.

A `PIECES_ONLY` cell is deliberately not a theorem assembled from its sources.
A `PRIORITY_GAP` is not a literature-absence claim beyond the reviewed corpus.
Nothing in this expansion establishes a weakest base, a controlled continuum
limit, or a new `LORENTZIAN-CAUSAL` result.
