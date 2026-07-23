# Exterior-norm boundary replay

This bounded remedy tests the full correlated exterior squared norm at the
single shell-4/segment-3 boundary where both exact q00 children previously
refused a raw-coordinate pivot.

For the 20-complex-coordinate Pluecker vector `p`, the Forge replay builds

```text
||p||^2 = sum_j ((Re p_j)^2 + (Im p_j)^2)
```

as one correlated order-4 interval-Taylor expression.  A strictly positive
lower enclosure proves that the decomposable exterior vector is nonzero and
therefore that the represented three-plane has rank three.  This uses every
coordinate and does not select a single scalar linear witness.

The replay fails closed with:

- code 36 when the squared-norm enclosure is not strictly positive;
- code 37 when the derived projective conditioning ratio is not positive.

The prior 19 segment heartbeats must remain byte-identical to the exact split
children.  No later shell is attempted.

Exact interval QR was also audited but is not implementable with the current
kernel: there is no validated interval square-root/orthogonalization
primitive.  This exterior norm is the strongest equivalent multi-functional
test available without extending the substrate.

Run:

```bash
PYTHONPATH=. python3 -m \
  black_hole_programme.phase3.axial_horizon_h4_plucker_exterior_norm_v1.run_children
PYTHONPATH=. python3 -m unittest -v \
  black_hole_programme.phase3.axial_horizon_h4_plucker_exterior_norm_v1.test_exterior
PYTHONPATH=. python3 -m \
  black_hole_programme.phase3.axial_horizon_h4_plucker_exterior_norm_v1.verify
```
