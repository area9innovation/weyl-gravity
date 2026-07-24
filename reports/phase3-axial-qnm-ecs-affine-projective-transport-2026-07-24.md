# Phase 3 axial QNM: affine projective transport to r=32

The outgoing reduced-amplitude initializer now advances across every one of
the 16 QNM contour panels to the fixed radius `r=32`.

The rail uses a midpoint reference Taylor trajectory recentered after every
step and simultaneous zero-centered radii for the shared frequency
dependence of `q`, `eta`, and `xi`.  Its essential improvement is the
backward scalar logarithmic norm of the Riccati linearization.  This removes
the artificial absolute-norm growth that stopped the rectangular rail near
`r=40`.

The calculation continues inward beyond `r=32` and then fails closed when
the q-remainder Riccati discriminant becomes nonpositive.  The
panel-dependent first obstruction is materialized in `affine-run.json`.
The omega-sensitivity enclosure is already broad at `r=32`; it is certified
but not yet adequate for a two-sided simple-root gate.

No Evans zero, root count, QNM, Smith fibre, or EP2 is claimed.
