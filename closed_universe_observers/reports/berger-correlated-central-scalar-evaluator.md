# Correlated central scalar evaluator

For an even representation `two_j=2j`, the central diagonal coefficient is
exactly

`D^(j)_(0,0) = P_j(1-2 y_perp^2)`.

Expanding this Legendre polynomial gives coefficients
`(-1)^k C(j,k) C(j+k,k)`.  On the fixed radius-`1/128` support the resulting
series is geometrically controlled, so validated radial, clock and exact
angular moments can be combined without the catastrophic cancellation of the
general independent-moment polynomial.

All 70 central even `p=0` intervals through `two_j=138` overlap the published
scalar stream.  The new interval width at `two_j=256` is below `0.001`, and
the exploratory central rail remains below width `0.1` through
`two_j=2048`.

This is the stable seed, not the full profile evaluator.  Noncentral
diagonals, odd representations and clock powers `p=2,...,28` remain open and
must be handled before widening the polarized form rail or certifying an
infinite tail.
