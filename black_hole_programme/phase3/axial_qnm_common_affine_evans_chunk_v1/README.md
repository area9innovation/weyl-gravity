# Axial QNM common-affine Evans chunk v1

This package evaluates panels 0 through 15 of the 512-panel projective Evans
boundary rail.  It uses four-process batches, sorts results by panel, writes
a checkpoint after every batch, and stops ordered output at the first panel
whose physical mismatch enclosure does not exclude zero.

Every panel uses one exact generator shared by the horizon export, outgoing
export, and

```text
Delta = q_H - q_out + 2*I*omega.
```

The argument principle is deliberately not run because this chunk is not the
complete closed contour.

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.
