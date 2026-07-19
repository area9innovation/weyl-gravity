# Berger recoil `two_j=5` all-channel-column binding

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The first omitted direct carrier is now consumed by the cell-partitioned
feedback backend.  All eight `I_abc[5,k]` channel families are evaluated for
all six passive columns `k=0,...,5`: 48 complex coefficient blocks in total.
Strict support ordering makes the 24 blocks in `I_001`, `I_010`, `I_011` and
`I_110` exact zeros.  The other 24 use the matched, D1-on-h0, or h0-to-h1
causal paths as appropriate.
All 24 causally allowed rectangles still contain zero, so no sign or
nonvanishing claim follows.

The base evaluation uses two cells and rigorous 96-bit dyadic outward
rounding on the validation mass-squared intervals `[1,2]`.  A four-cell
`k=0` sentinel proves strict real- and imaginary-width contraction for each of
the four causally allowed paths.  Outward
rounding is optional in the backend and defaults off, so older exact-rational
certificates are unchanged.  The new batch callable reuses three advanced and
three retarded intermediates per column rather than recomputing eight complete
pipelines.

For each detector/source pair, the two feedback-channel arrays now contain
exactly six passive columns, which is the input shape required by the existing
exact shell aggregator.  Couplings are deliberately absent, so this result
does not form a shell scalar or choose physical parameters.  It remains one
finite shell, has `NO_CERTIFIED_MAP` to the separate hashed exact-`T` stream,
and does not close the all-shell tail, quotient, tangent cone, Bridge 3 or any
quantum claim.
