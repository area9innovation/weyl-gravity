# Homogeneous common-zero quadric at second order

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

For the complete standard homogeneous tangent

```text
K=a+b*t,
C=a*t^2+(b/3)*t^3+c+d*t,
A_x=W_x+Q_e*t,
```

the direct four-dimensional quadratic Weyl--Maxwell source has

```text
S_E00=-(a^2+b^2-b*d+Q_e^2)/2.
```

This is exactly the homogeneous moment-map equation.  The second dependent
metric relation differs by the same quadric, while `c` and `W_x` do not enter
the source at all.  On the complete common-zero locus, all remaining rows are
removed by the explicit polynomial correction stored in the certificate.

Thus the entire standard homogeneous common-zero quadric—not just the
example `a=Q_e=0,b=d`—extends through second order at fixed magnetic bundle
topology.  This does not rescue the isolated constant radion: it lies off the
quadric and retains its certified fixed-bundle obstruction.

Twist velocities, physical `ell=1` inputs, exceptional fourth-order modes,
and all-orders integration remain open.
