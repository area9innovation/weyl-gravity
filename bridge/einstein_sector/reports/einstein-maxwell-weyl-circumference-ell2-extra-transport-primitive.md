# Circumference–extra resonant transport primitive

The `ell=0` circumference tangent crossed with the complete axial-plus-polar
`ell=2,k=0` extra block lies at the potential `p=0` propagation resonance,
with `omega^2=16/3` and `q=-104/9`.  The physical source nevertheless does
not require a secular time prefactor.

The reason is exact family transport.  For
`g_R=-dt^2+R^2 dx^2+dOmega_2^2`, `R^2=1+eta*c`, differentiation of
`L_R u_R=0` gives the mixed source as the negative linear image of the
transported representative.  Each covariant `x` index and each `A_x`
coefficient contributes one radius weight.

All two axial and the first polar source columns vanish.  The second polar
column has the nonzero source, in row order
`metric_00, metric_01, metric_11, metric_0a, metric_1a, sphere_trace,
sphere_tracefree, maxwell_axial_density`,

```text
(-36 c, 0, 164 c, -6 i c omega, 0, -100 c, -24 c, -20 c),
```

and the ordinary same-frequency correction

```text
(A_t, B, C_t, U) = (0, 0, -72 c, 24 c).
```

Every one of the six axial and eight polar equation-row remainders vanishes
exactly on the `p` shell.  Mutating the two-covariant-`x` weight of `C_t` from
two to one produces a nonzero eight-row remainder, providing a convention
negative control.

This is a coefficient-explicit reduced-mode transport theorem, not a causal
right inverse, final residual descent, particle statement, or quantum result.
