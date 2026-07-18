# The `two_j<=4` detector-profile tail obstruction

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The detector radius is `1/128`, so the first five Peter--Weyl representation
dimensions are not a plausible uniform approximation by scale alone.  The
certificate makes this quantitative without assuming coefficient decay.

At either clock center, Parseval and the certified Berger volume convert a
validated lower bound on the normalized one-form profile's `L2` norm into a
total Fourier-energy lower bound above `2.809e8`.  Unitarity and the exact rod
chart bound every retained coefficient by one.  All three coframe components,
all matrix entries and the Peter--Weyl dimension weights through `two_j=4`
therefore contribute at most `3 sum_{d=1}^5 d^3=675`.  More than `0.9999975`
of the clock-center profile energy necessarily lies above the current cutoff.

This is an obstruction to a uniform small-tail theorem at `two_j<=4`, not an
upper bound on the infinite tail.  The next honest route is an adaptive cutoff
near the profile bandwidth or a physical-space Green-chain evaluation.  The
finite-mode advanced Maxwell block remains valid, but it cannot be promoted
to the full image from this cutoff.
