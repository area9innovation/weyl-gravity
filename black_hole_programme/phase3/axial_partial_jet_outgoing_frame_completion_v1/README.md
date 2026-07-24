# Outgoing partial-jet frame completion preflight

This package completes the exact *formal* outgoing factor frame in the
declared order `(E,R,S)` and distinguishes it from a validated common
`omega/tau` endpoint enclosure.

The normalized Einstein column `E=2 EI2` is the epsilon-copy of the selected
spin-two Jost column.  It therefore reuses the already certified all-order
spin-two Volterra remainder.  The normalized quotient column
`S=i XI3/(2 omega)` is exact, log-free, and has unit spin-one quotient.
The existing practical infinity certificate supplies an all-order six-state
existence enclosure for `XI3`, but it does not retain the shared
frequency/dual-number dependence needed to reinterpret that enclosure as one
correlated partial-jet column.

In the canonical formal recurrence gauge (unit leading amplitudes and zero
free `EI2` coefficient) the endpoint jet normalizer is `K_plus=0`.  This is
not promoted to a validated analytic endpoint normalizer because the
correlated all-order `S` remainder is still missing.  Consequently the
package makes no `T_plus`, reflection, Stokes, scattering, or flux claim.

Run:

```bash
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_frame_completion_v1.produce
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_frame_completion_v1.produce --check
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_frame_completion_v1.verify
python3 -m unittest black_hole_programme.phase3.axial_partial_jet_outgoing_frame_completion_v1.test_completion
```
