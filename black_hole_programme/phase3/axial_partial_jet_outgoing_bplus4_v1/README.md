# Bplus4 correlated transport diagnosis

This package starts from the sole admissible common-moving outgoing
checkpoint at `r=31` and transports the `R` and `S` columns together as one
`8 x 2` base/tangent Taylor model.  It preserves frequency generator `7315`,
the intrinsic dual-number correlation, the typed zero-free factor `h0`, and
the structurally frozen spin-one tangent.

The bounded prototype certifies one order-96 panel:

```text
start       31
end         247/8
step        -1/8
box radius  1/16
tail        0.007426513552203137
width       1.78453621449834
```

The partial-jet result is compared against the independently expanded direct
sixteen-state series.  Exact Taylor coefficients agree and the interval
difference contains zero.

This is deliberately a shortfall result.  The complete `r=4` section is not
reached, so `Bplus4`, `T_plus`, and Stokes remain fail-closed.

The smallest next repair is to resume the serialized `r=247/8` state in
content-addressed high-order chunks, transporting the exact partial jet on
every panel and performing the much more expensive independent direct
sixteen-state comparison at chunk boundaries.  Step/order must remain
adaptive and fail closed on width or tail.

Checks:

```bash
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_bplus4_v1.produce --check
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_bplus4_v1.verify
python3 -m unittest black_hole_programme.phase3.axial_partial_jet_outgoing_bplus4_v1.test_bplus4
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_bplus4_v1.audit
```
