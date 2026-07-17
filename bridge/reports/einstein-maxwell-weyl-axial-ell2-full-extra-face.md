# Axial ell=2 face with both extra polarizations

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The extra `p`-primary shell has two axial polarizations.  Paper 91 and the
first cone extension used only the spatial representative `e2`.  A direct
four-dimensional calculation now gives

```text
S_e1(0) = (-1728/5) (1,0,1/2,0),
S_e1,e2(0) = 0.
```

Thus both extra self-sources lie on the same spacetime cokernel ray, while
their phase-sensitive zero-frequency interference vanishes.  Their two
coefficients are proportional to the diagonal positive extra Lee--Wald Gram
entries at `k=0`.

Balancing the negative coefficients of Einstein-plus, `e1`, and `e2` against
Einstein-minus produces a three-parameter positive cone.  The complete
homogeneous zero source cancels throughout it.  Adding `e1` creates no new
frequencies; every nonzero homogeneous source lies in the exact Noether
kernel/image, and the inherited polar `ell=2,4` shell witnesses remain
nonzero.  Hence the entire declared axisymmetric face is second-order
extendible, with arbitrary constant phases.

This is not yet an all-`m` theorem.  Non-axisymmetric products admit odd
output angular momenta, including exceptional `L=1` and generic axial `L=3`
zero-frequency channels.  Those must be tested directly before symmetry
promotion.
