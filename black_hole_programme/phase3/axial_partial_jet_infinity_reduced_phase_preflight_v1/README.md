# Reduced-phase outgoing-infinity partial-jet preflight

This package keeps the exact selected factor
\(e^{-2i\omega r_*}\) symbolic and transports only the reduced amplitude in
`IvTaylor4_omega tensor dual_tau`.  The seed is the exact finite
\(R_+=XI2-i(16\omega^2-4i\omega-5)XI3/\omega\) endpoint head, transformed
to the certified factor coordinates.

One tiny inward panel from \(r=32\) is bounded, and the direct repeated block
agrees coefficientwise with its dual-number transport.  The finite endpoint
head does not yet carry an all-order shared-\(\omega\), dual-\(\tau\) Jost
remainder.  Consequently this package does not certify the outgoing Jost
column, \(T_+\), reflection, scattering, flux, or QNM data.

Run:

```bash
python3 -m black_hole_programme.phase3.axial_partial_jet_infinity_reduced_phase_preflight_v1.produce
python3 -m black_hole_programme.phase3.axial_partial_jet_infinity_reduced_phase_preflight_v1.verify
python3 -m unittest black_hole_programme.phase3.axial_partial_jet_infinity_reduced_phase_preflight_v1.test_preflight
```
