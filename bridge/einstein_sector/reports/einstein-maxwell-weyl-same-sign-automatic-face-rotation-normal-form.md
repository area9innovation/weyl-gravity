# Automatic-face rotation normal form

The axisymmetric rank-two critical locus is not a hidden definite quadratic
obstruction.  On every nonzero fixed-occupation support stratum of the five
automatic faces, restrict to angular perturbations aligned with the occupied
current eigenlines.  If `N` eigenlines are occupied, the kernel of the two
linear transverse rotation equations has exact real inertia

```text
(positive, negative, null) = (4*N-2, 4*N-2, 2)
```

for the quadratic `mu_J3` form.  The two null directions arise from the
single complex radical left by the null hyperplane constraint in the
`m=+/-1` sector.  The `m=+/-2` sector supplies an explicit hyperbolic block
for every occupied eigenline.

The same exact spin-two calculation also supplies a full-amplitude arc
through every axisymmetric point.
For any occupied node, fix its phase so its `m=0` coefficient is `a>0` and
replace it by

```text
sqrt(a^2-12*t^2) e_0 + t e_(+2) + t e_(-2).
```

The angular norm is unchanged, all three rotation moment maps vanish, and
the automatic resonance remains zero because the absent resonant node stays
zero.  Thus every such axisymmetric point is non-isolated and lies on a
genuinely nonaxisymmetric branch.

This does not classify the full current-orthogonal normal space or its
two-dimensional radical, glue occupation strata, treat candidate 16, or
settle any active resonance component.

Verification on 2026-07-19 passed the producer, independent exact verifier
and three focused tests.  The verifier reconstructs the spin-two form, the
constraint-hyperplane Gram minors and all support-stratum inertia formulas
without importing the producer payload.  The regenerated Einstein atlas
passed its independent verifier and all 94 atlas tests.  Paper 13 compiled in
three `pdflatex` passes with no undefined references, layout warnings or box
warnings.
