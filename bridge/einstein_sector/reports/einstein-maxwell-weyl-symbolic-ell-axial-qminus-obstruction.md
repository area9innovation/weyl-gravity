# Symbolic-ell axial q-minus bounded obstruction

## Result

For every integer `ell>=2`, tune the allowed nonzero compact momentum by

```text
k^2=sqrt(2*ell*(ell+1))-ell/2-1/6.
```

On the twist-aligned common-zero tangent, the two axial Einstein-minus modes
at `+k` and `-k` source the unique polar extra-primary shell
`L=2*ell,K=0,Omega=2*omega_minus`.  Its reduced adjoint pairing is strictly
positive.  Consequently the tangent has no bounded or finite-quasiperiodic
second-order correction, even though all five stabilizer moment maps vanish.

## Exact coefficient

Put

```text
C_ell=binomial(2*ell,ell)^2/binomial(4*ell,2*ell),
r=sqrt(2*ell*(ell+1)),
A_ell=18*ell^4+24*ell^3+4*ell^2+16*ell+2,
B_ell=9*ell^3+21*ell^2-9*ell+11.
```

The axisymmetric resonant functional is

```text
-8*C_ell*ell^2*(ell+1)*(2*ell+1)*(r*B_ell-A_ell)
--------------------------------------------------- .
                 3*(6*ell^2+3*ell-1)
```

The sign is fixed by

```text
A_ell^2-2*ell*(ell+1)*B_ell^2
 =2*(ell-1)^3*(ell+2)*(81*ell^4+54*ell^3+42*ell-1)>0.
```

Both `A_ell` and `B_ell` are positive, hence `A_ell>r*B_ell` and the pairing
is strictly positive.

## Why this is not interpolation

The action-derived quadratic PBW operator is evaluated on the highest-weight
representative

```text
Y_(ell,ell)=sin(theta)^ell exp(i*ell*phi).
```

The output has `M=2*ell`, so no lower angular representation can contribute.
Evaluation at the equator therefore extracts the complete `L=2*ell`
coefficient.  The axisymmetric normalization is recovered with the exact top
Legendre/Gaunt factor `C_ell`.  The formula reproduces the independent direct
four-dimensional `ell=2` replay and the exact `ell=3,4,5,6` slow-rail probes.

## Claim boundary

This is an axial, one-`|k|`, separately tuned-circumference theorem.  Polar
and mixed input coefficients remain open, as do a single fixed circumference
across angular degrees, multiple-`|k|` joins, causal/retarded inversion, final
residual descent and quantum interpretation.  Smooth exponential-polynomial
secular correction remains certified by the existing finite-source theorem.
