# Validated flat-bump moment enclosures

The standard flat bump is reduced to the radial integrands

```text
f_p(r)=r^p exp(1-1/(1-r^2)),  0<=r<1.
```

Their logarithmic derivatives have the exact sign polynomial
`p(1-r^2)^2-2r^2`, so every integrand is unimodal.  A 32768-cell dyadic
Darboux sum combines this fact with directed-rounding exponential endpoint
intervals.  The certificate serializes the resulting binary endpoints as
exact rationals and encloses normalized even moments through order twelve.

Exact scaling supplies moments for the clock radius `1/64` and the fixed
detector rod radius `1/128`.  Rotational symmetry also reduces the needed
second and fourth Cartesian tensors to radial moments.

This closes a numerical-foundation subgate, not the harmonic calculation.
The Peter--Weyl coefficients still require the local `SU(2)` mode
polynomials and a validated remainder for powers of
`y0=sqrt(1-|y|^2)`.  The infinite spectral tail additionally requires an
evaluated Sobolev norm; the general spectral inequality alone is not counted
as that bound.
