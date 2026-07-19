# Symbolic-ell q-minus two-parity resonance matrix

## Result

For every integer `ell>=2`, on the separately tuned opposite-momentum
q-minus divisor, the unique `L=2*ell`, `K=0`, `Omega=2*omega_minus`
resonance has the exact two-output matrix

```text
R_polar = R_ell*(a_+*a_- - ell*(ell+1)*p_+*p_-/2),
R_axial = X_ell*(a_+*p_- - a_-*p_+).
```

Here `R_ell>0` is the already certified axial self-coefficient.  The polar
self-coefficient is exactly `-ell*(ell+1)*R_ell/2`, and `X_ell` is nonzero.

## Cross coefficient

With

```text
C_ell=binomial(2*ell,ell)^2/binomial(4*ell,2*ell),
r=sqrt(2*ell*(ell+1)),
k^2=r-ell/2-1/6,
```

the cross coefficient is

```text
X_ell=4*C_ell*ell^2*(ell+1)*(2*ell+1)*k
      *(r*(2*ell^2+5*ell+1)-(3*ell^3+8*ell^2+5*ell)).
```

It is strictly negative for positive `k`, because

```text
(3*ell^3+8*ell^2+5*ell)^2
-2*ell*(ell+1)*(2*ell^2+5*ell+1)^2
=ell*(ell-1)^3*(ell+1)*(ell+2)>0.
```

The exact `ell=2` specialization reproduces all three coefficients of the
independent direct four-dimensional parity matrix.

## Complete resonant zero variety

The two equations vanish on exactly four components:

1. `a_+=p_+=0`, with the minus-momentum pair arbitrary;
2. `a_-=p_-=0`, with the plus-momentum pair arbitrary;
3. `a_+=s*p_+`, `a_-=s*p_-`;
4. `a_+=-s*p_+`, `a_-=-s*p_-`;

where `s=sqrt(ell*(ell+1)/2)`.  The last two are nonzero mixed-parity,
two-momentum null sheets.  Away from this variety the unique p-shell
collision obstructs bounded or finite-quasiperiodic correction.

## Claim boundary

This theorem classifies the unique resonant matrix, not the complete
second-order equation on its null sheets.  Full bounded inversion on those
sheets remains open for general `ell`.  A single fixed circumference,
multiple absolute momenta, causal/retarded transport, final residual descent,
observational claims and quantum claims are also outside scope.
