# Global Berger rod source-sector solvability

## Exact result

The complete stress source of the six global detector-indexed rods has no
second-order compact Taub obstruction in the certified retained Berger metric
complex.

The source occupies ten spatial basis functions (`j=0,1`) and the temporal
frequencies `0,+-sqrt(58)/3`.  Because its Hopf-position dependence is
quadratic in `cos(z),sin(z)`, three phase-polynomial columns span every
detector position.  On these 100-component blocks, exact reduction gives

```text
frequency 0:            rank(H)=70, rank(H|-q0)=70 for all 3 columns
frequency +sqrt(58)/3:  rank(H)=68, rank(H|-q0)=68 for all 3 columns
frequency -sqrt(58)/3:  complex conjugate of the positive block
```

Every source column is Noether closed.  The certificate retains sparse exact
metric primitives with zero replay residual for
`H_retained Phi2=-q0^rod`.  Time translations only multiply the oscillatory
columns by phases, so the sum of the two detector sources is also exact.

## Boundary

This proves solvability only through order `epsilon_R^2`.  It does not build
an all-orders backreacted branch, the corrected 84-row cyclic interacting
complex, a causal Green homotopy for that complex, apparatus recoil, or a
quantum observer algebra.
