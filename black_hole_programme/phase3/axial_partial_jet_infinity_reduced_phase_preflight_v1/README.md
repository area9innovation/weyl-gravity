# Reduced-phase outgoing-infinity partial-jet preflight

This package keeps the exact selected factor
\(e^{-2i\omega r_*}\) symbolic and transports only the reduced amplitude in
`IvTaylor4_omega tensor dual_tau`.  The seed is the exact finite
\(R_+=XI2-i(16\omega^2-4i\omega-5)XI3/\omega\) endpoint head, transformed
to the certified factor coordinates.

The finite head is corrected by an all-order scalar Regge--Wheeler Volterra
remainder, uniformly on the first frequency child.  A first inward
macropanel from \(r=32\) to \(r=1023/32\) is bounded, and the direct repeated
block agrees coefficientwise with its dual-number transport.

This certifies the selected repeated-spin-two outgoing Jost column at the
seed and through that panel.  It does not construct the remaining outgoing
factor columns, the endpoint shear, \(T_+\), reflection, scattering, flux,
or QNM data.

Run:

```bash
python3 -m black_hole_programme.phase3.axial_partial_jet_infinity_reduced_phase_preflight_v1.produce
python3 -m black_hole_programme.phase3.axial_partial_jet_infinity_reduced_phase_preflight_v1.verify
python3 -m unittest black_hole_programme.phase3.axial_partial_jet_infinity_reduced_phase_preflight_v1.test_preflight
```
