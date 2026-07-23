# Phase 3 axial horizon Grassmann/Möbius one-shell preflight

## Result

The isolated exact-affine Grassmann/Möbius rail passes on the first dyadic
future-horizon shell

\[
\rho\in[2^{-22},2^{-21}]
\]

for axial \(\ell=2\) pure-Weyl perturbations and the four ordered exact
frequency subcells partitioning

\[
M\omega\in[1/2,129/256].
\]

All 64 panel checks retain generator `7315`, certify rank six, and keep the
chart-norm upper bound below \(1.095\).  Every subcell has:

* exact rational column-gauge invariance;
* entrywise intersection with the independently propagated direct endpoint
  rechart;
* a direct-to-Grassmann width-improvement factor between \(4.632\) and
  \(4.640\).

The native and C backends both return `42` with byte-identical stdout:

```text
3716026f1685a50daf91775ad6ef3d868d29e59c335e2b38273e9c1ee94ce1b8
```

The independent verifier passes, as do all eight scoped mutation and unit
tests.

## Interpretation

This closes the first-shell method gate that the predecessor full-column
transport could not pass.  It establishes that a parameter-correlated
Grassmann chart, checked Möbius right solve, and four exact frequency
subcells materially control enclosure growth on this shell.

It does **not** yet preserve horizon-labelled amplitudes or reach \(r=4\).
The immediate successor must add the separate amplitude/pivot map, certified
chart switching, and an ordered dyadic-shell join before emitting a channel
handoff.

## Claim boundary

This preflight does not establish:

* transport beyond the first dyadic horizon shell;
* horizon-labelled amplitude transport;
* a horizon-to-\(r=4\) map or horizon-to-infinity connection;
* scattering, flux sign, stability, a physical ghost, positivity, CPT, or
  unitarity;
* another frequency interval, angular momentum, or polar parity.

CLOSE-OUT: DONE — exact one-shell Grassmann/Möbius transport passes all four frequency subcells and both backends

EVIDENCE: black_hole_programme/phase3/axial_horizon_grassmann_mobius_preflight/certificate.json
