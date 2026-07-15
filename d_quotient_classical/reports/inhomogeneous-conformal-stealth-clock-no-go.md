# Complete one-field conformal stealth-clock no-go

## Theorem

For one real conformal scalar with standard positive kinetic sign and quartic
Weyl-invariant potential on the unit Einstein cylinder, there is no smooth
global stealth configuration whose gradient is everywhere timelike and
nonzero.  Thus this complete one-field stealth family cannot provide the
required relational clock.

## Why the reciprocal variable is legitimate

At a zero of (T), the zero-stress equation reduces to

\[
4\,dT\otimes dT=g\,(dT)^2.
\]

The left side has rank at most one while a nonzero right side has rank four;
if ((dT)^2=0), the equation itself gives (dT=0).  Hence a stealth field
cannot cross (T=0) with nonzero gradient.  Every clock candidate therefore
lies in a nowhere-zero sector where

\[
\sigma=T^{-1}
\]

is well defined.

## Exact classification

After multiplying the improved stress tensor by (3\sigma^4), its
trace-free part is the linear equation

\[
(\nabla_\mu\nabla_\nu\sigma)^{\rm TF}
=-\frac{\sigma}{2}G_{\mu\nu}^{\rm TF}.
\]

The mixed component gives (sigma=f(t)+s(n)).  The spatial equation is

\[
(D_iD_js)^{\rm TF}=0.
\]

Taking its divergence on the unit (S^3) gives

\[
D_i(\Delta_{S^3}+3)s=0,
\]

so compactness implies (s=s_0+C\cdot n), where (n\in S^3\subset\mathbb
R^4).  The temporal equation cancels (s_0).  The complete denominator is

\[
\boxed{\sigma=A\cos t+B\sin t+C\cdot n},
\]

and the trace equation fixes

\[
\boxed{\kappa=2(|C|^2-A^2-B^2)}.
\]

The homogeneous secant family is the special case (C=0).

## Global obstruction

If (A^2+B^2>0), choose (n\perp C) and a zero of
(A\cos t+B\sin t).  Then (sigma=0), so (T=1/\sigma) has a pole.  If
(A=B=0) and (C\ne0), choose (n\perp C); again (sigma=0), and the
field is time independent anyway.  The all-zero denominator is invalid.

There is also an independent clock-gradient obstruction.  For every
time-dependent member, choose (n\perp C) and a time extremum of the temporal
sinusoid.  At that regular point

\[
(\nabla\sigma)^2=|C|^2\geq0,
\]

so the gradient is spacelike or zero, never timelike.

Therefore

```text
INHOMOGENEOUS_STEALTH_OR_NONCONFORMALLY_FLAT_CLOCK
    = STANDARD_ONE_FIELD_STEALTH_BRANCH_OBSTRUCTED
```

and the surviving standard-model gate is
`POSITIVE_ENERGY_NONCONFORMALLY_FLAT_BACH_SOURCED_CLOCK`.

This does not rule out generalized non-Noetherian/higher-derivative scalar
actions, but those would be new theories with new health and BV gates.
