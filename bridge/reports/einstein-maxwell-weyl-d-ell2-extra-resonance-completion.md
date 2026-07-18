# Circumference velocity crossed with the complete `ell=2` extra block

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The polar direct sources in action-row order are

```text
S(d,e1) = (0,-6 i sqrt(3),0,0),
S(d,e2) = (-376 i sqrt(3),0,-632 i sqrt(3)/9,384 i sqrt(3)).
```

The rational `z=cos(theta)` tensor replay reproduces the independent
theta-coordinate `e1` result exactly.  The dense `e2` representative is
computed by the exact sparse decomposition `e2=-8 At-72 Ct+48 U`.

At `omega^2=16/3`, the polar p-shell adjoint basis is

```text
w1=(0,1,0,0),
w2=(-1/6,0,-3/2,1).
```

Its source pairing is `diag(-6 i sqrt(3),552 i sqrt(3))`, with determinant
`9936`.  Together with the axial determinant `832`, the complete parity block
has determinant `8266752`.  Hence for `d!=0`, the axial and polar extra
amplitudes can cancel an arbitrary `ell=2` p-shell adjoint defect, for every
`m` by `SO(3)` equivariance.

This completes the `d` column of the live homogeneous/twist source matrix.
It does not solve the simultaneous stabilizer constraints, nonresonant rows,
or the remaining `a,b` and twist position/velocity columns.
