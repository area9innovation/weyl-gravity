# Adaptive Peter--Weyl route preflight

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The `two_j<=4` obstruction fixes the scale of the next calculation.  With
three coframe components and the certified unit bound on every Fourier entry,
the greatest possible retained energy through representation dimension `D`
is

`3 sum_(d=1)^D d^3 = 3[D(D+1)/2]^2`.

The certified profile-energy lower bound is greater than `2.809e8`.  Even the
necessary capacity condition for 99 percent of that lower bound fails at
`D=138` and first passes at `D=139`, or `two_j=138`.  This does not prove that
the actual coefficients below that cutoff carry 99 percent of the energy.

The next supported route is therefore a streamed, symmetry-reduced adaptive
Peter--Weyl contraction using the existing exact finite-block form engine.
The calculation must serialize per-mode detector contractions and tail
witnesses, not millions of dense intermediate matrix entries.  A
physical-space route remains open, but the repository has no validated Berger
hyperbolic solver or error estimator.

No convergence cutoff, infinite tail upper bound, full Green image, massive
image, recoil coefficient, tangent-cone restriction, physical-branch map, or
quantum claim is certified here.
