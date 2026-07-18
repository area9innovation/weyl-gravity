# Berger Peter--Weyl form-Laplacian engine

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

For each spin `j`, the engine realizes the left-invariant derivatives by exact
skew-Hermitian `SU(2)` matrices, with `e3=xi3/c` and
`c=3*sqrt(10)/20`.  It combines these with

```text
d theta1=-(1/c) theta2 wedge theta3,
d theta2= +(1/c) theta1 wedge theta3,
d theta3= -c theta1 wedge theta2
```

to construct every finite Peter--Weyl block of `d_p`, its adjoint, and
`Delta_p=d_p^dagger d_p+d_(p-1)d_(p-1)^dagger`.  Exact blocks through
`two_j=4` have zero `d^2` defect, Hermitian Laplacians, and matching Hodge-dual
spectra.  The `two_j=1` scalar eigenvalue is `29/18`, independently matching
the global detector-rod calculation.

This supplies the exact spatial operator needed by the Maxwell and massive
two-form Green images.  The compact flat bumps have infinite harmonic support,
so their coefficients and the spectral tail still require validated interval
quadrature and bounds before a recoil coefficient can be claimed.
