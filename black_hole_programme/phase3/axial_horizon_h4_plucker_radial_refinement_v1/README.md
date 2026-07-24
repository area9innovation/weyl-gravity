# H4 Pluecker radial refinement

This bounded successor changes only the radial panelization of shell 4,
segment 3.  It replays both exact q00 frequency half-cells from the same
certified pre-boundary state, first at twice and then, only if necessary, at
four times the original radial panel depth.

Each refined panel first tries an existing raw Pluecker coordinate.  Only a
typed raw code-32 refusal falls back to the already certified
midpoint-Hermitian functional.  No later shell is attempted.

Run:

```bash
python3 -m black_hole_programme.phase3.axial_horizon_h4_plucker_radial_refinement_v1.run_refinement
python3 -m black_hole_programme.phase3.axial_horizon_h4_plucker_radial_refinement_v1.verify
python3 -m unittest black_hole_programme.phase3.axial_horizon_h4_plucker_radial_refinement_v1.test_radial_refinement
```
