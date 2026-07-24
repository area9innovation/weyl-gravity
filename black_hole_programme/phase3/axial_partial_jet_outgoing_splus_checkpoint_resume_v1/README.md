# Outgoing S normalized checkpoint continuation

This package resumes the content-addressed outgoing `S` checkpoint at
`r=8191/256` for sixteen `1/256`-wide inward panels.

The tangent is divided by the exact factor `512` once at restart and remains
normalized throughout all panels. The physical scale is restored only when
the final checkpoint is serialized. Each panel checks exact Taylor
coefficient equality and interval overlap between the partial-dual and
directly stacked transports.

The target is `r=8175/256`. No joint outgoing frame, `K_plus`, `T_plus`,
Stokes or flux claim is made.

Run:

```bash
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_splus_checkpoint_resume_v1.produce
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_splus_checkpoint_resume_v1.produce --check
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_splus_checkpoint_resume_v1.verify
python3 -m unittest -v black_hole_programme.phase3.axial_partial_jet_outgoing_splus_checkpoint_resume_v1.test_resume
```
