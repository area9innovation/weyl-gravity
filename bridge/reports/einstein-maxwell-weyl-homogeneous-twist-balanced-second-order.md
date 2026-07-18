# Balanced homogeneous and twist-velocity second-order fixture

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

For `Y_10=cos(theta)`, a pure twist velocity has its harmonic norm
`4*pi/3`.  The correct common-zero balance against the homogeneous
radion-position/Jordan coordinate is therefore

```text
3*a^2=4*B^2,
A=b=c=d=Q_e=W_x=0.
```

The direct four-dimensional quadratic source contains only homogeneous
`L=0`, polar `L=2`, and axial `L=1` blocks.  All are solved explicitly:

```text
L=0: K2=-(4/9)B^2*t^4;
polar L=2: (A_t2,C_t2,U2)=B^2*(-5/6,5/6-(2/3)t^2,-7/36);
axial L=1: (h_x2,q_x2)=aB*(t+t^3/6,-t^3/6).
```

The certificate checks all eight polar tensor rows and all six axial rows.
Thus a nonzero twist velocity survives the complete second-order test when it
is balanced by the homogeneous sector.  Arbitrary twist vectors and
positions, physical `ell=1` inputs, and all-orders integration remain open.
