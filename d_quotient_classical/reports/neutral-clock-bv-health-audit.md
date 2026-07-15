# Neutral clock-pair BV health audit

## Outcome

The neutral two-field model remains an exact homogeneous reference clock, but
it does **not** extend to a globally regular positive local matter clock by
simply declaring the opposite-sign direction gauge.

Write

\[
T_1=\rho\cos\theta,\qquad T_2=\rho\sin\theta.
\]

Weyl rescaling acts on \(\rho\), while \(\theta\) is Weyl invariant.  The
indefinite target line element is

\[
dT_1^2-dT_2^2
=\cos(2\theta)d\rho^2
-2\rho\sin(2\theta)d\rho,d\theta
-\rho^2\cos(2\theta)d\theta^2.
\]

After choosing the regular \(\rho=\text{constant}\) Weyl frame, the ratio
field retains a derivative action with target coefficient

\[
G_\theta=-\rho^2\cos(2\theta).
\]

It is therefore not a Weyl-contractible auxiliary field.

## Why every neutral winding clock crosses the problem

For the general equal-energy homogeneous pair,

\[
T_1=A\cos(t+\alpha),\qquad T_2=A\cos(t+\beta),
\]

one has

\[
W=A^2\sin(\alpha-\beta),
\qquad
N:=T_1^2-T_2^2=-W\sin(2t+\alpha+\beta).
\]

The clock condition is \(W\ne0\).  It forces \(N\) to cross zero four times
per compact \(D\) period.  Since \(G_\theta=-N\) in the fixed-radius frame,
the remaining local kinetic direction changes sign and becomes degenerate at
every crossing.  No regular neutral winding orbit stays inside one healthy
internal cone.

## What the gauge incidence does—and does not—prove

The scalar block of the linearized temporal-diffeomorphism/Weyl incidence has
determinant \(W\).  Its inverse is pointwise multiplication by \(1/W\), so
the scalar coordinates are excellent local gauge-fixing variables.  This is
why the homogeneous clock works.

But using those coordinates as unitary gauge transfers their derivative
dynamics into the metric and constraint rows.  It does not delete the coupled
physical degree of freedom.  Adding the scalar pair introduces no new gauge
symmetry, and the Weyl-reduced action still contains the ratio derivative
term explicitly.

Thus

```text
FULL_NEUTRAL_CLOCK_PAIR_BV_COMPLETION
    = OBSTRUCTED_AS_GLOBALLY_REGULAR_HEALTHY_CLOCK
```

while

```text
NEUTRAL_CONFORMAL_CLOCK_PAIR
    = VALID_HOMOGENEOUS_REFERENCE_CLOCK
```

remains unchanged.

## Next admissible model

The next search should avoid cancellation by a freely propagating opposite-
sign scalar.  The gate is
`POSITIVE_ENERGY_NONCONFORMALLY_FLAT_OR_STEALTH_CLOCK`: either construct a
positive-energy clock on a genuinely Bach-sourced non-conformally-flat
background, or find a stress-free conformal/stealth clock whose local kinetic
sector remains regular.

This audit is not a no-go theorem for those alternatives or for larger
contractible reference-matter extensions.
