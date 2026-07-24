# Bplus4 correlated transport report

## Bounded result

The common-moving `R/S` checkpoint was merged into one two-column
dual-number state.  The `R` spin-one rows and both exact spin-one tangent
columns are structurally zero.  The scalar analytic unit `h0` remains typed
and is not Taylor-expanded.

One validated panel from `r=31` to `r=247/8` passes with:

- frequency generator: `7315`;
- radial step: `-1/8`;
- coefficient box radius: `1/16`;
- exponential order: `96`;
- tail enclosure: `0.007426513552203137`;
- maximum joint width: `1.78453621449834`.

The dual-number series was compared against an independently expanded direct
sixteen-state series.  Their exact Taylor coefficients agree, and the
interval difference contains zero.  Rank three is preserved because all
columns undergo the same invertible radial flow and `h0` is zero-free.

## Diagnosis

Lower-order large-step trials suffered rapid tail wrapping.  Increasing the
exponential order makes an individual `1/8` panel bounded, so this is not a
scientific or algebraic refusal.

The first remaining obstruction is throughput: expanding the direct
sixteen-state order-64 comparison on every panel did not complete even a
one-unit radial chunk inside the 180-second probe budget.  The full `r=4`
transport was therefore not attempted.

The smallest repair is:

1. resume the content-addressed `r=247/8` checkpoint;
2. transport the exact `8 x 2` dual-number state on every panel;
3. run the independent sixteen-state expansion at chunk boundaries;
4. adapt step and order under fail-closed tail/width gates.

No `Bplus4`, `T_plus`, Stokes, scattering, or flux claim is promoted.

CLOSE-OUT: SHORTFALL — one correlated panel is certified, but throughput prevents the complete r=4 Bplus4 transport.
EVIDENCE: black_hole_programme/phase3/axial_partial_jet_outgoing_bplus4_v1/certificate.json
