# Outgoing S one-panel checkpoint

This package transports the certified common-generator outgoing `S` endpoint
column from `r=32` to `r=8191/256` through one validated inward panel.

The base four-state system is `(Y,Z)`. Its intrinsic tangent is `(X,0)`.
Internally, the tangent is divided by `512` and the tangent generator is
divided by the same exact factor. The scale is undone before the checkpoint
is serialized. This controls internal arithmetic without disguising the
physical enclosure width.

The runtime checks the partial-dual transport against the directly stacked
generator coefficient by coefficient and requires interval overlap after the
exponential tail is added.

No joint outgoing frame, `K_plus`, `T_plus`, Stokes or flux claim is made.

Run:

```bash
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_splus_checkpoint_v1.produce
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_splus_checkpoint_v1.produce --check
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_splus_checkpoint_v1.verify
python3 -m unittest -v black_hole_programme.phase3.axial_partial_jet_outgoing_splus_checkpoint_v1.test_checkpoint
```
