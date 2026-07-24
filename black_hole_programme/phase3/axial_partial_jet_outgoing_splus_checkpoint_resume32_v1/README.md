# Outgoing S 32-panel checkpoint successor

This new successor resumes the committed outgoing `S` checkpoint at
`r=8175/256` and attempts thirty-two further `1/256` inward panels.

The tangent remains divided by the exact factor `512` throughout transport.
The physical tangent is reconstructed only for final checkpoint
serialization. Every completed panel requires generator `7315`, exact
partial-dual/direct Taylor coefficient equality, interval overlap, a finite
tail, and finite widths.

The positive target is `r=8143/256`. The producer stops fail-closed on the
first rejected panel. No joint outgoing frame, `K_plus`, `T_plus`, Stokes or
flux claim is made.

Run:

```bash
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_splus_checkpoint_resume32_v1.produce
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_splus_checkpoint_resume32_v1.produce --check
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_splus_checkpoint_resume32_v1.verify
python3 -m unittest -v black_hole_programme.phase3.axial_partial_jet_outgoing_splus_checkpoint_resume32_v1.test_resume32
```
