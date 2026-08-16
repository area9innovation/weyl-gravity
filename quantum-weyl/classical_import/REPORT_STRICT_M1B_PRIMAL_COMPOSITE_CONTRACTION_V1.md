# Strict M1B primal composite contraction

**Result:** `STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION_V1`
**Lifecycle:** `CLASSIFIED`
**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The primal represented contraction is now an actual typed composite.  Removing
the 205 isolated comparison test doublets leaves 4,080
endpoint coordinates and 470 ordered primal residual
classes.  The restricted exact matrices contain 1,805
nonzero q0 entries, 1,805 homotopy entries,
and 470 inclusion/projection entries in each
direction.  Every declared normalized contraction identity has zero defects.

The full formula is

```text
pi_comp   = pi_rep o rho_[2,6] o p_end_graph
iota_comp = i_end_graph o iota_rep
s_comp    = H_alg_graph + i_end_graph o s_rep o rho_[2,6] o p_end_graph
```

This is a typed operator DAG.  The local 386-to-30 arrows are finite-order
component-jet operators; the 30-species endpoint bundle is realized on 4,080
global harmonic coordinates; and the residual target has 470 coordinates.
Those are different categories, so no 386-by-470 matrix is asserted.

## Exact checks

| Check family | Defects |
|---|---:|
| represented q0 squared | 0 |
| represented pi iota | 0 |
| represented contraction | 0 |
| represented chain maps | 0 |
| represented normalized side conditions | 0 |
| typed formal composition | 0 |

## Boundary and next gate

The graph-to-endpoint factor is support-local; harmonic restriction is global
and support-expanding.  This certificate completes only the primal M1B layer.
The action-derived compact-source dual must next be lifted through the composite,
after which the rank-940 pairing, adjointness, skew-homotopy, inclusion isometry,
and cyclic contraction identities must be replayed.  M1C, Gate A, nonlinear
Green compatibility, Hadamard data, products, QME, and residual transfer remain
fail closed.
