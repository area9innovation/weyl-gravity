# Explicit \(T_+\) band v1 — correlated continuation

This Phase-4 package resumes the last certified common-moving outgoing
partial-jet checkpoint at \(r=979/32\). It advances the joint \(R/S\) base and
intrinsic tangent with one correlated dual-number panel. The direct
sixteen-state expansion is used only as an independent boundary gate.

This is an append-only checkpoint in the explicit-\(T_+\) experiment. Until
the common outgoing frame reaches \(r=4\) and is joined to the typed horizon
frame, it does not establish \(T_+\), reflection amplitudes, a Stokes
identity, or scattering.

Run:

```bash
python3 -m black_hole_programme.phase4.axial_explicit_tplus_band_v1.produce --reproduce
python3 -m black_hole_programme.phase4.axial_explicit_tplus_band_v1.verify
python3 -m unittest -v black_hole_programme.phase4.axial_explicit_tplus_band_v1.test_checkpoint
```
