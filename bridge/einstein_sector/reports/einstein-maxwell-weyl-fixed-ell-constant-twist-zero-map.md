# Fixed-ell constant-twist same-shell zero map

For every one fixed `ell>=2` at `k=0`, the constant axial twist position has
zero adjoint-cokernel projection on both Einstein `q` shells and on the full
axial-plus-polar extra `p` shell.  Equivalently,

```text
Q_(ell,-)=0,  Q_(ell,+)=0,  P_ell=0.
```

This is not an interpolation from the corrected `ell=2` fixture.  A constant
twist is a flat lifted `SO(3)` connection along the circle, so on `V_ell` it
replaces circle momentum by

```text
K_alpha = k + alpha*(A_hat dot J_ell).
```

The action-reduced target primaries are

```text
p = omega^2-K_alpha^2-lambda+2/3,
q = (omega^2-K_alpha^2-lambda)^2-2*lambda.
```

Their Feynman--Hellmann derivatives with respect to `alpha` vanish at `k=0`.
A derivative of a regular action Gram or primary basis multiplies `p` or `q`
and therefore vanishes on shell.  The previously certified `SO(3)`
factorization then promotes the zero multiplicity matrices to every `m`.
The direct corrected `ell=2` four-dimensional replay is an independent
calibration of this structural argument.

The substitution follows from the local lifted rotation
`F_alpha(x,y)=(x,exp(alpha*x*A_hat)y)` and naturality of the Euler operator.
This lift need not be periodic globally: its finite holonomy is precisely why
the twist is physical rather than gauge.  The proof uses only the local
covariantization identity for the periodic bilinear source, so it does not
quotient the holonomy modulus away.

This closes only the same-shell resonance gate.  The complete bounded product
cone still requires a uniform inverse/nonresonance proof for the neighboring
`L=ell-1` and `L=ell+1` twist-wave outputs.  Finite multi-ell sums, nonzero
momentum, causal propagation, residual observables and quantum transfer remain
fail-closed.
