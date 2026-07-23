# Exterior multi-functional remedy: certified design blocker

## Aim

The raw coordinate and midpoint-Hermitian scalar charts both failed at
q00 shell 4 segment 3.  This experiment tests a genuinely different
coordinate-invariant certificate: positivity of the complete squared norm
of the 20-complex-coordinate Pluecker vector.

For a decomposable exterior three-vector `p`,

```text
sum_j |p_j|^2 > 0
```

is equivalent to `p != 0`, hence to a nonzero represented three-plane.  The
implementation uses exact Taylor multiplication and addition over the
shared frequency generator, retaining correlations across all 40 real
coordinates.  It does not rely on any one coordinate or linear functional.

## Result

Both exact q00 children refuse with typed code 36:

| child | frequency cell | squared-norm enclosure | component sup |
|---|---|---|---:|
| 0 | `[1/2, 4097/8192]` | `[-1.8806067696070636, 1.8806067696219595]` | `0.7575348795807845` |
| 1 | `[4097/8192, 2049/4096]` | `[-1.8915929169003969, 1.8915929169152985]` | `0.7597025238436113` |

The true squared norm is nonnegative, but the current generic
interval-Taylor multiplication loses that sum-of-squares structure: its
remainder enclosure extends far below zero.  Consequently neither a
positive exterior lower bound nor a conditioning ratio can be certified.

The first 19 heartbeats match the source split-child runs byte for byte.
Thus the result isolates the same refused boundary and does not perturb the
previously certified prefix.

## Feasibility verdict

An exact QR remedy is not currently available: the Forge substrate has no
validated interval square-root/orthogonalization primitive.  The strongest
equivalent multi-functional certificate supported by the existing exact
kernels also fails on both child enclosures.

This is a design blocker, not a rank-loss theorem.  Proceeding requires one
of:

1. a positivity-preserving sum-of-squares/Taylor model;
2. certified interval QR or orthogonal-frame propagation;
3. materially tighter correlated radial enclosures before the boundary.

Another scalar pivot or unchanged generic Taylor product is not justified.
No later shell, paper, or lifecycle state is changed.
