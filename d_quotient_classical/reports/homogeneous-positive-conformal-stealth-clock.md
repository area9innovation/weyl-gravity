# Homogeneous positive-sign conformal stealth-clock audit

## Result

Consider one real conformal scalar with the standard positive kinetic sign
and the complete local Weyl-invariant potential,

\[
S=-\int\sqrt{-g}\left[
\frac12(\nabla T)^2+\frac1{12}RT^2+\frac\kappa4T^4
\right].
\]

For a homogeneous field on the unit conformal cylinder, the exact equation
and improved stress tensor are

\[
\ddot T+T+\kappa T^3=0,
\qquad
\rho=\frac12(\dot T^2+T^2)+\frac\kappa4T^4,
\qquad
p=\frac\rho3.
\]

Thus a homogeneous stealth configuration is precisely a zero-energy
trajectory.

## Complete nonzero stealth family

For \(\kappa\geq0\), positivity of the three terms in \(\rho\) leaves only
\(T=0\).  A nonzero branch therefore requires \(\kappa=-g<0\).  Its first
integral is

\[
\dot T^2=T^2\left(\frac g2T^2-1\right).
\]

On a connected nonzero branch set

\[
u=\frac{\sqrt{2/g}}{T}.
\]

The first integral becomes

\[
\dot u^2+u^2=1.
\]

Therefore every nonzero real homogeneous stealth solution is, up to sign and
time translation,

\[
T(t)=\pm\sqrt{\frac2g}\sec(t-t_0).
\]

Direct substitution verifies both the scalar equation and
\(T_{\mu\nu}=0\).

## Clock obstruction

The field has a positive local kinetic sign, unlike the neutral two-scalar
candidate.  But its stealth potential is unbounded below.  More decisively,
every secant branch has

\[
\dot T(t_0)=0
\]

and poles at \(t=t_0\pm\pi/2\).  Hence it is neither globally monotone nor
globally regular on \(\mathbb R\times S^3\).  It supplies only local clock
charts separated by a turning point and finite-time singularities.

The scoped conclusion is

```text
HOMOGENEOUS_POSITIVE_STEALTH_CLOCK
    = OBSTRUCTED_BY_TURNING_POINT_AND_FINITE_TIME_POLES
```

The parent gate remains open.  This calculation does not exclude an
inhomogeneous stealth field with everywhere timelike nonzero gradient, nor a
positive clock on a genuinely non-conformally-flat Bach-sourced background.
The next gate is
`INHOMOGENEOUS_STEALTH_OR_NONCONFORMALLY_FLAT_CLOCK`.
